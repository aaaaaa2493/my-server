from itertools import combinations
from core.cards.card import Card, Rank
from holdem.poker.hand import Hand
from holdem.poker.strength import Strength


class HandStrength:
    @staticmethod
    def strength(c1: Card, c2: Card, c3: Card, c4: Card, c5: Card) -> Hand:

        c1, c2, c3, c4, c5 = sorted([c1, c2, c3, c4, c5], reverse=True)  # type: Card

        flush = c1.suit == c2.suit == c3.suit == c4.suit == c5.suit
        straight = (c1.rank.to_int() ==
                    c2.rank.to_int() + 1 ==
                    c3.rank.to_int() + 2 ==
                    c4.rank.to_int() + 3 ==
                    c5.rank.to_int() + 4) or (
                           c1.rank == Rank.Ace and
                           c2.rank == Rank.Five and
                           c3.rank == Rank.Four and
                           c4.rank == Rank.Three and
                           c5.rank == Rank.Two)

        if straight and flush:

            if c1.rank == Rank.Ace:
                return Hand([c1, c2, c3, c4, c5], Strength.RoyalFlush)

            return Hand([c1, c2, c3, c4, c5], Strength.StraightFlush, c1.rank)

        if c1.rank == c2.rank == c3.rank == c4.rank:
            return Hand([c1, c2, c3, c4, c5], Strength.Quad, c1.rank, c5.rank)

        if c2.rank == c3.rank == c4.rank == c5.rank:
            return Hand([c2, c3, c4, c5, c1], Strength.Quad, c2.rank, c1.rank)

        if c1.rank == c2.rank == c3.rank and c4.rank == c5.rank:
            return Hand([c1, c2, c3, c4, c5], Strength.FullHouse, c1.rank, c4.rank)

        if c1.rank == c2.rank and c3.rank == c4.rank == c5.rank:
            return Hand([c3, c4, c5, c1, c2], Strength.FullHouse, c3.rank, c1.rank)

        if flush:
            return Hand([c1, c2, c3, c4, c5], Strength.Flush, c1.rank, c2.rank, c3.rank, c4.rank, c5.rank)

        if straight:
            return Hand([c1, c2, c3, c4, c5], Strength.Straight, c1.rank)

        if c1.rank == c2.rank == c3.rank:
            return Hand([c1, c2, c3, c4, c5], Strength.Set, c1.rank, c4.rank, c5.rank)

        if c2.rank == c3.rank == c4.rank:
            return Hand([c2, c3, c4, c1, c5], Strength.Set, c2.rank, c1.rank, c5.rank)

        if c3.rank == c4.rank == c5.rank:
            return Hand([c3, c4, c5, c1, c2], Strength.Set, c3.rank, c1.rank, c2.rank)

        if c1.rank == c2.rank and c3.rank == c4.rank:
            return Hand([c1, c2, c3, c4, c5], Strength.Pairs, c1.rank, c3.rank, c5.rank)

        if c1.rank == c2.rank and c4.rank == c5.rank:
            return Hand([c1, c2, c4, c5, c3], Strength.Pairs, c1.rank, c4.rank, c3.rank)

        if c2.rank == c3.rank and c4.rank == c5.rank:
            return Hand([c2, c3, c4, c5, c1], Strength.Pairs, c2.rank, c4.rank, c1.rank)

        if c1.rank == c2.rank:
            return Hand([c1, c2, c3, c4, c5], Strength.Pair, c1.rank, c3.rank, c4.rank, c5.rank)

        if c2.rank == c3.rank:
            return Hand([c2, c3, c1, c4, c5], Strength.Pair, c2.rank, c1.rank, c4.rank, c5.rank)

        if c3.rank == c4.rank:
            return Hand([c3, c4, c1, c2, c5], Strength.Pair, c3.rank, c1.rank, c2.rank, c5.rank)

        if c4.rank == c5.rank:
            return Hand([c4, c5, c1, c2, c3], Strength.Pair, c4.rank, c1.rank, c2.rank, c3.rank)

        return Hand([c1, c2, c3, c4, c5], Strength.Nothing, c1.rank, c2.rank, c3.rank, c4.rank, c5.rank)

    @staticmethod
    def strength4(c1: Card, c2: Card, c3: Card, c4: Card) -> Hand:

        c1, c2, c3, c4 = sorted([c1, c2, c3, c4], reverse=True)  # type: Card

        if c1.rank == c2.rank == c3.rank == c4.rank:
            return Hand([c1, c2, c3, c4, None], Strength.Quad, c1.rank)

        if c1.rank == c2.rank == c3.rank:
            return Hand([c1, c2, c3, c4, None], Strength.Set, c1.rank, c4.rank)

        if c2.rank == c3.rank == c4.rank:
            return Hand([c2, c3, c4, c1, None], Strength.Set, c2.rank, c1.rank)

        if c1.rank == c2.rank and c3.rank == c4.rank:
            return Hand([c1, c2, c3, c4, None], Strength.Pairs, c1.rank, c3.rank)

        if c1.rank == c2.rank:
            return Hand([c1, c2, c3, c4, None], Strength.Pair, c1.rank, c3.rank, c4.rank)

        if c2.rank == c3.rank:
            return Hand([c2, c3, c1, c4, None], Strength.Pair, c2.rank, c1.rank, c4.rank)

        if c3.rank == c4.rank:
            return Hand([c3, c4, c1, c2, None], Strength.Pair, c3.rank, c1.rank, c2.rank)

        return Hand([c1, c2, c3, c4, None], Strength.Nothing, c1.rank, c2.rank, c3.rank, c4.rank)

    @staticmethod
    def strength3(c1: Card, c2: Card, c3: Card) -> Hand:

        c1, c2, c3 = sorted([c1, c2, c3], reverse=True)  # type: Card

        if c1.rank == c2.rank == c3.rank:
            return Hand([c1, c2, c3, None, None], Strength.Set, c1.rank)

        if c1.rank == c2.rank:
            return Hand([c1, c2, c3, None, None], Strength.Pair, c1.rank, c3.rank)

        if c2.rank == c3.rank:
            return Hand([c2, c3, c1, None, None], Strength.Pair, c2.rank, c1.rank)

        return Hand([c1, c2, c3, None, None], Strength.Nothing, c1.rank, c2.rank, c3.rank)

    @staticmethod
    def strength2(c1: Card, c2: Card) -> Hand:

        c1, c2 = sorted([c1, c2], reverse=True)  # type: Card

        if c1.rank == c2.rank:
            return Hand([c1, c2, None, None, None], Strength.Pair, c1.rank)

        return Hand([c1, c2, None, None, None], Strength.Nothing, c1.rank, c2.rank)

    @staticmethod
    def strength1(c1: Card) -> Hand:

        return Hand([c1, None, None, None, None], Strength.Nothing, c1.rank)

    @staticmethod
    def max_strength(cards: Card.Cards) -> Hand:
        return max(HandStrength.strength(*c) for c in combinations(cards, 5))
