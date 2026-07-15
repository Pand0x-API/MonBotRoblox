from flask import Flask, request, jsonify
import json
import os
import time

app = Flask(__name__)
DATABASE = "database.json"

# Codes temporaires générés par le bot Discord
verification_codes = {}


# Priorité des rôles Discord vers Roblox
ROLE_PRIORITY = {
    "Owner": {
        "name": "👑 Owner",
        "color": {"r": 255, "g": 80, "b": 80}
    },
    "Booster III": {
        "name": "💎 Booster III",
        "color": {"r": 180, "g": 0, "b": 255}
    },
    "Booster II": {
        "name": "💎 Booster II",
        "color": {"r": 80, "g": 120, "b": 255}
    },
    "Booster I": {
        "name": "💎 Booster I",
        "color": {"r": 255, "g": 180, "b": 0}
    },
    "Roblox Vérifié": {
        "name": "✅ Roblox Vérifié",
        "color": {"r": 0, "g": 255, "b": 0}
    }
}


def charger():
    if not os.path.exists(DATABASE):
        return {}
    with open(DATABASE, "r") as f:
        return json.load(f)


def sauvegarder(data):
    with open(DATABASE, "w") as f:
        json.dump(data, f, indent=4)


@app.route("/")
def accueil():
    return "✅ API Discord Roblox en ligne"


@app.route("/api/player/<user_id>")
def player_role(user_id):
    comptes = charger()

    compte = None
    for value in comptes.values():
        if str(value.get("roblox_id")) == str(user_id):
            compte = value
            break

    if not compte:
        return jsonify({
            "verified": False,
            "role": "",
            "color": {"r": 255, "g": 255, "b": 255}
        })

    roles = compte.get("roles", [])

    for role in ["Owner", "Booster III", "Booster II", "Booster I", "Roblox Vérifié"]:
        if role in roles:
            return jsonify({
                "verified": True,
                "role": ROLE_PRIORITY[role]["name"],
                "color": ROLE_PRIORITY[role]["color"]
            })

    return jsonify({
        "verified": True,
        "role": "",
        "color": {"r": 255, "g": 255, "b": 255}
    })


@app.route("/roblox/check_player", methods=["POST"])
def check_player():
    data = request.json or {}
    username = data.get("username")

    if not username:
        return jsonify({"found": False, "message": "Pseudo manquant"})

    players = data.get("players", [])
    for player in players:
        if player.lower() == username.lower():
            return jsonify({"found": True, "message": "Joueur connecté"})

    return jsonify({"found": False, "message": "Utilisateur non connecté"})


@app.route("/roblox/verify", methods=["POST"])
def verify_roblox():
    data = request.json or {}

    code = data.get("code")
    user_id = data.get("userId")
    username = data.get("username")

    if not code or not user_id or not username:
        return jsonify({"success": False, "status": "invalid_request"})

    saved = verification_codes.get(code)

    if not saved:
        return jsonify({"success": False, "status": "invalid_code"})

    if time.time() - saved["created"] > 300:
        del verification_codes[code]
        return jsonify({"success": False, "status": "expired_code"})

    comptes = charger()

    comptes[str(user_id)] = {
        "roblox_id": user_id,
        "username": username,
        "discord_id": saved["discord_id"],
        "roles": ["Roblox Vérifié"]
    }

    sauvegarder(comptes)
    del verification_codes[code]

    return jsonify({"success": True, "status": "success"})


@app.route("/roblox/status/<user_id>")
def status(user_id):
    comptes = charger()
    for compte in comptes.values():
        if str(compte.get("roblox_id")) == str(user_id):
            return jsonify({"verified": True, "username": compte.get("username")})
    return jsonify({"verified": False})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
