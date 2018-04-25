from typing import Tuple
from pokereval.card import Card as _Card
from pokereval.hand_evaluator import HandEvaluator
from holdem.poker.strength import Strength
from core.cards.card import Card
from core.cards.cards_pair import CardsPair


class HoldemPoker:

    @staticmethod
    def probability(c: CardsPair, f: Card.Cards) -> float:
        return HandEvaluator.evaluate_hand([_Card(c.first.rank.to_int(), c.first.suit.to_int()),
                                            _Card(c.second.rank.to_int(), c.second.suit.to_int())],
                                           [_Card(card.rank.to_int(), card.suit.to_int()) for card in f])

    @staticmethod
    def calculate_outs(hidden: CardsPair, common: Card.Cards) -> Tuple[int, Card.Cards]:

        if len(common) == 5 or not common:
            return 0, []

        cards: Card.Cards = [hidden.first, hidden.second] + common

        curr_hand_strength = Strength.max_strength(cards).strength

        outs: int = 0
        outs_cards = []

        for card in Card.cards_52():

            if card not in cards:

                new_hand_strength = Strength.max_strength(cards + [card]).strength

                if len(common) == 4:
                    new_board_strength = Strength.strength(*common, card).strength

                else:
                    new_board_strength = Strength.strength4(*common, card).strength

                if new_board_strength < new_hand_strength > curr_hand_strength:
                    outs += 1
                    outs_cards += [card]

        return outs, outs_cards
