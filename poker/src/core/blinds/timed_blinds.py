from threading import Thread
from time import sleep
from core.blinds.scheme.scheme import Scheme
from core.blinds.blinds import Blinds
from core.base_game import BaseGame


class TimedBlinds(Blinds):

    def __init__(self, scheme: Scheme, game: BaseGame):
        super().__init__(scheme)

        self.game: BaseGame = game
        self.thread: Thread = None

    def start(self) -> None:

        self.thread = Thread(target=self.infinite, name='Blinds infinite')
        self.thread.start()

    def infinite(self) -> None:

        self.curr_round += 1

        while self.curr_round < len(self.order) - 1 and (
                not self.game.game_finished and not self.game.game_broken):

            sleep(self.time.to_int() * 60)

            self.curr_round += 1
            self.set_blinds()

            if not self.game.game_finished and not self.game.game_broken:
                self.game.blinds_increased()
