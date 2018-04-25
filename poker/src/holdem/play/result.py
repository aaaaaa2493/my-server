from typing import Dict
from enum import Enum


class Result(Enum):
    DoNotPlay = 0
    Fold = 1
    Call = 2
    Check = 3
    Raise = 4
    Allin = 5
    InAllin = 6
    Ante = 7
    SmallBlind = 8
    BigBlind = 9
    WinMoney = 10
    ReturnMoney = 11

    def __str__(self) -> str:
        return _to_str[self]


_to_str: Dict[Result, str] = {
    Result.DoNotPlay: 'do not play',
    Result.Fold: 'fold',
    Result.Call: 'call',
    Result.Check: 'check',
    Result.Raise: 'raise',
    Result.Allin: 'all in',
    Result.InAllin: 'in all in',
    Result.Ante: 'ante',
    Result.SmallBlind: 'sb',
    Result.BigBlind: 'bb',
    Result.WinMoney: 'win',
    Result.ReturnMoney: 'return'
}
