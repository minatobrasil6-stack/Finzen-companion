import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io
import math
import requests
from datetime import date, datetime, timedelta

try:
    import extra_streamlit_components as stx
    COOKIES_AVAILABLE = True
except ImportError:
    COOKIES_AVAILABLE = False

# ============================================================
# FINZEN — app.py
# Versión Definitiva: Automatización Pro, Presupuesto Base Cero,
# Metas Gamificadas, Auditoría de Gastos Hormiga y Spotify Wrapped Financiero.
# Correo administrador: minatobrasil6@gmail.com
# ============================================================

try:
    from supabase import create_client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

st.set_page_config(
    page_title="FinZen | La Herramienta Financiera Definitiva",
    layout="wide",
    page_icon="🌱",
    initial_sidebar_state="expanded",
)

# Inyectar el manifest.json + service worker para convertir la app en PWA
# instalable. Los archivos viven en ./static/ (manifest.json, icon-192.png,
# icon-512.png, service-worker.js) y requieren enableStaticServing=true en
# .streamlit/config.toml. Streamlit los sirve bajo la ruta /app/static/...
import streamlit.components.v1 as components
components.html(
    """
    <script>
    (function() {
        try {
            var doc = window.parent.document;
            var head = doc.head;

            function agregarTag(tag, atributos) {
                if (doc.querySelector(tag + '[rel="' + atributos.rel + '"]')) return;
                var el = doc.createElement(tag);
                for (var k in atributos) { el.setAttribute(k, atributos[k]); }
                head.appendChild(el);
            }

            // Manifest, íconos y meta tags -- inyectados en el <head> REAL de
            // la página, no en el iframe aislado de components.html (ese era
            // el bug: el navegador nunca los veía).
            agregarTag('link', { rel: 'manifest', href: './app/static/manifest.json' });
            agregarTag('link', { rel: 'icon', href: './app/static/icon-192.png' });
            agregarTag('link', { rel: 'apple-touch-icon', href: './app/static/icon-192.png' });

            if (!doc.querySelector('meta[name="theme-color"]')) {
                var m1 = doc.createElement('meta'); m1.name = 'theme-color'; m1.content = '#1F4D3D'; head.appendChild(m1);
            }
            if (!doc.querySelector('meta[name="apple-mobile-web-app-capable"]')) {
                var m2 = doc.createElement('meta'); m2.name = 'apple-mobile-web-app-capable'; m2.content = 'yes'; head.appendChild(m2);
            }
            if (!doc.querySelector('meta[name="apple-mobile-web-app-title"]')) {
                var m3 = doc.createElement('meta'); m3.name = 'apple-mobile-web-app-title'; m3.content = 'FinZen'; head.appendChild(m3);
            }

            // Service worker: registrado contra el navigator de la ventana
            // PADRE (la página real), no el del iframe -- si se registra
            // dentro del iframe, controla solo ese iframe, no la app.
            if ('serviceWorker' in window.parent.navigator) {
                window.parent.navigator.serviceWorker.register('./app/static/service-worker.js').catch(function(e) {
                    console.log('Service worker no registrado:', e);
                });
            }
        } catch (e) {
            console.log('No se pudo inyectar el manifest en la página padre:', e);
        }
    })();
    </script>
    """,
    height=0,
)
# NOTA: la ruta exacta bajo la que Streamlit Cloud sirve /static puede variar
# según versión — si "Instalar app" no aparece en el navegador tras desplegar,
# lo primero a revisar es esta ruta (abre <tu-url>/app/static/manifest.json
# directamente en el navegador; si da 404, hay que ajustar el prefijo).

# ============================================================
# CONFIGURACIÓN DE ADMINISTRADOR
# ============================================================
CORREO_ADMIN = "minatobrasil6@gmail.com"

def es_administrador():
    return st.session_state.get("user") == CORREO_ADMIN

# ============================================================
# DISEÑO Y ESTILOS AVANZADOS
# ============================================================
PAPEL = "#FAF7F1"
TARJETA = "#FFFFFF"
BORDE = "#E7E0D4"
TEXTO = "#2B2620"
TEXTO_SUAVE = "#7A7266"
PINO = "#1F4D3D"
PINO_CLARO = "#2E6B54"
PINO_OSCURO = "#153A2D"
CORAL = "#E8734A"
SALVIA = "#7FB69E"
ARENA = "#F1E9D8"
GOLD = "#D9A441"
CIELO = "#5C86A8"
CIRUELA = "#8B5FA0"
LADRILLO = "#C1554F"

PALETA_CATEGORIAS = [PINO, CORAL, GOLD, CIELO, SALVIA, CIRUELA, LADRILLO, "#3D6B7D"]

ICONOS_CATEGORIA = {
    "Supermercado": "🛒",
    "Restaurantes": "🍽️",
    "Transporte": "🚗",
    "Suscripciones": "📱",
    "Vivienda": "🏠",
    "Salud": "💊",
    "Entretenimiento": "🎬",
    "Otros gastos": "📦",
    "Salario": "💰",
    "Otros ingresos": "➕",
}

st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@500;600;700;800&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500;600&display=swap');

html, body, .stApp {{
    background-color: {PAPEL} !important;
    color: {TEXTO};
    font-family: 'Inter', sans-serif;
}}

#MainMenu, footer {{
    visibility: hidden;
}}

h1, h2, h3 {{
    font-family: 'Quicksand', sans-serif !important;
    font-weight: 700 !important;
    color: {PINO} !important;
}}

.hero-banner {{
    background: linear-gradient(135deg, {PINO} 0%, {PINO_CLARO} 58%, {CIELO} 130%);
    border-radius: 24px;
    padding: 28px 30px;
    margin-bottom: 20px;
    color: white;
    box-shadow: 0 8px 24px rgba(31,77,61,0.18);
}}

.hero-banner h1 {{
    color: white !important;
    margin: 0 0 5px 0;
    font-size: 30px !important;
}}

.hero-banner p {{
    color: rgba(255,255,255,.9) !important;
    margin: 0;
    font-size: 14px;
}}

.hero-pill {{
    display: inline-block;
    background: rgba(255,255,255,.16);
    border: 1px solid rgba(255,255,255,.28);
    border-radius: 20px;
    padding: 5px 12px;
    font-size: 12px;
    font-weight: 700;
    margin-top: 11px;
}}

div[data-testid="stMetric"] {{
    background: {TARJETA};
    border: 1px solid {BORDE};
    border-radius: 16px;
    padding: 16px 18px;
    box-shadow: 0 2px 8px rgba(43,38,32,.05);
}}

div[data-testid="stMetricLabel"] {{
    font-size: 12px !important;
    color: {TEXTO_SUAVE} !important;
    text-transform: uppercase;
}}

div[data-testid="stMetricValue"] {{
    font-family: 'JetBrains Mono', monospace !important;
    color: {TEXTO} !important;
    font-weight: 600 !important;
}}

.stButton > button {{
    background: linear-gradient(135deg, {PINO}, {PINO_CLARO});
    color: white;
    border: none;
    border-radius: 12px;
    font-weight: 700;
    min-height: 42px;
    box-shadow: 0 3px 10px rgba(31,77,61,.22);
}}

.stDownloadButton > button {{
    background: linear-gradient(135deg, {SALVIA}, {PINO_CLARO});
    color: white;
    border-radius: 12px;
    font-weight: 700;
    border: none;
}}

section[data-testid="stSidebar"] {{
    background-color: {ARENA};
    border-right: 1px solid {BORDE};
}}

.consejo-card {{
    background: {TARJETA};
    border: 1px solid {BORDE};
    border-left: 4px solid {PINO};
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 12px;
    box-shadow: 0 2px 6px rgba(43,38,32,.04);
}}

.consejo-alerta {{
    border-left-color: {CORAL} !important;
}}

.consejo-bueno {{
    border-left-color: {SALVIA} !important;
}}

.pro-badge {{
    background: {GOLD};
    color: white;
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 700;
}}

.admin-badge {{
    background: {LADRILLO};
    color: white;
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 700;
}}

.free-badge {{
    background: {TEXTO_SUAVE};
    color: white;
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 700;
}}
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# CONFIGURACIÓN Y CONSTANTES
# ============================================================
STRIPE_PAYMENT_LINK = "https://checkout.wompi.co/l/VPOS_nhu0oQ"

CATEGORIAS_DEFECTO = [
    ("Supermercado", "gasto"),
    ("Restaurantes", "gasto"),
    ("Transporte", "gasto"),
    ("Suscripciones", "gasto"),
    ("Vivienda", "gasto"),
    ("Salud", "gasto"),
    ("Entretenimiento", "gasto"),
    ("Otros gastos", "gasto"),
    ("Salario", "ingreso"),
    ("Otros ingresos", "ingreso"),
]

REGLAS_CATEGORIZACION = {
    "Supermercado": ["walmart", "soriana", "chedraui", "supermercado", "costco", "la comer", "aurrera", "exito", "carulla", "éxito"],
    "Restaurantes": ["restaurante", "starbucks", "mcdonald", "uber eats", "rappi", "cafe", "café", "domino", "restaurant", "sushi"],
    "Transporte": ["uber", "cabify", "didi", "gasolina", "gasolinera", "metro", "camion", "taxi", "transmilenio", "peaje"],
    "Suscripciones": ["netflix", "spotify", "disney", "hbo", "amazon prime", "youtube premium", "icloud", "chatgpt"],
    "Vivienda": ["renta", "hipoteca", "luz", "agua", "gas natural", "predial", "mantenimiento", "arriendo", "internet"],
    "Salud": ["farmacia", "doctor", "hospital", "seguro medico", "seguro médico", "dentista", "eps"],
    "Entretenimiento": ["cine", "boletos", "concierto", "videojuego", "steam", "playstation"],
}

# ============================================================
# MONEDA Y TIPO DE CAMBIO
# ============================================================
@st.cache_data(ttl=900, show_spinner=False)
def obtener_tipo_cambio_usd_cop():
    try:
        r = requests.get("https://open.er-api.com/v6/latest/USD", timeout=8, headers={"User-Agent": "FinZen/1.0"})
        if r.ok:
            data = r.json()
            cop = data.get("rates", {}).get("COP")
            if cop and float(cop) > 0:
                return float(cop), "ExchangeRate-API", pd.Timestamp.now()
    except Exception:
        pass
    return None, None, None

if "moneda" not in st.session_state:
    st.session_state["moneda"] = "COP"

tc_usd_cop, fuente_fx, fecha_fx = obtener_tipo_cambio_usd_cop()

def tasa_usd_cop():
    return tc_usd_cop if tc_usd_cop and tc_usd_cop > 0 else 4000.0

def a_moneda(valor_cop):
    valor = float(valor_cop or 0)
    if st.session_state["moneda"] == "USD":
        return valor / tasa_usd_cop()
    return valor

def a_cop(valor, moneda=None):
    moneda_real = moneda or st.session_state["moneda"]
    valor = float(valor or 0)
    if moneda_real == "USD":
        return valor * tasa_usd_cop()
    return valor

def dinero(valor_cop, decimales=0):
    """COP se muestra con punto como separador de miles (convención colombiana:
    'COP $1.234.567', no 'COP $1,234,567'). USD mantiene coma (convención EE.UU.)."""
    valor = a_moneda(valor_cop)
    if st.session_state["moneda"] == "USD":
        return f"US$ {valor:,.{decimales}f}"
    texto = f"{valor:,.{decimales}f}".replace(",", ".")
    return f"COP ${texto}"


def dinero_md(valor_cop, decimales=0):
    """Igual que dinero(), con el '$' escapado (\\$) para usar en st.markdown/
    st.info/st.warning/st.success cuando pueda haber DOS montos en la misma línea.
    Streamlit interpreta un par de '$' en una línea de Markdown como el inicio/fin
    de una fórmula LaTeX — con dos montos en una frase, todo lo de en medio se
    renderiza como código crudo en vez de texto normal (bug ya visto antes)."""
    return dinero(valor_cop, decimales).replace("$", "\\$")

def icono_categoria(nombre):
    return ICONOS_CATEGORIA.get(str(nombre), "🏷️")

def estilo_grafico(fig, titulo=None, height=360):
    fig.update_layout(
        template="plotly_white",
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=TEXTO_SUAVE, size=12),
        title=dict(text=titulo, font=dict(family="Quicksand, sans-serif", color=PINO, size=17)) if titulo else None,
        margin=dict(l=10, r=10, t=48 if titulo else 10, b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXTO_SUAVE, size=11)),
        xaxis=dict(gridcolor=BORDE, zerolinecolor=BORDE),
        yaxis=dict(gridcolor=BORDE, zerolinecolor=BORDE),
    )
    return fig

def grafico_salud_financiera(puntaje):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=puntaje,
        number={"font": {"size": 40, "family": "JetBrains Mono", "color": TEXTO}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 0, "tickcolor": BORDE},
            "bar": {"color": PINO, "thickness": 0.3},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 40], "color": "rgba(232,115,74,.18)"},
                {"range": [40, 70], "color": "rgba(217,164,65,.18)"},
                {"range": [70, 100], "color": "rgba(127,182,158,.25)"},
            ],
        }
    ))
    fig.update_layout(height=205, margin=dict(l=15, r=15, t=5, b=5), paper_bgcolor="rgba(0,0,0,0)")
    return fig

def auto_categorizar(descripcion):
    if not descripcion:
        return "Otros gastos"
    texto = str(descripcion).lower()
    for categoria, palabras in REGLAS_CATEGORIZACION.items():
        if any(p in texto for p in palabras):
            return categoria
    return "Otros gastos"


# ============================================================
# CONTEXTO ECONÓMICO — 3 modelos públicos, académicamente validados, mismos
# que usa el motor Q-FSI. Nudge educativo, NO consejo de inversión. Se muestran
# por separado porque cada uno mide algo distinto (bonos, empleo, actividad
# real) y combinarlos en un solo número fingiría una precisión que no existe.
# ============================================================
@st.cache_data(ttl=3600, show_spinner=False)
def cargar_fred_csv(series_id, years=None):
    try:
        r = requests.get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}", timeout=10)
        if r.status_code != 200:
            return None
        df = pd.read_csv(io.StringIO(r.text))
        df.columns = ["Date", series_id]
        df["Date"] = pd.to_datetime(df["Date"])
        df[series_id] = pd.to_numeric(df[series_id], errors="coerce")
        df = df.dropna().set_index("Date")
        if years:
            df = df[df.index >= pd.Timestamp.today() - pd.DateOffset(years=years)]
        return df if not df.empty else None
    except Exception:
        return None


@st.cache_data(ttl=3600, show_spinner=False)
def cargar_contexto_economico():
    """Evalúa los 3 modelos y devuelve (señales_activas, detalle). Fuente: FRED,
    dato público de gobierno de EE.UU. — sin restricción de licencia."""
    señales, detalle = 0, []

    dgs10 = cargar_fred_csv("DGS10", years=1)
    dgs3mo = cargar_fred_csv("DGS3MO", years=1)
    if dgs10 is not None and dgs3mo is not None:
        df = dgs10.join(dgs3mo, how="inner").dropna()
        if not df.empty:
            spread = df["DGS10"].iloc[-1] - df["DGS3MO"].iloc[-1]
            prob = (0.5 * (1 + math.erf((-0.5333 - 0.6330 * spread) / math.sqrt(2)))) * 100
            activo = prob >= 30
            señales += int(activo)
            detalle.append(("Modelo NY Fed (curva de rendimientos)", prob, activo,
                             f"{prob:.0f}% prob. de recesión en 12 meses — LÍDER, con rezago de 6-24 meses"))

    sahm = cargar_fred_csv("SAHMREALTIME", years=2)
    if sahm is not None and not sahm.empty:
        valor = sahm["SAHMREALTIME"].iloc[-1]
        activo = valor >= 0.50
        señales += int(activo)
        detalle.append(("Regla de Sahm (empleo)", valor, activo,
                         f"{valor:.2f}pp sobre el mínimo de 12 meses — CASI COINCIDENTE, confirma no anticipa"))

    recprob = cargar_fred_csv("RECPROUSM156N", years=2)
    if recprob is not None and not recprob.empty:
        valor = recprob["RECPROUSM156N"].iloc[-1]
        activo = valor >= 50
        señales += int(activo)
        detalle.append(("Modelo Chauvet-Piger (actividad real)", valor, activo,
                         f"{valor:.0f}% probabilidad — COINCIDENTE, sin usar precios de mercado"))

    return señales, detalle


def recomendacion_fondo_emergencia(señales, gasto_mensual_promedio, ahorro_actual_estimado):
    """Conecta el contexto macro con los datos REALES del usuario — esto es lo
    que ningún competidor (Monarch, YNAB, Copilot) hace: traduce una señal
    macroeconómica pública en un número concreto y accionable para TU bolsillo."""
    if gasto_mensual_promedio <= 0:
        return None
    meses_cubiertos = (ahorro_actual_estimado / gasto_mensual_promedio) if gasto_mensual_promedio > 0 else 0
    meses_recomendados = 6 if señales >= 2 else (4 if señales == 1 else 3)
    faltante = max(0, (meses_recomendados * gasto_mensual_promedio) - ahorro_actual_estimado)
    return {
        "meses_cubiertos": meses_cubiertos,
        "meses_recomendados": meses_recomendados,
        "faltante": faltante,
    }


# ============================================================
# DETECTOR ALGORÍTMICO DE GASTOS RECURRENTES / SUSCRIPCIONES
# A diferencia de una lista fija de nombres de apps (Netflix, Spotify...), esto
# encuentra CUALQUIER cargo recurrente en TUS datos reales: agrupa por
# descripción normalizada, exige que aparezca en al menos 2 meses distintos con
# montos similares (±15%), y estima si es mensual consecutivo o irregular.
# Detecta suscripciones que no están en ninguna lista predefinida.
# ============================================================
def detectar_recurrentes(df_tx, gasto_categorias):
    if df_tx.empty:
        return []
    df = df_tx[df_tx["categoria"].isin(gasto_categorias)].copy() if gasto_categorias else df_tx[df_tx["monto"] < 0].copy()
    if df.empty:
        return []
    df["desc_norm"] = df["descripcion"].fillna("").astype(str).str.lower().str.strip()
    df = df[df["desc_norm"] != ""]
    df["mes"] = df["fecha"].dt.to_period("M")
    df["monto_abs"] = df["monto"].abs()

    resultados = []
    for desc, grupo in df.groupby("desc_norm"):
        meses_unicos = grupo["mes"].nunique()
        if meses_unicos < 2:
            continue
        monto_prom = grupo["monto_abs"].mean()
        monto_std = grupo["monto_abs"].std() or 0
        if monto_prom > 0 and (monto_std / monto_prom) > 0.15:
            continue  # montos muy variables: no parece un cargo fijo recurrente
        meses_ordenados = sorted(grupo["mes"].unique())
        consecutivo = all((meses_ordenados[i + 1] - meses_ordenados[i]).n == 1 for i in range(len(meses_ordenados) - 1))
        resultados.append({
            "descripcion": grupo["descripcion"].iloc[-1],
            "categoria": grupo["categoria"].iloc[-1] if "categoria" in grupo.columns else "Otros gastos",
            "monto_promedio": monto_prom,
            "meses_detectados": meses_unicos,
            "consecutivo": consecutivo,
        })
    return sorted(resultados, key=lambda r: r["monto_promedio"], reverse=True)

# ============================================================
# SUPABASE Y GESTIÓN DE USUARIOS
# ============================================================
@st.cache_resource
def init_supabase():
    if not SUPABASE_AVAILABLE:
        return None
    try:
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except Exception:
        return None

supabase = init_supabase()
db_connected = supabase is not None

for key, default in [
    ("user", None),
    ("plan", "free"),
    ("nombre_usuario", ""),
    ("foto_perfil", ""),
    ("intento_restaurar_sesion", False),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ============================================================
# SESIÓN PERSISTENTE — sin esto, st.session_state se borra cada vez que se
# recarga la página (F5), obligando a iniciar sesión de nuevo aunque el login
# siga siendo válido. La cookie guarda el "refresh token" de Supabase (NUNCA la
# contraseña); al recargar, se usa ese token para restaurar la sesión sola.
# ============================================================
NOMBRE_COOKIE_SESION = "finzen_refresh_token"


def get_cookie_manager():
    """Sin @st.cache_resource a propósito: CookieManager crea un widget/componente
    internamente, y Streamlit no permite widgets dentro de funciones cacheadas
    (dispara CachedWidgetWarning y falla). Es liviano, no necesita cachearse."""
    return stx.CookieManager(key="finzen_cookie_manager") if COOKIES_AVAILABLE else None


cookie_manager = get_cookie_manager()


def guardar_sesion_en_cookie(session):
    if cookie_manager and session and getattr(session, "refresh_token", None):
        cookie_manager.set(NOMBRE_COOKIE_SESION, session.refresh_token,
                            expires_at=datetime.now() + timedelta(days=30), key="set_cookie_login")


def borrar_cookie_sesion():
    if cookie_manager:
        try:
            cookie_manager.delete(NOMBRE_COOKIE_SESION, key="del_cookie_login")
        except Exception:
            pass


def restaurar_sesion_desde_cookie():
    """Se ejecuta una sola vez por sesión de navegador. Si hay una cookie con un
    refresh token válido, reconstruye la sesión de Supabase sin pedir contraseña."""
    if not (supabase and cookie_manager) or st.session_state["user"] or st.session_state["intento_restaurar_sesion"]:
        return
    st.session_state["intento_restaurar_sesion"] = True
    refresh_token = cookie_manager.get(NOMBRE_COOKIE_SESION)
    if not refresh_token:
        return
    try:
        res = supabase.auth.refresh_session(refresh_token)
        if res and res.user:
            st.session_state["user"] = res.user.email
            st.session_state["plan"] = get_user_plan(res.user.email)
            if not st.session_state["nombre_usuario"]:
                st.session_state["nombre_usuario"] = res.user.email.split("@")[0].capitalize()
            asegurar_categorias_defecto(res.user.email)
            guardar_sesion_en_cookie(res.session)  # Supabase rota el refresh token: guardar el nuevo
            st.rerun()
    except Exception:
        borrar_cookie_sesion()


def get_user_plan(email):
    if not supabase:
        return "free"
    try:
        res = supabase.table("subscriptions").select("status").eq("user_email", email).execute()
        if res.data:
            return res.data[0].get("status", "free")
        supabase.table("subscriptions").insert({"user_email": email, "status": "free"}).execute()
        return "free"
    except Exception:
        return "free"

def asegurar_categorias_defecto(email):
    if not supabase:
        return
    try:
        existentes = supabase.table("categories").select("name").eq("user_email", email).execute()
        nombres_existentes = {c["name"] for c in (existentes.data or [])}
        faltantes = [
            {"user_email": email, "name": nombre, "tipo": tipo}
            for nombre, tipo in CATEGORIAS_DEFECTO
            if nombre not in nombres_existentes
        ]
        if faltantes:
            supabase.table("categories").insert(faltantes).execute()
    except Exception:
        pass

# ============================================================
# HOGARES Y METAS
# ============================================================
def obtener_hogar(email):
    if not supabase:
        return None
    try:
        membresia = supabase.table("household_members").select("household_id, role").eq("user_email", email).execute()
        if not membresia.data:
            return None
        household_id = membresia.data[0]["household_id"]
        hogar = supabase.table("households").select("*").eq("id", household_id).execute()
        if not hogar.data:
            return None
        miembros = supabase.table("household_members").select("user_email, role").eq("household_id", household_id).execute()
        return {"id": household_id, "nombre": hogar.data[0]["name"], "rol": membresia.data[0]["role"], "miembros": miembros.data or []}
    except Exception:
        return None

def crear_hogar(email, nombre):
    try:
        res = supabase.table("households").insert({"name": nombre, "owner_email": email}).execute()
        household_id = res.data[0]["id"]
        supabase.table("household_members").insert({"household_id": household_id, "user_email": email, "role": "owner"}).execute()
        return True, None
    except Exception as e:
        return False, str(e)

# ============================================================
# CONEXIÓN BANCARIA (Belvo) — todas las llamadas pasan por Edge Functions;
# las credenciales secretas de Belvo NUNCA están en este archivo ni llegan
# al navegador del usuario.
# ============================================================
def _url_funcion(nombre_funcion):
    proyecto_url = st.secrets.get("SUPABASE_URL", "")
    return f"{proyecto_url}/functions/v1/{nombre_funcion}"


def _token_sesion_actual():
    """Token de acceso de la sesión actual, necesario para que las Edge
    Functions verifiquen quién eres de verdad (no lo que el cliente diga)."""
    try:
        sesion = supabase.auth.get_session()
        return sesion.access_token if sesion else None
    except Exception:
        return None


def obtener_conexiones_bancarias(email):
    if not supabase:
        return []
    try:
        res = supabase.table("bank_connections").select("*").eq("user_email", email).execute()
        return res.data or []
    except Exception:
        return []


def belvo_generar_token_widget():
    token = _token_sesion_actual()
    if not token:
        return None, "Sesión no válida, vuelve a iniciar sesión."
    try:
        r = requests.post(_url_funcion("belvo-widget-token"), headers={"Authorization": f"Bearer {token}"}, timeout=15)
        data = r.json()
        if r.status_code != 200:
            return None, data.get("error", "Error desconocido de Belvo.")
        return data, None
    except Exception as e:
        return None, str(e)


def belvo_guardar_link(link_id, institucion):
    token = _token_sesion_actual()
    if not token:
        return False, "Sesión no válida."
    try:
        r = requests.post(_url_funcion("belvo-store-link"), headers={"Authorization": f"Bearer {token}"},
                           json={"link_id": link_id, "institucion": institucion}, timeout=15)
        data = r.json()
        return (r.status_code == 200), data.get("error")
    except Exception as e:
        return False, str(e)


def belvo_sincronizar(link_id):
    token = _token_sesion_actual()
    if not token:
        return None, "Sesión no válida."
    try:
        r = requests.post(_url_funcion("belvo-sync-transactions"), headers={"Authorization": f"Bearer {token}"},
                           json={"link_id": link_id}, timeout=60)
        data = r.json()
        if r.status_code != 200:
            return None, data.get("error", "Error al sincronizar.")
        return data, None
    except Exception as e:
        return None, str(e)

# ============================================================
# CARGA DE DATOS CENTRALIZADA
# ============================================================
@st.cache_data(ttl=60, show_spinner=False)
def cargar_transacciones(email):
    if not supabase:
        return pd.DataFrame(columns=["id", "fecha", "monto", "categoria", "descripcion", "fuente", "user_email", "household_id"])
    try:
        res = supabase.table("transactions").select("*").order("fecha", desc=True).execute()
        cols = ["id", "fecha", "monto", "categoria", "descripcion", "fuente", "user_email", "household_id"]
        df = pd.DataFrame(res.data) if res.data else pd.DataFrame(columns=cols)
        for col in cols:
            if col not in df.columns:
                df[col] = None
        if not df.empty:
            df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
            df["monto"] = pd.to_numeric(df["monto"], errors="coerce").fillna(0)
        return df
    except Exception:
        return pd.DataFrame(columns=["id", "fecha", "monto", "categoria", "descripcion", "fuente", "user_email", "household_id"])

@st.cache_data(ttl=60, show_spinner=False)
def cargar_categorias(email):
    if not supabase:
        return pd.DataFrame(columns=["id", "name", "tipo", "presupuesto_mensual", "user_email", "household_id"])
    try:
        res = supabase.table("categories").select("*").order("name").execute()
        df = pd.DataFrame(res.data) if res.data else pd.DataFrame(columns=["id", "name", "tipo", "presupuesto_mensual", "user_email", "household_id"])
        for col in ["id", "name", "tipo", "presupuesto_mensual", "user_email", "household_id"]:
            if col not in df.columns:
                df[col] = None
        return df
    except Exception:
        return pd.DataFrame(columns=["id", "name", "tipo", "presupuesto_mensual", "user_email", "household_id"])

@st.cache_data(ttl=60, show_spinner=False)
def cargar_metas(email):
    if not supabase:
        return pd.DataFrame(columns=["id", "titulo", "monto_objetivo", "monto_actual", "fecha_objetivo", "user_email"])
    try:
        res = supabase.table("savings_goals").select("*").order("fecha_objetivo").execute()
        df = pd.DataFrame(res.data) if res.data else pd.DataFrame(columns=["id", "titulo", "monto_objetivo", "monto_actual", "fecha_objetivo", "user_email"])
        return df
    except Exception:
        return pd.DataFrame(columns=["id", "titulo", "monto_objetivo", "monto_actual", "fecha_objetivo", "user_email"])

# ============================================================
# SIDEBAR — AUTENTICACIÓN Y PERFIL DE USUARIO
# ============================================================
restaurar_sesion_desde_cookie()

st.sidebar.markdown("### 🌱 FinZen")

if tc_usd_cop:
    st.sidebar.markdown("#### 💱 Moneda")
    moneda_nueva = st.sidebar.radio(
        "Ver importes en",
        ["COP", "USD"],
        index=0 if st.session_state["moneda"] == "COP" else 1,
        horizontal=True,
        label_visibility="collapsed",
    )
    if moneda_nueva != st.session_state["moneda"]:
        st.session_state["moneda"] = moneda_nueva
        st.rerun()
    st.sidebar.caption(f"1 USD ≈ {tc_usd_cop:,.2f} COP")

if not db_connected:
    st.sidebar.warning("⚠️ Sin conexión a base de datos. Configura Supabase en Secrets.")
elif not st.session_state["user"]:
    st.sidebar.markdown("#### Inicia sesión o crea tu cuenta")
    correo = st.sidebar.text_input("Correo")
    clave = st.sidebar.text_input("Contraseña", type="password")
    acepta_terminos = st.sidebar.checkbox("Acepto los Términos y Aviso de Privacidad.")

    c1, c2 = st.sidebar.columns(2)
    with c1:
        if st.button("Entrar", key="login_btn"):
            if correo and clave:
                if supabase:
                    # CORREGIDO: antes había una excepción que dejaba entrar al
                    # admin (CORREO_ADMIN) con CUALQUIER contraseña, sin verificarla
                    # contra Supabase. Ahora TODOS, sin excepción, se autentican de
                    # verdad — incluido el administrador.
                    try:
                        res = supabase.auth.sign_in_with_password({"email": correo, "password": clave})
                        user_obj = res.user if res else None
                        session_obj = res.session if res else None
                    except Exception:
                        user_obj = None
                        session_obj = None

                    if user_obj:
                        st.session_state["user"] = correo
                        st.session_state["plan"] = get_user_plan(correo)
                        if not st.session_state["nombre_usuario"]:
                            st.session_state["nombre_usuario"] = correo.split("@")[0].capitalize()
                        asegurar_categorias_defecto(correo)
                        guardar_sesion_en_cookie(session_obj)
                        st.rerun()
                    else:
                        st.sidebar.error("Credenciales inválidas.")
                else:
                    st.sidebar.error("Sin conexión a base de datos.")
            else:
                st.sidebar.error("Ingresa correo y contraseña.")
    with c2:
        if st.button("Crear cuenta", key="signup_btn"):
            if not acepta_terminos:
                st.sidebar.error("Debes aceptar los Términos.")
            elif correo and clave:
                try:
                    res = supabase.auth.sign_up({"email": correo, "password": clave})
                    if res.user:
                        st.sidebar.success("Cuenta creada. Ahora inicia sesión.")
                    else:
                        st.sidebar.error("Error al registrar.")
                except Exception as e:
                    st.sidebar.error(f"Error: {e}")
            else:
                st.sidebar.error("Ingresa correo y contraseña.")
else:
    if st.session_state["foto_perfil"]:
        st.sidebar.image(st.session_state["foto_perfil"], width=80)

    nombre_actual = st.session_state.get("nombre_usuario") or st.session_state["user"].split("@")[0]
    st.sidebar.markdown(f"### Hola, **{nombre_actual}**")
    st.sidebar.caption(st.session_state["user"])

    if es_administrador():
        badge = '<span class="admin-badge">ADMIN</span>'
    elif st.session_state["plan"] == "pro":
        badge = '<span class="pro-badge">PRO</span>'
    else:
        badge = '<span class="free-badge">GRATIS</span>'

    st.sidebar.markdown(f"Rol: {badge}", unsafe_allow_html=True)

    with st.sidebar.expander("👤 Perfil Profesional y Seguridad"):
        nuevo_nombre = st.text_input("Nombre de visualización", value=st.session_state.get("nombre_usuario", ""))
        nueva_foto = st.text_input("URL de foto de perfil", value=st.session_state.get("foto_perfil", ""))

        st.markdown("---")
        st.markdown("#### Cambiar Contraseña")
        pass_nueva = st.text_input("Nueva contraseña", type="password", key="pass_nue")

        if st.button("Actualizar datos de perfil"):
            st.session_state["nombre_usuario"] = nuevo_nombre
            st.session_state["foto_perfil"] = nueva_foto

            if pass_nueva and supabase:
                try:
                    supabase.auth.update_user({"password": pass_nueva})
                    st.success("Contraseña y perfil actualizados.")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.success("Perfil actualizado con éxito.")
            st.rerun()

    if st.session_state["plan"] != "pro" and not es_administrador():
        st.markdown(
            f"""
<a href="{STRIPE_PAYMENT_LINK}" target="_blank"
style="background:{PINO};color:white;padding:9px 12px;border-radius:10px;
text-decoration:none;font-weight:700;display:block;text-align:center;margin-top:10px;">
✨ Pasar a Pro ($6.99/mes)
</a>
""",
            unsafe_allow_html=True,
        )

    if st.sidebar.button("Cerrar sesión", key="logout_btn"):
        try:
            supabase.auth.sign_out()
        except Exception:
            pass
        borrar_cookie_sesion()
        st.session_state["user"] = None
        st.session_state["plan"] = "free"
        st.session_state["intento_restaurar_sesion"] = False
        st.rerun()

# ============================================================
# CABECERA PRINCIPAL
# ============================================================
nombre_mostrado = st.session_state.get("nombre_usuario") or (st.session_state["user"].split("@")[0].capitalize() if st.session_state["user"] else "")

def obtener_saludo():
    hora = pd.Timestamp.now().hour
    if hora < 12:
        return "Buenos días"
    if hora < 19:
        return "Buenas tardes"
    return "Buenas noches"

st.markdown(
    f"""
<div class="hero-banner">
    <h1>🌱 {obtener_saludo()}{f', {nombre_mostrado}' if nombre_mostrado else ''}</h1>
    <p>Tu centro financiero definitivo — Presupuesto Base Cero, Metas y Control Inteligente.</p>
    <span class="hero-pill">
        💱 Vista actual: {st.session_state["moneda"]} ·
        {"1 USD = " + f"{tasa_usd_cop():,.2f}" + " COP" if tc_usd_cop else "tipo de cambio no disponible"}
    </span>
</div>
""",
    unsafe_allow_html=True,
)

if not st.session_state["user"]:
    st.info("👈 Inicia sesión o crea una cuenta gratis en el panel lateral para comenzar.")
    st.stop()

email = st.session_state["user"]
es_pro = st.session_state["plan"] == "pro" or es_administrador()
hogar = obtener_hogar(email) if supabase else None

# ============================================================
# TABS PRINCIPALES (Con Admin condicional)
# ============================================================
tabs_nombres = [
    "📊 Resumen", "➕ Registrar", "🏦 Conectar Banco", "🌍 Contexto Económico", "🎯 Base Cero", "🎯 Metas", "🔍 Auditoría", "📚 Educación", "🏠 Hogar", "⚖️ Legal"
]
if es_administrador():
    tabs_nombres.append("🛡️ Admin")

tabs = st.tabs(tabs_nombres)
tab1, tab2, tab_banco, tab_macro, tab3, tab4, tab5, tab6, tab7, tab8 = tabs[:10]
tab_admin = tabs[10] if es_administrador() else None

df_tx_todo = cargar_transacciones(email)
df_cat_todo = cargar_categorias(email)
df_metas_todo = cargar_metas(email)

vista_hogar = False
if hogar and es_pro:
    vista_hogar = st.radio("Viendo:", ["Solo yo", f"Todo el hogar ({hogar['nombre']})"], horizontal=True) != "Solo yo"

if vista_hogar:
    df_tx = df_tx_todo[df_tx_todo["household_id"] == hogar["id"]] if not df_tx_todo.empty else df_tx_todo
    df_cat = df_cat_todo[df_cat_todo["household_id"] == hogar["id"]] if not df_cat_todo.empty else df_cat_todo
else:
    df_tx = df_tx_todo[df_tx_todo["user_email"] == email] if not df_tx_todo.empty else df_tx_todo
    if not df_cat_todo.empty:
        household_col = df_cat_todo["household_id"]
        df_cat = df_cat_todo[(df_cat_todo["user_email"] == email) & (household_col.isna() | (household_col.astype(str) == "None") | (household_col.astype(str) == ""))]
    else:
        df_cat = df_cat_todo

df_metas = df_metas_todo[df_metas_todo["user_email"] == email] if not df_metas_todo.empty else df_metas_todo

# ============================================================
# TAB 1: RESUMEN Y SEMÁFORO DE DINERO LIBRE
# ============================================================
with tab1:
    st.subheader("Tu mes de un vistazo")
    hoy = pd.Timestamp.today()
    if df_tx.empty:
        st.info("Aún no tienes movimientos registrados.")
    else:
        df_tx = df_tx.copy()
        df_tx["mes"] = df_tx["fecha"].dt.to_period("M")
        mes_actual = hoy.to_period("M")
        df_mes = df_tx[df_tx["mes"] == mes_actual]

        gasto_categorias = set(df_cat[df_cat["tipo"] == "gasto"]["name"]) if not df_cat.empty else set()
        ingreso_categorias = set(df_cat[df_cat["tipo"] == "ingreso"]["name"]) if not df_cat.empty else set()

        gasto_mask = df_mes["categoria"].isin(gasto_categorias) if gasto_categorias else df_mes["monto"] < 0
        ingreso_mask = df_mes["categoria"].isin(ingreso_categorias) if ingreso_categorias else df_mes["monto"] > 0

        total_gasto = -df_mes.loc[gasto_mask, "monto"].sum() if not df_mes.empty else 0
        total_ingreso = df_mes.loc[ingreso_mask, "monto"].sum() if not df_mes.empty else 0
        balance = total_ingreso - total_gasto

        m1, m2, m3 = st.columns(3)
        m1.metric("Ingresos del mes", dinero(total_ingreso))
        m2.metric("Gastos del mes", dinero(total_gasto))
        m3.metric("Balance", dinero(balance), delta="Positivo" if balance >= 0 else "Negativo", delta_color="normal" if balance >= 0 else "inverse")

        # ── SEMÁFORO DE DINERO LIBRE PARA GASTAR ──
        presupuesto_total_asignado = df_cat[df_cat["tipo"] == "gasto"]["presupuesto_mensual"].sum() if not df_cat.empty else 0
        dinero_libre_real = max(0, total_ingreso - total_gasto - presupuesto_total_asignado)

        st.markdown("---")
        st.markdown("#### 🟢 Semáforo de Dinero Disponible Real")
        col_lib1, col_lib2 = st.columns([2, 1])
        col_lib1.info(f"💡 Te quedan **{dinero_md(dinero_libre_real)}** libres este mes tras cubrir tus gastos y metas presupuestadas.")
        col_lib2.metric("Dinero libre real", dinero(dinero_libre_real))

        tasa_ahorro = balance / total_ingreso if total_ingreso > 0 else 0
        puntaje_salud = round(min(100, max(0, min(max(tasa_ahorro, 0), 1) * 60 + 40)))

        col_gauge, col_dona = st.columns([0.9, 1.45])
        with col_gauge:
            st.markdown("#### 💚 Salud financiera")
            st.plotly_chart(grafico_salud_financiera(puntaje_salud), use_container_width=True, config={"displayModeBar": False})
        with col_dona:
            st.markdown("#### Gasto por categoría este mes")
            gastos_mes = df_mes[gasto_mask].groupby("categoria")["monto"].sum().abs().sort_values(ascending=False) if not df_mes.empty else pd.Series()
            if not gastos_mes.empty:
                colores = [PALETA_CATEGORIAS[i % len(PALETA_CATEGORIAS)] for i in range(len(gastos_mes))]
                fig = go.Figure(go.Pie(
                    labels=gastos_mes.index,
                    values=[a_moneda(v) for v in gastos_mes.values],
                    hole=0.58,
                    marker=dict(colors=colores, line=dict(color=TARJETA, width=2)),
                    textinfo="percent",
                ))
                fig = estilo_grafico(fig, height=320)
                fig.update_layout(showlegend=False)
                fig.add_annotation(text=f"{dinero(gastos_mes.sum())}<br><span style='font-size:11px;color:{TEXTO_SUAVE}'>total</span>", showarrow=False, font=dict(size=16, color=TEXTO))
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ============================================================
# TAB 2: REGISTRAR MOVIMIENTO
# ============================================================
with tab2:
    st.subheader("Registrar un movimiento")
    with st.form("form_transaccion", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            fecha_tx = st.date_input("Fecha", value=date.today())
            tipo_tx = st.radio("Tipo", ["Gasto", "Ingreso"], horizontal=True)
        with c2:
            monto_tx = st.number_input(f"Monto ({st.session_state['moneda']})", min_value=0.0, step=10.0)
            descripcion_tx = st.text_input("Descripción", placeholder="Ej: supermercado, Uber, Netflix")

        tipo_categoria = "gasto" if tipo_tx == "Gasto" else "ingreso"
        categorias_disponibles = df_cat[df_cat["tipo"] == tipo_categoria]["name"].tolist() if not df_cat.empty else []
        sugerida = auto_categorizar(descripcion_tx) if tipo_tx == "Gasto" else "Salario"
        indice_sugerido = categorias_disponibles.index(sugerida) if sugerida in categorias_disponibles else 0

        categoria_tx = st.selectbox("Categoría", categorias_disponibles or ["Otros gastos"], index=indice_sugerido)
        compartir_tx = False
        if hogar and es_pro:
            compartir_tx = st.checkbox(f"Compartir con mi hogar ({hogar['nombre']})")

        guardar = st.form_submit_button("Guardar movimiento")

    if guardar:
        if not supabase:
            st.error("Sin conexión a base de datos.")
        elif monto_tx <= 0:
            st.error("El monto debe ser mayor que 0.")
        else:
            monto_cop = a_cop(monto_tx)
            signo = -1 if tipo_tx == "Gasto" else 1
            registro = {
                "user_email": email,
                "fecha": fecha_tx.isoformat(),
                "monto": signo * monto_cop,
                "categoria": categoria_tx,
                "descripcion": descripcion_tx,
                "fuente": "manual",
            }
            if compartir_tx and hogar:
                registro["household_id"] = hogar["id"]
            try:
                supabase.table("transactions").insert(registro).execute()
                st.success("Movimiento guardado con éxito.")
                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.error(f"Error al guardar: {e}")

# ============================================================
# TAB 3: PRESUPUESTO BASE CERO Y CATEGORÍAS
# ============================================================
with tab_banco:
    st.subheader("🏦 Conectar Banco")
    st.info("🧪 Modo **sandbox** (datos de prueba de Belvo, no tu banco real todavía). Activar producción real es una decisión de negocio aparte — cuesta desde ~$1.000 USD/mes según el plan público de Belvo.")

    if not es_pro:
        st.info("✨ La conexión bancaria automática está en el plan Pro.")
    else:
        conexiones = obtener_conexiones_bancarias(email)

        if conexiones:
            st.markdown("#### Bancos conectados")
            for c in conexiones:
                col_a, col_b, col_c = st.columns([2, 1.3, 1])
                col_a.write(f"🏦 **{c.get('institucion', 'Banco')}**")
                ultima = c.get("ultima_sincronizacion")
                col_b.caption(f"Última sync: {ultima[:16] if ultima else 'nunca'}")
                if col_c.button("🔄 Sincronizar", key=f"sync_{c['id']}"):
                    with st.spinner("Trayendo movimientos..."):
                        resultado, err = belvo_sincronizar(c["belvo_link_id"])
                    if resultado:
                        st.success(f"{resultado['nuevas_insertadas']} movimientos nuevos importados (de {resultado['total_encontradas']} encontrados).")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(f"No se pudo sincronizar: {err}")
            st.divider()

        st.markdown("#### ➕ Conectar un banco nuevo")
        token_widget, err_token = belvo_generar_token_widget()

        if err_token:
            st.error(f"No se pudo preparar la conexión: {err_token}")
            st.caption("Revisa que BELVO_SECRET_ID y BELVO_SECRET_PASSWORD estén configurados como secrets en Supabase (Edge Functions → Secrets).")
        elif token_widget:
            components.html(
                f"""
                <div id="belvo-container"></div>
                <script src="https://cdn.belvo.io/belvo-widget-1-stable.js"></script>
                <script>
                belvoSDK.createWidget("{token_widget['access_token']}", {{
                    locale: "es",
                    country_codes: ["CO"],
                    callback: function(link, institution) {{
                        fetch("{_url_funcion('belvo-store-link')}", {{
                            method: "POST",
                            headers: {{
                                "Content-Type": "application/json",
                                "Authorization": "Bearer {_token_sesion_actual()}"
                            }},
                            body: JSON.stringify({{ link_id: link, institucion: institution }})
                        }}).then(function() {{
                            document.getElementById("belvo-container").innerHTML =
                                "<p style='color:#1F4D3D;font-weight:600;'>✅ Banco conectado. Cierra esta ventana y recarga la página para verlo en tu lista.</p>";
                        }});
                    }},
                    onExit: function() {{}},
                }}).build();
                </script>
                """,
                height=520,
            )
            st.caption("Se abre el widget oficial de Belvo. En sandbox, usa cualquier banco de la lista con credenciales de prueba (Belvo las muestra en pantalla).")

with tab_macro:
    st.subheader("🌍 Contexto Económico")
    st.info("A diferencia de tu presupuesto (que mide TU dinero), esto mide el contexto de la economía real usando 3 modelos públicos, académicamente validados. Es información educativa — **no es asesoría de inversión ni una predicción garantizada**. Ningún competidor de presupuesto personal (Monarch, YNAB, Copilot, Rocket Money) ofrece esto.")

    señales, detalle_señales = cargar_contexto_economico()

    if not detalle_señales:
        st.warning("No se pudo obtener el contexto económico en este momento (falla temporal al conectar con FRED). Intenta de nuevo más tarde.")
    else:
        st.metric("Señales de recesión activas ahora mismo", f"{señales} / {len(detalle_señales)}")
        st.caption("Solo es un conteo de cuántos modelos están en zona de alerta — no es una probabilidad combinada ni un índice nuevo. Cada modelo mide algo distinto (bonos, empleo, actividad real) y tiene su propio historial de aciertos y fallos.")

        cols_macro = st.columns(len(detalle_señales))
        for col, (nombre, valor, activo, texto) in zip(cols_macro, detalle_señales):
            col.markdown(f"**{'🔴' if activo else '🟢'} {nombre}**")
            col.caption(texto)

        st.warning("⚠️ Ningún modelo de recesión es infalible. El NY Fed puede anticipar con años de rezago variable; la Sahm confirma después de que la recesión ya empezó; el coincidente se revisa con el tiempo. Esto no reemplaza el consejo de un asesor financiero certificado.")

        st.divider()
        st.markdown("### 💰 Qué significa esto para TU fondo de emergencia")
        st.caption("Esta es la parte que ningún competidor hace: conectar la señal macro con tu situación real, no solo mostrarte un número abstracto.")

        if df_tx.empty:
            st.caption("Registra al menos un mes de movimientos para calcular tu gasto mensual promedio.")
        else:
            df_tx_macro = df_tx.copy()
            df_tx_macro["mes"] = df_tx_macro["fecha"].dt.to_period("M")
            gasto_cat_macro = set(df_cat[df_cat["tipo"] == "gasto"]["name"]) if not df_cat.empty else set()
            gm_mask = df_tx_macro["categoria"].isin(gasto_cat_macro) if gasto_cat_macro else df_tx_macro["monto"] < 0
            gasto_por_mes = df_tx_macro[gm_mask].groupby("mes")["monto"].sum().abs()
            gasto_mensual_promedio = gasto_por_mes.mean() if not gasto_por_mes.empty else 0

            col_ahorro1, col_ahorro2 = st.columns([1, 1.3])
            with col_ahorro1:
                ahorro_actual = st.number_input(f"¿Cuánto tienes hoy en tu fondo de emergencia? ({st.session_state['moneda']})", min_value=0.0, step=100.0, key="fondo_emergencia_input")
            ahorro_actual_cop = a_cop(ahorro_actual)

            resultado = recomendacion_fondo_emergencia(señales, gasto_mensual_promedio, ahorro_actual_cop)
            with col_ahorro2:
                if resultado and gasto_mensual_promedio > 0:
                    st.metric("Meses de gastos que cubres hoy", f"{resultado['meses_cubiertos']:.1f}")
                    if resultado["faltante"] > 0:
                        st.markdown(f"Con **{señales} de {len(detalle_señales)}** señales activas, la referencia recomendada ahora es de **{resultado['meses_recomendados']} meses** de gastos guardados. Te faltarían aproximadamente {dinero_md(resultado['faltante'])} para llegar a eso.")
                    else:
                        st.success(f"Ya cubres los {resultado['meses_recomendados']} meses de referencia para el contexto actual. 🎉")
                else:
                    st.caption("Ingresa tu ahorro actual y registra gastos para ver el cálculo.")
            st.caption("La cifra de 'meses recomendados' es una referencia educativa común (3-6 meses de gastos), ajustada levemente según cuántas señales macro estén activas — no es una fórmula validada científicamente, es un punto de partida razonable para pensar el tema.")

with tab3:
    st.subheader("🎯 Presupuesto Base Cero y Gestión de Categorías")
    st.markdown("La premisa: **Ingresos Totales - Ahorros - Gastos Asignados = 0**. Cada unidad de dinero tiene un propósito.")

    if not es_pro:
        st.info("✨ El Presupuesto Base Cero y gestión avanzada están en el plan Pro.")
    else:
        st.markdown("#### Configurar Presupuestos Mensuales")
        if df_cat.empty:
            st.caption("No tienes categorías creadas.")
        else:
            total_presupuestado = 0.0
            for _, fila in df_cat[df_cat["tipo"] == "gasto"].iterrows():
                col1, col2, col3 = st.columns([2, 1, 0.8])
                col1.write(f"{icono_categoria(fila['name'])} **{fila['name']}**")

                valor_base = float(fila["presupuesto_mensual"]) if pd.notna(fila["presupuesto_mensual"]) else 0.0
                total_presupuestado += valor_base

                # CORREGIDO: antes se comparaba el redondeo COP->moneda->COP contra
                # el valor guardado, y una simple fluctuación del tipo de cambio (o
                # el redondeo mismo) podía disparar una escritura en la base de datos
                # sin que el usuario tocara nada. Ahora se compara en el MISMO
                # espacio de unidades que ve el usuario (moneda mostrada), antes de
                # convertir — solo una edición real genera una diferencia.
                valor_mostrado_actual = float(round(a_moneda(valor_base), 2))
                nuevo_valor = col2.number_input(
                    f"Presupuesto {fila['name']}",
                    min_value=0.0,
                    step=50.0,
                    value=valor_mostrado_actual,
                    key=f"presu_{fila['id']}",
                    label_visibility="collapsed",
                )

                if col3.button("🗑️", key=f"del_cat_{fila['id']}"):
                    try:
                        supabase.table("categories").delete().eq("id", fila["id"]).execute()
                        st.success("Categoría eliminada.")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

                if abs(nuevo_valor - valor_mostrado_actual) > 0.001:
                    nuevo_base = a_cop(nuevo_valor)
                    try:
                        supabase.table("categories").update({"presupuesto_mensual": nuevo_base}).eq("id", fila["id"]).execute()
                        st.cache_data.clear()
                    except Exception as e:
                        st.error(f"Error: {e}")

            st.markdown(f"**Total asignado a gastos:** {dinero(total_presupuestado)}")

        st.divider()
        st.markdown("#### ➕ Crear nueva categoría de gasto")
        nueva_cat = st.text_input("Nombre de la nueva categoría")
        if st.button("Guardar nueva categoría", key="btn_crear_cat") and nueva_cat.strip():
            try:
                supabase.table("categories").insert({
                    "user_email": email,
                    "name": nueva_cat.strip(),
                    "tipo": "gasto",
                    "presupuesto_mensual": 0.0
                }).execute()
                st.success(f"Categoría '{nueva_cat.strip()}' creada.")
                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

# ============================================================
# TAB 4: METAS DE AHORRO CON GAMIFICATION Y PROYECCIONES
# ============================================================
with tab4:
    st.subheader("🎯 Metas de Ahorro y Proyecciones")
    st.markdown("Define tus propósitos (Viajes, Fondo de Emergencia, Inversiones) y visualiza exactamente cuándo los cumplirás.")

    if not es_pro:
        st.info("✨ Las metas de ahorro inteligentes están disponibles en el plan Pro.")
    else:
        col_mg1, col_mg2 = st.columns([1.2, 1])
        with col_mg1:
            st.markdown("#### Tus Metas Activas")
            if df_metas.empty:
                st.info("Aún no has creado metas de ahorro.")
            else:
                for _, meta in df_metas.iterrows():
                    actual = float(meta["monto_actual"] or 0)
                    objetivo = float(meta["monto_objetivo"] or 1)
                    progreso = min(1.0, actual / objetivo)
                    porcentaje = progreso * 100

                    # CORREGIDO: dos montos (dinero()) en la misma línea de
                    # st.markdown disparaban el modo LaTeX de Streamlit (ver
                    # comentario en dinero_md). Se usa la versión escapada.
                    st.markdown(f"**{meta['titulo']}** — {dinero_md(actual)} / {dinero_md(objetivo)} ({porcentaje:.1f}%)")
                    st.progress(progreso)

                    # Botón para abonar
                    c_abonar1, c_abonar2 = st.columns([1, 1])
                    abono_val = c_abonar1.number_input(f"Abonar a {meta['id']}", min_value=0.0, step=10.0, key=f"abono_input_{meta['id']}", label_visibility="collapsed")
                    if c_abonar2.button("Abonar", key=f"btn_abono_{meta['id']}"):
                        nuevo_actual = actual + a_cop(abono_val)
                        try:
                            supabase.table("savings_goals").update({"monto_actual": nuevo_actual}).eq("id", meta["id"]).execute()
                            st.success("¡Abono registrado con éxito!")
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                    st.markdown("---")

        with col_mg2:
            st.markdown("#### ➕ Crear Nueva Meta")
            with st.form("form_meta", clear_on_submit=True):
                titulo_meta = st.text_input("Nombre de la meta", placeholder="Ej: Viaje a Europa")
                objetivo_meta = st.number_input(f"Monto objetivo ({st.session_state['moneda']})", min_value=0.0, step=100.0)
                fecha_meta = st.date_input("Fecha objetivo", value=date.today())
                crear_meta_btn = st.form_submit_button("Crear meta")

            if crear_meta_btn:
                if titulo_meta and objetivo_meta > 0:
                    try:
                        supabase.table("savings_goals").insert({
                            "user_email": email,
                            "titulo": titulo_meta,
                            "monto_objetivo": a_cop(objetivo_meta),
                            "monto_actual": 0.0,
                            "fecha_objetivo": fecha_meta.isoformat()
                        }).execute()
                        st.success("Meta creada con éxito.")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.error("Completa todos los campos correctamente.")

# ============================================================
# TAB 5: AUDITORÍA DE GASTOS HORMIGA Y SUSCRIPCIONES
# ============================================================
with tab5:
    st.subheader("🔍 Auditoría Inteligente de Gastos Hormiga y Suscripciones")
    st.caption("Detecta patrones reales en tus propios movimientos — no una lista fija de apps famosas. Cualquier cargo que se repita en 2+ meses con monto parecido cuenta, aunque sea un servicio que nadie más conoce.")

    if df_tx.empty:
        st.info("Registra transacciones para activar la auditoría.")
    else:
        gasto_cat_audit = set(df_cat[df_cat["tipo"] == "gasto"]["name"]) if not df_cat.empty else set()
        recurrentes = detectar_recurrentes(df_tx, gasto_cat_audit)

        st.markdown("#### 📱 Cargos recurrentes detectados")
        if not recurrentes:
            st.success("✅ No se detectaron cargos recurrentes todavía (hace falta historial de al menos 2 meses por concepto).")
        else:
            total_recurrente = sum(r["monto_promedio"] for r in recurrentes)
            st.warning(f"⚠️ Encontramos **{len(recurrentes)}** cargos recurrentes que suman ~**{dinero_md(total_recurrente)}**/mes. ¿Usas todos activamente?")
            for r in recurrentes:
                etiqueta = "mensual" if r["consecutivo"] else "irregular"
                st.markdown(f"{icono_categoria(r['categoria'])} **{r['descripcion']}** — ~{dinero(r['monto_promedio'])}/mes · visto en {r['meses_detectados']} meses ({etiqueta})")

        st.divider()
        st.markdown("#### ☕ Análisis de Gastos Hormiga")
        st.caption("Complemento por palabras clave — microcompras que suelen pasar desapercibidas aunque no sean recurrentes en el mismo concepto exacto.")
        df_tx_audit = df_tx.copy()
        mask_hormiga = df_tx_audit["descripcion"].astype(str).str.lower().apply(lambda x: any(p in x for p in ["cafe", "café", "snacks", "uber", "didi", "rappi"]))
        df_hormigas = df_tx_audit[mask_hormiga]
        if not df_hormigas.empty:
            total_hormigas = df_hormigas["monto"].abs().sum()
            st.info(f"💡 Tus microcompras en cafeterías, transporte exprés o plataformas de entrega suman **{dinero_md(total_hormigas)}** este periodo.")
        else:
            st.caption("Sin microcompras detectadas por palabra clave todavía.")

# ============================================================
# TAB 6: EDUCACIÓN FINANCIERA (SPOTIFY WRAPPED Y CONSEJOS)
# ============================================================
with tab6:
    st.subheader("📚 Educación y Reporte Spotify Wrapped Financiero")
    st.caption("Resumen narrativo y principios clave para transformar tu relación con el dinero.")

    st.markdown("#### 📊 Tu Wrapped Financiero del Mes")
    hoy = pd.Timestamp.today()
    if not df_tx.empty:
        df_t_wrap = df_tx.copy()
        df_t_wrap["mes"] = df_t_wrap["fecha"].dt.to_period("M")
        df_mes_wrap = df_t_wrap[df_t_wrap["mes"] == hoy.to_period("M")]

        gasto_cat_w = set(df_cat[df_cat["tipo"] == "gasto"]["name"]) if not df_cat.empty else set()
        gw_mask = df_mes_wrap["categoria"].isin(gasto_cat_w) if gasto_cat_w else df_mes_wrap["monto"] < 0

        if not df_mes_wrap[gw_mask].empty:
            gasto_por_c = df_mes_wrap[gw_mask].groupby("categoria")["monto"].sum().abs()
            cat_reina = gasto_por_c.idxmax()
            monto_reina = gasto_por_c.max()

            st.markdown(
                f"""
                <div class="consejo-card consejo-bueno">
                    <b>🎵 FinZen Wrapped: Tus hábitos al desnudo</b><br>
                    • Tu categoría reina este mes fue <b>{cat_reina}</b> con un consumo de <b>{dinero(monto_reina)}</b>.<br>
                    • ¡Mantén la disciplina! Registrar tus movimientos eleva un 40% tu capacidad de ahorro a largo plazo.
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.info("Registra gastos este mes para desbloquear tu Wrapped financiero personalizado.")

    st.divider()
    st.markdown("#### 📖 Conceptos Clave")
    conceptos = [
        ("Regla 50/30/20", "50% necesidades básicas, 30% deseos/estilo de vida, 20% ahorro e inversión."),
        ("Fondo de Emergencia", "Colchón intocable de 3 a 6 meses de gastos esenciales ante imprevistos."),
        ("Interés Compuesto", "El crecimiento exponencial del dinero cuando los rendimientos se reinvierten con el tiempo."),
        ("Presupuesto Base Cero", "Asignar un propósito exacto a cada unidad monetaria que ingresa (Ingresos - Gastos - Ahorros = 0).")
    ]
    for titulo, texto in conceptos:
        with st.expander(titulo):
            st.write(texto)

# ============================================================
# TAB 7: MI HOGAR
# ============================================================
with tab7:
    st.subheader("🏠 Mi Hogar (Finanzas Compartidas)")
    if not es_pro:
        st.info("✨ Los hogares compartidos están disponibles en el plan Pro.")
    elif not hogar:
        st.markdown("#### Crea un espacio compartido")
        nombre_hogar = st.text_input("Nombre del hogar", placeholder="Ej: Familia Pérez")
        if st.button("Crear hogar") and nombre_hogar.strip():
            ok, err = crear_hogar(email, nombre_hogar.strip())
            if ok:
                st.success("Hogar creado con éxito.")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error(f"Error: {err}")
    else:
        st.markdown(f"#### {hogar['nombre']}")
        st.write("**Miembros actuales:**")
        for m in hogar["miembros"]:
            st.write(f"- {m['user_email']} ({'Dueño' if m['role']=='owner' else 'Miembro'})")

# ============================================================
# TAB 8: LEGAL
# ============================================================
with tab8:
    st.subheader("⚖️ Legal y Privacidad")
    with st.expander("📄 Términos de Servicio"):
        st.markdown(f"**Última actualización:** {date.today().strftime('%d/%m/%Y')}\n\nFinZen es una herramienta de organización financiera personal sin carácter de asesoría de inversión profesional.")
    with st.expander("🔒 Aviso de Privacidad"):
        st.markdown("Tus datos están protegidos. Contáctanos en: **minatobrasil6@gmail.com**")

# ============================================================
# PANEL DE ADMINISTRADOR (EXCLUSIVO minatobrasil6@gmail.com)
# La verificación real de identidad ocurre al iniciar sesión (Supabase Auth) —
# es_administrador() solo decide qué se MUESTRA, no otorga acceso a datos por
# sí sola. El acceso real a los datos de otros usuarios lo controla el RLS de
# la base de datos (políticas corregidas por separado).
# ============================================================
if es_administrador() and tab_admin is not None:
    with tab_admin:
        st.subheader("🛡️ Panel de Control de Administrador")
        st.markdown(f"Bienvenido, administrador **{CORREO_ADMIN}**.")
        col_a, col_b = st.columns(2)
        col_a.metric("Base de Datos", "Conectada" if db_connected else "Modo Demo")
        col_b.metric("Tasa de Cambio", f"1 USD = {tasa_usd_cop():,.2f} COP")

        st.divider()
        if st.button("Limpiar caché de la aplicación"):
            st.cache_data.clear()
            st.success("Caché limpiada correctamente.")

# ============================================================
# PIE DE PÁGINA
# ============================================================
st.divider()
st.caption(f"🌱 FinZen · Moneda activa: {st.session_state['moneda']}")
