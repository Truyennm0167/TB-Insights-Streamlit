from __future__ import annotations

import streamlit as st


def inject_css() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
        :root {
          --navy:#142D4E; --navy-2:#203F63; --teal:#149C91;
          --blue:#4F78D8; --muted:#718096; --line:#E5EAF1;
        }
        html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
        .stApp { background:linear-gradient(180deg,#F5F8FC 0%,#F4F7FB 100%); color:#172B45; }
        .block-container { max-width:1480px; padding-top:1.35rem; padding-bottom:3rem; }
        [data-testid="stSidebar"] { background:#10243A; border-right:1px solid rgba(255,255,255,.08); }
        [data-testid="stSidebar"] * { color:#E8EEF6; }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color:#C8D4E1; }
        [data-testid="stSidebar"] hr { border-color:rgba(255,255,255,.12); }
        [data-testid="stSidebar"] div[data-baseweb="select"] > div { background:#1A344F; border-color:#34506B; }
        [data-testid="stSidebar"] input { color:#FFFFFF; }
        [data-testid="stSidebar"] [data-testid="stSidebarNav"] { padding-top:.25rem; }
        h1,h2,h3 { font-family:'Manrope','DM Sans',sans-serif !important; color:var(--navy); letter-spacing:-.025em; }
        h1 { font-weight:800 !important; }
        h2 { font-weight:750 !important; }
        h3 { font-weight:700 !important; }
        [data-testid="stMetric"] {
          background:#FFFFFF; border:1px solid #E7EDF4; border-radius:16px;
          padding:17px 18px; box-shadow:0 5px 18px rgba(18,45,78,.045);
          min-height:112px;
        }
        [data-testid="stMetricLabel"] { color:#687A90 !important; font-weight:600; }
        [data-testid="stMetricValue"] { color:#142D4E !important; font-family:'Manrope',sans-serif; font-weight:800; }
        [data-testid="stMetricDelta"] { font-size:.78rem; }
        [data-testid="stVerticalBlockBorderWrapper"] {
          background:#FFFFFF; border-color:#E6ECF3 !important; border-radius:18px;
          box-shadow:0 5px 18px rgba(18,45,78,.035);
        }
        div[data-testid="stPlotlyChart"] { border-radius:14px; overflow:hidden; }
        [data-testid="stDataFrame"] { border:1px solid #E7EDF4; border-radius:12px; overflow:hidden; }
        [data-testid="stDownloadButton"] button, .stButton button {
          border-radius:10px; font-weight:650; transition:all .18s ease;
        }
        [data-testid="stDownloadButton"] button:hover, .stButton button:hover {
          transform:translateY(-1px); box-shadow:0 5px 14px rgba(20,45,78,.10);
        }
        .hero {
          background:linear-gradient(112deg,#142D4E 0%,#1E496B 70%,#167E83 100%);
          padding:27px 30px; border-radius:22px; color:#FFFFFF; margin-bottom:20px;
          box-shadow:0 12px 30px rgba(20,45,78,.14);
        }
        .hero-kicker { color:#9FE4D9; text-transform:uppercase; letter-spacing:.14em; font-size:.72rem; font-weight:700; margin-bottom:7px; }
        .hero-title { color:#FFFFFF !important; font-family:'Manrope',sans-serif; font-size:2rem; line-height:1.15; font-weight:800; margin:0; }
        .hero-sub { color:#D4E3EF; margin-top:9px; font-size:.93rem; line-height:1.55; }
        .eyebrow { color:#148F87; text-transform:uppercase; letter-spacing:.12em; font-size:.71rem; font-weight:800; margin-bottom:5px; }
        .section-title { color:#142D4E; font-family:'Manrope',sans-serif; font-size:1.12rem; font-weight:800; margin:0 0 2px 0; }
        .section-help { color:#78889A; font-size:.82rem; margin:0 0 11px 0; line-height:1.5; }
        .insight-card {
          background:#FFFFFF; border:1px solid #E5ECF3; border-left:4px solid #149C91;
          border-radius:14px; padding:17px 18px; box-shadow:0 5px 18px rgba(18,45,78,.035); min-height:126px;
        }
        .insight-card.warning { border-left-color:#E58A4E; }
        .insight-label { color:#718096; text-transform:uppercase; letter-spacing:.09em; font-size:.68rem; font-weight:800; }
        .insight-value { color:#142D4E; font-family:'Manrope',sans-serif; font-size:1.5rem; font-weight:800; margin:5px 0; }
        .insight-copy { color:#66788C; font-size:.82rem; line-height:1.5; }
        .note { background:#EDF5F7; border:1px solid #D5E8E9; border-radius:12px; padding:12px 15px; color:#31556A; font-size:.82rem; line-height:1.55; }
        .muted { color:#74859A; font-size:.82rem; }
        [data-testid="stTabs"] button { font-weight:650; }
        [data-testid="stAlert"] { border-radius:12px; }
        footer { visibility:hidden; }
        @media (max-width: 900px) {
          .block-container { padding-left:1rem; padding-right:1rem; }
          .hero { padding:22px 20px; border-radius:17px; }
          .hero-title { font-size:1.55rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str, kicker: str = "WHO · TUBERCULOSIS DATA") -> None:
    st.markdown(
        f'''<div class="hero"><div class="hero-kicker">{kicker}</div>
        <div class="hero-title">{title}</div><div class="hero-sub">{subtitle}</div></div>''',
        unsafe_allow_html=True,
    )


def section_title(title: str, help_text: str | None = None) -> None:
    help_html = f'<div class="section-help">{help_text}</div>' if help_text else ""
    st.markdown(f'<div class="section-title">{title}</div>{help_html}', unsafe_allow_html=True)


def insight_card(label: str, value: str, text: str, warning: bool = False) -> None:
    cls = "insight-card warning" if warning else "insight-card"
    st.markdown(
        f'<div class="{cls}"><div class="insight-label">{label}</div>'
        f'<div class="insight-value">{value}</div><div class="insight-copy">{text}</div></div>',
        unsafe_allow_html=True,
    )


def footnote(text: str) -> None:
    st.markdown(f'<div class="muted">{text}</div>', unsafe_allow_html=True)
