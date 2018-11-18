from typing import Tuple, List
from itertools import combinations
from core.cards.card import Card, Cards
from core.cards.cards_pair import CardsPair
from lib.deuces.evaluator import Evaluator
from holdem.poker.strength import Strength


class HoldemPoker:

    MAX_OUTS: int = 21
    _evaluator = Evaluator()

    @staticmethod
    def probability(c: CardsPair, f: Cards) -> float:
        ev = HoldemPoker._evaluator
        board = [card.convert() for card in f]
        hand = [c.first.convert(), c.second.convert()]

        if len(board) == 0:
            pr = ev.evaluate(board, hand)
        else:
            pr = 1 - ev.get_five_card_rank_percentage(ev.evaluate(board, hand))

        return pr

    @staticmethod
    def fast_card_strength(cards: Cards) -> int:
        return HoldemPoker._evaluator.evaluate([card.convert() for card in cards], [])

    @staticmethod
    def fast_hand_strength(cards: Cards) -> Strength:
        fast_strength = HoldemPoker.fast_card_strength(cards)
        if fast_strength == 1:
            return Strength.RoyalFlush
        return Strength.from_deuces(HoldemPoker._evaluator.get_rank_class(fast_strength))

    @staticmethod
    def fast_max_strength(cards: Cards) -> Strength:
        int_cards: List[int] = [card.convert() for card in cards]
        max_strength = min(HoldemPoker._evaluator.evaluate(list(c), []) for c in combinations(int_cards, 5))
        if max_strength == 1:
            return Strength.RoyalFlush
        return Strength.from_deuces(HoldemPoker._evaluator.get_rank_class(max_strength))

    @staticmethod
    def calculate_outs(hidden: CardsPair, common: Cards) -> Tuple[int, Cards]:

        if len(common) == 5 or not common:
            return 0, []

        cards: Cards = [hidden.first, hidden.second] + common

        curr_hand_strength = HoldemPoker.fast_max_strength(cards)

        outs: int = 0
        outs_cards = []

        for card in Card.cards_52():

            if card not in cards:

                new_hand_strength = HoldemPoker.fast_max_strength(cards + [card])

                if new_hand_strength > curr_hand_strength:
                    outs += 1
                    outs_cards += [card]

        return outs, outs_cards
