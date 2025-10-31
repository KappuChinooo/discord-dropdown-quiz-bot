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

    @nextcord.slash_command(name="start", description="Start a new guess scoring session")
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

    @nextcord.slash_command(name="create_guess", description="Creates a guess dropdown")
    async def create_guess(self,
                     interaction: Interaction,
                     title: str = SlashOption(description="Guess embed title", required=False, default=None) ):
        session: GuessSession = self.state_manager.get_session(interaction.channel.id)
        if(session is None):
            await interaction.response.send_message("This channel does not have an active session.", ephemeral=True)
            return
        if(interaction.user.id != session.owner_id):
            await interaction.response.send_message("You are not the owner of the channel's session.", ephemeral=True)
            return
        
        entry = models.Entry(session.options)

        embed = make_guess_embed(title=title)
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
        
        message_id = message.id
        entry = await session.find_entry(message_id)
        if(entry is None):
            await interaction.response.send_message("Message is not a guess entry.", ephemeral=True)
            return
        view = SelectAnswerView(entry)
        embed = make_answer_select_embed()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        await view.wait()
        if view.value is None:
            await interaction.followup.send("You didn’t select an answer in time.", ephemeral=True)
            return
        correct = view.value
        await session.score_guesses(entry, correct)
        print(f"{interaction.channel.id}: scored {message_id}")
        
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

    @nextcord.slash_command(name="add_player", description="Manually add a player into the session")
    async def add_player(self, 
                             interaction: Interaction, 
                             player: nextcord.User = SlashOption(description="Player to add", required=True), 
                             score: int = SlashOption(description="Points to give", required=False, default=0)):
        session: GuessSession = self.state_manager.get_session(interaction.channel.id)
        if(session is None):
            await interaction.response.send_message("This channel does not have an active session.", ephemeral=True)
            return
        if(interaction.user.id != session.owner_id):
            await interaction.response.send_message("You are not the owner of the channel's session.", ephemeral=True)
            return

        result = await session.add_player(player.id, player.name, score)
        if(result is None):
            await interaction.response.send_message("Player already exists.", ephemeral=True)
            return
        await interaction.response.send_message(f"Player **{result.name}** added.", ephemeral=True)

    @nextcord.slash_command(name="increase_score", description="Increase score of player by some points")
    async def increase_score(self, 
                             interaction: Interaction, 
                             player: nextcord.User = SlashOption(description="Player to increase score", required=True), 
                             points: int = SlashOption(description="Number of points to increase by", required=True)):
        session: GuessSession = self.state_manager.get_session(interaction.channel.id)
        if(session is None):
            await interaction.response.send_message("This channel does not have an active session.", ephemeral=True)
            return
        if(interaction.user.id != session.owner_id):
            await interaction.response.send_message("You are not the owner of the channel's session.", ephemeral=True)
            return

        result = await session.increase_score(player.id, points)
        if(result is None):
            await interaction.response.send_message("Player doesn't exist.", ephemeral=True)
            return
        await interaction.response.send_message(f"Score increased. **{result.name}** :{result.score}", ephemeral=True)

    @nextcord.slash_command(name="change_score", description="Change score of player to some points")
    async def change_score(self, 
                           interaction: Interaction, 
                           player: nextcord.User = SlashOption(description="Player to change score", required=True), 
                           points: int = SlashOption(description="Number of points to be set", required=True)):
        session: GuessSession = self.state_manager.get_session(interaction.channel.id)
        if(session is None):
            await interaction.response.send_message("This channel does not have an active session.", ephemeral=True)
            return
        if(interaction.user.id != session.owner_id):
            await interaction.response.send_message("You are not the owner of the channel's session.", ephemeral=True)
            return

        result = await session.change_score(player.id, points)
        if(result is None):
            await interaction.response.send_message("Player doesn't exist.", ephemeral=True)
            return
        await interaction.response.send_message("Score changed. **{result.name}** :{result.score}", ephemeral=True)

    @nextcord.slash_command(name="increment_score", description="Increase score of a player by 1")
    async def increment_score(self, 
                             interaction: Interaction, 
                             player: nextcord.User = SlashOption(description="Player to increment score", required=True)):
        session: GuessSession = self.state_manager.get_session(interaction.channel.id)
        if(session is None):
            await interaction.response.send_message("This channel does not have an active session.", ephemeral=True)
            return
        if(interaction.user.id != session.owner_id):
            await interaction.response.send_message("You are not the owner of the channel's session.", ephemeral=True)
            return

        result = await session.increase_score(player.id, 1)
        if(result is None):
            await interaction.response.send_message("Player doesn't exist.", ephemeral=True)
            return
        await interaction.response.send_message("Score incremented. **{result.name}** :{result.score}", ephemeral=True)

    @nextcord.slash_command(name="decrement_score", description="Decrease score of a player by 1")
    async def decrement_score(self, 
                             interaction: Interaction, 
                             player: nextcord.User = SlashOption(description="Player to decrement score", required=True)):
        session: GuessSession = self.state_manager.get_session(interaction.channel.id)
        if(session is None):
            await interaction.response.send_message("This channel does not have an active session.", ephemeral=True)
            return
        if(interaction.user.id != session.owner_id):
            await interaction.response.send_message("You are not the owner of the channel's session.", ephemeral=True)
            return

        result = await session.increase_score(player.id, -1)
        if(result is None):
            await interaction.response.send_message("Player doesn't exist.", ephemeral=True)
            return
        await interaction.response.send_message("Score decremented. **{result.name}** :{result.score}", ephemeral=True)

    @nextcord.slash_command(name="change_options", description="Change list of option for dropdowns")
    async def change_options(self, 
                             interaction: Interaction, 
                             choices: str = SlashOption(description="comma-separated choices to be used in the next guess", required=True)):
        session: GuessSession = self.state_manager.get_session(interaction.channel.id)
        if(session is None):
            await interaction.response.send_message("This channel does not have an active session.", ephemeral=True)
            return
        if(interaction.user.id != session.owner_id):
            await interaction.response.send_message("You are not the owner of the channel's session.", ephemeral=True)
            return
        
        options = [x.strip() for x in choices.split(",")]
        result = await session.change_options(options)
        if(result is None):
            await interaction.response.send_message("Options can not be nothing.", ephemeral=True)
        print(f"{interaction.channel.id}: Options changed to {options}")
        await interaction.response.send_message(f"Options changed to **{", ".join(options)}**.", ephemeral=True)


    @nextcord.slash_command(name="end", description="Ends the active scoring session in the current channel")
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
        
