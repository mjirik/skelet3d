#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 mjirik <mjirik@mjirik-Latitude-E6520>
#
# Distributed under terms of the MIT license.

"""

"""
import numpy as np
import unittest
import pytest
import skelet3d
import skelet3d.skeleton_analyser as sk
import copy
import os


class SkeletonAnalyserTest(unittest.TestCase):
    @pytest.mark.slow
    # @unittest.skip("I dont know how to turn off this test on travis-ci")
    @unittest.skipIf(os.environ.get("TRAVIS", True), "Skip on Travis-CI")
    def test_nodes_aggregation_big_data(self):

        data = np.zeros([1000, 1000, 100], dtype=np.int8)
        voxelsize_mm = [14, 10, 6]

        # snake
        # data[15:17, 13, 13] = 1
        data[18, 3:17, 12] = 1
        data[18, 17, 13:17] = 1
        data[18, 9, 4:12] = 1
        data[18, 14, 12:19] = 1
        # data[18, 18, 15:17] = 1

        # T-junction on the left
        data[18, 4:16, 3] = 1
        # import sed3
        # ed = sed3.sed3(data)
        # ed.show()

        skel = data

        skan = sk.SkeletonAnalyser(
            copy.copy(skel),
            volume_data=data,
            voxelsize_mm=voxelsize_mm,
            cut_wrong_skeleton=False,
            aggregate_near_nodes_distance=20,
        )
        vessel_tree = skan.skeleton_analysis()

        # ed = sed3.sed3(skan.sklabel, contour=data)
        # ed.show()
        # import ipdb; ipdb.set_trace() #  noqa BREAKPOINT

        # number of terminals + inner nodes
        self.assertEqual(np.min(skan.sklabel), -7)
        # number of edges
        self.assertEqual(np.max(skan.sklabel), 6)

    def test_nodes_aggregation(self):

        data = np.zeros([20, 20, 20], dtype=np.int8)
        voxelsize_mm = [14, 10, 6]

        # snake
        # data[15:17, 13, 13] = 1
        data[17, 3:17, 12] = 1
        data[17, 17, 13:17] = 1
        data[17, 9, 4:12] = 1
        data[17, 14, 12:19] = 1
        # data[18, 18, 15:17] = 1

        # T-junction on the left
        data[17, 4:16, 3] = 1
        # import sed3
        # ed = sed3.sed3(data)
        # ed.show()

        skel = data

        skan = sk.SkeletonAnalyser(
            copy.copy(skel),
            volume_data=data,
            voxelsize_mm=voxelsize_mm,
            cut_wrong_skeleton=False,
            aggregate_near_nodes_distance=20,
        )
        vessel_tree = skan.skeleton_analysis()

        # ed = sed3.sed3(skan.sklabel, contour=data)
        # ed.show()
        # import ipdb; ipdb.set_trace() #  noqa BREAKPOINT

        # number of terminals + inner nodes
        self.assertEqual(np.min(skan.sklabel), -7)
        # number of edges
        self.assertEqual(np.max(skan.sklabel), 6)

    def test_generate_elipse(self):
        import skelet3d.skeleton_analyser

        mask = skelet3d.skeleton_analyser.generate_binary_elipsoid([6, 4, 3])

        self.assertEqual(mask[0][0][0], 0)
        self.assertEqual(mask[6][4][3], 1)
        # on axis border should be zero
        self.assertEqual(mask[0][4][3], 0)
        self.assertEqual(mask[6][0][3], 0)
        self.assertEqual(mask[6][4][0], 0)

        # on axis border one pixel into center should be one
        self.assertEqual(mask[1][4][3], 1)
        self.assertEqual(mask[6][1][3], 1)
        self.assertEqual(mask[6][4][1], 1)

    def test_length_types(self):
        """
        Test for comparation of various length estimation methods.
        No strong assert here.
        """
        data = np.zeros([20, 20, 20], dtype=np.int8)
        # snake
        data[8:10, 14, 13] = 1
        data[10:12, 15, 13] = 1
        data[12:14, 16, 13] = 1
        # data[18, 14:17, 13] = 1
        # data[18, 17, 14:17] = 1
        # data[14:18, 17, 17] = 1

        skel = data

        skan = sk.SkeletonAnalyser(
            copy.copy(skel), volume_data=data, voxelsize_mm=[1, 20, 300]
        )
        # skan.spline_smoothing = 5
        vessel_tree = skan.skeleton_analysis()
        pixel = vessel_tree[1]["lengthEstimationPixel"]
        poly = vessel_tree[1]["lengthEstimationPoly"]
        spline = vessel_tree[1]["lengthEstimationSpline"]

        # import ipdb; ipdb.set_trace() #  noqa BREAKPOINT
        # self.assertAlmostEqual
        # self.assertAlmostEqual(vessel_tree[1]['lengthEstimationPixel'], 10)
        # self.assertAlmostEqual(vessel_tree[2]['lengthEstimationPixel'], 200)
        # self.assertAlmostEqual(vessel_tree[3]['lengthEstimationPixel'], 3000)
        # self.assertAlmostEqual(vessel_tree[1]['lengthEstimationPixel'],
        #                        diag_length)

    def test_length(self):

        data = np.zeros([20, 20, 20], dtype=np.int8)
        data[2:13, 4, 4] = 1
        data[6, 2:13, 6] = 1
        data[8, 8, 2:13] = 1

        # diagonala
        data[11, 11, 11] = 1
        data[12, 12, 12] = 1
        data[13, 13, 13] = 1

        # snake
        # data[15:17, 13, 13] = 1
        data[18, 14:17, 13] = 1
        data[18, 17, 14:17] = 1
        data[14:18, 17, 17] = 1

        # import sed3
        # ed = sed3.sed3(data)
        # ed.show()

        skel = data

        skan = sk.SkeletonAnalyser(
            copy.copy(skel),
            volume_data=data,
            voxelsize_mm=[1, 20, 300],
            cut_wrong_skeleton=False,
        )

        # ed = sed3.sed3(skan.sklabel)
        # ed.show()
        vessel_tree = skan.skeleton_analysis()

        self.assertAlmostEqual(vessel_tree[1]["lengthEstimationPixel"], 10)
        self.assertAlmostEqual(vessel_tree[2]["lengthEstimationPixel"], 200)
        self.assertAlmostEqual(vessel_tree[3]["lengthEstimationPixel"], 3000)
        diag_length = 2 * ((1 ** 2 + 20 ** 2 + 300 ** 2) ** 0.5)
        self.assertAlmostEqual(vessel_tree[4]["lengthEstimationPixel"], diag_length)
        # test spline
        self.assertLess(
            vessel_tree[3]["lengthEstimationPixel"]
            - vessel_tree[3]["lengthEstimationSpline"],
            0.001,
        )
        # test poly
        self.assertLess(
            vessel_tree[1]["lengthEstimationPixel"]
            - vessel_tree[1]["lengthEstimationPoly"],
            0.001,
        )

    def test_tortuosity(self):
        import skelet3d

        data = np.zeros([20, 20, 20], dtype=np.int8)
        # banana
        data[5, 3:11, 4:6] = 1
        data[5, 10:12, 5:12] = 1

        # bar
        data[5, 3:11, 15:17] = 1

        # import sed3 as ped
        # pe = ped.sed3(data)
        # pe.show()
        skel = skelet3d.skelet3d(data)

        # pe = ped.sed3(skel)
        # pe.show()

        skan = sk.SkeletonAnalyser(
            copy.copy(skel), volume_data=data, voxelsize_mm=[1, 1, 1]
        )
        vessel_tree = skan.skeleton_analysis()

        # banana
        self.assertGreater(vessel_tree[1]["tortuosity"], 1.2)
        # bar
        self.assertLess(vessel_tree[2]["tortuosity"] - 1, 0.00001)

    def test_filter_small(self):
        import skelet3d

        data = np.zeros([20, 20, 20], dtype=np.int8)
        data[5, 3:17, 5] = 1
        # crossing
        data[5, 12, 5:13] = 1
        # vyrustek
        data[5, 8, 5:9] = 1

        data = skelet3d.skelet3d(data)
        # pe = ped.sed3(data)
        # pe.show()

        skan = sk.SkeletonAnalyser(copy.copy(data))
        output = skan.filter_small_objects(data, 3)
        # skan.skeleton_analysis()

        # pe = ped.sed3(output)
        # pe.show()

        self.assertEqual(output[5, 8, 7], 0)

    def test_small_with_write_to_file(self):
        filename = "test_output.yaml"

        # delete file if exists
        if os.path.exists(filename):
            os.remove(filename)

        data = np.zeros([60, 60, 60], dtype=np.int8)
        data[5:8, 13:27, 5:9] = 1
        # crossing
        data[6:21, 18:20, 4:7] = 1

        data_skelet = skelet3d.skelet3d(data)
        # pe = ped.sed3(data)
        # pe.show()

        skan = sk.SkeletonAnalyser(copy.copy(data_skelet), volume_data=data)

        # output = skan.filter_small_objects(data, 3)
        skan.skeleton_analysis()

        # self.assertEqual(output[5, 8, 7], 0)
        skan.to_yaml(filename)
        self.assertTrue(os.path.exists(filename))

    def test_skeleton_analyser_from_portal_vein(self):
        filename = "test_output_synthetic_porta.yaml"

        # delete file if exists
        if os.path.exists(filename):
            os.remove(filename)
        import io3d.datasets

        data3d, segm, voxelsize_mm, slab, seeds_liver, seeds_porta = (
            io3d.datasets.generate_synthetic_liver()
        )

        data_segm = segm == 2
        data_skelet = skelet3d.skelet3d(data_segm)
        self.assertEqual(np.max(data_skelet), 1)
        self.assertEqual(np.min(data_skelet), 0)

        skan = sk.SkeletonAnalyser(copy.copy(data_skelet), volume_data=data_segm)

        skan.skeleton_analysis()

        # self.assertEqual(output[5, 8, 7], 0)
        skan.to_yaml(filename)
        self.assertTrue(os.path.exists(filename))

    def test_skeleton_analyser_from_portal_vein_to_its_branches(self):
        filename = "test_output_synthetic_porta.yaml"

        # delete file if exists
        if os.path.exists(filename):
            os.remove(filename)
        import io3d.datasets

        data3d, segm, voxelsize_mm, slab, seeds_liver, seeds_porta = (
            io3d.datasets.generate_synthetic_liver()
        )

        data_segm = segm == 2

        # data_segm[41:44, 122:127, 68:70] = True
        data_segm[40:45, 77:80, 100:110] = False
        data_segm[42:44, 77:80, 103:106] = True
        data_skelet = skelet3d.skelet3d(data_segm)
        self.assertEqual(np.max(data_skelet), 1)
        self.assertEqual(np.min(data_skelet), 0)

        # import sed3
        # ed = sed3.sed3(data_skelet, contour=data_segm)# , contour=branche_label)
        # ed.show()

        skan = sk.SkeletonAnalyser(copy.copy(data_skelet), volume_data=data_segm)

        branche_label = skan.get_branch_label()

        # import sed3
        # ed = sed3.sed3(branche_label) #, contour=skan.sklabel)
        # ed.show()

        # import sed3
        # ed = sed3.sed3(skan.sklabel)# , contour=branche_label)
        # ed.show()
        self.assertGreater(np.max(branche_label), 2)
        # self.assertLess(np.max(branche_label), -4)
        self.assertEqual(branche_label[0, 0, 0], 0)

    def test_skan_from_skeleton_of_one_tube(self):

        import skelet3d.skeleton_analyser

        # fn_out = 'tree_one_tube.vtk'
        # if os.path.exists(fn_out):
        #     os.remove(fn_out)

        volume_data = np.zeros([7, 8, 9], dtype=np.int)
        volume_data[4:8, 4:6, 1:3] = 1
        volume_data[:, 5, 2:9] = 1
        volume_data[:, 0:7, 5] = 1
        skelet = skelet3d.skelet3d(volume_data)

        skan = skelet3d.skeleton_analyser.SkeletonAnalyser(
            skelet, volume_data=volume_data, voxelsize_mm=[1, 1, 1],
        )
        stats = skan.skeleton_analysis()

        self.assertEqual(
            len(stats),
            1,
            "There should be just one cylinder based on data with different diameter",
        )

    def test_skeleton_analyser_from_portal_vein_to_its_branches_and_save_to_pandas(self):
        filename = "test_output_synthetic_porta.yaml"

        # delete file if exists
        if os.path.exists(filename):
            os.remove(filename)
        import io3d.datasets

        data3d, segm, voxelsize_mm, slab, seeds_liver, seeds_porta = (
            io3d.datasets.generate_synthetic_liver()
        )

        data_segm = segm == 2

        # data_segm[41:44, 122:127, 68:70] = True
        data_segm[40:45, 77:80, 100:110] = False
        data_segm[42:44, 77:80, 103:106] = True
        data_skelet = skelet3d.skelet3d(data_segm)
        self.assertEqual(np.max(data_skelet), 1)
        self.assertEqual(np.min(data_skelet), 0)

        # import sed3
        # ed = sed3.sed3(data_skelet, contour=data_segm)# , contour=branche_label)
        # ed.show()

        skan = sk.SkeletonAnalyser(copy.copy(data_skelet), volume_data=data_segm)
        stats = skan.skeleton_analysis()

        print(stats)
        df = skan.stats_as_dataframe()
        assert df is not None
        # import missingno as msno
        # print(df)
        # msno.matrix(df)
        # from matplotlib import pyplot as plt
        # plt.show()
        # pass

    # def test_skan_from_skeleton_of_one_tube(self):
    #
    #     import skelet3d.skeleton_analyser
    #
    #     # fn_out = 'tree_one_tube.vtk'
    #     # if os.path.exists(fn_out):
    #     #     os.remove(fn_out)
    #
    #     volume_data = np.zeros([7, 8, 9], dtype=np.int)
    #     volume_data[4:8, 4:6, 1:3] = 1
    #     volume_data[:, 5, 2:9] = 1
    #     volume_data[:, 0:7, 5] = 1
    #     skelet = skelet3d.skelet3d(volume_data)
    #
    #     skan = skelet3d.skeleton_analyser.SkeletonAnalyser(
    #         skelet, volume_data=volume_data, voxelsize_mm=[1, 1, 1]
    #     )
    #     stats = skan.skeleton_analysis()
    #
    #     self.assertEqual(
    #         len(stats),
    #         1,
    #         "There should be just one cylinder based on data with different diameter",
    #     )


if __name__ == "__main__":
    unittest.main()
