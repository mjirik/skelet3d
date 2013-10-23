skelet3d
========

Skeletonize algorithm based on ITKThinningImageFilter3D. 
There is dynamic linked library installed by cmake. Python and Matlab 
scripts call this library. 



Install notes
=============


    cd build
    cmake ..
    make
    make install

For matlab wrapper run src/compile.m

    matlab -nodesktop -nosplash -r "cd src;compile;exit"

Then there is binaryThhinningMex.mexa64 file. It is used by skelet3d.m.

