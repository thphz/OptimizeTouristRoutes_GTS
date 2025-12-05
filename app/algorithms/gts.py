"""
Module thuật toán Greedy TSP (GTS) cho tối ưu tuyến đường du lịch.

Module này cung cấp các hàm để tối ưu hóa tuyến đường tham quan sử dụng
thuật toán Greedy (tham lam) dựa trên phương pháp Nearest Neighbor.
"""

import math
import requests
from typing import List, Dict, Tuple, Optional, Any


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Tính khoảng cách giữa hai điểm theo công thức Haversine.
    
    Tham số:
        lat1, lon1: Vĩ độ và kinh độ điểm 1
        lat2, lon2: Vĩ độ và kinh độ điểm 2
    
    Trả về:
        Khoảng cách tính bằng kilômét (km)
    """
    R = 6371.0  # Bán kính Trái Đất tính bằng km
    
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_phi / 2.0) ** 2 + 
         math.cos(phi1) * math.cos(phi2) * 
         math.sin(delta_lambda / 2.0) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


def calculate_route_distance(route: List[Dict], return_to_start: bool = False) -> float:
    """
    Tính tổng khoảng cách của một tuyến đường.
    
    Tham số:
        route: Danh sách các điểm tham quan theo thứ tự (mỗi điểm có 'lat', 'lng')
        return_to_start: Có quay về điểm xuất phát hay không
    
    Trả về:
        Tổng khoảng cách tính bằng km
    """
    if len(route) < 2:
        return 0.0
    
    total_distance = 0.0
    
    for i in range(len(route) - 1):
        lat1 = route[i].get('lat') or route[i].get('vi_do')
        lon1 = route[i].get('lng') or route[i].get('kinh_do')
        lat2 = route[i + 1].get('lat') or route[i + 1].get('vi_do')
        lon2 = route[i + 1].get('lng') or route[i + 1].get('kinh_do')
        
        if lat1 and lon1 and lat2 and lon2:
            total_distance += haversine_distance(
                float(lat1), float(lon1), 
                float(lat2), float(lon2)
            )
    
    # Nếu quay về điểm xuất phát
    if return_to_start and len(route) > 1:
        lat_start = route[0].get('lat') or route[0].get('vi_do')
        lon_start = route[0].get('lng') or route[0].get('kinh_do')
        lat_end = route[-1].get('lat') or route[-1].get('vi_do')
        lon_end = route[-1].get('lng') or route[-1].get('kinh_do')
        
        if lat_start and lon_start and lat_end and lon_end:
            total_distance += haversine_distance(
                float(lat_end), float(lon_end),
                float(lat_start), float(lon_start)
            )
    
    return total_distance


def greedy_nearest_neighbor(points: List[Dict], 
                           start_point_id: Optional[int] = None,
                           return_to_start: bool = False) -> Dict[str, Any]:
    """
    Thuật toán Greedy TSP sử dụng phương pháp Nearest Neighbor.
    
    Tham số:
        points: Danh sách các điểm tham quan (mỗi điểm cần có 'id', 'lat'/'vi_do', 'lng'/'kinh_do')
        start_point_id: ID điểm xuất phát (nếu None, chọn điểm đầu tiên)
        return_to_start: Có quay về điểm xuất phát hay không
    
    Trả về:
        Dict chứa:
            - route: Danh sách các điểm đã sắp xếp tối ưu
            - route_order: Danh sách ID theo thứ tự
            - total_distance: Tổng khoảng cách (km)
            - waypoints: Danh sách điểm với thông tin bổ sung
    """
    if not points or len(points) == 0:
        return {
            'route': [],
            'route_order': [],
            'total_distance': 0.0,
            'waypoints': []
        }
    
    if len(points) == 1:
        point = points[0]
        return {
            'route': [point],
            'route_order': [point.get('id')],
            'total_distance': 0.0,
            'waypoints': [_format_waypoint(point, 0, True, True)]
        }
    
    # Chuẩn hóa dữ liệu điểm
    normalized_points = []
    for p in points:
        lat = p.get('lat') or p.get('vi_do') or getattr(p, 'vi_do', None) or getattr(p, 'lat', None)
        lng = p.get('lng') or p.get('kinh_do') or getattr(p, 'kinh_do', None) or getattr(p, 'lng', None)
        point_id = p.get('id') or getattr(p, 'id', None)
        name = p.get('name') or p.get('ten') or getattr(p, 'ten', None) or getattr(p, 'TenDiem', None)
        
        if lat is not None and lng is not None and point_id is not None:
            normalized_points.append({
                'id': point_id,
                'lat': float(lat),
                'lng': float(lng),
                'name': name or f"Điểm {point_id}",
                'original': p
            })
    
    if not normalized_points:
        return {
            'route': [],
            'route_order': [],
            'total_distance': 0.0,
            'waypoints': []
        }
    
    # Tìm điểm xuất phát
    if start_point_id is not None:
        start_index = next((i for i, p in enumerate(normalized_points) if p['id'] == start_point_id), 0)
    else:
        start_index = 0
    
    # Thuật toán Greedy - Nearest Neighbor
    unvisited = normalized_points.copy()
    route = []
    current = unvisited.pop(start_index)
    route.append(current)
    
    while unvisited:
        # Tìm điểm gần nhất chưa thăm
        nearest_dist = float('inf')
        nearest_index = 0
        
        for i, point in enumerate(unvisited):
            dist = haversine_distance(
                current['lat'], current['lng'],
                point['lat'], point['lng']
            )
            if dist < nearest_dist:
                nearest_dist = dist
                nearest_index = i
        
        current = unvisited.pop(nearest_index)
        route.append(current)
    
    # Tính tổng khoảng cách
    total_distance = calculate_route_distance(route, return_to_start)
    
    # Tạo danh sách waypoints với thông tin chi tiết
    waypoints = []
    for idx, point in enumerate(route):
        is_start = (idx == 0)
        is_end = (idx == len(route) - 1)
        waypoints.append(_format_waypoint(point, idx, is_start, is_end))
    
    if return_to_start and len(route) > 1:
        waypoints.append(_format_waypoint(route[0], len(route), False, True, "Quay về điểm xuất phát"))
    
    return {
        'route': route,
        'route_order': [p['id'] for p in route],
        'total_distance': round(total_distance, 2),
        'waypoints': waypoints
    }


def _format_waypoint(point: Dict, index: int, is_start: bool, is_end: bool, detail: Optional[str] = None) -> Dict:
    """
    Định dạng thông tin waypoint để trả về.
    
    Tham số:
        point: Điểm tham quan
        index: Thứ tự trong tuyến đường
        is_start: Có phải điểm xuất phát
        is_end: Có phải điểm cuối
        detail: Mô tả bổ sung
    
    Trả về:
        Dict chứa thông tin waypoint đã định dạng
    """
    if detail is None:
        if is_start:
            detail = "Điểm xuất phát"
        elif is_end:
            detail = "Điểm đến"
        else:
            detail = f"Điểm {index + 1}"
    
    return {
        'name': point['name'],
        'detail': detail,
        'order': index + 1,
        'lat': point['lat'],
        'lng': point['lng'],
        'id': point['id']
    }


def optimize_route_with_osrm(points: List[Dict],
                             start_point_id: Optional[int] = None,
                             osrm_base: str = 'http://router.project-osrm.org') -> Dict[str, Any]:
    """
    Tối ưu tuyến đường sử dụng OSRM Trip service (kết hợp Greedy fallback).
    
    Tham số:
        points: Danh sách các điểm tham quan
        start_point_id: ID điểm xuất phát
        osrm_base: URL cơ sở của OSRM server
    
    Trả về:
        Dict chứa thông tin tuyến đường tối ưu hoặc fallback về Greedy
    """
    if not points or len(points) < 2:
        return greedy_nearest_neighbor(points, start_point_id, False)
    
    try:
        # Chuẩn hóa dữ liệu
        normalized_points = []
        for p in points:
            lat = p.get('lat') or p.get('vi_do') or getattr(p, 'vi_do', None)
            lng = p.get('lng') or p.get('kinh_do') or getattr(p, 'kinh_do', None)
            point_id = p.get('id') or getattr(p, 'id', None)
            
            if lat and lng and point_id:
                normalized_points.append({
                    'id': point_id,
                    'lat': float(lat),
                    'lng': float(lng),
                    'name': p.get('name') or p.get('ten') or f"Điểm {point_id}",
                    'original': p
                })
        
        if len(normalized_points) < 2:
            return greedy_nearest_neighbor(points, start_point_id, False)
        
        # Xây dựng chuỗi tọa độ cho OSRM (lon,lat)
        coords = ";".join([f"{p['lng']},{p['lat']}" for p in normalized_points])
        
        # Xác định điểm xuất phát
        source_param = ""
        if start_point_id:
            start_idx = next((i for i, p in enumerate(normalized_points) if p['id'] == start_point_id), None)
            if start_idx is not None:
                source_param = f"&source={start_idx}"
        
        url = f"{osrm_base}/trip/v1/driving/{coords}?roundtrip=false{source_param}&annotations=distance,duration"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('code') == 'Ok' and 'trips' in data and len(data['trips']) > 0:
            trip = data['trips'][0]
            waypoints = data.get('waypoints', [])
            
            # Sắp xếp lại điểm theo thứ tự OSRM trả về
            optimized_route = []
            for wp in waypoints:
                wp_index = wp.get('waypoint_index')
                if wp_index is not None and wp_index < len(normalized_points):
                    optimized_route.append(normalized_points[wp_index])
            
            total_distance = trip.get('distance', 0) / 1000.0  # Chuyển sang km
            total_duration = trip.get('duration', 0) / 60.0  # Chuyển sang phút
            
            # Tạo waypoints
            waypoints_list = []
            for idx, point in enumerate(optimized_route):
                is_start = (idx == 0)
                is_end = (idx == len(optimized_route) - 1)
                waypoints_list.append(_format_waypoint(point, idx, is_start, is_end))
            
            return {
                'route': optimized_route,
                'route_order': [p['id'] for p in optimized_route],
                'total_distance': round(total_distance, 2),
                'total_duration': round(total_duration, 1),
                'waypoints': waypoints_list,
                'method': 'osrm'
            }
        
    except Exception as e:
        # Nếu OSRM thất bại, fallback về Greedy
        pass
    
    # Fallback về thuật toán Greedy
    result = greedy_nearest_neighbor(points, start_point_id, False)
    result['method'] = 'greedy'
    return result


def calculate_estimated_duration(route: List[Dict], avg_speed_kmh: float = 30.0, 
                                visit_duration_min: int = 60) -> Dict[str, Any]:
    """
    Tính thời gian ước tính cho tuyến đường.
    
    Tham số:
        route: Danh sách các điểm đã sắp xếp
        avg_speed_kmh: Tốc độ trung bình (km/h)
        visit_duration_min: Thời gian tham quan mỗi điểm (phút)
    
    Trả về:
        Dict chứa thông tin thời gian chi tiết
    """
    if not route or len(route) == 0:
        return {
            'travel_time_min': 0,
            'visit_time_min': 0,
            'total_time_min': 0
        }
    
    # Tính thời gian di chuyển
    distance = calculate_route_distance(route, False)
    travel_time_hours = distance / avg_speed_kmh
    travel_time_min = travel_time_hours * 60
    
    # Tính thời gian tham quan
    total_visit_time = len(route) * visit_duration_min
    
    # Tổng thời gian
    total_time = travel_time_min + total_visit_time
    
    return {
        'travel_time_min': round(travel_time_min, 1),
        'visit_time_min': total_visit_time,
        'total_time_min': round(total_time, 1),
        'travel_time_hours': round(travel_time_hours, 2),
        'total_time_hours': round(total_time / 60, 2)
    }


def gts_optimize(points: List[Dict], 
                start_point_id: Optional[int] = None,
                return_to_start: bool = False,
                use_osrm: bool = True,
                avg_speed_kmh: float = 30.0,
                visit_duration_min: int = 60) -> Dict[str, Any]:
    """
    Hàm chính để tối ưu tuyến đường du lịch bằng thuật toán GTS.
    
    Đây là hàm tiện ích chính được sử dụng trong các route/API endpoints.
    
    Tham số:
        points: Danh sách các điểm tham quan
        start_point_id: ID điểm xuất phát (optional)
        return_to_start: Có quay về điểm xuất phát không
        use_osrm: Có sử dụng OSRM API không (nếu không thì dùng Greedy thuần)
        avg_speed_kmh: Tốc độ trung bình để ước tính thời gian
        visit_duration_min: Thời gian tham quan mỗi điểm
    
    Trả về:
        Dict chứa đầy đủ thông tin tuyến đường tối ưu:
            - route: Danh sách điểm đã sắp xếp
            - route_order: Danh sách ID theo thứ tự
            - total_distance: Tổng khoảng cách (km)
            - waypoints: Thông tin các điểm dừng
            - duration_info: Thông tin thời gian chi tiết
            - method: Phương pháp được sử dụng ('osrm' hoặc 'greedy')
    """
    if not points:
        return {
            'route': [],
            'route_order': [],
            'total_distance': 0.0,
            'waypoints': [],
            'duration_info': calculate_estimated_duration([]),
            'method': 'none',
            'error': 'Không có điểm tham quan nào'
        }
    
    # Tối ưu tuyến đường
    if use_osrm and len(points) >= 2:
        result = optimize_route_with_osrm(points, start_point_id)
    else:
        result = greedy_nearest_neighbor(points, start_point_id, return_to_start)
    
    # Tính thời gian ước tính
    duration_info = calculate_estimated_duration(
        result['route'], 
        avg_speed_kmh, 
        visit_duration_min
    )
    result['duration_info'] = duration_info
    
    return result
