#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 mjirik <mjirik@hp-mjirik>
#
# Distributed under terms of the MIT license.

"""

"""
import logging
logger = logging.getLogger(__name__)
import unittest
import os
import sys
from nose.plugins.attrib import attr
import numpy as np
import skelet3d

path_to_script = os.path.dirname(os.path.abspath(__file__))
imcut_path = os.path.join(path_to_script, "../../io3d/")
sys.path.insert(0, imcut_path)


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

    def test_import_libfixer(self):
        import skelet3d.libfixer
        condadir = skelet3d.libfixer.get_conda_dir()
        condadir_old = skelet3d.libfixer.get_conda_dir_old()

    def test_skeleton_from_portal_vein(self):
        import io3d.datasets
        data3d, segm, voxelsize_mm, slab, seeds_liver, seeds_porta = io3d.datasets.generate_synthetic_liver()

        skelet = skelet3d.skelet3d(segm == 2)
        self.assertEqual(np.max(skelet), 1)
        self.assertEqual(np.min(skelet), 0)

if __name__ == "__main__":
    unittest.main()
