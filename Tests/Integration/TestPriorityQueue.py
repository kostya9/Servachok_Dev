from utils.utils import PriorityQueueEvent, EventPriorityQueue
from threading import Thread
from multiprocessing import Queue
from typing import List


class ProducerThread(Thread):
    def __init__(self, event_queue: 'PriorityQueueEvent', message_queue: Queue, events: List[EventPriorityQueue]):
        Thread.__init__(self)
        self.event_queue_ref = event_queue
        self.message_queue_ref = message_queue
        self.event_list = events

    def run(self):
        for event in self.events:
            pass

