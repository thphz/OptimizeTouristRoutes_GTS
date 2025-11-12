import folium

def generate_map(points, route_order):
    start_point = points[route_order[0]]
    m = folium.Map(location=start_point, zoom_start=12)

    for i, idx in enumerate(route_order):
        folium.Marker(
            location=points[idx],
            popup=f"<b>Điểm {i+1}</b>",
            tooltip=f"Điểm {i+1}"
        ).add_to(m)

    route_coords = [points[i] for i in route_order]
    folium.PolyLine(route_coords, color="blue", weight=3).add_to(m)

    return m._repr_html_()
