# Báo cáo khai phá dữ liệu bằng K-means — WHO TB 2024

## 1. Mục tiêu

Phân nhóm các quốc gia/vùng lãnh thổ theo hồ sơ gánh nặng bệnh lao, sử dụng ba chỉ số: tỷ lệ mắc ước tính (`e_inc_100k`), tỷ lệ tử vong ước tính (`e_mort_100k`) và tỷ lệ phát hiện ca bệnh/độ bao phủ điều trị (`c_cdr`). Định nghĩa biến được lấy từ Data Dictionary do người dùng cung cấp.

## 2. Phạm vi dữ liệu

- Năm phân tích: 2024.
- Số quốc gia/vùng lãnh thổ có đủ cả ba biến: **193**.
- Ba biến đầu vào: `e_inc_100k, e_mort_100k, c_cdr`.
- Không đưa dân số (`e_pop_num`) vào K-means vì mục tiêu là phân nhóm theo hồ sơ chỉ số, không phải theo quy mô dân số. Không đưa đồng thời số ca và tỷ lệ trên 100.000 dân để tránh trộn quy mô tuyệt đối với cường độ tương đối.
- Các bản ghi thiếu ít nhất một biến không được tự điền; chúng không thuộc tập complete-case dùng cho K-means.

## 3. Tiền xử lý và lựa chọn mô hình

Đã so sánh ba cấu hình: (1) StandardScaler trên biến gốc; (2) log1p cho hai tỷ lệ mắc/tử vong rồi StandardScaler; (3) RobustScaler trên biến gốc. Với mỗi cấu hình, thử `k=2..8`, `random_state=42`, `n_init=50`. Đồng thời đánh giá độ nhạy với khởi tạo bằng 10 lần chạy `n_init=1` cho `k=2..6`, so sánh nhãn qua Adjusted Rand Index (ARI).

Cấu hình được chọn: **RobustScaler trên ba biến gốc, K-means với k=2, random_state=42, n_init=50**. Cơ sở lựa chọn: trong các tổ hợp đã thử, cấu hình này cho Silhouette cao nhất tại k=2 (**0.664**), Calinski–Harabasz **249.6**, Davies–Bouldin **0.636**, và ARI trung bình từng cặp giữa 10 seed là **0.985**. Kết quả k=3 trở lên có Silhouette thấp hơn trong cấu hình này; do đó k=2 được chọn cho phiên bản chính.

RobustScaler biến đổi từng đặc trưng dựa trên trung vị và khoảng tứ phân vị (IQR), giúp giảm tác động của độ lệch phân phối khi chuẩn hóa. K-means vẫn dựa trên khoảng cách Euclidean và không hoàn toàn miễn nhiễm với ngoại lệ; kết quả cần được hiểu trong phạm vi các biến đã chọn.

## 4. Kết quả phân nhóm

| Nhóm mô tả | Số quốc gia/vùng lãnh thổ | Trung vị tỷ lệ mắc | Trung vị tỷ lệ tử vong | Trung vị c_cdr |
|---|---:|---:|---:|---:|
| Hồ sơ gánh nặng tương đối thấp hơn | 167 | 35.0 | 2.60 | 77.0% |
| Hồ sơ gánh nặng tương đối cao hơn | 26 | 379.5 | 64.00 | 67.0% |

Đơn vị: tỷ lệ mắc và tử vong trên 100.000 dân; `c_cdr` theo phần trăm. Nhãn “thấp hơn/cao hơn” là mô tả tương đối giữa hai cụm trong mẫu, không phải phân loại nguy cơ y tế hoặc đánh giá hiệu quả hệ thống y tế.

Việt Nam (`VNM`) được gán vào **Nhóm có hồ sơ gánh nặng tương đối thấp hơn**. Điều này không có nghĩa Việt Nam có gánh nặng thấp theo chuẩn y tế; nó chỉ phản ánh vị trí tương đối của Việt Nam so với 193 quốc gia/vùng lãnh thổ và ba biến đầu vào trong mô hình. Các chỉ số riêng của Việt Nam vẫn cần được trình bày trực tiếp trên dashboard.

## 5. Kiểm tra độ nhạy

Trong tập 193 quốc gia/vùng lãnh thổ có 3 giá trị `c_cdr` lớn hơn 100 (Belgium, Bulgaria, Croatia). Chúng được giữ nguyên trong mô hình chính vì đây là giá trị được cung cấp trong nguồn, không tự ý cắt ngưỡng. Khi chạy lại mô hình sau khi loại riêng 3 trường hợp này để kiểm tra độ nhạy, số quan sát còn **190**, Silhouette là **0.667**, ARI so với nhãn mô hình chính trên cùng các quốc gia là **1.000**, số quốc gia đổi nhóm sau khi chuẩn hóa cách đặt tên cụm là **0**.

Đây là kiểm tra độ nhạy, không phải đề xuất loại các quốc gia đó khỏi dữ liệu chính.

## 6. Diễn giải và giới hạn

1. Mô hình chỉ sử dụng ba biến ở cấp quốc gia trong năm 2024; không mô tả khác biệt bên trong từng quốc gia.
2. `c_cdr` được Data Dictionary định nghĩa là case detection rate (also known as TB treatment coverage), percent. Giá trị lớn hơn 100 được giữ lại và cần diễn giải thận trọng.
3. K-means tạo nhóm theo khoảng cách và các biến đã chọn; mô hình không xác định nguyên nhân, không chứng minh quan hệ nhân quả và không phải công cụ chẩn đoán.
4. Các nước/vùng lãnh thổ thiếu ít nhất một trong ba biến không được phân nhóm trong kết quả này.
5. Cần kiểm tra thêm độ nhạy với lựa chọn biến, năm phân tích và cách chuẩn hóa nếu có thời gian.

## 7. Khuyến nghị sử dụng trong dashboard

- Dùng màu/nhãn để phân biệt hai cụm, kèm bảng trung vị và số lượng quốc gia.
- Cho phép lọc theo khu vực WHO và tìm Việt Nam.
- Hiển thị rõ đơn vị của từng chỉ số.
- Ghi chú rằng phân nhóm mang tính khám phá và không phải bảng xếp hạng quốc gia.

## 8. Tệp kết quả

- `data/processed/tb_country_clusters_2024.csv`: dữ liệu gốc ứng viên kèm cluster id, tên nhóm và giá trị đã scale.
- `data/processed/tb_dashboard_cluster_2024.csv`: bảng gọn để nạp vào Tableau.
- `reports/kmeans_model_comparison.csv`: so sánh cấu hình tiền xử lý và k.
- `reports/kmeans_seed_stability.csv`: độ ổn định theo 10 seed.
- `reports/kmeans_cluster_profiles_2024.csv`: hồ sơ các cụm.
- `reports/kmeans_country_membership_2024.csv`: danh sách thành viên cụm.
- `reports/kmeans_cdr_gt100_sensitivity.csv`: kiểm tra độ nhạy `c_cdr > 100`.
- `charts/09` đến `charts/13`: biểu đồ mô hình và hồ sơ cụm.
