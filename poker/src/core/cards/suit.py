from typing import Dict, Iterator
from special.ordered_enum import OrderedEnum


class Suit(OrderedEnum):
    Hearts = 1
    Diamonds = 2
    Clubs = 3
    Spades = 4

    @classmethod
    def get_suit(cls, suit: str) -> 'Suit':
        return _from_str[suit]

    @classmethod
    def all(cls) -> Iterator['Suit']:
        for suit in Suits:
            yield _from_str[suit]

    @property
    def short(self) -> str:
        return _to_short_str[self]

    def __str__(self) -> str:
        return _to_str[self]


_to_str: Dict[Suit, str] = {
    Suit.Hearts: 'hearts',
    Suit.Diamonds: 'diamonds',
    Suit.Clubs: 'clubs',
    Suit.Spades: 'spades'
}

_to_short_str: Dict[Suit, str] = {
    Suit.Hearts: 'H',
    Suit.Diamonds: 'D',
    Suit.Clubs: 'C',
    Suit.Spades: 'S'
}

_from_str: Dict[str, Suit] = {
    'H': Suit.Hearts,
    'D': Suit.Diamonds,
    'C': Suit.Clubs,
    'S': Suit.Spades
}

Suits: str = 'HDCS'
