import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io
import re
from datetime import date

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

st.set_page_config(page_title="FinZen | Tu compañero de finanzas", layout="wide", page_icon="🌱")

# ============================================================
# SISTEMA DE DISEÑO — FinZen
# Distinto a propósito del motor de riesgo Q-FSI: esto es un producto de
# consumo masivo, no una terminal institucional. Paleta cálida, tono cercano,
# tipografía redondeada. El trabajo emocional es "calma y control sin culpa",
# no "gravedad de mercado".
# ============================================================
PAPEL = "#FAF7F1"
TARJETA = "#FFFFFF"
BORDE = "#E7E0D4"
TEXTO = "#2B2620"
TEXTO_SUAVE = "#7A7266"
PINO = "#1F4D3D"
PINO_CLARO = "#2E6B54"
CORAL = "#E8734A"
SALVIA = "#7FB69E"
ARENA = "#F1E9D8"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500;600&display=swap');

    html, body, .stApp {{ background-color: {PAPEL} !important; color: {TEXTO}; font-family: 'Inter', sans-serif; }}
    #MainMenu, footer, header {{ visibility: hidden; }}
    h1, h2, h3 {{ font-family: 'Quicksand', sans-serif !important; font-weight: 700 !important; color: {PINO} !important; }}

    div[data-testid="stMetric"] {{
        background: {TARJETA}; border: 1px solid {BORDE}; border-radius: 14px; padding: 16px 18px;
        box-shadow: 0 1px 3px rgba(43,38,32,0.04);
    }}
    div[data-testid="stMetricLabel"] {{ font-family: 'Inter', sans-serif; font-size: 12.5px !important; color: {TEXTO_SUAVE} !important; }}
    div[data-testid="stMetricValue"] {{ font-family: 'JetBrains Mono', monospace !important; color: {TEXTO} !important; }}

    button[data-baseweb="tab"] {{ font-family: 'Quicksand', sans-serif; font-weight: 600; color: {TEXTO_SUAVE}; }}
    button[data-baseweb="tab"][aria-selected="true"] {{ color: {PINO} !important; border-bottom: 3px solid {PINO} !important; }}
    div[data-baseweb="tab-highlight"] {{ background-color: {PINO} !important; }}

    .stButton > button {{ background-color: {PINO}; color: white; border: none; border-radius: 10px; font-weight: 600; padding: 0.5rem 1.1rem; }}
    .stButton > button:hover {{ background-color: {PINO_CLARO}; color: white; }}
    .stDownloadButton > button {{ background-color: {SALVIA}; color: {TEXTO}; border-radius: 10px; font-weight: 600; }}

    .stTextInput input, .stNumberInput input, .stDateInput input, div[data-baseweb="select"] > div {{
        background-color: {TARJETA} !important; border: 1px solid {BORDE} !important; border-radius: 10px !important; color: {TEXTO} !important;
    }}
    div[data-testid="stExpander"] {{ background-color: {TARJETA}; border: 1px solid {BORDE}; border-radius: 14px; }}
    section[data-testid="stSidebar"] {{ background-color: {ARENA}; border-right: 1px solid {BORDE}; }}
    div[data-testid="stAlert"] {{ background-color: {TARJETA} !important; border: 1px solid {BORDE} !important; border-left: 4px solid {PINO} !important; border-radius: 10px !important; }}
    hr {{ border-color: {BORDE} !important; }}

    .pro-badge {{ background-color: {PINO}; color: white; padding: 4px 10px; border-radius: 20px; font-weight: 700; font-size: 11px; }}
    .free-badge {{ background-color: {BORDE}; color: {TEXTO}; padding: 4px 10px; border-radius: 20px; font-weight: 700; font-size: 11px; }}
    .insight-card {{ background: {TARJETA}; border: 1px solid {BORDE}; border-left: 4px solid {PINO}; border-radius: 12px; padding: 14px 16px; margin-bottom: 10px; }}
    .insight-alerta {{ border-left: 4px solid {CORAL} !important; }}
    .insight-buena {{ border-left: 4px solid {SALVIA} !important; }}
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


st.sidebar.markdown("### 🌱 FinZen")
if not db_connected:
    st.sidebar.warning("⚠️ Sin conexión a base de datos (modo demo). Configura SUPABASE_URL y SUPABASE_KEY en secrets.")
elif not st.session_state["user"]:
    st.sidebar.markdown("#### Inicia sesión o crea tu cuenta")
    correo = st.sidebar.text_input("Correo")
    clave = st.sidebar.text_input("Contraseña", type="password")
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
            if correo and clave:
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

st.title("🌱 FinZen")
st.caption("Tu compañero de finanzas — sin culpa, sin jerga, sin consejos de inversión que no te puedo dar.")

if not st.session_state["user"]:
    st.info("👈 Inicia sesión o crea una cuenta gratis en el panel lateral para empezar a registrar tus gastos.")
    st.stop()

email = st.session_state["user"]
es_pro = st.session_state["plan"] == "pro"


@st.cache_data(ttl=60)
def cargar_transacciones(email):
    if not supabase:
        return pd.DataFrame(columns=["id", "fecha", "monto", "categoria", "descripcion", "fuente"])
    try:
        res = supabase.table("transactions").select("*").eq("user_email", email).order("fecha", desc=True).execute()
        df = pd.DataFrame(res.data) if res.data else pd.DataFrame(columns=["id", "fecha", "monto", "categoria", "descripcion", "fuente"])
        if not df.empty:
            df["fecha"] = pd.to_datetime(df["fecha"])
        return df
    except Exception:
        return pd.DataFrame(columns=["id", "fecha", "monto", "categoria", "descripcion", "fuente"])


@st.cache_data(ttl=60)
def cargar_categorias(email):
    if not supabase:
        return pd.DataFrame(columns=["name", "tipo", "presupuesto_mensual"])
    try:
        res = supabase.table("categories").select("*").eq("user_email", email).order("name").execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame(columns=["name", "tipo", "presupuesto_mensual"])
    except Exception:
        return pd.DataFrame(columns=["name", "tipo", "presupuesto_mensual"])


tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Resumen", "➕ Registrar", "📥 Importar CSV", "🎯 Presupuestos", "📚 Educación Financiera"])

df_tx = cargar_transacciones(email)
df_cat = cargar_categorias(email)

with tab1:
    st.subheader("Tu mes de un vistazo")
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

        st.markdown("#### Gasto por categoría este mes")
        gastos_mes = df_mes[df_mes["categoria"].isin(gasto_categorias)].groupby("categoria")["monto"].sum().abs().sort_values(ascending=False)
        if not gastos_mes.empty:
            fig = go.Figure(go.Bar(x=gastos_mes.values, y=gastos_mes.index, orientation="h", marker_color=PINO))
            fig = estilo_grafico(fig, height=max(280, 40 * len(gastos_mes)))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("Sin gastos categorizados este mes todavía.")

        if es_pro:
            st.markdown("#### Tendencia últimos 6 meses")
            df_tx["mes_str"] = df_tx["mes"].astype(str)
            ult_6 = sorted(df_tx["mes_str"].unique())[-6:]
            serie = df_tx[df_tx["mes_str"].isin(ult_6) & df_tx["categoria"].isin(gasto_categorias)].groupby("mes_str")["monto"].sum().abs()
            fig2 = go.Figure(go.Scatter(x=serie.index, y=serie.values, line=dict(color=PINO, width=3), fill="tozeroy", fillcolor="rgba(31,77,61,0.08)"))
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
                            st.markdown(f'<div class="insight-card {clase}">Gastaste <b>{abs(cambio):.0f}% {direccion}</b> en <b>{cat}</b> que el mes pasado.</div>', unsafe_allow_html=True)
            if not df_cat.empty:
                presupuestos = df_cat[(df_cat["tipo"] == "gasto") & df_cat["presupuesto_mensual"].notna()]
                for _, fila in presupuestos.iterrows():
                    gastado = comp_actual.get(fila["name"], 0)
                    presupuesto = fila["presupuesto_mensual"]
                    if presupuesto and gastado > presupuesto:
                        st.markdown(f'<div class="insight-card insight-alerta">Ya superaste tu presupuesto de <b>{fila["name"]}</b>: ${gastado:,.0f} de ${presupuesto:,.0f}.</div>', unsafe_allow_html=True)
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

        if st.form_submit_button("Guardar movimiento"):
            if not supabase:
                st.error("Sin conexión a base de datos.")
            elif monto_tx <= 0:
                st.error("El monto debe ser mayor a 0.")
            else:
                signo = -1 if tipo_tx == "Gasto" else 1
                try:
                    supabase.table("transactions").insert({
                        "user_email": email, "fecha": fecha_tx.isoformat(), "monto": signo * monto_tx,
                        "categoria": categoria_tx, "descripcion": descripcion_tx, "fuente": "manual",
                    }).execute()
                    st.success("Movimiento guardado.")
                    st.cache_data.clear()
                except Exception as e:
                    st.error(f"No se pudo guardar: {e}")

    st.divider()
    st.markdown("#### Movimientos recientes")
    if not df_tx.empty:
        st.dataframe(df_tx[["fecha", "categoria", "descripcion", "monto"]].head(20), use_container_width=True, hide_index=True)
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
                col1.write(fila["name"])
                nuevo_valor = col2.number_input("", min_value=0.0, step=50.0,
                                                 value=float(fila["presupuesto_mensual"]) if pd.notna(fila["presupuesto_mensual"]) else 0.0,
                                                 key=f"presu_{fila['name']}", label_visibility="collapsed")
                if nuevo_valor != (fila["presupuesto_mensual"] or 0):
                    try:
                        supabase.table("categories").update({"presupuesto_mensual": nuevo_valor}).eq("user_email", email).eq("name", fila["name"]).execute()
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
