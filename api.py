from flask import Flask, request, jsonify
import requests
import json
import os
from datetime import datetime


app = Flask(__name__)


DATABASE = "database.json"


# ================= BASE DE DONNÉES =================

def charger():

    if not os.path.exists(DATABASE):
        return {}

    with open(DATABASE, "r") as fichier:
        return json.load(fichier)



def sauvegarder(data):

    with open(DATABASE, "w") as fichier:
        json.dump(
            data,
            fichier,
            indent=4
        )



# ================= PAGE TEST =================

@app.route("/")
def accueil():

    return "✅ API Discord Roblox en ligne"



# ================= VERIFICATION ROBLOX =================

@app.route("/verify", methods=["POST"])
def verify():

    data = request.json


    discord_id = data.get("discord_id")
    username = data.get("roblox_username")


    if not discord_id or not username:

        return jsonify({
            "success": False,
            "message": "Informations manquantes"
        })



    comptes = charger()



    # Discord déjà lié

    if discord_id in comptes:

        return jsonify({

            "success": False,

            "message": "Ce Discord est déjà lié"

        })



    try:

        resultat = requests.post(

            "https://users.roblox.com/v1/usernames/users",

            json={

                "usernames":[username],

                "excludeBannedUsers":True

            }

        ).json()


    except:

        return jsonify({

            "success":False,

            "message":"Erreur Roblox"

        })



    if not resultat.get("data"):

        return jsonify({

            "success":False,

            "message":"Compte Roblox introuvable"

        })



    joueur = resultat["data"][0]


    roblox_id = joueur["id"]

    vrai_nom = joueur["name"]



    # Roblox déjà utilisé

    for compte in comptes.values():

        if compte["roblox_id"] == roblox_id:

            return jsonify({

                "success":False,

                "message":"Ce compte Roblox est déjà lié"

            })



    comptes[discord_id] = {


        "discord_id":discord_id,

        "roblox_id":roblox_id,

        "username":vrai_nom,

        "date":str(datetime.now()),

        "banned":False


    }


    sauvegarder(comptes)



    return jsonify({

        "success":True,

        "message":"Compte lié",

        "roblox_id":roblox_id,

        "username":vrai_nom

    })





# ================= VERIFICATION ROBLOX STUDIO =================


@app.route("/roblox/<user_id>")
def roblox_check(user_id):


    comptes = charger()



    for compte in comptes.values():


        if str(compte["roblox_id"]) == str(user_id):


            return jsonify({


                "verified":True,


                "banned":compte["banned"],


                "username":compte["username"]


            })



    return jsonify({

        "verified":False,

        "banned":False

    })





# ================= BAN =================


@app.route("/ban", methods=["POST"])
def ban():


    data=request.json


    roblox_id=str(data.get("roblox_id"))


    comptes=charger()



    for compte in comptes.values():

        if str(compte["roblox_id"]) == roblox_id:


            compte["banned"]=True

            sauvegarder(comptes)


            return jsonify({

                "success":True

            })



    return jsonify({

        "success":False,

        "message":"Compte inconnu"

    })





# ================= UNBAN =================


@app.route("/unban", methods=["POST"])
def unban():


    data=request.json


    roblox_id=str(data.get("roblox_id"))


    comptes=charger()



    for compte in comptes.values():

        if str(compte["roblox_id"]) == roblox_id:


            compte["banned"]=False

            sauvegarder(comptes)


            return jsonify({

                "success":True

            })



    return jsonify({

        "success":False

    })





if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=5000

    )
