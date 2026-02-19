import math
import time
import random
import asyncio
import json

# --- THE USER BLUEPRINT ---
class User:
    def __init__(self, id, username, is_premium=False, on_clock=False, 
                 nudges_balance=5, lat=0.0, lon=0.0, last_nudge_time=0):
        self.id = id
        self.username = username
        self.is_premium = is_premium
        self.on_clock = on_clock
        self.nudges_balance = nudges_balance
        self.lat = lat
        self.lon = lon
        self.last_nudge_time = last_nudge_time

    def to_dict(self):
        """Converts user object to a dictionary for JSON saving"""
        return vars(self)

# --- DATABASE TOOLS ---
def save_to_db(users_list):
    """Writes the current state of all users to the JSON file"""
    data = {"users": [u.to_dict() for u in users_list]}
    with open('users_db.json', 'w') as f:
        json.dump(data, f, indent=4)
    print("💾 [DATABASE]: All changes saved to users_db.json")

def load_from_db():
    """Reads users from the JSON file"""
    try:
        with open('users_db.json', 'r') as f:
            data = json.load(f)
            return [User(**u) for u in data["users"]]
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# --- THE SPAZZ ENGINE ---
if __name__ == "__main__":
    print("🚀 Spazz Engine Starting...")
    
    # Load users from your new database file
    active_users = load_from_db()

    # If the file is empty, create the OG users
    if not active_users:
        print("⚡ No users found. Initializing SpazzMaster and RizzQueen...")
        u1 = User(1, "SpazzMaster_99", is_premium=True)
        u2 = User(2, "RizzQueen", is_premium=False)
        active_users = [u1, u2]
        save_to_db(active_users)

    # Let's simulate you CLOCKING IN
    me = active_users[0]
    me.on_clock = True
    me.lat, me.lon = 40.7128, -74.0060 # Setting test coordinates
    
    print(f"✅ User {me.username} is now ON THE CLOCK at {me.lat}, {me.lon}")

    # Save the status back to the database
    save_to_db(active_users)
    print("🏁 Session complete. Check your users_db.json file!")

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Spazz API is Live!"}


@app.get("/users")
def get_users():
    # We turn the objects back into a list of dictionaries for the web
    users = load_from_db()
    return [u.to_dict() for u in users]
