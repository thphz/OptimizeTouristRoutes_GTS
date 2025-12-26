from app import app
from flask import redirect, url_for, request, render_template, jsonify
import math
import traceback
import requests
import re


class Obj:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def sort_quan_key(quan):
    """
    Helper function để sắp xếp quận theo thứ tự: số trước, chữ sau.
    VD: Quận 1, Quận 2, ..., Quận 12, Quận Bình Thạnh, Quận Phú Nhuận
    """
    ten_quan = quan.ten if hasattr(quan, 'ten') else quan.TenQuan
    
    # Tìm số trong tên quận (VD: "Quận 1" -> 1, "Quận 12" -> 12)
    match = re.search(r'\d+', ten_quan)
    if match:
        # Nếu có số, trả về tuple (0, số) để sort số trước
        return (0, int(match.group()))
    else:
        # Nếu không có số (quận tên chữ), trả về tuple (1, tên) để sort sau
        return (1, ten_quan)


@app.route('/')
def index():
    return render_template('homepage.html')


@app.route('/homepage')
def homepage():
    return render_template('homepage.html')


@app.route('/select_points', methods=['GET', 'POST'])
def select_points():
    # Cố gắng tải từ các model thực tế; nếu có lỗi thì dùng dữ liệu giả để thay thế
    error = None
    try:
        from app.models import Quan, LoaiDiemThamQuan, DiemThamQuan

        quans = Quan.query.all()
        # Sắp xếp quận: số trước, chữ sau
        quans = sorted(quans, key=sort_quan_key)
        
        loai_diems = LoaiDiemThamQuan.query.order_by(LoaiDiemThamQuan.TenLoai).all()
        diems = DiemThamQuan.query.order_by(DiemThamQuan.TenDiem).all()

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

        quans = [
            Obj(id=1, ten='Quận 1'), 
            Obj(id=2, ten='Quận 2'),
            Obj(id=3, ten='Quận 3'), 
            Obj(id=4, ten='Quận 4'),
            Obj(id=5, ten='Quận 5'),
            Obj(id=6, ten='Quận 6'),
            Obj(id=7, ten='Quận 7'),
            Obj(id=8, ten='Quận 8'),
            Obj(id=9, ten='Quận 9'),
            Obj(id=10, ten='Quận 10'),
            Obj(id=11, ten='Quận 11'),
            Obj(id=12, ten='Quận 12'),
            Obj(id=13, ten='Quận Bình Tân'),
            Obj(id=14, ten='Quận Bình Thạnh'),
            Obj(id=15, ten='Quận Gò Vấp'),
            Obj(id=16, ten='Quận Phú Nhuận'),
            Obj(id=17, ten='Quận Tân Bình'),
            Obj(id=18, ten='Quận Tân Phú'),
            Obj(id=19, ten='Quận Thủ Đức')
        ]
        loai_diems = [Obj(id=1, ten='Đền/Đình'), Obj(id=2, ten='Bảo tàng'), Obj(id=3, ten='Nhà thờ')]
        diems = [
            Obj(id=1, ten='Dinh Độc Lập', duration=60, quan_id=1, quan=quans[0], loai_id=1, vi_do=10.7769, kinh_do=106.7009),
            Obj(id=2, ten='Nhà Thờ Đức Bà', duration=45, quan_id=1, quan=quans[0], loai_id=3, vi_do=10.7798, kinh_do=106.6996),
            Obj(id=3, ten='Bưu Điện Trung Tâm Sài Gòn', duration=30, quan_id=1, quan=quans[0], loai_id=1, vi_do=10.7790, kinh_do=106.6992),
            Obj(id=4, ten='Phố Đi Bộ Nguyễn Huệ', duration=45, quan_id=1, quan=quans[0], loai_id=2, vi_do=10.7774, kinh_do=106.6991),
            Obj(id=5, ten='Bảo Tàng Chứng Tích Chiến Tranh', duration=90, quan_id=3, quan=quans[2], loai_id=2, vi_do=10.7776, kinh_do=106.6887),
        ]

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
        from app.algorithms.gts import gts_optimize
        
        data = request.get_json()
        points = data.get('points', [])
        start_point_id = data.get('start_point_id')
        return_to_start = data.get('return_to_start', True)  # Mặc định là True
        use_osrm = data.get('use_osrm', True)
        use_multi_start = data.get('use_multi_start', True)  # Mặc định bật Multi-Start
       
        if len(points) < 2:
            return jsonify({"error": "Vui lòng chọn ít nhất 2 điểm để tìm tuyến đường."}), 400
        
        # Log các tham số đầu vào
        app.logger.info(f"=== API /api/route_optimize ===")
        app.logger.info(f"Points count: {len(points)}")
        app.logger.info(f"start_point_id: {start_point_id}")
        app.logger.info(f"return_to_start: {return_to_start}")
        app.logger.info(f"use_osrm: {use_osrm}")
        app.logger.info(f"use_multi_start: {use_multi_start}")
        
        # Sử dụng thuật toán GTS để tối ưu tuyến đường
        result = gts_optimize(
            points=points,
            start_point_id=start_point_id,
            return_to_start=return_to_start,
            use_osrm=use_osrm,
            use_multi_start=use_multi_start,
            avg_speed_kmh=30.0
        )
        
        # Log kết quả
        app.logger.info(f"Result method: {result.get('method')}")
        app.logger.info(f"Result multi_start_used: {result.get('multi_start_used')}")
        app.logger.info(f"Result attempts: {result.get('attempts')}")
        app.logger.info(f"Result total_distance: {result.get('total_distance')}")
        
        if 'error' in result:
            return jsonify(result), 400
    
        response_data = {
            "route_order": result['route_order'],
            "total_distance": result['total_distance'],
            "waypoints": result['waypoints'],
            "duration_info": result['duration_info'],
            "method": result.get('method', 'greedy'),
            "return_to_start": result.get('return_to_start', False),
            "coordinates": [[p['lat'], p['lng']] for p in result['route']],
            "multi_start_used": result.get('multi_start_used', False),
            "attempts": result.get('attempts', 1)
        }
        
        app.logger.info(f"Response multi_start_used: {response_data['multi_start_used']}")
        app.logger.info(f"Response attempts: {response_data['attempts']}")
        
        return jsonify(response_data)
        
    except Exception as e:
        app.logger.exception('Error optimizing route: %s', e)
        return jsonify({'error': str(e)}), 500


@app.route('/find-route')
def find_route_page():
    """Hiển thị trang giao diện 'Tìm Đường'."""
    return render_template('find_route.html', title='Tìm Lộ Trình Tối Ưu')


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
    use_multi_start = data.get('use_multi_start', True)  # Mặc định bật Multi-Start

    try:
        from app.models import DiemThamQuan
        from app.algorithms.gts import gts_optimize
        
        start_point = DiemThamQuan.query.get(start_point_id)
        end_point = DiemThamQuan.query.get(end_point_id)
        
        if not start_point or not end_point:
             return jsonify({'error': 'Không tìm thấy điểm bắt đầu hoặc kết thúc trong DB'}), 404
        
        start_point_name = start_point.TenDiem
        end_point_name = end_point.TenDiem
        
        if route_type == 'scenic':
            # Sử dụng GTS để tối ưu tuyến đường tham quan nhiều điểm
            # Lấy các điểm lân cận để tạo tuyến tham quan
            try:
                all_points = DiemThamQuan.query.limit(10).all()
                points_data = [p.to_dict() for p in all_points]
                
                result = gts_optimize(
                    points=points_data,
                    start_point_id=start_point_id,
                    return_to_start=True,
                    use_osrm=True,
                    use_multi_start=use_multi_start,
                    avg_speed_kmh=25.0
                )
                
                # Tạo coordinates từ route
                coordinates = [[p['lat'], p['lng']] for p in result.get('route', [])]
                
                gts_route = {
                    'distance_km': result.get('total_distance', 0), 
                    'duration_min': result.get('duration_info', {}).get('total_time_min', 0),
                    'travel_time_min': result.get('duration_info', {}).get('travel_time_min', 0),
                    'visit_time_min': result.get('duration_info', {}).get('visit_time_min', 0),
                    'traffic': f"Tối ưu bằng {result.get('method', 'GTS')}.",
                    'steps': [f"Thăm quan {len(result.get('route', []))} điểm"],
                    'waypoints_timeline': result.get('waypoints', []),
                    'coordinates': coordinates,
                    'method': result.get('method', 'greedy'),
                    'multi_start_used': result.get('multi_start_used', False),
                    'attempts': result.get('attempts', 1)
                }
                return jsonify(gts_route)
                
            except Exception as e:
                app.logger.exception('Error using GTS for scenic route: %s', e)
                # Fallback về dữ liệu mô phỏng cũ
                dummy_gts_route = {
                    'distance_km': 51.2, 
                    'duration_min': 148,
                    'traffic': 'Giao thông không áp dụng.',
                    'steps': ['Lộ trình tham quan vòng quanh thành phố.'],
                    'waypoints_timeline': [
                        {'name': start_point_name, 'detail': 'Xuất phát'},
                        {'name': 'Dinh Độc Lập'},
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


# --- QUẢN LÝ ĐỊA ĐIỂM THAM QUAN ---

@app.route('/manage_locations')
def manage_locations():
    """Hiển thị trang quản lý địa điểm tham quan."""
    try:
        from app.models import Quan, LoaiDiemThamQuan
        
        quans = Quan.query.all()
        # Sắp xếp quận: số trước, chữ sau
        quans = sorted(quans, key=sort_quan_key)
        
        loai_diems = LoaiDiemThamQuan.query.order_by(LoaiDiemThamQuan.TenLoai).all()
        
        return render_template('manage_locations.html', quans=quans, loai_diems=loai_diems)
        
    except Exception as e:
        app.logger.exception('Could not load data for manage_locations: %s', e)
        # Fallback với dữ liệu mock - đã sắp xếp
        quans = [
            Obj(id=1, ten='Quận 1'), 
            Obj(id=2, ten='Quận 2'),
            Obj(id=3, ten='Quận 3'),
            Obj(id=4, ten='Quận 4'),
            Obj(id=5, ten='Quận 5'),
            Obj(id=6, ten='Quận 6'),
            Obj(id=7, ten='Quận 7'),
            Obj(id=8, ten='Quận 8'),
            Obj(id=9, ten='Quận 9'),
            Obj(id=10, ten='Quận 10'),
            Obj(id=11, ten='Quận 11'),
            Obj(id=12, ten='Quận 12'),
            Obj(id=13, ten='Quận Bình Tân'),
            Obj(id=14, ten='Quận Bình Thạnh'),
            Obj(id=15, ten='Quận Gò Vấp'),
            Obj(id=16, ten='Quận Phú Nhuận'),
            Obj(id=17, ten='Quận Tân Bình'),
            Obj(id=18, ten='Quận Tân Phú'),
            Obj(id=19, ten='Quận Thủ Đức')
        ]
        loai_diems = [Obj(id=1, ten='Đền/Đình'), Obj(id=2, ten='Bảo tàng')]
        return render_template('manage_locations.html', quans=quans, loai_diems=loai_diems)


@app.route('/api/manage/locations', methods=['GET'])
def api_get_all_locations():
    """API lấy danh sách tất cả địa điểm cho trang quản lý."""
    try:
        from app.models import DiemThamQuan

        diems = DiemThamQuan.query.order_by(DiemThamQuan.TenDiem).all()

        result = []
        for diem in diems:
            result.append({
                'id': diem.DiemID,
                'name': diem.TenDiem,
                'description': diem.MoTa,
                'address': diem.DiaChi,
                'quan_id': diem.QuanID,
                'quan_name': diem.quan.TenQuan if diem.quan else '',
                'loai_id': diem.LoaiID,
                'loai_name': diem.loai.TenLoai if diem.loai else '',
                'lat': float(diem.ViDo) if diem.ViDo else 0,
                'lng': float(diem.KinhDo) if diem.KinhDo else 0,
                'open_time': diem.GioMoCua.strftime('%H:%M') if diem.GioMoCua else '',
                'close_time': diem.GioDongCua.strftime('%H:%M') if diem.GioDongCua else '',
                'duration': diem.duration,
                'image_url': diem.image_url
            })

        return jsonify(result)

    except Exception as e:
        app.logger.exception('Error getting locations: %s', e)
        return jsonify({'error': str(e)}), 500


@app.route('/api/manage/locations/<int:location_id>', methods=['GET'])
def api_get_single_location(location_id):
    """API lấy thông tin chi tiết một địa điểm."""
    try:
        from app.models import DiemThamQuan

        diem = DiemThamQuan.query.get(location_id)

        if not diem:
            return jsonify({'error': 'Không tìm thấy địa điểm'}), 404

        result = {
            'id': diem.DiemID,
            'name': diem.TenDiem,
            'description': diem.MoTa,
            'address': diem.DiaChi,
            'quan_id': diem.QuanID,
            'quan_name': diem.quan.TenQuan if diem.quan else '',
            'loai_id': diem.LoaiID,
            'loai_name': diem.loai.TenLoai if diem.loai else '',
            'lat': float(diem.ViDo) if diem.ViDo else 0,
            'lng': float(diem.KinhDo) if diem.KinhDo else 0,
            'open_time': diem.GioMoCua.strftime('%H:%M') if diem.GioMoCua else '',
            'close_time': diem.GioDongCua.strftime('%H:%M') if diem.GioDongCua else '',
            'duration': diem.duration,
            'image_url': diem.image_url
        }

        return jsonify(result)

    except Exception as e:
        app.logger.exception('Error getting location: %s', e)
        return jsonify({'error': str(e)}), 500


@app.route('/api/manage/locations', methods=['POST'])
def api_create_location():
    """API tạo địa điểm mới."""
    try:
        from app.models import DiemThamQuan, HinhAnhDiem
        from app import db
        from datetime import datetime

        data = request.get_json()

        # Validate dữ liệu
        if not data.get('name'):
            return jsonify({'error': 'Tên địa điểm không được để trống'}), 400
        if not data.get('lat') or not data.get('lng'):
            return jsonify({'error': 'Vị trí (tọa độ) không được để trống'}), 400

        duration = data.get('duration')
        try:
            duration = int(duration) if duration is not None and str(duration).strip() != '' else 60
        except (TypeError, ValueError):
            return jsonify({'error': 'Thời gian tham quan không hợp lệ'}), 400

        # Tạo địa điểm mới
        new_diem = DiemThamQuan(
            TenDiem=data.get('name'),
            MoTa=data.get('description'),
            DiaChi=data.get('address'),
            QuanID=data.get('quan_id'),
            LoaiID=data.get('loai_id'),
            ViDo=float(data.get('lat')),
            KinhDo=float(data.get('lng')),
            GioMoCua=datetime.strptime(data.get('open_time'), '%H:%M').time() if data.get('open_time') else None,
            GioDongCua=datetime.strptime(data.get('close_time'), '%H:%M').time() if data.get('close_time') else None,
            Duration=duration
        )

        db.session.add(new_diem)
        db.session.flush()  # Để lấy ID của địa điểm mới

        # Thêm hình ảnh nếu có
        image_url = data.get('image_url')
        if image_url and image_url.strip():
            new_image = HinhAnhDiem(
                DiemID=new_diem.DiemID,
                UrlHinh=image_url.strip(),
                MoTaHinh=f"Hình ảnh của {new_diem.TenDiem}"
            )
            db.session.add(new_image)

        db.session.commit()

        return jsonify({
            'message': 'Tạo địa điểm thành công',
            'id': new_diem.DiemID
        }), 201

    except Exception as e:
        app.logger.exception('Error creating location: %s', e)
        if db:
            db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/manage/locations/<int:location_id>', methods=['PUT'])
def api_update_location(location_id):
    """API cập nhật thông tin địa điểm."""
    try:
        from app.models import DiemThamQuan, HinhAnhDiem
        from app import db
        from datetime import datetime

        diem = DiemThamQuan.query.get(location_id)

        if not diem:
            return jsonify({'error': 'Không tìm thấy địa điểm'}), 404

        data = request.get_json()

        # Validate dữ liệu
        if not data.get('name'):
            return jsonify({'error': 'Tên địa điểm không được để trống'}), 400
        if not data.get('lat') or not data.get('lng'):
            return jsonify({'error': 'Vị trí (tọa độ) không được để trống'}), 400

        duration = data.get('duration')
        try:
            duration = int(duration) if duration is not None and str(duration).strip() != '' else diem.duration
        except (TypeError, ValueError):
            return jsonify({'error': 'Thời gian tham quan không hợp lệ'}), 400

        # Cập nhật thông tin
        diem.TenDiem = data.get('name')
        diem.MoTa = data.get('description')
        diem.DiaChi = data.get('address')
        diem.QuanID = data.get('quan_id')
        diem.LoaiID = data.get('loai_id')
        diem.ViDo = float(data.get('lat'))
        diem.KinhDo = float(data.get('lng'))
        diem.GioMoCua = datetime.strptime(data.get('open_time'), '%H:%M').time() if data.get('open_time') else None
        diem.GioDongCua = datetime.strptime(data.get('close_time'), '%H:%M').time() if data.get('close_time') else None
        diem.Duration = duration

        # Cập nhật hình ảnh
        image_url = data.get('image_url')

        # Lấy hình ảnh hiện tại (nếu có)
        existing_image = HinhAnhDiem.query.filter_by(DiemID=location_id).first()

        if image_url and image_url.strip():
            # Nếu có URL mới
            if existing_image:
                # Cập nhật hình ảnh hiện tại
                existing_image.UrlHinh = image_url.strip()
                existing_image.MoTaHinh = f"Hình ảnh của {diem.TenDiem}"
            else:
                # Tạo hình ảnh mới
                new_image = HinhAnhDiem(
                    DiemID=location_id,
                    UrlHinh=image_url.strip(),
                    MoTaHinh=f"Hình ảnh của {diem.TenDiem}"
                )
                db.session.add(new_image)
        else:
            # Nếu không có URL (xóa hình ảnh)
            if existing_image:
                db.session.delete(existing_image)

        db.session.commit()

        return jsonify({'message': 'Cập nhật địa điểm thành công'})

    except Exception as e:
        app.logger.exception('Error updating location: %s', e)
        if db:
            db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/manage/locations/<int:location_id>', methods=['DELETE'])
def api_delete_location(location_id):
    """API xóa địa điểm."""
    try:
        from app.models import DiemThamQuan
        from app import db
        
        diem = DiemThamQuan.query.get(location_id)
        
        if not diem:
            return jsonify({'error': 'Không tìm thấy địa điểm'}), 404
        
        db.session.delete(diem)
        db.session.commit()
        
        return jsonify({'message': 'Xóa địa điểm thành công'})
        
    except Exception as e:
        app.logger.exception('Error deleting location: %s', e)
        if db:
            db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/locations')
def get_locations():
    """API endpoint để trả về danh sách các địa điểm cho trang find-route."""
    try:
        from app.models import DiemThamQuan

        locations_data = DiemThamQuan.query.order_by(DiemThamQuan.TenDiem).all()
        locations_list = [loc.to_dict() for loc in locations_data]
        return jsonify(locations_list)

    except Exception as e:
        # Giữ UI hoạt động ngay cả khi DB/models không khả dụng (tương tự `select_points`).
        app.logger.exception('Could not load locations from DB, using mock data: %s', e)

        mock_locations = [
            Obj(id=1, name='Dinh Độc Lập', lat=10.7769, lng=106.7009),
            Obj(id=2, name='Nhà Thờ Đức Bà', lat=10.7798, lng=106.6996),
            Obj(id=3, name='Bưu Điện Trung Tâm Sài Gòn', lat=10.7790, lng=106.6992),
            Obj(id=4, name='Phố Đi Bộ Nguyễn Huệ', lat=10.7774, lng=106.6991),
            Obj(id=5, name='Bảo Tàng Chứng Tích Chiến Tranh', lat=10.7776, lng=106.6887),
        ]

        return jsonify([
            {
                'id': loc.id,
                'name': loc.name,
                'lat': loc.lat,
                'lng': loc.lng,
            }
            for loc in mock_locations
        ])
