import json
import random
import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# --- 1. DYNAMIC PATH LOGIC (The 500 Error Killer) ---
current_file_path = os.path.abspath(__file__)
api_dir = os.path.dirname(current_file_path)
root_dir = os.path.dirname(api_dir)
static_dir = os.path.join(root_dir, "static")

# If for some reason the folder is missing, this prevents the crash
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

# --- 2. CONFIG & PATHS ---
DB_FILE = '/tmp/users_db.json'

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 3. DATA MODEL ---
class User(BaseModel):
    id: str
    username: str
    type: str
    lat: float
    lon: float
    credits: int = 0
    gender: str = "other"
    is_premium: bool = False
    is_shadow_banned: bool = False
    age: int = 25
    wisp_class: Optional[str] = None

# --- 4. DATABASE TOOLS ---
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
        return []

# --- 5. THE ENGINE ---
def move_wisps(all_entities: List[User]):
    for entity in all_entities:
        if entity.type == "wisp":
            entity.lat += random.uniform(-0.0001, 0.0001)
            entity.lon += random.uniform(-0.0001, 0.0001)
    return all_entities

# --- 6. ENDPOINTS ---

@app.get("/api/users")
def get_users():
    all_entities = load_from_db()
    
    if not any(u.id == "user_ben" for u in all_entities):
        all_entities.append(User(
            id="user_ben", username="Ben", type="user",
            lat=39.333, lon=-82.982, credits=0
        ))
    
    if len(all_entities) < 10:
        for i in range(30):
            new_id = f"gen_{random.randint(1000, 9999)}"
            all_entities.append(User(
                id=new_id, username="Wisp", type="wisp",
                lat=39.333 + random.uniform(-0.005, 0.005),
                lon=-82.982 + random.uniform(-0.005, 0.005),
                wisp_class="whisp-cyan"
            ))

    all_entities = move_wisps(all_entities)
    save_to_db(all_entities)
    
    return {
        "entities": [u for u in all_entities if not u.is_shadow_banned],
        "coach": "COACH: Scanning for Phantoms..."
    }

@app.post("/api/collect/{wisp_id}")
async def collect_wisp(wisp_id: str):
    all_entities = load_from_db()
    target_wisp = next((x for x in all_entities if x.id == wisp_id), None)
    user_ben = next((x for x in all_entities if x.id == "user_ben"), None)

    if target_wisp and user_ben:
        user_ben.credits += 15
        all_entities = [u for u in all_entities if u.id != wisp_id]
        save_to_db(all_entities)
        return {"new_balance": user_ben.credits, "status": "success"}
    
    return {"status": "failed", "message": "Target lost"}

@app.get("/", response_class=HTMLResponse)
async def read_index():
    index_path = os.path.join(root_dir, "index.html")
    try:
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return HTMLResponse(content=f"Error loading index: {str(e)}", status_code=500)