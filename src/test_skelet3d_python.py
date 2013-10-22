#! /usr/bin/python
# -*- coding: utf-8 -*-
import unittest
import numpy as np

import skelet3d

class Skelet3DTest(unittest.TestCase):
    def test_skelet3d(self):
        data = np.zeros([8,9,10], dtype=np.int8)
        data [1:4, 3:7,1:12] = 1
        #data [2:5, 2:8, 3:7] = 1
        #data [2:5, 2:8, 3:5] = 1
        skelet = skelet3d.skelet3d(data)

# expected result
        expected_skelet = np.zeros([8,9,10], dtype=np.int8)
        expected_skelet[2,5,2:9] = 1

        self.assertTrue(np.array_equal(expected_skelet, skelet))


if __name__ == "__main__":
    unittest.main()
