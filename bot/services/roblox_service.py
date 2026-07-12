"""Service Roblox centralise.

Cette couche permet de migrer progressivement la logique de bot.py
sans casser le fonctionnement actuel.
"""

import aiohttp

ROBLOX_SEARCH = "https://users.roblox.com/v1/usernames/users"


async def verify_username(username: str):
    payload = {
        "usernames": [username],
        "excludeBannedUsers": True,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(ROBLOX_SEARCH, json=payload) as response:
            data = await response.json()

    if not data.get("data"):
        return {
            "verified": False,
            "message": "Compte Roblox introuvable"
        }

    player = data["data"][0]

    return {
        "verified": True,
        "roblox_id": player["id"],
        "username": player["name"]
    }
