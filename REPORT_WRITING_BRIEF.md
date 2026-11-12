# Phiếu chuẩn bị viết báo cáo — Đồ án CT312, đề tài 1

Tài liệu này là bản tóm tắt các nội dung và số liệu đã kiểm tra để người thực hiện dùng khi tự viết báo cáo. Đây **không phải báo cáo hoàn chỉnh**. Khi viết, cần diễn đạt bằng lời của mình, thêm ảnh dashboard/screenshot thực tế sau khi kiểm thử trên máy, và trích dẫn đầy đủ nguồn WHO cùng tài liệu thuật toán.

## 1. Bố cục báo cáo theo đề cương

1. Giới thiệu vấn đề: bệnh lao và nhu cầu khai thác dữ liệu để theo dõi gánh nặng bệnh lao; mục tiêu, phạm vi, câu hỏi phân tích.
2. Giới thiệu dữ liệu: nguồn WHO TB Burden Estimates, ngày tải 29/10/2026, Data Dictionary; cấp quan sát quốc gia/vùng lãnh thổ theo năm; mô tả các biến.
3. Cơ sở lý thuyết: thống kê mô tả và tỷ suất; làm sạch dữ liệu; chuẩn hóa RobustScaler; thuật toán K-means; Silhouette, Calinski–Harabasz, Davies–Bouldin; Adjusted Rand Index (ARI); PCA chỉ để trực quan hóa.
4. Thiết kế và cài đặt: kiến trúc dự án, pipeline tiền xử lý, EDA, lựa chọn mô hình, đánh giá mô hình, dashboard Streamlit + Plotly.
5. Kết quả đạt được: chất lượng dữ liệu, phát hiện EDA, kết quả K-means, các chức năng dashboard và đề xuất hành động.
6. Hạn chế và hướng phát triển: ước tính WHO, thiếu dữ liệu, biến động độ bao phủ, dữ liệu cấp quốc gia, các giới hạn của K-means; đề xuất dữ liệu cấp dưới quốc gia/chuỗi thời gian/độ bất định.

## 2. Mô tả dữ liệu đã xác minh

- CSV WHO gốc: 5.347 dòng, 50 cột.
- Sau khi bỏ 2 cột hoàn toàn trống: 5.347 dòng, 48 cột.
- Bảng ứng dụng: 5.347 dòng, 25 cột; 217 mã ISO3; giai đoạn 2000–2024.
- Không có khóa `iso3`–`year` trùng.
- Năm 2024 có 215 thực thể; 214 thực thể có số ca mắc/tử vong ước tính và dân số; 193 thực thể có đủ ba biến dùng cho K-means.
- Không tự động điền thiếu bằng 0. Không cắt các giá trị `c_cdr > 100`; có 8 quan sát như vậy trên toàn chuỗi và 3 trong mẫu K-means 2024.

## 3. Công thức tỷ suất tổng hợp do đồ án tính

Tỷ suất mắc mới tổng hợp (phép tính của đồ án):

`Tổng số ca mắc mới ước tính của các thực thể có dữ liệu / Tổng dân số tương ứng × 100.000`.

Tỷ suất tử vong tổng hợp được tính tương tự bằng số ca tử vong ước tính.

Đây là phép tổng hợp từ các dòng quốc gia/vùng lãnh thổ, không phải chỉ số toàn cầu chính thức do WHO công bố. Khi viết báo cáo, phải nói rõ mẫu số chỉ gồm dân số thuộc các thực thể có tử số hợp lệ tương ứng.

### KPI năm 2024

- Số ca mắc mới ước tính: 10.553.581; 214 thực thể có dữ liệu.
- Tỷ suất mắc mới tổng hợp: 130,2 ca/100.000 dân.
- Số ca tử vong ước tính: 1.198.800; 214 thực thể có dữ liệu.
- Tỷ suất tử vong tổng hợp: 14,8 ca/100.000 dân.

## 4. Phát hiện EDA đã xác minh

### Việt Nam, 2000–2024

- Tỷ suất mắc mới ước tính: 296 năm 2000, 199 năm 2015, 171 năm 2020, 185 năm 2023, 182 năm 2024 (ca/100.000 dân).
- Tỷ suất tử vong ước tính: 47 năm 2000, 18 năm 2015, 12 năm 2020, 13 năm 2023, 12 năm 2024 (ca/100.000 dân).
- Chỉ số `c_cdr`: 39% năm 2000 và 58% năm 2024.
- Có thể mô tả xu hướng giảm dài hạn trong chuỗi ước tính, đồng thời lưu ý tỷ suất mắc tăng từ 2020 đến 2023 trước khi giảm nhẹ năm 2024. Không suy diễn nguyên nhân từ dữ liệu mô tả.

### Phân biệt số ca tuyệt đối và tỷ suất

- Kiribati có tỷ suất mắc mới ước tính cao nhất năm 2024 trong file: 945 ca/100.000 dân.
- Ấn Độ có số ca mắc mới ước tính tuyệt đối cao nhất: 2.710.000.
- Hai kết quả trả lời hai câu hỏi khác nhau; không dùng hai thứ hạng thay thế cho nhau.

### Việt Nam so với Khu vực Tây Thái Bình Dương (WPR), năm 2024

- Tỷ suất mắc mới Việt Nam: 182; trung vị WPR: 55 ca/100.000 dân; thứ hạng Việt Nam là 10/37 thực thể có dữ liệu về tỷ suất mắc.
- Tỷ suất tử vong Việt Nam: 12; trung vị WPR: 5,7 ca/100.000 dân.
- `c_cdr` Việt Nam: 58%; trung vị WPR: 75% (31 thực thể có dữ liệu cho biến này).
- Đây là so sánh mô tả giữa các ước tính cấp quốc gia, không xác định nguyên nhân, hiệu quả chính sách hay chất lượng hệ thống y tế.

## 5. Kết quả khai phá dữ liệu K-means đã xác minh

- Thời điểm: năm 2024; 193 quốc gia/vùng lãnh thổ có đủ cả ba biến.
- Biến đầu vào: `e_inc_100k`, `e_mort_100k`, `c_cdr`; không đưa dân số vào mô hình.
- Thử nghiệm: 3 cách tiền xử lý × K từ 2 đến 8 = 21 cấu hình.
- Cấu hình được chọn: RobustScaler trên ba biến gốc + KMeans K=2, `random_state=42`, `n_init=50`.
- Silhouette = 0,6638; Calinski–Harabasz = 249,63; Davies–Bouldin = 0,6360.
- Kích thước cụm: 167 và 26; ARI trung bình cặp qua 10 lần khởi tạo đơn = 0,9848.
- Kiểm tra độ nhạy khi loại 3 quan sát `c_cdr > 100`: ARI = 1,000 trên 190 thực thể chung, không đổi phân nhóm.
- Trung vị cụm 1 (167 thực thể): tỷ suất mắc 35; tỷ suất tử vong 2,6; `c_cdr` 77%.
- Trung vị cụm 2 (26 thực thể): tỷ suất mắc 379,5; tỷ suất tử vong 64; `c_cdr` 67%.
- Việt Nam thuộc cụm 1. Không diễn giải điều này là Việt Nam có gánh nặng thấp theo chuẩn y tế; nhãn cụm chỉ tương đối trong mẫu và theo ba biến chọn.
- PCA trên trang dashboard chỉ là phép chiếu 2 chiều để trực quan hóa; mô hình K-means thực tế chạy trên 3 biến đã chuẩn hóa.

## 6. Hướng đề xuất hành động

Nên gắn từng đề xuất với một phát hiện cụ thể:

1. Xem nhóm 26 thực thể thuộc cụm có hồ sơ gánh nặng tương đối cao là điểm bắt đầu để rà soát sâu các chỉ số mắc, tử vong và phát hiện ca bệnh; không dùng cụm làm bảng phân bổ nguồn lực tự động.
2. Khi so sánh quốc gia, trình bày song song số ca tuyệt đối và tỷ suất trên 100.000 dân.
3. Rà soát độ đầy đủ và phương pháp ước tính đối với nơi thiếu `c_cdr` hoặc có giá trị trên 100; không tự ý cắt ngưỡng.
4. Theo dõi chuỗi thời gian, số thực thể có dữ liệu và khoảng bất định, tránh kết luận từ một năm đơn lẻ.
5. Với Việt Nam, xem kết quả so sánh WPR như tín hiệu nghiên cứu tiếp; muốn đề xuất chính sách cụ thể cần dữ liệu chi tiết hơn trong nước.
6. Khi có dữ liệu tỉnh/thành hoặc nhóm dân cư phù hợp, mở rộng phân tích xuống cấp dưới quốc gia.

## 7. Những diễn giải không nên dùng

- Không gọi 130,2 là tỷ suất toàn cầu chính thức của WHO; đó là phép tổng hợp của đồ án.
- Không nói India có tỷ suất mắc cao nhất; Kiribati mới là cao nhất theo tỷ suất trong file năm 2024. India cao nhất theo số ca tuyệt đối.
- Không nói K-means phân loại nguy cơ y tế hoặc tìm ra nguyên nhân bệnh.
- Không nói Silhouette 0,664 chứng minh hai cụm là cấu trúc tự nhiên/duy nhất.
- Không nói `c_cdr > 100` chắc chắn là lỗi dữ liệu; giữ nguyên và giải thích theo Data Dictionary/giới hạn ước tính.
- Không kết luận xu hướng thay đổi do một chính sách hoặc sự kiện nếu không có thiết kế nghiên cứu và nguồn dữ liệu nhân quả bổ sung.

## 8. Tệp và bằng chứng có thể đưa vào phụ lục

- `notebooks/01_TB_data_cleaning_and_EDA.ipynb`
- `notebooks/02_Kmeans_clustering.ipynb`
- `data/TB_data_quality_summary.csv`
- `data/TB_year_coverage.csv`
- `data/TB_kmeans_model_comparison.csv`
- `data/TB_kmeans_seed_stability.csv`
- `data/TB_kmeans_sensitivity.csv`
- `reports/figures/` (biểu đồ EDA và K-means)
- Ảnh chụp giao diện 5 trang dashboard sau khi kiểm tra thực tế trên máy.
