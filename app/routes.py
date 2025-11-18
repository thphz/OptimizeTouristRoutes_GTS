from flask import Blueprint, render_template, jsonify, request
from app.models import DiemThamQuan, HinhAnhDiem, LoaiDiemThamQuan, Quan 
# Giả định các hàm này tồn tại
# from app.algorithms.gts import greedy_tsp
# from app.utils import generate_map

from sqlalchemy.orm import joinedload
from types import SimpleNamespace # Dùng để mô phỏng data nếu thiếu hàm thật

main = Blueprint("main", __name__)

# Ánh xạ ID sang TÊN MÀU (chuỗi)
COLOR_MAPPING = {
    1: 'red',    
    2: 'blue',   
    3: 'purple', 
    4: 'orange', 
    5: 'green',  
}

@main.route("/")
@main.route("/map")
def display_map():
    loai_diem_all = LoaiDiemThamQuan.query.all()
    
    diem_tham_quan_all = DiemThamQuan.query.options(
        joinedload(DiemThamQuan.quan), 
        joinedload(DiemThamQuan.loai)
    ).all()
    
    diem_data_list = []
    for d in diem_tham_quan_all:
        color_name = COLOR_MAPPING.get(d.LoaiID, 'gray')
        
        diem_data_list.append({
            'DiemID': d.DiemID,
            'TenDiem': d.TenDiem,
            'LoaiID': d.LoaiID,
            'TenQuan': d.quan.TenQuan if d.quan else 'N/A', 
            'TenLoai': d.loai.TenLoai if d.loai else 'N/A',
            'ColorName': color_name, 
        })

    id_to_color_map = {}
    for loai in loai_diem_all:
        id_to_color_map[loai.LoaiID] = COLOR_MAPPING.get(loai.LoaiID, 'gray') 

    return render_template(
        "display_map.html",
        diem_tham_quan_da_chon=diem_data_list, 
        loai_diem=loai_diem_all,
        color_mapping=id_to_color_map
    )

@main.route("/api/map_data")
def api_map_data():
    diem_tham_quan_all = DiemThamQuan.query.options(
        joinedload(DiemThamQuan.quan), 
        joinedload(DiemThamQuan.loai)
    ).all()
    
    points = []
    for d in diem_tham_quan_all:
        img = d.hinh_anh[0].UrlHinh if d.hinh_anh else None
        
        quan_name = d.quan.TenQuan if d.quan else None
        loai_name = d.loai.TenLoai if d.loai else None
        
        points.append({
            "id": d.DiemID,
            "name": d.TenDiem,
            "lat": float(d.ViDo),
            "lng": float(d.KinhDo),
            "quan": quan_name,
            "loai_id": d.LoaiID,
            "loai_name": loai_name,
            "img": img
        })
    return jsonify(points)

@main.route("/api/route_optimize", methods=["POST"])
def api_route_optimize():
    data = request.get_json()
    points = data.get("points", []) 
    
    if len(points) < 2:
        return jsonify({"error": "Vui lòng chọn ít nhất 2 điểm để tìm tuyến đường."}), 400

    coords = [(p["lat"], p["lng"]) for p in points]
    
    # Dữ liệu mô phỏng
    path = list(range(len(coords)))
    total_distance = len(coords) * 1.5 
    
    return jsonify({
        "route_order": path,
        "total_distance": round(total_distance, 2),
        "map_html": "" 
    })