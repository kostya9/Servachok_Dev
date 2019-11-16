from queue import PriorityQueue
from threading import Event, Lock, Thread

from utils.events import GameEvent, EventName


def __generate_id() -> int:
    """ генератор id """

    id_ = 1
    while True:
        yield id_
        id_ += 1


ID_GENERATOR = __generate_id()


class PriorityQueueEvent(object):
    """ элемент очереди событий по максимальному приоритету """

    def __init__(self, event: GameEvent, priority: int):
        self.event = event

        if priority is None:
            self.priority = self.__priority_factory()
        else:
            self.priority = priority

    def __priority_factory(self) -> int:
        if self.event.name == EventName.MOVE:
            return 0
        return 1

    def __gt__(self, other: 'PriorityQueueEvent') -> bool:
        return self.priority < other.priority

    def __lt__(self, other: 'PriorityQueueEvent') -> bool:
        return self.priority > other.priority


class EventPriorityQueue(object):
    """ очередь событий по максимальному приоритету """

    def __init__(self):
        self.__queue = PriorityQueue()
        self.__mutex = Lock()

    def insert(self, event: GameEvent, priority: int = None):
        with self.__mutex:
            item = PriorityQueueEvent(event, priority)
            self.__queue.put(item)

    def remove(self) -> GameEvent:
        with self.__mutex:
            item = self.__queue.get()
        return item.event if item else None

    def empty(self) -> bool:
        with self.__mutex:
            return self.__queue.empty()


class Coords(object):
    """ координата точки """

    def __init__(self, x: float = 0, y: float = 0):
        self.x = x
        self.y = y

    def __str__(self):
        return '({}, {})'.format(self.x, self.y)

    def get_dict(self) -> dict:
        return vars(self)

    def radius_calculation(self) -> float:
        return (self.x ** 2 + self.y ** 2) ** 0.5

    def get_coord(self) -> tuple:
        return self.x, self.y

    def calc_distance(self, point: 'Coords') -> float:
        return ((self.x - point.x) ** 2 + (self.y - point.y) ** 2) ** 0.5


class StoppedThread(Thread):
    """ обертка (wrapper) для ручной остановки потоков """

    def __init__(self, target=None, name=None, args=(), **kwargs):
        self._target = target
        self._args = args
        self._kwargs = kwargs
        super().__init__(target=target, name=name, args=args, kwargs=kwargs)
        self.stopper = Event()

    def is_alive(self) -> bool:
        return not self.stopper.is_set()

    def run(self):
        while self.is_alive():
            self._target()

    def start(self):
        super().start()
        print('{} started'.format(self.name))

    def stop(self):
        print('{} stopping...'.format(self.name))
        self.stopper.set()
        print('{} stopped'.format(self.name))
