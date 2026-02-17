import math # Fixed the 'Import' typo

def calculate_distance(lat1, lon1, lat2, lon2):
    """The 'Spazz' Proximity Engine: Calculates distance in km."""
    R = 6371 # Earth radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def spazz_intensity(distance_km):
    """
    Calculates how fast the phone should flash (0-100%).
    - Under 5 meters: Returns 101 (Solid Mode)
    - 5m to 500m: Exponentially increases intensity
    """
    max_range = 0.5 # 500 meters
    
    if distance_km > max_range: 
        return 0
    
    # Face-to-Face Trigger (Within 5 meters)
    if distance_km <= 0.005:
        return 101 
    
    # Exponential Intensity: Closer = much faster 'spazz'
    intensity = ((1 - (distance_km / max_range)) ** 2) * 100
    return round(intensity)

# --- Example Demo Walk ---
# Simulating being 10 meters away
dist = calculate_distance(40.7128, -74.0060, 40.71285, -74.00605)
intensity = spazz_intensity(dist)

if intensity == 101:
    print("🚨 SOLID LIGHTS & VIBRATION: FACE TO FACE MODE 🚨")
else:
    print(f"Match nearby! Spazz Intensity: {intensity}%")


# --- Spazz AI Feedback & Ego Shield ---

def ego_shield_coach(raw_feedback):
    """
    Translates raw (potentially harsh) feedback into 
    encouraging AI coaching tips.
    """
    coaching_tips = {
        "weight": "GOAL: Let's hit a 1-mile walk today! Staying active keeps your Spazz energy high. 🔥",
        "hair": "STYLE TIP: A fresh trim or a quick groom today will boost your match rate by 40%!",
        "breath": "PRO-TIP: Keep some mints handy; first impressions in the Spazz Zone are everything. 🍬",
        "hygiene": "AI TIP: Looking sharp is 50% of the Rizz. Fresh fit, fresh hair, fresh starts!"
    }
    
    # AI selects encouragement; defaults to a general tip if tag isn't found
    return [coaching_tips.get(tag, "Keep leveling up! You got this.") for tag in raw_feedback]

# Test the AI Shield
private_tags = ["weight", "hygiene"]
print(ego_shield_coach(private_tags))
