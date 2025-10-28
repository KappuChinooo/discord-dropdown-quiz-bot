from nextcord.ext import commands
from nextcord import Interaction, SlashOption
import nextcord
from ui import SelectAnswerView, make_score_embed, make_guess_embed, GuessingView, make_answer_select_embed, make_show_answer_embed
from state import ChannelStateManager
from guess_session import GuessSession
import models

class dropdownGuessCog(commands.Cog):
    def __init__(self, bot, state_manager):
        self.bot = bot
        self.state_manager: ChannelStateManager = state_manager

    @nextcord.slash_command(name="start", description="Start a new guess scoring session.")
    async def start_session(self,
                         interaction: Interaction):
        channel_id = interaction.channel.id
        owner = interaction.user.id
        if(self.state_manager.get_session(channel_id=channel_id)):
            await interaction.response.send_message("This channel already has an active session.", ephemeral=True)
            return
        await self.state_manager.start_session(channel_id, owner)
        await interaction.response.send_message("Session started.", ephemeral=True)
        print(f"session started in {channel_id}")

    @nextcord.slash_command(name="create_guess", description="Creates a guess dropdown.")
    async def create_guess(self,
                     interaction: Interaction):
        session: GuessSession = self.state_manager.get_session(interaction.channel.id)
        if(session is None):
            await interaction.response.send_message("This channel does not have an active session.", ephemeral=True)
            return
        if(interaction.user.id != session.owner_id):
            await interaction.response.send_message("You are not the owner of the channel's session.", ephemeral=True)
            return
        
        entry = models.Entry(session.options)

        embed = make_guess_embed()
        view = GuessingView(session, entry)
        await interaction.response.send_message(embed=embed, view=view)
        print(f"guess created in {interaction.channel.id}")
        message = await interaction.original_message()
        session.entries[message.id] = entry


    @nextcord.message_command(name="Score this entry")
    async def score_entry(self, interaction: nextcord.Interaction, message: nextcord.Message):
        session = self.state_manager.get_session(interaction.channel.id)
        if(session is None):
            await interaction.response.send_message("This channel does not have an active session.", ephemeral=True)
            return
        if(interaction.user.id != session.owner_id):
            await interaction.response.send_message("You are not the owner of the channel's session.", ephemeral=True)
            return
        
        await interaction.response.defer()
        message_id = message.id
        entry = await session.find_entry(message_id)
        view = SelectAnswerView(entry)
        embed = make_answer_select_embed()
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)
        await view.wait()
        if view.value is None:
            await interaction.followup.send("You didn’t select an answer in time.", ephemeral=True)
            return
        correct = view.value
        await session.score_guesses(entry, correct)
        print(f"{interaction.channel.id}: scored {message_id}")
        await interaction.followup.send("Points scored.", ephemeral=True)
        
        embed = make_show_answer_embed(session, entry, correct)
        await interaction.followup.send(embed=embed)

        scores = await session.get_score()
        embed = make_score_embed(scores)
        await interaction.followup.send(embed=embed)



    @nextcord.slash_command(name="scoreboard", description="Sends currenct scoreboard")
    async def scoreboard(self, interaction: Interaction):
        session: GuessSession = self.state_manager.get_session(interaction.channel.id)
        if(session is None):
            await interaction.response.send_message("This channel does not have an active session.", ephemeral=True)
            return
        
        scores = await session.get_score()

        embed = make_score_embed(scores)
        await interaction.response.send_message(embed=embed)

    @nextcord.slash_command(name="increase_score", description="Increase score of player by some points.")
    async def increase_score(self, interaction: Interaction, user: nextcord.User, points: int):
        session: GuessSession = self.state_manager.get_session(interaction.channel.id)
        if(session is None):
            await interaction.response.send_message("This channel does not have an active session.", ephemeral=True)
            return
        if(interaction.user.id != session.owner_id):
            await interaction.response.send_message("You are not the owner of the channel's session.", ephemeral=True)
            return

        await session.increase_score(user.id, points)
        await interaction.response.send_message("Score increased.", ephemeral=True)

    @nextcord.slash_command(name="change_options", description="Change list of option for dropdowns. (comma split)")
    async def change_options(self, interaction: Interaction, choices: str):
        session: GuessSession = self.state_manager.get_session(interaction.channel.id)
        if(session is None):
            await interaction.response.send_message("This channel does not have an active session.", ephemeral=True)
            return
        if(interaction.user.id != session.owner_id):
            await interaction.response.send_message("You are not the owner of the channel's session.", ephemeral=True)
            return
        
        options = [x.strip() for x in choices.split(",")]
        session.options = options
        print(f"{interaction.channel.id}: Options changed to {options}")
        await interaction.response.send_message("Options changed.", ephemeral=True)


    @nextcord.slash_command(name="end", description="Ends the active scoring session in the current channel.")
    async def end(self, interaction: Interaction):
        session: GuessSession = self.state_manager.get_session(interaction.channel.id)
        if(session is None):
            await interaction.response.send_message("This channel does not have an active session.", ephemeral=True)
            return
        if(interaction.user.id != session.owner_id):
            await interaction.response.send_message("You are not the owner of the channel's session.", ephemeral=True)
            return
        
        self.start_session.end_session(interaction.channel.id)
        await interaction.response.send_message("Session Ended.", ephemeral=True)
        print(f"ended session in {interaction.channel.id}")
        
