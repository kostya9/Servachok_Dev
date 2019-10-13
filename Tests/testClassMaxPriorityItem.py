from utils import MaxPriorityItem
import unittest
import math



class Test_case_MaxPriorityItem(unittest.TestCase):

    def setUp(self):
        self.item=0
        self.priority=10
        self.c=MaxPriorityItem(self.item,self.priority)

    def test_right_init(self):
        self.assertEqual(self.c.item==self.item,True,"wrong item init")
        self.assertEqual(self.c.priority==self.priority,True,"wrong priority init")

    def test_right_compare_more(self):
        self.assertEqual(self.c>MaxPriorityItem(self.item,self.priority+1),True,"wrong compare (more)")

    def test_right_compare_less(self):
        self.assertEqual(self.c<MaxPriorityItem(self.item,(self.priority+1)),False,"wrong compare (less)")


if __name__ == '__main__':
    unittest.main()
