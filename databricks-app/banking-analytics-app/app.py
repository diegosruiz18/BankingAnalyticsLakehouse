import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Banking Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

GENIE_URL = (
    "https://adb-7405616816492775.15.azuredatabricks.net"
    "/embed/genie/rooms/01f1e137b1a61fa3b401a3f9e948a6a9"
    "?o=7405616816492775"
)

DASHBOARD_URL = (
    "https://adb-7405616816492775.15.azuredatabricks.net"
    "/embed/dashboardsv3/01f1e1220df9161083e136beace1f112"
    "?o=7405616816492775"
)

st.markdown(
    """
    <style>
      .block-container {
          padding-top: 3rem;
          padding-bottom: 1rem;
      }
      .main-title {
          font-size: 2rem;
          font-weight: 750;
          letter-spacing: .08em;
          line-height: 1.3;
      }
      .subtitle {
          color: #9CA3AF;
          margin-top: .15rem;
          margin-bottom: 1.2rem;
      }
      div[data-testid="stTabs"] button {
          font-weight: 600;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="main-title">BANKING ANALYTICS</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="subtitle">FINANCIAL INTELLIGENCE · PRODUCTION</div>',
    unsafe_allow_html=True,
)

dashboard_tab, genie_tab = st.tabs(["📊 Dashboard", "🤖 Genie Assistant"])

with dashboard_tab:
    st.subheader("Dashboard de indicadores bancarios")
    st.caption("Indicadores financieros, transacciones y detección de fraude.")
    components.iframe(DASHBOARD_URL, height=850, scrolling=True)

with genie_tab:
    st.subheader("Genie Banking Analytics")
    st.caption("Consulta información bancaria y financiera en lenguaje natural.")
    components.iframe(GENIE_URL, height=850, scrolling=True)
