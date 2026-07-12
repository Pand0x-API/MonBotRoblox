"""Routes Roblox preparees pour la connexion jeu/API."""

from flask import Blueprint, jsonify

roblox_routes = Blueprint("roblox", __name__)


@roblox_routes.route("/player/<roblox_id>")
def player(roblox_id):
    return jsonify({
        "roblox_id": roblox_id,
        "connected": True,
        "message": "Endpoint Roblox pret"
    })


@roblox_routes.route("/health")
def health():
    return jsonify({"roblox_api": "online"})
