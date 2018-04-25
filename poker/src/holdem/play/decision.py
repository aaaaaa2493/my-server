from typing import Dict
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

    @property
    def str_decision(self):
        return _to_str[self]


_to_str: Dict[Decision, str] = {
    Decision.Fold: 'fold',
    Decision.Check: 'check',
    Decision.Bet: 'bet',
    Decision.Raise: 'raise',
    Decision.Bet3: '3-bet',
    Decision.Bet4: '4-bet+',
    Decision.Allin: 'all in',
    Decision.CallR: 'call raise',
    Decision.Call3: 'call 3-bet',
    Decision.Call4: 'call 4-bet+',
    Decision.CallA: 'call and go all in',
    Decision.CheckFold: 'check then fold',
    Decision.BetFold: 'bet then fold',
    Decision.CallFold: 'call then fold',
    Decision.RaiseFold: 'raise then fold',
    Decision.CheckCall: 'check then call',
    Decision.CheckRaise: 'check then raise',
    Decision.CheckAllin: 'check then all in'
}
