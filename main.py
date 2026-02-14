import math

def calculate_distance(lat1, lon1, lat2, lon2):
    """The 'Spazz' Proximity Engine: Calculates distance in km."""
    R = 6371 # Earth radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def spazz_intensity(distance_km):
    """Calculates how fast the jewelry/phone should flash (0-100%)."""
    max_range = 0.5 # 500 meters
    if distance_km > max_range: return 0
    return round((1 - (distance_km / max_range)) * 100)

# Example Demo Match
dist = calculate_distance(40.7128, -74.0060, 40.7130, -74.0062)
print(f"Match found! Spazz Intensity: {spazz_intensity(dist)}%")
