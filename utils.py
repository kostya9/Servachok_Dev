import math


class Coords(object):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def radius_calculation(self):
        return math.pow(math.pow(self.x, 2) + math.pow(self.y, 2), 1 / 2)

    def get_coord(self):
        return self.x, self.y

    def calc_distance(self, point):
        return math.pow(math.pow(self.x - point.x, 2) + math.pow(self.y - point.y, 2), 1 / 2)

    def __str__(self):
        return "({}, {})".format(self.x, self.y)
