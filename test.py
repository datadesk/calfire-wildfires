#! /usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import calfire_wildfires


class MyUnitTest(unittest.TestCase):

    def test_fires(self):
        calfire_wildfires.get_fires()

    def test_active_fires(self):
        calfire_wildfires.get_active_fires()


if __name__ == '__main__':
    unittest.main()
