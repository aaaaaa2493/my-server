from pickle import load
from numpy import array
from typing import Callable, Tuple
from sklearn.neural_network import MLPClassifier
from holdem.player.player import Player
from holdem.play.play import Play
from holdem.play.option import Option
from holdem.base_network import BaseNetwork


class BaseNeuralNetworkPlayer(Player):
    def __init__(self, _id: int, money: int, path: str):
        super().__init__(_id, money, False, path, Play(), BaseNetwork())
        self.play.name = path
        self.nn: MLPClassifier = load(open(f'networks/{path}', 'rb'))

    @staticmethod
    def create_input(*args):
        return array([array(args)])

    def _decide(self, **kwargs) -> Tuple[Option, int]:
        raise NotImplementedError('NeuralNetworkPlayer::decide')


NeuralNetworkClass = Callable[..., BaseNeuralNetworkPlayer]
