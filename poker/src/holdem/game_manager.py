from threading import Thread
from holdem.game import Game
from holdem.network import Network
from holdem.blinds import Blinds
from special.debug import Debug


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
