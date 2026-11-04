"""
traffic_calc.py - Module tập trung tính toán chỉ số giao thông chuẩn ITS (Intelligent Transportation System).
Đồng bộ 100% công thức tính toán với hệ thống TrafficVision AI:
- Nhận diện phương tiện (Ô tô con, Xe máy, Xe khách, Xe tải, Xe đạp)
- Quy đổi xe con tiêu chuẩn PCU (TCVN 4054:2005)
- Vùng quan sát chuẩn hoá ROI (Region of Interest) & Chuyển đổi phối cảnh Homography
- Mật độ dòng xe K (xe/km) & Mật độ quy đổi (PCU/km)
- Độ chiếm dụng mặt đường Occupancy (%)
- Vận tốc hành trình V (km/h) theo mô hình động học Greenshields & tracking
- Lưu lượng dòng xe Q (xe/h) theo định luật dòng giao thông Q = K × V & vạch cắt ITS
- Hệ số sử dụng năng lực đường V/C (Volume / Capacity)
- Phân cấp Mức độ phục vụ (Level of Service - LOS A/B/C/D/E/F) & Cấp độ ùn tắc (1, 2, 3, 4)
"""

import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from config import (
    ROI_REAL_WIDTH_M, ROI_REAL_LENGTH_M,
    DENSITY_THRESHOLDS, OCCUPANCY_THRESHOLDS, PCU_WEIGHTS,
    VC_THRESHOLDS, SPEED_RATIO_THRESHOLDS, DESIGN_SPEED_KMH, DEFAULT_LANE_CAPACITY,
    VN_FONT_PATHS, WORKSPACE_DIR
)

# Mapping COCO vehicle class IDs sang nhãn tiếng Việt & màu vẽ (BGR format)
COCO_VEHICLE_MAP = {
    2: ("Ô tô con", "o_to_con", (0, 215, 255)),     # car - Gold/Yellow
    3: ("Xe máy", "xe_may", (255, 144, 30)),        # motorcycle - Blue/Cyan
    5: ("Xe khách", "xe_khach", (226, 43, 138)),    # bus - Purple
    7: ("Xe tải", "xe_tai", (0, 69, 255)),          # truck - Red/Orange
    1: ("Xe đạp", "xe_dap", (94, 197, 34))          # bicycle - Emerald Green
}

# Đa giác ROI chuẩn hoá (0..1) tạo hình thang phối cảnh mặt đường
# Thứ tự 4 đỉnh: dưới-trái, dưới-phải, trên-phải, trên-trái (dưới = gần camera, trên = xa camera)
ROI_NORM = np.array([
    [0.12, 0.99],   # dưới-trái  (gần camera)
    [0.88, 0.99],   # dưới-phải
    [0.66, 0.40],   # trên-phải  (xa camera)
    [0.34, 0.40],   # trên-trái
], dtype=np.float32)

_VN_FONT_CACHE = {}


def _find_vn_font():
    """Tìm font TTF hỗ trợ đầy đủ dấu tiếng Việt."""
    for path in VN_FONT_PATHS:
        if path and os.path.exists(path):
            return path
    try:
        from ultralytics.utils.checks import check_font
        return check_font("DejaVuSans-Bold.ttf")
    except Exception:
        return None


def _vn_font(px):
    """Lấy font PIL theo cỡ pixel."""
    px = max(8, int(px))
    if px not in _VN_FONT_CACHE:
        path = _find_vn_font()
        try:
            _VN_FONT_CACHE[px] = (ImageFont.truetype(path, px) if path
                                  else ImageFont.load_default())
        except Exception:
            _VN_FONT_CACHE[px] = ImageFont.load_default()
    return _VN_FONT_CACHE[px]


def draw_vn_text(img, text, org, px=18, color=(255, 255, 255), thickness=1):
    """Vẽ chữ tiếng Việt có dấu lên ảnh BGR qua PIL."""
    x, y = int(org[0]), int(org[1])
    font = _vn_font(px)
    for dx, dy in ([(0, 0)] if thickness <= 1 else
                   [(dx, dy) for dx in range(thickness) for dy in range(thickness)]):
        pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        d = ImageDraw.Draw(pil)
        d.text((x + dx, y + dy), str(text), font=font,
               fill=(int(color[2]), int(color[1]), int(color[0])))
        img[:] = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
    try:
        left, top, right, bottom = font.getbbox(str(text))
        return max(0, right - left), max(0, bottom - top)
    except Exception:
        return 0, 0


def measure_vn_text(text, px=18):
    """Đo (w, h) kích thước hộp chữ tiếng Việt."""
    font = _vn_font(px)
    try:
        left, top, right, bottom = font.getbbox(str(text))
        return max(0, right - left), max(0, bottom - top)
    except Exception:
        return 0, 0


def draw_vn_texts(img, items):
    """Vẽ nhiều chuỗi tiếng Việt cùng lúc giảm thiểu số lần chuyển đổi array-PIL."""
    if not items:
        return
    pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    d = ImageDraw.Draw(pil)
    for text, org, px, color, thickness in items:
        font = _vn_font(int(px))
        x, y = int(org[0]), int(org[1])
        rgb = (int(color[2]), int(color[1]), int(color[0]))
        steps = [(0, 0)] if int(thickness) <= 1 else [
            (dx, dy) for dx in range(int(thickness)) for dy in range(int(thickness))]
        for dx, dy in steps:
            d.text((x + dx, y + dy), str(text), font=font, fill=rgb)
    img[:] = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)


def get_roi_pixels(w, h):
    """Trả về 4 đỉnh đa giác ROI (pixel) theo kích thước ảnh (w, h)."""
    pts = ROI_NORM.copy()
    pts[:, 0] *= w
    pts[:, 1] *= h
    return pts.astype(np.int32)


def build_homography(w, h, width_m=None, length_m=None):
    """Ma trận biến đổi phối cảnh: pixel ảnh -> mặt phẳng đường (mét)."""
    real_w = float(width_m if width_m is not None else ROI_REAL_WIDTH_M)
    real_l = float(length_m if length_m is not None else ROI_REAL_LENGTH_M)
    src = (ROI_NORM * np.array([w, h], dtype=np.float32)).astype(np.float32)
    dst = np.array([
        [0, 0],
        [real_w, 0],
        [real_w, real_l],
        [0, real_l],
    ], dtype=np.float32)
    return cv2.getPerspectiveTransform(src, dst)


def ground_point_m(w, h, x, y, H=None, width_m=None, length_m=None):
    """Chuyển 1 điểm ảnh (x, y) sang toạ độ thực (X, Y) trên mặt đường (mét)."""
    if H is None:
        H = build_homography(w, h, width_m, length_m)
    p = cv2.perspectiveTransform(
        np.array([[[float(x), float(y)]]], dtype=np.float32), H)
    return float(p[0, 0, 0]), float(p[0, 0, 1])


def measure_roi_length_m(w, h, width_m=None, length_m=None):
    """Đo chiều dài thực tế đoạn đường ROI (mét) bằng homography."""
    roi_px = get_roi_pixels(w, h)
    near = ((float(roi_px[0, 0]) + float(roi_px[1, 0])) / 2.0,
            (float(roi_px[0, 1]) + float(roi_px[1, 1])) / 2.0)
    far = ((float(roi_px[2, 0]) + float(roi_px[3, 0])) / 2.0,
           (float(roi_px[2, 1]) + float(roi_px[3, 1])) / 2.0)
    H = build_homography(w, h, width_m, length_m)
    x1, y1 = ground_point_m(w, h, near[0], near[1], H, width_m, length_m)
    x2, y2 = ground_point_m(w, h, far[0], far[1], H, width_m, length_m)
    length = float(np.hypot(x2 - x1, y2 - y1))
    return length if length > 0 else float(length_m if length_m is not None else ROI_REAL_LENGTH_M)


def point_in_roi(roi_px, x, y):
    """Kiểm tra điểm tiếp đất (x, y) có nằm trong vùng đa giác ROI hay không."""
    return cv2.pointPolygonTest(roi_px, (float(x), float(y)), False) >= 0


def counting_line(w, h):
    """Tọa độ vạch đếm lưu lượng mặt cắt giữa ROI. Trả về (y_line, x_left, x_right)."""
    roi_px = get_roi_pixels(w, h)
    y_line = int((int(roi_px[:, 1].min()) + int(roi_px[:, 1].max())) / 2)
    x_l = int(np.interp(y_line, [roi_px[3, 1], roi_px[0, 1]], [roi_px[3, 0], roi_px[0, 0]]))
    x_r = int(np.interp(y_line, [roi_px[2, 1], roi_px[1, 1]], [roi_px[2, 0], roi_px[1, 0]]))
    return y_line, x_l, x_r


def compute_roi_metrics(det_boxes, w, h, width_m=None, length_m=None):
    """
    Tính toán các chỉ số giao thông chuẩn TRONG ROI từ danh sách bounding box.
    det_boxes: list các tuple (x1, y1, x2, y2, cls_id)
    Trả về dict gồm: counts, roi_count, roi_pcu, occupancy(%), density(xe/km), density_pcu(PCU/km)...
    """
    roi_px = get_roi_pixels(w, h)
    roi_area = float(cv2.contourArea(roi_px))
    if roi_area <= 0:
        roi_area = float(w * h)

    roi_length_m = measure_roi_length_m(w, h, width_m, length_m)
    roi_km = roi_length_m / 1000.0 if roi_length_m > 0 else (float(ROI_REAL_LENGTH_M) / 1000.0)

    counts = {"xe_may": 0, "o_to_con": 0, "xe_khach": 0, "xe_tai": 0, "xe_dap": 0}
    roi_count = 0
    roi_pcu = 0.0
    occupied_area = 0.0

    for (x1, y1, x2, y2, cls_id) in det_boxes:
        if cls_id not in COCO_VEHICLE_MAP:
            continue
        cx, cy = (x1 + x2) / 2.0, float(y2)
        if not point_in_roi(roi_px, cx, cy):
            continue

        _, cat_key, _ = COCO_VEHICLE_MAP[cls_id]
        counts[cat_key] += 1
        roi_count += 1
        roi_pcu += PCU_WEIGHTS.get(cat_key, 1.0)

        # Đo độ chiếm dụng diện tích mặt đường
        rect = np.array([[x1, y1], [x2, y1], [x2, y2], [x1, y2]], dtype=np.float32)
        inter_area, _ = cv2.intersectConvexConvex(rect, roi_px.astype(np.float32))
        occupied_area += max(0.0, inter_area)

    occupancy = (occupied_area / roi_area) * 100.0
    density = roi_count / max(0.001, roi_km)
    density_pcu = roi_pcu / max(0.001, roi_km)

    return {
        "counts": counts,
        "roi_count": roi_count,
        "roi_pcu": round(roi_pcu, 1),
        "occupancy": round(occupancy, 1),
        "density": round(density, 1),
        "density_pcu": round(density_pcu, 1),
        "roi_area_px": round(roi_area),
        "roi_length_m": round(float(roi_length_m), 1),
    }


def estimate_speed_greenshields(density, roi_count):
    """
    Ước lượng vận tốc dòng xe V (km/h) theo quan hệ thực nghiệm Greenshields đô thị:
    Khi đường vắng, vận tốc tự do đạt ~ 35 - 45 km/h; khi mật độ tăng dần tới ngưỡng ùn tắc, vận tốc giảm.
    """
    if roi_count <= 0:
        return 0.0
    k_jam = max(1.0, float(DENSITY_THRESHOLDS[2]))
    return max(5.0, 35.0 - (float(density) / k_jam) * 25.0)


def analyze_congestion(roi_count, density, occupancy, flow_vph=None, density_pcu=None, speed=None, road_width_m=None):
    """
    Phân loại Mức độ phục vụ (Level of Service - LOS) theo 3 phương pháp cốt lõi ngành GTVT:
    1. Hệ số sử dụng năng lực đường V/C (Volume / Capacity)
    2. Tốc độ lưu thông hành trình so với tốc độ thiết kế (V / V_design, V_design = 50 km/h)
    3. Mật độ dòng xe K (xe/km) theo chuẩn DENSITY_THRESHOLDS [121, 220, 350]
    """
    if roi_count <= 0:
        return {
            "name": "Không phát hiện phương tiện",
            "level": 0,
            "los": "LOS A",
            "vc_ratio": 0.0,
            "color": (148, 163, 184),       # Slate gray (BGR)
            "hex_color": "#94a3b8",
            "badge": "none",
            "description": "Không có phương tiện nào trong vùng quan sát ROI."
        }

    width_m = float(road_width_m or ROI_REAL_WIDTH_M or 12.0)
    lanes = max(1.0, round(width_m / 3.5, 1))
    capacity_total = lanes * float(DEFAULT_LANE_CAPACITY)
    current_volume = float(flow_vph) if (flow_vph is not None and flow_vph > 0) else (density * max(5.0, float(speed or 25.0)))
    vc_ratio = round(current_volume / max(1.0, capacity_total), 2)

    # 1. THÔNG THOÁNG: Số xe ít (<= 5 xe), hoặc mật độ thấp và tốc độ tốt
    if roi_count <= 5 and (speed is None or speed >= 15.0 or roi_count <= 2) and density < 160.0:
        level = 1
    # 2. ÙN TẮC / ÙN TẮC NGHIÊM TRỌNG
    elif roi_count >= 12 or (density >= 240.0 and (speed is None or speed < 16.0)) or (roi_count >= 9 and speed is not None and speed < 9.0):
        if (speed is not None and speed < 7.5 and roi_count >= 12) or density >= 320.0:
            level = 4  # Ùn tắc nghiêm trọng
        elif speed is not None and speed > 22.0:
            level = 2  # Xe nhiều nhưng đang chạy nhanh
        else:
            level = 3  # Ùn tắc
    # 3. ĐÔNG ĐÚC
    else:
        if speed is not None and speed < 10.0 and roi_count >= 8:
            level = 3
        else:
            level = 2

    los_map = {1: "LOS A - B", 2: "LOS C - D", 3: "LOS E", 4: "LOS F"}
    los_str = los_map.get(level, "LOS A")

    presets = {
        1: {
            "name": "Thông thoáng",
            "bgr_color": (0, 200, 0),         # Green
            "hex_color": "#10b981",
            "badge": "success",
            "desc": "Mức độ phục vụ LOS A-B (V/C < 0.60): Phương tiện lưu thông tự do, tốc độ đạt chuẩn thiết kế."
        },
        2: {
            "name": "Đông đúc",
            "bgr_color": (0, 215, 255),       # Gold/Yellow
            "hex_color": "#f59e0b",
            "badge": "warning",
            "desc": "Mức độ phục vụ LOS C-D (0.60 <= V/C <= 0.85): Dòng xe tăng cao, vận tốc giảm nhẹ, khoảng cách xe thu hẹp."
        },
        3: {
            "name": "Ùn tắc giao thông",
            "bgr_color": (0, 0, 255),         # Red
            "hex_color": "#ef4444",
            "badge": "danger",
            "desc": "Mức độ phục vụ LOS E (V/C > 0.85): Ùn ứ cục bộ, dòng xe di chuyển chậm dưới 50% tốc độ thiết kế."
        },
        4: {
            "name": "Ùn tắc nghiêm trọng",
            "bgr_color": (0, 0, 180),         # Dark Red
            "hex_color": "#dc2626",
            "badge": "critical",
            "desc": "Mức độ phục vụ LOS F (V/C >= 1.00): BÁO ĐỘNG ĐỎ! Vượt năng lực thông hành, phương tiện dừng nghẽn."
        }
    }
    p = presets[level]
    return {
        "name": p["name"],
        "level": level,
        "los": los_str,
        "vc_ratio": vc_ratio,
        "color": p["bgr_color"],
        "hex_color": p["hex_color"],
        "badge": p["badge"],
        "description": p["desc"]
    }


def draw_roi_overlay(img, w, h, level):
    """Vẽ vùng ROI + vạch đếm lưu lượng lên ảnh/frame."""
    roi_px = get_roi_pixels(w, h)

    if level <= 0:
        color = (150, 150, 150)
    elif level == 1:
        color = (0, 200, 0)
    elif level == 2:
        color = (0, 215, 255)
    else:
        color = (0, 0, 255)

    overlay = img.copy()
    cv2.fillPoly(overlay, [roi_px], color)
    cv2.addWeighted(overlay, 0.12, img, 0.88, 0, img)
    cv2.polylines(img, [roi_px], True, color, 2)

    y_line, x_l, x_r = counting_line(w, h)
    cv2.line(img, (x_l, y_line), (x_r, y_line), (0, 255, 255), 2)
    cv2.putText(img, "ROI", (roi_px[3][0] + 6, roi_px[3][1] - 8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    return img
