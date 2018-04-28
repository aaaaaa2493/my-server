from enum import Enum
from typing import Dict
from holdem.play.result import Result


class Event(Enum):
    Fold = 0
    Call = 1
    Check = 2
    Raise = 3
    Allin = 4
    Ante = 5
    SmallBlind = 6
    BigBlind = 7
    WinMoney = 8
    ReturnMoney = 9
    ChatMessage = 10
    ObserverChatMessage = 11
    Disconnected = 12
    Connected = 13
    FinishGame = 14

    def __str__(self) -> str:
        return _to_str[self]

    def to_result(self) -> Result:
        return _to_result[self]


_to_result: Dict[Event, Result] = {
    Event.Fold: Result.Fold,
    Event.Check: Result.Check,
    Event.Call: Result.Call,
    Event.Raise: Result.Raise,
    Event.Allin: Result.Allin
}

_to_str: Dict[Event, str] = {
    Event.Fold: 'fold',
    Event.Call: 'call',
    Event.Check: 'check',
    Event.Raise: 'raise',
    Event.Allin: 'all in',
    Event.Ante: 'ante',
    Event.SmallBlind: 'sb',
    Event.BigBlind: 'bb',
    Event.WinMoney: 'win',
    Event.ReturnMoney: 'return',
    Event.ChatMessage: 'chat message',
    Event.ObserverChatMessage: 'observer message',
    Event.Disconnected: 'disconnected',
    Event.Connected: 'connected',
    Event.FinishGame: 'finished'
}
