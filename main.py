import math
import time
import random
import asyncio
import json
from fastapi import FastAPI

app = FastAPI()

# --- THE USER BLUEPRINT ---
class User:
    def __init__(self, id, username, is_premium=False, on_clock=False, 
                 nudges_balance=5, lat=0.0, lon=0.0, last_nudge_time=0):
        self.id = int(id)  # Ensure ID is always an integer
        self.username = username
        self.is_premium = is_premium
        self.on_clock = on_clock
        self.nudges_balance = nudges_balance
        self.lat = lat
        self.lon = lon
        self.last_nudge_time = last_nudge_time

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
    users = load_from_db()
    return [u.to_dict() for u in users]

@app.post("/nudge/{sender_id}/{receiver_id}")
def nudge_user(sender_id: int, receiver_id: int):
    users = load_from_db()
    sender = next((u for u in users if u.id == sender_id), None)
    receiver = next((u for u in users if u.id == receiver_id), None)

    if not sender or not receiver:
        return {"error": "User missing from database"}

    if sender.nudges_balance <= 0 and not sender.is_premium:
        return {"error": "No nudges left. Wait for refill or buy Premium!"}

    # Execute Nudge
    sender.nudges_balance -= 1
    sender.last_nudge_time = time.time()
    
    save_to_db(users)
    return {"message": f"Nudge sent from {sender.username} to {receiver.username}!"}

# --- LOCAL SIMULATOR ---
if __name__ == "__main__":
    active_users = load_from_db()
    if not active_users:
        u1 = User(1, "SpazzMaster_99", is_premium=True)
        u2 = User(2, "RizzQueen", is_premium=False)
        active_users = [u1, u2]
        save_to_db(active_users)
    print("🚀 Simulator mode active. Run 'uvicorn main:app --reload' for Web mode.")
