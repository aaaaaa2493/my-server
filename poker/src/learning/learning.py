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
        mlp = MLPClassifier(hidden_layer_sizes=(200, 100, 100))
        mlp.fit(x_train, y_train)
        Debug.learning('train', mlp.score(x_train, y_train))
        Debug.learning('test ', mlp.score(x_test, y_test))
        if not exists('networks'):
            mkdir('networks')
        dump(mlp, open(f'networks/{path}', 'wb'))

        # nn1 10x2 - 0.753
        # nn1 10x3 - 0.752

        # nn2 10x2  - 0.751
        # nn2 10x3  - 0.755
        # nn2 100x2 - 0.761
        # nn2 100x3 - 0.762

        # nn3 10x2  - 0.703
        # nn3 10x3  - 0.705
        # nn3 100x2 - 0.715

        # nn4 10x2  - 0.71

        # nn5 10x2  - 0.724
        # nn5 10x3  - 0.725
        # nn5 100x2 - 0.738
        # nn5 100x3 - 0.739

        # nn6 100x2 - 0.762
