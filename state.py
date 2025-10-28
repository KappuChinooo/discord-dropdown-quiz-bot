import asyncio 
from guess_session import GuessSession

class ChannelStateManager:
    def __init__(self):
        self.active_sessions = {}
        self._lock = asyncio.Lock()

    async def start_session(self, channel_id, owner_id):
        async with self._lock:
            if(channel_id in self.active_sessiosn):
                raise ValueError("Channel already has an active game.")
            game = GuessSession(owner_id)
            self.active_sessions[channel_id] = game
            return game
        
    async def end_session(self, channel_id):
        async with self._lock:
            if(channel_id in self.active_sessions):
                del self.active_sessions[channel_id]

    def get_session(self, channel_id):
        return self.active_sessions.get(channel_id)