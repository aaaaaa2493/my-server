from numpy import array
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
            self.money_in_pot / self.money_to_call,
            self.my_money / self.money_to_call,
            self.money_in_pot / self.money_to_call,
        ]
        return array(arr)
