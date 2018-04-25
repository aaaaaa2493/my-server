from threading import Thread
from holdem.game import Game
from core.blinds.scheme.schemes import Schemes
from holdem.network import Network
from special.debug import Debug


class QuickGame(Game):

    def __init__(self, id_: int, name: str):

        super().__init__(id_, 9, 9, 1000, Schemes.Static.value)

        # adding 8 bots
        for _ in range(8):
            self.add_player()

        self.network = Network({'type': 'gh',
                                'id': self.id,
                                'game type': 'quick',
                                'name': name})

        self.network.send({'type': 'start registration'})
        Thread(target=lambda: self.network_process(), name=f'Quick game {self.id}: network process').start()

    def network_process(self):

        Debug.game_manager(f'Game {self.id}: ready to listen game')

        while True:

            try:

                request = self.network.receive()

                Debug.game_manager(f'Game {self.id}:  message {request}')

                if request['type'] == 'add player' and not self.game_started:
                    Debug.game_manager(f'Game {self.id}: add player')
                    if self.add_player(request['name']):
                        self.network.send({'type': 'start game'})
                        Thread(target=lambda: self.wait_for_end(), name=f'Game {self.id}: wait for end').start()

                elif request['type'] == 'delete player' and not self.game_started:
                    Debug.game_manager(f'Game {self.id}: delete quick game')
                    self.break_game()

                elif request['type'] == 'break':
                    Debug.game_manager(f'Game {self.id}: break game')
                    self.break_game()

                    if self.thread:
                        self.thread.join()

                    self.network.send({'type': 'broken'})

            except ValueError:
                continue

            except IndexError:
                continue

    def wait_for_end(self) -> None:

        self.thread.join()

        if not self.game_broken:
            self.network.send({'type': 'end game'})
