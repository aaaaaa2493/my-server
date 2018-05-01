from numpy import array
from typing import List, Callable
from enum import Enum
from data.game_model.poker_hand import PokerHand
from data.game_model.poker_game import PokerGame


class Answer(Enum):
    pass


class BasePokerDecision:

    def __init__(self):
        self._answer: Answer = 0

    def get_answer(self) -> int:
        return self._answer.value

    def set_answer(self, ans: Answer) -> None:
        self._answer = ans

    def to_array(self) -> array:
        raise NotImplementedError('to array')

    @staticmethod
    def get_decisions(game: PokerGame, hand: PokerHand) -> List['BasePokerDecision']:
        raise NotImplementedError('get_decisions')


DecisionClass = Callable[..., BasePokerDecision]
