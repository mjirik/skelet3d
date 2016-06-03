
# Linux install notes

## Use Anaconda packages


Install ubuntu packages

    sudo apt-get install cmake python-numpy libinsighttoolkit3-dev libpng12-dev libgdcm2-dev

For Ubuntu 16.04 install 

    sudo apt-get install libgdcm2.6

Install Miniconda

    wget http://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh -O Miniconda-latest-Linux-x86_64.sh
    bash Miniconda-latest-Linux-x86_64.sh -b


Add `miniconda2/bin` directory to path or restart terminal


    cd
    export "PATH=`pwd`/miniconda2/bin:$PATH"

Install skelet3d

    conda install -c mjirik skelet3d
    
To build `.so` libraries you will need download skelet3d sources:

    cd build
    cmake ..
    make
    make install



## Install skelet without Anaconda

Install prerequisites

    sudo apt-get install cmake python-numpy libinsighttoolkit3-dev libpng12-dev libgdcm2-dev python-pip

Install python package

    pip install skelet3d

Install `.so` libraries

    sudo python -m skelet3d.libfixer

## Get `.so` libraries

There are 3 ways how to obtain `.so` libs:

* Install with `skelet3d`

      sudo python -m skelet3d.libfixer

* Manual download

    Download [linux build](http://147.228.240.61/queetech/install/Skelet3D_so.zip)
    and install to `/usr/local/lib`


* Build

    To build `.so` libraries you will need download skelet3d sources.

    build c++ library

        cd build
        cmake ..
        make
        make install
    


