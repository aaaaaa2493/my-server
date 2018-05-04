from unittest import TestCase
from importlib import import_module
from unit_tests.testing import UnitTesting


class ImportingTest(TestCase):
    def test_import_loop(self):
        modules = UnitTesting.find_modules('src')
        with self.assertRaises(ImportError):
            import_module('123')
        for module in modules:
            # print('import', module)
            import_module(module)
