import json
import select
import socket
import struct
from typing import Callable, Dict, List, Union

from events import ConnectEvent, EventNames, PlayerEvent, PriorityQueueEvent, SimpleEvent
from map_generator import MapGenerator
from planet import Planet
from player import Player
from utils import ID_GENERATOR, MaxPriorityQueue, Singleton, StoppedThread

MAX_CLIENT_COUNT = 8


def create_tcp_server(server_address: Union[tuple, str, bytes], backlog: int, blocking: bool = False) -> socket.socket:
    server_socket = socket.socket(type=socket.SOCK_STREAM)
    server_socket.setblocking(blocking)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(server_address)
    server_socket.listen(backlog)
    return server_socket


def request(string: str) -> bytes:
    return struct.pack('i', len(string)) + string.encode('utf-8')


class Server(metaclass=Singleton):
    RECEIVER_TIMEOUT = 10  # seconds

    def __init__(self, port: int = 10800, max_client_count: int = MAX_CLIENT_COUNT):
        self.server = create_tcp_server(('127.0.0.1', port), max_client_count)
        self.started = True
        self.clients: List[socket.socket] = []
        self.__max_clients_count = max_client_count
        self.players: Dict[socket.socket, Player] = {}
        self.next_player_id = 0
        self.readiness = False
        self.game_started = False

        self.__handler_queue = MaxPriorityQueue()
        self.__sender_queue = MaxPriorityQueue()
        self.__threads: List[StoppedThread] = []

        # self.__map = None

    def __start_thread(self, name, callback, args=None):
        t = StoppedThread(name=name, target=callback, args=args)
        self.__threads.append(t)
        # t.daemon = True
        t.start()

    def start(self):
        self.__start_thread(name='receiver', callback=self.receiver, args=())
        self.__start_thread(name='handler', callback=self.handler, args=())
        self.__start_thread(name='sender', callback=self.sender, args=())

    def stop(self):
        for thread in self.__threads:
            thread.stop()
            thread.join()

    def __wait_for_clients(self, server_sock):
        if not self.game_started and not self.readiness and len(self.clients) < self.__max_clients_count:
            client, address = server_sock.accept()
            print(address)
            client.setblocking(0)
            self.clients.append(client)
            self.next_player_id += 1

            player = Player(address=address, id_=self.next_player_id)
            self.players[client] = player
            event = PriorityQueueEvent(ConnectEvent(player=player))
            self.__sender_queue.insert(**event.get_queue_payload())

    def __remove_client(self, client_sock):
        self.clients.remove(client_sock)
        del self.players[client_sock]
        client_sock.close()

    def __wait_for_client_data(self, client_sock):
        data_size = client_sock.recv(struct.calcsize('i'))

        if data_size:
            data_size = struct.unpack('i', data_size)[0]
            event = client_sock.recv(data_size)

            if event:
                event = json.loads(event)
                player = self.players[client_sock]
                event = PriorityQueueEvent(PlayerEvent(raw_event=event, sender=player))
                self.__handler_queue.insert(**event.get_queue_payload())
            else:
                self.__remove_client(client_sock)
        else:
            self.__remove_client(client_sock)

    def receiver(self, is_alive: Callable):
        while is_alive():
            readable, *_ = select.select([self.server, *self.clients], [], [], self.RECEIVER_TIMEOUT)

            for sock in readable:
                if sock is self.server:
                    self.__wait_for_clients(sock)
                else:
                    self.__wait_for_client_data(sock)

    def sender(self, is_alive: Callable):
        while is_alive():
            if not self.__sender_queue.empty():
                data = self.__sender_queue.remove()

                for player in self.clients:
                    player.send(request(json.dumps(data)))

    def __is_game_over(self):
        active_players = []

        for player in self.players.values():
            if len(player.object_ids) > 0:
                for planet in Planet.cache.values():
                    if planet.owner == player.id:
                        active_players.append(player.id)
                        break
            if len(active_players) >= 2:
                break
        else:
            event = PriorityQueueEvent(SimpleEvent(
                name=EventNames.GAME_OVER,
                winner=active_players[0]
            ), 1)
            self.__sender_queue.insert(**event.get_queue_payload())

            self.readiness = False
            self.game_started = False

            self.players = {}
            self.clients = []

    # def handler(self, client, client_event):
    def handler(self, is_alive: Callable):
        while is_alive():
            if not self.__handler_queue.empty():
                event, player = self.__handler_queue.remove()

                if event['name'] == EventNames.READY:
                    player.ready = event['ready']

                    event = PriorityQueueEvent(SimpleEvent(
                        name=EventNames.READY,
                        player=player.id,
                        ready=event['ready']
                    ), 1)
                    self.__sender_queue.insert(**event.get_queue_payload())

                    all_ready = all(player.is_ready() for player in self.players.values())

                    if all_ready and len(self.players) > 1:
                        gen = MapGenerator()
                        map_ = gen.run([player.id for player in self.players.values()])
                        gen.display()
                        game_map = [planet.get_dict() for planet in map_]

                        self.readiness = True

                        event = PriorityQueueEvent(SimpleEvent(
                            name=EventNames.MAP_INIT,
                            map=game_map
                        ), 1)
                        self.__sender_queue.insert(**event.get_queue_payload())

                elif event['name'] == EventNames.RENDERED:
                    player.rendered = True

                    if all(player.is_rendered() for player in self.players.values()):
                        # TODO game start event
                        event = PriorityQueueEvent(SimpleEvent(
                            name=EventNames.GAME_STARTED
                        ), 1)
                        self.__sender_queue.insert(**event.get_queue_payload())
                        self.game_started = True

                if self.game_started:
                    if event['name'] == EventNames.MOVE:
                        if int(event['unit_id']) in player.object_ids:
                            event = PriorityQueueEvent(SimpleEvent(
                                **event
                            ), 0)
                            self.__sender_queue.insert(**event.get_queue_payload())

                    elif event['name'] == EventNames.SELECT:
                        planet_ids = event['from']
                        percentage = event['percentage']

                        punits = {}

                        for planet_id in planet_ids:
                            planet_id = int(planet_id)

                            if Planet.cache[planet_id].owner == player.id:
                                new_ships_count = round(Planet.cache[planet_id].units_count * int(percentage) / 100.0)
                                Planet.cache[planet_id].units_count -= new_ships_count
                                punits[planet_id] = [next(ID_GENERATOR) for _ in range(new_ships_count)]
                                player.object_ids += punits[planet_id]

                        event = PriorityQueueEvent(SimpleEvent(
                            name=EventNames.SELECT,
                            selected=punits
                        ), 1)
                        self.__sender_queue.insert(**event.get_queue_payload())

                    elif event['name'] == EventNames.ADD_HP:
                        planet_id = int(event['planet_id'])
                        hp_count = int(event['hp_count'])

                        planet = Planet.cache[planet_id]

                        if planet.owner == player.id:
                            planet.units_count += hp_count
                            event = PriorityQueueEvent(SimpleEvent(
                                **event
                            ), 1)
                            self.__sender_queue.insert(**event.get_queue_payload())

                    elif event['name'] == EventNames.DAMAGE:
                        planet_id = int(event['planet_id'])
                        unit_id = int(event['unit_id'])
                        hp_count = int(event.get('hp_count', 1))

                        planet = Planet.cache[planet_id]

                        if unit_id in player.object_ids:
                            if planet.owner == player.id:
                                planet.units_count += hp_count
                            else:
                                planet.units_count -= hp_count
                                if planet.units_count < 0:
                                    planet.owner = player.id
                                    planet.units_count = abs(planet.units_count)

                            player.object_ids.remove(unit_id)

                            event = PriorityQueueEvent(SimpleEvent(
                                name=EventNames.DAMAGE,
                                planet_change={
                                    'id': planet_id,
                                    'units_count': planet.units_count,
                                    'owner': planet.owner,
                                },
                                unit_id=unit_id
                            ), 1)
                            self.__sender_queue.insert(**event.get_queue_payload())

                        # check game over

                        self.__is_game_over()
