from __future__ import annotations

import pandas as pd
import streamlit as st

from ..data import cluster_display_name, cluster_profiles, format_decimal, format_int
from ..runtime import get_dataframes
from ..ui import hero, insight_card, section_title


def _country_value(df: pd.DataFrame, iso3: str, year: int, field: str):
    row = df[(df["iso3"].eq(iso3)) & (df["year"].eq(year))]
    return row.iloc[0][field] if not row.empty else None


def _change(start, end):
    if start is None or end is None or pd.isna(start) or pd.isna(end) or float(start) == 0:
        return None
    return (float(end) - float(start)) / float(start) * 100


def _direction_text(start, end, metric: str) -> str:
    if start is None or end is None or pd.isna(start) or pd.isna(end):
        return "không đủ dữ liệu để so sánh"
    if float(end) < float(start):
        return f"giảm từ {format_decimal(start, 1)} xuống {format_decimal(end, 1)} {metric}"
    if float(end) > float(start):
        return f"tăng từ {format_decimal(start, 1)} lên {format_decimal(end, 1)} {metric}"
    return f"giữ nguyên ở mức {format_decimal(end, 1)} {metric}"


def render() -> None:
    df, clusters = get_dataframes()
    hero(
        "Phát hiện và khuyến nghị",
        "Chuyển các kết quả mô tả và phân nhóm thành những điểm cần chú ý, cùng các hướng hành động có căn cứ.",
        "04 / PHÁT HIỆN VÀ ĐỀ XUẤT",
    )

    vn_inc_2000 = _country_value(df, "VNM", 2000, "e_inc_100k")
    vn_inc_2024 = _country_value(df, "VNM", 2024, "e_inc_100k")
    vn_mort_2000 = _country_value(df, "VNM", 2000, "e_mort_100k")
    vn_mort_2024 = _country_value(df, "VNM", 2024, "e_mort_100k")
    vn_inc_2020 = _country_value(df, "VNM", 2020, "e_inc_100k")
    vn_inc_2023 = _country_value(df, "VNM", 2023, "e_inc_100k")
    vn_cdr_2000 = _country_value(df, "VNM", 2000, "c_cdr")
    vn_cdr_2024 = _country_value(df, "VNM", 2024, "c_cdr")

    inc_change = _change(vn_inc_2000, vn_inc_2024)
    mort_change = _change(vn_mort_2000, vn_mort_2024)
    cdr_change = (
        float(vn_cdr_2024) - float(vn_cdr_2000)
        if pd.notna(vn_cdr_2000) and pd.notna(vn_cdr_2024) else None
    )

    st.subheader("Phát hiện 1 — Diễn biến tại Việt Nam")
    c1, c2, c3 = st.columns(3)
    with c1:
        insight_card(
            "Tỷ suất mắc mới 2000 → 2024", f"{inc_change:+.1f}%" if inc_change is not None else "—",
            _direction_text(vn_inc_2000, vn_inc_2024, "ca/100.000 dân"),
        )
    with c2:
        insight_card(
            "Tỷ suất tử vong 2000 → 2024", f"{mort_change:+.1f}%" if mort_change is not None else "—",
            _direction_text(vn_mort_2000, vn_mort_2024, "ca/100.000 dân"),
        )
    with c3:
        cdr_copy = (
            f"Từ {format_decimal(vn_cdr_2000, 1)}% đến {format_decimal(vn_cdr_2024, 1)}%; "
            f"thay đổi {cdr_change:+.1f} điểm phần trăm."
            if cdr_change is not None else "Không đủ dữ liệu để so sánh hai mốc."
        )
        insight_card("Tỷ lệ phát hiện ca bệnh 2000 → 2024", f"{cdr_change:+.1f} điểm %" if cdr_change is not None else "—", cdr_copy)

    if pd.notna(vn_inc_2020) and pd.notna(vn_inc_2023) and pd.notna(vn_inc_2024):
        recent_direction = _direction_text(vn_inc_2020, vn_inc_2023, "ca/100.000 dân")
        st.markdown(
            f"<div class='note'>Trong giai đoạn gần đây, tỷ suất mắc mới ước tính tại Việt Nam {recent_direction} "
            f"trong giai đoạn 2020–2023, sau đó còn {format_decimal(vn_inc_2024, 1)} ca/100.000 dân năm 2024. "
            "Đây là mô tả theo chuỗi ước tính, không đủ để xác định nguyên nhân biến động.</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.subheader("Phát hiện 2 — Khác biệt giữa số ca và tỷ suất mắc mới")
    snapshot = df[df["year"].eq(2024)]
    rate_rows = snapshot.dropna(subset=["e_inc_100k"])
    case_rows = snapshot.dropna(subset=["e_inc_num"])
    if not rate_rows.empty and not case_rows.empty:
        top_rate = rate_rows.nlargest(1, "e_inc_100k").iloc[0]
        top_cases = case_rows.nlargest(1, "e_inc_num").iloc[0]
        c1, c2 = st.columns(2)
        with c1:
            insight_card(
                "Tỷ suất mắc mới cao nhất năm 2024", str(top_rate["country"]),
                f"{format_decimal(top_rate['e_inc_100k'], 1)} ca/100.000 dân. Chỉ số này thể hiện số ca mắc mới ước tính trên 100.000 dân.",
                warning=True,
            )
        with c2:
            insight_card(
                "Số ca mắc mới ước tính lớn nhất năm 2024", str(top_cases["country"]),
                f"{format_int(top_cases['e_inc_num'])} ca ước tính. Thước đo này phản ánh quy mô tuyệt đối.",
            )
        st.caption("Hai cách xếp hạng trả lời hai câu hỏi khác nhau; không nên dùng số ca tuyệt đối thay cho tỷ suất mắc mới hoặc ngược lại.")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.subheader("Phát hiện 3 — Việt Nam trong Khu vực Tây Thái Bình Dương")
    wpr = df[(df["year"].eq(2024)) & (df["g_whoregion"].eq("WPR"))].copy()
    wpr_inc = wpr.dropna(subset=["e_inc_100k"])
    wpr_mort = wpr.dropna(subset=["e_mort_100k"])
    wpr_cdr = wpr.dropna(subset=["c_cdr"])
    vn_wpr = wpr[wpr["iso3"].eq("VNM")]
    if not vn_wpr.empty and not wpr_inc.empty and not wpr_mort.empty and not wpr_cdr.empty:
        wpr_rank_values = wpr_inc["e_inc_100k"].rank(ascending=False, method="min")
        vn_index = wpr_inc.index[wpr_inc["iso3"].eq("VNM")]
        wpr_rank = int(wpr_rank_values.loc[vn_index[0]]) if len(vn_index) else None
        vn_row = vn_wpr.iloc[0]
        inc_median = float(wpr_inc["e_inc_100k"].median())
        mort_median = float(wpr_mort["e_mort_100k"].median())
        cdr_median = float(wpr_cdr["c_cdr"].median())
        a, b, c = st.columns(3)
        with a:
            insight_card(
                "Tỷ suất mắc mới của Việt Nam",
                f"{format_decimal(vn_row['e_inc_100k'], 1)} / 100.000 dân",
                f"Khoảng {format_decimal(vn_row['e_inc_100k'] / inc_median, 2)} lần trung vị khu vực ({format_decimal(inc_median, 1)}). Xếp thứ {wpr_rank}/{len(wpr_inc)} theo tỷ suất mắc mới.",
                warning=True,
            )
        with b:
            insight_card(
                "Tỷ suất tử vong của Việt Nam",
                f"{format_decimal(vn_row['e_mort_100k'], 1)} / 100.000 dân",
                f"Khoảng {format_decimal(vn_row['e_mort_100k'] / mort_median, 2)} lần trung vị khu vực ({format_decimal(mort_median, 1)}).",
                warning=True,
            )
        with c:
            cdr_gap = float(vn_row["c_cdr"]) - cdr_median
            insight_card(
                "Tỷ lệ phát hiện ca bệnh của Việt Nam",
                f"{format_decimal(vn_row['c_cdr'], 1)}%",
                f"Thấp hơn trung vị khu vực {format_decimal(abs(cdr_gap), 1)} điểm phần trăm ({format_decimal(cdr_median, 1)}%).",
                warning=cdr_gap < 0,
            )
        st.caption(
            f"So sánh mô tả trên {len(wpr)} quốc gia/vùng lãnh thổ thuộc Khu vực Tây Thái Bình Dương năm 2024; "
            f"trung vị tỷ suất mắc có {len(wpr_inc)} thực thể, tử vong có {len(wpr_mort)}, và tỷ lệ phát hiện có {len(wpr_cdr)}. "
            "Khác biệt không chứng minh nguyên nhân hoặc chất lượng của một chương trình y tế."
        )
    else:
        st.info("Chưa đủ dữ liệu để so sánh Việt Nam với Khu vực Tây Thái Bình Dương năm 2024.")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.subheader("Phát hiện 4 — Đặc điểm hai nhóm quốc gia")
    profiles = cluster_profiles(clusters)
    cols = st.columns(max(1, len(profiles)))
    for col, (_, row) in zip(cols, profiles.iterrows()):
        with col:
            insight_card(
                cluster_display_name(row["cluster_name_vi"]), f"{int(row['countries'])} quốc gia/vùng lãnh thổ",
                f"Trung vị tỷ suất mắc mới {format_decimal(row['incidence_median'], 1)}/100.000 dân; "
                f"trung vị tỷ suất tử vong {format_decimal(row['mortality_median'], 1)}/100.000 dân; "
                f"Tỷ lệ phát hiện ca bệnh {format_decimal(row['cdr_median'], 1)}%.",
                warning=int(row["cluster_id"]) == 2,
            )

    higher = profiles[profiles["cluster_id"].eq(2)]
    higher_count = int(higher.iloc[0]["countries"]) if not higher.empty else 0
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    section_title(
        "Đề xuất hành động",
        "Các đề xuất dưới đây là hướng ưu tiên phân tích/chính sách ở cấp hệ thống, không phải chỉ định lâm sàng.",
    )
    recommendations = [
        (
            "01", "Ưu tiên rà soát nhóm có hồ sơ gánh nặng tương đối cao",
            f"Sử dụng danh sách {higher_count} quốc gia/vùng lãnh thổ thuộc cụm gánh nặng tương đối cao làm điểm bắt đầu "
            "để xem xét tỷ suất mắc mới, tỷ suất tử vong và tỷ lệ phát hiện ca bệnh cùng lúc. Không xem nhãn nhóm là xếp hạng y tế tuyệt đối.",
        ),
        (
            "02", "Theo dõi đồng thời số ca và tỷ suất mắc mới",
            "Khi so sánh quốc gia, trình bày cả quy mô ca ước tính và tỷ suất trên 100.000 dân để tránh ưu tiên sai do chỉ nhìn một thước đo.",
        ),
        (
            "03", "Kiểm tra khoảng trống dữ liệu và chất lượng báo cáo",
            "Với các quốc gia thiếu dữ liệu về tỷ lệ phát hiện ca bệnh hoặc có giá trị trên 100%, cần xem xét định nghĩa, phương pháp ước tính và độ đầy đủ báo cáo trước khi so sánh.",
        ),
        (
            "04", "Theo dõi chuỗi thời gian và độ bất định",
            "Quan sát nhiều năm liên tiếp, xem xét các cận ước tính thấp/cao của WHO và tránh kết luận dựa trên biến động một năm đơn lẻ.",
        ),
        (
            "05", "Bổ sung phân tích cấp dưới quốc gia khi có dữ liệu phù hợp",
            "Dữ liệu cấp quốc gia không cho biết khác biệt giữa tỉnh/thành hoặc nhóm dân cư. Phân tích chi tiết hơn cần nguồn dữ liệu địa phương có định nghĩa và độ bao phủ phù hợp.",
        ),
        (
            "06", "Đối chiếu sâu hơn tình hình Việt Nam trong khu vực WHO",
            "Năm 2024, tỷ suất mắc mới và tỷ suất tử vong của Việt Nam cao hơn trung vị Khu vực Tây Thái Bình Dương trong bộ dữ liệu; tỷ lệ phát hiện ca bệnh thấp hơn trung vị khu vực. Nên xem đây là tín hiệu để rà soát chuỗi thời gian, độ bất định và dữ liệu chi tiết trong nước, không phải kết luận về nguyên nhân.",
        ),
    ]
    for number, title, body in recommendations:
        with st.container(border=True):
            a, b = st.columns([0.1, 0.9])
            with a:
                st.markdown(f"<div style='color:#149C91;font-weight:800;font-size:1.3rem'>{number}</div>", unsafe_allow_html=True)
            with b:
                st.markdown(f"**{title}**")
                st.write(body)

    st.markdown(
        "<div class='note'><b>Giới hạn diễn giải:</b> Dữ liệu là ước tính ở cấp quốc gia; các mối liên hệ và xu hướng mô tả không chứng minh quan hệ nhân quả. "
        "K-means chỉ gom nhóm theo ba biến được lựa chọn, không đánh giá hiệu quả hệ thống y tế hoặc nguy cơ của từng cá nhân.</div>",
        unsafe_allow_html=True,
    )
