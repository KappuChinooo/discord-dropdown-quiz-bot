# Discord dropdown guessing bot

### Description
A Discord bot for interactive guessing games/quizzes using dropdowns. Players can submit guesses, and the bot can automatically score responses, show results, and maintain a scoreboard.

---

## Commands

### Slash Commands

| Command | Description |
|---------|-------------|
| `/start` | Start a new guess scoring session in the current channel. |
| `/create_guess` | Creates a guess dropdown for players to select their answer. |
| `/scoreboard` | Shows the current scoreboard. |
| `/increase_score <user> <points>` | Increases a player's score by the specified points. |
| `/change_score <user> <points>` | Change a player's score to some amount of points. |
| `/change_options <choices>` | Change the dropdown options (comma-separated). |
| `/end` | Ends the active scoring session in the current channel. |

### Message Commands (Context Menu)

| Command | Description |
|---------|-------------|
| `Score this entry` | Used on a guess message to select the correct answer and score players. |

---

## Example Flow

1. Start a session in a channel: `/start`
2. Change options (if needed): `/change_options Apple, Banana, Orange`
3. Create a guess dropdown: `/create_guess`
4. Players select their guesses.
5. Score entries using the context menu: `Score this entry`
6. Select the correct answer(s) from the 
6. View the results and scoreboard: `/scoreboard`
7. End the session: `/end`

---

## Installation & Setup

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/discord-dropdown-guessing.git
    cd discord-dropdown-guessing
    ```

2. Install dependencies:

    ```bash
    pip install -U nextcord python-dotenv
    ```

3. Create a bot on the [Discord Developer Portal](https://discord.com/developers/applications), copy the token.

4. Create a `.env` file in the root directory:

    ```text
    DISCORD_TOKEN=your_bot_token_here
    ```

    GUILD_ID can also be entered for commands refresh on that guild

---

## Running the Bot

```bash
python bot.py