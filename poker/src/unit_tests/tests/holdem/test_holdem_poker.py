from unittest import TestCase
from itertools import combinations
from holdem.poker.holdem_poker import HoldemPoker
from holdem.poker.strength import Strength
from holdem.poker.hand_strength import HandStrength
from core.cards.card import Card
from core.cards.deck import Deck


class TestHoldemPoker(TestCase):
    def test_fast_hand_strength(self):

        cards = [Card('AS'), Card('8C'), Card('9D'), Card('2S'), Card('KD')]
        self.assertEqual(HoldemPoker.fast_hand_strength(cards), Strength.Nothing)

        cards = [Card('AS'), Card('AC'), Card('9D'), Card('2S'), Card('KD')]
        self.assertEqual(HoldemPoker.fast_hand_strength(cards), Strength.Pair)

        cards = [Card('AS'), Card('AC'), Card('9D'), Card('9S'), Card('KD')]
        self.assertEqual(HoldemPoker.fast_hand_strength(cards), Strength.Pairs)

        cards = [Card('AS'), Card('KC'), Card('9D'), Card('9S'), Card('9H')]
        self.assertEqual(HoldemPoker.fast_hand_strength(cards), Strength.Set)

        cards = [Card('JS'), Card('QC'), Card('KD'), Card('9S'), Card('TH')]
        self.assertEqual(HoldemPoker.fast_hand_strength(cards), Strength.Straight)

        cards = [Card('AS'), Card('8S'), Card('9S'), Card('2S'), Card('KS')]
        self.assertEqual(HoldemPoker.fast_hand_strength(cards), Strength.Flush)

        cards = [Card('AS'), Card('AC'), Card('9D'), Card('9S'), Card('9H')]
        self.assertEqual(HoldemPoker.fast_hand_strength(cards), Strength.FullHouse)

        cards = [Card('AS'), Card('AH'), Card('9S'), Card('AC'), Card('AD')]
        self.assertEqual(HoldemPoker.fast_hand_strength(cards), Strength.Quad)

        cards = [Card('QS'), Card('8S'), Card('9S'), Card('JS'), Card('TS')]
        self.assertEqual(HoldemPoker.fast_hand_strength(cards), Strength.StraightFlush)

        cards = [Card('QS'), Card('AS'), Card('KS'), Card('JS'), Card('TS')]
        self.assertEqual(HoldemPoker.fast_hand_strength(cards), Strength.RoyalFlush)

        deck = Deck()
        for _ in range(100):
            deck.shuffle()
            cards = [deck.next(), deck.next(), deck.next(), deck.next(), deck.next()]
            self.assertEqual(HoldemPoker.fast_hand_strength(cards), HandStrength.strength(*cards).strength)

    def test_test_6_card_hand_strength(self):
        self.n_card_strength(6)

    def test_test_7_card_hand_strength(self):
        self.n_card_strength(7)

    def n_card_strength(self, n: int):
        deck = Deck()
        for _ in range(100):
            deck.shuffle()
            cards = []
            for _ in range(n):
                cards += [deck.next()]

            correct_result = max(HandStrength.strength(*c) for c in combinations(cards, 5)).strength
            self.assertEqual(HoldemPoker.fast_max_strength(cards), correct_result)
