from utils import StoppedThread
import unittest


class Test_case_StoppedThread(unittest.TestCase):

    def setUp(self):
        self.st = StoppedThread()

    def test_StThread_is_alive_when_stopped(self):
        self.st.stop()
        self.assertEqual(self.st.is_alive(), False, "is alive when thread stopped")

    def test_StThread_is_alive_when_inited(self):
        self.assertEqual(self.st.is_alive(), True, "isnt alive when inited")
        # What can i test here more?


if __name__ == '__main__':
    unittest.main()
