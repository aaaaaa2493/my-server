from typing import Dict, Iterator, Tuple
from itertools import combinations
from .special.ordered_enum import OrderedEnum
from .card import Card
from .cards_pair import CardsPair

from pokereval.card import Card as _Card
from pokereval.hand_evaluator import HandEvaluator


class HoldemPoker:

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

    ToStrength: Dict[Strength, str] = {Strength.Nothing: 'nothing',
                                       Strength.Pair: 'pair',
                                       Strength.Pairs: 'pairs',
                                       Strength.Set: 'set',
                                       Strength.Straight: 'straight',
                                       Strength.Flush: 'flush',
                                       Strength.FullHouse: 'full house',
                                       Strength.Quad: 'quad',
                                       Strength.StraightFlush: 'straight flush',
                                       Strength.RoyalFlush: 'royal flush'}

    class Hand:

        def __init__(self, cards: Card.Cards, strength: 'HoldemPoker.Strength', kicker1: Card.Rank = None,
                     kicker2: Card.Rank = None, kicker3: Card.Rank = None,
                     kicker4: Card.Rank = None, kicker5: Card.Rank = None):

            self.strength: HoldemPoker.Strength = strength

            self.kicker1: Card.Rank = kicker1
            self.kicker2: Card.Rank = kicker2
            self.kicker3: Card.Rank = kicker3
            self.kicker4: Card.Rank = kicker4
            self.kicker5: Card.Rank = kicker5

            if self.kicker1 is None:
                self.kicker1 = Card.Rank.Invalid
            elif self.kicker2 is None:
                self.kicker2 = Card.Rank.Invalid
            elif self.kicker3 is None:
                self.kicker3 = Card.Rank.Invalid
            elif self.kicker4 is None:
                self.kicker4 = Card.Rank.Invalid
            elif self.kicker5 is None:
                self.kicker5 = Card.Rank.Invalid

            self.cards = cards

        def kickers(self) -> Iterator[Card.Rank]:

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

        def __lt__(self, other: 'HoldemPoker.Hand') -> bool:

            return (self.strength, self.kicker1, self.kicker2, self.kicker3, self.kicker4, self.kicker5) < \
                   (other.strength, other.kicker1, other.kicker2, other.kicker3, other.kicker4, other.kicker5)

        def __le__(self, other: 'HoldemPoker.Hand') -> bool:

            return (self.strength, self.kicker1, self.kicker2, self.kicker3, self.kicker4, self.kicker5) <= \
                   (other.strength, other.kicker1, other.kicker2, other.kicker3, other.kicker4, other.kicker5)

        def __gt__(self, other: 'HoldemPoker.Hand') -> bool:

            return (self.strength, self.kicker1, self.kicker2, self.kicker3, self.kicker4, self.kicker5) > \
                   (other.strength, other.kicker1, other.kicker2, other.kicker3, other.kicker4, other.kicker5)

        def __ge__(self, other: 'HoldemPoker.Hand') -> bool:

            return (self.strength, self.kicker1, self.kicker2, self.kicker3, self.kicker4, self.kicker5) >= \
                   (other.strength, other.kicker1, other.kicker2, other.kicker3, other.kicker4, other.kicker5)

        def __eq__(self, other: 'HoldemPoker.Hand') -> bool:

            return (self.strength, self.kicker1, self.kicker2, self.kicker3, self.kicker4, self.kicker5) == \
                   (other.strength, other.kicker1, other.kicker2, other.kicker3, other.kicker4, other.kicker5)

        def __ne__(self, other: 'HoldemPoker.Hand') -> bool:

            return (self.strength, self.kicker1, self.kicker2, self.kicker3, self.kicker4, self.kicker5) != \
                   (other.strength, other.kicker1, other.kicker2, other.kicker3, other.kicker4, other.kicker5)

        def __str__(self) -> str:

            if self.strength == HoldemPoker.Strength.RoyalFlush:
                return 'royal flush'

            if self.strength == HoldemPoker.Strength.StraightFlush:
                return f'straight flush starts with {Card.ToRank[self.kicker1]}'

            if self.strength == HoldemPoker.Strength.Quad:
                return f'quad of {Card.ToRank[self.kicker1]}, kicker {Card.ToRank[self.kicker2]}))'

            if self.strength == HoldemPoker.Strength.FullHouse:
                return f'full house of {Card.ToRank[self.kicker1]} and {Card.ToRank[self.kicker2]}'

            if self.strength == HoldemPoker.Strength.Flush:
                return f'flush, kickers: {" ".join(Card.ToRank[i] for i in self.kickers())}'

            if self.strength == HoldemPoker.Strength.Straight:
                return f'straight starts with {Card.ToRank[self.kicker1]}'

            if self.strength == HoldemPoker.Strength.Set:
                return f'set of {Card.ToRank[self.kicker1]}, kickers: ' \
                       f'{Card.ToRank[self.kicker2]} {Card.ToRank[self.kicker3]}'

            if self.strength == HoldemPoker.Strength.Pairs:
                return f'two pairs of {Card.ToRank[self.kicker1]} and {Card.ToRank[self.kicker2]}, ' \
                       f'kicker {Card.ToRank[self.kicker3]}'

            if self.strength == HoldemPoker.Strength.Pair:
                return f'pair of {Card.ToRank[self.kicker1]}, kickers: {Card.ToRank[self.kicker2]} ' \
                       f'{Card.ToRank[self.kicker3]} {Card.ToRank[self.kicker4]}'

            if self.strength == HoldemPoker.Strength.Nothing:
                return f'nothing, kickers: {" ".join(Card.ToRank[i] for i in self.kickers())}'

            raise IndexError(f'Impossible hand with strength id {self.strength}')

    @staticmethod
    def strength(c1: Card, c2: Card, c3: Card, c4: Card, c5: Card) -> Hand:

        c1, c2, c3, c4, c5 = sorted([c1, c2, c3, c4, c5], reverse=True)  # type: Card

        flush = c1.suit == c2.suit == c3.suit == c4.suit == c5.suit
        straight = (c1.rank.to_int() ==
                    c2.rank.to_int() + 1 ==
                    c3.rank.to_int() + 2 ==
                    c4.rank.to_int() + 3 ==
                    c5.rank.to_int() + 4) or (
            c1.rank == Card.Rank.Ace and
            c2.rank == Card.Rank.Five and
            c3.rank == Card.Rank.Four and
            c4.rank == Card.Rank.Three and
            c5.rank == Card.Rank.Two)

        if straight and flush:

            if c1.rank == Card.Rank.Ace:
                return HoldemPoker.Hand([c1, c2, c3, c4, c5], HoldemPoker.Strength.RoyalFlush)

            return HoldemPoker.Hand([c1, c2, c3, c4, c5], HoldemPoker.Strength.StraightFlush, c1.rank)

        if c1.rank == c2.rank == c3.rank == c4.rank:
            return HoldemPoker.Hand([c1, c2, c3, c4, c5], HoldemPoker.Strength.Quad, c1.rank, c5.rank)

        if c2.rank == c3.rank == c4.rank == c5.rank:
            return HoldemPoker.Hand([c2, c3, c4, c5, c1], HoldemPoker.Strength.Quad, c2.rank, c1.rank)

        if c1.rank == c2.rank == c3.rank and c4.rank == c5.rank:
            return HoldemPoker.Hand([c1, c2, c3, c4, c5], HoldemPoker.Strength.FullHouse, c1.rank, c4.rank)

        if c1.rank == c2.rank and c3.rank == c4.rank == c5.rank:
            return HoldemPoker.Hand([c3, c4, c5, c1, c2], HoldemPoker.Strength.FullHouse, c3.rank, c1.rank)

        if flush:
            return HoldemPoker.Hand([c1, c2, c3, c4, c5], HoldemPoker.Strength.Flush,
                                    c1.rank, c2.rank, c3.rank, c4.rank, c5.rank)

        if straight:
            return HoldemPoker.Hand([c1, c2, c3, c4, c5], HoldemPoker.Strength.Straight, c1.rank)

        if c1.rank == c2.rank == c3.rank:
            return HoldemPoker.Hand([c1, c2, c3, c4, c5], HoldemPoker.Strength.Set, c1.rank, c4.rank, c5.rank)

        if c2.rank == c3.rank == c4.rank:
            return HoldemPoker.Hand([c2, c3, c4, c1, c5], HoldemPoker.Strength.Set, c2.rank, c1.rank, c5.rank)

        if c3.rank == c4.rank == c5.rank:
            return HoldemPoker.Hand([c3, c4, c5, c1, c2], HoldemPoker.Strength.Set, c3.rank, c1.rank, c2.rank)

        if c1.rank == c2.rank and c3.rank == c4.rank:
            return HoldemPoker.Hand([c1, c2, c3, c4, c5], HoldemPoker.Strength.Pairs, c1.rank, c3.rank, c5.rank)

        if c1.rank == c2.rank and c4.rank == c5.rank:
            return HoldemPoker.Hand([c1, c2, c4, c5, c3], HoldemPoker.Strength.Pairs, c1.rank, c4.rank, c3.rank)

        if c2.rank == c3.rank and c4.rank == c5.rank:
            return HoldemPoker.Hand([c2, c3, c4, c5, c1], HoldemPoker.Strength.Pairs, c2.rank, c4.rank, c1.rank)

        if c1.rank == c2.rank:
            return HoldemPoker.Hand([c1, c2, c3, c4, c5], HoldemPoker.Strength.Pair, c1.rank, c3.rank, c4.rank, c5.rank)

        if c2.rank == c3.rank:
            return HoldemPoker.Hand([c2, c3, c1, c4, c5], HoldemPoker.Strength.Pair, c2.rank, c1.rank, c4.rank, c5.rank)

        if c3.rank == c4.rank:
            return HoldemPoker.Hand([c3, c4, c1, c2, c5], HoldemPoker.Strength.Pair, c3.rank, c1.rank, c2.rank, c5.rank)

        if c4.rank == c5.rank:
            return HoldemPoker.Hand([c4, c5, c1, c2, c3], HoldemPoker.Strength.Pair, c4.rank, c1.rank, c2.rank, c3.rank)

        return HoldemPoker.Hand([c1, c2, c3, c4, c5], HoldemPoker.Strength.Nothing,
                                c1.rank, c2.rank, c3.rank, c4.rank, c5.rank)

    @staticmethod
    def strength4(c1: Card, c2: Card, c3: Card, c4: Card) -> Hand:

        c1, c2, c3, c4 = sorted([c1, c2, c3, c4], reverse=True)  # type: Card

        if c1.rank == c2.rank == c3.rank == c4.rank:
            return HoldemPoker.Hand([c1, c2, c3, c4, None], HoldemPoker.Strength.Quad, c1.rank)

        if c1.rank == c2.rank == c3.rank:
            return HoldemPoker.Hand([c1, c2, c3, c4, None], HoldemPoker.Strength.Set, c1.rank, c4.rank)

        if c2.rank == c3.rank == c4.rank:
            return HoldemPoker.Hand([c2, c3, c4, c1, None], HoldemPoker.Strength.Set, c2.rank, c1.rank)

        if c1.rank == c2.rank and c3.rank == c4.rank:
            return HoldemPoker.Hand([c1, c2, c3, c4, None], HoldemPoker.Strength.Pairs, c1.rank, c3.rank)

        if c1.rank == c2.rank:
            return HoldemPoker.Hand([c1, c2, c3, c4, None], HoldemPoker.Strength.Pair, c1.rank, c3.rank, c4.rank)

        if c2.rank == c3.rank:
            return HoldemPoker.Hand([c2, c3, c1, c4, None], HoldemPoker.Strength.Pair, c2.rank, c1.rank, c4.rank)

        if c3.rank == c4.rank:
            return HoldemPoker.Hand([c3, c4, c1, c2, None], HoldemPoker.Strength.Pair, c3.rank, c1.rank, c2.rank)

        return HoldemPoker.Hand([c1, c2, c3, c4, None],
                                HoldemPoker.Strength.Nothing, c1.rank, c2.rank, c3.rank, c4.rank)

    @staticmethod
    def strength3(c1: Card, c2: Card, c3: Card) -> Hand:

        c1, c2, c3 = sorted([c1, c2, c3], reverse=True)  # type: Card

        if c1.rank == c2.rank == c3.rank:
            return HoldemPoker.Hand([c1, c2, c3, None, None], HoldemPoker.Strength.Set, c1.rank)

        if c1.rank == c2.rank:
            return HoldemPoker.Hand([c1, c2, c3, None, None], HoldemPoker.Strength.Pair, c1.rank, c3.rank)

        if c2.rank == c3.rank:
            return HoldemPoker.Hand([c2, c3, c1, None, None], HoldemPoker.Strength.Pair, c2.rank, c1.rank)

        return HoldemPoker.Hand([c1, c2, c3, None, None], HoldemPoker.Strength.Nothing, c1.rank, c2.rank, c3.rank)

    @staticmethod
    def strength2(c1: Card, c2: Card) -> Hand:

        c1, c2 = sorted([c1, c2], reverse=True)  # type: Card

        if c1.rank == c2.rank:
            return HoldemPoker.Hand([c1, c2, None, None, None], HoldemPoker.Strength.Pair, c1.rank)

        return HoldemPoker.Hand([c1, c2, None, None, None], HoldemPoker.Strength.Nothing, c1.rank, c2.rank)

    @staticmethod
    def strength1(c1: Card) -> Hand:

        return HoldemPoker.Hand([c1, None, None, None, None], HoldemPoker.Strength.Nothing, c1.rank)

    @staticmethod
    def max_strength(cards: Card.Cards) -> Hand:
        return max(HoldemPoker.strength(*c) for c in combinations(cards, 5))

    @staticmethod
    def probability(c: CardsPair, f: Card.Cards) -> float:
        return HandEvaluator.evaluate_hand([_Card(c.first.rank.to_int(), c.first.suit.to_int()),
                                            _Card(c.second.rank.to_int(), c.second.suit.to_int())],
                                           [_Card(card.rank.to_int(), card.suit.to_int()) for card in f])

    @staticmethod
    def calculate_outs(hidden: CardsPair, common: Card.Cards) -> Tuple[int, Card.Cards]:

        if len(common) == 5 or len(common) == 0:
            return 0, []

        cards: Card.Cards = [hidden.first, hidden.second] + common

        curr_hand_strength = HoldemPoker.max_strength(cards).strength

        outs: int = 0
        outs_cards = []

        for card in Card.cards_52():

            if card not in cards:

                new_hand_strength = HoldemPoker.max_strength(cards + [card]).strength

                if len(common) == 4:
                    new_board_strength = HoldemPoker.strength(*common, card).strength

                else:
                    new_board_strength = HoldemPoker.strength4(*common, card).strength

                if new_board_strength < new_hand_strength > curr_hand_strength:
                    outs += 1
                    outs_cards += [card]

        return outs, outs_cards
