import os
from datetime import timedelta
from threading import Thread

import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask

from logger import logger
from roblox import get_user
from ai_moderation import analyze_message
from database import add_risk, add_warning, add_mute

BOT_VERSION = "1.3.1"
BOT_LOG_CHANNEL = 1525582433775390830
GUILD_ID = 1525500692423508018

app = Flask(__name__)


@app.route("/")
def home():
    return "MonBotRoblox Online"


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


async def moderate_message(message):
    if message.author.bot or not message.content:
        return

    try:
        result = await analyze_message(message.content)
        risk = int(result.get("risk", 0))
        reason = result.get("reason", "Analyse IA")
        total = add_risk(message.author.id, risk, reason)

        if total >= 400:
            await send_log(f"🚨 Vérification humaine\n{message.author.mention}\nScore: {total}\nRaison: {reason}")
        elif total >= 300:
            await message.author.timeout(timedelta(minutes=10), reason="Score anti-spam élevé")
            add_mute(message.author.id)
            await send_log(f"🔇 Mute automatique {message.author.mention} Score: {total}")
        elif total >= 100:
            add_warning(message.author.id)
            await message.reply(f"⚠️ Avertissement automatique ({total}/500)")

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

    try:
        # Synchronisation serveur (rapide)
        guild = discord.Object(id=GUILD_ID)
        guild_commands = await bot.tree.sync(guild=guild)

        # Synchronisation globale (pour que les commandes apparaissent partout)
        global_commands = await bot.tree.sync()

        logger.info(f"Connecté : {bot.user}")
        logger.info(f"Commandes serveur: {len(guild_commands)} | globales: {len(global_commands)}")

        await send_log(
            f"🟢 Bot connecté\n"
            f"Version: {BOT_VERSION}\n"
            f"Commandes serveur: {len(guild_commands)}\n"
            f"Commandes globales: {len(global_commands)}"
        )
    except Exception as e:
        logger.exception(e)


@bot.tree.command(name="version", description="Version du bot")
async def version(interaction):
    await interaction.response.send_message(
        f"🤖 MonBotRoblox {BOT_VERSION}\n🐍 discord.py {discord.__version__}"
    )


@bot.tree.command(name="ping", description="Ping du bot")
async def ping(interaction):
    await interaction.response.send_message(f"🏓 {round(bot.latency * 1000)}ms")


@bot.tree.command(name="verify", description="Vérifier Roblox")
@app_commands.describe(pseudo="Pseudo Roblox")
async def verify(interaction: discord.Interaction, pseudo: str):
    await interaction.response.defer(ephemeral=True)
    joueur = await get_user(pseudo)

    if not joueur:
        await interaction.followup.send("❌ Joueur introuvable")
        return

    await interaction.followup.send(f"✅ Compte lié : {joueur['name']}")


bot.run(TOKEN)
