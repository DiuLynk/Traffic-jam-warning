"""
backend/core/telegram_notifier.py - Module phát cảnh báo ùn tắc qua Telegram Bot.

Đặc điểm:
- Gửi bất đồng bộ (Thread) hoàn toàn không ảnh hưởng đến FPS xử lý video của camera.
- Tự động mã hóa ảnh chụp hiện trường (có vẽ khung và thông số) đính kèm tin nhắn.
- Cơ chế Cooldown thông minh: tránh spam tin nhắn liên tục khi đoạn đường bị kẹt xe kéo dài.
- Tương thích cấu hình tập trung từ config.py và file .env.
"""
import io
import time
import threading
import urllib.request
import urllib.parse
import json
import cv2
import numpy as np

try:
    from config import (
        TELEGRAM_BOT_TOKEN,
        TELEGRAM_CHAT_ID,
        TELEGRAM_ALERT_ENABLED,
        TELEGRAM_COOLDOWN_SEC,
    )
except ImportError:
    TELEGRAM_BOT_TOKEN = "8725237057:AAEdJdaQQCRJfLRD47HM-pFmiMz3vZurD4Y"
    TELEGRAM_CHAT_ID = "8368719317"
    TELEGRAM_ALERT_ENABLED = True
    TELEGRAM_COOLDOWN_SEC = 180

# Quản lý thời gian cảnh báo gần nhất theo từng Camera để tránh spam
_cooldown_lock = threading.Lock()
_last_alert_times = {}


def is_configured() -> bool:
    """Kiểm tra xem thông số Bot Token và Chat ID đã hợp lệ chưa."""
    token = (TELEGRAM_BOT_TOKEN or "").strip()
    chat_id = str(TELEGRAM_CHAT_ID or "").strip()
    return bool(token and chat_id and ":" in token)


def should_alert(camera_id: str, force: bool = False, cooldown_sec: int = None) -> bool:
    """Kiểm tra thời gian cooldown cho từng camera."""
    if force:
        return True
    if not TELEGRAM_ALERT_ENABLED:
        return False
    if not is_configured():
        return False

    cd = cooldown_sec if cooldown_sec is not None else TELEGRAM_COOLDOWN_SEC
    now = time.time()
    with _cooldown_lock:
        last_time = _last_alert_times.get(str(camera_id), 0.0)
        if now - last_time < cd:
            return False
        _last_alert_times[str(camera_id)] = now
        return True


def _send_telegram_http(caption_or_text: str, frame: np.ndarray = None) -> dict:
    """
    Thực hiện gửi HTTP Request tới Telegram Bot API.
    Nếu có ảnh frame, gửi qua endpoint sendPhoto (multipart/form-data).
    Nếu không, gửi qua endpoint sendMessage (url-encoded).
    """
    token = (TELEGRAM_BOT_TOKEN or "").strip()
    chat_id = str(TELEGRAM_CHAT_ID or "").strip()

    if not token or not chat_id:
        return {"ok": False, "error": "Chưa cấu hình Telegram Token hoặc Chat ID"}

    if frame is not None and isinstance(frame, np.ndarray) and frame.size > 0:
        # Mã hóa frame thành JPEG
        ret, jpeg_buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if ret:
            url = f"https://api.telegram.org/bot{token}/sendPhoto"
            boundary = f"----WebKitFormBoundary{int(time.time() * 1000)}"

            body = bytearray()
            # Trường chat_id
            body.extend(f"--{boundary}\r\nContent-Disposition: form-data; name=\"chat_id\"\r\n\r\n{chat_id}\r\n".encode("utf-8"))
            # Trường parse_mode
            body.extend(f"--{boundary}\r\nContent-Disposition: form-data; name=\"parse_mode\"\r\n\r\nHTML\r\n".encode("utf-8"))
            # Trường caption
            body.extend(f"--{boundary}\r\nContent-Disposition: form-data; name=\"caption\"\r\n\r\n{caption_or_text}\r\n".encode("utf-8"))
            # Trường photo file
            body.extend(f"--{boundary}\r\nContent-Disposition: form-data; name=\"photo\"; filename=\"alert_{int(time.time())}.jpg\"\r\nContent-Type: image/jpeg\r\n\r\n".encode("utf-8"))
            body.extend(jpeg_buffer.tobytes())
            body.extend(f"\r\n--{boundary}--\r\n".encode("utf-8"))

            req = urllib.request.Request(
                url,
                data=bytes(body),
                headers={
                    "Content-Type": f"multipart/form-data; boundary={boundary}",
                    "User-Agent": "TrafficVisionAI-TelegramNotifier/1.0"
                }
            )
            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    res_data = json.loads(resp.read().decode("utf-8"))
                    return res_data
            except Exception as e:
                # Nếu gửi ảnh lỗi, fallback xuống gửi văn bản
                print(f"[TelegramNotifier] Lỗi gửi ảnh ({e}), thử gửi lại bằng văn bản...")

    # Gửi văn bản đơn giản
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    post_data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": caption_or_text,
        "parse_mode": "HTML"
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=post_data,
        headers={"User-Agent": "TrafficVisionAI-TelegramNotifier/1.0"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def send_congestion_alert(
    camera_id: str,
    congestion_level: int,
    congestion_name: str,
    los: str = "",
    roi_count: int = 0,
    density: float = 0.0,
    speed: float = 0.0,
    vc_ratio: float = None,
    advice: str = None,
    frame: np.ndarray = None,
    force: bool = False
) -> bool:
    """
    Tạo nội dung cảnh báo và gửi đến Telegram.
    Hàm này chạy đồng bộ (thường được bọc trong send_congestion_alert_async).
    """
    if not should_alert(camera_id, force=force):
        return False

    # Chọn biểu tượng theo mức độ nghiêm trọng
    if congestion_level >= 4:
        header_icon = "🚨🚨🚨"
        level_title = "ÙN TẮC NGHIÊM TRỌNG (BÁO ĐỘNG ĐỎ)"
    elif congestion_level == 3:
        header_icon = "⚠️⚠️"
        level_title = "ÙN TẮC GIAO THÔNG (MỨC 3)"
    else:
        header_icon = "ℹ️"
        level_title = f"{congestion_name.upper()} (MỨC {congestion_level})"

    now_str = time.strftime("%H:%M:%S · %d/%m/%Y")
    vc_str = f" · <b>V/C:</b> {vc_ratio:.2f}" if vc_ratio is not None else ""
    advice_block = f"\n💡 <b>Điều tiết khuyến nghị:</b>\n<i>{advice}</i>\n" if advice else ""

    message = (
        f"{header_icon} <b>CẢNH BÁO GIAO THÔNG TỰ ĐỘNG</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📹 <b>Vị trí:</b> {camera_id}\n"
        f"🚦 <b>Trạng thái:</b> <b>{level_title}</b>\n"
        f"📈 <b>Mức phục vụ:</b> {los or 'N/A'}\n"
        f"🚗 <b>Phương tiện trong ROI:</b> <b>{roi_count} xe</b>\n"
        f"📏 <b>Mật độ dòng xe:</b> {density:.1f} xe/km\n"
        f"⚡ <b>Vận tốc trung bình:</b> {speed:.1f} km/h{vc_str}\n"
        f"{advice_block}"
        f"⏰ <b>Thời gian:</b> {now_str}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🤖 <i>TrafficVision AI Monitoring System</i>"
    )

    try:
        res = _send_telegram_http(message, frame=frame)
        if res.get("ok"):
            print(f"[TelegramNotifier] [OK] Da gui canh bao {camera_id} (Level {congestion_level}) thanh cong!")
            return True
        else:
            print(f"[TelegramNotifier] [FAIL] Gui that bai: {res.get('description')}")
            return False
    except Exception as exc:
        print(f"[TelegramNotifier] [ERROR] Loi ket noi Telegram API: {exc}")
        return False


def send_congestion_alert_async(
    camera_id: str,
    congestion_level: int,
    congestion_name: str,
    los: str = "",
    roi_count: int = 0,
    density: float = 0.0,
    speed: float = 0.0,
    vc_ratio: float = None,
    advice: str = None,
    frame: np.ndarray = None,
    force: bool = False
):
    """
    Bọc hàm gửi cảnh báo trong một Thread ngầm.
    Không bao giờ làm nghẽn hoặc sụt FPS xử lý luồng camera!
    """
    # Tạo bản copy an toàn của frame nếu có để tránh race condition khi frame gốc bị ghi đè
    frame_copy = frame.copy() if frame is not None and isinstance(frame, np.ndarray) else None

    t = threading.Thread(
        target=send_congestion_alert,
        kwargs={
            "camera_id": camera_id,
            "congestion_level": congestion_level,
            "congestion_name": congestion_name,
            "los": los,
            "roi_count": roi_count,
            "density": density,
            "speed": speed,
            "vc_ratio": vc_ratio,
            "advice": advice,
            "frame": frame_copy,
            "force": force
        },
        daemon=True
    )
    t.start()
    return t


def test_telegram_alert(camera_id: str = None, worker = None) -> bool:
    """
    Gửi thông báo kiểm tra / cảnh báo thử nghiệm cho đúng camera được chọn.
    Tự động trích xuất frame ảnh và chỉ số thực tế từ CameraWorker nếu có.
    """
    if worker is not None:
        cam_id = getattr(worker, "cam_id", "CAM-01")
        cam_name = getattr(worker, "name", None) or getattr(worker, "cam_name", "Camera giám sát")
        cam_label = f"{cam_id} · {cam_name}"
        metrics = getattr(worker, "metrics", {}) or {}
        roi_count = metrics.get("total_vehicles", metrics.get("roi_count", 0))
        density = metrics.get("density", 0.0)
        speed = metrics.get("speed", 0.0)
        cg_lvl = max(2, metrics.get("congestion_level", 2))
        cg_name = metrics.get("congestion_name", "Đông đúc")
        los = metrics.get("los", "LOS C - D")
        vc = metrics.get("vc_ratio", 0.72)
        advice = f"Cảnh báo thử nghiệm trực tiếp từ trạm {cam_id}. Trạng thái giám sát thời gian thực hoạt động ổn định."

        # Trích xuất ảnh thực tế từ bộ đệm của camera worker
        frame = None
        if hasattr(worker, "latest_jpeg_high") and worker.latest_jpeg_high:
            try:
                frame = cv2.imdecode(np.frombuffer(worker.latest_jpeg_high, np.uint8), cv2.IMREAD_COLOR)
            except Exception:
                frame = None

        return send_congestion_alert(
            camera_id=cam_label,
            congestion_level=cg_lvl,
            congestion_name=cg_name,
            los=los,
            roi_count=roi_count,
            density=density,
            speed=speed,
            vc_ratio=vc,
            advice=advice,
            frame=frame,
            force=True
        )

    # Nếu không có worker nhưng có camera_id truyền vào
    target_id = camera_id or "CAM-01"
    clean_id = target_id.split()[0] if " " in target_id else target_id
    cam_label = f"{clean_id} · Trạm giám sát giao thông ({clean_id})"

    return send_congestion_alert(
        camera_id=cam_label,
        congestion_level=2,
        congestion_name="Đông đúc (Thử nghiệm)",
        los="LOS C - D",
        roi_count=12,
        density=145.0,
        speed=28.5,
        vc_ratio=0.68,
        advice=f"Thử nghiệm gửi cảnh báo từ trạm {clean_id} thành công. Hệ thống sẵn sàng phát cảnh báo tự động.",
        force=True
    )

