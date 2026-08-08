import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io
import re
import math
import requests
from datetime import date, datetime

# ============================================================
# FINZEN
# Finanzas personales — COP / USD
# ============================================================

st.set_page_config(
    page_title="FinZen | Tu compañero de finanzas",
    layout="wide",
    page_icon="🌱",
    initial_sidebar_state="expanded",
)

# ============================================================
# IMPORTACIONES OPCIONALES
# ============================================================

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

try:
    REQUESTS_AVAILABLE = True
except Exception:
    REQUESTS_AVAILABLE = False


# ============================================================
# CONFIGURACIÓN
# ============================================================

STRIPE_PAYMENT_LINK = "https://buy.stripe.com/tu-link-de-pago"

# Moneda interna:
# TODA la información financiera se almacena en COP.
MONEDA_BASE = "COP"

MONEDAS = {
    "COP": {
        "nombre": "Peso colombiano",
        "simbolo": "$",
        "flag": "🇨🇴",
        "decimales": 0,
    },
    "USD": {
        "nombre": "Dólar estadounidense",
        "simbolo": "US$",
        "flag": "🇺🇸",
        "decimales": 2,
    },
}

# ============================================================
# PALETA FINZEN
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
    PINO,
    CORAL,
    GOLD,
    CIELO,
    SALVIA,
    CIRUELA,
    LADRILLO,
    "#3D6B7D",
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


def icono_categoria(nombre):
    return ICONOS_CATEGORIA.get(nombre, "🏷️")


# ============================================================
# CSS
# ============================================================

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

header {{
    visibility: hidden;
}}

h1, h2, h3, h4 {{
    font-family: 'Quicksand', sans-serif !important;
    font-weight: 700 !important;
    color: {PINO} !important;
}}

@keyframes fadeInUp {{
    from {{
        opacity: 0;
        transform: translateY(6px);
    }}
    to {{
        opacity: 1;
        transform: translateY(0);
    }}
}}

@media (prefers-reduced-motion: reduce) {{
    * {{
        animation: none !important;
        transition: none !important;
    }}
}}

/* ========================================================
   HERO
   ======================================================== */

.hero-banner {{
    background:
        linear-gradient(
            135deg,
            {PINO} 0%,
            {PINO_CLARO} 55%,
            {CIELO} 130%
        );
    border-radius: 22px;
    padding: 28px 30px;
    margin-bottom: 22px;
    color: white;
    box-shadow: 0 8px 24px rgba(31,77,61,0.18);
    animation: fadeInUp 0.4s ease;
}}

.hero-banner h1 {{
    color: white !important;
    margin: 0 0 4px 0;
    font-size: 28px !important;
}}

.hero-banner p {{
    color: rgba(255,255,255,0.88) !important;
    margin: 0;
    font-size: 14.5px;
}}

.hero-pill {{
    display: inline-block;
    background: rgba(255,255,255,0.16);
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 12px;
    font-weight: 600;
    margin-top: 10px;
}}

/* ========================================================
   MÉTRICAS
   ======================================================== */

div[data-testid="stMetric"] {{
    background: {TARJETA};
    border: 1px solid {BORDE};
    border-radius: 16px;
    padding: 16px 18px;
    box-shadow: 0 2px 8px rgba(43,38,32,0.05);
}}

div[data-testid="stMetricLabel"] {{
    font-family: 'Inter', sans-serif;
    font-size: 12.5px !important;
    color: {TEXTO_SUAVE} !important;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}}

div[data-testid="stMetricValue"] {{
    font-family: 'JetBrains Mono', monospace !important;
    color: {TEXTO} !important;
    font-weight: 600 !important;
}}

/* ========================================================
   TABS
   ======================================================== */

button[data-baseweb="tab"] {{
    font-family: 'Quicksand', sans-serif;
    font-weight: 600;
    color: {TEXTO_SUAVE};
    border-radius: 10px 10px 0 0;
}}

button[data-baseweb="tab"][aria-selected="true"] {{
    color: {PINO} !important;
    border-bottom: 3px solid {PINO} !important;
    background: {ARENA};
}}

/* ========================================================
   BOTONES
   ======================================================== */

.stButton > button {{
    background: linear-gradient(135deg, {PINO}, {PINO_CLARO});
    color: white;
    border: none;
    border-radius: 12px;
    font-weight: 700;
    padding: 0.55rem 1.2rem;
    box-shadow: 0 3px 10px rgba(31,77,61,0.22);
}}

.stButton > button:hover {{
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(31,77,61,0.3);
    color: white;
}}

.stDownloadButton > button {{
    background: linear-gradient(135deg, {SALVIA}, {PINO_CLARO});
    color: white;
    border-radius: 12px;
    font-weight: 700;
    border: none;
}}

/* ========================================================
   INPUTS
   ======================================================== */

.stTextInput input,
.stNumberInput input,
.stDateInput input,
div[data-baseweb="select"] > div {{
    background-color: {TARJETA} !important;
    border: 1px solid {BORDE} !important;
    border-radius: 10px !important;
    color: {TEXTO} !important;
}}

/* ========================================================
   EXPANDERS / SIDEBAR
   ======================================================== */

div[data-testid="stExpander"] {{
    background-color: {TARJETA};
    border: 1px solid {BORDE};
    border-radius: 16px;
    box-shadow: 0 2px 6px rgba(43,38,32,0.04);
}}

section[data-testid="stSidebar"] {{
    background-color: {ARENA};
    border-right: 1px solid {BORDE};
}}

div[data-testid="stAlert"] {{
    background-color: {TARJETA} !important;
    border: 1px solid {BORDE} !important;
    border-left: 4px solid {PINO} !important;
    border-radius: 12px !important;
}}

hr {{
    border-color: {BORDE} !important;
}}

/* ========================================================
   CARDS
   ======================================================== */

.insight-card {{
    background: {TARJETA};
    border: 1px solid {BORDE};
    border-left: 4px solid {PINO};
    border-radius: 14px;
    padding: 14px 16px;
    margin-bottom: 10px;
    box-shadow: 0 2px 6px rgba(43,38,32,0.04);
}}

.insight-alerta {{
    border-left: 4px solid {CORAL} !important;
}}

.insight-buena {{
    border-left: 4px solid {SALVIA} !important;
}}

/* ========================================================
   MONEDA
   ======================================================== */

.currency-card {{
    background: {TARJETA};
    border: 1px solid {BORDE};
    border-radius: 16px;
    padding: 13px 16px;
    margin-bottom: 15px;
}}

.currency-rate {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    color: {PINO};
    font-weight: 600;
}}

.currency-date {{
    font-size: 11px;
    color: {TEXTO_SUAVE};
}}

/* ========================================================
   CATEGORÍAS
   ======================================================== */

.category-card {{
    background: {TARJETA};
    border: 1px solid {BORDE};
    border-radius: 15px;
    padding: 12px 14px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}}

.category-name {{
    font-weight: 700;
    color: {TEXTO};
}}

.category-amount {{
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    color: {PINO};
}}

.cat-chip {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: {ARENA};
    padding: 6px 11px;
    border-radius: 18px;
    font-size: 12.5px;
    font-weight: 600;
    color: {TEXTO};
    margin: 3px;
}}

/* ========================================================
   MOBILE
   ======================================================== */

@media (max-width: 768px) {{

    .hero-banner {{
        padding: 21px 18px;
        border-radius: 18px;
    }}

    .hero-banner h1 {{
        font-size: 23px !important;
    }}

    .hero-banner p {{
        font-size: 13px;
    }}

    div[data-testid="stMetric"] {{
        padding: 12px;
    }}

    div[data-testid="stMetricValue"] {{
        font-size: 19px !important;
    }}

    h2 {{
        font-size: 23px !important;
    }}

    h3 {{
        font-size: 20px !important;
    }}

    .category-card {{
        padding: 10px;
    }}
}}

::-webkit-scrollbar {{
    width: 8px;
    height: 8px;
}}

::-webkit-scrollbar-thumb {{
    background: {BORDE};
    border-radius: 10px;
}}

::-webkit-scrollbar-track {{
    background: {PAPEL};
}}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# FORMATO DE DINERO
# ============================================================

def formatear_numero(valor, moneda):
    try:
        valor = float(valor)
    except Exception:
        valor = 0.0

    if moneda == "USD":
        return f"US${valor:,.2f}"

    return f"${valor:,.0f}"


def formatear_monto_base(valor_cop, moneda, tasa_usd_cop):
    """
    Convierte un valor almacenado en COP a la moneda visual seleccionada.
    """
    try:
        valor_cop = float(valor_cop)
    except Exception:
        valor_cop = 0

    if moneda == "USD":
        if not tasa_usd_cop or tasa_usd_cop <= 0:
            return "US$0.00"
        return formatear_numero(valor_cop / tasa_usd_cop, "USD")

    return formatear_numero(valor_cop, "COP")


# ============================================================
# DIVISAS REALES
# ============================================================

@st.cache_data(ttl=1800, show_spinner=False)
def obtener_tasa_usd_cop():
    """
    Obtiene USD -> COP desde Frankfurter.

    Frankfurter:
    https://api.frankfurter.dev/v2/rate/USD/COP

    La API no requiere API key.
    La tasa corresponde al último día hábil disponible.
    """

    try:
        url = "https://api.frankfurter.dev/v2/rate/USD/COP"

        respuesta = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": "FinZen/1.0"
            }
        )

        respuesta.raise_for_status()

        data = respuesta.json()

        tasa = float(data["rate"])
        fecha = data.get("date", "")

        if tasa <= 0:
            raise ValueError("Tasa inválida")

        return {
            "rate": tasa,
            "date": fecha,
            "source": "Frankfurter",
            "ok": True,
        }

    except Exception as e:

        return {
            "rate": None,
            "date": None,
            "source": "Frankfurter",
            "ok": False,
            "error": str(e),
        }


def convertir_a_cop(monto, moneda):
    """
    Convierte el monto introducido por el usuario a COP.
    """

    monto = float(monto)

    if moneda == "COP":
        return monto, None

    datos = obtener_tasa_usd_cop()

    if not datos["ok"]:
        return None, "No fue posible obtener la tasa USD/COP."

    tasa = datos["rate"]

    return monto * tasa, tasa


# ============================================================
# SELECTOR DE MONEDA
# ============================================================

if "moneda_visual" not in st.session_state:
    st.session_state["moneda_visual"] = "COP"


def mostrar_selector_moneda():

    moneda_actual = st.session_state["moneda_visual"]

    seleccion = st.radio(
        "Moneda",
        options=["COP", "USD"],
        index=0 if moneda_actual == "COP" else 1,
        horizontal=True,
        format_func=lambda x: (
            "🇨🇴 COP — Pesos colombianos"
            if x == "COP"
            else "🇺🇸 USD — Dólares"
        ),
        key="selector_moneda",
    )

    st.session_state["moneda_visual"] = seleccion

    datos = obtener_tasa_usd_cop()

    if datos["ok"]:

        tasa = datos["rate"]

        if seleccion == "COP":
            texto = f"1 USD = {formatear_numero(tasa, 'COP')}"
        else:
            texto = f"1 USD = {formatear_numero(tasa, 'COP')} COP"

        st.markdown(
            f"""
            <div class="currency-card">
                <div class="currency-rate">💱 {texto}</div>
                <div class="currency-date">
                    Tasa real · {datos["source"]} · última fecha disponible: {datos["date"]}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    else:
        st.warning(
            "⚠️ No se pudo consultar la tasa de cambio. "
            "La aplicación continuará mostrando los valores almacenados en COP."
        )


# ============================================================
# GRÁFICOS
# ============================================================

def estilo_grafico(fig, titulo=None, height=360):

    fig.update_layout(
        template="plotly_white",
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Inter, sans-serif",
            color=TEXTO_SUAVE,
            size=12,
        ),
        title=dict(
            text=titulo,
            font=dict(
                family="Quicksand, sans-serif",
                color=PINO,
                size=17,
            ),
        ) if titulo else None,
        margin=dict(
            l=15,
            r=15,
            t=45 if titulo else 15,
            b=15,
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(
                color=TEXTO_SUAVE,
                size=11,
            ),
        ),
        xaxis=dict(
            gridcolor=BORDE,
            zerolinecolor=BORDE,
        ),
        yaxis=dict(
            gridcolor=BORDE,
            zerolinecolor=BORDE,
        ),
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
                "bar": {
                    "color": PINO,
                    "thickness": 0.30,
                },
                "bgcolor": "rgba(0,0,0,0)",
                "borderwidth": 0,
                "steps": [
                    {
                        "range": [0, 40],
                        "color": "rgba(232,115,74,0.18)",
                    },
                    {
                        "range": [40, 70],
                        "color": "rgba(217,164,65,0.18)",
                    },
                    {
                        "range": [70, 100],
                        "color": "rgba(127,182,158,0.25)",
                    },
                ],
            },
        )
    )

    fig.update_layout(
        height=200,
        margin=dict(l=20, r=20, t=5, b=5),
        paper_bgcolor="rgba(0,0,0,0)",
    )

    return fig


def grafico_dona_categorias(gastos_mes, moneda, tasa):

    valores = gastos_mes.values

    colores = [
        PALETA_CATEGORIAS[i % len(PALETA_CATEGORIAS)]
        for i in range(len(gastos_mes))
    ]

    total_cop = float(gastos_mes.sum())

    if moneda == "USD":
        total_visual = total_cop / tasa if tasa else 0
        total_texto = formatear_numero(total_visual, "USD")
    else:
        total_texto = formatear_numero(total_cop, "COP")

    fig = go.Figure(
        go.Pie(
            labels=gastos_mes.index.tolist(),
            values=valores,
            hole=0.58,
            marker=dict(
                colors=colores,
                line=dict(
                    color=TARJETA,
                    width=3,
                ),
            ),
            textinfo="percent",
            textposition="inside",
            insidetextorientation="auto",
            textfont=dict(
                family="Inter",
                size=13,
                color="white",
            ),
            hovertemplate=(
                "<b>%{label}</b><br>"
                "%{percent}<extra></extra>"
            ),
        )
    )

    fig = estilo_grafico(
        fig,
        height=350,
    )

    fig.update_layout(
        showlegend=False,
    )

    fig.add_annotation(
        text=(
            f"<b>{total_texto}</b>"
            f"<br>"
            f"<span style='font-size:11px;color:{TEXTO_SUAVE}'>total</span>"
        ),
        showarrow=False,
        font=dict(
            family="JetBrains Mono",
            size=20,
            color=TEXTO,
        ),
    )

    return fig


# ============================================================
# TEXTO RESUMEN
# ============================================================

def generar_resumen_narrado(
    total_ingreso,
    total_gasto,
    balance,
    tasa_ahorro,
    tasa_ahorro_ant,
    categoria_top,
    moneda,
    tasa,
):

    frases = []

    if total_ingreso == 0 and total_gasto == 0:
        return (
            "Todavía no hay suficientes movimientos este mes "
            "para armar un resumen."
        )

    ingreso = formatear_monto_base(
        total_ingreso,
        moneda,
        tasa,
    )

    gasto = formatear_monto_base(
        total_gasto,
        moneda,
        tasa,
    )

    bal = formatear_monto_base(
        abs(balance),
        moneda,
        tasa,
    )

    frases.append(
        f"Este mes llevas {ingreso} de ingresos y {gasto} "
        f"de gastos, con un balance "
        f"{'positivo' if balance >= 0 else 'negativo'} de {bal}."
    )

    if tasa_ahorro_ant is not None and total_ingreso > 0:

        diferencia_pp = (
            tasa_ahorro - tasa_ahorro_ant
        ) * 100

        if abs(diferencia_pp) >= 3:

            direccion = (
                "subió"
                if diferencia_pp > 0
                else "bajó"
            )

            frases.append(
                f"Tu tasa de ahorro {direccion} de "
                f"{tasa_ahorro_ant*100:.0f}% a "
                f"{tasa_ahorro*100:.0f}% respecto al mes pasado."
            )

    if categoria_top:

        nombre_top, monto_top = categoria_top

        pct = (
            monto_top / total_gasto * 100
            if total_gasto > 0
            else 0
        )

        monto_top_txt = formatear_monto_base(
            monto_top,
            moneda,
            tasa,
        )

        frases.append(
            f"{icono_categoria(nombre_top)} Tu mayor gasto fue "
            f"**{nombre_top}**, con {monto_top_txt} "
            f"({pct:.0f}% del total)."
        )

    return " ".join(frases)


# ============================================================
# CATEGORÍAS
# ============================================================

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

    "Supermercado": [
        "walmart",
        "soriana",
        "chedraui",
        "supermercado",
        "costco",
        "la comer",
        "aurrera",
        "exito",
        "carulla",
        "olimpica",
    ],

    "Restaurantes": [
        "restaurante",
        "starbucks",
        "mcdonald",
        "uber eats",
        "rappi",
        "cafe",
        "domino",
        "juan valdez",
    ],

    "Transporte": [
        "uber",
        "cabify",
        "didi",
        "gasolina",
        "gasolinera",
        "metro",
        "camion",
        "taxi",
        "transmilenio",
    ],

    "Suscripciones": [
        "netflix",
        "spotify",
        "disney",
        "hbo",
        "amazon prime",
        "youtube premium",
        "icloud",
    ],

    "Vivienda": [
        "renta",
        "hipoteca",
        "luz",
        "agua",
        "gas natural",
        "predial",
        "mantenimiento",
        "arriendo",
    ],

    "Salud": [
        "farmacia",
        "doctor",
        "hospital",
        "seguro medico",
        "dentista",
        "medicina",
    ],

    "Entretenimiento": [
        "cine",
        "boletos",
        "concierto",
        "videojuego",
        "steam",
    ],
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
# CONTEXTO ECONÓMICO
# ============================================================

@st.cache_data(ttl=3600)
def cargar_fred_csv(series_id, years=None):

    if not REQUESTS_AVAILABLE:
        return None

    try:

        resp = requests.get(
            f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}",
            timeout=10,
        )

        if resp.status_code != 200:
            return None

        df = pd.read_csv(
            io.StringIO(resp.text)
        )

        df.columns = [
            "Date",
            series_id,
        ]

        df["Date"] = pd.to_datetime(
            df["Date"]
        )

        df[series_id] = pd.to_numeric(
            df[series_id],
            errors="coerce",
        )

        df = df.dropna().set_index("Date")

        if years:
            df = df[
                df.index
                >= pd.Timestamp.today()
                - pd.DateOffset(years=years)
            ]

        return df if not df.empty else None

    except Exception:
        return None


@st.cache_data(ttl=3600)
def cargar_contexto_economico():

    señales = 0
    detalle = []

    dgs10 = cargar_fred_csv(
        "DGS10",
        years=1,
    )

    dgs3mo = cargar_fred_csv(
        "DGS3MO",
        years=1,
    )

    if dgs10 is not None and dgs3mo is not None:

        df = dgs10.join(
            dgs3mo,
            how="inner",
        ).dropna()

        if not df.empty:

            spread = (
                df["DGS10"].iloc[-1]
                - df["DGS3MO"].iloc[-1]
            )

            prob = (
                0.5
                * (
                    1
                    + math.erf(
                        (
                            -0.5333
                            - 0.6330 * spread
                        )
                        / math.sqrt(2)
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

    sahm = cargar_fred_csv(
        "SAHMREALTIME",
        years=2,
    )

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

    recprob = cargar_fred_csv(
        "RECPROUSM156N",
        years=2,
    )

    if recprob is not None and not recprob.empty:

        valor = recprob["RECPROUSM156N"].iloc[-1]

        activo = valor >= 50

        señales += int(activo)

        detalle.append(
            (
                "Modelo Chauvet-Piger",
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


# ============================================================
# AUTH
# ============================================================

def sign_in(email, password):

    try:

        res = supabase.auth.sign_in_with_password(
            {
                "email": email,
                "password": password,
            }
        )

        return res.user, None

    except Exception as e:
        return None, str(e)


def sign_up(email, password):

    try:

        res = supabase.auth.sign_up(
            {
                "email": email,
                "password": password,
            }
        )

        return res.user, None

    except Exception as e:
        return None, str(e)


def get_user_plan(email):

    if not supabase:
        return "free"

    try:

        res = (
            supabase
            .table("subscriptions")
            .select("status")
            .eq("user_email", email)
            .execute()
        )

        if res.data:
            return res.data[0].get(
                "status",
                "free",
            )

        (
            supabase
            .table("subscriptions")
            .insert(
                {
                    "user_email": email,
                    "status": "free",
                }
            )
            .execute()
        )

        return "free"

    except Exception:
        return "free"


def asegurar_categorias_defecto(email):

    if not supabase:
        return

    try:

        existentes = (
            supabase
            .table("categories")
            .select("name")
            .eq("user_email", email)
            .execute()
        )

        nombres_existentes = {
            c["name"]
            for c in existentes.data
        } if existentes.data else set()

        faltantes = [
            {
                "user_email": email,
                "name": nombre,
                "tipo": tipo,
            }
            for nombre, tipo in CATEGORIAS_DEFECTO
            if nombre not in nombres_existentes
        ]

        if faltantes:

            (
                supabase
                .table("categories")
                .insert(faltantes)
                .execute()
            )

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
            supabase
            .table("household_members")
            .select("household_id, role")
            .eq("user_email", email)
            .execute()
        )

        if not membresia.data:
            return None

        household_id = membresia.data[0]["household_id"]
        rol = membresia.data[0]["role"]

        hogar = (
            supabase
            .table("households")
            .select("*")
            .eq("id", household_id)
            .execute()
        )

        if not hogar.data:
            return None

        miembros = (
            supabase
            .table("household_members")
            .select(
                "user_email, role"
            )
            .eq(
                "household_id",
                household_id,
            )
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

        res = (
            supabase
            .table("households")
            .insert(
                {
                    "name": nombre,
                    "owner_email": email,
                }
            )
            .execute()
        )

        household_id = res.data[0]["id"]

        (
            supabase
            .table("household_members")
            .insert(
                {
                    "household_id": household_id,
                    "user_email": email,
                    "role": "owner",
                }
            )
            .execute()
        )

        return True, None

    except Exception as e:
        return False, str(e)


def invitar_miembro(
    household_id,
    email_nuevo,
):

    try:

        (
            supabase
            .table("household_members")
            .insert(
                {
                    "household_id": household_id,
                    "user_email": email_nuevo,
                    "role": "member",
                }
            )
            .execute()
        )

        return True, None

    except Exception as e:
        return False, str(e)


def quitar_miembro(
    household_id,
    email_miembro,
):

    try:

        (
            supabase
            .table("household_members")
            .delete()
            .eq(
                "household_id",
                household_id,
            )
            .eq(
                "user_email",
                email_miembro,
            )
            .execute()
        )

        return True, None

    except Exception as e:
        return False, str(e)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown("### 🌱 FinZen")

if not db_connected:

    st.sidebar.warning(
        "⚠️ Sin conexión a base de datos. "
        "Configura SUPABASE_URL y SUPABASE_KEY."
    )

elif not st.session_state["user"]:

    st.sidebar.markdown(
        "#### Inicia sesión o crea tu cuenta"
    )

    correo = st.sidebar.text_input(
        "Correo"
    )

    clave = st.sidebar.text_input(
        "Contraseña",
        type="password",
    )

    acepta_terminos = st.sidebar.checkbox(
        "Acepto los Términos de Servicio y el Aviso de Privacidad."
    )

    c1, c2 = st.sidebar.columns(2)

    with c1:

        if st.button(
            "Entrar",
            use_container_width=True,
        ):

            if correo and clave:

                user, err = sign_in(
                    correo,
                    clave,
                )

                if user:

                    st.session_state["user"] = user.email

                    st.session_state["plan"] = get_user_plan(
                        user.email
                    )

                    asegurar_categorias_defecto(
                        user.email
                    )

                    st.rerun()

                else:

                    st.sidebar.error(
                        f"No se pudo iniciar sesión: {err}"
                    )

            else:

                st.sidebar.error(
                    "Ingresa correo y contraseña."
                )

    with c2:

        if st.button(
            "Crear cuenta",
            use_container_width=True,
        ):

            if not acepta_terminos:

                st.sidebar.error(
                    "Debes aceptar los Términos y el Aviso de Privacidad."
                )

            elif correo and clave:

                user, err = sign_up(
                    correo,
                    clave,
                )

                if user:

                    st.sidebar.success(
                        "Cuenta creada. Inicia sesión."
                    )

                else:

                    st.sidebar.error(
                        f"No se pudo registrar: {err}"
                    )

            else:

                st.sidebar.error(
                    "Ingresa correo y contraseña."
                )

else:

    st.sidebar.success(
        f"Hola, **{st.session_state['user']}**"
    )

    if st.session_state["plan"] == "pro":

        st.sidebar.markdown(
            '<span class="pro-badge">PRO</span>',
            unsafe_allow_html=True,
        )

    else:

        st.sidebar.markdown(
            '<span class="free-badge">GRATIS</span>',
            unsafe_allow_html=True,
        )

    st.sidebar.markdown("### 💱 Moneda")

    moneda_sidebar = st.sidebar.radio(
        "Mostrar valores en:",
        ["COP", "USD"],
        index=(
            0
            if st.session_state["moneda_visual"] == "COP"
            else 1
        ),
        format_func=lambda x: (
            "🇨🇴 COP — Pesos"
            if x == "COP"
            else "🇺🇸 USD — Dólares"
        ),
    )

    st.session_state["moneda_visual"] = moneda_sidebar

    datos_fx = obtener_tasa_usd_cop()

    if datos_fx["ok"]:

        st.sidebar.caption(
            f"💱 1 USD = "
            f"{formatear_numero(datos_fx['rate'], 'COP')}"
            f" COP"
        )

        st.sidebar.caption(
            f"Actualización: {datos_fx['date']}"
        )

    if st.session_state["plan"] != "pro":

        st.sidebar.markdown(
            f"""
            <br>
            <a href="{STRIPE_PAYMENT_LINK}"
               target="_blank"
               style="
               background-color:{PINO};
               color:white;
               padding:9px 12px;
               border-radius:10px;
               text-decoration:none;
               font-weight:700;
               display:block;
               text-align:center;">
               ✨ Pasar a Pro ($6.99/mes)
            </a>
            """,
            unsafe_allow_html=True,
        )

    if st.sidebar.button(
        "Cerrar sesión",
        use_container_width=True,
    ):

        if supabase:

            try:
                supabase.auth.sign_out()
            except Exception:
                pass

        st.session_state["user"] = None
        st.session_state["plan"] = "free"

        st.rerun()


# ============================================================
# HERO
# ============================================================

def obtener_saludo():

    hora = pd.Timestamp.now().hour

    if hora < 12:
        return "Buenos días"

    elif hora < 19:
        return "Buenas tardes"

    return "Buenas noches"


nombre_mostrado = (
    st.session_state["user"]
    .split("@")[0]
    .capitalize()
    if st.session_state["user"]
    else ""
)

st.markdown(
    f"""
    <div class="hero-banner">

        <h1>
            🌱 {obtener_saludo()}
            {f', {nombre_mostrado}' if nombre_mostrado else ''}
        </h1>

        <p>
            Tu compañero de finanzas — sin culpa,
            sin jerga y con claridad.
        </p>

        <span class="hero-pill">
            ✨ Claridad financiera en un vistazo
        </span>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LOGIN CHECK
# ============================================================

if not st.session_state["user"]:

    st.info(
        "👈 Inicia sesión o crea una cuenta gratis "
        "en el panel lateral para empezar."
    )

    st.stop()


email = st.session_state["user"]
es_pro = st.session_state["plan"] == "pro"

moneda_visual = st.session_state["moneda_visual"]

datos_fx = obtener_tasa_usd_cop()

if datos_fx["ok"]:
    tasa_usd_cop = datos_fx["rate"]
else:
    tasa_usd_cop = None


# ============================================================
# DATOS SUPABASE
# ============================================================

@st.cache_data(ttl=60)
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
            supabase
            .table("transactions")
            .select("*")
            .order(
                "fecha",
                desc=True,
            )
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

        if not df.empty:

            df["fecha"] = pd.to_datetime(
                df["fecha"]
            )

            df["monto"] = pd.to_numeric(
                df["monto"],
                errors="coerce",
            ).fillna(0)

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


@st.cache_data(ttl=60)
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
            supabase
            .table("categories")
            .select("*")
            .order("name")
            .execute()
        )

        cols = [
            "id",
            "name",
            "tipo",
            "presupuesto_mensual",
            "user_email",
            "household_id",
        ]

        return (
            pd.DataFrame(res.data)
            if res.data
            else pd.DataFrame(columns=cols)
        )

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


hogar = (
    obtener_hogar(email)
    if supabase
    else None
)


# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
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


# ============================================================
# VISTA HOGAR
# ============================================================

vista_hogar = False

if hogar and es_pro:

    vista_hogar = (
        st.radio(
            "Viendo:",
            [
                "Solo yo",
                f"Todo el hogar ({hogar['nombre']})",
            ],
            horizontal=True,
        )
        != "Solo yo"
    )


if vista_hogar:

    if not df_tx_todo.empty:

        df_tx = df_tx_todo[
            df_tx_todo["household_id"]
            == hogar["id"]
        ].copy()

    else:
        df_tx = df_tx_todo.copy()

    if not df_cat_todo.empty:

        df_cat = df_cat_todo[
            df_cat_todo["household_id"]
            == hogar["id"]
        ].copy()

    else:
        df_cat = df_cat_todo.copy()

else:

    if not df_tx_todo.empty:

        df_tx = df_tx_todo[
            df_tx_todo["user_email"]
            == email
        ].copy()

    else:
        df_tx = df_tx_todo.copy()

    if not df_cat_todo.empty:

        df_cat = df_cat_todo[
            (df_cat_todo["user_email"] == email)
            &
            (
                df_cat_todo["household_id"]
                .isna()
            )
        ].copy()

    else:
        df_cat = df_cat_todo.copy()


# ============================================================
# TAB 1 — RESUMEN
# ============================================================

with tab1:

    st.subheader(
        "Tu mes de un vistazo"
    )

    # --------------------------------------------------------
    # FX
    # --------------------------------------------------------

    mostrar_selector_moneda()

    # --------------------------------------------------------
    # CONTEXTO ECONÓMICO
    # --------------------------------------------------------

    señales, detalle_señales = (
        cargar_contexto_economico()
    )

    if detalle_señales:

        if señales == 0:

            st.markdown(
                """
                <div class="insight-card insight-buena">
                    🟢 <b>Contexto económico:</b>
                    los indicadores públicos de recesión
                    más seguidos no muestran alerta activa por ahora.
                </div>
                """,
                unsafe_allow_html=True,
            )

        else:

            st.markdown(
                f"""
                <div class="insight-card insight-alerta">
                    🟡 <b>Contexto económico:</b>
                    {señales} de {len(detalle_señales)}
                    indicadores públicos están en zona de alerta.
                </div>
                """,
                unsafe_allow_html=True,
            )

        if es_pro:

            with st.expander(
                "Ver detalle de los indicadores"
            ):

                for (
                    nombre,
                    valor,
                    activo,
                    texto,
                ) in detalle_señales:

                    st.write(
                        ("🔴" if activo else "🟢")
                        + f" **{nombre}**: {texto}"
                    )

    # --------------------------------------------------------
    # SIN MOVIMIENTOS
    # --------------------------------------------------------

    hoy = pd.Timestamp.today()

    if df_tx.empty:

        st.info(
            "Aún no tienes movimientos registrados. "
            "Ve a **➕ Registrar** para agregar el primero."
        )

    else:

        # ----------------------------------------------------
        # FECHAS
        # ----------------------------------------------------

        df_tx["mes"] = (
            df_tx["fecha"]
            .dt.to_period("M")
        )

        mes_actual = hoy.to_period("M")
        mes_anterior = mes_actual - 1

        df_mes = df_tx[
            df_tx["mes"] == mes_actual
        ]

        df_mes_ant = df_tx[
            df_tx["mes"] == mes_anterior
        ]

        # ----------------------------------------------------
        # CATEGORÍAS
        # ----------------------------------------------------

        gasto_categorias = (
            set(
                df_cat[
                    df_cat["tipo"] == "gasto"
                ]["name"]
            )
            if not df_cat.empty
            else set()
        )

        ingreso_categorias = (
            set(
                df_cat[
                    df_cat["tipo"] == "ingreso"
                ]["name"]
            )
            if not df_cat.empty
            else set()
        )

        # ----------------------------------------------------
        # TOTALES
        # ----------------------------------------------------

        total_gasto = (
            -df_mes[
                df_mes["categoria"]
                .isin(gasto_categorias)
            ]["monto"].sum()
            if not df_mes.empty
            else 0
        )

        total_ingreso = (
            df_mes[
                df_mes["categoria"]
                .isin(ingreso_categorias)
            ]["monto"].sum()
            if not df_mes.empty
            else 0
        )

        balance = (
            total_ingreso
            - total_gasto
        )

        # ----------------------------------------------------
        # MÉTRICAS VISUALES
        # ----------------------------------------------------

        ingreso_visual = formatear_monto_base(
            total_ingreso,
            moneda_visual,
            tasa_usd_cop,
        )

        gasto_visual = formatear_monto_base(
            total_gasto,
            moneda_visual,
            tasa_usd_cop,
        )

        balance_visual = formatear_monto_base(
            abs(balance),
            moneda_visual,
            tasa_usd_cop,
        )

        m1, m2, m3 = st.columns(3)

        m1.metric(
            "Ingresos del mes",
            ingreso_visual,
        )

        m2.metric(
            "Gastos del mes",
            gasto_visual,
        )

        m3.metric(
            "Balance",
            balance_visual,
            delta=(
                "Positivo"
                if balance >= 0
                else "Negativo"
            ),
            delta_color=(
                "normal"
                if balance >= 0
                else "inverse"
            ),
        )

        # ----------------------------------------------------
        # SALUD
        # ----------------------------------------------------

        tasa_ahorro = (
            balance / total_ingreso
            if total_ingreso > 0
            else 0
        )

        if not df_cat.empty:

            presupuestos_activos = df_cat[
                (df_cat["tipo"] == "gasto")
                &
                (
                    df_cat["presupuesto_mensual"]
                    .notna()
                )
            ]

        else:

            presupuestos_activos = (
                pd.DataFrame()
            )

        gastos_por_cat_actual = (
            df_mes[
                df_mes["categoria"]
                .isin(gasto_categorias)
            ]
            .groupby("categoria")["monto"]
            .sum()
            .abs()
        )

        if not presupuestos_activos.empty:

            cumplidos = sum(
                1
                for _, fila
                in presupuestos_activos.iterrows()
                if gastos_por_cat_actual.get(
                    fila["name"],
                    0,
                )
                <= float(
                    fila["presupuesto_mensual"]
                )
            )

            pct_presupuesto_ok = (
                cumplidos
                / len(presupuestos_activos)
            )

        else:

            pct_presupuesto_ok = 0.7

        puntaje_salud = round(
            min(
                100,
                max(
                    0,
                    min(
                        max(tasa_ahorro, 0),
                        1,
                    ) * 60
                    +
                    pct_presupuesto_ok * 40,
                ),
            )
        )

        # ----------------------------------------------------
        # GAUGE + DONA
        # ----------------------------------------------------

        col_gauge, col_dona = st.columns(
            [0.85, 1.65]
        )

        with col_gauge:

            st.markdown(
                "#### 💚 Salud financiera"
            )

            st.plotly_chart(
                grafico_salud_financiera(
                    puntaje_salud
                ),
                use_container_width=True,
                config={
                    "displayModeBar": False,
                },
            )

            if puntaje_salud >= 70:

                st.success(
                    "Vas muy bien este mes."
                )

            elif puntaje_salud >= 40:

                st.info(
                    "Vas en terreno neutral — "
                    "hay margen para ajustar."
                )

            else:

                st.warning(
                    "Este mes viene apretado. "
                    "Revisa tus categorías con más gasto."
                )

        with col_dona:

            st.markdown(
                "#### Gasto por categoría este mes"
            )

            gastos_mes = (
                df_mes[
                    df_mes["categoria"]
                    .isin(gasto_categorias)
                ]
                .groupby("categoria")["monto"]
                .sum()
                .abs()
                .sort_values(
                    ascending=False
                )
            )

            if not gastos_mes.empty:

                fig = grafico_dona_categorias(
                    gastos_mes,
                    moneda_visual,
                    tasa_usd_cop,
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    config={
                        "displaylogo": False,
                        "responsive": True,
                    },
                )

                # --------------------------------------------
                # TARJETAS DE CATEGORÍA
                # --------------------------------------------

                for categoria, monto in gastos_mes.items():

                    monto_visual = (
                        formatear_monto_base(
                            monto,
                            moneda_visual,
                            tasa_usd_cop,
                        )
                    )

                    porcentaje = (
                        monto
                        / gastos_mes.sum()
                        * 100
                    )

                    st.markdown(
                        f"""
                        <div class="category-card">

                            <div>
                                <span style="font-size:20px">
                                    {icono_categoria(categoria)}
                                </span>

                                <span class="category-name">
                                    {categoria}
                                </span>

                                <div style="
                                    font-size:11px;
                                    color:{TEXTO_SUAVE};
                                    margin-top:2px;
                                ">
                                    {porcentaje:.1f}% del gasto
                                </div>
                            </div>

                            <div class="category-amount">
                                {monto_visual}
                            </div>

                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            else:

                st.caption(
                    "Sin gastos categorizados este mes todavía."
                )

        # ----------------------------------------------------
        # RESUMEN NARRADO
        # ----------------------------------------------------

        total_ingreso_ant = (
            df_mes_ant[
                df_mes_ant["categoria"]
                .isin(ingreso_categorias)
            ]["monto"].sum()
            if not df_mes_ant.empty
            else 0
        )

        total_gasto_ant = (
            -df_mes_ant[
                df_mes_ant["categoria"]
                .isin(gasto_categorias)
            ]["monto"].sum()
            if not df_mes_ant.empty
            else 0
        )

        tasa_ahorro_ant = (
            (
                total_ingreso_ant
                - total_gasto_ant
            )
            / total_ingreso_ant
            if total_ingreso_ant > 0
            else None
        )

        categoria_top = (
            (
                gastos_mes.index[0],
                gastos_mes.iloc[0],
            )
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
            moneda_visual,
            tasa_usd_cop,
        )

        st.markdown(
            f"""
            <div class="insight-card">

                📝 <b>Tu mes en resumen:</b>
                {resumen}

            </div>
            """,
            unsafe_allow_html=True,
        )

        # ----------------------------------------------------
        # PRO
        # ----------------------------------------------------

        if es_pro:

            st.markdown(
                "#### 📈 Tendencia últimos 6 meses"
            )

            df_tx["mes_str"] = (
                df_tx["mes"].astype(str)
            )

            ult_6 = sorted(
                df_tx["mes_str"].unique()
            )[-6:]

            serie = (
                df_tx[
                    df_tx["mes_str"].isin(ult_6)
                    &
                    df_tx["categoria"].isin(
                        gasto_categorias
                    )
                ]
                .groupby("mes_str")["monto"]
                .sum()
                .abs()
            )

            if not serie.empty:

                serie_visual = (
                    serie / tasa_usd_cop
                    if moneda_visual == "USD"
                    and tasa_usd_cop
                    else serie
                )

                fig2 = go.Figure(
                    go.Scatter(
                        x=serie_visual.index,
                        y=serie_visual.values,
                        line=dict(
                            color=PINO,
                            width=3,
                        ),
                        fill="tozeroy",
                        fillcolor=(
                            "rgba(31,77,61,0.08)"
                        ),
                        mode="lines+markers",
                        marker=dict(
                            size=7,
                            color=GOLD,
                            line=dict(
                                width=2,
                                color=PINO,
                            ),
                        ),
                    )
                )

                fig2 = estilo_grafico(
                    fig2,
                    height=280,
                )

                st.plotly_chart(
                    fig2,
                    use_container_width=True,
                )

            # ------------------------------------------------
            # INSIGHTS
            # ------------------------------------------------

            st.markdown(
                "#### 💡 Insights"
            )

            comp_actual = (
                df_mes[
                    df_mes["categoria"]
                    .isin(gasto_categorias)
                ]
                .groupby("categoria")["monto"]
                .sum()
                .abs()
            )

            if not df_mes_ant.empty:

                comp_anterior = (
                    df_mes_ant[
                        df_mes_ant["categoria"]
                        .isin(gasto_categorias)
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
                                    Gastaste
                                    <b>{abs(cambio):.0f}% {direccion}</b>
                                    en <b>{cat}</b>
                                    que el mes pasado.
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

        else:

            st.info(
                "✨ Los insights automáticos y "
                "la tendencia de 6 meses están en el plan Pro."
            )


# ============================================================
# TAB 2 — REGISTRAR
# ============================================================

with tab2:

    st.subheader(
        "Registrar un movimiento"
    )

    st.caption(
        "Puedes introducir el movimiento en COP o USD. "
        "FinZen lo convertirá a COP usando la tasa real "
        "consultada en Internet."
    )

    with st.form(
        "form_transaccion",
        clear_on_submit=True,
    ):

        c1, c2 = st.columns(2)

        with c1:

            fecha_tx = st.date_input(
                "Fecha",
                value=date.today(),
            )

            tipo_tx = st.radio(
                "Tipo",
                [
                    "Gasto",
                    "Ingreso",
                ],
                horizontal=True,
            )

        with c2:

            moneda_tx = st.selectbox(
                "Moneda del movimiento",
                [
                    "COP",
                    "USD",
                ],
                format_func=lambda x: (
                    "🇨🇴 COP — Pesos colombianos"
                    if x == "COP"
                    else "🇺🇸 USD — Dólares"
                ),
            )

            monto_tx = st.number_input(
                (
                    "Monto (COP)"
                    if moneda_tx == "COP"
                    else "Monto (USD)"
                ),
                min_value=0.0,
                step=10.0,
            )

        descripcion_tx = st.text_input(
            "Descripción",
            placeholder="Ej: Starbucks, Uber, arriendo..."
        )

        categorias_disponibles = (
            df_cat[
                df_cat["tipo"]
                == (
                    "gasto"
                    if tipo_tx == "Gasto"
                    else "ingreso"
                )
            ]["name"]
            .tolist()
        )

        sugerida = (
            auto_categorizar(
                descripcion_tx
            )
            if tipo_tx == "Gasto"
            else "Salario"
        )

        indice_sugerido = (
            categorias_disponibles.index(
                sugerida
            )
            if sugerida in categorias_disponibles
            else 0
        )

        categoria_tx = st.selectbox(
            "Categoría",
            categorias_disponibles
            or ["Otros gastos"],
            index=(
                indice_sugerido
                if categorias_disponibles
                else 0
            ),
        )

        compartir_tx = False

        if hogar and es_pro:

            compartir_tx = st.checkbox(
                f"Compartir con mi hogar ({hogar['nombre']})"
            )

        guardar = st.form_submit_button(
            "💾 Guardar movimiento",
            use_container_width=True,
        )

        if guardar:

            if not supabase:

                st.error(
                    "Sin conexión a base de datos."
                )

            elif monto_tx <= 0:

                st.error(
                    "El monto debe ser mayor a 0."
                )

            else:

                monto_cop, tasa_usada = (
                    convertir_a_cop(
                        monto_tx,
                        moneda_tx,
                    )
                )

                if monto_cop is None:

                    st.error(
                        "No se pudo obtener la tasa de cambio."
                    )

                else:

                    signo = (
                        -1
                        if tipo_tx == "Gasto"
                        else 1
                    )

                    registro = {
                        "user_email": email,
                        "fecha": fecha_tx.isoformat(),
                        "monto": signo * monto_cop,
                        "categoria": categoria_tx,
                        "descripcion": descripcion_tx,
                        "fuente": "manual",
                    }

                    if compartir_tx and hogar:

                        registro[
                            "household_id"
                        ] = hogar["id"]

                    try:

                        (
                            supabase
                            .table("transactions")
                            .insert(registro)
                            .execute()
                        )

                        st.success(
                            "✅ Movimiento guardado."
                        )

                        if moneda_tx == "USD":

                            st.caption(
                                f"Conversión realizada: "
                                f"US${monto_tx:,.2f} × "
                                f"${tasa_usada:,.2f} COP/USD = "
                                f"${monto_cop:,.0f} COP."
                            )

                        st.cache_data.clear()

                    except Exception as e:

                        st.error(
                            f"No se pudo guardar: {e}"
                        )

    st.divider()

    st.markdown(
        "#### Movimientos recientes"
    )

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
            pd.to_datetime(
                df_mostrar["fecha"]
            ).dt.strftime(
                "%d/%m/%Y"
            )
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

        df_mostrar["monto"] = (
            df_mostrar["monto"]
            .apply(
                lambda x:
                formatear_monto_base(
                    x,
                    moneda_visual,
                    tasa_usd_cop,
                )
            )
        )

        df_mostrar.columns = [
            "Fecha",
            "Categoría",
            "Descripción",
            "Monto
