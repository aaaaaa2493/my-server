from enum import Enum
from typing import Dict, Tuple
from .card import Card


class CardsPair:

    All: Tuple[str] = ('22o', '32s', '32o', '33o', '42s', '42o', '43s', '43o', '44o', '52s', '52o', '53s', '53o',
                       '54s', '54o', '55o', '62s', '62o', '63s', '63o', '64s', '64o', '65s', '65o', '66o', '72s',
                       '72o', '73s', '73o', '74s', '74o', '75s', '75o', '76s', '76o', '77o', '82s', '82o', '83s',
                       '83o', '84s', '84o', '85s', '85o', '86s', '86o', '87s', '87o', '88o', '92s', '92o', '93s',
                       '93o', '94s', '94o', '95s', '95o', '96s', '96o', '97s', '97o', '98s', '98o', '99o', 'T2s',
                       'T2o', 'T3s', 'T3o', 'T4s', 'T4o', 'T5s', 'T5o', 'T6s', 'T6o', 'T7s', 'T7o', 'T8s', 'T8o',
                       'T9s', 'T9o', 'TTo', 'J2s', 'J2o', 'J3s', 'J3o', 'J4s', 'J4o', 'J5s', 'J5o', 'J6s', 'J6o',
                       'J7s', 'J7o', 'J8s', 'J8o', 'J9s', 'J9o', 'JTs', 'JTo', 'JJo', 'Q2s', 'Q2o', 'Q3s', 'Q3o',
                       'Q4s', 'Q4o', 'Q5s', 'Q5o', 'Q6s', 'Q6o', 'Q7s', 'Q7o', 'Q8s', 'Q8o', 'Q9s', 'Q9o', 'QTs',
                       'QTo', 'QJs', 'QJo', 'QQo', 'K2s', 'K2o', 'K3s', 'K3o', 'K4s', 'K4o', 'K5s', 'K5o', 'K6s',
                       'K6o', 'K7s', 'K7o', 'K8s', 'K8o', 'K9s', 'K9o', 'KTs', 'KTo', 'KJs', 'KJo', 'KQs', 'KQo',
                       'KKo', 'A2s', 'A2o', 'A3s', 'A3o', 'A4s', 'A4o', 'A5s', 'A5o', 'A6s', 'A6o', 'A7s', 'A7o',
                       'A8s', 'A8o', 'A9s', 'A9o', 'ATs', 'ATo', 'AJs', 'AJo', 'AQs', 'AQo', 'AKs', 'AKo', 'AAo')

    class Suitability(Enum):
        Suited = True
        Offsuited = False

    Suitabilities: str = 'so'

    ToSuitability: Dict[Suitability, str] = {Suitability.Suited: 'suited',
                                             Suitability.Offsuited: 'offsuited'}

    FromSuitability: Dict[str, Suitability] = {'s': Suitability.Suited,
                                               'o': Suitability.Offsuited}

    @staticmethod
    def gt_str(self: str, opp: str):

        sfv = Card.FromRank[self[0]]
        ssv = Card.FromRank[self[1]]
        ss = CardsPair.FromSuitability[self[2]]

        ofv = Card.FromRank[opp[0]]
        osv = Card.FromRank[opp[1]]
        os = CardsPair.FromSuitability[opp[2]]

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

        elif first is not None and second is None:
            self.first: Card = first
            self.second: Card = None

        else:
            self.first: Card = None
            self.second: Card = None

    def initialized(self) -> bool:
        return self.second is not None

    def suitability(self) -> Suitability:

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
