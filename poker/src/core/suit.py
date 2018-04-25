from typing import Dict
from special.ordered_enum import OrderedEnum


class Suit(OrderedEnum):
    Hearts = 1
    Diamonds = 2
    Clubs = 3
    Spades = 4

    @property
    def str_suit(self) -> str:
        return _to_str[self]

    @classmethod
    def get_suit(cls, suit: str) -> 'Suit':
        return _from_str[suit]


_to_str: Dict[Suit, str] = {
    Suit.Hearts: 'hearts',
    Suit.Diamonds: 'diamonds',
    Suit.Clubs: 'clubs',
    Suit.Spades: 'spades'
}

_from_str: Dict[str, Suit] = {
    'H': Suit.Hearts,
    'D': Suit.Diamonds,
    'C': Suit.Clubs,
    'S': Suit.Spades
}

Suits: str = 'HDCS'
