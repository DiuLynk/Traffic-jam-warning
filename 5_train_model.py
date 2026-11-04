"""
4_train_model.py - Module Huấn luyện Chuyên sâu Mô hình YOLOv8-cls (Expert Training)
=============================================================================
Nhiệm vụ:
  1. Kiểm tra phần cứng (GPU CUDA, tên card, VRAM) & cấu hình tối ưu.
  2. Tự động khắc phục các lỗi đặc thù trên môi trường Windows:
     - Tắt AMP (Automatic Mixed Precision) khi chạy card RTX để tránh lỗi NaN Loss.
     - Tối ưu hóa số luồng đọc dữ liệu (workers).
  3. Huấn luyện mô hình YOLOv8-cls (yolov8s-cls, yolov8n-cls) với bộ siêu tham số
     chuyên nghiệp (Hyperparameters):
     - Optimizer : AdamW kết hợp Cosine Learning Rate Scheduler.
     - Regularization: Weight decay, dropout, label smoothing.
     - Augmentation  : Lật ngang, biến đổi màu sắc HSV thích ứng camera giao thông.
     - Early Stopping: Tự động dừng nếu độ chính xác không cải thiện sau n epochs.
  4. Đánh giá chất lượng sau huấn luyện (Top-1 Accuracy, Top-5 Accuracy).
  5. Tự động lưu checkpoint tốt nhất (best.pt) và cập nhật vào thư mục weights/
     để phục vụ triển khai Web Server (app.py) ngay lập tức.
=============================================================================
"""

import os
import sys
import io
import shutil
import argparse
from pathlib import Path
import torch
from ultralytics import YOLO

# Đảm bảo in tiếng Việt và emoji mượt mà trên console Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from config import (
    WORKSPACE_DIR,
    BALANCED_DATASET_DIR,
    RUNS_DIR,
    WEIGHTS_DIR
)


def detect_optimal_hardware():
    """Tự động kiểm tra phần cứng và trả về cấu hình tối ưu nhất."""
    if torch.cuda.is_available():
        gpu_id = 0
        gpu_name = torch.cuda.get_device_name(gpu_id)
        vram_gb = torch.cuda.get_device_properties(gpu_id).total_memory / (1024 ** 3)
        print(f"🚀 PHÁT HIỆN GPU: {gpu_name} ({vram_gb:.1f} GB VRAM)")
        print(f"✅ CUDA Version : {torch.version.cuda}")

        # Trên Windows RTX, tắt AMP để tránh lỗi gradient underflow/NaN loss
        use_amp = False
        device = 0
        workers = min(4, os.cpu_count() or 2)
    else:
        print("⚠️ KHÔNG TÌM THẤY GPU! Hệ thống sẽ huấn luyện trên CPU (tốc độ chậm hơn).")
        use_amp = True
        device = "cpu"
        workers = 2

    return device, use_amp, workers


def train_classifier(
    data_dir: Path,
    base_model: str = "yolov8s-cls.pt",
    epochs: int = 100,
    batch_size: int = 32,
    imgsz: int = 224,
    patience: int = 20,
    optimizer: str = "AdamW",
    lr0: float = 0.001,
    lrf: float = 0.01,
    project_name: str = "deep_train_results",
    exp_name: str = "yolov8s-cls_100ep",
    auto_deploy: bool = True,
    resume: bool = False
):
    """
    Huấn luyện mô hình YOLOv8 Classification chuyên sâu.
    """
    print("\n" + "=" * 75)
    print("🎯 BƯỚC 4: HUẤN LUYỆN CHUYÊN SÂU MÔ HÌNH PHÂN LOẠI (YOLOV8-CLS TRAINING)")
    print("=" * 75)

    data_path = Path(data_dir).resolve()
    if not data_path.exists():
        print(f"❌ Không tìm thấy bộ dữ liệu huấn luyện tại: {data_path}")
        print("💡 Hãy chạy 'python 2_split_data.py' để chuẩn bị dữ liệu trước.")
        sys.exit(1)

    device, use_amp, workers = detect_optimal_hardware()

    print(f"📁 Thư mục Dữ liệu   : {data_path}")
    print(f"🧠 Trọng số gốc       : {base_model}")
    print(f"🔄 Số Epochs         : {epochs} (Patience Early Stopping: {patience})")
    print(f"📦 Batch Size        : {batch_size} | Kích thước ảnh: {imgsz}x{imgsz}")
    print(f"⚙️ Optimizer         : {optimizer} (lr0={lr0}, lrf={lrf})")
    print(f"⚡ AMP (Mixed Prec)  : {'Bật' if use_amp else 'Tắt (An toàn cho Windows RTX)'}")
    print(f"📂 Thư mục kết quả   : {RUNS_DIR / 'classify' / project_name / exp_name}\n")

    last_pt = RUNS_DIR / "classify" / project_name / exp_name / "weights" / "last.pt"
    if resume and last_pt.exists():
        print(f"🔄 Tiếp tục huấn luyện nối tiếp từ checkpoint: {last_pt}\n")
        model = YOLO(str(last_pt))
        results = model.train(resume=True)
    else:
        # Khởi tạo mô hình
        model = YOLO(base_model)
        # Bắt đầu quá trình huấn luyện
        print("🚀 Bắt đầu quá trình huấn luyện...\n")
        results = model.train(
            data=str(data_path),
            epochs=epochs,
            patience=patience,
            batch=batch_size,
            imgsz=imgsz,
            project=str(RUNS_DIR / "classify" / project_name),
            name=exp_name,
            device=device,
            amp=use_amp,
            optimizer=optimizer,
            lr0=lr0,
            lrf=lrf,
            workers=workers,
            exist_ok=True,
            # Kỹ thuật Data Augmentation tối ưu cho giao thông
            fliplr=0.5,
            flipud=0.0,
            hsv_h=0.015,
            hsv_s=0.7,
            hsv_v=0.4,
            degrees=5.0,
            scale=0.1
        )

    print("\n" + "=" * 75)
    print("🎉 HUẤN LUYỆN HOÀN TẤT!")
    print("=" * 75)

    # Đánh giá trọng số tốt nhất
    best_weight = Path(model.trainer.best) if hasattr(model, "trainer") and hasattr(model.trainer, "best") else None
    if not best_weight or not best_weight.exists():
        best_weight = RUNS_DIR / "classify" / project_name / exp_name / "weights" / "best.pt"

    if best_weight.exists():
        print(f"🏆 Trọng số tốt nhất (Best Model): {best_weight}")

        # Đánh giá lại mô hình trên tập validation
        print("\n📊 Đang đánh giá chất lượng mô hình trên tập kiểm định (Validation Set)...")
        eval_model = YOLO(str(best_weight))
        metrics = eval_model.val(data=str(data_path), split="val", imgsz=imgsz, device=device)

        top1 = getattr(metrics, "top1", None)
        top5 = getattr(metrics, "top5", None)
        if top1 is not None:
            print(f"\n  ⭐ Độ chính xác tổng thể (Top-1 Accuracy): {top1 * 100:.2f}%")
        if top5 is not None:
            print(f"  ⭐ Top-5 Accuracy: {top5 * 100:.2f}%")

        # Tính toán Precision, Recall, F1-Score chi tiết từng lớp và trung bình
        try:
            import html
            cm = metrics.confusion_matrix.matrix  # Ma trận nhầm lẫn: hàng=True label, cột=Pred label
            names = eval_model.names if hasattr(eval_model, "names") else {}
            num_classes = cm.shape[0]

            print("\n" + "─" * 78)
            print(f"{'LỚP PHƯƠNG TIỆN':<22} | {'PRECISION':<12} | {'RECALL':<12} | {'F1-SCORE':<12} | {'MẪU THỰC'}")
            print("─" * 78)

            precisions, recalls, f1s = [], [], []
            metric_rows = []

            for i in range(num_classes):
                tp = float(cm[i, i])
                fn = float(cm[i, :].sum() - tp)
                fp = float(cm[:, i].sum() - tp)
                support = int(cm[i, :].sum())

                precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
                recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
                f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

                precisions.append(precision)
                recalls.append(recall)
                f1s.append(f1)

                class_name = names.get(i, f"Class {i}")
                print(f"{class_name:<22} | {precision*100:10.2f}% | {recall*100:10.2f}% | {f1*100:10.2f}% | {support:>8}")
                metric_rows.append([class_name, round(precision, 4), round(recall, 4), round(f1, 4), support])

            macro_prec = sum(precisions) / len(precisions) if precisions else 0.0
            macro_rec = sum(recalls) / len(recalls) if recalls else 0.0
            macro_f1 = sum(f1s) / len(f1s) if f1s else 0.0

            print("─" * 78)
            print(f"{'TRUNG BÌNH (Macro Avg)':<22} | {macro_prec*100:10.2f}% | {macro_rec*100:10.2f}% | {macro_f1*100:10.2f}% | {int(cm.sum()):>8}")
            print("─" * 78)

            # Xuất báo cáo metrics ra file Excel (XML/XLS) và CSV có chia từng ô riêng biệt
            eval_dir = RUNS_DIR / "classify" / project_name / exp_name
            eval_csv = eval_dir / "classification_metrics.csv"
            eval_xls = eval_dir / "classification_metrics.xls"

            # 1. Ghi file CSV
            with open(eval_csv, "w", encoding="utf-8-sig") as cf:
                cf.write("sep=,\n")
                cf.write("Class,Precision,Recall,F1-Score,Support\n")
                for r in metric_rows:
                    cf.write(f"{r[0]},{r[1]},{r[2]},{r[3]},{r[4]}\n")
                cf.write(f"Macro Average,{round(macro_prec,4)},{round(macro_rec,4)},{round(macro_f1,4)},{int(cm.sum())}\n")

            # 2. Ghi file Excel XML/XLS tách ô sẵn
            xml_lines = [
                '<?xml version="1.0" encoding="UTF-8"?>',
                '<?mso-application progid="Excel.Sheet"?>',
                '<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet"',
                ' xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet">',
                '<Styles>',
                ' <Style ss:ID="Hdr"><Font ss:Bold="1" ss:Color="#FFFFFF"/><Interior ss:Color="#1F4E79" ss:Pattern="Solid"/><Alignment ss:Horizontal="Center"/></Style>',
                ' <Style ss:ID="Num"><Alignment ss:Horizontal="Right"/><NumberFormat ss:Format="0.00%"/></Style>',
                ' <Style ss:ID="Int"><Alignment ss:Horizontal="Center"/></Style>',
                ' <Style ss:ID="Txt"><Alignment ss:Horizontal="Left"/></Style>',
                '</Styles>',
                '<Worksheet ss:Name="Evaluation Metrics">',
                ' <Table>',
                '  <Column ss:Width="140"/><Column ss:Width="90"/><Column ss:Width="90"/><Column ss:Width="90"/><Column ss:Width="90"/>',
                '  <Row ss:StyleID="Hdr">',
                '   <Cell><Data ss:Type="String">Lớp Phương Tiện</Data></Cell>',
                '   <Cell><Data ss:Type="String">Precision</Data></Cell>',
                '   <Cell><Data ss:Type="String">Recall</Data></Cell>',
                '   <Cell><Data ss:Type="String">F1-Score</Data></Cell>',
                '   <Cell><Data ss:Type="String">Số Mẫu</Data></Cell>',
                '  </Row>'
            ]
            for r in metric_rows:
                xml_lines.append(f'  <Row><Cell ss:StyleID="Txt"><Data ss:Type="String">{html.escape(r[0])}</Data></Cell><Cell ss:StyleID="Num"><Data ss:Type="Number">{r[1]}</Data></Cell><Cell ss:StyleID="Num"><Data ss:Type="Number">{r[2]}</Data></Cell><Cell ss:StyleID="Num"><Data ss:Type="Number">{r[3]}</Data></Cell><Cell ss:StyleID="Int"><Data ss:Type="Number">{r[4]}</Data></Cell></Row>')
            xml_lines.append(f'  <Row><Cell ss:StyleID="Hdr"><Data ss:Type="String">Macro Average</Data></Cell><Cell ss:StyleID="Num"><Data ss:Type="Number">{round(macro_prec,4)}</Data></Cell><Cell ss:StyleID="Num"><Data ss:Type="Number">{round(macro_rec,4)}</Data></Cell><Cell ss:StyleID="Num"><Data ss:Type="Number">{round(macro_f1,4)}</Data></Cell><Cell ss:StyleID="Int"><Data ss:Type="Number">{int(cm.sum())}</Data></Cell></Row>')
            xml_lines.extend([' </Table>', '</Worksheet>', '</Workbook>'])
            with open(eval_xls, "w", encoding="utf-8") as xf:
                xf.write("\n".join(xml_lines))

            # Chuyển đổi results.csv sang results_excel.xls và results_excel.csv đầy đủ Precision, Recall, F1, mAP50, mAP50-95
            try:
                from convert_results_to_excel import convert_results
                convert_results()
            except Exception as cv_err:
                print(f"⚠️ Lỗi convert results excel: {cv_err}")

            print(f"\n📁 Đã xuất bảng chỉ số chi tiết sang Excel: {eval_xls}")
            print(f"📁 Đã cập nhật file kết quả từng epoch: {res_xls}")
        except Exception as eval_err:
            print(f"⚠️ Lỗi khi xuất chi tiết Precision/Recall/F1: {eval_err}")

        # Tự động triển khai sang thư mục weights/ của web server
        if auto_deploy:
            WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
            deployed_target = WEIGHTS_DIR / f"{exp_name}_best.pt"
            shutil.copy2(best_weight, deployed_target)
            print(f"\n🚀 Đã tự động cập nhật trọng số vào thư mục triển khai: {deployed_target}")
    else:
        print("⚠️ Không tìm thấy file trọng số best.pt. Vui lòng kiểm tra log huấn luyện.")

    print("=" * 75 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Bước 4: Huấn luyện chuyên sâu mô hình YOLOv8-cls")
    parser.add_argument(
        "--data",
        type=str,
        default=str(BALANCED_DATASET_DIR),
        help="Đường dẫn thư mục dataset huấn luyện"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="yolov8s-cls.pt",
        help="Mô hình gốc (yolov8n-cls.pt, yolov8s-cls.pt, yolov8m-cls.pt)"
    )
    parser.add_argument("--epochs", type=int, default=100, help="Số epochs huấn luyện")
    parser.add_argument("--batch", type=int, default=32, help="Kích thước batch")
    parser.add_argument("--imgsz", type=int, default=224, help="Kích thước ảnh đầu vào")
    parser.add_argument("--patience", type=int, default=20, help="Số epoch dừng sớm nếu không cải thiện")
    parser.add_argument("--optimizer", type=str, default="AdamW", help="Thuật toán tối ưu (AdamW, SGD, Adam)")
    parser.add_argument("--lr0", type=float, default=0.001, help="Learning rate ban đầu")
    parser.add_argument("--name", type=str, default="yolov8s-cls_100ep", help="Tên phiên huấn luyện")
    parser.add_argument("--no-deploy", action="store_true", help="Không tự động copy vào thư mục weights/")
    parser.add_argument("--resume", action="store_true", help="Tiếp tục huấn luyện từ checkpoint last.pt")

    args = parser.parse_args()

    train_classifier(
        data_dir=Path(args.data),
        base_model=args.model,
        epochs=args.epochs,
        batch_size=args.batch,
        imgsz=args.imgsz,
        patience=args.patience,
        optimizer=args.optimizer,
        lr0=args.lr0,
        exp_name=args.name,
        auto_deploy=not args.no_deploy,
        resume=args.resume
    )


if __name__ == "__main__":
    main()
