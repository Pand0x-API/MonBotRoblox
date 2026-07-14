from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)
DATABASE = "database.json"


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
    """Reçoit une demande du serveur Roblox pour savoir si un joueur est connecté."""
    data = request.json or {}
    username = data.get("username")

    if not username:
        return jsonify({"found": False, "message": "Pseudo manquant"})

    # Le serveur Roblox devra envoyer la liste des joueurs connectés
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


@app.route("/roblox/status/<user_id>")
def status(user_id):
    comptes = charger()
    for compte in comptes.values():
        if str(compte.get("roblox_id")) == str(user_id):
            return jsonify({"verified": True, "username": compte.get("username")})
    return jsonify({"verified": False})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
