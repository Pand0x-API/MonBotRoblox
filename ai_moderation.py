import re


async def get_action(risk: int):
    if risk < 100:
        return "none"
    if risk < 200:
        return "warning"
    if risk < 300:
        return "mute"
    if risk >= 400:
        return "human_review"
    return "review"


async def analyze_message(content: str):
    """Analyse locale d'un message Discord sans API externe."""

    text = content.lower()
    risk = 0
    reasons = []

    # Flood / répétitions
    words = text.split()
    if len(words) >= 10 and len(set(words)) <= 3:
        risk += 80
        reasons.append("répétition excessive")

    # Messages trop longs
    if len(content) > 1000:
        risk += 50
        reasons.append("message très long")

    # Liens suspects
    if re.search(r"https?://", text):
        risk += 30
        reasons.append("lien détecté")

    # Spam de caractères
    if re.search(r"(.)\1{6,}", text):
        risk += 60
        reasons.append("spam de caractères")

    # Mots indicateurs simples
    suspicious = [
        "free robux",
        "nitro gratuit",
        "hack",
        "token",
        "raid"
    ]

    for word in suspicious:
        if word in text:
            risk += 100
            reasons.append(f"mot suspect: {word}")

    risk = min(risk, 500)

    return {
        "risk": risk,
        "reason": ", ".join(reasons) if reasons else "aucun comportement suspect",
        "action": await get_action(risk)
    }
