import json
import os
import tempfile
from datetime import datetime

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


def get_or_create_user(discord_id):
    user = get_user(discord_id)

    if user is None:
        user = {
            "risk_score": 0,
            "warnings": 0,
            "mutes": 0,
            "last_reason": None,
            "history": [],
        }
        set_user(discord_id, user)

    return user


def add_risk(discord_id, points, reason):
    user = get_or_create_user(discord_id)

    user["risk_score"] = user.get("risk_score", 0) + points
    user["last_reason"] = reason

    user.setdefault("history", []).append({
        "date": datetime.utcnow().isoformat(),
        "points": points,
        "reason": reason,
    })

    user["history"] = user["history"][-20:]

    set_user(discord_id, user)
    return user["risk_score"]


def add_warning(discord_id):
    user = get_or_create_user(discord_id)
    user["warnings"] = user.get("warnings", 0) + 1
    set_user(discord_id, user)
    return user["warnings"]


def add_mute(discord_id):
    user = get_or_create_user(discord_id)
    user["mutes"] = user.get("mutes", 0) + 1
    set_user(discord_id, user)
    return user["mutes"]
