import unittest
import calfire_wildfires


class MyUnitTest(unittest.TestCase):

    def test_all_fires(self):
        calfire_wildfires.get_all_fires()

    def test_active_fires(self):
        calfire_wildfires.get_active_fires()


if __name__ == '__main__':
    unittest.main()
