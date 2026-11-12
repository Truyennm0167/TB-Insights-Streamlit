# Checklist cuối trước khi nộp CT312

## Ứng dụng và dữ liệu
- [ ] Chạy ứng dụng từ thư mục dự án trên máy cá nhân.
- [ ] Mở đủ 5 trang và kiểm tra bộ lọc, đặc biệt trang Phân nhóm quốc gia (scatter, hồ sơ cụm, bảng benchmark, số lượng/tỷ trọng khu vực).
- [ ] Kiểm tra biểu đồ K-means, bảng 21 cấu hình và biểu đồ tỷ trọng theo khu vực.
- [ ] Xác nhận KPI năm 2024 khớp với `scripts/validate_data.py`.
- [ ] Kiểm tra dashboard trên trình duyệt sau khi deploy.

## Nghiên cứu và tính tái lập
- [ ] Chạy `python src/run_eda.py`.
- [ ] Chạy `python src/run_kmeans.py`.
- [ ] Chạy `python scripts/validate_data.py`.
- [ ] Chạy `python -m unittest discover -s tests -v`.
- [ ] Giữ file WHO gốc và Data Dictionary trong gói mã nguồn.
- [ ] Đảm bảo hai notebook chạy từ thư mục dự án theo hướng dẫn; kiểm tra các cell đầu ra không báo lỗi.

## Báo cáo và thuyết trình
- [ ] Trang bìa ghi tên đề tài và người thực hiện.
- [ ] Giới thiệu vấn đề và mục tiêu.
- [ ] Giới thiệu nguồn dữ liệu, đơn vị đo và Data Dictionary.
- [ ] Cơ sở lý thuyết: thống kê mô tả, chuẩn hóa, K-means, Silhouette, Calinski–Harabasz, Davies–Bouldin, ARI.
- [ ] Thiết kế và cài đặt: tiền xử lý, EDA, K-means, đánh giá, dashboard.
- [ ] Kết quả, phát hiện, đề xuất, hạn chế và hướng phát triển.
- [ ] Word và PDF đồng nhất nội dung.
- [ ] Slide và demo live đã được tập dượt.

## Quản lý và nộp bài
- [ ] Đẩy code lên GitHub.
- [ ] Triển khai dashboard trên cloud miễn phí và kiểm tra quyền truy cập.
- [ ] Đóng gói code + báo cáo Word + PDF thành một ZIP theo tên nhóm mà giảng viên yêu cầu.

## Tài liệu hỗ trợ viết báo cáo
- Dùng `REPORT_WRITING_BRIEF.md` để đối chiếu số liệu đã xác minh, cách diễn giải và các kết luận không nên viết. Đây là phiếu chuẩn bị, không thay thế báo cáo Word/PDF do sinh viên tự hoàn thiện.
