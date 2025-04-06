import math

def haversine(lat1, lon1, lat2, lon2):
    """
    Вычисляет расстояние между двумя точками в метрах
    """
    R = 6371000  # радиус Земли
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c  # расстояние в метрах

def is_near_point(lat1, lon1, lat2, lon2, threshold=20):
    return haversine(lat1, lon1, lat2, lon2) <= threshold
