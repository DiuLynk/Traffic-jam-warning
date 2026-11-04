# -*- coding: utf-8 -*-
"""
Script tính toán và vẽ Ma trận tương quan giữa các biến đặc trưng (Feature Correlation Matrix)
phục vụ phân tích dữ liệu trước khi huấn luyện (EDA / Pre-training Analysis).
"""

import os
from pathlib import Path
from PIL import Image
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def main():
    cleaned_dir = Path(r"D:\doan2027-dieulinh-main\datasets\cleaned_traffic")
    reports_dir = Path(r"D:\doan2027-dieulinh-main\reports\data_cleaning")
    reports_dir.mkdir(parents=True, exist_ok=True)

    class_folders = ["0_Xe_may", "1_O_to_con", "2_Xe_khach", "3_Xe_tai"]
    features = []

    print("Dang thu thap dac trung anh tu cleaned_traffic...")
    for cls_idx, cname in enumerate(class_folders):
        cdir = cleaned_dir / cname
        if not cdir.exists():
            continue
        # Lay 250 anh moi lop (tong cong 1000 anh) dai dien cho toan bo tap du lieu
        files = list(cdir.glob("*.*"))[:250]
        for p in files:
            try:
                with Image.open(p).convert("RGB") as img:
                    arr = np.array(img, dtype=float)
                    # Grayscale
                    gray = 0.2989 * arr[:, :, 0] + 0.5870 * arr[:, :, 1] + 0.1140 * arr[:, :, 2]
                    brightness = float(np.mean(gray))
                    contrast = float(np.std(gray))
                    file_size = p.stat().st_size / 1024.0
                    
                    # Saturation (Do bao hoa mau)
                    max_c = np.max(arr, axis=2)
                    min_c = np.min(arr, axis=2)
                    sat = float(np.mean(np.where(max_c > 0, (max_c - min_c) / (max_c + 1e-5), 0)))
                    
                    # Sharpness (Do sac net dua tren gradient anh)
                    gx, gy = np.gradient(gray)
                    sharpness = float(np.mean(np.hypot(gx, gy)))
                    
                    features.append([brightness, contrast, sat, file_size, sharpness, cls_idx])
            except Exception:
                pass

    print(f"Thu thap thanh cong {len(features)} mau anh! Dang tinh ma tran tuong quan Pearson...")
    
    var_names_vn = [
        "Do sang\n(Brightness)",
        "Tuong phan\n(Contrast)",
        "Bao hoa mau\n(Saturation)",
        "Dung luong KB\n(File Size)",
        "Do sac net\n(Sharpness)",
        "Ma lop\n(Class ID)"
    ]

    feat_mat = np.array(features, dtype=float)
    feat_corr = np.corrcoef(feat_mat, rowvar=False)

    # Khoi tao bieu do heatmap
    fig, ax = plt.subplots(figsize=(9, 7.5), dpi=220)
    cax = ax.matshow(feat_corr, cmap="coolwarm", vmin=-1.0, vmax=1.0)
    cbar = fig.colorbar(cax, fraction=0.046, pad=0.04)
    cbar.set_label("He so tuong quan Pearson (r)", fontsize=11, fontweight="bold")

    n_vars = len(var_names_vn)
    ax.set_xticks(range(n_vars))
    ax.set_yticks(range(n_vars))
    ax.set_xticklabels(var_names_vn, fontsize=9.5, fontweight="bold")
    ax.set_yticklabels(var_names_vn, fontsize=9.5, fontweight="bold")
    ax.set_title("MA TRAN TUONG QUAN GIUA CAC BIEN DAC TRUNG HINH ANH\n(Feature Correlation Matrix - Pre-training)", 
                 fontsize=12, fontweight="bold", pad=25)

    # Dien gia tri r vao tung o
    for i in range(n_vars):
        for j in range(n_vars):
            val = feat_corr[i, j]
            color_text = "white" if abs(val) > 0.45 else "black"
            ax.text(j, i, f"{val:+.2f}", ha="center", va="center", color=color_text, fontweight="bold", fontsize=11)

    plt.tight_layout()
    corr_path = reports_dir / "3_feature_correlation_matrix.png"
    plt.savefig(corr_path, dpi=220)
    plt.close()
    print(f"Da tao thanh cong bieu do: {corr_path}")

if __name__ == "__main__":
    main()
