from unittest import TestLoader, TextTestRunner, TestSuite
from unit_tests.tests.test_rank import RankTest


class UnitTesting:

    @staticmethod
    def test_all():

        loader = TestLoader()
        suite = TestSuite((
            loader.loadTestsFromTestCase(RankTest),
        ))

        runner = TextTestRunner(verbosity=2)
        runner.run(suite)
