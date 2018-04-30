from unittest import TestCase
from core.cards.suit import Suit


class SuitTest(TestCase):
    def test_different(self):
        self.assertNotEqual(Suit.Hearts, Suit.Diamonds)
        self.assertNotEqual(Suit.Hearts, Suit.Clubs)
        self.assertNotEqual(Suit.Hearts, Suit.Spades)
        self.assertNotEqual(Suit.Diamonds, Suit.Clubs)
        self.assertNotEqual(Suit.Diamonds, Suit.Spades)
        self.assertNotEqual(Suit.Clubs, Suit.Spades)

    def test_get_suits(self):
        self.assertEqual(Suit.get_suit('H'), Suit.Hearts)
        self.assertEqual(Suit.get_suit('D'), Suit.Diamonds)
        self.assertEqual(Suit.get_suit('C'), Suit.Clubs)
        self.assertEqual(Suit.get_suit('S'), Suit.Spades)

    def test_to_str(self):
        self.assertEqual(str(Suit.Hearts), 'hearts')
        self.assertEqual(str(Suit.Diamonds), 'diamonds')
        self.assertEqual(str(Suit.Clubs), 'clubs')
        self.assertEqual(str(Suit.Spades), 'spades')

    def test_short(self):
        self.assertEqual(Suit.Hearts.short, 'H')
        self.assertEqual(Suit.Diamonds.short, 'D')
        self.assertEqual(Suit.Clubs.short, 'C')
        self.assertEqual(Suit.Spades.short, 'S')
