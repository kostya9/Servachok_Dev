import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib import Server

if __name__ == '__main__':
    server = Server()
    server.start()
