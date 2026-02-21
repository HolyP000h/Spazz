import math
import time
import json
import random
import asyncio
from fastapi import FastAPI

app = FastAPI()

async def startup_event():
    print("🧪 [DIAGNOSTIC]: Checking for users...")
    active_users = load_from_db()
    if not active_users:
        u1 = User(1, "SpazzMaster_99", 25, "M", "F", lat=34.0522, lon=-118.2437, credits=1000)
        u2 = User(2, "RizzQueen", 22, "F", "M", lat=34.0525, lon=-118.2440, credits=500)
        save_to_db([u1, u2])
        print("✨ [DIAGNOSTIC]: No users found. Generated SpazzMaster and RizzQueen.")
    else:
        print(f"✅ [DIAGNOSTIC]: {len(active_users)} users loaded and ready.")

# --- THE SPAZZ SHOP CATALOG ---
SPAZZ_CATALOG = {
    "basic_white": {"name": "Standard Strobe", "type": "Skin", "color": "#FFFFFF", "price": 0},
    "boss_gold": {"name": "The Final Boss", "type": "Legendary", "color": "#FFD700", "price": 500},
    "neon_heart": {"name": "Lover Pulse", "type": "Skin", "color": "#FF1493", "price": 200},
    "police_chase": {"name": "The Heat", "type": "Strobe", "color": "Blue/Red", "price": 300}
}

# --- THE USER BLUEPRINT ---
class User:
    def __init__(self, id, username, age, gender, interested_in, 
                 min_age=18, max_age=99, is_premium=False, 
                 on_clock=False, nudges_balance=5, lat=0.0, lon=0.0, 
                 last_nudge_time=0, blocked_users=None, 
                 credits=0, inventory=None, active_skin="basic_white", 
                 last_reward_time=0, **kwargs):
        
        self.id = int(id)
        self.username = username
        self.age = int(age)
        self.gender = gender
        self.interested_in = interested_in
        self.min_age = int(min_age)
        self.max_age = int(max_age)
        self.is_premium = is_premium
        self.on_clock = on_clock
        self.nudges_balance = nudges_balance
        self.lat = lat
        self.lon = lon
        self.last_nudge_time = last_nudge_time
        self.blocked_users = blocked_users if blocked_users else []
        self.credits = credits  
        self.active_skin = active_skin 
        self.inventory = inventory if inventory else ["basic_white"]
        self.last_reward_time = last_reward_time

    def to_dict(self):
        return vars(self)

# --- DATABASE TOOLS ---
def save_to_db(users_list):
    data = {"users": [u.to_dict() for u in users_list]}
    with open('users_db.json', 'w') as f:
        json.dump(data, f, indent=4)
    print("💾 [DATABASE]: Sync complete.")

def load_from_db():
    try:
        with open('users_db.json', 'r') as f:
            data = json.load(f)
            return [User(**u) for u in data["users"]]
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# --- MATH TOOLS ---
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 3958.8 # Miles
    dlat, dlon = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a)))

def get_bearing(lat1, lon1, lat2, lon2):
    dlon = math.radians(lon2 - lon1)
    y = math.sin(dlon) * math.cos(math.radians(lat2))
    x = math.cos(math.radians(lat1)) * math.sin(math.radians(lat2)) - \
        math.sin(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.cos(dlon)
    bearing = (math.degrees(math.atan2(y, x)) + 360) % 360
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    return directions[int((bearing + 22.5) // 45) % 8]

# --- WEB ENDPOINTS ---

@app.get("/")
def home():return {"status": "Spazz Engine Online", "docs": "/docs"}

@app.get("/users")
def get_users():
    return [u.to_dict() for u in load_from_db()]

@app.post("/nudge/{sender_id}/{receiver_id}")
def nudge_user(sender_id: int, receiver_id: int):
    users = load_from_db()
    sender = next((u for u in users if u.id == sender_id), None)
    receiver = next((u for u in users if u.id == receiver_id), None)
    if not sender or not receiver: return {"error": "User missing"}
    
    if sender_id in receiver.blocked_users: return {"error": "Blocked."}
    if not (sender.min_age <= receiver.age <= sender.max_age): return {"error": "Age mismatch."}
    if not (receiver.min_age <= sender.age <= receiver.max_age): return {"error": "They don't want you."}
    
    if sender.nudges_balance <= 0 and not sender.is_premium:
        return {"error": "No nudges left!"}

    sender.nudges_balance -= 1
    save_to_db(users)
    return {"message": "Nudge delivered!"}

@app.get("/pulse/{user_id}/{target_id}")
def get_pulse(user_id: int, target_id: int):
    users = load_from_db()
    me = next((u for u in users if u.id == user_id), None)
    them = next((u for u in users if u.id == target_id), None)
    
    dist = calculate_distance(me.lat, me.lon, them.lat, them.lon)
    
    # PULSE LOGIC: Distance in Miles
    if dist < 0.002: # ~10 feet
        status = {"mode": "STROBE", "vibe": "SOLID", "speed": 0}
    elif dist < 0.05: # Close
        status = {"mode": "PULSE", "vibe": "FAST", "speed": 0.5}
    elif dist < 0.2: # Getting warmer
        status = {"mode": "PULSE", "vibe": "MEDIUM", "speed": 2.0}
    else: # Cold
        status = {"mode": "PULSE", "vibe": "SLOW", "speed": 5.0}
        
    skin = SPAZZ_CATALOG.get(them.active_skin, SPAZZ_CATALOG["basic_white"])
    return {"distance": round(dist, 4), "pulse": status, "target_skin": skin}

@app.post("/buy_item/{user_id}/{item_id}")
def buy_item(user_id: int, item_id: str):
    users = load_from_db()
    user = next((u for u in users if u.id == user_id), None)
    if not user or item_id not in SPAZZ_CATALOG: return {"error": "Invalid item"}
    
    price = SPAZZ_CATALOG[item_id]["price"]
    if user.credits >= price and item_id not in user.inventory:
        user.credits -= price
        user.inventory.append(item_id)
        user.active_skin = item_id
        save_to_db(users)
        return {"message": f"Equipped {SPAZZ_CATALOG[item_id]['name']}!"}
    return {"error": "Purchase failed"}

@app.post("/spawn/{username}")
def spawn_ghost(username: str):
    users = load_from_db()
    
    # Create a unique ID by finding the max ID and adding 1
    new_id = max([u.id for u in users], default=0) + 1
    
    # Spawn near a base coordinate (or your current lat/lon)
    # Adding a small random offset so they don't all stack on top of each other
    new_ghost = User(
        id=new_id,
        username=username,
        age=random.randint(18, 99),
        gender="Ghost",
        interested_in="All",
        lat=34.0522 + random.uniform(-0.01, 0.01),
        lon=-118.2437 + random.uniform(-0.01, 0.01),
        credits=0
    )
    
    users.append(new_ghost)
    save_to_db(users)
    return {"message": f"Entity {username} materialized at {new_ghost.lat}, {new_ghost.lon}"}

@app.post("/daily_reward/{user_id}")
def claim_daily_reward(user_id: int):
    users = load_from_db()
    user = next((u for u in users if u.id == user_id), None)
    now = time.time()
    if now - user.last_reward_time < 86400:
        return {"error": "Too soon!"}
    user.credits += 50
    user.last_reward_time = now
    save_to_db(users)
    return {"message": "Credits added!"}

@app.post("/move/{user_id}/{direction}")
def move_user(user_id: int, direction: str):
    users = load_from_db()
    user = next((u for u in users if u.id == user_id), None)
    
    if not user:
        return {"error": "User not found"}

    # A "step" is about 100 feet in GPS coordinates
    step = 0.0003 

    if direction.lower() == "north":
        user.lat += step
    elif direction.lower() == "south":
        user.lat -= step
    elif direction.lower() == "east":
        user.lon += step
    elif direction.lower() == "west":
        user.lon -= step
    else:
        return {"error": "Invalid direction. Use North, South, East, or West."}

    save_to_db(users)
    return {
        "message": f"{user.username} moved {direction}",
        "new_coords": {"lat": user.lat, "lon": user.lon}
    }

@app.post("/teleport/{user_id}")
def teleport_user(user_id: int, lat: float, lon: float):
    users = load_from_db()
    user = next((u for u in users if u.id == user_id), None)
    
    if user:
        user.lat = lat
        user.lon = lon
        save_to_db(users)
        return {"message": f"{user.username} warped to new coordinates!"}
    return {"error": "User not found"}



@app.get("/radar/{user_id}")
async def get_radar(user_id: int):
    users = load_from_db()
    me = next((u for u in users if u.id == user_id), None)
    
    if not me:
        return {"error": "User not found"}

    radar_results = []
    for user in users:
        if user.id == me.id:
            continue

    # ... existing distance calculation ...
        bearing_label = get_bearing(me.lat, me.lon, user.lat, user.lon)
        radar_results.append({
            "username": user.username,
            "distance_miles": round(distance, 2),
            "direction": bearing_label, # <--- New field!
            "status": "Target Locked" if distance < 5 else "Searching..."
        })    
            
        # Haversine Distance Calculation (Miles)
        R = 3958.8 # Radius of Earth in miles
        dlat = math.radians(user.lat - me.lat)
        dlon = math.radians(user.lon - me.lon)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(me.lat)) * math.cos(math.radians(user.lat)) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        
        radar_results.append({
            "username": user.username,
            "distance_miles": round(distance, 2),
            "status": "Target Locked" if distance < 5 else "Searching..."
        })
        
    return {"my_location": f"{me.lat}, {me.lon}", "nearby_spazzers": radar_results}

async def startup_event():
    # ... your existing user creation code ...
    
    # Start the Ghost Protocol in the background
    asyncio.create_task(ghost_heartbeat())

async def ghost_heartbeat():
    while True:
        move_ghosts()
        print("👻 [GHOST]: RizzQueen has shifted positions...")
        await asyncio.sleep(10) # Wait 10 seconds between moves

# --- GHOST PROTOCOL (The AI Brain) ---

def move_ghosts():
    users = load_from_db()
    moved = False
    for user in users:
        # ID 1 is usually YOU. Everyone else (Ghosts) should wander.
        if user.id != 1:
            user.lat += random.uniform(-0.0005, 0.0005)
            user.lon += random.uniform(-0.0005, 0.0005)
            moved = True
    if moved:
        save_to_db(users)

async def ghost_heartbeat():
    """The background loop that triggers every 10 seconds."""
    while True:
        try:
            move_ghosts()
        except Exception as e:
            print(f"❌ [GHOST ERROR]: {e}")
        await asyncio.sleep(10)        

if __name__ == "__main__":
    # This now only triggers if you run 'python main.py' directly
    import uvicorn
    print("🚀 Engine starting in standalone mode...")
    uvicorn.run(app, host="0.0.0.0", port=8000)