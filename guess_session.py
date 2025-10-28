import asyncio
import models

class GuessSession:
    def __init__(self, owner_id):
        self.owner_id = owner_id
        self.options = None
        self.players: dict[int, models.Player] = {}
        self.entries: dict[int, models.Entry] = {}
        self._lock = asyncio.Lock()

    async def score_guesses(self, entry: models.Entry, correct):
        async with self._lock:
            for guesser, guess in entry.guesses.items():
                if(guess == correct):
                    try:
                        self.players[guesser].score += 1
                    except:
                        pass

    async def increase_score(self, player, points):
        async with self._lock:
            try:
                self.players[player].score += points
            except:
                pass

    async def get_score(self):
        async with self._lock:
            players_list = list(self.players.values())
        players_list.sort(key=lambda p: p.score, reverse=True)
        return players_list
    
    async def find_entry(self, message_id):
        async with self._lock:
            return self.entries.get(message_id)