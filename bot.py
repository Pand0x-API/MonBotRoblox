import os
from datetime import timedelta
from threading import Thread

import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask, request, jsonify

from logger import logger
from roblox import get_user
from verification import create_code, check_code, consume_code
from ai_moderation import analyze_message
from database import add_risk, add_warning, add_mute

BOT_VERSION = "1.4.1"
BOT_LOG_CHANNEL = 1525582433775390830
GUILD_ID = 1525500692423508018

app = Flask(__name__)


@app.route("/")
def home():
    return "MonBotRoblox Online"


@app.route("/roblox/verify", methods=["POST"])
def roblox_verify():
    data = request.json or {}
    code = data.get("code")
    user_id = data.get("userId")
    username = data.get("username")

    if not code or not user_id or not username:
        return jsonify({"success": False, "status": "invalid_request"})

    if not check_code(code, username):
        return jsonify({
            "success": False,
            "status": "invalid_code",
            "message": "Code invalide ou expiré"
        })

    info = consume_code(code)

    return jsonify({
        "success": True,
        "status": "success",
        "message": "Compte lié avec succès",
        "discord_id": info["discord_id"]
    })


def lancer_serveur():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))


Thread(target=lancer_serveur, daemon=True).start()

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise RuntimeError("TOKEN manquant dans Render")

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


async def send_log(text):
    channel = bot.get_channel(BOT_LOG_CHANNEL)
    if channel:
        await channel.send(text)


@bot.event
async def on_message(message):
    await bot.process_commands(message)


@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("MonBotRoblox 🛡️"))
    await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
    await bot.tree.sync()
    logger.info(f"Connecté : {bot.user}")
    await send_log(f"🟢 Bot connecté\nVersion: {BOT_VERSION}")


@bot.tree.command(name="version", description="Version du bot")
async def version(interaction):
    await interaction.response.send_message(f"🤖 MonBotRoblox {BOT_VERSION}\n🐍 discord.py {discord.__version__}")


@bot.tree.command(name="verify", description="Vérifier un compte Roblox connecté au jeu")
@app_commands.describe(pseudo="Pseudo Roblox")
async def verify(interaction: discord.Interaction, pseudo: str):
    await interaction.response.defer(ephemeral=True)

    joueur = await get_user(pseudo)
    if not joueur:
        await interaction.followup.send("❌ Utilisateur Roblox introuvable")
        return

    code = create_code(interaction.user.id, joueur["name"])

    await interaction.followup.send(
        f"🎮 Vérification Roblox\n\nCompte : **{joueur['name']}**\nCode : **{code}**\n\nEntre ce code dans le jeu Roblox."
    )


bot.run(TOKEN)
