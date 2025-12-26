"""
Module thuật toán Greedy TSP (GTS) cho tối ưu tuyến đường du lịch.

Module này cung cấp các hàm để tối ưu hóa tuyến đường tham quan sử dụng
thuật toán Greedy (tham lam) dựa trên phương pháp Nearest Neighbor với Multi-Start.

Tất cả logic tính toán thời gian được tập trung tại đây để đảm bảo tính nhất quán.
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


def get_real_time_duration_osrm(lat1: float, lon1: float, lat2: float, lon2: float, 
                                 osrm_base: str = 'http://router.project-osrm.org',
                                 timeout: int = 5) -> Optional[Dict[str, float]]:
    """
    Lấy thông tin khoảng cách và thời gian thực tế từ OSRM API.
    
    Tham số:
        lat1, lon1: Tọa độ điểm xuất phát
        lat2, lon2: Tọa độ điểm đích
        osrm_base: URL cơ sở của OSRM server
        timeout: Thời gian timeout cho request (giây)
    
    Trả về:
        Dict chứa 'distance_km' và 'duration_min', hoặc None nếu lỗi
    """
    try:
        coords = f"{lon1},{lat1};{lon2},{lat2}"
        url = f"{osrm_base}/route/v1/driving/{coords}?overview=false"
        
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('code') == 'Ok' and 'routes' in data and len(data['routes']) > 0:
            route = data['routes'][0]
            distance_km = route.get('distance', 0) / 1000.0
            duration_min = route.get('duration', 0) / 60.0
            
            return {
                'distance_km': distance_km,
                'duration_min': duration_min
            }
    except Exception:
        # Nếu có lỗi, trả về None để fallback về phương pháp ước tính
        pass
    
    return None


def get_route_segments_duration_osrm(route: List[Dict],
                                     return_to_start: bool = False,
                                     osrm_base: str = 'http://router.project-osrm.org',
                                     timeout: int = 10) -> Optional[List[Dict[str, float]]]:
    """
    Lấy thông tin thời gian thực cho tất cả các đoạn đường trong tuyến.
    
    Tham số:
        route: Danh sách các điểm theo thứ tự
        return_to_start: Có tính đoạn quay về điểm xuất phát không
        osrm_base: URL cơ sở của OSRM server
        timeout: Thời gian timeout cho request
    
    Trả về:
        List các dict chứa thông tin mỗi đoạn đường, hoặc None nếu lỗi
    """
    if len(route) < 2:
        return []
    
    try:
        # Xây dựng chuỗi tọa độ
        coords_list = []
        for point in route:
            lat = point.get('lat') or point.get('vi_do')
            lng = point.get('lng') or point.get('kinh_do')
            if lat and lng:
                coords_list.append(f"{lng},{lat}")
        
        # Nếu quay về điểm xuất phát, thêm điểm đầu vào cuối
        if return_to_start and len(coords_list) > 0:
            coords_list.append(coords_list[0])
        
        if len(coords_list) < 2:
            return None
        
        coords = ";".join(coords_list)
        url = f"{osrm_base}/route/v1/driving/{coords}?overview=false&steps=false"
        
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('code') == 'Ok' and 'routes' in data and len(data['routes']) > 0:
            route_data = data['routes'][0]
            legs = route_data.get('legs', [])
            
            segments = []
            for leg in legs:
                segments.append({
                    'distance_km': leg.get('distance', 0) / 1000.0,
                    'duration_min': leg.get('duration', 0) / 60.0
                })
            
            return segments
    except Exception:
        pass
    
    return None


def get_point_duration(point: Dict, default: int = 60) -> int:
    """
    Lấy thời gian tham quan của một điểm (phút).
    
    Tham số:
        point: Dictionary hoặc object chứa thông tin điểm
        default: Thời gian mặc định nếu không tìm thấy
    
    Trả về:
        Thời gian tham quan (phút)
    """
    duration = None
    
    if isinstance(point, dict):
        # Thử lowercase trước (từ to_dict), sau đó uppercase (từ DB)
        duration = point.get('duration')
        if duration is None:
            duration = point.get('Duration')
    else:
        # Thử lowercase trước (property), sau đó uppercase (attribute DB)
        duration = getattr(point, 'duration', None)
        if duration is None:
            duration = getattr(point, 'Duration', None)
    
    # Nếu vẫn chưa tìm thấy, thử trong original object
    if duration is None and isinstance(point, dict) and 'original' in point:
        orig = point['original']
        if isinstance(orig, dict):
            duration = orig.get('duration')
            if duration is None:
                duration = orig.get('Duration')
        else:
            duration = getattr(orig, 'duration', None)
            if duration is None:
                duration = getattr(orig, 'Duration', None)
    
    # Trả về duration nếu tìm thấy (kể cả khi = 0), ngược lại trả về default
    return int(duration) if duration is not None else default


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


def calculate_travel_time(distance_km: float, avg_speed_kmh: float = 30.0) -> float:
    """
    Tính thời gian di chuyển dựa trên khoảng cách và tốc độ trung bình.
    
    Tham số:
        distance_km: Khoảng cách (km)
        avg_speed_kmh: Tốc độ trung bình (km/h)
    
    Trả về:
        Thời gian di chuyển (phút)
    """
    if distance_km <= 0:
        return 0.0
    travel_hours = distance_km / avg_speed_kmh
    return travel_hours * 60


def calculate_estimated_duration(route: List[Dict], 
                                avg_speed_kmh: float = 30.0,
                                use_real_time: bool = False,
                                return_to_start: bool = False) -> Dict[str, Any]:
    """
    Tính thời gian ước tính cho tuyến đường.
    
    Hàm này tính thời gian dựa trên:
    - Thời gian di chuyển: từ OSRM (nếu use_real_time=True) hoặc khoảng cách + tốc độ
    - Thời gian tham quan: từ thuộc tính duration của mỗi điểm
    
    Tham số:
        route: Danh sách các điểm đã sắp xếp
        avg_speed_kmh: Tốc độ trung bình (km/h) - dùng khi không có dữ liệu thực
        use_real_time: Có sử dụng OSRM để lấy thời gian thực không
        return_to_start: Có tính đoạn quay về điểm xuất phát không
    
    Trả về:
        Dict chứa thông tin thời gian chi tiết
    """
    if not route or len(route) == 0:
        return {
            'travel_time_min': 0,
            'visit_time_min': 0,
            'total_time_min': 0,
            'travel_time_hours': 0,
            'total_time_hours': 0,
            'time_source': 'none'
        }
    
    # Tính thời gian tham quan từ thuộc tính duration của mỗi điểm
    total_visit_time = sum(get_point_duration(point) for point in route)
    
    travel_time_min = 0
    time_source = 'estimated'
    
    # Thử lấy thời gian thực từ OSRM
    if use_real_time and len(route) >= 2:
        segments = get_route_segments_duration_osrm(route, return_to_start)
        
        if segments:
            # Sử dụng thời gian thực từ OSRM
            travel_time_min = sum(seg['duration_min'] for seg in segments)
            time_source = 'osrm_real_time'
        else:
            # Fallback: tính từ khoảng cách Haversine
            distance = calculate_route_distance(route, return_to_start)
            travel_time_min = calculate_travel_time(distance, avg_speed_kmh)
            time_source = 'haversine_estimated'
    else:
        # Tính từ khoảng cách Haversine
        distance = calculate_route_distance(route, return_to_start)
        travel_time_min = calculate_travel_time(distance, avg_speed_kmh)
        time_source = 'haversine_estimated'
    
    # Tổng thời gian
    total_time = travel_time_min + total_visit_time
    
    return {
        'travel_time_min': round(travel_time_min, 1),
        'visit_time_min': total_visit_time,
        'total_time_min': round(total_time, 1),
        'travel_time_hours': round(travel_time_min / 60, 2),
        'total_time_hours': round(total_time / 60, 2),
        'time_source': time_source
    }


def _greedy_from_start_index(normalized_points: List[Dict], 
                             start_index: int,
                             return_to_start: bool = False) -> Tuple[List[Dict], float]:
    """
    Chạy thuật toán Greedy Nearest Neighbor từ một điểm xuất phát cụ thể.
    
    Hàm helper này được sử dụng trong Multi-Start Greedy.
    
    Tham số:
        normalized_points: Danh sách điểm đã chuẩn hóa
        start_index: Index của điểm xuất phát
        return_to_start: Có quay về điểm xuất phát không
    
    Trả về:
        Tuple (route, total_distance)
    """
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
    
    return route, total_distance


def _format_waypoint(point: Dict, index: int, is_start: bool, is_end: bool, 
                    detail: Optional[str] = None, arrival_min: float = 0.0) -> Dict:
    """
    Định dạng thông tin waypoint để trả về.
    
    Tham số:
        point: Điểm tham quan
        index: Thứ tự trong tuyến đường
        is_start: Có phải điểm xuất phát
        is_end: Có phải điểm cuối
        detail: Mô tả bổ sung
        arrival_min: Thời gian đến tại điểm này (phút, tính từ điểm xuất phát)
    
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
        'id': point['id'],
        'arrival_min': round(arrival_min, 1),
        'duration': get_point_duration(point)
    }


def greedy_nearest_neighbor(points: List[Dict], 
                           start_point_id: Optional[int] = None,
                           return_to_start: bool = False,
                           use_multi_start: bool = True,
                           use_real_time: bool = False,
                           avg_speed_kmh: float = 30.0) -> Dict[str, Any]:
    """
    Thuật toán Greedy TSP sử dụng phương pháp Nearest Neighbor với Multi-Start.
    
    Tham số:
        points: Danh sách các điểm tham quan (mỗi điểm cần có 'id', 'lat'/'vi_do', 'lng'/'kinh_do', 'duration')
        start_point_id: ID điểm xuất phát (nếu None và use_multi_start=True, thử tất cả điểm)
        return_to_start: Có quay về điểm xuất phát hay không
        use_multi_start: Có sử dụng Multi-Start không (chỉ áp dụng khi start_point_id=None)
        use_real_time: Có sử dụng OSRM để lấy thời gian thực không
        avg_speed_kmh: Tốc độ trung bình để tính thời gian di chuyển
    
    Trả về:
        Dict chứa:
            - route: Danh sách các điểm đã sắp xếp tối ưu
            - route_order: Danh sách ID theo thứ tự
            - total_distance: Tổng khoảng cách (km)
            - waypoints: Danh sách điểm với thông tin bổ sung (bao gồm arrival_min và duration)
            - return_to_start: Có quay về điểm đầu hay không
            - multi_start_used: Có sử dụng Multi-Start không
            - attempts: Số lần thử (nếu dùng Multi-Start)
    """
    if not points or len(points) == 0:
        return {
            'route': [],
            'route_order': [],
            'total_distance': 0.0,
            'waypoints': [],
            'return_to_start': False,
            'multi_start_used': False
        }
    
    if len(points) == 1:
        point = points[0]
        return {
            'route': [point],
            'route_order': [point.get('id')],
            'total_distance': 0.0,
            'waypoints': [_format_waypoint(point, 0, True, True, arrival_min=0.0)],
            'return_to_start': False,
            'multi_start_used': False
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
            'waypoints': [],
            'return_to_start': False,
            'multi_start_used': False
        }
    
    # Xác định điểm xuất phát và chiến lược
    best_route = None
    best_distance = float('inf')
    attempts = 0
    multi_start_used = False
    
    if start_point_id is not None:
        # Điểm xuất phát đã được chỉ định - không dùng Multi-Start
        start_index = next((i for i, p in enumerate(normalized_points) if p['id'] == start_point_id), 0)
        best_route, best_distance = _greedy_from_start_index(normalized_points, start_index, return_to_start)
        attempts = 1
    elif use_multi_start and len(normalized_points) >= 3:
        # Multi-Start: thử tất cả các điểm xuất phát
        multi_start_used = True
        for start_idx in range(len(normalized_points)):
            route, distance = _greedy_from_start_index(normalized_points, start_idx, return_to_start)
            attempts += 1
            
            if distance < best_distance:
                best_distance = distance
                best_route = route
    else:
        # Không dùng Multi-Start, chỉ dùng điểm đầu tiên
        best_route, best_distance = _greedy_from_start_index(normalized_points, 0, return_to_start)
        attempts = 1
    
    # Tạo danh sách waypoints với thông tin chi tiết bao gồm arrival_min
    waypoints = []
    cumulative_time = 0.0  # Thời gian tích lũy (phút)
    
    # Nếu sử dụng thời gian thực, lấy thông tin segments từ OSRM
    segments = None
    if use_real_time and len(best_route) >= 2:
        segments = get_route_segments_duration_osrm(best_route, return_to_start)
    
    for idx, point in enumerate(best_route):
        is_start = (idx == 0)
        is_end = (idx == len(best_route) - 1) and not return_to_start
        
        # Tính thời gian đến tại điểm này
        if idx > 0:
            prev_point = best_route[idx - 1]
            
            # Thử sử dụng thời gian thực từ segments
            if segments and idx - 1 < len(segments):
                travel_time = segments[idx - 1]['duration_min']
            else:
                # Fallback: tính từ khoảng cách Haversine
                distance = haversine_distance(
                    prev_point['lat'], prev_point['lng'],
                    point['lat'], point['lng']
                )
                travel_time = calculate_travel_time(distance, avg_speed_kmh)
            
            cumulative_time += travel_time
            # Thêm thời gian tham quan tại điểm trước
            cumulative_time += get_point_duration(prev_point)
        
        waypoints.append(_format_waypoint(point, idx, is_start, is_end, arrival_min=cumulative_time))
    
    if return_to_start and len(best_route) > 1:
        # Tính thời gian quay về điểm xuất phát
        last_point = best_route[-1]
        first_point = best_route[0]
        
        # Thử sử dụng thời gian thực
        if segments and len(segments) == len(best_route):
            travel_time = segments[-1]['duration_min']
        else:
            distance = haversine_distance(
                last_point['lat'], last_point['lng'],
                first_point['lat'], first_point['lng']
            )
            travel_time = calculate_travel_time(distance, avg_speed_kmh)
        
        cumulative_time += travel_time
        cumulative_time += get_point_duration(last_point)  # Thời gian tham quan tại điểm cuối
        
        waypoints.append(_format_waypoint(first_point, len(best_route), False, True, 
                                         "Quay về điểm xuất phát", cumulative_time))
    
    return {
        'route': best_route,
        'route_order': [p['id'] for p in best_route],
        'total_distance': round(best_distance, 2),
        'waypoints': waypoints,
        'return_to_start': return_to_start,
        'multi_start_used': multi_start_used,
        'attempts': attempts
    }


def optimize_route_with_osrm(points: List[Dict],
                             start_point_id: Optional[int] = None,
                             return_to_start: bool = False,
                             osrm_base: str = 'http://router.project-osrm.org',
                             use_real_time: bool = True,
                             avg_speed_kmh: float = 30.0) -> Dict[str, Any]:
    """
    Tối ưu tuyến đường sử dụng OSRM Trip service (kết hợp Greedy fallback).
    
    Tham số:
        points: Danh sách các điểm tham quan
        start_point_id: ID điểm xuất phát
        return_to_start: Có quay về điểm xuất phát không
        osrm_base: URL cơ sở của OSRM server
        use_real_time: Có sử dụng thời gian thực từ OSRM không
        avg_speed_kmh: Tốc độ trung bình để tính thời gian
    
    Trả về:
        Dict chứa thông tin tuyến đường tối ưu hoặc fallback về Greedy
    """
    if not points or len(points) < 2:
        return greedy_nearest_neighbor(points, start_point_id, return_to_start, 
                                       use_real_time=use_real_time,
                                       avg_speed_kmh=avg_speed_kmh)
    
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
            return greedy_nearest_neighbor(points, start_point_id, return_to_start,
                                          use_real_time=use_real_time,
                                          avg_speed_kmh=avg_speed_kmh)
        
        # Xây dựng chuỗi tọa độ cho OSRM (lon,lat)
        coords = ";".join([f"{p['lng']},{p['lat']}" for p in normalized_points])
        
        # Xác định điểm xuất phát
        source_param = ""
        if start_point_id:
            start_idx = next((i for i, p in enumerate(normalized_points) if p['id'] == start_point_id), None)
            if start_idx is not None:
                source_param = f"&source={start_idx}"
        
        # Sử dụng roundtrip parameter
        roundtrip_param = "true" if return_to_start else "false"
        url = f"{osrm_base}/trip/v1/driving/{coords}?roundtrip={roundtrip_param}{source_param}&annotations=distance,duration"
        
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
            
            # Tạo waypoints với arrival_min sử dụng thời gian thực
            waypoints_list = []
            cumulative_time = 0.0
            
            # Lấy thông tin chi tiết về các segments
            segments = None
            if use_real_time:
                segments = get_route_segments_duration_osrm(optimized_route, return_to_start)
            
            for idx, point in enumerate(optimized_route):
                is_start = (idx == 0)
                is_end = (idx == len(optimized_route) - 1) and not return_to_start
                
                # Tính thời gian đến
                if idx > 0:
                    prev_point = optimized_route[idx - 1]
                    
                    # Thử sử dụng thời gian thực từ segments
                    if segments and idx - 1 < len(segments):
                        travel_time = segments[idx - 1]['duration_min']
                    else:
                        distance = haversine_distance(
                            prev_point['lat'], prev_point['lng'],
                            point['lat'], point['lng']
                        )
                        travel_time = calculate_travel_time(distance, avg_speed_kmh)
                    
                    cumulative_time += travel_time
                    cumulative_time += get_point_duration(prev_point)
                
                waypoints_list.append(_format_waypoint(point, idx, is_start, is_end, 
                                                      arrival_min=cumulative_time))
            
            if return_to_start and len(optimized_route) > 1:
                last_point = optimized_route[-1]
                first_point = optimized_route[0]
                
                # Thử sử dụng thời gian thực
                if segments and len(segments) == len(optimized_route):
                    travel_time = segments[-1]['duration_min']
                else:
                    distance = haversine_distance(
                        last_point['lat'], last_point['lng'],
                        first_point['lat'], first_point['lng']
                    )
                    travel_time = calculate_travel_time(distance, avg_speed_kmh)
                
                cumulative_time += travel_time
                cumulative_time += get_point_duration(last_point)
                
                waypoints_list.append(_format_waypoint(first_point, len(optimized_route), 
                                                      False, True, "Quay về điểm xuất phát", 
                                                      cumulative_time))
            
            return {
                'route': optimized_route,
                'route_order': [p['id'] for p in optimized_route],
                'total_distance': round(total_distance, 2),
                'total_duration': round(total_duration, 1),
                'waypoints': waypoints_list,
                'method': 'osrm',
                'return_to_start': return_to_start,
                'multi_start_used': False,
                'attempts': 1
            }
        
    except Exception as e:
        # Nếu OSRM thất bại, fallback về Greedy
        pass
    
    # Fallback về thuật toán Greedy (với Multi-Start)
    result = greedy_nearest_neighbor(points, start_point_id, return_to_start,
                                     use_real_time=use_real_time,
                                     avg_speed_kmh=avg_speed_kmh)
    result['method'] = 'greedy'
    return result


def gts_optimize(points: List[Dict], 
                start_point_id: Optional[int] = None,
                return_to_start: bool = False,
                use_osrm: bool = True,
                use_multi_start: bool = True,
                use_real_time: bool = True,
                avg_speed_kmh: float = 30.0) -> Dict[str, Any]:
    """
    Hàm chính để tối ưu tuyến đường du lịch bằng thuật toán GTS.
    
    Đây là hàm tiện ích chính được sử dụng trong các route/API endpoints.
    
    Tham số:
        points: Danh sách các điểm tham quan (mỗi điểm có 'duration' cho thời gian tham quan)
        start_point_id: ID điểm xuất phát (optional)
        return_to_start: Có quay về điểm xuất phát không
        use_osrm: Có sử dụng OSRM API không (nếu không thì dùng Greedy thuần)
        use_multi_start: Có sử dụng Multi-Start Greedy không (chỉ khi start_point_id=None)
        use_real_time: Có sử dụng thời gian thực từ OSRM không
        avg_speed_kmh: Tốc độ trung bình để ước tính thời gian
    
    Trả về:
        Dict chứa đầy đủ thông tin tuyến đường tối ưu:
            - route: Danh sách điểm đã sắp xếp
            - route_order: Danh sách ID theo thứ tự
            - total_distance: Tổng khoảng cách (km)
            - waypoints: Thông tin các điểm dừng (bao gồm duration của mỗi điểm)
            - duration_info: Thông tin thời gian chi tiết
            - method: Phương pháp được sử dụng ('osrm' hoặc 'greedy')
            - multi_start_used: Có sử dụng Multi-Start không
    """
    if not points:
        return {
            'route': [],
            'route_order': [],
            'total_distance': 0.0,
            'waypoints': [],
            'duration_info': calculate_estimated_duration([], use_real_time=use_real_time, return_to_start=return_to_start),
            'method': 'none',
            'error': 'Không có điểm tham quan nào'
        }
    
    # Tối ưu tuyến đường
    # Nếu bật Multi-Start và không có điểm xuất phát cố định, ưu tiên Multi-Start Greedy
    if use_multi_start and start_point_id is None and len(points) >= 3:
        # Sử dụng Multi-Start Greedy để tìm tuyến đường tốt nhất
        result = greedy_nearest_neighbor(
            points, start_point_id, return_to_start, 
            use_multi_start=True,
            use_real_time=use_real_time,
            avg_speed_kmh=avg_speed_kmh
        )
        
        # Nếu cũng bật OSRM, thử OSRM và so sánh kết quả
        if use_osrm and len(points) >= 2:
            try:
                osrm_result = optimize_route_with_osrm(
                    points, start_point_id, return_to_start,
                    use_real_time=use_real_time,
                    avg_speed_kmh=avg_speed_kmh
                )
                # So sánh khoảng cách, chọn kết quả tốt hơn
                if osrm_result.get('total_distance', float('inf')) < result['total_distance']:
                    result = osrm_result
            except Exception:
                # Nếu OSRM thất bại, giữ kết quả Greedy Multi-Start
                pass
    elif use_osrm and len(points) >= 2:
        # Ưu tiên OSRM nếu không dùng Multi-Start hoặc có điểm xuất phát cố định
        result = optimize_route_with_osrm(
            points, start_point_id, return_to_start,
            use_real_time=use_real_time,
            avg_speed_kmh=avg_speed_kmh
        )
    else:
        # Sử dụng Greedy thuần (có thể có hoặc không có Multi-Start)
        result = greedy_nearest_neighbor(
            points, start_point_id, return_to_start, use_multi_start,
            use_real_time=use_real_time,
            avg_speed_kmh=avg_speed_kmh
        )
    
    # Tính thời gian ước tính dựa trên duration thực tế của từng điểm
    duration_info = calculate_estimated_duration(
        result['route'],
        avg_speed_kmh,
        use_real_time=use_real_time,
        return_to_start=return_to_start
    )
    result['duration_info'] = duration_info
    
    return result
