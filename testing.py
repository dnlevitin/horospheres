import unittest 

# To run: 
# sage --python3 -m unittest testing.py
# to run a specific test:
# sage --python3 -m unittest test_something
class BasicTestSuit(unittest.TestCase):
    """ Basic test cases """

    def test_something(self):
        self.assertEqual(1, True)
        self.assertEqual(2, False)