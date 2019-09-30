import socket
import select
import struct
import json

from planet import Planet, PlanetType
from utils import Coords


MAX_CLIENT_COUNT = 6


def create_tcp_server(server_address, backlog, blocking=False):
    server_socket = socket.socket(type=socket.SOCK_STREAM)
    server_socket.setblocking(blocking)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(server_address)
    server_socket.listen(backlog)
    return server_socket


def request(string):
    return struct.pack('i', len(string)) + string.encode('utf-8')


class Game(object):
    def __init__(self, port, clients_count):
        self.server = create_tcp_server(('0.0.0.0', port), clients_count)
        self.started = True
        self.clients = []
        self.clients_count = clients_count
        self.players = {}
        self.number = 0
        self.is_game = False

    def start(self):
        while True:
            readable, *_ = select.select([self.server, *self.clients], [], [], 10)

            for sock in readable:
                if sock is self.server:
                    if not self.is_game:
                        client, address = sock.accept()
                        client.setblocking(0)
                        self.clients.append(client)
                        self.number += 1
                        self.players[client] = {
                            'id': self.number,
                            'address': address,
                            'ready': False,
                            'rendered': False,
                            'name': '',
                        }
                else:
                    bytes4 = sock.recv(struct.calcsize('i'))

                    if bytes4:
                        size = struct.unpack('i', bytes4)[0]
                        event = sock.recv(size)

                        if event:
                            self.handle(self.players[sock], json.loads(event))
                        else:
                            # remove ?
                            self.clients.remove(sock)
                            sock.close()
                    else:
                        # remove ?
                        self.clients.remove(sock)
                        sock.close()

    def notify(self, event):
        for client in self.clients:
            client.send(request(json.dumps(event)))

    def all_clients(self, field):
        return all(player[field] for player in self.players.values())

    def handle(self, client, client_event):
        event_name = client_event['name']

        if event_name == 'ready':
            client['ready'] = client_event['ready']

            self.notify({
                'name': 'ready',
                'player': client['id'],
                'ready': client['ready'],
            })

            ready = self.all_clients('ready')

            if ready:
                # TODO: generate map
                map = None

                self.notify({
                    'name': 'mapinit',
                    'map': map,
                })
        elif event_name == 'rendered':
            client['rendered'] = True

            rendered = self.all_clients('rendered')

            if rendered:
                self.is_game = True
                self.notify({
                    'name': 'game-started'
                })

        if not self.is_game:
            return

        planets = [
            Planet(Coords(1, 2), PlanetType.MEDIUM, 1),
            Planet(Coords(3, 3), PlanetType.BIG, None),
            Planet(Coords(2, 1), PlanetType.MEDIUM, 2),
            Planet(Coords(2, 2), PlanetType.BIG, None),
        ]

        if event_name == 'select':
            # TODO: select

            client_id = client_event['client_id']
            planets_ids = client_event['from']
            percentage = client_event['percentage']

            self.notify({
                'name': 'change',
            })
        elif event_name == 'move':
            # TODO: move

            client_id = client_event['client_id']
            unit_id = client_event['unit_id']
            x = client_event['x']
            y = client_event['y']

            self.notify({
                'name': 'change',
            })
        elif event_name == 'damage':
            # TODO: damage

            client_id = client_event['client_id']
            planet_id = client_event['to']

            self.notify({
                'name': 'change',
            })

            if self.is_gameover():
                self.notify({
                    'name': 'game-over',
                })
                self.is_game = False

    def is_gameover(self):
        # TODO: check game-over
        return False
