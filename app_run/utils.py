from geopy.distance import geodesic


def check_weight(weight):
    if weight.isdigit():
        if 0 < int(weight) < 900:
            return True
        else:
            return False

    return False


def calculate_distance(coords):
    total_distance_km = 0

    if len(coords) > 1:
        for i in range(len(coords) - 1):
            coord_1 = coords[i]
            coord_2 = coords[i + 1]
            total_distance_km += geodesic(coord_1, coord_2).km

    return total_distance_km
