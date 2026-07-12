"""Service Roblox - future migration de la logique existante."""


async def verify_username(username: str):
    return {"username": username, "verified": False}
