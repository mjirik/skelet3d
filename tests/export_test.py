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
# import sys

import skelet3d
logger.debug(str(dir(skelet3d)))
logger.debug(skelet3d.__file__)
# import skelet3d.

#

class ExportTest(unittest.TestCase):
    def setUp(self):
        self.interactivetTest = False
    # interactivetTest = True


    def test_test_export_to_esofspy(self):
        """
        tests export function
        """

        import skelet3d.vesseltree_export as vt
        yaml_input = os.path.join(path_to_script, "vt_biodur_simple.yaml")
        yaml_output = os.path.join(path_to_script, "delme_esofspy.txt")
        vt.vt2esofspy(yaml_input, yaml_output)




if __name__ == "__main__":
    unittest.main()
