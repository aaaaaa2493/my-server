from unittest import TestLoader, TextTestRunner, TestSuite
from unit_tests.tests.test_rank import RankTest
from unit_tests.tests.test_suit import SuitTest


class UnitTesting:

    @staticmethod
    def test_all():

        loader = TestLoader()
        suite = TestSuite((
            loader.loadTestsFromTestCase(RankTest),
            loader.loadTestsFromTestCase(SuitTest),
        ))

        runner = TextTestRunner(verbosity=2)
        runner.run(suite)
