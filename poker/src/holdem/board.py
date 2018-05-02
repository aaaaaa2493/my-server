from time import sleep
from core.cards.card import Card
from core.cards.deck import Deck
from holdem.play.step import Step
from holdem.delay import Delay


class Board:

    def __init__(self, deck: Deck, start_hand: int = 0):

        self.flop1: Card = None
        self.flop2: Card = None
        self.flop3: Card = None
        self.turn: Card = None
        self.river: Card = None

        self.deck: Deck = deck

        self.hand: int = start_hand

        self.state: Step = Step.Preflop

    def clear(self) -> None:

        self.flop1 = None
        self.flop2 = None
        self.flop3 = None
        self.turn = None
        self.river = None

        self.hand += 1

        self.state = Step.Preflop

    def set_flop_cards(self, card1: Card, card2: Card, card3: Card) -> None:

        if self.state == Step.Preflop:
            self.flop1 = card1
            self.flop2 = card2
            self.flop3 = card3
            self.state = Step.Flop
        else:
            raise ValueError('Setting flop cards not in preflop state')

    def open_flop(self) -> None:

        self.deck.skip()
        self.flop1 = self.deck.next()
        self.flop2 = self.deck.next()
        self.flop3 = self.deck.next()
        self.state = Step.Flop

    def open_flop_with_network(self, table) -> None:

        self.open_flop()

        if table.online:
            table.network.flop(self.flop1, self.flop2, self.flop3)
            sleep(Delay.Flop)

    def set_turn_card(self, card: Card) -> None:

        if self.state == Step.Flop:
            self.turn = card
            self.state = Step.Turn
        else:
            raise ValueError('Setting turn card not in flop state')

    def open_turn(self) -> None:

        self.deck.skip()
        self.turn = self.deck.next()
        self.state = Step.Turn

    def open_turn_with_network(self, table) -> None:

        self.open_turn()

        if table.online:
            table.network.turn(self.turn)
            sleep(Delay.Turn)

    def set_river_card(self, card: Card) -> None:

        if self.state == Step.Turn:
            self.river = card
            self.state = Step.River
        else:
            raise ValueError('Setting river card not in turn state')

    def open_river(self) -> None:

        self.deck.skip()
        self.river = self.deck.next()
        self.state = Step.River

    def open_river_with_network(self, table) -> None:

        self.open_river()

        if table.online:
            table.network.river(self.river)
            sleep(Delay.River)

    def open(self) -> None:

        if self.state == Step.Preflop:
            self.open_flop()

        elif self.state == Step.Flop:
            self.open_turn()

        elif self.state == Step.Turn:
            self.open_river()

        else:
            raise OverflowError('Board can not contain more than 5 cards')

    def open_with_network(self, table) -> None:

        if self.state == Step.Preflop:
            self.open_flop_with_network(table)

        elif self.state == Step.Flop:
            self.open_turn_with_network(table)

        elif self.state == Step.Turn:
            self.open_river_with_network(table)

        else:
            raise OverflowError('Board can not contain more than 5 cards')

    def open_all(self) -> None:

        if self.state == Step.Preflop:
            self.open_flop()

        if self.state == Step.Flop:
            self.open_turn()

        if self.state == Step.Turn:
            self.open_river()

    def open_all_with_network(self, table) -> None:

        if self.state == Step.Preflop:
            self.open_flop_with_network(table)

        if self.state == Step.Flop:
            self.open_turn_with_network(table)

        if self.state == Step.Turn:
            self.open_river_with_network(table)

    def get(self) -> Card.Cards:
        return self.get_from_step(self.state)

    def get_from_step(self, step: Step) -> Card.Cards:
        if step == Step.Preflop:
            return []

        elif step == Step.Flop:
            return [self.flop1, self.flop2, self.flop3]

        elif step == Step.Turn:
            return [self.flop1, self.flop2, self.flop3, self.turn]

        return [self.flop1, self.flop2, self.flop3, self.turn, self.river]

    def __str__(self):

        cards = self.get()
        return Card.str(cards) if cards else 'no cards'
