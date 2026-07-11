from flask import Flask, request, jsonify
import requests


app = Flask(__name__)


# Stockage temporaire des comptes liés
comptes = {}


@app.route("/")
def accueil():
    return "✅ API Discord Roblox en ligne"



@app.route("/verify", methods=["POST"])
def verify():

    donnees = request.json

    if not donnees:
        return jsonify({
            "success": False,
            "message": "Aucune donnée reçue"
        })


    discord_id = donnees.get("discord_id")
    roblox_username = donnees.get("roblox_username")


    if not discord_id or not roblox_username:
        return jsonify({
            "success": False,
            "message": "Informations manquantes"
        })


    # Minimum 3 caractères
    if len(roblox_username) < 3:
        return jsonify({
            "success": False,
            "message": "Le pseudo doit contenir au moins 3 caractères"
        })


    # Empêche un Discord d'avoir plusieurs comptes Roblox
    if str(discord_id) in comptes:
        return jsonify({
            "success": False,
            "message": "Ce compte Discord est déjà lié"
        })


    # Vérification auprès de Roblox
    try:

        reponse = requests.post(
            "https://users.roblox.com/v1/usernames/users",
            json={
                "usernames": [roblox_username],
                "excludeBannedUsers": True
            }
        )


        resultat = reponse.json()


    except Exception:

        return jsonify({
            "success": False,
            "message": "Impossible de contacter Roblox"
        })


    if not resultat.get("data"):

        return jsonify({
            "success": False,
            "message": "Ce compte Roblox n'existe pas"
        })


    joueur = resultat["data"][0]

    roblox_id = joueur["id"]
    vrai_nom = joueur["name"]


    # Empêche un Roblox d'être lié à plusieurs Discord
    for compte in comptes.values():

        if compte["roblox_id"] == roblox_id:

            return jsonify({
                "success": False,
                "message": "Ce compte Roblox est déjà lié"
            })


    # Sauvegarde
    comptes[str(discord_id)] = {

        "roblox_username": vrai_nom,
        "roblox_id": roblox_id

    }


    return jsonify({

        "success": True,

        "message": "Compte Roblox vérifié",

        "roblox_username": vrai_nom,

        "roblox_id": roblox_id

    })



@app.route("/user/<discord_id>")
def utilisateur(discord_id):

    if discord_id in comptes:

        return jsonify({

            "success": True,

            "compte": comptes[discord_id]

        })


    return jsonify({

        "success": False,

        "message": "Aucun compte lié"

    })



if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )