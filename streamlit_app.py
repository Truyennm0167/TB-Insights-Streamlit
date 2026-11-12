from __future__ import annotations

import streamlit as st

from tb_insights.pages import about, clustering, country, insights, overview
from tb_insights.ui import inject_css

st.set_page_config(
    page_title="TB Insights | Phân tích bệnh lao WHO",
    page_icon="🫁",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()

with st.sidebar:
    st.markdown(
        """
        <div style="padding:8px 4px 18px 4px">
          <div style="font-family:Manrope,sans-serif;font-size:1.45rem;font-weight:800;color:#FFFFFF;letter-spacing:-.04em">TB <span style="color:#69D7C7">INSIGHTS</span></div>
          <div style="font-size:.68rem;letter-spacing:.14em;color:#9FB4C9;font-weight:700;margin-top:3px">DỮ LIỆU WHO · 2000—2024</div>
        </div>
        <div style="height:1px;background:rgba(255,255,255,.13);margin-bottom:14px"></div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("BẢNG ĐIỀU KHIỂN ĐỒ ÁN CT312")

def render_overview():
    overview.render()
def render_country():
    country.render()
def render_clustering():
    clustering.render()
def render_insights():
    insights.render()
def render_about():
    about.render()

pages = {
    "KHÁM PHÁ DỮ LIỆU": [
        st.Page(render_overview, title="Tổng quan toàn cầu", icon=":material/dashboard:", default=True),
        st.Page(render_country, title="Phân tích theo quốc gia", icon=":material/public:"),
        st.Page(render_clustering, title="Phân nhóm quốc gia", icon=":material/hub:"),
    ],
    "KẾT QUẢ NGHIÊN CỨU": [
        st.Page(render_insights, title="Phát hiện và đề xuất", icon=":material/lightbulb:"),
        st.Page(render_about, title="Dữ liệu và phương pháp", icon=":material/menu_book:"),
    ],
}

page = st.navigation(pages, position="sidebar")
with st.sidebar:
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    st.markdown(
        "<div style='font-size:.72rem;color:#A9BBCD;line-height:1.6'>Dữ liệu ước tính gánh nặng bệnh lao của WHO. Dashboard phục vụ mục đích học thuật, không phải công cụ chẩn đoán.</div>",
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:.67rem;color:#7F96AD'>CT312 · DATA MINING PROJECT · PHIÊN BẢN 1.3</div>", unsafe_allow_html=True)

page.run()
