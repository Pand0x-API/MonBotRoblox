import os
import random
import string
from datetime import timedelta
from threading import Thread

import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask

from logger import logger
from roblox import get_user
from ai_moderation import analyze_message

BOT_VERSION = "1.2.0"
BOT_LOG_CHANNEL = 1525582433775390830
GUILD_ID = 1525500692423508018

app = Flask(__name__)

@app.route("/")
def home():
    return "MonBotRoblox Online"


def lancer_serveur():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

Thread(target=lancer_serveur, daemon=True).start()

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise RuntimeError("TOKEN manquant dans Render")

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
tickets = {}


async def send_log(text):
    channel = bot.get_channel(BOT_LOG_CHANNEL)
    if channel:
        await channel.send(text)


async def moderate_message(message):
    if message.author.bot or not message.content:
        return

    result = await analyze_message(message.content)
    risk = int(result.get("risk", 0))
    action = result.get("action", "none")

    if risk >= 400:
        await send_log(f"🚨 Vérification humaine requise\nUtilisateur: {message.author.mention}\nScore: {risk}\nRaison: {result.get('reason')}")
        return

    if action == "warning":
        await message.reply("⚠️ Comportement suspect détecté.")

    elif action == "mute":
        try:
            await message.author.timeout(timedelta(minutes=10), reason="AI anti-spam detection")
            await send_log(f"🔇 Mute automatique\nUtilisateur: {message.author.mention}\nScore: {risk}")
        except Exception as e:
            logger.exception(e)


@bot.event
async def on_message(message):
    await moderate_message(message)
    await bot.process_commands(message)


@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game("MonBotRoblox 🛡️")
    )

    guild = discord.Object(id=GUILD_ID)
    await bot.tree.sync(guild=guild)

    logger.info(f"Connecté : {bot.user}")
    await send_log(f"🟢 Bot connecté\nVersion: {BOT_VERSION}\nDiscord.py: {discord.__version__}")


@bot.tree.command(name="version", description="Voir la version du bot")
async def version(interaction):
    await interaction.response.send_message(f"🤖 MonBotRoblox\n📦 Version: {BOT_VERSION}\n🐍 discord.py: {discord.__version__}")


@bot.tree.command(name="ping", description="Tester le bot")
async def ping(interaction):
    await interaction.response.send_message(f"🏓 {round(bot.latency * 1000)}ms")


@bot.tree.command(name="status", description="Etat du bot")
async def status(interaction):
    await interaction.response.send_message("✅ Online")


@bot.tree.command(name="verify", description="Lier un compte Roblox")
@app_commands.describe(pseudo="Pseudo Roblox")
async def verify(interaction: discord.Interaction, pseudo: str):
    await interaction.response.defer(ephemeral=True)
    joueur = await get_user(pseudo)

    if not joueur:
        await interaction.followup.send("❌ Joueur Roblox introuvable")
        return

    role = discord.utils.get(interaction.guild.roles, name="Verified Player")
    if role:
        await interaction.user.add_roles(role)

    await interaction.followup.send(f"✅ Compte Roblox lié : {joueur['name']}")


bot.run(TOKEN)
