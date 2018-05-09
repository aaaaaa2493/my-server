from typing import Tuple, Iterator
from data.game_model.poker_position import PokerPosition


class TablePosition:
    def __init__(self, utg: int, mid: int, late: int, blinds: int):
        self.early: int = utg
        self.middle: int = mid
        self.late: int = late
        self.blinds: int = blinds

    def __iter__(self) -> Iterator[Tuple[PokerPosition, int]]:
        yield PokerPosition.Blinds, self.blinds
        yield PokerPosition.Early, self.early
        yield PokerPosition.Middle, self.middle
        yield PokerPosition.Late, self.late

    def __str__(self) -> str:
        return f'TablePosition{(self.early, self.middle, self.late, self.blinds)}'
