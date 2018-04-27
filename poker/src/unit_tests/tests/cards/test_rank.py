from unittest import TestCase
from core.cards.rank import Rank


class RankTest(TestCase):
    def test_ranks_strength(self):
        self.assertGreater(Rank.Ace, Rank.King)
        self.assertGreater(Rank.King, Rank.Queen)
        self.assertGreater(Rank.Queen, Rank.Jack)
        self.assertGreater(Rank.Jack, Rank.Ten)
        self.assertGreater(Rank.Ten, Rank.Nine)
        self.assertGreater(Rank.Nine, Rank.Eight)
        self.assertGreater(Rank.Eight, Rank.Seven)
        self.assertGreater(Rank.Seven, Rank.Six)
        self.assertGreater(Rank.Six, Rank.Five)
        self.assertGreater(Rank.Five, Rank.Four)
        self.assertGreater(Rank.Four, Rank.Three)
        self.assertGreater(Rank.Three, Rank.Two)
        self.assertGreater(Rank.Two, Rank.Invalid)

    def test_get_ranks(self):
        self.assertEqual(Rank.get_rank('A'), Rank.Ace)
        self.assertEqual(Rank.get_rank('K'), Rank.King)
        self.assertEqual(Rank.get_rank('Q'), Rank.Queen)
        self.assertEqual(Rank.get_rank('J'), Rank.Jack)
        self.assertEqual(Rank.get_rank('T'), Rank.Ten)
        self.assertEqual(Rank.get_rank('9'), Rank.Nine)
        self.assertEqual(Rank.get_rank('8'), Rank.Eight)
        self.assertEqual(Rank.get_rank('7'), Rank.Seven)
        self.assertEqual(Rank.get_rank('6'), Rank.Six)
        self.assertEqual(Rank.get_rank('5'), Rank.Five)
        self.assertEqual(Rank.get_rank('4'), Rank.Four)
        self.assertEqual(Rank.get_rank('3'), Rank.Three)
        self.assertEqual(Rank.get_rank('2'), Rank.Two)

    def test_to_str(self):
        self.assertEqual(str(Rank.Ace), 'ace')
        self.assertEqual(str(Rank.King), 'king')
        self.assertEqual(str(Rank.Queen), 'queen')
        self.assertEqual(str(Rank.Jack), 'jack')
        self.assertEqual(str(Rank.Ten), 'ten')
        self.assertEqual(str(Rank.Nine), 'nine')
        self.assertEqual(str(Rank.Eight), 'eight')
        self.assertEqual(str(Rank.Seven), 'seven')
        self.assertEqual(str(Rank.Six), 'six')
        self.assertEqual(str(Rank.Five), 'five')
        self.assertEqual(str(Rank.Four), 'four')
        self.assertEqual(str(Rank.Three), 'three')
        self.assertEqual(str(Rank.Two), 'two')
