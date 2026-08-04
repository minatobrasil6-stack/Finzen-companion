import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io
import re
import math
from datetime import date

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

st.set_page_config(page_title="FinZen | Tu compañero de finanzas", layout="wide", page_icon="🌱")

# ============================================================
# SISTEMA DE DISEÑO — FinZen
# Distinto a propósito del motor de riesgo Q-FSI: esto es un producto de
# consumo masivo, no una terminal institucional. Paleta cálida, tono cercano,
# tipografía redondeada. El trabajo emocional es "calma y control sin culpa",
# no "gravedad de mercado" — pero calma no significa aburrido: hay color,
# movimiento sutil y jerarquía visual clara.
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

# Paleta cualitativa para gráficas de categorías — coordinada pero variada,
# para que el desglose se sienta vivo en vez de un solo tono monocromático.
PALETA_CATEGORIAS = [PINO, CORAL, GOLD, CIELO, SALVIA, CIRUELA, LADRILLO, "#3D6B7D"]

ICONOS_CATEGORIA = {
    "Supermercado": "🛒", "Restaurantes": "🍽️", "Transporte": "🚗", "Suscripciones": "📱",
    "Vivienda": "🏠", "Salud": "💊", "Entretenimiento": "🎬", "Otros gastos": "📦",
    "Salario": "💰", "Otros ingresos": "➕",
}


def icono_categoria(nombre):
    return ICONOS_CATEGORIA.get(nombre, "🏷️")


st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@500;600;700;800&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500;600&display=swap');

    html, body, .stApp {{ background-color: {PAPEL} !important; color: {TEXTO}; font-family: 'Inter', sans-serif; }}
    #MainMenu, footer, header {{ visibility: hidden; }}
    h1, h2, h3 {{ font-family: 'Quicksand', sans-serif !important; font-weight: 700 !important; color: {PINO} !important; }}

    @keyframes fadeInUp {{ from {{ opacity: 0; transform: translateY(6px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; transition: none !important; }} }}

    .hero-banner {{
        background: linear-gradient(135deg, {PINO} 0%, {PINO_CLARO} 55%, {CIELO} 130%);
        border-radius: 22px; padding: 28px 30px; margin-bottom: 22px; color: white;
        box-shadow: 0 8px 24px rgba(31,77,61,0.18); animation: fadeInUp 0.4s ease;
    }}
    .hero-banner h1 {{ color: white !important; margin: 0 0 4px 0; font-size: 28px !important; }}
    .hero-banner p {{ color: rgba(255,255,255,0.88) !important; margin: 0; font-size: 14.5px; }}
    .hero-pill {{ display:inline-block; background: rgba(255,255,255,0.16); border: 1px solid rgba(255,255,255,0.3);
        border-radius: 20px; padding: 4px 12px; font-size: 12px; font-weight: 600; margin-top: 10px; }}

    div[data-testid="stMetric"] {{
        background: {TARJETA}; border: 1px solid {BORDE}; border-radius: 16px; padding: 16px 18px;
        box-shadow: 0 2px 8px rgba(43,38,32,0.05); transition: transform 0.15s ease, box-shadow 0.15s ease;
    }}
    div[data-testid="stMetric"]:hover {{ transform: translateY(-3px); box-shadow: 0 8px 20px rgba(43,38,32,0.10); }}
    div[data-testid="stMetricLabel"] {{ font-family: 'Inter', sans-serif; font-size: 12.5px !important; color: {TEXTO_SUAVE} !important; text-transform: uppercase; letter-spacing: 0.03em; }}
    div[data-testid="stMetricValue"] {{ font-family: 'JetBrains Mono', monospace !important; color: {TEXTO} !important; font-weight: 600 !important; }}

    button[data-baseweb="tab"] {{ font-family: 'Quicksand', sans-serif; font-weight: 600; color: {TEXTO_SUAVE}; border-radius: 10px 10px 0 0; }}
    button[data-baseweb="tab"][aria-selected="true"] {{ color: {PINO} !important; border-bottom: 3px solid {PINO} !important; background: {ARENA}; }}
    div[data-baseweb="tab-highlight"] {{ background-color: {PINO} !important; }}

    .stButton > button {{
        background: linear-gradient(135deg, {PINO}, {PINO_CLARO}); color: white; border: none; border-radius: 12px;
        font-weight: 700; padding: 0.55rem 1.2rem; box-shadow: 0 3px 10px rgba(31,77,61,0.22);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }}
    .stButton > button:hover {{ transform: translateY(-2px); box-shadow: 0 6px 16px rgba(31,77,61,0.3); color: white; }}
    .stDownloadButton > button {{ background: linear-gradient(135deg, {SALVIA}, {PINO_CLARO}); color: white; border-radius: 12px; font-weight: 700; border: none; }}

    .stTextInput input, .stNumberInput input, .stDateInput input, div[data-baseweb="select"] > div {{
        background-color: {TARJETA} !important; border: 1px solid {BORDE} !important; border-radius: 10px !important; color: {TEXTO} !important;
    }}
    div[data-testid="stExpander"] {{ background-color: {TARJETA}; border: 1px solid {BORDE}; border-radius: 16px; box-shadow: 0 2px 6px rgba(43,38,32,0.04); }}
    section[data-testid="stSidebar"] {{ background-color: {ARENA}; border-right: 1px solid {BORDE}; }}
    div[data-testid="stAlert"] {{ background-color: {TARJETA} !important; border: 1px solid {BORDE} !important; border-left: 4px solid {PINO} !important; border-radius: 12px !important; }}
    hr {{ border-color: {BORDE} !important; }}

    .pro-badge {{ background: linear-gradient(135deg, {GOLD}, {CORAL}); color: white; padding: 4px 12px; border-radius: 20px; font-weight: 700; font-size: 11px; letter-spacing: 0.03em; }}
    .free-badge {{ background-color: {BORDE}; color: {TEXTO}; padding: 4px 12px; border-radius: 20px; font-weight: 700; font-size: 11px; }}
    .insight-card {{ background: {TARJETA}; border: 1px solid {BORDE}; border-left: 4px solid {PINO}; border-radius: 14px; padding: 14px 16px; margin-bottom: 10px; animation: fadeInUp 0.35s ease; box-shadow: 0 2px 6px rgba(43,38,32,0.04); }}
    .insight-alerta {{ border-left: 4px solid {CORAL} !important; }}
    .insight-buena {{ border-left: 4px solid {SALVIA} !important; }}

    .cat-chip {{ display:inline-flex; align-items:center; gap:7px; background: {ARENA}; padding:5px 13px; border-radius:20px; font-size:13.5px; font-weight:600; color:{TEXTO}; margin: 3px 4px 3px 0; }}

    ::-webkit-scrollbar {{ width: 10px; height: 10px; }}
    ::-webkit-scrollbar-thumb {{ background: {BORDE}; border-radius: 10px; }}
    ::-webkit-scrollbar-track {{ background: {PAPEL}; }}
</style>
""", unsafe_allow_html=True)


def estilo_grafico(fig, titulo=None, height=360):
    fig.update_layout(
        template="plotly_white", height=height, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=TEXTO_SUAVE, size=12),
        title=dict(text=titulo, font=dict(family="Quicksand, sans-serif", color=PINO, size=17)) if titulo else None,
        margin=dict(l=20, r=20, t=48 if titulo else 20, b=20),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXTO_SUAVE, size=11)),
        xaxis=dict(gridcolor=BORDE, zerolinecolor=BORDE), yaxis=dict(gridcolor=BORDE, zerolinecolor=BORDE),
    )
    return fig


def grafico_salud_financiera(puntaje):
    """Gauge visual de 'salud financiera' — síntesis de un vistazo, mucho más
    atractivo que otra fila de números. 0-100: rojo/coral si va mal, dorado si
    va regular, verde pino si va bien."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=puntaje, number={"suffix": "", "font": {"size": 40, "family": "JetBrains Mono", "color": TEXTO}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 0, "tickcolor": BORDE},
            "bar": {"color": PINO, "thickness": 0.3},
            "bgcolor": "rgba(0,0,0,0)", "borderwidth": 0,
            "steps": [
                {"range": [0, 40], "color": "rgba(232,115,74,0.18)"},
                {"range": [40, 70], "color": "rgba(217,164,65,0.18)"},
                {"range": [70, 100], "color": "rgba(127,182,158,0.25)"},
            ],
        },
    ))
    fig.update_layout(height=200, margin=dict(l=20, r=20, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)",
                       font=dict(family="Inter, sans-serif", color=TEXTO_SUAVE))
    return fig


def generar_resumen_narrado(total_ingreso, total_gasto, balance, tasa_ahorro, tasa_ahorro_ant,
                             comp_actual, comp_anterior, categoria_top):
    """Narra los números del mes en 2-3 frases, en español simple. Todo lo que
    dice sale directo de los datos reales del usuario — no interpreta causas
    ('gastaste más porque...'), no da consejos, solo describe lo que pasó."""
    frases = []

    if total_ingreso == 0 and total_gasto == 0:
        return "Todavía no hay suficientes movimientos este mes para armar un resumen."

    frases.append(f"Este mes llevas ${total_ingreso:,.0f} de ingresos y ${total_gasto:,.0f} de gastos, "
                   f"con un balance {'positivo' if balance >= 0 else 'negativo'} de ${abs(balance):,.0f}.")

    if tasa_ahorro_ant is not None and total_ingreso > 0:
        diferencia_pp = (tasa_ahorro - tasa_ahorro_ant) * 100
        if abs(diferencia_pp) >= 3:
            direccion = "subió" if diferencia_pp > 0 else "bajó"
            frases.append(f"Tu tasa de ahorro {direccion} de {tasa_ahorro_ant*100:.0f}% a {tasa_ahorro*100:.0f}% respecto al mes pasado.")

    if categoria_top:
        nombre_top, monto_top = categoria_top
        pct_del_total = (monto_top / total_gasto * 100) if total_gasto > 0 else 0
        frases.append(f"{icono_categoria(nombre_top)} Tu mayor gasto fue **{nombre_top}**, con ${monto_top:,.0f} ({pct_del_total:.0f}% del total).")

    return " ".join(frases)


# ============================================================
# CONFIGURACIÓN — reemplaza antes de producción
# ============================================================
STRIPE_PAYMENT_LINK = "https://buy.stripe.com/tu-link-de-pago"  # TODO: link real de Stripe

CATEGORIAS_DEFECTO = [
    ("Supermercado", "gasto"), ("Restaurantes", "gasto"), ("Transporte", "gasto"),
    ("Suscripciones", "gasto"), ("Vivienda", "gasto"), ("Salud", "gasto"),
    ("Entretenimiento", "gasto"), ("Otros gastos", "gasto"), ("Salario", "ingreso"), ("Otros ingresos", "ingreso"),
]

REGLAS_CATEGORIZACION = {
    "Supermercado": ["walmart", "soriana", "chedraui", "supermercado", "costco", "la comer", "aurrera"],
    "Restaurantes": ["restaurante", "starbucks", "mcdonald", "uber eats", "rappi", "cafe", "domino"],
    "Transporte": ["uber", "cabify", "didi", "gasolina", "gasolinera", "metro", "camion", "taxi"],
    "Suscripciones": ["netflix", "spotify", "disney", "hbo", "amazon prime", "youtube premium", "icloud"],
    "Vivienda": ["renta", "hipoteca", "luz", "agua", "gas natural", "predial", "mantenimiento"],
    "Salud": ["farmacia", "doctor", "hospital", "seguro medico", "dentista"],
    "Entretenimiento": ["cine", "boletos", "concierto", "videojuego", "steam"],
}


def auto_categorizar(descripcion):
    if not descripcion:
        return "Otros gastos"
    texto = descripcion.lower()
    for categoria, palabras in REGLAS_CATEGORIZACION.items():
        if any(p in texto for p in palabras):
            return categoria
    return "Otros gastos"


# ============================================================
# CONTEXTO ECONÓMICO — nudge educativo, NO consejo de inversión.
# Reutiliza la misma metodología pública y honesta que Q-FSI: modelos
# académicos validados, datos de FRED (gobierno de EE.UU., dominio público),
# mostrados con sus límites explícitos. Ningún broker de presupuesto hace
# esto — es la diferenciación real de FinZen frente a Monarch/YNAB/Copilot.
# ============================================================
@st.cache_data(ttl=3600)
def cargar_fred_csv(series_id, years=None):
    if not REQUESTS_AVAILABLE:
        return None
    try:
        resp = requests.get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}", timeout=10)
        if resp.status_code != 200:
            return None
        df = pd.read_csv(io.StringIO(resp.text))
        df.columns = ["Date", series_id]
        df["Date"] = pd.to_datetime(df["Date"])
        df[series_id] = pd.to_numeric(df[series_id], errors="coerce")
        df = df.dropna().set_index("Date")
        if years:
            df = df[df.index >= pd.Timestamp.today() - pd.DateOffset(years=years)]
        return df if not df.empty else None
    except Exception:
        return None


@st.cache_data(ttl=3600)
def cargar_contexto_economico():
    """Evalúa los 3 modelos de recesión públicos (mismos que Q-FSI) y devuelve un
    estado resumido de una sola línea, sin pretender más precisión de la que
    realmente tienen. Ver Q-FSI para la metodología completa y sus límites."""
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
            detalle.append(("Modelo NY Fed (curva de rendimientos)", prob, activo, f"{prob:.0f}% prob. de recesión en 12 meses"))

    sahm = cargar_fred_csv("SAHMREALTIME", years=2)
    if sahm is not None and not sahm.empty:
        valor = sahm["SAHMREALTIME"].iloc[-1]
        activo = valor >= 0.50
        señales += int(activo)
        detalle.append(("Regla de Sahm (empleo)", valor, activo, f"{valor:.2f}pp sobre el mínimo de 12 meses"))

    recprob = cargar_fred_csv("RECPROUSM156N", years=2)
    if recprob is not None and not recprob.empty:
        valor = recprob["RECPROUSM156N"].iloc[-1]
        activo = valor >= 50
        señales += int(activo)
        detalle.append(("Modelo Chauvet-Piger (actividad real)", valor, activo, f"{valor:.0f}% probabilidad coincidente"))

    return señales, detalle


# ============================================================
# SUPABASE / AUTENTICACIÓN REAL
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

for key, default in [("user", None), ("plan", "free")]:
    if key not in st.session_state:
        st.session_state[key] = default


def sign_in(email, password):
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        return res.user, None
    except Exception as e:
        return None, str(e)


def sign_up(email, password):
    try:
        res = supabase.auth.sign_up({"email": email, "password": password})
        return res.user, None
    except Exception as e:
        return None, str(e)


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
        nombres_existentes = {c["name"] for c in existentes.data} if existentes.data else set()
        faltantes = [{"user_email": email, "name": n, "tipo": t} for n, t in CATEGORIAS_DEFECTO if n not in nombres_existentes]
        if faltantes:
            supabase.table("categories").insert(faltantes).execute()
    except Exception:
        pass


# ============================================================
# HOGARES COMPARTIDOS (Pro) — pareja/familia viendo el mismo presupuesto,
# sin dejar de poder tener categorías y gastos 100% personales si quieren.
# ============================================================
def obtener_hogar(email):
    if not supabase:
        return None
    try:
        membresia = supabase.table("household_members").select("household_id, role").eq("user_email", email).execute()
        if not membresia.data:
            return None
        household_id = membresia.data[0]["household_id"]
        rol = membresia.data[0]["role"]
        hogar = supabase.table("households").select("*").eq("id", household_id).execute()
        if not hogar.data:
            return None
        miembros = supabase.table("household_members").select("user_email, role").eq("household_id", household_id).execute()
        return {"id": household_id, "nombre": hogar.data[0]["name"], "rol": rol, "miembros": miembros.data or []}
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


def invitar_miembro(household_id, email_nuevo):
    try:
        supabase.table("household_members").insert({"household_id": household_id, "user_email": email_nuevo, "role": "member"}).execute()
        return True, None
    except Exception as e:
        return False, str(e)


def quitar_miembro(household_id, email_miembro):
    try:
        supabase.table("household_members").delete().eq("household_id", household_id).eq("user_email", email_miembro).execute()
        return True, None
    except Exception as e:
        return False, str(e)


st.sidebar.markdown("### 🌱 FinZen")
if not db_connected:
    st.sidebar.warning("⚠️ Sin conexión a base de datos (modo demo). Configura SUPABASE_URL y SUPABASE_KEY en secrets.")
elif not st.session_state["user"]:
    st.sidebar.markdown("#### Inicia sesión o crea tu cuenta")
    correo = st.sidebar.text_input("Correo")
    clave = st.sidebar.text_input("Contraseña", type="password")
    acepta_terminos = st.sidebar.checkbox("Acepto los Términos de Servicio y el Aviso de Privacidad (pestaña ⚖️ Legal)")
    c1, c2 = st.sidebar.columns(2)
    with c1:
        if st.button("Entrar"):
            if correo and clave:
                user, err = sign_in(correo, clave)
                if user:
                    st.session_state["user"] = user.email
                    st.session_state["plan"] = get_user_plan(user.email)
                    asegurar_categorias_defecto(user.email)
                    st.rerun()
                else:
                    st.sidebar.error(f"No se pudo iniciar sesión: {err}")
            else:
                st.sidebar.error("Ingresa correo y contraseña.")
    with c2:
        if st.button("Crear cuenta"):
            if not acepta_terminos:
                st.sidebar.error("Debes aceptar los Términos y el Aviso de Privacidad para crear una cuenta.")
            elif correo and clave:
                user, err = sign_up(correo, clave)
                if user:
                    st.sidebar.success("Cuenta creada. Inicia sesión.")
                else:
                    st.sidebar.error(f"No se pudo registrar: {err}")
            else:
                st.sidebar.error("Ingresa correo y contraseña.")
else:
    st.sidebar.success(f"Hola, **{st.session_state['user']}**")
    badge = '<span class="pro-badge">PRO</span>' if st.session_state["plan"] == "pro" else '<span class="free-badge">GRATIS</span>'
    st.sidebar.markdown(f"Plan: {badge}", unsafe_allow_html=True)
    if st.session_state["plan"] != "pro":
        st.sidebar.markdown(
            f'<br><a href="{STRIPE_PAYMENT_LINK}" target="_blank" style="background-color:{PINO}; color:white; '
            'padding:8px 12px; border-radius:10px; text-decoration:none; font-weight:700; display:block; text-align:center;">'
            '✨ Pasar a Pro ($6.99/mes)</a>', unsafe_allow_html=True)
    if st.sidebar.button("Cerrar sesión"):
        if supabase:
            try:
                supabase.auth.sign_out()
            except Exception:
                pass
        st.session_state["user"] = None
        st.session_state["plan"] = "free"
        st.rerun()

def obtener_saludo():
    hora = pd.Timestamp.now().hour
    if hora < 12:
        return "Buenos días"
    elif hora < 19:
        return "Buenas tardes"
    return "Buenas noches"


nombre_mostrado = st.session_state["user"].split("@")[0].capitalize() if st.session_state["user"] else ""
st.markdown(f"""
<div class="hero-banner">
    <h1>🌱 {obtener_saludo()}{f', {nombre_mostrado}' if nombre_mostrado else ''}</h1>
    <p>Tu compañero de finanzas — sin culpa, sin jerga, sin consejos de inversión que no te puedo dar.</p>
    <span class="hero-pill">✨ Claridad financiera en un vistazo</span>
</div>
""", unsafe_allow_html=True)

if not st.session_state["user"]:
    st.info("👈 Inicia sesión o crea una cuenta gratis en el panel lateral para empezar a registrar tus gastos.")
    st.stop()

email = st.session_state["user"]
es_pro = st.session_state["plan"] == "pro"


@st.cache_data(ttl=60)
def cargar_transacciones(email):
    """No filtra por user_email en el cliente: el RLS ya decide qué filas puede ver
    (propias + las del hogar del que es miembro) — filtrar aquí además ocultaría
    las transacciones compartidas por otros miembros del hogar."""
    if not supabase:
        return pd.DataFrame(columns=["id", "fecha", "monto", "categoria", "descripcion", "fuente", "user_email", "household_id"])
    try:
        res = supabase.table("transactions").select("*").order("fecha", desc=True).execute()
        cols = ["id", "fecha", "monto", "categoria", "descripcion", "fuente", "user_email", "household_id"]
        df = pd.DataFrame(res.data) if res.data else pd.DataFrame(columns=cols)
        if not df.empty:
            df["fecha"] = pd.to_datetime(df["fecha"])
        return df
    except Exception:
        return pd.DataFrame(columns=["id", "fecha", "monto", "categoria", "descripcion", "fuente", "user_email", "household_id"])


@st.cache_data(ttl=60)
def cargar_categorias(email):
    if not supabase:
        return pd.DataFrame(columns=["name", "tipo", "presupuesto_mensual", "user_email", "household_id"])
    try:
        res = supabase.table("categories").select("*").order("name").execute()
        cols = ["name", "tipo", "presupuesto_mensual", "user_email", "household_id"]
        return pd.DataFrame(res.data) if res.data else pd.DataFrame(columns=cols)
    except Exception:
        return pd.DataFrame(columns=["name", "tipo", "presupuesto_mensual", "user_email", "household_id"])


hogar = obtener_hogar(email) if supabase else None

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["📊 Resumen", "➕ Registrar", "📥 Importar CSV", "🎯 Presupuestos", "📚 Educación Financiera", "🏠 Mi Hogar", "⚖️ Legal"])

df_tx_todo = cargar_transacciones(email)
df_cat_todo = cargar_categorias(email)

vista_hogar = False
if hogar and es_pro:
    vista_hogar = st.radio("Viendo:", ["Solo yo", f"Todo el hogar ({hogar['nombre']})"], horizontal=True) != "Solo yo"

if vista_hogar:
    df_tx = df_tx_todo[df_tx_todo["household_id"] == hogar["id"]] if not df_tx_todo.empty else df_tx_todo
    df_cat = df_cat_todo[df_cat_todo["household_id"] == hogar["id"]] if not df_cat_todo.empty else df_cat_todo
else:
    df_tx = df_tx_todo[df_tx_todo["user_email"] == email] if not df_tx_todo.empty else df_tx_todo
    df_cat = df_cat_todo[(df_cat_todo["user_email"] == email) & (df_cat_todo["household_id"].isna())] if not df_cat_todo.empty else df_cat_todo

with tab1:
    st.subheader("Tu mes de un vistazo")

    with st.container():
        señales, detalle_señales = cargar_contexto_economico()
        if detalle_señales:
            if señales == 0:
                st.markdown('<div class="insight-card insight-buena">🟢 <b>Contexto económico:</b> los indicadores públicos de recesión más seguidos no muestran alerta activa por ahora.</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="insight-card insight-alerta">🟡 <b>Contexto económico:</b> {señales} de {len(detalle_señales)} indicadores públicos de recesión están en zona de alerta. No es una predicción segura, pero puede ser buen momento para revisar tu fondo de emergencia.</div>', unsafe_allow_html=True)
            if es_pro:
                with st.expander("Ver detalle de los indicadores"):
                    for nombre, valor, activo, texto in detalle_señales:
                        st.write(("🔴" if activo else "🟢") + f" **{nombre}**: {texto}")
                    st.caption("Mismos modelos públicos y validados académicamente que usa el motor Q-FSI (NY Fed, Regla de Sahm, Chauvet-Piger). Ninguno es infalible — esto es información de contexto, no asesoría de inversión ni una predicción garantizada.")
            else:
                st.caption("✨ El detalle de cada indicador está en el plan Pro.")

    hoy = pd.Timestamp.today()
    if df_tx.empty:
        st.info("Aún no tienes movimientos registrados. Ve a la pestaña **➕ Registrar** para agregar el primero.")
    else:
        df_tx["mes"] = df_tx["fecha"].dt.to_period("M")
        mes_actual = hoy.to_period("M")
        mes_anterior = mes_actual - 1
        df_mes = df_tx[df_tx["mes"] == mes_actual]
        df_mes_ant = df_tx[df_tx["mes"] == mes_anterior]

        gasto_categorias = set(df_cat[df_cat["tipo"] == "gasto"]["name"]) if not df_cat.empty else set()
        ingreso_categorias = set(df_cat[df_cat["tipo"] == "ingreso"]["name"]) if not df_cat.empty else set()

        total_gasto = -df_mes[df_mes["categoria"].isin(gasto_categorias)]["monto"].sum() if not df_mes.empty else 0
        total_ingreso = df_mes[df_mes["categoria"].isin(ingreso_categorias)]["monto"].sum() if not df_mes.empty else 0
        balance = total_ingreso - total_gasto

        m1, m2, m3 = st.columns(3)
        m1.metric("Ingresos del mes", f"${total_ingreso:,.0f}")
        m2.metric("Gastos del mes", f"${total_gasto:,.0f}")
        m3.metric("Balance", f"${balance:,.0f}", delta="Positivo" if balance >= 0 else "Negativo", delta_color="normal" if balance >= 0 else "inverse")

        # --- Medidor de salud financiera: síntesis visual, no otro número más ---
        tasa_ahorro = (balance / total_ingreso) if total_ingreso > 0 else 0
        presupuestos_activos = df_cat[(df_cat["tipo"] == "gasto") & df_cat["presupuesto_mensual"].notna()] if not df_cat.empty else pd.DataFrame()
        gastos_por_cat_actual = df_mes[df_mes["categoria"].isin(gasto_categorias)].groupby("categoria")["monto"].sum().abs()
        if not presupuestos_activos.empty:
            cumplidos = sum(1 for _, f in presupuestos_activos.iterrows() if gastos_por_cat_actual.get(f["name"], 0) <= f["presupuesto_mensual"])
            pct_presupuesto_ok = cumplidos / len(presupuestos_activos)
        else:
            pct_presupuesto_ok = 0.7  # neutral si aún no configura presupuestos
        puntaje_salud = round(min(100, max(0, min(max(tasa_ahorro, 0), 1) * 60 + pct_presupuesto_ok * 40)))

        col_gauge, col_dona = st.columns([1, 1.4])
        with col_gauge:
            st.markdown("#### 💚 Salud financiera")
            st.plotly_chart(grafico_salud_financiera(puntaje_salud), use_container_width=True)
            if puntaje_salud >= 70:
                st.caption("Vas muy bien este mes.")
            elif puntaje_salud >= 40:
                st.caption("Vas en terreno neutral — hay margen para ajustar.")
            else:
                st.caption("Este mes viene apretado. Revisa tus categorías con más gasto.")

        with col_dona:
            st.markdown("#### Gasto por categoría este mes")
            gastos_mes = df_mes[df_mes["categoria"].isin(gasto_categorias)].groupby("categoria")["monto"].sum().abs().sort_values(ascending=False)
            if not gastos_mes.empty:
                colores = [PALETA_CATEGORIAS[i % len(PALETA_CATEGORIAS)] for i in range(len(gastos_mes))]
                fig = go.Figure(go.Pie(labels=gastos_mes.index, values=gastos_mes.values, hole=0.58,
                                        marker=dict(colors=colores, line=dict(color=TARJETA, width=2)),
                                        textinfo="percent", textfont=dict(family="Inter", size=12, color="white")))
                fig = estilo_grafico(fig, height=300)
                fig.update_layout(showlegend=False)
                fig.add_annotation(text=f"${gastos_mes.sum():,.0f}<br><span style='font-size:11px;color:{TEXTO_SUAVE}'>total</span>",
                                    showarrow=False, font=dict(family="JetBrains Mono", size=18, color=TEXTO))
                st.plotly_chart(fig, use_container_width=True)
                chips = "".join(f'<span class="cat-chip">{icono_categoria(cat)} {cat} · ${monto:,.0f}</span>' for cat, monto in gastos_mes.items())
                st.markdown(chips, unsafe_allow_html=True)
            else:
                st.caption("Sin gastos categorizados este mes todavía.")

        clave_celebracion = f"celebrado_{mes_actual}"
        if balance > 0 and puntaje_salud >= 75 and not st.session_state.get(clave_celebracion):
            st.balloons()
            st.session_state[clave_celebracion] = True

        # --- Resumen narrado: 2-3 frases en español simple, sin gráficos que interpretar ---
        total_ingreso_ant = df_mes_ant[df_mes_ant["categoria"].isin(ingreso_categorias)]["monto"].sum() if not df_mes_ant.empty else 0
        total_gasto_ant = -df_mes_ant[df_mes_ant["categoria"].isin(gasto_categorias)]["monto"].sum() if not df_mes_ant.empty else 0
        tasa_ahorro_ant = ((total_ingreso_ant - total_gasto_ant) / total_ingreso_ant) if total_ingreso_ant > 0 else None
        categoria_top = (gastos_mes.index[0], gastos_mes.iloc[0]) if not gastos_mes.empty else None
        comp_actual_base = gastos_mes
        comp_anterior_base = df_mes_ant[df_mes_ant["categoria"].isin(gasto_categorias)].groupby("categoria")["monto"].sum().abs() if not df_mes_ant.empty else pd.Series(dtype=float)
        resumen = generar_resumen_narrado(total_ingreso, total_gasto, balance, tasa_ahorro, tasa_ahorro_ant,
                                           comp_actual_base, comp_anterior_base, categoria_top)
        st.markdown(f'<div class="insight-card">📝 <b>Tu mes en resumen:</b> {resumen}</div>', unsafe_allow_html=True)

        if es_pro:
            st.markdown("#### Tendencia últimos 6 meses")
            df_tx["mes_str"] = df_tx["mes"].astype(str)
            ult_6 = sorted(df_tx["mes_str"].unique())[-6:]
            serie = df_tx[df_tx["mes_str"].isin(ult_6) & df_tx["categoria"].isin(gasto_categorias)].groupby("mes_str")["monto"].sum().abs()
            fig2 = go.Figure(go.Scatter(x=serie.index, y=serie.values, line=dict(color=PINO, width=3), fill="tozeroy", fillcolor="rgba(31,77,61,0.08)",
                                         mode="lines+markers", marker=dict(size=7, color=GOLD, line=dict(width=2, color=PINO))))
            fig2 = estilo_grafico(fig2, height=280)
            st.plotly_chart(fig2, use_container_width=True)

            st.markdown("#### 💡 Insights")
            comp_actual = df_mes[df_mes["categoria"].isin(gasto_categorias)].groupby("categoria")["monto"].sum().abs()
            if not df_mes_ant.empty:
                comp_anterior = df_mes_ant[df_mes_ant["categoria"].isin(gasto_categorias)].groupby("categoria")["monto"].sum().abs()
                for cat in comp_actual.index:
                    if cat in comp_anterior.index and comp_anterior[cat] > 0:
                        cambio = (comp_actual[cat] / comp_anterior[cat] - 1) * 100
                        if abs(cambio) >= 20:
                            clase = "insight-alerta" if cambio > 0 else "insight-buena"
                            direccion = "más" if cambio > 0 else "menos"
                            st.markdown(f'<div class="insight-card {clase}">{icono_categoria(cat)} Gastaste <b>{abs(cambio):.0f}% {direccion}</b> en <b>{cat}</b> que el mes pasado.</div>', unsafe_allow_html=True)
            if not df_cat.empty:
                presupuestos = df_cat[(df_cat["tipo"] == "gasto") & df_cat["presupuesto_mensual"].notna()]
                for _, fila in presupuestos.iterrows():
                    gastado = comp_actual.get(fila["name"], 0)
                    presupuesto = fila["presupuesto_mensual"]
                    if presupuesto and gastado > presupuesto:
                        st.markdown(f'<div class="insight-card insight-alerta">{icono_categoria(fila["name"])} Ya superaste tu presupuesto de <b>{fila["name"]}</b>: ${gastado:,.0f} de ${presupuesto:,.0f}.</div>', unsafe_allow_html=True)
        else:
            st.info("✨ Los insights automáticos y la tendencia de 6 meses están en el plan Pro.")

with tab2:
    st.subheader("Registrar un movimiento")
    with st.form("form_transaccion", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            fecha_tx = st.date_input("Fecha", value=date.today())
            tipo_tx = st.radio("Tipo", ["Gasto", "Ingreso"], horizontal=True)
        with c2:
            monto_tx = st.number_input("Monto", min_value=0.0, step=10.0)
            descripcion_tx = st.text_input("Descripción (ej: Starbucks, Uber, renta)")

        categorias_disponibles = df_cat[df_cat["tipo"] == ("gasto" if tipo_tx == "Gasto" else "ingreso")]["name"].tolist()
        sugerida = auto_categorizar(descripcion_tx) if tipo_tx == "Gasto" else "Salario"
        indice_sugerido = categorias_disponibles.index(sugerida) if sugerida in categorias_disponibles else 0
        categoria_tx = st.selectbox("Categoría", categorias_disponibles or ["Otros gastos"], index=indice_sugerido if categorias_disponibles else 0)

        compartir_tx = False
        if hogar and es_pro:
            compartir_tx = st.checkbox(f"Compartir con mi hogar ({hogar['nombre']})")

        if st.form_submit_button("Guardar movimiento"):
            if not supabase:
                st.error("Sin conexión a base de datos.")
            elif monto_tx <= 0:
                st.error("El monto debe ser mayor a 0.")
            else:
                signo = -1 if tipo_tx == "Gasto" else 1
                try:
                    registro = {
                        "user_email": email, "fecha": fecha_tx.isoformat(), "monto": signo * monto_tx,
                        "categoria": categoria_tx, "descripcion": descripcion_tx, "fuente": "manual",
                    }
                    if compartir_tx and hogar:
                        registro["household_id"] = hogar["id"]
                    supabase.table("transactions").insert(registro).execute()
                    st.success("Movimiento guardado.")
                    st.cache_data.clear()
                except Exception as e:
                    st.error(f"No se pudo guardar: {e}")

    st.divider()
    st.markdown("#### Movimientos recientes")
    if not df_tx.empty:
        df_mostrar = df_tx[["fecha", "categoria", "descripcion", "monto"]].head(20).copy()
        df_mostrar["categoria"] = df_mostrar["categoria"].apply(lambda c: f"{icono_categoria(c)} {c}" if pd.notna(c) else c)
        st.dataframe(df_mostrar, use_container_width=True, hide_index=True)
    else:
        st.caption("Sin movimientos todavía.")

with tab3:
    st.subheader("📥 Importar movimientos desde CSV")
    if not es_pro:
        st.info("✨ La importación de CSV está en el plan Pro. Puedes seguir registrando movimientos a mano en la pestaña anterior.")
    else:
        st.caption("Sube el CSV que exportas de tu banco. Detectamos automáticamente las columnas de fecha, monto y descripción — revisa antes de confirmar.")
        archivo = st.file_uploader("Archivo CSV", type=["csv"])
        if archivo:
            try:
                df_csv = pd.read_csv(archivo)
                cols = {c.lower().strip(): c for c in df_csv.columns}

                def encontrar_col(posibles):
                    for p in posibles:
                        for c_lower, c_original in cols.items():
                            if p in c_lower:
                                return c_original
                    return None

                col_fecha = encontrar_col(["fecha", "date"])
                col_monto = encontrar_col(["monto", "amount", "importe", "cargo", "abono"])
                col_desc = encontrar_col(["descripcion", "concepto", "description", "detalle"])

                st.write("Columnas detectadas:")
                c1, c2, c3 = st.columns(3)
                col_fecha = c1.selectbox("Columna de fecha", df_csv.columns, index=list(df_csv.columns).index(col_fecha) if col_fecha else 0)
                col_monto = c2.selectbox("Columna de monto", df_csv.columns, index=list(df_csv.columns).index(col_monto) if col_monto else 0)
                col_desc = c3.selectbox("Columna de descripción", df_csv.columns, index=list(df_csv.columns).index(col_desc) if col_desc else 0)

                df_prev = pd.DataFrame({
                    "fecha": pd.to_datetime(df_csv[col_fecha], errors="coerce"),
                    "monto": pd.to_numeric(df_csv[col_monto], errors="coerce"),
                    "descripcion": df_csv[col_desc].astype(str),
                }).dropna(subset=["fecha", "monto"])
                df_prev["categoria"] = df_prev["descripcion"].apply(auto_categorizar)

                st.markdown(f"**Vista previa** ({len(df_prev)} movimientos detectados):")
                st.dataframe(df_prev.head(15), use_container_width=True, hide_index=True)

                if st.button(f"Importar {len(df_prev)} movimientos"):
                    registros = [{
                        "user_email": email, "fecha": row["fecha"].date().isoformat(), "monto": row["monto"],
                        "categoria": row["categoria"], "descripcion": row["descripcion"], "fuente": "csv",
                    } for _, row in df_prev.iterrows()]
                    try:
                        supabase.table("transactions").insert(registros).execute()
                        st.success(f"{len(registros)} movimientos importados.")
                        st.cache_data.clear()
                    except Exception as e:
                        st.error(f"Error al importar: {e}")
            except Exception as e:
                st.error(f"No se pudo leer el CSV: {e}")

with tab4:
    st.subheader("🎯 Presupuestos mensuales por categoría")
    if not es_pro:
        st.info("✨ Los presupuestos por categoría están en el plan Pro.")
    else:
        if df_cat.empty:
            st.caption("Aún no tienes categorías. Se crean automáticamente al iniciar sesión.")
        else:
            for _, fila in df_cat[df_cat["tipo"] == "gasto"].iterrows():
                col1, col2 = st.columns([2, 1])
                col1.write(f"{icono_categoria(fila['name'])} {fila['name']}")
                nuevo_valor = col2.number_input("", min_value=0.0, step=50.0,
                                                 value=float(fila["presupuesto_mensual"]) if pd.notna(fila["presupuesto_mensual"]) else 0.0,
                                                 key=f"presu_{fila['name']}", label_visibility="collapsed")
                if nuevo_valor != (fila["presupuesto_mensual"] or 0):
                    try:
                        supabase.table("categories").update({"presupuesto_mensual": nuevo_valor}).eq("id", fila["id"]).execute()
                        st.cache_data.clear()
                    except Exception:
                        pass

        st.divider()
        st.markdown("#### Agregar categoría nueva")
        nueva_cat = st.text_input("Nombre de la categoría")
        if st.button("Agregar categoría") and nueva_cat:
            try:
                supabase.table("categories").insert({"user_email": email, "name": nueva_cat, "tipo": "gasto"}).execute()
                st.success(f"Categoría '{nueva_cat}' agregada.")
                st.cache_data.clear()
            except Exception as e:
                st.error(f"No se pudo agregar: {e}")

with tab5:
    st.subheader("📚 Educación Financiera")
    st.caption("Información general para entender mejor tus finanzas. Esto NO es asesoría de inversión ni una recomendación personalizada — para eso, habla con un asesor financiero certificado.")
    conceptos = [
        ("Regla 50/30/20", "Una guía común para repartir el ingreso: 50% en necesidades (renta, comida, servicios), 30% en gustos, 20% en ahorro o pago de deudas. Es un punto de partida, no una regla fija."),
        ("Fondo de emergencia", "Dinero guardado aparte para imprevistos (pérdida de empleo, gastos médicos). Una referencia común es cubrir entre 3 y 6 meses de gastos básicos."),
        ("Interés compuesto", "Cuando los intereses que ganas (o debes) también generan intereses. Con el tiempo, este efecto crece de forma acelerada — por eso ahorrar temprano importa tanto como cuánto se ahorra."),
        ("Score o historial crediticio", "Un registro de cómo has manejado créditos en el pasado (pagos a tiempo, uso de tarjetas). Los bancos lo usan para decidir si prestarte dinero y en qué condiciones."),
        ("Deuda 'buena' vs. deuda cara", "No toda deuda es igual: una hipoteca suele tener tasas más bajas que una tarjeta de crédito. Priorizar pagar primero las deudas con tasas de interés más altas suele ahorrar más dinero en el tiempo."),
    ]
    for titulo, texto in conceptos:
        with st.expander(titulo):
            st.write(texto)

with tab6:
    st.subheader("🏠 Mi Hogar")
    st.caption("Comparte presupuesto con tu pareja o familia sin perder la opción de tener gastos personales privados. Cada quien decide, gasto por gasto, si lo comparte o no.")

    if not es_pro:
        st.info("✨ Los hogares compartidos están en el plan Pro.")
    elif not hogar:
        st.markdown("#### Crear un hogar")
        nombre_hogar = st.text_input("Nombre del hogar (ej: 'Casa de Ana y Luis')")
        if st.button("Crear hogar") and nombre_hogar:
            ok, err = crear_hogar(email, nombre_hogar)
            if ok:
                st.success("Hogar creado. Ahora puedes invitar a alguien.")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error(f"No se pudo crear: {err}")
    else:
        st.markdown(f"#### {hogar['nombre']}")
        st.write("**Miembros:**")
        for m in hogar["miembros"]:
            etiqueta = "👑 Dueño" if m["role"] == "owner" else "Miembro"
            c1, c2 = st.columns([3, 1])
            c1.write(f"{m['user_email']} — {etiqueta}")
            if hogar["rol"] == "owner" and m["user_email"] != email:
                if c2.button("Quitar", key=f"quitar_{m['user_email']}"):
                    ok, err = quitar_miembro(hogar["id"], m["user_email"])
                    if ok:
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(err)

        if hogar["rol"] == "owner":
            st.divider()
            st.markdown("#### Invitar a alguien")
            st.caption("La otra persona debe tener ya una cuenta en FinZen con ese correo.")
            correo_nuevo = st.text_input("Correo de la persona a invitar")
            if st.button("Invitar") and correo_nuevo:
                ok, err = invitar_miembro(hogar["id"], correo_nuevo)
                if ok:
                    st.success(f"{correo_nuevo} agregado al hogar.")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error(f"No se pudo invitar: {err}")

        st.divider()
        st.caption("💡 Cuando registres un gasto en la pestaña ➕ Registrar, verás la opción de marcarlo como compartido con el hogar. Los gastos que no marques siguen siendo privados, solo tú los ves.")

with tab7:
    st.subheader("⚖️ Legal")
    st.warning("⚠️ **Importante:** este texto es una plantilla de referencia generada para acelerar el arranque del producto. **No reemplaza la revisión de un abogado** antes de operar con usuarios reales o cobrar dinero. Ajusta jurisdicción, datos de contacto y cláusulas específicas de tu país antes de publicarlo como definitivo.")

    with st.expander("📄 Términos de Servicio", expanded=False):
        st.markdown(f"""
**Última actualización:** {date.today().strftime('%d/%m/%Y')}

**1. Qué es FinZen**
FinZen es una herramienta de organización financiera personal: registro de gastos e ingresos, presupuestos y educación financiera general.

**2. Lo que FinZen NO es**
FinZen **no es un asesor de inversión registrado, no ofrece asesoría financiera personalizada, y no recomienda comprar, vender o mantener ningún instrumento financiero**. La sección "Contexto Económico" muestra indicadores públicos con fines informativos y educativos únicamente. Ninguna funcionalidad de la app debe interpretarse como una recomendación de inversión.

**3. Cuentas y elegibilidad**
Debes tener al menos la mayoría de edad legal en tu jurisdicción para crear una cuenta. Eres responsable de mantener la confidencialidad de tu contraseña.

**4. Planes y pagos**
El plan Pro es una suscripción recurrente que se cobra a través de Stripe. Puedes cancelar en cualquier momento; el acceso Pro continúa hasta el final del período ya pagado.

**5. Exactitud de los datos**
Los datos que muestra FinZen dependen de lo que tú registras o importas. FinZen no verifica la exactitud de las transacciones que ingresas ni de los archivos CSV que subes.

**6. Limitación de responsabilidad**
FinZen se ofrece "tal cual". En la máxima medida permitida por la ley, no somos responsables por decisiones financieras que tomes basándote en la información de la app.

**7. Cambios a estos términos**
Podemos actualizar estos términos; te avisaremos dentro de la app ante cambios materiales.
        """)

    with st.expander("🔒 Aviso de Privacidad", expanded=False):
        st.markdown("""
**Qué datos recopilamos**
- Correo electrónico (para tu cuenta)
- Transacciones que registras manualmente o importas por CSV (fecha, monto, categoría, descripción)
- Información de tu hogar compartido, si creas uno (correos de los miembros)

**Qué NO recopilamos**
- No conectamos tu cuenta bancaria ni pedimos tus credenciales bancarias
- No vendemos tus datos a terceros
- No mostramos anuncios de terceros basados en tus datos financieros

**Dónde se almacenan tus datos**
Tus datos se guardan en una base de datos (Supabase/PostgreSQL) con seguridad a nivel de fila (Row Level Security): solo tú, y quien invites explícitamente a tu hogar, pueden ver tu información.

**Pagos**
El procesamiento de pagos del plan Pro lo realiza Stripe. FinZen no almacena números de tarjeta.

**Tus derechos**
Puedes solicitar la eliminación de tu cuenta y tus datos en cualquier momento. (Nota: el flujo de autoservicio para esto aún no está implementado — contacto manual por ahora.)

**Contacto**
Para dudas sobre privacidad: [agrega aquí tu correo de contacto real].
        """)

    st.info("💡 **Recordatorio permanente:** todo lo que ves en la pestaña 'Contexto Económico' del Resumen son datos públicos con fines educativos — no una señal de compra o venta. Para decisiones de inversión, consulta a un asesor financiero certificado en tu país.")
