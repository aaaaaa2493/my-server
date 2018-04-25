from random import uniform, random
from typing import Dict
from holdem.play.step import Step
from holdem.play.decision import Decision
from holdem.play.result import Result


class BasePlay:

    ToStep: Dict[Step, str] = {
        Step.Preflop: 'preflop',
        Step.Flop: 'flop',
        Step.Turn: 'turn',
        Step.River: 'river'
    }

    ToResult: Dict[Result, str] = {
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

    ToDecision: Dict[Decision, str] = {
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

    def __init__(self):

        self.fold = 0
        self.check = 0
        self.bet = 0
        self.raise_ = 0
        self.bet3 = 0
        self.bet4 = 0
        self.allin = 0
        self.call_r = 0
        self.call_3 = 0
        self.call_4 = 0
        self.call_a = 0
        self.check_fold = 0
        self.bet_fold = 0
        self.call_fold = 0
        self.raise_fold = 0
        self.check_call = 0
        self.check_raise = 0
        self.check_allin = 0

        self.wins = 0
        self.total = 0

        # Вероятность сделать ререйз вместо сброса карт
        self.bluff = random()

        # Играть если шансы твоих карт больше чем эти
        self.min_probability_to_play = random()

        # Если шансы карт больше чем эти то
        self.min_probability_to_all_in = random()
        # Сходить в олл ин с такой вероятностью
        self.probability_to_all_in = random()

        # если шансы твоих карт больше min_probability_to_play, то
        #   ставка равна max(шансы * bet, 1) * money
        # если минимальный рейз больше ставки то колл
        # если минимальный рейз меньше ставик то рейз
        # если необходимый колл больше ставки то фолд
        self.bet_ = random() * 3

        # если решил сделать рейз то поставит
        # max( max(шансы * bet * reduced_raise, 1) * money, min(min_raise, money))
        self.reduced_raise = random()

        # если что то хочет поставить то с такой вероятностью чекнет
        self.check_ = random()

        # если хочет сделать ререйз то с такой вероятностью сделает колл
        self.call = random()

    def add(self, decision: Decision) -> None:

        self.total += 1

        if decision == Decision.Fold:
            self.fold += 1

        elif decision == Decision.Check:
            self.check += 1

        elif decision == Decision.Bet:
            self.bet += 1

        elif decision == Decision.Raise:
            self.raise_ += 1

        elif decision == Decision.Bet3:
            self.bet3 += 1

        elif decision == Decision.Bet4:
            self.bet4 += 1

        elif decision == Decision.Allin:
            self.allin += 1

        elif decision == Decision.CallR:
            self.call_r += 1

        elif decision == Decision.Call3:
            self.call_3 += 1

        elif decision == Decision.Call4:
            self.call_4 += 1

        elif decision == Decision.CallA:
            self.call_a += 1

        elif decision == Decision.CheckFold:
            self.check_fold += 1

        elif decision == Decision.BetFold:
            self.bet_fold += 1

        elif decision == Decision.CallFold:
            self.call_fold += 1

        elif decision == Decision.RaiseFold:
            self.raise_fold += 1

        elif decision == Decision.CheckCall:
            self.check_call += 1

        elif decision == Decision.CheckRaise:
            self.check_raise += 1

        elif decision == Decision.CheckAllin:
            self.check_allin += 1

        else:
            raise ValueError(f'Undefined decision id {decision}')

    def mutate(self, percent: float) -> None:

        self.bluff *= uniform(1 - percent, 1 + percent)
        self.min_probability_to_play *= uniform(1 - percent, 1 + percent)
        self.min_probability_to_all_in *= uniform(1 - percent, 1 + percent)
        self.probability_to_all_in *= uniform(1 - percent, 1 + percent)
        self.bet_ *= uniform(1 - percent, 1 + percent)
        self.reduced_raise *= uniform(1 - percent, 1 + percent)
        self.check_ *= uniform(1 - percent, 1 + percent)
        self.call *= uniform(1 - percent, 1 + percent)
