import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import os
import json
import random
import string


TOKEN = os.getenv("TOKEN")

API_URL = "https://monbotroblox.onrender.com"

LOG_CHANNEL_ID = 1525582433775390830

ROLE_NAME = "Verified Player"


intents = discord.Intents.default()
intents.guilds = True
intents.members = True


bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


tickets = {}

DATABASE = "users.json"


def load_users():

    if not os.path.exists(DATABASE):
        return {}

    with open(DATABASE, "r") as f:
        return json.load(f)



def save_users(data):

    with open(DATABASE, "w") as f:
        json.dump(data, f, indent=4)



users = load_users()



def create_ticket_id():

    chars = string.ascii_letters + string.digits

    return "-".join(
        "".join(random.choice(chars) for _ in range(4))
        for _ in range(4)
    )



async def log(message):

    channel = bot.get_channel(LOG_CHANNEL_ID)

    if channel:

        embed = discord.Embed(
            title="📋 Logs",
            description=message,
            color=discord.Color.blue()
        )

        await channel.send(embed=embed)



@bot.event
async def on_ready():

    await bot.tree.sync()

    print(f"✅ Connecté : {bot.user}")
    print("✅ Commandes synchronisées")



@bot.tree.command(
    name="ticket",
    description="Créer un ticket privé"
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


    identifiant = create_ticket_id()


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
            view_channel=True
        )
    }


    salon = await guild.create_text_channel(
        f"ticket-{identifiant}",
        overwrites=permissions
    )


    tickets[user.id] = salon.id


    await salon.send(
        f"🎫 Ticket ouvert\n\nID : `{identifiant}`\n\nBonjour {user.mention}"
    )


    await interaction.response.send_message(
        "✅ Ticket créé.",
        ephemeral=True
    )



@bot.tree.command(
    name="close",
    description="Fermer le ticket"
)
async def close(interaction: discord.Interaction):

    if interaction.channel.id not in tickets.values():

        await interaction.response.send_message(
            "❌ Ce n'est pas un ticket.",
            ephemeral=True
        )

        return


    await interaction.response.send_message(
        "🔒 Fermeture..."
    )


    await interaction.channel.delete()



@bot.tree.command(
    name="verify",
    description="Lier un compte Roblox"
)
@app_commands.describe(
    pseudo="Pseudo Roblox"
)
async def verify(
    interaction: discord.Interaction,
    pseudo:str
):

    await interaction.response.defer(
        ephemeral=True
    )


    data = {

        "discord_id": str(interaction.user.id),

        "roblox_username": pseudo

    }


    async with aiohttp.ClientSession() as session:

        async with session.post(
            API_URL + "/verify",
            json=data
        ) as response:

            result = await response.json()



    if result.get("success"):


        role = discord.utils.get(
            interaction.guild.roles,
            name=ROLE_NAME
        )


        if role:

            await interaction.user.add_roles(role)



        users[str(interaction.user.id)] = result

        save_users(users)



        await interaction.followup.send(
            "✅ Roblox vérifié !",
            ephemeral=True
        )

    else:

        await interaction.followup.send(
            "❌ Vérification impossible.",
            ephemeral=True
        )



@bot.tree.command(
    name="profil",
    description="Voir ton profil Roblox"
)
async def profil(interaction: discord.Interaction):

    data = users.get(
        str(interaction.user.id)
    )


    if not data:

        await interaction.response.send_message(
            "❌ Aucun compte lié.",
            ephemeral=True
        )

        return


    await interaction.response.send_message(
        f"🎮 Roblox : {data.get('username')}",
        ephemeral=True
    )



bot.run(TOKEN)
