from abc import ABC, abstractmethod

from player import Player


class EventNames(object):
    """ Enum """
    CONNECT = 'connect'
    READY = 'ready'
    MAP_INIT = 'mapinit'
    RENDERED = 'rendered'
    GAME_STARTED = 'game_started'
    MOVE = 'move'
    SELECT = 'select'
    ADD_HP = 'add_hp'
    DAMAGE = 'damage'
    GAME_OVER = 'gameover'


class Event(ABC):
    @abstractmethod
    def get_queue_payload(self) -> dict:
        pass


# TODO create more classes for specific Events instead of this stub-class
class SimpleEvent(Event):
    def __init__(self, **kwargs):
        self.__kwargs = kwargs

    def get_queue_payload(self) -> dict:
        return self.__kwargs


class PlayerEvent(Event):
    def __init__(self, raw_event: dict, sender: Player):
        self.name = raw_event['name']
        self.raw_event = raw_event
        self.player = sender

    def get_queue_payload(self) -> tuple:
        return self.raw_event, self.player


class ConnectEvent(Event):
    def __init__(self, player: Player):
        self.name = EventNames.CONNECT
        self.player = player

    def get_queue_payload(self) -> dict:
        return {
            'name': self.name,
            'player': self.player.get_sender_event_dict(),
        }


class PriorityQueueEvent(Event):
    def __init__(self, event: Event, priority: int = None):
        self.event = event
        if priority is None:
            priority = self.__priority_factory()
        self.priority = priority

    def __priority_factory(self):
        if isinstance(self.event, PlayerEvent):
            if self.event.name == EventNames.MOVE:
                return 0
            else:
                return 1
        # TODO create priority rules for classes for specific Events
        return 0

    def get_queue_payload(self) -> dict:
        return {
            'item': super().get_queue_payload(),
            'priority': self.priority,
        }
