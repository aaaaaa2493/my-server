from __future__ import annotations
from typing import Iterator
from core.cards.rank import Rank
from core.cards.card import Cards
from holdem.poker.strength import Strength
from holdem.poker.holdem_poker import HoldemPoker


class BadStrength(Exception):
    pass


class Hand:

    def __init__(self, cards: Cards, strength: Strength, kicker1: Rank = None,
                 kicker2: Rank = None, kicker3: Rank = None,
                 kicker4: Rank = None, kicker5: Rank = None):

        self.strength: Strength = strength

        self.kicker1: Rank = kicker1
        self.kicker2: Rank = kicker2
        self.kicker3: Rank = kicker3
        self.kicker4: Rank = kicker4
        self.kicker5: Rank = kicker5

        if self.kicker1 is None:
            self.kicker1 = Rank.Invalid
        elif self.kicker2 is None:
            self.kicker2 = Rank.Invalid
        elif self.kicker3 is None:
            self.kicker3 = Rank.Invalid
        elif self.kicker4 is None:
            self.kicker4 = Rank.Invalid
        elif self.kicker5 is None:
            self.kicker5 = Rank.Invalid

        self.cards = cards

        if sum(card is not None for card in cards) == 5:
            self.value = - HoldemPoker.fast_card_strength(cards)  # with minus because less is better
        else:
            self.value = self.strength, self.kicker1, self.kicker2, self.kicker3, self.kicker4, self.kicker5

    def kickers(self) -> Iterator[Rank]:

        if self.kicker1 is None:
            return
        yield self.kicker1

        if self.kicker2 is None:
            return
        yield self.kicker2

        if self.kicker3 is None:
            return
        yield self.kicker3

        if self.kicker4 is None:
            return
        yield self.kicker4

        if self.kicker5 is None:
            return
        yield self.kicker5

    def __lt__(self, other: Hand) -> bool:
        return self.value < other.value

    def __le__(self, other: Hand) -> bool:
        return self.value <= other.value

    def __gt__(self, other: Hand) -> bool:
        return self.value > other.value

    def __ge__(self, other: Hand) -> bool:
        return self.value >= other.value

    def __eq__(self, other: Hand) -> bool:
        return self.value == other.value

    def __ne__(self, other: Hand) -> bool:
        return self.value != other.value

    @property
    def safe_value(self):
        return self.kicker5 is not None, self.value

    def __str__(self) -> str:

        if self.strength == Strength.RoyalFlush:
            return 'royal flush'

        if self.strength == Strength.StraightFlush:
            return f'straight flush starts with {self.kicker1}'

        if self.strength == Strength.Quad:
            return f'quad of {self.kicker1}, kicker {self.kicker2}))'

        if self.strength == Strength.FullHouse:
            return f'full house of {self.kicker1} and {self.kicker2}'

        if self.strength == Strength.Flush:
            return f'flush, kickers: {" ".join(str(i) for i in self.kickers())}'

        if self.strength == Strength.Straight:
            return f'straight starts with {self.kicker1}'

        if self.strength == Strength.Set:
            return f'set of {self.kicker1}, kickers: {self.kicker2} {self.kicker3}'

        if self.strength == Strength.Pairs:
            return f'two pairs of {self.kicker1} and {self.kicker2}, kicker {self.kicker3}'

        if self.strength == Strength.Pair:
            return f'pair of {self.kicker1}, kickers: {self.kicker2} {self.kicker3} {self.kicker4}'

        if self.strength == Strength.Nothing:
            return f'nothing, kickers: {" ".join(str(i) for i in self.kickers())}'

        raise BadStrength(f'Impossible hand with strength id {self.strength}')
