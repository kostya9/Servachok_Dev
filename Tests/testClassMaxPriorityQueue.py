from utils import MaxPriorityQueue, MaxPriorityItem
import unittest
import math
from queue import PriorityQueue
from threading import Thread, Event, Lock


class Test_case_MaxPriorityQueue(unittest.TestCase):

    def setUp(self):
        self.item1=10
        self.item2=20
        self.item3=30
        self.priority1=1
        self.priority2=2
        self.priority3=3
        self.c=MaxPriorityQueue()

    def test_right_init(self):
        self.assertEqual(type(self.c._MaxPriorityQueue__queue),type(PriorityQueue()),"wrong priority queue init")

    def test_queue_is_queue(self):
        self.c.insert(self.item1)
        self.c.insert(self.item2)
        self.c.insert(self.item3)
        self.assertEqual(self.c.remove(),self.item1,"wrong first item")
        self.assertEqual(self.c.remove(),self.item2,"wrong second item")
        self.assertEqual(self.c.remove(),self.item3,"wrong third item")

    def test_queue_is_sorted_max_to_less_priority(self):
        self.c.insert(self.item2,self.priority2)
        self.c.insert(self.item1,self.priority1)
        self.c.insert(self.item3,self.priority3)
        self.assertEqual(self.c.remove(),self.item3,"wrong first item")
        self.assertEqual(self.c.remove(),self.item2,"wrong second item")
        self.assertEqual(self.c.remove(),self.item1,"wrong third item")

    def test_queue_empty(self):
        self.c.insert(self.item2,self.priority2)
        self.c.insert(self.item1,self.priority1)
        self.c.insert(self.item3,self.priority3)
        self.assertEqual(self.c.empty(),False,"wrong empty queue (3 elems)")
        self.c.remove()
        self.c.remove()
        self.assertEqual(self.c.empty(),False,"wrong empty queue (1 elem)")
        self.c.remove()
        self.assertEqual(self.c.empty(),True,"wrong empty queue (0 elems)")


if __name__ == '__main__':
    unittest.main()
