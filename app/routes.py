from app import app
from flask import redirect, url_for, request, render_template, jsonify
import math
import traceback
import requests


class Obj:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


@app.route('/')
def index():
    return redirect(url_for('select_points'))


@app.route('/select_points', methods=['GET', 'POST'])
def select_points():
    # Cố gắng tải từ các model thực tế; nếu có lỗi thì dùng dữ liệu giả để thay thế
    error = None
    try:
        from app.models import Quan, LoaiDiemThamQuan, DiemThamQuan, compute_travel_durations_from_dinh_doc_lap

        quans = Quan.query.order_by(Quan.TenQuan).all()
        loai_diems = LoaiDiemThamQuan.query.order_by(LoaiDiemThamQuan.TenLoai).all()
        diems = DiemThamQuan.query.order_by(DiemThamQuan.TenDiem).all()

        # tính thời gian di chuyển từ điểm gốc và gắn vào từng diem dưới thuộc tính _computed_duration
        try:
            durations = compute_travel_durations_from_dinh_doc_lap(diems)
            # chuẩn hoá về dict để tránh lỗi NoneType
            if not isinstance(durations, dict):
                app.logger.debug('compute_travel_durations_from_dinh_doc_lap returned non-dict (%r), normalizing to empty dict', durations)
                durations = {}
            app.logger.debug('Computed travel durations: %s', durations)
            for d in diems:
                rid = getattr(d, 'id', None)
                # fallback về thuộc tính duration hoặc --
                default_dur = getattr(d, 'duration', "--")
                if rid is not None:
                    setattr(d, '_computed_duration', durations.get(rid, default_dur))
                else:
                    setattr(d, '_computed_duration', default_dur)
        except Exception:
            # không để lỗi làm crash page,vẫn đảm bảo thuộc tính tồn tại
            app.logger.exception('Could not compute travel durations; falling back to defaults')
            for d in diems:
                setattr(d, '_computed_duration', getattr(d, 'duration', "--"))

        if request.method == 'POST':
            selected = request.form.getlist('selected_diems')
            if not selected:
                error = 'Vui lòng chọn ít nhất 1 điểm tham quan.'
            else:
                ids = ','.join(selected)
                return redirect(url_for('index') + f'?selected={ids}')

        return render_template('select_points.html', quans=quans, loai_diems=loai_diems, diems=diems, error=error)

    except Exception as e:
        # Nếu DB/models không dùng được thì dùng dữ liệu giả để UI
        app.logger.exception('Could not load real data, using mock data: %s', e)

        quans = [Obj(id=1, ten='Quận 1'), Obj(id=3, ten='Quận 3'), Obj(id=4, ten='Quận 4')]
        loai_diems = [Obj(id=1, ten='Đền/Đình'), Obj(id=2, ten='Bảo tàng'), Obj(id=3, ten='Nhà thờ')]
        diems = [
            Obj(id=1, ten='Dinh Độc Lập', duration=60, quan_id=1, quan=quans[0], loai_id=1, vi_do=10.7769, kinh_do=106.7009),
            Obj(id=2, ten='Nhà Thờ Đức Bà', duration=45, quan_id=1, quan=quans[0], loai_id=3, vi_do=10.7798, kinh_do=106.6996),
            Obj(id=3, ten='Bưu Điện Trung Tâm Sài Gòn', duration=30, quan_id=1, quan=quans[0], loai_id=1, vi_do=10.7790, kinh_do=106.6992),
            Obj(id=4, ten='Phố Đi Bộ Nguyễn Huệ', duration=45, quan_id=1, quan=quans[0], loai_id=2, vi_do=10.7774, kinh_do=106.6991),
            Obj(id=5, ten='Bảo Tàng Chứng Tích Chiến Tranh', duration=90, quan_id=3, quan=quans[1], loai_id=2, vi_do=10.7776, kinh_do=106.6887),
        ]

        # tính thời gian cho dữ liệu giả
        try:
            from app.models import compute_travel_durations_from_dinh_doc_lap
            durations = compute_travel_durations_from_dinh_doc_lap(diems)
            if not isinstance(durations, dict):
                app.logger.debug('compute_travel_durations_from_dinh_doc_lap (mock) returned non-dict (%r), normalizing to empty dict', durations)
                durations = {}
            app.logger.debug('Computed travel durations (mock): %s', durations)
            for d in diems:
                rid = getattr(d, 'id', None)
                default_dur = getattr(d, 'duration', "--")
                if rid is not None:
                    setattr(d, '_computed_duration', durations.get(rid, default_dur))
                else:
                    setattr(d, '_computed_duration', default_dur)
        except Exception:
            app.logger.exception('Could not compute travel durations for mock data')
            for d in diems:
                setattr(d, '_computed_duration', getattr(d, 'duration', "--"))

        if request.method == 'POST':
            selected = request.form.getlist('selected_diems')
            if not selected:
                error = 'Vui lòng chọn ít nhất 1 điểm tham quan.'
            else:
                ids = ','.join(selected)
                return redirect(url_for('index') + f'?selected={ids}')

        return render_template('select_points.html', quans=quans, loai_diems=loai_diems, diems=diems, error=error)


@app.route('/display_map')
def display_map():
    try:
        from app.models import LoaiDiemThamQuan
        
        loai_diem = LoaiDiemThamQuan.query.order_by(LoaiDiemThamQuan.TenLoai).all()
        
        # Map LoaiID to color names
        color_mapping = {1: 'red', 2: 'blue', 3: 'purple', 4: 'orange', 5: 'green'}
        
        return render_template('display_map.html', loai_diem=loai_diem, color_mapping=color_mapping)
        
    except Exception as e:
        app.logger.exception('Could not load loai_diem data: %s', e)
        # Fallback with mock data
        loai_diem = [
            Obj(LoaiID=1, TenLoai='Đền/Đình'),
            Obj(LoaiID=2, TenLoai='Bảo tàng'),
            Obj(LoaiID=3, TenLoai='Nhà thờ'),
            Obj(LoaiID=4, TenLoai='Công viên'),
            Obj(LoaiID=5, TenLoai='Chợ')
        ]
        color_mapping = {1: 'red', 2: 'blue', 3: 'purple', 4: 'orange', 5: 'green'}
        return render_template('display_map.html', loai_diem=loai_diem, color_mapping=color_mapping)


@app.route('/api/map_data')
def api_map_data():
    try:
        from app.models import DiemThamQuan, Quan, LoaiDiemThamQuan
        
        diems = DiemThamQuan.query.all()
        
        result = []
        for diem in diems:
            result.append({
                'id': diem.DiemID,
                'name': diem.TenDiem,
                'lat': float(diem.ViDo) if diem.ViDo else 0,
                'lng': float(diem.KinhDo) if diem.KinhDo else 0,
                'quan': diem.quan.TenQuan if diem.quan else '',
                'loai_id': diem.LoaiID,
                'loai_name': diem.loai.TenLoai if diem.loai else ''
            })
        
        return jsonify(result)
        
    except Exception as e:
        app.logger.exception('Error loading map data: %s', e)
        return jsonify({'error': str(e)}), 500


@app.route('/api/route_optimize', methods=['POST'])
def api_route_optimize():
    try:
        data = request.get_json()
        points = data.get('points', [])
       
        if len(points) < 2:
            return jsonify({"error": "Vui lòng chọn ít nhất 2 điểm để tìm tuyến đường."}), 400

        coords = [(p["lat"], p["lng"]) for p in points]
    
        # Dữ liệu mô phỏng
        path = list(range(len(coords)))
        total_distance = len(coords) * 1.5 
    
        return jsonify({
            "route_order": path,
            "total_distance": round(total_distance, 2),
        })
        
    except Exception as e:
        app.logger.exception('Error optimizing route: %s', e)
        return jsonify({'error': str(e)}), 500


@app.route('/find-route')
def find_route_page():
    """Hiển thị trang giao diện 'Tìm Đường'."""
    return render_template('find_route.html', title='Tìm Lộ Trình Tối Ưu')


@app.route('/api/locations')
def get_locations():
    """API endpoint để trả về danh sách các địa điểm."""
    try:
        from app.models import DiemThamQuan
        
        locations_data = DiemThamQuan.query.order_by(DiemThamQuan.TenDiem).all()
        locations_list = [loc.to_dict() for loc in locations_data]
        return jsonify(locations_list)
        
    except Exception as e:
        app.logger.exception('======= LỖI KẾT NỐI DB / QUERY MODEL =======')
        return jsonify({'error': f"Lỗi DB hoặc Model: {str(e)}"}), 500


@app.route('/api/find-route', methods=['POST'])
def api_find_route():
    """API endpoint nhận yêu cầu tìm đường và trả về lộ trình."""
    data = request.json
    
    try:
        start_point_id = int(data.get('start'))
        end_point_id = int(data.get('end'))
    except (TypeError, ValueError):
        return jsonify({'error': 'ID điểm bắt đầu hoặc kết thúc không hợp lệ'}), 400

    route_type = data.get('type') 

    try:
        from app.models import DiemThamQuan
        
        start_point = DiemThamQuan.query.get(start_point_id)
        end_point = DiemThamQuan.query.get(end_point_id)
        
        if not start_point or not end_point:
             return jsonify({'error': 'Không tìm thấy điểm bắt đầu hoặc kết thúc trong DB'}), 404
        
        start_point_name = start_point.TenDiem
        end_point_name = end_point.TenDiem
        
        if route_type == 'scenic':
            dummy_gts_route = {
                'distance_km': 51.2, 
                'duration_min': 148,
                'traffic': 'Giao thông không áp dụng.',
                'steps': ['Lộ trình tham quan vòng quanh thành phố.'],
                'waypoints_timeline': [
                    {'name': start_point_name, 'detail': 'Xuất phát'},
                    {'name': 'Dinh Độc Lập (Giả)'},
                    {'name': '... (và 8 điểm khác)'},
                    {'name': start_point_name, 'detail': 'Đích đến'}
                ],
                'coordinates': [ [10.7769, 106.6955], [10.7714, 106.7038] ]
            }
            return jsonify(dummy_gts_route)
        
        else: 
            coords_start = f"{start_point.KinhDo},{start_point.ViDo}"
            coords_end = f"{end_point.KinhDo},{end_point.ViDo}"
            osrm_url = f"http://router.project-osrm.org/route/v1/driving/{coords_start};{coords_end}?steps=true"
            
            app.logger.info(f"Đang gọi API OSRM: {osrm_url}")
            
            response = requests.get(osrm_url, timeout=10)
            response.raise_for_status() 
            
            route_data = response.json()
            
            if route_data.get('code') != 'Ok':
                return jsonify({'error': f"OSRM API báo lỗi: {route_data.get('message')}"}), 500
            
            main_route = route_data['routes'][0]
            main_leg = main_route['legs'][0]
            steps_list = []
            for step in main_leg['steps']:
                if step['name'] and step['name'] not in steps_list:
                    steps_list.append(step['name'])
            
            waypoints_timeline = [
                {'name': start_point_name, 'detail': 'Xuất phát'},
                {'name': end_point_name, 'detail': 'Đích đến'}
            ]
            
            real_route_result = {
                'distance_km': round(main_route['distance'] / 1000.0, 1),
                'duration_min': math.ceil(main_route['duration'] / 60.0),
                'traffic': 'Dữ liệu thời gian thực từ OSRM.', 
                'steps': steps_list, 
                'waypoints_timeline': waypoints_timeline, 
                'coordinates': [ 
                    [start_point.ViDo, start_point.KinhDo], 
                    [end_point.ViDo, end_point.KinhDo] 
                ]
            }
            return jsonify(real_route_result)

    except requests.exceptions.RequestException as e:
        app.logger.exception('======= LỖI KHI GỌI OSRM API =======')
        return jsonify({'error': f"Lỗi khi gọi API định tuyến: {str(e)}"}), 500
        
    except Exception as e:
        app.logger.exception('======= LỖI TRONG API /api/find-route =======')
        return jsonify({'error': f"Lỗi server khi tìm đường: {str(e)}"}), 500
