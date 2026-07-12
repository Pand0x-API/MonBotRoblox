import json
import os
import tempfile
from config import DATABASE_FILE


def load_database():
    if not os.path.exists(DATABASE_FILE):
        return {}
    try:
        with open(DATABASE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_database(data):
    fd, path = tempfile.mkstemp()
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        os.replace(path, DATABASE_FILE)
    except Exception:
        if os.path.exists(path):
            os.remove(path)


def set_user(discord_id, data):
    db = load_database()
    db[str(discord_id)] = data
    save_database(db)


def get_user(discord_id):
    return load_database().get(str(discord_id))
