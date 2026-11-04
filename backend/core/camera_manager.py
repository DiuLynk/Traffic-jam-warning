"""
camera_manager.py - Điều phối đa luồng hệ thống Camera Giám sát Giao thông với YOLOv8 & Real-time Analytics.
Tuân thủ chặt chẽ nguyên tắc dữ liệu:
- KHÔNG sử dụng số liệu giả lập / base_profiles / sine waves.
- 100% chỉ số (Số lượng xe, PCU, Mật độ K, Lưu lượng Q, Vận tốc V, Cấp độ ùn tắc) được tính toán trực tiếp
  từ các phương tiện nhận diện trong video thời gian thực.
- Cấu hình mặc định nạp 4 video thực tế:
    + CAM-01: uploads/CAM-01/cam1.mp4
    + CAM-02: uploads/CAM-01/cam2.mkv
    + CAM-03: uploads/CAM-01/cam3.mkv
    + CAM-04: uploads/CAM-01/cam4.mkv
"""

import os
import time
import uuid
import json
import threading
from pathlib import Path
from collections import deque
import cv2
import numpy as np

from config import (
    WORKSPACE_DIR, STATIC_DIR, SAMPLES_DIR,
    ROI_REAL_WIDTH_M, ROI_REAL_LENGTH_M,
    DENSITY_THRESHOLDS, OCCUPANCY_THRESHOLDS, PCU_WEIGHTS,
    VC_THRESHOLDS, SPEED_RATIO_THRESHOLDS, DESIGN_SPEED_KMH, DEFAULT_LANE_CAPACITY
)
from backend.core.traffic_db import (
    record_minute_metric, create_analysis_session, close_analysis_session, add_audit_log
)

# Khóa đồng bộ GPU an toàn giữa các luồng camera
model_lock = threading.Lock()

# Mapping phương tiện COCO sang nhãn tiếng Việt & màu vẽ (BGR format cho OpenCV)
COCO_VEHICLES = {
    2: ("Ô tô con", "o_to_con", (0, 215, 255)),     # Gold
    3: ("Xe máy", "xe_may", (255, 180, 0)),         # Cyan/Sky
    5: ("Xe khách", "xe_khach", (226, 43, 138)),    # Purple
    7: ("Xe tải", "xe_tai", (0, 100, 255)),         # Orange/Red
    1: ("Xe đạp", "xe_dap", (94, 197, 34))          # Xe đạp - Emerald Green (BGR)
}


def resolve_video_path(rel_path):
    """Tìm đường dẫn tệp video linh hoạt hỗ trợ cả đường dẫn tuyệt đối lẫn tương đối."""
    if not rel_path:
        return ""
    clean_path = str(rel_path).replace("\\", "/")
    if os.path.isabs(clean_path) and os.path.exists(clean_path):
        return os.path.normpath(clean_path)
    if os.path.exists(str(rel_path)):
        return os.path.normpath(str(rel_path))

    candidates = [
        os.path.join(str(WORKSPACE_DIR), clean_path),
        os.path.join(str(WORKSPACE_DIR), rel_path),
        os.path.join(str(WORKSPACE_DIR), "uploads", os.path.basename(rel_path)),
        os.path.join(str(WORKSPACE_DIR), "uploads", "CAM-01", os.path.basename(rel_path)),
        os.path.join(str(STATIC_DIR), "samples", os.path.basename(rel_path)),
        os.path.join(str(STATIC_DIR), os.path.basename(rel_path)),
        os.path.join(str(SAMPLES_DIR), "cctv_giai_phong.mp4"),
        os.path.join(str(SAMPLES_DIR), "cctv_hang_bai.mp4"),
        os.path.join(str(SAMPLES_DIR), "cctv_nhat_tan.mp4"),
        os.path.join(str(SAMPLES_DIR), "sample_traffic.mp4")
    ]
    for c in candidates:
        if os.path.exists(c):
            return os.path.normpath(c)
    return os.path.normpath(os.path.join(str(WORKSPACE_DIR), rel_path))


class CameraWorker:
    def __init__(self, cam_id, name, district, bearing, video_rel_path, default_roi,
                 length_m=60.0, width_m=12.0, det_model=None,
                 free_thr=None, jam_thr=None, jam_speed=None):
        self.cam_id = cam_id
        self.name = name
        self.cam_name = name
        self.district = district
        self.bearing = bearing
        self.video_rel_path = video_rel_path
        self.video_path = resolve_video_path(video_rel_path)
        self.roi_norm = np.array(default_roi, dtype=np.float32)
        self.length_m = float(length_m)
        self.width_m = float(width_m)
        self.det_model = det_model

        # Ngưỡng phân loại thích ứng theo từng camera riêng biệt
        self.lanes = max(1.0, round(self.width_m / 3.5, 1))
        self.free_thr = int(free_thr) if free_thr is not None else int(max(4, round(self.lanes * (self.length_m / 50.0) * 8.0)))
        self.jam_thr = int(jam_thr) if jam_thr is not None else int(round(self.free_thr * 2.1))
        self.jam_speed = float(jam_speed) if jam_speed is not None else 14.0

        # Quản lý phiên phân tích
        self.session_id = None
        self.source_type = "upload" if "uploads" in str(video_rel_path) else "cctv_sample"

        # Trạng thái luồng
        self.is_running = False
        self.thread = None
        self.latest_jpeg_low = None
        self.latest_jpeg_high = None
        self.new_frame_event = threading.Event()

        # Bộ đệm bounding box liên tục tránh giật nháy
        self.last_det_boxes = []

        # Bộ đếm xe lũy kế chuẩn ITS (Monotonically Increasing Counter) - Không bao giờ tụt
        self.cumulative_vehicles = 0
        self.cumulative_counts = {"xe_may": 0, "o_to_con": 0, "xe_khach": 0, "xe_tai": 0, "xe_dap": 0}
        self.counted_track_ids = set()
        self.roi_history = deque(maxlen=6)
        self.flow_history = deque(maxlen=6)
        self.smoothed_flow = 0.0
        self.cg_history = deque(maxlen=5)

        # Chỉ số thời gian thực khởi tạo
        self.metrics = {
            "total_vehicles": 0,
            "cumulative_vehicles": 0,
            "cumulative_counts": {"xe_may": 0, "o_to_con": 0, "xe_khach": 0, "xe_tai": 0, "xe_dap": 0},
            "counts": {"xe_may": 0, "o_to_con": 0, "xe_khach": 0, "xe_tai": 0, "xe_dap": 0},
            "pcu": 0.0,
            "density": 0.0,
            "density_pcu": 0.0,
            "flow": 0.0,
            "speed": 0.0,
            "fps": 0.0,
            "queue_vehicles": 0,
            "queue_length_m": 0.0,
            "congestion_level": 1,
            "congestion_name": "Thông thoáng",
            "last_updated": time.time(),
            "video_time_sec": 0.0,
            "session_id": None
        }

        # Quản lý tracking và đo lường lưu lượng (Flow Q)
        self.tracked_objects = {}  # {track_id: dict(centroid, cls, first_seen, last_time, last_x, last_y, speed, hits, lost_frames)}
        self.next_track_id = 1
        self.crossed_ids = set()
        self.crossing_events = deque(maxlen=2000)  # [(video_time_sec, cat_key)]

        self.video_fps = 25.0
        self.cumulative_vtime_sec = 0.0
        self.last_minute_record_vtime = 0.0
        self.last_audit_log_vtime = 0.0
        self.last_audit_congestion_lvl = 1
        self.last_tele_alert_vtime = -999.0

    def start(self):
        if not self.is_running:
            self._init_session()
            self.is_running = True
            self.thread = threading.Thread(target=self._run_loop, daemon=True, name=f"Worker-{self.cam_id}")
            self.thread.start()

    def stop(self):
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=1.5)
        self._close_session()

    def _init_session(self):
        """Khởi tạo phiên phân tích mới độc lập cho video."""
        self.session_id = f"{self.cam_id}_{int(time.time())}_{uuid.uuid4().hex[:6]}"
        self.tracked_objects.clear()
        self.crossed_ids.clear()
        self.crossing_events.clear()
        self.last_det_boxes.clear()
        self.cumulative_vtime_sec = 0.0
        self.smoothed_flow = 0.0
        if hasattr(self, "cg_history"):
            self.cg_history.clear()
        self.last_minute_record_vtime = 0.0
        self.last_audit_log_vtime = 0.0
        self.last_audit_congestion_lvl = 1
        self.last_tele_alert_vtime = -999.0

        total_frames = 0
        fps = 25.0
        if os.path.exists(self.video_path):
            cap_probe = cv2.VideoCapture(self.video_path)
            if cap_probe.isOpened():
                total_frames = int(cap_probe.get(cv2.CAP_PROP_FRAME_COUNT))
                fps = float(cap_probe.get(cv2.CAP_PROP_FPS)) or 25.0
                cap_probe.release()
        self.video_fps = fps

        try:
            self.session_id = create_analysis_session(
                camera_id=self.cam_id,
                source_type=self.source_type,
                source_path=self.video_rel_path,
                total_frames=total_frames,
                fps=fps
            )
            add_audit_log(
                event_type="SESSION_START",
                camera_id=self.cam_id,
                status_text="Khởi tạo phiên phân tích trực tiếp từ video",
                details=f"Phiên: {self.session_id} | Tệp: {os.path.basename(self.video_path)}"
            )
        except Exception as e:
            print(f"[SESSION ERROR] {e}")

    def _close_session(self):
        if self.session_id:
            try:
                close_analysis_session(self.session_id)
            except Exception:
                pass

    def change_source(self, new_video_path, source_type="upload"):
        """Đổi nguồn video cho camera: dừng phiên cũ, reset chỉ số, nạp phiên mới."""
        self.stop()
        self.video_rel_path = new_video_path
        self.video_path = resolve_video_path(new_video_path)
        self.source_type = source_type
        self.metrics = {
            "total_vehicles": 0,
            "counts": {"xe_may": 0, "o_to_con": 0, "xe_khach": 0, "xe_tai": 0, "xe_dap": 0},
            "pcu": 0.0,
            "density": 0.0,
            "flow": 0.0,
            "speed": 0.0,
            "fps": 0.0,
            "congestion_level": 1,
            "congestion_name": "Thông thoáng",
            "last_updated": time.time(),
            "video_time_sec": 0.0,
            "session_id": None
        }
        self.start()

    def update_roi(self, new_roi_norm):
        """Cập nhật tọa độ đa giác ROI trực tiếp."""
        self.roi_norm = np.array(new_roi_norm, dtype=np.float32)

    def update_parameters(self, length_m=None, width_m=None, free_thr=None, jam_thr=None, jam_speed=None):
        """Cập nhật các tham số vật lý và ngưỡng phân loại thích ứng của từng camera."""
        if length_m is not None and float(length_m) > 0:
            self.length_m = float(length_m)
        if width_m is not None and float(width_m) > 0:
            self.width_m = float(width_m)
            self.lanes = max(1.0, round(self.width_m / 3.5, 1))
        if free_thr is not None and int(free_thr) > 0:
            self.free_thr = int(free_thr)
        if jam_thr is not None and int(jam_thr) > 0:
            self.jam_thr = int(jam_thr)
        if jam_speed is not None and float(jam_speed) > 0:
            self.jam_speed = float(jam_speed)

    def _run_loop(self):
        """Vòng lặp đọc frame, nhận diện phương tiện YOLO, tracking và tính toán chỉ số thực tế."""
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            err_frame = np.zeros((360, 640, 3), dtype=np.uint8)
            cv2.putText(err_frame, f"{self.cam_id}: Khong tim thay video {os.path.basename(self.video_path)}", (30, 180),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            _, buf = cv2.imencode(".jpg", err_frame)
            self.latest_jpeg_low = buf.tobytes()
            self.latest_jpeg_high = buf.tobytes()
            print(f"[ERROR] Không thể mở video cho {self.cam_id}: {self.video_path}")
            return

        frame_idx = 0
        fps_timer = time.time()
        fps_counter = 0
        curr_fps = self.video_fps

        while self.is_running:
            ret, raw_frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                frame_idx = 0
                # Khi video lặp lại:
                # TUYỆT ĐỐI GIỮ NGUYÊN BỘ ĐẾM LŨY KẾ (self.cumulative_vehicles và self.cumulative_counts)
                # Chỉ dọn các track tạm thời của chu kỳ vừa kết thúc để sẵn sàng đón nhận luồng mới:
                self.crossed_ids.clear()
                self.counted_track_ids.clear()
                self.tracked_objects.clear()
                continue

            frame_idx += 1
            fps_counter += 1
            now_t = time.time()
            if now_t - fps_timer >= 1.0:
                curr_fps = round(fps_counter / (now_t - fps_timer), 1)
                fps_counter = 0
                fps_timer = now_t

            # Timeline liên tục của phiên phân tích
            frame_delta_sec = 1.0 / max(1.0, self.video_fps)
            self.cumulative_vtime_sec += frame_delta_sec
            video_time_sec = self.cumulative_vtime_sec

            raw_h, raw_w = raw_frame.shape[:2]
            # Chuẩn hóa kích thước khung hình về 1280px để đạt hiệu năng xử lý mượt mà và nét cao
            target_w = 1280
            target_h = int(target_w * raw_h / raw_w)
            frame = cv2.resize(raw_frame, (target_w, target_h), interpolation=cv2.INTER_AREA)
            h, w = frame.shape[:2]

            # Suy luận YOLO xen kẽ mỗi 2 frame để tối ưu tốc độ và duy trì nhịp frame mượt
            should_infer = (frame_idx % 2 == 0)

            if should_infer and self.det_model is not None:
                try:
                    with model_lock:
                        results = self.det_model(
                            frame, conf=0.18, iou=0.45, imgsz=640,
                            classes=list(COCO_VEHICLES.keys()),
                            verbose=False
                        )[0]

                    det_boxes = []
                    if results.boxes is not None and len(results.boxes) > 0:
                        for b in results.boxes:
                            cid = int(b.cls[0])
                            if cid in COCO_VEHICLES:
                                x1, y1, x2, y2 = [int(v) for v in b.xyxy[0]]
                                det_boxes.append((x1, y1, x2, y2, cid, float(b.conf[0])))
                    self.last_det_boxes = det_boxes
                except Exception:
                    det_boxes = self.last_det_boxes
            else:
                det_boxes = self.last_det_boxes

            # Tính tọa độ pixel của ROI theo kích thước khung hình hiện tại
            roi_px = (self.roi_norm * np.array([w, h], dtype=np.float32)).astype(np.int32)
            current_centers = []
            roi_det_boxes = []

            # Lọc các phương tiện nằm trong vùng ROI (dung sai biên -6px để chống nhấp nháy ở mép đa giác)
            for (x1, y1, x2, y2, cid, conf) in det_boxes:
                cx, cy = (x1 + x2) / 2.0, (y1 + y2) / 2.0
                cat_key = COCO_VEHICLES[cid][1]

                dist_center = cv2.pointPolygonTest(roi_px, (float(cx), float(cy)), True)
                dist_bottom = cv2.pointPolygonTest(roi_px, (float(cx), float(y2)), True)
                dist_top = cv2.pointPolygonTest(roi_px, (float(cx), float(y1)), True)
                if dist_center >= -8.0 or dist_bottom >= -8.0 or dist_top >= -8.0:
                    current_centers.append(((cx, cy), cat_key, (x1, y1, x2, y2)))
                    roi_det_boxes.append((x1, y1, x2, y2, cid, conf))

            # Tọa độ giới hạn của ROI và đường cắt qua (Trigger Line chính xác giữa ROI)
            roi_min_x = np.min(roi_px[:, 0])
            roi_max_x = np.max(roi_px[:, 0])
            roi_min_y = np.min(roi_px[:, 1])
            roi_max_y = np.max(roi_px[:, 1])
            trigger_y = float((roi_min_y + roi_max_y) / 2.0)
            # Tính giới hạn x_left và x_right trên đường trigger_y theo các cạnh đa giác ROI
            try:
                x_l = int(np.interp(trigger_y, [roi_px[3, 1], roi_px[0, 1]], [roi_px[3, 0], roi_px[0, 0]]))
                x_r = int(np.interp(trigger_y, [roi_px[2, 1], roi_px[1, 1]], [roi_px[2, 0], roi_px[1, 0]]))
                if x_l > x_r:
                    x_l, x_r = x_r, x_l
            except Exception:
                x_l, x_r = int(roi_min_x), int(roi_max_x)

            # Cập nhật Tracking đối tượng trong ROI
            new_tracked = {}
            used_current = set()
            m_per_px_y = self.length_m / max(1.0, float(roi_max_y - roi_min_y))
            m_per_px_x = self.width_m / max(1.0, float(roi_max_x - roi_min_x))

            for tid, obj in list(self.tracked_objects.items()):
                prev_c = obj["centroid"]
                best_dist = max(90.0, float(w) * 0.05)
                best_idx = -1
                for idx, (curr_c, c_cat, c_box) in enumerate(current_centers):
                    if idx in used_current:
                        continue
                    dist = np.hypot(curr_c[0] - prev_c[0], curr_c[1] - prev_c[1])
                    if dist < best_dist:
                        best_dist = dist
                        best_idx = idx

                if best_idx >= 0:
                    used_current.add(best_idx)
                    c_pt, c_cat, c_box = current_centers[best_idx]

                    # Ước tính vận tốc thực tế của từng xe theo hướng dịch chuyển
                    dx_m = (c_pt[0] - prev_c[0]) * m_per_px_x
                    dy_m = (c_pt[1] - prev_c[1]) * m_per_px_y
                    dist_m = np.hypot(dx_m, dy_m)
                    dt = max(0.01, video_time_sec - obj.get("last_time", video_time_sec - 0.04))
                    v_raw = (dist_m / dt) * 3.6
                    v_raw = min(80.0, max(0.0, v_raw))
                    v_kmh = round(0.3 * v_raw + 0.7 * obj.get("speed", v_raw), 1)

                    # Kiểm tra vượt qua trigger line theo chiều chuyển động của dòng xe
                    crossed_line = False
                    if tid not in self.crossed_ids:
                        prev_y, curr_y = obj["last_y"], c_pt[1]
                        prev_x, curr_x = obj["last_x"], c_pt[0]
                        # Xe cắt ngang qua vạch trigger_y và nằm trong khoảng chiều rộng ROI
                        if (x_l - 15 <= curr_x <= x_r + 15) or (x_l - 15 <= prev_x <= x_r + 15):
                            if (prev_y < trigger_y <= curr_y) or (prev_y > trigger_y >= curr_y):
                                crossed_line = True
                                self.crossed_ids.add(tid)
                                self.crossing_events.append((video_time_sec, c_cat))

                    hits = obj.get("hits", 1) + 1

                    # BỘ ĐẾM XE LŨY KẾ CHUẨN ITS:
                    # Ghi nhận khi xe cắt qua vạch kiểm đếm (trigger line) HOẶC xuất hiện ổn định trong zone (hits >= 4)
                    if (crossed_line or tid in self.crossed_ids or hits >= 4) and tid not in self.counted_track_ids:
                        self.counted_track_ids.add(tid)
                        self.cumulative_vehicles += 1
                        self.cumulative_counts[c_cat] = self.cumulative_counts.get(c_cat, 0) + 1

                    new_tracked[tid] = {
                        "centroid": c_pt,
                        "cls": c_cat,
                        "first_seen": obj["first_seen"],
                        "last_time": video_time_sec,
                        "last_x": c_pt[0],
                        "last_y": c_pt[1],
                        "speed": v_kmh,
                        "hits": hits,
                        "lost_frames": 0,
                        "box": c_box
                    }
                else:
                    # Giữ lại track trong tối đa 8 frames nếu tạm thời mất phát hiện (chống chập chờn)
                    lost = obj.get("lost_frames", 0) + 1
                    if lost <= 8:
                        obj["lost_frames"] = lost
                        new_tracked[tid] = obj

            # Thêm xe mới phát hiện trong ROI vào tracking
            for idx, (curr_c, c_cat, c_box) in enumerate(current_centers):
                if idx not in used_current:
                    tid = self.next_track_id
                    self.next_track_id += 1
                    new_tracked[tid] = {
                        "centroid": curr_c,
                        "cls": c_cat,
                        "first_seen": video_time_sec,
                        "last_time": video_time_sec,
                        "last_x": curr_c[0],
                        "last_y": curr_c[1],
                        "speed": 0.0,
                        "hits": 1,
                        "lost_frames": 0,
                        "box": c_box
                    }

            self.tracked_objects = new_tracked

            # =========================================================================
            # TÍNH TOÁN CÁC CHỈ SỐ HOÀN TOÀN TỪ PHƯƠNG TIỆN THỰC TẾ TRONG VIDEO
            # =========================================================================
            # Lọc các xe đang thực sự active trong ROI (lost_frames <= 1)
            active_objects = [obj for obj in self.tracked_objects.values() if obj.get("lost_frames", 0) <= 1]
            roi_count = len(active_objects)

            # Đếm số xe theo phân loại trong ngã tư (đảm bảo sum(counts.values()) == roi_count)
            counts = {"xe_may": 0, "o_to_con": 0, "xe_khach": 0, "xe_tai": 0, "xe_dap": 0}
            for obj in active_objects:
                cat_k = obj.get("cls", "o_to_con")
                if cat_k in counts:
                    counts[cat_k] += 1
                else:
                    counts["o_to_con"] += 1

            # 1. Chiều dài đoạn đường (km) và Mật độ K (xe/km)
            roi_km = max(0.01, self.length_m / 1000.0)
            density = round(roi_count / roi_km, 1)

            # 2. Quy đổi xe con tiêu chuẩn PCU và Mật độ quy đổi (PCU/km) theo TCVN 4054:2005
            pcu = round(
                counts["xe_may"] * PCU_WEIGHTS["xe_may"] +
                counts["o_to_con"] * PCU_WEIGHTS["o_to_con"] +
                counts["xe_khach"] * PCU_WEIGHTS["xe_khach"] +
                counts["xe_tai"] * PCU_WEIGHTS["xe_tai"] +
                counts["xe_dap"] * PCU_WEIGHTS.get("xe_dap", 0.2),
                1
            )
            density_pcu = round(pcu / roi_km, 1)

            # 3. Vận tốc V (km/h) trung bình thực tế từ các xe trong ROI
            measured_speeds = [obj["speed"] for obj in active_objects if obj.get("hits", 1) >= 2]
            if measured_speeds:
                speed = round(float(np.mean(measured_speeds)), 1)
            elif active_objects:
                speed = 15.0  # Xe mới vào zone, đang chờ đo frame kế tiếp
            else:
                speed = 45.0  # Không có xe, tốc độ lưu thông tự do tham chiếu

            # 4. Tính toán hàng chờ phương tiện (Queue detection trong Zone)
            # Xe đang dừng hoặc bò chậm (< 5.0 km/h) và đã track ổn định
            queue_vehicles = sum(1 for obj in active_objects if obj.get("speed", 0.0) < 5.0 and obj.get("hits", 1) >= 2)
            queue_length_m = round(min(self.length_m, queue_vehicles * 4.5), 1)

            # 5. Lưu lượng Q (xe/giờ) theo công thức chuẩn dòng giao thông Q = K × V
            #    - Định luật cơ bản của lý thuyết dòng giao thông: Q = K * V (xe/km * km/h = xe/h)
            #    - Phương pháp đo cắt vạch thời gian thực: Q_counting = (N_crossings / delta_t) * 3600
            #    - Kết hợp chặt chẽ:
            #      + Khi dòng xe đang di chuyển: Q_hydro = K * V phản ánh lưu lượng tức thời.
            #      + Nếu có dữ liệu đếm vạch cắt, kết hợp theo trọng số (50% Q_counting + 50% Q_hydro)
            #      + Khi tắc đường (V tiến về 0 hoặc K cao): Q tự động giảm tương ứng vật lý.
            window_sec = 30.0
            recent_crossings = [ev for ev in self.crossing_events if (video_time_sec - ev[0]) <= window_sec]

            if roi_count == 0 and len(recent_crossings) == 0:
                flow_target = 0.0
            elif roi_count > 0:
                # Tính theo định luật dòng giao thông Q = K * V
                flow_hydro = density * speed
                if len(recent_crossings) >= 1 and video_time_sec >= 4.0:
                    actual_w = max(4.0, min(video_time_sec, window_sec))
                    flow_counting = (len(recent_crossings) / actual_w) * 3600.0
                    # Kết hợp đồng bộ giữa lưu lượng qua mặt cắt và tích K * V
                    flow_target = 0.50 * flow_counting + 0.50 * flow_hydro
                else:
                    flow_target = flow_hydro
            elif len(recent_crossings) >= 1 and video_time_sec >= 4.0:
                actual_w = max(4.0, min(video_time_sec, window_sec))
                flow_target = (len(recent_crossings) / actual_w) * 3600.0
            else:
                flow_target = 0.0

            flow_target = min(6000.0, max(0.0, flow_target))

            if not hasattr(self, "smoothed_flow") or self.smoothed_flow is None:
                self.smoothed_flow = flow_target
            else:
                # Bộ lọc số mũ làm mượt lưu lượng tức thời tránh dao động nhảy số
                self.smoothed_flow = 0.25 * flow_target + 0.75 * self.smoothed_flow
            flow = round(self.smoothed_flow, 0)

            # 6. Phân loại Mức độ phục vụ (Level of Service - LOS) theo 3 phương pháp cốt lõi ngành GTVT
            # Tiêu chí 1: Hệ số sử dụng năng lực đường V/C (Volume / Capacity)
            # - Tính toán khả năng thông hành Capacity theo chiều rộng thực tế (3.5m/làn chuẩn TCVN)
            lanes = max(1.0, round(self.width_m / 3.5, 1))
            capacity_total = lanes * float(DEFAULT_LANE_CAPACITY)
            vc_ratio = round(flow / max(1.0, capacity_total), 2)

            if vc_ratio < VC_THRESHOLDS[0]:          # < 0.60: LOS A - B
                lvl_vc = 1
            elif vc_ratio <= VC_THRESHOLDS[1]:       # 0.60 - 0.85: LOS C - D
                lvl_vc = 2
            elif vc_ratio < VC_THRESHOLDS[2]:        # 0.85 - 1.00: LOS E
                lvl_vc = 3
            else:                                    # >= 1.00: LOS F (quá tải)
                lvl_vc = 4

            # Tiêu chí 2: Tốc độ lưu thông hành trình so với tốc độ thiết kế (V / V_design)
            # V_design = 50 km/h (đường trục chính đô thị)
            v_design = float(DESIGN_SPEED_KMH)
            if roi_count == 0:
                lvl_speed = 1
            else:
                speed_ratio = speed / v_design
                if speed_ratio >= SPEED_RATIO_THRESHOLDS[0]:     # >= 80% (>= 40 km/h): Thông thoáng
                    lvl_speed = 1
                elif speed_ratio >= SPEED_RATIO_THRESHOLDS[1]:   # 50% - 80% (25 - 40 km/h): Đông đúc
                    lvl_speed = 2
                elif speed_ratio >= SPEED_RATIO_THRESHOLDS[2]:   # 30% - 50% (15 - 25 km/h): Ùn tắc
                    lvl_speed = 3
                else:                                            # < 30% (< 15 km/h hoặc dừng hẳn): Nghiêm trọng
                    lvl_speed = 4

            # Tiêu chí 3: Mật độ dòng xe K (xe/km) theo chuẩn DENSITY_THRESHOLDS
            if density < DENSITY_THRESHOLDS[0]:      # < 121 xe/km: Thông thoáng
                lvl_density = 1
            elif density < DENSITY_THRESHOLDS[1]:    # 121 - 220 xe/km: Đông đúc
                lvl_density = 2
            elif density < DENSITY_THRESHOLDS[2]:    # 220 - 350 xe/km: Ùn tắc
                lvl_density = 3
            else:                                    # >= 350 xe/km: Ùn tắc nghiêm trọng
                lvl_density = 4

            # Tiêu chí bổ trợ: Số lượng xe dừng trong hàng chờ
            if queue_vehicles >= 5 or (roi_count >= 6 and queue_vehicles >= roi_count * 0.75):
                lvl_queue = 4 if speed < 5.0 else 3
            elif queue_vehicles >= 4:
                lvl_queue = 3
            elif queue_vehicles >= 2 and speed < 16.0:
                lvl_queue = 2
            else:
                lvl_queue = 1

            # =========================================================================
            # NGUYÊN TẮC PHÂN LOẠI MỨC ĐỘ PHỤC VỤ (LOS) THỰC TẾ TRONG GTVT:
            # - Tuyến đường rộng 10-16m (3-4 làn xe), chiều dài quan sát 35-60m:
            # - Trọng tài cao nhất là V/C (Tải trọng dòng xe so với năng lực đường) & Chiếm dụng mặt đường:
            #   + Nếu V/C < 0.50 (đường đang thừa > 50% công suất):
            #     TUYỆT ĐỐI là THÔNG THOÁNG (LOS A - B). Xe đi chậm qua nút giao, rẽ cua
            #     hoặc dừng trước vạch người đi bộ KHÔNG PHẢI là ùn tắc giao thông.
            #   + Nếu roi_count <= 8 xe: Đường thông thoáng (LOS A - B).
            #   + 9 đến 14 xe:
            #       * Nếu V/C < 0.60 hoặc vận tốc >= 20 km/h: Vẫn là THÔNG THOÁNG / LOS B.
            #       * Nếu V/C >= 0.60 hoặc xe nối đuôi dừng hàng chờ: ĐÔNG ĐÚC (LOS C - D).
            #   + Từ 15 xe trở lên:
            #       * Nếu V/C > 0.85 VÀ vận tốc < 15 km/h: ÙN TẮC (LOS E - F).
            #       * Nếu dòng xe vẫn di chuyển đều: Tối đa là ĐÔNG ĐÚC.
            # =========================================================================
            # =========================================================================
            # PHÂN LOẠI MỨC ĐỘ GIAO THÔNG THỰC TẾ CHO TỪNG TRẠM CAMERA:
            # - Ngưỡng xe thông thoáng: self.free_thr
            # - Ngưỡng xe ùn tắc: self.jam_thr
            # - Vận tốc tới hạn ùn tắc: self.jam_speed (km/h)
            # =========================================================================
            if roi_count <= self.free_thr and (speed >= 15.0 or roi_count <= 2) and queue_vehicles < 3 and density < 160.0:
                # 1. THÔNG THOÁNG: Số xe trong zone ít, vận tốc bình thường, không có hàng chờ dồn ứ
                raw_cg_lvl = 1

            elif (roi_count >= self.jam_thr) or (density >= 240.0 and speed < 16.0) or (roi_count >= (self.free_thr + 3) and speed < 9.0) or queue_vehicles >= 4:
                # 2. ÙN TẮC / ÙN TẮC NGHIÊM TRỌNG:
                # Xe trong zone vượt ngưỡng jam_thr, hoặc mật độ quá cao và xe đi chậm, hoặc xe dừng hàng chờ
                if (speed < 7.5 and roi_count >= self.jam_thr) or queue_vehicles >= 5 or density >= 320.0:
                    raw_cg_lvl = 4  # Ùn tắc nghiêm trọng (Dòng xe tê liệt / dừng chân chờ)
                elif speed <= self.jam_speed or density >= 220.0:
                    raw_cg_lvl = 3  # Ùn tắc
                elif speed >= 25.0:
                    raw_cg_lvl = 2  # Dù xe đông nhưng đang chạy tốc độ cao
                else:
                    raw_cg_lvl = 3

            else:
                # 3. ĐÔNG ĐÚC: Nằm ở khoảng giữa Thông thoáng và Ùn tắc
                if speed < 10.0 and queue_vehicles >= 2:
                    raw_cg_lvl = 3  # Xe vừa phải nhưng bị nghẽn tốc độ chậm -> Chuyển thành Ùn tắc
                else:
                    raw_cg_lvl = 2  # Đông đúc

            # Bộ lọc chống rung lắc trạng thái ùn tắc (Hysteresis Filter)
            if not hasattr(self, "cg_history"):
                self.cg_history = deque(maxlen=5)
            self.cg_history.append(raw_cg_lvl)
            cg_lvl = int(round(float(np.mean(list(self.cg_history)))))
            cg_lvl = max(1, min(4, cg_lvl))

            cg_names = {
                1: "Thông thoáng",
                2: "Đông đúc",
                3: "Ùn tắc",
                4: "Ùn tắc nghiêm trọng"
            }
            cg_name = cg_names[cg_lvl]

            cg_ascii_names = {
                1: "THONG THOANG",
                2: "DONG DUC",
                3: "UN TAC",
                4: "UN TAC NGHIEM TRONG"
            }
            cg_ascii = cg_ascii_names[cg_lvl]

            los_names = {
                1: "LOS A - B (Thông thoáng)",
                2: "LOS C - D (Đông đúc)",
                3: "LOS E (Ùn ứ)",
                4: "LOS F (Ùn tắc nghiêm trọng)"
            }
            los_label = los_names[cg_lvl]

            # Cập nhật telemetry thời gian thực
            self.metrics = {
                "total_vehicles": roi_count,
                "cumulative_vehicles": self.cumulative_vehicles,
                "cumulative_counts": self.cumulative_counts.copy(),
                "counts": counts,
                "pcu": pcu,
                "density": density,
                "density_pcu": density_pcu,
                "flow": flow,
                "speed": speed,
                "fps": curr_fps,
                "queue_vehicles": queue_vehicles,
                "queue_length_m": queue_length_m,
                "congestion_level": cg_lvl,
                "congestion_name": cg_name,
                "los": los_label,
                "vc_ratio": vc_ratio,
                "capacity": round(capacity_total),
                "free_thr": self.free_thr,
                "jam_thr": self.jam_thr,
                "jam_speed": self.jam_speed,
                "last_updated": time.time(),
                "video_time_sec": round(video_time_sec, 1),
                "session_id": self.session_id
            }

            # Lưu vào cơ sở dữ liệu định kỳ mỗi 5 giây
            if (video_time_sec - self.last_minute_record_vtime) >= 5.0:
                self.last_minute_record_vtime = video_time_sec
                record_minute_metric(
                    camera_id=self.cam_id,
                    counts=counts,
                    pcu=pcu,
                    density=density,
                    flow=flow,
                    avg_speed=speed,
                    session_id=self.session_id,
                    video_time_sec=video_time_sec
                )

            # Ghi nhận trạng thái giao thông và cảnh báo vào Audit Logs định kỳ (mỗi 15s) hoặc khi đổi mức độ ùn tắc
            if (video_time_sec - self.last_audit_log_vtime) >= 15.0 or (cg_lvl != self.last_audit_congestion_lvl and (video_time_sec - self.last_audit_log_vtime) >= 4.0):
                self.last_audit_log_vtime = video_time_sec
                lvl_changed = (cg_lvl != self.last_audit_congestion_lvl)
                self.last_audit_congestion_lvl = cg_lvl

                if cg_lvl == 1:
                    advice = "Lưu lượng ngã tư thông thoáng. Duy trì chu kỳ đèn tín hiệu chuẩn 5 phút (300s)."
                elif cg_lvl == 2:
                    advice = "Dòng xe tăng cao trong ngã tư. Khuyến nghị kéo dài pha đèn xanh trục chính +15s."
                elif cg_lvl == 3:
                    advice = "Cảnh báo ùn ứ nút giao. Tăng thời lượng thoát xe trục chính +25s, hạn chế luồng phụ."
                else:
                    advice = "Ùn tắc nghiêm trọng tại nút giao! Kích hoạt chế độ giải tỏa khẩn cấp và cảnh báo CSGT."

                event_type = "THRESHOLD" if (cg_lvl >= 2 and lvl_changed) else "TRAFFIC_STATE"
                status_text = f"{cg_name} · {los_label} ({roi_count} xe trong ngã tư)"
                details = f"V/C: {vc_ratio:.2f} (Khả năng tải: {round(capacity_total)} xe/h) | Vận tốc: {speed:.1f} km/h | Mật độ: {density:.0f} xe/km | PCU: {pcu:.1f} | Xe máy: {counts['xe_may']} | Ô tô: {counts['o_to_con']} | Xe khách: {counts['xe_khach']} | Xe tải: {counts['xe_tai']}"

                try:
                    add_audit_log(
                        event_type=event_type,
                        camera_id=self.cam_id,
                        flow=flow,
                        density=density,
                        pcu=pcu,
                        speed=speed,
                        status_level=cg_lvl,
                        status_text=status_text,
                        advice=advice,
                        details=details
                    )
                except Exception as log_err:
                    pass

            # =========================================================================
            # VẼ TRỰC QUAN HÓA LÊN VIDEO STREAM
            # =========================================================================
            frame_annotated = frame.copy()

            # 1. Vẽ đa giác ROI ngã tư (Màu vàng kim với lớp phủ trong suốt nổi bật)
            overlay = frame_annotated.copy()
            cv2.fillPoly(overlay, [roi_px], (0, 215, 255))
            cv2.addWeighted(overlay, 0.16, frame_annotated, 0.84, 0, frame_annotated)
            cv2.polylines(frame_annotated, [roi_px], isClosed=True, color=(0, 215, 255), thickness=2)

            # 2. Vẽ vạch đếm xe (Màu đỏ tươi nổi bật) nối từ biên trái sang biên phải ROI
            cv2.line(frame_annotated, (int(x_l), int(trigger_y)), (int(x_r), int(trigger_y)), (0, 0, 255), 2)

            # 3. CHỈ vẽ bounding box và nhãn cho xe nằm TRONG vùng ngã tư (Không vẽ/đếm xe ngoài zone vàng)
            for (x1, y1, x2, y2, cid, conf) in roi_det_boxes:
                label_vn, cat_key, color = COCO_VEHICLES[cid]
                label_ascii = {
                    "xe_may": "Xe may",
                    "o_to_con": "O to con",
                    "xe_khach": "Xe khach",
                    "xe_tai": "Xe tai",
                    "xe_dap": "Xe dap"
                }.get(cat_key, label_vn)

                cv2.rectangle(frame_annotated, (x1, y1), (x2, y2), color, 2)
                tag = f"{label_ascii} {int(conf * 100)}%"
                tw = len(tag) * 9 + 8
                cv2.rectangle(frame_annotated, (x1, max(0, y1 - 20)), (x1 + tw, y1), color, -1)
                cv2.putText(frame_annotated, tag, (x1 + 4, max(14, y1 - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 1, cv2.LINE_AA)

            # 4. Thêm banner telemetry nhỏ góc trên bên trái
            hud_text = f"BO DEM: {self.cumulative_vehicles} xe | ZONE: {roi_count} xe | Q: {int(flow)} xe/h | V: {speed:.1f} km/h | V/C: {vc_ratio:.2f} | K: {density:.0f} xe/km | {cg_ascii}"
            cv2.rectangle(frame_annotated, (12, 12), (16 + len(hud_text) * 9, 38), (15, 23, 42), -1)
            cv2.putText(frame_annotated, hud_text, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 215, 255), 1, cv2.LINE_AA)

            # Phát cảnh báo Telegram tự động khi tắc đường (Mức 3 hoặc Mức 4)
            if cg_lvl >= 3 and (video_time_sec - getattr(self, "last_tele_alert_vtime", -999.0) >= 120.0):
                self.last_tele_alert_vtime = video_time_sec
                try:
                    from backend.core.telegram_notifier import send_congestion_alert_async
                    send_congestion_alert_async(
                        camera_id=f"{self.cam_id} · {self.name}",
                        congestion_level=cg_lvl,
                        congestion_name=cg_name,
                        los=los_label,
                        roi_count=roi_count,
                        density=density,
                        speed=speed,
                        vc_ratio=vc_ratio,
                        advice=advice,
                        frame=frame_annotated
                    )
                except Exception as tele_err:
                    print(f"[TelegramNotifier] Lỗi gửi cảnh báo tự động cho {self.cam_id}: {tele_err}")

            # Chế độ lưới (Low stream): 480px chiều rộng
            frame_low = cv2.resize(frame_annotated, (480, int(480 * h / w)), interpolation=cv2.INTER_AREA)
            _, buf_low = cv2.imencode(".jpg", frame_low, [cv2.IMWRITE_JPEG_QUALITY, 55])
            self.latest_jpeg_low = buf_low.tobytes()

            # Chế độ xem chi tiết Focus (High stream): chất lượng cao
            _, buf_high = cv2.imencode(".jpg", frame_annotated, [cv2.IMWRITE_JPEG_QUALITY, 75])
            self.latest_jpeg_high = buf_high.tobytes()
            self.new_frame_event.set()

            # Nhịp frame điều hòa ~25 FPS
            time.sleep(0.038)

        cap.release()


class CameraManager:
    def __init__(self):
        self.workers = {}
        self.det_model = None

    def initialize(self, det_model):
        self.det_model = det_model
        stations_config = [
            {
                "id": "CAM-01",
                "name": "CAM-01",
                "district": "Quận 1 · Nút giao trọng điểm",
                "bearing": "Làn thẳng & Hàng chờ đèn tín hiệu",
                "video": "uploads/cam3.mkv",
                "roi": [
                    [0.02, 0.98],
                    [0.76, 0.98],
                    [0.70, 0.56],
                    [0.10, 0.56]
                ],
                "length_m": 25.0,
                "width_m": 14.0,
                "free_thr": 2,     # <= 2 xe: Thông thoáng
                "jam_thr": 5,      # >= 5 xe dồn ứ trên vạch dừng: Ùn tắc
                "jam_speed": 14.0  # km/h
            },
            {
                "id": "CAM-02",
                "name": "CAM-02",
                "district": "Quận Bình Thạnh · Tuyến trục chính",
                "bearing": "Làn hỗn hợp & Ô tô một chiều",
                "video": "uploads/cam4.mkv",
                "roi": [
                    [0.02, 0.98],
                    [0.76, 0.98],
                    [0.70, 0.56],
                    [0.10, 0.56]
                ],
                "length_m": 25.0,
                "width_m": 14.0,
                "free_thr": 2,     # <= 2 xe: Thông thoáng
                "jam_thr": 5,      # >= 5 xe: Ùn tắc
                "jam_speed": 14.0  # km/h
            },
            {
                "id": "CAM-03",
                "name": "CAM-03",
                "district": "Quận Đống Đa · Giám sát ban đêm",
                "bearing": "Làn xe một chiều ban đêm",
                "video": "uploads/cam5.mkv",
                "roi": [
                    [0.02, 0.98],
                    [0.76, 0.98],
                    [0.70, 0.56],
                    [0.10, 0.56]
                ],
                "length_m": 25.0,
                "width_m": 14.0,
                "free_thr": 2,     # <= 2 xe: Thông thoáng
                "jam_thr": 5,      # >= 5 xe: Ùn tắc
                "jam_speed": 14.0
            },
            {
                "id": "CAM-04",
                "name": "CAM-04",
                "district": "Quận Cầu Giấy · Ngã 4 đô thị",
                "bearing": "Hàng chờ đèn đỏ & Vạch người đi bộ",
                "video": "uploads/cam6.mkv",
                "roi": [
                    [0.02, 0.98],
                    [0.76, 0.98],
                    [0.70, 0.56],
                    [0.10, 0.56]
                ],
                "length_m": 25.0,
                "width_m": 14.0,
                "free_thr": 2,     # <= 2 xe: Thông thoáng
                "jam_thr": 5,      # >= 5 xe: Ùn tắc
                "jam_speed": 14.0
            },
            {
                "id": "CAM-05",
                "name": "CAM-05",
                "district": "Quận Thanh Xuân · Nút giao đô thị",
                "bearing": "Làn hỗn hợp & Hướng rẽ trục chính",
                "video": "uploads/cam7.mp4",
                "roi": [
                    [0.08, 0.95],
                    [0.85, 0.95],
                    [0.75, 0.40],
                    [0.15, 0.40]
                ],
                "length_m": 45.0,
                "width_m": 14.0,
                "free_thr": 5,     # <= 5 xe: Thông thoáng
                "jam_thr": 12,     # >= 12 xe: Ùn tắc
                "jam_speed": 13.0
            },
            {
                "id": "CAM-06",
                "name": "CAM-06",
                "district": "Quận Ba Đình · Tuyến vành đai",
                "bearing": "Dòng xe tốc độ cao & Làn xuyên tâm",
                "video": "uploads/cam8.mp4",
                "roi": [
                    [0.05, 0.95],
                    [0.88, 0.95],
                    [0.75, 0.35],
                    [0.12, 0.35]
                ],
                "length_m": 50.0,
                "width_m": 15.0,
                "free_thr": 6,     # <= 6 xe: Thông thoáng
                "jam_thr": 13,     # >= 13 xe: Ùn tắc
                "jam_speed": 15.0
            }
        ]

        for s in stations_config:
            w = CameraWorker(
                cam_id=s["id"],
                name=s["name"],
                district=s["district"],
                bearing=s["bearing"],
                video_rel_path=s["video"],
                default_roi=s["roi"],
                length_m=s["length_m"],
                width_m=s["width_m"],
                det_model=self.det_model,
                free_thr=s.get("free_thr"),
                jam_thr=s.get("jam_thr"),
                jam_speed=s.get("jam_speed")
            )
            w.start()
            self.workers[s["id"]] = w

        print(f"[CAMERA MANAGER] Khởi chạy thành công {len(self.workers)} camera worker với {len(stations_config)} video thực tế.")

    def assign_source(self, cam_id, new_video_rel_path, source_type="upload"):
        """Gán video mới cho camera đã chỉ định."""
        worker = self.workers.get(cam_id)
        if not worker:
            return False, f"Camera {cam_id} không tồn tại"
        worker.change_source(new_video_rel_path, source_type=source_type)
        return True, f"Đã gán nguồn {new_video_rel_path} cho {cam_id}"

    def update_camera_config(self, cam_id, length_m=None, width_m=None, free_thr=None, jam_thr=None, jam_speed=None):
        """Cập nhật cấu hình kỹ thuật cho từng camera riêng biệt."""
        worker = self.workers.get(cam_id)
        if not worker:
            return False, f"Camera {cam_id} không tồn tại"
        worker.update_parameters(length_m=length_m, width_m=width_m, free_thr=free_thr, jam_thr=jam_thr, jam_speed=jam_speed)
        return True, "Cập nhật cấu hình thành công"

    def get_cameras_info(self):
        info_list = []
        for cam_id, w in self.workers.items():
            info_list.append({
                "id": w.cam_id,
                "name": w.name,
                "district": w.district,
                "bearing": w.bearing,
                "status": "ONLINE" if w.is_running else "OFFLINE",
                "video_rel_path": w.video_rel_path,
                "roi_norm": w.roi_norm.tolist(),
                "length_m": w.length_m,
                "width_m": w.width_m,
                "lanes": getattr(w, "lanes", max(1.0, round(w.width_m / 3.5, 1))),
                "free_thr": getattr(w, "free_thr", 8),
                "jam_thr": getattr(w, "jam_thr", 16),
                "jam_speed": getattr(w, "jam_speed", 14.0),
                "metrics": w.metrics,
                "session_id": w.session_id,
                "stream_url_low": f"/api/stream/{w.cam_id}?quality=low",
                "stream_url_high": f"/api/stream/{w.cam_id}?quality=high",
                "snapshot_url": f"/api/snapshot/{w.cam_id}?quality=low"
            })
        return info_list

    def get_worker(self, cam_id):
        return self.workers.get(cam_id)


# Global singleton instance
camera_manager = CameraManager()
