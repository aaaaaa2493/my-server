from holdem.player.player import Player
from holdem.play.play import Play
from holdem.play.result import Result
from holdem.base_network import BaseNetwork


class DummyPlayer(Player):
    def __init__(self, _id: int, name: str, money: int):
        super().__init__(_id, money, False, name, Play(), BaseNetwork())

    def decide(self, *args) -> Result:
        return Result.Fold
