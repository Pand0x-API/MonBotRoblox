import os
import random
import string
from threading import Thread

import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask


# ======================
# Petit serveur pour Render
# ======================

app = Flask(__name__)

@app.route("/")
def accueil():
    return "Bot Discord en ligne"


def lancer_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


Thread(target=lancer_web, daemon=True).start()


# ======================
# Discord
# ======================

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise Exception("TOKEN manquant dans les variables Render")


intents = discord.Intents.default()
intents.guilds = True


bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


tickets = {}


def creer_id():
    chars = string.ascii_uppercase + string.digits

    return "-".join(
        "".join(random.choice(chars) for _ in range(4))
        for _ in range(3)
    )


@bot.event
async def on_ready():

    await bot.tree.sync()

    print("--------------------")
    print(f"Connecté : {bot.user}")
    print("Commandes synchronisées")
    print("--------------------")


# ======================
# TICKET
# ======================

@bot.tree.command(
    name="ticket",
    description="Créer un ticket support"
)
async def ticket(interaction: discord.Interaction):

    user = interaction.user
    guild = interaction.guild


    if user.id in tickets:

        await interaction.response.send_message(
            "❌ Tu as déjà un ticket.",
            ephemeral=True
        )
        return


    identifiant = creer_id()


    permissions = {

        guild.default_role:
        discord.PermissionOverwrite(
            view_channel=False
        ),

        user:
        discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True
        ),

        guild.me:
        discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True
        )
    }


    salon = await guild.create_text_channel(
        f"ticket-{identifiant}",
        overwrites=permissions
    )


    tickets[user.id] = salon.id


    embed = discord.Embed(
        title="🎫 Ticket ouvert",
        description=f"""
Bonjour {user.mention}

Un membre du staff va répondre.

ID :
`{identifiant}`

Fermer :
`/close`
""",
        color=discord.Color.blue()
    )


    await salon.send(embed=embed)


    await interaction.response.send_message(
        "✅ Ticket créé",
        ephemeral=True
    )



@bot.tree.command(
    name="close",
    description="Fermer le ticket"
)
async def close(interaction: discord.Interaction):

    if interaction.channel.id not in tickets.values():

        await interaction.response.send_message(
            "❌ Pas un ticket.",
            ephemeral=True
        )
        return


    await interaction.response.send_message(
        "🔒 Fermeture..."
    )


    for user, channel in list(tickets.items()):

        if channel == interaction.channel.id:
            del tickets[user]


    await interaction.channel.delete()



# ======================
# TEST
# ======================

@bot.tree.command(
    name="ping",
    description="Tester le bot"
)
async def ping(interaction: discord.Interaction):

    await interaction.response.send_message(
        "🏓 Pong !"
    )



bot.run(TOKEN)
