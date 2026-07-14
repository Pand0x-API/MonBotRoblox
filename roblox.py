import aiohttp

_cache = {}


async def get_user(username: str):
    key = str(username).lower()

    if key in _cache:
        return _cache[key]

    url = "https://users.roblox.com/v1/usernames/users"

    payload = {
        "usernames": [username],
        "excludeBannedUsers": True
    }

    timeout = aiohttp.ClientTimeout(total=10)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(url, json=payload) as response:
            data = await response.json()

    if not data.get("data"):
        return None

    user = data["data"][0]
    _cache[key] = user
    return user


async def get_user_by_id(user_id: int):
    key = f"id_{user_id}"

    if key in _cache:
        return _cache[key]

    url = f"https://users.roblox.com/v1/users/{user_id}"

    timeout = aiohttp.ClientTimeout(total=10)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url) as response:
            if response.status != 200:
                return None
            user = await response.json()

    _cache[key] = user
    return user
