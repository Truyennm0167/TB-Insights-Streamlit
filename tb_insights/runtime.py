import streamlit as st
from .data import load_country_data, load_cluster_data


@st.cache_data(show_spinner="Đang tải dữ liệu WHO...")
def get_dataframes():
    return load_country_data(), load_cluster_data()
