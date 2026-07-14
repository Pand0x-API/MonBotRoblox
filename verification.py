import random
import time


_codes = {}


def create_code(discord_id: int, roblox_username: str):
    code = f"RBX-{random.randint(100000, 999999)}"
    _codes[code] = {
        "discord_id": str(discord_id),
        "username": roblox_username,
        "created": time.time()
    }
    return code


def check_code(code: str, username: str):
    data = _codes.get(code)

    if not data:
        return False

    if time.time() - data["created"] > 300:
        del _codes[code]
        return False

    return data["username"].lower() == username.lower()
