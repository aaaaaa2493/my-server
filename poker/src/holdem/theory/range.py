from typing import List
from core.cards.cards_pair import CardsPair


class Range:

    SortedRangeItems = (
        'AA', 'KK', 'QQ', 'JJ', 'TT', 'AKs', '99', 'AQs', 'AKo', 'AJs', 'KQs', '88', 'ATs',
        'AQo', 'KJs', 'KTs', 'QJs', 'AJo', 'KQo', 'QTs', 'A9s', '77', 'ATo', 'JTs', 'KJo', 'A8s',
        'K9s', 'QJo', 'A7s', 'KTo', 'Q9s', 'A5s', '66', 'A6s', 'QTo', 'J9s', 'A9o', 'T9s', 'A4s',
        'K8s', 'JTo', 'K7s', 'A8o', 'A3s', 'Q8s', 'K9o', 'A2s', 'K6s', 'J8s', 'T8s', 'A7o', '55',
        'Q9o', '98s', 'K5s', 'Q7s', 'J9o', 'A5o', 'T9o', 'A6o', 'K4s', 'K8o', 'Q6s', 'J7s', 'T7s',
        'A4o', '97s', 'K3s', '87s', 'Q5s', 'K7o', '44', 'Q8o', 'A3o', 'K2s', 'J8o', 'Q4s', 'T8o',
        'J6s', 'K6o', 'A2o', 'T6s', '98o', '76s', '86s', '96s', 'Q3s', 'J5s', 'K5o', 'Q7o', 'Q2s',
        'J4s', '33', '65s', 'J7o', 'T7o', 'K4o', '75s', 'T5s', 'Q6o', 'J3s', '95s', '87o', '85s',
        '97o', 'T4s', 'K3o', 'J2s', '54s', 'Q5o', '64s', 'T3s', '22', 'K2o', '74s', '76o', 'T2s',
        'Q4o', 'J6o', '84s', '94s', '86o', 'T6o', '96o', '53s', '93s', 'Q3o', 'J5o', '63s', '43s',
        '92s', '73s', '65o', 'Q2o', 'J4o', '83s', '75o', '52s', '85o', '82s', 'T5o', '95o', 'J3o',
        '62s', '54o', '42s', 'T4o', 'J2o', '72s', '64o', 'T3o', '32s', '74o', '84o', 'T2o', '94o',
        '53o', '93o', '63o', '43o', '92o', '73o', '83o', '52o', '82o', '42o', '62o', '72o', '32o'
    )

    def __init__(self, pairs: List[CardsPair]):
        self.pairs = [pair for pair in set(pairs)]

    @staticmethod
    def get_range(pairs: List[str]) -> 'Range': ...
