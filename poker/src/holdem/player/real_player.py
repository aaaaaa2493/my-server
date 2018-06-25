from typing import Tuple
from core.cards.card import Card, Cards
from holdem.player.player import Player
from holdem.play.play import Play
from holdem.play.step import Step
from holdem.play.option import Option
from holdem.play.result import Result
from holdem.network import Network
from holdem.base_network import BaseNetwork
from holdem.poker.holdem_poker import HoldemPoker
from holdem.poker.hand_strength import HandStrength
from special.debug import Debug


class RealPlayer(Player):
    def __init__(self, game_id: int, _id: int, name: str, money: int):
        play: Play = Play()
        network: BaseNetwork = Network(
            {
                'type': 'py',
                'name': f'{self.name}',
                'id': self.id,
                'game id': game_id
            }
        )
        super().__init__(_id, money, True, name, play, network)

    def _decide(self, *,
                step: Step,
                to_call: int,
                min_raise: int,
                board: Cards,
                online: bool,
                **_) -> Tuple[Option, int]:

        Debug.input_decision()
        Debug.input_decision(f'you have {self.get_cards()}')
        if step != Step.Preflop:
            Debug.input_decision(f'on table {Card.str(board)}')
            Debug.input_decision(f'your combination: {HandStrength.max_strength(self.cards.get() + board)}')
        Debug.input_decision(f'probability to win: {HoldemPoker.probability(self.cards, board)}')

        outs, outs_cards = HoldemPoker.calculate_outs(self.cards, board)

        Debug.input_decision(f'outs: {outs} - {" ".join([card.card for card in outs_cards])}')
        Debug.input_decision()

        available_decisions = [(Result.Fold,)]

        Debug.input_decision('1 - fold')
        if self.remaining_money() > to_call:
            if to_call == 0 or self.gived == to_call:
                available_decisions += [(Result.Check,)]
                Debug.input_decision(f'2 - check')
            else:
                available_decisions += [(Result.Call, to_call)]
                Debug.input_decision(f'2 - call {to_call} you called {self.gived} remains {to_call - self.gived}')

            if min_raise < self.remaining_money():
                available_decisions += [(Result.Raise, min_raise, self.remaining_money())]
                Debug.input_decision(f'3 - raise from {min_raise} to {self.remaining_money()}')
            else:
                available_decisions += [(Result.Allin, self.remaining_money())]
                Debug.input_decision(f'3 - all in {self.remaining_money()} you called '
                                     f'{self.gived} remains {self.money}')

        else:
            available_decisions += [(Result.Call, self.remaining_money())]
            Debug.input_decision(f'2 - call all in {self.remaining_money()}')

        answer = self.network.input_decision(available_decisions)

        if answer[0] == '1':
            return Option.Fold, 0

        elif answer[0] == '2':
            if self.remaining_money() > to_call:
                if to_call == 0 or self.gived == to_call:
                    return Option.CheckCall, 0
                else:
                    return Option.CheckCall, to_call
            else:
                return Option.CheckCall, self.remaining_money()

        elif answer[0] == '3':

            if self.remaining_money() > to_call:

                if len(answer) == 2:
                    raised_money = int(answer[1])
                    return Option.Raise, raised_money

                else:
                    return Option.Raise, self.remaining_money()

        else:
            return Option.Fold, 0
