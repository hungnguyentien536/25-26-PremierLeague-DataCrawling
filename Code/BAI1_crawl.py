from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
from pathlib import Path
import time
import random


def setup_chrome():
    """
    Khởi tạo và cấu hình Chrome driver.
    
    Returns:
        webdriver.Chrome: Trình duyệt Chrome đã được cấu hình
    """
    chrome_options = Options()  # biến chứa cấu hình cho chrome
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # tắt thuộc tính nagivator.webdrive=false
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=chrome_options)  # khởi động trình duyệt
    return driver


def fetch_html(driver, url, delay=(3, 7)):
    """
    Lấy mã HTML từ URL bằng Selenium.
    
    Args:
        driver (webdriver.Chrome): Trình duyệt Chrome
        url (str): Địa chỉ URL cần lấy
        delay (tuple): Khoảng thời gian chờ (min, max) theo giây
    
    Returns:
        str: Mã HTML của trang
    """
    driver.get(url)  # lấy link
    time.sleep(random.uniform(delay[0], delay[1]))
    
    html_content = driver.page_source  # copy toàn bộ mã html
    return html_content


def extract_table(html_content, table_id="stats_standard"):
    """
    Trích xuất bảng từ HTML và chuyển thành DataFrame.
    
    Args:
        html_content (str): Mã HTML cần phân tích
        table_id (str): ID của bảng trong HTML
    
    Returns:
        pd.DataFrame: DataFrame chứa dữ liệu bảng hoặc None nếu không tìm thấy
    """
    html_content = html_content.replace('', '')
    soup = BeautifulSoup(html_content, "html.parser")
    table = soup.find("table", {"id": table_id})
    
    if table is None:
        return None
    
    df = pd.read_html(StringIO(str(table)))[0]
    new_columns = []
    
    for col in df.columns:
        if isinstance(col, tuple):
            new_columns.append(col[-1])
        else:
            new_columns.append(col)
    
    df.columns = new_columns
    
    return df


def clean_data(df, min_minutes=90):
    """
    Làm sạch và lọc dữ liệu cầu thủ.
    
    Args:
        df (pd.DataFrame): DataFrame thô từ bảng HTML
        min_minutes (int): Ngưỡng số phút tối thiểu (mặc định 90)
    
    Returns:
        pd.DataFrame: DataFrame đã được làm sạch và lọc
    """
    # Loại bỏ hàng header lặp
    mask = df['Player'] != 'Player'
    df_temp = df[mask]
    df = df_temp.copy()
    
    # Chuyển đổi cột Min sang số
    df['Min'] = df['Min'].astype(str).str.replace(',', '')
    df['Min'] = pd.to_numeric(df['Min'], errors='coerce')
    
    # Lọc cầu thủ có ít nhất min_minutes phút thi đấu
    df_filtered = df[df['Min'] > min_minutes].copy()
    
    # Điền các giá trị NaN
    df_filtered.fillna('N/a', inplace=True)
    
    return df_filtered


def format_data(df):
    """
    Định dạng lại cột của DataFrame theo yêu cầu.
    
    Args:
        df (pd.DataFrame): DataFrame cần định dạng
    
    Returns:
        pd.DataFrame: DataFrame đã được định dạng
    """
    # Chỉ giữ lại các cột cần thiết
    cols_to_keep = ['Player']
    for col in df.columns:
        if col not in ['Rk', 'Player', 'Matches']:
            cols_to_keep.append(col)
    
    df_formatted = df[cols_to_keep]
    
    # Thêm cột STT ở đầu
    df_formatted.insert(0, 'STT', range(1, len(df_formatted) + 1))
    
    # Đổi tên cột
    df_formatted.rename(columns={'Player': 'Tên cầu thủ'}, inplace=True)
    
    return df_formatted


def export_csv(df, output_path):
    """
    Xuất DataFrame ra file CSV.
    
    Args:
        df (pd.DataFrame): DataFrame cần xuất
        output_path (str | Path): Đường dẫn file đầu ra
    
    Returns:
        bool: True nếu thành công, False nếu lỗi
    """
    try:
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"Xong! Đã lưu thành công dữ liệu vào {output_path}")
        return True
    except Exception as e:
        print(f"Lỗi khi lưu file: {e}")
        return False


def crawl_premier_league(url, output_filename="25-26_PremierLeague_Players.csv", min_minutes=90):
    """
    Hàm chính: Cào dữ liệu cầu thủ Premier League.
    
    Args:
        url (str): URL của trang cần cào
        output_filename (str): Tên file CSV đầu ra
        min_minutes (int): Ngưỡng số phút tối thiểu
    
    Returns:
        pd.DataFrame: DataFrame cuối cùng hoặc None nếu lỗi
    """
    driver = setup_chrome()
    
    try:
        # Lấy HTML
        html_content = fetch_html(driver, url)
        
        # Trích xuất bảng
        df = extract_table(html_content)
        
        if df is None:
            print("Không tìm thấy bảng dữ liệu.")
            return None
        
        # Làm sạch dữ liệu
        df = clean_data(df, min_minutes)
        
        # Định dạng dữ liệu
        df = format_data(df)
        
        # Xuất CSV
        output_path = Path(__file__).parent / output_filename
        export_csv(df, output_path)
        
        return df
    
    finally:
        driver.quit()


# Chương trình chính
if __name__ == "__main__":
    url_epl = "https://fbref.com/en/comps/9/stats/Premier-League-Stats"
    crawl_premier_league(url_epl)