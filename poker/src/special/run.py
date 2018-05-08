from sys import argv
from special.mode import Mode
from special.settings import Settings


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

        nicks_path = 'nicks_test'
        play_path = 'play_test'
        games_path = 'games_test'
        chat_path = 'chat_test'
        testing_data_path = 'testing'
        backup_testing_path = 'backup testing'
        network_name = 'neural network'

        if args[0] == '--unit-tests':
            Settings.game_mode = Mode.UnitTest
            self.start_unit_tests()

        elif args[0] == '--evolution-tests':
            from holdem.name_manager import NameManager
            from holdem.play.play_manager import PlayManager
            Settings.game_mode = Mode.Evolution
            NameManager.NicksPath = nicks_path
            PlayManager.PlayPath = play_path
            PlayManager.GenCount = 30
            self.start_evolution(3, 9, 27, 1000)
            NameManager.remove_folder()

        elif args[0] == '--parsing-tests':
            from data.game_parser import GameParser, PokerGame
            Settings.game_mode = Mode.Parse
            PokerGame.converted_games_folder = games_path
            PokerGame.converted_chat_folder = chat_path
            games = GameParser.parse_dir(testing_data_path, True, True)
            assert len(games) == 6
            GameParser.copy_dir(backup_testing_path, testing_data_path)
            PokerGame.load_dir(testing_data_path)

        elif args[0] == '--learning-tests':
            from learning.learning import Learning
            from learning.data_sets.decision_model.poker_decision import PokerDecision
            Settings.game_mode = Mode.Learning
            learn = Learning()
            learn.create_data_set(PokerDecision)
            learn.add_data_set(testing_data_path)
            learn.save_data_set(network_name)
            learn.load_data_set(network_name)
            learn.learning(network_name)

        elif args[0] == '--network-play-tests':
            from holdem.game.game import Game
            from holdem.play.play_manager import PlayManager
            from holdem.player.neural_network.net1_net2_player import Net1Net2Player
            Settings.game_mode = Mode.Testing
            PlayManager.PlayPath = play_path
            game = Game()
            for _ in range(8):
                game.add_bot_player()
            game.add_nn_player(network_name, Net1Net2Player)
            PlayManager.remove_folder()

        else:
            raise BadCommandLineArguments(str(args))

    def parse_mode(self, mode):
        Settings.game_mode = mode
        if mode == Mode.GameEngine:
            from holdem.game.game_manager import GameManager
            # PlayManager.standings()
            GameManager().run()

        elif mode == Mode.Parse:
            from data.game_parser import GameParser, PokerGame
            # GameParser.parse_dir('pack0')
            GameParser.parse_dir('pack1', False, False)
            # game.save()
            # game.convert()
            # print(game)
            # PokerGame.load('hh.txt')

        elif mode == Mode.Evolution:
            self.start_evolution(100000, 9, 999, 10000)

        elif mode == Mode.Testing:
            # from learning.neural_network import NeuralNetwork
            # NeuralNetwork.PokerDecision.Bubble(100, 9).show()
            from time import sleep
            from datetime import datetime
            from pickle import load
            from holdem.game.game import Game
            from holdem.player.neural_network.net1_net2_player import Net1Net2Player
            from holdem.player.neural_network.net3_player import Net3Player
            from holdem.player.neural_network.net6_player import Net6Player
            from holdem.play.play_manager import PlayManager
            start_time = datetime.now()

            if 1:
                for _id in range(400):
                    game = Game(players=100)
                    for _ in range(98):
                        game.add_bot_player()
                    game.add_nn_player('nn2', Net1Net2Player)
                    game.add_nn_player('nn6', Net6Player)
                    print('Start game #', _id + 1)
                    while not game.game_finished:
                        sleep(0.01)

                plays = load(open('networks/plays', 'rb'))

            else:
                plays = {}
                for i in range(11):
                    curr = load(open('networks/plays nn2 ' + str(i+1), 'rb'))
                    for k, v in curr.items():
                        plays[k] = plays.get(k, 0) + v

            plays = sorted([(k, v) for k, v in plays.items()], key=lambda k: k[1])
            for i, play in enumerate(plays):
                pl = PlayManager.get_play_by_name(play[0])
                print(f'{i+1:>4}. {play[1]:>6} ({round(play[1] / 600, 2):>6}) {play[0]:>10}  '
                      f'(ex {pl.exemplar:>6}) {"*" * pl.wins}')
            print('It took', datetime.now() - start_time)

        elif mode == Mode.UnitTest:
            self.start_unit_tests()

        elif mode == Mode.Learning:
            from learning.learning import Learning
            from learning.data_sets.decision_model.poker_decision_5 import PokerDecision5
            from data.game_parser import GameParser
            from datetime import datetime
            learn = Learning()
            learn.create_data_set(PokerDecision5)
            start = datetime.now()
            # GameParser.parse_dir('pack1', False, False)
            learn.add_data_set('pack1')
            learn.save_data_set('nn6 added self cards.txt')
            # learn.load_data_set('nn3 a lot of raises variants.txt')
            learn.learning('nn6')
            end = datetime.now()
            print('Learning took', end - start)

        elif mode == Mode.Search:
            from data.game_parser import GameParser
            GameParser.search_in_dir('pack1', 'Seat 10')

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
