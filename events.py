import json
import struct

from player import Player


class EventName(object):
    READY = 'ready'
    RENDERED = 'rendered'
    MOVE = 'move'
    SELECT = 'select'
    ADD_HP = 'add_hp'
    DAMAGE = 'damage'


class ClientEventName(EventName):
    pass


class ServerEventName(EventName):
    CONNECT = 'connect'
    MAP_INIT = 'mapinit'
    GAME_STARTED = 'game_started'
    GAME_OVER = 'gameover'


class GameEvent(object):
    def __init__(self, name: EventName, kwargs: dict):
        self.name = name
        self.payload = kwargs

    def request(self) -> bytes:
        raise NotImplementedError


class ClientEvent(GameEvent):
    def __init__(self, player: Player, string: str):
        o = json.loads(string)
        GameEvent.__init__(self, o.pop('name'), {**o, 'player': player})

    def request(self) -> bytes:
        pass


class ServerEvent(GameEvent):
    def request(self) -> bytes:
        string = json.dumps({'name': self.name, **self.payload})
        return struct.pack('i', len(string)) + string.encode('utf-8')
