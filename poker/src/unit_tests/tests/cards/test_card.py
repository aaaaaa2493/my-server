from unittest import TestCase
from core.cards.card import Card, Rank, Suit


class CardTest(TestCase):
    def test_equals(self):
        self.assertEqual(Card('AS'), Card('AS'))
        self.assertNotEqual(Card('AS'), Card('AC'))

    def test_rank(self):
        self.assertEqual(Card('TH').rank, Rank.Ten)
        self.assertEqual(Card('5H').rank, Rank.Five)
        self.assertEqual(Card('AS').rank, Rank.Ace)

    def test_suit(self):
        self.assertEqual(Card('TH').suit, Suit.Hearts)
        self.assertEqual(Card('TC').suit, Suit.Clubs)
        self.assertEqual(Card('TD').suit, Suit.Diamonds)
        self.assertEqual(Card('TS').suit, Suit.Spades)

    def test_short_cards(self):
        self.assertEqual(Card('4C').r, '4')
        self.assertEqual(Card('7C').r, '7')
        self.assertEqual(Card('JH').r, 'J')
        self.assertEqual(Card('4C').s, 'C')
        self.assertEqual(Card('7S').s, 'S')
        self.assertEqual(Card('JH').s, 'H')

    def test_str_cards(self):
        self.assertEqual(Card('KD').card, 'KD')
        self.assertEqual(Card('QC').card, 'QC')
        self.assertEqual(Card('8H').card, '8H')
        self.assertEqual(Card('4C').card, '4C')
        self.assertEqual(Card('7S').card, '7S')
        self.assertEqual(Card('2H').card, '2H')

    def test_str_cards_list(self):
        self.assertEqual(Card.str([Card('AS'), Card('QD'), Card('2C')]), 'AS QD 2C')

    def test_there_is_all_cards_different(self):
        cards = Card.cards_52()
        self.assertEqual(len(set(cards)), 52)

    def test_compare_cards(self):
        self.assertGreater(Card('AD'), Card('KC'))
        self.assertGreater(Card('QD'), Card('2C'))
        self.assertGreater(Card('7H'), Card('4D'))
        self.assertGreater(Card('TS'), Card('9S'))

    def test_convert(self):
        for card in Card('AS'), Card('QH'), Card('TD'), Card('4C'):
            card2 = card.convert()
            self.assertEqual(card.rank.value, card2.rank)
            self.assertEqual(card.suit.value, card2.suit)
            self.assertEqual(card, Card.get_card(card2))
