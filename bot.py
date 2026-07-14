import os
from threading import Thread

import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask, request, jsonify

from logger import logger
from roblox import get_user, get_user_by_id
from verification import create_code, check_code, consume_code

BOT_VERSION = "1.7.0"
BOT_LOG_CHANNEL = 1525582433775390830
GUILD_ID = 1525500692423508018

VERIFIED_ROLE_ID = 1525621386884944065
OWNER_ROLE_ID = 1525820770167554078

BOOST_ROLES = {
    1: 1526586093934350469,
    5: 1526588739743125514,
    10: 1526588881779163246
}

app = Flask(__name__)

@app.route("/")
def home():
    return "MonBotRoblox Online"

@app.route("/roblox/verify", methods=["POST"])
def roblox_verify():
    data = request.json or {}
    code = data.get("code")
    username = data.get("username")

    if not code or not username or not check_code(code, username):
        return jsonify({"success": False, "status": "invalid_code"})

    info = consume_code(code)
    return jsonify({"success": True, "status": "success", "discord_id": info["discord_id"]})


def lancer_serveur():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

Thread(target=lancer_serveur, daemon=True).start()

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise RuntimeError("TOKEN manquant")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

async def send_log(text):
    channel = bot.get_channel(BOT_LOG_CHANNEL)
    if channel:
        await channel.send(text)


def is_owner(member):
    return any(role.id == OWNER_ROLE_ID for role in member.roles)


@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(f"MonBotRoblox v{BOT_VERSION}"))
    await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
    await bot.tree.sync()
    logger.info(f"Connecté : {bot.user}")
    await send_log(f"🟢 Bot connecté\nVersion: {BOT_VERSION}")


@bot.tree.command(name="version", description="Informations du bot")
async def version(interaction):
    embed = discord.Embed(title="🤖 MonBotRoblox")
    embed.add_field(name="Version", value=BOT_VERSION)
    embed.add_field(name="discord.py", value=discord.__version__)
    embed.add_field(name="Fonctions", value="Roblox + Modération + Boost + Tests")
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="testboost", description="Tester les rôles boost (Owner uniquement)")
@app_commands.describe(niveau="Nombre de boosts simulés: 1, 5 ou 10")
async def testboost(interaction, niveau: int):
    if not is_owner(interaction.user):
        await interaction.response.send_message("❌ Commande réservée aux Owners", ephemeral=True)
        return

    if niveau not in BOOST_ROLES:
        await interaction.response.send_message("❌ Utilise 1, 5 ou 10", ephemeral=True)
        return

    role = interaction.guild.get_role(BOOST_ROLES[niveau])
    if role:
        await interaction.user.add_roles(role)
        await interaction.response.send_message(f"🚀 Test boost {niveau} réussi : {role.name}")


@bot.tree.command(name="removeboosttest", description="Retirer les rôles boost de test")
async def removeboosttest(interaction):
    if not is_owner(interaction.user):
        await interaction.response.send_message("❌ Commande réservée aux Owners", ephemeral=True)
        return

    for role_id in BOOST_ROLES.values():
        role = interaction.guild.get_role(role_id)
        if role:
            await interaction.user.remove_roles(role)

    await interaction.response.send_message("✅ Rôles boost de test retirés")


@bot.tree.command(name="ping", description="Ping du bot")
async def ping(interaction):
    await interaction.response.send_message(f"🏓 {round(bot.latency * 1000)}ms")


@bot.tree.command(name="verify", description="Vérifier un compte Roblox")
@app_commands.describe(compte="Pseudo Roblox ou ID Roblox")
async def verify(interaction, compte: str):
    await interaction.response.defer(ephemeral=True)

    joueur = await get_user_by_id(int(compte)) if compte.isdigit() else await get_user(compte)

    if not joueur:
        await interaction.followup.send("❌ Compte Roblox introuvable")
        return

    code = create_code(interaction.user.id, joueur["name"])
    await interaction.followup.send(f"🎮 Compte: {joueur['name']}\nID: {joueur['id']}\nCode: {code}")


bot.run(TOKEN)
