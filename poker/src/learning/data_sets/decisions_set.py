from numpy import array
from typing import List
from learning.data_sets.base_poker_decision import BasePokerDecision


class DecisionsSet:
    def __init__(self):
        self._data: List[BasePokerDecision] = []

    def add(self, decision: BasePokerDecision) -> None:
        self._data += [decision]

    def get_data(self) -> array:
        arr = [d.to_array() for d in self._data]
        return array(arr)

    def get_answers(self) -> array:
        arr = [d.answer for d in self._data]
        return array(arr)
