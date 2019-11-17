import unittest
from utils.player import Player

ADDRESS_DEFAULT = (1, 2, 3)
PLAYER_ID_DEFAULT = 23


class TestClassPLayer(unittest.TestCase):

    def setUp(self):
        self.p = Player(ADDRESS_DEFAULT, PLAYER_ID_DEFAULT)

    def test_constructor(self):
        self.assertEqual(self.p.id, PLAYER_ID_DEFAULT, 'incorrect id init')
        self.assertEqual(self.p.address, ADDRESS_DEFAULT, 'incorrect address init')

    def test_info(self):
        self.assertEqual({'id': self.p.id, 'name': self.p.name,
                          'ready': self.p.ready}, self.p.info(),
                         'incorrect dictionary format')


if __name__ == '__main__':
    unittest.main()
