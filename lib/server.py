"""
Модуль сервера
"""

import select
import socket
import struct
from typing import Dict, List, Union

from lib.map_generator import MapGenerator
from lib.planet import Planet
from utils import Config, EventPriorityQueue, ID_GENERATOR, StoppedThread
from utils.events import ClientEvent, ClientEventName, GameEvent, ServerEvent, ServerEventName
from utils.player import Player

CFG = Config()


def create_tcp_server(server_address: Union[tuple, str, bytes], backlog: int, blocking: bool = False) -> socket.socket:
    server_socket = socket.socket(type=socket.SOCK_STREAM)
    server_socket.setblocking(blocking)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(server_address)
    server_socket.listen(backlog)
    return server_socket


class Server(object):
    RECEIVER_TIMEOUT = int(CFG['Server']['select_timeout'])
    HOST = CFG['Server']['ip']
    PORT = int(CFG['Server']['port'])
    MAX_CLIENT_COUNT = int(CFG['Server']['max_client_count'])

    def __init__(self, port: int = PORT, max_client_count: int = MAX_CLIENT_COUNT):
        self.server = create_tcp_server((self.HOST, port), max_client_count)
        self.started = True
        # список клиентских сокетов
        self.clients: List[socket.socket] = []
        self.__max_clients_count = max_client_count
        # словарь с информацией про игрока (ключ - сокет, значение - обьект игрока)
        self.players: Dict[socket.socket, Player] = {}
        self.next_player_id = 0
        self.readiness = False
        self.game_started = False

        # очередь клиентских событий
        self.__handler_queue = EventPriorityQueue()
        # очередь событий на отправку клиентам
        self.__sender_queue = EventPriorityQueue()

        # потоки для функций приема событий, их обработки и отправки
        self.__threads: List[StoppedThread] = []

    def __start_thread(self, name, callback, args=None):
        """ запуск потока """

        t = StoppedThread(name=name, target=callback, args=args)
        self.__threads.append(t)
        t.start()

    def start(self):
        """ запуск всех потоков сервера """

        self.__start_thread(name='receiver', callback=self.__receiver, args=())
        self.__start_thread(name='handler', callback=self.__handler, args=())
        self.__start_thread(name='sender', callback=self.__sender, args=())

    def stop(self):
        """ остановка всех потоков сервера """

        for thread in self.__threads:
            thread.stop()
            thread.join()

    def __wait_for_client(self, server_sock):
        """ ожидание подключения клиента """

        if not self.game_started and not self.readiness and len(self.clients) < self.__max_clients_count:
            client, address = server_sock.accept()
            client.setblocking(0)

            self.next_player_id += 1

            player = Player(address, self.next_player_id)

            self.__notify(ServerEventName.PLAYER_INIT, {
                'players': [pl.info() for pl in self.players.values()],
                "id": player.id
            }, receivers=client)

            self.__notify(ServerEventName.CONNECT, {
                'player': player.info()
            }, receivers=[cl for cl in self.clients])

            self.clients.append(client)
            self.players[client] = player

    def __remove_client(self, client_sock):
        """ удаляет клиентов со списка и закрывает соединение """

        player = self.players[client_sock]

        self.clients.remove(client_sock)
        del self.players[client_sock]
        client_sock.close()

        self.__notify(ServerEventName.DISCONNECT, {
            'player': player.info(),
        })

    def __wait_for_client_data(self, client_sock):
        """
        получает данные клиента,
        создает экземпляр события,
        добавляет в очередь
        """
        try:
            client_sock.setblocking(1)
            data_size = client_sock.recv(struct.calcsize('i'))

            if data_size:
                data_size = struct.unpack('i', data_size)[0]
                event = client_sock.recv(data_size)

                if event:
                    player = self.players[client_sock]
                    event = ClientEvent(player, event)
                    self.__handler_queue.insert(event)
                else:
                    print('no evnt')
                    self.__remove_client(client_sock)
            else:
                print('no dat size')
                self.__remove_client(client_sock)
        except ConnectionResetError:
            print('ConnectionResetError')
            self.__remove_client(client_sock)

        client_sock.setblocking(0)

    def __receiver(self):
        """ слушает изменения в сокетах """

        readable, *_ = select.select([self.server, *self.clients], [], [], self.RECEIVER_TIMEOUT)

        for sock in readable:
            if sock is self.server:
                self.__wait_for_client(sock)
            else:
                self.__wait_for_client_data(sock)

    def __sender(self):
        """ рассылает данные с очереди """

        if not self.__sender_queue.empty():
            event = self.__sender_queue.remove()

            receivers = event.payload.pop("receivers", self.clients)

            for client in receivers:
                client.send(event.request())

    def __notify(self, name: str, args: dict, receivers=None):
        """ создает и добавляет событие в очередь на отправку """

        if receivers is not None:
            if not isinstance(receivers, list):
                receivers = [receivers, ]
            args['receivers'] = receivers

        self.__sender_queue.insert(ServerEvent(name, args))

    def __on_event_ready(self, event: GameEvent, player: Player):
        """ обработчик события: ready """

        player.ready = event.payload['ready']

        self.__notify(event.name, {
            'player': player.id,
            'ready': event.payload['ready'],
        })

        all_ready = all(player.ready for player in self.players.values())

        if all_ready and len(self.players) > 1:
            gen = MapGenerator()
            map_ = gen.run([player.id for player in self.players.values()])
            game_map = [planet.get_dict() for planet in map_]

            self.readiness = True

            self.__notify(ServerEventName.MAP_INIT, {
                'map': game_map,
            })

    def __on_event_rendered(self, player: Player):
        """ обработчик события: rendered """

        player.rendered = True

        if all(player.rendered for player in self.players.values()):
            self.__notify(ServerEventName.GAME_STARTED, {})
            self.game_started = True

    def __on_event_move(self, event: GameEvent, player: Player):
        """ обработчик события: move """
        unit_id = event.payload['unit_id']
        x = event.payload['x']
        y = event.payload['y']

        if int(unit_id) in player.object_ids:
            self.__notify(event.name, {
                'unit_id': unit_id,
                'x': x,
                'y': y
            })

    def __on_event_select(self, event: GameEvent, player: Player):
        """ обработчик события: select """

        planet_ids = event.payload['from']
        percentage = event.payload['percentage']

        punits = {}

        for planet_id in planet_ids:
            planet_id = int(planet_id)

            if Planet.cache[planet_id].owner == player.id:
                new_ships_count = round(Planet.cache[planet_id].units_count * int(percentage) / 100.0)
                Planet.cache[planet_id].units_count -= new_ships_count
                punits[planet_id] = [next(ID_GENERATOR) for _ in range(new_ships_count)]
                player.object_ids += punits[planet_id]

        self.__notify(event.name, {
            'selected': punits,
        })

    def __on_event_add_hp(self, event: GameEvent, player: Player):
        """ обработчик события: add_hp """

        planet_id = int(event.payload['planet_id'])
        hp_count = int(event.payload['hp_count'])

        planet = Planet.cache[planet_id]

        if planet.owner == player.id:
            planet.units_count += hp_count
            self.__notify(event.name, {
                'planet_id': planet_id,
                'hp_count': hp_count
            })

    def __check_game_over(self):
        """ проверяет окончание игры """

        active_players = []

        for player in self.players.values():
            for planet in Planet.cache.values():
                if planet.owner == player.id:
                    active_players.append(player.id)
                    break
                
            if len(active_players) >= 2:
                break
        else:
            print('over')
            self.__notify(ServerEventName.GAME_OVER, {
                'winner': active_players[0],
            })

            self.readiness = False
            self.game_started = False

            self.players = {}
            self.clients = []

    def __on_event_damage(self, event: GameEvent, player: Player):
        """ обработчик события: damage """

        planet_id = int(event.payload['planet_id'])
        unit_id = int(event.payload['unit_id'])
        hp_count = int(event.payload.get('hp_count', 1))

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

            self.__notify(event.name, {
                'planet_change': {
                    'id': planet_id,
                    'units_count': planet.units_count,
                    'owner': planet.owner,
                },
                'unit_id': unit_id,
            })

        self.__check_game_over()

    def __handler(self):
        """ обработчик событий """

        if not self.__handler_queue.empty():
            event = self.__handler_queue.remove()
            player = event.payload['player']

            if event.name == ClientEventName.READY:
                self.__on_event_ready(event, player)
            elif event.name == ClientEventName.RENDERED:
                self.__on_event_rendered(player)
            elif self.game_started:
                if event.name == ClientEventName.MOVE:
                    self.__on_event_move(event, player)
                elif event.name == ClientEventName.SELECT:
                    self.__on_event_select(event, player)
                elif event.name == ClientEventName.ADD_HP:
                    self.__on_event_add_hp(event, player)
                elif event.name == ClientEventName.DAMAGE:
                    self.__on_event_damage(event, player)
