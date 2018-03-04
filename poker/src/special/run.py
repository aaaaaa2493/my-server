from special.settings import Settings, Mode
from holdem.game_manager import GameManager
from holdem.play_manager import PlayManager
from holdem.blinds import Blinds
from parsing.game_parser import GameParser
from learning.evolution import Evolution
from learning.neural_network import NeuralNetwork


class Run:

    def __init__(self, mode: Mode):

        Settings.game_mode = mode
        if mode == Mode.GameEngine:
            # PlayManager.standings()
            GameManager().run()

        elif mode == Mode.Parse:
            GameParser.parse_dir('pack1')
            # game.save()
            # game.convert()
            # print(game)

        elif mode == Mode.Evolution:
            PlayManager.standings()
            Evolution(100000, 9, 999, 10000, Blinds.Scheme.Rapid).run()

        elif mode == Mode.Testing:
            NeuralNetwork.PokerDecision.Bubble(100, 9).show()
