from utils import Coords
import unittest

x = 10
y = 15


class Test_case_coord(unittest.TestCase):

    def test_constructor(self):
        c = Coords(x, y)
        self.assertEqual(c.x, x,
                         'incorrect x')
        self.assertEqual(c.y, y, 'incorrect y')

    def test_str(self):
        c = Coords(x, y)
        self.assertEqual(c.__str__(), "(10, 15)", 'incorrect format of str')

    def test_get_dictionary(self):
        c = Coords(x, y)
        self.assertEqual(c.get_dict()["x"], x, 'incorrect convertion to dict (x)')
        self.assertEqual(c.get_dict()["y"], y, 'incorrect convertion to dict (x)')

    def test_radius_calculation(self):
        c = Coords(x, y)
        self.assertEqual(c.radius_calculation(), (c.x ** 2 + c.y ** 2) ** (0.5), 'incorrect radius-vector')

    def test_get_coord(self):
        c = Coords(x, y)
        self.assertEqual(c.get_coord(), (x, y), 'returned value is incorrect')

    def test_calc_distance(self):
        c = Coords(x, y)
        testList = [Coords(0, 0), Coords(x, y), Coords(5, 12)]
        for i in range(len(testList)):
            with self.subTest(i=i):
                self.assertEqual(c.calc_distance(testList[i]),
                                 ((x - testList[i].x) ** 2 + (y - testList[i].y) ** 2) ** 0.5,
                                 "wrong calc_distance for point " + str(testList[i].x) + "," + str(testList[i].y))
