from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from ..charts import CHART_CONFIG, BLUE, ORANGE, TEAL, bar_figure, choropleth_figure, trend_figure
from ..data import (
    available_regions, available_years, filter_region, format_decimal, format_int,
    format_signed, region_label, region_weighted_summary, weighted_summary,
    yearly_weighted_summary,
)
from ..runtime import get_dataframes
from ..ui import hero, section_title


def _delta(current, previous, *, integer: bool = False):
    if current is None or previous is None or pd.isna(current) or pd.isna(previous):
        return None
    difference = float(current) - float(previous)
    return format_signed(difference, digits=1, integer=integer)


def render() -> None:
    df, _ = get_dataframes()
    years = available_years(df)
    regions = available_regions(df)
    if not years:
        st.error("Không tìm thấy năm hợp lệ trong dữ liệu.")
        return

    hero(
        "Bức tranh bệnh lao toàn cầu",
        "Theo dõi gánh nặng bệnh lao, xu hướng mắc và tử vong qua các quốc gia và khu vực WHO.",
        "01 / TỔNG QUAN TOÀN CẦU · WHO 2000–2024",
    )

    c1, c2 = st.columns([1, 2])
    with c1:
        selected_year = st.selectbox("Năm thống kê", years, index=len(years) - 1, key="overview_year")
    with c2:
        selected_regions = st.multiselect(
            "Khu vực WHO", regions, default=[], format_func=region_label,
            placeholder="Tất cả khu vực WHO", key="overview_regions",
        )

    scoped = filter_region(df[df["year"].eq(selected_year)], selected_regions)
    summary = weighted_summary(scoped)
    previous = filter_region(df[df["year"].eq(selected_year - 1)], selected_regions)
    prev = weighted_summary(previous) if selected_year - 1 in years else None
    region_text = ", ".join(region_label(r) for r in selected_regions) if selected_regions else "Tất cả khu vực WHO"
    st.caption(
        f"Phạm vi: {region_text} · Năm {selected_year} · "
        f"{summary.get('countries_inc', 0)} thực thể có ước tính mắc bệnh."
    )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric(
        "Số ca mắc mới ước tính", format_int(summary.get("inc_cases")),
        delta=_delta(summary.get("inc_cases"), prev.get("inc_cases") if prev else None, integer=True),
        delta_color="inverse",
        help="Tổng số ca mắc ước tính trong các dòng quốc gia/vùng lãnh thổ có dữ liệu của năm được chọn. Mũi tên so sánh với năm trước; giảm được hiển thị theo chiều tích cực.",
    )
    m2.metric(
        "Tỷ suất mắc mới ước tính", format_decimal(summary.get("inc_rate"), 1),
        delta=_delta(summary.get("inc_rate"), prev.get("inc_rate") if prev else None),
        delta_color="inverse",
        help="Tổng số ca mắc mới ước tính chia cho tổng dân số của các quốc gia có dữ liệu, rồi nhân 100.000. Đây là phép tính tổng hợp của đồ án, không phải chỉ số toàn cầu chính thức do WHO công bố.",
    )
    m3.metric(
        "Số ca tử vong ước tính", format_int(summary.get("mort_cases")),
        delta=_delta(summary.get("mort_cases"), prev.get("mort_cases") if prev else None, integer=True),
        delta_color="inverse",
        help="Tổng số ca tử vong ước tính trong các dòng quốc gia/vùng lãnh thổ có dữ liệu của năm được chọn.",
    )
    m4.metric(
        "Tỷ suất tử vong ước tính", format_decimal(summary.get("mort_rate"), 1),
        delta=_delta(summary.get("mort_rate"), prev.get("mort_rate") if prev else None),
        delta_color="inverse",
        help="Tổng số ca tử vong ước tính chia cho tổng dân số của các quốc gia có dữ liệu, rồi nhân 100.000. Đây là phép tính tổng hợp của đồ án, không phải chỉ số toàn cầu chính thức do WHO công bố.",
    )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    trend_data = yearly_weighted_summary(df, selected_regions)
    left, right = st.columns(2)
    with left:
        with st.container(border=True):
            section_title("Xu hướng tỷ suất mắc mới", "Số ca mắc mới ước tính trên 100.000 dân; được tính từ tổng số ca và tổng dân số của các quốc gia có dữ liệu trong từng năm.")
            fig = trend_figure(trend_data, "inc_rate", "Tỷ suất mắc mới ước tính", BLUE, " ca/100.000 dân")
            st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
    with right:
        with st.container(border=True):
            section_title("Xu hướng tỷ suất tử vong", "Số ca tử vong ước tính trên 100.000 dân; được tính từ tổng số ca và tổng dân số của các quốc gia có dữ liệu trong từng năm.")
            fig = trend_figure(trend_data, "mort_rate", "Tỷ suất tử vong ước tính", TEAL, " ca/100.000 dân")
            st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    snapshot = filter_region(df[df["year"].eq(selected_year)], selected_regions)
    lcol, rcol = st.columns([1, 1.35])
    with lcol:
        with st.container(border=True):
            section_title("10 quốc gia có tỷ suất mắc mới cao nhất", f"Năm {selected_year} · Số ca trên 100.000 dân")
            top_rate = snapshot.dropna(subset=["e_inc_100k"]).nlargest(10, "e_inc_100k")
            st.plotly_chart(
                bar_figure(top_rate, "e_inc_100k", "Tỷ suất mắc mới (ca/100.000 dân)", ORANGE, height=430),
                use_container_width=True, config=CHART_CONFIG,
            )
        with st.container(border=True):
            section_title("10 quốc gia có số ca mắc mới lớn nhất", f"Năm {selected_year} · Số ca ước tính")
            top_cases = snapshot.dropna(subset=["e_inc_num"]).nlargest(10, "e_inc_num").copy()
            top_cases["case_millions"] = top_cases["e_inc_num"] / 1_000_000
            fig_cases = px.bar(
                top_cases.sort_values("case_millions"), x="case_millions", y="country",
                orientation="h", text="case_millions", color_discrete_sequence=[BLUE],
                hover_data={"iso3": True, "case_millions": ":,.2f"},
            )
            fig_cases.update_traces(
                texttemplate="%{text:.2f}M", textposition="outside", cliponaxis=False,
                hovertemplate="%{y}<br>Số ca ước tính: %{x:,.2f} triệu<extra></extra>",
            )
            fig_cases.update_layout(
                title=None, showlegend=False, xaxis_title="Triệu ca", yaxis_title="",
                margin=dict(l=8, r=25, t=8, b=8), height=410,
            )
            fig_cases.update_xaxes(showgrid=True, gridcolor="#E8EDF3")
            st.plotly_chart(fig_cases, use_container_width=True, config=CHART_CONFIG)
    with rcol:
        with st.container(border=True):
            section_title("Phân bố tỷ suất mắc mới theo quốc gia", f"Năm {selected_year} · Di chuột lên bản đồ để xem từng quốc gia")
            st.plotly_chart(choropleth_figure(snapshot), use_container_width=True, config=CHART_CONFIG)
        with st.container(border=True):
            section_title("So sánh tỷ suất mắc mới giữa các khu vực WHO", f"Năm {selected_year} · Tổng hợp từ các dòng có dữ liệu")
            regional = region_weighted_summary(df, selected_year)
            if selected_regions:
                regional = regional[regional["region_code"].isin(selected_regions)]
            if not regional.empty:
                fig_region = px.bar(
                    regional.sort_values("inc_rate"), x="inc_rate", y="region", orientation="h",
                    text="inc_rate", color_discrete_sequence=[TEAL],
                    hover_data={"countries": True, "inc_cases": ":,.0f"},
                )
                fig_region.update_traces(
                    texttemplate="%{text:.1f}", textposition="outside", cliponaxis=False,
                    hovertemplate="%{y}<br>Tỷ suất mắc mới: %{x:.1f}/100.000 dân<extra></extra>",
                )
                fig_region.update_layout(
                    showlegend=False, xaxis_title="Ca/100.000 dân", yaxis_title="", height=340,
                    margin=dict(l=8, r=25, t=8, b=8),
                )
                fig_region.update_xaxes(showgrid=True, gridcolor="#E8EDF3")
                st.plotly_chart(fig_region, use_container_width=True, config=CHART_CONFIG)
            else:
                st.info("Không có dữ liệu khu vực cho bộ lọc đang chọn.")

    st.markdown(
        "<div class='note'><b>Lưu ý phương pháp:</b> Các số liệu mắc và tử vong là ước tính WHO. "
        "Các tỷ suất tổng hợp trên trang này do đồ án tính bằng cách chia tổng số ca ước tính cho tổng dân số của các quốc gia có dữ liệu, "
        "không phải chỉ số tổng hợp chính thức do WHO công bố. Số lượng thực thể có dữ liệu có thể thay đổi theo năm.</div>",
        unsafe_allow_html=True,
    )
