import math
import time
import json
from fastapi import FastAPI

app = FastAPI()

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
                 credits=0, inventory=None, active_skin="basic_white", **kwargs):
        
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

# --- WEB ENDPOINTS ---

@app.get("/")
def home():
    return {"status": "Spazz Engine Online", "docs": "/docs"}

@app.get("/users")
def get_users():
    return [u.to_dict() for u in load_from_db()]

@app.post("/nudge/{sender_id}/{receiver_id}")
def nudge_user(sender_id: int, receiver_id: int):
    users = load_from_db()
    sender = next((u for u in users if u.id == sender_id), None)
    receiver = next((u for u in users if u.id == receiver_id), None)

    if not sender or not receiver:
        return {"error": "User missing"}

    # THE SHIELD
    if sender_id in receiver.blocked_users: return {"error": "Blocked."}
    if not (sender.min_age <= receiver.age <= sender.max_age): return {"error": "Age mismatch."}
    if not (receiver.min_age <= sender.age <= receiver.max_age): return {"error": "They don't want you."}
    if sender.interested_in != "Both" and sender.interested_in != receiver.gender: return {"error": "Gender mismatch."}

    if sender.nudges_balance <= 0 and not sender.is_premium:
        return {"error": "No nudges left!"}

    sender.nudges_balance -= 1
    save_to_db(users)
    return {"message": "Nudge delivered!"}

@app.post("/buy_item/{user_id}/{item_id}")
def buy_item(user_id: int, item_id: str):
    users = load_from_db()
    user = next((u for u in users if u.id == user_id), None)
    
    if not user or item_id not in SPAZZ_CATALOG:
        return {"error": "Invalid item or user"}
    if item_id in user.inventory:
        return {"error": "Already owned!"}
        
    price = SPAZZ_CATALOG[item_id]["price"]
    if user.credits >= price:
        user.credits -= price
        user.inventory.append(item_id)
        user.active_skin = item_id
        save_to_db(users)
        return {"message": f"Equipped {SPAZZ_CATALOG[item_id]['name']}!"}
    return {"error": "Broke! Need more credits."}

@app.post("/block/{user_id}/{target_id}")
def block_user(user_id: int, target_id: int):
    users = load_from_db()
    me = next((u for u in users if u.id == user_id), None)
    if me and target_id not in me.blocked_users:
        me.blocked_users.append(target_id)
        save_to_db(users)
        return {"message": "User blocked."}
    return {"error": "Action failed."}

if __name__ == "__main__":
    print("🚀 Simulator mode active. Run 'uvicorn main:app --reload' for Web mode.")
