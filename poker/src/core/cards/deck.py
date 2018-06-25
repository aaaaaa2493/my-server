from random import shuffle
from core.cards.card import Card, Cards


class NotEnoughCards(Exception):
    pass


class Deck:

    def __init__(self):
        self.cards: Cards = Card.cards_52()
        self.used: Cards = []

    def next(self) -> Card:

        if not self.cards:
            raise NotEnoughCards('All 52 cards of the deck is already used')

        card = self.cards[0]

        self.cards[:1] = []
        self.used += [card]

        return card

    def merge(self) -> None:
        self.cards += self.used
        self.used = []

    def curr(self) -> Card:
        return self.cards[0]

    def shuffle(self) -> None:
        self.merge()
        shuffle(self.cards)

    def skip(self, count: int = 1) -> None:
        cards = self.cards[:count]
        self.cards[:count] = []
        self.used += cards

    def __len__(self):
        return len(self.cards)
