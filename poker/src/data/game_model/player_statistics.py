class PlayerStatistics:
    def __init__(self):
        self._activated = 0
        self._total_actions = 0

    def get_stats(self):
        if self._total_actions == 0:
            return 0
        return self._activated / self._total_actions

    def activate(self):
        self._activated += 1
        self._total_actions += 1

    def skip(self):
        self._total_actions += 1
