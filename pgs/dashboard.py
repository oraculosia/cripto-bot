
import streamlit as st

# Importações pesadas só são carregadas quando necessário
def lazy_imports():
    global pd, components, init_streamlit_comm, get_streamlit_html, ui
    import pandas as pd
    import streamlit.components.v1 as components
    from pygwalker.api.streamlit import init_streamlit_comm, get_streamlit_html
    import streamlit_shadcn_ui as ui
    globals().update(locals())

lazy_imports()


async def showDashboard():

    st.title("Sistema Flash Pagamentos")

    st.header("Dashboard Flash")
    ui.badges(badge_list=[("Dataframe", "default"), ("to", "secondary"), ("Interactive Data App", "destructive")], class_name="flex gap-2", key="viz_badges1")
    st.caption("Dashboard interativo para controle de vendas e análise para tomadas de decisão.")
    ui.badges(badge_list=[("pip install pygwalker", "secondary")], class_name="flex gap-2", key="viz_badges2")

    cols = st.columns(3)

    with cols[0]:
        ui.metric_card(title="Github Stars", content="7,984", description="1k stars in 12 hours.", key="card1")
    with cols[1]:
        ui.metric_card(title="Total Install", content="234,300", description="Since launched in 2023/02", key="card2")
    with cols[2]:
        ui.metric_card(title="HackerNews upvotes", content="712", description="Rank No.1 story of the day", key="card3")

    with ui.element("div", className="flex gap-2", key="buttons_group1"):
        ui.element("link_button", variant="primary", url="https://github.com/Kanaries/pygwalker", text="Get Started", key="btn1")
        ui.element("link_button", text="Github", url="https://github.com/Kanaries/pygwalker", variant="outline", key="btn2")

    # Initialize pygwalker communication
    init_streamlit_comm()

    # Caching the pygwalker HTML
    @st.cache_resource
    def get_pyg_html(df: pd.DataFrame) -> str:
        html = get_streamlit_html(df, use_kernel_calc=True, debug=False)
        return html

    @st.cache_data
    def get_df() -> pd.DataFrame:
        return pd.read_csv("https://kanaries-app.s3.ap-northeast-1.amazonaws.com/public-datasets/bike_sharing_dc.csv")

    df = get_df()

    components.html(get_pyg_html(df), width=1000, height=1000, scrolling=True)


