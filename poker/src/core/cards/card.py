from __future__ import annotations
from typing import List
from core.cards.rank import Rank, Ranks
from core.cards.suit import Suit, Suits
from lib.pokereval.card import Card as _Card


class Card:

    UndefinedCard: str = 'UP'
    EmptyCard: str = 'ZZ'

    @staticmethod
    def cards_52() -> Cards:
        return [Card(value + suit) for value in Ranks for suit in Suits]

    @staticmethod
    def str(cards: Cards) -> str:
        return ' '.join(card.card for card in cards)

    def __init__(self, card: str):

        self.card: str = card
        self.rank: Rank = Rank.get_rank(card[0])
        self.suit: Suit = Suit.get_suit(card[1])

    @property
    def str_rank(self) -> str:
        return str(self.rank)

    @property
    def str_suit(self) -> str:
        return str(self.suit)

    @property
    def r(self) -> str:
        return self.card[0]

    @property
    def s(self) -> str:
        return self.card[1]

    def convert(self) -> _Card:
        return _Card(self.rank.to_int(), self.suit.to_int())

    @staticmethod
    def get_card(card: _Card) -> Card:
        return Card(Rank(card.rank).short + Suit(card.suit).short)

    def __str__(self) -> str:
        return f'{self.str_rank} of {self.str_suit}'

    def __hash__(self) -> int:
        return hash((self.rank, self.suit))

    def __lt__(self, other: Card) -> bool:
        return (self.rank, self.suit) < (other.rank, other.suit)

    def __le__(self, other: Card) -> bool:
        return (self.rank, self.suit) <= (other.rank, other.suit)

    def __gt__(self, other: Card) -> bool:
        return (self.rank, self.suit) > (other.rank, other.suit)

    def __ge__(self, other: Card) -> bool:
        return (self.rank, self.suit) >= (other.rank, other.suit)

    def __eq__(self, other: Card) -> bool:
        return (self.rank, self.suit) == (other.rank, other.suit)

    def __ne__(self, other: Card) -> bool:
        return (self.rank, self.suit) != (other.rank, other.suit)


Cards = List[Card]
