from learning.data_sets.base_poker_decision import DecisionClass
from learning.data_sets.data_set import DataSet


class Learning:
    def __init__(self):
        self._data: DataSet = None

    def create_data_set(self, cls: DecisionClass) -> None:
        self._data = DataSet(cls)

    def add_data_set(self, games_path: str) -> None:
        self._data.add_data_from_folder(games_path)

    def save_data_set(self, path: str) -> None:
        self._data.save(path)
