class Player:
    def __init__(self, name, score = 0):
        self.name: str = name
        self.score: int = score


class Entry:
    def __init__(self, options):
        self.options: list[str] = options
        self.guesses: dict[int, str] = {}