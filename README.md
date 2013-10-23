skelet3d
========

Skeletonize algorithm based on ITKThinningImageFilter3D. 
There is dynamic linked library installed by cmake. Python and Matlab 
scripts call this library. 

Prerequisites
=============

  * Python (2.7)
  * CMake
  * ITK



Install notes
=============


    cd build
    cmake ..
    make
    make install

For matlab wrapper run src/compile.m

    matlab -nodesktop -nosplash -r "cd src;compile;exit"

Then there is binaryThhinningMex.mexa64 file. It is used by skelet3d.m.


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





