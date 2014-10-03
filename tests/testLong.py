import unittest
import time

class TestLong(unittest.TestCase):

    def test_longtest(self):
        time.sleep(5)
        self.assertTrue(True)
    
    def test_mediumtest(self):
        time.sleep(3)
        self.assertTrue(True)
    
    def test_shorttest(self):
        time.sleep(4)
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
