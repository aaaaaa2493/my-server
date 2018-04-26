from special.settings import Settings, Mode


class BadMode(Exception):
    pass


class Run:

    def __init__(self, mode: Mode):

        Settings.game_mode = mode
        if mode == Mode.GameEngine:
            from holdem.game.game_manager import GameManager
            # PlayManager.standings()
            GameManager().run()

        elif mode == Mode.Parse:
            from data.game_parser import GameParser
            GameParser.parse_dir('pack1')
            # game.save()
            # game.convert()
            # print(game)

        elif mode == Mode.Evolution:
            from holdem.play.play_manager import PlayManager
            from learning.evolution import Evolution
            from core.blinds.scheme.schemes import Schemes
            PlayManager.standings()
            Evolution(100000, 9, 999, 10000, Schemes.Rapid.value).run()

        elif mode == Mode.Testing:
            from learning.neural_network import NeuralNetwork
            NeuralNetwork.PokerDecision.Bubble(100, 9).show()

        elif mode == Mode.UnitTest:
            from unit_tests.testing import UnitTesting
            UnitTesting.test_all()

        else:
            raise BadMode('Bad mode')
