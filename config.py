import os

TOKEN = os.getenv("TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TOKEN:
    raise RuntimeError("TOKEN manquant dans Render")

DATABASE_FILE = "database.json"
ROBLOX_TIMEOUT = 10
