import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import requests
import matplotlib.pyplot as plt
import numpy as np
import threading
import pandas as pd

# ==========================================
# PALETTE MÀU SẮC & FONT 
# ==========================================
BG_MAIN = "#121212"
BG_CARD = "#1E1E1E"
BG_INPUT = "#2A2A2A"
FG_PRIMARY = "#FFFFFF"
FG_SECONDARY = "#A0A0A0"

COLOR_P1 = "#00A8FF"
COLOR_P2 = "#FF3838"
COLOR_COMPARE = "#2ED573"
FONT_FAMILY = "Segoe UI"


# ==========================================
# QUẢN LÝ DỮ LIỆU CẦU THỦ
# ==========================================
class PlayerData:
    def __init__(self):
        self.player1 = {}
        self.player2 = {}
    
    def set_player(self, player_num, data):
        if player_num == 1:
            self.player1 = data
        else:
            self.player2 = data
    
    def get_player(self, player_num):
        return self.player1 if player_num == 1 else self.player2


players = PlayerData()
checkbox_vars = {}


def show_player_selection(player_list, player_num):
    """
    Hiển thị hộp thoại cho phép người dùng chọn từ danh sách cầu thủ
    
    Args:
        player_list: Danh sách các cầu thủ
        player_num: Số cầu thủ (1 hoặc 2)
    
    Returns:
        Dữ liệu cầu thủ được chọn hoặc None
    """
    window = tk.Toplevel(root)
    window.title(f"Chọn Cầu Thủ #{player_num}")
    window.geometry("500x400")
    window.configure(bg=BG_MAIN)
    window.transient(root)
    window.grab_set()
    
    selected = [None]
    
    # Header
    tk.Label(window, text=f"Tìm thấy {len(player_list)} cầu thủ. Vui lòng chọn:", 
             font=(FONT_FAMILY, 11, "bold"), bg=BG_MAIN, fg=FG_PRIMARY).pack(pady=10)
    
    # Listbox với scrollbar
    frame_list = tk.Frame(window, bg=BG_MAIN)
    frame_list.pack(fill="both", expand=True, padx=10, pady=10)
    
    scrollbar = ttk.Scrollbar(frame_list)
    scrollbar.pack(side="right", fill="y")
    
    listbox = tk.Listbox(
        frame_list, 
        font=(FONT_FAMILY, 10),
        bg=BG_INPUT,
        fg=FG_PRIMARY,
        selectmode="single",
        yscrollcommand=scrollbar.set
    )
    listbox.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=listbox.yview)
    
    # Thêm các cầu thủ vào listbox
    for idx, player in enumerate(player_list):
        player_info = f"{player.get('Tên cầu thủ', 'N/a')} - {player.get('Squad', 'N/a')} (Min: {player.get('Min', 'N/a')})"
        listbox.insert(idx, player_info)
    
    # Chọn mục đầu tiên mặc định
    listbox.selection_set(0)
    listbox.see(0)
    
    # Frame nút
    frame_buttons = tk.Frame(window, bg=BG_MAIN)
    frame_buttons.pack(fill="x", padx=10, pady=10)
    
    def on_select():
        """Xử lý khi người dùng nhấn OK"""
        selection = listbox.curselection()
        if selection:
            selected[0] = player_list[selection[0]]
            window.destroy()
    
    def on_cancel():
        """Xử lý khi người dùng nhấn Hủy"""
        selected[0] = None
        window.destroy()
    
    btn_ok = tk.Button(
        frame_buttons, text="✓ CHỌN", bg=COLOR_COMPARE, fg="white",
        font=(FONT_FAMILY, 10, "bold"), relief="flat", padx=15, pady=8,
        command=on_select
    )
    btn_ok.pack(side="left", padx=5)
    
    btn_cancel = tk.Button(
        frame_buttons, text="✗ HỦY", bg="#FF5555", fg="white",
        font=(FONT_FAMILY, 10, "bold"), relief="flat", padx=15, pady=8,
        command=on_cancel
    )
    btn_cancel.pack(side="left", padx=5)
    
    # Chờ window đóng
    window.wait_window()
    
    return selected[0]


def search_player(player_num):
    """Tìm kiếm cầu thủ trong thread riêng"""
    if player_num == 1:
        name = entry_p1.get()
    else:
        name = entry_p2.get()

    if name.strip() == "":
        messagebox.showwarning("Cảnh báo", "Vui lòng nhập tên cầu thủ!")
        return

    t = threading.Thread(target=get_player_data_worker, args=(name, player_num), daemon=True)
    t.start()


def get_player_data_worker(name, player_num):
    """Lấy dữ liệu cầu thủ từ API"""
    url = f"http://localhost:5000/player/{name}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            
            # Xử lý trường hợp có nhiều kết quả
            if 'players' in data and data['players']:
                player_list = data['players']
                
                # Nếu có nhiều hơn 1 cầu thủ, hiển thị dialog chọn
                if len(player_list) > 1:
                    def show_and_select():
                        """Hiển thị dialog, chờ chọn, rồi cập nhật"""
                        selected = show_player_selection(player_list, player_num)
                        if selected:
                            update_player_display(player_num, selected, name)
                    
                    root.after(0, show_and_select)
                    return
                else:
                    # Chỉ 1 kết quả, lấy luôn
                    stats = player_list[0]
                    root.after(0, lambda s=stats: update_player_display(player_num, s, name))
            else:
                stats = data[0] if data else None
                if stats:
                    root.after(0, lambda s=stats: update_player_display(player_num, s, name))
        else:
            root.after(0, lambda: messagebox.showerror("Lỗi", f"Không tìm thấy cầu thủ: {name}"))
    except requests.exceptions.ConnectionError:
        root.after(0, lambda: messagebox.showerror(
            "Lỗi kết nối",
            "Không thể kết nối tới Flask API!\n"
            "Hãy chắc chắn rằng bạn đã chạy file BAI2_flask.py (port 5000) trước."
        ))
    except Exception as e:
        root.after(0, lambda: messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {str(e)}"))


def update_player_display(player_num, stats, name):
    """Cập nhật hiển thị thông tin cầu thủ"""
    players.set_player(player_num, stats)
    
    if player_num == 1:
        display_stats(frame_stats1, stats, is_player1=True)
        label_name1.config(text=stats.get('Tên cầu thủ', name).upper())
    else:
        display_stats(frame_stats2, stats, is_player1=False)
        label_name2.config(text=stats.get('Tên cầu thủ', name).upper())


def display_stats(frame, stats, is_player1):
    """Hiển thị chỉ số cầu thủ"""
    for widget in frame.winfo_children():
        widget.destroy()

    ignore_keys = ['STT', 'Tên cầu thủ', 'Nation', 'Pos', 'Squad', 'Age', 'Born', 'Matches', 'Rk']
    row_idx = 0
    
    for key, value in stats.items():
        if key in ignore_keys or any(x in key for x in ['STT', 'Player']):
            continue

        display_text = f" {key}: {value}"
        if is_player1:
            var = tk.BooleanVar()
            checkbox_vars[key] = var
            chk = tk.Checkbutton(
                frame, text=display_text, variable=var, 
                font=(FONT_FAMILY, 10), bg=BG_CARD, fg=FG_PRIMARY,
                selectcolor=BG_INPUT, activebackground=BG_CARD, 
                activeforeground=COLOR_P1, relief="flat", bd=0
            )
            chk.grid(row=row_idx, column=0, sticky="w", pady=3, padx=10)
        else:
            lbl = tk.Label(
                frame, text=display_text, font=(FONT_FAMILY, 10), 
                bg=BG_CARD, fg=FG_PRIMARY, anchor="w"
            )
            lbl.grid(row=row_idx, column=0, sticky="w", pady=4, padx=15)
        row_idx += 1


def compare_players():
    """So sánh hai cầu thủ và vẽ biểu đồ"""
    player1_data = players.get_player(1)
    player2_data = players.get_player(2)
    
    if not player1_data or not player2_data:
        messagebox.showwarning("Cảnh báo", "Vui lòng tìm kiếm đủ 2 cầu thủ trước khi so sánh!")
        return

    selected_stats = [stat_name for stat_name, var in checkbox_vars.items() if var.get()]

    if len(selected_stats) < 3:
        messagebox.showwarning("Cảnh báo", "Vui lòng chọn ít nhất 3 chỉ số để vẽ biểu đồ Radar!")
        return

    def clean_value(val):
        if val in ['N/a', None, '', 'nan']:
            return 0.0
        try:
            return float(str(val).replace(',', ''))
        except (ValueError, TypeError):
            return 0.0

    values1 = [clean_value(player1_data.get(stat, 0)) for stat in selected_stats]
    values2 = [clean_value(player2_data.get(stat, 0)) for stat in selected_stats]

    draw_radar_chart(
        selected_stats, 
        values1, 
        values2, 
        player1_data.get('Tên cầu thủ', 'Cầu thủ 1'),
        player2_data.get('Tên cầu thủ', 'Cầu thủ 2')
    )


def draw_radar_chart(categories, values1, values2, name1, name2):
    """Vẽ biểu đồ radar so sánh phong cách Dark Mode"""
    N = len(categories)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]

    values1_plot = values1 + values1[:1]
    values2_plot = values2 + values2[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor(BG_CARD)
    ax.set_facecolor(BG_INPUT)
    
    ax.plot(angles, values1_plot, linewidth=2, linestyle='solid', label=name1, color=COLOR_P1)
    ax.fill(angles, values1_plot, color=COLOR_P1, alpha=0.25)
    
    ax.plot(angles, values2_plot, linewidth=2, linestyle='solid', label=name2, color=COLOR_P2)
    ax.fill(angles, values2_plot, color=COLOR_P2, alpha=0.25)

    clean_categories = [
        cat.replace('Expected_', 'x').replace('Per 90 Mins_', '').replace('_', ' ')[:15]
        for cat in categories
    ]
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(clean_categories, size=10, color=FG_PRIMARY, fontweight='bold')
    ax.set_ylim(0, max(max(values1), max(values2)) * 1.2)
    
    ax.spines['polar'].set_color('#444444')
    ax.grid(color='#444444', linestyle='--')
    ax.tick_params(axis='y', colors=FG_SECONDARY, labelsize=9)
    
    legend = plt.legend(loc='upper right', bbox_to_anchor=(1.2, 1.1), fontsize=10, facecolor=BG_CARD, edgecolor='#444444')
    for text in legend.get_texts():
        text.set_color(FG_PRIMARY)
        
    plt.title(f"SO SÁNH: {name1.upper()} VS {name2.upper()}", size=14, y=1.08, fontweight='bold', color=FG_PRIMARY)
    plt.tight_layout()
    plt.show()


def on_mousewheel(event, canvas):
    """Xử lý cuộn chuột"""
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


# === GIAO DIỆN CHÍNH ===
root = tk.Tk()
root.title("EPL Player Analytics Dashboard")
root.geometry("950x750")
root.configure(bg=BG_MAIN)
root.resizable(True, True)

style = ttk.Style()
style.theme_use('clam')
style.configure("Vertical.TScrollbar", gripcount=0, background=BG_INPUT, 
                darkcolor=BG_MAIN, lightcolor=BG_MAIN, troughcolor=BG_MAIN, bordercolor=BG_MAIN)

# 1. Khung Tìm kiếm Thượng tầng
frame_top = tk.Frame(root, bg=BG_CARD, padx=20, pady=15)
frame_top.pack(fill="x", padx=20, pady=15)

lbl_header = tk.Label(frame_top, text="📊 EPL STATS COMPARISON", font=(FONT_FAMILY, 12, "bold"), fg=COLOR_COMPARE, bg=BG_CARD)
lbl_header.grid(row=0, column=0, columnspan=6, sticky="w", pady=(0, 15))

tk.Label(frame_top, text="Cầu thủ 1:", font=(FONT_FAMILY, 10), bg=BG_CARD, fg=FG_PRIMARY).grid(row=1, column=0, sticky="e", padx=5)
entry_p1 = tk.Entry(frame_top, width=18, font=(FONT_FAMILY, 11), bg=BG_INPUT, fg=FG_PRIMARY, insertbackground=FG_PRIMARY, relief="flat")
entry_p1.grid(row=1, column=1, padx=5, ipady=4)
btn_s1 = tk.Button(frame_top, text="🔍 TÌM KIẾM 1", bg=COLOR_P1, fg="white", activebackground="#0086CC", activeforeground="white",
                   command=lambda: search_player(1), font=(FONT_FAMILY, 9, "bold"), relief="flat", padx=10)
btn_s1.grid(row=1, column=2, padx=(5, 25), ipady=2)

tk.Label(frame_top, text="Cầu thủ 2:", font=(FONT_FAMILY, 10), bg=BG_CARD, fg=FG_PRIMARY).grid(row=1, column=3, sticky="e", padx=5)
entry_p2 = tk.Entry(frame_top, width=18, font=(FONT_FAMILY, 11), bg=BG_INPUT, fg=FG_PRIMARY, insertbackground=FG_PRIMARY, relief="flat")
entry_p2.grid(row=1, column=4, padx=5, ipady=4)
btn_s2 = tk.Button(frame_top, text="🔍 TÌM KIẾM 2", bg=COLOR_P2, fg="white", activebackground="#D62728", activeforeground="white",
                   command=lambda: search_player(2), font=(FONT_FAMILY, 9, "bold"), relief="flat", padx=10)
btn_s2.grid(row=1, column=5, padx=5, ipady=2)

# 2. Khung Hiển thị Trung tầng
frame_mid = tk.Frame(root, bg=BG_MAIN)
frame_mid.pack(fill="both", expand=True, padx=10, pady=5)

# CỘT CẦU THỦ 1
frame_left = tk.Frame(frame_mid, bg=BG_CARD, bd=0)
frame_left.pack(side="left", fill="both", expand=True, padx=10, pady=5)

label_name1 = tk.Label(frame_left, text="THÔNG TIN CẦU THỦ 1", font=(FONT_FAMILY, 12, "bold"), fg=COLOR_P1, bg=BG_CARD)
label_name1.pack(anchor="w", padx=15, pady=10)

canvas1 = tk.Canvas(frame_left, borderwidth=0, highlightthickness=0, bg=BG_CARD)
scrollbar1 = ttk.Scrollbar(frame_left, orient="vertical", command=canvas1.yview)
frame_stats1 = tk.Frame(canvas1, bg=BG_CARD)

frame_stats1.bind("<Configure>", lambda event: canvas1.configure(scrollregion=canvas1.bbox("all")))
canvas1.create_window((0, 0), window=frame_stats1, anchor="nw")
canvas1.configure(yscrollcommand=scrollbar1.set)

canvas1.pack(side="left", fill="both", expand=True, padx=5, pady=5)
scrollbar1.pack(side="right", fill="y", pady=5)
canvas1.bind_all("<MouseWheel>", lambda event: on_mousewheel(event, canvas1))

# CỘT CẦU THỦ 2
frame_right = tk.Frame(frame_mid, bg=BG_CARD, bd=0)
frame_right.pack(side="right", fill="both", expand=True, padx=10, pady=5)

label_name2 = tk.Label(frame_right, text="THÔNG TIN CẦU THỦ 2", font=(FONT_FAMILY, 12, "bold"), fg=COLOR_P2, bg=BG_CARD)
label_name2.pack(anchor="w", padx=15, pady=10)

canvas2 = tk.Canvas(frame_right, borderwidth=0, highlightthickness=0, bg=BG_CARD)
scrollbar2 = ttk.Scrollbar(frame_right, orient="vertical", command=canvas2.yview)
frame_stats2 = tk.Frame(canvas2, bg=BG_CARD)

frame_stats2.bind("<Configure>", lambda event: canvas2.configure(scrollregion=canvas2.bbox("all")))
canvas2.create_window((0, 0), window=frame_stats2, anchor="nw")
canvas2.configure(yscrollcommand=scrollbar2.set)

canvas2.pack(side="left", fill="both", expand=True, padx=5, pady=5)
scrollbar2.pack(side="right", fill="y", pady=5)

# 3. Khung Hạ tầng - Nút So Sánh
frame_bottom = tk.Frame(root, bg=BG_MAIN, pady=20)
frame_bottom.pack(fill="x")

btn_compare = tk.Button(
    frame_bottom, 
    text="📊 VẼ BIỂU ĐỒ RADAR / COMPARE NOW", 
    font=(FONT_FAMILY, 11, "bold"),
    bg=COLOR_COMPARE, 
    fg="white", 
    activebackground="#21A956",
    activeforeground="white",
    relief="flat",
    padx=30, 
    pady=12,
    command=compare_players
)
btn_compare.pack()

root.mainloop()