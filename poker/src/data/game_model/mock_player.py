from typing import List
from data.game_model.player_event import Event, PlayerEvent
from core.cards.cards_pair import CardsPair
from holdem.play.step import Step


class MockPlayer:

    def __init__(self, name: str, money: int, seat: int, is_active: bool):
        self.name: str = name
        self.money: int = money
        self.seat: int = seat
        self.is_active = is_active
        self.is_all_in: bool = False
        self.is_winner: bool = False
        self.is_loser: bool = False
        self.cards: CardsPair = None
        self.preflop: List[PlayerEvent] = []
        self.flop: List[PlayerEvent] = []
        self.turn: List[PlayerEvent] = []
        self.river: List[PlayerEvent] = []

    def get_list(self, step: Step) -> List[PlayerEvent]:

        if step == Step.Preflop:
            return self.preflop
        elif step == Step.Flop:
            return self.flop
        elif step == Step.Turn:
            return self.turn
        elif step == Step.River:
            return self.river
        else:
            raise ValueError('No such step id ' + str(step))

    def add_decision(self, step: Step, event: Event, money: int) -> None:
        self.get_list(step).append(PlayerEvent(event, money))

    def gived(self, step: Step) -> int:

        curr_list = self.get_list(step)
        for action in reversed(curr_list):

            if action.event == Event.Check:
                return 0

            elif action.event == Event.Allin or \
                    action.event == Event.BigBlind or \
                    action.event == Event.SmallBlind or \
                    action.event == Event.Call or \
                    action.event == Event.Raise:
                return action.money

        return 0
