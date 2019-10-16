import random
from enum import IntEnum

from utils import id_generator


class PlanetType(IntEnum):
    SMALL = 1
    MEDIUM = 2
    BIG = 3


class Planet:
    cache = {}

    def __init__(self, coords, planet_type, owner=None, units_count=None):
        self.coords = coords
        self.type = planet_type
        if units_count:
            self.units_count = units_count
        else:
            self.units_count = random.randint(0, 40) * planet_type.value
        self.owner = owner
        self.__id = next(id_generator)

        self.cache[self.__id] = self

    def get_dict(self):
        result_dict = {'type': self.type, 'units_count': self.units_count, 'owner': self.owner,
                       'coords': self.coords.get_dict(), 'id': self.__id}
        return result_dict
