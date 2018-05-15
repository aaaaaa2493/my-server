from numpy import array
from typing import List, Dict, Tuple
from statistics import mean
from holdem.poker.holdem_poker import HoldemPoker
from holdem.play.step import Step
from data.game_model.event import Event
from data.game_model.poker_hand import PokerHand
from data.game_model.poker_game import PokerGame
from data.game_model.poker_position import PokerPosition
from data.game_model.player_statistics import PlayerStatistics
from data.game_model.mock_player import MockPlayer
from learning.data_sets.decision_model.base_poker_decision import BasePokerDecision
from learning.data_sets.decision_model.base_poker_decision_answer import BasePokerDecisionAnswer
from learning.data_sets.decision_model.poker_decision_answer_3 import PokerDecisionAnswer3
from special.debug import Debug
from core.cards.card import Card
from core.cards.cards_pair import CardsPair
from core.cards.suitability import Suitability
from core.blinds.blinds import Blinds
from holdem.poker.hand_strength import HandStrength


class PokerDecision9(BasePokerDecision):

    CurrGame: PokerGame = None
    CurrRaisers: Dict[Tuple[str, PokerPosition], PlayerStatistics] = None
    CurrCheckers: Dict[Tuple[str, PokerPosition], PlayerStatistics] = None
    CurrCallers: Dict[Tuple[str, PokerPosition], PlayerStatistics] = None  # only preflop
    CurrFolders: Dict[Tuple[str, PokerPosition], PlayerStatistics] = None  # only preflop

    def __init__(self):
        super().__init__()
        self.probability_to_win: float = 0
        self.my_money: int = 0
        self.money_in_pot: int = 0
        self.money_to_call: int = 0
        self.big_blind: int = 0
        self.is_preflop: int = 0
        self.is_flop: int = 0
        self.is_turn: int = 0
        self.is_river: int = 0
        self.strength = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.first = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.second = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.have_suited_cards: int = 0
        self.players_on_table = [0, 0, 0, 0, 0, 0, 0, 0, 0]  # 2 - 10
        self.players_playing = [0, 0, 0, 0, 0, 0, 0, 0, 0]  # 2 - 10
        self.players_not_moved = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # 0 - 9
        self.outs: float = 0  # 1 is 21 out
        self.max_playing_stack = 0
        self.average_stack_on_table: int = 0
        self.max_raiser: float = 0
        self.min_raiser: float = 0
        self.avg_raiser: float = 0
        self.max_caller: float = 0
        self.min_caller: float = 0
        self.avg_caller: float = 0
        self.max_folder: float = 0
        self.min_folder: float = 0
        self.avg_folder: float = 0
        self.max_checker: float = 0
        self.min_checker: float = 0
        self.avg_checker: float = 0
        self.my_position_is_early: int = 0
        self.my_position_is_middle: int = 0
        self.my_position_is_late: int = 0
        self.my_position_is_blinds: int = 0

    def to_array(self) -> array:
        arr = [
            self.probability_to_win,
            self.my_money / self.money_in_pot,
            self.money_to_call / self.money_in_pot,
            self.big_blind / self.money_in_pot,
            self.is_preflop,
            self.is_flop,
            self.is_turn,
            self.is_river,
        ] + self.strength + self.first + self.second + [
            self.have_suited_cards
        ] + self.players_on_table + self.players_playing + self.players_not_moved + [
            self.outs,
            self.my_money / self.big_blind / Blinds.NORMAL_BBS - 1,
            self.max_playing_stack / self.big_blind / Blinds.NORMAL_BBS - 1,
            self.average_stack_on_table / self.big_blind / Blinds.NORMAL_BBS - 1,
            self.max_raiser,
            self.min_raiser,
            self.avg_raiser,
            self.max_caller,
            self.min_caller,
            self.avg_caller,
            self.max_folder,
            self.min_folder,
            self.avg_folder,
            self.max_checker,
            self.min_checker,
            self.avg_checker,
            self.my_position_is_early,
            self.my_position_is_middle,
            self.my_position_is_late,
            self.my_position_is_blinds,
        ]
        return array(arr)

    def __str__(self) -> str:
        return f'{self._answer.name} ' \
               f'money {self.my_money} ' \
               f'pot {self.money_in_pot} ' \
               f'bb {self.big_blind} ' \
               f'call {self.money_to_call} ' \
               f'prob {self.probability_to_win} '

    @staticmethod
    def initialize(game: PokerGame, hand: PokerHand) -> None:
        print('init hand', hand.id)

    @staticmethod
    def create(res: BasePokerDecisionAnswer,
               money: int,
               pot: int,
               call: int,
               bb: int,
               step: Step,
               cards: CardsPair,
               board: Card.Cards,
               players_on_table: int,
               players_active: int,
               players_not_moved: int,
               max_playing_stack: int,
               average_stack_on_table: int,
               players: List[MockPlayer],
               folded_players: List[str],
               my_position: PokerPosition) -> 'PokerDecision9':

        if money < 0:
            raise ValueError(f'Money must be > 0, gived {money}')

        if pot < 0:
            raise ValueError(f'Pot must be > 0, gived {pot}')

        if call < 0:
            raise ValueError(f'Call must be > 0, gived {call}')

        if bb < 0:
            raise ValueError(f'Big blinds must be > 0, gived {bb}')

        if pot <= call and step != Step.Preflop:
            raise ValueError(f'Pot must be > call, gived call {call} pot {pot}')

        if type(res) is not PokerDecisionAnswer3:
            raise ValueError(f'Result must ne instance of PokerDecisionAnswer, gived {res}')

        pr = HoldemPoker.probability(cards, board)
        strength = HandStrength.get_strength(cards, board)
        outs: float = HoldemPoker.calculate_outs(cards, board)[0] / HoldemPoker.MAX_OUTS

        des = PokerDecision9()
        des.set_answer(res)
        des.probability_to_win = pr
        des.my_money = money
        des.money_in_pot = pot
        des.money_to_call = call
        des.big_blind = bb

        if step == Step.Preflop:
            des.is_preflop = 1
        elif step == Step.Flop:
            des.is_flop = 1
        elif step == Step.Turn:
            des.is_turn = 1
        elif step == Step.River:
            des.is_river = 1
        else:
            raise ValueError('bad step', step)

        int_strength: int = strength.value
        if int_strength < 0:
            raise ValueError('strength is < 0', int_strength, strength)
        des.strength[int_strength] = 1

        rank: int = cards.first.rank.value - 2
        if rank < 0:
            raise ValueError('rank is < 0', rank, cards.first.rank)
        des.first[rank] = 1

        rank: int = cards.second.rank.value - 2
        if rank < 0:
            raise ValueError('rank is < 0', rank, cards.second.rank)
        des.second[rank] = 1

        if cards.suitability == Suitability.Suited:
            des.have_suited_cards = 1

        if players_on_table < 2 or players_on_table > 10:
            raise ValueError('bad players on table:', players_active)

        if players_active < 2 or players_active > 10:
            raise ValueError('bad players active:', players_active)

        if players_active > players_on_table:
            raise ValueError('bad players active:', players_active, 'with players on table:', players_on_table)

        if players_not_moved < 0 or players_not_moved >= players_active:
            raise ValueError('bad players not moved:', players_not_moved, 'with players active:', players_active)

        des.players_on_table[players_on_table - 2] = 1
        des.players_playing[players_on_table - 2] = 1
        des.players_not_moved[players_not_moved] = 1

        des.outs = outs

        des.max_playing_stack = max_playing_stack
        des.average_stack_on_table = average_stack_on_table

        curr_raisers: Dict[Tuple[str, PokerPosition], PlayerStatistics] = PokerDecision9.CurrRaisers
        curr_callers: Dict[Tuple[str, PokerPosition], PlayerStatistics] = PokerDecision9.CurrCallers
        curr_folders: Dict[Tuple[str, PokerPosition], PlayerStatistics] = PokerDecision9.CurrFolders
        curr_checkers: Dict[Tuple[str, PokerPosition], PlayerStatistics] = PokerDecision9.CurrCheckers

        raisers = []
        callers = []
        folders = []
        checkers = []
        for player in players:
            if player.name not in folded_players:
                raisers += [curr_raisers[player.name, player.position].get_stats()]
                callers += [curr_callers[player.name, player.position].get_stats()]
                folders += [curr_folders[player.name, player.position].get_stats()]
                checkers += [curr_checkers[player.name, player.position].get_stats()]

        des.max_raiser = max(raisers)
        des.min_raiser = min(raisers)
        des.avg_raiser = mean(raisers)

        des.max_caller = max(callers)
        des.min_caller = min(callers)
        des.avg_caller = mean(callers)

        des.max_folder = max(folders)
        des.min_folder = min(folders)
        des.avg_folder = mean(folders)

        des.max_checker = max(checkers)
        des.min_checker = min(checkers)
        des.avg_checker = mean(checkers)

        des.my_position_is_early = my_position is PokerPosition.Early
        des.my_position_is_middle = my_position is PokerPosition.Middle
        des.my_position_is_late = my_position is PokerPosition.Late
        des.my_position_is_blinds = my_position is PokerPosition.Blinds

        return des

    @staticmethod
    def get_decisions(game: PokerGame, hand: PokerHand) -> List[BasePokerDecision]:

        if game != PokerDecision9.CurrGame:
            PokerDecision9.CurrGame = game
            PokerDecision9.CurrRaisers = dict()
            PokerDecision9.CurrCallers = dict()
            PokerDecision9.CurrFolders = dict()
            PokerDecision9.CurrCheckers = dict()

        curr_raisers: Dict[Tuple[str, PokerPosition], PlayerStatistics] = PokerDecision9.CurrRaisers
        curr_callers: Dict[Tuple[str, PokerPosition], PlayerStatistics] = PokerDecision9.CurrCallers
        curr_folders: Dict[Tuple[str, PokerPosition], PlayerStatistics] = PokerDecision9.CurrFolders
        curr_checkers: Dict[Tuple[str, PokerPosition], PlayerStatistics] = PokerDecision9.CurrCheckers

        for player in hand.players:
            key = (player.name, player.position)
            if key not in curr_raisers:
                curr_raisers[key] = PlayerStatistics()
            if key not in curr_callers:
                curr_callers[key] = PlayerStatistics()
            if key not in curr_folders:
                curr_folders[key] = PlayerStatistics()
            if key not in curr_checkers:
                curr_checkers[key] = PlayerStatistics()

        decisions: List[BasePokerDecision] = []

        pot_size = 0

        players_on_table = len(hand.players)
        players_active = players_on_table

        folded_players: List[str] = []

        money: Dict[str, int] = {p.name: p.money for p in hand.players}

        average_money_on_table: int = int(sum(p.money for p in hand.players) / len(hand.players))
        max_money_on_table: int = max(p.money for p in hand.players)

        bb: int = hand.big_blind

        Debug.datasets(')' * 20)
        for n, v in money.items():
            Debug.datasets(f'{n} - {v}')
        Debug.datasets('(' * 20)

        for step, stage in hand:
            Debug.datasets('NEW STEP', step)
            gived: Dict[str, int] = {p.name: 0 for p in hand.players}

            players_not_moved = players_active - 1  # myself don`t count so minus 1

            if step == Step.Preflop:
                raise_amount = hand.big_blind
            else:
                raise_amount = 0

            for act in stage:
                if act.event.is_statement():
                    continue

                Debug.datasets(act, raise_amount)

                folder = curr_folders[act.player.name, act.player.position]
                caller = curr_callers[act.player.name, act.player.position]
                raiser = curr_raisers[act.player.name, act.player.position]
                checker = curr_checkers[act.player.name, act.player.position]

                if act.event == Event.Ante:
                    pot_size += act.money
                    money[act.player.name] -= act.money

                elif act.event == Event.SmallBlind:
                    pot_size += act.money
                    gived[act.player.name] = act.money
                    money[act.player.name] -= act.money

                elif act.event == Event.BigBlind:
                    pot_size += act.money
                    gived[act.player.name] = act.money
                    money[act.player.name] -= act.money

                elif act.event == Event.Fold:
                    if act.player.cards is not None and act.player.cards.initialized() and not act.player.is_loser:
                        my_money = money[act.player.name]
                        to_call = raise_amount - gived[act.player.name]
                        des = PokerDecision9.create(
                            PokerDecisionAnswer3.Fold,
                            my_money,
                            pot_size,
                            to_call,
                            bb,
                            step,
                            act.player.cards,
                            hand.board.get_from_step(step),
                            players_on_table,
                            players_active,
                            players_not_moved,
                            max_money_on_table,
                            average_money_on_table,
                            hand.players,
                            folded_players,
                            act.player.position,
                        )
                        decisions += [des]

                    if step == Step.Preflop:
                        folder.activate()
                        caller.skip()
                    raiser.skip()
                    if raise_amount == 0 or raise_amount == gived[act.player.name]:
                        checker.skip()

                    players_active -= 1
                    players_not_moved -= 1
                    folded_players += [act.player.name]

                elif act.event == Event.Check:
                    if act.player.cards is not None and act.player.cards.initialized() and not act.player.is_loser:
                        my_money = money[act.player.name]
                        to_call = raise_amount - gived[act.player.name]
                        des = PokerDecision9.create(
                            PokerDecisionAnswer3.CheckCall,
                            my_money,
                            pot_size,
                            to_call,
                            bb,
                            step,
                            act.player.cards,
                            hand.board.get_from_step(step),
                            players_on_table,
                            players_active,
                            players_not_moved,
                            max_money_on_table,
                            average_money_on_table,
                            hand.players,
                            folded_players,
                            act.player.position,
                        )
                        decisions += [des]

                    if step == Step.Preflop:
                        folder.skip()
                    checker.activate()
                    raiser.skip()

                    players_not_moved -= 1

                elif act.event == Event.Call:
                    if act.player.cards is not None and act.player.cards.initialized() and not act.player.is_loser:
                        my_money = money[act.player.name]
                        if raise_amount > my_money + gived[act.player.name]:
                            to_call = my_money
                        else:
                            to_call = raise_amount - gived[act.player.name]
                        des = PokerDecision9.create(
                            PokerDecisionAnswer3.CheckCall,
                            my_money,
                            pot_size,
                            to_call,
                            bb,
                            step,
                            act.player.cards,
                            hand.board.get_from_step(step),
                            players_on_table,
                            players_active,
                            players_not_moved,
                            max_money_on_table,
                            average_money_on_table,
                            hand.players,
                            folded_players,
                            act.player.position,
                        )
                        decisions += [des]

                    if step == Step.Preflop:
                        folder.skip()
                        caller.activate()
                    raiser.skip()

                    pot_size += act.money - gived[act.player.name]
                    money[act.player.name] -= act.money - gived[act.player.name]
                    gived[act.player.name] = act.money
                    players_not_moved -= 1

                elif act.event == Event.Raise or act.event == Event.Allin:
                    if act.player.cards is not None and act.player.cards.initialized() and not act.player.is_loser:
                        my_money = money[act.player.name]
                        to_call = raise_amount - gived[act.player.name]

                        actually_raised = act.money - gived[act.player.name]
                        pot_sized_raise = actually_raised / pot_size
                        if my_money == actually_raised:
                            answer = PokerDecisionAnswer3.AllIn
                        elif pot_sized_raise < 0.25:
                            answer = PokerDecisionAnswer3.RaiseSmall
                        elif pot_sized_raise < 0.75:
                            answer = PokerDecisionAnswer3.RaiseMedium
                        else:
                            answer = PokerDecisionAnswer3.RaiseALot

                        des = PokerDecision9.create(
                            answer,
                            my_money,
                            pot_size,
                            to_call,
                            bb,
                            step,
                            act.player.cards,
                            hand.board.get_from_step(step),
                            players_on_table,
                            players_active,
                            players_not_moved,
                            max_money_on_table,
                            average_money_on_table,
                            hand.players,
                            folded_players,
                            act.player.position,
                        )
                        decisions += [des]

                    if step == Step.Preflop:
                        folder.skip()
                        caller.skip()
                    raiser.activate()
                    if raise_amount == 0 or raise_amount == gived[act.player.name]:
                        checker.skip()

                    pot_size += act.money - gived[act.player.name]
                    money[act.player.name] -= act.money - gived[act.player.name]
                    gived[act.player.name] = act.money
                    if raise_amount < act.money:
                        raise_amount = act.money
                    players_not_moved = players_active - 2  # without raiser and myself

                elif act.event == Event.ReturnMoney:
                    pot_size -= act.money

                else:
                    raise ValueError('you forget about', act.event)

                Debug.datasets(')' * 20)
                for n, v in gived.items():
                    Debug.datasets(f'{n}: {money[n]} ({v})')
                Debug.datasets('(' * 20)

        Debug.datasets('*' * 20)

        for des in decisions:
            Debug.datasets(des)

        Debug.datasets('_' * 20)
        return decisions
