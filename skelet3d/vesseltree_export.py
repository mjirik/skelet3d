#! /usr/bin/python
# -*- coding: utf-8 -*-
"""
Modul is used for skeleton binary 3D data analysis
"""

# import sys
import os.path

# path_to_script = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(os.path.join(path_to_script, "../extern/dicom2fem/src"))

from loguru import logger
import argparse
from io import open

# import traceback

# import numpy as np
# import scipy.ndimage


def vt2esofspy(vesseltree, outputfilename="tracer.txt", axisorder=[0, 1, 2]):
    """
    exports vesseltree to esofspy format

    :param vesseltree: filename or vesseltree dictionary structure
    :param outputfilename: output file name
    :param axisorder: order of axis can be specified with this option
    :return:
    """

    if (type(vesseltree) == str) and os.path.isfile(vesseltree):
        from ruamel.yaml import YAML

        yaml = YAML(typ="unsafe")
        with open(vesseltree, encoding="utf-8") as f:
            vt = yaml.load(f)
    else:
        vt = vesseltree
    logger.debug(str(vt["general"]))
    logger.debug(str(vt.keys()))
    vtgm = vt["graph"]["microstructure"]
    lines = []
    vs = vt["general"]["voxel_size_mm"]
    sh = vt["general"]["shape_px"]

    # switch axis
    ax = axisorder

    lines.append("#Tracer+\n")
    lines.append("#voxelsize mm %f %f %f\n" % (vs[ax[0]], vs[ax[1]], vs[ax[2]]))
    lines.append("#shape %i %i %i\n" % (sh[ax[0]], sh[ax[1]], sh[ax[2]]))
    lines.append(str(len(vtgm) * 2) + "\n")

    i = 1
    for id in vtgm:
        try:
            nda = vtgm[id]["nodeA_ZYX"]
            ndb = vtgm[id]["nodeB_ZYX"]
            lines.append("%i\t%i\t%i\t%i\n" % (nda[ax[0]], nda[ax[1]], nda[ax[2]], i))
            lines.append("%i\t%i\t%i\t%i\n" % (ndb[ax[0]], ndb[ax[1]], ndb[ax[2]], i))
            i += 1
        except:
            pass

    lines.append("%i\t%i\t%i\t%i" % (0, 0, 0, 0))
    lines[3] = str(i - 1) + "\n"
    from builtins import str as text

    with open(outputfilename, "wt") as f:
        for line in lines:
            f.write(text(line))
        # f.writelines(lines)


if __name__ == "__main__":

    # logger.debug('input params')

    # input parser
    parser = argparse.ArgumentParser(description="Vessel tree export to esofspy")
    parser.add_argument("-o", "--output", default="tracer.txt", help="output file name")
    parser.add_argument("-i", "--input", default=None, help="input")
    parser.add_argument(
        "-ao",
        "--axisorder",
        metavar="N",
        type=int,
        nargs=3,
        default=[0, 1, 2],
        help="Drder of axis in output. Default: 0 1 2",
    )
    args = parser.parse_args()

    vt2esofspy(args.input, outputfilename=args.output, axisorder=args.axisorder)
