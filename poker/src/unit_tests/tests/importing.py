from unittest import TestCase
from os.path import dirname
from importlib import import_module
from unit_tests.testing import UnitTesting


class ImportingTest(TestCase):
    def test_import_loop(self):
        dr = dirname(__file__).replace('\\', '/')
        dr = dr[:dr.find('/poker/src') + 10]
        modules = UnitTesting.find_modules(dr)
        with self.assertRaises(ImportError):
            import_module('123')
        for module in modules:
            # print('import', module)
            import_module(module)
