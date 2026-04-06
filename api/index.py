import json
import random
import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# --- 1. CONFIG & PATHS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, 'users_db.json')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. DATA MODEL ---
class User(BaseModel):
    id: str
    username: str
    type: str
    lat: float
    lon: float
    credits: int = 0
    gender: str = "other"
    seeking: str = "female"  # Added: "male", "female", or "everyone"
    is_premium: bool = False
    is_shadow_banned: bool = False
    age: int = 25
    wisp_class: Optional[str] = None

# --- 3. DATABASE TOOLS ---
def save_to_db(users_list: List[User]):
    data = {"users": [u.model_dump() for u in users_list]}
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def load_from_db() -> List[User]:
    if not os.path.exists(DB_FILE):
        return []
    try:
        with open(DB_FILE, 'r') as f:
            data = json.load(f)
            user_data = data.get("users", [])
            return [User(**u) for u in user_data]
    except Exception as e:
        print(f"Error loading DB: {e}")
        return []

# --- 4. THE ENGINE ---
def move_wisps(all_entities: List[User]):
    for entity in all_entities:
        if entity.type == "wisp":
            entity.lat += random.uniform(-0.0001, 0.0001)
            entity.lon += random.uniform(-0.0001, 0.0001)
    return all_entities

# --- 5. ENDPOINTS ---

@app.get("/api/users")
def get_users():
    all_entities = load_from_db()
    
    # Initialize Ben if missing (Defaulting Ben to seeking females)
    if not any(u.id == "user_ben" for u in all_entities):
        all_entities.append(User(
            id="user_ben", username="Ben", type="user",
            lat=39.333, lon=-82.982, credits=0, 
            gender="male", seeking="female"
        ))
    
    user_ben = next(u for u in all_entities if u.id == "user_ben")

    # Populate ghosts/targets if needed
    if len(all_entities) < 10:
        for i in range(30):
            new_id = f"gen_{random.randint(1000, 9999)}"
            is_match_candidate = random.random() > 0.7 
            
            # Randomize gender for ghosts/targets
            gen_gender = random.choice(["male", "female", "non-binary"])
            
            all_entities.append(User(
                id=new_id, 
                username="Potential Spazz" if is_match_candidate else "Wisp", 
                type="user" if is_match_candidate else "wisp",
                lat=39.333 + random.uniform(-0.015, 0.015),
                lon=-82.982 + random.uniform(-0.015, 0.015),
                gender=gen_gender,
                age=random.randint(19, 45),
                wisp_class="whisp-purple" if is_match_candidate else "whisp-cyan"
            ))
            
    # Move ghosts every time the radar is checked
    all_entities = move_wisps(all_entities)
    save_to_db(all_entities)
    
    # --- UNIVERSAL COMPATIBILITY LOGIC ---
    # We tag each entity with 'is_match' based on Ben's specific settings
    output_entities = []
    for u in all_entities:
        u_dict = u.model_dump()
        u_dict["is_match"] = False
        
        # Only check if it's a "user" and not Ben himself
        if u.type == "user" and u.id != "user_ben":
            # Match if seeking everyone, or if gender matches Ben's 'seeking'
            if user_ben.seeking == "everyone" or user_ben.seeking == u.gender:
                u_dict["is_match"] = True
        
        output_entities.append(u_dict)
    
    return {
        "entities": [u for u in output_entities if not u.get("is_shadow_banned")],
        "coach": "COACH: Be vewy vewy quiet... we hunting wisps." if random.random() > 0.5 else "COACH: Target detected. Stay frosty."
    }    

@app.post("/api/collect/{wisp_id}")
async def collect_wisp(wisp_id: str):
    all_entities = load_from_db()
    target_wisp = next((x for x in all_entities if x.id == wisp_id), None)
    user_ben = next((x for x in all_entities if x.id == "user_ben"), None)

    if target_wisp and user_ben:
        user_ben.credits += 15
        # Remove the collected target
        all_entities = [u for u in all_entities if u.id != wisp_id]
        save_to_db(all_entities)
        return {"new_balance": user_ben.credits, "status": "success"}
    
    return {"status": "failed", "message": "Target lost"}, 400

@app.get("/", response_class=HTMLResponse)
async def read_index():
    root_index = os.path.join(BASE_DIR, "..", "index.html")
    with open(root_index, "r", encoding="utf-8") as f:
        return f.read()