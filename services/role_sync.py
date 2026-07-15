ROLE_PRIORITY = [
    {
        "discord_id": 1525820770167554078,
        "name": "👑 Owner",
        "color": {"r": 255, "g": 80, "b": 80}
    },
    {
        "discord_id": 1526588881779163246,
        "name": "💎 Booster III",
        "color": {"r": 180, "g": 0, "b": 255}
    },
    {
        "discord_id": 1526588739743125514,
        "name": "💎 Booster II",
        "color": {"r": 80, "g": 120, "b": 255}
    },
    {
        "discord_id": 1526586093934350469,
        "name": "💎 Booster I",
        "color": {"r": 255, "g": 180, "b": 0}
    },
    {
        "discord_id": 1525621386884944065,
        "name": "✅ Roblox Vérifié",
        "color": {"r": 0, "g": 255, "b": 0}
    }
]


def get_highest_role(member):
    for role in ROLE_PRIORITY:
        if any(discord_role.id == role["discord_id"] for discord_role in member.roles):
            return {
                "role": role["name"],
                "color": role["color"]
            }

    return {
        "role": "",
        "color": {"r": 255, "g": 255, "b": 255}
    }
