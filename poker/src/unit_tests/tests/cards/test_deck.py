from unittest import TestCase
from core.cards.deck import Deck, NotEnoughCards


class DeckTest(TestCase):
    def setUp(self):
        self.deck = Deck()
        self.deck2 = Deck()

    def test_52_cards(self):
        self.assertEqual(len(self.deck), 52)

    def test_not_equals_decks(self):
        self.assertNotEqual(self.deck, self.deck2)

    def test_equals_from_begin(self):
        self.assertEqual(self.deck.cards, self.deck2.cards)

    def test_not_equals_after_shuffle(self):
        self.deck.shuffle()
        self.assertNotEqual(self.deck.cards, self.deck2.cards)

    def test_after_removing(self):
        self.deck.next()
        self.assertEqual(len(self.deck), 51)

    def test_skip(self):
        self.deck.skip(10)
        self.assertEqual(len(self.deck), 42)
        self.deck.skip(20)
        self.assertEqual(len(self.deck), 22)
        self.deck.skip(30)
        self.assertEqual(len(self.deck), 0)

    def test_merge(self):
        self.deck.shuffle()
        self.deck.next()
        self.deck.skip(10)
        self.deck.merge()
        self.assertEqual(len(self.deck), 52)

    def test_len_after_shuffle(self):
        self.deck.shuffle()
        self.deck.next()
        self.deck.skip(10)
        self.deck.shuffle()
        self.assertEqual(len(self.deck), 52)

    def test_error_not_enough_cards(self):
        self.deck.skip(52)
        with self.assertRaises(NotEnoughCards):
            self.deck.next()
