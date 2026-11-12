# Đánh giá cuối cùng theo vai trò giảng viên — Đồ án CT312, đề tài 1

## 1. Căn cứ đánh giá

Đề cương môn học nêu riêng cho đề tài 1 ba yêu cầu: (1) tìm thông tin hữu ích từ dữ liệu bệnh lao WHO; (2) xây dựng dashboard; (3) đề xuất các hành động. Ghi chú chung yêu cầu báo cáo có giới thiệu vấn đề, dữ liệu, cơ sở lý thuyết, thiết kế/cài đặt (tiền xử lý, phân tích trực quan, mô hình và đánh giá mô hình), kết quả và hướng phát triển. Rubric: hoàn thành yêu cầu chính 50%, báo cáo 20%, trình bày 20%, chương trình dễ hiểu 10%. Sản phẩm nộp gồm code và báo cáo Word/PDF, dùng GitHub và triển khai cloud miễn phí.

## 2. Nhận xét như người chấm

### Điểm mạnh
- Đề tài bám sát cả ba yêu cầu riêng của đề tài 1.
- Có quy trình dữ liệu từ nguồn WHO đến dữ liệu sạch, EDA, K-means và dashboard.
- Phân biệt số ca mắc tuyệt đối và tỷ suất trên 100.000 dân; đây là phân biệt cần thiết khi xếp hạng quốc gia.
- K-means có so sánh cấu hình, nhiều chỉ số đánh giá, kiểm tra độ ổn định và độ nhạy; tốt hơn việc chỉ chạy một mô hình rồi báo silhouette.
- Dashboard có năm trang; có thể dùng làm sản phẩm demo và công cụ khám phá kết quả.
- Source code được chia module và có script tái lập dữ liệu/thực nghiệm.

### Điểm cần thận trọng khi bảo vệ
- Các biến `e_*` là ước tính của WHO, không phải toàn bộ ca quan sát trực tiếp.
- Tỷ suất tổng hợp trên dashboard là phép tính của đồ án từ các dòng quốc gia/vùng lãnh thổ có dữ liệu, không phải một chỉ số tổng hợp chính thức do WHO công bố.
- Số lượng thực thể có dữ liệu thay đổi theo năm; xu hướng tổng hợp có thể chịu ảnh hưởng của độ bao phủ.
- K-means phụ thuộc vào ba biến, chuẩn hóa và mẫu complete-case năm 2024; 2 cụm không phải cách phân loại y tế duy nhất.
- Nhãn “gánh nặng cao hơn/thấp hơn” chỉ mô tả tương đối trong mẫu; không dùng để chẩn đoán, phân bổ nguồn lực tự động hoặc kết luận nhân quả.
- Giá trị `c_cdr` >100 được giữ nguyên theo file; phải giải thích cách diễn giải và kiểm tra độ nhạy, không tự ý cắt về 100.

## 3. Đánh giá theo rubric kỹ thuật

| Hạng mục | Nhận xét | Mức đánh giá tham khảo |
|---|---|---:|
| Tìm thông tin hữu ích | Có EDA, xu hướng, top theo tỷ suất và số ca, khu vực WHO, so sánh Việt Nam, phân nhóm | 21–23/25 phần phân tích |
| Dashboard | 5 trang, KPI, biểu đồ, bộ lọc, bảng và tải CSV | 17–19/20 phần dashboard |
| Đề xuất hành động | Có 6 hướng đề xuất, gắn với phát hiện; cần trình bày ngắn gọn trong báo cáo và bảo vệ | 4–4/5 phần đề xuất |
| Code dễ hiểu | Module hóa, script tái lập, notebook, kiểm thử | 8–9/10 |

Ước lượng tổng thể cho phần sản phẩm kỹ thuật có thể ở mức tốt nếu người học kiểm tra giao diện thực tế và triển khai cloud thành công. Đây không phải điểm do giảng viên xác nhận và không thay thế kết quả chấm chính thức.

## 4. Những điều kiện chưa thể xem là hoàn tất đồ án nộp bài

- Chưa có quyển báo cáo Word/PDF hoàn chỉnh.
- Chưa có slide và phần thuyết trình được đánh giá.
- Chưa có repository GitHub và đường dẫn cloud công khai được xác minh.
- Môi trường đóng gói không có Streamlit nên chưa thực hiện browser smoke test v1.3; cần người học kiểm tra 5 trang trên máy.

## 5. Kết quả kiểm toán cuối sau nâng cấp v1.3
- Đã chạy lại `src/run_eda.py` từ CSV WHO gốc: 5.347 dòng, 50 cột đầu vào; loại hai cột hoàn toàn trống; 5.347 dòng và 48 cột ở bản sạch; không có khóa ISO3–năm trùng.
- Đã chạy lại `src/run_kmeans.py`: 193 quốc gia, 21 cấu hình, cấu hình chọn vẫn là RobustScaler + K=2; kết quả chỉ số không thay đổi.
- Hai notebook EDA và K-means đã được thực thi bằng Jupyter kernel, không có cell lỗi.
- Bộ kiểm thử cuối: 20/20 PASS; `scripts/validate_data.py` PASS; Python compilation PASS.
- Bổ sung kiểm thử cho hai thứ hạng quốc gia năm 2024 và so sánh Việt Nam với trung vị Khu vực Tây Thái Bình Dương.
- Các KPI mô hình Silhouette được lấy trực tiếp từ bảng benchmark đã chọn thay vì ghi cứng trong trang giao diện.
- Chưa thể xác nhận giao diện cuối trong browser của người dùng hoặc deployment cloud từ môi trường này; cần người học tự smoke-test sau khi cập nhật.

## 6. Kết luận của người đánh giá

Về phạm vi đề tài 1, sản phẩm kỹ thuật hiện tại đã đáp ứng yêu cầu và có phần mở rộng K-means để thể hiện rõ nội dung khai phá dữ liệu. Không cần bổ sung thêm thuật toán hoặc tăng số trang dashboard chỉ để làm sản phẩm phức tạp hơn. Ưu tiên từ đây là bảo đảm tính tái lập, kiểm thử thực tế, ghi lại bằng chứng kết quả, viết báo cáo đúng cấu trúc và chuẩn bị thuyết trình.
