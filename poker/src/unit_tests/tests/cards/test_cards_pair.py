from unittest import TestCase
from core.cards.cards_pair import CardsPair, CanNotAddAnotherCard, NotInitializedCards, Card, Suitability


class CardsPairTest(TestCase):
    def setUp(self):
        self.none = CardsPair()
        self.half = CardsPair(Card('KS'))
        self.full = CardsPair(Card('QS'), Card('TH'))

    def test_initialized(self):
        self.assertFalse(self.none.initialized())
        self.assertFalse(self.none.half_initialized())

        self.assertFalse(self.half.initialized())
        self.assertTrue(self.half.half_initialized())

        self.assertTrue(self.full.initialized())
        self.assertFalse(self.full.half_initialized())

    def test_raise_third_card_add(self):
        with self.assertRaises(CanNotAddAnotherCard):
            self.full.set(Card('AS'))

        self.half.set(Card('TC'))
        with self.assertRaises(CanNotAddAnotherCard):
            self.half.set(Card('AS'))

        self.none.set(Card('2D'))
        self.none.set(Card('3D'))
        with self.assertRaises(CanNotAddAnotherCard):
            self.none.set(Card('AS'))

    def test_suitability(self):
        suited = CardsPair(Card('AS'), Card('QS'))
        self.assertEqual(suited.suitability, Suitability.Suited)

        offsuited = CardsPair(Card('AS'), Card('QC'))
        self.assertEqual(offsuited.suitability, Suitability.Offsuited)

    def test_first_always_stronger(self):
        weak = Card('2C')
        strong = Card('AD')

        pair = CardsPair(strong, weak)
        self.assertEqual(pair.first, strong)
        self.assertEqual(pair.second, weak)

        pair = CardsPair(weak, strong)
        self.assertEqual(pair.first, strong)
        self.assertEqual(pair.second, weak)

        pair = CardsPair(weak)
        self.assertEqual(pair.first, weak)
        self.assertEqual(pair.second, None)

        pair.set(strong)
        self.assertEqual(pair.first, strong)
        self.assertEqual(pair.second, weak)

        pair = CardsPair(strong)
        self.assertEqual(pair.first, strong)

        pair.set(weak)
        self.assertEqual(pair.first, strong)
        self.assertEqual(pair.second, weak)

        pair = CardsPair()
        self.assertEqual(pair.first, None)
        self.assertEqual(pair.second, None)

        pair.set(weak)
        self.assertEqual(pair.first, weak)
        self.assertEqual(pair.second, None)

        pair.set(strong)
        self.assertEqual(pair.first, strong)
        self.assertEqual(pair.second, weak)

        pair = CardsPair()
        pair.set(strong)
        pair.set(weak)
        self.assertEqual(pair.first, strong)
        self.assertEqual(pair.second, weak)

    def test_drop(self):
        self.full.drop()
        self.assertFalse(self.full.initialized())
        self.assertFalse(self.full.half_initialized())

        self.half.drop()
        self.assertFalse(self.half.initialized())
        self.assertFalse(self.half.half_initialized())

        self.none.drop()
        self.assertFalse(self.none.initialized())
        self.assertFalse(self.none.half_initialized())

    def test_str_not_initialized(self):
        self.full.str()
        self.full.long_str()

        with self.assertRaises(NotInitializedCards):
            self.half.str()
        with self.assertRaises(NotInitializedCards):
            self.half.long_str()

        with self.assertRaises(NotInitializedCards):
            self.none.str()
        with self.assertRaises(NotInitializedCards):
            self.none.long_str()

    def test_equal(self):
        pair1 = CardsPair(Card('AS'), Card('5D'))
        pair2 = CardsPair(Card('AS'), Card('5C'))
        pair3 = CardsPair(Card('AS'), Card('5D'))
        self.assertNotEqual(pair1, pair2)
        self.assertEqual(pair1, pair3)

    def test_str(self):
        self.assertRegex(str(self.full), '.. ..')
        self.assertRegex(str(self.half), '.. \?\?')
        self.assertRegex(str(self.none), '\?\? \?\?')

    def test_hash(self):
        pair1 = CardsPair(Card('AS'), Card('5D'))
        pair2 = CardsPair(Card('AS'), Card('5C'))
        pair3 = CardsPair(Card('AS'), Card('5D'))
        self.assertEqual(len({pair1, pair2, pair3}), 2)
