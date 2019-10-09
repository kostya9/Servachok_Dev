from enum import IntEnum
from typing import Dict

from utils import Coords, ID_GENERATOR


class PlanetType(IntEnum):
    SMALL = 1
    MEDIUM = 2
    BIG = 3
    BIGGEST = 4


class Planet(object):
    __UNITS_PER_PLANET_TYPE_COUNT = 50
    cache: Dict[int, 'Planet'] = {}

    def __init__(self, coords: Coords, planet_type: PlanetType, owner: int = None):
        self.coords = coords
        self.type = planet_type
        self.owner = owner
        self.units_count = self.__UNITS_PER_PLANET_TYPE_COUNT * planet_type.value
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
