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



# --- Spazz AI Feedback System ---

def process_feedback(survey_results):
    """Analyzes private user feedback to generate AI tips."""
    # Example: feedback is a list of scores from 1-10
    average_score = sum(survey_results) / len(survey_results)
    
    if average_score < 6:
        return "AI TIP: Your energy might be coming off too strong. Try slowing down the 'Rizz' and listening more!"
    else:
        return "AI TIP: Great match! Your confidence is your strength. Keep it up!"

# Example usage for your trial run
mock_feedback = [4, 5, 7] # Private scores from a date
print(process_feedback(mock_feedback))



# --- SPAZZ HOTSPOT LOGIC ---

def check_hotspot(user_lat, user_lon):
    """Checks if the user is inside a high-energy 'Spazz Zone'."""
    # Example: The 'Bar on Main St' coordinates
    hotspot_lat, hotspot_lon = 40.7128, -74.0060 
    
    distance = calculate_distance(user_lat, user_lon, hotspot_lat, hotspot_lon)
    
    if distance < 0.1: # Within 100 meters
        return "🔥 YOU ARE IN A SPAZZ ZONE! Energy is 10x. Go find a match!"
    return "Scanning for nearby Hotspots..."


def generate_ai_coaching(private_tags):
    """
    Turns private feedback into encouraging lifestyle goals.
    """
    tips = []
    
    if "hygiene" in private_tags:
        tips.append("AI TIP: Looking sharp is 50% of the Rizz. Fresh fit, fresh hair, fresh starts!")
        
    if "fitness" in private_tags:
        tips.append("GOAL ALERT: It's beautiful out! Let's hit a 1-mile walk today to stay Spazz-ready.")
        
    return tips

# Example: If a user got private tags about weight or hair
user_needs_improvement = ["fitness", "hygiene"]
print(generate_ai_coaching(user_needs_improvement))
