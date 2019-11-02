"""
Модуль генерации карты
screen size 16:9
"""

import math
import random
from typing import List

import matplotlib.pyplot as plt
import numpy as np

from lib.planet import Planet, PlanetType
from utils import Coords, Config

CFG = Config()

SCREEN_MULTIPLIER = int(CFG['Screen']['multiplier'])


class MapGenerator(object):
    LENGTH_MULTIPLIER = int(CFG['Screen']['length_multiplier'])
    HEIGHT_MULTIPLIER = int(CFG['Screen']['height_multiplier'])

    def __init__(self, screen_scale_multiplier=SCREEN_MULTIPLIER, planet_free_space_radius=None):
        self.__screen_length = self.LENGTH_MULTIPLIER * screen_scale_multiplier
        self.__screen_height = self.HEIGHT_MULTIPLIER * screen_scale_multiplier
        self.__border_angle = math.atan(self.HEIGHT_MULTIPLIER / self.LENGTH_MULTIPLIER) * 180 / math.pi
        self.__planets: List[Planet] = []
        self.__max_planet_count = random.randint(40, 55)
        self.__players = -1
        self.__start_position_radius = 0
        self.__max_gen_try_subplanets = 25
        self.__max_gen_try_separated_planets = self.__max_gen_try_subplanets * 200

        if planet_free_space_radius:
            self.__planet_free_space_radius = planet_free_space_radius
        else:
            self.__planet_free_space_radius = round(50 / 120 * screen_scale_multiplier)

    def run(self, players_ids: List[int]) -> List[Planet]:
        """ запускает генерацию карты """

        self.__players = len(players_ids)
        self.__generate_start_position(players_ids)
        self.__generate_subplanets()
        self.__generate_separated_planets()
        return self.__planets

    def __generate_start_position(self, players_ids: List[int]):
        """ генерирует начальные планеты игроков """

        players_count = len(players_ids)
        planets = []
        alpha = random.randint(0, int(360 / players_count))

        for player_id in players_ids:
            coord = Coords()
            tang = math.tan(alpha * math.pi / 180)

            if alpha >= 360:
                alpha -= 360

            if alpha in (90, 270, ):
                coord.x = 0
                coord.y = self.__screen_height * math.sin(alpha * math.pi / 180) / 2
            elif alpha in (0, 180, ):
                coord.x = self.__screen_length * math.cos(alpha * math.pi / 180) / 2
                coord.y = 0
            elif 0 < alpha < 90:
                if alpha >= self.__border_angle:
                    height_border = self.__screen_height / 2
                    coord.x = height_border / tang
                    coord.y = height_border
                else:
                    height_border = self.__screen_length / 2
                    coord.x = height_border
                    coord.y = height_border * tang
            elif 90 < alpha < 180:
                if alpha <= 180 - self.__border_angle:
                    height_border = self.__screen_height / 2
                    coord.x = height_border / tang
                    coord.y = height_border
                else:
                    height_border = self.__screen_length / 2
                    coord.x = -height_border
                    coord.y = abs(height_border * tang)
            elif 180 < alpha < 270:
                if alpha >= 180 + self.__border_angle:
                    height_border = self.__screen_height / 2
                    coord.x = -height_border / tang
                    coord.y = -height_border
                else:
                    height_border = self.__screen_length / 2
                    coord.x = -height_border
                    coord.y = -height_border * tang
            elif 270 < alpha < 360:
                if alpha <= 360 - self.__border_angle:
                    height_border = self.__screen_height / 2
                    coord.x = abs(height_border / tang)
                    coord.y = -height_border
                else:
                    height_border = self.__screen_length / 2
                    coord.x = self.__screen_length / 2
                    coord.y = height_border * tang

            planets.append([coord.radius_calculation(), Planet(coord, PlanetType.BIG, player_id,
                                                               units_count=100), alpha])
            alpha += 360 / players_count

        min_rad = min(planets, key=lambda x: x[0])
        self.__start_position_radius = min_rad[0] - self.__planet_free_space_radius

        for i in planets:
            i[1].coords.x = int(self.__start_position_radius * math.cos(i[2] * math.pi / 180))
            i[1].coords.y = int(self.__start_position_radius * math.sin(i[2] * math.pi / 180))
            i[0] = self.__start_position_radius

        self.__planets += [planet[1] for planet in planets]

    def __get_random_planet_type(self):
        """ выбирает тип планеты из спика в зависимости от веса элемента """

        return random.choices([PlanetType.SMALL, PlanetType.MEDIUM, PlanetType.BIG], [600, 300, 200])[0]

    def __generate_subplanets(self):
        """ генерирует планеты вокруг планет игроков """

        subplanet_max_count = round((self.__max_planet_count - self.__players - 1) * 0.6 / self.__players)

        for planet in self.__planets[:self.__players]:

            subplanet_num = 0
            try_num = 0
            subplanets = []

            while (try_num <= self.__max_gen_try_subplanets) and (subplanet_num < subplanet_max_count):
                sub_alpha = random.randint(0, 359)
                sub_radius = random.randint(
                    2 * self.__planet_free_space_radius,
                    int(self.__start_position_radius * math.sin(math.pi / self.__players))
                    - self.__planet_free_space_radius)

                check = True
                new_planet = Planet(
                    Coords(
                        sub_radius * math.cos(sub_alpha * math.pi / 180) + planet.coords.x,
                        sub_radius * math.sin(sub_alpha * math.pi / 180) + planet.coords.y
                    ),
                    self.__get_random_planet_type()
                )

                if (abs(new_planet.coords.x) > self.__screen_length / 2 - self.__planet_free_space_radius) or (
                        abs(new_planet.coords.y) > self.__screen_height / 2 - self.__planet_free_space_radius
                ):
                    try_num += 1
                    continue

                for sp in subplanets:
                    if new_planet.coords.calc_distance(sp.coords) < 2 * self.__planet_free_space_radius:
                        check = False
                        break

                if check:
                    subplanets.append(new_planet)
                    try_num = 0
                else:
                    try_num += 1
                    continue

                subplanet_num += 1

            self.__planets += subplanets

    def __generate_separated_planets(self):
        """ генерирует оставшиеся планеты (добавляет планеты в пустых местах карты, теоретически) """

        separated_max_count = self.__max_planet_count - len(self.__planets)
        separated_num = 0
        try_num = 0
        separated = []

        while True:
            x = random.randint(-self.__screen_length / 2, self.__screen_length / 2)
            y = random.randint(-self.__screen_height / 2, self.__screen_height / 2)

            check = True
            new_planet = Planet(Coords(x, y), self.__get_random_planet_type())

            if abs(new_planet.coords.x) > self.__screen_length / 2 - self.__planet_free_space_radius or (
                    abs(new_planet.coords.y) > self.__screen_height / 2 - self.__planet_free_space_radius
            ):
                check = False

            subradius = self.__start_position_radius * math.sin(math.pi / self.__players)

            for i in self.__planets[:self.__players]:
                if new_planet.coords.calc_distance(i.coords) < subradius:
                    check = False
                    break

            for i in separated:
                if new_planet.coords.calc_distance(i.coords) < 2 * self.__planet_free_space_radius:
                    check = False
                    break

            if check:
                separated.append(new_planet)
                try_num = 0
            else:
                try_num += 1
                if try_num > self.__max_gen_try_separated_planets:
                    break
                continue

            separated_num += 1
            if separated_num >= separated_max_count:
                break

        self.__planets += separated

    def display(self):
        """ отображает карту (при тестировании) """

        coords = []

        plt.figure()

        colors = ['red', 'orange', 'brown', 'purple']

        for i in self.__planets:
            position = i.coords.get_coord()
            coords.append(position)

        X = np.array(coords)

        plt.axis("equal")
        plt.xlim((-self.__screen_length / 2 - 150, self.__screen_length / 2 + 150))
        plt.ylim((-self.__screen_height / 2 - 150, self.__screen_height / 2 + 150))

        t1 = plt.Polygon(X[:self.__players], fill=False, color="black")
        plt.gca().add_patch(t1)

        screen = plt.Rectangle((-self.__screen_length / 2, -self.__screen_height / 2), self.__screen_length,
                               self.__screen_height, fill=False,
                               color="black")
        plt.gca().add_patch(screen)
        colors = [colors[i.type.value - 1] for i in self.__planets]

        plt.scatter(X[:, 0], X[:, 1], color=colors)

        plt.show()
