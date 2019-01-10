#!/bin/bash

$PYTHON setup.py install

# Add more build steps here, if they are necessary.

# See
# http://docs.continuum.io/conda/build.html
# for a list of environment variables that are set during the build process.

mkdir build_cmake
cd build_cmake
CMAKE_GENERATOR="Unix Makefiles"
# CMAKE_ARCH="-m"$ARCH

cmake .. -G"$CMAKE_GENERATOR" -DCMAKE_INSTALL_PREFIX=$PREFIX
cmake --build .
cmake --build . --target install
cd ..