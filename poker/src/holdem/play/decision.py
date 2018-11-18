from __future__ import annotations
from typing import Dict
from enum import Enum


class UndefinedDecisionBehaviour(Exception):
    pass


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

    def __str__(self) -> str:
        return _to_str[self]

    @staticmethod
    def update(curr: Decision, decision: Decision) -> Decision:

        if curr is None:
            if decision == Decision.Fold:
                return Decision.CheckFold

            return decision

        else:

            if decision == Decision.Fold and curr == Decision.Check:
                return Decision.CheckFold

            elif decision == Decision.Fold and (curr == Decision.CheckCall or
                                                curr == Decision.CallR or
                                                curr == Decision.Call3 or
                                                curr == Decision.Call4):
                return Decision.CallFold

            elif decision == Decision.Fold and curr == Decision.Bet:
                return Decision.BetFold

            elif decision == Decision.Fold and (curr == Decision.Raise or
                                                curr == Decision.Bet3 or
                                                curr == Decision.Bet4 or
                                                curr == Decision.CheckRaise):
                return Decision.RaiseFold

            elif curr == Decision.Check and (decision == Decision.CheckCall or
                                             decision == Decision.CallR or
                                             decision == Decision.Call3 or
                                             decision == Decision.Call4 or
                                             decision == Decision.CallA):
                return decision

            elif curr == Decision.Check and (decision == Decision.Raise or
                                             decision == Decision.Bet3 or
                                             decision == Decision.Bet4):
                return Decision.CheckRaise

            elif curr == Decision.Check and decision == Decision.Allin:
                return Decision.CheckAllin

            elif curr == Decision.Bet and (decision == Decision.Bet3 or
                                           decision == Decision.Bet4 or
                                           decision == Decision.Allin or
                                           decision == Decision.CallR or
                                           decision == Decision.Call3 or
                                           decision == Decision.Call4 or
                                           decision == Decision.CallA):
                return decision

            elif curr == Decision.CheckRaise and (decision == Decision.Bet4 or
                                                  decision == Decision.Call3 or
                                                  decision == Decision.Call4):
                return Decision.CheckRaise

            elif curr == Decision.CheckRaise and (decision == Decision.Allin or
                                                  decision == Decision.CallA):
                return Decision.CheckAllin

            elif curr == Decision.Raise and (decision == Decision.Bet4 or
                                             decision == Decision.Allin or
                                             decision == Decision.Call3 or
                                             decision == Decision.Call4 or
                                             decision == Decision.CallA):
                return decision

            elif curr == Decision.Bet3 and (decision == Decision.Bet4 or
                                            decision == Decision.Allin or
                                            decision == Decision.Call4 or
                                            decision == Decision.CallA):
                return decision

            elif curr == Decision.Bet4 and (decision == Decision.Bet4 or
                                            decision == Decision.Allin or
                                            decision == Decision.Call4 or
                                            decision == Decision.CallA):
                return decision

            elif curr == Decision.CheckCall and (decision == Decision.CallR or
                                                 decision == Decision.Call3 or
                                                 decision == Decision.Call4):
                return decision

            elif curr == Decision.CheckCall and (decision == Decision.Bet3 or
                                                 decision == Decision.Bet4):
                return Decision.CheckRaise

            elif curr == Decision.CheckCall and (decision == Decision.Allin or
                                                 decision == Decision.CallA):
                return Decision.CheckAllin

            elif curr == Decision.CallR and (decision == Decision.Call3 or
                                             decision == Decision.Call4):
                return decision

            elif curr == Decision.CallR and decision == Decision.Bet4:
                return Decision.CheckRaise

            elif curr == Decision.CallR and (decision == Decision.Allin or
                                             decision == Decision.CallA):
                return Decision.CheckAllin

            elif curr == Decision.Call3 and (decision == Decision.Call4 or
                                             decision == Decision.Check):
                return decision

            elif curr == Decision.Call3 and decision == Decision.Bet4:
                return Decision.CheckRaise

            elif curr == Decision.Call3 and (decision == Decision.Allin or
                                             decision == Decision.CallA):
                return Decision.CheckAllin

            elif curr == Decision.Call4 and decision == Decision.Call4:
                return decision

            elif curr == Decision.Call4 and decision == Decision.Bet4:
                return Decision.CheckRaise

            elif curr == Decision.Call4 and (decision == Decision.Allin or
                                             decision == Decision.CallA):
                return Decision.CheckAllin

            else:
                raise UndefinedDecisionBehaviour(f'Undefined behavior curr = {curr} decision = {decision}')


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
