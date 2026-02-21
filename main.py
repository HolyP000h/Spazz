import math
import time
import json
import asyncio
import random
import winsound
from fastapi import FastAPI

app = FastAPI()

# --- 1. HELPERS (Keep these at the top, outside functions) ---
def create_entity(entity_id, username, e_type="user", lat=0.0, lon=0.0):
    return {
        "id": str(entity_id),
        "username": username,
        "type": e_type, 
        "mode": "vibe",
        "credits": 0,
        "lat": lat,
        "lon": lon,
        "pet": {
            "name": f"{username}'s Buddy",
            "type": "Starter Pet",
            "aura": "White",
            "level": 1
        } if e_type == "user" else None 
    }

# --- 2. THE HEARTBEAT (The background engine) ---
async def ghost_heartbeat():
    print("💓 Ghost Heartbeat is officially pumping...")
    while True:
        all_entities = load_from_db()
        
        # SPAWN LOGIC: Keep the map populated
        if len(all_entities) < 3:
            new_wisp = create_entity(f"wisp_{random.randint(1,99)}", "Golden Wisp", "wisp", 34.052, -118.243)
            all_entities = load_from_db() # Pure and simple.
            print("✨ [SPAWNER]: A Golden Wisp has appeared!")

        for entity in all_entities:
            # MOVEMENT
            entity["lat"] += random.uniform(-0.0005, 0.0005)
            entity["lon"] += random.uniform(-0.0005, 0.0005)

            # ZOMBIE SOUND
            if entity["type"] == "zombie":
                # Only play if you have the file!
                # winsound.PlaySound("zombie.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
                pass

        save_to_db(all_entities)
        await asyncio.sleep(30)

# --- 3. STARTUP EVENT (The ignition switch) ---
@app.on_event("startup")
async def startup_event():
    print("🧪 [DIAGNOSTIC]: Checking for users...")
    
    active_users = load_from_db()
    
    # Generate defaults if DB is empty
    if not active_users:
        # NEW WAY (Standard Dictionary)
        u1 = create_entity(1, "SpazzMaster_99", "user", 34.0522, -118.2437)
        u1["credits"] = 1000  # Now this works!
        u2 = create_entity(2, "RizzQueen", "user", 34.0525, -118.2440)
        save_to_db([u1, u2])
        print("✨ [DIAGNOSTIC]: Generated SpazzMaster and RizzQueen.")
    else:
        print(f"✅ [DIAGNOSTIC]: {len(active_users)} entities loaded.")

    # START the background task properly
    asyncio.create_task(ghost_heartbeat())
    print("🚀 Engine fully initialized and background tasks running.")

# --- THE SPAZZ SHOP CATALOG ---
SPAZZ_CATALOG = {
    "basic_white": {"name": "Standard Strobe", "type": "Skin", "color": "#FFFFFF", "price": 0},
    "boss_gold": {"name": "The Final Boss", "type": "Legendary", "color": "#FFD700", "price": 500},
    "neon_heart": {"name": "Lover Pulse", "type": "Skin", "color": "#FF1493", "price": 200},
    "police_chase": {"name": "The Heat", "type": "Strobe", "color": "Blue/Red", "price": 300}
}

# --- THE USER BLUEPRINT ---
def create_entity(entity_id, username, e_type="user", lat=0.0, lon=0.0):
    return {
        "id": str(entity_id),
        "username": username,
        "type": e_type, 
        "mode": "vibe",
        "credits": 0,
        "lat": lat,
        "lon": lon,
        "pet": {
            "name": f"{username}'s Buddy",
            "type": "Starter Pet",
            "aura": "White",
            "level": 1
        } if e_type == "user" else None 
    }

@app.on_event("startup")
async def startup_event():
    print("🧪 [DIAGNOSTIC]: Checking for users...")
    active_users = load_from_db()
    
    if not active_users:
        u1 = create_entity(1, "SpazzMaster_99", "user", 34.0522, -118.2437)
        u2 = create_entity(2, "RizzQueen", "user", 34.0525, -118.2440)
        save_to_db([u1, u2])
        print("✨ [DIAGNOSTIC]: Generated fresh entities.")

    asyncio.create_task(ghost_heartbeat())
    print("🚀 Engine fully initialized.")
    # ADD THIS PART SO ASSIGNMENT [] = WORK
    def __setitem__(self, key, value):
        setattr(self, key, value)

    def to_dict(self):
        return vars(self)

    # ADD THIS PART SO ASSIGNMENT [] = WORK
    def __setitem__(self, key, value):
        setattr(self, key, value)

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

import math

def calculate_bearing(lat1, lon1, lat2, lon2):
    """
    Calculates the bearing (direction) between two points.
    Returns degrees from 0 to 360.
    """
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_lambda = math.radians(lon2 - lon1)

    y = math.sin(delta_lambda) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - \
        math.sin(phi1) * math.cos(phi2) * math.cos(delta_lambda)

    theta = math.atan2(y, x)
    # Convert radians to degrees and normalize to 0-360
    return (math.degrees(theta) + 360) % 360

# --- WEB ENDPOINTS ---

from fastapi.responses import HTMLResponse

@app.get("/ui", response_class=HTMLResponse)
async def get_ui():
    with open("index.html", "r") as f:
        return f.read()

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
    
    if me is None or them is None:
        return {"error": "One or both users not found", "status": "offline"}

    dist = calculate_distance(me.lat, me.lon, them.lat, them.lon)
    bearing = calculate_bearing(me.lat, me.lon, them.lat, them.lon)
    
    # --- PULSE LOGIC: Determining the Vibe ---
    if dist < 0.002: # ~10 feet
        pulse_status = {"mode": "STROBE", "vibe": "SOLID", "speed": 0}
    elif dist < 0.05: # Close
        pulse_status = {"mode": "PULSE", "vibe": "FAST", "speed": 0.5}
    elif dist < 0.2: # Getting warmer
        pulse_status = {"mode": "PULSE", "vibe": "MEDIUM", "speed": 2.0}
    else: # Cold
        pulse_status = {"mode": "PULSE", "vibe": "SLOW", "speed": 5.0}
        
    skin = SPAZZ_CATALOG.get(them.active_skin, SPAZZ_CATALOG["basic_white"])

    # ONE FINAL RETURN with everything combined
    return {
        "target": them.username,
        "distance_miles": round(dist, 4),
        "bearing_degrees": round(bearing, 0),
        "pulse": pulse_status,
        "target_skin": skin,
        "status": "locked"
    }
    
    # --- THE SAFETY CHECK ---
    if me is None or them is None:
        return {"error": "One or both users not found", "status": "offline"}

    # Now Pylance knows 'me' and 'them' are safe to access
    dist = calculate_distance(me.lat, me.lon, them.lat, them.lon)
    bearing = calculate_bearing(me.lat, me.lon, them.lat, them.lon)
    
    return {
        "target": them.username,
        "distance_miles": round(dist, 2),
        "bearing_degrees": round(bearing, 0),
        "status": "locked"
    }
    
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

import time # Ensure this is at the VERY top of your file

@app.post("/daily_reward/{user_id}")
def claim_daily_reward(user_id: int):
    # 1. Load the data
    all_users = load_from_db() 
    
    # 2. Find the specific user (using a more explicit loop to help Pylance)
    target_user = None
    for u in all_users:
        if isinstance(u, dict) and u.get("id") == user_id:
            target_user = u
            break
    
    if not target_user:
        return {"error": "User not found"}

    # 3. Time Logic
    now = time.time()
    last_claim = target_user.get("last_reward_time", 0)
    
    if now - last_claim < 86400:
        seconds_left = int(86400 - (now - last_claim))
        hours_left = seconds_left // 3600
        return {"error": f"Too soon! Try again in {hours_left} hours."}
    
    # 4. Update and Save
    target_user["credits"] = target_user.get("credits", 0) + 50
    target_user["last_reward_time"] = now
    
    save_to_db(all_users)
    return {"message": "50 Credits added!", "new_balance": target_user["credits"]}
    
    user["credits"] = user.get("credits", 0) + 50
    user["last_reward_time"] = now
    
    save_to_db(users)
    return {"message": "50 Credits added!", "new_balance": user["credits"]}

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
def get_radar(user_id: int):
    users = load_from_db()
    me = next((u for u in users if u.id == user_id), None)
    
    if not me:
        return {"error": "User not found", "nearby_spazzers": []}

    nearby = []
    for user in users:
        if user.id != me.id:
            dist = calculate_distance(me.lat, me.lon, user.lat, user.lon)
            bearing = calculate_bearing(me.lat, me.lon, user.lat, user.lon)
            
            # Distance Logic for Pulse Speed
            if dist < 0.05:
                speed = 0.5  # Fast blink
            elif dist < 0.2:
                speed = 2.0  # Medium blink
            else:
                speed = 5.0  # Slow blink

            nearby.append({
                "username": user.username,
                "distance_miles": round(dist, 4),
                "bearing_degrees": round(bearing, 0),
                "pulse": {"speed": speed}
            })

    return {"nearby_spazzers": nearby}

    # ... existing distance calculation ...

    for user in users:
        if user.id != me.id:
            # All these lines must have the EXACT same starting gap (8 spaces)
            distance = calculate_distance(me.lat, me.lon, user.lat, user.lon)
            bearing_label = calculate_bearing(me.lat, me.lon, user.lat, user.lon)
            
            radar_results.append({
                "username": user.username,
                "distance_miles": round(distance, 2),
                "direction": bearing_label,
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



# --- GHOST PROTOCOL (The AI Brain) ---

def move_ghosts():
    users = load_from_db()
    me = next((u for u in users if u.id == 1), None)
    moved = False

    for user in users:
        if user.id != 1:
            user.lat += random.uniform(-0.0005, 0.0005)
            user.lon += random.uniform(-0.0005, 0.0005)
            moved = True
            
            # --- PROXIMITY CHECK ---
            if me:
                dist = calculate_distance(me.lat, me.lon, user.lat, user.lon)
                if dist < 0.05:  # Closer than 0.05 miles (~260 feet)
                    print(f"⚠️ [ALARM]: {user.username} is NEARBY! ({round(dist, 3)} mi)")
                    # winsound.Beep(frequency, duration_ms)
                    winsound.Beep(1000, 200) 
    
    if moved:
        save_to_db(users)

if __name__ == "__main__":
    import uvicorn
    print("🚀 Engine starting in standalone mode...")
    # Change 8000 to 8001
    uvicorn.run(app, host="0.0.0.0", port=8001)