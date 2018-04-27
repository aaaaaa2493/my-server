from typing import Dict
from special.ordered_enum import OrderedEnum


class Strength(OrderedEnum):
    RoyalFlush = 9
    StraightFlush = 8
    Quad = 7
    FullHouse = 6
    Flush = 5
    Straight = 4
    Set = 3
    Pairs = 2
    Pair = 1
    Nothing = 0

    def __str__(self) -> str:
        return _to_str[self]


_to_str: Dict[Strength, str] = {
    Strength.Nothing: 'nothing',
    Strength.Pair: 'pair',
    Strength.Pairs: 'pairs',
    Strength.Set: 'set',
    Strength.Straight: 'straight',
    Strength.Flush: 'flush',
    Strength.FullHouse: 'full house',
    Strength.Quad: 'quad',
    Strength.StraightFlush: 'straight flush',
    Strength.RoyalFlush: 'royal flush'
}