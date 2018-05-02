from time import sleep
from core.blinds.scheme.scheme import Scheme
from holdem.play.play import Play
from holdem.game.game import Game
from holdem.play.play_manager import PlayManager
from special.debug import Debug


class Evolution:

    def __init__(self, games: int, seats: int, players: int, money: int, blinds_scheme: Scheme):

        self.games: int = games
        self.players: int = players
        self.seats: int = seats
        self.money: int = money
        self.blinds_scheme: Scheme = blinds_scheme
        Play.EvolutionMode = True

    def run(self) -> None:

        for num in range(self.games):

            game = Game(0, self.players, self.seats, self.money, self.blinds_scheme)

            for _ in range(game.total_players):
                game.add_bot_player()

            Debug.evolution(f'Start game #{num + 1}')

            while not game.game_finished:
                sleep(1)

            PlayManager.standings(10)
            PlayManager.delete_bad_plays()
