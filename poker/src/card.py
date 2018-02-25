from typing import List, Dict
from .special.ordered_enum import OrderedEnum


class Card:

    Cards = List['Card']

    UndefinedCard: str = 'UP'
    EmptyCard: str = 'ZZ'

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

    Ranks: str = '23456789TJQKA'

    ToRank: Dict[Rank, str] = {Rank.Two: 'two',
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
                               Rank.Ace: 'ace'}

    FromRank: Dict[str, Rank] = {'2': Rank.Two,
                                 '3': Rank.Three,
                                 '4': Rank.our,
                                 '5': Rank.Five,
                                 '6': Rank.Six,
                                 '7': Rank.Seven,
                                 '8': Rank.Eight,
                                 '9': Rank.Nine,
                                 'T': Rank.Ten,
                                 'J': Rank.Jack,
                                 'Q': Rank.Queen,
                                 'K': Rank.King,
                                 'A': Rank.Ace}

    class Suit(OrderedEnum):
        Hearts = 1
        Diamonds = 2
        Clubs = 3
        Spades = 4

    Suits: str = 'HDCS'

    ToSuit: Dict[Suit, str] = {Suit.Hearts: 'hearts',
                               Suit.Diamonds: 'diamonds',
                               Suit.Clubs: 'clubs',
                               Suit.Spades: 'spades'}

    FromSuit: Dict[str, Suit] = {'H': Suit.Hearts,
                                 'D': Suit.Diamonds,
                                 'C': Suit.Clubs,
                                 'S': Suit.Spades}

    @staticmethod
    def cards_52() -> Cards:
        return [Card(value + suit) for value in Card.Ranks for suit in Card.Suits]

    @staticmethod
    def str(cards: Cards) -> str:
        return ' '.join(card.card for card in cards)

    def __init__(self, card: str):

        self.card: str = card
        self.rank: Card.Rank = Card.FromRank[card[0]]
        self.suit: Card.Suit = Card.FromSuit[card[1]]

    def get_rank(self) -> str:
        return Card.Rank.ToStr[self.rank]

    def get_suit(self) -> str:
        return Card.Suit.ToStr[self.suit]

    def r(self) -> str:
        return self.card[0]

    def s(self) -> str:
        return self.card[1]

    def __str__(self) -> str:
        return f'{self.get_rank()} of {self.get_suit()}'

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
