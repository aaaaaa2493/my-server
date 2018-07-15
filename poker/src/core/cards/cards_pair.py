from typing import List
from core.cards.card import Card, Cards
from core.cards.suit import Suit, Suits
from core.cards.suitability import Suitability


class CanNotAddAnotherCard(Exception):
    pass


class NotInitializedCards(Exception):
    pass


class InitializeWithSameCard(Exception):
    pass


class BadCardsPairStringRepresentation(Exception):
    pass


class CardsPair:

    All = (
        '22', '32s', '32o', '33', '42s', '42o', '43s', '43o', '44', '52s', '52o', '53s', '53o',
        '54s', '54o', '55', '62s', '62o', '63s', '63o', '64s', '64o', '65s', '65o', '66', '72s',
        '72o', '73s', '73o', '74s', '74o', '75s', '75o', '76s', '76o', '77', '82s', '82o', '83s',
        '83o', '84s', '84o', '85s', '85o', '86s', '86o', '87s', '87o', '88', '92s', '92o', '93s',
        '93o', '94s', '94o', '95s', '95o', '96s', '96o', '97s', '97o', '98s', '98o', '99', 'T2s',
        'T2o', 'T3s', 'T3o', 'T4s', 'T4o', 'T5s', 'T5o', 'T6s', 'T6o', 'T7s', 'T7o', 'T8s', 'T8o',
        'T9s', 'T9o', 'TT', 'J2s', 'J2o', 'J3s', 'J3o', 'J4s', 'J4o', 'J5s', 'J5o', 'J6s', 'J6o',
        'J7s', 'J7o', 'J8s', 'J8o', 'J9s', 'J9o', 'JTs', 'JTo', 'JJ', 'Q2s', 'Q2o', 'Q3s', 'Q3o',
        'Q4s', 'Q4o', 'Q5s', 'Q5o', 'Q6s', 'Q6o', 'Q7s', 'Q7o', 'Q8s', 'Q8o', 'Q9s', 'Q9o', 'QTs',
        'QTo', 'QJs', 'QJo', 'QQ', 'K2s', 'K2o', 'K3s', 'K3o', 'K4s', 'K4o', 'K5s', 'K5o', 'K6s',
        'K6o', 'K7s', 'K7o', 'K8s', 'K8o', 'K9s', 'K9o', 'KTs', 'KTo', 'KJs', 'KJo', 'KQs', 'KQo',
        'KK', 'A2s', 'A2o', 'A3s', 'A3o', 'A4s', 'A4o', 'A5s', 'A5o', 'A6s', 'A6o', 'A7s', 'A7o',
        'A8s', 'A8o', 'A9s', 'A9o', 'ATs', 'ATo', 'AJs', 'AJo', 'AQs', 'AQo', 'AKs', 'AKo', 'AA'
    )

    def __init__(self, first: Card = None, second: Card = None):

        if first is not None and second is not None:

            if first == second:
                raise InitializeWithSameCard('Can not initialize with same card')

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

    @staticmethod
    def get_all_pairs() -> List['CardsPair']:
        pairs: List['CardsPair'] = []
        for card1 in Card.cards_52():
            for card2 in Card.cards_52():
                if card1 > card2:
                    pairs += [CardsPair(card1, card2)]
        return pairs

    @staticmethod
    def get_possible_pairs(pairs: str) -> List['CardsPair']:
        if pairs not in CardsPair.All:
            raise BadCardsPairStringRepresentation()

        result: List['CardsPair'] = []
        if len(pairs) == 2:
            rank = pairs[0]
            for suit1 in Suit.all():
                for suit2 in Suit.all():
                    if suit1 > suit2:
                        result += [CardsPair(Card(rank + suit1.short), Card(rank + suit2.short))]

        elif pairs[-1] == 's':
            rank1 = pairs[0]
            rank2 = pairs[1]
            for suit in Suits:
                result += [CardsPair(Card(rank1 + suit), Card(rank2 + suit))]

        elif pairs[-1] == 'o':
            rank1 = pairs[0]
            rank2 = pairs[1]
            for suit1 in Suits:
                for suit2 in Suits:
                    if suit1 != suit2:
                        result += [CardsPair(Card(rank1 + suit1), Card(rank2 + suit2))]

        return result

    def initialized(self) -> bool:
        return self.second is not None

    def half_initialized(self) -> bool:
        return self.first is not None and self.second is None

    @property
    def suitability(self) -> Suitability:

        if self.first.suit == self.second.suit:
            return Suitability.Suited

        return Suitability.Offsuited

    def is_pocket_pairs(self) -> bool:
        if not self.initialized():
            raise NotInitializedCards()
        return self.first.rank == self.second.rank

    def get(self) -> Cards:
        return [self.first, self.second]

    def drop(self) -> None:

        self.first = None
        self.second = None

    def set(self, card: Card) -> None:

        if self.first is None:
            self.first = card
        elif self.second is None:
            if self.first == card:
                raise InitializeWithSameCard('Can not initialize with same card')
            if card > self.first:
                self.second = self.first
                self.first = card
            else:
                self.second = card
        else:
            raise CanNotAddAnotherCard('Can not set third card to pair of cards')

    def str(self) -> str:

        if self.initialized():
            first = self.first.r
            second = self.second.r
            if first == second:
                return first + second
            suitability = 's' if self.first.suit == self.second.suit else 'o'
            return first + second + suitability

        raise NotInitializedCards('Pair of cards is not initialized')

    def long_str(self) -> str:

        if self.initialized():
            return f'{self.first.str_rank} and {self.second.str_rank} {self.suitability}'

        raise NotInitializedCards('Pair of cards is not initialized')

    def __eq__(self, other: 'CardsPair') -> bool:
        return self.first == other.first and self.second == other.second

    def __ne__(self, other: 'CardsPair') -> bool:
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.first, self.second))

    def __str__(self):

        if self.initialized():
            return f'{self.first.card} {self.second.card}'
        elif self.half_initialized():
            return f'{self.first.card} ??'
        else:
            return '?? ??'
