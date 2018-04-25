from threading import Thread
from typing import Dict
from special.debug import Debug
from holdem.game import Game
from holdem.network import Network
from holdem.blinds import Blinds
from holdem.tournament_game import TournamentGame
from holdem.quick_game import QuickGame


class GameManager:

    def __init__(self):

        self.network: Network = Network({'type': 'ge', 'name': 'main'})
        self.tournaments: Dict[int, Game] = dict()
        self.quick_games: Dict[int, Game] = dict()
        self.next_id = 0

    def run(self):

        Thread(target=self.infinite, name='GameManager infinite').start()

    def create_tournament(self, json_message: dict):

        name = json_message['name']
        total = int(json_message['total count'])
        bots = int(json_message['bot count'])
        stack = int(json_message['chip count'])
        seats = int(json_message['players'])
        blinds_speed = json_message['blinds speed']
        start_blinds = int(json_message['start blinds'])
        password = json_message['password']

        real = total - bots

        if real < 0 or bots < 0 or stack < 0 or seats < 2 or seats > 9:
            return

        if start_blinds < 1 or start_blinds > 3:
            return

        if blinds_speed == 'standard':
            scheme = Blinds.Scheme.Standard

        elif blinds_speed == 'fast':
            scheme = Blinds.Scheme.Fast

        elif blinds_speed == 'rapid':
            scheme = Blinds.Scheme.Rapid

        elif blinds_speed == 'bullet':
            scheme = Blinds.Scheme.Bullet

        else:
            return

        game = TournamentGame(self.next_id, name, total, bots,
                              stack, seats, scheme, start_blinds, password)
        self.tournaments[self.next_id] = game
        self.next_id += 1

    def create_quick_game(self, request: dict):
        self.quick_games[self.next_id] = QuickGame(self.next_id, request['name'])
        self.next_id += 1

    def delete_game(self, request: dict):
        if request['id'] in self.tournaments:
            del self.tournaments[request['id']]
            Debug.game_manager('Game manager: successful delete tournament')
        elif request['id'] in self.quick_games:
            del self.quick_games[request['id']]
            Debug.game_manager('Game manager: successful delete quick game')
        else:
            Debug.game_manager(f'Game manager: BAD ID FOR DELETING GAME: {request["id"]}')

    def infinite(self):

        Debug.game_manager('Game manager: ready to listen')

        while True:

            try:

                request = self.network.receive()

                Debug.game_manager(f'Game manager: message {request}')

                if request['type'] == 'create tournament':
                    Debug.game_manager('Game manager: create tournament')
                    self.create_tournament(request)
                    Debug.game_manager('Game manager: tournament created')

                elif request['type'] == 'create quick game':
                    Debug.game_manager('Game manager: create quick game')
                    self.create_quick_game(request)
                    Debug.game_manager('Game manager: quick game created')

                elif request['type'] == 'delete game':
                    Debug.game_manager('Game manager: delete game')
                    self.delete_game(request)
                    Debug.game_manager('Game manager: game deleted')

            except ValueError:
                continue

            except IndexError:
                continue
