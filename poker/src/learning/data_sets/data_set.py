from __future__ import annotations
from pickle import load, dump
from os.path import exists
from os import mkdir
from learning.data_sets.decision_model.base_poker_decision import BasePokerDecision, DecisionClass
from learning.data_sets.decisions_set import DecisionsSet
from data.game_model.poker_hand import PokerHand
from data.game_model.poker_game import PokerGame
from special.debug import Debug


class DataSet:

    dataset_folder = 'datasets'

    def __init__(self, cls: DecisionClass):
        self.cls: DecisionClass = cls
        self.obj: BasePokerDecision = self.cls()
        self.decisions: DecisionsSet = DecisionsSet()

    def add_data_from_hand(self, game: PokerGame, hand: PokerHand) -> None:
        data = self.obj.get_decisions(game, hand)
        self.decisions.add_many(data)

    def add_data_from_game(self, game: PokerGame) -> None:
        Debug.learning('Start eject data from game', game.name)
        for hand in game.hands:
            self.add_data_from_hand(game, hand)

    def add_data_from_folder(self, path: str) -> None:
        for game in PokerGame.load_dir_gen(path):
            self.add_data_from_game(game)

    def save(self, path) -> None:
        if not exists(DataSet.dataset_folder):
            mkdir(DataSet.dataset_folder)
        dump(self, open(DataSet.dataset_folder + '/' + path, 'wb'))

    @staticmethod
    def load(path) -> DataSet:
        return load(open(DataSet.dataset_folder + '/' + path, 'rb'))
