from typing import Tuple
from holdem.poker.hand_strength import HandStrength
from core.cards.card import Card, Cards
from core.cards.cards_pair import CardsPair
from lib.deuces.evaluator import Evaluator


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
    def calculate_outs(hidden: CardsPair, common: Cards) -> Tuple[int, Cards]:

        if len(common) == 5 or not common:
            return 0, []

        cards: Cards = [hidden.first, hidden.second] + common

        curr_hand_strength = HandStrength.max_strength(cards).strength

        outs: int = 0
        outs_cards = []

        for card in Card.cards_52():

            if card not in cards:

                new_hand_strength = HandStrength.max_strength(cards + [card]).strength

                if len(common) == 4:
                    new_board_strength = HandStrength.strength(*common, card).strength

                else:
                    new_board_strength = HandStrength.strength4(*common, card).strength

                if new_board_strength < new_hand_strength > curr_hand_strength:
                    outs += 1
                    outs_cards += [card]

        return outs, outs_cards
