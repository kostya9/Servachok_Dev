# screen size 16:9
import math
import random

import matplotlib.pyplot as plt
import numpy as np

from planet import Planet, PlanetType
from utils import Coords

SCREEN_MULTIPLIER = 100

PLAYERS = random.randint(2, 8)

# PLAYERS = 8

PLANET_FREE_SPACE_RADIUS = 50


class MapGenerator(object):
    LENGTH_MULTIPLIER = 16
    HEIGHT_MULTIPLIER = 9

    def __init__(self, screen_scale_multiplier):
        self.__screen_length = self.LENGTH_MULTIPLIER * screen_scale_multiplier
        self.__screen_height = self.HEIGHT_MULTIPLIER * screen_scale_multiplier
        self.__border_angle = math.atan(self.HEIGHT_MULTIPLIER / self.LENGTH_MULTIPLIER) * 180 / math.pi
        self.__planets = []
        self.__max_planet_count = random.randint(40, 55)
        # self.__max_planet_count = 45
        print(self.__max_planet_count)
        self.__players = -1
        self.__start_position_radius = 0
        self.__max_gen_try = 25

    def run(self, players_count):
        self.__players = players_count
        self.__generate_start_position(players_count)
        self.__generate_subplanet()
        self.__generate_separated_planet()
        return self.__planets

    def __generate_start_position(self, players_count):

        planets = [[0, Planet(Coords(0, 0), PlanetType.BIGGEST), 0]]

        alpha = random.randint(0, int(360 / players_count))
        for i in range(players_count):
            coord = Coords()
            tang = math.tan(alpha * math.pi / 180)

            if alpha >= 360:
                alpha -= 360

            if alpha == 90 or alpha == 270:
                coord.x = 0
                coord.y = self.__screen_height * math.sin(alpha * math.pi / 180) / 2
            elif alpha == 180 or alpha == 0:
                coord.y = 0
                coord.x = self.__screen_length * math.cos(alpha * math.pi / 180) / 2
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

            planets.append([coord.radius_calculation(), Planet(coord, PlanetType.BIG), alpha])
            alpha += 360 / players_count

        min_rad = min(planets[1:], key=lambda x: x[0])
        self.__start_position_radius = min_rad[0] - PLANET_FREE_SPACE_RADIUS

        for i in planets[1:]:
            i[1].coords.x = int(self.__start_position_radius * math.cos(i[2] * math.pi / 180))
            i[1].coords.y = int(self.__start_position_radius * math.sin(i[2] * math.pi / 180))
            i[0] = self.__start_position_radius

        self.__planets += [planet[1] for planet in planets]

    def __generate_subplanet(self):
        subplanet_max_count = round((self.__max_planet_count - self.__players - 1) * 0.6 / self.__players)
        max_try = 25
        for planet in self.__planets[1:]:
            subplanet_num = 0
            try_num = 0
            subplanets = []
            while True:
                sub_alpha = random.randint(0, 359)
                sub_radius = random.randint(2 * PLANET_FREE_SPACE_RADIUS,
                                            int(self.__start_position_radius * math.sin(
                                                math.pi / self.__players)) - PLANET_FREE_SPACE_RADIUS)
                check = True
                new_planet = Planet(Coords(sub_radius * math.cos(sub_alpha * math.pi / 180) + planet.coords.x,
                                           sub_radius * math.sin(sub_alpha * math.pi / 180) + planet.coords.y),
                                    random.choices([PlanetType.SMALL, PlanetType.MEDIUM, PlanetType.BIG],
                                                   [600, 300, 200])[0])

                if abs(new_planet.coords.x) > self.__screen_length / 2 - PLANET_FREE_SPACE_RADIUS or \
                        abs(new_planet.coords.y) > self.__screen_height / 2 - PLANET_FREE_SPACE_RADIUS:
                    try_num += 1
                    if try_num > max_try:
                        break
                    continue

                for i in subplanets:
                    if new_planet.coords.calc_distance(i.coords) < 2 * PLANET_FREE_SPACE_RADIUS:
                        check = False
                        break

                if check:
                    subplanets.append(new_planet)
                    try_num = 0
                else:
                    try_num += 1
                    if try_num > max_try:
                        break
                    continue

                subplanet_num += 1
                if subplanet_num >= subplanet_max_count:
                    break

            self.__planets += subplanets

    def __generate_separated_planet(self):
        separated_max_count = self.__max_planet_count - len(self.__planets)
        separated_num = 0
        try_num = 0
        separated = [self.__planets[0]]
        while True:
            x = random.randint(-self.__screen_length / 2, self.__screen_length / 2)
            y = random.randint(-self.__screen_height / 2, self.__screen_height / 2)

            check = True
            new_planet = Planet(Coords(x, y),
                                random.choices([PlanetType.SMALL, PlanetType.MEDIUM, PlanetType.BIG],
                                               [600, 300, 200])[0])

            if abs(new_planet.coords.x) > self.__screen_length / 2 - PLANET_FREE_SPACE_RADIUS or \
                    abs(new_planet.coords.y) > self.__screen_height / 2 - PLANET_FREE_SPACE_RADIUS:
                check = False

            subradius = self.__start_position_radius * math.sin(math.pi / self.__players)

            for i in self.__planets[1:1 + self.__players]:
                if new_planet.coords.calc_distance(i.coords) < subradius:
                    check = False
                    break

            # for i in self.__planets:
            #     # print(new_planet.coords.calc_distance(i[1].coords), i[0])
            #     if new_planet.coords.calc_distance(i.coords) < 2 * PLANET_FREE_SPACE_RADIUS:
            #         check = False
            #         break

            for i in separated:
                if new_planet.coords.calc_distance(i.coords) < 2 * PLANET_FREE_SPACE_RADIUS:
                    check = False
                    break

            if check:
                separated.append(new_planet)
                try_num = 0
            else:
                try_num += 1
                if try_num > self.__max_gen_try * 200:
                    break
                continue

            separated_num += 1
            if separated_num >= separated_max_count:
                break

        self.__planets += separated[1:]

    def display(self):
        print(len(self.__planets))
        coords = []

        # subplanet_radius = self.__start_position_radius * math.sin(math.pi / self.__players)

        plt.figure()

        # for i in self.__planets[1: 1 + self.__players]:
        #     position = i.coords.get_coord()
        #     c = plt.Circle(position, radius=subplanet_radius, fill=False, color="blue")
        #     plt.gca().add_patch(c)

        colors = ['red', 'orange', 'brown', 'purple']

        for i in self.__planets:
            position = i.coords.get_coord()
            coords.append(position)
        #     b = plt.Circle(position, radius=PLANET_FREE_SPACE_RADIUS, color=colors[i.type.value - 1])
        #     plt.gca().add_patch(b)

        X = np.array(coords)

        plt.axis("equal")
        plt.xlim((-self.__screen_length / 2 - 150, self.__screen_length / 2 + 150))
        plt.ylim((-self.__screen_height / 2 - 150, self.__screen_height / 2 + 150))

        t1 = plt.Polygon(X[1:1 + self.__players], fill=False, color="black")
        # t2 = plt.Circle((0.0, 0.0), radius=self.__start_position_radius, fill=False, color="green")
        plt.gca().add_patch(t1)
        # plt.gca().add_patch(t2)

        screen = plt.Rectangle((-self.__screen_length / 2, -self.__screen_height / 2), self.__screen_length,
                               self.__screen_height, fill=False,
                               color="black")
        plt.gca().add_patch(screen)
        colors = [colors[i.type.value - 1] for i in self.__planets]

        plt.scatter(X[:, 0], X[:, 1], color=colors)

        plt.show()


test = MapGenerator(SCREEN_MULTIPLIER)
print(test.run(PLAYERS))
test.display()
