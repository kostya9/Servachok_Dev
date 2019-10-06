import json
import select
import socket
import struct

from map_generator import MapGenerator
from planet import Planet
from utils import Singleton, MaxPriorityQueue, id_generator, StoppedThread

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


class Server(metaclass=Singleton):
    def __init__(self, port=10800, max_client_count=8):
        self.server = create_tcp_server(('127.0.0.1', port), max_client_count)
        self.started = True
        self.clients = []
        self.__max_clients_count = max_client_count
        self.players = {}
        self.next_player_id = 0
        self.readiness = False
        self.game_started = False

        self.__handler_queue = MaxPriorityQueue()
        self.__sender_queue = MaxPriorityQueue()
        self.__threads = []

        # self.__map = None

    def __start_thread(self, name, callback, args=None):
        self.__threads.append(StoppedThread(name=name, target=callback, args=args))
        # self._threads[-1].daemon = True
        self.__threads[-1].start()

    def start(self):
        self.__start_thread(name="receiver", callback=self.receiver, args=())
        self.__start_thread(name="handler", callback=self.handle, args=())
        self.__start_thread(name='sender', callback=self.sender, args=())

    def stop(self):
        for thread in self.__threads:
            thread.stop()
            thread.join()

    def receiver(self, is_alive):
        while is_alive():
            readable, *_ = select.select([self.server, *self.clients], [], [], 10)

            for sock in readable:
                if sock is self.server:
                    if not self.game_started and not self.readiness and len(self.clients) < self.__max_clients_count:
                        client, address = sock.accept()
                        print(address)
                        client.setblocking(0)
                        self.clients.append(client)
                        self.next_player_id += 1
                        player = {
                            'id': self.next_player_id,
                            'address': address,
                            'ready': False,
                            'rendered': False,
                            'object_ids': [],
                            'name': 'client {}'.format(self.next_player_id),
                        }

                        self.players[client] = player

                        self.__sender_queue.insert({
                            'name': 'connect',
                            'player': {
                                'id': player['id'],
                                'name': player['name'],
                                'ready': player['ready'],
                            },
                        }, 1)
                else:
                    data_size = sock.recv(struct.calcsize('i'))

                    if data_size:
                        data_size = struct.unpack('i', data_size)[0]
                        event = sock.recv(data_size)

                        if event:
                            event = json.loads(event)

                            if event['name'] == "move":
                                self.__handler_queue.insert((event, sock), 0)
                            else:
                                self.__handler_queue.insert((event, sock), 1)
                        else:
                            self.clients.remove(sock)
                            del self.players[sock]
                            sock.close()
                    else:
                        self.clients.remove(sock)
                        del self.players[sock]
                        sock.close()

    def sender(self, is_alive):
        while is_alive():
            if not self.__sender_queue.empty():
                data = self.__sender_queue.remove()

                for player in self.clients:
                    player.send(request(json.dumps(data)))

    def all_clients(self, field):
        return all(player[field] for player in self.players.values())

    # def handle(self, client, client_event):
    def handle(self, is_alive):
        while is_alive():
            if not self.__handler_queue.empty():
                event, client = self.__handler_queue.remove()

                if event['name'] == "ready":
                    self.players[client]['ready'] = event['ready']

                    message = {
                        'name': 'ready',
                        'player': self.players[client]['id'],
                        'ready': event['ready']
                    }

                    self.__sender_queue.insert(message, 1)

                    ready = self.all_clients('ready')

                    if ready and len(self.players) > 1:
                        gen = MapGenerator()
                        map = gen.run([player['id'] for player in self.players.values()])
                        gen.display()
                        game_map = [planet.get_dict() for planet in map]

                        self.readiness = True

                        message = {
                            'name': 'mapinit',
                            'map': game_map,
                        }

                        self.__sender_queue.insert(message, 1)

                elif event['name'] == 'rendered':
                    self.players[client]['rendered'] = True

                    if self.all_clients('rendered'):
                        # TODO game start event
                        self.__sender_queue.insert({'name': 'game_started'}, 1)
                        self.game_started = True

                if self.game_started:
                    if event['name'] == 'move':
                        if int(event['unit_id']) in self.players[client]['object_ids']:
                            self.__sender_queue.insert(event, 0)

                    elif event['name'] == 'select':
                        planets_ids = event['from']
                        percentage = event['percentage']

                        punits = {}

                        for planet_id in planets_ids:
                            planet_id = int(planet_id)

                            if Planet.cache[planet_id].owner == self.players[client]['id']:
                                new_ships_count = round(Planet.cache[planet_id].units_count * int(percentage) / 100.0)
                                Planet.cache[planet_id].units_count -= new_ships_count
                                punits[planet_id] = [next(id_generator) for _ in range(new_ships_count)]
                                self.players[client]['object_ids'] += punits[planet_id]

                        self.__sender_queue.insert({
                            'name': 'select',
                            'selected': punits
                        }, 1)

                    elif event['name'] == 'add_hp':
                        planet_id = int(event['planet_id'])
                        hp_count = int(event['hp_count'])

                        planet = Planet.cache[planet_id]

                        if planet.owner == self.players[client]['id']:
                            planet.units_count += hp_count
                            self.__sender_queue.insert(event, 1)

                    elif event['name'] == 'damage':
                        planet_id = int(event['planet_id'])
                        unit_id = int(event['unit_id'])
                        hp_count = int(event.get('hp_count', 1))

                        planet = Planet.cache[planet_id]

                        if unit_id in self.players[client]['object_ids']:
                            if planet.owner == self.players[client]['id']:
                                planet.units_count += hp_count
                            else:
                                planet.units_count -= hp_count
                                if planet.units_count < 0:
                                    planet.owner = self.players[client]['id']
                                    planet.units_count = abs(planet.units_count)

                            self.players[client]['object_ids'].remove(unit_id)

                            self.__sender_queue.insert({
                                'name': 'damage',
                                'planet_change': {'id': planet_id,
                                                  'units_count': planet.units_count,
                                                  'owner': planet.owner},
                                'unit_id': unit_id,
                            }, 1)

                        # check game over

                        active_players = []

                        for player in self.players.values():
                            if len(player["object_ids"]):
                                for planet in Planet.cache.values():
                                    if planet.owner == player['id']:
                                        active_players.append(player['id'])
                                        break
                            if len(active_players) >= 2:
                                break
                        else:
                            self.__sender_queue.insert({
                                'name': 'gameover',
                                'winner': active_players[0]
                            }, 1)

                            self.readiness = False
                            self.game_started = False

                            self.players = {}
                            self.clients = []
