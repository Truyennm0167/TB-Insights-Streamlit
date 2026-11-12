# Trạng thái bàn giao — TB Insights CT312 v1.3 Final

## Kết luận kiểm toán
Đối chiếu với đề cương CT312, sản phẩm hiện có đáp ứng được ba đầu việc riêng của đề tài số 1: tìm thông tin hữu ích từ dữ liệu WHO, xây dựng dashboard và đề xuất hành động. Dashboard được triển khai bằng Streamlit + Plotly; đây là một lựa chọn dashboard thay thế được, vì đề cương nêu Tableau/Looker Studio bằng cụm “có thể sử dụng ...”.

Đây là đánh giá về sản phẩm kỹ thuật. Đồ án chỉ hoàn tất nộp bài sau khi người học viết báo cáo Word/PDF, chuẩn bị thuyết trình, quản lý mã nguồn bằng GitHub và triển khai ứng dụng trên cloud miễn phí theo ghi chú chung của đề cương.

## Các phần đã hoàn thành
- Dashboard Streamlit gồm 5 trang: Tổng quan toàn cầu; Phân tích theo quốc gia; Phân nhóm quốc gia; Phát hiện và khuyến nghị; Dữ liệu và phương pháp.
- KPI và công thức tỷ suất tổng hợp được giải thích rõ; không gọi đây là số liệu tổng hợp chính thức của WHO.
- EDA: xu hướng 2000–2024, so sánh quốc gia, so sánh khu vực, phân biệt số ca tuyệt đối với tỷ suất trên 100.000 dân, kiểm tra chất lượng và độ bao phủ dữ liệu.
- K-means năm 2024 trên 193 quốc gia/vùng lãnh thổ có đủ ba biến.
- So sánh 21 cấu hình K-means (3 cách chuẩn hóa × K=2..8), đánh giá Silhouette, Calinski–Harabasz, Davies–Bouldin; kiểm tra ổn định 10 lần khởi tạo; kiểm tra độ nhạy với ba trường hợp c_cdr > 100.
- Dashboard có bộ lọc, bản đồ, xu hướng, hồ sơ nhóm, bảng quốc gia và tải CSV theo bộ lọc.
- Đề xuất hành động được trình bày kèm giới hạn diễn giải.

## Kết quả thực nghiệm đã xác minh
### Dữ liệu
- Dữ liệu gốc: 5.347 dòng, 50 cột.
- Hai cột hoàn toàn trống được bỏ khỏi bản làm sạch; bản sạch còn 48 cột.
- Bảng phục vụ dashboard: 5.347 dòng, 25 cột; 217 mã ISO3 trong toàn chuỗi 2000–2024.
- Năm 2024: 215 thực thể; 214 thực thể có ước tính mắc/tử vong; 193 thực thể có đủ ba biến cho K-means.
- Không tự động điền dữ liệu thiếu bằng 0; giữ nguyên 8 quan sát c_cdr > 100 trong toàn chuỗi và 3 quan sát trong mẫu K-means 2024.

### KPI 2024 (phép tổng hợp của đồ án)
- Tổng số ca mắc mới ước tính: 10.553.581.
- Tỷ suất mắc mới tổng hợp: 130,2 ca/100.000 dân.
- Tổng số ca tử vong ước tính: 1.198.800.
- Tỷ suất tử vong tổng hợp: 14,8 ca/100.000 dân.
- Các tỷ suất trên được tính bằng tổng số ca ước tính chia tổng dân số của các thực thể có dữ liệu tương ứng, nhân 100.000. Đây không phải chỉ số tổng hợp chính thức do WHO công bố.

### EDA nổi bật
- Tỷ suất mắc mới ước tính tại Việt Nam: 296 năm 2000; 182 năm 2024.
- Tỷ suất tử vong ước tính tại Việt Nam: 47 năm 2000; 12 năm 2024.
- Năm 2024, Kiribati đứng đầu theo tỷ suất mắc mới (945/100.000 dân); Ấn Độ đứng đầu theo số ca mắc mới ước tính (2,71 triệu ca). Không được nhầm hai thứ hạng này.
- Việt Nam trong Khu vực Tây Thái Bình Dương: tỷ suất mắc mới 182 so với trung vị khu vực 55; tỷ suất tử vong 12 so với trung vị 5,7; c_cdr 58% so với trung vị 75%. Đây là so sánh mô tả từ mẫu dữ liệu, không chỉ ra nguyên nhân.

### K-means
- Mẫu: 193 quốc gia/vùng lãnh thổ.
- Biến: e_inc_100k, e_mort_100k, c_cdr.
- Phương pháp: RobustScaler + KMeans(K=2, random_state=42, n_init=50).
- Silhouette: 0,6638; Calinski–Harabasz: 249,63; Davies–Bouldin: 0,6360.
- Kích thước cụm: 167 và 26.
- ARI trung bình cặp giữa 10 lần khởi tạo đơn: 0,9848.
- Loại 3 trường hợp c_cdr >100 để kiểm tra độ nhạy: ARI trên 190 quốc gia chung = 1,000; không đổi phân nhóm.
- Việt Nam thuộc cụm có hồ sơ gánh nặng tương đối thấp hơn trong mẫu; điều này không có nghĩa Việt Nam có gánh nặng thấp theo chuẩn y tế.

## Khả năng tái lập
- `src/run_eda.py`: tạo dữ liệu sạch, bảng kiểm tra chất lượng, độ bao phủ, dữ liệu ứng viên và biểu đồ EDA.
- `src/run_kmeans.py`: tái tạo benchmark 21 cấu hình, mô hình cuối, bảng thành viên, hồ sơ cụm, độ ổn định, độ nhạy và các hình minh họa.
- `notebooks/01_TB_data_cleaning_and_EDA.ipynb` và `notebooks/02_Kmeans_clustering.ipynb` đã được sửa để gọi các script này từ thư mục dự án.
- Chạy `python scripts/validate_data.py` và `python -m unittest discover -s tests -v` để kiểm tra.

## Kiểm thử trong môi trường đóng gói
- Python compilation: PASS.
- Unit tests: 20/20 PASS.
- Kiểm tra KPI và đối chiếu file cluster với dữ liệu nguồn 2024: PASS.
- Kiểm tra biểu đồ lựa chọn mô hình, tỷ trọng theo khu vực và coverage hover: PASS.
- Streamlit browser smoke test: chưa chạy được trong môi trường này do Streamlit không được cài và không truy cập PyPI. Người dùng đã xác nhận chạy thành công phiên bản trước trên máy; cần kiểm tra giao diện v1.3 sau khi cập nhật.

## Những việc còn lại trước khi nộp
1. Người học kiểm thử 5 trang v1.3 trên máy Windows.
2. Đẩy source lên GitHub.
3. Triển khai trên Streamlit Community Cloud hoặc cloud miễn phí tương đương, kiểm tra link công khai.
4. Viết báo cáo Word và xuất PDF theo cấu trúc giảng viên yêu cầu.
5. Chuẩn bị slide và demo.
6. Đóng gói code + báo cáo Word + PDF thành một file ZIP theo quy ước nhóm.
