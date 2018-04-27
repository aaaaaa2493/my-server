from sys import argv
from special.settings import Settings, Mode


class BadMode(Exception):
    pass


class BadCommandLineArguments(Exception):
    pass


class Run:

    def __init__(self, mode: Mode):
        if len(argv) > 1:
            self.parse_arguments(argv[1:])
        else:
            self.parse_mode(mode)

    def parse_arguments(self, args):
        if args[0] == '--unit-tests':
            Settings.game_mode = Mode.UnitTest
            self.start_unit_tests()
        elif args[0] == '--evolution-tests':
            from holdem.name_manager import NameManager
            from holdem.play.play_manager import PlayManager
            Settings.game_mode = Mode.Evolution
            NameManager.NicksPath = 'nicks_test'
            PlayManager.PlayPath = 'play_test'
            PlayManager.GenCount = 30
            self.start_evolution(3, 9, 27, 1000)
            PlayManager.remove_folder()
            NameManager.remove_folder()
        else:
            raise BadCommandLineArguments(str(args))

    def parse_mode(self, mode):
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
            self.start_evolution(100000, 9, 999, 10000)

        elif mode == Mode.Testing:
            from learning.neural_network import NeuralNetwork
            NeuralNetwork.PokerDecision.Bubble(100, 9).show()

        elif mode == Mode.UnitTest:
            self.start_unit_tests()

        else:
            raise BadMode('Bad mode')

    @staticmethod
    def start_unit_tests():
        from unit_tests.testing import UnitTesting
        UnitTesting.test_all()

    @staticmethod
    def start_evolution(games: int, seats_on_table: int, players: int, start_money: int):
        from holdem.play.play_manager import PlayManager
        from learning.evolution import Evolution
        from core.blinds.scheme.schemes import Schemes
        PlayManager.standings()
        Evolution(games, seats_on_table, players, start_money, Schemes.Rapid.value).run()
