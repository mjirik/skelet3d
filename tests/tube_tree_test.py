#! /usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
# import funkcí z jiného adresáře
import os
import os.path

from nose.plugins.attrib import attr
path_to_script = os.path.dirname(os.path.abspath(__file__))
import unittest
import numpy as np
import sys

import skelet3d
logger.debug(str(dir(skelet3d)))
logger.debug(skelet3d.__file__)
# import skelet3d.
# from skelet3d import TreeBuilder
import skelet3d.tree
from skelet3d.tree import TreeBuilder

#

class TubeTreeTest(unittest.TestCase):
    def setUp(self):
        self.interactivetTest = False
    # interactivetTest = True

    @attr("LAR")
    def test_vessel_tree_lar(self):
        import skelet3d.tb_lar
        tvg = TreeBuilder(skelet3d.tb_lar.TBLar)
        yaml_path = os.path.join(path_to_script, "./hist_stats_test.yaml")
        tvg.importFromYaml(yaml_path)
        tvg.voxelsize_mm = [1, 1, 1]
        tvg.shape = [100, 100, 100]
        output = tvg.buildTree() # noqa
        if self.interactiveTests:
            tvg.show()

    def test_vessel_tree_vtk(self):
        tvg = TreeBuilder('vtk')
        yaml_path = os.path.join(path_to_script, "./hist_stats_test.yaml")
        tvg.importFromYaml(yaml_path)
        tvg.voxelsize_mm = [1, 1, 1]
        tvg.shape = [100, 100, 100]
        output = tvg.buildTree() # noqa
        tvg.show()
        tvg.saveToFile("tree_output.vtk")

    @unittest.skipIf(not ("skelet3d" in sys.modules), "skelet3d is not installed")
    def test_vessel_tree_vtk_from_skeleton(self):

        import skelet3d
        import skelet3d.skeleton_analyser
        import shutil

        fn_out = 'tree.vtk'
        if os.path.exists(fn_out):
            os.remove(fn_out)

        volume_data = np.zeros([3, 7, 9], dtype=np.int)
        volume_data [:, :, 1:3] = 1
        volume_data [:, 5, 2:9] = 1
        volume_data [:, 0:7, 5] = 1
        skelet = skelet3d.skelet3d(volume_data)

        skan = skelet3d.skeleton_analyser.SkeletonAnalyser(skelet, volume_data=volume_data, voxelsize_mm=[1,1,1])
        stats = skan.skeleton_analysis()

        tvg = TreeBuilder('vtk')
        tvg.voxelsize_mm = [1, 1, 1]
        tvg.shape = [100, 100, 100]
        tvg.tree_data = stats
        output = tvg.buildTree() # noqa
        tvg.saveToFile(fn_out)
        os.path.exists(fn_out)

    # TODO finish this test
    def test_vessel_tree_vol(self):
        import skelet3d.tb_volume
        tvg = TreeBuilder(skelet3d.tb_volume.TBVolume)
        yaml_path = os.path.join(path_to_script, "./hist_stats_test.yaml")
        tvg.importFromYaml(yaml_path)
        tvg.voxelsize_mm = [1, 1, 1]
        tvg.shape = [100, 100, 100]
        output = tvg.buildTree() # noqa
        # tvg.show()
        # if self.interactiveTests:
        #     tvg.show()

    def test_import_new_vt_format(self):

        tvg = TreeBuilder()
        yaml_path = os.path.join(path_to_script, "vt_biodur.yaml")
        tvg.importFromYaml(yaml_path)
        tvg.voxelsize_mm = [1, 1, 1]
        tvg.shape = [150, 150, 150]
        data3d = tvg.buildTree()

    def test_test_export_to_esofspy(self):
        """
        tests export function
        """

        import skelet3d.vesseltree_export as vt
        yaml_input = os.path.join(path_to_script, "vt_biodur.yaml")
        yaml_output = os.path.join(path_to_script, "delme_esofspy.txt")
        vt.vt2esofspy(yaml_input, yaml_output)


    def test_tree_generator(self):
        import numpy as np
        tree_data = {

        }
        element_number = 5
        np.random.seed(0)
        pts = np.random.random([element_number, 3]) * 100

        # construct voronoi
        import scipy.spatial
        vor3 = scipy.spatial.Voronoi(pts)


        for i, two_points in enumerate(vor3.ridge_points):
            edge = {
                #"nodeA_ZYX_mm": np.random.random(3) * 100,
                "nodeA_ZYX_mm": vor3.vertices[two_points[0]],
                "nodeB_ZYX_mm": vor3.vertices[two_points[1]],
                #"nodeB_ZYX_mm": np.random.random(3) * 100,
                "radius_mm": 3
            }
            tree_data[i] = edge

        length = len(tree_data)
        for i in range(element_number):
            edge = {
                #         #"nodeA_ZYX_mm": np.random.random(3) * 100,
                "nodeA_ZYX_mm": pts[i-1],
                "nodeB_ZYX_mm": pts[i],
                #         "nodeB_ZYX_mm": np.random.random(3) * 100,
                "radius_mm": 1
            }
            tree_data[i+length] = edge

        tvg = TreeBuilder('vtk')
        yaml_path = os.path.join(path_to_script, "./hist_stats_test.yaml")
        # tvg.importFromYaml(yaml_path)
        tvg.voxelsize_mm = [1, 1, 1]
        tvg.shape = [100, 100, 100]
        tvg.tree_data = tree_data
        output = tvg.buildTree() # noqa
        # tvg.show()
        tvg.saveToFile("tree_output.vtk")

        tvg.voxelsize_mm = [1, 1, 1]
        # self.assertTrue(False)



def dist_to_vectors(v1, vlist):
    import numpy as np
    out = []
    for v2 in vlist:
        dist = np.linalg.norm(v1-v2)
        out.append(dist)
    return np.asarray(out)




if __name__ == "__main__":
    unittest.main()
