class Player:
    def __init__(self, name):
        self.name: str = name
        self.score: int = 0


class Entry:
    def __init__(self, options):
        self.options: list[str] = options
        self.guesses: dict[int, str] = None