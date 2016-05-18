# bumpversion patch
# python setup.py register sdist upload

# from distutils.core import setup
from setuptools import setup, find_packages
import sys
import os
import os.path as op
import distutils.spawn as ds
import distutils.dir_util as dd

## This file is not used now. TODO finish setup.py install process

#################
# CMake function
#################
#def run_cmake(cmake_args="-DSIMX_USE_PRIME=1 -DSIMX_USE_MPI=1"):

cmake_pkgdir = '${CMAKE_CURRENT_SOURCE_DIR}'

if cmake_pkgdir[0] == '$':
    package_dir={}# {'':'./'}
else:
    package_dir={ '': cmake_pkgdir }

__VERSION__='1.4.15'

# src_dir = os.path.abspath(__file__)
# src_dir, fl = os.path.split(src_dir)
# src_dir = src_dir + "/src"


def run_cmake(no_setuppy=1):
    """
    Runs CMake to determine configuration for this build
    """
    if ds.find_executable('cmake') is None:
        print "CMake  is required to build SimX"
        print "Please install cmake version >= 2.6 and re-run setup"
        sys.exit(-1)
        
    print "Configuring SimX build with CMake.... "
    new_dir = op.join(op.split(__file__)[0],'build')
    dd.mkpath(new_dir)
    os.chdir(new_dir)
    # construct argument string
    cmake_args = ''
    # cmake_args ="-DNO_SETUPPY=" + str(no_setuppy)

    try:
        ds.spawn(['cmake','../']+cmake_args.split())
    except ds.DistutilsExecError:
        print "Error while running cmake"
        print "run 'setup.py build --help' for build options"
        print "You may also try editing the settings in CMakeLists.txt file and re-running setup"
        sys.exit(-1)

# run_cmake()
print 'pkgdir ', package_dir
setup(
    name='skelet3d',
    version=__VERSION__,
    package_dir=package_dir,
    author='Miroslav Jirik',
    author_email="miroslav.jirik@gmail.com",

#	"c:\\users/mjirik/projects/skelet3d/src" },
    packages=find_packages(),
    # py_modules=['skelet3d']
    install_requires=['numpy', 'scipy'],
    )
