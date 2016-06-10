#!/usr/bin/env bash
#
# if script is called with:
#   no argument: stable version is installed
#   devel: devel version with ssh
#   noclone: requirements are installed but lisa is not cloned
#   any other argument: devel version with https is used
#
# installer.sh - main script for linux and osx
# install_nosudo.sh - install conda requirements and skelet3d (to ~/projects/ directory) for linux and osx
#
NARGS=$#
ARG1=$1
ACTUALDIR="`pwd`"
cd ~
HOMEDIR="`pwd`"
USER="$(echo `pwd` | sed 's|.*home/\([^/]*\).*|\1|')"

echo "installing for user:"
echo "$USER"

#REQUIREMENTS_APT="ttps://raw.githubusercontent.com/mjirik/lisa/master/requirements_apt.txt"

# 0. install apt-get/brew dependencies
if [[ "$OSTYPE" == "linux-gnu" ]]; then
#    wget `echo $REQUIREMENTS_APT`-O requirements_apt.txt
#    sudo apt-get install -y -qq $(grep -vE "^\s*#" requirements_apt.txt | tr "\n" " ")
#    wget https://raw.githubusercontent.com/mjirik/lisa/master/install_nosudo.sh -O install_nosudo.sh

    sudo apt-get install -qq cmake git libinsighttoolkit3-dev libpng12-dev libgdcm2-dev
elif [[ "$OSTYPE" == "darwin"* ]]; then
    if hash brew 2>/dev/null; then
        echo "brew is installed"
    else
        echo "installing brew"
        ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
    fi
    brew install git cmake homebrew/science/insighttoolkit libpng
#    curl https://raw.githubusercontent.com/mjirik/lisa/master/install_nosudo.sh -o install_nosudo.sh
fi

# 1. conda python packages
if hash conda 2>/dev/null; then
    echo "Conda is installed"
else

    touch ~/.bashrc
    MACHINE_TYPE=`uname -m`
    if [[ "$OSTYPE" == "linux-gnu" ]]; then
        if [ ${MACHINE_TYPE} == 'x86_64' ]; then
            echo "Installing 64-bit conda"
        # 64-bit stuff here
            wget http://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh -O Miniconda-latest-Linux-x86_64.sh
            bash Miniconda-latest-Linux-x86_64.sh -b
        else
        # 32-bit stuff here
            echo "Installing 32-bit conda"
            wget http://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86.sh -O Miniconda-latest-Linux-x86.sh
            bash Miniconda-latest-Linux-x86.sh -b
        fi
        # we are not sure which version will be installed
        echo "export PATH=$HOMEDIR/miniconda/bin:\$PATH" >> ~/.bashrc
        echo "export PATH=$HOMEDIR/miniconda2/bin:\$PATH" >> ~/.bashrc

    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "Installing conda"
        curl "http://repo.continuum.io/miniconda/Miniconda-latest-MacOSX-x86_64.sh" -o "Miniconda-latest.sh"
        bash Miniconda-latest.sh -b
        # we are not sure which version will be installed
        echo "export PATH=$HOMEDIR/miniconda/bin:\$PATH" >> ~/.profile
        echo "export PATH=$HOMEDIR/miniconda2/bin:\$PATH" >> ~/.profile

        curl https://raw.githubusercontent.com/mjirik/lisa/master/install_nosudo.sh -o install_nosudo.sh
    fi
    export PATH=$HOMEDIR/miniconda/bin:$PATH
    export PATH=$HOMEDIR/miniconda2/bin:$PATH
    conda -V
fi


cd $ACTUALDIR

mkdir projects
cd projects

git clone https://github.com/mjirik/skelet3d.git
cd skelet3d
mkdir build
cd build
cmake ..
cmake --build .
sudo make install


conda install skelet3d
