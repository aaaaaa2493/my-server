from unittest import TestCase
from core.cards.suitability import Suitability


class SuitabilityTest(TestCase):
    def test_different(self):
        self.assertNotEqual(Suitability.Suited, Suitability.Offsuited)

    def test_get_suitability(self):
        self.assertEqual(Suitability.get_suitability('s'), Suitability.Suited)
        self.assertEqual(Suitability.get_suitability('o'), Suitability.Offsuited)