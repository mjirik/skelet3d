[![Build Status](https://travis-ci.org/mjirik/skelet3d.svg)](https://travis-ci.org/mjirik/skelet3d)
[![Coverage Status](https://coveralls.io/repos/mjirik/skelet3d/badge.svg)](https://coveralls.io/r/mjirik/skelet3d)

skelet3d
========

Skeletonize algorithm based on [ITKThinningImageFilter3D](http://hdl.handle.net/1926/1292). 
There is dynamic linked library installed by cmake. Python and Matlab 
scripts call this library. 

Prerequisites
=============

  * Python (2.7)
  * CMake
  * ITK
  * Numpy
  * InsightToolkit

Install prerequisites on Ubuntu 14.04

    sudo apt-get install cmake python-numpy libinsighttoolkit3-dev libpng12-dev libgdcm2-dev
    
 Windows 
 
* install [cmake](https://cmake.org/)
* Download Visual Studio Express (https://www.visualstudio.com/products/visual-studio-community-vs#)
* install numpy. Recommended is installation with [Anaconda](https://www.continuum.io/downloads) 
* download and install [InsightToolkit](http://www.itk.org/) - [video GUI tutorial](https://www.youtube.com/watch?v=f79joU6FTFQ) or with command line:

        mkdir itk-build-64
        cd itk-build-64
        cmake cmake -G "Visual Studio 14 2015 Win64" -DBUILD_EXAMPLES=OFF -DBUILD_TESTING=OFF -DBUILD_SHARED_LIBS=ON ..\InsightToolkit-4.7.1
        C:\Windows\Microsoft.NET\Framework64\v4.0.30319\MSBuild.exe ALL_BUILD.vcxproj
* Build skelet3d library

        mkdir build
        cd build
        cmake -G "Visual Studio 14 2015 Win64" ..
        C:\Windows\Microsoft.NET\Framework64\v4.0.30319\MSBuild.exe ALL_BUILD.vcxproj
        
 


Install notes
=============


    cd build
    cmake ..
    make
    make install

For matlab wrapper run src/compile.m

    matlab -nodesktop -nosplash -r "cd src;compile;exit"

Then there is binaryThhinningMex.mexa64 file. It is used by skelet3d.m.

Example
=======

Simple example with donut shape

    import skelet3d

    # Create donut shape
    data = np.ones([3,7,9])
    data [:, 3, 3:6] = 0

    skelet = skelet3d.skelet3d(data)

    print skelet

Result:

    array([[[0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0]],

            [[0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 1, 1, 1, 1, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 1, 0],
            [0, 1, 0, 0, 0, 0, 0, 1, 0],
            [0, 1, 0, 0, 0, 0, 0, 1, 0],
            [0, 0, 1, 1, 1, 1, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0]],

            [[0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0]]], dtype=uint8)



Troubleshooting
===============

Problems with build
-------------------

In case of any problems You can use binary files and manually copy it into 
expected paths. BinaryThinningCxxShared library should be in `/usr/local/lib` 
on Linux or somewhere in system `PATH` on windows. Python module `skelet3d.py`
can be used directly.


Cannot find library
-------------------


libBinaryThinningCxxShared.so: cannot open shared object file: No such file or 
directory


Probably there is a problem in Ubuntu with `LD_LIBRARY_PATH`. If you do want 
to add correct library paths:

    echo "include /usr/local/lib" | sudo tee -a /etc/ld.so.conf
    sudo ldconfig -v

More information on:

http://bugs.python.org/issue18502

http://ubuntuforums.org/showthread.php?t=1498755

ld cannot find -lz and -lpng
-----------------------------

Problem is probabli in 32-bit compiling in 64-bit system. You need install fallowing packages. 
    
    sudo apt-get install lib32z1-dev libpng12-dev


