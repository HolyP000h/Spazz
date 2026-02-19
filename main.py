import math
import time
import random
import asyncio
import json
from fastapi import FastAPI

app = FastAPI()

# --- THE USER BLUEPRINT ---
class User:
    def __init__(self, id, username, age, gender, interested_in, 
                 min_age=18, max_age=99, is_premium=False, 
                 on_clock=False, nudges_balance=5, lat=0.0, lon=0.0, 
                 last_nudge_time=0, blocked_users=None, **kwargs):
        self.id = int(id)
        self.username = username
        self.age = int(age)
        self.gender = gender           # "M", "F", "NB"
        self.interested_in = interested_in # "M", "F", "Both"
        self.min_age = int(min_age)
        self.max_age = int(max_age)
        self.is_premium = is_premium
        self.on_clock = on_clock
        self.nudges_balance = nudges_balance
        self.lat = lat
        self.lon = lon
        self.last_nudge_time = last_nudge_time
        self.blocked_users = blocked_users if blocked_users else []

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
        return {"error": "User missing from database"}

    # --- THE SHIELD (Safety Logic) ---
    
    # 1. Block Check
    if sender_id in receiver.blocked_users:
        return {"error": "You are blocked by this user."}

    # 2. Age Check (Does the receiver fit the sender's preference?)
    if not (sender.min_age <= receiver.age <= sender.max_age):
        return {"error": "This user is outside your age preference."}

    # 3. Reverse Age Check (Does the sender fit the receiver's preference?)
    if not (receiver.min_age <= sender.age <= receiver.max_age):
        return {"error": "You are outside this user's age preference."}

    # 4. Gender Check
    if sender.interested_in != "Both" and sender.interested_in != receiver.gender:
        return {"error": "Gender preference mismatch."}

    # --- NUDGE EXECUTION ---
    if sender.nudges_balance <= 0 and not sender.is_premium:
        return {"error": "No nudges left! Wait for refill or buy Premium."}

    sender.nudges_balance -= 1
    sender.last_nudge_time = time.time()
    
    save_to_db(users)
    return {"message": f"Nudge delivered from {sender.username} to {receiver.username}!"}

# --- LOCAL SIMULATOR ---
@app.post("/block/{user_id}/{target_id}")
def block_user(user_id: int, target_id: int):
    users = load_from_db()
    me = next((u for u in users if u.id == user_id), None)
    
    if me:
        if target_id not in me.blocked_users:
            me.blocked_users.append(target_id)
            save_to_db(users)
            return {"message": f"User {target_id} has been blocked."}
        return {"message": "User already blocked."}
    
    return {"error": "User not found."}

if __name__ == "__main__":
    active_users = load_from_db()
    if not active_users:
        # Create fresh users with Age and Gender for the new logic
        u1 = User(1, "SpazzMaster_99", 25, "M", "F", is_premium=True)
        u2 = User(2, "RizzQueen", 22, "F", "M", is_premium=False)
        active_users = [u1, u2]
        save_to_db(active_users)
    print("🚀 Simulator mode active.")
