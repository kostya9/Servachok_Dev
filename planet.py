from enum import Enum

from utils import Coords


class PlanetType(Enum):
    SMALL = 1
    MEDIUM = 2
    BIG = 3
    BIGGEST = 4


class Planet:
    def __init__(self, coords, type , owner=None):
        self.coords = coords
        self.type = type
        self.units_count = 50 * type.value
        self.owner = owner

    def __setattr__(self, key, value):
    #     print("|I'm changed {}={}".format(key,value))
        self.__dict__[key] = value


# test = Planet(Coords(), PlanetType.SMALL , 10)
#
# test.units_count = 15
# print(test.units_count)
