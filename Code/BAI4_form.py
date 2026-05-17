import os
import pandas as pd
import numpy as np

# Lấy thư mục chứa file code
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, "25-26_PremierLeague_Players.csv")
df = pd.read_csv(csv_path)

# Thay thế 'N/a' bằng NaN
df.replace('N/a', np.nan, inplace=True)

# Xác định các cột số để tính toán
cols_to_exclude = ['STT', 'Tên cầu thủ', 'Nation', 'Pos', 'Squad', 'Age', 'Born']
numeric_cols = [col for col in df.columns if col not in cols_to_exclude]

# Chuyển đổi sang kiểu số
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Tính toán thống kê theo đội
team_stats = df.groupby('Squad')[numeric_cols].agg(['median', 'mean', 'std'])

# Đổi tên cột
team_stats.columns = [f"{col[0]}_{col[1]}" for col in team_stats.columns]
team_stats = team_stats.reset_index()

# Xuất file CSV vào cùng thư mục
output_file = os.path.join(script_dir, "25-26_PremierLeague_Teams.csv")
team_stats.to_csv(output_file, index=False)
print(f"Đã lưu kết quả thống kê vào file {output_file}!")

# Tìm đội dẫn đầu từng chỉ số
team_mean = df.groupby('Squad')[numeric_cols].mean()
best_teams_per_stat = team_mean.idxmax()

print("\n--- CÁC ĐỘI DẪN ĐẦU TỪNG CHỈ SỐ ---")
for stat, team in best_teams_per_stat.items():
    print(f"Chỉ số {stat}: Dẫn đầu là {team}")

# Xác định đội phong độ tốt nhất
best_team_overall = best_teams_per_stat.mode()[0]

print("\n" + "="*60)
print(f" KẾT LUẬN: ĐỘI CÓ PHONG ĐỘ TỐT NHẤT LÀ: {best_team_overall.upper()} ")
print("="*60)