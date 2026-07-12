import os

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise RuntimeError("TOKEN manquant dans Render")

DATABASE_FILE = "database.json"
ROBLOX_TIMEOUT = 10
