from unittest import TestCase
from importlib import import_module
from unit_tests.testing import UnitTesting
from special.debug import Debug


class ImportingTest(TestCase):
    def test_import_loop(self):
        modules = UnitTesting.find_modules('src')
        with self.assertRaises(ImportError):
            import_module('123')
        modules_count = 0
        for module in modules:
            # print('import', module)
            modules_count += 1
            import_module(module)
        Debug.unit_test(f'\nSUCCESSFULLY IMPORTED {modules_count} MODULES\n')
