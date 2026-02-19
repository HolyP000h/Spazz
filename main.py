import math
import time
import random
import asyncio

# --- 1. THE CORE ENGINE ---
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371 # Earth radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def spazz_intensity(distance_km):
    max_range = 0.5 # 500 meters
    if distance_km > max_range: return 0
    if distance_km <= 0.005: return 101 # Face-to-Face
    return round(((1 - (distance_km / max_range)) ** 2) * 100)

# --- 2. AI COACHING (EGO SHIELD) ---
def ego_shield_coach(raw_feedback_tags):
    coaching_tips = {
        "weight": "GOAL: Let's hit a 1-mile walk today! Staying active keeps your Spazz energy high. 🔥",
        "hair": "STYLE TIP: A fresh trim or a quick groom today will boost your match rate by 40%!",
        "breath": "PRO-TIP: Keep some mints handy; first impressions in the Spazz Zone are everything. 🍬",
        "hygiene": "AI TIP: Looking sharp is 50% of the Rizz. Fresh fit, fresh hair, fresh starts!"
    }
    return [coaching_tips.get(tag, "Keep leveling up! You got this.") for tag in raw_feedback_tags]

# --- 3. THE USER SYSTEM ---
class User:
    def __init__(self, user_id, username, is_premium=False):
        self.id = user_id
        self.username = username
        self.is_premium = is_premium
        self.on_clock = False
        self.nudges_balance = 5
        self.lat = 0.0
        self.lon = 0.0
        self.last_nudge_time = 0

    def can_be_nudged(self):
        return (time.time() - self.last_nudge_time) > 300

    def update_nudge_cooldown(self):
        self.last_nudge_time = time.time()

# --- 4. THE COMMUNICATION LAYER ---
def send_notification(user_id, message, intensity=0):
    print(f"--- 📱 NOTIFICATION TO {user_id} ---")
    print(f"Message: {message}")
    if intensity > 0:
        print(f"Haptic Intensity: {intensity}%")
    print("-" * 30)
    return True

def trigger_nudge_with_shield(target_user):
    concerns = ["weight", "hair", "breath", "hygiene"]
    detected_concern = [random.choice(concerns)]
    shielded_tips = ego_shield_coach(detected_concern)
    full_message = f"Someone is nearby! {shielded_tips[0]} Clock in?"
    send_notification(target_user.id, full_message)

# --- 5. THE LOGIC GATEKEEPER ---
async def check_user_vibe(user_a, user_b):
    dist = calculate_distance(user_a.lat, user_a.lon, user_b.lat, user_b.lon)

    # SCENARIO A: Both On the Clock
    if user_a.on_clock and user_b.on_clock:
        intensity = spazz_intensity(dist)
        if intensity > 0:
            send_notification(user_a.id, "MATCH NEARBY! Find the lights!", intensity)
            send_notification(user_b.id, "MATCH NEARBY! Find the lights!", intensity)
    
    # SCENARIO B: The Smart Nudge (Ego Shield)
    elif not user_b.on_clock and dist < 0.1:
        if user_b.can_be_nudged():
            trigger_nudge_with_shield(user_b)
            user_b.update_nudge_cooldown()

# --- 6. EXECUTION ---
me = User(1, "SpazzMaster_99", is_premium=False)
them = User(2, "RizzQueen", is_premium=True)

me.lat, me.lon = 40.7128, -74.0060
them.lat, them.lon = 40.71285, -74.00605 

if not me.is_premium:
    print("PRO TIP: Upgrade to Spazz Pro to see Hotspots!")

asyncio.run(check_user_vibe(me, them))
