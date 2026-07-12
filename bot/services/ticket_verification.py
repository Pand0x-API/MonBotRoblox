import discord


class RobloxVerificationView(discord.ui.View):
    """Bouton de verification Roblox pour les tickets Discord."""

    def __init__(self, verification_service):
        super().__init__(timeout=300)
        self.verification_service = verification_service

    @discord.ui.button(
        label="🔗 Vérifier mon compte Roblox",
        style=discord.ButtonStyle.primary,
        custom_id="verify_roblox"
    )
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        code = self.verification_service.create_code(interaction.user.id)

        await interaction.response.send_message(
            "🔐 **Début de la vérification Roblox**\n\n"
            f"Ton code temporaire : `{code}`\n\n"
            "Utilise ce code dans le jeu Roblox pour confirmer que tu possèdes bien le compte.",
            ephemeral=True
        )
