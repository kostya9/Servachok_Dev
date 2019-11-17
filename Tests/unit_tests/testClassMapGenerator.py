from lib.map_generator import MapGenerator
import unittest


class Test_case_MapGenerator(unittest.TestCase):

    def setUp(self):
        self.mg = MapGenerator()

    def test_check_planets_count(self):
        a = self.mg.run([1, 2])
        self.assertEqual(len(a) >= 40 & len(a) <= 55, True, "wrong planets count")

    def test_check_start_position_equal_radius_generated(self):  # Точность теста около 1 процента +-
        a = self.mg._MapGenerator__generate_start_position([1, 2, 3, 4, 5])
        temp = self.mg._MapGenerator__planets[1].coords.radius_calculation()
        for i in range(len(self.mg._MapGenerator__planets) - 1):
            self.assertEqual(self.mg._MapGenerator__planets[i + 1].coords.radius_calculation() - temp < (temp / 100),
                             True, "radiuses arent the same")

    def test_check_start_position_player_to_player_distance(self):  # Точность теста около 1 процента +-
        players_ids = [1, 2, 3, 4, 5, 6, 7, 8]
        a = self.mg._MapGenerator__generate_start_position(players_ids)
        temp = self.mg._MapGenerator__planets[0].coords.calc_distance(
            self.mg._MapGenerator__planets[len(players_ids)-1].coords)
        for i in range(len(players_ids) - 1):
            self.assertEqual(self.mg._MapGenerator__planets[i].coords.calc_distance(
                self.mg._MapGenerator__planets[i + 1].coords) - temp < (temp / 100), True, "wrong distance to planets")

    # def test_check_same_count_of_planets_in_players_area(self):
    #    players_ids=[1,2,3,4,5,6,7,8]
    #    a=self.mg.run(players_ids)


if __name__ == '__main__':
    unittest.main()
