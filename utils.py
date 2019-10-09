from queue import PriorityQueue
from threading import Event, Lock, Thread
from typing import Any


def __generate_id() -> int:
    id_ = 1
    while True:
        yield id_
        id_ += 1


ID_GENERATOR = __generate_id()


class Coords(object):
    def __init__(self, x: int = 0, y: int = 0):
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


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class MaxPriorityItem(object):
    def __init__(self, item: Any, priority: int):
        self.item = item
        self.priority = priority

    def __gt__(self, other):
        return self.priority < other.priority

    def __lt__(self, other):
        return self.priority > other.priority


class MaxPriorityQueue(object):
    def __init__(self):
        self.__queue = PriorityQueue()
        self.__mutex = Lock()

    def insert(self, item: Any, priority: int = 0):
        with self.__mutex:
            self.__queue.put(MaxPriorityItem(item, priority))

    def remove(self) -> Any:
        with self.__mutex:
            mp_item = self.__queue.get()
        return mp_item.item if mp_item else None

    def empty(self) -> bool:
        with self.__mutex:
            return self.__queue.empty()


class StoppedThread(Thread):
    def __init__(self, target=None, name=None, args=(), **kwargs):
        self._target = target
        self._args = args
        self._kwargs = kwargs
        super().__init__(target=target, name=name, args=args, kwargs=kwargs)
        self.stopper = Event()

    def is_alive(self) -> bool:
        return not self.stopper.is_set()

    def run(self):
        self._target(self.is_alive, *self._args, **self._kwargs)

    def start(self):
        super().start()
        print('{} started'.format(self.name))

    def stop(self):
        print('{} stopping...'.format(self.name))
        self.stopper.set()
        print('{} stopped'.format(self.name))
