# Cập nhật TB Insights từ phiên bản 1.1 lên 1.2

## Cách khuyến nghị: cập nhật source, giữ môi trường Python hiện tại

1. Tắt ứng dụng Streamlit bằng `Ctrl + C` trong cửa sổ terminal.
2. Sao lưu thư mục dự án v1.1.
3. Giải nén gói v1.2 vào một thư mục tạm.
4. Mở thư mục `TB-Insights-Streamlit-v1.2`, chọn toàn bộ nội dung bên trong (không sao chép `.venv`) và chép vào thư mục dự án hiện tại.
5. Chọn **Replace the files in the destination** khi Windows hỏi ghi đè. Giữ nguyên `.venv` hiện tại.
6. Chạy lại `run_windows.bat`.

## Cách thay thế: dùng thư mục mới hoàn toàn

1. Giải nén gói v1.2 vào thư mục mới.
2. Chạy `run_windows.bat`. Script sẽ tạo môi trường ảo và cài thư viện nếu chưa có.

Không nên sao chép `.venv` từ thư mục cũ sang thư mục mới vì môi trường ảo trên Windows có thể chứa đường dẫn tuyệt đối.

## Những điểm cần kiểm tra sau cập nhật

- Mở trang **Phân nhóm quốc gia**: tên bộ lọc chỉ còn “Gánh nặng thấp hơn” và “Gánh nặng cao hơn”, không bị cắt chữ.
- Kiểm tra biểu đồ phân bố: không còn dòng tiêu đề lặp bên trong vùng biểu đồ; chú giải không có tên trường `cluster_label`.
- Kiểm tra biểu đồ so sánh đặc điểm: không còn radar; các thanh ngang không chồng chữ.
- Kiểm tra biểu đồ khu vực WHO: tên khu vực hiển thị bằng tiếng Việt và không còn chú giải chồng tiêu đề.
- Chọn riêng một nhóm: biểu đồ so sánh vẫn giữ thang tham chiếu của toàn bộ mẫu 193 quốc gia, không tự biến mọi giá trị thành 100%.
- Mở các trang Tổng quan, Phân tích theo quốc gia, Phát hiện và đề xuất, Dữ liệu và phương pháp để kiểm tra thuật ngữ tiếng Việt.
- Chọn một số bộ lọc khác nhau và xác nhận bảng, KPI và biểu đồ cập nhật nhất quán.
