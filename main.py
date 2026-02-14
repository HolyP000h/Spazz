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



def find_closest_match(user_location, all_nearby_users):
    """Sorts everyone in the Spazz Zone by distance."""
    # Logic to find the absolute closest connection
    sorted_matches = sorted(all_nearby_users, key=lambda x: calculate_distance(
        user_location['lat'], user_location['lon'], x['lat'], x['lon']
    ))
    return sorted_matches[0] # Returns the person right next to you!
    


​{
"action": "image_generation",
"action_input": "A high-energy, neon app icon for 'Spazz'. The design features a stylized heart made of electric lightning bolts pulsing with vibrant pink and cyan light. The aesthetic is futuristic and disruptive, set against a deep matte black background to make the glow pop. It looks like a premium tech brand, 3D rendered with a slight glass-morphism effect."
}
