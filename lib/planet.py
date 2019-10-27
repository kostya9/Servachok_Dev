import random
from enum import IntEnum
from typing import Dict

from utils import ID_GENERATOR


class PlanetType(IntEnum):
    SMALL = 1
    MEDIUM = 2
    BIG = 3


class Planet(object):
    cache: Dict[int, 'Planet'] = {}

    def __init__(self, coords, planet_type, owner=None, units_count=None):
        self.coords = coords
        self.type = planet_type

        if units_count:
            self.units_count = units_count
        else:
            self.units_count = random.randint(0, 40) * planet_type.value

        self.owner = owner
        self.__id = next(ID_GENERATOR)

        self.cache[self.__id] = self

    def get_dict(self) -> dict:
        return {
            'type': self.type,
            'owner': self.owner,
            'units_count': self.units_count,
            'coords': self.coords.get_dict(),
            'id': self.__id,
        }
