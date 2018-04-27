from typing import List
from unittest import TestLoader, TextTestRunner, TestSuite, TestCase
from inspect import getmembers, isclass
from importlib import import_module
from os.path import dirname, isfile, isdir
from os import listdir


class UnitTesting:

    @staticmethod
    def test_all() -> None:

        tests_suite = []
        loader = TestLoader()

        print('BEFORE FIND')

        for module in UnitTesting.find_modules():
            imported = import_module(f'unit_tests.{module}')
            for name, obj in getmembers(imported):
                if isclass(obj) and issubclass(obj, TestCase):
                    tests_suite += [loader.loadTestsFromTestCase(obj)]

        suite = TestSuite(tests_suite)

        runner = TextTestRunner(verbosity=2)
        runner.run(suite)

    @staticmethod
    def find_modules() -> List[str]:

        curr_dir = dirname(__file__)
        catalogs = [curr_dir]

        print('FIND', curr_dir)
        print(listdir(curr_dir))

        modules = []

        while catalogs:
            curr_catalog = catalogs.pop()
            for file in listdir(curr_catalog):
                curr_location = curr_catalog + '/' + file
                print('TEST', curr_location, file.startswith('__'), isfile(curr_location), isdir(curr_location))
                if file.startswith('__'):
                    print('IGNORE', curr_location)
                    continue
                if isfile(curr_location):
                    if file.endswith('.py'):
                        print('PY', curr_location)
                        modules += [curr_location[len(curr_dir)+1:-3].replace('/', '.')]
                elif isdir(curr_location):
                    print('DIR', curr_location)
                    catalogs += [curr_location]

        return modules

print(__name__)
print(__file__)
if __name__ == '__main__':
    UnitTesting.test_all()
