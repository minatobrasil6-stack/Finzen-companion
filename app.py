import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io
import math
import requests
from datetime import date

# ============================================================
# CONFIGURACIÓN DE ADMINISTRADOR
# ============================================================
ADMIN_EMAIL = "minatobrasil6@gmail.com"  # <--- Reemplaza con tu correo real para activar el admin

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

.currency-box {{
    background: {TARJETA};
    border: 1px solid {BORDE};
    border-radius: 16px;
    padding: 12px 14px;
    box-shadow: 0 2px 8px rgba(43,38,32,.05);
    margin-bottom: 14px;
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

section[data-testid="stSidebar"] {{
    background-color: {ARENA};
    border-right: 1px solid {BORDE};
}}

.insight-card {{
    background: {TARJETA};
    border: 1px solid {BORDE};
    border-left: 4px solid {PINO};
    border-radius: 14px;
    padding: 14px 16px;
    margin-bottom: 10px;
}}
.cat-chip {{
    display: inline-flex;
    align-items: center;
    gap: 7px;
    background: {ARENA};
    padding: 7px 12px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 600;
    color: {TEXTO};
    margin: 3px 4px 3px 0;
}}
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# CONFIGURACIONES Y CONSTANTES
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

@st.cache_data(ttl=900, show_spinner=False)
def obtener_tipo_cambio_usd_cop():
    try:
        r = requests.get("https://open.er-api.com/v6/latest/USD", timeout=8)
        if r.ok:
            data = r.json()
            cop = data.get("rates", {}).get("COP")
            if cop and float(cop) > 0:
                return float(cop), "ExchangeRate-API"
    except Exception:
        pass
    return 4000.0, "Fallback Estático"

if "moneda" not in st.session_state:
    st.session_state["moneda"] = "COP"

tc_usd_cop, fuente_fx = obtener_tipo_cambio_usd_cop()

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

def simbolo_moneda():
    return "US$" if st.session_state["moneda"] == "USD" else "COP $"

def dinero(valor_cop, decimales=0):
    valor = a_moneda(valor_cop)
    if st.session_state["moneda"] == "USD":
        return f"US$ {valor:,.{decimales}f}"
    return f"COP ${valor:,.{decimales}f}"

def dinero_desde_valor(valor, decimales=0):
    if st.session_state["moneda"] == "USD":
        return f"US$ {float(valor):,.{decimales}f}"
    return f"COP ${float(valor):,.{decimales}f}"

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
        xaxis=dict(gridcolor=BORDE, zerolinecolor=BORDE),
        yaxis=dict(gridcolor=BORDE, zerolinecolor=BORDE),
    )
    return fig

# ============================================================
# SUPABASE CLIENTE Y AUTENTICACIÓN
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

for key, default in [("user", None), ("plan", "free"), ("user_nombre", "")]:
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
        nombres_existentes = {c["name"] for c in (existentes.data or [])}
        faltantes = [{"user_email": email, "name": nombre, "tipo": tipo} for nombre, tipo in CATEGORIAS_DEFECTO if nombre not in nombres_existentes]
        if faltantes:
            supabase.table("categories").insert(faltantes).execute()
    except Exception:
        pass

# ============================================================
# FUNCIONES DE DATOS Y HOGARES
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
        return df
    except Exception:
        return pd.DataFrame(columns=["id", "name", "tipo", "presupuesto_mensual", "user_email", "household_id"])

# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.markdown("### 🌱 FinZen")

if tc_usd_cop:
    st.sidebar.markdown("#### 💱 Moneda")
    moneda_nueva = st.sidebar.radio("Ver importes en", ["COP", "USD"], index=0 if st.session_state["moneda"] == "COP" else 1, horizontal=True, label_visibility="collapsed")
    if moneda_nueva != st.session_state["moneda"]:
        st.session_state["moneda"] = moneda_nueva
        st.rerun()

if not db_connected:
    st.sidebar.warning("⚠️ Sin conexión a base de datos.")
elif not st.session_state["user"]:
    st.sidebar.markdown("#### Inicia sesión o crea tu cuenta")
    correo = st.sidebar.text_input("Correo")
    clave = st.sidebar.text_input("Contraseña", type="password")
    acepta_terminos = st.sidebar.checkbox("Acepto los Términos y Privacidad.")

    c1, c2 = st.sidebar.columns(2)
    with c1:
        if st.button("Entrar", key="login_btn"):
            if correo and clave:
                user, err = sign_in(correo, clave)
                if user:
                    st.session_state["user"] = user.email
                    st.session_state["plan"] = get_user_plan(user.email)
                    asegurar_categorias_defecto(user.email)
                    st.rerun()
                else:
                    st.sidebar.error(f"Error: {err}")
            else:
                st.sidebar.error("Ingresa credenciales.")
    with c2:
        if st.button("Crear cuenta", key="signup_btn"):
            if not acepta_terminos:
                st.sidebar.error("Acepta los términos.")
            elif correo and clave:
                user, err = sign_up(correo, clave)
                if user:
                    st.sidebar.success("¡Cuenta creada! Ya puedes iniciar sesión.")
                else:
                    st.sidebar.error(f"Error: {err}")
else:
    nombre_usuario = st.session_state.get("user_nombre") or st.session_state["user"].split("@")[0].capitalize()
    st.sidebar.success(f"Hola, **{nombre_usuario}**")

    if st.session_state["user"] == ADMIN_EMAIL:
        with st.sidebar.expander("🛡️ Panel Admin"):
            if st.button("Limpiar Caché"):
                st.cache_data.clear()
                st.success("Caché limpia.")

    if st.session_state["plan"] != "pro":
        st.sidebar.markdown(f'<a href="{STRIPE_PAYMENT_LINK}" target="_blank" style="background:{PINO};color:white;padding:9px 12px;border-radius:10px;text-decoration:none;font-weight:700;display:block;text-align:center;">✨ Pasar a Pro ($6.99/mes)</a>', unsafe_allow_html=True)

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
nombre_mostrado = st.session_state.get("user_nombre") or (st.session_state["user"].split("@")[0].capitalize() if st.session_state["user"] else "")

def obtener_saludo():
    hora = pd.Timestamp.now().hour
    if hora < 12: return "Buenos días"
    if hora < 19: return "Buenas tardes"
    return "Buenas noches"

st.markdown(f"""
<div class="hero-banner">
    <h1>🌱 {obtener_saludo()}{f', {nombre_mostrado}' if nombre_mostrado else ''}</h1>
    <p>Tu compañero de finanzas — claridad, control y cero culpa.</p>
</div>
""", unsafe_allow_html=True)

if not st.session_state["user"]:
    st.info("👈 Inicia sesión en el panel lateral para empezar.")
    st.stop()

email = st.session_state["user"]
es_pro = st.session_state["plan"] == "pro"
hogar = obtener_hogar(email) if supabase else None

# ============================================================
# TABS DE NAVEGACIÓN (Incluyendo Perfil Profesional)
# ============================================================
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "📊 Resumen", "➕ Registrar", "📥 Importar", "🎯 Presupuestos", "📚 Educación", "🏠 Hogar", "⚙️ Mi Perfil", "⚖️ Legal"
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
    df_cat = df_cat_todo[(df_cat_todo["user_email"] == email) & (df_cat_todo["household_id"].isna())] if not df_cat_todo.empty else df_cat_todo

# ============================================================
# 1. RESUMEN
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

        total_gasto = -df_mes[df_mes["monto"] < 0]["monto"].sum() if not df_mes.empty else 0
        total_ingreso = df_mes[df_mes["monto"] > 0]["monto"].sum() if not df_mes.empty else 0
        balance = total_ingreso - total_gasto

        m1, m2, m3 = st.columns(3)
        m1.metric("Ingresos del mes", dinero(total_ingreso))
        m2.metric("Gastos del mes", dinero(total_gasto))
        m3.metric("Balance", dinero(balance), delta="Positivo" if balance >= 0 else "Negativo")

# ============================================================
# 2. REGISTRAR
# ============================================================
with tab2:
    st.subheader("Registrar movimiento")
    with st.form("form_transaccion", clear_on_submit=True):
        c1, c2 = st.columns(2)
        fecha_tx = c1.date_input("Fecha", value=date.today())
        tipo_tx = c1.radio("Tipo", ["Gasto", "Ingreso"], horizontal=True)
        monto_tx = c2.number_input(f"Monto ({st.session_state['moneda']})", min_value=0.0, step=10.0)
        descripcion_tx = c2.text_input("Descripción")
        
        tipo_categoria = "gasto" if tipo_tx == "Gasto" else "ingreso"
        categorias_disponibles = df_cat[df_cat["tipo"] == tipo_categoria]["name"].tolist() if not df_cat.empty else []
        categoria_tx = st.selectbox("Categoría", categorias_disponibles or ["Otros gastos"])
        
        guardar = st.form_submit_button("Guardar movimiento")
    
    if guardar and monto_tx > 0 and supabase:
        monto_cop = a_cop(monto_tx)
        signo = -1 if tipo_tx == "Gasto" else 1
        supabase.table("transactions").insert({
            "user_email": email, "fecha": fecha_tx.isoformat(), "monto": signo * monto_cop,
            "categoria": categoria_tx, "descripcion": descripcion_tx, "fuente": "manual"
        }).execute()
        st.success("¡Movimiento registrado con éxito!")
        st.cache_data.clear()
        st.rerun()

# ============================================================
# 3. IMPORTAR CSV
# ============================================================
with tab3:
    st.subheader("📥 Importar movimientos desde CSV")
    if not es_pro:
        st.info("✨ Función exclusiva del plan Pro.")
    else:
        archivo = st.file_uploader("Sube tu archivo CSV", type=["csv"])
        if archivo:
            df_csv = pd.read_csv(archivo)
            st.dataframe(df_csv.head(5))

# ============================================================
# 4. PRESUPUESTOS Y GESTIÓN DE CATEGORÍAS
# ============================================================
with tab4:
    st.subheader("🎯 Presupuestos y Control por Categoría")
    if not es_pro:
        st.info("✨ Función exclusiva del plan Pro.")
    elif not df_cat.empty:
        st.markdown("#### 📊 Presupuesto vs Gasto Actual")
        gastos_reales_cat = df_tx[df_tx["monto"] < 0].groupby("categoria")["monto"].sum().abs() if not df_tx.empty else pd.Series()
        
        tabla_comparativa = df_cat[df_cat["tipo"] == "gasto"].copy()
        tabla_comparativa["Gastado"] = tabla_comparativa["name"].map(gastos_reales_cat).fillna(0)
        
        df_mostrar_comp = tabla_comparativa[["name", "presupuesto_mensual", "Gastado"]].copy()
        df_mostrar_comp["presupuesto_mensual"] = df_mostrar_comp["presupuesto_mensual"].fillna(0).apply(dinero)
        df_mostrar_comp["Gastado"] = df_mostrar_comp["Gastado"].apply(dinero)
        df_mostrar_comp.columns = ["Categoría", "Presupuesto", "Gasto Real"]
        st.dataframe(df_mostrar_comp, use_container_width=True, hide_index=True)

        st.divider()
        st.markdown("#### 🗑️ Eliminar Categoría")
        cat_a_borrar = st.selectbox("Selecciona categoría para borrar:", df_cat["name"].tolist())
        if st.button("Eliminar categoría seleccionada"):
            supabase.table("categories").delete().eq("name", cat_a_borrar).eq("user_email", email).execute()
            st.success(f"Categoría '{cat_a_borrar}' eliminada.")
            st.cache_data.clear()
            st.rerun()

# ============================================================
# 5. EDUCACIÓN
# ============================================================
with tab5:
    st.subheader("📚 Educación Financiera")
    st.write("Aprende conceptos clave para mejorar tu salud financiera a largo plazo.")

# ============================================================
# 6. HOGAR
# ============================================================
with tab6:
    st.subheader("🏠 Gestión de Hogar Compartido")
    if not es_pro:
        st.info("✨ Funcionalidad Pro.")
    elif not hogar:
        nombre_h = st.text_input("Nombre del nuevo hogar")
        if st.button("Crear hogar") and nombre_h:
            supabase.table("households").insert({"name": nombre_h, "owner_email": email}).execute()
            st.success("Hogar creado correctamente.")
            st.rerun()

# ============================================================
# 7. MI PERFIL PROFESIONAL (Editar Perfil, Foto, Contraseña)
# ============================================================
with tab7:
    st.subheader("⚙️ Configuración de Perfil y Seguridad")
    
    col_perfil_1, col_perfil_2 = st.columns(2)
    
    with col_perfil_1:
        st.markdown("#### 👤 Información Personal")
        nuevo_nombre = st.text_input("Nombre visible", value=st.session_state.get("user_nombre", nombre_mostrado))
        
        if st.button("Guardar cambios de perfil"):
            st.session_state["user_nombre"] = nuevo_nombre
            st.success("¡Perfil actualizado con éxito!")
            st.rerun()
            
        st.markdown("---")
        st.markdown("#### 🖼️ Foto de Perfil (Avatar)")
        avatar_file = st.file_uploader("Sube tu nueva foto de perfil", type=["png", "jpg", "jpeg"])
        if avatar_file:
            st.success("Foto de perfil cargada temporalmente con éxito.")

    with col_perfil_2:
        st.markdown("#### 🔒 Seguridad y Contraseña")
        with st.form("form_cambiar_clave"):
            pass_actual = st.text_input("Contraseña actual", type="password")
            pass_nueva = st.text_input("Nueva contraseña", type="password")
            pass_confirmar = st.text_input("Confirmar nueva contraseña", type="password")
            
            submit_clave = st.form_submit_button("Actualizar contraseña")
            
            if submit_clave:
                if pass_nueva != pass_confirmar:
                    st.error("Las nuevas contraseñas no coinciden.")
                elif len(pass_nueva) < 6:
                    st.error("La contraseña debe tener al menos 6 caracteres.")
                else:
                    try:
                        supabase.auth.update_user({"password": pass_nueva})
                        st.success("¡Contraseña actualizada correctamente!")
                    except Exception as e:
                        st.error(f"Error al actualizar la contraseña: {e}")

    st.markdown("---")
    st.markdown("#### 💳 Detalles de Suscripción")
    st.info(f"Tu plan actual es: **{st.session_state['plan'].upper()}**")
    if st.session_state["plan"] != "pro":
        st.markdown(f'<a href="{STRIPE_PAYMENT_LINK}" target="_blank">Actualiza a PRO para desbloquear todas las funciones</a>', unsafe_allow_html=True)

# ============================================================
# 8. LEGAL
# ============================================================
with tab8:
    st.subheader("⚖️ Términos y Privacidad")
    st.write("Consulta los avisos legales y políticas de privacidad que rigen el uso de FinZen.")

# ============================================================
# PIE DE PÁGINA
# ============================================================
st.divider()
st.caption(f"🌱 FinZen · Moneda activa: {st.session_state['moneda']} · 1 USD = {tc_usd_cop:,.2f} COP")
