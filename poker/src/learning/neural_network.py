from scipy.interpolate import splrep, splev
from matplotlib.pyplot import plot, show
from numpy import linspace


class NeuralNetwork:

    class PokerDecision:

        class Bubble:

            # coefficients for y = ax**2 + bx + c
            A_COEFFICIENT = 1501 / 1764
            B_COEFFICIENT = 10375 / 588
            C_COEFFICIENT = - 8375 / 882

            def __init__(self, total_players: int, total_prizes: int):

                a = self.A_COEFFICIENT
                b = self.B_COEFFICIENT
                c = self.C_COEFFICIENT - total_players

                self.total_prizes = total_prizes
                self.total_players = total_players

                self.bubble_count = round((-b + (b*b - 4*a*c)**.5) / (2*a))

                x_points = [total_prizes - 1,
                            total_prizes,
                            total_prizes + 1,
                            total_prizes + self.bubble_count + 1,
                            total_prizes + 2 * self.bubble_count + 1,
                            total_prizes + 3 * self.bubble_count + 1,
                            total_prizes + 4 * self.bubble_count + 1,
                            total_prizes + 5 * self.bubble_count + 1,
                            total_prizes + 6 * self.bubble_count + 1,
                            total_prizes + 7 * self.bubble_count + 1,
                            total_players + 7 * self.bubble_count + 1,
                            total_players + 7 * self.bubble_count + 2,
                            total_players + 7 * self.bubble_count + 3]

                y_points = [1, 1, 1, 0.8, 0.2, 0.02, 0.002, 0, 0, 0, 0, 0, 0]

                self.spline = splrep(x_points, y_points)

            def get(self, point: float) -> float:
                if point < self.total_prizes + 1 or point > self.total_players:
                    return 0
                return float(splev([point], self.spline))

            def show(self, points: int = 10000):
                x_coords = linspace(0, self.total_players, points)
                y_coords = [self.get(i) for i in x_coords]
                plot(x_coords, y_coords)
                show()
