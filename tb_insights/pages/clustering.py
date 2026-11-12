from __future__ import annotations

import pandas as pd
import streamlit as st

from ..charts import (
    CHART_CONFIG,
    cluster_profile_comparison,
    cluster_region_figure,
    cluster_region_share_figure,
    clustering_scatter,
    kmeans_model_selection_figure,
)
from ..data import (
    CLUSTER_DISPLAY_NAMES,
    cluster_display_name,
    cluster_profiles,
    load_kmeans_benchmark,
    format_decimal,
    format_int,
    region_label,
)
from ..runtime import get_dataframes
from ..ui import hero, section_title


def render() -> None:
    _, clusters = get_dataframes()
    hero(
        "Phân nhóm quốc gia",
        "Nhóm các quốc gia có đặc điểm bệnh lao tương đồng dựa trên số liệu năm 2024.",
        "03 / PHÂN TÍCH NHÓM QUỐC GIA · K-MEANS",
    )

    regions = sorted(clusters["g_whoregion"].dropna().unique().tolist())
    labels = sorted(clusters["cluster_name_vi"].dropna().unique().tolist())
    c1, c2 = st.columns([1, 1])
    with c1:
        selected_regions = st.multiselect(
            "Khu vực WHO",
            regions,
            default=[],
            format_func=region_label,
            placeholder="Tất cả khu vực",
            key="cluster_regions",
        )
    with c2:
        selected_clusters = st.multiselect(
            "Nhóm quốc gia",
            labels,
            default=labels,
            format_func=cluster_display_name,
            placeholder="Chọn nhóm muốn xem",
            key="cluster_labels",
        )
    st.caption(
        "Để trống khu vực sẽ hiển thị tất cả khu vực. Có thể chọn một hoặc cả hai nhóm quốc gia."
    )

    scoped = clusters.copy()
    if selected_regions:
        scoped = scoped[scoped["g_whoregion"].isin(selected_regions)]
    if selected_clusters:
        scoped = scoped[scoped["cluster_name_vi"].isin(selected_clusters)]
    else:
        scoped = scoped.iloc[0:0]

    if scoped.empty:
        st.warning("Không có quốc gia phù hợp. Hãy thay đổi bộ lọc khu vực hoặc nhóm quốc gia.")
        return

    total_countries = int(clusters["iso3"].nunique())
    selected_cluster_count = int(scoped["cluster_id"].nunique())
    benchmark = load_kmeans_benchmark()
    selected_benchmark = benchmark[benchmark["is_selected"]] if not benchmark.empty else benchmark
    silhouette_value = float(selected_benchmark.iloc[0]["silhouette"]) if not selected_benchmark.empty else float("nan")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Quốc gia đã được phân nhóm", format_int(total_countries))
    m2.metric("Số nhóm đang hiển thị", format_int(selected_cluster_count))
    m3.metric(
        "Silhouette của mô hình đầy đủ",
        format_decimal(silhouette_value, 3) if pd.notna(silhouette_value) else "—",
        help=(
            "Chỉ số được tính trên toàn bộ 193 quốc gia/vùng lãnh thổ của mô hình đã chọn, "
            "không thay đổi theo bộ lọc đang xem. Giá trị càng gần 1 thường cho thấy các nhóm "
            "càng tách biệt trong không gian đặc trưng đã chuẩn hóa; đây không phải chỉ số nguy cơ y tế."
        ),
    )
    m4.metric("Quốc gia phù hợp bộ lọc", format_int(scoped["iso3"].nunique()))

    st.markdown(
        "<div class='note'><b>Cách phân nhóm:</b> Thuật toán K-means so sánh ba chỉ số: "
        "tỷ suất mắc mới ước tính, tỷ suất tử vong ước tính và tỷ lệ phát hiện ca bệnh. "
        "Trước khi phân nhóm, các chỉ số được đưa về thang đo có thể so sánh bằng RobustScaler "
        "(cách chuẩn hóa ít bị ảnh hưởng bởi giá trị quá lớn). Tên nhóm chỉ mô tả sự khác biệt trong "
        "bộ dữ liệu, không phải mức nguy cơ bệnh của người dân hay bảng xếp hạng quốc gia. "
        "Biểu đồ phân bố dùng thang logarit để các quốc gia có giá trị rất cao không làm các điểm còn lại bị dồn sát nhau.</div>",
        unsafe_allow_html=True,
    )

    with st.expander("Kiểm chứng cách chọn số nhóm và phương pháp chuẩn hóa", expanded=False):
        st.write(
            "Đồ án đã so sánh 3 cách chuẩn hóa và các giá trị K từ 2 đến 8. "
            "Biểu đồ thể hiện Silhouette Score; điểm hình ngôi sao là cấu hình được chọn. "
            "Điểm cao hơn thường cho thấy các nhóm tách biệt tốt hơn, nhưng cần xem thêm "
            "độ ổn định, kích thước cụm và khả năng diễn giải."
        )
        st.plotly_chart(
            kmeans_model_selection_figure(benchmark),
            use_container_width=True,
            config=CHART_CONFIG,
        )
        if not benchmark.empty:
            table = benchmark.rename(columns={
                "preprocessing_vi": "Cách chuẩn hóa",
                "k": "Số nhóm K",
                "silhouette": "Silhouette Score",
                "calinski_harabasz": "Calinski–Harabasz",
                "davies_bouldin": "Davies–Bouldin",
                "cluster_sizes_ascending": "Kích thước các nhóm",
                "is_selected": "Cấu hình được chọn",
            })
            keep = [c for c in ["Cách chuẩn hóa", "Số nhóm K", "Silhouette Score", "Calinski–Harabasz", "Davies–Bouldin", "Kích thước các nhóm", "Cấu hình được chọn"] if c in table.columns]
            st.dataframe(
                table[keep].sort_values(["Cấu hình được chọn", "Silhouette Score"], ascending=[False, False]),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Silhouette Score": st.column_config.NumberColumn(format="%.3f"),
                    "Calinski–Harabasz": st.column_config.NumberColumn(format="%.1f"),
                    "Davies–Bouldin": st.column_config.NumberColumn(format="%.3f"),
                },
            )
        st.caption(
            "Cấu hình cuối cùng: RobustScaler trên ba biến gốc, K=2, random_state=42, n_init=50. "
            "Silhouette được dùng để so sánh nội bộ các cấu hình; đây không phải bằng chứng rằng "
            "hai nhóm là phân loại y tế tự nhiên hoặc duy nhất."
        )

    left, right = st.columns([1.35, 1])
    with left:
        with st.container(border=True):
            section_title(
                "Các quốc gia trên biểu đồ phân bố",
                "Mỗi chấm đại diện cho một quốc gia/vùng lãnh thổ; chấm lớn hơn tương ứng dân số lớn hơn. "
                "Việt Nam được đánh dấu bằng ngôi sao. Di chuột lên chấm để xem số liệu gốc.",
            )
            st.plotly_chart(clustering_scatter(scoped), use_container_width=True, config=CHART_CONFIG)
    with right:
        with st.container(border=True):
            section_title(
                "So sánh đặc điểm giữa các nhóm",
                "Mỗi chỉ số được so sánh với giá trị trung vị cao nhất trong toàn bộ 193 quốc gia. Trung vị là giá trị nằm giữa khi sắp xếp dữ liệu. "
                "Bảng bên dưới cung cấp số liệu thực tế.",
            )
            profile_scope = cluster_profiles(scoped)
            profile_reference = cluster_profiles(clusters)
            st.plotly_chart(
                cluster_profile_comparison(profile_scope, profile_reference),
                use_container_width=True,
                config=CHART_CONFIG,
            )
            shown = profile_scope.copy()
            shown["cluster_name_vi"] = shown["cluster_name_vi"].map(cluster_display_name)
            shown = shown.rename(columns={
                "cluster_name_vi": "Nhóm quốc gia",
                "countries": "Số quốc gia",
                "share_pct": "Tỷ trọng (%)",
                "incidence_median": "Trung vị tỷ suất mắc mới/100.000 dân",
                "mortality_median": "Trung vị tỷ suất tử vong/100.000 dân",
                "cdr_median": "Trung vị tỷ lệ phát hiện ca bệnh (%)",
            })
            st.dataframe(
                shown[[
                    "Nhóm quốc gia", "Số quốc gia", "Tỷ trọng (%)",
                    "Trung vị tỷ suất mắc mới/100.000 dân",
                    "Trung vị tỷ suất tử vong/100.000 dân",
                    "Trung vị tỷ lệ phát hiện ca bệnh (%)",
                ]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Tỷ trọng (%)": st.column_config.NumberColumn(format="%.1f%%"),
                    "Trung vị tỷ suất mắc mới/100.000 dân": st.column_config.NumberColumn(format="%.1f"),
                    "Trung vị tỷ suất tử vong/100.000 dân": st.column_config.NumberColumn(format="%.1f"),
                    "Trung vị tỷ lệ phát hiện ca bệnh (%)": st.column_config.NumberColumn(format="%.1f"),
                },
            )

    with st.container(border=True):
        section_title(
            "Phân bố nhóm theo khu vực WHO",
            "Có hai cách nhìn: số lượng tuyệt đối và tỷ trọng của từng nhóm trong chính khu vực đó.",
        )
        count_tab, share_tab = st.tabs(["Số lượng", "Tỷ trọng trong khu vực (%)"])
        with count_tab:
            st.plotly_chart(cluster_region_figure(scoped), use_container_width=True, config=CHART_CONFIG)
        with share_tab:
            st.plotly_chart(cluster_region_share_figure(scoped), use_container_width=True, config=CHART_CONFIG)

    with st.container(border=True):
        section_title(
            "Danh sách quốc gia và số liệu",
            "Tìm tên quốc gia hoặc lọc theo khu vực và nhóm bằng các lựa chọn phía trên.",
        )
        search = st.text_input(
            "Tìm quốc gia",
            placeholder="Ví dụ: Viet Nam, India, Brazil…",
            key="cluster_search",
        )
        table = scoped.copy()
        if search.strip():
            table = table[table["country"].str.contains(search.strip(), case=False, na=False)]
        table = table.sort_values(["cluster_id", "e_inc_100k"], ascending=[True, False])
        display = table[[
            "country", "iso3", "g_whoregion", "cluster_name_vi", "e_inc_100k", "e_mort_100k", "c_cdr",
        ]].copy()
        display["g_whoregion"] = display["g_whoregion"].map(region_label)
        display["cluster_name_vi"] = display["cluster_name_vi"].map(cluster_display_name)
        display = display.rename(columns={
            "country": "Quốc gia/vùng lãnh thổ",
            "iso3": "Mã quốc gia",
            "g_whoregion": "Khu vực WHO",
            "cluster_name_vi": "Nhóm quốc gia",
            "e_inc_100k": "Tỷ suất mắc mới/100.000 dân",
            "e_mort_100k": "Tỷ suất tử vong/100.000 dân",
            "c_cdr": "Tỷ lệ phát hiện ca bệnh (%)",
        })
        st.dataframe(
            display,
            use_container_width=True,
            hide_index=True,
            height=420,
            column_config={
                "Tỷ suất mắc mới/100.000 dân": st.column_config.NumberColumn(format="%.1f"),
                "Tỷ suất tử vong/100.000 dân": st.column_config.NumberColumn(format="%.1f"),
                "Tỷ lệ phát hiện ca bệnh (%)": st.column_config.NumberColumn(format="%.1f"),
            },
        )
        st.download_button(
            "Tải danh sách đang lọc (CSV)",
            table.to_csv(index=False).encode("utf-8-sig"),
            file_name="danh_sach_quoc_gia_theo_nhom.csv",
            mime="text/csv",
        )
