from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from ..charts import CHART_CONFIG, TEAL
from ..data import (
    data_quality_summary, format_int, validate_inputs,
    year_coverage_summary, load_kmeans_benchmark,
)
from ..runtime import get_dataframes
from ..ui import hero, section_title


def render() -> None:
    df, clusters = get_dataframes()
    hero(
        "Dữ liệu và phương pháp",
        "Nguồn dữ liệu, quy trình xử lý, cấu hình khai phá dữ liệu và những giới hạn cần biết khi đọc kết quả.",
        "05 / DỮ LIỆU VÀ PHƯƠNG PHÁP",
    )

    st.subheader("Nguồn dữ liệu")
    st.markdown(
        "Dữ liệu nền được lấy từ bộ WHO Tuberculosis Burden Estimates và Data Dictionary do người thực hiện cung cấp trong đồ án. "
        "Tên file đầu vào thể hiện ngày tải **29/10/2026**. Tham khảo nguồn chính thức: "
        "[WHO Global Tuberculosis Programme – Data](https://www.who.int/teams/global-tuberculosis-programme/data)."
    )
    benchmark = load_kmeans_benchmark()
    selected_benchmark = benchmark[benchmark["is_selected"]] if not benchmark.empty else benchmark
    silhouette_value = float(selected_benchmark.iloc[0]["silhouette"]) if not selected_benchmark.empty else float("nan")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Bản ghi quốc gia–năm", format_int(len(df)))
    c2.metric("Khoảng thời gian", f"{int(df['year'].min())}–{int(df['year'].max())}")
    c3.metric("Mã ISO3 phân biệt", format_int(df["iso3"].nunique()))
    c4.metric("Quốc gia được phân nhóm", format_int(len(clusters)))

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    section_title("Nhóm biến sử dụng")
    variables = pd.DataFrame([
        ["e_inc_100k", "Tỷ suất mắc mới lao ước tính trên 100.000 dân", "Phân tích xu hướng, so sánh quốc gia, K-means"],
        ["e_inc_num", "Số ca mắc lao ước tính", "KPI số ca và tính tỷ suất tổng hợp"],
        ["e_mort_100k", "Tỷ suất tử vong do lao ước tính trên 100.000 dân", "Phân tích xu hướng, so sánh quốc gia, K-means"],
        ["e_mort_num", "Số ca tử vong do lao ước tính", "KPI số ca và tính tỷ suất tổng hợp"],
        ["c_cdr", "Tỷ lệ phát hiện ca bệnh (WHO cũng dùng chỉ số này để thể hiện độ bao phủ điều trị), tính bằng %", "Phân tích mô tả và K-means"],
        ["e_pop_num", "Dân số ước tính", "Mẫu số khi tính tỷ suất tổng hợp; không đưa vào K-means"],
    ], columns=["Biến", "Ý nghĩa", "Vai trò trong đồ án"])
    st.dataframe(
        variables,
        use_container_width=True, hide_index=True,
    )

    st.subheader("Chất lượng và độ đầy đủ dữ liệu")
    quality = data_quality_summary(df)
    st.dataframe(
        quality,
        column_config={
            "Chỉ số": st.column_config.TextColumn("Chỉ số"),
            "Cột": st.column_config.TextColumn("Tên cột"),
            "Thiếu": st.column_config.NumberColumn("Thiếu", format="%d"),
            "Đầy đủ": st.column_config.NumberColumn("Có dữ liệu", format="%d"),
            "Tỷ lệ đầy đủ (%)": st.column_config.NumberColumn("Tỷ lệ đầy đủ (%)", format="%.1f"),
        },
        use_container_width=True, hide_index=True,
    )
    coverage = year_coverage_summary(df)
    if not coverage.empty:
        with st.container(border=True):
            section_title("Mức độ bao phủ dữ liệu theo năm", "Số thực thể có đủ dữ liệu cho từng chỉ số; số lượng có thể thay đổi theo năm.")
            fig = px.line(
                coverage, x="year",
                y=["incidence_available", "mortality_available", "cdr_available"],
                markers=True,
                labels={
                    "year": "Năm", "value": "Số thực thể", "variable": "Chỉ số",
                    "incidence_available": "Có dữ liệu mắc", "mortality_available": "Có dữ liệu tử vong",
                    "cdr_available": "Có dữ liệu về tỷ lệ phát hiện ca bệnh",
                },
                color_discrete_sequence=["#4F78D8", TEAL, "#E58A4E"],
            )
            fig.update_layout(legend_title_text="", yaxis_title="Số quốc gia/vùng lãnh thổ", xaxis_title="Năm")
            st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

    cdr_over_100 = int((df["c_cdr"] > 100).sum())
    cdr_missing = int(df["c_cdr"].isna().sum())
    st.info(
        f"Chỉ số tỷ lệ phát hiện ca bệnh có {format_int(cdr_missing)} bản ghi thiếu và {format_int(cdr_over_100)} bản ghi lớn hơn 100 trong toàn bộ chuỗi dữ liệu. "
        "Các giá trị này được giữ nguyên, không tự động thay bằng 0 hoặc giới hạn ở 100. Cần đọc theo định nghĩa và phương pháp ước tính của WHO."
    )

    st.subheader("Quy trình tiền xử lý")
    st.markdown("""
    1. Giữ nguyên file nguồn; tạo bản phân tích riêng.
    2. Loại hai cột hoàn toàn trống khỏi bản phân tích.
    3. Chuẩn hóa khoảng trắng, mã ISO3, mã WHO region và kiểu dữ liệu năm.
    4. Không tự động điền giá trị thiếu bằng 0.
    5. Không tự ý giới hạn các giá trị tỷ lệ phát hiện ca bệnh lớn hơn 100; giữ nguyên và diễn giải thận trọng.
    6. Khi tính tỷ suất tổng hợp, chỉ đưa dân số của các quốc gia có số ca ước tính tương ứng vào mẫu số.
    """)

    st.subheader("Cách phân nhóm quốc gia bằng K-means")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Quốc gia có đủ dữ liệu", format_int(len(clusters)))
    k2.metric("Số cụm", format_int(clusters["cluster_id"].nunique()))
    k3.metric("Cách chuẩn hóa", "Trung vị và độ phân tán")
    k4.metric(
        "Mức độ tách biệt nhóm",
        format_decimal(silhouette_value, 3) if pd.notna(silhouette_value) else "—",
        help="Chỉ số Silhouette; giá trị càng gần 1 thường cho thấy các nhóm càng tách biệt trong không gian đặc trưng đã chuẩn hóa.",
    )
    if not benchmark.empty:
        chosen = selected_benchmark.iloc[0] if not selected_benchmark.empty else benchmark.iloc[0]
        b1, b2, b3 = st.columns(3)
        b1.metric("Silhouette Score", f"{float(chosen['silhouette']):.3f}")
        b2.metric("Calinski–Harabasz", f"{float(chosen['calinski_harabasz']):.1f}")
        b3.metric("Davies–Bouldin", f"{float(chosen['davies_bouldin']):.3f}")
        with st.expander("Xem toàn bộ bảng so sánh 21 cấu hình K-means"):
            display_benchmark = benchmark.rename(columns={
                "preprocessing_vi": "Cách chuẩn hóa", "k": "Số nhóm K",
                "silhouette": "Silhouette Score", "calinski_harabasz": "Calinski–Harabasz",
                "davies_bouldin": "Davies–Bouldin", "cluster_sizes_ascending": "Kích thước nhóm",
                "is_selected": "Được chọn",
            })
            st.dataframe(display_benchmark, use_container_width=True, hide_index=True)

    st.markdown("""
    - Thời điểm: năm 2024.
    - Ba chỉ số đầu vào: tỷ suất mắc mới, tỷ suất tử vong và tỷ lệ phát hiện ca bệnh.
    - Cấu hình: K-means với 2 nhóm; dữ liệu được chuẩn hóa bằng RobustScaler (dựa trên trung vị và khoảng tứ phân vị), `random_state=42`, `n_init=50`.
    - Đánh giá bổ sung: Calinski–Harabasz 249,6; Davies–Bouldin 0,636; ARI trung bình cặp giữa 10 lần khởi tạo độc lập 0,985.
    - Lý do chọn: trong 21 tổ hợp gồm 3 cách tiền xử lý và K từ 2 đến 8, cấu hình RobustScaler với K=2 có Silhouette cao nhất. Quyết định còn được xem xét cùng kích thước cụm, độ ổn định và khả năng diễn giải; không chỉ dựa vào một chỉ số.
    - Kiểm tra độ nhạy: loại riêng ba quan sát có `c_cdr > 100` cho ARI 1,000 trên 190 quốc gia còn lại; đây là kiểm tra độ nhạy, không phải quy tắc loại dữ liệu chính.
    """)

    st.subheader("Kiểm tra tính toàn vẹn của dữ liệu ứng dụng")
    issues = validate_inputs(df, clusters)
    if issues:
        for issue in issues:
            st.error(issue)
    else:
        st.success("Hai bảng dữ liệu đã qua kiểm tra cấu trúc, khóa quốc gia–năm và số quốc gia có đủ dữ liệu để phân nhóm.")

    st.subheader("Giới hạn")
    st.markdown("""
    - Các biến `e_*` là ước tính của WHO, không phải số đếm quan sát trực tiếp của mọi ca bệnh thực tế.
    - Dữ liệu là cấp quốc gia/vùng lãnh thổ, không đại diện cho từng cá nhân hoặc từng tỉnh/thành.
    - Tỷ suất tổng hợp trên dashboard được đồ án tính từ tổng số ca ước tính chia cho tổng dân số của các quốc gia có dữ liệu; đây không phải chỉ số tổng hợp chính thức do WHO công bố.
    - Số thực thể có dữ liệu có thể thay đổi theo năm; khi diễn giải xu hướng cần lưu ý độ bao phủ.
    - Ước tính có bất định; xem các cận `_lo` và `_hi` khi phù hợp.
    - K-means là phương pháp không giám sát; nhãn nhóm mang tính tương đối, phụ thuộc vào biến và cách tiền xử lý, không chứng minh quan hệ nhân quả.
    - Dashboard chỉ phục vụ mục đích học thuật và khám phá dữ liệu; không dùng để chẩn đoán hoặc ra quyết định điều trị cá nhân.
    """)
