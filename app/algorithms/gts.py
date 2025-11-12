from math import radians, sin, cos, sqrt, atan2

def haversine(p1, p2):
    R = 6371
    lat1, lon1 = radians(p1[0]), radians(p1[1])
    lat2, lon2 = radians(p2[0]), radians(p2[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return 2 * R * atan2(sqrt(a), sqrt(1 - a))

def greedy_tsp(points, start_index=0):
    n = len(points)
    visited = [False] * n
    path = [start_index]
    visited[start_index] = True
    total_distance = 0

    for _ in range(n - 1):
        last = path[-1]
        nearest = None
        nearest_dist = float("inf")
        for j in range(n):
            if not visited[j]:
                dist = haversine(points[last], points[j])
                if dist < nearest_dist:
                    nearest = j
                    nearest_dist = dist
        path.append(nearest)
        visited[nearest] = True
        total_distance += nearest_dist

    return path, total_distance
