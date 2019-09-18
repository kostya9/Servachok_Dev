# screen size 16:9
import math
import random

import matplotlib.pyplot as plt
import numpy as np

SCREEN_MULTIPLIER = 120

PLAYERS = 3


class Coords(object):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def radius_calculation(self):
        return math.pow(math.pow(self.x, 2) + math.pow(self.y, 2), 1 / 2)

    def get_coord(self):
        return self.x, self.y

    def __str__(self):
        return "({}, {})".format(self.x, self.y)


class MapGenerator(object):
    LENGTH_MULTIPLIER = 16
    HEIGHT_MULTIPLIER = 9

    def __init__(self, screen_scale_multiplier):
        self.__screen_length = self.LENGTH_MULTIPLIER * screen_scale_multiplier
        self.__screen_height = self.HEIGHT_MULTIPLIER * screen_scale_multiplier
        self.__border_angle = math.atan(self.HEIGHT_MULTIPLIER / self.LENGTH_MULTIPLIER) * 180 / math.pi
        self.__planets = []

    def run(self, players_count):
        self.__generate_start_position(players_count)
        return self.__planets

    def __generate_start_position(self, players_count):

        alpha = random.randint(0, int(360 / players_count))

        for i in range(players_count):
            coord = Coords()
            tang = math.tan(alpha * math.pi / 180)

            if alpha >= 360:
                alpha -= 360

            if alpha == 90:
                coord.x = 0
                coord.y = self.__screen_height / 2
            elif alpha == 270:
                coord.x = 0
                coord.y = -self.__screen_height / 2
            elif alpha == 180:
                coord.y = 0
                coord.x = -self.__screen_length / 2
            elif 0 < alpha < 90:
                if alpha >= self.__border_angle:
                    height_border = self.__screen_height / 2
                    coord.x = height_border / tang
                    coord.y = height_border
                else:
                    height_border = self.__screen_length / 2
                    coord.y = height_border * tang
                    coord.x = height_border
            elif 180 < alpha < 270:
                if alpha >= self.__border_angle + 180:
                    height_border = self.__screen_height / 2
                    coord.x = -height_border / tang
                    coord.y = -height_border
                else:
                    height_border = self.__screen_length / 2
                    coord.y = -height_border * tang
                    coord.x = -height_border
            elif 90 < alpha < 180:
                if alpha <= 180 - self.__border_angle:
                    height_border = self.__screen_height / 2
                    coord.x = height_border / tang
                    coord.y = height_border
                else:
                    height_border = self.__screen_length / 2
                    coord.y = abs(height_border * tang)
                    coord.x = -height_border
            elif 270 < alpha < 360:
                if alpha <= 360 - self.__border_angle:
                    height_border = self.__screen_height / 2
                    coord.x = abs(height_border / tang)
                    coord.y = -height_border
                else:
                    height_border = self.__screen_length / 2
                    coord.y = height_border * tang
                    coord.x = self.__screen_length / 2
            else:
                coord.y = 0
                coord.x = self.__screen_length / 2
            self.__planets.append([coord.radius_calculation(), coord, alpha])
            alpha += 360 / players_count

        min_rad = min(self.__planets, key=lambda x: x[0])
        circle_rad = min_rad[0]

        for i in self.__planets:
            i[1].x = int(circle_rad * math.cos(i[2] * math.pi / 180))
            i[1].y = int(circle_rad * math.sin(i[2] * math.pi / 180))
            i[0] = circle_rad

    def display(self):
        min_rad = min(self.__planets, key=lambda x: x[0])
        circle_rad = min_rad[0]
        coords = []

        subplanet_radius = circle_rad * math.sin(math.pi / PLAYERS)

        plt.figure()

        for i in self.__planets:
            position = i[1].get_coord()
            coords.append(position)
            c = plt.Circle(position, radius=subplanet_radius, fill=False, color="blue")
            plt.gca().add_patch(c)

        X = np.array(coords)

        plt.axis("equal")
        plt.xlim((-self.__screen_length / 2, self.__screen_length / 2))
        plt.ylim((-self.__screen_height / 2, self.__screen_height / 2))

        t1 = plt.Polygon(X, fill=False, color="red")
        t2 = plt.Circle((0.0, 0.0), radius=circle_rad, fill=False, color="green")
        plt.gca().add_patch(t1)
        plt.gca().add_patch(t2)

        plt.scatter(X[:, 0], X[:, 1])

        plt.show()


test = MapGenerator(SCREEN_MULTIPLIER)
print(test.run(PLAYERS))
test.display()
