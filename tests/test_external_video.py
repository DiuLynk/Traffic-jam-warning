"""
test_external_video.py - Kiểm thử nhận diện và phân tích dòng giao thông trên VIDEO NGOÀI.
Sử dụng 100% công thức tính toán chuẩn ITS đồng bộ với ứng dụng:
- Theo dõi chuyển động phương tiện đa mục tiêu (Multi-object Tracking)
- Vạch cắt đếm lưu lượng mặt cắt ngang đường (ITS Counting Trigger Line)
- Vận tốc hành trình V (km/h) theo mô hình động học Greenshields
- Lưu lượng dòng xe Q (xe/giờ) kết hợp định luật dòng giao thông Q = K × V và đếm thực tế
- Hệ số sử dụng năng lực đường V/C (Volume / Capacity)
- Phân cấp Mức độ phục vụ (Level of Service - LOS A/B/C/D/E/F) & Cấp độ ùn tắc (1 - 4)
"""

import os
import sys
from pathlib import Path

# Đảm bảo import được module gốc dù chạy từ thư mục bất kỳ
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import time
from collections import deque
import cv2
import numpy as np
from ultralytics import YOLO

from config import (
    DET_WEIGHTS_PATH, WORKSPACE_DIR, ROI_REAL_WIDTH_M, ROI_REAL_LENGTH_M,
    DEFAULT_LANE_CAPACITY
)
from backend.core.traffic_calc import (
    COCO_VEHICLE_MAP,
    counting_line,
    compute_roi_metrics,
    estimate_speed_greenshields,
    analyze_congestion,
    draw_roi_overlay,
    draw_vn_text,
    draw_vn_texts,
    measure_vn_text
)


def process_video(video_path, output_path=None, conf_thresh=0.25, show_window=True, max_frames=None):
    """Xử lý video ngoài theo đầy đủ công thức tính toán của hệ thống TrafficVision AI."""
    if not os.path.exists(video_path):
        print(f"❌ Không tìm thấy file video: {video_path}")
        return

    if not os.path.exists(DET_WEIGHTS_PATH):
        print(f"❌ Không tìm thấy file trọng số mô hình YOLO tại: {DET_WEIGHTS_PATH}")
        return

    print("\n" + "=" * 70)
    print("🚦 TRAFFICVISION AI - KIỂM THỬ PHÂN TÍCH VIDEO GIAO THÔNG")
    print(f"📁 Tệp video: {video_path}")
    print(f"🧠 Trọng số YOLO: {DET_WEIGHTS_PATH}")
    print(f"🎯 Ngưỡng tin cậy (Confidence): {conf_thresh}")
    print("=" * 70)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Không thể mở file video: {video_path}")
        return

    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if max_frames and max_frames > 0:
        total_frames = min(total_frames, max_frames)

    if output_path is None:
        out_dir = os.path.join(str(WORKSPACE_DIR), "runs", "predict_video")
        os.makedirs(out_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        output_path = os.path.join(out_dir, f"{base_name}_analyzed.mp4")

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

    y_line, x_l, x_r = counting_line(w, h)

    # Khởi tạo mô hình
    model = YOLO(str(DET_WEIGHTS_PATH))

    # Bộ theo dõi cắt vạch và lưu lượng
    track_last_y = {}
    counted_ids = set()
    crossing_times = deque(maxlen=2000)
    stream_start = time.time()
    smoothed_flow = 0.0

    win_name = "TrafficVision AI - Video Analysis Preview"
    if show_window:
        try:
            cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(win_name, min(1080, max(640, int(w * 0.75))), min(720, max(360, int(h * 0.75))))
        except Exception:
            show_window = False

    print(f"📐 Kích thước: {w}x{h} | FPS: {fps:.1f} | Tổng số frames xử lý: {total_frames}")
    print(f"💾 Video kết quả sẽ lưu tại: {output_path}")
    print(f"🖥️  Hiển thị cửa sổ xem thử: {'CÓ (bấm q trên cửa sổ để dừng)' if show_window else 'KHÔNG'}")
    print("\n" + "-" * 110)
    print(f"{'Frame':>9} | {'FPS':>5} | {'ROI(xe)':>7} | {'Mật độ K':>9} | {'Vận tốc V':>9} | {'Lưu lượng Q':>11} | {'V/C':>5} | {'Mức độ (LOS)':<25}")
    print("-" * 110)

    frame_idx = 0
    start_time = time.time()

    try:
        while cap.isOpened():
            if max_frames and frame_idx >= max_frames:
                break

            ret, frame = cap.read()
            if not ret:
                break

            frame_idx += 1
            annotated = frame.copy()

            # Tracking phương tiện
            try:
                results = model.track(
                    source=frame,
                    persist=True,
                    tracker="bytetrack.yaml",
                    conf=conf_thresh,
                    classes=list(COCO_VEHICLE_MAP.keys()),
                    verbose=False
                )[0]
            except Exception:
                results = model.predict(
                    source=frame,
                    conf=conf_thresh,
                    classes=list(COCO_VEHICLE_MAP.keys()),
                    verbose=False
                )[0]

            det_boxes = []
            vn_text_queue = []

            if results.boxes is not None and len(results.boxes) > 0:
                boxes_xyxy = results.boxes.xyxy.cpu().numpy()
                classes = results.boxes.cls.cpu().numpy().astype(int)
                confs = results.boxes.conf.cpu().numpy()
                track_ids = (results.boxes.id.cpu().numpy().astype(int)
                             if results.boxes.id is not None else [None] * len(boxes_xyxy))

                for box, cid, conf, tid in zip(boxes_xyxy, classes, confs, track_ids):
                    if cid not in COCO_VEHICLE_MAP:
                        continue

                    label_vn, cat_key, color = COCO_VEHICLE_MAP[cid]
                    x1, y1, x2, y2 = [int(v) for v in box]
                    det_boxes.append((x1, y1, x2, y2, cid))

                    # Vẽ bounding box
                    cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)

                    # Nhãn tiếng Việt
                    tag_text = f"{label_vn} {conf * 100:.0f}%" if tid is None else f"#{tid} {label_vn}"
                    tw, th = measure_vn_text(tag_text, px=13)
                    cv2.rectangle(annotated, (x1, max(0, y1 - 22)), (x1 + tw + 10, y1), color, -1)
                    vn_text_queue.append((tag_text, (x1 + 5, max(2, y1 - 20)), 13, (255, 255, 255), 1))

                    # Kiểm tra cắt qua vạch kiểm đếm lưu lượng ITS
                    if tid is not None:
                        cx, cy = (x1 + x2) / 2.0, float(y2)
                        prev_y = track_last_y.get(tid)
                        if prev_y is not None and x_l <= cx <= x_r:
                            if (prev_y < y_line <= cy) or (prev_y > y_line >= cy):
                                if tid not in counted_ids:
                                    counted_ids.add(tid)
                                    crossing_times.append(time.time())
                        track_last_y[tid] = cy

            # =========================================================================
            # CÔNG THỨC CHUẨN ITS ĐỒNG BỘ 100% VỚI APP LOCAL:
            # =========================================================================
            # 1. Chỉ số trong vùng quan sát ROI
            roi_metrics = compute_roi_metrics(det_boxes, w, h)
            roi_count = roi_metrics["roi_count"]
            density_val = roi_metrics["density"]

            # 2. Vận tốc dòng xe V (km/h) theo Greenshields đô thị
            speed_est = estimate_speed_greenshields(density_val, roi_count)

            # 3. Lưu lượng dòng xe Q (xe/h) theo định luật dòng Q = K × V & vạch cắt ITS
            now = time.time()
            window_s = 30.0
            recent = [t for t in crossing_times if now - t <= window_s]
            eff = min(window_s, max(now - stream_start, 3.0))
            flow_counting = (len(recent) / eff) * 3600.0

            if roi_count == 0 and len(recent) == 0:
                target_flow = 0.0
            elif roi_count > 0:
                flow_hydro = density_val * speed_est
                if len(recent) >= 1:
                    target_flow = 0.50 * flow_counting + 0.50 * flow_hydro
                else:
                    target_flow = flow_hydro
            else:
                target_flow = flow_counting

            target_flow = min(6000.0, max(0.0, target_flow))
            flow_vph = 0.25 * target_flow + 0.75 * smoothed_flow
            smoothed_flow = flow_vph

            # 4. Phân tích mức độ ùn tắc và Level of Service (LOS)
            cg = analyze_congestion(
                roi_count=roi_count,
                density=density_val,
                occupancy=roi_metrics["occupancy"],
                flow_vph=flow_vph,
                density_pcu=roi_metrics["density_pcu"],
                speed=speed_est if roi_count > 0 else None,
                road_width_m=float(ROI_REAL_WIDTH_M)
            )

            # 5. Vẽ overlay ROI và vạch đếm
            draw_roi_overlay(annotated, w, h, cg["level"])

            # 6. Vẽ thanh trạng thái HUD trên đầu video
            vc_val = cg.get("vc_ratio", 0.0)
            hud_text = (
                f"ROI: {roi_count} xe | "
                f"Q: {flow_vph:.0f} xe/h | "
                f"V/C: {vc_val:.2f} | "
                f"K: {density_val:.0f} xe/km | "
                f"V: {speed_est:.1f} km/h | "
                f"{cg['name'].upper()} ({cg['los']})"
            )
            cv2.rectangle(annotated, (10, 10), (w - 10, 52), (15, 15, 25), -1)
            vn_text_queue.append((hud_text, (20, 20), 18, (0, 242, 254), 2))
            draw_vn_texts(annotated, vn_text_queue)

            writer.write(annotated)

            if show_window:
                cv2.imshow(win_name, annotated)
                if cv2.waitKey(1) & 0xFF in (ord('q'), 27):
                    print("\n[INFO] Đã hủy cửa sổ xem thử bởi người dùng.")
                    break

            if frame_idx % 25 == 0 or frame_idx == total_frames:
                elapsed = time.time() - start_time
                fps_proc = frame_idx / max(0.001, elapsed)
                print(
                    f"{frame_idx:>4}/{total_frames:<4} | "
                    f"{fps_proc:>5.1f} | "
                    f"{roi_count:>7} | "
                    f"{density_val:>7.0f} xe/km | "
                    f"{speed_est:>7.1f} km/h | "
                    f"{flow_vph:>9.0f} xe/h | "
                    f"{vc_val:>5.2f} | "
                    f"[L{cg['level']}] {cg['name']} ({cg['los']})"
                )

    finally:
        cap.release()
        writer.release()
        if show_window:
            cv2.destroyAllWindows()

    total_time = time.time() - start_time
    size_mb = os.path.getsize(output_path) / (1024 * 1024) if os.path.exists(output_path) else 0

    print("-" * 110)
    print("✅ HOÀN TẤT XỬ LÝ VIDEO!")
    print(f"⏱️ Tổng thời gian: {total_time:.2f} giây ({frame_idx / max(0.1, total_time):.1f} FPS)")
    print(f"📁 Video kết quả đã lưu: {output_path} ({size_mb:.2f} MB)")
    print("=" * 70)


if __name__ == "__main__":
    show_window = "--no-window" not in sys.argv
    max_frames = None
    for arg in sys.argv:
        if arg.startswith("--max-frames="):
            try:
                max_frames = int(arg.split("=")[1])
            except ValueError:
                pass

    args = [a for a in sys.argv[1:] if not a.startswith("--")]

    v_path = None
    if args:
        v_path = args[0].strip('"')
    elif show_window:
        # Thử mở hộp thoại chọn file của Windows
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            selected = filedialog.askopenfilename(
                title="Chọn file video ngoài để thử nghiệm TrafficVision AI",
                filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv *.webm *.m4v"), ("All files", "*.*")]
            )
            root.destroy()
            if selected:
                v_path = selected
        except Exception:
            pass

    if not v_path:
        # Tìm video mẫu có sẵn trong thư mục uploads/
        candidates = [
            os.path.join(str(WORKSPACE_DIR), "uploads", "cam7.mp4"),
            os.path.join(str(WORKSPACE_DIR), "uploads", "cam3.mkv"),
            os.path.join(str(WORKSPACE_DIR), "uploads", "cam8.mp4")
        ]
        default_sample = next((c for c in candidates if os.path.exists(c)), candidates[0])

        if not show_window:
            v_path = default_sample
        else:
            print("\n💡 Nhập đường dẫn file video ngoài (hoặc nhấn ENTER để dùng video mẫu sẵn có):")
            inp = input(f"👉 Đường dẫn video [mặc định: {os.path.basename(default_sample)}]: ").strip('"')
            v_path = inp if inp else default_sample

    process_video(v_path, show_window=show_window, max_frames=max_frames)
