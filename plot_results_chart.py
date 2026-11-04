# -*- coding: utf-8 -*-
"""
Vẽ đồ thị kết quả huấn luyện chuẩn định dạng YOLOv8 (results.png & results_all_metrics.png)
Mô phỏng chính xác phong cách đồ thị của Ultralytics YOLO:
- Đường màu xanh kèm điểm tròn biểu diễn 'results'
- Đường màu cam nét chấm biểu diễn 'smooth'
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

def smooth_curve(y, span=7):
    """Tính đường cong làm mịn (smooth curve) bằng Exponential Moving Average."""
    s = pd.Series(y).ewm(span=span, adjust=False).mean().values
    return s

def plot_charts():
    base_dir = Path(r"D:\doan2027-dieulinh-main\runs\classify\deep_train_results\yolov8s-cls_100ep")
    csv_path = base_dir / "results_excel.csv"
    
    # Đọc dữ liệu với sep=; và decimal=,
    df = pd.read_csv(csv_path, sep=";", skiprows=1, decimal=",")
    
    epochs = df["Epoch"].values
    
    # Thiết lập phong cách matplotlib chuẩn
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.size"] = 9
    plt.rcParams["axes.titlesize"] = 10
    plt.rcParams["axes.labelsize"] = 9
    plt.rcParams["xtick.labelsize"] = 8.5
    plt.rcParams["ytick.labelsize"] = 8.5
    
    # =========================================================================
    # 1. BIỂU ĐỒ 2x2: CHUẨN Y HỆT HÌNH ẢNH MẪU YOLOV8-CLS
    # (train/loss, metrics/accuracy_top1, val/loss, metrics/accuracy_top5)
    # =========================================================================
    fig, axes = plt.subplots(2, 2, figsize=(6.2, 7.0), dpi=300)
    
    plots_config_2x2 = [
        (0, 0, "train/loss", df["Train Loss"].values),
        (0, 1, "metrics/accuracy_top1", df["Accuracy (Top-1)"].values),
        (1, 0, "val/loss", df["Val Loss"].values),
        (1, 1, "metrics/accuracy_top5", df["Top-5 Acc"].values)
    ]
    
    for r, c, title, y in plots_config_2x2:
        ax = axes[r, c]
        y_smooth = smooth_curve(y, span=6)
        
        # Đường xanh + chấm tròn (results)
        line1, = ax.plot(epochs, y, color="#1f77b4", marker="o", markersize=2.2, linewidth=1.1, label="results")
        # Đường cam chấm chấm (smooth)
        line2, = ax.plot(epochs, y_smooth, color="#ff7f0e", linestyle=":", linewidth=1.3, label="smooth")
        
        ax.set_title(title, pad=6)
        ax.set_xlim(-2, 105)
        ax.set_xticks([0, 25, 50, 75, 100])
        
        # Nếu là accuracy_top5, đặt giới hạn y đẹp
        if "top5" in title:
            ax.set_ylim(0.95, 1.05)
            
        # Thêm chú thích legend vào ô metrics/accuracy_top1
        if r == 0 and c == 1:
            ax.legend(loc="lower right", fontsize=8, framealpha=0.8)
            
        ax.set_box_aspect(1)
        
    plt.tight_layout()
    results_path = base_dir / "results.png"
    plt.savefig(results_path, dpi=300)
    plt.close()
    print(f"Created: {results_path}")
    
    # =========================================================================
    # 2. BIỂU ĐỒ MỞ RỘNG (3x3): ĐẦY ĐỦ TẤT CẢ CÁC CHỈ SỐ THEO YÊU CẦU
    # (train/loss, val/loss, top1, precision, recall, f1, mAP50, mAP50-95, top5)
    # =========================================================================
    fig, axes = plt.subplots(3, 3, figsize=(9.5, 9.8), dpi=300)
    
    all_metrics_config = [
        (0, 0, "train/loss", df["Train Loss"].values),
        (0, 1, "val/loss", df["Val Loss"].values),
        (0, 2, "metrics/accuracy_top1", df["Accuracy (Top-1)"].values),
        (1, 0, "metrics/precision", df["Precision"].values),
        (1, 1, "metrics/recall", df["Recall"].values),
        (1, 2, "metrics/f1_score", df["F1-Score"].values),
        (2, 0, "metrics/mAP50", df["mAP50"].values),
        (2, 1, "metrics/mAP50-95", df["mAP50-95"].values),
        (2, 2, "metrics/accuracy_top5", df["Top-5 Acc"].values)
    ]
    
    for r, c, title, y in all_metrics_config:
        ax = axes[r, c]
        y_smooth = smooth_curve(y, span=6)
        
        ax.plot(epochs, y, color="#1f77b4", marker="o", markersize=2.2, linewidth=1.1, label="results")
        ax.plot(epochs, y_smooth, color="#ff7f0e", linestyle=":", linewidth=1.3, label="smooth")
        
        ax.set_title(title, pad=6)
        ax.set_xlim(-2, 105)
        ax.set_xticks([0, 25, 50, 75, 100])
        
        if "top5" in title:
            ax.set_ylim(0.95, 1.05)
            
        if r == 0 and c == 2:
            ax.legend(loc="lower right", fontsize=8, framealpha=0.8)
            
        ax.set_box_aspect(1)
        
    plt.tight_layout()
    all_metrics_path = base_dir / "results_all_metrics.png"
    plt.savefig(all_metrics_path, dpi=300)
    plt.close()
    print(f"Created: {all_metrics_path}")

if __name__ == "__main__":
    plot_charts()
