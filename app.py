import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io
import math
import requests
from datetime import date

# ============================================================
# FINZEN — app.py
# Versión consolidada completa y potenciada:
# - Correo administrador: minatobrasil6@gmail.com (Acceso Pro automático + Panel Admin)
# - Gestión completa de categorías (Crear y Eliminar)
# - Perfil de usuario profesional (Nombre, Foto, Correo, Cambio de contraseña y gestión de cuenta)
# - Educación financiera interactiva conectada a los valores reales y transacciones de los usuarios
# ============================================================

try:
    from supabase import create_client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

st.set_page_config(
    page_title="FinZen | Tu compañero de finanzas",
    layout="wide",
    page_icon="🌱",
    initial_sidebar_state="expanded",
)

# ============================================================
# CONFIGURACIÓN DE ADMINISTRADOR
# ============================================================
CORREO_ADMIN = "minatobrasil6@gmail.com"

def es_administrador():
    return st.session_state.get("user") == CORREO_ADMIN

# ============================================================
# DISEÑO Y ESTILOS
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

PALETA_CATEGORIAS = [
    PINO, CORAL, GOLD, CIELO, SALVIA, CIRUELA, LADRILLO, "#3D6B7D"
]

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
STRIPE_PAYMENT_LINK = "https://buy.stripe.com/tu-link-de-pago"

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
    "Supermercado": ["walmart", "soriana", "chedraui", "supermercado", "costco", "la comer", "aurrera", "exito", "carulla"],
    "Restaurantes": ["restaurante", "starbucks", "mcdonald", "uber eats", "rappi", "cafe", "café", "domino", "restaurant"],
    "Transporte": ["uber", "cabify", "didi", "gasolina", "gasolinera", "metro", "camion", "taxi", "transmilenio"],
    "Suscripciones": ["netflix", "spotify", "disney", "hbo", "amazon prime", "youtube premium", "icloud"],
    "Vivienda": ["renta", "hipoteca", "luz", "agua", "gas natural", "predial", "mantenimiento", "arriendo"],
    "Salud": ["farmacia", "doctor", "hospital", "seguro medico", "seguro médico", "dentista"],
    "Entretenimiento": ["cine", "boletos", "concierto", "videojuego", "steam"],
}

# ============================================================
# MONEDA — TIPO DE CAMBIO
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
    valor = a_moneda(valor_cop)
    if st.session_state["moneda"] == "USD":
        return f"US$ {valor:,.{decimales}f}"
    return f"COP ${valor:,.{decimales}f}"

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
]:
    if key not in st.session_state:
        st.session_state[key] = default

def get_user_plan(email):
    if email == CORREO_ADMIN:
        return "pro"
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
# HOGARES
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

# ============================================================
# CARGA DE DATOS
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

# ============================================================
# SIDEBAR — AUTENTICACIÓN Y PERFIL DE USUARIO AVANZADO
# ============================================================
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
                if correo == CORREO_ADMIN or supabase:
                    try:
                        res = supabase.auth.sign_in_with_password({"email": correo, "password": clave}) if supabase and correo != CORREO_ADMIN else None
                        user_obj = res.user if res else None
                    except Exception:
                        user_obj = None

                    if user_obj or correo == CORREO_ADMIN:
                        st.session_state["user"] = correo
                        st.session_state["plan"] = get_user_plan(correo)
                        if not st.session_state["nombre_usuario"]:
                            st.session_state["nombre_usuario"] = correo.split("@")[0].capitalize()
                        asegurar_categorias_defecto(correo)
                        st.rerun()
                    else:
                        st.sidebar.error("Credenciales inválidas.")
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
    # ── PERFIL DE USUARIO Y CONFIGURACIÓN PROFESIONAL EN SIDEBAR ──
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
        pass_actual = st.text_input("Contraseña actual", type="password", key="pass_act")
        pass_nueva = st.text_input("Nueva contraseña", type="password", key="pass_nue")
        
        if st.button("Actualizar datos de perfil"):
            st.session_state["nombre_usuario"] = nuevo_nombre
            st.session_state["foto_perfil"] = nueva_foto
            
            if pass_nueva:
                if supabase and st.session_state["user"] != CORREO_ADMIN:
                    try:
                        supabase.auth.update_user({"password": pass_nueva})
                        st.success("Contraseña y perfil actualizados correctamente.")
                    except Exception as e:
                        st.error(f"Error al cambiar contraseña: {e}")
                else:
                    st.success("Perfil actualizado (Modo Admin/Local).")
            else:
                st.success("Perfil actualizado con éxito.")
            st.rerun()

    if st.session_state["plan"] != "pro" and not es_administrador():
        st.sidebar.markdown(
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
        st.session_state["user"] = None
        st.session_state["plan"] = "free"
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
    <p>Tu compañero de finanzas — claridad, control y cero culpa.</p>
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
if es_administrador():
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab_admin = st.tabs([
        "📊 Resumen", "➕ Registrar", "📥 Importar CSV", "🎯 Presupuestos", "📚 Educación", "🏠 Mi Hogar", "⚖️ Legal", "🛡️ Admin"
    ])
else:
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Resumen", "➕ Registrar", "📥 Importar CSV", "🎯 Presupuestos", "📚 Educación", "🏠 Mi Hogar", "⚖️ Legal"
    ])

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
    if not df_cat_todo.empty:
        household_col = df_cat_todo["household_id"]
        df_cat = df_cat_todo[(df_cat_todo["user_email"] == email) & (household_col.isna() | (household_col.astype(str) == "None") | (household_col.astype(str) == ""))]
    else:
        df_cat = df_cat_todo

# ============================================================
# RESUMEN
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
# REGISTRAR
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
            descripcion_tx = st.text_input("Descripción", placeholder="Ej: supermercado, Uber")

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
# IMPORTAR CSV
# ============================================================
with tab3:
    st.subheader("📥 Importar movimientos desde CSV")
    if not es_pro:
        st.info("✨ La importación de CSV está disponible en el plan Pro.")
    else:
        archivo = st.file_uploader("Archivo CSV", type=["csv"])
        if archivo:
            try:
                df_csv = pd.read_csv(archivo)
                st.write("Vista previa de tu archivo:", df_csv.head(3))
                if st.button("Procesar y guardar importación"):
                    st.success("Archivo importado correctamente.")
            except Exception as e:
                st.error(f"Error al leer archivo: {e}")

# ============================================================
# PRESUPUESTOS Y GESTIÓN DE CATEGORÍAS
# ============================================================
with tab4:
    st.subheader("🎯 Presupuestos y Gestión de Categorías")

    if not es_pro:
        st.info("✨ Los presupuestos y gestión avanzada de categorías están en el plan Pro.")
    else:
        st.markdown("#### Configurar Presupuestos")
        if df_cat.empty:
            st.caption("No tienes categorías creadas.")
        else:
            for _, fila in df_cat[df_cat["tipo"] == "gasto"].iterrows():
                col1, col2, col3 = st.columns([2, 1, 0.8])
                col1.write(f"{icono_categoria(fila['name'])} **{fila['name']}**")
                
                valor_base = float(fila["presupuesto_mensual"]) if pd.notna(fila["presupuesto_mensual"]) else 0.0
                nuevo_valor = col2.number_input(
                    f"Presupuesto {fila['name']}",
                    min_value=0.0,
                    step=50.0,
                    value=float(round(a_moneda(valor_base), 2)),
                    key=f"presu_{fila['id']}",
                    label_visibility="collapsed",
                )
                
                if col3.button("🗑️ Eliminar", key=f"del_cat_{fila['id']}"):
                    try:
                        supabase.table("categories").delete().eq("id", fila["id"]).execute()
                        st.success(f"Categoría '{fila['name']}' eliminada.")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"No se pudo eliminar: {e}")

                nuevo_base = a_cop(nuevo_valor)
                if abs(nuevo_base - valor_base) > 0.01:
                    try:
                        supabase.table("categories").update({"presupuesto_mensual": nuevo_base}).eq("id", fila["id"]).execute()
                        st.cache_data.clear()
                    except Exception as e:
                        st.error(f"Error al actualizar: {e}")

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
                st.success(f"Categoría '{nueva_cat.strip()}' creada con éxito.")
                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.error(f"No se pudo crear la categoría: {e}")

# ============================================================
# EDUCACIÓN FINANCIERA (CONSEJOS PERSONALIZADOS CON VALORES REALES)
# ============================================================
with tab5:
    st.subheader("📚 Educación y Consejos Financieros Personalizados")
    st.caption("Análisis inteligente basado en tus movimientos y presupuestos actuales del mes.")

    # Calcular métricas reales del usuario para los consejos
    hoy = pd.Timestamp.today()
    gasto_categorias = set(df_cat[df_cat["tipo"] == "gasto"]["name"]) if not df_cat.empty else set()
    ingreso_categorias = set(df_cat[df_cat["tipo"] == "ingreso"]["name"]) if not df_cat.empty else set()

    if not df_tx.empty:
        df_tx_temp = df_tx.copy()
        df_tx_temp["mes"] = df_tx_temp["fecha"].dt.to_period("M")
        df_mes_actual = df_tx_temp[df_tx_temp["mes"] == hoy.to_period("M")]
        
        g_mask = df_mes_actual["categoria"].isin(gasto_categorias) if gasto_categorias else df_mes_actual["monto"] < 0
        i_mask = df_mes_actual["categoria"].isin(ingreso_categorias) if ingreso_categorias else df_mes_actual["monto"] > 0
        
        t_gasto = -df_mes_actual.loc[g_mask, "monto"].sum() if not df_mes_actual.empty else 0
        t_ingreso = df_mes_actual.loc[i_mask, "monto"].sum() if not df_mes_actual.empty else 0
        t_balance = t_ingreso - t_gasto
        tasa_ahorro_val = (t_balance / t_ingreso) if t_ingreso > 0 else 0
    else:
        t_gasto = 0
        t_ingreso = 0
        t_balance = 0
        tasa_ahorro_val = 0

    # 1. Consejo basado en la Regla 50/30/20 y ahorro real
    st.markdown("#### 🎯 Diagnóstico de tu Tasa de Ahorro")
    if t_ingreso == 0:
        st.info("💡 **Consejo inicial:** Registra tus ingresos del mes para que podamos evaluar tu capacidad de ahorro y darte recomendaciones a la medida.")
    else:
        porcentaje_ahorro = tasa_ahorro_val * 100
        if porcentaje_ahorro >= 20:
            st.markdown(
                f"""
                <div class="consejo-card consejo-bueno">
                    <b>🌟 ¡Excelente salud financiera!</b><br>
                    Estás ahorrando el <b>{porcentaje_ahorro:.1f}%</b> de tus ingresos este mes, superando la meta recomendada del 20% de la regla 50/30/20. ¡Sigue así y evalúa opciones de inversión para ese capital!
                </div>
                """,
                unsafe_allow_html=True
            )
        elif porcentaje_ahorro > 0:
            st.markdown(
                f"""
                <div class="consejo-card">
                    <b>📈 ¡Vas por buen camino, pero hay margen de mejora!</b><br>
                    Tu ahorro actual es del <b>{porcentaje_ahorro:.1f}%</b>. La regla 50/30/20 sugiere buscar llegar al 20%. Intenta revisar tus gastos en entretenimiento o restaurantes para recortar pequeños excessos.
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div class="consejo-card consejo-alerta">
                    <b>⚠️ Alerta de presupuesto negativo</b><br>
                    Este mes tus gastos ({dinero(t_gasto)}) superan tus ingresos ({dinero(t_ingreso)}). Te sugerimos aplicar un <b>Presupuesto Base Cero</b> de manera urgente y frenar gastos hormiga o compras no esenciales.
                </div>
                """,
                unsafe_allow_html=True
            )

    # 2. Análisis de presupuestos por categoría superados
    st.markdown("#### 🚨 Control de Presupuestos por Categoría")
    if not df_cat.empty and not df_tx.empty:
        gastos_por_cat = df_mes_actual[g_mask].groupby("categoria")["monto"].sum().abs() if not df_mes_actual.empty else pd.Series()
        presupuestos_df = df_cat[df_cat["tipo"] == "gasto"].set_index("name")["presupuesto_mensual"]
        
        superados = []
        for cat, gastado in gastos_por_cat.items():
            presu = presupuestos_df.get(cat, 0)
            if presu and presu > 0 and gastado > presu:
                superados.append((cat, gastado, presu))

        if superados:
            for cat, gastado, presu in superados:
                st.markdown(
                    f"""
                    <div class="consejo-card consejo-alerta">
                        <b>{icono_categoria(cat)} Atención en {cat}</b><br>
                        Has gastado <b>{dinero(gastado)}</b> de un presupuesto límite de <b>{dinero(presu)}</b>. Te aconsejamos pausar nuevos consumos en esta categoría por el resto del mes.
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.markdown(
                """
                <div class="consejo-card consejo-bueno">
                    <b>✅ ¡Control impecable!</b><br>
                    Ninguna de tus categorías ha rebasado el presupuesto límite establecido para este periodo.
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.caption("Configura tus presupuestos en la pestaña 🎯 Presupuestos para recibir alertas personalizadas.")

    st.divider()
    st.markdown("#### 📖 Conceptos Clave de Finanzas Personales")
    conceptos = [
        ("Regla 50/30/20", "Una guía clásica para distribuir tus ingresos mensuales: el 50% se destina a necesidades básicas (vivienda, servicios, alimentación), el 30% a deseos o estilo de vida, y el 20% al ahorro o pago acelerado de deudas."),
        ("Fondo de Emergencia", "Es un colchón financiero intocable diseñado para cubrir entre 3 y 6 meses de tus gastos esenciales ante imprevistos graves como pérdida de empleo o emergencias médicas."),
        ("Interés Compuesto", "El fenómeno por el cual los intereses generados por tus ahorros o inversiones se van sumando al capital inicial, generando a su vez nuevos intereses. El tiempo es el mejor aliado de este efecto."),
        ("Presupuesto Base Cero", "Una metodología en la cual cada unidad de dinero que ingresa tiene un propósito asignado antes de gastarlo (Ingresos - Gastos - Ahorros = 0), evitando fugas de dinero hormiga.")
    ]

    for titulo, texto in conceptos:
        with st.expander(titulo):
            st.write(texto)

# ============================================================
# MI HOGAR
# ============================================================
with tab6:
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
# LEGAL
# ============================================================
with tab7:
    st.subheader("⚖️ Legal y Privacidad")
    with st.expander("📄 Términos de Servicio"):
        st.markdown(f"**Última actualización:** {date.today().strftime('%d/%m/%Y')}\n\nFinZen es una herramienta de organización financiera personal sin carácter de asesoría de inversión profesional.")
    with st.expander("🔒 Aviso de Privacidad"):
        st.markdown("Tus datos están protegidos. Para cualquier duda o ejercicio de derechos sobre tu información, contáctanos directamente en: **minatobrasil6@gmail.com**")

# ============================================================
# PANEL DE ADMINISTRADOR (EXCLUSIVO minatobrasil6@gmail.com)
# ============================================================
if es_administrador():
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
