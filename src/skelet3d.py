#! /usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np

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

    libpath = ctypes.util.find_library('BinaryThinningCxxShared')
    
    #os.environ['PATH'] 
    #import pdb; pdb.set_trace()
    hlibc = ctypes.CDLL(libpath)
    
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



    pass

if __name__ == "__main__":
    main()
