# screen size 16:9
import math
import random
from typing import List

import matplotlib.pyplot as plt
import numpy as np

from planet import Planet, PlanetType
from utils import Coords

SCREEN_MULTIPLIER = 120

PLAYERS = random.randint(2, 8)

# PLAYERS = 8


class _InternalPlanet(object):
    def __init__(
        self,
        start_position_radius: float = 0,
        planet: Planet = Planet(Coords(0, 0), PlanetType.BIGGEST),
        alpha: float = 0
    ):
        self.start_position_radius = start_position_radius
        self.planet = planet
        self.alpha = alpha


class MapGenerator(object):
    LENGTH_MULTIPLIER = 16
    HEIGHT_MULTIPLIER = 9
    SUBPLANET_MAX_COUNT_MULTIPLIER = 0.6

    def __init__(self, screen_scale_multiplier: float = SCREEN_MULTIPLIER, planet_free_space_radius: float = None):
        self.__screen_length = self.LENGTH_MULTIPLIER * screen_scale_multiplier
        self.__screen_height = self.HEIGHT_MULTIPLIER * screen_scale_multiplier
        self.__border_angle = math.atan(self.HEIGHT_MULTIPLIER / self.LENGTH_MULTIPLIER) * 180 / math.pi
        self.__planets: List[Planet] = []
        self.__max_planet_count = random.randint(40, 55)
        # self.__max_planet_count = 45
        # print(self.__max_planet_count)
        self.__players = -1
        self.__start_position_radius = 0
        self.__max_gen_try_subplanets = 25
        self.__max_gen_try_separated_planets = self.__max_gen_try_subplanets * 200

        if planet_free_space_radius:
            self.__planet_free_space_radius = planet_free_space_radius
        else:
            self.__planet_free_space_radius = round(50 / 120 * screen_scale_multiplier)

    def run(self, players_ids: List[int]) -> List[Planet]:
        self.__players = len(players_ids)
        self.__generate_start_position(players_ids)
        self.__generate_subplanets()
        self.__generate_separated_planets()
        return self.__planets

    def __generate_start_position(self, players_ids: List[int]):
        players_count = len(players_ids)

        internal_planets = []

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

            internal_planets.append(_InternalPlanet(
                start_position_radius=coord.radius_calculation(),
                planet=Planet(coord, PlanetType.BIG, player_id),
                alpha=alpha
            ))
            alpha += 360 / players_count

        planet_with_min_radius = min(internal_planets, key=lambda x: x.start_position_radius)
        self.__start_position_radius = planet_with_min_radius.start_position_radius - self.__planet_free_space_radius

        for ip in internal_planets:
            ip.planet.coords.x = int(self.__start_position_radius * math.cos(ip.alpha * math.pi / 180))
            ip.planet.coords.y = int(self.__start_position_radius * math.sin(ip.alpha * math.pi / 180))
            ip.start_position_radius = self.__start_position_radius

        internal_planets.insert(0, _InternalPlanet())
        self.__planets.extend(ip.planet for ip in internal_planets)

    @staticmethod
    def __get_random_planet_type() -> PlanetType:
        sizes = [PlanetType.SMALL, PlanetType.MEDIUM, PlanetType.BIG, ]
        weighs = [600, 300, 200, ]
        return random.choices(
            sizes,
            weighs
        )[0]

    def __generate_subplanets(self):
        subplanet_max_count = round(
            (self.__max_planet_count - self.__players - 1) * self.SUBPLANET_MAX_COUNT_MULTIPLIER / self.__players
        )
        for planet in self.__planets[1:]:
            subplanet_num = 0
            try_num = 0
            subplanets = []
            while (try_num <= self.__max_gen_try_subplanets) and (subplanet_num < subplanet_max_count):
                sub_alpha = random.randint(0, 359)
                sub_radius = random.randint(
                    2 * self.__planet_free_space_radius,
                    int(
                        self.__start_position_radius * math.sin(math.pi / self.__players)
                    ) - self.__planet_free_space_radius
                )
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
        separated_max_count = self.__max_planet_count - len(self.__planets)
        separated_num = 0
        try_num = 0
        separated = [self.__planets[0], ]
        while (try_num <= self.__max_gen_try_separated_planets) and (separated_num < separated_max_count):
            x = random.randint(-self.__screen_length / 2, self.__screen_length / 2)
            y = random.randint(-self.__screen_height / 2, self.__screen_height / 2)

            check = True
            new_planet = Planet(
                Coords(x, y),
                self.__get_random_planet_type()
            )

            if abs(new_planet.coords.x) > self.__screen_length / 2 - self.__planet_free_space_radius or (
                abs(new_planet.coords.y) > self.__screen_height / 2 - self.__planet_free_space_radius
            ):
                check = False

            subradius = self.__start_position_radius * math.sin(math.pi / self.__players)

            for p in self.__planets[1:1 + self.__players]:
                if new_planet.coords.calc_distance(p.coords) < subradius:
                    check = False
                    break

            # for p in self.__planets:
            #     # print(new_planet.coords.calc_distance(p[1].coords), p[0])
            #     if new_planet.coords.calc_distance(p.coords) < 2 * PLANET_FREE_SPACE_RADIUS:
            #         check = False
            #         break

            for s in separated:
                if new_planet.coords.calc_distance(s.coords) < 2 * self.__planet_free_space_radius:
                    check = False
                    break

            if check:
                separated.append(new_planet)
                try_num = 0
            else:
                try_num += 1
                continue

            separated_num += 1

        self.__planets += separated[1:]

    def display(self):
        # print(len(self.__planets))
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

#
# test = MapGenerator(SCREEN_MULTIPLIER)
# print(test.run(PLAYERS))
# test.display()
