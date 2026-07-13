import os
import random
import string
from threading import Thread

import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask

from logger import logger
from roblox import get_user
from ai_moderation import analyze_message


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


async def moderate_message(message):
    if message.author.bot:
        return

    result = await analyze_message(message.content)
    risk = result.get("risk", 0)
    action = result.get("action", "none")

    if risk >= 400:
        logger.warning(
            f"Human review required | {message.author} | {result}"
        )
        return

    if action == "warning":
        await message.reply("⚠️ Attention : comportement suspect détecté.")

    elif action == "mute":
        try:
            await message.author.timeout(
                discord.utils.utcnow() + discord.timedelta(minutes=10),
                reason="AI anti-spam detection"
            )
        except Exception as e:
            logger.exception(e)


@bot.event
async def on_message(message):
    await moderate_message(message)
    await bot.process_commands(message)


def creer_id_ticket():
    chars = string.ascii_uppercase + string.digits
    return "-".join("".join(random.choice(chars) for _ in range(4)) for _ in range(3))


@bot.event
async def on_ready():
    try:
        await bot.tree.sync()
        logger.info(f"Connecté : {bot.user}")
    except Exception as e:
        logger.exception(e)


@bot.event
async def on_error(event, *args, **kwargs):
    logger.exception(f"Erreur Discord : {event}")


@bot.tree.command(name="ping", description="Tester le bot")
async def ping(interaction):
    await interaction.response.send_message(
        f"🏓 Pong ! {round(bot.latency * 1000)}ms"
    )


@bot.tree.command(name="status", description="Etat du bot")
async def status(interaction):
    await interaction.response.send_message(
        f"✅ Online\nPing: {round(bot.latency * 1000)}ms"
    )


@bot.tree.command(name="ticket", description="Créer un ticket privé")
async def ticket(interaction):
    user = interaction.user
    guild = interaction.guild

    if user.id in tickets:
        await interaction.response.send_message("❌ Tu as déjà un ticket.", ephemeral=True)
        return

    permissions = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
    }

    channel = await guild.create_text_channel(
        "ticket-" + creer_id_ticket(),
        overwrites=permissions
    )

    tickets[user.id] = channel.id
    await channel.send(f"🎫 Ticket ouvert pour {user.mention}\nUtilise /close pour fermer.")
    await interaction.response.send_message("✅ Ticket créé", ephemeral=True)


@bot.tree.command(name="close", description="Fermer un ticket")
async def close(interaction):
    if interaction.channel.id not in tickets.values():
        await interaction.response.send_message("❌ Pas un ticket.", ephemeral=True)
        return

    await interaction.response.send_message("🔒 Fermeture...")

    for user, channel in list(tickets.items()):
        if channel == interaction.channel.id:
            del tickets[user]

    await interaction.channel.delete()


@bot.tree.command(name="verify", description="Lier un compte Roblox")
@app_commands.describe(pseudo="Pseudo Roblox")
async def verify(interaction: discord.Interaction, pseudo: str):
    await interaction.response.defer(ephemeral=True)

    try:
        joueur = await get_user(pseudo)
    except Exception as e:
        logger.exception(e)
        await interaction.followup.send("❌ Erreur Roblox")
        return

    if not joueur:
        await interaction.followup.send("❌ Joueur Roblox introuvable")
        return

    role = discord.utils.get(interaction.guild.roles, name="Verified Player")
    if role:
        await interaction.user.add_roles(role)

    await interaction.followup.send(
        f"✅ Compte Roblox lié : **{joueur['name']}**"
    )


bot.run(TOKEN)
