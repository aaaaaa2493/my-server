from typing import List
from random import randint


class NameManager:

    Names = List[str]

    FreeNames = []
    BusyNames = []
    _length = 0
    _initialized = False
    _free_nicks_path = 'nicks/free.txt'
    _busy_nicks_path = 'nicks/busy.txt'

    @staticmethod
    def init():

        NameManager.FreeNames = open(NameManager._free_nicks_path).read().split()
        NameManager.BusyNames = open(NameManager._busy_nicks_path).read().split()
        NameManager._length = len(NameManager.FreeNames)
        NameManager._initialized = True

    @staticmethod
    def get_name():

        if not NameManager._initialized:
            NameManager.init()

        if NameManager._length > 0:

            random_index = randint(0, NameManager._length - 1)
            random_name = NameManager.FreeNames[random_index]

            del NameManager.FreeNames[random_index]
            NameManager.BusyNames += [random_name]

            NameManager._length -= 1
            NameManager.save()

            return random_name

        else:
            raise IndexError("Out of free unique names")

    @staticmethod
    def add_name(name):

        if not NameManager._initialized:
            NameManager.init()

        if name not in NameManager.FreeNames:

            if name in NameManager.BusyNames:

                del NameManager.BusyNames[NameManager.BusyNames.index(name)]
                NameManager.FreeNames += [name]

                NameManager._length += 1
                NameManager.save()

                return

            else:
                raise IndexError('This name was not busy')

        else:
            raise IndexError("Trying to add name that already exists as free " + name)

    @staticmethod
    def save():

        if not NameManager._initialized:
            NameManager.init()

        open(NameManager._free_nicks_path, 'w').write('\n'.join(NameManager.FreeNames))
        open(NameManager._busy_nicks_path, 'w').write('\n'.join(NameManager.BusyNames))
