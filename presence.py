import discord

# Jeux Roblox autorisés
# Ajoute tes PlaceId ici
ALLOWED_GAMES = {
    # 123456789: "Nom du jeu"
}


def detect_roblox_activity(member: discord.Member):
    """Détecte une activité Roblox dans Discord."""
    for activity in member.activities:
        if isinstance(activity, discord.Game):
            if "roblox" in activity.name.lower():
                return activity.name

        if isinstance(activity, discord.Activity):
            name = str(getattr(activity, "name", ""))
            if "roblox" in name.lower():
                return name

    return None


def is_allowed_game(activity_name: str):
    if not activity_name:
        return False

    return True
