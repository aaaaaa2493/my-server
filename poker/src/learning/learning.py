from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from numpy import array
from pickle import load, dump
from learning.data_sets.base_poker_decision import DecisionClass
from learning.data_sets.data_set import DataSet


class Learning:
    def __init__(self):
        self._data: DataSet = None

    def create_data_set(self, cls: DecisionClass) -> None:
        self._data = DataSet(cls)

    def add_data_set(self, games_path: str) -> None:
        self._data.add_data_from_folder(games_path)
        print('data set contains', len(self._data.decisions), 'decisions with answers')

    def save_data_set(self, path: str) -> None:
        self._data.save(path)

    def load_data_set(self, path: str) -> None:
        self._data = DataSet.load(path)

    def learning(self) -> None:
        x = self._data.decisions.get_data()
        y = self._data.decisions.get_answers()
        print(x.shape)
        print(y.shape)
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25)
        print(x_train.shape)
        print(x_test.shape)
        # mlp = MLPClassifier(hidden_layer_sizes=(10, 10))
        mlp = load(open('networks/nn2', 'rb'))
        # mlp.fit(x_train, y_train)
        print('train', mlp.score(x_train, y_train))
        print('test ', mlp.score(x_test, y_test))
        # dump(mlp, open('networks/nn2', 'wb'))
        for x, y in zip(x_test[:100], y_test[:100]):
            print(mlp.predict(array([x])), y)
