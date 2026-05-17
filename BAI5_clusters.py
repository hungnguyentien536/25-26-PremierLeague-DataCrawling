import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from mpl_toolkits.mplot3d import Axes3D

# Lấy thư mục chứa file code
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, "25-26_PremierLeague_Players.csv")

# Đọc dữ liệu
df = pd.read_csv(csv_path)
df.replace('N/a', np.nan, inplace=True)

# Xác định các cột số (tiêu chí phân cụm)
cols_to_exclude = ['STT', 'Tên cầu thủ', 'Nation', 'Pos', 'Squad', 'Age', 'Born', 'Matches', 'Rk']
numeric_cols = [col for col in df.columns if col not in cols_to_exclude]

print("=" * 80)
print("TIÊU CHÍ PHÂN CỤM CẦU THỦ (CLUSTERING CRITERIA)")
print("=" * 80)
print(f"\nTổng số tiêu chí: {len(numeric_cols)}\n")
for idx, col in enumerate(numeric_cols, 1):
    print(f"{idx:2d}. {col}")
print("\n" + "=" * 80)

# Chuẩn bị dữ liệu số
df_numeric = df[numeric_cols].copy()
for col in numeric_cols:
    df_numeric[col] = pd.to_numeric(df_numeric[col], errors='coerce')

# Điền giá trị thiếu
df_numeric.fillna(df_numeric.mean(), inplace=True)

# Chuẩn hóa dữ liệu
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df_numeric)

# Tìm số cụm tối ưu
print("\nĐang tính toán số cụm tối ưu...")
wcss = []
silhouette_scores = []
K_range = range(2, 11)

for k in K_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(X_scaled)
    wcss.append(kmeans.inertia_)
    silhouette_scores.append(silhouette_score(X_scaled, kmeans.labels_))

# Vẽ biểu đồ Elbow và Silhouette
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
fig.patch.set_facecolor('#121212')

ax1.plot(K_range, wcss, marker='o', linewidth=2, markersize=8, color='#00A8FF')
ax1.set_title('Biểu đồ Elbow', fontsize=12, fontweight='bold', color='white')
ax1.set_xlabel('Số lượng cụm (k)', fontsize=11, color='white')
ax1.set_ylabel('WCSS', fontsize=11, color='white')
ax1.set_facecolor('#1E1E1E')
ax1.grid(True, alpha=0.3)
ax1.tick_params(colors='white')

ax2.plot(K_range, silhouette_scores, marker='s', linewidth=2, markersize=8, color='#2ED573')
ax2.set_title('Biểu đồ Silhouette', fontsize=12, fontweight='bold', color='white')
ax2.set_xlabel('Số lượng cụm (k)', fontsize=11, color='white')
ax2.set_ylabel('Silhouette Score', fontsize=11, color='white')
ax2.set_facecolor('#1E1E1E')
ax2.grid(True, alpha=0.3)
ax2.tick_params(colors='white')

plt.tight_layout()
plt.show()

# Chọn số cụm tối ưu
optimal_k = K_range[np.argmax(silhouette_scores)]
print(f"\nSố cụm tối ưu: {optimal_k}")
print(f"Silhouette Score tốt nhất: {max(silhouette_scores):.4f}\n")

# Áp dụng K-means với số cụm tối ưu
kmeans_final = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
clusters = kmeans_final.fit_predict(X_scaled)
df['Cluster'] = clusters

# ===== PHÂN TÍCH ĐẶC ĐIỂM TỪNG CỤM =====
print("=" * 80)
print("PHÂN TÍCH ĐẶC ĐIỂM CỦA TỪNG CỤM")
print("=" * 80)

cluster_profiles = []
for cluster_id in range(optimal_k):
    cluster_mask = clusters == cluster_id
    cluster_count = cluster_mask.sum()
    
    print(f"\n📊 CỤM {cluster_id} ({cluster_count} cầu thủ):")
    print("-" * 80)
    
    # Tính trung bình các tiêu chí cho cụm này
    cluster_mean = df_numeric[cluster_mask].mean()
    cluster_profiles.append(cluster_mean)
    
    # Sắp xếp theo giá trị cao nhất
    top_features = cluster_mean.nlargest(5)
    low_features = cluster_mean.nsmallest(5)
    
    print("  ⬆️  Top 5 Tiêu chí cao nhất:")
    for feat, val in top_features.items():
        print(f"      • {feat}: {val:.2f}")
    
    print("\n  ⬇️  Top 5 Tiêu chí thấp nhất:")
    for feat, val in low_features.items():
        print(f"      • {feat}: {val:.2f}")

# Lưu kết quả phân cụm
output_file = os.path.join(script_dir, "25-26_PremierLeague_Clusters.csv")
df.to_csv(output_file, index=False)
print(f"\n✓ Đã lưu kết quả phân cụm vào {output_file}\n")

# ===== PCA ANALYSIS =====
pca_2d = PCA(n_components=2)
X_pca_2d = pca_2d.fit_transform(X_scaled)

pca_3d = PCA(n_components=3)
X_pca_3d = pca_3d.fit_transform(X_scaled)

# FIX: Lấy PCA loadings (tiêu chí ảnh hưởng nhất)
# Chuyển numeric_cols thành numpy array để indexing hoạt động
numeric_cols_arr = np.array(numeric_cols)
pca_loadings_2d = pca_2d.components_

# Lấy indices của 3 tiêu chí có ảnh hưởng lớn nhất
indices_pc1 = np.argsort(np.abs(pca_loadings_2d[0]))[-3:]
indices_pc2 = np.argsort(np.abs(pca_loadings_2d[1]))[-3:]

top_features_pc1 = numeric_cols_arr[indices_pc1]
top_features_pc2 = numeric_cols_arr[indices_pc2]

print("=" * 80)
print("TIÊU CHÍ CHÍNH ẢNH HƯỞNG ĐẾN PHÂN CỤM (PCA Analysis)")
print("=" * 80)
print(f"\n🔵 PC1 (Giải thích {pca_2d.explained_variance_ratio_[0]:.2%} phương sai):")
print(f"   Tiêu chí chính: {', '.join(top_features_pc1)}")

print(f"\n🟢 PC2 (Giải thích {pca_2d.explained_variance_ratio_[1]:.2%} phương sai):")
print(f"   Tiêu chí chính: {', '.join(top_features_pc2)}")

print(f"\n📈 Tổng cộng giải thích được {(pca_2d.explained_variance_ratio_.sum()):.2%} phương sai của dữ liệu\n")

# PCA 2D với chú thích tiêu chí
print("Vẽ biểu đồ PCA 2D...")
fig, ax = plt.subplots(figsize=(12, 9))
fig.patch.set_facecolor('#121212')
ax.set_facecolor('#1E1E1E')

scatter_2d = ax.scatter(X_pca_2d[:, 0], X_pca_2d[:, 1], c=clusters, cmap='viridis', 
                         alpha=0.7, s=100, edgecolors='white', linewidth=0.5)

ax.set_title('Phân cụm cầu thủ (PCA 2D)\n' + 
             f'PC1: {", ".join(top_features_pc1)} | PC2: {", ".join(top_features_pc2)}',
             fontsize=13, fontweight='bold', color='white', pad=20)
ax.set_xlabel(f'PC1 ({pca_2d.explained_variance_ratio_[0]:.2%} variance)\n← {top_features_pc1[0]} vs {top_features_pc1[-1]} →',
              fontsize=11, color='white')
ax.set_ylabel(f'PC2 ({pca_2d.explained_variance_ratio_[1]:.2%} variance)\n← {top_features_pc2[0]} vs {top_features_pc2[-1]} →',
              fontsize=11, color='white')
ax.grid(True, alpha=0.2, color='white')
ax.tick_params(colors='white')

cbar = plt.colorbar(scatter_2d, ax=ax, label='Cluster')
cbar.set_label('Cluster', fontsize=11, color='white')
cbar.ax.tick_params(colors='white')

# Thêm chú thích
textstr = f"Tiêu chí phân cụm: {len(numeric_cols)} chỉ số hiệu suất\nPhương pháp: K-Means (k={optimal_k})"
ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=10,
        verticalalignment='top', bbox=dict(boxstyle='round', facecolor='#2A2A2A', alpha=0.8),
        color='white')

plt.tight_layout()
plt.show()

# PCA 3D
print("Vẽ biểu đồ PCA 3D...")
fig = plt.figure(figsize=(12, 9))
fig.patch.set_facecolor('#121212')
ax3d = fig.add_subplot(111, projection='3d')
ax3d.set_facecolor('#1E1E1E')

scatter_3d = ax3d.scatter(X_pca_3d[:, 0], X_pca_3d[:, 1], X_pca_3d[:, 2], 
                          c=clusters, cmap='viridis', alpha=0.7, s=100, edgecolors='white', linewidth=0.5)

ax3d.set_title(f'Phân cụm cầu thủ (PCA 3D) - {len(numeric_cols)} tiêu chí phân cụm',
              fontsize=13, fontweight='bold', color='white', pad=20)
ax3d.set_xlabel(f'PC1 ({pca_3d.explained_variance_ratio_[0]:.2%})', fontsize=10, color='white')
ax3d.set_ylabel(f'PC2 ({pca_3d.explained_variance_ratio_[1]:.2%})', fontsize=10, color='white')
ax3d.set_zlabel(f'PC3 ({pca_3d.explained_variance_ratio_[2]:.2%})', fontsize=10, color='white')
ax3d.tick_params(colors='white')

cbar_3d = plt.colorbar(scatter_3d, ax=ax3d, pad=0.1, shrink=0.8, label='Cluster')
cbar_3d.set_label('Cluster', fontsize=11, color='white')
cbar_3d.ax.tick_params(colors='white')

plt.tight_layout()
plt.show()

print("\n✓ Hoàn tất phân cụm!")