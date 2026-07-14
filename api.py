from flask import Flask, request, jsonify
import json
import os
import time

app = Flask(__name__)
DATABASE = "database.json"

# Codes temporaires générés par le bot Discord
verification_codes = {}


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


@app.route("/roblox/check_player", methods=["POST"])
def check_player():
    data = request.json or {}
    username = data.get("username")

    if not username:
        return jsonify({"found": False, "message": "Pseudo manquant"})

    players = data.get("players", [])

    for player in players:
        if player.lower() == username.lower():
            return jsonify({
                "found": True,
                "message": "Joueur connecté"
            })

    return jsonify({
        "found": False,
        "message": "Utilisateur non connecté"
    })


@app.route("/roblox/verify", methods=["POST"])
def verify_roblox():
    data = request.json or {}

    code = data.get("code")
    user_id = data.get("userId")
    username = data.get("username")

    if not code or not user_id or not username:
        return jsonify({
            "success": False,
            "status": "invalid_request",
            "message": "Informations manquantes"
        })

    saved = verification_codes.get(code)

    if not saved:
        return jsonify({
            "success": False,
            "status": "invalid_code",
            "message": "Code invalide"
        })

    if time.time() - saved["created"] > 300:
        del verification_codes[code]
        return jsonify({
            "success": False,
            "status": "expired_code",
            "message": "Code expiré"
        })

    comptes = charger()

    comptes[str(user_id)] = {
        "roblox_id": user_id,
        "username": username,
        "discord_id": saved["discord_id"]
    }

    sauvegarder(comptes)
    del verification_codes[code]

    return jsonify({
        "success": True,
        "status": "success",
        "message": "Compte lié avec succès"
    })


@app.route("/roblox/status/<user_id>")
def status(user_id):
    comptes = charger()
    for compte in comptes.values():
        if str(compte.get("roblox_id")) == str(user_id):
            return jsonify({"verified": True, "username": compte.get("username")})
    return jsonify({"verified": False})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
