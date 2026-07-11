import os
import random
import string
from threading import Thread

import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask
import aiohttp


# ==========================
# SERVEUR POUR RENDER
# ==========================

app = Flask(__name__)


@app.route("/")
def home():
    return "Ticket Bot Online"


def lancer_serveur():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


Thread(target=lancer_serveur, daemon=True).start()


# ==========================
# DISCORD
# ==========================

TOKEN = os.getenv("TOKEN")

if TOKEN is None:
    raise Exception("TOKEN manquant dans Render")


intents = discord.Intents.default()
intents.guilds = True
intents.members = True


bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


tickets = {}


def creer_id_ticket():

    caracteres = string.ascii_uppercase + string.digits

    return "-".join(
        "".join(random.choice(caracteres) for _ in range(4))
        for _ in range(3)
    )


# ==========================
# READY
# ==========================

@bot.event
async def on_ready():

    await bot.tree.sync()

    print("---------------------")
    print(f"Connecté : {bot.user}")
    print("Commandes synchronisées")
    print("---------------------")



# ==========================
# PING
# ==========================

@bot.tree.command(
    name="ping",
    description="Tester le bot"
)
async def ping(interaction):

    await interaction.response.send_message(
        f"🏓 Pong ! {round(bot.latency * 1000)}ms"
    )



# ==========================
# TICKET
# ==========================

@bot.tree.command(
    name="ticket",
    description="Créer un ticket privé"
)
async def ticket(interaction):

    user = interaction.user
    guild = interaction.guild


    if user.id in tickets:

        await interaction.response.send_message(
            "❌ Tu as déjà un ticket.",
            ephemeral=True
        )
        return


    nom = "ticket-" + creer_id_ticket()


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
        nom,
        overwrites=permissions
    )


    tickets[user.id] = salon.id


    embed = discord.Embed(
        title="🎫 Ticket ouvert",
        description=f"""
Bonjour {user.mention}

Le support va répondre.

Pour fermer :
/close
""",
        color=discord.Color.blue()
    )


    await salon.send(embed=embed)


    await interaction.response.send_message(
        "✅ Ticket créé",
        ephemeral=True
    )



# ==========================
# CLOSE
# ==========================

@bot.tree.command(
    name="close",
    description="Fermer le ticket"
)
async def close(interaction):

    if interaction.channel.id not in tickets.values():

        await interaction.response.send_message(
            "❌ Ce n'est pas un ticket.",
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



# ==========================
# ROBLOX VERIFY
# ==========================

@bot.tree.command(
    name="verify",
    description="Lier ton compte Roblox"
)
@app_commands.describe(
    pseudo="Ton pseudo Roblox"
)
async def verify(
    interaction: discord.Interaction,
    pseudo: str
):

    await interaction.response.defer(ephemeral=True)


    url = (
        "https://users.roblox.com/v1/users/search"
        f"?keyword={pseudo}&limit=1"
    )


    async with aiohttp.ClientSession() as session:

        async with session.get(url) as response:

            data = await response.json()



    if not data.get("data"):

        await interaction.followup.send(
            "❌ Joueur Roblox introuvable."
        )
        return



    joueur = data["data"][0]


    role = discord.utils.get(
        interaction.guild.roles,
        name="Verified Player"
    )


    if role:

        await interaction.user.add_roles(role)


    await interaction.followup.send(
        f"✅ Compte Roblox lié : **{joueur['name']}**"
    )



# ==========================

bot.run(TOKEN)
