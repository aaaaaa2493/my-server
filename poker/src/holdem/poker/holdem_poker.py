from typing import Tuple
from lib.pokereval.hand_evaluator import HandEvaluator
from holdem.poker.hand_strength import HandStrength
from core.cards.card import Card
from core.cards.cards_pair import CardsPair


class HoldemPoker:

    @staticmethod
    def probability(c: CardsPair, f: Card.Cards) -> float:
        pr = HandEvaluator.evaluate_hand([c.first.convert(), c.second.convert()], [card.convert() for card in f])
        # print('EVALUATING', c, 'board', Card.str(f), '=', pr)
        return pr

    @staticmethod
    def calculate_outs(hidden: CardsPair, common: Card.Cards) -> Tuple[int, Card.Cards]:

        if len(common) == 5 or not common:
            return 0, []

        cards: Card.Cards = [hidden.first, hidden.second] + common

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
