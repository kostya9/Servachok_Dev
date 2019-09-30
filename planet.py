from enum import IntEnum

from utils import Coords


class PlanetType(IntEnum):
    SMALL = 1
    MEDIUM = 2
    BIG = 3
    BIGGEST = 4


class Planet:
    def __init__(self, coords, planet_type, owner=None):
        self.coords = coords
        self.type = planet_type
        self.units_count = 50 * planet_type.value
        self.used_units_count = 0
        self.owner = owner

    def __setattr__(self, key, value):
    #     print("|I'm changed {}={}".format(key,value))
        self.__dict__[key] = value

    # def __json__(self):
    #     return self.__dict__
    #
    # for_json = __json__  # supported by simplejson

    # @classmethod
    # def from_json(cls, json):
    #     obj = cls()
    #     obj.a = json['a']
    #     obj.b = json['b']
    #     return obj

# test = Planet(Coords(), PlanetType.SMALL , 10)
#
# test.units_count = 15
# print(test.units_count)


# import simplejson

# planets = [
#     Planet(Coords(1, 2), PlanetType.MEDIUM, 1).__dict__,
#     Planet(Coords(3, 3), PlanetType.BIG, None).__dict__,
#     Planet(Coords(2, 1), PlanetType.MEDIUM, 2).__dict__,
#     Planet(Coords(2, 2), PlanetType.BIG, None).__dict__,
# ]

# print(planets)
# print(simplejson.dumps(Planet(Coords(1, 2).__dict__, PlanetType.MEDIUM, 1), for_json=True))
# print(json.loads(json.dumps(planets)))
