from __future__ import annotations
from typing import List, Tuple
from functools import lru_cache
from copy import deepcopy
from holdem.play.base_play import BasePlay
from special.mode import Mode
from special.settings import Settings


class Play:
    ExtendedName = False

    def __init__(self):

        self.preflop: BasePlay = BasePlay()
        self.flop: BasePlay = BasePlay()
        self.turn: BasePlay = BasePlay()
        self.river: BasePlay = BasePlay()

        self.total_hands = 0

        self.wins_before_showdown = 0
        self.wins_after_showdown = 0
        self.goes_to_showdown = 0

        self.generation: int = 0
        self.exemplar: int = 0
        self.previous: int = 0

        self.busy = False

        self.name = '???'

        self.plays_history: List[Tuple[int, int]] = []

        self.wins: int = 0
        self.total_plays: int = 0
        self.average_places: float = 0

    def __str__(self):

        if Settings.game_mode == Mode.Evolution:
            return f'<Gen{self.generation} e{self.exemplar:<6} ' \
                   f'f{self.previous} p{int(self.average_places * 1000):<3} g{self.total_plays:<6} ' \
                   f'{len(self.plays_history):<4} {round(self.value(), 2)}' \
                   f'{(" " + self.wins * "*" + " ") if self.wins else ""}>   ' \
                   f'[ {", ".join(str(i[0]) for i in self.plays_history[-10:])} ]'

        else:
            return self.name

    @staticmethod
    @lru_cache(1024)
    def calc_norm(out_of: int) -> float:
        return out_of / sum(1 / i for i in range(1, out_of + 1))

    def value(self) -> float:
        if not self.plays_history:
            return 0
        return sum(1 / place * self.calc_norm(out_of) for place, out_of in self.plays_history) / len(self.plays_history)

    def mutate(self, percent: float) -> None:

        self.generation += 1
        self.wins = 0
        self.total_plays = 0
        self.average_places = 0
        self.busy = False

        self.preflop.mutate(percent)
        self.flop.mutate(percent)
        self.turn.mutate(percent)
        self.river.mutate(percent)

    def get_mutated(self, percent: float = 0.1) -> Play:

        mutated = deepcopy(self)
        mutated.previous = self.exemplar
        mutated.mutate(percent)

        return mutated

    def set_place(self, place: int, out_of: int) -> None:

        # TODO move to top
        from holdem.play.play_manager import PlayManager

        self.busy = False

        if Settings.game_mode == Mode.Evolution:

            if place == 1:
                self.wins += 1

            self.plays_history += [(place, out_of)]

            restore_places = self.total_plays * self.average_places
            self.total_plays += 1
            self.average_places = (restore_places + place / out_of) / self.total_plays

            PlayManager.save_play(self)
