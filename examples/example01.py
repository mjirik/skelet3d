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
data = np.ones([3,7,9])
data [:, 3, 3:6] = 0

skelet = skelet3d.skelet3d(data)

print(skelet)
