from numpy import array
from typing import List
from data.game_model.poker_hand import PokerHand
from learning.data_sets.base_poker_decision import BasePokerDecision


class PokerDecision(BasePokerDecision):
    def __init__(self):
        super().__init__()
        self.probability_to_win: float = 0
        self.my_money: int = 0
        self.money_in_pot: int = 0
        self.money_to_call: int = 0

    def to_array(self) -> array:
        arr = [
            self.probability_to_win,
            self.money_in_pot / self.money_in_pot,
            self.my_money / self.money_in_pot,
            self.money_in_pot / self.money_in_pot,
        ]
        return array(arr)

    @staticmethod
    def get_decisions(hand: PokerHand) -> List[BasePokerDecision]:
        print(hand)
        return [PokerDecision()]
