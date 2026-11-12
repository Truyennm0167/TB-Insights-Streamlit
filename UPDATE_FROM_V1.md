# Cập nhật TB Insights từ phiên bản 1.0 lên 1.1

## Cách khuyến nghị: cập nhật source, giữ môi trường Python hiện tại

1. Tắt ứng dụng Streamlit đang chạy bằng `Ctrl + C` trong cửa sổ terminal.
2. Sao lưu thư mục dự án hiện tại, ví dụ đổi tên thành `TB-Insights-Streamlit-backup`.
3. Giải nén gói v1.1 vào một thư mục tạm.
4. Mở thư mục `TB-Insights-Streamlit-v1.1`, chọn toàn bộ nội dung bên trong (không có thư mục `.venv`) và sao chép vào thư mục dự án hiện tại `TB-Insights-Streamlit`.
5. Chọn **Replace the files in the destination** khi Windows hỏi ghi đè file. Thư mục `.venv` hiện tại vẫn được giữ nguyên.
6. Mở terminal tại thư mục dự án cũ và chạy `run_windows.bat`, hoặc chạy `python -m streamlit run streamlit_app.py` trong môi trường ảo đang dùng.

## Cách thay thế: dùng thư mục mới hoàn toàn

1. Giải nén toàn bộ gói v1.1 vào một thư mục mới.
2. Chạy `run_windows.bat`. Script sẽ tạo môi trường ảo mới và cài dependencies nếu cần.

Không nên sao chép thư mục `.venv` từ vị trí cũ sang thư mục mới vì virtual environment trên Windows có thể chứa đường dẫn tuyệt đối.

## Các điểm cần kiểm tra sau cập nhật

- Trang Global Overview: chọn từng khu vực WHO, xác nhận `SEA` hiển thị là South-East Asia Region.
- Trang Country Analysis: chọn một quốc gia không thuộc Top 12 của khu vực; quốc gia đó vẫn xuất hiện và được tô màu riêng.
- Trang Clustering Analysis: thử lọc một khu vực và một nhóm; bảng, biểu đồ radar, scatter và biểu đồ khu vực phải thay đổi cùng nhau.
- Trang Insights: kiểm tra câu mô tả tăng/giảm tại Việt Nam.
- Trang About Data: xem bảng độ đầy đủ dữ liệu và đồ thị coverage theo năm.
