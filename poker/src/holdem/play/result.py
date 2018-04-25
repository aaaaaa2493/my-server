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
