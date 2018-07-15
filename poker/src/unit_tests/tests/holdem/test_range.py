from unittest import TestCase
from holdem.theory.range import Range
from core.cards.cards_pair import CardsPair


class TestRange(TestCase):
    def test_sorted_range_items(self):
        self.assertEqual(set(CardsPair.All) - set(Range.SortedRangeItems), set())
        self.assertEqual(set(Range.SortedRangeItems) - set(CardsPair.All), set())
        self.assertEqual(len(CardsPair.All), len(set(CardsPair.All)))
        self.assertEqual(len(Range.SortedRangeItems), len(set(Range.SortedRangeItems)))
