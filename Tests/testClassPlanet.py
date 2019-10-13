from planet import Planet, PlanetType
from utils import Coord
import unittest


class Test_case_Planet(unittest.TestCase):

    def setUp(self):
        self.coords=Coords(5,10)
        self.planet_type=PlanetType.SMALL
        self.owner="owner"
        self.p=Planet(self.coords,self.planet_type,self.owner)

    def test_right_init(self):
        self.assertEqual(self.p.coords,self.coords,"wrong coord init")
        self.assertEqual(self.p.type,self.type,"wrong type init")
        self.assertEqual(self.p.units_count,self.planet_type.value*50,"wrong count of units init")
        self.assertEqual(self.p.owner,self.owner,"wrong owner init")

    def test_get_dict(self):
        self.assertEqual(p.get_dict(), {'type': self.type, 'units_count': self.planet_type.value*50, 'owner': self.owner,'coords': self.coords.get_dict(), 'id': self.p.__id}, "wrong dictionary")



if __name__ == '__main__':
    unittest.main()
