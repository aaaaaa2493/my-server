from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from pickle import dump
from os.path import exists
from os import mkdir
from learning.data_sets.decision_model.base_poker_decision import DecisionClass
from learning.data_sets.data_set import DataSet
from special.debug import Debug


class Learning:
    def __init__(self):
        self._data: DataSet = None

    def create_data_set(self, cls: DecisionClass) -> None:
        self._data = DataSet(cls)

    def add_data_set(self, games_path: str) -> None:
        self._data.add_data_from_folder(games_path)
        Debug.learning('data set contains', len(self._data.decisions), 'decisions with answers')

    def save_data_set(self, path: str) -> None:
        self._data.save(path)

    def load_data_set(self, path: str) -> None:
        self._data = DataSet.load(path)

    def learning(self, path: str) -> None:
        x = self._data.decisions.get_data()
        y = self._data.decisions.get_answers()
        Debug.learning(f'Start learning from {y.size} samples')
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25)
        mlp = MLPClassifier(hidden_layer_sizes=(10, 10))
        mlp.fit(x_train, y_train)
        Debug.learning('train', mlp.score(x_train, y_train))
        Debug.learning('test ', mlp.score(x_test, y_test))
        if not exists('networks'):
            mkdir('networks')
        dump(mlp, open(f'networks/{path}', 'wb'))
