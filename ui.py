from nextcord import ui, Interaction, SelectOption, Embed
import models

COLOR = 0x2ab4f2

class GuessingView(ui.View):
    def __init__(self, entry: models.Entry):
        super().__init__(timeout=None)
        self.add_item(self.GuessDropdown(entry, entry.options))
        self.entry = entry

    class GuessDropdown(ui.Select): 
        def __init__(self, entry, options_list):
            self.entry: models.Entry = entry
            options = [
                SelectOption(label=f"{item}", value=str(item))
                for item in options_list
            ]

            super().__init__(placeholder="Guess the owner...", min_values=1, max_values=1, options=options)

        async def callback(self, interaction: Interaction):
            player_id = interaction.user.id
            player_name = interaction.user.name
            owner_guess = int(self.values[0])

            self.entry.guesses[player_id] = owner_guess

class SelectAnswerView(ui.View):
    def __init__(self, entry: models.Entry):
        super().__init__("Select Correct Answer", timeout=60)
        self.value = None
        self.add_item(self.AnswerChoice(entry))

    class AnswerChoice(ui.Select):
        def __init__(self, entry: models.Entry):
            super().__init__(placeholder="Select correct answer", options=entry.options)

            async def callback(self, interaction: Interaction):
                self.view.value = self.values[0]
                self.view.stop()

def make_score_embed(score_list: list[models.Player]):
    embed = Embed(title="Scores:", color=COLOR)
    embed.description = "\n".join(f"**{player.name}:** {player.score}" for player in score_list)
    return embed

def make_guess_embed():
    embed = Embed(title="Select your guess", color=COLOR)
    return embed