#! /usr/bin/python
# -*- coding: utf-8 -*-


import wget
import zipfile
import glob
import shutil
import os.path as op
import tempfile

def libfix(url="http://147.228.240.61/queetech/install/ITK%2bSkelet3D_dll.zip"):
    
    outdir = tempfile.gettempdir()
    print "temp directory ", outdir
    outdir = tempfile.mkdtemp()
    print "temp directory ", outdir
    filename = wget.download(url, out=outdir)


    zf = zipfile.ZipFile(filename)
    zf.extractall()
    # for filename in [ 'README.txt', 'notthere.txt' ]:
    #     try:
    #         data = zf.read(filename)
    #     except KeyError:
    #         print 'ERROR: Did not find %s in zip file' % filename
    #     else:
    #         print filename, ':'
    #         print repr(data)
    #     print

    dest_dir = get_conda_dir()

    for file in glob.glob(r'ITK+Skelet3D_dll/*.dll'):
        shutil.copy(file, dest_dir)
        print "copy %s into %s" % (file, dest_dir)


def get_conda_dir():
    from os.path import expanduser
    home = expanduser("~")
    if op.isdir(op.join(home, "anaconda")):
        dstdir = op.join(home, "anaconda")
    elif op.isdir(op.join(home, "miniconda")):
        dstdir = op.join(home, "miniconda")
    elif op.isdir(op.join(home, "miniconda2")):
        dstdir = op.join(home, "miniconda2")
    else:
        print "Cannot find anaconda/miniconda directory"
        dstdir = None

    return dstdir

def main():
    libfix()

if '__main__' == __name__:
    main()
