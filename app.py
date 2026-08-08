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
ADMIN_EMAIL = "tu-correo@ejemplo.com"  # <--- Reemplaza con tu correo real para activar el admin

# ============================================================
# FINZEN — app.py
# Versión consolidada y actualizada
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
# DISEÑO
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

@keyframes fadeInUp {{
    from {{ opacity: 0; transform: translateY(6px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

.hero-banner {{
    background: linear-gradient(135deg, {PINO} 0%, {PINO_CLARO} 58%, {CIELO} 130%);
    border-radius: 24px;
    padding: 28px 30px;
    margin-bottom: 20px;
    color: white;
    box-shadow: 0 8px 24px rgba(31,77,61,0.18);
    animation: fadeInUp .4s ease;
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

.currency-rate {{
    color: {TEXTO_SUAVE};
    font-size: 12px;
    margin-top: 4px;
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
    letter-spacing: .03em;
}}

div[data-testid="stMetricValue"] {{
    font-family: 'JetBrains Mono', monospace !important;
    color: {TEXTO} !important;
    font-weight: 600 !important;
}}

button[data-baseweb="tab"] {{
    font-family: 'Quicksand', sans-serif;
    font-weight: 700;
    color: {TEXTO_SUAVE};
    border-radius: 10px 10px 0 0;
}}

button[data-baseweb="tab"][aria-selected="true"] {{
    color: {PINO} !important;
    border-bottom: 3px solid {PINO} !important;
    background: {ARENA};
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

.stTextInput input,
.stNumberInput input,
.stDateInput input,
div[data-baseweb="select"] > div {{
    background-color: {TARJETA} !important;
    border: 1px solid {BORDE} !important;
    border-radius: 10px !important;
    color: {TEXTO} !important;
}}

div[data-testid="stExpander"] {{
    background-color: {TARJETA};
    border: 1px solid {BORDE};
    border-radius: 16px;
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
    box-shadow: 0 2px 6px rgba(43,38,32,.04);
}}

.insight-alerta {{
    border-left-color: {CORAL} !important;
}}

.insight-buena {{
    border-left-color: {SALVIA} !important;
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
# CONFIGURACIÓN
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
# MONEDA — TIPO DE CAMBIO REAL
# ============================================================
@st.cache_data(ttl=900, show_spinner=False)
def obtener_tipo_cambio_usd_cop():
    try:
        r = requests.get(
            "https://open.er-api.com/v6/latest/USD",
            timeout=8,
            headers={"User-Agent": "FinZen/1.0"},
        )
        if r.ok:
            data = r.json()
            cop = data.get("rates", {}).get("COP")
            if cop and float(cop) > 0:
                return float(cop), "ExchangeRate-API", pd.Timestamp.now()
    except Exception:
        pass

    try:
        r = requests.get(
            "https://api.frankfurter.app/latest?from=USD&to=COP",
            timeout=8,
            headers={"User-Agent": "FinZen/1.0"},
        )
        if r.ok:
            data = r.json()
            cop = data.get("rates", {}).get("COP")
            if cop and float(cop) > 0:
                fecha = pd.to_datetime(data.get("date", pd.Timestamp.now()))
                return float(cop), "Frankfurter/ECB", fecha
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


# ============================================================
# FUNCIONES VISUALES
# ============================================================
def icono_categoria(nombre):
    return ICONOS_CATEGORIA.get(str(nombre), "🏷️")


def estilo_grafico(fig, titulo=None, height=360):
    fig.update_layout(
        template="plotly_white",
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=TEXTO_SUAVE, size=12),
        title=dict(
            text=titulo,
            font=dict(family="Quicksand, sans-serif", color=PINO, size=17),
        ) if titulo else None,
        margin=dict(l=10, r=10, t=48 if titulo else 10, b=10),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=TEXTO_SUAVE, size=11),
        ),
        xaxis=dict(gridcolor=BORDE, zerolinecolor=BORDE),
        yaxis=dict(gridcolor=BORDE, zerolinecolor=BORDE),
    )
    return fig


def grafico_salud_financiera(puntaje):
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=puntaje,
            number={
                "suffix": "",
                "font": {
                    "size": 40,
                    "family": "JetBrains Mono",
                    "color": TEXTO,
                },
            },
            gauge={
                "axis": {
                    "range": [0, 100],
                    "tickwidth": 0,
                    "tickcolor": BORDE,
                },
                "bar": {"color": PINO, "thickness": 0.3},
                "bgcolor": "rgba(0,0,0,0)",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 40], "color": "rgba(232,115,74,.18)"},
                    {"range": [40, 70], "color": "rgba(217,164,65,.18)"},
                    {"range": [70, 100], "color": "rgba(127,182,158,.25)"},
                ],
            },
        )
    )
    fig.update_layout(
        height=205,
        margin=dict(l=15, r=15, t=5, b=5),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def generar_resumen_narrado(
    total_ingreso,
    total_gasto,
    balance,
    tasa_ahorro,
    tasa_ahorro_ant,
    categoria_top,
):
    frases = []

    if total_ingreso == 0 and total_gasto == 0:
        return "Todavía no hay suficientes movimientos este mes para armar un resumen."

    frases.append(
        f"Este mes llevas <b>{dinero(total_ingreso)}</b> de ingresos y "
        f"<b>{dinero(total_gasto)}</b> de gastos, con un balance "
        f"<b>{'positivo' if balance >= 0 else 'negativo'} de {dinero(abs(balance))}</b>."
    )

    if tasa_ahorro_ant is not None and total_ingreso > 0:
        diferencia_pp = (tasa_ahorro - tasa_ahorro_ant) * 100
        if abs(diferencia_pp) >= 3:
            direccion = "subió" if diferencia_pp > 0 else "bajó"
            frases.append(
                f"Tu tasa de ahorro {direccion} de "
                f"{tasa_ahorro_ant * 100:.0f}% a {tasa_ahorro * 100:.0f}% "
                f"respecto al mes pasado."
            )

    if categoria_top:
        nombre_top, monto_top = categoria_top
        pct = (monto_top / total_gasto * 100) if total_gasto > 0 else 0
        frases.append(
            f"{icono_categoria(nombre_top)} Tu mayor gasto fue "
            f"<b>{nombre_top}</b>, con <b>{dinero(monto_top)}</b> ({pct:.0f}% del total)."
        )

    return " ".join(frases)


# ============================================================
# CATEGORIZACIÓN
# ============================================================
def auto_categorizar(descripcion):
    if not descripcion:
        return "Otros gastos"
    texto = str(descripcion).lower()
    for categoria, palabras in REGLAS_CATEGORIZACION.items():
        if any(p in texto for p in palabras):
            return categoria
    return "Otros gastos"


# ============================================================
# FRED / CONTEXTO ECONÓMICO
# ============================================================
@st.cache_data(ttl=3600, show_spinner=False)
def cargar_fred_csv(series_id, years=None):
    try:
        resp = requests.get(
            f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}",
            timeout=10,
        )
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


@st.cache_data(ttl=3600, show_spinner=False)
def cargar_contexto_economico():
    señales = 0
    detalle = []

    dgs10 = cargar_fred_csv("DGS10", years=1)
    dgs3mo = cargar_fred_csv("DGS3MO", years=1)

    if dgs10 is not None and dgs3mo is not None:
        df = dgs10.join(dgs3mo, how="inner").dropna()
        if not df.empty:
            spread = df["DGS10"].iloc[-1] - df["DGS3MO"].iloc[-1]
            prob = (
                0.5
                * (
                    1
                    + math.erf(
                        (-0.5333 - 0.6330 * spread) / math.sqrt(2)
                    )
                )
            ) * 100
            activo = prob >= 30
            señales += int(activo)
            detalle.append(
                (
                    "Modelo NY Fed (curva de rendimientos)",
                    prob,
                    activo,
                    f"{prob:.0f}% prob. de recesión en 12 meses",
                )
            )

    sahm = cargar_fred_csv("SAHMREALTIME", years=2)
    if sahm is not None and not sahm.empty:
        valor = sahm["SAHMREALTIME"].iloc[-1]
        activo = valor >= 0.50
        señales += int(activo)
        detalle.append(
            (
                "Regla de Sahm (empleo)",
                valor,
                activo,
                f"{valor:.2f}pp sobre el mínimo de 12 meses",
            )
        )

    recprob = cargar_fred_csv("RECPROUSM156N", years=2)
    if recprob is not None and not recprob.empty:
        valor = recprob["RECPROUSM156N"].iloc[-1]
        activo = valor >= 50
        señales += int(activo)
        detalle.append(
            (
                "Modelo Chauvet-Piger (actividad real)",
                valor,
                activo,
                f"{valor:.0f}% probabilidad coincidente",
            )
        )

    return señales, detalle


# ============================================================
# SUPABASE
# ============================================================
@st.cache_resource
def init_supabase():
    if not SUPABASE_AVAILABLE:
        return None

    try:
        return create_client(
            st.secrets["SUPABASE_URL"],
            st.secrets["SUPABASE_KEY"],
        )
    except Exception:
        return None


supabase = init_supabase()
db_connected = supabase is not None

for key, default in [
    ("user", None),
    ("plan", "free"),
]:
    if key not in st.session_state:
        st.session_state[key] = default


def sign_in(email, password):
    try:
        res = supabase.auth.sign_in_with_password(
            {"email": email, "password": password}
        )
        return res.user, None
    except Exception as e:
        return None, str(e)


def sign_up(email, password):
    try:
        res = supabase.auth.sign_up(
            {"email": email, "password": password}
        )
        return res.user, None
    except Exception as e:
        return None, str(e)


def get_user_plan(email):
    if not supabase:
        return "free"

    try:
        res = (
            supabase.table("subscriptions")
            .select("status")
            .eq("user_email", email)
            .execute()
        )

        if res.data:
            return res.data[0].get("status", "free")

        supabase.table("subscriptions").insert(
            {"user_email": email, "status": "free"}
        ).execute()

        return "free"
    except Exception:
        return "free"


def asegurar_categorias_defecto(email):
    if not supabase:
        return

    try:
        existentes = (
            supabase.table("categories")
            .select("name")
            .eq("user_email", email)
            .execute()
        )

        nombres_existentes = {
            c["name"] for c in (existentes.data or [])
        }

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
        membresia = (
            supabase.table("household_members")
            .select("household_id, role")
            .eq("user_email", email)
            .execute()
        )

        if not membresia.data:
            return None

        household_id = membresia.data[0]["household_id"]
        rol = membresia.data[0]["role"]

        hogar = (
            supabase.table("households")
            .select("*")
            .eq("id", household_id)
            .execute()
        )

        if not hogar.data:
            return None

        miembros = (
            supabase.table("household_members")
            .select("user_email, role")
            .eq("household_id", household_id)
            .execute()
        )

        return {
            "id": household_id,
            "nombre": hogar.data[0]["name"],
            "rol": rol,
            "miembros": miembros.data or [],
        }
    except Exception:
        return None


def crear_hogar(email, nombre):
    try:
        res = supabase.table("households").insert(
            {"name": nombre, "owner_email": email}
        ).execute()

        household_id = res.data[0]["id"]

        supabase.table("household_members").insert(
            {
                "household_id": household_id,
                "user_email": email,
                "role": "owner",
            }
        ).execute()

        return True, None
    except Exception as e:
        return False, str(e)


def invitar_miembro(household_id, email_nuevo):
    try:
        supabase.table("household_members").insert(
            {
                "household_id": household_id,
                "user_email": email_nuevo,
                "role": "member",
            }
        ).execute()
        return True, None
    except Exception as e:
        return False, str(e)


def quitar_miembro(household_id, email_miembro):
    try:
        (
            supabase.table("household_members")
            .delete()
            .eq("household_id", household_id)
            .eq("user_email", email_miembro)
            .execute()
        )
        return True, None
    except Exception as e:
        return False, str(e)


# ============================================================
# CARGA DE DATOS
# ============================================================
@st.cache_data(ttl=60, show_spinner=False)
def cargar_transacciones(email):
    if not supabase:
        return pd.DataFrame(
            columns=[
                "id",
                "fecha",
                "monto",
                "categoria",
                "descripcion",
                "fuente",
                "user_email",
                "household_id",
            ]
        )

    try:
        res = (
            supabase.table("transactions")
            .select("*")
            .order("fecha", desc=True)
            .execute()
        )

        cols = [
            "id",
            "fecha",
            "monto",
            "categoria",
            "descripcion",
            "fuente",
            "user_email",
            "household_id",
        ]

        df = (
            pd.DataFrame(res.data)
            if res.data
            else pd.DataFrame(columns=cols)
        )

        for col in cols:
            if col not in df.columns:
                df[col] = None

        if not df.empty:
            df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
            df["monto"] = pd.to_numeric(df["monto"], errors="coerce").fillna(0)

        return df
    except Exception:
        return pd.DataFrame(
            columns=[
                "id",
                "fecha",
                "monto",
                "categoria",
                "descripcion",
                "fuente",
                "user_email",
                "household_id",
            ]
        )


@st.cache_data(ttl=60, show_spinner=False)
def cargar_categorias(email):
    if not supabase:
        return pd.DataFrame(
            columns=[
                "id",
                "name",
                "tipo",
                "presupuesto_mensual",
                "user_email",
                "household_id",
            ]
        )

    try:
        res = (
            supabase.table("categories")
            .select("*")
            .order("name")
            .execute()
        )

        df = (
            pd.DataFrame(res.data)
            if res.data
            else pd.DataFrame(
                columns=[
                    "id",
                    "name",
                    "tipo",
                    "presupuesto_mensual",
                    "user_email",
                    "household_id",
                ]
            )
        )

        for col in [
            "id",
            "name",
            "tipo",
            "presupuesto_mensual",
            "user_email",
            "household_id",
        ]:
            if col not in df.columns:
                df[col] = None

        return df
    except Exception:
        return pd.DataFrame(
            columns=[
                "id",
                "name",
                "tipo",
                "presupuesto_mensual",
                "user_email",
                "household_id",
            ]
        )


# ============================================================
# SIDEBAR
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

    st.sidebar.caption(
        f"1 USD ≈ {tc_usd_cop:,.2f} COP · fuente: {fuente_fx}"
    )
else:
    st.sidebar.warning(
        "No se pudo consultar el tipo de cambio ahora. "
        "Se mantiene COP como moneda base."
    )

if not db_connected:
    st.sidebar.warning(
        "⚠️ Sin conexión a base de datos. "
        "Configura SUPABASE_URL y SUPABASE_KEY en Secrets."
    )
elif not st.session_state["user"]:
    st.sidebar.markdown("#### Inicia sesión o crea tu cuenta")

    correo = st.sidebar.text_input("Correo")
    clave = st.sidebar.text_input("Contraseña", type="password")
    acepta_terminos = st.sidebar.checkbox(
        "Acepto los Términos de Servicio y el Aviso de Privacidad."
    )

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
                    st.sidebar.error(f"No se pudo iniciar sesión: {err}")
            else:
                st.sidebar.error("Ingresa correo y contraseña.")

    with c2:
        if st.button("Crear cuenta", key="signup_btn"):
            if not acepta_terminos:
                st.sidebar.error(
                    "Debes aceptar los Términos y el Aviso de Privacidad."
                )
            elif correo and clave:
                user, err = sign_up(correo, clave)

                if user:
                    st.sidebar.success(
                        "Cuenta creada. Ahora inicia sesión."
                    )
                else:
                    st.sidebar.error(
                        f"No se pudo registrar: {err}"
                    )
            else:
                st.sidebar.error("Ingresa correo y contraseña.")
else:
    # ── MODIFICACIÓN: Mostrar el NOMBRE en lugar del correo ──
    nombre_usuario = st.session_state["user"].split("@")[0].capitalize()
    st.sidebar.success(f"Hola, **{nombre_usuario}**")

    # ── MODIFICACIÓN: Panel de Administrador exclusivo ──
    if st.session_state["user"] == ADMIN_EMAIL:
        with st.sidebar.expander("🛡️ Panel de Administrador"):
            st.write("Herramientas exclusivas activas.")
            if st.button("Limpiar Caché Global"):
                st.cache_data.clear()
                st.success("Caché limpiada correctamente.")

    badge = (
        '<span class="pro-badge">PRO</span>'
        if st.session_state["plan"] == "pro"
        else '<span class="free-badge">GRATIS</span>'
    )

    st.sidebar.markdown(
        f"Plan: {badge}",
        unsafe_allow_html=True,
    )

    if st.session_state["plan"] != "pro":
        st.sidebar.markdown(
            f"""
<a href="{STRIPE_PAYMENT_LINK}" target="_blank"
style="background:{PINO};color:white;padding:9px 12px;border-radius:10px;
text-decoration:none;font-weight:700;display:block;text-align:center;">
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
# CABECERA
# ============================================================
nombre_mostrado = (
    st.session_state["user"].split("@")[0].capitalize()
    if st.session_state["user"]
    else ""
)


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
    st.info(
        "👈 Inicia sesión o crea una cuenta gratis en el panel lateral para comenzar."
    )
    st.stop()

email = st.session_state["user"]
es_pro = st.session_state["plan"] == "pro"

hogar = obtener_hogar(email) if supabase else None

# ============================================================
# TABS
# ============================================================
(
    tab1,
    tab2,
    tab3,
    tab4,
    tab5,
    tab6,
    tab7,
) = st.tabs(
    [
        "📊 Resumen",
        "➕ Registrar",
        "📥 Importar CSV",
        "🎯 Presupuestos",
        "📚 Educación",
        "🏠 Mi Hogar",
        "⚖️ Legal",
    ]
)

df_tx_todo = cargar_transacciones(email)
df_cat_todo = cargar_categorias(email)

vista_hogar = False

if hogar and es_pro:
    vista_hogar = (
        st.radio(
            "Viendo:",
            ["Solo yo", f"Todo el hogar ({hogar['nombre']})"],
            horizontal=True,
        )
        != "Solo yo"
    )

if vista_hogar:
    df_tx = (
        df_tx_todo[df_tx_todo["household_id"] == hogar["id"]]
        if not df_tx_todo.empty
        else df_tx_todo
    )

    df_cat = (
        df_cat_todo[df_cat_todo["household_id"] == hogar["id"]]
        if not df_cat_todo.empty
        else df_cat_todo
    )
else:
    df_tx = (
        df_tx_todo[df_tx_todo["user_email"] == email]
        if not df_tx_todo.empty
        else df_tx_todo
    )

    if not df_cat_todo.empty:
        household_col = df_cat_todo["household_id"]
        df_cat = df_cat_todo[
            (df_cat_todo["user_email"] == email)
            & (
                household_col.isna()
                | (household_col.astype(str) == "None")
                | (household_col.astype(str) == "")
            )
        ]
    else:
        df_cat = df_cat_todo

# ============================================================
# RESUMEN
# ============================================================
with tab1:
    st.subheader("Tu mes de un vistazo")

    if tc_usd_cop:
        st.markdown(
            f"""
<div class="currency-box">
    <b>💱 Tipo de cambio real</b>
    <div class="currency-rate">
        1 USD = <b>{tc_usd_cop:,.2f} COP</b> ·
        fuente: {fuente_fx} ·
        consulta: {pd.Timestamp.now().strftime("%d/%m/%Y %H:%M")}
    </div>
</div>
""",
            unsafe_allow_html=True,
        )

    señales, detalle_señales = cargar_contexto_economico()

    if detalle_señales:
        if señales == 0:
            st.markdown(
                """
<div class="insight-card insight-buena">
🟢 <b>Contexto económico:</b>
los indicadores públicos de recesión no muestran alerta activa por ahora.
</div>
""",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
<div class="insight-card insight-alerta">
🟡 <b>Contexto económico:</b>
{señales} de {len(detalle_señales)} indicadores públicos
están en zona de alerta.
</div>
""",
                unsafe_allow_html=True,
            )

        if es_pro:
            with st.expander("Ver detalle de indicadores"):
                for nombre, valor, activo, texto in detalle_señales:
                    st.write(
                        ("🔴" if activo else "🟢")
                        + f" **{nombre}**: {texto}"
                    )
        else:
            st.caption(
                "✨ El detalle de cada indicador está en el plan Pro."
            )

    hoy = pd.Timestamp.today()

    if df_tx.empty:
        st.info(
            "Aún no tienes movimientos registrados. "
            "Ve a **➕ Registrar** para agregar el primero."
        )
    else:
        df_tx = df_tx.copy()
        df_tx["mes"] = df_tx["fecha"].dt.to_period("M")

        mes_actual = hoy.to_period("M")
        mes_anterior = mes_actual - 1

        df_mes = df_tx[df_tx["mes"] == mes_actual]
        df_mes_ant = df_tx[df_tx["mes"] == mes_anterior]

        gasto_categorias = (
            set(df_cat[df_cat["tipo"] == "gasto"]["name"])
            if not df_cat.empty
            else set()
        )

        ingreso_categorias = (
            set(df_cat[df_cat["tipo"] == "ingreso"]["name"])
            if not df_cat.empty
            else set()
        )

        if not gasto_categorias:
            gasto_mask = df_mes["monto"] < 0
        else:
            gasto_mask = df_mes["categoria"].isin(gasto_categorias)

        if not ingreso_categorias:
            ingreso_mask = df_mes["monto"] > 0
        else:
            ingreso_mask = df_mes["categoria"].isin(ingreso_categorias)

        total_gasto = (
            -df_mes.loc[gasto_mask, "monto"].sum()
            if not df_mes.empty
            else 0
        )

        total_ingreso = (
            df_mes.loc[ingreso_mask, "monto"].sum()
            if not df_mes.empty
            else 0
        )

        balance = total_ingreso - total_gasto

        m1, m2, m3 = st.columns(3)

        m1.metric(
            "Ingresos del mes",
            dinero(total_ingreso),
        )

        m2.metric(
            "Gastos del mes",
            dinero(total_gasto),
        )

        m3.metric(
            "Balance",
            dinero(balance),
            delta="Positivo" if balance >= 0 else "Negativo",
            delta_color="normal" if balance >= 0 else "inverse",
        )

        tasa_ahorro = (
            balance / total_ingreso
            if total_ingreso > 0
            else 0
        )

        presupuestos_activos = (
            df_cat[
                (df_cat["tipo"] == "gasto")
                & df_cat["presupuesto_mensual"].notna()
            ]
            if not df_cat.empty
            else pd.DataFrame()
        )

        gastos_por_cat_actual = (
            df_mes[
                df_mes["categoria"].isin(gasto_categorias)
            ]
            .groupby("categoria")["monto"]
            .sum()
            .abs()
        )

        if not presupuestos_activos.empty:
            cumplidos = sum(
                1
                for _, fila in presupuestos_activos.iterrows()
                if gastos_por_cat_actual.get(fila["name"], 0)
                <= float(fila["presupuesto_mensual"])
            )
            pct_presupuesto_ok = (
                cumplidos / len(presupuestos_activos)
            )
        else:
            pct_presupuesto_ok = 0.7

        puntaje_salud = round(
            min(
                100,
                max(
                    0,
                    min(max(tasa_ahorro, 0), 1) * 60
                    + pct_presupuesto_ok * 40,
                ),
            )
        )

        col_gauge, col_dona = st.columns([0.9, 1.45])

        with col_gauge:
            st.markdown("#### 💚 Salud financiera")
            st.plotly_chart(
                grafico_salud_financiera(puntaje_salud),
                use_container_width=True,
                config={"displayModeBar": False},
            )

            if puntaje_salud >= 70:
                st.caption("Vas muy bien este mes.")
            elif puntaje_salud >= 40:
                st.caption(
                    "Vas en terreno neutral — hay margen para ajustar."
                )
            else:
                st.caption(
                    "Este mes viene apretado. Revisa tus categorías."
                )

        with col_dona:
            st.markdown("#### Gasto por categoría este mes")

            if gasto_categorias:
                gastos_mes = (
                    df_mes[
                        df_mes["categoria"].isin(gasto_categorias)
                    ]
                    .groupby("categoria")["monto"]
                    .sum()
                    .abs()
                    .sort_values(ascending=False)
                )
            else:
                gastos_mes = (
                    df_mes[df_mes["monto"] < 0]
                    .groupby("categoria")["monto"]
                    .sum()
                    .abs()
                    .sort_values(ascending=False)
                )

            if not gastos_mes.empty:
                colores = [
                    PALETA_CATEGORIAS[
                        i % len(PALETA_CATEGORIAS)
                    ]
                    for i in range(len(gastos_mes))
                ]

                valores_visual = [
                    a_moneda(v) for v in gastos_mes.values
                ]

                fig = go.Figure(
                    go.Pie(
                        labels=gastos_mes.index,
                        values=valores_visual,
                        hole=0.58,
                        marker=dict(
                            colors=colores,
                            line=dict(
                                color=TARJETA,
                                width=2,
                            ),
                        ),
                        textinfo="percent",
                        textfont=dict(
                            family="Inter",
                            size=12,
                            color="white",
                        ),
                    )
                )

                fig = estilo_grafico(fig, height=320)
                fig.update_layout(showlegend=False)

                fig.add_annotation(
                    text=(
                        f"{dinero(gastos_mes.sum())}"
                        f"<br><span style='font-size:11px;"
                        f"color:{TEXTO_SUAVE}'>total</span>"
                    ),
                    showarrow=False,
                    font=dict(
                        family="JetBrains Mono",
                        size=18,
                        color=TEXTO,
                    ),
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    config={"displayModeBar": False},
                )

                chips = "".join(
                    f'<span class="cat-chip">'
                    f'{icono_categoria(cat)} {cat} · '
                    f'{dinero(monto)}'
                    f"</span>"
                    for cat, monto in gastos_mes.items()
                )

                st.markdown(
                    chips,
                    unsafe_allow_html=True,
                )
            else:
                st.caption(
                    "Sin gastos categorizados este mes todavía."
                )

        total_ingreso_ant = (
            df_mes_ant[
                df_mes_ant["categoria"].isin(
                    ingreso_categorias
                )
            ]["monto"].sum()
            if not df_mes_ant.empty
            else 0
        )

        total_gasto_ant = (
            -df_mes_ant[
                df_mes_ant["categoria"].isin(
                    gasto_categorias
                )
            ]["monto"].sum()
            if not df_mes_ant.empty
            else 0
        )

        tasa_ahorro_ant = (
            (total_ingreso_ant - total_gasto_ant)
            / total_ingreso_ant
            if total_ingreso_ant > 0
            else None
        )

        categoria_top = (
            (gastos_mes.index[0], gastos_mes.iloc[0])
            if not gastos_mes.empty
            else None
        )

        resumen = generar_resumen_narrado(
            total_ingreso,
            total_gasto,
            balance,
            tasa_ahorro,
            tasa_ahorro_ant,
            categoria_top,
        )

        st.markdown(
            f"""
<div class="insight-card">
📝 <b>Tu mes en resumen:</b> {resumen}
</div>
""",
            unsafe_allow_html=True,
        )

        if es_pro:
            st.markdown("#### Tendencia últimos 6 meses")

            df_tx["mes_str"] = df_tx["mes"].astype(str)
            ult_6 = sorted(
                df_tx["mes_str"].dropna().unique()
            )[-6:]

            if gasto_categorias:
                serie = (
                    df_tx[
                        df_tx["mes_str"].isin(ult_6)
                        & df_tx["categoria"].isin(
                            gasto_categorias
                        )
                    ]
                    .groupby("mes_str")["monto"]
                    .sum()
                    .abs()
                )
            else:
                serie = (
                    df_tx[
                        df_tx["mes_str"].isin(ult_6)
                        & (df_tx["monto"] < 0)
                    ]
                    .groupby("mes_str")["monto"]
                    .sum()
                    .abs()
                )

            serie = serie.sort_index()

            if not serie.empty:
                fig2 = go.Figure(
                    go.Scatter(
                        x=serie.index,
                        y=[a_moneda(v) for v in serie.values],
                        line=dict(
                            color=PINO,
                            width=3,
                        ),
                        fill="tozeroy",
                        fillcolor="rgba(31,77,61,.08)",
                        mode="lines+markers",
                        marker=dict(
                            size=7,
                            color=GOLD,
                            line=dict(
                                width=2,
                                color=PINO,
                            ),
                        ),
                        hovertemplate=(
                            "%{x}<br>"
                            + simbolo_moneda()
                            + " %{y:,.0f}<extra></extra>"
                        ),
                    )
                )

                fig2 = estilo_grafico(fig2, height=280)

                st.plotly_chart(
                    fig2,
                    use_container_width=True,
                    config={"displayModeBar": False},
                )

            st.markdown("#### 💡 Insights")

            if gasto_categorias:
                comp_actual = (
                    df_mes[
                        df_mes["categoria"].isin(
                            gasto_categorias
                        )
                    ]
                    .groupby("categoria")["monto"]
                    .sum()
                    .abs()
                )
            else:
                comp_actual = (
                    df_mes[df_mes["monto"] < 0]
                    .groupby("categoria")["monto"]
                    .sum()
                    .abs()
                )

            if not df_mes_ant.empty:
                if gasto_categorias:
                    comp_anterior = (
                        df_mes_ant[
                            df_mes_ant["categoria"].isin(
                                gasto_categorias
                            )
                        ]
                        .groupby("categoria")["monto"]
                        .sum()
                        .abs()
                    )
                else:
                    comp_anterior = (
                        df_mes_ant[
                            df_mes_ant["monto"] < 0
                        ]
                        .groupby("categoria")["monto"]
                        .sum()
                        .abs()
                    )

                for cat in comp_actual.index:
                    if (
                        cat in comp_anterior.index
                        and comp_anterior[cat] > 0
                    ):
                        cambio = (
                            comp_actual[cat]
                            / comp_anterior[cat]
                            - 1
                        ) * 100

                        if abs(cambio) >= 20:
                            clase = (
                                "insight-alerta"
                                if cambio > 0
                                else "insight-buena"
                            )
                            direccion = (
                                "más"
                                if cambio > 0
                                else "menos"
                            )

                            st.markdown(
                                f"""
<div class="insight-card {clase}">
{icono_categoria(cat)}
Gastaste <b>{abs(cambio):.0f}% {direccion}</b>
en <b>{cat}</b> que el mes pasado.
</div>
""",
                                unsafe_allow_html=True,
                            )

            if not df_cat.empty:
                presupuestos = df_cat[
                    (df_cat["tipo"] == "gasto")
                    & df_cat["presupuesto_mensual"].notna()
                ]

                for _, fila in presupuestos.iterrows():
                    gastado = comp_actual.get(
                        fila["name"],
                        0,
                    )
                    presupuesto = float(
                        fila["presupuesto_mensual"]
                    )

                    if presupuesto and gastado > presupuesto:
                        st.markdown(
                            f"""
<div class="insight-card insight-alerta">
{icono_categoria(fila["name"])}
Ya superaste tu presupuesto de
<b>{fila["name"]}</b>:
<b>{dinero(gastado)}</b> de
<b>{dinero(presupuesto)}</b>.
</div>
""",
                            unsafe_allow_html=True,
                        )
        else:
            st.info(
                "✨ Los insights automáticos y la tendencia de 6 meses están en Pro."
            )


# ============================================================
# REGISTRAR
# ============================================================
with tab2:
    st.subheader("Registrar un movimiento")

    st.caption(
        f"Los importes se guardarán internamente en COP. "
        f"Ahora mismo estás introduciendo valores en **{st.session_state['moneda']}**."
    )

    with st.form("form_transaccion", clear_on_submit=True):
        c1, c2 = st.columns(2)

        with c1:
            fecha_tx = st.date_input(
                "Fecha",
                value=date.today(),
            )

            tipo_tx = st.radio(
                "Tipo",
                ["Gasto", "Ingreso"],
                horizontal=True,
            )

        with c2:
            monto_tx = st.number_input(
                f"Monto ({st.session_state['moneda']})",
                min_value=0.0,
                step=10.0,
            )

            descripcion_tx = st.text_input(
                "Descripción",
                placeholder="Ej: supermercado, Uber, arriendo",
            )

        tipo_categoria = (
            "gasto" if tipo_tx == "Gasto" else "ingreso"
        )

        categorias_disponibles = (
            df_cat[
                df_cat["tipo"] == tipo_categoria
            ]["name"].tolist()
            if not df_cat.empty
            else []
        )

        sugerida = (
            auto_categorizar(descripcion_tx)
            if tipo_tx == "Gasto"
            else "Salario"
        )

        indice_sugerido = (
            categorias_disponibles.index(sugerida)
            if sugerida in categorias_disponibles
            else 0
        )

        categoria_tx = st.selectbox(
            "Categoría",
            categorias_disponibles
            or (
                ["Otros gastos"]
                if tipo_tx == "Gasto"
                else ["Otros ingresos"]
            ),
            index=indice_sugerido,
        )

        compartir_tx = False

        if hogar and es_pro:
            compartir_tx = st.checkbox(
                f"Compartir con mi hogar ({hogar['nombre']})"
            )

        guardar = st.form_submit_button(
            "Guardar movimiento"
        )

    if guardar:
        if not supabase:
            st.error(
                "Sin conexión a base de datos."
            )
        elif monto_tx <= 0:
            st.error(
                "El monto debe ser mayor que 0."
            )
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
                supabase.table("transactions").insert(
                    registro
                ).execute()

                st.success(
                    f"Movimiento guardado: "
                    f"{dinero_desde_valor(monto_tx)} "
                    f"({dinero(monto_cop)} base)."
                )

                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.error(
                    f"No se pudo guardar: {e}"
                )

    st.divider()
    st.markdown("#### Movimientos recientes")

    if not df_tx.empty:
        df_mostrar = df_tx[
            [
                "fecha",
                "categoria",
                "descripcion",
                "monto",
            ]
        ].head(20).copy()

        df_mostrar["fecha"] = (
            pd.to_datetime(df_mostrar["fecha"])
            .dt.strftime("%d/%m/%Y")
        )

        df_mostrar["categoria"] = (
            df_mostrar["categoria"]
            .apply(
                lambda c:
                f"{icono_categoria(c)} {c}"
                if pd.notna(c)
                else c
            )
        )

        df_mostrar["monto"] = df_mostrar[
            "monto"
        ].apply(dinero)

        df_mostrar.columns = [
            "Fecha",
            "Categoría",
            "Descripción",
            "Monto",
        ]

        st.dataframe(
            df_mostrar,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.caption(
            "Sin movimientos todavía."
        )


# ============================================================
# IMPORTAR CSV
# ============================================================
with tab3:
    st.subheader("📥 Importar movimientos desde CSV")

    if not es_pro:
        st.info(
            "✨ La importación de CSV está en el plan Pro."
        )
    else:
        st.caption(
            f"Los importes del archivo se interpretarán como "
            f"**{st.session_state['moneda']}** y se convertirán a COP "
            f"con el tipo de cambio actual."
        )

        archivo = st.file_uploader(
            "Archivo CSV",
            type=["csv"],
        )

        if archivo:
            try:
                df_csv = pd.read_csv(archivo)
                cols = {
                    c.lower().strip(): c
                    for c in df_csv.columns
                }

                def encontrar_col(posibles):
                    for posible in posibles:
                        for c_lower, c_original in cols.items():
                            if posible in c_lower:
                                return c_original
                    return None

                col_fecha_detectada = encontrar_col(
                    ["fecha", "date"]
                )
                col_monto_detectada = encontrar_col(
                    [
                        "monto",
                        "amount",
                        "importe",
                        "cargo",
                        "abono",
                    ]
                )
                col_desc_detectada = encontrar_col(
                    [
                        "descripcion",
                        "concepto",
                        "description",
                        "detalle",
                    ]
                )

                st.write("Columnas detectadas:")

                c1, c2, c3 = st.columns(3)

                col_fecha = c1.selectbox(
                    "Columna de fecha",
                    df_csv.columns,
                    index=(
                        list(df_csv.columns).index(
                            col_fecha_detectada
                        )
                        if col_fecha_detectada
                        in df_csv.columns
                        else 0
                    ),
                )

                col_monto = c2.selectbox(
                    "Columna de monto",
                    df_csv.columns,
                    index=(
                        list(df_csv.columns).index(
                            col_monto_detectada
                        )
                        if col_monto_detectada
                        in df_csv.columns
                        else 0
                    ),
                )

                col_desc = c3.selectbox(
                    "Columna de descripción",
                    df_csv.columns,
                    index=(
                        list(df_csv.columns).index(
                            col_desc_detectada
                        )
                        if col_desc_detectada
                        in df_csv.columns
                        else 0
                    ),
                )

                df_prev = pd.DataFrame(
                    {
                        "fecha": pd.to_datetime(
                            df_csv[col_fecha],
                            errors="coerce",
                        ),
                        "monto_original": pd.to_numeric(
                            df_csv[col_monto],
                            errors="coerce",
                        ),
                        "descripcion": df_csv[
                            col_desc
                        ].astype(str),
                    }
                ).dropna(
                    subset=[
                        "fecha",
                        "monto_original",
                    ]
                )

                df_prev["categoria"] = (
                    df_prev["descripcion"]
                    .apply(auto_categorizar)
                )

                def convertir_csv(row):
                    valor_cop = a_cop(
                        abs(row["monto_original"])
                    )

                    if row["categoria"] in [
                        c[0]
                        for c in CATEGORIAS_DEFECTO
                        if c[1] == "gasto"
                    ]:
                        return -valor_cop

                    return (
                        valor_cop
                        if row["monto_original"] >= 0
                        else -valor_cop
                    )

                df_prev["monto"] = df_prev.apply(
                    convertir_csv,
                    axis=1,
                )

                st.markdown(
                    f"**Vista previa** "
                    f"({len(df_prev)} movimientos detectados):"
                )

                preview = df_prev[
                    [
                        "fecha",
                        "categoria",
                        "descripcion",
                        "monto",
                    ]
                ].head(15).copy()

                preview["monto"] = preview[
                    "monto"
                ].apply(dinero)

                st.dataframe(
                    preview,
                    use_container_width=True,
                    hide_index=True,
                )

                if st.button(
                    f"Importar {len(df_prev)} movimientos",
                    key="importar_csv",
                ):
                    registros = []

                    for _, row in df_prev.iterrows():
                        registros.append(
                            {
                                "user_email": email,
                                "fecha": row[
                                    "fecha"
                                ].date().isoformat(),
                                "monto": float(
                                    row["monto"]
                                ),
                                "categoria": row[
                                    "categoria"
                                ],
                                "descripcion": row[
                                    "descripcion"
                                ],
                                "fuente": "csv",
                            }
                        )

                    try:
                        supabase.table(
                            "transactions"
                        ).insert(registros).execute()

                        st.success(
                            f"{len(registros)} movimientos importados."
                        )

                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(
                            f"Error al importar: {e}"
                        )

            except Exception as e:
                st.error(
                    f"No se pudo leer el CSV: {e}"
                )


# ============================================================
# PRESUPUESTOS (Con Presupuesto vs Gasto y Eliminar Categoría)
# ============================================================
with tab4:
    st.subheader("🎯 Presupuestos y Control por Categoría")

    if not es_pro:
        st.info(
            "✨ Los presupuestos por categoría están en el plan Pro."
        )
    elif df_cat.empty:
        st.caption(
            "Aún no tienes categorías."
        )
    else:
        # ── NUEVO: Tabla comparativa Presupuesto vs Gasto ──
        st.markdown("#### 📊 Presupuesto vs. Gasto Actual")
        
        # Calcular gastos reales del mes actual
        hoy = pd.Timestamp.today()
        mes_actual = hoy.to_period("M")
        df_tx_copia = df_tx.copy()
        if not df_tx_copia.empty and "fecha" in df_tx_copia.columns:
            df_tx_copia["mes"] = pd.to_datetime(df_tx_copia["fecha"]).dt.to_period("M")
            df_mes_actual = df_tx_copia[df_tx_copia["mes"] == mes_actual]
            gastos_reales_cat = df_mes_actual.groupby("categoria")["monto"].sum().abs()
        else:
            gastos_reales_cat = pd.Series(dtype=float)

        tabla_comparativa = df_cat[df_cat["tipo"] == "gasto"].copy()
        tabla_comparativa["Gastado"] = tabla_comparativa["name"].map(gastos_reales_cat).fillna(0)
        
        # Mostrar tabla organizada
        df_mostrar_comp = tabla_comparativa[["name", "presupuesto_mensual", "Gastado"]].copy()
        df_mostrar_comp["presupuesto_mensual"] = df_mostrar_comp["presupuesto_mensual"].fillna(0).apply(dinero)
        df_mostrar_comp["Gastado"] = df_mostrar_comp["Gastado"].apply(dinero)
        df_mostrar_comp.columns = ["Categoría", "Presupuesto", "Gasto Actual"]
        
        st.dataframe(df_mostrar_comp, use_container_width=True, hide_index=True)
        st.divider()

        st.markdown("#### ⚙️ Ajustar Presupuestos")
        for _, fila in df_cat[
            df_cat["tipo"] == "gasto"
        ].iterrows():

            col1, col2 = st.columns(
                [2, 1]
            )

            col1.write(
                f"{icono_categoria(fila['name'])} "
                f"{fila['name']}"
            )

            valor_base = (
                float(
                    fila["presupuesto_mensual"]
                )
                if pd.notna(
                    fila["presupuesto_mensual"]
                )
                else 0.0
            )

            valor_visual = a_moneda(
                valor_base
            )

            nuevo_valor = col2.number_input(
                f"Presupuesto {fila['name']}",
                min_value=0.0,
                step=50.0,
                value=float(
                    round(valor_visual, 2)
                ),
                key=f"presu_{fila['name']}",
                label_visibility="collapsed",
            )

            nuevo_base = a_cop(
                nuevo_valor
            )

            if abs(nuevo_base - valor_base) > 0.01:
                try:
                    (
                        supabase.table("categories")
                        .update(
                            {
                                "presupuesto_mensual": nuevo_base
                            }
                        )
                        .eq("id", fila["id"])
                        .execute()
                    )

                    st.cache_data.clear()
                except Exception as e:
                    st.error(
                        f"No se pudo actualizar: {e}"
                    )

    if es_pro:
        st.divider()
        st.markdown(
            "#### Agregar categoría nueva"
        )

        nueva_cat = st.text_input(
            "Nombre de la categoría"
        )

        if st.button(
            "Agregar categoría",
            key="agregar_categoria",
        ) and nueva_cat.strip():

            try:
                supabase.table(
                    "categories"
                ).insert(
                    {
                        "user_email": email,
                        "name": nueva_cat.strip(),
                        "tipo": "gasto",
                    }
                ).execute()

                st.success(
                    f"Categoría '{nueva_cat.strip()}' agregada."
                )

                st.cache_data.clear()
                st.rerun()

            except Exception as e:
                st.error(
                    f"No se pudo agregar: {e}"
                )

        # ── NUEVO: Opción para eliminar categoría ──
        st.divider()
        st.markdown("#### 🗑️ Eliminar Categoría")
        
        categorias_disponibles_borrar = df_cat["name"].tolist() if not df_cat.empty else []
        if categorias_disponibles_borrar:
            cat_a_borrar = st.selectbox("Selecciona la categoría a eliminar", categorias_disponibles_borrar, key="select_borrar_cat")
            
            if st.button("Eliminar categoría seleccionada", key="btn_borrar_cat"):
                try:
                    supabase.table("categories").delete().eq("name", cat_a_borrar).eq("user_email", email).execute()
                    st.success(f"La categoría '{cat_a_borrar}' ha sido eliminada.")
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"No se pudo eliminar la categoría: {e}")
        else:
            st.caption("No hay categorías disponibles para eliminar.")


# ============================================================
# EDUCACIÓN
# ============================================================
with tab5:
    st.subheader("📚 Educación Financiera")

    st.caption(
        "Información general para entender mejor tus finanzas. "
        "No es asesoría de inversión."
    )

    conceptos = [
        (
            "Regla 50/30/20",
            "Una guía común para repartir el ingreso: 50% en necesidades, "
            "30% en gustos y 20% en ahorro o pago de deudas. "
            "Es un punto de partida, no una regla fija.",
        ),
        (
            "Fondo de emergencia",
            "Dinero guardado aparte para imprevistos. "
            "Una referencia común es cubrir entre 3 y 6 meses "
            "de gastos básicos.",
        ),
        (
            "Interés compuesto",
            "Cuando los intereses que ganas o debes también generan "
            "intereses. Con el tiempo, este efecto puede crecer "
            "de forma acelerada.",
        ),
        (
            "Score o historial crediticio",
            "Registro de cómo has manejado créditos en el pasado. "
            "Las entidades financieras pueden usarlo para evaluar "
            "solicitudes de crédito.",
        ),
        (
            "Deuda cara",
            "No toda deuda cuesta lo mismo. Las deudas con tasas altas "
            "pueden consumir una parte importante del flujo mensual.",
        ),
    ]

    for titulo, texto in conceptos:
        with st.expander(titulo):
            st.write(texto)


# ============================================================
# HOGAR
# ============================================================
with tab6:
    st.subheader("🏠 Mi Hogar")

    st.caption(
        "Comparte presupuesto con tu pareja o familia y decide "
        "qué movimientos permanecen privados."
    )

    if not es_pro:
        st.info(
            "✨ Los hogares compartidos están en el plan Pro."
        )

    elif not hogar:
        st.markdown("#### Crear un hogar")

        nombre_hogar = st.text_input(
            "Nombre del hogar",
            placeholder="Ej: Casa de Ana y Luis",
        )

        if st.button(
            "Crear hogar",
            key="crear_hogar",
        ) and nombre_hogar.strip():

            ok, err = crear_hogar(
                email,
                nombre_hogar.strip(),
            )

            if ok:
                st.success(
                    "Hogar creado. Ahora puedes invitar a alguien."
                )
                st.cache_data.clear()
                st.rerun()
            else:
                st.error(
                    f"No se pudo crear: {err}"
                )

    else:
        st.markdown(
            f"#### {hogar['nombre']}"
        )

        st.write("**Miembros:**")

        for m in hogar["miembros"]:
            etiqueta = (
                "👑 Dueño"
                if m["role"] == "owner"
                else "Miembro"
            )

            c1, c2 = st.columns(
                [3, 1]
            )

            c1.write(
                f"{m['user_email']} — {etiqueta}"
            )

            if (
                hogar["rol"] == "owner"
                and m["user_email"] != email
            ):
                if c2.button(
                    "Quitar",
                    key=f"quitar_{m['user_email']}",
                ):
                    ok, err = quitar_miembro(
                        hogar["id"],
                        m["user_email"],
                    )

                    if ok:
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(err)

        if hogar["rol"] == "owner":
            st.divider()
            st.markdown(
                "#### Invitar a alguien"
            )

            correo_nuevo = st.text_input(
                "Correo de la persona a invitar"
            )

            if st.button(
                "Invitar",
                key="invitar_hogar",
            ) and correo_nuevo.strip():

                ok, err = invitar_miembro(
                    hogar["id"],
                    correo_nuevo.strip(),
                )

                if ok:
                    st.success(
                        f"{correo_nuevo.strip()} agregado al hogar."
                    )
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error(
                        f"No se pudo invitar: {err}"
                    )

        st.divider()

        st.caption(
            "💡 En ➕ Registrar puedes marcar un gasto como "
            "compartido con el hogar."
        )


# ============================================================
# LEGAL
# ============================================================
with tab7:
    st.subheader("⚖️ Legal")

    st.warning(
        "⚠️ Este texto es una plantilla de referencia y debe "
        "ser revisado por un abogado antes de operar con usuarios reales."
    )

    with st.expander(
        "📄 Términos de Servicio"
    ):
        st.markdown(
            f"""
**Última actualización:** {date.today().strftime("%d/%m/%Y")}

**1. Qué es FinZen**

FinZen es una herramienta de organización financiera personal:
registro de gastos e ingresos, presupuestos y educación financiera general.

**2. Lo que FinZen NO es**

FinZen no es un asesor de inversión registrado, no ofrece asesoría
financiera personalizada y no recomienda comprar, vender o mantener
instrumentos financieros.

**3. Planes y pagos**

El plan Pro es una suscripción recurrente procesada por Stripe.
El precio mostrado actualmente es de $6.99/mes.

**4. Exactitud de los datos**

Los datos dependen de la información que el usuario registra o importa.

**5. Tipo de cambio**

La conversión COP/USD utiliza una tasa de referencia consultada
desde un proveedor externo. No representa necesariamente el precio
final que un banco, tarjeta o casa de cambio aplicará a una operación.

**6. Limitación de responsabilidad**

FinZen se ofrece "tal cual". La información de la aplicación no
constituye asesoría financiera personalizada.

**7. Cambios**

Estos términos pueden actualizarse cuando sea necesario.
"""
        )

    with st.expander(
        "🔒 Aviso de Privacidad"
    ):
        st.markdown(
            """
**Datos recopilados**

- Correo electrónico.
- Transacciones registradas o importadas.
- Categorías y presupuestos.
- Información del hogar compartido cuando el usuario lo utiliza.

**Datos bancarios**

FinZen no solicita credenciales bancarias ni almacena números
de tarjetas bancarias.

**Pagos**

Los pagos Pro son procesados por Stripe.

**Almacenamiento**

Los datos de la aplicación pueden almacenarse en Supabase/PostgreSQL
cuando la base de datos está configurada.

**Contacto**

Agrega aquí el correo oficial de soporte de FinZen.
"""
        )

    st.info(
        "💡 El contexto económico mostrado en FinZen es informativo "
        "y educativo, no una señal de compra o venta."
    )

# ============================================================
# PIE
# ============================================================
st.divider()

fx_texto = (
    f"1 USD = {tc_usd_cop:,.2f} COP"
    if tc_usd_cop
    else "Tipo de cambio temporalmente no disponible"
)

st.caption(
    f"🌱 FinZen · Moneda: {st.session_state['moneda']} · {fx_texto}"
)
