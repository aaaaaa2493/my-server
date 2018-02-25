
from re import compile
from datetime import datetime, timedelta
from calendar import month_name
from functools import lru_cache
from os import listdir, mkdir, makedirs, remove
from os.path import exists
from shutil import rmtree
from pickle import load, dump
from random import shuffle, random, choice, uniform, randint
from statistics import mean
from threading import Thread, Lock
from time import sleep
from typing import List, Dict, Tuple, Optional, Iterator, Union
from websocket import create_connection
from json import loads, dumps
from copy import deepcopy

from special.debug import Debug
from core.card import Card
from holdem.cards_pair import CardsPair
from holdem.holdem_poker import HoldemPoker as Poker, Hand
from core.deck import Deck
from learning.neural import Neural
from holdem.base_play import BasePlay
from special.settings import Settings, Mode


class Evolution:

    def __init__(self, games: int, seats: int, players: int, money: int,
                 blinds_scheme: Blinds.SchemeType = Blinds.Scheme.Standard):

        self.games: int = games
        self.players: int = players
        self.seats: int = seats
        self.money: int = money
        self.blinds_scheme: Blinds.SchemeType = blinds_scheme
        Play.EvolutionMode = True

    def run(self) -> None:

        for num in range(self.games):

            game = Game(self.players, self.seats, self.money, self.blinds_scheme)

            for _ in range(game.total_players):
                game.add_player()

            Debug.evolution(f'Start game #{num + 1}')

            while not game.game_finished:
                sleep(1)

            PlayManager.standings(10)
            PlayManager.delete_bad_plays()


class Run:

    def __init__(self, mode: BasePlay.ModeType):

        Play.Mode = mode
        if mode == BasePlay.Mode.GameEngine:
            # PlayManager.standings()
            GameManager().run()

        elif mode == BasePlay.Mode.Parse:
            GameParser.parse_dir('pack1')
            # game.save()
            # game.convert()
            # print(game)

        elif mode == BasePlay.Mode.Evolution:
            PlayManager.standings()
            Evolution(100000, 9, 999, 10000, Blinds.Scheme.Rapid).run()

        elif mode == BasePlay.Mode.Testing:
            NeuralNetwork.PokerDecision.Bubble(100, 9).show()


if __name__ == '__main__':
    Run(BasePlay.Mode.Parse)
