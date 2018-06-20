from __future__ import annotations
from typing import Dict
from special.ordered_enum import OrderedEnum


class Rank(OrderedEnum):
    Ace = 14
    King = 13
    Queen = 12
    Jack = 11
    Ten = 10
    Nine = 9
    Eight = 8
    Seven = 7
    Six = 6
    Five = 5
    Four = 4
    Three = 3
    Two = 2
    Invalid = 1

    @classmethod
    def get_rank(cls, rank: str) -> Rank:
        return _from_str[rank]

    @property
    def short(self) -> str:
        return _to_short_str[self]

    def __str__(self) -> str:
        return _to_str[self]


_to_str: Dict[Rank, str] = {
    Rank.Two: 'two',
    Rank.Three: 'three',
    Rank.Four: 'four',
    Rank.Five: 'five',
    Rank.Six: 'six',
    Rank.Seven: 'seven',
    Rank.Eight: 'eight',
    Rank.Nine: 'nine',
    Rank.Ten: 'ten',
    Rank.Jack: 'jack',
    Rank.Queen: 'queen',
    Rank.King: 'king',
    Rank.Ace: 'ace'
}

_to_short_str: Dict[Rank, str] = {
    Rank.Two: '2',
    Rank.Three: '3',
    Rank.Four: '4',
    Rank.Five: '5',
    Rank.Six: '6',
    Rank.Seven: '7',
    Rank.Eight: '8',
    Rank.Nine: '9',
    Rank.Ten: 'T',
    Rank.Jack: 'J',
    Rank.Queen: 'Q',
    Rank.King: 'K',
    Rank.Ace: 'A'
}

_from_str: Dict[str, Rank] = {
    '2': Rank.Two,
    '3': Rank.Three,
    '4': Rank.Four,
    '5': Rank.Five,
    '6': Rank.Six,
    '7': Rank.Seven,
    '8': Rank.Eight,
    '9': Rank.Nine,
    'T': Rank.Ten,
    'J': Rank.Jack,
    'Q': Rank.Queen,
    'K': Rank.King,
    'A': Rank.Ace
}

Ranks: str = '23456789TJQKA'
