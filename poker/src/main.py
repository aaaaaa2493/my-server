
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
















class GameManager:

    def __init__(self):

        self.network: Network = Network('ge', 'main')
        self.game: Game = None

    def run(self):

        Thread(target=lambda: self.infinite(), name='GameManager infinite').start()

    def create_game(self, real, bots, seats, stack, scheme, name=''):

        real = int(real)
        bots = int(bots)
        seats = int(seats)
        stack = int(stack)

        self.network.send_raw('http name:' + name)
        self.network.send_raw('http players:' + str(real+bots))

        if scheme == 'standard':
            scheme = Blinds.Scheme.Standard

        elif scheme == 'fast':
            scheme = Blinds.Scheme.Fast

        elif scheme == 'rapid':
            scheme = Blinds.Scheme.Rapid

        elif scheme == 'bullet':
            scheme = Blinds.Scheme.Bullet

        else:
            return

        self.game = Game(real + bots, seats, stack, scheme)

        for _ in range(bots):
            self.game.add_player()

        self.network.send_raw('http start_registration')

    def add_player(self, name) -> None:

        if self.game.add_player(name):
            self.network.send_raw('http start')
            Thread(target=lambda: self.wait_for_end(), name='GameManager: wait for end').start()

    def delete_player(self, name) -> None:

        self.game.delete_player(name)

    def wait_for_end(self) -> None:

        self.game.thread.join()

        if not self.game.game_broken:
            del self.game
            self.game = None
            self.network.send_raw('http end')

    def break_game(self):

        self.game.break_game()

        if self.game.thread:
            self.game.thread.join()

        del self.game
        self.game = None
        self.network.send_raw('http broken')

    def infinite(self):

        Debug.game_manager('Game manager: ready to listen')

        while True:

            try:

                request = self.network.receive_raw()

                Debug.game_manager('Game manager: message "' + request + '"')

                request = request.split()

                if request[0] == 'create' and self.game is None:
                    Debug.game_manager('Game manager: create game')
                    self.create_game(*request[1:])
                    Debug.game_manager('Game manager: game created')

                elif request[0] == 'add' and self.game is not None and not self.game.game_started:
                    Debug.game_manager('Game manager: add player')
                    self.add_player(request[1])
                    Debug.game_manager('Game manager: player added')

                elif request[0] == 'delete' and self.game is not None and not self.game.game_started:
                    Debug.game_manager('Game manager: delete player')
                    self.delete_player(request[1])
                    Debug.game_manager('Game manager: player deleted')

                elif request[0] == 'break' and self.game is not None:
                    Debug.game_manager('Game manager: break game')
                    self.break_game()
                    Debug.game_manager('Game manager: game broken')

            except ValueError:
                continue

            except IndexError:
                continue


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
