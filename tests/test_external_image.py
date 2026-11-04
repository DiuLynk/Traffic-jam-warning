"""
test_external_image.py - Kiểm thử nhận diện và phân tích giao thông trên HÌNH ẢNH NGOÀI.
Sử dụng 100% công thức tính toán chuẩn ITS đồng bộ với ứng dụng:
- Đếm số lượng theo 5 loại phương tiện (Ô tô con, Xe máy, Xe khách, Xe tải, Xe đạp)
- Điểm quy đổi xe con tiêu chuẩn PCU (TCVN 4054:2005)
- Vùng quan sát ROI & Homography mặt đường thực tế
- Mật độ dòng xe K (xe/km) & Mật độ quy đổi (PCU/km)
- Tỷ lệ chiếm dụng mặt đường Occupancy (%)
- Đánh giá Cấp độ ùn tắc (1 - 4) & Mức độ phục vụ (LOS A - F) theo hệ số V/C
"""

import os
import sys
from pathlib import Path

# Đảm bảo import được module gốc dù chạy từ thư mục bất kỳ
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import time
import cv2
import numpy as np
import matplotlib.pyplot as plt
from ultralytics import YOLO

from config import DET_WEIGHTS_PATH, CLS_WEIGHTS_PATH, WORKSPACE_DIR
from backend.core.traffic_calc import (
    COCO_VEHICLE_MAP,
    compute_roi_metrics,
    analyze_congestion,
    draw_roi_overlay,
    draw_vn_text,
    measure_vn_text
)


def imread_unicode(path):
    """Đọc ảnh an toàn hỗ trợ đường dẫn Unicode (tiếng Việt có dấu) trên Windows."""
    try:
        buffer = np.fromfile(path, dtype=np.uint8)
        return cv2.imdecode(buffer, cv2.IMREAD_COLOR)
    except (OSError, ValueError):
        return None


def imwrite_unicode(path, img):
    """Ghi ảnh an toàn hỗ trợ đường dẫn Unicode trên Windows."""
    try:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        ext = os.path.splitext(path)[1] or ".jpg"
        _, buf = cv2.imencode(ext, img)
        with open(path, "wb") as f:
            f.write(buf.tobytes())
        return True
    except Exception as e:
        print(f"⚠️ Không thể lưu ảnh: {e}")
        return False


def test_image(image_path, conf_thresh=0.25, show_plot=True):
    """Phân tích ảnh tĩnh theo đầy đủ công thức tính toán của hệ thống TrafficVision AI."""
    if not os.path.exists(image_path):
        print(f"❌ Không tìm thấy file ảnh: {image_path}")
        return

    if not os.path.exists(DET_WEIGHTS_PATH):
        print(f"❌ Không tìm thấy file trọng số mô hình YOLO tại: {DET_WEIGHTS_PATH}")
        return

    print("\n" + "=" * 65)
    print("🚦 TRAFFICVISION AI - KIỂM THỬ PHÂN TÍCH HÌNH ẢNH GIAO THÔNG")
    print(f"📁 Tệp ảnh: {image_path}")
    print(f"🧠 Trọng số YOLO: {DET_WEIGHTS_PATH}")
    print(f"🎯 Ngưỡng tin cậy (Confidence): {conf_thresh}")
    print("=" * 65)

    img_bgr = imread_unicode(image_path)
    if img_bgr is None:
        print("❌ Không thể đọc file ảnh (định dạng không hỗ trợ hoặc đường dẫn sai).")
        return

    h, w = img_bgr.shape[:2]
    annotated = img_bgr.copy()

    start_time = time.time()
    model = YOLO(str(DET_WEIGHTS_PATH))

    # Chạy YOLO Object Detection
    results = model.predict(
        source=img_bgr,
        conf=conf_thresh,
        classes=list(COCO_VEHICLE_MAP.keys()),
        verbose=False
    )[0]

    detections = []
    det_boxes = []
    total_detected = 0

    if results.boxes is not None and len(results.boxes) > 0:
        for box in results.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            if cls_id not in COCO_VEHICLE_MAP:
                continue

            total_detected += 1
            x1, y1, x2, y2 = [int(v) for v in box.xyxy[0]]
            label_vn, cat_key, color = COCO_VEHICLE_MAP[cls_id]

            # Vẽ bounding box
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)

            # Vẽ nhãn tiếng Việt và confidence
            tag_text = f"{label_vn} {conf * 100:.0f}%"
            tw, th = measure_vn_text(tag_text, px=14)
            cv2.rectangle(annotated, (x1, max(0, y1 - 22)), (x1 + tw + 10, y1), color, -1)
            draw_vn_text(annotated, tag_text, (x1 + 5, max(2, y1 - 20)),
                         px=14, color=(255, 255, 255), thickness=1)

            detections.append({
                "label": label_vn,
                "category": cat_key,
                "confidence": conf,
                "box": (x1, y1, x2, y2)
            })
            det_boxes.append((x1, y1, x2, y2, cls_id))

    # ÁP DỤNG CÔNG THỨC CHUẨN ITS:
    # 1. Tính toán các chỉ số trong vùng quan sát ROI
    roi_metrics = compute_roi_metrics(det_boxes, w, h)

    # 2. Phân tích mức độ ùn tắc và Level of Service (LOS)
    cg = analyze_congestion(
        roi_count=roi_metrics["roi_count"],
        density=roi_metrics["density"],
        occupancy=roi_metrics["occupancy"],
        density_pcu=roi_metrics["density_pcu"]
    )

    elapsed_ms = (time.time() - start_time) * 1000.0

    # 3. Vẽ vùng phủ ROI & HUD Header lên ảnh
    draw_roi_overlay(annotated, w, h, cg["level"])

    # Vẽ HUD banner trạng thái ở đỉnh ảnh
    hud_h = 48
    cv2.rectangle(annotated, (10, 10), (w - 10, 10 + hud_h), (20, 24, 33), -1)
    hud_text = (
        f"ROI: {roi_metrics['roi_count']} xe | "
        f"K: {roi_metrics['density']:.0f} xe/km | "
        f"Chiếm: {roi_metrics['occupancy']:.0f}% | "
        f"PCU: {roi_metrics['roi_pcu']:.1f} | "
        f"{cg['name'].upper()} ({cg['los']})"
    )
    draw_vn_text(annotated, hud_text, (20, 22), px=18, color=(0, 242, 254), thickness=2)

    # In kết quả chi tiết ra màn hình console
    counts = roi_metrics["counts"]
    print("\n📊 BẢNG KẾT QUẢ PHÂN TÍCH CHỈ SỐ GIAO THÔNG (ITS):")
    print("-" * 65)
    print(f"🚗 Tổng số xe nhận diện trên ảnh : {total_detected} xe")
    print(f"🎯 Số xe nằm trong vùng quan sát ROI: {roi_metrics['roi_count']} xe")
    print(f"   ├─ Xe máy     : {counts['xe_may']:>3} xe (x0.33 PCU)")
    print(f"   ├─ Ô tô con   : {counts['o_to_con']:>3} xe (x1.00 PCU)")
    print(f"   ├─ Xe khách   : {counts['xe_khach']:>3} xe (x2.50 PCU)")
    print(f"   ├─ Xe tải     : {counts['xe_tai']:>3} xe (x2.00 PCU)")
    print(f"   └─ Xe đạp     : {counts['xe_dap']:>3} xe (x0.20 PCU)")
    print(f"📐 Chiều dài thực tế đoạn đường  : {roi_metrics['roi_length_m']:.1f} m")
    print(f"📈 Mật độ dòng xe (K)             : {roi_metrics['density']:.1f} xe/km")
    print(f"🚙 Điểm xe con quy đổi (PCU)     : {roi_metrics['roi_pcu']:.1f} PCU (Mật độ: {roi_metrics['density_pcu']:.1f} PCU/km)")
    print(f"⬛ Độ chiếm dụng mặt đường       : {roi_metrics['occupancy']:.1f} %")
    print(f"🚦 Mức độ phục vụ (LOS)           : {cg['los']}")
    print(f"⚠️ Trạng thái ùn tắc              : [Cấp {cg['level']}] {cg['name']}")
    print(f"📝 Đánh giá chi tiết              : {cg['description']}")
    print(f"⏱️ Thời gian xử lý frame         : {elapsed_ms:.1f} ms")
    print("=" * 65)

    # Lưu ảnh kết quả
    out_dir = os.path.join(str(WORKSPACE_DIR), "runs", "predict_image")
    os.makedirs(out_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    output_path = os.path.join(out_dir, f"{base_name}_analyzed.jpg")
    imwrite_unicode(output_path, annotated)
    print(f"💾 Ảnh kết quả đã lưu tại: {output_path}")

    if show_plot:
        try:
            img_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
            plt.figure(figsize=(10, 7))
            plt.imshow(img_rgb)
            plt.title(f"TrafficVision AI: {cg['name']} ({cg['los']}) - {roi_metrics['roi_count']} xe trong ROI",
                      fontsize=13, fontweight='bold', color='darkblue')
            plt.axis('off')
            plt.tight_layout()
            plt.show()
        except Exception as e:
            print(f"ℹ️ Không thể hiển thị cửa sổ đồ họa: {e}")

    return {
        "roi_metrics": roi_metrics,
        "congestion": cg,
        "output_path": output_path
    }


if __name__ == "__main__":
    show_plot = "--no-show" not in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]

    img_path = None
    if args:
        img_path = args[0].strip('"')
    elif show_plot:
        # Thử mở hộp thoại chọn file của Windows
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            selected = filedialog.askopenfilename(
                title="Chọn file ảnh ngoài để thử nghiệm TrafficVision AI",
                filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.webp"), ("All files", "*.*")]
            )
            root.destroy()
            if selected:
                img_path = selected
        except Exception:
            pass

    if not img_path:
        default_candidate = os.path.join(str(WORKSPACE_DIR), "test_CAM-01.jpg")
        if not show_plot:
            img_path = default_candidate
        else:
            print("\n💡 Nhập đường dẫn file ảnh ngoài (hoặc nhấn ENTER để dùng ảnh test_CAM-01.jpg):")
            inp = input("👉 Đường dẫn ảnh: ").strip('"')
            img_path = inp if inp else default_candidate

    test_image(img_path, show_plot=show_plot)
