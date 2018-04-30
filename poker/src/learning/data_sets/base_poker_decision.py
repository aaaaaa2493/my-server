from numpy import array
from typing import List
from data.game_model.poker_hand import PokerHand


class BasePokerDecision:

    def __init__(self):
        self.answer: float = 0

    def to_array(self) -> array:
        raise NotImplementedError('to array')

    @staticmethod
    def get_decisions(hand: PokerHand) -> List['BasePokerDecision']:
        raise NotImplementedError('get_decisions')
