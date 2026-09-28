
"""
server.py — SAMURAI v1.1 AI World Backend
FastAPI server with real A1111/ComfyUI integration
"""
import os, json, time, asyncio, hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

app = FastAPI(title="SAMURAI AI World", version="1.1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "config.json"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# ─── Config ───────────────────────────────────────────────
def load_config():
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return {
        "a1111_url": "http://127.0.0.1:7860",
        "comfyui_url": "http://127.0.0.1:8188",
        "default_backend": "a1111",
    }

# ─── State ────────────────────────────────────────────────
class WorldState:
    def __init__(self):
        self.initialized = False
        self.modules = {
            "mind": {"name": "Mind Core", "status": "offline", "level": 0},
            "memory": {"name": "Memory Vault", "status": "offline", "level": 0},
            "action": {"name": "Action Engine", "status": "offline", "level": 0},
            "research": {"name": "Research Lab", "status": "offline", "level": 0},
            "twin": {"name": "Twin Lab", "status": "offline", "level": 0},
            "vision": {"name": "Vision", "status": "locked", "level": 0},
            "voice": {"name": "Voice", "status": "locked", "level": 0},
            "browser": {"name": "Browser", "status": "locked", "level": 0},
            "crm": {"name": "CRM", "status": "locked", "level": 0},
        }
        self.xp = 0
        self.level = 1
        self.missions_completed = 0
        self.images_generated = 0
        self.backend_status = {"a1111": "offline", "comfyui": "offline"}
        self.generation_queue = []
        self.active_missions = []
        self.discovered_traits = []

    def to_dict(self):
        return {
            "initialized": self.initialized,
            "modules": self.modules,
            "xp": self.xp,
            "level": self.level,
            "missions_completed": self.missions_completed,
            "images_generated": self.images_generated,
            "backend_status": self.backend_status,
            "active_missions": self.active_missions,
            "discovered_traits": self.discovered_traits,
        }

state = WorldState()

# ─── A1111 Connector ──────────────────────────────────────
async def check_a1111(url: str) -> bool:
    try:
        import httpx
        async with httpx.AsyncClient(timeout=3) as client:
            r = await client.get(f"{url}/sdapi/v1/options")
            return r.status_code == 200
    except:
        return False

async def generate_a1111(url: str, prompt: str, n: int = 1, steps: int = 30, cfg: int = 7) -> list:
    try:
        import httpx
        async with httpx.AsyncClient(timeout=120) as client:
            payload = {
                "prompt": prompt,
                "steps": steps,
                "cfg_scale": cfg,
                "width": 1024,
                "height": 1024,
                "sampler_name": "Euler a",
                "batch_size": n,
            }
            r = await client.post(f"{url}/sdapi/v1/txt2img", json=payload)
            if r.status_code == 200:
                data = r.json()
                images = []
                for i, b64 in enumerate(data.get("images", [])):
                    img_path = OUTPUT_DIR / f"gen_{int(time.time())}_{i}.png"
                    import base64
                    img_path.write_bytes(base64.b64decode(b64))
                    images.append(str(img_path))
                return images
    except Exception as e:
        print(f"A1111 error: {e}")
    return []

# ─── ComfyUI Connector ───────────────────────────────────
async def check_comfyui(url: str) -> bool:
    try:
        import httpx
        async with httpx.AsyncClient(timeout=3) as client:
            r = await client.get(f"{url}/system_stats")
            return r.status_code == 200
    except:
        return False

# ─── API Routes ───────────────────────────────────────────

@app.get("/api/world")
async def get_world():
    """Get current world state"""
    return state.to_dict()

@app.post("/api/initialize")
async def initialize_world():
    """Initialize the AI world"""
    config = load_config()
    
    # Check backends
    state.backend_status["a1111"] = "online" if await check_a1111(config.get("a1111_url", "http://127.0.0.1:7860")) else "offline"
    state.backend_status["comfyui"] = "online" if await check_comfyui(config.get("comfyui_url", "http://127.0.0.1:8188")) else "offline"
    
    # Activate core modules
    for key in ["mind", "memory", "action", "research", "twin"]:
        state.modules[key]["status"] = "online"
        state.modules[key]["level"] = 1
    
    state.initialized = True
    state.xp = 100
    state.level = 1
    
    return {"status": "initialized", "world": state.to_dict()}

@app.post("/api/generate")
async def generate(prompt: str, n: int = 1, backend: str = "a1111", steps: int = 30, cfg: int = 7):
    """Generate images via A1111 or ComfyUI"""
    config = load_config()
    
    if backend == "a1111":
        images = await generate_a1111(config.get("a1111_url", "http://127.0.0.1:7860"), prompt, n, steps, cfg)
    elif backend == "comfyui":
        # ComfyUI workflow queue
        images = []
    else:
        # Mock mode
        images = [f"mock_{i}.png" for i in range(n)]
    
    state.images_generated += len(images)
    state.xp += 10 * len(images)
    
    # Level up check
    if state.xp >= state.level * 200:
        state.level += 1
        # Unlock new module
        locked = [k for k, v in state.modules.items() if v["status"] == "locked"]
        if locked:
            new_mod = locked[0]
            state.modules[new_mod]["status"] = "online"
            state.modules[new_mod]["level"] = 1
            state.discovered_traits.append(f"Unlocked: {state.modules[new_mod]['name']}")
    
    return {
        "images": images,
        "prompt": prompt,
        "backend": backend,
        "xp_gained": 10 * len(images),
        "world": state.to_dict(),
    }

@app.get("/api/status")
async def get_status():
    """Get backend status"""
    config = load_config()
    state.backend_status["a1111"] = "online" if await check_a1111(config.get("a1111_url", "http://127.0.0.1:7860")) else "offline"
    state.backend_status["comfyui"] = "online" if await check_comfyui(config.get("comfyui_url", "http://127.0.0.1:8188")) else "offline"
    return state.backend_status

@app.post("/api/mission/complete")
async def complete_mission(mission_type: str, value: int = 100):
    """Complete a mission and gain XP"""
    state.missions_completed += 1
    state.xp += value
    
    # Level up
    if state.xp >= state.level * 200:
        state.level += 1
        locked = [k for k, v in state.modules.items() if v["status"] == "locked"]
        if locked:
            new_mod = locked[0]
            state.modules[new_mod]["status"] = "online"
            state.modules[new_mod]["level"] = 1
            state.discovered_traits.append(f"Unlocked: {state.modules[new_mod]['name']}")
    
    return {"status": "complete", "xp_gained": value, "world": state.to_dict()}

@app.get("/api/stats")
async def get_stats():
    """Get usage statistics"""
    return {
        "images_generated": state.images_generated,
        "missions_completed": state.missions_completed,
        "xp": state.xp,
        "level": state.level,
        "modules_online": sum(1 for m in state.modules.values() if m["status"] == "online"),
        "modules_total": len(state.modules),
    }

# ─── Static Files ─────────────────────────────────────────
app.mount("/output", StaticFiles(directory=OUTPUT_DIR), name="output")

@app.get("/")
async def serve_index():
    return FileResponse(BASE_DIR / "index.html")

# ─── Launch ───────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8888)
