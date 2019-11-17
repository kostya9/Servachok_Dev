import unittest
from lib.server import *

ADDRESS_DEFAULT = (1, 2, 3)
PLAYER_ID_DEFAULT = 23

SERVER_ADDRESS = ('', 9080)
BACKLOG = 10


class TestFunctions(unittest.TestCase):

    def test_create_tcp_server(self):
        tcp_server = create_tcp_server(SERVER_ADDRESS, BACKLOG)
        self.assertEqual(str(type(tcp_server)), "<class 'socket.socket'>", 'incorrect return type')


if __name__ == '__main__':
    unittest.main()
