#! /usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import traceback
import sys

def skelet3d(data):
    """
    skel = skeleton (data)

    data: 3D numpy data
    skel: 3D skeleton

    """
    import ctypes
    import ctypes.util
    #import os

    data = data.astype('int8')

# ThinningCxxShared is C++, ThinningShared is C
    #libpath = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) +\
    #        "/../bin/libBinaryThinningCxxShared.so")
    #        #"/../bin/libBinaryThinningShared.so")
    #if not os.path.exists(libpath):
    #    libpath = "libBinaryThinningCxxShared.so"

    libname = 'BinaryThinningCxxShared'
    libpath = ctypes.util.find_library(libname)

    if libpath is None:
        if sys.platform.startswith('win'):
            import libfixer
            libfixer.libfix()
            print "Trying to download dll libraries"
            libpath = ctypes.util.find_library(libname)
        if sys.platform.startswith('linux'):
            import libfixer
            libfixer.libfix_linux_conda()
            print "Trying to download dll libraries"
            libpath = ctypes.util.find_library(libname)



    #os.environ['PATH'] 
    #import pdb; pdb.set_trace()
    try:
        hlibc = ctypes.CDLL(libpath)
    except Exception, e:
        print "libname: ", libname
        print "libpath: ", libpath
        print traceback.format_exc()
        if libpath != None:
            print "CDLL cannot find library."
            print "On Linux is the problem with LD_LIBRARY_PATH."
            print "On Windows could be problem with messing 32-bit and 64-bit DLL libraries."
            print "Please read skelet3d/README.md"
            print "https://github.com/mjirik/skelet3d/blob/master/README.md"

        #print e

        exit()

    
# unsigned char * thinningCxx (int sizeX, int sizeY, int sizeZ, unsigned char *)
# function .tostring() give char stream
    thinning = hlibc.thinningCxx
    #thinning = hlibc.thinning
    thinning.restype = ctypes.c_char_p

    sdata = data.tostring()

    outstr = thinning(
            data.shape[2], 
            data.shape[1],
            data.shape[0],
            ctypes.c_char_p(sdata)
            )

    outa = np.fromstring(sdata, dtype='uint8')
    return outa.reshape(data.shape)



def main():
    data = np.zeros([8,9,10], dtype='int8')
    data [1:4, 3:7,1:12] = 1
    print "Example"
    print "Input data"
    print data
    skelet3d(data)
    print "Output data"

if __name__ == "__main__":
    main()
