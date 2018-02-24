#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 mjirik <mjirik@hp-mjirik>
#
# Distributed under terms of the MIT license.

"""

"""
import unittest
from nose.plugins.attrib import attr
import numpy as np

import skelet3d


class Skelet3DTest(unittest.TestCase):

    # @attr('interactive')
    def test_donut(self):
        # Create donut shape
        data = np.ones([3, 7, 9])
        data[:, 3, 3:6] = 0

        expected_skelet = [
            [
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0]],
            [
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 1, 1, 1, 1, 0, 0],
                [0, 1, 0, 0, 0, 0, 0, 1, 0],
                [0, 1, 0, 0, 0, 0, 0, 1, 0],
                [0, 1, 0, 0, 0, 0, 0, 1, 0],
                [0, 0, 1, 1, 1, 1, 1, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0]],
            [
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0]]]
        skelet = skelet3d.skelet3d(data)

        self.assertEqual(
            0,
            np.sum(np.abs(skelet - expected_skelet))
        )

    def test_skelet3d(self):
        data = np.zeros([8, 9, 10], dtype=np.int8)
        data[1:4, 3:7, 1:12] = 1
        # data[2:5, 2:8, 3:7] = 1
        # data[2:5, 2:8, 3:5] = 1
        skelet = skelet3d.skelet3d(data)

# expected result
        expected_skelet = np.zeros([8, 9, 10], dtype=np.int8)
        expected_skelet[2, 5, 2:9] = 1

        self.assertTrue(np.array_equal(expected_skelet, skelet))

if __name__ == "__main__":
    unittest.main()
