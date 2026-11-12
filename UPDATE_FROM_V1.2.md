# Cập nhật TB Insights từ v1.2 lên v1.3 Final

1. Tắt ứng dụng Streamlit bằng `Ctrl + C`.
2. Sao lưu thư mục dự án hiện tại.
3. Giải nén gói `TB-Insights-CT312-Final-v1.3.zip`.
4. Dùng thư mục mới làm thư mục dự án chính. Nếu muốn giữ môi trường ảo cũ, sao chép thư mục `.venv` từ dự án trước sang thư mục mới; không chép đè source v1.3 bằng source v1.2.
5. Chạy `run_windows.bat` để khởi động dashboard.
6. Kiểm tra lần lượt 5 trang, đặc biệt trang Phân nhóm quốc gia và expander kiểm chứng 21 cấu hình K-means.

## Nếu muốn tái tạo toàn bộ dữ liệu và thực nghiệm
- Cài Python 3.11.
- Chạy `run_research_windows.bat`, hoặc cài `requirements-research.txt` rồi chạy:
  - `python src/run_eda.py`
  - `python src/run_kmeans.py`
  - `python scripts/validate_data.py`
  - `python -m unittest discover -s tests -v`

Lưu ý: chạy lại EDA/K-means sẽ tạo lại các file dữ liệu và hình trong `data/` và `reports/`. File nguồn tại `data/raw/` không bị thay đổi.
