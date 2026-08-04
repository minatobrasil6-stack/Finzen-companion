import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
import io
import os
import time
import math

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

# Streamlit Community Cloud no tiene escritura en la ruta de caché por defecto de
# yfinance (~/.cache), lo que puede hacer fallar silenciosamente las descargas.
# Se redirige a /tmp, que sí es escribible en ese entorno.
try:
    os.makedirs("/tmp/yfinance_cache", exist_ok=True)
    yf.set_tz_cache_location("/tmp/yfinance_cache")
except Exception:
    pass

st.set_page_config(
    page_title="Q-FSI Core | Institutional Risk & Allocation Engine",
    layout="wide"
)

# ============================================================
# SISTEMA DE DISEÑO — Q-FSI Terminal
# Paleta: tinta institucional + acento latón (no plantilla cian/violeta genérica)
# Tipografía: Fraunces (display, con carácter) + Inter (UI) + JetBrains Mono (datos)
# Firma visual: cinta de cotizaciones (ticker tape) en la cabecera
# ============================================================
INK = "#0A0E17"
PANEL = "#10151F"
PANEL_2 = "#141B29"
HAIRLINE = "#26314A"
TEXT = "#E7ECF5"
MUTED = "#8996AC"
BRASS = "#C9A24B"
GREEN = "#3FB68B"
RED = "#E2574C"
BLUE = "#4F8FE0"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    html, body, .stApp {{
        background-color: {INK} !important;
        color: {TEXT};
        font-family: 'Inter', sans-serif;
    }}
    #MainMenu, footer, header {{ visibility: hidden; }}

    h1, h2, h3 {{
        font-family: 'Fraunces', serif !important;
        letter-spacing: -0.01em;
        color: {TEXT} !important;
    }}
    h1 {{ font-weight: 600 !important; }}
    p, span, label, div {{ font-family: 'Inter', sans-serif; }}

    /* ---- Cinta de cotizaciones (elemento de firma) ---- */
    .ticker-wrap {{
        width: 100%;
        overflow: hidden;
        background: {PANEL};
        border-top: 1px solid {HAIRLINE};
        border-bottom: 1px solid {HAIRLINE};
        padding: 9px 0;
        margin: -1rem 0 1.6rem 0;
    }}
    .ticker-move {{
        display: inline-flex;
        white-space: nowrap;
        animation: ticker-scroll 42s linear infinite;
    }}
    @keyframes ticker-scroll {{
        0% {{ transform: translateX(0); }}
        100% {{ transform: translateX(-50%); }}
    }}
    @media (prefers-reduced-motion: reduce) {{
        .ticker-move {{ animation: none; }}
    }}
    .ticker-item {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 12.5px;
        letter-spacing: 0.03em;
        color: {MUTED};
        padding: 0 26px;
        border-right: 1px solid {HAIRLINE};
    }}
    .ticker-item b {{ color: {TEXT}; font-weight: 500; }}
    .t-up {{ color: {GREEN}; }}
    .t-down {{ color: {RED}; }}

    .eyebrow {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: {BRASS};
        margin-bottom: 2px;
    }}

    /* ---- Métricas ---- */
    div[data-testid="stMetric"] {{
        background: {PANEL};
        border: 1px solid {HAIRLINE};
        border-top: 2px solid {BRASS};
        border-radius: 4px;
        padding: 14px 16px;
    }}
    div[data-testid="stMetricLabel"] {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px !important;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: {MUTED} !important;
    }}
    div[data-testid="stMetricValue"] {{
        font-family: 'JetBrains Mono', monospace !important;
        color: {TEXT} !important;
    }}

    /* ---- Pestañas ---- */
    button[data-baseweb="tab"] {{
        font-family: 'Inter', sans-serif;
        font-size: 13px;
        letter-spacing: 0.04em;
        color: {MUTED};
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: {TEXT} !important;
        border-bottom: 2px solid {BRASS} !important;
    }}
    div[data-baseweb="tab-highlight"] {{ background-color: {BRASS} !important; }}
    div[data-baseweb="tab-border"] {{ background-color: {HAIRLINE} !important; }}

    /* ---- Botones ---- */
    .stButton > button {{
        background-color: transparent;
        color: {BRASS};
        border: 1px solid {BRASS};
        border-radius: 3px;
        font-weight: 500;
        letter-spacing: 0.01em;
    }}
    .stButton > button:hover {{
        background-color: {BRASS};
        color: {INK};
        border: 1px solid {BRASS};
    }}
    .stDownloadButton > button {{
        background-color: {GREEN};
        color: {INK};
        border: 1px solid {GREEN};
        border-radius: 3px;
        font-weight: 600;
    }}

    /* ---- Inputs ---- */
    .stTextInput input, .stNumberInput input, div[data-baseweb="select"] > div {{
        background-color: {PANEL} !important;
        border: 1px solid {HAIRLINE} !important;
        color: {TEXT} !important;
        border-radius: 3px !important;
    }}
    .stTextInput input:focus, .stNumberInput input:focus {{
        border: 1px solid {BRASS} !important;
        box-shadow: none !important;
    }}

    /* ---- Expanders ---- */
    div[data-testid="stExpander"] {{
        background-color: {PANEL};
        border: 1px solid {HAIRLINE};
        border-radius: 4px;
    }}

    /* ---- Sidebar ---- */
    section[data-testid="stSidebar"] {{
        background-color: {PANEL_2};
        border-right: 1px solid {HAIRLINE};
    }}

    /* ---- Alertas ---- */
    div[data-testid="stAlert"] {{
        background-color: {PANEL} !important;
        border: 1px solid {HAIRLINE} !important;
        border-left: 3px solid {BRASS} !important;
        border-radius: 3px !important;
    }}

    hr {{ border-color: {HAIRLINE} !important; }}

    .pro-badge {{ background-color: {GREEN}; color: {INK}; padding: 4px 10px; border-radius: 3px; font-weight: 700; font-size: 11px; letter-spacing: 0.05em; }}
    .free-badge {{ background-color: {HAIRLINE}; color: {TEXT}; padding: 4px 10px; border-radius: 3px; font-weight: 700; font-size: 11px; letter-spacing: 0.05em; }}
    .demo-badge {{ background-color: {BRASS}; color: {INK}; padding: 4px 10px; border-radius: 3px; font-weight: 700; font-size: 11px; letter-spacing: 0.05em; }}
</style>
""", unsafe_allow_html=True)


def estilo_grafico(fig, titulo=None, height=400):
    """Aplica el template visual consistente de la terminal a cualquier figura Plotly."""
    fig.update_layout(
        template="plotly_dark",
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=MUTED, size=12),
        title=dict(text=titulo, font=dict(family="Fraunces, serif", color=TEXT, size=16)) if titulo else None,
        margin=dict(l=20, r=20, t=48 if titulo else 20, b=20),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=MUTED, size=11)),
        xaxis=dict(gridcolor=HAIRLINE, zerolinecolor=HAIRLINE),
        yaxis=dict(gridcolor=HAIRLINE, zerolinecolor=HAIRLINE),
    )
    return fig


# ============================================================
# DESCARGA DE DATOS DE YAHOO FINANCE — sesión con headers de navegador,
# reintentos con backoff y descarga batched para minimizar el riesgo de
# rate-limit (429), muy común cuando se corre desde hosting compartido
# como Streamlit Community Cloud.
# ============================================================
@st.cache_resource
def yf_session():
    """Sesión HTTP compartida con encabezados de navegador real. Yahoo Finance
    identifica y bloquea con más facilidad el tráfico que parece de bot (sin
    User-Agent de navegador), algo especialmente común en IPs compartidas de
    hosting como Streamlit Community Cloud."""
    if not REQUESTS_AVAILABLE:
        return None
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    })
    return s


def _yf_history_con_reintento(symbol, period, intentos=3):
    """Descarga el historial de UN ticker con reintento y backoff exponencial ante
    errores 429 (rate-limit) de Yahoo Finance, muy frecuentes en hosting compartido."""
    for intento in range(intentos):
        try:
            t = yf.Ticker(symbol, session=yf_session())
            df = t.history(period=period)
            if df is not None and not df.empty:
                return df, t
        except Exception:
            pass
        if intento < intentos - 1:
            time.sleep(1.5 * (intento + 1))
    return pd.DataFrame(), None


@st.cache_data(ttl=1800)
def cargar_multi(symbols, period=None, start=None, end=None):
    """Descarga varios tickers en UNA sola llamada batched (yf.download) en vez de
    una solicitud por ticker — reduce drásticamente el número de requests a Yahoo
    Finance y, con eso, la probabilidad de toparse con el límite de tasa (429) que
    Yahoo aplica a IPs de hosting compartido como Streamlit Community Cloud.
    Acepta 'period' (modo normal, relativo a hoy) O 'start'/'end' (modo histórico,
    rango de fechas fijo — usado por el Modo Histórico de la pestaña FSI)."""
    symbols = list(symbols)
    data = None
    for intento in range(3):
        try:
            if start is not None:
                data = yf.download(symbols, start=start, end=end, session=yf_session(),
                                    group_by="ticker", progress=False, threads=False,
                                    auto_adjust=True)
            else:
                data = yf.download(symbols, period=period, session=yf_session(),
                                    group_by="ticker", progress=False, threads=False,
                                    auto_adjust=True)
            if data is not None and not data.empty:
                break
        except Exception:
            data = None
        time.sleep(1.5 * (intento + 1))
    resultado = {}
    if data is None or data.empty:
        return resultado
    if len(symbols) == 1:
        try:
            resultado[symbols[0]] = data["Close"].dropna()
        except Exception:
            pass
    else:
        for sym in symbols:
            try:
                resultado[sym] = data[sym]["Close"].dropna()
            except Exception:
                continue
    return resultado


# ============================================================
# CINTA DE COTIZACIONES (elemento de firma de la terminal)
# ============================================================
@st.cache_data(ttl=900)
def snapshot_watchlist():
    watchlist = {
        "S&P 500": "SPY", "NASDAQ 100": "QQQ", "VIX": "^VIX",
        "ORO": "GLD", "TLT 20Y+": "TLT", "DXY": "DX-Y.NYB",
    }
    series = cargar_multi(list(watchlist.values()), "5d")
    items = []
    for label, tk in watchlist.items():
        s = series.get(tk)
        if s is not None and len(s) >= 2:
            last, prev = s.iloc[-1], s.iloc[-2]
            chg = (last / prev - 1) * 100
            items.append((label, last, chg))
    return items


def render_ticker_tape():
    datos = snapshot_watchlist()
    if not datos:
        st.markdown(
            f'<div class="ticker-wrap"><div class="ticker-item">'
            f'Mercados sin datos en vivo en este momento — reintentando en el próximo refresco.'
            f'</div></div>', unsafe_allow_html=True
        )
        return
    piezas = []
    for label, last, chg in datos:
        clase = "t-up" if chg >= 0 else "t-down"
        signo = "+" if chg >= 0 else ""
        piezas.append(f'<span class="ticker-item"><b>{label}</b> {last:,.2f} <span class="{clase}">{signo}{chg:.2f}%</span></span>')
    fila = "".join(piezas)
    st.markdown(f'<div class="ticker-wrap"><div class="ticker-move">{fila}{fila}</div></div>', unsafe_allow_html=True)


render_ticker_tape()

# ============================================================
# CONFIGURACIÓN — reemplaza estos placeholders antes de producción
# ============================================================
STRIPE_PAYMENT_LINK = "https://buy.stripe.com/tu-link-de-pago"  # TODO: reemplazar por tu link real de Stripe

# ============================================================
# SUPABASE / AUTENTICACIÓN REAL
# ============================================================
@st.cache_resource
def init_supabase():
    if not SUPABASE_AVAILABLE:
        return None
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception:
        return None

supabase = init_supabase()
db_connected = supabase is not None

if "user" not in st.session_state:
    st.session_state["user"] = None
if "plan" not in st.session_state:
    st.session_state["plan"] = "free"
if "backtest_result" not in st.session_state:
    st.session_state["backtest_result"] = None
if "var_result" not in st.session_state:
    st.session_state["var_result"] = None


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


def get_user_plan(user_id, email):
    """El plan viene de la tabla 'subscriptions' (columna status), nunca del texto del email.
    El paso a 'pro' solo lo puede escribir un backend de confianza (ej. webhook de Stripe
    con la service_role key) — el cliente únicamente puede leer y crear su propia fila 'free'."""
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


st.sidebar.markdown('<div class="eyebrow">Acceso</div>', unsafe_allow_html=True)
st.sidebar.title("🔐 Q-FSI Portal")

if not db_connected:
    st.sidebar.markdown('<span class="demo-badge">MODO DEMO — SIN BASE DE DATOS</span>', unsafe_allow_html=True)
    st.sidebar.caption(
        "No hay conexión a Supabase configurada en `st.secrets`. "
        "El login, el guardado de portafolios y el plan Pro están deshabilitados "
        "hasta que se configure SUPABASE_URL y SUPABASE_KEY."
    )
elif not st.session_state["user"]:
    st.sidebar.markdown("### Iniciar Sesión / Registro")
    auth_email = st.sidebar.text_input("Correo Electrónico")
    auth_pass = st.sidebar.text_input("Contraseña", type="password")

    col_l1, col_l2 = st.sidebar.columns(2)
    with col_l1:
        if st.button("🔑 Entrar"):
            if auth_email and auth_pass:
                user, error = sign_in(auth_email, auth_pass)
                if user:
                    st.session_state["user"] = user.email
                    st.session_state["plan"] = get_user_plan(user.id, user.email)
                    st.rerun()
                else:
                    st.sidebar.error(f"No se pudo iniciar sesión: {error}")
            else:
                st.sidebar.error("Ingresa correo y contraseña.")
    with col_l2:
        if st.button("📝 Registrarse"):
            if auth_email and auth_pass:
                user, error = sign_up(auth_email, auth_pass)
                if user:
                    st.sidebar.success("Cuenta creada. Revisa tu correo para confirmar (si aplica) e inicia sesión.")
                else:
                    st.sidebar.error(f"No se pudo registrar: {error}")
            else:
                st.sidebar.error("Ingresa correo y contraseña.")
else:
    st.sidebar.success(f"Sesión activa:\n**{st.session_state['user']}**")
    if st.session_state["plan"] == "pro":
        st.sidebar.markdown('Estado: <span class="pro-badge">PRO INSTITUCIONAL</span>', unsafe_allow_html=True)
    else:
        st.sidebar.markdown('Estado: <span class="free-badge">PLAN BÁSICO (FREE)</span>', unsafe_allow_html=True)
        st.sidebar.markdown(
            f'<br><a href="{STRIPE_PAYMENT_LINK}" target="_blank" '
            f'style="background-color:{GREEN}; color:{INK}; padding:8px 12px; border-radius:3px; '
            'text-decoration:none; font-weight:700; display:block; text-align:center;">'
            '💳 Actualizar a PRO ($99/mo)</a>', unsafe_allow_html=True
        )

    if st.sidebar.button("🚪 Cerrar Sesión"):
        if supabase:
            try:
                supabase.auth.sign_out()
            except Exception:
                pass
        st.session_state["user"] = None
        st.session_state["plan"] = "free"
        st.rerun()


def guardar_portafolio(email, nombre, lista_tickers):
    if supabase:
        try:
            data = {"user_email": email, "portfolio_name": nombre, "tickers": lista_tickers}
            supabase.table("portfolios").insert(data).execute()
            st.success(f"Portafolio '{nombre}' guardado exitosamente.")
        except Exception as e:
            st.error(f"Error al guardar: {e}")


def obtener_portafolios(email):
    if supabase:
        try:
            res = supabase.table("portfolios").select("*").eq("user_email", email).execute()
            return res.data
        except Exception:
            return []
    return []


col_hdr1, col_hdr2 = st.columns([3, 1])
with col_hdr1:
    st.markdown('<div class="eyebrow">Motor de Riesgo Institucional</div>', unsafe_allow_html=True)
    st.title("Q-FSI Core")
with col_hdr2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.session_state["plan"] == "pro":
        st.markdown('<span class="pro-badge" style="font-size:13px; padding:8px 15px;">✓ LICENCIA PRO ACTIVA</span>', unsafe_allow_html=True)
    else:
        st.markdown(
            f'<a href="{STRIPE_PAYMENT_LINK}" target="_blank" '
            f'style="background-color:{GREEN}; color:{INK}; padding:10px 15px; border-radius:3px; '
            'text-decoration:none; font-weight:700;">💳 Comprar Plan Pro</a>', unsafe_allow_html=True
        )

st.markdown(
    f'<div style="background:{PANEL}; border:1px solid {HAIRLINE}; border-left:3px solid {BRASS}; '
    f'border-radius:4px; padding:8px 14px; margin-bottom:16px; font-size:12.5px; color:{MUTED};">'
    '⚠️ Q-FSI es una herramienta de análisis y educación cuantitativa. '
    '<b style="color:'+TEXT+'">No es asesoría de inversión ni una recomendación de compra/venta.</b> '
    'Los datos provienen de fuentes públicas y de terceros no oficiales — verifica antes de operar. '
    'Ver pestaña 📜 Legal para el aviso completo.</div>', unsafe_allow_html=True
)

PORTAFOLIO_INSTITUCIONAL = {
    "Tecnología y Crecimiento": {
        "Apple Inc.": "AAPL", "Microsoft Corporation": "MSFT", "Alphabet Inc. (Google)": "GOOGL",
        "Amazon.com Inc.": "AMZN", "NVIDIA Corporation": "NVDA", "Meta Platforms Inc.": "META", "Tesla Inc.": "TSLA",
        "Marvell Technology Inc.": "MRVL", "Broadcom Inc.": "AVGO", "Advanced Micro Devices": "AMD",
        "Intel Corporation": "INTC", "Oracle Corporation": "ORCL", "Salesforce Inc.": "CRM", "Adobe Inc.": "ADBE",
        "QUALCOMM Inc.": "QCOM", "Micron Technology": "MU", "Palo Alto Networks": "PANW", "ServiceNow Inc.": "NOW",
        "International Business Machines": "IBM", "Cisco Systems Inc.": "CSCO"
    },
    "Banca y Servicios Financieros": {
        "JPMorgan Chase & Co.": "JPM", "Bank of America Corp.": "BAC", "Wells Fargo & Co.": "WFC",
        "Goldman Sachs Group": "GS", "Morgan Stanley": "MS", "Citigroup Inc.": "C", "BlackRock Inc.": "BLK",
        "Visa Inc.": "V", "Mastercard Inc.": "MA", "American Express Co.": "AXP", "Charles Schwab Corp.": "SCHW",
        "US Bancorp": "USB", "PNC Financial Services": "PNC"
    },
    "Energía y Commodities": {
        "Exxon Mobil Corp.": "XOM", "Chevron Corporation": "CVX", "Shell PLC": "SHEL",
        "TotalEnergies SE": "TTE", "BP PLC": "BP", "ConocoPhillips": "COP", "Schlumberger Limited": "SLB",
        "Occidental Petroleum": "OXY", "Baker Hughes Co.": "BKR", "Freeport-McMoRan Inc.": "FCX"
    },
    "Índices y Cobertura Macroeconómica": {
        "S&P 500 ETF Trust": "SPY", "Invesco QQQ Trust (Nasdaq 100)": "QQQ", "iShares Russell 2000 ETF": "IWM",
        "Volatility Index Proxy (VIX)": "^VIX", "SPDR Gold Shares (Oro)": "GLD",
        "iShares 20+ Year Treasury Bond": "TLT", "US Dollar Index (DXY)": "DX-Y.NYB",
        "Dow Jones Industrial Average ETF": "DIA", "iShares MSCI Emerging Markets": "EEM"
    },
    "Bonos y Refugios": {
        "Bono EE.UU. 10Y": "^TNX", "TLT (20+ Year Treasury)": "TLT", "SPDR Gold Shares (Oro)": "GLD",
        "iShares Silver Trust": "SLV", "iShares iBoxx Investment Grade Corp Bond": "LQD"
    }
}

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "📈 Análisis Técnico", "🏦 Factor Macro (FSI)", "🤖 Sentimiento IA",
    "⚖️ Optimización & VaR", "📊 Backtesting", "🔌 API & Broker", "📉 Backtest de Recesión", "📜 Legal"
])


@st.cache_data(ttl=1800)
def cargar_datos(symbol, period):
    try:
        df, t = _yf_history_con_reintento(symbol, period)
        if df.empty:
            return None, None
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        df['SMA200'] = df['Close'].rolling(window=200).mean()
        df['SMA50'] = df['Close'].rolling(window=50).mean()
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        df['ATR'] = np.max(ranges, axis=1).rolling(14).mean()
        df['Highest_22'] = df['High'].rolling(22).max()
        df['Chandelier_Exit'] = df['Highest_22'] - (3.0 * df['ATR'])
        info = None
        try:
            info = t.info if t is not None else None
        except Exception:
            info = None
        return df, info
    except Exception:
        return None, None


@st.cache_data(ttl=3600)
def buscar_tickers(query):
    """Busca símbolos reales que cotizan en bolsa (acciones y ETFs) contra el buscador
    de Yahoo Finance — cubre prácticamente cualquier empresa listada en el mercado,
    no solo las precargadas en PORTAFOLIO_INSTITUCIONAL."""
    if not REQUESTS_AVAILABLE or not query or len(query.strip()) < 1:
        return []
    try:
        resp = requests.get(
            "https://query1.finance.yahoo.com/v1/finance/search",
            params={"q": query.strip(), "lang": "en-US", "region": "US", "quotesCount": 10, "newsCount": 0},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=6,
        )
        if resp.status_code != 200:
            return []
        data = resp.json()
        resultados = []
        for q in data.get("quotes", []):
            symbol = q.get("symbol")
            nombre = q.get("shortname") or q.get("longname") or symbol
            tipo = q.get("quoteType", "")
            bolsa = q.get("exchange", "")
            if symbol and tipo in ("EQUITY", "ETF"):
                resultados.append((symbol, nombre, bolsa))
        return resultados
    except Exception:
        return []


@st.cache_data(ttl=1800)
def cargar_serie_macro(symbol, period="1y"):
    try:
        df, _ = _yf_history_con_reintento(symbol, period)
        return df['Close'] if not df.empty else pd.Series(dtype=float)
    except Exception:
        return pd.Series(dtype=float)


@st.cache_data(ttl=3600)
def cargar_baseline_fsi(fecha_corte=None):
    """Media y desviación estándar de referencia sobre una ventana FIJA de 5 años
    (precios públicos de Yahoo Finance, sin restricción de licencia), terminando en
    'fecha_corte' si se da (Modo Histórico) o en hoy si no. Se calculan separado de
    la ventana visible para que el nivel del FSI sea comparable en el tiempo."""
    if fecha_corte:
        fin = pd.Timestamp(fecha_corte)
        inicio = fin - pd.DateOffset(years=5)
        series = cargar_multi(["^VIX", "HYG", "LQD"], start=inicio.strftime("%Y-%m-%d"), end=fin.strftime("%Y-%m-%d"))
    else:
        series = cargar_multi(["^VIX", "HYG", "LQD"], period="5y")
    if not series or "^VIX" not in series:
        return None
    tiene_credito = "HYG" in series and "LQD" in series and len(series.get("HYG", [])) > 100 and len(series.get("LQD", [])) > 100
    df = pd.DataFrame({"VIX": series["^VIX"]})
    if tiene_credito:
        df["HYG"], df["LQD"] = series["HYG"], series["LQD"]
    df = df.dropna()
    if df.empty or len(df) < 200:
        return None
    resultado = {"vix_mean": df["VIX"].mean(), "vix_std": df["VIX"].std(), "tiene_credito": tiene_credito}
    if tiene_credito:
        df["Credit_Proxy"] = df["HYG"] / df["LQD"]
        resultado["credit_mean"] = df["Credit_Proxy"].mean()
        resultado["credit_std"] = df["Credit_Proxy"].std()
    return resultado


@st.cache_data(ttl=3600)
def cargar_yield_curve_3y(fecha_corte=None):
    """10Y-2Y Treasury spread (T10Y2Y): serie del propio Sistema de la Reserva Federal
    (H.15 Selected Interest Rates), dato público de gobierno de EE.UU. — a diferencia
    de las series de ICE BofA en FRED, no tiene restricción de redistribución.
    Ventana de 3 años terminando en 'fecha_corte' (Modo Histórico) o en hoy.
    Una curva invertida (T10Y2Y negativo) es una señal clásica de estrés/recesión."""
    if not REQUESTS_AVAILABLE:
        return None
    try:
        resp = requests.get("https://fred.stlouisfed.org/graph/fredgraph.csv?id=T10Y2Y", timeout=10)
        if resp.status_code != 200:
            return None
        df = pd.read_csv(io.StringIO(resp.text))
        df.columns = ["Date", "T10Y2Y"]
        df["Date"] = pd.to_datetime(df["Date"])
        df["T10Y2Y"] = pd.to_numeric(df["T10Y2Y"], errors="coerce")
        df = df.dropna().set_index("Date")
        fin = pd.Timestamp(fecha_corte) if fecha_corte else pd.Timestamp.today()
        inicio = fin - pd.DateOffset(years=3)
        df = df[(df.index >= inicio) & (df.index <= fin)]
        return df if not df.empty else None
    except Exception:
        return None


@st.cache_data(ttl=3600)
def cargar_stlfsi4():
    """St. Louis Fed Financial Stress Index (STLFSI4): obra del gobierno de EE.UU.,
    de dominio público, sin restricción de redistribución (a diferencia de las series
    de ICE BofA licenciadas dentro de FRED). Se usa únicamente como referencia visual
    externa para contrastar el Q-FSI, nunca como insumo de su cálculo."""
    if not REQUESTS_AVAILABLE:
        return None
    try:
        resp = requests.get("https://fred.stlouisfed.org/graph/fredgraph.csv?id=STLFSI4", timeout=10)
        if resp.status_code != 200:
            return None
        df = pd.read_csv(io.StringIO(resp.text))
        df.columns = ["Date", "STLFSI4"]
        df["Date"] = pd.to_datetime(df["Date"])
        df["STLFSI4"] = pd.to_numeric(df["STLFSI4"], errors="coerce")
        return df.dropna().set_index("Date")
    except Exception:
        return None


# ============================================================
# PANEL DE RIESGO DE RECESIÓN REAL — 3 modelos públicos, académicamente
# validados, independientes entre sí y del Q-FSI. Se muestran por separado
# a propósito: cada uno mide algo distinto (mercado de bonos, mercado
# laboral, actividad económica real) y tiene su propio historial de
# aciertos y fallos. Ninguno es infalible, y no se combinan en un solo
# número porque eso fingiría una precisión que no existe.
# ============================================================
@st.cache_data(ttl=3600)
def cargar_fred_csv(series_id, years=None, fecha_corte=None):
    """Helper genérico para descargar cualquier serie PÚBLICA de FRED (obra de
    gobierno de EE.UU. o de investigadores que la publican en dominio público,
    nunca series licenciadas de ICE) vía su endpoint CSV, sin necesidad de API key.
    Si se da 'fecha_corte' (Modo Histórico), recorta la serie para no ver nada
    posterior a esa fecha — evita fuga de información del futuro en el backtest."""
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
        fin = pd.Timestamp(fecha_corte) if fecha_corte else pd.Timestamp.today()
        df = df[df.index <= fin]
        if years:
            inicio = fin - pd.DateOffset(years=years)
            df = df[df.index >= inicio]
        return df if not df.empty else None
    except Exception:
        return None


@st.cache_data(ttl=3600)
def cargar_modelo_ny_fed(fecha_corte=None):
    """Modelo probit de Estrella & Mishkin (1996/1998) — el mismo que publica
    mensualmente la Federal Reserve Bank of New York: probabilidad de recesión en
    los próximos 12 meses a partir del spread 10 años - 3 meses del Tesoro.
    Coeficientes públicos ampliamente citados y replicados (α=-0.5333, β=-0.6330).
    Indicador LÍDER: históricamente antecede a la recesión, pero con un rezago
    variable de 6 a 24 meses — no da una fecha exacta.
    Fuente: FRED (DGS10, DGS3MO), rendimientos del Tesoro de EE.UU., dato público."""
    dgs10 = cargar_fred_csv("DGS10", years=1, fecha_corte=fecha_corte)
    dgs3mo = cargar_fred_csv("DGS3MO", years=1, fecha_corte=fecha_corte)
    if dgs10 is None or dgs3mo is None:
        return None
    df = dgs10.join(dgs3mo, how="inner").dropna()
    if df.empty:
        return None
    df["Spread"] = df["DGS10"] - df["DGS3MO"]
    df["Prob_Recesion_12m"] = df["Spread"].apply(lambda s: (0.5 * (1 + math.erf((-0.5333 - 0.6330 * s) / math.sqrt(2)))) * 100)
    return df


@st.cache_data(ttl=3600)
def cargar_sahm_rule(fecha_corte=None):
    """Regla de Sahm: se activa cuando el promedio móvil de 3 meses de la tasa de
    desempleo sube ≥0.50pp sobre su mínimo de los últimos 12 meses. Indicador CASI
    COINCIDENTE (confirma, no anticipa): activó correctamente en las 11 recesiones
    de EE.UU. desde 1950, con solo 1 falso positivo. Fuente: FRED (SAHMREALTIME),
    obra pública de la Reserva Federal / Claudia Sahm."""
    return cargar_fred_csv("SAHMREALTIME", years=5, fecha_corte=fecha_corte)


@st.cache_data(ttl=3600)
def cargar_recprob_coincidente(fecha_corte=None):
    """Modelo de Chauvet & Piger: probabilidad de recesión a partir de un modelo
    dinámico de cambio de régimen (Markov-switching) sobre 4 variables de actividad
    económica REAL — nómina no agrícola, producción industrial, ingreso personal real
    y ventas reales de manufactura/comercio. No usa NINGÚN precio de mercado.
    Indicador COINCIDENTE: confirma el presente, con datos que se revisan con 1-2
    meses de rezago. Fuente: FRED (RECPROUSM156N), dato público de investigación."""
    return cargar_fred_csv("RECPROUSM156N", years=5, fecha_corte=fecha_corte)


# ============================================================
# BACKTEST HISTÓRICO DE RECESIÓN — evalúa los 3 modelos contra las 8
# recesiones oficiales del NBER (National Bureau of Economic Research,
# la autoridad que fecha recesiones en EE.UU.) desde 1969. Fechas de
# inicio publicadas y de dominio público — no son un juicio nuestro.
# ============================================================
NBER_RECESIONES = [
    ("1969-12-01", "Dic 1969 – Nov 1970"),
    ("1973-11-01", "Nov 1973 – Mar 1975"),
    ("1980-01-01", "Ene 1980 – Jul 1980"),
    ("1981-07-01", "Jul 1981 – Nov 1982"),
    ("1990-07-01", "Jul 1990 – Mar 1991"),
    ("2001-03-01", "Mar 2001 – Nov 2001"),
    ("2007-12-01", "Dic 2007 – Jun 2009"),
    ("2020-02-01", "Feb 2020 – Abr 2020"),
]


@st.cache_data(ttl=3600)
def calcular_serie_ny_fed_completa():
    """Igual que cargar_modelo_ny_fed, pero sobre TODO el historial disponible
    (no solo 1 año) para poder correr el backtest contra recesiones antiguas.
    DGS3MO solo tiene historial desde 1981 en FRED — las recesiones anteriores
    a esa fecha quedan marcadas como 'sin datos', no se inventan."""
    dgs10 = cargar_fred_csv("DGS10")
    dgs3mo = cargar_fred_csv("DGS3MO")
    if dgs10 is None or dgs3mo is None:
        return None
    df = dgs10.join(dgs3mo, how="inner").dropna()
    if df.empty:
        return None
    df["Spread"] = df["DGS10"] - df["DGS3MO"]
    df["Prob_Recesion_12m"] = df["Spread"].apply(lambda s: (0.5 * (1 + math.erf((-0.5333 - 0.6330 * s) / math.sqrt(2)))) * 100)
    return df


def backtest_serie_recesion(serie, umbral, meses_atras=24, meses_adelante=12):
    """Para cada recesión oficial del NBER, busca si 'serie' cruzó 'umbral' en la
    ventana [inicio-meses_atras, inicio+meses_adelante]. meses_anticipacion positivo
    = disparó ANTES del inicio oficial (anticipó); negativo = disparó DESPUÉS
    (confirmó con rezago). Si la serie no tiene historial para esa fecha, se marca
    honestamente como 'sin datos' en vez de inventar un resultado."""
    resultados = []
    for fecha_inicio_str, etiqueta in NBER_RECESIONES:
        inicio = pd.Timestamp(fecha_inicio_str)
        if serie is None or serie.empty or serie.index.min() > inicio - pd.DateOffset(months=meses_atras - 6):
            resultados.append({"Recesión (NBER)": etiqueta, "Resultado": "Sin datos históricos", "Señal": "—", "Meses de anticipación": None})
            continue
        ventana_desde = inicio - pd.DateOffset(months=meses_atras)
        ventana_hasta = inicio + pd.DateOffset(months=meses_adelante)
        tramo = serie[(serie.index >= ventana_desde) & (serie.index <= ventana_hasta)]
        cruces = tramo[tramo >= umbral]
        if cruces.empty:
            resultados.append({"Recesión (NBER)": etiqueta, "Resultado": "No disparó", "Señal": "—", "Meses de anticipación": None})
        else:
            primera = cruces.index.min()
            meses = (inicio.to_period('M') - primera.to_period('M')).n
            resultados.append({
                "Recesión (NBER)": etiqueta, "Resultado": "Anticipó" if meses > 0 else ("Coincidió" if meses == 0 else "Confirmó tarde"),
                "Señal": primera.strftime("%Y-%m"), "Meses de anticipación": meses,
            })
    return resultados


def resumen_backtest(resultados):
    validos = [r for r in resultados if r["Meses de anticipación"] is not None]
    evaluables = [r for r in resultados if r["Resultado"] != "Sin datos históricos"]
    if not evaluables:
        return 0, 0, None
    tasa_acierto = len(validos) / len(evaluables) * 100
    anticipacion_prom = np.mean([r["Meses de anticipación"] for r in validos]) if validos else None
    return tasa_acierto, len(evaluables), anticipacion_prom



with tab1:
    st.markdown("### 📊 Panel de Control y Activos")

    if "selected_sector" not in st.session_state:
        st.session_state["selected_sector"] = list(PORTAFOLIO_INSTITUCIONAL.keys())[0]
    if "selected_asset_name" not in st.session_state:
        primer_sector = list(PORTAFOLIO_INSTITUCIONAL.keys())[0]
        st.session_state["selected_asset_name"] = list(PORTAFOLIO_INSTITUCIONAL[primer_sector].keys())[0]

    with st.expander(f"📁 Sector Actual: **{st.session_state['selected_sector']}**", expanded=False):
        st.write("Selecciona un sector institucional:")
        cols_sector = st.columns(2)
        for i, sector in enumerate(PORTAFOLIO_INSTITUCIONAL.keys()):
            with cols_sector[i % 2]:
                if st.button(sector, key=f"sec_btn_{i}", use_container_width=True):
                    st.session_state["selected_sector"] = sector
                    primer_activo = list(PORTAFOLIO_INSTITUCIONAL[sector].keys())[0]
                    st.session_state["selected_asset_name"] = primer_activo
                    st.rerun()

    sector_actual = st.session_state["selected_sector"]
    activos_del_sector = PORTAFOLIO_INSTITUCIONAL[sector_actual]

    with st.expander(f"🎯 Activo: **{st.session_state['selected_asset_name']}**", expanded=False):
        st.write(f"Corporaciones en *{sector_actual}*:")
        for nombre_activo in activos_del_sector.keys():
            if st.button(nombre_activo, key=f"ast_btn_{nombre_activo}", use_container_width=True):
                st.session_state["selected_asset_name"] = nombre_activo
                st.rerun()

        st.markdown("**O busca cualquier empresa que cotice en bolsa (nombre o ticker):**")
        query_busqueda = st.text_input("Ej: Marvell, MRVL, Nvidia, Ferrari...", value="", key="busqueda_ticker")
        if query_busqueda.strip():
            resultados = buscar_tickers(query_busqueda)
            if resultados:
                for symbol, nombre, bolsa in resultados:
                    etiqueta = f"{symbol} — {nombre} ({bolsa})"
                    if st.button(etiqueta, key=f"buscar_btn_{symbol}", use_container_width=True):
                        st.session_state["ticker_manual_input"] = symbol
                        st.rerun()
            else:
                st.caption("Sin resultados (o sin conexión al buscador). Puedes ingresar el ticker exacto abajo.")

        st.text_input("O ingresa Ticker Manual directo:", value="", key="ticker_manual_input")

    ticker_manual = st.session_state.get("ticker_manual_input", "").strip().upper()
    ticker_main = ticker_manual if ticker_manual else activos_del_sector[st.session_state["selected_asset_name"]]
    st.session_state["ticker_main"] = ticker_main

    periodo1 = st.select_slider("Horizonte de Análisis:", options=["6mo", "1y", "2y", "5y"], value="1y", key="per1")
    st.session_state["periodo_main"] = periodo1

    df_main, _ = cargar_datos(ticker_main, periodo1)
    if df_main is not None and not df_main.empty:
        last_price = df_main['Close'].iloc[-1]
        last_atr = df_main['ATR'].dropna().iloc[-1] if not df_main['ATR'].dropna().empty else 0
        last_chandelier = df_main['Chandelier_Exit'].dropna().iloc[-1] if not df_main['Chandelier_Exit'].dropna().empty else 0

        m1, m2, m3 = st.columns(3)
        m1.metric("Precio Actual", f"${last_price:.2f}")
        m2.metric("Chandelier Exit", f"${last_chandelier:.2f}", delta="-Protección", delta_color="inverse")
        m3.metric("ATR (14D)", f"${last_atr:.2f}")

        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08, row_heights=[0.7, 0.3])
        fig.add_trace(go.Candlestick(x=df_main.index, open=df_main['Open'], high=df_main['High'], low=df_main['Low'], close=df_main['Close'],
                                      name=ticker_main, increasing_line_color=GREEN, decreasing_line_color=RED), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_main.index, y=df_main['SMA200'], line=dict(color=BRASS, width=1.5), name="SMA 200"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_main.index, y=df_main['Chandelier_Exit'], line=dict(color=RED, width=1.5, dash='dash'), name="Chandelier Exit"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_main.index, y=df_main['RSI'], line=dict(color=BLUE, width=1.5), name="RSI"), row=2, col=1)
        fig = estilo_grafico(fig, height=450)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(f"No se pudieron cargar datos históricos para el activo: {ticker_main}")

with tab2:
    st.subheader("Matriz Multivariable de Estrés Financiero (FSI)")
    st.info("El índice combina volatilidad de mercado (VIX), presión crediticia (HYG frente a LQD) y la curva de rendimientos del Tesoro (10Y-2Y) para detectar regímenes de alta tensión sistémica.")

    with st.expander("🕰️ Modo Histórico — ver el panel como se habría visto en el pasado", expanded=False):
        st.caption("Recalcula TODO lo de abajo (Q-FSI y panel de recesión) usando SOLO datos disponibles hasta la fecha elegida, sin ver nada del futuro. Útil para comprobar qué habría mostrado el sistema antes de una crisis conocida — ej. agosto de 2007 (justo antes de que estallara la crisis subprime) o julio de 2006 (cuando se invirtió la curva 16 meses antes de la recesión de 2008).")
        modo_historico = st.checkbox("Activar Modo Histórico", value=False, key="modo_historico_fsi")
        fecha_corte = None
        if modo_historico:
            fecha_corte = st.date_input("Fecha de corte (el sistema no verá nada posterior a esta fecha):",
                                         value=pd.Timestamp("2007-08-01"), min_value=pd.Timestamp("1996-01-01"),
                                         max_value=pd.Timestamp.today(), key="fecha_corte_fsi")
            st.caption(f"📍 Analizando como si hoy fuera **{fecha_corte}**. Nota: HYG (el ETF de bonos high-yield que usamos para crédito) recién empezó a cotizar en abril de 2007, así que para fechas anteriores el factor de crédito se omite automáticamente — no se rellena con datos falsos.")

    baseline = cargar_baseline_fsi(fecha_corte)
    if fecha_corte:
        fin_1y, inicio_1y = pd.Timestamp(fecha_corte), pd.Timestamp(fecha_corte) - pd.DateOffset(years=1)
        series_1y = cargar_multi(["^VIX", "HYG", "LQD"], start=inicio_1y.strftime("%Y-%m-%d"), end=fin_1y.strftime("%Y-%m-%d"))
    else:
        series_1y = cargar_multi(["^VIX", "HYG", "LQD"], period="1y")

    tiene_credito_1y = "HYG" in series_1y and "LQD" in series_1y and len(series_1y.get("HYG", [])) > 20
    df_m = pd.DataFrame({'VIX': series_1y.get("^VIX", pd.Series(dtype=float))})
    if tiene_credito_1y:
        df_m['HYG'], df_m['LQD'] = series_1y["HYG"], series_1y["LQD"]
    df_m = df_m.dropna(subset=['VIX'])

    datos_simulados = df_m.empty or baseline is None
    factores = []
    if datos_simulados:
        st.warning("⚠️ No se pudo descargar VIX de Yahoo Finance para esta ventana. Mostrando **datos sintéticos de demostración**, no reales.")
        dates = pd.date_range(end=pd.Timestamp(fecha_corte) if fecha_corte else pd.Timestamp.today(), periods=252, freq='B')
        np.random.seed(42)
        df_m = pd.DataFrame({'VIX': 15 + np.cumsum(np.random.randn(252) * 0.5)}, index=dates)
        z_vix = (df_m['VIX'] - df_m['VIX'].mean()) / (df_m['VIX'].std() + 1e-6)
        factores.append(('VIX', z_vix))
    else:
        z_vix = (df_m['VIX'] - baseline['vix_mean']) / (baseline['vix_std'] + 1e-6)
        factores.append(('VIX', z_vix))

        if tiene_credito_1y and baseline.get('tiene_credito'):
            df_m['Credit_Proxy'] = df_m['HYG'] / df_m['LQD']
            z_credit = -(df_m['Credit_Proxy'] - baseline['credit_mean']) / (baseline['credit_std'] + 1e-6)
            factores.append(('Crédito HYG/LQD', z_credit))
        elif fecha_corte:
            st.caption("ℹ️ Factor de crédito (HYG/LQD) omitido para esta fecha: HYG no tiene suficiente historial antes de abril de 2007.")

        curva = cargar_yield_curve_3y(fecha_corte)
        if curva is not None and not curva.empty:
            curva_mean, curva_std = curva['T10Y2Y'].mean(), curva['T10Y2Y'].std()
            z_curva_full = -(curva['T10Y2Y'] - curva_mean) / (curva_std + 1e-6)
            z_curva = z_curva_full.reindex(df_m.index.union(z_curva_full.index)).sort_index().ffill().reindex(df_m.index)
            if not z_curva.isna().all():
                factores.append(('Curva 10Y-2Y', z_curva))

    tiene_curva = any(n == 'Curva 10Y-2Y' for n, _ in factores)

    # Pesos iguales tras estandarizar cada serie: convención de los índices de estrés
    # de la Fed regional cuando no hay calibración empírica (PCA) que justifique
    # ponderaciones distintas. Escala ×12: para 2 factores mapea aprox. z=-0.73→FSI≈40
    # y z=+1.82→FSI≈70, cerca de los grados 1 y 4 del Cleveland Fed CFSI — aproximado,
    # no una recalibración estadística exacta para cualquier número de factores.
    if factores:
        suma_z = sum(z for _, z in factores)
        df_m['FSI'] = (50 + ((suma_z / len(factores)) * 12)).clip(0, 100)
    last_fsi = df_m['FSI'].iloc[-1]

    col_f1, col_f2 = st.columns([2, 1])
    with col_f1:
        stlfsi = cargar_stlfsi4()
        fig_fsi = go.Figure()
        fig_fsi.add_trace(go.Scatter(x=df_m.index, y=df_m['FSI'], name="Q-FSI (0-100)", line=dict(color=BRASS, width=2), fill='tozeroy', fillcolor="rgba(201,162,75,0.08)"))
        if stlfsi is not None and not stlfsi.empty:
            ventana = stlfsi[stlfsi.index >= df_m.index.min()]
            if fecha_corte:
                ventana = ventana[ventana.index <= pd.Timestamp(fecha_corte)]
            if not ventana.empty:
                fig_fsi.add_trace(go.Scatter(x=ventana.index, y=ventana['STLFSI4'], name="STLFSI4 (Fed St. Louis, ref.)",
                                              line=dict(color=BLUE, width=1.3, dash='dot'), yaxis="y2"))
                fig_fsi.update_layout(yaxis2=dict(overlaying='y', side='right', showgrid=False,
                                                   title=dict(text="STLFSI4 (z-score)", font=dict(color=BLUE)),
                                                   tickfont=dict(color=BLUE)))
        titulo_fsi = "Índice Sintético de Estrés Financiero" + (" — DATOS SIMULADOS" if datos_simulados else "") + (f" — MODO HISTÓRICO al {fecha_corte}" if fecha_corte else "")
        fig_fsi = estilo_grafico(fig_fsi, titulo=titulo_fsi, height=380)
        st.plotly_chart(fig_fsi, use_container_width=True)
        if stlfsi is not None and not stlfsi.empty:
            st.caption("Línea punteada: STLFSI4, el índice oficial de estrés financiero de la Fed de St. Louis (18 series, actualización semanal, dato público). Se muestra solo como referencia de contraste — no participa en el cálculo del Q-FSI, que usa exclusivamente precios de mercado de Yahoo Finance.")
    with col_f2:
        st.metric("Nivel FSI Actual" if not fecha_corte else f"Nivel FSI al {fecha_corte}", f"{last_fsi:.1f} / 100", delta="Régimen Estable" if last_fsi < 60 else "Alerta Sistémica", delta_color="inverse")
        st.markdown("""
        * **< 40**: Expansión / Bajo Riesgo
        * **40 - 70**: Transición / Neutral
        * **> 70**: Estrés Severo / Cobertura
        """)
        nombres_factores = ", ".join(n for n, _ in factores) if factores else "ninguno disponible"
        st.caption(f"Metodología: promedio simple de z-scores de {len(factores)} factor(es) disponibles para esta fecha: {nombres_factores}. VIX y crédito normalizados contra una ventana fija de 5 años; la curva usa 3 años de historial (FRED). Pesos iguales y umbrales alineados aproximadamente con los grados de estrés del Cleveland Fed CFSI. Sigue siendo un índice propio, no un sustituto del STLFSI4 oficial (18 series).")

    st.divider()
    st.markdown("### 🚨 Panel de Riesgo de Recesión Real" + (f" — al {fecha_corte}" if fecha_corte else ""))
    st.info("A diferencia del Q-FSI (que mide estrés de MERCADO), estos tres modelos están construidos y validados académicamente para estimar riesgo de recesión ECONÓMICA real. Se muestran por separado, sin mezclarlos entre sí ni con el Q-FSI: cada uno mide algo distinto — bonos, empleo, actividad real — y tiene su propio historial de aciertos y fallos.")

    ny_fed = cargar_modelo_ny_fed(fecha_corte)
    sahm = cargar_sahm_rule(fecha_corte)
    recprob = cargar_recprob_coincidente(fecha_corte)

    señales_activas, señales_totales = 0, 0
    if ny_fed is not None and not ny_fed.empty:
        señales_totales += 1
        if ny_fed["Prob_Recesion_12m"].iloc[-1] >= 30:
            señales_activas += 1
    if sahm is not None and not sahm.empty:
        señales_totales += 1
        if sahm["SAHMREALTIME"].iloc[-1] >= 0.50:
            señales_activas += 1
    if recprob is not None and not recprob.empty:
        señales_totales += 1
        if recprob["RECPROUSM156N"].iloc[-1] >= 50:
            señales_activas += 1
    if señales_totales > 0:
        st.metric("Señales de recesión activas" + (f" al {fecha_corte}" if fecha_corte else " ahora mismo"), f"{señales_activas} / {señales_totales}")
        st.caption("Solo es un conteo de cuántos de los 3 modelos están en zona de alerta — no es una probabilidad combinada ni un cuarto índice. No existe evidencia de que 'más señales activas a la vez' sea más confiable que un modelo individual bien interpretado.")

    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1:
        if ny_fed is not None and not ny_fed.empty:
            prob_actual = ny_fed["Prob_Recesion_12m"].iloc[-1]
            estado = "🟢 Baja" if prob_actual < 15 else ("🟡 Moderada" if prob_actual < 30 else "🔴 Elevada")
            st.metric("Modelo NY Fed (curva 10Y-3M)", f"{prob_actual:.1f}%", delta=estado, delta_color="off")
            st.caption("Prob. de recesión en 12 meses (Estrella-Mishkin). LÍDER: antecede a la recesión, pero con rezago variable de 6-24 meses — no da fecha exacta.")
        else:
            st.metric("Modelo NY Fed (curva 10Y-3M)", "N/D")
            st.caption("No se pudo descargar DGS10/DGS3MO de FRED para esta fecha.")
    with col_r2:
        if sahm is not None and not sahm.empty:
            valor_sahm = sahm["SAHMREALTIME"].iloc[-1]
            disparado = valor_sahm >= 0.50
            st.metric("Regla de Sahm (desempleo)", f"{valor_sahm:.2f} pp", delta="🔴 Disparada" if disparado else "🟢 No disparada", delta_color="off")
            st.caption("Se activa en ≥0.50pp. CASI COINCIDENTE: activó en las 11 recesiones de EE.UU. desde 1950 (1 falso positivo) — confirma, no anticipa.")
        else:
            st.metric("Regla de Sahm (desempleo)", "N/D")
            st.caption("No se pudo descargar SAHMREALTIME de FRED para esta fecha.")
    with col_r3:
        if recprob is not None and not recprob.empty:
            valor_recprob = recprob["RECPROUSM156N"].iloc[-1]
            st.metric("Prob. Coincidente (Chauvet-Piger)", f"{valor_recprob:.1f}%", delta="🔴 Alta" if valor_recprob > 50 else "🟢 Baja", delta_color="off")
            st.caption("Modelo de 4 variables de actividad real (empleo, producción, ingreso, ventas) — sin precios de mercado. COINCIDENTE: confirma el presente, con revisión de 1-2 meses.")
        else:
            st.metric("Prob. Coincidente (Chauvet-Piger)", "N/D")
            st.caption("No se pudo descargar RECPROUSM156N de FRED para esta fecha.")

    st.warning("⚠️ Ningún modelo de recesión es infalible — ni siquiera estos tres, de los más citados y validados académicamente que existen. El de NY Fed puede anticipar con años de rezago variable; la Sahm confirma después de que la recesión ya empezó; el coincidente se revisa con el tiempo. Un algoritmo 'casi perfecto' para predecir recesiones no existe en ningún lado, ni siquiera en instituciones con muchos más recursos que este proyecto. Lo que sí existe aquí es un panel honesto con las tres señales públicas más confiables disponibles, sin fingir una certeza que no tienen.")

with tab3:
    st.subheader("🤖 Sintetizador de Sentimiento Algorítmico")
    st.info("El motor analiza la alineación técnica (precio vs SMA200), el momento del RSI y la volatilidad reciente para emitir una directriz cuantitativa. Es una regla determinística basada en indicadores técnicos, no un modelo de IA/NLP de sentimiento de noticias.")


    df_main = None
    if "ticker_main" in st.session_state and "periodo_main" in st.session_state:
        df_main, _ = cargar_datos(st.session_state["ticker_main"], st.session_state["periodo_main"])

    if df_main is not None and not df_main.empty:
        precio_actual = df_main['Close'].iloc[-1]
        sma_200 = df_main['SMA200'].iloc[-1] if 'SMA200' in df_main.columns else precio_actual
        rsi_actual = df_main['RSI'].iloc[-1] if 'RSI' in df_main.columns else 50

        if precio_actual > sma_200 and rsi_actual < 70:
            sesgo, color_sesgo = "ALCISTA (LONG)", "green"
            explicacion = "El activo cotiza por encima de su media móvil de largo plazo y el RSI no muestra sobrecompra extrema."
        elif precio_actual < sma_200:
            sesgo, color_sesgo = "BAJISTA / DEFENSIVO", "red"
            explicacion = "Cotización por debajo de la SMA 200. Se sugieren estrategias de cobertura o cautela institucional."
        else:
            sesgo, color_sesgo = "NEUTRAL / CONSOLIDACIÓN", "orange"
            explicacion = "Mercado en rango o con señales mixtas de momento técnico."

        st.markdown(f"### Sesgo Operacional Sugerido: :{color_sesgo}[{sesgo}]")
        st.write(f"**Análisis de Soporte:** {explicacion}")

        col_s1, col_s2, col_s3 = st.columns(3)
        col_s1.metric("Precio vs SMA200", f"{((precio_actual/sma_200)-1)*100:+.2f}%")
        col_s2.metric("RSI Actual", f"{rsi_actual:.1f}")
        vol_20d = df_main['Close'].pct_change().rolling(20).std().iloc[-1] * np.sqrt(252) * 100
        col_s3.metric("Volatilidad Anualizada (20D)", f"{vol_20d:.1f}%")
    else:
        st.warning("Selecciona y carga un activo válido en la Pestaña 1 para generar el análisis algorítmico de sentimiento.")


def cargar_retornos_portafolio(tickers, period="1y"):
    data = cargar_multi(tickers, period)
    if not data:
        return None
    df = pd.DataFrame(data).dropna()
    if df.empty or len(df) < 10:
        return None
    return df.pct_change().dropna()


def calcular_var(returns, weights, capital, confianza):
    port_returns = returns.dot(weights)
    z_scores = {0.95: 1.645, 0.99: 2.326}
    z = z_scores[confianza]
    var_hist = -np.percentile(port_returns, (1 - confianza) * 100) * capital
    mu, sigma = port_returns.mean(), port_returns.std()
    var_param = -(mu - z * sigma) * capital
    vol_anual = sigma * np.sqrt(252)
    return var_hist, var_param, vol_anual, port_returns


with tab4:
    st.subheader("⚖️ Value at Risk del Portafolio")
    st.info("Calcula el VaR histórico (percentil empírico de retornos) y el VaR paramétrico (asumiendo normalidad) sobre un portafolio con pesos iguales, usando precios de cierre reales del último año.")

    col_v1, col_v2, col_v3 = st.columns(3)
    with col_v1:
        tickers_var = st.text_input("Tickers del portafolio (separados por coma):", value="NVDA, AAPL, TLT, GLD, SPY", key="tickers_var")
    with col_v2:
        capital_var = st.number_input("Capital del Portafolio ($ USD)", value=100000, step=10000, min_value=1000, key="capital_var")
    with col_v3:
        confianza_var = st.selectbox("Nivel de Confianza:", [0.95, 0.99], format_func=lambda x: f"{int(x*100)}%", key="confianza_var")

    if st.button("Calcular VaR del Portafolio"):
        lista_tk = [t.strip().upper() for t in tickers_var.split(",") if t.strip()]
        if len(lista_tk) < 2:
            st.error("Ingresa al menos 2 tickers para calcular un VaR de portafolio diversificado.")
        else:
            returns = cargar_retornos_portafolio(lista_tk, "1y")
            if returns is None:
                st.error("No se pudieron obtener suficientes datos históricos para estos tickers.")
            else:
                pesos = np.array([1 / len(returns.columns)] * len(returns.columns))
                var_hist, var_param, vol_anual, port_returns = calcular_var(returns, pesos, capital_var, confianza_var)
                st.session_state["var_result"] = {
                    "tickers": list(returns.columns), "capital": capital_var, "confianza": confianza_var,
                    "var_hist": var_hist, "var_param": var_param, "vol_anual": vol_anual,
                }
                st.success(f"VaR calculado sobre {len(returns.columns)} activos con pesos iguales ({', '.join(returns.columns)}).")

                m1, m2, m3 = st.columns(3)
                m1.metric(f"VaR Histórico ({int(confianza_var*100)}%, 1 día)", f"${var_hist:,.0f}")
                m2.metric(f"VaR Paramétrico ({int(confianza_var*100)}%, 1 día)", f"${var_param:,.0f}")
                m3.metric("Volatilidad Anualizada", f"{vol_anual*100:.1f}%")
                st.caption("Interpretación: con el nivel de confianza elegido, no se espera perder más que el VaR en un día normal de mercado. El VaR histórico usa la distribución empírica real; el paramétrico asume retornos normales, lo cual subestima el riesgo de eventos extremos (colas gordas).")

                fig_var = go.Figure()
                fig_var.add_trace(go.Histogram(x=port_returns * capital_var, nbinsx=40, marker_color=BLUE, name="Retornos diarios ($)"))
                fig_var.add_vline(x=-var_hist, line_color=RED, line_dash="dash", annotation_text="VaR histórico", annotation_font_color=RED)
                fig_var = estilo_grafico(fig_var, titulo="Distribución de Retornos Diarios del Portafolio", height=350)
                st.plotly_chart(fig_var, use_container_width=True)

    st.divider()
    st.subheader("💾 Gestión Persistente de Portafolios")
    if not db_connected:
        st.warning("⚠️ Esta función requiere una base de datos Supabase conectada. Configura `SUPABASE_URL` y `SUPABASE_KEY` en `st.secrets` para habilitarla.")
    elif st.session_state["user"] is None:
        st.warning("⚠️ Debes iniciar sesión en el panel lateral para guardar portafolios.")
    else:
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.markdown("#### Guardar Portafolio Actual")
            nombre_p = st.text_input("Nombre del Portafolio", value="Mi Portafolio Institucional")
            tickers_p = st.text_input("Tickers (separados por coma)", value="NVDA, AAPL, TLT, GLD, SPY", key="tickers_save")
            if st.button("Guardar en Base de Datos"):
                lista = [t.strip().upper() for t in tickers_p.split(",") if t.strip()]
                guardar_portafolio(st.session_state["user"], nombre_p, lista)
        with col_p2:
            st.markdown(f"#### Portafolios de: {st.session_state['user']}")
            portafolios_db = obtener_portafolios(st.session_state["user"])
            if portafolios_db:
                opciones = {p["portfolio_name"]: p["tickers"] for p in portafolios_db}
                seleccionado = st.selectbox("Seleccionar Portafolio:", list(opciones.keys()))
                st.write("Tickers asociados:", ", ".join(opciones[seleccionado]))
            else:
                st.info("No hay portafolios guardados para este usuario.")


def ejecutar_backtest(df, estrategia, capital_inicial):
    df = df.copy().dropna(subset=['SMA200'])
    if df.empty or len(df) < 30:
        return None

    df['Return'] = df['Close'].pct_change()

    if estrategia == "Cruce SMA 50/200":
        df['Signal'] = np.where(df['SMA50'] > df['SMA200'], 1, 0)
    else:
        posicion = 0
        señales = []
        for _, row in df.iterrows():
            precio, chandelier, sma200 = row['Close'], row['Chandelier_Exit'], row['SMA200']
            if pd.isna(chandelier) or pd.isna(sma200):
                señales.append(0)
                continue
            if posicion == 0 and precio > sma200 and precio > chandelier:
                posicion = 1
            elif posicion == 1 and precio < chandelier:
                posicion = 0
            señales.append(posicion)
        df['Signal'] = señales

    df['Signal'] = df['Signal'].shift(1).fillna(0)
    df['Strategy_Return'] = df['Signal'] * df['Return']
    df['Equity'] = capital_inicial * (1 + df['Strategy_Return'].fillna(0)).cumprod()
    df['BuyHold_Equity'] = capital_inicial * (1 + df['Return'].fillna(0)).cumprod()

    dias = len(df)
    años = dias / 252
    equity_final = df['Equity'].iloc[-1]
    cagr = (equity_final / capital_inicial) ** (1 / años) - 1 if años > 0 and equity_final > 0 else 0.0

    std_diario = df['Strategy_Return'].std()
    sharpe = (df['Strategy_Return'].mean() / std_diario) * np.sqrt(252) if std_diario and std_diario > 0 else 0.0

    running_max = df['Equity'].cummax()
    drawdown = (df['Equity'] - running_max) / running_max
    max_dd = drawdown.min()
    n_trades = int((df['Signal'].diff().fillna(0) != 0).sum())

    return {"df": df, "cagr": cagr, "sharpe": sharpe, "max_dd": max_dd, "equity_final": equity_final,
            "n_trades": n_trades, "buyhold_final": df['BuyHold_Equity'].iloc[-1]}


with tab5:
    st.subheader("📊 Módulo de Backtesting Institucional")
    st.info("Simula el rendimiento histórico real sobre el activo y horizonte seleccionados en la Pestaña 1, usando cruces de medias móviles o el Chandelier Exit. La señal se calcula con el cierre del día anterior para evitar sesgo de anticipación (lookahead bias).")

    ticker_bt = st.session_state.get("ticker_main", "SPY")
    st.caption(f"Activo actual (definido en Pestaña 1): **{ticker_bt}**")

    col_b1, col_b2 = st.columns(2)
    with col_b1:
        estrategia_bt = st.selectbox("Estrategia de Prueba:", ["Cruce SMA 50/200", "Trend Following con Chandelier Exit"])
    with col_b2:
        capital_bt = st.number_input("Capital Inicial ($ USD)", value=100000, step=10000, min_value=1000)

    if st.button("Ejecutar Simulación Retrospectiva"):
        periodo_bt = st.session_state.get("periodo_main", "1y")
        df_bt_source, _ = cargar_datos(ticker_bt, periodo_bt)
        if df_bt_source is None or df_bt_source.empty:
            st.error(f"No hay datos disponibles para {ticker_bt}.")
        else:
            resultado = ejecutar_backtest(df_bt_source, estrategia_bt, capital_bt)
            if resultado is None:
                st.error("Historial insuficiente para calcular el backtest (se requieren al menos ~30 sesiones con SMA200 disponible; prueba un horizonte más largo como 2y o 5y).")
            else:
                st.session_state["backtest_result"] = {
                    "ticker": ticker_bt, "estrategia": estrategia_bt, "capital": capital_bt,
                    "cagr": resultado["cagr"], "sharpe": resultado["sharpe"],
                    "max_dd": resultado["max_dd"], "equity_final": resultado["equity_final"],
                    "n_trades": resultado["n_trades"],
                }
                st.success("Simulación completada con datos históricos reales.")

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("CAGR (Estrategia)", f"{resultado['cagr']*100:+.2f}%")
                m2.metric("Sharpe Ratio", f"{resultado['sharpe']:.2f}")
                m3.metric("Max Drawdown", f"{resultado['max_dd']*100:.2f}%")
                m4.metric("N° de Operaciones", resultado["n_trades"])

                df_plot = resultado["df"]
                fig_bt = go.Figure()
                fig_bt.add_trace(go.Scatter(x=df_plot.index, y=df_plot['Equity'], name="Estrategia", line=dict(color=GREEN, width=2)))
                fig_bt.add_trace(go.Scatter(x=df_plot.index, y=df_plot['BuyHold_Equity'], name="Buy & Hold", line=dict(color=MUTED, width=1.5, dash='dot')))
                fig_bt = estilo_grafico(fig_bt, titulo=f"Curva de Equity: {estrategia_bt} vs Buy & Hold ({ticker_bt})", height=400)
                st.plotly_chart(fig_bt, use_container_width=True)

                st.caption(f"Buy & Hold habría terminado en ${resultado['buyhold_final']:,.0f} vs ${resultado['equity_final']:,.0f} de la estrategia, sobre el mismo período. Resultados históricos, no garantía de desempeño futuro. No incluye comisiones, slippage ni impuestos.")

with tab6:
    st.subheader("🔌 API Conectividad & Broker Execution")
    st.markdown("Verifica la conexión contra una cuenta real de **paper trading de Alpaca** (entorno de simulación del propio broker, sin dinero real). Crea credenciales gratis en `alpaca.markets` si no tienes.")

    if not REQUESTS_AVAILABLE:
        st.error("La librería `requests` no está disponible en este entorno; no se puede probar la conexión.")
    else:
        broker_key = st.text_input("API Key ID (Alpaca Paper):", type="password", value="", placeholder="Pega tu Key ID aquí")
        broker_secret = st.text_input("API Secret Key (Alpaca Paper):", type="password", value="", placeholder="Pega tu Secret Key aquí")

        if st.button("Probar Conexión con Broker"):
            if not broker_key or not broker_secret:
                st.error("Ingresa tu Key ID y Secret Key de Alpaca (entorno paper) para probar la conexión.")
            else:
                try:
                    resp = requests.get(
                        "https://paper-api.alpaca.markets/v2/account",
                        headers={"APCA-API-KEY-ID": broker_key, "APCA-API-SECRET-KEY": broker_secret},
                        timeout=8,
                    )
                    if resp.status_code == 200:
                        cuenta = resp.json()
                        st.success("Conexión establecida correctamente con la cuenta paper de Alpaca.")
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Estado de Cuenta", cuenta.get("status", "N/D"))
                        c2.metric("Equity", f"${float(cuenta.get('equity', 0)):,.2f}")
                        c3.metric("Poder de Compra", f"${float(cuenta.get('buying_power', 0)):,.2f}")
                    elif resp.status_code == 401 or resp.status_code == 403:
                        st.error("Credenciales rechazadas por Alpaca (401/403). Verifica que sean claves de entorno *paper*, no *live*.")
                    else:
                        st.error(f"Alpaca respondió con estado {resp.status_code}: {resp.text[:200]}")
                except requests.exceptions.RequestException as e:
                    st.error(f"No se pudo contactar a Alpaca: {e}")

with tab7:
    st.subheader("📉 Backtest Histórico de Recesión")
    st.info("Evalúa los 3 modelos del panel de recesión contra las 8 recesiones oficiales de EE.UU. desde 1969 (fechadas por el NBER, autoridad pública). Por cada una, mide si el modelo cruzó su umbral de alerta ANTES del inicio real (anticipó) o DESPUÉS (confirmó tarde) — con datos reales, no simulados. Donde el modelo no tenía historial disponible aún, se marca honestamente como 'sin datos' en vez de inventar un resultado.")

    umbral_nyfed = 30
    umbral_sahm = 0.50
    umbral_recprob = 50

    ny_fed_full = calcular_serie_ny_fed_completa()
    sahm_full = cargar_fred_csv("SAHMREALTIME")
    recprob_full = cargar_fred_csv("RECPROUSM156N")

    resultados_nyfed = backtest_serie_recesion(ny_fed_full["Prob_Recesion_12m"] if ny_fed_full is not None else None, umbral_nyfed)
    resultados_sahm = backtest_serie_recesion(sahm_full["SAHMREALTIME"] if sahm_full is not None else None, umbral_sahm)
    resultados_recprob = backtest_serie_recesion(recprob_full["RECPROUSM156N"] if recprob_full is not None else None, umbral_recprob)

    for titulo, resultados, nota in [
        ("🏦 Modelo NY Fed (curva 10Y-3M, umbral 30%)", resultados_nyfed,
         "DGS3MO (T-bill 3 meses) solo tiene historial en FRED desde 1981 — las recesiones de 1969, 1973 y 1980 quedan 'sin datos' honestamente, no se rellenan."),
        ("👷 Regla de Sahm (desempleo, umbral 0.50pp)", resultados_sahm, None),
        ("📊 Modelo Chauvet-Piger (actividad real, umbral 50%)", resultados_recprob, None),
    ]:
        st.markdown(f"#### {titulo}")
        tasa, n_evaluables, anticipacion_prom = resumen_backtest(resultados)
        c1, c2, c3 = st.columns(3)
        c1.metric("Tasa de acierto", f"{tasa:.0f}%" if n_evaluables else "N/D", help="% de recesiones evaluables en que el modelo cruzó su umbral en la ventana de -24 a +12 meses.")
        c2.metric("Recesiones evaluables", n_evaluables)
        c3.metric("Anticipación promedio", f"{anticipacion_prom:+.1f} meses" if anticipacion_prom is not None else "N/D",
                   help="Positivo = anticipó antes del inicio oficial. Negativo = confirmó después.")
        df_resultado = pd.DataFrame(resultados).drop(columns=["Meses de anticipación"]).rename(columns={"Señal": "Fecha de la señal"})
        # Reconstruir columna de meses para mostrarla con signo legible
        df_resultado["Anticipación"] = [
            f"{r['Meses de anticipación']:+d} meses" if r["Meses de anticipación"] is not None else "—"
            for r in resultados
        ]
        st.dataframe(df_resultado, use_container_width=True, hide_index=True)
        if nota:
            st.caption(f"ℹ️ {nota}")
        st.divider()

    st.warning("⚠️ Con solo 8 recesiones en ~55 años, esta tasa de acierto tiene un margen de error real — no es una muestra grande. Interprétala como 'lo que ha pasado hasta ahora', no como una garantía estadística de lo que pasará en la próxima. Ningún modelo aquí tuvo acceso a información del futuro: todo se calcula con datos publicados, filtrados a lo que existía en cada ventana.")

    st.markdown("#### Exportar Reporte")
    bt = st.session_state.get("backtest_result")
    var = st.session_state.get("var_result")

    if bt is None and var is None:
        st.info("Ejecuta un backtest de activo (Pestaña 5) o un cálculo de VaR (Pestaña 4) para poder exportar también esos resultados en el mismo CSV.")
    else:
        filas = []
        if bt is not None:
            filas.append({
                "Módulo": "Backtesting", "Activo/Portafolio": bt["ticker"], "Detalle": bt["estrategia"],
                "Capital": bt["capital"], "CAGR (%)": round(bt["cagr"] * 100, 2), "Sharpe": round(bt["sharpe"], 2),
                "Max Drawdown (%)": round(bt["max_dd"] * 100, 2), "Capital Final": round(bt["equity_final"], 2),
                "N° Operaciones": bt["n_trades"],
            })
        if var is not None:
            filas.append({
                "Módulo": "VaR", "Activo/Portafolio": ", ".join(var["tickers"]), "Detalle": f"Confianza {int(var['confianza']*100)}%",
                "Capital": var["capital"], "VaR Histórico ($)": round(var["var_hist"], 2),
                "VaR Paramétrico ($)": round(var["var_param"], 2), "Volatilidad Anual (%)": round(var["vol_anual"] * 100, 2),
            })
        reporte = pd.DataFrame(filas)
        st.dataframe(reporte, use_container_width=True)
        csv_buffer = io.StringIO()
        reporte.to_csv(csv_buffer, index=False)
        st.download_button("⬇️ Exportar Reporte de Riesgo (CSV)", data=csv_buffer.getvalue(),
                            file_name="reporte_riesgo_qfsi.csv", mime="text/csv")

with tab8:
    st.subheader("📜 Legal")
    st.warning("⚠️ **Importante:** este texto es una plantilla de referencia para acelerar el arranque del producto. **No reemplaza la revisión de un abogado especializado en servicios financieros** antes de operar con usuarios reales, cobrar dinero, o presentar esta herramienta como algo distinto a lo que es. Ajusta jurisdicción y cláusulas específicas antes de publicarlo como definitivo.")

    with st.expander("📄 Términos de Servicio", expanded=False):
        st.markdown(f"""
**Última actualización:** {pd.Timestamp.today().strftime('%d/%m/%Y')}

**1. Qué es Q-FSI Core**
Q-FSI es una herramienta de análisis cuantitativo y educación financiera: indicadores técnicos, un índice propio de estrés de mercado, backtesting histórico de estrategias, cálculo de VaR, y modelos públicos de riesgo de recesión.

**2. Lo que Q-FSI NO es — la cláusula más importante**
Q-FSI **no es un asesor de inversión registrado** (no está registrado ante la SEC, FINRA, CNBV ni ningún regulador equivalente), **no ofrece asesoría financiera personalizada, y ninguna salida de esta herramienta (sesgo alcista/bajista, niveles de FSI, señales de backtesting, probabilidades de recesión) constituye una recomendación de comprar, vender o mantener ningún instrumento financiero.** Toda la información se ofrece con fines educativos y de análisis únicamente. El uso de estrategias de trading o inversión basadas en esta herramienta es responsabilidad exclusiva del usuario.

**3. Fuentes de datos**
Los precios de mercado provienen de Yahoo Finance a través de una interfaz no oficial (`yfinance`), sujeta a interrupciones, errores o bloqueos sin previo aviso. Los datos macroeconómicos provienen de FRED (Federal Reserve Economic Data), fuente pública oficial. Q-FSI no garantiza la exactitud, integridad o disponibilidad continua de ningún dato mostrado.

**4. Resultados de backtesting**
El desempeño histórico de cualquier estrategia mostrada en el módulo de Backtesting **no garantiza resultados futuros**. Los backtests no incluyen comisiones, deslizamiento (slippage) ni impuestos, salvo que se indique explícitamente.

**5. Cuentas y planes**
El plan Pro es una suscripción recurrente procesada por Stripe. Puedes cancelar en cualquier momento; el acceso continúa hasta el final del período pagado.

**6. Conexión a brokers**
La pestaña "API & Broker" permite probar conexión con cuentas de *paper trading* (simuladas, sin dinero real). Q-FSI no ejecuta operaciones reales ni tiene custodia de fondos.

**7. Limitación de responsabilidad**
Q-FSI se ofrece "tal cual", sin garantías de ningún tipo. En la máxima medida permitida por la ley, no somos responsables por pérdidas financieras derivadas del uso de esta herramienta.
        """)

    with st.expander("🔒 Aviso de Privacidad", expanded=False):
        st.markdown("""
**Qué datos recopilamos**
- Correo electrónico (cuenta)
- Portafolios y tickers que guardas explícitamente
- Claves de API de broker que ingreses en la pestaña "API & Broker" — se usan solo para la prueba de conexión en el momento, no se almacenan en nuestra base de datos

**Dónde se almacenan tus datos**
Supabase/PostgreSQL con seguridad a nivel de fila (Row Level Security): solo tú puedes ver tus portafolios guardados.

**Terceros involucrados**
Yahoo Finance (precios de mercado), FRED (datos macroeconómicos públicos), Stripe (pagos), Alpaca (si pruebas la conexión de broker). Cada uno tiene sus propias políticas de privacidad.

**Tus derechos**
Puedes solicitar la eliminación de tu cuenta y datos en cualquier momento. (El flujo de autoservicio para esto aún no está implementado — contacto manual por ahora.)

**Contacto**
Para dudas sobre privacidad: [agrega aquí tu correo de contacto real].
        """)

    st.info("💡 **Recordatorio permanente:** ninguna pestaña de este motor —FSI, sentimiento, backtesting, panel de recesión— debe interpretarse como una señal de compra o venta. Para decisiones de inversión, consulta a un asesor financiero registrado en tu país.")
