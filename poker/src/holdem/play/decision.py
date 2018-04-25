from enum import Enum


class Decision(Enum):
    Fold = 0
    Check = 1
    Bet = 2
    Raise = 3
    Bet3 = 4
    Bet4 = 5
    Allin = 6
    CallR = 7
    Call3 = 8
    Call4 = 9
    CallA = 10
    CheckFold = 11
    BetFold = 12
    CallFold = 13
    RaiseFold = 14
    CheckCall = 15
    CheckRaise = 16
    CheckAllin = 17
