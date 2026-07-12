"""Couche API Roblox centralisee."""

import requests

ROBLOX_URL = "https://users.roblox.com/v1/usernames/users"


def normalize_player(username):
    return username.strip()


def find_player(username):
    response = requests.post(
        ROBLOX_URL,
        json={
            "usernames": [normalize_player(username)],
            "excludeBannedUsers": True,
        },
        timeout=10,
    )

    data = response.json()

    if not data.get("data"):
        return None

    return data["data"][0]
