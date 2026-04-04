import os
import json
import random
import psycopg2
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# --- 1. CONFIG & DATABASE CONNECTION ---
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    # Connects to Neon Postgres
    return psycopg2.connect(DATABASE_URL)

# Initialize the Database Table
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT,
            type TEXT,
            lat FLOAT,
            lon FLOAT,
            credits INTEGER DEFAULT 0,
            wisp_class TEXT
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

# Run init_db on startup
try:
    init_db()
except Exception as e:
    print(f"DB Init Error: {e}")

# --- 2. STATIC FILES & PATHS ---
current_file_path = os.path.abspath(__file__)
root_dir = os.path.dirname(os.path.dirname(current_file_path))
static_dir = os.path.join(root_dir, "static")

if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

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
    wisp_class: Optional[str] = None

# --- 4. ENDPOINTS ---

@app.get("/api/users")
def get_users():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Load all entities from Neon
    cur.execute("SELECT id, username, type, lat, lon, credits, wisp_class FROM users")
    rows = cur.fetchall()
    all_entities = [User(id=r[0], username=r[1], type=r[2], lat=r[3], lon=r[4], credits=r[5], wisp_class=r[6]) for r in rows]

    # Initialize Ben if missing
    if not any(u.id == "user_ben" for u in all_entities):
        ben = User(id="user_ben", username="Ben", type="user", lat=39.333, lon=-82.982, credits=0)
        cur.execute("INSERT INTO users (id, username, type, lat, lon, credits) VALUES (%s, %s, %s, %s, %s, %s)", 
                    (ben.id, ben.username, ben.type, ben.lat, ben.lon, ben.credits))
        all_entities.append(ben)

    # Populate Wisps if needed
    if len([u for u in all_entities if u.type == "wisp"]) < 10:
        for i in range(20):
            wisp = User(
                id=f"gen_{random.randint(1000, 9999)}", username="Wisp", type="wisp",
                lat=39.333 + random.uniform(-0.005, 0.005),
                lon=-82.982 + random.uniform(-0.005, 0.005),
                wisp_class="whisp-cyan"
            )
            cur.execute("INSERT INTO users (id, username, type, lat, lon, wisp_class) VALUES (%s, %s, %s, %s, %s, %s)",
                        (wisp.id, wisp.username, wisp.type, wisp.lat, wisp.lon, wisp.wisp_class))
            all_entities.append(wisp)

    # Move Wisps and Update DB
    for u in all_entities:
        if u.type == "wisp":
            u.lat += random.uniform(-0.0001, 0.0001)
            u.lon += random.uniform(-0.0001, 0.0001)
            cur.execute("UPDATE users SET lat = %s, lon = %s WHERE id = %s", (u.lat, u.lon, u.id))

    conn.commit()
    cur.close()
    conn.close()

    return {"entities": all_entities, "coach": "COACH: Data stored in the Cloud Vault."}

@app.post("/api/collect/{wisp_id}")
async def collect_wisp(wisp_id: str):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Add 15 credits to Ben and remove the wisp
    cur.execute("UPDATE users SET credits = credits + 15 WHERE id = 'user_ben'")
    cur.execute("DELETE FROM users WHERE id = %s", (wisp_id,))
    
    # Get new balance
    cur.execute("SELECT credits FROM users WHERE id = 'user_ben'")
    new_balance = cur.fetchone()[0]
    
    conn.commit()
    cur.close()
    conn.close()
    
    return {"new_balance": new_balance, "status": "success"}

@app.get("/", response_class=HTMLResponse)
async def read_index():
    index_path = os.path.join(root_dir, "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        return f.read()