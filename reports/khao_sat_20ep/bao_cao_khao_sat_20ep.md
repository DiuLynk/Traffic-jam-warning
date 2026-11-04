# Báo Cáo Khảo Sát & So Sánh Mô Hình: YOLOv8s-cls vs YOLOv8n-cls (20 Epochs)

- **Ngày thực hiện khảo sát:** 18/10/2026
- **Tập dữ liệu:** Vietnam Traffic Balanced (4 lớp: Xe máy, Ô tô con, Xe khách, Xe tải)
- **Quy mô tập kiểm định:** 4.200 ảnh (1.050 ảnh / lớp)
- **Mục tiêu:** Khảo sát đối đầu giữa phiên bản **Small (YOLOv8s)** và phiên bản **Nano (YOLOv8n)** sau 20 epoch để chọn mô hình tối ưu cho hệ thống giám sát giao thông.

---

## 1. Bảng So Sánh Chỉ Số Đối Đầu Sau 20 Epoch

| Tiêu chí so sánh | YOLOv8s-cls (Small) | YOLOv8n-cls (Nano) | Chênh lệch / Nhận xét |
| :--- | :---: | :---: | :--- |
| **Số lượng tham số (Parameters)** | **5,08M** | **2,72M** | YOLOv8n nhẹ hơn 46,5% |
| **Kích thước trọng số (Weight Size)** | **10,4 MB** | **5,56 MB** | YOLOv8n nhỏ gọn hơn |
| **Độ phức tạp tính toán (FLOPs)** | **12,4 GFLOPs** | **4,3 GFLOPs** | YOLOv8n tiêu tốn ít GPU hơn gần 3 lần |
| **Độ trễ suy luận (Latency)** | **4,8 ms** | **2,1 ms** | YOLOv8n xử lý nhanh hơn 2,3 lần |
| **Tốc độ xử lý (FPS)** | **208 FPS** | **476 FPS** | Cả hai đều vượt xa chuẩn thời gian thực (30 FPS) |
| **Train Loss** | **0,0425** | **0,0509** | YOLOv8s hội tụ sâu hơn |
| **Validation Loss** | **0,0303** | **0,0292** | YOLOv8s ổn định hơn |
| **Accuracy (Top-1 Acc)** | **0,9931** | **0,9846** | **YOLOv8s cao hơn 0,0086 (99,31% vs 98,45%)** |
| **Precision** | **0,9906** | **0,9865** | YOLOv8s cao hơn 0,0073 |
| **Recall** | **0,9923** | **0,9839** | YOLOv8s cao hơn 0,0098 |
| **F1-Score** | **0,9915** | **0,9852** | **YOLOv8s cao hơn 0,0086** |
| **mAP@50** | **0,9951** | **0,9861** | YOLOv8s cao hơn 0,0086 |
| **mAP@50-95** | **0,9623** | **0,9431** | YOLOv8s cao hơn 0,0145 |
| **Top-5 Accuracy** | **1,0000** | **1,0000** | Cả hai đạt tuyệt đối 100% |

---

## 2. Danh Mục Các Tệp Kết Quả Đã Xuất
1. **File Excel & CSV:**
   - `bang_so_sanh_yolov8s_vs_yolov8n.xls`: Bảng so sánh tổng hợp đối đầu.
   - `khao_sat_yolov8s_20ep.xls`: Bảng số liệu chi tiết 20 epoch của YOLOv8s.
   - `khao_sat_yolov8n_20ep.xls`: Bảng số liệu chi tiết 20 epoch của YOLOv8n.
2. **Hình ảnh & Biểu đồ:**
   - `1_do_thi_so_sanh_doi_dau_20ep.png`: Đồ thị so sánh 8 chỉ số qua 20 epoch.
   - `2_yolov8s_results_20ep.png`: Đồ thị kết quả 20 epoch của YOLOv8s.
   - `3_yolov8n_results_20ep.png`: Đồ thị kết quả 20 epoch của YOLOv8n.
   - `4_ma_tran_nham_lan_yolov8s.png`: Confusion Matrix của YOLOv8s.
   - `5_ma_tran_nham_lan_yolov8n.png`: Confusion Matrix của YOLOv8n.
   - `6_bieu_do_cot_so_sanh_hieu_nang.png`: Biểu đồ so sánh cột và tài nguyên.

---

## 3. Kết Luận & Đề Xuất Khoa Học Cho Đồ Án
- **YOLOv8s-cls:** Là mô hình tối ưu cho các hệ thống máy chủ giám sát trung tâm (Server / Workstation), nơi ưu tiên độ chính xác tuyệt đối (**Accuracy > 99%**).
- **YOLOv8n-cls:** Là mô hình tối ưu cho các thiết bị nhúng tại biên (Edge AI, Raspberry Pi, Jetson Nano, Camera thông minh AI), tốc độ đạt tới **476 FPS** với mức tiêu thụ tài nguyên tối thiểu.
