# src/traffic_api.py

from functools import lru_cache
import math

# ----------------------------
# 🧠 SMART ROAD DENSITY (NO API)
# ----------------------------
@lru_cache(maxsize=200)
def get_road_density(lat, lon):
    try:
        # base variation
        value = abs(lat * lon) % 10

        # smooth realistic pattern
        density = 2 + (value * 0.8)

        # geo variation
        density += math.sin(lat) * 0.5 + math.cos(lon) * 0.5

        # clamp
        density = max(1.5, min(density, 10))

        return round(density, 2)

    except Exception as e:
        print("Density Error:", e)
        return 3


# ----------------------------
# 📍 AREA GRID (3x3)
# ----------------------------
def generate_area_grid(lat, lon):
    areas = []

    for i in range(-1, 2):
        for j in range(-1, 2):
            areas.append({
                "lat": lat + i * 0.03,
                "lon": lon + j * 0.03,
                "name": f"Zone {i+2}-{j+2}"
            })

    return areas


# ----------------------------
# 🚦 APPLY DENSITY
# ----------------------------
def apply_density(base_pred, density):
    pred = base_pred * (1 + density / 5)
    return int(max(500, min(pred, 5000)))


# ----------------------------
# 🌆 CITY FACTOR
# ----------------------------
def get_city_factor(city):
    city_factor = {
        "mumbai": 2.2,
        "delhi": 2.0,
        "bangalore": 1.9,
        "pune": 1.5,
        "hyderabad": 1.7,
        "chennai": 1.8,
        "default": 1.0
    }

    return city_factor.get(city.lower(), 1.0)