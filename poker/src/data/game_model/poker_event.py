from typing import Union
from data.game_model.event import Event
from data.game_model.mock_player import MockPlayer
from data.game_model.observer_player import ObserverPlayer


class PokerEvent:

    def __init__(self, player: Union[MockPlayer, ObserverPlayer],
                 event: Event, money: int, msg: str):
        self.player = player
        self.event: Event = event
        self.money: int = money
        self.message: str = msg

    def __str__(self) -> str:
        if self.event == Event.Fold or \
                self.event == Event.Check or \
                self.event == Event.Disconnected or \
                self.event == Event.Connected:
            return f'{self.player.name} {self.event}'

        elif self.event == Event.Call or \
                self.event == Event.Raise or \
                self.event == Event.Allin or \
                self.event == Event.Ante or \
                self.event == Event.SmallBlind or \
                self.event == Event.BigBlind or \
                self.event == Event.WinMoney or \
                self.event == Event.ReturnMoney:
            return f'{self.player.name} {self.event} {self.money}'

        elif self.event == Event.ChatMessage:
            return f'{self.player.name}: {self.message}'

        elif self.event == Event.ObserverChatMessage:
            return f'{self.player.name} [observer]: {self.message}'

        elif self.event == Event.FinishGame:
            return f'{self.player.name} {self.event} ' \
                   f'{self.message} and get {self.money / 100}'

        raise ValueError(f'Do not know how to interpret Event {self.event}')
