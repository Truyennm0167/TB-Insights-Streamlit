# TB Insights — Dashboard phân tích dữ liệu bệnh lao WHO

**Phiên bản 1.3 Final · 12/11/2026**

Ứng dụng dashboard đa trang phục vụ đồ án môn Khai khoáng dữ liệu CT312. Ứng dụng sử dụng Streamlit + Plotly; dữ liệu được xử lý bằng pandas và kết quả phân nhóm được tái tạo bằng scikit-learn.

## 1. Các trang trong ứng dụng

1. **Tổng quan toàn cầu:** KPI theo năm/khu vực, xu hướng mắc mới và tử vong, xếp hạng theo tỷ suất và số ca tuyệt đối, bản đồ và so sánh khu vực WHO.
2. **Phân tích theo quốc gia:** diễn biến qua các năm của một quốc gia, khoảng ước tính WHO nếu có và so sánh với khu vực WHO.
3. **Phân nhóm quốc gia:** kết quả K-means năm 2024, phân bố quốc gia, so sánh đặc điểm nhóm, phân bố theo khu vực và bảng lựa chọn cấu hình mô hình.
4. **Phát hiện và khuyến nghị:** các phát hiện mô tả từ dữ liệu cùng hướng hành động có căn cứ.
5. **Dữ liệu và phương pháp:** nguồn dữ liệu, chất lượng, quy trình xử lý, cấu hình khai phá dữ liệu và giới hạn diễn giải.

## 2. Cấu trúc dự án

```text
TB-Insights-CT312-Final-v1.3/
├── streamlit_app.py
├── requirements.txt                 # Chỉ thư viện cần để chạy dashboard
├── requirements-research.txt        # Thêm scikit-learn, matplotlib, notebook
├── run_windows.bat
├── run_research_windows.bat
├── data/
│   ├── raw/                          # CSV WHO gốc
│   ├── TB_data_dictionary.csv
│   ├── TB_country_year.csv
│   ├── TB_clusters_2024.csv
│   └── TB_kmeans_*.csv / *.json      # Benchmark và đầu ra thực nghiệm
├── src/
│   ├── run_eda.py                    # Tạo lại dữ liệu sạch và EDA
│   └── run_kmeans.py                 # Tái tạo 21 cấu hình và mô hình cuối
├── tb_insights/                      # Logic dữ liệu, biểu đồ, giao diện và 5 trang
├── notebooks/                        # Notebook EDA và K-means đã chạy kiểm tra
├── reports/                          # Báo cáo EDA/K-means và hình phục vụ báo cáo
├── scripts/validate_data.py
├── tests/
└── tài liệu kiểm toán, cập nhật và checklist
```

## 3. Chạy dashboard trên Windows 11

Khuyến nghị Python 3.11. Cách nhanh nhất là nhấp đúp `run_windows.bat`; script tạo môi trường ảo nếu chưa có và cài các thư viện cần cho ứng dụng.

Hoặc mở PowerShell tại thư mục dự án:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Ứng dụng thường mở tại `http://localhost:8501`.

Nếu PowerShell chặn kích hoạt môi trường ảo, chạy lệnh sau trong cửa sổ hiện tại rồi kích hoạt lại:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## 4. Tái tạo toàn bộ quy trình nghiên cứu

Cài Python 3.11, mở PowerShell tại thư mục dự án và cài thêm nhóm thư viện nghiên cứu:

```powershell
pip install -r requirements-research.txt
python src/run_eda.py
python src/run_kmeans.py
python scripts/validate_data.py
python -m unittest discover -s tests -v
```

Hoặc chạy `run_research_windows.bat`. Hai notebook trong `notebooks/` được thiết kế để mở từ thư mục gốc hoặc thư mục `notebooks`; các notebook gọi script tương ứng, sau đó trình bày bảng, biểu đồ và kết quả. File WHO gốc trong `data/raw/` không bị thay đổi.

## 5. Kết quả đã kiểm tra

### Dữ liệu
- File WHO gốc: 5.347 dòng, 50 cột.
- Loại hai cột hoàn toàn trống khỏi bản làm sạch; bản sạch còn 48 cột.
- Bảng ứng dụng: 5.347 dòng, 25 cột; 217 mã ISO3 trong giai đoạn 2000–2024.
- Không có khóa ISO3–năm trùng lặp.
- Năm 2024: 214 thực thể có đủ số ca mắc ước tính và dân số; 193 thực thể có đủ ba biến K-means và dân số.

### KPI năm 2024
- Tổng số ca mắc mới ước tính trong các dòng có dữ liệu: 10.553.581.
- Tỷ suất mắc mới tổng hợp do đồ án tính: 130,2 ca/100.000 dân.
- Tổng số ca tử vong ước tính trong các dòng có dữ liệu: 1.198.800.
- Tỷ suất tử vong tổng hợp do đồ án tính: 14,8 ca/100.000 dân.

Các tỷ suất tổng hợp được tính bằng tổng số ca ước tính chia cho tổng dân số của các thực thể có số liệu tương ứng, rồi nhân 100.000. Đây là phép tổng hợp của đồ án, **không phải chỉ số toàn cầu chính thức do WHO công bố**. Số liệu mắc/tử vong đầu vào là ước tính WHO, không phải số đếm quan sát trực tiếp của mọi ca bệnh thực tế.

### Phát hiện EDA nổi bật
- Tại Việt Nam, tỷ suất mắc mới ước tính là 296/100.000 dân năm 2000 và 182/100.000 dân năm 2024; tỷ suất tử vong tương ứng là 47 và 12/100.000 dân.
- Năm 2024, **Kiribati** có tỷ suất mắc mới ước tính cao nhất trong file (945/100.000 dân), trong khi **Ấn Độ** có số ca mắc mới ước tính tuyệt đối lớn nhất (2,71 triệu). Hai thứ hạng dùng hai thước đo khác nhau.
- Tại Khu vực Tây Thái Bình Dương năm 2024, Việt Nam có tỷ suất mắc mới 182 so với trung vị khu vực 55; tỷ suất tử vong 12 so với 5,7; tỷ lệ phát hiện ca bệnh 58% so với trung vị 75%. Đây là so sánh mô tả, không xác định nguyên nhân.

### K-means
- Mẫu: 193 quốc gia/vùng lãnh thổ có đủ ba biến trong năm 2024.
- Biến: tỷ suất mắc mới (`e_inc_100k`), tỷ suất tử vong (`e_mort_100k`), tỷ lệ phát hiện ca bệnh (`c_cdr`).
- So sánh 21 cấu hình: 3 cách tiền xử lý × K từ 2 đến 8.
- Cấu hình được chọn: RobustScaler trên ba biến gốc + KMeans K=2, `random_state=42`, `n_init=50`.
- Silhouette 0,6638; Calinski–Harabasz 249,63; Davies–Bouldin 0,6360.
- Kích thước cụm: 167 và 26; ARI trung bình cặp giữa 10 lần khởi tạo độc lập 0,9848.
- Kiểm tra độ nhạy khi loại 3 trường hợp `c_cdr > 100`: ARI = 1,000 trên 190 quốc gia chung, không thay đổi phân nhóm.
- Nhãn cụm chỉ mô tả tương đối trong mẫu và theo ba biến đã chọn; không phải phân loại nguy cơ y tế, bảng xếp hạng hay kết luận nhân quả. Việt Nam thuộc nhóm có hồ sơ tương đối thấp hơn trong mẫu, nhưng không có nghĩa gánh nặng bệnh lao tại Việt Nam là thấp theo một chuẩn y tế.

## 6. Kiểm thử

```powershell
python scripts/validate_data.py
python -m unittest discover -s tests -v
```

Bộ kiểm thử hiện có 18 kiểm tra về dữ liệu, KPI, cấu hình K-means, biểu đồ, bộ lọc và đối chiếu nhãn cụm với dữ liệu nguồn. Hai notebook đã được thực thi bằng Jupyter kernel trong môi trường kiểm tra và không có cell lỗi.

**Giới hạn kiểm thử giao diện:** môi trường đóng gói không có Streamlit và không kết nối được PyPI, vì vậy chưa thể thực hiện browser smoke test phiên bản cuối tại đây. Cần mở ứng dụng trên máy của người thực hiện, kiểm tra cả 5 trang, các bộ lọc và các nút tải CSV trước khi deploy.

## 7. Triển khai Streamlit Community Cloud

1. Tạo repository GitHub và đưa toàn bộ dự án lên (bao gồm `requirements.txt`, `data/` và `.streamlit/config.toml`).
2. Truy cập <https://share.streamlit.io/> và đăng nhập bằng GitHub.
3. Chọn **Create app**, chọn repository, branch và entrypoint `streamlit_app.py`.
4. Nhấn Deploy, kiểm tra ứng dụng bằng đường dẫn công khai.

Community Cloud chỉ cần `requirements.txt` để cài thư viện chạy dashboard; không cần cài Jupyter/scikit-learn/matplotlib cho runtime của ứng dụng vì kết quả K-means đã được chuẩn bị trước. Nếu chạy lại thực nghiệm, cài thêm `requirements-research.txt`.

## 8. Nguồn và giới hạn

- WHO Global Tuberculosis Programme – Data: <https://www.who.int/teams/global-tuberculosis-programme/data>
- WHO Tuberculosis Dashboard: <https://data.who.int/dashboards/tuberculosis>
- Streamlit Community Cloud: <https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy>
- Streamlit multipage apps: <https://docs.streamlit.io/develop/concepts/multipage-apps/overview>

Dữ liệu có thể thiếu theo quốc gia/năm; độ bao phủ có thể thay đổi theo thời gian. Các ước tính WHO có khoảng bất định. K-means là phương pháp không giám sát và kết quả phụ thuộc vào biến, mẫu và tiền xử lý. Dashboard chỉ phục vụ học thuật/khám phá dữ liệu, không dùng để chẩn đoán hay quyết định điều trị cá nhân.

## 9. Tài liệu kiểm toán và chuẩn bị báo cáo

- `FINAL_TEACHER_REVIEW.md`: nhận xét theo góc nhìn người chấm, đối chiếu rubric và các giới hạn cần bảo vệ.
- `REPORT_WRITING_BRIEF.md`: cấu trúc báo cáo, số liệu đã xác minh, kết quả EDA/K-means và những diễn giải cần tránh.
- `FINAL_SUBMISSION_CHECKLIST.md`: checklist trước khi nộp.
- `FINAL_AUDIT_TEST_RESULTS.txt`: kết quả chạy lại pipeline, notebook, validator và unit tests.
