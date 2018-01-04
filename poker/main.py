import re
from datetime import datetime
from itertools import combinations
from operator import add, sub, mul, truediv, pow, abs, neg, gt
from os import listdir, mkdir, makedirs, remove
from os.path import exists
from pickle import load, dump
from random import shuffle, random, choice, uniform, randint
from statistics import mean
from threading import Thread, Lock
from time import sleep
from typing import List, Dict, Tuple, Callable, Optional, Iterator, Union
from websocket import create_connection
from json import loads, dumps
from copy import deepcopy
from pokereval.card import Card as _Card
from pokereval.hand_evaluator import HandEvaluator


class Debug:
    Debug = 1
    Table = 0
    Decision = 0
    InputDecision = 0
    Resitting = 0
    Standings = 0
    GameProgress = 1
    Evolution = 1
    PlayManager = 0
    GameManager = 1
    Error = 1

    if Table:
        @staticmethod
        def table(*args, **kwargs):
            print(*args, **kwargs)
    else:
        @staticmethod
        def table(*args, **kwargs):
            pass

    if Decision:
        @staticmethod
        def decision(*args, **kwargs):
            print(*args, **kwargs)
    else:
        @staticmethod
        def decision(*args, **kwargs):
            pass

    if InputDecision:
        @staticmethod
        def input_decision(*args, **kwargs):
            print(*args, **kwargs)
    else:
        @staticmethod
        def input_decision(*args, **kwargs):
            pass

    if Resitting:
        @staticmethod
        def resitting(*args, **kwargs):
            print(*args, **kwargs)
    else:
        @staticmethod
        def resitting(*args, **kwargs):
            pass

    if Standings:
        @staticmethod
        def standings(*args, **kwargs):
            print(*args, **kwargs)
    else:
        @staticmethod
        def standings(*args, **kwargs):
            pass

    if GameProgress:
        @staticmethod
        def game_progress(*args, **kwargs):
            print(*args, **kwargs)
    else:
        @staticmethod
        def game_progress(*args, **kwargs):
            pass

    if GameManager:
        @staticmethod
        def game_manager(*args, **kwargs):
            print(*args, **kwargs)
    else:
        @staticmethod
        def game_manager(*args, **kwargs):
            pass

    if Evolution:
        @staticmethod
        def evolution(*args, **kwargs):
            print(*args, **kwargs)
    else:
        @staticmethod
        def evolution(*args, **kwargs):
            pass

    if PlayManager:
        @staticmethod
        def play_manager(*args, **kwargs):
            print(*args, **kwargs)
    else:
        @staticmethod
        def play_manager(*args, **kwargs):
            pass

    if Error:
        @staticmethod
        def error(*args, **kwargs):
            print(*args, **kwargs)
    else:
        @staticmethod
        def error(*args, **kwargs):
            pass


class Card:

    Cards = List['Card']

    RankType = int

    class Rank:
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

        All = '23456789TJQKA'

        ToStr = {Two: 'two',
                 Three: 'three',
                 Four: 'four',
                 Five: 'five',
                 Six: 'six',
                 Seven: 'seven',
                 Eight: 'eight',
                 Nine: 'nine',
                 Ten: 'ten',
                 Jack: 'jack',
                 Queen: 'queen',
                 King: 'king',
                 Ace: 'ace'}

        FromStr = {'2': Two,
                   '3': Three,
                   '4': Four,
                   '5': Five,
                   '6': Six,
                   '7': Seven,
                   '8': Eight,
                   '9': Nine,
                   'T': Ten,
                   'J': Jack,
                   'Q': Queen,
                   'K': King,
                   'A': Ace}

    SuitType = int

    class Suit:
        Hearts = 1
        Diamonds = 2
        Clubs = 3
        Spades = 4

        All = 'HDCS'

        ToStr = {Hearts: 'hearts',
                 Diamonds: 'diamonds',
                 Clubs: 'clubs',
                 Spades: 'spades'}

        FromStr = {'H': Hearts,
                   'D': Diamonds,
                   'C': Clubs,
                   'S': Spades}

    @staticmethod
    def cards_52() -> Cards:
        return [Card(value + suit) for value in Card.Rank.All for suit in Card.Suit.All]

    @staticmethod
    def str(cards: Cards) -> str:
        return ' '.join(card.card for card in cards)

    def __init__(self, card: str):

        self.card: str = card
        self.rank: Card.RankType = Card.Rank.FromStr[card[0]]
        self.suit: Card.SuitType = Card.Suit.FromStr[card[1]]

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


class CardsPair:

    SuitabilityType = bool

    All = ('22o', '32s', '32o', '33o', '42s', '42o', '43s', '43o', '44o', '52s', '52o', '53s', '53o', '54s', '54o',
           '55o', '62s', '62o', '63s', '63o', '64s', '64o', '65s', '65o', '66o', '72s', '72o', '73s', '73o', '74s',
           '74o', '75s', '75o', '76s', '76o', '77o', '82s', '82o', '83s', '83o', '84s', '84o', '85s', '85o', '86s',
           '86o', '87s', '87o', '88o', '92s', '92o', '93s', '93o', '94s', '94o', '95s', '95o', '96s', '96o', '97s',
           '97o', '98s', '98o', '99o', 'T2s', 'T2o', 'T3s', 'T3o', 'T4s', 'T4o', 'T5s', 'T5o', 'T6s', 'T6o', 'T7s',
           'T7o', 'T8s', 'T8o', 'T9s', 'T9o', 'TTo', 'J2s', 'J2o', 'J3s', 'J3o', 'J4s', 'J4o', 'J5s', 'J5o', 'J6s',
           'J6o', 'J7s', 'J7o', 'J8s', 'J8o', 'J9s', 'J9o', 'JTs', 'JTo', 'JJo', 'Q2s', 'Q2o', 'Q3s', 'Q3o', 'Q4s',
           'Q4o', 'Q5s', 'Q5o', 'Q6s', 'Q6o', 'Q7s', 'Q7o', 'Q8s', 'Q8o', 'Q9s', 'Q9o', 'QTs', 'QTo', 'QJs', 'QJo',
           'QQo', 'K2s', 'K2o', 'K3s', 'K3o', 'K4s', 'K4o', 'K5s', 'K5o', 'K6s', 'K6o', 'K7s', 'K7o', 'K8s', 'K8o',
           'K9s', 'K9o', 'KTs', 'KTo', 'KJs', 'KJo', 'KQs', 'KQo', 'KKo', 'A2s', 'A2o', 'A3s', 'A3o', 'A4s', 'A4o',
           'A5s', 'A5o', 'A6s', 'A6o', 'A7s', 'A7o', 'A8s', 'A8o', 'A9s', 'A9o', 'ATs', 'ATo', 'AJs', 'AJo', 'AQs',
           'AQo', 'AKs', 'AKo', 'AAo')

    class Suitability:
        Suited = True
        Offsuited = False

        All = 'so'

        ToStr = {Suited: 'suited',
                 Offsuited: 'offsuited'}

        FromStr = {'s': Suited,
                   'o': Offsuited}

    @staticmethod
    def gt_str(self: str, opp: str):

        sfv = Card.Rank.FromStr[self[0]]
        ssv = Card.Rank.FromStr[self[1]]
        ss = CardsPair.Suitability.FromStr[self[2]]

        ofv = Card.Rank.FromStr[opp[0]]
        osv = Card.Rank.FromStr[opp[1]]
        os = CardsPair.Suitability.FromStr[opp[2]]

        if sfv == ssv:
            if ofv != osv:
                return True
            elif sfv > ofv:
                return True
            return False

        elif ofv == osv:
            return False

        if sfv > ofv:
            return True
        elif sfv < ofv:
            return False

        if ssv > osv:
            return True
        elif ssv < osv:
            return False

        if ss == CardsPair.Suitability.Suited and os == CardsPair.Suitability.Offsuited:
            return True

        return False

    def __init__(self, first: Card = None, second: Card = None):

        if first is not None and second is not None:

            if first >= second:
                self.first: Card = first
                self.second: Card = second
            else:
                self.first: Card = second
                self.second: Card = first

        else:
            self.first: Card = None
            self.second: Card = None

    def initialized(self) -> bool:
        return self.second is not None

    def suitability(self) -> SuitabilityType:

        if self.first.suit == self.second.suit:
            return CardsPair.Suitability.Suited

        return CardsPair.Suitability.Offsuited

    def get(self) -> Card.Cards:
        return [self.first, self.second]

    def drop(self) -> None:

        self.first = None
        self.second = None

    def set(self, card: Card) -> None:

        if self.first is None:
            self.first = card
        elif self.second is None:
            if card.rank > self.first.rank:
                self.second = self.first
                self.first = card
            else:
                self.second = card
        else:
            raise OverflowError('Can not set third card to pair of cards')

    def str(self) -> str:

        if self.initialized():
            return self.first.r() + self.second.r() + ('s' if self.first.suit == self.second.suit else 'o')

        raise ValueError('Pair of cards is not initialized')

    def long_str(self) -> str:

        if self.initialized():
            return f'{self.first.get_rank()} and {self.second.get_rank()} {self.suitability()}'

        raise ValueError('Pair of cards is not initialized')

    def __gt__(self, opp: 'CardsPair') -> bool:

        if self.first.rank == self.second.rank:
            if opp.first.rank != opp.second.rank:
                return True
            elif self.first.rank > opp.first.rank:
                return True
            return False

        elif opp.first.rank == opp.second.rank:
            return False

        if self.first.rank > opp.first.rank:
            return True
        elif self.first.rank < opp.first.rank:
            return False

        if self.second.rank > opp.second.rank:
            return True
        elif self.second.rank < opp.second.rank:
            return False

        if self.first.suit == self.second.suit and opp.first.suit != opp.second.suit:
            return True

        return False

    def __eq__(self, other: 'CardsPair') -> bool:
        return self.first == other.first and self.second == other.second

    def __ne__(self, other: 'CardsPair') -> bool:
        return not self.__eq__(other)

    def __str__(self):

        if self.initialized():
            return f'{self.first.card} {self.second.card}'
        elif self.first is not None:
            return f'{self.first.card} ??'
        else:
            return '?? ??'


class Poker:

    StrengthType = int

    class Strength:
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

        All = (Nothing, Pair, Pairs, Set, Straight, Flush, FullHouse, Quad, StraightFlush, RoyalFlush)

        ToStr = {Nothing: 'nothing',
                 Pair: 'pair',
                 Pairs: 'pairs',
                 Set: 'set',
                 Straight: 'straight',
                 Flush: 'flush',
                 FullHouse: 'full house',
                 Quad: 'quad',
                 StraightFlush: 'straight flush',
                 RoyalFlush: 'royal flush'}

    class Hand:

        def __init__(self, cards: Card.Cards, strength: 'Poker.StrengthType', kicker1: Card.RankType = None,
                     kicker2: Card.RankType = None, kicker3: Card.RankType = None,
                     kicker4: Card.RankType = None, kicker5: Card.RankType = None):

            self.strength: Poker.StrengthType = strength

            self.kicker1: Card.RankType = kicker1
            self.kicker2: Card.RankType = kicker2
            self.kicker3: Card.RankType = kicker3
            self.kicker4: Card.RankType = kicker4
            self.kicker5: Card.RankType = kicker5

            self.cards = cards

        def kickers(self) -> Iterator[Card.RankType]:

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

        def __lt__(self, other: 'Poker.Hand') -> bool:

            return (self.strength, self.kicker1, self.kicker2, self.kicker3, self.kicker4, self.kicker5) < \
                   (other.strength, other.kicker1, other.kicker2, other.kicker3, other.kicker4, other.kicker5)

        def __le__(self, other: 'Poker.Hand') -> bool:

            return (self.strength, self.kicker1, self.kicker2, self.kicker3, self.kicker4, self.kicker5) <= \
                   (other.strength, other.kicker1, other.kicker2, other.kicker3, other.kicker4, other.kicker5)

        def __gt__(self, other: 'Poker.Hand') -> bool:

            return (self.strength, self.kicker1, self.kicker2, self.kicker3, self.kicker4, self.kicker5) > \
                   (other.strength, other.kicker1, other.kicker2, other.kicker3, other.kicker4, other.kicker5)

        def __ge__(self, other: 'Poker.Hand') -> bool:

            return (self.strength, self.kicker1, self.kicker2, self.kicker3, self.kicker4, self.kicker5) >= \
                   (other.strength, other.kicker1, other.kicker2, other.kicker3, other.kicker4, other.kicker5)

        def __eq__(self, other: 'Poker.Hand') -> bool:

            return (self.strength, self.kicker1, self.kicker2, self.kicker3, self.kicker4, self.kicker5) == \
                   (other.strength, other.kicker1, other.kicker2, other.kicker3, other.kicker4, other.kicker5)

        def __ne__(self, other: 'Poker.Hand') -> bool:

            return (self.strength, self.kicker1, self.kicker2, self.kicker3, self.kicker4, self.kicker5) != \
                   (other.strength, other.kicker1, other.kicker2, other.kicker3, other.kicker4, other.kicker5)

        def __str__(self) -> str:

            if self.strength == Poker.Strength.RoyalFlush:
                return 'royal flush'

            if self.strength == Poker.Strength.StraightFlush:
                return f'straight flush starts with {Card.Rank.ToStr[self.kicker1]}'

            if self.strength == Poker.Strength.Quad:
                return f'quad of {Card.Rank.ToStr[self.kicker1]}, kicker {Card.Rank.ToStr[self.kicker2]}))'

            if self.strength == Poker.Strength.FullHouse:
                return f'full house of {Card.Rank.ToStr[self.kicker1]} and {Card.Rank.ToStr[self.kicker2]}'

            if self.strength == Poker.Strength.Flush:
                return f'flush, kickers: {" ".join(Card.Rank.ToStr[i] for i in self.kickers())}'

            if self.strength == Poker.Strength.Straight:
                return f'straight starts with {Card.Rank.ToStr[self.kicker1]}'

            if self.strength == Poker.Strength.Set:
                return f'set of {Card.Rank.ToStr[self.kicker1]}, kickers: ' \
                       f'{Card.Rank.ToStr[self.kicker2]} {Card.Rank.ToStr[self.kicker3]}'

            if self.strength == Poker.Strength.Pairs:
                return f'two pairs of {Card.Rank.ToStr[self.kicker1]} and {Card.Rank.ToStr[self.kicker2]}, ' \
                       f'kicker {Card.Rank.ToStr[self.kicker3]}'

            if self.strength == Poker.Strength.Pair:
                return f'pair of {Card.Rank.ToStr[self.kicker1]}, kickers: {Card.Rank.ToStr[self.kicker2]} ' \
                       f'{Card.Rank.ToStr[self.kicker3]} {Card.Rank.ToStr[self.kicker4]}'

            if self.strength == Poker.Strength.Nothing:
                return f'nothing, kickers: {" ".join(Card.Rank.ToStr[i] for i in self.kickers())}'

            raise IndexError(f'Impossible hand with strength id {self.strength}')

    @staticmethod
    def strength(c1: Card, c2: Card, c3: Card, c4: Card, c5: Card) -> Hand:

        c1, c2, c3, c4, c5 = sorted([c1, c2, c3, c4, c5], reverse=True)  # type: Card

        flush = c1.suit == c2.suit == c3.suit == c4.suit == c5.suit
        straight = c1.rank == c2.rank + 1 == c3.rank + 2 == c4.rank + 3 == c5.rank + 4 or (
            c1.rank == Card.Rank.Ace and c2.Rank == Card.Rank.Five and c3.rank == Card.Rank.Four and
            c4.rank == Card.Rank.Three and c5.Rank == Card.Rank.Two
        )

        if straight and flush:

            if c1.rank == Card.Rank.Ace:
                return Poker.Hand([c1, c2, c3, c4, c5], Poker.Strength.RoyalFlush)

            return Poker.Hand([c1, c2, c3, c4, c5], Poker.Strength.StraightFlush, c1.rank)

        if c1.rank == c2.rank == c3.rank == c4.rank:
            return Poker.Hand([c1, c2, c3, c4, c5], Poker.Strength.Quad, c1.rank, c5.rank)

        if c2.rank == c3.rank == c4.rank == c5.rank:
            return Poker.Hand([c2, c3, c4, c5, c1], Poker.Strength.Quad, c2.rank, c1.rank)

        if c1.rank == c2.rank == c3.rank and c4.rank == c5.rank:
            return Poker.Hand([c1, c2, c3, c4, c5], Poker.Strength.FullHouse, c1.rank, c4.rank)

        if c1.rank == c2.rank and c3.rank == c4.rank == c5.rank:
            return Poker.Hand([c3, c4, c5, c1, c2], Poker.Strength.FullHouse, c3.rank, c1.rank)

        if flush:
            return Poker.Hand([c1, c2, c3, c4, c5], Poker.Strength.Flush,
                              c1.rank, c2.rank, c3.rank, c4.rank, c5.rank)

        if straight:
            return Poker.Hand([c1, c2, c3, c4, c5], Poker.Strength.Straight, c1.rank)

        if c1.rank == c2.rank == c3.rank:
            return Poker.Hand([c1, c2, c3, c4, c5], Poker.Strength.Set, c1.rank, c4.rank, c5.rank)

        if c2.rank == c3.rank == c4.rank:
            return Poker.Hand([c2, c3, c4, c1, c5], Poker.Strength.Set, c2.rank, c1.rank, c5.rank)

        if c3.rank == c4.rank == c5.rank:
            return Poker.Hand([c3, c4, c5, c1, c2], Poker.Strength.Set, c3.rank, c1.rank, c2.rank)

        if c1.rank == c2.rank and c3.rank == c4.rank:
            return Poker.Hand([c1, c2, c3, c4, c5], Poker.Strength.Pairs, c1.rank, c3.rank, c5.rank)

        if c1.rank == c2.rank and c4.rank == c5.rank:
            return Poker.Hand([c1, c2, c4, c5, c3], Poker.Strength.Pairs, c1.rank, c4.rank, c3.rank)

        if c2.rank == c3.rank and c4.rank == c5.rank:
            return Poker.Hand([c2, c3, c4, c5, c1], Poker.Strength.Pairs, c2.rank, c4.rank, c1.rank)

        if c1.rank == c2.rank:
            return Poker.Hand([c1, c2, c3, c4, c5], Poker.Strength.Pair, c1.rank, c3.rank, c4.rank, c5.rank)

        if c2.rank == c3.rank:
            return Poker.Hand([c2, c3, c1, c4, c5], Poker.Strength.Pair, c2.rank, c1.rank, c4.rank, c5.rank)

        if c3.rank == c4.rank:
            return Poker.Hand([c3, c4, c1, c2, c5], Poker.Strength.Pair, c3.rank, c1.rank, c2.rank, c5.rank)

        if c4.rank == c5.rank:
            return Poker.Hand([c4, c5, c1, c2, c3], Poker.Strength.Pair, c4.rank, c1.rank, c2.rank, c3.rank)

        return Poker.Hand([c1, c2, c3, c4, c5], Poker.Strength.Nothing,
                          c1.rank, c2.rank, c3.rank, c4.rank, c5.rank)

    @staticmethod
    def strength4(c1: Card, c2: Card, c3: Card, c4: Card) -> Hand:

        c1, c2, c3, c4 = sorted([c1, c2, c3, c4], reverse=True)  # type: Card

        if c1.rank == c2.rank == c3.rank == c4.rank:
            return Poker.Hand([c1, c2, c3, c4, None], Poker.Strength.Quad, c1.rank)

        if c1.rank == c2.rank == c3.rank:
            return Poker.Hand([c1, c2, c3, c4, None], Poker.Strength.Set, c1.rank, c4.rank)

        if c2.rank == c3.rank == c4.rank:
            return Poker.Hand([c2, c3, c4, c1, None], Poker.Strength.Set, c2.rank, c1.rank)

        if c1.rank == c2.rank and c3.rank == c4.rank:
            return Poker.Hand([c1, c2, c3, c4, None], Poker.Strength.Pairs, c1.rank, c3.rank)

        if c1.rank == c2.rank:
            return Poker.Hand([c1, c2, c3, c4, None], Poker.Strength.Pair, c1.rank, c3.rank, c4.rank)

        if c2.rank == c3.rank:
            return Poker.Hand([c2, c3, c1, c4, None], Poker.Strength.Pair, c2.rank, c1.rank, c4.rank)

        if c3.rank == c4.rank:
            return Poker.Hand([c3, c4, c1, c2, None], Poker.Strength.Pair, c3.rank, c1.rank, c2.rank)

        return Poker.Hand([c1, c2, c3, c4, None], Poker.Strength.Nothing, c1.rank, c2.rank, c3.rank, c4.rank)

    @staticmethod
    def strength3(c1: Card, c2: Card, c3: Card) -> Hand:

        c1, c2, c3 = sorted([c1, c2, c3], reverse=True)  # type: Card

        if c1.rank == c2.rank == c3.rank:
            return Poker.Hand([c1, c2, c3, None, None], Poker.Strength.Set, c1.rank)

        if c1.rank == c2.rank:
            return Poker.Hand([c1, c2, c3, None, None], Poker.Strength.Pair, c1.rank, c3.rank)

        if c2.rank == c3.rank:
            return Poker.Hand([c2, c3, c1, None, None], Poker.Strength.Pair, c2.rank, c1.rank)

        return Poker.Hand([c1, c2, c3, None, None], Poker.Strength.Nothing, c1.rank, c2.rank, c3.rank)

    @staticmethod
    def max_strength(cards: Card.Cards) -> Hand:
        return max(Poker.strength(*c) for c in combinations(cards, 5))

    @staticmethod
    def probability(c: CardsPair, f: Card.Cards) -> float:
        return HandEvaluator.evaluate_hand([_Card(c.first.rank, c.first.suit),
                                            _Card(c.second.rank, c.second.suit)],
                                           [_Card(card.rank, card.suit) for card in f])

    @staticmethod
    def calculate_outs(c: CardsPair, f: Card.Cards) -> Tuple[int, Card.Cards]:

        if len(f) == 5 or len(f) == 0:
            return 0, []

        cards: Card.Cards = [c.first, c.second] + f

        curr_hand_strength = Poker.max_strength(cards).strength

        outs: int = 0
        outs_cards = []

        for card in Card.cards_52():

            if card not in cards:

                new_hand_strength = Poker.max_strength(cards + [card]).strength

                if len(f) == 4:
                    new_board_strength = Poker.strength(*f, card).strength

                else:
                    new_board_strength = Poker.strength4(*f, card).strength

                if new_board_strength < new_hand_strength > curr_hand_strength:
                    outs += 1
                    outs_cards += [card]

        return outs, outs_cards


class Deck:

    def __init__(self):

        self.cards: Card.Cards = Card.cards_52()
        self.used: Card.Cards = []

    def next(self) -> Card:

        if not self.cards:
            raise OverflowError('All 52 cards of the deck is already used')

        card = self.cards[0]

        self.cards[:1] = []
        self.used += [card]

        return card

    def merge(self) -> None:

        self.cards += self.used
        self.used = []

    def curr(self) -> Card:

        return self.cards[0]

    def shuffle(self) -> None:

        self.merge()
        shuffle(self.cards)

    def skip(self, count: int = 1) -> None:

        cards = self.cards[:count]
        self.cards[:count] = []
        self.used += cards

    def __len__(self):
        return len(self.cards)


class Neural:

    class Node:

        def __init__(self, value: float = 0, relation: 'Neural.Relation' = None):
            self.value: float = value
            self.relation = relation

        def __call__(self) -> float:
            if self.relation is None:
                return self.value
            else:
                return self.relation()

        def __getitem__(self, item) -> None:
            self.value = item

    Nodes = List[Node]

    OperationType = int
    Binary = 2
    Unary = 1

    Operation = Callable[..., float]
    Operations: List[Tuple[Operation, OperationType]] = [(add, Binary), (sub, Binary),
                                                         (truediv, Binary), (mul, Binary),
                                                         (pow, Binary), (gt, Binary),
                                                         (neg, Unary), (abs, Unary)]

    class Relation:

        def __init__(self, op: 'Neural.Operation', n1: 'Neural.Node', n2: 'Neural.Node' = None):
            self.first: Neural.Node = n1
            self.second: Neural.Node = n2
            self.op: Neural.Operation = op

            self.result: Neural.Node = Neural.Node(self(), self)

        def __call__(self) -> float:
            try:
                if self.second is None:
                    return self.op(self.first())
                else:
                    return self.op(self.first(), self.second())

            except ZeroDivisionError:
                return 0

    def __init__(self):

        # Result Node, stores how much can bet to this hand to this opponent coefficients
        self.result = None

        # Need constant because most coefficients are probabilities from 0 to 1
        self.const_1 = Neural.Node(1)

        # From BasePlay, divided by total
        self.fold = Neural.Node()
        self.check = Neural.Node()
        self.bet = Neural.Node()
        self.raise_ = Neural.Node()
        self.bet3 = Neural.Node()
        self.bet4 = Neural.Node()
        self.allin = Neural.Node()
        self.call_r = Neural.Node()
        self.call_3 = Neural.Node()
        self.call_4 = Neural.Node()
        self.call_a = Neural.Node()
        self.check_fold = Neural.Node()
        self.bet_fold = Neural.Node()
        self.call_fold = Neural.Node()
        self.raise_fold = Neural.Node()
        self.check_call = Neural.Node()
        self.check_raise = Neural.Node()
        self.check_allin = Neural.Node()
        self.wins = Neural.Node()

        # From Play, divided by total hands
        self.wins_before_showdown = Neural.Node()
        self.wins_after_showdown = Neural.Node()
        self.goes_to_showdown = Neural.Node()

        # More far from small blinds - the number is bigger
        self.my_position = Neural.Node()
        self.his_position = Neural.Node()

        # remaining_money()
        self.my_stack = Neural.Node()
        self.his_stack = Neural.Node()

        # .gived
        self.his_decision = Neural.Node()
        self.me_already_gived = Neural.Node()

        # .in_pot + .gived
        self.in_pot = Neural.Node()

        # Probability from Poker.probability
        self.probability = Neural.Node()
        self.outs = Neural.Node()

        # Blinds situation
        self.small_blind = Neural.Node()
        self.big_blind = Neural.Node()
        self.ante = Neural.Node()

        # 1 if action is on this stage else 0
        self.is_preflop = Neural.Node()
        self.is_flop = Neural.Node()
        self.is_turn = Neural.Node()
        self.is_river = Neural.Node()

        self.base: Neural.Nodes = [self.const_1, self.fold, self.check, self.bet, self.raise_, self.bet3, self.bet4,
                                   self.allin, self.call_r, self.call_3, self.call_4, self.call_a,
                                   self.check_fold, self.bet_fold, self.call_fold, self.raise_fold,
                                   self.check_call, self.check_raise, self.check_allin, self.wins,
                                   self.wins_before_showdown, self.wins_after_showdown, self.goes_to_showdown,
                                   self.my_position, self.his_position, self.my_stack, self.his_stack,
                                   self.his_decision, self.me_already_gived, self.in_pot,
                                   self.probability, self.outs, self.small_blind, self.big_blind, self.ante,
                                   self.is_preflop, self.is_flop, self.is_turn, self.is_river]

        self.secondary: Neural.Nodes = []
        self.mutate()

    def mutate(self):

        for _ in range(10):

            if random() < 0.5:

                relation, params = choice(Neural.Operations)

                if params == Neural.Binary:

                    first_node = choice(self.base + self.secondary)
                    second_node = choice(self.base + self.secondary)
                    self.secondary += [Neural.Relation(relation, first_node, second_node).result]

                elif params == Neural.Unary:

                    node = choice(self.base + self.secondary)
                    self.secondary += [Neural.Relation(relation, node).result]

        self.result = choice(self.base + self.secondary)


class BasePlay:

    StepType = int

    class Step:
        Preflop = 1
        Flop = 2
        Turn = 3
        River = 4
        GameSteps = (Preflop, Flop, Turn, River)

        ToStr = {Preflop: 'preflop',
                 Flop: 'flop',
                 Turn: 'turn',
                 River: 'river'}

        @staticmethod
        def next_step(step: 'BasePlay.StepType') -> 'BasePlay.StepType':

            if step == BasePlay.Step.Preflop:
                return BasePlay.Step.Flop
            elif step == BasePlay.Step.Flop:
                return BasePlay.Step.Turn
            elif step == BasePlay.Step.Turn:
                return BasePlay.Step.River

            raise ValueError('No next game step id ' + str(step))

    ResultType = int

    class Result:
        DoNotPlay = 0
        Fold = 1
        Call = 2
        Check = 3
        Raise = 4
        Allin = 5
        InAllin = 6
        Ante = 7
        SmallBlind = 8
        BigBlind = 9
        WinMoney = 10
        ReturnMoney = 11

        ToStr = {DoNotPlay: 'do not play',
                 Fold: 'fold',
                 Call: 'call',
                 Check: 'check',
                 Raise: 'raise',
                 Allin: 'all in',
                 InAllin: 'in all in',
                 Ante: 'ante',
                 SmallBlind: 'sb',
                 BigBlind: 'bb',
                 WinMoney: 'win',
                 ReturnMoney: 'return'}

    DecisionType = int

    class Decision:
        Fold = 0
        Check = 1
        Bet = 2
        Raise = 3
        Bet3 = 4
        Bet4 = 5
        Allin = 6
        CallR = 7
        Call3 = 8
        Call4 = 9
        CallA = 10

        CheckFold = 11
        BetFold = 12
        CallFold = 13
        RaiseFold = 14
        CheckCall = 15
        CheckRaise = 16
        CheckAllin = 17

        ToStr = {Fold: 'fold',
                 Check: 'check',
                 Bet: 'bet',
                 Raise: 'raise',
                 Bet3: '3-bet',
                 Bet4: '4-bet+',
                 Allin: 'all in',
                 CallR: 'call raise',
                 Call3: 'call 3-bet',
                 Call4: 'call 4-bet+',
                 CallA: 'call and go all in',
                 CheckFold: 'check then fold',
                 BetFold: 'bet then fold',
                 CallFold: 'call then fold',
                 RaiseFold: 'raise then fold',
                 CheckCall: 'check then call',
                 CheckRaise: 'check then raise',
                 CheckAllin: 'check then all in'}

    def __init__(self):

        self.fold = 0
        self.check = 0
        self.bet = 0
        self.raise_ = 0
        self.bet3 = 0
        self.bet4 = 0
        self.allin = 0
        self.call_r = 0
        self.call_3 = 0
        self.call_4 = 0
        self.call_a = 0
        self.check_fold = 0
        self.bet_fold = 0
        self.call_fold = 0
        self.raise_fold = 0
        self.check_call = 0
        self.check_raise = 0
        self.check_allin = 0

        self.wins = 0
        self.total = 0

        # Вероятность сделать ререйз вместо сброса карт
        self.bluff = random()

        # Играть если шансы твоих карт больше чем эти
        self.min_probability_to_play = random()

        # Если шансы карт больше чем эти то
        self.min_probability_to_all_in = random()
        # Сходить в олл ин с такой вероятностью
        self.probability_to_all_in = random()

        # если шансы твоих карт больше min_probability_to_play, то
        #   ставка равна max(шансы * bet, 1) * money
        # если минимальный рейз больше ставки то колл
        # если минимальный рейз меньше ставик то рейз
        # если необходимый колл больше ставки то фолд
        self.bet_ = random() * 3

        # если решил сделать рейз то поставит max( max(шансы * bet * reduced_raise, 1) * money, min(min_raise, money))
        self.reduced_raise = random()

        # если что то хочет поставить то с такой вероятностью чекнет
        self.check_ = random()

        # если хочет сделать ререйз то с такой вероятностью сделает колл
        self.call = random()

    def add(self, decision: 'BasePlay.DecisionType') -> None:

        self.total += 1

        if decision == BasePlay.Decision.Fold:
            self.fold += 1

        elif decision == BasePlay.Decision.Check:
            self.check += 1

        elif decision == BasePlay.Decision.Bet:
            self.bet += 1

        elif decision == BasePlay.Decision.Raise:
            self.raise_ += 1

        elif decision == BasePlay.Decision.Bet3:
            self.bet3 += 1

        elif decision == BasePlay.Decision.Bet4:
            self.bet4 += 1

        elif decision == BasePlay.Decision.Allin:
            self.allin += 1

        elif decision == BasePlay.Decision.CallR:
            self.call_r += 1

        elif decision == BasePlay.Decision.Call3:
            self.call_3 += 1

        elif decision == BasePlay.Decision.Call4:
            self.call_4 += 1

        elif decision == BasePlay.Decision.CallA:
            self.call_a += 1

        elif decision == BasePlay.Decision.CheckFold:
            self.check_fold += 1

        elif decision == BasePlay.Decision.BetFold:
            self.bet_fold += 1

        elif decision == BasePlay.Decision.CallFold:
            self.call_fold += 1

        elif decision == BasePlay.Decision.RaiseFold:
            self.raise_fold += 1

        elif decision == BasePlay.Decision.CheckCall:
            self.check_call += 1

        elif decision == BasePlay.Decision.CheckRaise:
            self.check_raise += 1

        elif decision == BasePlay.Decision.CheckAllin:
            self.check_allin += 1

        else:
            raise ValueError(f'Undefined decision id {decision}')

    def mutate(self, percent: float) -> None:

        self.bluff *= uniform(1 - percent, 1 + percent)
        self.min_probability_to_play *= uniform(1 - percent, 1 + percent)
        self.min_probability_to_all_in *= uniform(1 - percent, 1 + percent)
        self.probability_to_all_in *= uniform(1 - percent, 1 + percent)
        self.bet_ *= uniform(1 - percent, 1 + percent)
        self.reduced_raise *= uniform(1 - percent, 1 + percent)
        self.check_ *= uniform(1 - percent, 1 + percent)
        self.call *= uniform(1 - percent, 1 + percent)


class Play:

    ExtendedName = False

    def __init__(self):

        self.neural: Neural = Neural()

        self.preflop: BasePlay = BasePlay()
        self.flop: BasePlay = BasePlay()
        self.turn: BasePlay = BasePlay()
        self.river: BasePlay = BasePlay()

        self.total_hands = 0

        self.wins_before_showdown = 0
        self.wins_after_showdown = 0
        self.goes_to_showdown = 0

        self.generation: int = 0
        self.exemplar: int = 0
        self.previous: int = 0

        self.busy = False

        self.name = '???'

        self.wins: int = 0
        self.total_plays: int = 0
        self.average_places: float = 0

    def __str__(self):

        if Play.ExtendedName:
            return f'<Gen{self.generation} e{self.exemplar:<6} ' \
                   f'f{self.previous} p{int(self.average_places * 1000):<3} g{self.total_plays}' \
                   f'{(" " + self.wins * "*" + " ") if self.wins else ""}>'

        else:

            if self.name != '???':
                return self.name

            else:
                return f'ex{self.exemplar} {str(self.wins) + "*" if self.wins else ""}'

    def mutate(self, percent: float) -> None:

        self.generation += 1
        self.wins = 0
        self.total_plays = 0
        self.average_places = 0
        self.busy = False

        self.preflop.mutate(percent)
        self.flop.mutate(percent)
        self.turn.mutate(percent)
        self.river.mutate(percent)

    def get_mutated(self, percent: float = 0.1) -> 'Play':

        mutated = deepcopy(self)
        mutated.previous = self.exemplar
        mutated.mutate(percent)

        return mutated

    def set_place(self, place: int, out_of: int) -> None:

        if out_of == 999:

            if place == 1 and out_of == 999:
                self.wins += 1

            restore_places = self.total_plays * self.average_places
            self.total_plays += 1
            self.average_places = (restore_places + place / out_of) / self.total_plays
            self.busy = False
            PlayManager.save_play(self)


class PlayManager:

    Plays = List[Play]

    EnableShortInit = True

    _initialized = False
    _bank_of_plays: Plays = None
    _zero_gen_count: int = 10000

    @staticmethod
    def init():

        Debug.play_manager('Start initialization')

        PlayManager._bank_of_plays = []

        if not exists('play'):
            mkdir('play')

        if PlayManager.EnableShortInit and 'all' in listdir('play'):
            PlayManager._initialized = True
            PlayManager._bank_of_plays = load(open('play/all', 'rb'))
            for play in PlayManager._bank_of_plays:
                play.busy = False
            Debug.play_manager('End initialization (short way)')
            return

        generations = listdir('play')

        for gen_path in generations:
            Debug.play_manager(f'Initialize generation {gen_path}')
            exemplars = listdir(f'play/{gen_path}')

            for ex_path in exemplars:
                Debug.play_manager(f'Initialize exemplar {gen_path} {ex_path}')
                play: Play = load(open(f'play/{gen_path}/{ex_path}', 'rb'))

                if play.generation != int(gen_path):
                    raise ValueError(f'Generation path {gen_path} does not work')

                if play.exemplar != int(ex_path):
                    raise ValueError(f'Exemplar path {ex_path} does not work')

                play.busy = False
                PlayManager._bank_of_plays += [play]

        PlayManager._initialized = True

        dump(PlayManager._bank_of_plays, open('play/all', 'wb'))

        Debug.play_manager('End initialization')

    @staticmethod
    def delete_bad_plays():

        if not PlayManager._initialized:
            PlayManager.init()

        if not PlayManager.EnableShortInit:

            indexes_to_delete = []

            for index, play in enumerate(PlayManager._bank_of_plays):

                if (play.total_plays > 10 and play.average_places > 0.8 and play.wins == 0 or
                        play.total_plays > 50 and play.average_places > 0.45 and play.wins == 0 or
                        play.total_plays > 100 and play.average_places > 0.40 and play.wins < 1 or
                        play.total_plays > 200 and play.average_places > 0.35 and play.wins < 2 or
                        play.total_plays > 300 and play.average_places > 0.30 and play.wins < 3 or
                        play.total_plays > 400 and play.average_places > 0.25 and play.wins < 4 or
                        play.total_plays > 500 and play.average_places > 0.20 and play.wins < 6 or
                        play.total_plays > 600 and play.average_places > 0.15 and play.wins < 8 or
                        play.total_plays > 700 and play.average_places > 0.13 and play.wins < 10 or
                        play.total_plays > 800 and play.average_places > 0.12 and play.wins < 12):

                    indexes_to_delete += [index]
                    remove(f'play/{play.generation}/{play.exemplar}')

                    Debug.play_manager(f'Delete bad play gen {play.generation} '
                                       f'ex {play.exemplar} after {play.total_plays} games '
                                       f'wins {play.wins} avg {int(play.average_places * 1000)}')

            for index in reversed(indexes_to_delete):
                NameManager.add_name(PlayManager._bank_of_plays[index].name)
                del PlayManager._bank_of_plays[index]

            PlayManager.fill_zero_gens()

    @staticmethod
    def save_play(play: Play):

        if not PlayManager._initialized:
            PlayManager.init()

        if not PlayManager.EnableShortInit:

            if not exists(f'play/{play.generation}'):
                mkdir(f'play/{play.generation}')

            dump(play, open(f'play/{play.generation}/{play.exemplar}', 'wb'))

    @staticmethod
    def fill_zero_gens():

        if not PlayManager._initialized:
            PlayManager.init()

        if not PlayManager.EnableShortInit:

            zero_plays = [play.exemplar for play in PlayManager._bank_of_plays if play.generation == 0]
            zero_count = len(zero_plays)
            max_exemplar = max(zero_plays) if zero_count > 0 else 0

            to_fill = PlayManager._zero_gen_count - zero_count
            starts_with = max_exemplar + 1

            for curr_ex in range(starts_with, starts_with + to_fill):
                play = Play()
                play.name = NameManager.get_name()
                play.exemplar = curr_ex
                PlayManager._bank_of_plays += [play]
                PlayManager.save_play(play)

    @staticmethod
    def get_play(only_profitable: bool = False) -> Play:

        if not PlayManager._initialized:
            PlayManager.init()

        if len(PlayManager._bank_of_plays) == 0:
            PlayManager.fill_zero_gens()

        if only_profitable:
            best_plays = sorted([play for play in PlayManager._bank_of_plays if play.total_plays > 10],
                                key=lambda p: p.average_places)[:100]

            for play in best_plays:
                if not play.busy:
                    play.busy = True
                    return play

        len_plays = len(PlayManager._bank_of_plays)
        start_index = index = randint(0, len_plays - 1)
        while PlayManager._bank_of_plays[index].busy:
            index = (index + 1) % len_plays
            if index == start_index:
                raise OverflowError('There is no plays available')

        PlayManager._bank_of_plays[index].busy = True
        return PlayManager._bank_of_plays[index]

    @staticmethod
    def standings(count: int = -1):

        if not PlayManager._initialized:
            PlayManager.init()

        if count == -1:
            count = len(PlayManager._bank_of_plays)

        Debug.evolution(f'Top {count} exemplars of evolution:')

        for place, play in enumerate(sorted([play for play in PlayManager._bank_of_plays if play.total_plays > 100],
                                            key=lambda p: p.average_places / (1 + p.wins * 100 / p.total_plays +
                                                                              p.total_plays / 1000))[:count]):
            Debug.evolution(f'{place + 1}) {play}')


class NameManager:

    Names = List[str]

    FreeNames = []
    BusyNames = []
    _length = 0
    _initialized = False
    _free_nicks_path = 'nicks/free.txt'
    _busy_nicks_path = 'nicks/busy.txt'

    @staticmethod
    def init():

        NameManager.FreeNames = open(NameManager._free_nicks_path).read().split()
        NameManager.BusyNames = open(NameManager._busy_nicks_path).read().split()
        NameManager._length = len(NameManager.FreeNames)
        NameManager._initialized = True

    @staticmethod
    def get_name():

        if not NameManager._initialized:
            NameManager.init()

        if NameManager._length > 0:

            random_index = randint(0, NameManager._length - 1)
            random_name = NameManager.FreeNames[random_index]

            del NameManager.FreeNames[random_index]
            NameManager.BusyNames += [random_name]

            NameManager._length -= 1
            NameManager.save()

            return random_name

        else:
            raise IndexError("Out of free unique names")

    @staticmethod
    def add_name(name):

        if not NameManager._initialized:
            NameManager.init()

        if name not in NameManager.FreeNames:

            if name in NameManager.BusyNames:

                del NameManager.BusyNames[NameManager.BusyNames.index(name)]
                NameManager.FreeNames += [name]

                NameManager._length += 1
                NameManager.save()

                return

            else:
                raise IndexError('This name was not busy')

        else:
            raise IndexError("Trying to add name that already exists as free")

    @staticmethod
    def save():

        if not NameManager._initialized:
            NameManager.init()

        open(NameManager._free_nicks_path, 'w').write('\n'.join(NameManager.FreeNames))
        open(NameManager._busy_nicks_path, 'w').write('\n'.join(NameManager.BusyNames))


class Player:

    class History:

        Decisions = List[BasePlay.DecisionType]

        def __init__(self):

            self.preflop: BasePlay.DecisionType = None
            self.flop: BasePlay.DecisionType = None
            self.turn: BasePlay.DecisionType = None
            self.river: BasePlay.DecisionType = None

        def drop(self) -> None:

            self.preflop: BasePlay.DecisionType = None
            self.flop: BasePlay.DecisionType = None
            self.turn: BasePlay.DecisionType = None
            self.river: BasePlay.DecisionType = None

        @staticmethod
        def decide(curr: BasePlay.DecisionType, decision: BasePlay.DecisionType) -> BasePlay.DecisionType:

            if curr is None:
                if decision == BasePlay.Decision.Fold:
                    return BasePlay.Decision.CheckFold

                return decision

            else:

                if decision == BasePlay.Decision.Fold and curr == BasePlay.Decision.Check:
                    return BasePlay.Decision.CheckFold

                elif decision == BasePlay.Decision.Fold and (curr == BasePlay.Decision.CheckCall or
                                                             curr == BasePlay.Decision.CallR or
                                                             curr == BasePlay.Decision.Call3 or
                                                             curr == BasePlay.Decision.Call4):
                    return BasePlay.Decision.CallFold

                elif decision == BasePlay.Decision.Fold and curr == BasePlay.Decision.Bet:
                    return BasePlay.Decision.BetFold

                elif decision == BasePlay.Decision.Fold and (curr == BasePlay.Decision.Raise or
                                                             curr == BasePlay.Decision.Bet3 or
                                                             curr == BasePlay.Decision.Bet4 or
                                                             curr == BasePlay.Decision.CheckRaise):
                    return BasePlay.Decision.RaiseFold

                elif curr == BasePlay.Decision.Check and (decision == BasePlay.Decision.CheckCall or
                                                          decision == BasePlay.Decision.CallR or
                                                          decision == BasePlay.Decision.Call3 or
                                                          decision == BasePlay.Decision.Call4 or
                                                          decision == BasePlay.Decision.CallA):
                    return decision

                elif curr == BasePlay.Decision.Check and (decision == BasePlay.Decision.Raise or
                                                          decision == BasePlay.Decision.Bet3 or
                                                          decision == BasePlay.Decision.Bet4):
                    return BasePlay.Decision.CheckRaise

                elif curr == BasePlay.Decision.Check and decision == BasePlay.Decision.Allin:
                    return BasePlay.Decision.CheckAllin

                elif curr == BasePlay.Decision.Bet and (decision == BasePlay.Decision.Bet3 or
                                                        decision == BasePlay.Decision.Bet4 or
                                                        decision == BasePlay.Decision.Allin or
                                                        decision == BasePlay.Decision.CallR or
                                                        decision == BasePlay.Decision.Call3 or
                                                        decision == BasePlay.Decision.Call4 or
                                                        decision == BasePlay.Decision.CallA):
                    return decision

                elif curr == BasePlay.Decision.CheckRaise and (decision == BasePlay.Decision.Bet4 or
                                                               decision == BasePlay.Decision.Call3 or
                                                               decision == BasePlay.Decision.Call4):
                    return BasePlay.Decision.CheckRaise

                elif curr == BasePlay.Decision.CheckRaise and (decision == BasePlay.Decision.Allin or
                                                               decision == BasePlay.Decision.CallA):
                    return BasePlay.Decision.CheckAllin

                elif curr == BasePlay.Decision.Raise and (decision == BasePlay.Decision.Bet4 or
                                                          decision == BasePlay.Decision.Allin or
                                                          decision == BasePlay.Decision.Call3 or
                                                          decision == BasePlay.Decision.Call4 or
                                                          decision == BasePlay.Decision.CallA):
                    return decision

                elif curr == BasePlay.Decision.Bet3 and (decision == BasePlay.Decision.Bet4 or
                                                         decision == BasePlay.Decision.Allin or
                                                         decision == BasePlay.Decision.Call4 or
                                                         decision == BasePlay.Decision.CallA):
                    return decision

                elif curr == BasePlay.Decision.Bet4 and (decision == BasePlay.Decision.Bet4 or
                                                         decision == BasePlay.Decision.Allin or
                                                         decision == BasePlay.Decision.Call4 or
                                                         decision == BasePlay.Decision.CallA):
                    return decision

                elif curr == BasePlay.Decision.CheckCall and (decision == BasePlay.Decision.CallR or
                                                              decision == BasePlay.Decision.Call3 or
                                                              decision == BasePlay.Decision.Call4):
                    return decision

                elif curr == BasePlay.Decision.CheckCall and (decision == BasePlay.Decision.Bet3 or
                                                              decision == BasePlay.Decision.Bet4):
                    return BasePlay.Decision.CheckRaise

                elif curr == BasePlay.Decision.CheckCall and (decision == BasePlay.Decision.Allin or
                                                              decision == BasePlay.Decision.CallA):
                    return BasePlay.Decision.CheckAllin

                elif curr == BasePlay.Decision.CallR and (decision == BasePlay.Decision.Call3 or
                                                          decision == BasePlay.Decision.Call4):
                    return decision

                elif curr == BasePlay.Decision.CallR and decision == BasePlay.Decision.Bet4:
                    return BasePlay.Decision.CheckRaise

                elif curr == BasePlay.Decision.CallR and (decision == BasePlay.Decision.Allin or
                                                          decision == BasePlay.Decision.CallA):
                    return BasePlay.Decision.CheckAllin

                elif curr == BasePlay.Decision.Call3 and (decision == BasePlay.Decision.Call4 or
                                                          decision == BasePlay.Decision.Check):
                    return decision

                elif curr == BasePlay.Decision.Call3 and decision == BasePlay.Decision.Bet4:
                    return BasePlay.Decision.CheckRaise

                elif curr == BasePlay.Decision.Call3 and (decision == BasePlay.Decision.Allin or
                                                          decision == BasePlay.Decision.CallA):
                    return BasePlay.Decision.CheckAllin

                elif curr == BasePlay.Decision.Call4 and decision == BasePlay.Decision.Call4:
                    return decision

                elif curr == BasePlay.Decision.Call4 and decision == BasePlay.Decision.Bet4:
                    return BasePlay.Decision.CheckRaise

                elif curr == BasePlay.Decision.Call4 and (decision == BasePlay.Decision.Allin or
                                                          decision == BasePlay.Decision.CallA):
                    return BasePlay.Decision.CheckAllin

                else:
                    raise ValueError(f'Undefined behavior curr = {curr} decision = {decision}')

        def set(self, step: BasePlay.StepType, result: BasePlay.ResultType,
                raise_counter: int, all_in: bool) -> None:

            if result == BasePlay.Result.Fold:
                decision = BasePlay.Decision.Fold

            elif result == BasePlay.Result.Check:
                decision = BasePlay.Decision.Check

            elif result == BasePlay.Result.Call:
                if all_in:
                    decision = BasePlay.Decision.CallA

                elif raise_counter == 1:
                    decision = BasePlay.Decision.CheckCall

                elif raise_counter == 2:
                    decision = BasePlay.Decision.CallR

                elif raise_counter == 3:
                    decision = BasePlay.Decision.Call3

                elif raise_counter >= 4:
                    decision = BasePlay.Decision.Call4

                else:
                    raise ValueError('Wrong call decision when raise counter == 0')

            elif result == BasePlay.Result.Raise:
                if raise_counter == 0:
                    decision = BasePlay.Decision.Bet

                elif raise_counter == 1:
                    decision = BasePlay.Decision.Raise

                elif raise_counter == 2:
                    decision = BasePlay.Decision.Bet3

                elif raise_counter >= 3:
                    decision = BasePlay.Decision.Bet4

                else:
                    raise ValueError('Wrong raise counter')

            elif result == BasePlay.Result.Allin:
                decision = BasePlay.Decision.Allin

            else:
                raise ValueError(f'Wrong result id {result}')

            if step == BasePlay.Step.Preflop:
                self.preflop = self.decide(self.preflop, decision)

            elif step == BasePlay.Step.Flop:
                self.flop = self.decide(self.flop, decision)

            elif step == BasePlay.Step.Turn:
                self.turn = self.decide(self.turn, decision)

            elif step == BasePlay.Step.River:
                self.river = self.decide(self.river, decision)

            else:
                raise ValueError(f'Undefined step id {step}')

    def __init__(self, _id: int, name: str, money: int, controlled: bool):

        self.id: int = _id
        self.name: str = name
        self.money: int = money
        self.money_last_time: int = money
        self.gived: int = 0
        self.in_pot: int = 0
        self.wins: int = 0
        self.in_game: bool = False
        self.in_play: bool = True
        self.re_seat: Players = None
        self.cards: CardsPair = CardsPair()
        self.history: Player.History = Player.History()
        self.hand: Poker.Hand = None
        self.controlled: bool = controlled
        self.lose_time: int = None

        if not self.controlled:
            self.play: Play = PlayManager.get_play()
            self.name: str = str(self.play)

        else:
            self.play: Play = Play()
            self.network: Network = Network('py', self.name)

    def __str__(self):

        return f'player {self.name} with {self.money} stack and {self.get_cards()}'

    def get_cards(self) -> str:

        return str(self.cards)

    def pay(self, money: int) -> int:

        self.money -= money - self.gived
        self.gived = money

        return money

    def pay_blind(self, money: int) -> int:

        return self.pay(min(money, self.money))

    def pay_ante(self, money: int) -> int:

        self.pay(min(money, self.money))
        return self.move_money_to_pot()

    def move_money_to_pot(self) -> int:

        self.in_pot += self.gived
        paid = self.gived
        self.gived = 0
        return paid

    def drop_cards(self) -> None:

        self.cards.drop()

    def fold(self) -> None:

        self.drop_cards()
        self.in_game = False

    def remaining_money(self) -> int:

        return self.money + self.gived

    def go_all_in(self) -> int:

        return self.pay(self.remaining_money())

    def in_all_in(self) -> bool:

        return self.in_game and self.money == 0

    def in_game_not_in_all_in(self) -> bool:

        return self.in_game and self.money > 0

    def add_card(self, card: Card) -> None:

        self.cards.set(card)

    def was_resit(self) -> None:

        self.re_seat = None

    def can_resit(self) -> bool:

        return self.re_seat is None

    def wait_to_resit(self) -> bool:

        return self.re_seat is not None

    def win_without_showdown(self, step: BasePlay.StepType) -> None:

        self.play.wins_before_showdown += 1

        if step == BasePlay.Step.Preflop:
            self.play.preflop.wins += 1

        elif step == BasePlay.Step.Flop:
            self.play.flop.wins += 1

        elif step == BasePlay.Step.Turn:
            self.play.turn.wins += 1

        elif step == BasePlay.Step.River:
            self.play.river.wins += 1

        else:
            raise ValueError(f'Undefined step id {step}')

    def save_decisions(self) -> None:

        self.play.total_hands += 1

        for step in BasePlay.Step.GameSteps:

            if step == BasePlay.Step.Preflop:
                curr = self.history.preflop
                play = self.play.preflop

            elif step == BasePlay.Step.Flop:
                curr = self.history.flop
                play = self.play.flop

            elif step == BasePlay.Step.Turn:
                curr = self.history.turn
                play = self.play.turn

            else:
                curr = self.history.river
                play = self.play.river

            if curr is not None:
                play.add(curr)

        self.history.drop()

    def set_lose_time(self, stack: int = 0, place: int = 0) -> None:

        self.lose_time = int(datetime.now().timestamp() * 10 ** 6) * 10 ** 2 + stack * 10 + place

    def decide(self, step: BasePlay.StepType, to_call: int, can_raise_from: int,
               cards: Card.Cards, online: bool) -> BasePlay.ResultType:

        if not self.in_game:
            return BasePlay.Result.DoNotPlay

        if self.money == 0 and self.in_game:
            return BasePlay.Result.InAllin

        if self.controlled:
            return self.input_decision(step, to_call, can_raise_from, cards)

        if step == BasePlay.Step.Preflop:
            curr_play: BasePlay = self.play.preflop

        elif step == BasePlay.Step.Flop:
            curr_play: BasePlay = self.play.flop

        elif step == BasePlay.Step.Turn:
            curr_play: BasePlay = self.play.turn

        elif step == BasePlay.Step.River:
            curr_play: BasePlay = self.play.river

        else:
            raise ValueError(f'Undefined step id {step}')

        if self.remaining_money() > can_raise_from * 3 and random() < curr_play.bluff:
            bluff = int(can_raise_from * (1 + random()))
            self.pay(bluff)
            Debug.decision(f'609 {self.name} raise bluff {bluff}; bluff = {curr_play.bluff}')

            if online:
                sleep(uniform(0.5, uniform(1, 2)))

            return BasePlay.Result.Raise

        probability = Poker.probability(self.cards, cards)

        if probability < curr_play.min_probability_to_play:

            if to_call == 0 or to_call == self.gived:
                Debug.decision(f'617 {self.name} check on low '
                               f'prob = {probability}; '
                               f'bet coefficient = {curr_play.bet} '
                               f'to call = {to_call} self.gived = {self.gived}')

                if online:
                    sleep(uniform(0.5, 1))

                return BasePlay.Result.Check

            else:
                self.fold()
                Debug.decision(f'624 {self.name} fold low probability; '
                               f'prob = {probability}; '
                               f'min = {curr_play.min_probability_to_play}')

                if online:
                    sleep(uniform(0.5, 1))

                return BasePlay.Result.Fold

        if probability > curr_play.min_probability_to_all_in and random() < curr_play.probability_to_all_in:
            self.go_all_in()

            if self.remaining_money() <= to_call:
                Debug.decision(f'630 {self.name} call all in {self.gived} on high '
                               f'prob = {probability}; '
                               f'min = {curr_play.min_probability_to_all_in}')

                if online:
                    sleep(uniform(1, uniform(1.5, 3)))

                return BasePlay.Result.Call

            else:
                Debug.decision(f'631 {self.name} all in {self.gived} on high '
                               f'prob = {probability}; '
                               f'min = {curr_play.min_probability_to_all_in}')

                if online:
                    sleep(uniform(1, uniform(1.5, 3)))

                return BasePlay.Result.Allin

        bet = int(min(probability * curr_play.bet_, 1) * self.remaining_money())

        if bet == self.remaining_money():
            self.go_all_in()

            if self.remaining_money() <= to_call:
                Debug.decision(f'632 {self.name} call all in {self.gived} on high bet '
                               f'prob = {probability}; '
                               f'min = {curr_play.min_probability_to_all_in}')

                if online:
                    sleep(uniform(2, uniform(3, 5)))

                return BasePlay.Result.Call

            else:
                Debug.decision(f'640 {self.name} all in {self.gived} on high bet '
                               f'prob = {probability}; '
                               f'bet coefficient = {curr_play.bet}')

                if online:
                    sleep(uniform(2, uniform(3, 5)))

                return BasePlay.Result.Allin

        if to_call > bet:

            if to_call == 0 or self.gived == to_call:
                Debug.decision(f'643 {self.name} check while can not raise bet = {bet}')

                if online:
                    sleep(uniform(0.5, uniform(1, 3)))

                return BasePlay.Result.Check

            else:
                self.fold()
                Debug.decision(f'647 {self.name} fold on low bet '
                               f'prob = {probability}; '
                               f'bet coefficient = {curr_play.bet} '
                               f'bet = {bet}')

                if online:
                    sleep(uniform(1, uniform(2, 4)))

                return BasePlay.Result.Fold

        if can_raise_from > bet:

            if to_call == 0 or self.gived == to_call:
                Debug.decision(f'656 {self.name} check on mid bet '
                               f'prob = {probability}; '
                               f'bet coefficient = {curr_play.bet} '
                               f'bet = {bet}')

                if online:
                    sleep(uniform(0.5, uniform(1, 2)))

                return BasePlay.Result.Check

            else:
                self.pay(to_call)
                Debug.decision(f'666 {self.name} call {to_call} on mid bet '
                               f'prob = {probability}; '
                               f'bet coefficient = {curr_play.bet} '
                               f'bet = {bet}')

                if online:
                    sleep(uniform(2, uniform(4, 6)))

                return BasePlay.Result.Call

        else:

            raise_bet = int(min(probability * curr_play.bet_ * curr_play.reduced_raise, 1) * self.remaining_money())

            if raise_bet <= self.gived:

                if to_call == 0 or self.gived == to_call:
                    Debug.decision(f'670 {self.name} check while thinks about raise {raise_bet}')

                    if online:
                        sleep(uniform(1, uniform(2, 3)))

                    return BasePlay.Result.Check

                else:
                    self.fold()
                    Debug.decision(f'672 {self.name} fold while thinks about raise {raise_bet}')

                    if online:
                        sleep(uniform(2, uniform(4, 6)))

                    return BasePlay.Result.Fold

            if raise_bet < to_call:

                if to_call == 0 or self.gived == to_call:
                    Debug.decision(f'673 {self.name} check while thinks about raise {raise_bet}')

                    if online:
                        sleep(uniform(1, uniform(2, 3)))

                    return BasePlay.Result.Check

                else:
                    self.fold()
                    Debug.decision(f'677 {self.name} fold while thinks about raise {raise_bet}')

                    if online:
                        sleep(uniform(2, uniform(4, 6)))

                    return BasePlay.Result.Fold

            if raise_bet < can_raise_from:

                if to_call == 0 or to_call == self.gived:
                    Debug.decision(f'656 {self.name} check while thinks about raise {raise_bet}')

                    if online:
                        sleep(uniform(0.5, uniform(1, 2)))

                    return BasePlay.Result.Check

                else:
                    self.pay(to_call)
                    Debug.decision(f'682 {self.name} call {to_call} while thinks about raise {raise_bet}')

                    if online:
                        sleep(uniform(3, uniform(6, 8)))

                    return BasePlay.Result.Call

            if raise_bet == self.remaining_money():

                self.go_all_in()

                if raise_bet <= to_call:
                    Debug.decision(f'684 {self.name} call all in {self.gived}')

                    if online:
                        sleep(uniform(2, uniform(4, 6)))

                    return BasePlay.Result.Call

                else:
                    Debug.decision(f'687 {self.name} all in {self.gived} while thinks about raise {raise_bet}')

                    if online:
                        sleep(uniform(1, uniform(2, 3)))

                    return BasePlay.Result.Allin

            if to_call == 0 and random() < curr_play.check_:
                Debug.decision(f'690 {self.name} cold check wanted to raise {raise_bet} '
                               f'check probability {curr_play.check}')

                if online:
                    sleep(uniform(0.5, uniform(1, 2)))

                return BasePlay.Result.Check

            elif to_call != 0 and random() < curr_play.call:

                if self.remaining_money() <= to_call:
                    self.go_all_in()
                    Debug.decision(f'691 {self.name} cold call all in {self.gived}')

                    if online:
                        sleep(uniform(2, uniform(4, 6)))

                    return BasePlay.Result.Call

                else:
                    self.pay(to_call)
                    Debug.decision(f'692 {self.name} cold call {to_call} while wanted to raise {raise_bet} '
                                   f'call probability {curr_play.call}')

                    if online:
                        sleep(uniform(2, uniform(4, 6)))

                    return BasePlay.Result.Call

            if self.remaining_money() <= raise_bet:

                self.go_all_in()

                if self.remaining_money() <= to_call:
                    Debug.decision(f'693 {self.name} call all in {self.gived}')

                    if online:
                        sleep(uniform(2, uniform(4, 6)))

                    return BasePlay.Result.Call

                else:
                    Debug.decision(f'694 {self.name} raise all in {self.gived}')

                    if online:
                        sleep(uniform(2, uniform(4, 6)))

                    return BasePlay.Result.Allin

            else:
                self.pay(raise_bet)
                Debug.decision(f'695 {self.name} raise {raise_bet} on high bet '
                               f'prob = {probability}; '
                               f'bet coefficient = {curr_play.bet} '
                               f'bet = {bet}')

                if online:
                    sleep(uniform(3, uniform(6, 9)))

                return BasePlay.Result.Raise

    def input_decision(self, step: BasePlay.StepType, to_call: int, min_raise: int, cards: Card.Cards) \
            -> BasePlay.ResultType:

        Debug.input_decision()
        Debug.input_decision(f'you have {self.get_cards()}')
        if step != BasePlay.Step.Preflop:
            Debug.input_decision(f'on table {Card.str(cards)}')
            Debug.input_decision(f'your combination: {Poker.max_strength(self.cards.get() + cards)}')
        Debug.input_decision(f'probability to win: {Poker.probability(self.cards, cards)}')

        outs, outs_cards = Poker.calculate_outs(self.cards, cards)

        Debug.input_decision(f'outs: {outs} - {" ".join([card.card for card in outs_cards])}')
        Debug.input_decision()

        available_decisions = [(BasePlay.Result.Fold,)]

        Debug.input_decision('1 - fold')
        if self.remaining_money() > to_call:
            if to_call == 0 or self.gived == to_call:
                available_decisions += [(BasePlay.Result.Check,)]
                Debug.input_decision(f'2 - check')
            else:
                available_decisions += [(BasePlay.Result.Call, to_call)]
                Debug.input_decision(f'2 - call {to_call} you called {self.gived} remains {to_call - self.gived}')

            if min_raise < self.remaining_money():
                available_decisions += [(BasePlay.Result.Raise, min_raise, self.remaining_money())]
                Debug.input_decision(f'3 - raise from {min_raise} to {self.remaining_money()}')
            else:
                available_decisions += [(BasePlay.Result.Allin, self.remaining_money())]
                Debug.input_decision(f'3 - all in {self.remaining_money()} you called '
                                     f'{self.gived} remains {self.money}')

        else:
            available_decisions += [(BasePlay.Result.Call, self.remaining_money())]
            Debug.input_decision(f'2 - call all in {self.remaining_money()}')

        while True:
            answer = self.network.input_decision(available_decisions)
            try:
                if answer[0] == '1':
                    self.fold()
                    return BasePlay.Result.Fold

                elif answer[0] == '2':
                    if self.remaining_money() > to_call:
                        if to_call == 0 or self.gived == to_call:
                            return BasePlay.Result.Check
                        else:
                            self.pay(to_call)
                            return BasePlay.Result.Call
                    else:
                        self.go_all_in()
                        return BasePlay.Result.Call

                elif answer[0] == '3':

                    if self.remaining_money() > to_call:

                        if len(answer) == 2:

                            raised_money = int(answer[1])

                            if raised_money == self.remaining_money():
                                self.go_all_in()
                                return BasePlay.Result.Allin

                            if raised_money < min_raise:
                                raise IndexError

                            if raised_money > self.remaining_money():
                                raise IndexError

                            self.pay(raised_money)
                            return BasePlay.Result.Raise

                        else:
                            self.go_all_in()
                            return BasePlay.Result.Allin

            except IndexError:
                continue
            else:
                break

        self.fold()
        return BasePlay.Result.Fold


class Board:

    def __init__(self, deck: Deck, start_hand: int = 0):

        self.flop1: Card = None
        self.flop2: Card = None
        self.flop3: Card = None
        self.turn: Card = None
        self.river: Card = None

        self.deck: Deck = deck

        self.hand: int = start_hand

        self.state: BasePlay.StepType = BasePlay.Step.Preflop

    def clear(self) -> None:

        self.flop1 = None
        self.flop2 = None
        self.flop3 = None
        self.turn = None
        self.river = None

        self.hand += 1

        self.state = BasePlay.Step.Preflop

    def set_flop_cards(self, card1: Card, card2: Card, card3: Card) -> None:

        if self.state == BasePlay.Step.Preflop:
            self.flop1 = card1
            self.flop2 = card2
            self.flop3 = card3
            self.state = BasePlay.Step.Flop
        else:
            raise ValueError('Setting flop cards not in preflop state')

    def open_flop(self) -> None:

        self.deck.skip()
        self.flop1 = self.deck.next()
        self.flop2 = self.deck.next()
        self.flop3 = self.deck.next()
        self.state = BasePlay.Step.Flop

    def open_flop_with_network(self, table) -> None:

        self.open_flop()

        for player in table.players.controlled:
            player.network.flop(self.flop1, self.flop2, self.flop3)

        if table.online:
            table.network.flop(self.flop1, self.flop2, self.flop3)
            sleep(Table.Delay.Flop)

    def set_turn_card(self, card: Card) -> None:

        if self.state == BasePlay.Step.Flop:
            self.turn = card
            self.state = BasePlay.Step.Turn
        else:
            raise ValueError('Setting turn card not in flop state')

    def open_turn(self) -> None:

        self.deck.skip()
        self.turn = self.deck.next()
        self.state = BasePlay.Step.Turn

    def open_turn_with_network(self, table) -> None:

        self.open_turn()

        for player in table.players.controlled:
            player.network.turn(self.turn)

        if table.online:
            table.network.turn(self.turn)
            sleep(Table.Delay.Turn)

    def set_river_card(self, card: Card) -> None:

        if self.state == BasePlay.Step.Turn:
            self.river = card
            self.state = BasePlay.Step.River
        else:
            raise ValueError('Setting river card not in turn state')

    def open_river(self) -> None:

        self.deck.skip()
        self.river = self.deck.next()
        self.state = BasePlay.Step.River

    def open_river_with_network(self, table) -> None:

        self.open_river()

        for player in table.players.controlled:
            player.network.river(self.river)

        if table.online:
            table.network.river(self.river)
            sleep(Table.Delay.River)

    def open(self) -> None:

        if self.state == BasePlay.Step.Preflop:
            self.open_flop()

        elif self.state == BasePlay.Step.Flop:
            self.open_turn()

        elif self.state == BasePlay.Step.Turn:
            self.open_river()

        else:
            raise OverflowError('Board can not contain more than 5 cards')

    def open_with_network(self, table) -> None:

        if self.state == BasePlay.Step.Preflop:
            self.open_flop_with_network(table)

        elif self.state == BasePlay.Step.Flop:
            self.open_turn_with_network(table)

        elif self.state == BasePlay.Step.Turn:
            self.open_river_with_network(table)

        else:
            raise OverflowError('Board can not contain more than 5 cards')

    def open_all(self) -> None:

        if self.state == BasePlay.Step.Preflop:
            self.open_flop()

        if self.state == BasePlay.Step.Flop:
            self.open_turn()

        if self.state == BasePlay.Step.Turn:
            self.open_river()

    def open_all_with_network(self, table) -> None:

        if self.state == BasePlay.Step.Preflop:
            self.open_flop_with_network(table)

        if self.state == BasePlay.Step.Flop:
            self.open_turn_with_network(table)

        if self.state == BasePlay.Step.Turn:
            self.open_river_with_network(table)

    def get(self) -> Card.Cards:

        if self.state == BasePlay.Step.Preflop:
            return []

        elif self.state == BasePlay.Step.Flop:
            return [self.flop1, self.flop2, self.flop3]

        elif self.state == BasePlay.Step.Turn:
            return [self.flop1, self.flop2, self.flop3, self.turn]

        return [self.flop1, self.flop2, self.flop3, self.turn, self.river]

    def __str__(self):

        cards = self.get()
        return Card.str(cards) if cards else 'no cards'


class Players:

    TablePlayers = List[Optional[Player]]

    def __init__(self, seats: int, _id: int):

        self.players: Players.TablePlayers = [None] * seats
        self.controlled: Players.TablePlayers = []
        self.network: Network = None
        self.online: bool = False

        self.id = _id
        self.curr_player: int = -1
        self.curr_seat: int = -1
        self.button: int = -1
        self.wait_to_sit: int = 0
        self.wait_to_leave: int = 0
        self.total_seats: int = seats
        self.count: int = 0
        self.game_without_small_blind: bool = False
        self.lock: Lock = Lock()

    def move_button(self) -> None:

        if self.to_button() is None and self.count == 2:
            self.button = (self.button + 1) % self.total_seats
            while self.players[self.button] is None:
                self.button = (self.button + 1) % self.total_seats

        self.button = (self.button + 1) % self.total_seats
        while self.players[self.button] is None:
            self.button = (self.button + 1) % self.total_seats

    def get_curr_seat(self) -> Player:

        return self.players[self.curr_seat]

    def is_seat_free(self) -> bool:

        return self.players[self.curr_seat] is None

    def is_seat_busy(self) -> bool:

        return self.players[self.curr_seat] is not None

    def get_curr_player(self) -> Player:

        return self.players[self.curr_player]

    def next_seat(self) -> Player:

        self.curr_seat = (self.curr_seat + 1) % self.total_seats
        return self.players[self.curr_seat]

    def next_free_seat(self) -> None:

        self.curr_seat = (self.curr_seat + 1) % self.total_seats
        while self.players[self.curr_seat] is not None:
            self.curr_seat = (self.curr_seat + 1) % self.total_seats

    def next_busy_seat(self) -> Player:

        self.curr_seat = (self.curr_seat + 1) % self.total_seats
        while self.players[self.curr_seat] is None:
            self.curr_seat = (self.curr_seat + 1) % self.total_seats

        return self.players[self.curr_seat]

    def next_player(self) -> Player:

        self.curr_player = (self.curr_player + 1) % self.total_seats
        while self.players[self.curr_player] is None:
            self.curr_player = (self.curr_player + 1) % self.total_seats

        return self.players[self.curr_player]

    def seat_to_player(self) -> Player:

        self.curr_seat = self.curr_player
        return self.players[self.curr_seat]

    def to_button(self) -> Player:

        self.curr_player = self.button
        return self.players[self.curr_player]

    def get_button(self) -> Player:

        return self.players[self.button]

    def to_button_seat(self) -> Player:

        self.curr_seat = self.button
        return self.players[self.curr_seat]

    def to_small_blind(self) -> Player:

        if self.game_without_small_blind:
            raise ValueError('This table play hand without small blind')

        if self.count == 2:
            return self.to_button()
        else:
            self.curr_player = self.button
            return self.next_player()

    def to_big_blind(self) -> Player:

        if self.game_without_small_blind:
            self.to_button()
        else:
            self.to_small_blind()

        return self.next_player()

    def all_players(self) -> Iterator[Player]:

        for player in self.players:
            if player is not None:
                yield player

    def in_game_players(self) -> Iterator[Player]:

        for player in self.all_players():
            if player.in_game:
                yield player

    def not_in_game_players(self) -> Iterator[Player]:

        for player in self.all_players():
            if not player.in_game:
                yield player

    def count_in_game_players(self) -> int:

        count = 0
        for _ in self.in_game_players():
            count += 1
        return count

    def all_in_players(self) -> Iterator[Player]:

        for player in self.all_players():
            if player.in_all_in():
                yield player

    def in_game_not_in_all_in_players(self) -> Iterator[Player]:

        for player in self.all_players():
            if player.in_game_not_in_all_in():
                yield player

    def count_all_in_players(self) -> int:

        count = 0
        for _ in self.all_in_players():
            count += 1
        return count

    def length_to_button(self, player: Player) -> int:

        save_curr_player = self.curr_player
        length = 0

        self.to_button()
        while self.next_player() != player:
            length += 1

        self.curr_player = save_curr_player
        return length

    def sort_by_nearest_to_button(self, players: TablePlayers) -> TablePlayers:

        return sorted(players, key=lambda p: self.length_to_button(p))

    def player_position(self, player: Player) -> str:

        if self.count == 2:
            return 'D/SB' if self.to_button() == player else ' BB '

        curr = self.to_button()
        if player == curr:
            return '  D '

        if not self.game_without_small_blind:
            curr = self.next_player()
            if player == curr:
                return ' SB '

        curr = self.next_player()
        if player == curr:
            return ' BB '

        return '    '

    def sit_player(self, player: Player, from_other_table) -> None:

        if self.is_seat_busy():
            raise IndexError(f'Can not sit {player.name}: on this seat sits {self.get_curr_seat().name}')

        self.players[self.curr_seat] = player

        for curr_player in self.controlled:
            curr_player.network.add_player(player, self.curr_seat)

        if self.online:
            self.network.add_player(player, self.curr_seat)
            sleep(Table.Delay.AddPlayer)

        if player.controlled:
            self.controlled += [player]
            player.network.resit(player, self)

        self.count += 1

        if from_other_table:

            self.wait_to_sit -= 1

            player.re_seat.wait_to_leave -= 1

            player.was_resit()

    def add_player(self, player: Player, from_other_table: bool = True) -> None:

        if self.count == self.total_seats:
            raise OverflowError(f'Can not sit {player.name}: {self.count} sits on this table')

        if from_other_table and self.wait_to_sit == 0:
            raise ValueError(f'Can not sit {player.name}: table was not notified')

        with self.lock:

            if self.count == 0:
                self.button = 0
                self.to_button_seat()
                self.sit_player(player, from_other_table)

            elif self.count == 1:

                self.to_button_seat()
                self.next_free_seat()
                self.sit_player(player, from_other_table)

            else:
                self.to_button_seat()

                for _ in range(2):
                    self.next_seat()
                    while self.is_seat_free():
                        self.next_seat()

                self.next_free_seat()
                self.sit_player(player, from_other_table)

    def remove_player(self, players: 'Players') -> None:

        if self.count == 0:
            raise ValueError('No one to remove')

        self.to_big_blind()

        while self.get_curr_player().wait_to_resit():
            self.next_player()

        self.get_curr_player().re_seat = players

        self.wait_to_leave += 1

        players.wait_to_sit += 1

    def delete_player(self, player: Player) -> None:

        self.players[self.players.index(player)] = None

        if player in self.controlled:
            del self.controlled[self.controlled.index(player)]

        self.count -= 1

        for curr_player in self.controlled:
            curr_player.network.delete_player(player)

        if self.online:
            self.network.delete_player(player)
            sleep(Table.Delay.DeletePlayer)

    def resit_all_needed_players(self) -> None:

        for player in self.all_players():
            if player.wait_to_resit():
                self.delete_player(player)
                player.re_seat.add_player(player)

    def remove_losers(self, game) -> None:

        losers: List[Player] = []

        self.game_without_small_blind = False
        for player in self.all_players():
            if player.money == 0:

                if player == self.to_big_blind() and self.count > 3:
                    self.game_without_small_blind = True

                losers += [player]
                player.in_play = False

            else:
                player.money_last_time = player.money

        loser_stacks = sorted(player.money_last_time for player in losers)
        loser_sits = sorted([self.length_to_button(player) for player in losers], reverse=True)

        for loser in losers:
            loser.set_lose_time(loser_stacks.index(loser.money_last_time),
                                loser_sits.index(self.length_to_button(loser)))

        for loser in losers:

            if loser.controlled:
                loser.network.busted(game.find_place(loser))

            self.delete_player(loser)

        if self.game_without_small_blind and self.count < 3:
            self.game_without_small_blind = False

    def __str__(self):

        return '\n'.join('     Empty seat' if p is None else
                         f'{self.player_position(p)} {p.get_cards()} {p.name} money = {p.money}'
                         for p in self.players)


class Blinds:

    SchemeType = dict

    class Scheme:

        OrderType = List[Tuple[int, int, int]]

        class Order:

            Standard = [(5, 10, 0), (10, 20, 0), (20, 40, 0), (40, 80, 0),
                        (60, 120, 0), (80, 160, 0), (120, 240, 0), (160, 320, 0),
                        (180, 360, 0), (220, 440, 10), (300, 600, 30), (400, 800, 50),
                        (500, 1000, 100), (700, 1400, 200), (1000, 2000, 300),
                        (1500, 3000, 400), (2000, 4000, 500), (3000, 6000, 700),
                        (4000, 8000, 900), (6000, 12000, 1200), (8000, 16000, 1600),
                        (10000, 20000, 2000), (15000, 30000, 3000), (20000, 40000, 4000),
                        (30000, 60000, 6000), (40000, 80000, 8000), (60000, 120000, 12000),
                        (100000, 200000, 20000), (150000, 300000, 30000),
                        (200000, 400000, 50000), (300000, 600000, 80000),
                        (400000, 800000, 120000), (600000, 1200000, 160000),
                        (800000, 1600000, 220000), (1000000, 2000000, 300000)]

        TimeType = int

        class Time:
            Standard = 15
            Fast = 8
            Rapid = 3
            Bullet = 1

        HandsType = int

        class Hands:
            Standard = 75
            Fast = 40
            Rapid = 20
            Bullet = 5

        Standard = {'order': Order.Standard,
                    'time': Time.Standard,
                    'hands': Hands.Standard}

        Fast = {'order': Order.Standard,
                'time': Time.Fast,
                'hands': Hands.Fast}

        Rapid = {'order': Order.Standard,
                 'time': Time.Rapid,
                 'hands': Hands.Rapid}

        Bullet = {'order': Order.Standard,
                  'time': Time.Bullet,
                  'hands': Hands.Bullet}

    def __init__(self, scheme: 'Blinds.SchemeType', game: 'Game'):

        self.game: Game = game
        self.thread: Thread = None

        self.order: Blinds.Scheme.OrderType = scheme['order']
        self.hands: Blinds.Scheme.HandsType = scheme['hands']
        self.time: Blinds.Scheme.TimeType = scheme['time']

        self.curr_round: int = -1
        self.to_next_round: int = 1

        self.small_blind: int = self.order[0][0]
        self.big_blind: int = self.order[0][1]
        self.ante: int = self.order[0][2]

    def set_blinds(self) -> None:

        self.small_blind = self.order[self.curr_round][0]
        self.big_blind = self.order[self.curr_round][1]
        self.ante = self.order[self.curr_round][2]

    def next_hand(self) -> bool:

        self.to_next_round -= 1

        if self.to_next_round == 0 and self.curr_round < len(self.order) - 1:
            self.curr_round += 1
            self.to_next_round = self.hands
            self.set_blinds()
            return True

        return False

    def start(self) -> None:

        self.thread = Thread(target=lambda: self.infinite(), name='Blinds infinite')
        self.thread.start()

    def infinite(self) -> None:

        self.curr_round += 1

        while self.curr_round < len(self.order) - 1 and not self.game.game_finished and not self.game.game_broken:

            sleep(self.time * 60)

            self.curr_round += 1
            self.set_blinds()

            if not self.game.game_finished and not self.game.game_broken:

                self.game.blinds_increased()


class Pot:

    def __init__(self):

        self.money: int = 0

    def __str__(self):

        return str(self.money)


class Table:

    Tables = List['Table']

    class Delay:
        InitHand = 0
        Ante = 0.5
        CollectMoney = 1
        Blinds = 0.5
        BlindsIncreased = 0
        DealCards = 0.5
        DeletePlayer = 0
        AddPlayer = 0
        SwitchDecision = 0
        MadeDecision = 0.1
        ExcessMoney = 0.5
        Flop = 1
        Turn = 1
        River = 1
        OpenCards = 2
        GiveMoney = 2
        MoneyResults = 0
        HandResults = 0
        Clear = 0
        EndOfRound = 1

    class History:

        Decisions = List['Table.History.Decision']

        class Decision:

            def __init__(self, player: Player, decision: BasePlay.ResultType, money: int):

                self.player: Player = player
                self.decision: BasePlay.ResultType = decision
                self.money: int = money

            def __str__(self):
                return f'{self.player.cards} {self.player.id:>3} ' \
                       f'{BasePlay.Result.ToStr[self.decision]:<5} {self.money}'

        Steps = List['Table.History.Step']

        class Step:

            def __init__(self):

                self.decisions: Table.History.Decisions = []

            def add(self, player: Player, decision: BasePlay.ResultType, money: int) -> None:

                self.decisions += [Table.History.Decision(player, decision, money)]

        Hands = List['Table.History.Hands']

        class Hand:

            def __init__(self, number: int):

                self.number = number
                self.opened_cards: Card.Cards = None
                self.dealt_cards: List[Tuple[Player, CardsPair]] = None
                self.last_step: BasePlay.StepType = BasePlay.Step.Preflop

                self.preflop: Table.History.Step = Table.History.Step()
                self.flop: Table.History.Step = None
                self.turn: Table.History.Step = None
                self.river: Table.History.Step = None

            def add(self, player: Player, result: BasePlay.ResultType, money: int) -> None:

                if self.last_step == BasePlay.Step.River:
                    self.river.add(player, result, money)

                elif self.last_step == BasePlay.Step.Turn:
                    self.turn.add(player, result, money)

                elif self.last_step == BasePlay.Step.Flop:
                    self.flop.add(player, result, money)

                elif self.last_step == BasePlay.Step.Preflop:
                    self.preflop.add(player, result, money)

                else:
                    raise OverflowError('Undefined step')

            def give_cards(self, players: Players) -> None:

                self.dealt_cards = []

                for player in players.all_players():
                    self.dealt_cards += [(player, player.cards)]

            def next_step(self) -> None:

                if self.last_step == BasePlay.Step.Turn:
                    self.river = Table.History.Step()
                    self.last_step = BasePlay.Step.River

                elif self.last_step == BasePlay.Step.Flop:
                    self.turn = Table.History.Step()
                    self.last_step = BasePlay.Step.Turn

                elif self.last_step == BasePlay.Step.Preflop:
                    self.flop = Table.History.Step()
                    self.last_step = BasePlay.Step.Flop

                else:
                    raise OverflowError('Can not save more steps')

        def __init__(self, start_hand: int):

            self.number: int = start_hand
            self.curr: Table.History.Hand = Table.History.Hand(start_hand)
            self.hands: Table.History.Hands = []

        def save(self, cards: Card.Cards) -> None:

            self.curr.opened_cards = cards

            self.hands += [self.curr]
            self.number += 1
            self.curr = Table.History.Hand(self.number)

        def next_step(self) -> None:

            self.curr.next_step()

        def deal(self, players: Players) -> None:

            self.curr.give_cards(players)

        def add(self, player: Player, result: BasePlay.ResultType, money: int) -> None:

            self.curr.add(player, result, money)

    def __init__(self, game, _id: int, seats: int, blinds: Blinds, start_hand: int = 1):

        self.game = game
        self.id: int = _id
        self.in_game = False
        self.wait: bool = False
        self.thread: Thread = None
        self.network: Network = None
        self.online: bool = False
        self.first_hand: bool = True
        self.raise_counter: int = 0
        self.lock = Lock()

        self.pot: Pot = Pot()
        self.deck: Deck = Deck()
        self.blinds: Blinds = blinds
        self.board: Board = Board(self.deck, start_hand)
        self.players: Players = Players(seats, _id)
        self.history: Table.History = Table.History(start_hand)

    def __del__(self):

        if self.online:
            del self.network

    def run(self):

        with self.lock:

            self.in_game = True
            self.thread = Thread(target=lambda: self.start_game(), name=f'Table {self.id}')

            if not self.wait:

                if Debug.Table and Debug.Decision and not self.online:
                    self.start_game()
                else:
                    self.thread.start()

    def save_history(self) -> None:

        for player in self.players.all_players():
            player.save_decisions()

        self.history.save(self.board.get())

    def collect_ante(self, ante: int) -> None:

        if self.blinds.ante > 0:

            all_paid = []
            for player in self.players.all_players():
                paid = player.pay_ante(ante)
                self.pot.money += paid
                all_paid += [(player, paid)]
                self.history.add(player, BasePlay.Result.Ante, paid)
                Debug.table(f'Table {self.id} hand {self.board.hand}: player {player.name} paid ante {paid}')

            for player in self.players.controlled:
                player.network.ante(all_paid)

            if self.online:
                self.network.ante(all_paid)
                sleep(Table.Delay.Ante)

            for player in self.players.controlled:
                player.network.collect_money()

            if self.online:
                self.network.collect_money()
                sleep(Table.Delay.CollectMoney)

    def collect_blinds(self, sb: int, bb: int) -> None:

        self.players.to_button_seat()

        if self.players.count == 2:
            player1 = self.players.to_button()
            Debug.table(f'Table {self.id} hand {self.board.hand}: button on {player1.name}')
            paid1 = player1.pay_blind(sb)
            self.history.add(player1, BasePlay.Result.SmallBlind, paid1)
            Debug.table(f'Table {self.id} hand {self.board.hand}: player {player1.name} paid small blind {paid1}')
            player2 = self.players.next_player()
            paid2 = player2.pay_blind(bb)
            self.history.add(player2, BasePlay.Result.BigBlind, paid2)
            Debug.table(f'Table {self.id} hand {self.board.hand}: player {player2.name} paid big blind {paid2}')

            for player in self.players.controlled:
                player.network.blinds(player1, [(player1, paid1), (player2, paid2)])

            if self.online:
                self.network.blinds(player1, [(player1, paid1), (player2, paid2)])
                sleep(Table.Delay.Blinds)

        elif self.players.game_without_small_blind and self.players.next_seat() is None:
            player1 = self.players.to_button()
            Debug.table(f'Table {self.id} hand {self.board.hand}: button on {player1.name}')
            player2 = self.players.next_player()
            paid2 = player2.pay_blind(bb)
            self.history.add(player2, BasePlay.Result.BigBlind, paid2)
            Debug.table(f'Table {self.id} hand {self.board.hand}: player {player2.name} paid big blind {paid2}')

            for player in self.players.controlled:
                player.network.blinds(player1, [(player2, paid2)])

            if self.online:
                self.network.blinds(player1, [(player2, paid2)])
                sleep(Table.Delay.Blinds)

        else:
            player1 = self.players.to_button()
            Debug.table(f'Table {self.id} hand {self.board.hand}: button on {player1.name}')
            player2 = self.players.next_player()
            paid2 = player2.pay_blind(sb)
            self.history.add(player2, BasePlay.Result.SmallBlind, paid2)
            Debug.table(f'Table {self.id} hand {self.board.hand}: player {player2.name} paid small blind {paid2}')
            player3 = self.players.next_player()
            paid3 = player3.pay_blind(bb)
            self.history.add(player3, BasePlay.Result.BigBlind, paid3)
            Debug.table(f'Table {self.id} hand {self.board.hand}: player {player3.name} paid big blind {paid3}')

            for player in self.players.controlled:
                player.network.blinds(player1, [(player2, paid2), (player3, paid3)])

            if self.online:
                self.network.blinds(player1, [(player2, paid2), (player3, paid3)])
                sleep(Table.Delay.Blinds)

    def collect_pot(self) -> None:

        all_paid: int = 0

        print('Collect pot', self.pot.money)

        for player in self.players.all_players():
            paid = player.move_money_to_pot()
            self.pot.money += paid
            all_paid += paid
            Debug.table(f'Table {self.id} hand {self.board.hand}: player {player.name} paid to pot {paid}')
        Debug.table(f'Table {self.id} hand {self.board.hand}: total pot = {self.pot}')

        if all_paid > 0:

            for player in self.players.controlled:
                player.network.collect_money()

            if self.online:
                self.network.collect_money()
                sleep(Table.Delay.CollectMoney)

    def give_cards(self) -> None:

        for player in self.players.all_players():
            player.in_game = True

        self.deck.shuffle()

        button = self.players.to_button_seat()
        for _ in range(2):
            while button != self.players.next_busy_seat():
                self.players.get_curr_seat().add_card(self.deck.next())
            button.add_card(self.deck.next())

        self.players.lock.release()

        self.history.deal(self.players)

        for player in self.players.controlled:
            player.network.give_cards(player)

        if self.online:
            self.network.deal_cards()
            self.network.open_cards(self, True)
            sleep(Table.Delay.DealCards)

    def start_game(self) -> None:

        if self.wait:
            self.in_game = False
            return

        if self.players.count < 2:
            Debug.table(f'Table {self.id} has {self.players.count} player')
            self.in_game = False
            return

        for player in self.players.controlled:
            player.network.init_hand(player, self, self.game)
            player.network.place(self.game.find_place(player))

        if self.online:
            self.network.init_hand(None, self, self.game)
            sleep(Table.Delay.InitHand)

        if not self.first_hand:
            self.players.move_button()
        else:
            self.first_hand = False

        self.players.lock.acquire()

        ante = self.blinds.ante
        sb = self.blinds.small_blind
        bb = self.blinds.big_blind

        self.collect_ante(ante)

        for step in BasePlay.Step.GameSteps:

            if step == BasePlay.Step.Preflop:

                self.collect_blinds(sb, bb)

                self.give_cards()

                Debug.table(self)

                to_call = bb
                self.raise_counter = 1

            else:
                self.players.to_button()
                to_call = 0
                self.raise_counter = 0

            player = self.players.next_player()
            last_seat = player.id
            min_raise = bb
            can_raise_from = to_call + min_raise

            while True:

                if player.money > 0 and player.in_game and self.players.count_in_game_players() > 1 and not (
                            self.players.count_in_game_players() - self.players.count_all_in_players() == 1 and
                            max(p.gived for p in self.players.in_game_not_in_all_in_players()) >=
                            max(p.gived for p in self.players.all_in_players())):

                    for controlled_player in self.players.controlled:
                        controlled_player.network.switch_decision(player)

                    if self.online:
                        self.network.switch_decision(player)
                        sleep(Table.Delay.SwitchDecision)

                    result = player.decide(step, to_call, can_raise_from, self.board.get(), self.online)

                    for controlled_player in self.players.controlled:
                        controlled_player.network.made_decision(player, result)

                    if self.online:
                        self.network.made_decision(player, result)
                        sleep(Table.Delay.MadeDecision)

                    player.history.set(step, result, self.raise_counter, player.in_all_in())
                    self.history.add(player, result, player.gived)

                    if result == BasePlay.Result.Raise or result == BasePlay.Result.Allin:

                        raised = player.gived
                        difference = raised - to_call

                        if difference > 0:
                            last_seat = player.id
                            to_call = raised
                        else:
                            Debug.error('ERROR IN DECISIONS')
                            raise ValueError('Error in decisions: player actually did not raised')

                        if difference >= min_raise:
                            min_raise = difference

                        self.raise_counter += 1
                        can_raise_from = raised + min_raise

                player = self.players.next_player()

                if last_seat == player.id:
                    break

            if self.online:
                sleep(Table.Delay.EndOfRound)

            if self.players.count_in_game_players() == 1:

                player_max_pot = max(p for p in self.players.in_game_players())
                second_max_pot = max(p.gived for p in self.players.all_players() if p != player_max_pot)
                difference = player_max_pot.gived - second_max_pot
                player_max_pot.gived -= difference
                player_max_pot.money += difference

                for controlled_player in self.players.controlled:
                    controlled_player.network.back_excess_money(player_max_pot, difference)

                if self.online:
                    self.network.back_excess_money(player_max_pot, difference)
                    sleep(Table.Delay.ExcessMoney)

                self.history.add(player_max_pot, BasePlay.Result.ReturnMoney, difference)
                Debug.table(f'Table {self.id} hand {self.board.hand}: '
                            f'{difference} money back to {player_max_pot.name}')

                self.collect_pot()

                self.end_game()
                return

            if self.players.count_in_game_players() - self.players.count_all_in_players() <= 1:

                if self.players.count_in_game_players() == self.players.count_all_in_players():
                    max_all_in = sorted(p.gived + p.in_pot for p in self.players.all_players())[-2]
                    max_in_pot = max(p.gived + p.in_pot for p in self.players.in_game_players())

                else:
                    max_all_in = max([p.gived + p.in_pot for p in self.players.all_in_players()] +
                                     [p.gived + p.in_pot for p in self.players.not_in_game_players()])
                    max_in_pot = max(p.gived + p.in_pot for p in self.players.in_game_players())

                if max_in_pot > max_all_in:
                    player_max_pot = max(p for p in self.players.in_game_players()
                                         if p.gived + p.in_pot == max_in_pot)
                    difference = max_in_pot - max_all_in
                    player_max_pot.gived -= difference
                    player_max_pot.money += difference

                    for controlled_player in self.players.controlled:
                        controlled_player.network.back_excess_money(player_max_pot, difference)

                    if self.online:
                        self.network.back_excess_money(player_max_pot, difference)
                        sleep(Table.Delay.ExcessMoney)

                    self.history.add(player, BasePlay.Result.ReturnMoney, difference)
                    Debug.table(f'Table {self.id} hand {self.board.hand}: {difference} money back to {player.name}')

                self.collect_pot()

                for controlled_player in self.players.controlled:
                    controlled_player.network.open_cards(self)

                if self.online:
                    self.network.open_cards(self)
                    sleep(Table.Delay.OpenCards)

                self.board.open_all_with_network(self)
                self.end_game()
                return

            if step == BasePlay.Step.Preflop:
                Debug.table(f'Table {self.id} hand {self.board.hand}: open flop')
            elif step == BasePlay.Step.Flop:
                Debug.table(f'Table {self.id} hand {self.board.hand}: open turn')
            elif step == BasePlay.Step.Turn:
                Debug.table(f'Table {self.id} hand {self.board.hand}: open river')
            elif step == BasePlay.Step.River:
                Debug.table(f'Table {self.id} hand {self.board.hand}: open cards')

                self.collect_pot()

                for controlled_player in self.players.controlled:
                    controlled_player.network.open_cards(self)

                if self.online:
                    self.network.open_cards(self)
                    sleep(Table.Delay.OpenCards)

                self.end_game()
                return

            self.collect_pot()

            self.board.open_with_network(self)
            self.history.next_step()
            Debug.table(f'Table {self.id} hand {self.board.hand}: board {self.board}')

    def give_money(self, winner: Player) -> None:

        winner.in_pot = 0
        winner.money += winner.wins
        self.pot.money -= winner.wins

        self.history.add(winner, BasePlay.Result.WinMoney, winner.wins)

        for controlled_player in self.players.controlled:
            controlled_player.network.give_money(winner, winner.wins)

        if self.online:
            self.network.give_money(winner, winner.wins)
            sleep(Table.Delay.GiveMoney)

        winner.wins = 0
        winner.in_game = False

    def print_result(self) -> None:

        results = []

        for player in self.players.all_players():
            if player.money > player.money_last_time:

                results += [f'{player.name} wins {player.money - player.money_last_time}']

                Debug.table(f'Table {self.id} hand {self.board.hand}: '
                            f'player {player.name} wins {player.money - player.money_last_time} '
                            f'and has {player.money} money')
            elif player.money < player.money_last_time:

                results += [f'{player.name} loses {player.money_last_time - player.money}']

                Debug.table(f'Table {self.id} hand {self.board.hand}: '
                            f'player {player.name} loses {player.money_last_time - player.money} '
                            f'and has {player.money} money')
            else:
                Debug.table(f'Table {self.id} hand {self.board.hand}: player {player.name} has {player.money} money')

        for player in self.players.controlled:
            player.network.money_results(results)

        if self.online:
            self.network.money_results(results)
            sleep(Table.Delay.MoneyResults)

    def take_cards(self) -> None:

        for player in self.players.all_players():
            player.drop_cards()

            if player.controlled:
                player.network.clear()

        if self.online:
            self.network.clear()
            sleep(Table.Delay.Clear)

        self.board.clear()

    def end_game(self) -> None:

        Debug.table(f'Table {self.id} hand {self.board.hand}: cards - {self.board}')

        if self.players.count_in_game_players() == 1:

            for player in self.players.controlled:
                player.network.hand_results(self.board, [])

            if self.online:
                self.network.hand_results(self.board, [])
                sleep(Table.Delay.HandResults)

            winner = max(p for p in self.players.in_game_players())
            winner.wins += winner.in_pot

            winner.win_without_showdown(self.board.state)

            for player in self.players.all_players():
                if player != winner:
                    if winner.in_pot >= player.in_pot:
                        winner.wins += player.in_pot
                        player.in_pot = 0
                    else:
                        Debug.error('THERE IS SOME ERROR')

            self.give_money(winner)

        else:

            self.collect_pot()

            hand_results = []

            for player in self.players.in_game_players():

                player.hand = Poker.max_strength(player.cards.get() + self.board.get())

                hand_results += [(player.hand, player, str(player.hand))]

                Debug.table(f'Table {self.id} hand {self.board.hand}: '
                            f'{player.get_cards()}, {player.name} has {player.hand}')
                player.play.goes_to_showdown += 1

            hand_results.sort(reverse=True, key=lambda x: x[0])

            for player in self.players.controlled:
                player.network.hand_results(self.board, hand_results)

            if self.online:
                self.network.hand_results(self.board, hand_results)
                sleep(Table.Delay.HandResults)

            while self.players.count_in_game_players() > 0:

                wins_hand = max(player.hand for player in self.players.in_game_players())
                players_wins = [p for p in self.players.in_game_players() if p.hand == wins_hand]
                count_winners = len(players_wins)

                for player in players_wins:
                    player.play.wins_after_showdown += 1

                Debug.table(f"Table {self.id} hand {self.board.hand}: "
                            f"{', '.join(p.name for p in players_wins)} wins with {wins_hand}")

                all_inners = [p for p in self.players.all_in_players()]
                undivided_money = 0

                if len(all_inners) > 0:
                    all_inners_wins = sorted([p for p in all_inners if p in players_wins], key=lambda x: x.in_pot)

                    for player in all_inners_wins:

                        side_pot = player.in_pot
                        Debug.table(f'Table {self.id} hand {self.board.hand}: '
                                    f'{player.name} opened pot with {player.in_pot}')

                        for opponent in self.players.all_players():
                            if opponent != player:
                                give_away = min(player.in_pot, opponent.in_pot)
                                Debug.table(f'Table {self.id} hand {self.board.hand}: '
                                            f'{opponent.name} moved to pot {give_away}')
                                side_pot += give_away
                                opponent.in_pot -= give_away

                        win_for_everyone = side_pot / count_winners
                        if win_for_everyone % 1 != 0:
                            undivided_money = round((win_for_everyone % 1) * count_winners)

                        win_for_everyone = int(win_for_everyone)

                        if undivided_money > 0:

                            for lucky_man in self.players.sort_by_nearest_to_button(players_wins):
                                lucky_man.wins += 1
                                undivided_money -= 1

                                if undivided_money == 0:
                                    break

                        for winner in players_wins:
                            winner.wins += win_for_everyone
                            Debug.table(f'Table {self.id} hand {self.board.hand}: '
                                        f'{winner.name} took {winner.wins} money from pot')

                        self.give_money(player)

                        del players_wins[players_wins.index(player)]
                        count_winners -= 1

                if count_winners > 0:

                    main_pot = sum(p.in_pot for p in players_wins)
                    Debug.table(f'Table {self.id} hand {self.board.hand}: '
                                f'{" ".join(p.name for p in players_wins)} opened main pot with '
                                f'{main_pot // len(players_wins)} each and sum {main_pot}')

                    for player in self.players.all_players():
                        if player not in players_wins:
                            Debug.table(f'Table {self.id} hand {self.board.hand}: '
                                        f'{player.name} move {player.in_pot} in main pot')
                            main_pot += player.in_pot
                            player.in_pot = 0
                            player.in_game = False

                    win_for_everyone = main_pot / count_winners
                    if win_for_everyone % 1 != 0:
                        undivided_money = round((win_for_everyone % 1) * count_winners)

                    win_for_everyone = int(win_for_everyone)

                    if undivided_money > 0:

                        for lucky_man in self.players.sort_by_nearest_to_button(players_wins):
                            lucky_man.wins += 1
                            undivided_money -= 1

                            if undivided_money == 0:
                                break

                    for winner in players_wins:
                        Debug.table(f'Table {self.id} hand {self.board.hand}: '
                                    f'{winner.name} took {win_for_everyone} money from main pot')
                        winner.wins += win_for_everyone
                        self.give_money(winner)

                for player in self.players.in_game_players():
                    if player.in_pot == 0:
                        player.in_game = False

        self.save_history()
        self.print_result()

        if self.pot.money != 0:
            Debug.error('ERROR IN POT')
            raise ValueError(f"POT != 0 pot = {self.pot.money}")

        self.players.remove_losers(self.game)
        self.take_cards()

        for player in self.players.all_players():
            if player.in_pot != 0:
                raise ValueError(f"POT != 0 on {player.name} POT = {player.in_pot}")

            if player.in_game:
                raise ValueError(f"{player.name} IN GAME AFTER ALL")

            if player.gived != 0:
                raise ValueError(f"GIVED != 0 on {player.name} gived = {player.gived}")

            if player.wins != 0:
                raise ValueError(f"WINS != 0 on {player.name} wins = {player.wins}")

        self.in_game = False

    def __str__(self):

        return f'Table {self.id} hand {self.board.hand}:\n{self.players}'


class Game:

    def __init__(self, players: int = 9, seats: int = 9, start_stack: int = 1000,
                 blinds: Blinds.SchemeType = Blinds.Scheme.Standard):

        if players < 1:
            raise ValueError("Can not be players less than one in new game")

        self.next_id: int = 0
        self.thread: Thread = None
        self.resitting_thread: Thread = None
        self.game_started: bool = False
        self.game_finished: bool = False
        self.game_broken: bool = False
        self.online: bool = False
        self.start_stack: int = start_stack
        self.total_players: int = players
        self.total_seats: int = seats
        self.total_tables: int = (players - 1) // seats + 1
        self.players_count: int = 0
        self.players: Players.TablePlayers = []
        self.blinds: Blinds = Blinds(blinds, self)

        if self.total_tables == 1:
            self.tables: Table.Tables = [Table(self, 0, seats, self.blinds)]

        else:
            self.tables: Table.Tables = [Table(self, _id, seats, self.blinds) for _id in range(1, self.total_tables+1)]
            self.final_table = Table(self, 0, self.total_seats, self.blinds)

        self.average_stack: int = None
        self.players_left: int = None
        self.top_9: Players.TablePlayers = None

    def add_player(self, name: str = '') -> bool:

        if self.players_count == self.total_players:
            raise OverflowError(f'Player limit reached max = {self.total_players}')

        controlled = False
        if name:
            controlled = True

        player = Player(self.next_id, name, self.start_stack, controlled)
        self.next_id += 1

        self.players += [player]
        self.players_count += 1

        if self.players_count == self.total_players:
            self.thread = Thread(target=lambda: self.start_game(), name='Game infinite')
            self.thread.start()
            return True

        return False

    def delete_player(self, name) -> None:

        if name in [player.name for player in self.players]:

            player_to_delete = max(player for player in self.players if name == player.name)

            del self.players[self.players.index(player_to_delete)]
            del player_to_delete

            self.players_count -= 1

    def start_game(self) -> None:

        shuffle(self.players)
        for player in self.players:
            min_count_players_on_table = min(table.players.count for table in self.tables)
            tables_with_min_count = [table for table in self.tables if
                                     table.players.count == min_count_players_on_table]
            found_table: Table = choice(tables_with_min_count)
            found_table.players.add_player(player, False)

        if any(player.controlled for player in self.players):

            self.online = True
            Play.ExtendedName = False

            for table in self.tables:

                table.network = Network('tb', str(table.id))
                table.online = True

                table.players.network = table.network
                table.players.online = True

        else:
            Play.ExtendedName = True

        self.game_started = True

        self.infinite()

    def do_one_hand(self) -> None:

        if self.blinds.next_hand():
            Debug.game_progress(f'Blinds are: {self.blinds.small_blind} {self.blinds.big_blind} {self.blinds.ante}')

        Debug.game_progress(f'Start hand {self.tables[0].board.hand} tables = {len(self.tables)} '
                            f'players = {sum(table.players.count for table in self.tables)}')

        for table in self.tables:
            table.run()

    def blinds_increased(self):

        Debug.game_progress(f'Blinds are: {self.blinds.small_blind} {self.blinds.big_blind} {self.blinds.ante}')

        sb = self.blinds.small_blind
        bb = self.blinds.big_blind
        ante = self.blinds.ante

        for table in self.tables:

            for player in table.players.controlled:
                player.network.blinds_increased(sb, bb, ante)

            if table.online:
                table.network.blinds_increased(sb, bb, ante)
                sleep(Table.Delay.BlindsIncreased)

    @staticmethod
    def get_first_free_table(tables: Table.Tables) -> Table:

        while True:

            for table in tables:

                    if table.in_game or table.wait:
                        continue

                    else:
                        with table.lock:

                            table.wait = True
                            return table
            sleep(0.01)

    def resit_players(self) -> None:

        total_players = sum(table.players.count for table in self.tables)

        if self.total_seats * len(self.tables) - total_players >= self.total_seats:
            Debug.resitting(f'Start to delete tables total tables = {len(self.tables)} '
                            f'seats = {self.total_seats * len(self.tables)} '
                            f'players = {total_players} '
                            f'difference = {self.total_seats * len(self.tables) - total_players}')

        while self.total_seats * len(self.tables) - total_players >= self.total_seats:

            if len(self.tables) == 2:

                self.tables[0].wait = True
                self.tables[1].wait = True

                while self.tables[0].in_game or self.tables[1].in_game:
                    sleep(0.01)

                if self.tables[0].online:
                    self.tables[0].network.end()

                if self.tables[1].online:
                    self.tables[1].network.end()

                last_players = [player for table in self.tables for player in table.players.all_players()]
                shuffle(last_players)
                final_table = self.final_table
                for player in last_players:
                    final_table.players.add_player(player, False)

                if self.online:
                    final_table.network = Network('tb', '0')
                    final_table.online = True
                    final_table.players.network = final_table.network
                    final_table.players.online = True

                Debug.resitting('Resit all players to final table')

                self.tables = [final_table]
                return

            if self.online:
                table_to_remove: Table = self.get_first_free_table(self.tables)

            else:
                table_to_remove: Table = choice(self.tables)

            while table_to_remove.in_game:
                sleep(0.01)

            while table_to_remove.players.count:

                other_min_count = min(table.players.count for table in self.tables if table != table_to_remove)

                other_tables_with_min_count = [table for table in self.tables if table != table_to_remove and
                                               table.players.count == other_min_count]

                table_to_resit: Table = choice(other_tables_with_min_count)

                Debug.resitting(f'Resit player from removing table {table_to_remove.id} '
                                f'count = {table_to_remove.players.count}'
                                f' to table {table_to_resit.id} count = {table_to_resit.players.count}')

                table_to_remove.players.remove_player(table_to_resit.players)
                table_to_remove.players.resit_all_needed_players()

            if table_to_remove.players.count != 0:
                raise ValueError(f'Try to delete table {table_to_remove.id} with players in it')

            Debug.resitting(f'Delete table {table_to_remove.id}')

            del self.tables[self.tables.index(table_to_remove)]

            if table_to_remove.online:
                table_to_remove.network.end()

            del table_to_remove

            if self.online:
                return

        counts = [table.players.count for table in self.tables]
        max_counts = max(counts)
        min_counts = min(counts)

        if max_counts - min_counts > 1:
            Debug.resitting(f'Start to resit without deleting tables max = {max_counts} min = {min_counts} '
                            f'players = {sum(counts)} '
                            f'difference = {self.total_seats * len(self.tables) - sum(counts)}')

        while max_counts - min_counts > 1:

            tables_with_max_count = [table for table in self.tables if table.players.count == max_counts]
            tables_with_min_count = [table for table in self.tables if table.players.count == min_counts]

            table_to_resit: Table = choice(tables_with_min_count)

            if self.online:
                table_from_resit = self.get_first_free_table(tables_with_max_count)

            else:
                table_from_resit: Table = choice(tables_with_max_count)

            Debug.resitting(f'Resit player from table {table_from_resit.id} count = {table_from_resit.players.count}'
                            f' to table {table_to_resit.id} count = {table_to_resit.players.count}')

            table_from_resit.players.remove_player(table_to_resit.players)

            while table_from_resit.in_game:
                sleep(0.01)

            table_from_resit.players.resit_all_needed_players()

            table_from_resit.wait = False

            if self.online:
                return

            counts = [table.players.count for table in self.tables]
            max_counts = max(counts)
            min_counts = min(counts)

    def print_places(self) -> None:

        for player in self.players:
            if player.lose_time is None:
                player.set_lose_time()
                if player.controlled:
                    player.network.win()
                Debug.evolution(f'Game wins {player.name}')

        for place, player in enumerate(sorted(self.players, key=lambda p: p.lose_time, reverse=True)):
            Debug.standings(f'{place+1:>4}) {player.name}')
            if not player.controlled:
                player.play.set_place(place+1, self.players_count)

        self.game_finished = True

    def find_place(self, player: Player) -> int:

        if player.lose_time is not None:

            finished = sorted([player for player in self.players if player.lose_time is not None],
                              key=lambda p: p.lose_time)

            return self.total_players - finished.index(player)

        else:

            remains = sorted([player for player in self.players if player.lose_time is None], reverse=True,
                             key=lambda p: p.money + p.gived + p.in_pot)

            return remains.index(player) + 1

    def curr_standings(self, do_print_standings: bool) -> None:

        players = [player for table in self.tables for player in table.players.all_players()]
        there_is_controlled_player = any(player.controlled for player in players)

        self.average_stack = int(mean([player.money + player.gived + player.in_pot for player in players]))
        self.players_left = len(players)

        sorted_by_stack = sorted(players, key=lambda player: player.money + player.gived + player.in_pot, reverse=True)

        self.top_9 = sorted_by_stack[:9]

        if there_is_controlled_player and do_print_standings:

            Debug.standings(f'Average stack: {self.average_stack}')
            Debug.standings(f'Players left: {self.players_left}')
            Debug.standings(f'Top 10 stacks:')
            Debug.standings('\n'.join(f'{player.name} has {player.money}' for player in self.top_9))

            Debug.standings()
            Debug.standings('\n'.join(f'{player.name} has {player.money} and sits on '
                                      f'{sorted_by_stack.index(player) + 1}'
                                      for player in players if player.controlled))

    def infinite_resitting(self) -> None:

        while not self.game_finished and not self.game_broken:
            try:
                self.resit_players()

            except IndexError:
                Debug.resitting('Cannot resit - index error')

            else:
                sleep(0.01)

    def infinite(self) -> None:

        if self.online:

            self.blinds.start()

            self.resitting_thread = Thread(target=lambda: self.infinite_resitting(), name='Resitting infinite')
            self.resitting_thread.start()

            counter = 0

            while not self.game_broken:

                if counter % 100 == 0:
                    Debug.game_progress(f'Tables = {len(self.tables)} '
                                        f'players = {sum(table.players.count for table in self.tables)}')

                self.curr_standings(counter % 100 == 0)

                for table in self.tables:
                    if not table.in_game and not table.wait:
                        table.run()

                if sum(table.players.count for table in self.tables) == 1:
                    Debug.game_progress('GAME OVER')
                    break

                counter += 1

                sleep(0.1)

        else:

            while not self.game_broken:

                if all(not table.in_game for table in self.tables):

                    self.resit_players()

                    for table in self.tables:
                        if table.players.count > 1:
                            self.do_one_hand()
                            break
                    else:
                        Debug.game_progress('GAME OVER')
                        break

                sleep(0.01)

        if not self.game_broken:

            if self.tables[0].online:
                self.tables[0].network.end()

            self.print_places()
            
        else:
            
            for table in self.tables:
                if table.online:
                    
                    table.online = False
                    table.network.end()

                    for player in table.players.controlled:
                        player.network.socket.close()

                    for player in table.players.all_players():

                        if player.controlled:
                            player.network.socket.close()

                        else:
                            player.play.busy = False

    def break_game(self) -> None:
        self.game_broken = True


class Network:

    if Debug.Debug:
        ip = '127.0.0.1'

    else:
        ip = '188.134.82.95'

    port = 9001

    def __init__(self, _id: str, name: str, is_dummy: bool = False):

        self.is_dummy = is_dummy

        if not is_dummy:
            self.socket = create_connection(f'ws://{Network.ip}:{Network.port}')
            self.socket.send(f'{_id} {name}')

    def __del__(self):

        if not self.is_dummy:
            self.socket.close()

    def send(self, obj: dict) -> Optional[str]:

        if not self.is_dummy:
            if self.socket.connected:
                self.socket.send(dumps(obj))
        else:
            return dumps(obj)

    def send_raw(self, text: str) -> Optional[str]:

        if not self.is_dummy:
            if self.socket.connected:
                self.socket.send(text)
        else:
            return text

    def receive(self) -> dict:

        if self.socket.connected and not self.is_dummy:
            return loads(self.socket.recv())

    def receive_raw(self) -> str:

        if self.socket.connected and not self.is_dummy:
            return self.socket.recv()

    def input_decision(self, available) -> Optional[List[str]]:

        if self.is_dummy:
            return

        self.send_raw('decision')

        to_send = dict()

        to_send['type'] = 'set decision'

        decisions = list()

        for decision in available:

            curr = dict()

            if decision[0] == BasePlay.Result.Fold:
                curr['type'] = 'fold'

            elif decision[0] == BasePlay.Result.Check:
                curr['type'] = 'check'

            elif decision[0] == BasePlay.Result.Call:
                curr['type'] = 'call'
                curr['money'] = decision[1]

            elif decision[0] == BasePlay.Result.Raise:
                curr['type'] = 'raise'
                curr['from'] = decision[1]
                curr['to'] = decision[2]

            elif decision[0] == BasePlay.Result.Allin:
                curr['type'] = 'all in'
                curr['money'] = decision[1]

            else:
                raise ValueError(f'THERE IS ANOTHER DECISION {decision[0]}')

            decisions += [curr]

        to_send['decisions'] = decisions

        self.send(to_send)

        reply = self.receive_raw()

        return reply.split()

    def init_hand(self, player: Optional[Player], table: Table, game: Game) -> Optional[str]:

        self.send_raw('new hand')

        to_send = dict()

        to_send['type'] = 'init hand'
        to_send['table_number'] = table.id
        to_send['seats'] = table.players.total_seats
        to_send['hand_number'] = table.board.hand
        to_send['ante'] = table.blinds.ante
        to_send['sb'] = table.blinds.small_blind
        to_send['bb'] = table.blinds.big_blind
        to_send['avg_stack'] = game.average_stack
        to_send['players_left'] = game.players_left

        top_9 = list()

        for curr_player in game.top_9:
            curr = dict()
            curr['name'] = curr_player.name
            curr['stack'] = curr_player.money + curr_player.gived + curr_player.in_pot
            top_9 += [curr]

        to_send['top_9'] = top_9

        players = list()

        if player is not None:

            for curr_player in table.players.players:
                curr = dict()

                if curr_player is None:
                    curr['id'] = None

                else:
                    curr['id'] = curr_player.id
                    curr['name'] = curr_player.name
                    curr['stack'] = curr_player.money
                    curr['controlled'] = player is curr_player

                players += [curr]

        else:

            for curr_player in table.players.players:
                curr = dict()

                if curr_player is None:
                    curr['id'] = None

                else:
                    curr['id'] = curr_player.id
                    curr['name'] = curr_player.name
                    curr['stack'] = curr_player.money
                    curr['controlled'] = True

                players += [curr]

        to_send['players'] = players

        return self.send(to_send)

    def ante(self, all_paid: List[Tuple[Player, int]]) -> Optional[str]:

        to_send = dict()

        to_send['type'] = 'ante'

        paid_send = list()

        for player, paid in all_paid:
            curr = dict()
            curr['id'] = player.id
            curr['paid'] = paid
            paid_send += [curr]

        to_send['paid'] = paid_send

        return self.send(to_send)

    def collect_money(self) -> Optional[str]:

        return self.send({'type': 'collect money'})

    def blinds(self, button: Player, blind_info: List[Tuple[Player, int]]) -> Optional[str]:

        to_send = dict()

        to_send['type'] = 'blinds'
        to_send['button'] = button.id

        blind_send = list()

        for curr_blind, paid in blind_info:
            curr = dict()
            curr['id'] = curr_blind.id
            curr['paid'] = paid
            blind_send += [curr]

        to_send['info'] = blind_send

        return self.send(to_send)

    def blinds_increased(self, sb: int, bb: int, ante: int) -> Optional[str]:

        to_send = dict()

        to_send['type'] = 'blinds increased'
        to_send['sb'] = sb
        to_send['bb'] = bb
        to_send['ante'] = ante

        return self.send(to_send)

    def give_cards(self, player: Player) -> Optional[str]:

        to_send = dict()

        to_send['type'] = 'give cards'
        to_send['first'] = player.cards.first.card
        to_send['second'] = player.cards.second.card

        return self.send(to_send)

    def deal_cards(self) -> Optional[str]:

        return self.send({'type': 'deal cards'})

    def delete_player(self, player: Player) -> Optional[str]:

        to_send = dict()

        to_send['type'] = 'delete player'
        to_send['id'] = player.id

        return self.send(to_send)

    def add_player(self, player: Player, seat: int) -> Optional[str]:

        to_send = dict()

        to_send['type'] = 'add player'
        to_send['name'] = player.name
        to_send['id'] = player.id
        to_send['stack'] = player.money
        to_send['seat'] = seat

        return self.send(to_send)

    def resit(self, player: Player, players: Players) -> Optional[str]:

        self.send_raw('resit ' + str(players.id))

        to_send = dict()

        to_send['type'] = 'resit'
        to_send['table_number'] = players.id

        players_send = list()

        for curr_player in players.players:
            curr = dict()

            if curr_player is None:
                curr['id'] = None

            else:
                curr['id'] = curr_player.id
                curr['name'] = curr_player.name
                curr['stack'] = curr_player.money
                curr['controlled'] = player is curr_player

            players_send += [curr]

        to_send['players'] = players_send

        return self.send(to_send)

    def switch_decision(self, player: Player) -> Optional[str]:

        to_send = dict()

        to_send['type'] = 'switch decision'
        to_send['id'] = player.id

        return self.send(to_send)

    def made_decision(self, player: Player, decision: BasePlay.ResultType) -> Optional[str]:

        to_send = dict()

        to_send['type'] = 'made decision'

        if decision == BasePlay.Result.Fold:
            to_send['result'] = 'fold'

        elif decision == BasePlay.Result.Check:
            to_send['result'] = 'check'

        elif decision == BasePlay.Result.Call:
            to_send['result'] = 'call'
            to_send['money'] = player.gived

        elif decision == BasePlay.Result.Raise:
            to_send['result'] = 'raise'
            to_send['money'] = player.gived

        elif decision == BasePlay.Result.Allin:
            to_send['result'] = 'all in'
            to_send['money'] = player.gived

        else:
            raise ValueError(f'I FORGOT ABOUT RESULT ID {decision}')

        return self.send(to_send)

    def back_excess_money(self, player: Player, money: int) -> Optional[str]:

        to_send = dict()

        to_send['type'] = 'excess money'
        to_send['id'] = player.id
        to_send['money'] = money

        return self.send(to_send)

    def flop(self, card1: Card, card2: Card, card3: Card) -> Optional[str]:

        to_send = dict()

        to_send['type'] = 'flop'
        to_send['card1'] = card1.card
        to_send['card2'] = card2.card
        to_send['card3'] = card3.card

        return self.send(to_send)

    def turn(self, card: Card) -> Optional[str]:

        to_send = dict()

        to_send['type'] = 'turn'
        to_send['card'] = card.card

        return self.send(to_send)

    def river(self, card: Card) -> Optional[str]:

        to_send = dict()

        to_send['type'] = 'river'
        to_send['card'] = card.card

        return self.send(to_send)

    def open_cards(self, table: Table, for_replay=False) -> Optional[str]:

        if for_replay:
            self.send_raw('open cards replay')

        to_send = dict()

        to_send['type'] = 'open cards'

        cards = list()

        for player in table.players.in_game_players():
            curr = dict()
            curr['id'] = player.id
            curr['card1'] = player.cards.first.card
            curr['card2'] = player.cards.second.card
            cards += [curr]

        to_send['cards'] = cards

        return self.send(to_send)

    def give_money(self, player: Player, money: int) -> Optional[str]:

        to_send = dict()

        to_send['type'] = 'give money'
        to_send['id'] = player.id
        to_send['money'] = money

        return self.send(to_send)

    def money_results(self, results: List[str]) -> Optional[str]:

        to_send = dict()

        to_send['type'] = 'money results'
        to_send['results'] = results

        return self.send(to_send)

    def hand_results(self, board: Board, results: List[Tuple[Poker.Hand, Player, str]]) -> Optional[str]:

        to_send = dict()

        to_send['type'] = 'hand results'

        if board.state == BasePlay.Step.Preflop:
            to_send['flop1'] = 'UP'
            to_send['flop2'] = 'UP'
            to_send['flop3'] = 'UP'
            to_send['turn'] = 'UP'
            to_send['river'] = 'UP'

        elif board.state == BasePlay.Step.Flop:
            to_send['flop1'] = board.flop1.card
            to_send['flop2'] = board.flop2.card
            to_send['flop3'] = board.flop3.card
            to_send['turn'] = 'UP'
            to_send['river'] = 'UP'

        elif board.state == BasePlay.Step.Turn:
            to_send['flop1'] = board.flop1.card
            to_send['flop2'] = board.flop2.card
            to_send['flop3'] = board.flop3.card
            to_send['turn'] = board.turn.card
            to_send['river'] = 'UP'

        elif board.state == BasePlay.Step.River:
            to_send['flop1'] = board.flop1.card
            to_send['flop2'] = board.flop2.card
            to_send['flop3'] = board.flop3.card
            to_send['turn'] = board.turn.card
            to_send['river'] = board.river.card

        else:
            raise OverflowError('Undefined board state')

        results_send = list()

        for hand, player, result in results:

            curr = dict()
            curr['id'] = player.id
            curr['name'] = player.name
            curr['first'] = player.cards.first.card
            curr['second'] = player.cards.second.card
            curr['card1'] = hand.cards[0].card
            curr['card2'] = hand.cards[1].card
            curr['card3'] = hand.cards[2].card
            curr['card4'] = hand.cards[3].card
            curr['card5'] = hand.cards[4].card
            curr['result'] = result

            results_send += [curr]

        to_send['results'] = results_send

        return self.send(to_send)

    def busted(self, place: int) -> None:

        if not self.is_dummy:
            self.send_raw('busted')
            self.send({'type': 'busted', 'place': place})
            self.socket.close()

    def clear(self) -> Optional[str]:

        return self.send({'type': 'clear'})

    def win(self) -> None:

        if not self.is_dummy:
            self.send({'type': 'win'})
            self.socket.close()

    def place(self, place: int) -> Optional[str]:

        return self.send({'type': 'place', 'place': place})

    def end(self) -> Optional[str]:

        return self.send_raw('end')


class PokerGame:

    EventType = int

    class Event:
        Fold = 0
        Call = 1
        Check = 2
        Raise = 3
        Allin = 4
        Ante = 5
        SmallBlind = 6
        BigBlind = 7
        WinMoney = 8
        ReturnMoney = 9
        ChatMessage = 10
        ObserverChatMessage = 11
        Disconnected = 12
        Connected = 13
        FinishGame = 14

        ToStr = {Fold: 'fold',
                 Call: 'call',
                 Check: 'check',
                 Raise: 'raise',
                 Allin: 'all in',
                 Ante: 'ante',
                 SmallBlind: 'sb',
                 BigBlind: 'bb',
                 WinMoney: 'win',
                 ReturnMoney: 'return',
                 ChatMessage: 'chat message',
                 ObserverChatMessage: 'observer message',
                 Disconnected: 'disconnected',
                 Connected: 'connected',
                 FinishGame: 'finished'}

    class MockPlayer:

        class PlayerEvent:

            def __init__(self, event: 'PokerGame.EventType', money: int):
                self.event: PokerGame.EventType = event
                self.money: int = money

        def __init__(self, name: str, money: int, seat: int, is_active: bool):
            self.name: str = name
            self.money: int = money
            self.seat: int = seat
            self.is_active = is_active
            self.is_winner: bool = False
            self.is_loser: bool = False
            self.cards: CardsPair = None
            self.preflop: List['PokerGame.MockPlayer.PlayerEvent'] = []
            self.flop: List['PokerGame.MockPlayer.PlayerEvent'] = []
            self.turn: List['PokerGame.MockPlayer.PlayerEvent'] = []
            self.river: List['PokerGame.MockPlayer.PlayerEvent'] = []

        def get_list(self, step: BasePlay.StepType) -> List['PokerGame.MockPlayer.PlayerEvent']:

            if step == BasePlay.Step.Preflop:
                return self.preflop
            elif step == BasePlay.Step.Flop:
                return self.flop
            elif step == BasePlay.Step.Turn:
                return self.turn
            elif step == BasePlay.Step.River:
                return self.river
            else:
                raise ValueError('No such step id ' + str(step))

        def add_decision(self, step: BasePlay.StepType, event: 'PokerGame.EventType', money: int) -> None:
            self.get_list(step).append(PokerGame.MockPlayer.PlayerEvent(event, money))

        def gived(self, step: BasePlay.StepType) -> int:

            curr_list = self.get_list(step)
            for action in reversed(curr_list):

                if action.event == PokerGame.Event.Check:
                    return 0

                elif action.event == PokerGame.Event.Allin or \
                        action.event == PokerGame.Event.BigBlind or \
                        action.event == PokerGame.Event.SmallBlind or \
                        action.event == PokerGame.Event.Call or \
                        action.event == PokerGame.Event.Raise:
                    return action.money

            return 0

    class ObserverPlayer:
        def __init__(self, name):
            self.name = name

    class PokerEvent:

        def __init__(self, player: Union['PokerGame.MockPlayer', 'PokerGame.ObserverPlayer'],
                     event: 'PokerGame.EventType', money: int, msg: str):
            self.player = player
            self.event: PokerGame.EventType = event
            self.money: int = money
            self.message: str = msg

        def __str__(self) -> str:
            if self.event == PokerGame.Event.Fold or \
                    self.event == PokerGame.Event.Check or \
                    self.event == PokerGame.Event.Disconnected or \
                    self.event == PokerGame.Event.Connected:
                return f'{self.player.name} {PokerGame.Event.ToStr[self.event]}'

            elif self.event == PokerGame.Event.Call or \
                    self.event == PokerGame.Event.Raise or \
                    self.event == PokerGame.Event.Allin or \
                    self.event == PokerGame.Event.Ante or \
                    self.event == PokerGame.Event.SmallBlind or \
                    self.event == PokerGame.Event.BigBlind or \
                    self.event == PokerGame.Event.WinMoney or \
                    self.event == PokerGame.Event.ReturnMoney:
                return f'{self.player.name} {PokerGame.Event.ToStr[self.event]} {self.money}'

            elif self.event == PokerGame.Event.ChatMessage:
                return f'{self.player.name}: {self.message}'

            elif self.event == PokerGame.Event.ObserverChatMessage:
                return f'{self.player.name} [observer]: {self.message}'

            elif self.event == PokerGame.Event.FinishGame:
                return f'{self.player.name} {PokerGame.Event.ToStr[self.event]} ' \
                       f'{self.message} and get {self.money / 100}'

            raise ValueError(f'Do not know how to interpret Event id {self.event}')

    class PokerHand:

        def __init__(self, players: List['PokerGame.MockPlayer']):
            self.id: int = 0
            self.players: List[PokerGame.MockPlayer] = players
            self.sit_during_game: List[PokerGame.MockPlayer] = None
            self.preflop: List[PokerGame.PokerEvent] = []
            self.flop: List[PokerGame.PokerEvent] = []
            self.turn: List[PokerGame.PokerEvent] = []
            self.river: List[PokerGame.PokerEvent] = []
            self.small_blind: int = 0
            self.big_blind: int = 0
            self.ante: int = 0
            self.total_pot: int = 0
            self.board: Board = Board(Deck())
            self.curr_step: BasePlay.StepType = BasePlay.Step.Preflop
            self.curr_events: List[PokerGame.PokerEvent] = self.preflop

        def add_winner(self, name: str) -> None:
            self.get_player(name).is_winner = True

        def get_winners(self) -> List['PokerGame.MockPlayer']:
            return [player for player in self.players if player.is_winner]

        def get_losers(self) -> List['PokerGame.MockPlayer']:
            return [player for player in self.players if player.is_loser]

        def add_loser(self, name: str) -> None:
            self.get_player(name).is_loser = True

        def set_flop_cards(self, card1: Card, card2: Card, card3: Card) -> None:
            self.board.set_flop_cards(card1, card2, card3)

        def set_turn_card(self, card: Card) -> None:
            self.board.set_turn_card(card)

        def set_river_card(self, card: Card) -> None:
            self.board.set_river_card(card)

        def set_cards(self, name: str, cards: CardsPair) -> None:
            player = self.get_player(name)
            if player.cards is None:
                player.cards = cards
            elif player.cards != cards:
                raise ValueError(f'Player {name} firstly has {player.cards} '
                                 f'then {cards} in one hand')

        def get_player(self, name: str) -> 'PokerGame.MockPlayer':
            return max(player for player in self.players if player.name == name)

        def add_decision(self, name: str, event: 'PokerGame.EventType', money: int, msg: str = '') -> None:
            if event == PokerGame.Event.ObserverChatMessage:
                self.curr_events += [PokerGame.PokerEvent(PokerGame.ObserverPlayer(name), event, money, msg)]
            else:
                player = self.get_player(name)
                self.curr_events += [PokerGame.PokerEvent(player, event, money, msg)]
                player.add_decision(self.curr_step, event, money)

        def switch_to_step(self, step: BasePlay.StepType) -> None:

            self.curr_step = step

            if step == BasePlay.Step.Preflop:
                self.curr_events = self.preflop
            elif step == BasePlay.Step.Flop:
                self.curr_events = self.flop
            elif step == BasePlay.Step.Turn:
                self.curr_events = self.turn
            elif step == BasePlay.Step.River:
                self.curr_events = self.river
            else:
                raise ValueError('No such step id ' + str(step))

        def next_decision(self) -> None:
            self.switch_to_step(BasePlay.Step.next_step(self.curr_step))

        def __str__(self) -> str:

            ret = [f'    Small blind: {self.small_blind}']
            ret += [f'    Big blind: {self.big_blind}']
            ret += [f'    Ante: {self.ante}']
            ret += [f'    Total pot: {self.total_pot}']

            ret += ['    Players:']
            for player in self.players:
                ret += [f'        {player.name} : {player.money} : '
                        f'{player.cards if player.cards is not None else "?? ??"} '
                        f'{"disconnected" if not player.is_active else ""}']

            if self.preflop:
                ret += ['    Preflop:']
                for event in self.preflop:
                    ret += [' ' * 8 + str(event)]

            if self.flop:
                ret += [f'    Flop: {self.board.flop1.card} '
                        f'{self.board.flop2.card} '
                        f'{self.board.flop3.card}']
                for event in self.flop:
                    ret += [' ' * 8 + str(event)]

            if self.turn:
                ret += [f'    Turn: {self.board.flop1.card} '
                        f'{self.board.flop2.card} '
                        f'{self.board.flop3.card} '
                        f'{self.board.turn.card}']
                for event in self.turn:
                    ret += [' ' * 8 + str(event)]

            if self.river:
                ret += [f'    River: {self.board.flop1.card} '
                        f'{self.board.flop2.card} '
                        f'{self.board.flop3.card} '
                        f'{self.board.turn.card} '
                        f'{self.board.river.card}']
                for event in self.river:
                    ret += [' ' * 8 + str(event)]

            ret += [f'    Board: {self.board}']

            winners = self.get_winners()
            losers = self.get_losers()

            if winners:
                ret += [f'    Winners:']
                for winner in winners:
                    ret += [' ' * 8 + winner.name]

            if losers:
                ret += [f'    Losers:']
                for loser in losers:
                    ret += [' ' * 8 + loser.name]

            return '\n'.join(ret)

    def __init__(self):
        self.id: int = 0
        self.name: str = ''
        self.date: str = ''
        self.time: str = ''
        self.source: str = ''
        self.hands: List[PokerGame.PokerHand] = []
        self.curr_hand: PokerGame.PokerHand = None

    def add_hand(self, players: List['PokerGame.MockPlayer']):
        new_hand = PokerGame.PokerHand(players)
        self.hands += [new_hand]
        self.curr_hand = new_hand

    def save(self, path: str = '') -> None:

        if path == '':
            path = self.source

        if not exists('games'):
            mkdir('games')

        if not exists('games/parsed'):
            mkdir('games/parsed')

        path = GameParser.path_to_parsed_games + path
        *dirs, file_name = path.split('/')

        dirs = '/'.join(dirs)

        if not exists(dirs):
            makedirs(dirs)

        dump(self, open(path, 'wb'))

    @staticmethod
    def load(path: str) -> 'PokerGame':
        return load(open(GameParser.path_to_parsed_games + path, 'rb'))

    def __str__(self) -> str:
        ret = [f'Poker game of {len(self.hands)} hands']
        i: int = 1
        for hand in self.hands:
            ret += [f'Hand #{i}']
            ret += [str(hand)]
            i += 1
        return '\n'.join(ret)


class GameParser:

    class RegEx:
        name = '[a-zA-Z0-9_\-@\' ]+'

        hand_border = re.compile(r'[*]{11} # [0-9]+ [*]{14}')
        step_border = re.compile(r'[*]{3} [A-Z ]+ [*]{3}')
        hand_and_game_id = re.compile(r'Hand #([0-9]+): Tournament #([0-9]+)')
        name_tournament = re.compile(r'Tournament #[0-9]+, ([^-]*) - Level')
        date_tournament = re.compile(r'- ([0-9]{4}/[0-9]{2}/[0-9]{2}) ([0-9]{1,2}:[0-9]{2}:[0-9]{2})')
        small_and_big_blind = re.compile(r'\(([0-9]+)/([0-9]+)\)')
        player_init = re.compile(r'^Seat ([0-9]+): (' + name + r') \(([0-9]+) in chips\)$')
        player_init_sitting_out = re.compile(r'^Seat ([0-9]+): (' + name + r') \(([0-9]+) in chips\) is sitting out$')
        player_init_out_of_hand = re.compile(r'^Seat ([0-9]+): (' + name + r') \(([0-9]+) in chips\) out of hand \(')
        find_ante = re.compile('^(' + name + r'): posts the ante ([0-9]+)$')
        find_ante_all_in = re.compile('^(' + name + r'): posts the ante ([0-9]+) and is all-in$')
        find_small_blind = re.compile('^(' + name + r'): posts small blind ([0-9]+)$')
        find_small_blind_all_in = re.compile('^(' + name + r'): posts small blind ([0-9]+) and is all-in$')
        find_big_blind = re.compile('^(' + name + r'): posts big blind ([0-9]+)$')
        find_big_blind_all_in = re.compile('^(' + name + r'): posts big blind ([0-9]+) and is all-in$')
        find_dealt_cards = re.compile(r'^Dealt to (' + name + r') \[(..) (..)]$')
        find_action = re.compile('^(' + name + r'): ([a-z0-9 -]+)$')
        find_flop = re.compile(r'\[(..) (..) (..)]$')
        find_turn = re.compile(r'\[.. .. ..] \[(..)]$')
        find_river = re.compile(r'\[.. .. .. ..] \[(..)]$')
        find_shows_in_show_down = re.compile(r'^(' + name + r'): shows \[(..) (..)] \([a-zA-Z0-9, +-]+\)$')
        find_total_pot = re.compile(r'^Total pot ([0-9]+) \| Rake [0-9]+$')
        find_total_pot_with_main_pot = re.compile(r'^Total pot ([0-9]+) Main pot [0-9a-zA-Z. ]+ \| Rake [0-9]+$')
        find_collected_pot_summary = re.compile(r'^Seat [0-9]+: (' + name + r') collected \([0-9]+\)$')
        find_lost = re.compile(r'^Seat [0-9]+: (' + name + r') showed \[(..) (..)] and lost with')
        find_won = re.compile(r'^Seat [0-9]+: (' + name + r') showed \[(..) (..)] and won \([0-9]+\) with')
        find_mucked_cards = re.compile(r'^Seat [0-9]+: (' + name + r') mucked \[(..) (..)]$')

        # for processing actions
        find_uncalled_bet = re.compile(r'^Uncalled bet \(([0-9]+)\) returned to (' + name + r')$')
        find_collect_pot = re.compile(r'^(' + name + r') collected ([0-9]+) from pot$')
        find_collect_side_pot = re.compile(r'^(' + name + r') collected ([0-9]+) from side pot$')
        find_collect_main_pot = re.compile(r'^(' + name + r') collected ([0-9]+) from main pot$')
        find_show_cards = re.compile(r'^(' + name + r'): shows \[([2-9AKQJT hdcs]+)]$')
        find_is_connected = re.compile(r'^(' + name + r') is connected$')
        find_is_disconnected = re.compile(r'^(' + name + r') is disconnected$')
        find_is_sitting_out = re.compile(r'^(' + name + r') is sitting out$')
        find_said = re.compile(r'^(' + name + ') said, "([^\n]+)"$')
        find_observer_said = re.compile(r'^(' + name + ') \[observer] said, "([^\n]+)"$')
        find_finished = re.compile(r'^(' + name + r') finished the tournament in ([0-9]+..) place$')
        find_received = re.compile(r'^(' + name + r') finished the tournament in ([0-9]+..) place '
                                                  r'and received \$([0-9]+\.[0-9]{2})\.$')
        find_winner = re.compile(r'^(' + name + r') wins the tournament and receives '
                                                r'\$([0-9]+\.[0-9]{2}) - congratulations!$')
        find_does_not_show = re.compile(r'^(' + name + '): doesn\'t show hand$')
        find_has_returned = re.compile(r'^(' + name + r') has returned$')
        find_has_timed_out = re.compile(r'^(' + name + r') has timed out$')
        find_timed_disconnected = re.compile(r'^(' + name + r') has timed out while disconnected$')
        find_mucks_hand = re.compile(r'^' + name + r': mucks hand$')
        find_fold_showing_cards = re.compile(r'^(' + name + r'): folds \[([2-9AKQJT hdcs]+)]$')

    path_to_raw_games = 'games/raw/'
    path_to_parsed_games = 'games/parsed/'

    @staticmethod
    def parse_game(path: str) -> PokerGame:
        game = PokerGame()
        text_game = open(GameParser.path_to_raw_games + path, 'r').read()
        game.source = path
        every_hand = GameParser.RegEx.hand_border.split(text_game)

        # first hand always empty because of separator in start of text
        for hand in every_hand[1:]:

            steps = GameParser.RegEx.step_border.split(hand)

            if len(steps) < 3 or len(steps) > 7:
                raise ValueError(f'Invalid count of steps: {len(steps)} at hand # {every_hand.index(hand)}')

            GameParser.process_initial(game, steps[0])
            GameParser.process_hole_cards(game, steps[1])

            if len(steps) == 3:
                GameParser.process_summary(game, steps[2])

            elif len(steps) == 4:
                GameParser.process_flop(game, steps[2])
                GameParser.process_summary(game, steps[3])

            elif len(steps) == 5:
                GameParser.process_flop(game, steps[2])
                GameParser.process_turn(game, steps[3])
                GameParser.process_summary(game, steps[4])

            elif len(steps) == 6:
                GameParser.process_flop(game, steps[2])
                GameParser.process_turn(game, steps[3])
                GameParser.process_river(game, steps[4])
                GameParser.process_summary(game, steps[5])

            elif len(steps) == 7:
                GameParser.process_flop(game, steps[2])
                GameParser.process_turn(game, steps[3])
                GameParser.process_river(game, steps[4])
                GameParser.process_show_down(game, steps[5])
                GameParser.process_summary(game, steps[6])

        return game

    @staticmethod
    def parse_action(player: PokerGame.MockPlayer, step: BasePlay.StepType, text: str) \
            -> Tuple[PokerGame.EventType, int]:

        if text == 'folds':
            return PokerGame.Event.Fold, 0

        elif text == 'checks':
            return PokerGame.Event.Check, 0

        elif 'all-in' in text:
            if 'raises' in text:
                return PokerGame.Event.Allin, int(text.split()[3])

            elif 'bets' in text:
                return PokerGame.Event.Allin, int(text.split()[1])

            elif 'calls' in text:
                return PokerGame.Event.Call, int(text.split()[1]) + player.gived(step)

        elif text.startswith('bets'):
            bets, money = text.split()
            return PokerGame.Event.Raise, int(money)

        elif text.startswith('calls'):
            calls, money = text.split()
            return PokerGame.Event.Call, int(money) + player.gived(step)

        elif text.startswith('raises'):
            return PokerGame.Event.Raise, int(text.split()[3])

        else:
            raise ValueError(f'Undefined action: {text}')

    @staticmethod
    def process_actions(game: PokerGame, lines: Iterator[str]) -> None:

        while True:

            try:
                line = next(lines)
            except StopIteration:
                return

            match = GameParser.RegEx.find_uncalled_bet.search(line)

            if match is not None:
                money = int(match.group(1))
                name = match.group(2)
                game.curr_hand.add_decision(name, PokerGame.Event.ReturnMoney, money)
                continue

            match = GameParser.RegEx.find_collect_pot.search(line)

            if match is not None:
                name = match.group(1)
                money = int(match.group(2))
                game.curr_hand.add_decision(name, PokerGame.Event.WinMoney, money)
                continue

            match = GameParser.RegEx.find_collect_side_pot.search(line)

            if match is not None:
                name = match.group(1)
                money = int(match.group(2))
                game.curr_hand.add_decision(name, PokerGame.Event.WinMoney, money)
                continue

            match = GameParser.RegEx.find_collect_main_pot.search(line)

            if match is not None:
                name = match.group(1)
                money = int(match.group(2))
                game.curr_hand.add_decision(name, PokerGame.Event.WinMoney, money)
                continue

            match = GameParser.RegEx.find_show_cards.search(line)

            if match is not None:
                name = match.group(1)
                cards = match.group(2)

                if len(cards) == 5:
                    card1, card2 = map(str.upper, cards.split())
                    pair = CardsPair(Card(card1), Card(card2))

                elif len(cards) == 2:
                    only_card = Card(cards.upper())
                    pair = CardsPair(only_card)

                else:
                    raise ValueError(f'Bad cards shown: {line}')

                game.curr_hand.set_cards(name, pair)
                continue

            match = GameParser.RegEx.find_is_connected.search(line)

            if match is not None:
                name = match.group(1)
                game.curr_hand.add_decision(name, PokerGame.Event.Connected, 0)
                continue

            match = GameParser.RegEx.find_is_disconnected.search(line)

            if match is not None:
                name = match.group(1)
                game.curr_hand.add_decision(name, PokerGame.Event.Disconnected, 0)
                continue

            match = GameParser.RegEx.find_is_sitting_out.search(line)

            if match is not None:
                name = match.group(1)
                try:
                    game.curr_hand.add_decision(name, PokerGame.Event.Disconnected, 0)
                except ValueError:
                    pass
                continue

            match = GameParser.RegEx.find_said.search(line)

            if match is not None:
                name = match.group(1)
                msg = match.group(2)
                game.curr_hand.add_decision(name, PokerGame.Event.ChatMessage, 0, msg)
                continue

            match = GameParser.RegEx.find_observer_said.search(line)

            if match is not None:
                name = match.group(1)
                msg = match.group(2)
                game.curr_hand.add_decision(name, PokerGame.Event.ObserverChatMessage, 0, msg)
                continue

            match = GameParser.RegEx.find_finished.search(line)

            if match is not None:
                name = match.group(1)
                place = match.group(2)
                game.curr_hand.add_decision(name, PokerGame.Event.FinishGame, 0, place)
                continue

            match = GameParser.RegEx.find_received.search(line)

            if match is not None:
                name = match.group(1)
                place = match.group(2)
                earn = int(match.group(3).replace('.', ''))
                game.curr_hand.add_decision(name, PokerGame.Event.FinishGame, earn, place)
                continue

            match = GameParser.RegEx.find_winner.search(line)

            if match is not None:
                name = match.group(1)
                earn = int(match.group(2).replace('.', ''))
                game.curr_hand.add_decision(name, PokerGame.Event.FinishGame, earn, '1st')
                continue

            match = GameParser.RegEx.find_does_not_show.search(line)

            if match is not None:
                continue

            match = GameParser.RegEx.find_has_returned.search(line)

            if match is not None:
                name = match.group(1)
                try:
                    game.curr_hand.add_decision(name, PokerGame.Event.Connected, 0)
                except ValueError:
                    pass
                continue

            match = GameParser.RegEx.find_has_timed_out.search(line)

            if match is not None:
                continue

            match = GameParser.RegEx.find_timed_disconnected.search(line)

            if match is not None:
                name = match.group(1)
                game.curr_hand.add_decision(name, PokerGame.Event.Disconnected, 0)
                continue

            match = GameParser.RegEx.find_shows_in_show_down.search(line)

            if match is not None:
                name = match.group(1)
                card1 = Card(match.group(2).upper())
                card2 = Card(match.group(3).upper())
                game.curr_hand.set_cards(name, CardsPair(card1, card2))
                continue

            match = GameParser.RegEx.find_fold_showing_cards.search(line)

            if match is not None:
                name = match.group(1)
                cards = match.group(2)

                if len(cards) == 5:
                    card1, card2 = map(str.upper, cards.split())
                    pair = CardsPair(Card(card1), Card(card2))

                elif len(cards) == 2:
                    only_card = Card(cards.upper())
                    pair = CardsPair(only_card)

                else:
                    raise ValueError(f'Bad cards shown: {line}')

                game.curr_hand.set_cards(name, pair)
                continue

            match = GameParser.RegEx.find_mucks_hand.search(line)

            if match is not None:
                continue

            match = GameParser.RegEx.find_action.search(line)

            try:
                name = match.group(1)
                action = match.group(2)
            except AttributeError:
                print('Cannot parse line:', line)
                raise

            result, money = GameParser.parse_action(game.curr_hand.get_player(name),
                                                    game.curr_hand.curr_step, action)

            game.curr_hand.add_decision(name, result, money)

    @staticmethod
    def process_initial(game: PokerGame, text: str) -> None:
        every_line: Iterator[str] = iter(text.strip().split('\n'))
        first_line = next(every_line)

        if not first_line.startswith('PokerStars Hand #'):
            raise ValueError('It is not initial step: ' + text)

        match = GameParser.RegEx.hand_and_game_id.search(first_line)
        hand_id = int(match.group(1))

        if game.curr_hand is None:
            game.id = int(match.group(2))

            match = GameParser.RegEx.name_tournament.search(first_line)
            name = match.group(1)
            name = name.replace(' USD ', ' ').replace('No Limit', 'NL')
            game.name = name

            match = GameParser.RegEx.date_tournament.search(first_line)
            date = match.group(1)
            time = match.group(2)
            game.date = date
            game.time = time

        match = GameParser.RegEx.small_and_big_blind.search(first_line)

        small_blind = int(match.group(1))
        big_blind = int(match.group(2))

        line = next(every_line)

        if not line.startswith('Table '):
            raise ValueError('It is not initial step (2nd line): ' + text)

        line = next(every_line)
        players: List[PokerGame.MockPlayer] = []
        out_of_hand: List[PokerGame.MockPlayer] = []

        while line.startswith('Seat') and '(' in line:

            if line.endswith('is sitting out'):
                match = GameParser.RegEx.player_init_sitting_out.search(line)
                is_active = False
                is_out_of_hand = False

            elif ') out of hand (' in line:
                match = GameParser.RegEx.player_init_out_of_hand.search(line)
                is_active = True
                is_out_of_hand = True

            else:
                match = GameParser.RegEx.player_init.search(line)
                is_active = True
                is_out_of_hand = False

            seat = int(match.group(1))

            try:
                name = match.group(2)
            except AttributeError:
                print('Found bad name:', line)
                raise

            money = int(match.group(3))
            line = next(every_line)

            if is_out_of_hand:
                out_of_hand += [PokerGame.MockPlayer(name, money, seat, is_active)]
            else:
                players += [PokerGame.MockPlayer(name, money, seat, is_active)]

        game.add_hand(players)
        game.curr_hand.id = hand_id
        game.curr_hand.small_blind = small_blind
        game.curr_hand.big_blind = big_blind
        game.curr_hand.sit_during_game = out_of_hand

        while ': posts the ante ' in line:

            if line.endswith('all-in'):
                match = GameParser.RegEx.find_ante_all_in.search(line)
            else:
                match = GameParser.RegEx.find_ante.search(line)

            name = match.group(1)
            ante = int(match.group(2))

            if game.curr_hand.ante == 0:
                game.curr_hand.ante = ante

            game.curr_hand.add_decision(name, PokerGame.Event.Ante, ante)
            line = next(every_line)

        if ': posts small blind' in line:

            if line.endswith('all-in'):
                match = GameParser.RegEx.find_small_blind_all_in.search(line)
            else:
                match = GameParser.RegEx.find_small_blind.search(line)

            name = match.group(1)
            small_blind = int(match.group(2))

            game.curr_hand.add_decision(name, PokerGame.Event.SmallBlind, small_blind)
            line = next(every_line)

        if ': posts big blind' in line:

            if line.endswith('all-in'):
                match = GameParser.RegEx.find_big_blind_all_in.search(line)
            else:
                match = GameParser.RegEx.find_big_blind.search(line)

            name = match.group(1)
            big_blind = int(match.group(2))

            game.curr_hand.add_decision(name, PokerGame.Event.BigBlind, big_blind)

        GameParser.process_actions(game, every_line)

    @staticmethod
    def process_hole_cards(game: PokerGame, text: str) -> None:
        every_line = iter(text.strip().split('\n'))
        first_line = next(every_line)

        if first_line.startswith('Dealt to'):

            match = GameParser.RegEx.find_dealt_cards.search(first_line)
            name = match.group(1)
            first_card = Card(match.group(2).upper())
            second_card = Card(match.group(3).upper())
            pair = CardsPair(first_card, second_card)

            game.curr_hand.set_cards(name, pair)

        GameParser.process_actions(game, every_line)

    @staticmethod
    def process_flop(game: PokerGame, text: str) -> None:

        game.curr_hand.switch_to_step(BasePlay.Step.Flop)

        every_line = iter(text.strip().split('\n'))
        first_line = next(every_line)

        match = GameParser.RegEx.find_flop.search(first_line)

        if match is None:
            raise ValueError(f'Bad first line in process flop: {text}')

        flop1 = Card(match.group(1).upper())
        flop2 = Card(match.group(2).upper())
        flop3 = Card(match.group(3).upper())

        game.curr_hand.set_flop_cards(flop1, flop2, flop3)

        GameParser.process_actions(game, every_line)

    @staticmethod
    def process_turn(game: PokerGame, text: str) -> None:

        game.curr_hand.switch_to_step(BasePlay.Step.Turn)

        every_line = iter(text.strip().split('\n'))
        first_line = next(every_line)

        match = GameParser.RegEx.find_turn.search(first_line)

        if match is None:
            raise ValueError(f'Bad first line in process turn: {text}')

        turn_card = Card(match.group(1).upper())
        game.curr_hand.set_turn_card(turn_card)

        GameParser.process_actions(game, every_line)

    @staticmethod
    def process_river(game: PokerGame, text: str) -> None:

        game.curr_hand.switch_to_step(BasePlay.Step.River)

        every_line = iter(text.strip().split('\n'))
        first_line = next(every_line)

        match = GameParser.RegEx.find_river.search(first_line)

        if match is None:
            raise ValueError(f'Bad first line in process river: {text}')

        river_card = Card(match.group(1).upper())
        game.curr_hand.set_river_card(river_card)

        GameParser.process_actions(game, every_line)

    @staticmethod
    def process_show_down(game: PokerGame, text: str) -> None:

        every_line = iter(text.strip().split('\n'))
        GameParser.process_actions(game, every_line)

    @staticmethod
    def process_summary(game: PokerGame, text: str) -> None:

        every_line = iter(text.strip().split('\n'))
        line = next(every_line)

        if not line.startswith('Total pot'):
            raise ValueError(f'Bad first line of summary: {text}')

        if 'Main pot' in line:
            match = GameParser.RegEx.find_total_pot_with_main_pot.search(line)
        else:
            match = GameParser.RegEx.find_total_pot.search(line)

        total_pot = int(match.group(1))
        game.curr_hand.total_pot = total_pot

        line = next(every_line)

        if line.startswith('Board'):
            line = next(every_line)

        if not line.startswith('Seat'):
            raise ValueError(f'Bad second/third line of summary: {text}')

        while line.startswith('Seat'):

            if line.endswith("folded before Flop (didn't bet)") or \
                    line.endswith('folded before Flop') or \
                    line.endswith('folded on the Flop') or \
                    line.endswith('folded on the Turn') or \
                    line.endswith('folded on the River'):

                try:
                    line = next(every_line)
                except StopIteration:
                    return

                continue

            if ' (button) ' in line:
                line = line.replace(' (button) ', ' ')
            if ' (big blind) ' in line:
                line = line.replace(' (big blind) ', ' ')
            if ' (small blind) ' in line:
                line = line.replace(' (small blind) ', ' ')

            match = GameParser.RegEx.find_collected_pot_summary.search(line)

            if match is not None:

                name = match.group(1)
                win_player_cards = game.curr_hand.get_player(name).cards
                if win_player_cards is not None and win_player_cards.initialized():
                    game.curr_hand.add_winner(name)

            else:

                match = GameParser.RegEx.find_lost.search(line)

                if match is not None:
                    name = match.group(1)
                    card1 = Card(match.group(2).upper())
                    card2 = Card(match.group(3).upper())
                    game.curr_hand.set_cards(name, CardsPair(card1, card2))
                    game.curr_hand.add_loser(name)

                else:

                    match = GameParser.RegEx.find_won.search(line)

                    if match is not None:
                        name = match.group(1)
                        card1 = Card(match.group(2).upper())
                        card2 = Card(match.group(3).upper())
                        game.curr_hand.set_cards(name, CardsPair(card1, card2))
                        game.curr_hand.add_winner(name)

                    else:

                        match = GameParser.RegEx.find_mucked_cards.search(line)

                        if match is not None:
                            name = match.group(1)
                            card1 = Card(match.group(2).upper())
                            card2 = Card(match.group(3).upper())
                            game.curr_hand.set_cards(name, CardsPair(card1, card2))
                            game.curr_hand.add_loser(name)

                        else:
                            raise ValueError(f'Bad summary processing line: {line}')

            try:
                line = next(every_line)
            except StopIteration:
                return

        GameParser.process_actions(game, every_line)


class GameManager:

    def __init__(self):

        self.network: Network = Network('main', 'main')
        self.game: Game = None

    def run(self):

        Thread(target=lambda: self.infinite(), name='GameManager infinite').start()

    def create_game(self, real, bots, seats, stack, scheme, name=''):

        real = int(real)
        bots = int(bots)
        seats = int(seats)
        stack = int(stack)

        self.network.send_raw('http name:' + name)
        self.network.send_raw('http players:' + str(real+bots))

        if scheme == 'standard':
            scheme = Blinds.Scheme.Standard

        elif scheme == 'fast':
            scheme = Blinds.Scheme.Fast

        elif scheme == 'rapid':
            scheme = Blinds.Scheme.Rapid

        elif scheme == 'bullet':
            scheme = Blinds.Scheme.Bullet

        else:
            return

        self.game = Game(real + bots, seats, stack, scheme)

        for _ in range(bots):
            self.game.add_player()

        self.network.send_raw('http start_registration')

    def add_player(self, name) -> None:

        if self.game.add_player(name):
            self.network.send_raw('http start')
            Thread(target=lambda: self.wait_for_end(), name='GameManager: wait for end').start()

    def delete_player(self, name) -> None:

        self.game.delete_player(name)

    def wait_for_end(self) -> None:

        self.game.thread.join()

        if not self.game.game_broken:
            del self.game
            self.game = None
            self.network.send_raw('http end')

    def break_game(self):

        self.game.break_game()

        if self.game.thread:
            self.game.thread.join()

        del self.game
        self.game = None
        self.network.send_raw('http broken')

    def infinite(self):

        Debug.game_manager('Game manager: ready to listen')

        while True:

            try:

                request = self.network.receive_raw()

                Debug.game_manager('Game manager: message "' + request + '"')

                request = request.split()

                if request[0] == 'create' and self.game is None:
                    Debug.game_manager('Game manager: create game')
                    self.create_game(*request[1:])
                    Debug.game_manager('Game manager: game created')

                elif request[0] == 'add' and self.game is not None and not self.game.game_started:
                    Debug.game_manager('Game manager: add player')
                    self.add_player(request[1])
                    Debug.game_manager('Game manager: player added')

                elif request[0] == 'delete' and self.game is not None and not self.game.game_started:
                    Debug.game_manager('Game manager: delete player')
                    self.delete_player(request[1])
                    Debug.game_manager('Game manager: player deleted')

                elif request[0] == 'break' and self.game is not None:
                    Debug.game_manager('Game manager: break game')
                    self.break_game()
                    Debug.game_manager('Game manager: game broken')

            except ValueError:
                continue

            except IndexError:
                continue


class Evolution:

    def __init__(self, games: int, players: int, seats: int, money: int,
                 blinds_scheme: Blinds.SchemeType = Blinds.Scheme.Standard):

        self.games: int = games
        self.players: int = players
        self.seats: int = seats
        self.money: int = money
        self.blinds_scheme: Blinds.SchemeType = blinds_scheme

    def run(self) -> None:

        for num in range(self.games):

            game = Game(self.players, self.seats, self.money, self.blinds_scheme)

            for __ in range(game.total_players):
                game.add_player()

            Debug.evolution(f'Start game #{num + 1}')

            while not game.game_finished:
                sleep(1)

            PlayManager.standings(10)
            PlayManager.delete_bad_plays()


class Stats:

    class StatElement:

        def __init__(self, cards: str):
            self.cards: str = cards

            self.win_good: int = 0
            self.win_bad: int = 0
            self.win_same: int = 0

            self.lose_good: int = 0
            self.lose_bad: int = 0
            self.lose_same: int = 0

            self.draw_good: int = 0
            self.draw_bad: int = 0
            self.draw_same: int = 0

            self.total: int = 0

            self.wins_with: Dict[Poker.StrengthType, Dict[str, int]] = {strength: {versus: 0
                                                                                   for versus in CardsPair.All}
                                                                        for strength in Poker.Strength.All}

            self.lose_with: Dict[Poker.StrengthType, Dict[str, int]] = {strength: {versus: 0
                                                                                   for versus in CardsPair.All}
                                                                        for strength in Poker.Strength.All}

            self.draw_with: Dict[Poker.StrengthType, Dict[str, int]] = {strength: {versus: 0
                                                                                   for versus in CardsPair.All}
                                                                        for strength in Poker.Strength.All}

            self.wins_whom: Dict[str, Dict[Poker.StrengthType, int]] = {versus: {strength: 0
                                                                                 for strength in Poker.Strength.All}
                                                                        for versus in CardsPair.All}

            self.lose_whom: Dict[str, Dict[Poker.StrengthType, int]] = {versus: {strength: 0
                                                                                 for strength in Poker.Strength.All}
                                                                        for versus in CardsPair.All}

            self.draw_whom: Dict[str, Dict[Poker.StrengthType, int]] = {versus: {strength: 0
                                                                                 for strength in Poker.Strength.All}
                                                                        for versus in CardsPair.All}

        def wins(self) -> int:
            return self.win_good + self.win_bad + self.win_same

        def loses(self) -> int:
            return self.lose_good + self.lose_bad + self.lose_same

        def draws(self) -> int:
            return self.draw_good + self.draw_bad + self.draw_same

        def wins_perc(self) -> float:
            return self.wins() / self.total

        def loses_perc(self) -> float:
            return self.loses() / self.total

        def draw_perc(self) -> float:
            return self.draws() / self.total

        def total_games_whom(self, opp: str) -> int:
            return sum(self.wins_whom[opp].values()) + sum(self.draw_whom[opp].values()) + sum(
                self.lose_whom[opp].values())

        def total_wins_whom(self, opp: str) -> int:
            return sum(self.wins_whom[opp].values())

        def total_lose_whom(self, opp: str) -> int:
            return sum(self.lose_whom[opp].values())

        def total_draw_whom(self, opp: str) -> int:
            return sum(self.draw_whom[opp].values())

        def total_wins_perc_whom(self, opp: str) -> float:
            return self.total_wins_whom(opp) / self.total_games_whom(opp)

        def total_lose_perc_whom(self, opp: str) -> float:
            return self.total_lose_whom(opp) / self.total_games_whom(opp)

        def total_draw_perc_whom(self, opp: str) -> float:
            return self.total_draw_whom(opp) / self.total_games_whom(opp)

        def wg(self, opp: str, strength: Poker.StrengthType) -> None:
            self.win_good += 1
            self.total += 1

            self.wins_with[strength][opp] += 1
            self.wins_whom[opp][strength] += 1

        def wb(self, opp: str, strength: Poker.StrengthType) -> None:
            self.win_bad += 1
            self.total += 1

            self.wins_with[strength][opp] += 1
            self.wins_whom[opp][strength] += 1

        def ws(self, opp: str, strength: Poker.StrengthType) -> None:
            self.win_same += 1
            self.total += 1

            self.wins_with[strength][opp] += 1
            self.wins_whom[opp][strength] += 1

        def lg(self, opp: str, strength: Poker.StrengthType) -> None:
            self.lose_good += 1
            self.total += 1

            self.lose_with[strength][opp] += 1
            self.lose_whom[opp][strength] += 1

        def lb(self, opp: str, strength: Poker.StrengthType) -> None:
            self.lose_bad += 1
            self.total += 1

            self.lose_with[strength][opp] += 1
            self.lose_whom[opp][strength] += 1

        def ls(self, opp: str, strength: Poker.StrengthType) -> None:
            self.lose_same += 1
            self.total += 1

            self.lose_with[strength][opp] += 1
            self.lose_whom[opp][strength] += 1

        def dg(self, opp: str, strength: Poker.StrengthType) -> None:
            self.draw_good += 1
            self.total += 1

            self.draw_with[strength][opp] += 1
            self.draw_whom[opp][strength] += 1

        def db(self, opp: str, strength: Poker.StrengthType) -> None:
            self.draw_bad += 1
            self.total += 1

            self.draw_with[strength][opp] += 1
            self.draw_whom[opp][strength] += 1

        def ds(self, opp: str, strength: Poker.StrengthType) -> None:
            self.draw_same += 1
            self.total += 1

            self.draw_with[strength][opp] += 1
            self.draw_whom[opp][strength] += 1

    stats_file_path: str = 'stats/stat'

    def __init__(self):

        if exists(Stats.stats_file_path):
            self.stat: Dict[str, Stats.StatElement] = load(open(Stats.stats_file_path, 'rb'))
            self.count: int = sum(s.total for s in self.stat.values()) // 2

        else:
            self.stat: Dict[str, Stats.StatElement] = {c: Stats.StatElement(c) for c in CardsPair.All}
            self.count: int = 0

        self.deck: Deck = Deck()
        self.p1: Player = Player(0, 'p0', 0, False)
        self.p2: Player = Player(0, 'P1', 0, False)
        self.board: Board = Board(self.deck)
        self.lock = False
        self.last_count: int = self.count

    def wins_perc(self, c1: str, c2: str) -> float:
        return self.stat[c1].total_wins_perc_whom(c2)

    def lose_perc(self, c1: str, c2: str) -> float:
        return self.stat[c1].total_lose_perc_whom(c2)

    def draw_perc(self, c1: str, c2: str) -> float:
        return self.stat[c1].total_draw_perc_whom(c2)

    def save(self):

        dump(self.stat, open(Stats.stats_file_path, 'wb'))
        if self.count//1000000 != self.last_count//1000000:
            dump(self.stat, open(f'backup/{self.count//1000000}m', 'wb'))
            print(f'backup {self.count//1000000}m')
        self.last_count = self.count

    def deal(self):

        self.deck.shuffle()

        self.p1.drop_cards()
        self.p2.drop_cards()

        self.board.clear()

        for _ in range(2):
            self.p1.add_card(self.deck.next())
            self.p2.add_card(self.deck.next())

        self.board.open_all()

        self.p1.hand = Poker.max_strength(self.p1.cards.get() + self.board.get())
        self.p2.hand = Poker.max_strength(self.p2.cards.get() + self.board.get())

        p1 = self.stat[self.p1.cards.str()]
        p2 = self.stat[self.p2.cards.str()]

        if self.p1.hand > self.p2.hand:
            if self.p1.cards > self.p2.cards:
                p1.wg(self.p2.cards.str(), self.p1.hand.strength)
                p2.lb(self.p1.cards.str(), self.p1.hand.strength)

            elif self.p2.cards > self.p1.cards:
                p1.wb(self.p2.cards.str(), self.p1.hand.strength)
                p2.lg(self.p1.cards.str(), self.p1.hand.strength)

            else:
                p1.ws(self.p2.cards.str(), self.p1.hand.strength)
                p2.ls(self.p1.cards.str(), self.p1.hand.strength)

        elif self.p2.hand > self.p1.hand:
            if self.p1.cards > self.p2.cards:
                p1.lg(self.p2.cards.str(), self.p2.hand.strength)
                p2.wb(self.p1.cards.str(), self.p2.hand.strength)

            elif self.p2.cards > self.p1.cards:
                p1.lb(self.p2.cards.str(), self.p2.hand.strength)
                p2.wg(self.p1.cards.str(), self.p2.hand.strength)

            else:
                p1.ls(self.p2.cards.str(), self.p2.hand.strength)
                p2.ws(self.p1.cards.str(), self.p2.hand.strength)

        else:
            if self.p1.cards > self.p2.cards:
                p1.dg(self.p2.cards.str(), self.p1.hand.strength)
                p2.db(self.p1.cards.str(), self.p1.hand.strength)

            elif self.p2.cards > self.p1.cards:
                p1.db(self.p2.cards.str(), self.p1.hand.strength)
                p2.dg(self.p1.cards.str(), self.p1.hand.strength)

            else:
                p1.ds(self.p2.cards.str(), self.p1.hand.strength)
                p2.ds(self.p1.cards.str(), self.p1.hand.strength)

        self.count += 1

    def const_save(self):

        while self.lock:
            for _ in range(150):
                sleep(0.2)
                if not self.lock:
                    self.save()
                    break
            else:
                self.save()

    def infinite(self):

        self.lock = True

        saving_thread = Thread(target=lambda: self.const_save(), name='Stats: saving infinite')
        saving_thread.start()

        while self.lock:
            self.deal()

        saving_thread.join()
        print(f'count = {self.count}')

    def stop(self):
        self.lock = False

    def main(self):

        for i in self.stat.values():
            print(f'{i.cards} {i.win_bad:>6} {i.total:>6} {i.win_bad / i.total:>.6}')

        print()
        q = max([s for s in self.stat.values()], key=lambda x: x.win_bad / x.total)

        print(q.cards)
        print(q.win_bad, q.total, q.win_bad / q.total)

        pairs = []

        for i in CardsPair.All:
            w = k = d = 0
            for j in CardsPair.All:
                if self.wins_perc(i, j) < self.lose_perc(i, j):
                    w += self.stat[i].total_wins_whom(j)
                    k += self.stat[i].total_lose_whom(j)
                    d += self.stat[i].total_draw_whom(j)
                    # print(i, 'vs', j, stat.stat[i].total_wins_whom(j) / (stat.stat[i].total_games_whom(j)))
            if w + k + d:
                # print('stat for', i, '=', w / (w + l + d))
                pairs += [(w / (w + k + d), i)]
                # print()

        print('\n'.join(f'{i[1]}\t{i[0]}' for i in sorted(pairs, reverse=True)))

        t = Thread(target=lambda: self.infinite())
        t.start()

        while True:
            a = input()
            if a == 'c':
                print(self.count)
            elif a == 'a':
                for i in self.stat.values():
                    print(f'{i.cards} {i.win_bad:>6} {i.total:>6} {i.win_bad / i.total:>.6}')
            elif a == 'q':
                self.stop()
                t.join()
                break


if __name__ == '__main__':

    # PlayManager.standings()
    # GameManager().run()

    print(GameParser.parse_game('hh.txt'))

    # Evolution(1000, 999, 9, 10000, Blinds.Scheme.Rapid).run()
