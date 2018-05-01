from data.game_model.event import Event


class PlayerEvent:

    def __init__(self, event: Event, money: int):
        self.event: Event = event
        self.money: int = money

    def __str__(self) -> str:
        return f'{self.event} {self.money}'
