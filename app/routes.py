from flask import Blueprint, render_template, jsonify, request
from app.models import DiemThamQuan, HinhAnhDiem
from app.algorithms.gts import greedy_tsp
from app.utils import generate_map

main = Blueprint("main", __name__)

@main.route("/")
def display_map():
    return render_template("display_map.html")

@main.route("/api/map")
def api_map():
    points = []
    for d in DiemThamQuan.query.all():
        img = HinhAnhDiem.query.filter_by(DiemID=d.DiemID).first()
        points.append({
            "id": d.DiemID,
            "name": d.TenDiem,
            "desc": d.MoTa,
            "address": d.DiaChi,
            "lat": d.ViDo,
            "lng": d.KinhDo,
            "quan": d.quan.TenQuan if d.quan else None,
            "loai": d.loai.TenLoai if d.loai else None,
            "img": img.UrlHinh if img else None
        })
    return jsonify(points)

@main.route("/api/route", methods=["POST"])
def api_route():
    data = request.get_json()
    points = data.get("points", [])
    if not points:
        return jsonify({"error": "Thiếu dữ liệu điểm."}), 400

    coords = [(p["lat"], p["lng"]) for p in points]
    path, total_distance = greedy_tsp(coords)
    map_html = generate_map(coords, path)
    return jsonify({
        "route_order": path,
        "total_distance": round(total_distance, 2),
        "map_html": map_html
    })
