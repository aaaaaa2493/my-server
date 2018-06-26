from typing import List
from functools import lru_cache
from core.cards.rank import Rank, Ranks
from core.cards.suit import Suit, Suits
from lib.deuces.card import Card as _Card


class Card:

    UndefinedCard: str = 'UP'
    EmptyCard: str = 'ZZ'

    @staticmethod
    def cards_52() -> 'Cards':
        return [Card(value + suit) for value in Ranks for suit in Suits]

    @staticmethod
    def str(cards: 'Cards') -> str:
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

    @lru_cache(100)
    def convert(self) -> int:
        return _Card.new(self.card)

    def __str__(self) -> str:
        return f'{self.str_rank} of {self.str_suit}'

    def __hash__(self) -> int:
        return hash((self.rank, self.suit))

    def __lt__(self, other: 'Card') -> bool:
        return (self.rank, self.suit) < (other.rank, other.suit)

    def __le__(self, other: 'Card') -> bool:
        return (self.rank, self.suit) <= (other.rank, other.suit)

    def __gt__(self, other: 'Card') -> bool:
        return (self.rank, self.suit) > (other.rank, other.suit)

    def __ge__(self, other: 'Card') -> bool:
        return (self.rank, self.suit) >= (other.rank, other.suit)

    def __eq__(self, other: 'Card') -> bool:
        return (self.rank, self.suit) == (other.rank, other.suit)

    def __ne__(self, other: 'Card') -> bool:
        return (self.rank, self.suit) != (other.rank, other.suit)


Cards = List[Card]
