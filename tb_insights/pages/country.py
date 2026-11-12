from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from ..charts import CHART_CONFIG, BLUE, ORANGE, TEAL, country_trend_figure
from ..data import available_years, format_decimal, format_int, region_label
from ..runtime import get_dataframes
from ..ui import hero, section_title


def render() -> None:
    df, _ = get_dataframes()
    years = available_years(df)
    countries = sorted(df["country"].dropna().unique().tolist())
    if not countries or not years:
        st.error("Không tìm thấy dữ liệu quốc gia hợp lệ.")
        return

    hero(
        "Phân tích theo quốc gia",
        "Theo dõi chuỗi thời gian, đối chiếu khu vực WHO và khám phá vị trí tương đối của từng quốc gia.",
        "02 / PHÂN TÍCH THEO QUỐC GIA",
    )

    c1, c2 = st.columns([1.6, 1])
    with c1:
        default_idx = countries.index("Viet Nam") if "Viet Nam" in countries else 0
        country = st.selectbox("Quốc gia / vùng lãnh thổ", countries, index=default_idx, key="country_select")
    with c2:
        year = st.selectbox("Năm đối chiếu", years, index=len(years) - 1, key="country_year")

    selected = df[df["country"].eq(country)].sort_values("year")
    row = selected[selected["year"].eq(year)]
    if row.empty:
        st.warning("Không có dữ liệu cho quốc gia và năm đang chọn.")
        return

    r = row.iloc[0]
    region_code = str(r["g_whoregion"])
    region_name = region_label(region_code)
    latest_rate = r["e_inc_100k"]
    region_rows = df[(df["year"].eq(year)) & (df["g_whoregion"].eq(region_code))]
    valid_region = region_rows.dropna(subset=["e_inc_100k"]).copy()
    region_median_inc = valid_region["e_inc_100k"].median()
    ranks = valid_region["e_inc_100k"].rank(ascending=False, method="min")
    match = valid_region.index[valid_region["iso3"].eq(r["iso3"])]
    rank = int(ranks.loc[match[0]]) if len(match) else None

    st.caption(f"{country} · {region_name} · ISO3: {r['iso3']} · Năm {year}")
    cols = st.columns(5)
    metrics = [
        ("Số ca mắc mới ước tính", format_int(r["e_inc_num"])),
        ("Tỷ suất mắc mới / 100.000 dân", format_decimal(r["e_inc_100k"], 1)),
        ("Số ca tử vong ước tính", format_int(r["e_mort_num"])),
        ("Tỷ suất tử vong / 100.000 dân", format_decimal(r["e_mort_100k"], 1)),
        ("Tỷ lệ phát hiện ca bệnh (%)", format_decimal(r["c_cdr"], 1)),
    ]
    for col, (label, value) in zip(cols, metrics):
        with col:
            st.metric(label, value)

    if pd.notna(r["c_cdr"]) and float(r["c_cdr"]) > 100:
        st.info(
            "Tỷ lệ phát hiện ca bệnh trong bản ghi này lớn hơn 100%. Giá trị được giữ nguyên theo dữ liệu WHO; "
            "không nên diễn giải như tỷ lệ bao phủ thực tế vượt quá 100% nếu chưa xem định nghĩa và phương pháp ước tính."
        )

    left, right = st.columns(2)
    with left:
        with st.container(border=True):
            section_title("Diễn biến tỷ suất mắc mới", "Dải tô thể hiện khoảng ước tính thấp–cao do WHO cung cấp nếu có.")
            st.plotly_chart(
                country_trend_figure(
                    selected, "e_inc_100k", "e_inc_100k_lo", "e_inc_100k_hi",
                    "Tỷ suất mắc mới ước tính", BLUE,
                ),
                use_container_width=True, config=CHART_CONFIG,
            )
    with right:
        with st.container(border=True):
            section_title("Diễn biến tỷ suất tử vong", "Số ca tử vong ước tính trên 100.000 dân.")
            st.plotly_chart(
                country_trend_figure(
                    selected, "e_mort_100k", "e_mort_100k_lo", "e_mort_100k_hi",
                    "Tỷ suất tử vong ước tính", TEAL,
                ),
                use_container_width=True, config=CHART_CONFIG,
            )

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    a, b = st.columns([1, 1.2])
    with a:
        with st.container(border=True):
            section_title(
                "Vị trí trong khu vực WHO",
                f"Xếp hạng theo tỷ suất mắc mới năm {year} trong các quốc gia/vùng lãnh thổ có dữ liệu thuộc {region_name}.",
            )
            st.metric("Thứ hạng theo tỷ suất mắc mới", f"#{rank}" if rank is not None else "—")
            st.metric("Số thực thể có dữ liệu", format_int(len(valid_region)))
            st.metric("Trung vị tỷ suất mắc mới của khu vực", f"{format_decimal(region_median_inc, 1)} / 100.000")
            if pd.notna(latest_rate) and pd.notna(region_median_inc) and region_median_inc > 0:
                ratio = latest_rate / region_median_inc
                st.markdown(
                    f"<div class='note'>Tỷ suất mắc mới của <b>{country}</b> bằng khoảng "
                    f"<b>{format_decimal(ratio, 2)} lần</b> trung vị của khu vực. "
                    "Đây là so sánh mô tả, không giải thích nguyên nhân khác biệt.</div>",
                    unsafe_allow_html=True,
                )
    with b:
        with st.container(border=True):
            section_title(
                "So sánh tỷ suất mắc mới trong khu vực",
                f"12 quốc gia có tỷ suất mắc mới cao và luôn giữ quốc gia đang chọn trong biểu đồ · {region_name} · {year}",
            )
            top = valid_region.nlargest(12, "e_inc_100k").copy()
            if r["iso3"] not in set(top["iso3"]):
                top = pd.concat([top, valid_region[valid_region["iso3"].eq(r["iso3"])]])
            top = top.drop_duplicates("iso3")
            top["comparison_group"] = top["iso3"].eq(r["iso3"]).map({True: "Quốc gia đang chọn", False: "Các quốc gia khác"})
            fig = px.bar(
                top.sort_values("e_inc_100k"), x="e_inc_100k", y="country", orientation="h",
                color="comparison_group",
                color_discrete_map={"Quốc gia đang chọn": ORANGE, "Các quốc gia khác": BLUE},
                hover_data={"iso3": True, "e_mort_100k": ":,.1f", "c_cdr": ":,.1f"},
                labels={"e_inc_100k": "Tỷ suất mắc mới/100.000 dân", "country": "", "comparison_group": ""},
            )
            fig.update_traces(hovertemplate="%{y}<br>Tỷ suất mắc mới: %{x:,.1f}/100.000 dân<extra></extra>")
            fig.update_layout(
                showlegend=False, xaxis_title="Ca/100.000 dân", yaxis_title="", height=420,
                margin=dict(l=8, r=18, t=8, b=8),
            )
            fig.update_xaxes(showgrid=True, gridcolor="#E8EDF3")
            st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

    with st.expander("Xem bảng dữ liệu lịch sử của quốc gia"):
        display_cols = [
            "year", "e_inc_num", "e_inc_100k", "e_mort_num", "e_mort_100k",
            "c_newinc_100k", "c_cdr",
        ]
        st.dataframe(
            selected[display_cols].rename(columns={
                "year": "Năm", "e_inc_num": "Ca mắc mới ước tính", "e_inc_100k": "Mắc mới/100.000 dân",
                "e_mort_num": "Tử vong ước tính", "e_mort_100k": "Tử vong/100.000 dân",
                "c_newinc_100k": "Ca mới/tái phát được thông báo/100.000 dân", "c_cdr": "Tỷ lệ phát hiện ca bệnh (%)",
            }),
            use_container_width=True, hide_index=True,
        )

    st.markdown(
        "<div class='note'><b>Diễn giải:</b> Các chỉ số là ước tính hoặc chỉ số báo cáo ở cấp quốc gia. "
        "Không thể dùng dữ liệu tổng hợp quốc gia để kết luận về tình trạng của một cá nhân hoặc một địa phương cụ thể.</div>",
        unsafe_allow_html=True,
    )
