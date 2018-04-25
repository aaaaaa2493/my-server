from typing import List, Dict
from core.rank import Rank
from core.suit import Suit


class Card:

    Cards = List['Card']

    UndefinedCard: str = 'UP'
    EmptyCard: str = 'ZZ'

    Ranks: str = '23456789TJQKA'

    ToRank: Dict[Rank, str] = {
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

    FromRank: Dict[str, Rank] = {
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

    Suits: str = 'HDCS'

    ToSuit: Dict[Suit, str] = {
        Suit.Hearts: 'hearts',
        Suit.Diamonds: 'diamonds',
        Suit.Clubs: 'clubs',
        Suit.Spades: 'spades'
    }

    FromSuit: Dict[str, Suit] = {
        'H': Suit.Hearts,
        'D': Suit.Diamonds,
        'C': Suit.Clubs,
        'S': Suit.Spades
    }

    @staticmethod
    def cards_52() -> Cards:
        return [Card(value + suit) for value in Card.Ranks for suit in Card.Suits]

    @staticmethod
    def str(cards: Cards) -> str:
        return ' '.join(card.card for card in cards)

    def __init__(self, card: str):

        self.card: str = card
        self.rank: Rank = Card.FromRank[card[0]]
        self.suit: Suit = Card.FromSuit[card[1]]

    @property
    def str_rank(self) -> str:
        return Rank.ToStr[self.rank]

    @property
    def str_suit(self) -> str:
        return Suit.ToStr[self.suit]

    @property
    def r(self) -> str:
        return self.card[0]

    @property
    def s(self) -> str:
        return self.card[1]

    def __str__(self) -> str:
        return f'{self.str_rank} of {self.str_suit}'

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
