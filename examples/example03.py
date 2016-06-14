#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

import numpy as np
import skelet3d
import skelet3d.skeleton_analyser
import skelet3d.tree
from skelet3d.tree import TreeGenerator

# output vtk file can be visualized with ParaView
fn_out = 'tree.vkt'

volume_data = np.zeros([3, 7, 9], dtype=np.int)
volume_data [:, :, 1:3] = 1
volume_data [:, 5, 2:9] = 1
volume_data [:, 0:7, 5] = 1
skelet = skelet3d.skelet3d(volume_data)

skan = skelet3d.skeleton_analyser.SkeletonAnalyser(skelet, volume_data=volume_data, voxelsize_mm=[1,1,1])
stats = skan.skeleton_analysis()

tvg = TreeGenerator('vtk')
tvg.voxelsize_mm = [1, 1, 1]
tvg.shape = [100, 100, 100]
tvg.tree_data = stats
output = tvg.generateTree() # noqa
tvg.saveToFile(fn_out)
print "Output saved as '{}'".format(fn_out)
