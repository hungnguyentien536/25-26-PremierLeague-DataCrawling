import os
from flask import Flask, jsonify, request
import pandas as pd

app = Flask(__name__)

script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, "25-26_PremierLeague_Players.csv")
df = pd.read_csv(csv_path)


@app.route('/', methods=['GET'])
def home():
    """Trang chủ - Hướng dẫn sử dụng API"""
    return jsonify({
        "message": "Chào mừng tới EPL Players API",
        "endpoints": {
            "GET /player/<name>": "Tìm kiếm cầu thủ theo tên",
            "GET /players": "Lấy danh sách tất cả cầu thủ",
            "GET /stats": "Xem thống kê chung"
        },
        "example": "http://localhost:5000/player/Haaland"
    })


@app.route('/player/<name>', methods=['GET'])
def get_player_stats(name):
    """Tìm kiếm cầu thủ bằng tên (tìm kiếm không chính xác, không phân biệt hoa/thường)"""
    ten_cau_thu_col = df['Tên cầu thủ']
    mask = ten_cau_thu_col.str.contains(name, case=False, na=False)
    result = df[mask]

    if result.empty:
        return jsonify({"message": f"Không tìm thấy cầu thủ: {name}"}), 404
    
    player_data = result.to_dict(orient='records')
    return jsonify({
        "count": len(player_data),
        "players": player_data
    })


@app.route('/players', methods=['GET'])
def get_all_players():
    """Lấy danh sách tất cả cầu thủ (hỗ trợ phân trang)"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    start = (page - 1) * per_page
    end = start + per_page
    
    total = len(df)
    players = df.iloc[start:end].to_dict(orient='records')
    
    return jsonify({
        "total": total,
        "page": page,
        "per_page": per_page,
        "data": players
    })


@app.route('/stats', methods=['GET'])
def get_stats():
    """Trả về thống kê chung về dữ liệu"""
    return jsonify({
        "total_players": len(df),
        "columns": df.columns.tolist(),
        "rows": len(df)
    })


@app.errorhandler(404)
def not_found(error):
    """Xử lý lỗi 404"""
    return jsonify({"error": "Endpoint không tồn tại. Truy cập / để xem hướng dẫn"}), 404


if __name__ == '__main__':
    app.run(debug=True, port=5000)