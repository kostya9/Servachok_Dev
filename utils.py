import math
from queue import PriorityQueue
from threading import Thread, Event, Lock


def generate_id():
    _id = 1
    while True:
        yield _id
        _id += 1


id_generator = generate_id()


class Coords(object):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __str__(self):
        return "({}, {})".format(self.x, self.y)

    def get_dict(self):
        res_dict = {'x': self.x, 'y': self.y}
        return res_dict

    def radius_calculation(self):
        return math.pow(math.pow(self.x, 2) + math.pow(self.y, 2), 1 / 2)

    def get_coord(self):
        return self.x, self.y

    def calc_distance(self, point):
        return math.pow(math.pow(self.x - point.x, 2) + math.pow(self.y - point.y, 2), 1 / 2)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class MaxPriorityItem(object):
    def __init__(self, item, priority):
        self.item = item
        self.priority = priority

    def __lt__(self, other):
        return self.priority > other.priority


class MaxPriorityQueue(object):
    def __init__(self):
        self.__queue = PriorityQueue()
        self.__mutex = Lock()

    def insert(self, item, priority=0):
        self.__mutex.acquire()
        self.__queue.put(MaxPriorityItem(item, priority))
        self.__mutex.release()

    def remove(self):
        self.__mutex.acquire()
        item = self.__queue.get()
        self.__mutex.release()
        return item.item if item else None

    def empty(self):
        self.__mutex.acquire()
        is_empty = self.__queue.empty()
        self.__mutex.release()
        return is_empty


class StoppedThread(Thread):
    def __init__(self, target=None, name=None, args=None, **kwargs):
        super().__init__(target=target, name=name, args=args, kwargs=kwargs)
        self.stopper = Event()

    def is_alive(self):
        return not self.stopper.is_set()

    def run(self):
        self._target(self.is_alive, *self._args, **self._kwargs)

    def start(self):
        super().start()
        print(self.name, "started")

    def stop(self):
        print(self.name, "stopping...")
        self.stopper.set()
        print(self.name, "stopped")
