from __future__ import annotations
from numpy import array
from typing import List, Callable
from learning.data_sets.decision_model.base_poker_decision_answer import BasePokerDecisionAnswer
from data.game_model.poker_hand import PokerHand
from data.game_model.poker_game import PokerGame


class BasePokerDecision:

    def __init__(self):
        self._answer: BasePokerDecisionAnswer = 0

    def get_answer(self) -> int:
        return self._answer.value

    def set_answer(self, ans: BasePokerDecisionAnswer) -> None:
        self._answer = ans

    def to_array(self) -> array:
        raise NotImplementedError('to array')

    @staticmethod
    def initialize(game: PokerGame, hand: PokerHand) -> None:
        pass

    @staticmethod
    def get_decisions(game: PokerGame, hand: PokerHand) -> List[BasePokerDecision]:
        raise NotImplementedError('get_decisions')


DecisionClass = Callable[..., BasePokerDecision]
