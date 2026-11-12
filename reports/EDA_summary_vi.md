# Báo cáo giai đoạn 2–3: Tiền xử lý và EDA dữ liệu bệnh lao WHO

## 1. Phạm vi và dữ liệu
- File nguồn: `TB_burden_countries_2026-10-29.csv`
- Từ điển biến: `TB_data_dictionary_2026-10-29.csv`
- Quy mô: 5,347 dòng, 50 cột, 2000–2024, 217 mã ISO3 khác nhau.
- Số dòng năm 2024: 215; số dòng có đủ ba biến `e_inc_100k`, `e_mort_100k`, `c_cdr`: 193.
- Đơn vị phân tích: quốc gia/vùng lãnh thổ theo từng năm; không xem các dòng là dữ liệu cá nhân bệnh nhân.

## 2. Quyết định tiền xử lý
- Bỏ khỏi bản phân tích 2 cột hoàn toàn trống: e_tbhiv_prct_lo, e_tbhiv_prct_hi. File gốc được giữ nguyên.
- Chuẩn hóa khoảng trắng ở tên quốc gia và mã; chuẩn hóa mã ISO3 và mã WHO region về chữ in hoa; chuyển `year` về số nguyên.
- Không điền giá trị thiếu; không loại bản ghi có dữ liệu thiếu khỏi bản đầy đủ. Phân tích từng chỉ số sử dụng các quan sát có dữ liệu ở đúng biến cần thiết.
- Không phát hiện trùng lặp theo `iso3-year`, `country-year` hoặc toàn bộ dòng.
- Không phát hiện giá trị âm trong các biến số cốt lõi hoặc dân số không dương.
- Có 25 dòng thiếu `e_inc_100k` và `e_mort_100k`; tất cả thuộc Democratic People's Republic of Korea trong 2000–2024.
- `c_cdr` thiếu 364 dòng (6.8%). Không thay bằng 0.
- Có 8 giá trị `c_cdr` lớn hơn 100. Giữ nguyên và gắn cờ để diễn giải; không tự động cắt về 100.

## 3. Phát hiện EDA ban đầu
- Trong file, tỷ lệ mắc lao ước tính tại Việt Nam giảm từ 296 xuống 182 ca/100.000 dân trong giai đoạn 2000–2024 (-38.5%).
- Tỷ lệ tử vong lao ước tính tại Việt Nam giảm từ 47 xuống 12 ca/100.000 dân trong giai đoạn 2000–2024 (-74.5%).
- Tỷ lệ mắc ước tính tại Việt Nam tăng từ 171 năm 2020 lên 185 năm 2023, sau đó giảm còn 182 năm 2024.
- Chỉ số c_cdr của Việt Nam thay đổi từ 39% năm 2000 lên 58% năm 2024; đây là chỉ số WHO định nghĩa là case detection rate, còn được gọi là TB treatment coverage.
- Năm 2024, Kiribati có tỷ lệ mắc ước tính cao nhất trong file (945/100.000 dân), trong khi India có số ca mắc ước tính lớn nhất (2,710,000 ca). Hai cách xếp hạng trả lời hai câu hỏi khác nhau: tỷ lệ theo dân số và quy mô tuyệt đối.

## 4. Hạn chế và lưu ý diễn giải
- `e_inc_num`, `e_inc_100k`, `e_mort_num`, `e_mort_100k` là các ước tính theo định nghĩa WHO trong từ điển biến; không mô tả chúng như số đếm quan sát trực tiếp.
- Số ca tuyệt đối và tỷ lệ trên 100.000 dân không thể thay thế cho nhau. Quốc gia đông dân có thể có số ca lớn nhưng tỷ lệ không cao nhất.
- Bảng và biểu đồ theo WHO region được tính lại từ các dòng quốc gia có dữ liệu và trọng số dân số. Đây là tổng hợp tính toán từ file, không phải số liệu tổng hợp chính thức do WHO công bố trong một dòng riêng.
- Chuỗi dữ liệu quốc gia không cân bằng hoàn toàn: số thực thể mỗi năm thay đổi; một số thực thể lịch sử có ít năm dữ liệu. Cần nêu rõ phạm vi khi so sánh dài hạn.
- Các ước tính có thể có bất định; khi trình bày, cần xem xét các cận `_lo` và `_hi` khi phù hợp.
- Tương quan hoặc xu hướng mô tả không chứng minh quan hệ nhân quả.

## 5. Các file đầu ra
- `data/processed/TB_cleaned_full.csv`: bản phân tích với các cột hoàn toàn trống đã loại bỏ.
- `data/processed/TB_core_analysis.csv`: tập biến cốt lõi đã chọn.
- `data/processed/vietnam_time_series.csv`: chuỗi thời gian Việt Nam.
- `data/processed/country_comparison_2024.csv`: dữ liệu so sánh năm mới nhất.
- `data/processed/who_region_weighted_trends.csv`: xu hướng theo khu vực WHO, trọng số dân số, tính từ các thực thể có dữ liệu.
- `data/processed/kmeans_candidate_2024_complete_cases.csv`: tập ứng viên cho bước K-means tiếp theo (complete cases, chưa huấn luyện mô hình).
- `charts/`: biểu đồ EDA.
- `reports/`: bảng kiểm tra chất lượng, độ thiếu và phạm vi dữ liệu.