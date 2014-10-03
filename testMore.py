import unittest
import time

class TestMore(unittest.TestCase):

    def test_morelongtest(self):
        time.sleep(5)
        self.assertTrue(True)
    
    def test_moremediumtest(self):
        time.sleep(3)
        self.assertTrue(True)
    
    def test_moreshorttest(self):
        time.sleep(1)
        self.assertTrue(True)

if __name__ == "__main__":
    uninttest.main()
