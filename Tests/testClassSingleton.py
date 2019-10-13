from utils import Singleton
import unittest
import math

class Test_class_for_meta_Singleton(metaclass=Singleton):
    pass
    
class Test_case_meta_Singleton(unittest.TestCase):

    def test_true_singleton(self):
        c=Test_class_for_meta_Singleton()
        self.assertEqual(c,Test_class_for_meta_Singleton(),"another class instance created")


if __name__ == '__main__':
    unittest.main()
