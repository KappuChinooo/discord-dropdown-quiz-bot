from nextcord import ui, Interaction, SelectOption, Embed, Message
import models
from guess_session import GuessSession

COLOR = 0x2ab4f2

class GuessingView(ui.View):
    def __init__(self, session, entry: models.Entry):
        super().__init__(timeout=None)
        self.session = session
        self.entry = entry
        self.add_item(self.GuessDropdown(session, entry, entry.options))

    class GuessDropdown(ui.Select): 
        def __init__(self, session, entry, options_list):
            self.session: GuessSession = session
            self.entry: models.Entry = entry
            options = [
                SelectOption(label=f"{item}", value=str(item))
                for item in options_list
            ]

            super().__init__(placeholder="Guess the owner...", min_values=1, max_values=(len(options_list) if self.session.multiple_guesses else 1), options=options)

        async def callback(self, interaction: Interaction):
            player_id = interaction.user.id
            player_name = interaction.user.name
            guess = self.values

            if(player_id not in self.session.players):
                await self.session.add_player(player_id, player_name)
            self.entry.guesses[player_id] = guess
            print(f"{interaction.channel.id}: {player_name} - {", ".join(guess)}")
            names = [self.session.players[id].name for id in self.entry.guesses.keys()]
            message = interaction.message
            title = message.embeds[0].title
            embed = make_guess_embed(guessed_list=names, title=title)
            await interaction.response.edit_message(embed=embed)

class SelectAnswerView(ui.View):
    def __init__(self, entry: models.Entry):
        super().__init__(timeout=60)
        self.value = None
        self.add_item(self.AnswerChoice(entry))

    class AnswerChoice(ui.Select):
        def __init__(self, entry: models.Entry):
            options = [
                SelectOption(label=f"{item}", value=str(item))
                for item in entry.options
            ]
            super().__init__(placeholder="Select correct answer", options=options, min_values=1, max_values=len(options))

        async def callback(self, interaction: Interaction):
            self.view.value = self.values
            print(f"{self.view.value} selected as correct")
            self.view.stop()

def make_score_embed(score_list: list[models.Player]):
    embed = Embed(title="Scores", color=COLOR)
    embed.description = "\n".join(f"**{player.name}:** {player.score}" for player in score_list)
    return embed

def make_guess_embed(guessed_list = None, title = None):
    if(title is None):
        title = "Select your guess"
    embed = Embed(title=title, color=COLOR)
    if(guessed_list):
        embed.description = "\n".join(f"**{player}** submitted" for player in guessed_list)
    return embed

def make_answer_select_embed():
    embed = Embed(title="Select the correct answer", color=COLOR)
    return embed

def make_show_answer_embed(session, entry, correct):
    embed = Embed(title="Answers", color=COLOR)
    names = {id: session.players[id].name for id in entry.guesses.keys()}
    correct_dict = {}
    for id, guesses in entry.guesses.items():
        correct_dict[id] = [(guess in correct) for guess in guesses]

    lines = []
    for id, guesses in entry.guesses.items():
        formatted_guesses = [
            f"**{guess}**" if correct_dict[id][i] else guess
            for i, guess in enumerate(guesses)
        ]
        lines.append(f"**{names[id]}** | {', '.join(formatted_guesses)}")

    embed.description = (
        f"**Correct Answers:** {', '.join(f'**{c}**' for c in correct)}\n\n" +
        "\n".join(lines)
    )
    return embed