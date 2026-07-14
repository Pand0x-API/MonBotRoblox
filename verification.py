import random
import time


_codes = {}

CODE_TIMEOUT = 300


def create_code(discord_id: int, roblox_username: str):
    code = f"RBX-{random.randint(100000, 999999)}"
    _codes[code] = {
        "discord_id": str(discord_id),
        "username": roblox_username,
        "created": time.time()
    }
    return code


def consume_code(code: str):
    data = _codes.get(code)

    if not data:
        return None

    if time.time() - data["created"] > CODE_TIMEOUT:
        del _codes[code]
        return None

    del _codes[code]
    return data


def check_code(code: str, username: str):
    data = _codes.get(code)

    if not data:
        return False

    if time.time() - data["created"] > CODE_TIMEOUT:
        del _codes[code]
        return False

    return data["username"].lower() == username.lower()
