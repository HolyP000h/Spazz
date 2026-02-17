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


def check_spazz_conditions(user_a, user_b, dist):
    # Condition 1: Are they within range?
    # Condition 2: Are they BOTH on the clock?
    # Condition 3: Have they BOTH swiped 'Yes' on each other?
    
    if dist < 0.5 and user_a.on_clock and user_b.on_clock:
        if user_a.has_liked(user_b) and user_b.has_liked(user_a):
            return spazz_intensity(dist)
    return 0


def process_vicinity_check(user_a, user_b, dist):
    # Both are on the clock? Full Spazz Mode.
    if user_a.on_clock and user_b.on_clock:
        return spazz_intensity(dist)
    
    # User B is off the clock but User A is near? Send the nudge.
    if not user_b.on_clock and dist < 0.1: # 100 meters
        send_nudge_notification(user_b.id, "Psst... someone is in your vicinity! Clock in?")
        
    return 0


def should_we_spazz(user_a, user_b, distance_km):
    """
    Final Gatekeeper: Only spazzes if BOTH users are 'On the Clock'.
    """
    if not user_a.is_on_clock or not user_b.is_on_clock:
        return "Silent Mode: One or both users are off the clock."
    
    # If both are on, get that intensity!
    return spazz_intensity(distance_km)


    # In a real app, you'd send this to Google/Apple:
    # requests.post(push_service_url, json=payload, headers=headers)
    print(f"NOTIFICATION SENT TO {user_id}: {message} (Intensity: {intensity})")

async def check_user_vibe(user_a, user_b):
    dist = calculate_distance(user_a.lat, user_a.lon, user_b.lat, user_b.lon)

    # SCENARIO A: Both On the Clock & Mutual Likes
    if user_a.on_clock and user_b.on_clock and user_a.likes(user_b):
        intensity = spazz_intensity(dist)
        if intensity > 0:
            send_push_notification(user_a.id, "HE IS NEAR! Look for the lights!", intensity)
            send_push_notification(user_b.id, "SHE IS NEAR! Look for the lights!", intensity)

    # SCENARIO B: One is Off the Clock (The Nudge)
    elif not user_b.on_clock and dist < 0.1: # Within 100 meters
        # We check a 'cooldown' so we don't spam them
        if user_b.can_be_nudged(): 
            send_push_notification(user_b.id, "Psst... someone's in your vicinity! Clock in to find them?")
            user_b.update_nudge_cooldown()

class User:
    def __init__(self, username, is_premium=False):
        self.username = username
        self.is_premium = is_premium
        self.rizz_tokens = 0

# Example logic:
if not user.is_premium and distance_km < 0.1:
    print("Upgrade to Spazz Pro to see exactly who is nearby!")
