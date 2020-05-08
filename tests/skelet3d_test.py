#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 mjirik <mjirik@hp-mjirik>
#
# Distributed under terms of the MIT license.

"""

"""
from loguru import logger
import unittest
import os
import sys
import numpy as np
import skelet3d
import pytest

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
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
            ],
            [
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 1, 1, 1, 1, 0, 0],
                [0, 1, 0, 0, 0, 0, 0, 1, 0],
                [0, 1, 0, 0, 0, 0, 0, 1, 0],
                [0, 1, 0, 0, 0, 0, 0, 1, 0],
                [0, 0, 1, 1, 1, 1, 1, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
            ],
            [
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0],
            ],
        ]
        skelet = skelet3d.skelet3d(data)

        self.assertEqual(0, np.sum(np.abs(skelet - expected_skelet)))

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

        data3d, segm, voxelsize_mm, slab, seeds_liver, seeds_porta = (
            io3d.datasets.generate_synthetic_liver()
        )

        skelet = skelet3d.skelet3d(segm == 2)
        self.assertEqual(np.max(skelet), 1)
        self.assertEqual(np.min(skelet), 0)

    @unittest.skip("TODO find solution for bug in skelet algorithm")
    def test_skeleton_problem_with_some_types_of_rectangular_structures(self):
        # TODO fix bug in skeletonization algorithm.
        # It ignores vertical structures and horizontal structures. Sometimes is just change the shape inough.
        #
        import io3d.datasets

        data3d, segm, voxelsize_mm, slab, seeds_liver, seeds_porta = (
            io3d.datasets.generate_synthetic_liver()
        )

        data_segm = segm == 2

        # data_segm[39:44, 120:170, 100:111] = True
        # data_segm[39:44, 50:120, 60:70] = True
        # data_segm[39:44, 60:120, 100:105] = True
        # data_segm[39:44, 60:120, 110:110 + 5] = True
        data_segm[39:44, 120:130, 120:240] = True
        data_segm[39:44, 60:120, 120 : 120 + 6] = True
        data_segm[39:44, 60:120, 130 : 130 + 7] = True
        data_segm[39:44, 60:120, 140 : 140 + 8] = True
        data_segm[39:44, 60:120, 160 : 160 + 9] = True
        data_segm[39:44, 60:120, 180 : 180 + 10] = True
        data_segm[39:44, 60:120, 200 : 200 + 11] = True
        data_segm[39:44, 60:120, 220 : 220 + 12] = True
        # data_segm[39:44, 60:120, 120:126] = True
        # data_segm[39:44, 60:120, 130:140] = True
        # data_segm[39:44, 60:120, 150:151] = True
        # data_segm[39:44, 60:120, 160:162] = True

        data_skelet = skelet3d.skelet3d(data_segm)

        import sed3

        ed = sed3.sed3(data_skelet, contour=data_segm)  # , contour=branche_label)
        ed.show()

        self.assertEqual(
            np.max(data_skelet[39:44, 60:100, 140 : 140 + 8]),
            1,
            "In this branche is expected skeleton",
        )
        self.assertEqual(np.min(data_skelet), 0)
        self.assertEqual(np.max(data_skelet), 1)


@unittest.skip("Complex example to debug all problems")
def test_skeleton_ircad():
    import io3d.datasets
    from pathlib import Path
    import sed3

    from skimage.measure import label
    pth = Path(io3d.datasets.join_path("medical/orig/3Dircadb1.16/MASKS_DICOM/portalvein", get_root=True))
    datap = io3d.read(pth, dataplus_format=True)
    data_segm = datap["data3d"]

    data_skelet = skelet3d.skelet3d(data_segm)
    lab_segm = label(data_segm)
    nlab_segm = np.max(lab_segm)
    un_sg = np.unique(lab_segm)
    logger.debug(nlab_segm)
    logger.debug(un_sg)

    lab_skel = label(data_skelet)
    un_sk = np.unique(lab_skel)
    nlab_skel = np.max(lab_skel)
    logger.debug(nlab_skel)
    logger.debug(un_sk)

    skvals = lab_segm[data_skelet > 0]
    sklabs = lab_skel[data_skelet > 0]
    import sklearn.metrics
    from matplotlib import pyplot as plt

    # cm = sklearn.metrics.confusion_matrix(sklabs, skvals, labels=un_sg)
    # plt.show()

    # ed = sed3.sed3(lab_skel, contour=lab_segm)  # , contour=branche_label)
    # ed.show()

    skan = skelet3d.skeleton_analyser.SkeletonAnalyser(
        (data_skelet > 0).astype(np.uint8), volume_data=(data_segm>0).astype(np.uint8), voxelsize_mm=[1, 1, 1]
    )

    stats = skan.skeleton_analysis()
    df = skan.stats_as_dataframe()
    import missingno as msno
    msno.matrix(df, labels=True)

    from matplotlib import pyplot as plt
    plt.show()
    assert False



