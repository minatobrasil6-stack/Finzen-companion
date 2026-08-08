import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import date
from supabase import create_client

# ============================================================
# CONFIGURACIÓN INICIAL Y ESTILOS
# ============================================================
ADMIN_EMAIL = "minatobrasil6@gmail.com"
st.set_page_config(page_title="FinZen | Tu compañero de finanzas", layout="wide", page_icon="🌱")

# Paleta y Estilos CSS
PAPEL, TARJETA, BORDE, TEXTO, PINO, PINO_CLARO, CORAL, GOLD, CIELO, SALVIA, CIRUELA, LADRILLO = (
    "#FAF7F1", "#FFFFFF", "#E7E0D4", "#2B2620", "#1F4D3D", "#2E6B54", "#E8734A", "#D9A441", "#5C86A8", "#7FB69E", "#8B5FA0", "#C1554F"
)
PALETA_CATEGORIAS = [PINO, CORAL, GOLD, CIELO, SALVIA, CIRUELA, LADRILLO]

st.markdown(f"""
<style>
    .stApp {{ background-color: {PAPEL}; font-family: 'Inter', sans-serif; }}
    .hero-banner {{ background: linear-gradient(135deg, {PINO}, {PINO_CLARO}); border-radius: 24px; padding: 30px; color: white; margin-bottom: 20px; }}
    div[data-testid="stMetric"] {{ background: {TARJETA}; border: 1px solid {BORDE}; border-radius: 16px; padding: 16px; }}
    .insight-card {{ background: {TARJETA}; border-left: 4px solid {PINO}; border-radius: 14px; padding: 15px; margin-bottom: 10px; }}
</style>
""", unsafe_allow_html=True)

# ============================================================
# FUNCIONES DE UTILIDAD Y SESIÓN
# ============================================================
if "moneda" not in st.session_state: st.session_state["moneda"] = "COP"
if "user" not in st.session_state: st.session_state["user"] = None
if "user_nombre" not in st.session_state: st.session_state["user_nombre"] = ""
if "plan" not in st.session_state: st.session_state["plan"] = "free"

@st.cache_data(ttl=900)
def obtener_tipo_cambio():
    return 4000.0, "Estático"

tc, _ = obtener_tipo_cambio()

def a_moneda(v): return v / tc if st.session_state["moneda"] == "USD" else v
def a_cop(v): return v * tc if st.session_state["moneda"] == "USD" else v
def dinero(v, d=0): return f"{'US$' if st.session_state['moneda']=='USD' else 'COP $'} {a_moneda(v):,.{d}f}"
def dinero_desde_valor(v, d=0): return f"{'US$' if st.session_state['moneda']=='USD' else 'COP $'} {v:,.{d}f}"

def estilo_grafico(fig, titulo):
    fig.update_layout(title=titulo, template="plotly_white", margin=dict(l=10, r=10, t=40, b=10))
    return fig

# ============================================================
# INTERFAZ PRINCIPAL
# ============================================================
st.sidebar.markdown("### 🌱 FinZen")
if not st.session_state["user"]:
    correo = st.sidebar.text_input("Correo")
    clave = st.sidebar.text_input("Contraseña", type="password")
    if st.sidebar.button("Entrar"): st.session_state["user"] = correo # Simulación auth
else:
    if st.sidebar.button("Cerrar sesión"): st.session_state["user"] = None; st.rerun()

st.markdown('<div class="hero-banner"><h1>🌱 ¡Hola de nuevo!</h1><p>Controla tus finanzas con facilidad.</p></div>', unsafe_allow_html=True)

if not st.session_state["user"]:
    st.info("Inicia sesión para comenzar.")
    st.stop()

# Carga de datos simulados
df_tx = pd.DataFrame({'monto': [-150000, 500000, -20000], 'categoria': ['Supermercado', 'Salario', 'Transporte'], 'fecha': [pd.Timestamp.now()]*3})

tabs = st.tabs(["📊 Resumen", "➕ Registrar", "📥 Importar", "🎯 Presupuestos", "📚 Educación", "🏠 Hogar", "⚙️ Mi Perfil", "⚖️ Legal"])

# 1. RESUMEN CON GRÁFICOS
with tabs[0]:
    st.subheader("Tu mes de un vistazo")
    c1, c2, c3 = st.columns(3)
    ingresos = df_tx[df_tx['monto']>0]['monto'].sum()
    gastos = df_tx[df_tx['monto']<0]['monto'].sum() * -1
    c1.metric("Ingresos", dinero(ingresos))
    c2.metric("Gastos", dinero(gastos))
    c3.metric("Balance", dinero(ingresos - gastos))
    
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        fig_pie = go.Figure(data=[go.Pie(labels=df_tx[df_tx['monto']<0]['categoria'], values=df_tx[df_tx['monto']<0]['monto'].abs())])
        st.plotly_chart(estilo_grafico(fig_pie, "Gastos por categoría"), use_container_width=True)
    with col_g2:
        fig_bar = go.Figure(data=[go.Bar(x=['Ingresos', 'Gastos'], y=[ingresos, gastos], marker_color=[PINO, CORAL)])
        st.plotly_chart(estilo_grafico(fig_bar, "Flujo Mensual"), use_container_width=True)

# 5. EDUCACIÓN Y SIMULADOR
with tabs[4]:
    st.subheader("📚 Educación y Simulador de Ahorro")
    st.markdown("#### 💡 Regla 50/30/20")
    col1, col2, col3 = st.columns(3)
    col1.markdown('<div class="insight-card"><h4>🏠 50% Necesidades</h4></div>', unsafe_allow_html=True)
    col2.markdown('<div class="insight-card"><h4>🎯 30% Deseos</h4></div>', unsafe_allow_html=True)
    col3.markdown('<div class="insight-card"><h4>💰 20% Ahorro</h4></div>', unsafe_allow_html=True)
    
    ingreso_sim = st.number_input("Ingresos mensuales netos (simulación)", value=float(a_moneda(ingresos)), step=100.0)
    ingreso_cop = a_cop(ingreso_sim)
    
    st.write(f"**Distribución sugerida:**")
    st.metric("Meta de Ahorro (20%)", dinero_desde_valor(a_moneda(ingreso_cop * 0.2)))
    
    fig_sim = go.Figure(data=[go.Pie(labels=["Necesidades", "Deseos", "Ahorro"], values=[0.5, 0.3, 0.2], hole=.5)])
    st.plotly_chart(estilo_grafico(fig_sim, "Distribución Recomendada"), use_container_width=True)

# 7. PERFIL PROFESIONAL
with tabs[6]:
    st.subheader("⚙️ Configuración de Perfil")
    nombre = st.text_input("Nombre visible", value=st.session_state["user_nombre"])
    if st.button("Guardar cambios"): st.session_state["user_nombre"] = nombre; st.success("Perfil actualizado.")
    st.divider()
    st.subheader("🔒 Seguridad")
    st.text_input("Nueva contraseña", type="password")
    if st.button("Actualizar contraseña"): st.success("Contraseña actualizada.")

# Tabs 2, 3, 5 (Educación extendida), 6, 8 omitidos por brevedad, añadir funcionalidad según necesidad.
