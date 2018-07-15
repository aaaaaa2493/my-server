from typing import Dict
from enum import Enum


class Suitability(Enum):
    Suited = True
    Offsuited = False

    @classmethod
    def get_suitability(cls, suitability: str) -> 'Suitability':
        return _from_str[suitability]

    @property
    def short(self) -> str:
        return _to_short_str[self]

    def __str__(self) -> str:
        return _to_str[self]


_to_str: Dict[Suitability, str] = {
    Suitability.Suited: 'suited',
    Suitability.Offsuited: 'offsuited'
}

_to_short_str: Dict[Suitability, str] = {
    Suitability.Suited: 's',
    Suitability.Offsuited: 'o'
}

_from_str: Dict[str, Suitability] = {
    's': Suitability.Suited,
    'o': Suitability.Offsuited
}

Suitabilities: str = 'so'
