import os
import importlib.util

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from core.engine import run_cognitive_cycle

from openai import OpenAI


app = FastAPI()


# =========================
# 🌱 ENVIRONMENT LOAD
# =========================

def load_environment():
    load_dotenv()

required = ["MODEL_NAME"]
for var in required:
    if not os.getenv(var):
        print(f"[ENV WARNING] Missing {var}")

        print("[ENV] Loaded.")


# =========================
# 🤖 LLM CLIENT INIT
# =========================

def init_llm_client(app_instance):
    """
Initializes an OpenAI-compatible client.
Works with:
- OpenAI
- LM Studio
- Ollama (via proxy)
- Custom endpoints
"""

api_key = os.getenv("API_KEY", "none")  # allow local models without key
base_url = os.getenv("API_BASE_URL", "http://localhost:1234/v1")
model = os.getenv("MODEL_NAME")

try:
     client = OpenAI(
     api_key=api_key,
     base_url=base_url
     )
except Exception as e:
     print(f"Client initialization failed: {e}")
     client = None(
     api_key=api_key,
     base_url=base_url
)

try:
    # Sanity test (lightweight)
    if not model:
        raise Exception("MODEL_NAME not set")

    app_instance.state.client = client

    print(f"[BOOT] LLM client ready → {base_url} | model={model}")

except Exception as e:
     print(f"[BOOT ERROR] LLM init failed: {e}")
     app_instance.state.client = None


# =========================
# 🔌 BUS LOADER
# =========================

def load_module_from_path(path, name):  
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
return module


def mount_pnp_buses(app_instance):
    buses = {
"patches": "patches/patches_bridge.py",
"tools": "tools/tools_bridge.py"
}

for bus_name, path in buses.items():
    if not os.path.exists(path):
        print(f"[BOOT WARNING] Missing {bus_name} bridge at {path}")
continue

module = load_module_from_path(path, f"{bus_name}_bridge")

if not hasattr(module, "call"):
    print(f"[BOOT ERROR] {bus_name}_bridge missing 'call'")
continue

setattr(app_instance, f"{bus_name}_bus", module)

print(f"[BOOT] {bus_name}_bus mounted")


# =========================
# 🚀 STARTUP
# =========================

@app.on_event("startup")
async def startup_event():
    print("[SYSTEM] Boot sequence initiated")

load_environment()
init_llm_client(app)
mount_pnp_buses(app)

print("[SYSTEM] Online")


# =========================
# 💬 CHAT ENDPOINT
# =========================

@app.get("/chat")
async def chat(q: str = Query(...)):
    try:
        client = getattr(app.state, "client", None)

if client is None:
    return JSONResponse({
"error": "LLM client not initialized"
})

response, _ = await run_cognitive_cycle(app, client, q)

return JSONResponse({
"response": response
})

except Exception as e:
return JSONResponse({
"error": f"KERNEL_EXCEPTION: {str(e)}"
})


# =========================
# ❤️ HEALTH
# =========================

@app.get("/health")
async def health():
return {
"status": "ok",
"model": os.getenv("MODEL_NAME"),
"base_url": os.getenv("API_BASE_URL"),
"tools": os.getenv("SVN_ACTIVE_TOOLS"),
"patches": os.getenv("SVN_ACTIVE_PATCHES")
}
