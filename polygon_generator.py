import sys
import random
import math

# based on
# https://github.com/bast/polygenerator

class PolyGenerator:
    @staticmethod
    def random_polygon(num_points, scale=1):
        assert num_points > 2

        angles = [random.uniform(0.0, math.pi * 2.0) for _ in range(num_points)]

        polygon = []
        for angle in sorted(angles):
            r = random.uniform(0.2, 1.0)
            x = r * math.cos(angle)
            y = r * math.sin(angle)
            polygon.append((x, y))

        if PolyGenerator.polygon_is_clockwise(polygon):
            polygon = list(reversed(polygon))

        # return polygon
        return PolyGenerator.fit_to_bbox(polygon, scale=scale)

    @staticmethod
    def polygon_is_clockwise(polygon) -> bool:
        num_points = len(polygon)
        s = 0.0
        for i in range(num_points):
            j = (i + 1) % num_points
            s += (polygon[j][0] - polygon[i][0]) * (polygon[j][1] + polygon[i][1])
        return s > 0.0

    @staticmethod
    def fit_to_bbox(points, scale):
        x_min, x_max, y_min, y_max = PolyGenerator.get_bbox(points)

        scale_x = scale / (x_max - x_min)
        scale_y = scale / (y_max - y_min)

        return [((x - x_min) * scale_x, (y - y_min) * scale_y) for (x, y) in points]

    @staticmethod
    def get_bbox(points):
        huge = sys.float_info.max
        x_min = huge
        x_max = -huge
        y_min = huge
        y_max = -huge
        for (x, y) in points:
            x_min = min(x_min, x)
            x_max = max(x_max, x)
            y_min = min(y_min, y)
            y_max = max(y_max, y)
        return x_min, x_max, y_min, y_max


# test drive
if __name__ == '__main__':
    import matplotlib.pyplot as plt

    # show polygon on a plot
    def plot_polygon(polygon):
        plt.figure()
        plt.gca().set_aspect("equal")
        for i, (x, y) in enumerate(polygon):
            plt.text(x, y, str(i), horizontalalignment="center", verticalalignment="center")

        # just so that it is plotted as closed polygon
        polygon.append(polygon[0])

        xs, ys = zip(*polygon)
        plt.plot(xs, ys, "r-", linewidth=0.4)
        plt.show()


    while True:
        test_polygon = PolyGenerator.random_polygon(num_points=15)
        print(test_polygon)
        plot_polygon(test_polygon)

