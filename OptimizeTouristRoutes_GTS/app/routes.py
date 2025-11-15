from app import app, db
from flask import render_template, jsonify, request
import traceback 
import math 
import requests 

from app.models import DiemThamQuan 
@app.route('/find-route')
def find_route_page():
    """Hiển thị trang giao diện 'Tìm Đường'."""
    return render_template('find_route.html', title='Tìm Lộ Trình Tối Ưu')

@app.route('/api/locations')
def get_locations():
    """API endpoint để trả về danh sách các địa điểm."""
    try:
        locations_data = DiemThamQuan.query.order_by(DiemThamQuan.TenDiem).all()
        locations_list = [loc.to_dict() for loc in locations_data]
        return jsonify(locations_list)
        
    except Exception as e:
        print("======= LỖI KẾT NỐI DB / QUERY MODEL =======")
        traceback.print_exc()
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
            
            print(f"Đang gọi API OSRM: {osrm_url}")
            
            response = requests.get(osrm_url)
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
        print(f"======= LỖI KHI GỌI OSRM API =======")
        traceback.print_exc()
        return jsonify({'error': f"Lỗi khi gọi API định tuyến: {str(e)}"}), 500
        
    except Exception as e:
        print("======= LỖI TRONG API /api/find-route =======")
        traceback.print_exc()
        return jsonify({'error': f"Lỗi server khi tìm đường: {str(e)}"}), 500