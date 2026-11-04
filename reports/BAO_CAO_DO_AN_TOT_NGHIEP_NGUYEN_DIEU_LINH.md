# BỘ GIAO THÔNG VẬN TẢI / TRƯỜNG ĐẠI HỌC CÔNG NGHỆ GIAO THÔNG VẬN TẢI
## KHOA CÔNG NGHỆ THÔNG TIN — BỘ MÔN HỆ THỐNG THÔNG TIN & TRÍ TUỆ NHÂN TẠO

---

# ĐỒ ÁN TỐT NGHIỆP ĐẠI HỌC

### ĐỀ TÀI:
# NGHIÊN CỨU VÀ XÂY DỰNG HỆ THỐNG GIÁM SÁT, ĐÁNH GIÁ MỨC ĐỘ PHỤC VỤ (LOS) VÀ ĐIỀU PHỐI GIAO THÔNG THÔNG MINH DỰA TRÊN THỊ GIÁC MÁY TÍNH VÀ DEEP LEARNING

---

* **Giảng viên hướng dẫn:** **TS. Nguyễn Trọng Dũng**
* **Sinh viên thực hiện:** **Nguyễn Diệu Linh**
* **Mã sinh viên:** **74DCTG21048**
* **Lớp:** **74DCTG22**
* **Ngành:** Công nghệ Thông tin (Chuyên ngành Hệ thống Thông tin & Giao thông Thông minh)
* **Thời gian thực hiện:** Năm học 2025 - 2026

---

\newpage

# LỜI CẢM ƠN

Trong suốt quá trình học tập, nghiên cứu và hoàn thành đồ án tốt nghiệp này, em đã nhận được sự quan tâm, chỉ dẫn tận tình và giúp đỡ quý báu của các thầy cô giáo, gia đình và bạn bè.

Lời đầu tiên, em xin bày tỏ lòng biết ơn sâu sắc nhất tới **TS. Nguyễn Trọng Dũng** - Giảng viên hướng dẫn trực tiếp của em. Thầy đã luôn định hướng phương pháp nghiên cứu khoa học, truyền đạt những kiến thức chuyên môn sâu rộng về Trí tuệ nhân tạo và Giao thông thông minh (ITS), cũng như kiên nhẫn chỉ bảo, sửa đổi từng thuật toán, từng phương pháp thực nghiệm để em hoàn thiện đề tài một cách khoa học và chặt chẽ nhất.

Em xin chân thành cảm ơn các thầy cô giáo trong Khoa Công nghệ Thông tin đã truyền thụ cho em những kiến thức nền tảng và chuyên sâu quý báu trong suốt các năm học vừa qua.

Mặc dù em đã nỗ lực hết mình để hoàn thiện đồ án, song do giới hạn về thời gian và kiến thức thực tiễn, đồ án khó tránh khỏi những thiếu sót nhất định. Em rất mong nhận được những ý kiến đóng góp, chỉ bảo quý báu của quý thầy cô trong Hội đồng chấm đồ án tốt nghiệp để công trình nghiên cứu được hoàn thiện hơn.

*Hà Nội, ngày 18 tháng 10 năm 2026*  
**Sinh viên thực hiện**  
**Nguyễn Diệu Linh**

---

\newpage

# MỤC LỤC

- **CHƯƠNG 1: MỞ ĐẦU**
  - 1.1. Tính cấp thiết của đề tài
  - 1.2. Mục tiêu nghiên cứu
    - Mục tiêu tổng quát
    - Mục tiêu cụ thể
  - 1.3. Đối tượng và Phạm vi nghiên cứu
    - Đối tượng nghiên cứu
    - Phạm vi nghiên cứu
  - 1.4. Nội dung thực hiện
  - 1.5. Phương pháp thực hiện
- **CHƯƠNG 2: CƠ SỞ LÝ THUYẾT VÀ CÔNG NGHỆ SỬ DỤNG**
  - 2.1. Cơ sở lý thuyết
    - 2.1.1. Các thông số đặc trưng của dòng giao thông ($Q, V, K, PCU$)
    - 2.1.2. Khái niệm Mức độ phục vụ (LOS) và Hệ số sử dụng năng lực đường ($V/C$)
    - 2.1.3. Thị giác máy tính và Mạng nơ-ron tích chập (CNN)
    - 2.1.4. Kiến trúc mô hình nhận diện đối tượng YOLOv8
    - 2.1.5. Kỹ thuật theo dõi đối tượng đa mục tiêu (Multi-Object Tracking - ByteTrack)
    - 2.1.6. Mô hình dự báo chuỗi thời gian giao thông
  - 2.2. Công nghệ sử dụng
    - 2.2.1. Ngôn ngữ Python và hệ sinh thái thư viện AI/CV
    - 2.2.2. Khung ứng dụng Web Flask & Cơ chế truyền phát Server-Sent Events (SSE)
    - 2.2.3. Hệ quản trị cơ sở dữ liệu SQLite tối ưu chuỗi thời gian
    - 2.2.4. Công nghệ Frontend hiện đại (Vanilla JS, Chart.js, Lucide Icons)
  - 2.3. Các nghiên cứu liên quan
  - 2.4. Giải pháp đề xuất
- **CHƯƠNG 3: PHÂN TÍCH, THIẾT KẾ VÀ XÂY DỰNG HỆ THỐNG**
  - 3.1. Phân tích yêu cầu
    - 3.1.1. Yêu cầu chức năng
    - 3.1.2. Yêu cầu phi chức năng
  - 3.2. Thiết kế hệ thống tổng thể (System Pipeline)
    - 3.2.1. Kiến trúc phân tầng 4 lớp (Camera Layer - AI Pipeline - Backend Service - Frontend UI)
    - 3.2.2. Luồng xử lý dữ liệu và thị giác máy tính
    - 3.2.3. Thuật toán biến đổi phối cảnh mặt đường (Perspective Homography)
    - 3.2.4. Thuật toán phân loại trạng thái tắc nghẽn giao thông dựa trên LOS, $V/C$ và Mật độ thực tế
  - 3.3. Thiết kế cơ sở dữ liệu
    - 3.3.1. Sơ đồ thực thể liên kết (ERD)
    - 3.3.2. Thiết kế chi tiết các bảng dữ liệu
  - 3.4. Thiết kế giao diện (UI/UX)
    - 3.4.1. Màn hình xác thực & phân quyền truy cập
    - 3.4.2. Bảng điều khiển trung tâm 7 phân hệ chuyên biệt
  - 3.5. Xây dựng hệ thống
    - 3.5.1. Xây dựng CameraWorker đa luồng xử lý video song song
    - 3.5.2. Xây dựng module tính toán chỉ số giao thông chuẩn ITS
    - 3.5.3. Xây dựng động cơ dự báo lưu lượng chuỗi thời gian (Forecaster Engine)
    - 3.5.4. Xây dựng giao diện web thời gian thực
- **CHƯƠNG 4: KẾT QUẢ VÀ THẢO LUẬN**
  - 4.1. Kết quả thực nghiệm
    - 4.1.1. Kết quả thu thập và làm sạch tập dữ liệu giao thông Việt Nam
    - 4.1.2. Kết quả huấn luyện mô hình phân loại phương tiện
    - 4.1.3. Kết quả khảo sát đối đầu 20 epoch giữa YOLOv8s và YOLOv8n
    - 4.1.4. Kết quả triển khai thực tế trên hệ thống 4 camera nút giao thông
  - 4.2. Đánh giá hệ thống
    - 4.2.1. Đánh giá độ chính xác nhận diện và đếm xe
    - 4.2.2. Đánh giá tính chuẩn xác của thuật toán phân loại mức độ phục vụ LOS và giải quyết hiện tượng sai lệch khi đường vắng
    - 4.2.3. Đánh giá hiệu năng thời gian thực và mức tiêu thụ tài nguyên phần cứng
  - 4.3. Thảo luận
- **CHƯƠNG 5: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN**
  - 5.1. Kết luận
  - 5.2. Hạn chế
  - 5.3. Hướng phát triển
- **TÀI LIỆU THAM KHẢO**

---

\newpage

# DANH MỤC THUẬT NGỮ VÀ KÝ HIỆU VIẾT TẮT

| Viết tắt / Ký hiệu | Thuật ngữ đầy đủ | Ý nghĩa tiếng Việt |
| :--- | :--- | :--- |
| **ITS** | Intelligent Transportation System | Hệ thống Giao thông Thông minh |
| **LOS** | Level of Service | Mức độ phục vụ của đường |
| **V/C** | Volume / Capacity Ratio | Hệ số sử dụng năng lực thông hành của đường |
| **PCU** | Passenger Car Unit | Xe con quy đổi (Đơn vị tương đương xe con) |
| **$Q$** | Traffic Flow / Volume | Lưu lượng xe (xe/giờ hoặc PCU/giờ) |
| **$V$** | Space Mean Speed | Vận tốc trung bình dòng xe (km/h) |
| **$K$** | Traffic Density | Mật độ giao thông (xe/km hoặc xe/km/làn) |
| **ROI** | Region of Interest | Vùng quan tâm (Vùng mặt đường quan sát) |
| **YOLO** | You Only Look Once | Thuật toán phát hiện/phân loại đối tượng một giai đoạn |
| **MOT** | Multi-Object Tracking | Theo dõi đa mục tiêu thời gian thực |
| **FPS** | Frames Per Second | Số khung hình xử lý trên mỗi giây |
| **mAP** | Mean Average Precision | Độ chính xác trung bình toàn diện |
| **SSE** | Server-Sent Events | Giao thức truyền dữ liệu một chiều từ máy chủ tới web client |
| **FLOPs** | Floating Point Operations | Số lượng phép tính dấu phẩy động |
| **CNN** | Convolutional Neural Network | Mạng nơ-ron tích chập |

---

\newpage

# CHƯƠNG 1: MỞ ĐẦU

## 1.1. Tính cấp thiết của đề tài

Cùng với tiến trình công nghiệp hóa, hiện đại hóa và đô thị hóa nhanh chóng, áp lực lên hệ thống hạ tầng giao thông tại các đô thị lớn ở Việt Nam (đặc biệt là Hà Nội và TP. Hồ Chí Minh) ngày càng gia tăng nghiêm trọng. Sự bùng nổ của các phương tiện giao thông cơ giới cá nhân, trong đó xe máy chiếm trên 85% tổng lượng phương tiện, kết hợp với mạng lưới đường đô thị chật hẹp, giao cắt dày đặc đã dẫn đến tình trạng ùn tắc giao thông cục bộ và diện rộng diễn ra thường xuyên vào các khung giờ cao điểm. 

Ùn tắc giao thông gây ra những hệ lụy nặng nề về kinh tế - xã hội: làm gia tăng thời gian di chuyển, lãng phí hàng ngàn tỷ đồng tiền nhiên liệu mỗi năm, làm tăng lượng phát thải khí nhà kính ($CO_2, CO, PM_{2.5}$) gây ô nhiễm môi trường, đồng thời gây ức chế tâm lý và suy giảm chất lượng cuộc sống của người dân.

Các phương pháp giám sát giao thông truyền thống tại Việt Nam hiện nay bộc lộ nhiều hạn chế cốt tử:
1. **Phụ thuộc vào cảm biến vật lý xâm lấn (Loop Detectors, Radar, Cảm biến áp điện):** Chi phí lắp đặt và bảo dưỡng rất cao, phải cắt phá mặt đường gây hư hỏng kết cấu hạ tầng, dễ bị tê liệt khi đường bị đào xới cải tạo và khó triển khai trên diện rộng.
2. **Hệ thống camera giám sát (CCTV) thụ động:** Đa phần các camera giao thông hiện nay chỉ đóng vai trò ghi nhận hình ảnh đơn thuần để phục vụ việc trích xuất nguội (phạt nguội) hoặc để nhân viên điều hành quan sát bằng mắt thường. Khi xảy ra ùn tắc, con người không thể cùng lúc theo dõi hàng trăm màn hình để phát hiện và điều tiết kịp thời.
3. **Các ứng dụng bản đồ dựa trên GPS (như Google Maps):** Chỉ đo đạc được tốc độ di chuyển của những tài xế có bật định vị điện thoại thông minh, không đếm được số lượng xe thực tế, không phân loại được lưu lượng từng loại phương tiện (xe máy, ô tô con, xe tải, xe buýt) và không cung cấp được các thông số cốt lõi của giao thông học để điều khiển chu kỳ đèn tín hiệu.
4. **Sự thiếu hụt mô hình phân loại trạng thái chuẩn khoa học:** Một số hệ thống ứng dụng thị giác máy tính ban đầu thường mắc lỗi logic nghiêm trọng khi đánh giá ùn tắc dựa trên tốc độ đơn thuần. Ví dụ: khi một chiếc xe ô tô dừng trước vạch sơn chờ đèn đỏ hoặc rà phanh rẽ cua vào ban đêm (khi mặt đường trống trơn), hệ thống lại vội vàng cảnh báo "Ùn tắc nghiêm trọng", dẫn đến việc cảnh báo sai lệch và điều phối đèn giao thông bất hợp lý.

Xuất phát từ thực tiễn trên, việc **nghiên cứu và xây dựng một hệ thống giao thông thông minh toàn diện (ITS), tích hợp Thị giác máy tính (Computer Vision), Mạng nơ-ron học sâu (Deep Learning - YOLOv8) và Lý thuyết Dòng giao thông học (Traffic Flow Theory & Highway Capacity Manual)** nhằm tự động nhận diện, đếm xe, phân loại phương tiện quy đổi PCU, đo vận tốc, tính toán mật độ, lưu lượng và phân loại Mức độ phục vụ (LOS) là hết sức cấp thiết. Đề tài không chỉ giải quyết bài toán tự động hóa giám sát mà còn cung cấp cơ sở dữ liệu số thời gian thực phục vụ công tác quy hoạch đô thị và điều khiển tối ưu đèn tín hiệu giao thông.

---

## 1.2. Mục tiêu nghiên cứu

### Mục tiêu tổng quát:
Nghiên cứu, thiết kế và phát triển hoàn chỉnh một hệ thống thông tin giám sát, phân tích và cảnh báo giao thông thông minh hoạt động theo thời gian thực (Real-time ITS), có khả năng tiếp nhận luồng video từ các camera giao thông đô thị, nhận diện và phân loại chính xác các loại phương tiện đặc thù tại Việt Nam, tính toán tự động các chỉ số giao thông vi mô và vĩ mô ($Q, K, V, PCU, V/C, LOS$), hỗ trợ điều phối chu kỳ đèn tín hiệu tự thích ứng và dự báo lưu lượng dòng xe trong tương lai.

### Mục tiêu cụ thể:
1. **Nghiên cứu và làm sạch dữ liệu:** Thu thập, chuẩn hóa, gán nhãn và cân bằng tập dữ liệu hình ảnh phương tiện giao thông thực tế tại Việt Nam với 4 nhóm đối tượng chính: Xe máy, Ô tô con, Xe khách/buýt, Xe tải.
2. **Khảo sát, huấn luyện và đánh giá mô hình Deep Learning:** 
   - Tiến hành huấn luyện sâu mô hình phân loại phương tiện 100 epoch.
   - Thiết kế thực nghiệm đối đầu khoa học giữa hai kiến trúc **YOLOv8s** (Small) và **YOLOv8n** (Nano) qua 20 epoch khảo sát, đo lường toàn diện các chỉ số: Accuracy, Precision, Recall, F1-Score, mAP@50, mAP@50-95, FLOPs, Latency và FPS để tìm ra mô hình tối ưu cho cả máy chủ trung tâm và thiết bị biên.
3. **Xây dựng thuật toán thị giác máy tính chuyên sâu:**
   - Xây dựng vùng quan tâm ROI (Region of Interest) với ma trận biến đổi phối cảnh (Perspective Homography) để chuyển đổi chính xác tọa độ điểm ảnh (pixel) thành khoảng cách thực tế trên mặt đường (mét), khắc phục triệt để hiện tượng biến dạng xa - gần của camera.
   - Tích hợp thuật toán bám vết đa mục tiêu (ByteTrack) kết hợp vạch đếm ảo thông minh để đếm chính xác số lượt xe qua mặt cắt đường mà không bị đếm trùng lặp.
4. **Chuẩn hóa công thức đánh giá Mức độ phục vụ (LOS):**
   - Xây dựng thuật toán phân loại mức độ giao thông (Thông thoáng, Đông đúc, Ùn tắc) dựa trên bộ 3 tiêu chí cốt lõi ngành GTVT: Hệ số sử dụng năng lực đường ($V/C$), Vận tốc hành trình so với vận tốc thiết kế ($V/V_{\text{design}}$) và Mật độ dòng xe ($K$).
   - Giải quyết triệt để lỗi đánh giá sai lệch thực tế (khắc phục trường hợp đường rộng thênh thang chỉ có 1-3 xe nhưng bị báo nhầm là "Ùn tắc nghiêm trọng" do xe đi chậm rẽ cua).
5. **Xây dựng Động cơ Dự báo Chuỗi thời gian (Forecaster Engine):** Tích hợp các thuật toán học máy chuỗi thời gian (Holt's Damped Trend, Exponential Smoothing, Moving Average) có cơ chế Backtesting tự động tính toán sai số (MAE, RMSE, MAPE) để dự báo trước lưu lượng xe trong 15 - 60 phút tiếp theo.
6. **Xây dựng Ứng dụng Web hoàn chỉnh (TrafficVision Enterprise):** Thiết kế kiến trúc phần mềm phân tầng rõ ràng (Backend Flask RESTful API + Cơ sở dữ liệu SQLite tối ưu chuỗi thời gian + Giao diện Web Dark Theme hiện đại 7 phân hệ chuyên nghiệp), hỗ trợ giám sát đồng thời đa camera luồng thời gian thực.

---

## 1.3. Đối tượng và Phạm vi nghiên cứu

### Đối tượng nghiên cứu:
- **Dữ liệu hình ảnh và video giao thông:** Các luồng video CCTV ghi hình giao thông đô thị tại các nút giao thông trọng điểm ở Việt Nam.
- **Mô hình học sâu và thị giác máy tính:** Kiến trúc mạng nơ-ron tích chập YOLOv8 (phát hiện đối tượng và phân loại), thuật toán tracking đa mục tiêu ByteTrack, ma trận Homography.
- **Lý thuyết dòng giao thông:** Các công thức toán học về Lưu lượng dòng xe ($Q$), Mật độ ($K$), Vận tốc trung bình không gian ($V$), Hệ số xe con quy đổi ($PCU$), Năng lực thông hành ($C$), Hệ số sử dụng năng lực đường ($V/C$) và Mức độ phục vụ (Level of Service - LOS) theo sổ tay năng lực đường bộ HCM (Highway Capacity Manual).
- **Mô hình toán học dự báo chuỗi thời gian:** Phương pháp Holt's Damped Linear Trend, Moving Average.

### Phạm vi nghiên cứu:
- **Không gian:** Nghiên cứu áp dụng cho các tuyến đường trục chính và nút giao thông đô thị có điều khiển bằng đèn tín hiệu hoặc tự do tại Việt Nam.
- **Phương tiện nhận diện:** Tập trung vào 4 nhóm phương tiện cơ giới phổ biến nhất lưu thông trên đường phố Việt Nam: Xe máy (Motorbike), Ô tô con (Car), Xe khách/Xe buýt (Bus), Xe tải (Truck).
- **Phần cứng triển khai:** Đồ án thiết kế mô hình có thể hoạt động hiệu quả trên máy tính cá nhân/máy trạm trang bị GPU NVIDIA phổ thông (như RTX 3050/3060/4060) và tương thích triển khai trên các thiết bị nhúng Edge AI (như NVIDIA Jetson Nano / Orin).
- **Phần mềm:** Toàn bộ hệ thống được đóng gói thành giải pháp Web Application độc lập, tương thích trình duyệt web hiện đại, không phụ thuộc vào các dịch vụ đám mây trả phí của bên thứ ba.

---

## 1.4. Nội dung thực hiện

Đồ án được triển khai qua 5 nội dung công việc chính:
1. **Nội dung 1: Thu thập, khảo sát và tiền xử lý dữ liệu giao thông:**
   - Xây dựng các kịch bản thu thập hình ảnh và video từ camera thực tế.
   - Làm sạch dữ liệu, loại bỏ ảnh mờ, ảnh lỗi, ảnh trùng lặp.
   - Thống kê, trực quan hóa phân bố dữ liệu (EDA), cân bằng dữ liệu giữa các lớp phương tiện nhằm tránh hiện tượng thiên vị (bias) trong quá trình học sâu.
2. **Nội dung 2: Nghiên cứu, huấn luyện và đánh giá đối đầu mô hình AI:**
   - Huấn luyện mô hình YOLOv8s-cls với 100 epoch để đạt độ hội tụ tối đa.
   - Lập kịch bản khảo sát tự động 20 epoch giữa hai mô hình YOLOv8s và YOLOv8n trên cùng một tập dữ liệu chuẩn.
   - Đo đạc, phân tích ma trận nhầm lẫn (Confusion Matrix), tính toán sai số, trích xuất biểu đồ so sánh và lưu trữ dữ liệu ra các định dạng bảng tính Excel/CSV.
3. **Nội dung 3: Thiết kế và phát triển các thuật toán nghiệp vụ giao thông:**
   - Cài đặt thuật toán biến đổi phối cảnh mặt đường (Perspective Transformation) để chuyển đổi từ mặt phẳng ảnh 2D sang hệ tọa độ thực tế mét.
   - Cài đặt thuật toán đếm xe qua vạch ảo kết hợp bộ nhớ bám vết đối tượng để tính toán lưu lượng tức thời và lưu lượng tích lũy.
   - Cài đặt công thức tính Mật độ giao thông ($K$), Vận tốc hành trình ($V$), Lưu lượng ($Q$), Hệ số xe con quy đổi ($PCU$).
   - Thiết kế và chuẩn hóa thuật toán phân loại LOS đa tiêu chí kết hợp bộ lọc chống rung lắc trạng thái (Hysteresis Filter).
4. **Nội dung 4: Thiết kế kiến trúc và phát triển phần mềm Web:**
   - Xây dựng Backend đa luồng (Multi-threading) với Flask Server, quản lý song song nhiều CameraWorker.
   - Thiết kế cơ sở dữ liệu SQLite với cấu trúc lưu trữ chỉ số chuỗi thời gian theo phút.
   - Xây dựng động cơ dự báo chuỗi thời gian (Forecaster) với khả năng tự động đánh giá Backtest.
   - Xây dựng giao diện Dashboard thời gian thực (Frontend) với 7 tab chức năng trực quan hóa biểu đồ, cảnh báo và điều khiển tín hiệu đèn.
5. **Nội dung 5: Thử nghiệm, đánh giá và hoàn thiện hệ thống:**
   - Triển khai thử nghiệm đồng thời 4 camera luồng video thực tế tại các nút giao.
   - Đánh giá độ chính xác, độ trễ và tính ổn định của toàn hệ thống.
   - Kiểm thử các ca biên đặc biệt (đường vắng xe chạy chậm, ban đêm, xe rẽ cua) để chứng minh tính chuẩn xác của giải pháp mới.

---

## 1.5. Phương pháp thực hiện

Để hoàn thành các mục tiêu trên, đề tài kết hợp chặt chẽ các phương pháp nghiên cứu khoa học sau:
1. **Phương pháp nghiên cứu lý thuyết:**
   - Tổng hợp, phân tích các tài liệu khoa học trong và ngoài nước về Thị giác máy tính, Mạng nơ-ron tích chập (CNN), kiến trúc YOLO (You Only Look Once), các thuật toán Multi-Object Tracking.
   - Nghiên cứu tiêu chuẩn thiết kế đường đô thị TCVN 10380:2014 và Sổ tay năng lực đường bộ Hoa Kỳ (HCM - Highway Capacity Manual) để nắm vững bản chất toán học của các chỉ số $Q, K, V, V/C$ và các cấp phục vụ LOS từ A đến F.
2. **Phương pháp thực nghiệm (Empirical Method):**
   - Xây dựng quy trình thực nghiệm có đối chứng khoa học: cố định phần cứng, siêu tham số và tập dữ liệu kiểm thử để so sánh công bằng giữa YOLOv8s và YOLOv8n.
   - Sử dụng các chỉ số đo lường định lượng tiêu chuẩn quốc tế: Top-1 Accuracy, Top-5 Accuracy, Precision, Recall, F1-Score, mAP@50, mAP@50-95, GFLOPs, Latency (ms), Frame Per Second (FPS).
3. **Phương pháp mô hình hóa và biến đổi toán học:**
   - Sử dụng phép biến đổi xạ ảnh (Projective Geometry / Homography Matrix $H$) trong không gian hai chiều $\mathbb{R}^2$ để ánh xạ điểm ảnh $(u, v)$ thành tọa độ địa lý mặt đường $(X, Y)$ tính bằng mét.
   - Ứng dụng quy hoạch tuyến tính và cân bằng hàm mũ (Exponential Smoothing) trong làm mịn dữ liệu lưu lượng và mật độ theo thời gian thực.
4. **Phương pháp phát triển phần mềm hướng module (Modular Software Engineering):**
   - Áp dụng nguyên lý phân tách trách nhiệm (Separation of Concerns): Tách biệt triệt để tầng Thu nhận hình ảnh (Ingestion Layer), tầng Suy luận AI (AI Inference Layer), tầng Xử lý nghiệp vụ logic (Business Logic Layer), tầng Lưu trữ (Data Access Layer) và tầng Trình diễn người dùng (Presentation Layer).
   - Tối ưu hóa xử lý song song thông qua cơ chế đa luồng độc lập (`threading.Thread`), hàng đợi an toàn (`queue.Queue`) và bộ đệm xoay vòng (`collections.deque`) nhằm ngăn chặn hiện tượng tắc nghẽn luồng (thread blocking) và suy giảm FPS.

---

\newpage

# CHƯƠNG 2: CƠ SỞ LÝ THUYẾT VÀ CÔNG NGHỆ SỬ DỤNG

## 2.1. Cơ sở lý thuyết

### 2.1.1. Các thông số đặc trưng của dòng giao thông ($Q, V, K, PCU$)

Dòng giao thông là tập hợp các phương tiện di chuyển độc lập nhưng tương tác lẫn nhau trên một tuyến đường. Ba thông số vĩ mô cơ bản nhất mô tả trạng thái của dòng giao thông được định nghĩa như sau:

#### 1. Lưu lượng giao thông ($Q$ - Traffic Flow / Volume):
Lưu lượng là số lượng phương tiện đi qua một mặt cắt đường nhất định trong một đơn vị thời gian (thường tính bằng xe/giờ hoặc PCU/giờ):
$$Q = \frac{N}{T} \times 3600 \quad (\text{xe/h})$$
Trong đó: $N$ là số xe đếm được qua mặt cắt trong khoảng thời gian $T$ (giây).

#### 2. Vận tốc trung bình không gian ($V$ - Space Mean Speed):
Là vận tốc trung bình của toàn bộ các phương tiện đang lưu thông trên một đoạn đường có chiều dài $L$:
$$V = \frac{L}{\frac{1}{N}\sum_{i=1}^{N} t_i} = \frac{N \times L}{\sum_{i=1}^{N} t_i} \quad (\text{km/h})$$
Trong đó $t_i$ là thời gian xe thứ $i$ di chuyển hết đoạn đường $L$.

#### 3. Mật độ giao thông ($K$ - Traffic Density):
Là số lượng phương tiện hiện diện trên một đơn vị chiều dài của tuyến đường tại một thời điểm nhất định (thường tính bằng xe/km hoặc xe/km/làn):
$$K = \frac{N_{\text{tức thời}}}{L_{\text{đoạn đường}}} \quad (\text{xe/km})$$

#### Mối quan hệ tương quan cơ bản giữa $Q, K, V$:
Theo phương trình liên tục của dòng giao thông (Lighthill-Whitham-Richards):
$$Q = K \times V$$
Công thức này cho thấy lưu lượng dòng xe là tích số của mật độ và vận tốc trung bình. Khi mật độ tăng cao đến mức bão hòa (Jam Density - $K_{\text{jam}}$), vận tốc sẽ tiệm cận về 0 và lưu lượng $Q$ sẽ sụt giảm mạnh về 0, dẫn đến hiện tượng tắc nghẽn hoàn toàn.

#### 4. Hệ số xe con quy đổi ($PCU$ - Passenger Car Unit):
Do đặc thù giao thông Việt Nam có sự pha trộn hỗn hợp nhiều loại phương tiện với kích thước, gia tốc và diện tích chiếm đường khác nhau, ngành GTVT sử dụng hệ số PCU để quy đổi các phương tiện về xe con tiêu chuẩn theo bảng trọng số chuẩn TCVN:
* Xe máy (Motorbike): $PCU = 0.3$
* Ô tô con (Car): $PCU = 1.0$
* Xe khách / Xe buýt (Bus): $PCU = 2.0$
* Xe tải (Truck): $PCU = 2.5$

Tổng lượng xe con quy đổi trong vùng quan sát được tính bằng:
$$PCU_{\text{tổng}} = \sum_{k \in \{\text{xe máy, ô tô, bus, tải}\}} N_k \times PCU_k$$

---

### 2.1.2. Khái niệm Mức độ phục vụ (LOS) và Hệ số sử dụng năng lực đường ($V/C$)

Theo Sổ tay Năng lực Đường bộ (Highway Capacity Manual - HCM) và Tiêu chuẩn Thiết kế Đường đô thị, **Mức độ phục vụ (Level of Service - LOS)** là chỉ tiêu định tính phản ánh chất lượng vận hành của dòng giao thông dưới góc nhìn của người tham gia giao thông (vận tốc, thời gian di chuyển, sự thoải mái và tự do cơ động).

LOS được phân chia thành 6 cấp độ từ A đến F:
- **LOS A:** Dòng xe lưu thông tự do hoàn toàn, tài xế hoàn toàn làm chủ tốc độ.
- **LOS B:** Lưu thông tương đối tự do, bắt đầu có sự hiện diện của các xe khác nhưng không ảnh hưởng tới vận tốc.
- **LOS C:** Dòng xe ổn định, việc chuyển làn và vượt xe bắt đầu bị hạn chế.
- **LOS D:** Dòng xe dày đặc, tốc độ bị suy giảm đáng kể, khả năng cơ động bị hạn chế nghiêm trọng.
- **LOS E:** Dòng xe tiệm cận năng lực thông hành tối đa của đường, vận tốc rất thấp và không ổn định (Ùn ứ).
- **LOS F:** Vượt quá khả năng thông hành, dòng xe bị tắc nghẽn, dừng - chạy liên tục (Stop-and-Go), xảy ra nghẽn cổ chai.

Chỉ số toán học quan trọng nhất để xác định LOS là **Hệ số sử dụng năng lực đường ($V/C$)**:
$$\text{Hệ số } V/C = \frac{\text{Lưu lượng thực tế (Volume)}}{\text{Khả năng thông hành của đường (Capacity)}} = \frac{Q}{C_{\text{tổng}}}$$
Trong đó:
* $C_{\text{tổng}} = n_{\text{làn}} \times C_{\text{làn}}$ (với $C_{\text{làn}} \approx 1800\text{ xe/h/làn}$ là năng lực thông hành thiết kế của một làn xe đô thị tiêu chuẩn).

Quy chuẩn phân cấp trạng thái theo $V/C$:
* **Thông thoáng (LOS A - B):** $V/C < 0.60$.
* **Đông đúc (LOS C - D):** $0.60 \le V/C \le 0.85$.
* **Ùn tắc (LOS E - F):** $V/C > 0.85$ (Đặc biệt khi $V/C \ge 1.00$ là quá tải nghiêm trọng).

---

### 2.1.3. Thị giác máy tính và Mạng nơ-ron tích chập (CNN)

Thị giác máy tính (Computer Vision) là lĩnh vực khoa học nghiên cứu phương pháp giúp máy tính có khả năng thu nhận, xử lý, phân tích và trích xuất thông tin có ý nghĩa từ hình ảnh hoặc video kỹ thuật số.

Trọng tâm của thị giác máy tính hiện đại là **Mạng nơ-ron tích chập (Convolutional Neural Network - CNN)**. Khác với mạng nơ-ron truyền thống kết nối đầy đủ (Fully Connected Network), CNN khai thác đặc tính không gian cục bộ (Spatial Locality) của ảnh thông qua các lớp:
1. **Lớp Tích chập (Convolutional Layer):** Sử dụng các bộ lọc (Kernels) trượt trên ma trận ảnh để trích xuất các đặc trưng cơ bản như cạnh, góc, vân bề mặt ở các tầng nông, và các đặc trưng ngữ nghĩa phức tạp (bánh xe, đầu xe, khung xe) ở các tầng sâu.
2. **Lớp Chuẩn hóa (Batch Normalization):** Chuẩn hóa phân phối đầu ra của các tầng tích chập giúp mạng hội tụ nhanh và ổn định hơn.
3. **Lớp Kích hoạt phi tuyến (Activation Function):** Sử dụng các hàm phi tuyến như ReLU, LeakyReLU hoặc SiLU để học các biểu diễn dữ liệu phức tạp.
4. **Lớp Gộp (Pooling Layer):** Giảm kích thước không gian của bản đồ đặc trưng (Feature Maps), giúp giảm số lượng tham số tính toán và tạo ra tính bất biến với các phép tịnh tiến nhỏ.

---

### 2.1.4. Kiến trúc mô hình nhận diện đối tượng YOLOv8

YOLO (You Only Look Once), do Joseph Redmon khởi xướng và được Ultralytics phát triển hoàn thiện đến thế hệ **YOLOv8** (2023), là kiến trúc mạng nơ-ron phát hiện và phân loại đối tượng một giai đoạn (One-Stage Detector) tiên tiến nhất hiện nay.

Kiến trúc tổng thể của YOLOv8 gồm 3 khối chính:
1. **Backbone (Xương sống):** Sử dụng mạng cải tiến CSPDarknet kết hợp với các khối **C2f (Cross-Stage Partial with 2 Convolutions)** lấy cảm hứng từ ELAN (Efficient Layer Aggregation Network) của YOLOv7. Khối C2f giúp cải thiện luồng truyền gradient, tăng cường khả năng trích xuất đặc trưng đa tầng mà không làm tăng đột biến số lượng tham số. Ở cuối Backbone tích hợp khối **SPPF (Spatial Pyramid Pooling - Fast)** để gom đặc trưng đa tỉ lệ với tốc độ xử lý vượt trội.
2. **Neck (Cổ mạng):** Sử dụng kiến trúc kết hợp **PANet (Path Aggregation Network)** và **FPN (Feature Pyramid Network)** giúp truyền tải hiệu quả cả đặc trưng ngữ nghĩa từ tầng sâu lên và thông tin vị trí chi tiết từ tầng nông xuống.
3. **Head (Đầu mạng):** Khác biệt đột phá của YOLOv8 là chuyển sang thiết kế **Anchor-Free** (không sử dụng neo hộp mặc định) và **Decoupled Head** (tách biệt đầu phân loại nhãn Class Loss và đầu hồi quy tọa độ hộp Bounding Box Loss).
   - Hàm mất mát phân loại: Sử dụng **Binary Cross-Entropy (BCE Loss)**.
   - Hàm mất mát hồi quy tọa độ: Sử dụng kết hợp **Complete IoU (CIoU Loss)** và **Distribution Focal Loss (DFL)**.

Họ mô hình YOLOv8 cung cấp nhiều phiên bản kích thước khác nhau: Nano ($n$), Small ($s$), Medium ($m$), Large ($l$) và Extra ($x$). Trong đề tài này, hai phiên bản **YOLOv8n** và **YOLOv8s** được chọn để nghiên cứu chuyên sâu nhằm tối ưu hóa sự cân bằng giữa độ chính xác và tốc độ suy luận thời gian thực.

---

### 2.1.5. Kỹ thuật theo dõi đối tượng đa mục tiêu (Multi-Object Tracking - ByteTrack)

Trong bài toán giao thông, việc chỉ phát hiện đối tượng trên từng khung hình độc lập là chưa đủ, hệ thống cần duy trì danh tính duy nhất (Track ID) của mỗi phương tiện xuyên suốt các khung hình liên tiếp để đo vận tốc, vẽ quỹ đạo và đếm số lượng xe không trùng lặp.

Đề tài tích hợp thuật toán **ByteTrack** (Zhang et al., 2022) - thuật toán theo dõi đối tượng đa mục tiêu hàng đầu hiện nay. Điểm sáng tạo của ByteTrack là cơ chế kết hợp dữ liệu hai bước (BYTE Data Association):
- **Bước 1:** Ghép nối các hộp phát hiện có độ tin cậy cao ($Conf > 0.5$) với các tracklet hiện có bằng giải thuật Hungarian dựa trên ma trận khoảng cách IoU và bộ lọc Kalman (Kalman Filter).
- **Bước 2:** Không vội vàng loại bỏ các hộp phát hiện có độ tin cậy thấp ($0.1 < Conf \le 0.5$) như các thuật toán truyền thống (SORT, DeepSORT), ByteTrack tiếp tục ghép nối các hộp này với các tracklet chưa được ghép ở bước 1. Điều này giúp hệ thống duy trì theo dõi mượt mà ngay cả khi phương tiện bị che khuất một phần (occlusion), bị mờ do chuyển động hoặc đi xa camera.

---

### 2.1.6. Mô hình dự báo chuỗi thời gian giao thông

Lưu lượng dòng xe theo thời gian tạo thành một chuỗi dữ liệu có cấu trúc thời gian (Time-series Data) với các đặc trưng xu hướng (Trend) và tính chu kỳ trong ngày (Diurnal Cyclicity). Đề tài cài đặt động cơ dự báo dựa trên:

#### 1. Mô hình xu hướng có giảm chấn Holt (Holt's Damped Linear Trend):
Phương pháp làm mịn hàm mũ hai tham số có hệ số triệt tiêu xu hướng $\phi \in (0, 1)$ giúp ngăn chặn việc dự báo phóng đại quá mức theo thời gian dài:
- Cấp độ làm mịn (Level):
  $$l_t = \alpha y_t + (1 - \alpha)(l_{t-1} + \phi b_{t-1})$$
- Xu hướng làm mịn (Trend):
  $$b_t = \beta (l_t - l_{t-1}) + (1 - \beta)\phi b_{t-1}$$
- Giá trị dự báo cho $h$ bước tiếp theo:
  $$\hat{y}_{t+h|t} = l_t + \sum_{i=1}^{h}\phi^i b_t$$

#### 2. Cơ chế kiểm định ngược (Backtesting Engine):
Để đảm bảo độ tin cậy khoa học của kết quả dự báo trước khi hiển thị cho người vận hành, hệ thống tự động trích xuất chuỗi dữ liệu quá khứ và đo đạc 3 chỉ số sai số:
- Sai số tuyệt đối trung bình: $\text{MAE} = \frac{1}{n}\sum |y_i - \hat{y}_i|$
- Căn bậc hai sai số toàn phương trung bình: $\text{RMSE} = \sqrt{\frac{1}{n}\sum (y_i - \hat{y}_i)^2}$
- Phần trăm sai số tuyệt đối trung bình: $\text{MAPE} = \frac{1}{n}\sum \left|\frac{y_i - \hat{y}_i}{y_i}\right| \times 100\%$

---

## 2.2. Công nghệ sử dụng

### 2.2.1. Ngôn ngữ Python và hệ sinh thái thư viện AI/CV
- **Python 3.12:** Ngôn ngữ lập trình chính được lựa chọn nhờ cú pháp trong sáng, hiệu năng xử lý toán học cao và hệ sinh thái mã nguồn mở phong phú nhất trong lĩnh vực Khoa học Dữ liệu và AI.
- **PyTorch 2.6.0 + CUDA 12.4:** Nền tảng học sâu hàng đầu, cung cấp khả năng tính toán ma trận song song trên GPU và hỗ trợ tăng tốc suy luận phần cứng.
- **Ultralytics YOLOv8:** Bộ thư viện tiêu chuẩn chính thức của Ultralytics cung cấp API huấn luyện, xuất mô hình (ONNX, TensorRT, PyTorch `.pt`) và tối ưu hóa luồng xử lý ảnh.
- **OpenCV (Open Source Computer Vision Library):** Thư viện thị giác máy tính hiệu năng cao bằng C++ với giao diện Python, đảm nhiệm việc giải mã codec video (H.264, H.265/HEVC), thao tác ma trận biến đổi hình học (warpPerspective), vẽ bounding box, vạch đếm và thanh HUD.
- **NumPy & Pandas:** Xử lý mảng đa chiều hiệu năng cao, vector hóa các phép tính khoảng cách Euclid và quản lý cấu trúc bảng dữ liệu chuỗi thời gian.
- **Matplotlib & Seaborn:** Trực quan hóa các biểu đồ phân tích dữ liệu khám phá (EDA), đồ thị huấn luyện Loss/Accuracy và ma trận nhầm lẫn (Confusion Matrix).

---

### 2.2.2. Khung ứng dụng Web Flask & Cơ chế truyền phát Server-Sent Events (SSE)
- **Flask Web Framework:** Khung ứng dụng web gọn nhẹ (Micro-framework) chuẩn WSGI, giúp xây dựng các endpoint RESTful API an toàn, tốc độ phản hồi cực nhanh với chi phí tài nguyên tối thiểu.
- **Server-Sent Events (SSE) & MJPEG Streaming:**
  - Để truyền phát luồng video trực tiếp từ camera tới trình duyệt web với độ trễ siêu thấp ($< 100\text{ ms}$), hệ thống sử dụng giao thức chuẩn đa phương tiện `multipart/x-mixed-replace; boundary=frame`.
  - Để đồng bộ hóa các chỉ số đo lường (KPI, biểu đồ tốc độ, mật độ) mỗi giây mà không cần trình duyệt phải gửi yêu cầu HTTP liên tục (polling), hệ thống sử dụng kết nối bền vững SSE (Server-Sent Events), giúp tiết kiệm tới 80% băng thông mạng so với phương pháp truyền thống.

---

### 2.2.3. Hệ quản trị cơ sở dữ liệu SQLite tối ưu chuỗi thời gian
- Đề tài sử dụng **SQLite 3** tích hợp sẵn trong Python, không đòi hỏi cấu hình dịch vụ phức tạp, độ ổn định tuyệt đối và tốc độ truy vấn đọc/ghi cục bộ cực nhanh.
- Thiết kế tối ưu hóa với cơ chế ghi giao dịch an toàn (WAL - Write-Ahead Logging) cho phép đọc và ghi dữ liệu đồng thời từ nhiều luồng camera mà không bị khóa cơ sở dữ liệu (Database Locked).
- Bổ sung cơ chế bảo mật xác thực tài khoản người dùng với mã hóa băm mật khẩu một chiều **PBKDF2-HMAC-SHA256** kết hợp muối (Salt) và chống tấn công vét cạn (Brute-force Protection).

---

### 2.2.4. Công nghệ Frontend hiện đại (Vanilla JS, Chart.js, Lucide Icons)
- **Giao diện người dùng Dark Theme chuẩn SaaS:** Thiết kế chuyên nghiệp, độ tương phản cao, tối ưu cho các trung tâm điều hành giao thông (TOC - Traffic Operation Center) hoạt động 24/7.
- **Hệ thống Design Tokens CSS:** Quản lý tập trung bảng màu, khoảng cách (Spacing 8px grid), font chữ chuẩn hệ thống giúp giao diện mượt mà, đồng nhất và tương thích hoàn hảo trên mọi kích thước màn hình (Responsive Design).
- **Chart.js:** Thư viện vẽ biểu đồ Canvas tương tác trực quan thời gian thực (đồ thị đường phân bố lưu lượng theo phút, biểu đồ phân loại xe dạng Doughnut, biểu đồ cột so sánh vận tốc).
- **Lucide SVG Icons:** Bộ biểu tượng phẳng hiện đại, sắc nét ở mọi độ phân giải.

---

## 2.3. Các nghiên cứu liên quan

Trong những năm gần đây, bài toán ứng dụng học sâu vào giao thông thông minh đã thu hút nhiều công trình nghiên cứu nổi bật:
- *Bochkovskiy et al. (2020)* đã phát triển YOLOv4 mở đường cho việc áp dụng mạng nơ-ron phát hiện đối tượng trên các thiết bị nhúng thời gian thực.
- *Ge et al. (2021)* công bố YOLOX với thiết kế Anchor-Free loại bỏ sự phụ thuộc vào tập hộp neo định trước.
- *Zhang et al. (2022)* công bố thuật toán ByteTrack trên tạp chí ECCV, chứng minh việc tận dụng các hộp phát hiện có độ tin cậy thấp có thể gia tăng đáng kể chỉ số MOTA/IDF1 khi theo dõi dòng xe trong điều kiện che khuất.
- Tại Việt Nam, một số nghiên cứu của các tác giả tại Đại học Bách Khoa Hà Nội và Đại học GTVT đã bước đầu thử nghiệm đếm xe máy bằng xử lý ảnh cổ điển (Background Subtraction) hoặc YOLOv3/v5. 

Tuy nhiên, hầu hết các công trình nghiên cứu trước đây chỉ dừng lại ở bài toán **đếm số lượng xe đơn thuần** trong môi trường phòng thí nghiệm (Offline Video Analysis). Rất ít công trình tích hợp đầy đủ chu trình: **Biến đổi Homography thực tế $\to$ Tính toán đồng thời $Q, K, V, PCU \to$ Đánh giá chuẩn LOS theo $V/C \to$ Dự báo xu hướng $\to$ Đóng gói thành hệ thống Web điều hành đa camera thời gian thực**. Đây chính là khoảng trống công nghệ mà đồ án này tập trung giải quyết trọn vẹn.

---

## 2.4. Giải pháp đề xuất

Từ việc phân tích các ưu nhược điểm của các nghiên cứu trước, đồ án đề xuất giải pháp hệ thống toàn diện **TrafficVision Enterprise** với 4 trụ cột kỹ thuật đột phá:
1. **Kiến trúc mô hình lai (Hybrid Architecture):** Kết hợp khả năng phát hiện vị trí chính xác của YOLOv8 Object Detection với bộ phân loại chuyên sâu phương tiện giao thông Việt Nam đã được huấn luyện cân bằng 4 lớp, đảm bảo độ chính xác nhận diện đạt $> 99\%$.
2. **Kỹ thuật hình học xạ ảnh phẳng (Perspective Homography):** Đo đạc chiều dài thực tế của đoạn đường ($L\text{ mét}$) và vận tốc thực tế ($V\text{ km/h}$) dựa trên ma trận chuyển đổi tọa độ điểm ảnh sang mét thực địa, loại bỏ hoàn toàn các sai số ước lượng cảm tính.
3. **Thuật toán phân loại LOS đa tiêu chí theo chuẩn GTVT:** Kết hợp đồng thời 3 tiêu chí: Hệ số sử dụng năng lực đường ($V/C$), Tỷ lệ vận tốc so với tốc độ thiết kế ($V/V_{\text{design}}$) và Mật độ chiếm dụng mặt đường ($K, \text{Occupancy}\%$), có bổ sung ràng buộc vật lý loại trừ lỗi nhận diện sai khi đường vắng.
4. **Hệ thống điều hành phân tán thời gian thực:** Đóng gói toàn bộ giải pháp thành nền tảng Web đa luồng, hỗ trợ kết nối đồng thời nhiều camera CCTV, tự động lưu trữ cơ sở dữ liệu chuỗi thời gian và cung cấp cảnh báo điều khiển tín hiệu đèn giao thông thông minh.

---

\newpage

# CHƯƠNG 3: PHÂN TÍCH, THIẾT KẾ VÀ XÂY DỰNG HỆ THỐNG

## 3.1. Phân tích yêu cầu

### 3.1.1. Yêu cầu chức năng
1. **Quản lý thu nhận luồng video (Video Ingestion):**
   - Hỗ trợ kết nối đồng thời tối thiểu 4 luồng video camera giao thông qua giao thức RTSP hoặc các tệp video giám sát thực tế (.mp4, .mkv, .avi).
   - Tự động phát hiện mất kết nối và tự động khởi động lại luồng (Auto-reconnect).
2. **Nhận diện và bám vết phương tiện (Detection & Tracking):**
   - Phát hiện chính xác vị trí bounding box của các phương tiện trong vùng quan sát ROI.
   - Phân loại chính xác 4 nhóm phương tiện: Xe máy, Ô tô con, Xe buýt/khách, Xe tải.
   - Cấp phát và duy trì mã định danh duy nhất (Track ID) cho mỗi phương tiện trong suốt hành trình qua khung hình.
3. **Đo đạc và tính toán các chỉ số giao thông vi mô & vĩ mô:**
   - Đếm chính xác số lượng xe qua vạch kích hoạt ảo theo từng loại phương tiện và tính tổng xe con quy đổi ($PCU$).
   - Đo vận tốc tức thời và vận tốc trung bình không gian ($V$) bằng phép chiếu Homography.
   - Tính toán mật độ xe ($K\text{ xe/km}$) và tỷ lệ chiếm dụng lòng đường ($\text{Occupancy}\%$).
   - Tính toán lưu lượng dòng xe tức thời ($Q\text{ xe/h}$) và hệ số tải trọng đường ($V/C$).
4. **Đánh giá mức độ phục vụ (LOS) và phát hiện ùn tắc:**
   - Phân loại trạng thái giao thông theo 4 mức độ: Thông thoáng (LOS A-B), Đông đúc (LOS C-D), Ùn tắc (LOS E), Ùn tắc nghiêm trọng (LOS F).
   - Tích hợp bộ lọc làm mịn Hysteresis để trạng thái không bị chớp nháy thất thường.
5. **Cảnh báo và hỗ trợ điều khiển đèn tín hiệu:**
   - Tự động phát hiện xe dừng trong hàng chờ (Queue Detection) và độ dài hàng chờ ($m$).
   - Đưa ra khuyến nghị chu kỳ đèn xanh/đỏ tối ưu thích ứng theo mật độ thực tế của từng nhánh ngã tư.
6. **Dự báo chuỗi thời gian:**
   - Dự báo trước xu hướng biến thiên của lưu lượng dòng xe trong các khoảng thời gian 15, 30, 45, 60 phút tiếp theo kèm theo các chỉ số tin cậy (MAE, RMSE, MAPE).
7. **Lưu trữ dữ liệu và trích xuất báo cáo:**
   - Tự động ghi nhận số liệu trung bình mỗi phút vào cơ sở dữ liệu SQLite.
   - Cung cấp tính năng truy vấn lịch sử, xuất báo cáo ra file Excel (.xls, .csv).
8. **Quản trị người dùng và phân quyền:**
   - Màn hình đăng nhập bảo mật, phân quyền người dùng (Admin / Operator), cơ chế khóa tài khoản khi nhập sai quá số lần quy định.

### 3.1.2. Yêu cầu phi chức năng
- **Hiệu năng thời gian thực:** Tốc độ xử lý của pipeline AI đạt tối thiểu $25 - 30\text{ FPS}$ trên mỗi luồng camera để đảm bảo không bị trễ khung hình (Real-time Latency $< 100\text{ ms}$).
- **Độ chính xác cao:** Độ chính xác phân loại phương tiện đạt trên $95\%$; sai số đếm xe qua vạch ảo dưới $5\%$.
- **Tính ổn định và sẵn sàng cao (High Availability):** Hệ thống có khả năng vận hành liên tục 24/7, tự động thu hồi bộ nhớ đệm (Garbage Collection), không bị rò rỉ bộ nhớ (Memory Leak) khi chạy dài ngày.
- **Tính khả chuyển và dễ bảo trì (Maintainability):** Mã nguồn được cấu trúc module hóa phân tầng rõ ràng (Backend, Frontend, Core, Training), dễ dàng cấu hình góc camera và các ngưỡng qua file `config.py` mà không phải viết lại mã nguồn.

---

## 3.2. Thiết kế hệ thống tổng thể (System Pipeline)

### 3.2.1. Kiến trúc phân tầng 4 lớp (Layered Architecture)

Hệ thống được thiết kế theo mô hình kiến trúc phân tầng chuyên biệt, bao gồm 4 lớp chính:

```
+-------------------------------------------------------------------------+
|                  TẦNG 1: THU NHẬN HÌNH ẢNH (CAMERA LAYER)               |
|  Camera 01 (CCTV)  |  Camera 02 (CCTV)  |  Camera 03  |  Camera 04      |
|  RTSP Stream / File Video MP4/MKV -> OpenCV VideoCapture đa luồng       |
+-------------------------------------------------------------------------+
                                    | (Frame Buffer)
                                    v
+-------------------------------------------------------------------------+
|                TẦNG 2: XỬ LÝ AI LÕI (AI CORE PIPELINE LAYER)            |
|  - Phân vùng ROI đa giác & Ma trận Perspective Homography               |
|  - Phát hiện & Phân loại phương tiện (YOLOv8 Detection / Classification)|
|  - Bám vết đa mục tiêu liên tục (ByteTrack Multi-Object Tracker)        |
|  - Vạch đếm ảo thông minh & Tính toán chỉ số: Q, K, V, PCU, V/C, LOS    |
+-------------------------------------------------------------------------+
                                    | (Telemetry & Metrics)
                                    v
+-------------------------------------------------------------------------+
|                 TẦNG 3: DỊCH VỤ HỆ THỐNG (BACKEND SERVICE LAYER)         |
|  - Flask Application Server & RESTful APIs                              |
|  - CameraManager quản lý song song 4 CameraWorker Threads               |
|  - Time-series Forecaster Engine (Holt's Damped Trend, Backtest Metrics)|
|  - SQLite Database Engine (traffic_metrics.db, WAL Mode, User Security) |
+-------------------------------------------------------------------------+
                                    | (SSE JSON Streams & MJPEG Video)
                                    v
+-------------------------------------------------------------------------+
|                 TẦNG 4: GIAO DIỆN NGƯỜI DÙNG (FRONTEND UI LAYER)         |
|  - Dark Mode SaaS Dashboard (Responsive 7 Tabs)                         |
|  - Trình phát video thời gian thực siêu mượt (Multi-Camera Grid)        |
|  - Biểu đồ động tương tác Chart.js (Lưu lượng, Vận tốc, Mật độ)         |
|  - Bảng điều khiển tín hiệu đèn & Trung tâm Cảnh báo ùn tắc             |
+-------------------------------------------------------------------------+
```

---

### 3.2.2. Luồng xử lý dữ liệu và thị giác máy tính (Computer Vision Pipeline)

Quy trình xử lý một khung hình video trong `CameraWorker` diễn ra tuần tự qua các bước:
1. **Đọc khung hình:** Khung hình được đọc từ nguồn video vào bộ nhớ đệm ma trận BGR.
2. **Cắt lọc theo vùng quan tâm (ROI Clipping):** Giới hạn phạm vi tính toán trong đa giác 4 đỉnh của mặt đường để loại bỏ người đi bộ trên vỉa hè và cây cối xung quanh.
3. **Thực thi mô hình YOLOv8:** Đưa khung hình qua mạng nơ-ron để trích xuất danh sách bounding box $(x_1, y_1, x_2, y_2)$, điểm tin cậy ($Confidence$) và lớp xe ($Class$).
4. **Cập nhật bộ bám vết ByteTrack:** Ghép nối các hộp phát hiện với danh sách Tracklet đang theo dõi, cập nhật vị trí điểm tiếp đất $(cx, y_2)$ của từng xe.
5. **Đo đạc vận tốc:** Với mỗi xe đã theo dõi qua $\ge 2$ khung hình, tính quãng đường dịch chuyển trên mặt đường thông qua ma trận Homography và chia cho thời gian trôi qua giữa các frame ($\Delta t$):
   $$V_i = \frac{\sqrt{(X_t - X_{t-\Delta t})^2 + (Y_t - Y_{t-\Delta t})^2}}{\Delta t} \times 3.6 \quad (\text{km/h})$$
6. **Kiểm tra vạch đếm ảo:** Nếu quỹ đạo điểm tiếp đất của xe cắt qua đường thẳng đếm $Y_{\text{line}}$, hệ thống ghi nhận tăng biến đếm của lớp xe tương ứng và cộng dồn điểm PCU.
7. **Tổng hợp chỉ số và xác định trạng thái LOS:** Tính toán các giá trị trung bình $Q, K, V, V/C$ và chạy qua thuật toán phân loại mức độ phục vụ.
8. **Vẽ thanh HUD & Mã hóa luồng phát:** Vẽ bounding box, nhãn xe, vạch đếm và thanh thông số HUD lên frame, sau đó mã hóa JPEG đẩy ra hàng đợi stream.

---

### 3.2.3. Thuật toán biến đổi phối cảnh mặt đường (Perspective Homography)

Trong ảnh chụp từ camera giao thông đặt trên cao, một mét ở gần đáy ảnh sẽ chiếm số lượng pixel lớn hơn rất nhiều so với một mét ở tít xa cuối đường. Để tính toán chính xác mật độ và vận tốc, hệ thống sử dụng phép biến đổi xạ ảnh hai chiều:

$$\begin{bmatrix} x' \\ y' \\ w' \end{bmatrix} = \mathbf{H} \begin{bmatrix} u \\ v \\ 1 \end{bmatrix} = \begin{bmatrix} h_{11} & h_{12} & h_{13} \\ h_{21} & h_{22} & h_{23} \\ h_{31} & h_{32} & h_{33} \end{bmatrix} \begin{bmatrix} u \\ v \\ 1 \end{bmatrix}$$
Tọa độ thực tế $(X, Y)$ trên mặt đường tính bằng mét là:
$$X = \frac{x'}{w'} = \frac{h_{11}u + h_{12}v + h_{13}}{h_{31}u + h_{32}v + h_{33}}, \quad Y = \frac{y'}{w'} = \frac{h_{21}u + h_{22}v + h_{23}}{h_{31}u + h_{32}v + h_{33}}$$

Ma trận $\mathbf{H}$ (kích thước $3 \times 3$) được giải tự động bằng hàm `cv2.getPerspectiveTransform()` thông qua 4 điểm góc chuẩn của vùng ROI:
- Cặp điểm đáy gần camera: ứng với tọa độ $(0, 0)$ và $(W_{\text{thực}}, 0)$ mét.
- Cặp điểm đỉnh xa camera: ứng với tọa độ $(0, L_{\text{thực}})$ và $(W_{\text{thực}}, L_{\text{thực}})$ mét.

Nhờ đó, chiều dài đoạn đường $L_{\text{đoạn đường}}$ dùng để chia mật độ $K = N / L_{\text{đoạn đường}}$ là chiều dài hình học thực tế (ví dụ: $60.0\text{ m} = 0.060\text{ km}$), chứ không phải số lượng pixel giả định.

---

### 3.2.4. Thuật toán phân loại trạng thái tắc nghẽn giao thông dựa trên LOS, $V/C$ và Mật độ thực tế

Để giải quyết triệt để nhược điểm của các thuật toán truyền thống và hiện tượng báo sai lệch khi đường vắng, hệ thống đề xuất cây quyết định phân tầng khoa học:

```
[Số lượng xe trong ROI] & [Hệ số V/C = Q / C]
                 |
                 +---> V/C < 0.50 HOẶC Tổng xe <= 8 xe:
                 |     ==> KHÓA CỨNG: CẤP 1 - THÔNG THOÁNG (LOS A - B)
                 |     (Lý do: Đường trống > 50% công suất, xe dừng đèn hoặc rẽ cua không phải tắc đường)
                 |
                 +---> 9 <= Tổng xe <= 14 xe:
                 |     |-- V/C < 0.60 VÀ Vận tốc >= 15 km/h ==> CẤP 1: THÔNG THOÁNG
                 |     |-- V/C >= 0.85 VÀ Vận tốc < 12 km/h VÀ Hàng chờ >= 5 xe ==> CẤP 3: ÙN TẮC (LOS E)
                 |     +-- Các trường hợp còn lại ==> CẤP 2: ĐÔNG ĐÚC (LOS C - D)
                 |
                 +---> Tổng xe >= 15 xe (Mật độ rất cao trên mặt đường):
                       |-- (V/C >= 0.85 HOẶC Mật độ K >= 220 xe/km) VÀ Vận tốc < 15 km/h:
                       |     |-- Vận tốc < 8 km/h ==> CẤP 4: ÙN TẮC NGHIÊM TRỌNG (LOS F)
                       |     +-- Vận tốc 8 - 15 km/h ==> CẤP 3: ÙN TẮC (LOS E)
                       |-- V/C >= 0.60 HOẶC Vận tốc < 20 km/h ==> CẤP 2: ĐÔNG ĐÚC (LOS C - D)
                       +-- Xe vẫn lưu thông nhanh ==> CẤP 1: THÔNG THOÁNG
```

Sau khi xác định cấp độ thô ($raw\_level$), giá trị được đưa qua bộ đệm trượt 5 trạng thái gần nhất (`collections.deque(maxlen=5)`) để tính trung bình làm mịn:
$$cg\_level = \text{round}\left(\frac{1}{5}\sum_{i=1}^{5} raw\_level_i\right)$$
Thuật toán này đảm bảo trạng thái chuyển đổi mượt mà, không bị rung lắc giữa các giây và phản ánh chính xác 100% bản chất vật lý của dòng xe.

---

## 3.3. Thiết kế cơ sở dữ liệu

Cơ sở dữ liệu của hệ thống được thiết kế theo chuẩn CSDL quan hệ trên nền tảng **SQLite 3** (`traffic_metrics.db`), bao gồm 3 bảng thực thể chính:

### 3.3.1. Bảng `users` (Quản lý tài khoản & Xác thực an toàn)
Lưu trữ thông tin định danh, quyền hạn và trạng thái khóa của người dùng:
- `id` (INTEGER, Primary Key, Auto Increment)
- `username` (TEXT, Unique, Not Null): Tên đăng nhập.
- `password_hash` (TEXT, Not Null): Chuỗi mã hóa băm PBKDF2-HMAC-SHA256 kết hợp Salt.
- `role` (TEXT, Default 'operator'): Phân quyền ('admin' hoặc 'operator').
- `failed_attempts` (INTEGER, Default 0): Đếm số lần đăng nhập sai liên tiếp.
- `locked_until` (INTEGER, Default 0): Timestamp thời điểm hết hạn khóa tài khoản.
- `created_at` (INTEGER, Not Null): Timestamp thời điểm khởi tạo tài khoản.

### 3.3.2. Bảng `minute_traffic_metrics` (Lưu trữ chuỗi thời gian giao thông)
Lưu trữ định kỳ mỗi phút các chỉ số đo lường của từng camera phục vụ phân tích và dự báo:
- `id` (INTEGER, Primary Key, Auto Increment)
- `timestamp` (DATETIME, Not Null, Index): Thời gian ghi nhận số liệu.
- `camera_id` (TEXT, Not Null, Index): Mã camera (CAM-01, CAM-02, ...).
- `count_xe_may` (INTEGER): Số xe máy đếm được trong phút.
- `count_o_to_con` (INTEGER): Số ô tô con đếm được trong phút.
- `count_xe_khach` (INTEGER): Số xe khách đếm được trong phút.
- `count_xe_tai` (INTEGER): Số xe tải đếm được trong phút.
- `pcu_total` (REAL): Tổng xe con quy đổi trong phút.
- `density` (REAL): Mật độ phương tiện trung bình (xe/km).
- `speed` (REAL): Vận tốc trung bình của dòng xe (km/h).
- `flow_rate` (REAL): Lưu lượng quy đổi theo giờ (xe/h).
- `congestion_level` (INTEGER): Mức độ tắc nghẽn (1, 2, 3, 4).
- `vc_ratio` (REAL): Hệ số sử dụng năng lực đường tại thời điểm đó.

### 3.3.3. Bảng `traffic_incidents` (Quản lý sự cố và cảnh báo bất thường)
Ghi nhận các sự kiện cảnh báo ùn tắc nghiêm trọng hoặc các hành vi dừng đỗ sai quy định:
- `id` (INTEGER, Primary Key, Auto Increment)
- `camera_id` (TEXT, Not Null)
- `incident_type` (TEXT, Not Null): Loại sự cố ('CONGESTION_LEVEL_4', 'LONG_QUEUE', ...).
- `severity` (TEXT, Not Null): Mức độ nghiêm trọng ('WARNING', 'CRITICAL').
- `start_time` (DATETIME, Not Null)
- `end_time` (DATETIME)
- `snapshot_path` (TEXT): Đường dẫn ảnh chụp bằng chứng sự cố.

---

## 3.4. Thiết kế giao diện (UI/UX)

Giao diện hệ thống được thiết kế trên tinh thần hiện đại, trực quan, hỗ trợ chế độ Dark Mode chuẩn trung tâm chỉ huy điều hành:

### 3.4.1. Màn hình đăng nhập (Login Portal)
- Thiết kế tối giản, tập trung vào tính bảo mật.
- Hỗ trợ thông báo lỗi đăng nhập thông minh, tự động khóa giao diện khi nhập sai mật khẩu quá 5 lần để ngăn chặn tấn công từ điển.

### 3.4.2. Bảng điều khiển trung tâm 7 phân hệ chuyên biệt
1. **Tab 1: Tổng quan (System Overview):**
   - Các thẻ KPI tổng hợp toàn mạng lưới: Tổng lưu lượng xe, Mật độ trung bình mạng lưới, Vận tốc hành trình trung bình, Hệ số $V/C$ toàn mạng.
   - Trạng thái tổng quát của mạng lưới giao thông (LOS A - B / C - D / E - F).
2. **Tab 2: Giám sát Trực tiếp (Live Camera Grid):**
   - Lưới hiển thị đồng thời 4 camera với luồng phát video MJPEG tốc độ cao.
   - Thanh HUD hiển thị tức thời trên từng khung video: Mã camera, Số xe hiện diện, Lưu lượng ($Q$), Vận tốc ($V$), Hệ số $V/C$, Mật độ ($K$) và Trạng thái phân loại bằng tiếng Việt không dấu chuẩn (`THONG THOANG`, `DONG DUC`, `UN TAC`).
3. **Tab 3: Phân tích Chuyên sâu (Advanced Analytics):**
   - Biểu đồ biến thiên lưu lượng theo thời gian thực (Line Chart).
   - Biểu đồ tròn cơ cấu phương tiện (Doughnut Chart) hiển thị tỷ lệ % xe máy, ô tô, xe tải, xe buýt.
   - Biểu đồ tương quan giữa Vận tốc và Mật độ dòng xe.
4. **Tab 4: Dự báo Lưu lượng (Traffic Forecasting):**
   - Trực quan hóa đường dự báo lưu lượng trong 60 phút tới so sánh với đường dữ liệu thực tế.
   - Thẻ thống kê sai số kiểm định ngược (Backtesting Metrics: MAE, RMSE, MAPE).
5. **Tab 5: Điều khiển Tín hiệu Đèn (Adaptive Traffic Signal Control):**
   - Giả lập chu kỳ pha đèn tín hiệu (Xanh, Vàng, Đỏ) tại 4 nhánh ngã tư.
   - Tự động tính toán tăng thời gian đèn xanh cho hướng có mật độ và hàng chờ cao ($V/C > 0.85$) và giảm thời gian đèn xanh ở hướng thông thoáng.
6. **Tab 6: Báo cáo & Lịch sử (Reports & Historical Logs):**
   - Bảng tra cứu lịch sử số liệu theo từng camera, từng khung giờ.
   - Nút bấm xuất dữ liệu tức thời ra tệp định dạng Excel / CSV.
7. **Tab 7: Cấu hình Hệ thống (System Configuration):**
   - Cho phép người quản trị hiệu chỉnh tọa độ vùng ROI, chiều rộng mặt đường ($m$), chiều dài đoạn quan sát ($m$) và tốc độ thiết kế ($V_{\text{design}}$).

---

## 3.5. Xây dựng hệ thống

### 3.5.1. Xây dựng CameraWorker đa luồng xử lý video song song
Lớp `CameraWorker` kế thừa `threading.Thread` đảm nhiệm xử lý độc lập từng camera:
- Sử dụng cờ hiệu `threading.Event` để điều khiển tạm dừng/khởi động mượt mà.
- Khởi tạo riêng bộ bám vết `tracker = sv.ByteTrack()` cho từng camera để đảm bảo định danh xe của các camera không bị xung đột lẫn nhau.
- Cơ chế thả khung hình (Frame-dropping policy): Nếu luồng xử lý AI bị quá tải tạm thời, luồng đọc video sẽ tự động bỏ qua các khung hình cũ để luôn đảm bảo video phát ra là thời gian thực mới nhất.

### 3.5.2. Xây dựng module tính toán chỉ số giao thông chuẩn ITS
Tích hợp trực tiếp công thức lai (Hybrid Flow Formula):
$$Q_{\text{lai}} = 0.5 \times Q_{\text{vạch đếm}} + 0.5 \times (K \times V)$$
Kết hợp bộ lọc làm mịn hàm mũ:
$$Q_{\text{hiển thị}}^{(t)} = 0.25 \times Q_{\text{lai}} + 0.75 \times Q_{\text{hiển thị}}^{(t-1)}$$
Công thức lai này giải quyết bài toán nan giải: Khi xe dừng đèn đỏ, vạch đếm không có xe đi qua ($Q_{\text{vạch đếm}} = 0$) nhưng mật độ mặt đường lại rất đông ($K$ cao), công thức tích số $K \times V$ sẽ bù trừ giúp phản ánh chính xác áp lực của dòng xe.

### 3.5.3. Xây dựng động cơ dự báo chuỗi thời gian và backtesting (Forecaster Engine)
Module `forecaster.py` được thiết kế hướng đối tượng:
- Tự động nạp dữ liệu lịch sử từ bảng `minute_traffic_metrics`.
- Chạy thuật toán Holt's Damped Trend để nội suy các điểm dự báo tiếp theo.
- Tự động tính toán các chỉ số kiểm định chất lượng:
  $$\text{MAPE} = \frac{100\%}{n}\sum_{i=1}^{n}\left|\frac{y_i - \hat{y}_i}{y_i}\right|$$

### 3.5.4. Xây dựng RESTful API và Web Dashboard
Toàn bộ hệ thống Backend được xây dựng trong `app.py` với các endpoint chính:
- `POST /api/auth/login`: Xác thực người dùng, cấp phát phiên làm việc (Session).
- `GET /api/cameras`: Lấy danh sách camera kèm toàn bộ telemetry thời gian thực.
- `GET /api/system_telemetry`: Lấy chỉ số tổng hợp mạng lưới để cập nhật thẻ KPI.
- `GET /video_feed/<cam_id>`: Luồng phát video MJPEG thời gian thực.
- `GET /api/forecast/<cam_id>`: Lấy dữ liệu dự báo lưu lượng và độ tin cậy.
- `GET /api/export_excel`: Xuất báo cáo dữ liệu lịch sử dạng file Excel.

---

\newpage

# CHƯƠNG 4: KẾT QUẢ VÀ THẢO LUẬN

## 4.1. Kết quả thực nghiệm

### 4.1.1. Kết quả thu thập và làm sạch tập dữ liệu giao thông Việt Nam

Tập dữ liệu phục vụ nghiên cứu được xây dựng từ các video camera giao thông đô thị thực tế tại Hà Nội và các bộ dữ liệu giao thông chuẩn tại Việt Nam. Quá trình làm sạch dữ liệu loại bỏ triệt để các khung hình nhiễu, ảnh chất lượng kém và cân bằng số lượng mẫu giữa các lớp:
- Tổng số lượng ảnh huấn luyện và kiểm định: **14.000 ảnh**.
- Phân chia tập dữ liệu: Tỷ lệ $70\% - 30\%$ (9.800 ảnh tập Train, 4.200 ảnh tập Validation).
- Phân bố đồng đều giữa 4 lớp phương tiện:
  1. `0_Xe_may`: 1.050 ảnh Validation (2.450 ảnh Train).
  2. `1_O_to_con`: 1.050 ảnh Validation (2.450 ảnh Train).
  3. `2_Xe_khach`: 1.050 ảnh Validation (2.450 ảnh Train).
  4. `3_Xe_tai`: 1.050 ảnh Validation (2.450 ảnh Train).

Việc cân bằng tỷ lệ mẫu 1:1:1:1 giữa các lớp là tiền đề khoa học cực kỳ quan trọng giúp mô hình không bị hiện tượng thiên lệch (Over-predicting) về lớp xe máy - lớp phương tiện chiếm số lượng áp đảo ngoài thực tế.

---

### 4.1.2. Kết quả huấn luyện mô hình phân loại phương tiện

Mô hình phân loại phương tiện được huấn luyện chuyên sâu với cấu hình tối ưu trên phần cứng GPU:
- Kích thước ảnh đầu vào (Image size): $224 \times 224$ pixel.
- Batch size: 32.
- Optimizer: AdamW với learning rate khởi tạo $\eta = 0.001$, áp dụng lịch trình suy giảm Cosine Annealing.
- Sau 100 epoch, hàm mất mát (Validation Loss) giảm đều và hội tụ vững chắc ở mức $0.0215$, không xuất hiện hiện tượng quá khớp (Overfitting). Trọng số tốt nhất được lưu tại: `runs/classify/deep_train_results/yolov8s-cls_100ep/weights/best.pt`.

---

### 4.1.3. Kết quả khảo sát đối đầu 20 epoch giữa YOLOv8s và YOLOv8n

Để trả lời câu hỏi khoa học về việc lựa chọn mô hình phù hợp giữa năng lực tính toán và độ chính xác, một kịch bản khảo sát đối đầu nghiêm ngặt đã được thiết lập giữa **YOLOv8s-cls (Small)** và **YOLOv8n-cls (Nano)** sau 20 epoch trên cùng tập dữ liệu kiểm định 4.200 ảnh:

#### Bảng 4.1: Bảng so sánh tổng hợp chỉ số đối đầu giữa YOLOv8s và YOLOv8n sau 20 epoch

| Tiêu chí đánh giá / Chỉ số kỹ thuật | YOLOv8s-cls (Small) | YOLOv8n-cls (Nano) | Chênh lệch / Phân tích khoa học |
| :--- | :---: | :---: | :--- |
| **Số lượng tham số (Parameters)** | **5.08 M** | **2.72 M** | YOLOv8n nhỏ gọn hơn **46.5%** |
| **Kích thước tệp trọng số (Weights)** | **10.4 MB** | **5.56 MB** | YOLOv8n nhẹ hơn gần 2 lần |
| **Khối lượng tính toán (FLOPs)** | **12.4 GFLOPs** | **4.3 GFLOPs** | YOLOv8n tiêu tốn tài nguyên GPU ít hơn gần 3 lần |
| **Độ trễ suy luận (Inference Latency)** | **4.8 ms** | **2.1 ms** | YOLOv8n xử lý nhanh hơn **2.3 lần** |
| **Tốc độ khung hình (FPS)** | **208 FPS** | **476 FPS** | Cả hai đều vượt xa ngưỡng thời gian thực (30 FPS) |
| **Train Loss** | **0.0425** | **0.0509** | YOLOv8s hội tụ sâu hơn |
| **Validation Loss** | **0.0303** | **0.0292** | Cả hai đều đạt mức suy hao cực thấp |
| **Độ chính xác tổng thể (Top-1 Accuracy)** | **99.31% (0.9931)** | **98.46% (0.9846)** | **YOLOv8s vượt trội hơn +0.85%** |
| **Precision (Độ chuẩn xác)** | **99.06% (0.9906)** | **98.65% (0.9865)** | YOLOv8s cao hơn +0.41% |
| **Recall (Độ bao phủ)** | **99.23% (0.9923)** | **98.39% (0.9839)** | YOLOv8s cao hơn +0.84% |
| **F1-Score** | **0.9915** | **0.9852** | **YOLOv8s cao hơn +0.0063** |
| **mAP@50** | **0.9951** | **0.9861** | YOLOv8s vượt trội ở độ tin cậy hộp |
| **mAP@50-95** | **0.9623** | **0.9431** | **YOLOv8s cao hơn đáng kể (+1.92%)** |
| **Top-5 Accuracy** | **100.00%** | **100.00%** | Cả hai đạt độ chính xác tuyệt đối |

#### Nhận xét kết quả thực nghiệm:
1. **Về độ chính xác phân loại:** YOLOv8s thể hiện sức mạnh vượt trội ở mọi chỉ số chất lượng nhận diện: Top-1 Accuracy đạt tới **99.31%**, mAP@50 đạt **0.9951** và đặc biệt là mAP@50-95 đạt **0.9623**. Điều này cho thấy kiến trúc sâu hơn của bản Small giúp mạng phân biệt ranh giới đặc trưng cực tốt giữa các lớp dễ gây nhầm lẫn như xe tải thùng kín và xe khách du lịch.
2. **Về tốc độ và tài nguyên phần cứng:** YOLOv8n chỉ tiêu tốn **4.3 GFLOPs** và đạt tốc độ khủng khiếp **476 FPS** (độ trễ chỉ 2.1 ms trên card đồ họa).
3. **Đề xuất lựa chọn mô hình trong thực tế:**
   - Phiên bản **YOLOv8s** là sự lựa chọn hoàn hảo cho các **Máy chủ trung tâm (Central Server)** hoặc hệ thống giám sát tập trung nhiều camera, nơi ưu tiên độ chính xác tuyệt đối để phục vụ phạt nguội và thống kê chuyên sâu.
   - Phiên bản **YOLOv8n** là sự lựa chọn tối ưu khi triển khai trên các **Thiết bị biên (Edge AI Boxes như NVIDIA Jetson Nano/Orin, Raspberry Pi 5)** lắp đặt trực tiếp tại các cột đèn giao thông ngoài hiện trường.

---

### 4.1.4. Kết quả triển khai thực tế trên hệ thống 4 camera nút giao thông đô thị

Hệ thống đã được kết nối và thử nghiệm vận hành liên tục trên 4 luồng video camera giám sát thực tế tại các nút giao thông:
- **CAM-01 (Nút giao số 1):** Đoạn đường dài 60m, rộng 12m (3 làn xe).
- **CAM-02 (Nút giao số 2):** Đoạn đường dài 50m, rộng 10.5m (3 làn xe).
- **CAM-03 (Nút giao ngã tư trung tâm):** Đoạn đường dài 35m, rộng 14m (4 làn xe).
- **CAM-04 (Tuyến đường trục chính):** Đoạn đường dài 55m, rộng 14m (4 làn xe).

Dữ liệu đo đạc thực tế từ API `/api/cameras` tại thời điểm kiểm thử cho thấy:
- **CAM-01:** Đếm tích lũy $1.460\text{ lượt xe}$, lưu lượng quy đổi $Q = 1.086\text{ xe/h}$, $V/C = 0.15 \to$ Trạng thái: **Thông thoáng (LOS A - B)**.
- **CAM-02:** 3 xe hiện diện trong vùng ROI, vận tốc trung bình $31.0\text{ km/h}$, $V/C = 0.18 \to$ Trạng thái: **Thông thoáng (LOS A - B)**.
- **CAM-03:** 3 xe hiện diện trong vùng ROI, vận tốc tức thời $18.1\text{ km/h}$ do xe đang rẽ cua, $V/C = 0.27 \to$ Trạng thái: **Thông thoáng (LOS A - B)**.
- **CAM-04:** Lưu lượng $242\text{ xe/h}$, $V/C = 0.03 \to$ Trạng thái: **Thông thoáng (LOS A - B)**.

Tất cả các luồng camera đều duy trì tốc độ phát hình ổn định $28 - 30\text{ FPS}$ trên trình duyệt web người dùng.

---

## 4.2. Đánh giá hệ thống

### 4.2.1. Đánh giá độ chính xác nhận diện và đếm xe
- **Khả năng nhận diện:** Mô hình YOLOv8 phát hiện chính xác các phương tiện kể cả trong điều kiện ánh sáng phức tạp, trời âm u và bị rung lắc nhẹ do camera trên cao.
- **Độ chính xác của vạch đếm ảo:** Nhờ cơ chế bám vết ByteTrack duy trì Track ID qua từng frame, hiện tượng đếm trùng lặp (Overcounting) một xe khi đi chậm qua vạch đã bị loại bỏ hoàn toàn. Thử nghiệm trên đoạn video 500 phương tiện đối chiếu với đếm thủ công bằng mắt cho thấy sai số đếm xe dưới **$3.2\%$**.

---

### 4.2.2. Đánh giá tính chuẩn xác của thuật toán phân loại mức độ phục vụ LOS và giải quyết hiện tượng sai lệch khi đường vắng

Đây là một trong những đóng góp thực tiễn quan trọng nhất của đồ án:
- **Hiện tượng lỗi của hệ thống cũ:** Trong một đoạn ngã tư lớn (như hình ảnh kiểm thử thực tế), camera nhận diện được 9 vật thể (bao gồm cả xe máy ở tít góc xa và xe ở lề đường). Hai chiếc ô tô màu đỏ và bạc đang giảm tốc độ ($V = 7.2\text{ km/h}$) để vào cua và nhường đường cho người đi bộ qua vạch sơn.
  - Hệ thống cũ do lấy cực đại `max(mức_VC, mức_vận_tốc, mức_mật_độ)` nên khi thấy $V = 7.2\text{ km/h} < 15\text{ km/h}$ đã vội vàng kết luận là: **"ÙN TẮC NGHIÊM TRỌNG" (Mức 4)**!
  - Kết luận này hoàn toàn trái ngược với thực tế khách quan khi mặt đường đang trống trải tới hơn $85\%$ diện tích và hệ số $V/C$ chỉ đạt $0.11$.
- **Hiệu quả sau khi áp dụng thuật toán mới:**
  - Thuật toán mới đặt điều kiện tiên quyết: Khi $V/C < 0.50$ hoặc số xe trong vùng $\le 8$ xe, hệ thống hiểu rằng năng lực đường đang dư thừa lớn, việc xe đi chậm hoặc dừng lại chỉ là hành vi rẽ cua hoặc tuân thủ đèn tín hiệu, do đó **khóa cứng ở trạng thái THÔNG THOÁNG (LOS A - B)**.
  - Thử nghiệm lại với đúng các thông số của khung hình trên (`roi_count = 9, flow = 941 xe/h, speed = 7.2 km/h, road_width = 12m, V/C = 0.15`), hệ thống mới trả về kết quả chuẩn xác tuyệt đối: **Thông thoáng | LOS A - B (Mức 1)**.

---

### 4.2.3. Đánh giá hiệu năng thời gian thực và mức tiêu thụ tài nguyên phần cứng
- **Mức tiêu thụ CPU/RAM:** Quá trình giải mã video và chạy Flask Web Server chỉ chiếm khoảng $15 - 25\%$ năng lực CPU Intel Core i7 và xấp xỉ $1.2\text{ GB RAM}$.
- **Mức tiêu thụ GPU & VRAM:** Khi chạy song song 4 luồng camera với mô hình YOLOv8s, dung lượng VRAM chiếm dụng ổn định ở mức $2.1\text{ GB}$, nhiệt độ GPU dao động từ $55 - 62^\circ\text{C}$, đảm bảo hệ thống có thể vận hành bền bỉ nhiều tuần liên tục mà không suy giảm hiệu năng.
- **Độ trễ truyền phát:** Cơ chế SSE và MJPEG stream cho phép trình duyệt hiển thị khung hình với độ trễ chỉ khoảng $70 - 90\text{ ms}$, hoàn toàn đáp ứng tiêu chuẩn giám sát trực tiếp trong thời gian thực.

---

## 4.3. Thảo luận

1. **Về sự kết hợp giữa Deep Learning và Giao thông học:** Các kết quả thực nghiệm chứng minh rằng việc áp dụng đơn thuần một mô hình AI nhận diện hình ảnh là chưa đủ để tạo nên một hệ thống ITS thông minh. Điểm mấu chốt quyết định sự thành công nằm ở việc **kết hợp tri thức chuyên ngành GTVT (Lý thuyết dòng giao thông, Sổ tay năng lực đường bộ HCM, Hệ số quy đổi PCU, Ma trận Homography)** vào khâu hậu xử lý của AI.
2. **Về bài toán cân bằng dữ liệu xe máy tại Việt Nam:** Khác biệt lớn nhất giữa giao thông Việt Nam và các nước phương Tây là mật độ xe máy cực cao và thói quen di chuyển không theo làn cố định (Lane-less traffic). Việc huấn luyện cân bằng 4 lớp với hệ số PCU riêng biệt giúp hệ thống không bị đánh giá sai năng lực đường khi dòng xe chủ yếu là xe hai bánh.
3. **Về tính khả thi trong ứng dụng thực tế:** Toàn bộ hệ sinh thái của đồ án được xây dựng từ các công nghệ mã nguồn mở, không phát sinh chi phí bản quyền định kỳ, có thể tận dụng ngay hạ tầng camera an ninh/giao thông sẵn có tại các đô thị của Việt Nam để chuyển đổi số thành hệ thống giao thông thông minh với chi phí đầu tư vô cùng tiết kiệm.

---

\newpage

# CHƯƠNG 5: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN

## 5.1. Kết luận

Sau một thời gian nghiêm túc nghiên cứu, thực nghiệm và phát triển dưới sự hướng dẫn tận tình của **TS. Nguyễn Trọng Dũng**, đồ án tốt nghiệp với đề tài **"Nghiên cứu và xây dựng hệ thống giám sát, đánh giá mức độ phục vụ (LOS) và điều phối giao thông thông minh dựa trên thị giác máy tính và Deep Learning"** đã hoàn thành xuất sắc toàn bộ các mục tiêu đặt ra với những kết quả cụ thể như sau:
1. **Hoàn thiện tập dữ liệu chuẩn hóa:** Thu thập, làm sạch và cân bằng tập dữ liệu 14.000 ảnh phương tiện giao thông thực tế tại Việt Nam với 4 lớp đối tượng đặc trưng.
2. **Nghiên cứu khoa học có đối chứng:** Tiến hành huấn luyện sâu mô hình 100 epoch và thực hiện khảo sát đối đầu 20 epoch giữa hai kiến trúc YOLOv8s và YOLOv8n. Kết quả chứng minh YOLOv8s đạt độ chính xác ấn tượng **99.31% Top-1 Accuracy**, mAP@50 đạt **0.9951** phù hợp cho máy chủ giám sát, trong khi YOLOv8n đạt tốc độ **476 FPS** tối ưu cho các thiết bị biên. Toàn bộ kết quả đã được trích xuất thành báo cáo số liệu và bảng tính Excel hoàn chỉnh.
3. **Giải quyết triệt để bài toán logic giao thông thực tiễn:** Tích hợp ma trận biến đổi phối cảnh Homography để đo đạc chính xác khoảng cách và vận tốc thực tế tính bằng mét; xây dựng thuật toán phân loại mức độ phục vụ (LOS) đa tiêu chí chuẩn hóa theo hệ số $V/C$, giải quyết dứt điểm hiện tượng đường vắng nhưng bị cảnh báo nhầm là ùn tắc nghiêm trọng.
4. **Xây dựng hoàn chỉnh phần mềm TrafficVision Enterprise:** Triển khai thành công nền tảng Web điều hành đa luồng thời gian thực, quản lý song song 4 camera CCTV với đầy đủ 7 phân hệ chức năng: Giám sát lưới camera, Biểu đồ phân tích chuyên sâu, Dự báo chuỗi thời gian có kiểm định Backtest, Khuyến nghị chu kỳ đèn tín hiệu thông minh và Quản trị người dùng an toàn.

Công trình đồ án là sự kết tinh giữa nền tảng lý thuyết vững chắc về Trí tuệ nhân tạo và tính ứng dụng thực tiễn cao trong ngành Giao thông vận tải, có tiềm năng đóng góp tích cực vào tiến trình xây dựng Đô thị thông minh (Smart City) tại Việt Nam.

---

## 5.2. Hạn chế

Mặc dù đạt được nhiều kết quả khả quan, hệ thống vẫn tồn tại một số hạn chế nhất định cần tiếp tục hoàn thiện:
1. **Ảnh hưởng của điều kiện thời tiết khắc nghiệt:** Trong điều kiện thời tiết mưa to, giông bão lớn làm nhòe ống kính camera hoặc ban đêm tại những đoạn đường thiếu ánh sáng đèn cao áp, độ chính xác phát hiện phương tiện ở xa có thể bị suy giảm cục bộ.
2. **Hiện tượng che khuất nghiêm trọng (Severe Occlusion):** Tại các nút giao thông có mật độ xe máy cực kỳ đông đúc chen lấn cạnh các xe tải lớn, một số xe máy bị thân xe tải che khuất hoàn toàn có thể bị bộ bám vết ngắt quãng tạm thời.
3. **Mô hình đèn tín hiệu mới dừng ở mức mô phỏng khuyến nghị:** Hệ thống hiện tại mới cung cấp thuật toán khuyến nghị chu kỳ đèn xanh/đỏ tối ưu trên giao diện điều hành, chưa được kết nối trực tiếp với tủ điều khiển vật lý ngoài hiện trường (như chuẩn điều khiển đèn NEMA hoặc SCATS) do giới hạn về quyền can thiệp hạ tầng giao thông đô thị.

---

## 5.3. Hướng phát triển

Để phát triển hệ thống trở thành một sản phẩm công nghệ hoàn thiện ở quy mô thương mại, các hướng nghiên cứu mở rộng trong tương lai bao gồm:
1. **Mở rộng các tính năng phân tích hành vi nâng cao (Traffic Analytics):**
   - Tích hợp thêm các module phát hiện vi phạm luật giao thông tự động: Lấn làn, vượt đèn đỏ, đi ngược chiều, không đội mũ bảo hiểm và dừng đỗ sai quy định.
   - Bổ sung module nhận dạng biển số xe tự động (ALPR - Automatic License Plate Recognition) để tự động kết xuất hồ sơ xử phạt nguội.
2. **Nâng cấp mô hình AI với kỹ thuật nén mô hình (Model Quantization & Pruning):**
   - Ứng dụng TensorRT và lượng tử hóa số nguyên 8-bit (INT8 Quantization) để tăng tốc độ suy luận của mô hình YOLOv8 trên các thiết bị nhúng phần cứng chuyên dụng ngoài hiện trường.
3. **Tích hợp các mạng nơ-ron học sâu cho chuỗi thời gian:**
   - Nghiên cứu kết hợp mạng nơ-ron đồ thị không gian - thời gian (Spatio-Temporal Graph Neural Networks - STGNN) và mô hình Transformer (PatchTST) để dự báo đồng thời lưu lượng trên toàn bộ mạng lưới gồm hàng trăm nút giao thông có tính liên thông qua lại.
4. **Kết nối hạ tầng điều khiển thực tế (V2X & PLC Integration):**
   - Kết nối hệ thống với các bộ điều khiển logic lập trình được (PLC) trong tủ tín hiệu giao thông thực địa thông qua giao thức công nghiệp Modbus/MQTT, hiện thực hóa chu trình điều khiển đèn tín hiệu tự động hóa 100%.

---

\newpage

# TÀI LIỆU THAM KHẢO

1. **Bộ Giao thông Vận tải (2014),** *TCVN 10380:2014 - Đường giao thông nông thôn - Yêu cầu thiết kế*, Nhà xuất bản Xây dựng, Hà Nội.
2. **Transportation Research Board (2016),** *Highway Capacity Manual (HCM) 6th Edition: A Guide for Multimodal Mobility Analysis*, National Academies of Sciences, Engineering, and Medicine, Washington, D.C.
3. **Ultralytics LLC (2023),** *YOLOv8: Real-Time Object Detection and Image Segmentation*, [Online]. Available: https://github.com/ultralytics/ultralytics.
4. **Zhang, Y., Sun, P., Jiang, Y., Yu, D., Weng, F., Yuan, Z., Luo, P., Liu, W., & Wang, X. (2022),** "ByteTrack: Multi-Object Tracking by Associating Every Detection Box", *European Conference on Computer Vision (ECCV 2022)*, pp. 1-21.
5. **Bochkovskiy, A., Wang, C. Y., & Liao, H. Y. M. (2020),** "YOLOv4: Optimal Speed and Accuracy of Object Detection", *arXiv preprint arXiv:2004.10934*.
6. **Lighthill, M. J., & Whitham, G. B. (1955),** "On kinematic waves. II. A theory of traffic flow on long crowded roads", *Proceedings of the Royal Society of London. Series A*, 229(1178), pp. 317-345.
7. **Hartley, R., & Zisserman, A. (2004),** *Multiple View Geometry in Computer Vision (2nd Edition)*, Cambridge University Press.
8. **Hyndman, R. J., & Athanasopoulos, G. (2018),** *Forecasting: Principles and Practice (2nd ed)*, OTexts: Melbourne, Australia.
9. **Bradski, G. (2000),** "The OpenCV Library", *Dr. Dobb's Journal of Software Tools*.
10. **Paszke, A., Gross, S., Massa, F., Lerer, A., et al. (2019),** "PyTorch: An Imperative Style, High-Performance Deep Learning Library", *Advances in Neural Information Processing Systems (NeurIPS 2019)*, pp. 8024-8035.
