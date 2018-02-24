#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © %YEAR% %USER% <%MAIL%>
#
# Distributed under terms of the %LICENSE% license.

"""
%HERE%
"""


import skelet3d
import numpy as np
# Create donut shape
volume_data = np.zeros([3, 7, 9], dtype=np.int)
volume_data [:, :, 1:3] = 1
volume_data [:, 5, 2:9] = 1
volume_data [:, 0:7, 5] = 1
skelet = skelet3d.skelet3d(volume_data)

skan = skelet3d.SkeletonAnalyser(skelet, volume_data=volume_data, voxelsize_mm=[1,1,1])
stats = skan.skeleton_analysis()
edge_number = 1
print(stats[edge_number]['radius_mm'])
