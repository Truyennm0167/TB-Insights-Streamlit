# Nhật ký thay đổi — TB Insights

## Version 1.3 Final — 12/11/2026

### Nâng cấp phương pháp và minh bạch thực nghiệm
- Đưa bảng so sánh 21 cấu hình K-means (3 phương pháp chuẩn hóa × K từ 2 đến 8) vào trang Phân nhóm quốc gia.
- Bổ sung biểu đồ Silhouette theo K, đánh dấu cấu hình được chọn.
- Bổ sung Calinski–Harabasz, Davies–Bouldin và kích thước cụm để người xem hiểu cơ sở lựa chọn.
- Ghi rõ Silhouette 0,664 là chỉ số của mô hình đầy đủ trên 193 quốc gia/vùng lãnh thổ, không thay đổi theo bộ lọc trang.
- Bổ sung biểu đồ tỷ trọng 100% theo khu vực WHO bên cạnh biểu đồ số lượng tuyệt đối.
- Bổ sung số quốc gia/vùng lãnh thổ có dữ liệu vào tooltip của biểu đồ xu hướng tổng hợp.
- Bổ sung phân tích mô tả Việt Nam so với trung vị Khu vực Tây Thái Bình Dương năm 2024.

### Tính tái lập và kiểm soát chất lượng
- Bổ sung `src/run_eda.py`: tái tạo bảng dữ liệu ứng dụng, bảng chất lượng, độ bao phủ theo năm và biểu đồ EDA từ dữ liệu WHO gốc.
- Bổ sung `src/run_kmeans.py`: tái tạo tập complete-case, 21 cấu hình thử nghiệm, mô hình cuối, bảng hồ sơ cụm, độ ổn định theo 10 lần khởi tạo và kiểm tra độ nhạy.
- Sửa hai notebook để chạy lại được từ thư mục dự án; loại bỏ tham chiếu tới script/file trung gian không được đóng gói.
- Bổ sung `requirements-research.txt` tách thư viện nghiên cứu khỏi thư viện cần cho ứng dụng Streamlit.
- Tăng kiểm tra toàn vẹn: so sánh các biến trong file cụm với dữ liệu nguồn năm 2024 theo ISO3.

### Kết quả kiểm thử
- 20/20 unit tests PASS.
- 21 cấu hình K-means được tái tạo; mô hình được chọn vẫn là RobustScaler + K=2.
- KPI 2024 giữ nguyên: 10.553.581 ca mắc mới ước tính; 1.198.800 ca tử vong ước tính; tỷ suất tổng hợp tương ứng 130,2 và 14,8 trên 100.000 dân.
- Biểu đồ tỷ trọng nhóm theo khu vực được kiểm tra tổng bằng 100% trong từng khu vực.
- Bổ sung kiểm thử hai phát hiện xếp hạng: Kiribati đứng đầu theo tỷ suất mắc; Ấn Độ đứng đầu theo số ca mắc tuyệt đối.
- Bổ sung kiểm thử đối chiếu các chỉ số Việt Nam với trung vị Khu vực Tây Thái Bình Dương.
- KPI Silhouette trên trang phân nhóm và trang phương pháp được lấy động từ cấu hình mô hình đã chọn, không hard-code.
- Python compile PASS; hai notebook được thực thi bằng Jupyter kernel, không có cell lỗi; hai pipeline được chạy lại từ dữ liệu WHO gốc.
- Chưa thể chạy browser smoke test Streamlit trong môi trường đóng gói vì Streamlit không được cài và môi trường không truy cập PyPI. Người dùng cần kiểm tra lần cuối trên máy đã chạy được ứng dụng.

## Version 1.2 — 12/11/2026
- Việt hóa giao diện và thuật ngữ; sửa lỗi hiển thị trang K-means.
- Thay radar chart bằng biểu đồ thanh ngang so sánh hồ sơ cụm.
