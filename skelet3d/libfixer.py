#! /usr/bin/python
# -*- coding: utf-8 -*-


import wget
import zipfile
import glob
import shutil
import os
import os.path as op
import tempfile

def download_and_unzip(url):
    outdir = tempfile.gettempdir()
    # print "temp directory ", outdir
    outdir = tempfile.mkdtemp()
    print "temp file ", outdir
    # there is problem with wget. It uses its ouwn tempfile in current dir. It is not sure that there will
    # be requred permisson for write
    filename = wget.download(url, out=op.join(outdir, "skelet3d.zip"))


    zf = zipfile.ZipFile(filename)
    zf.extractall()
    zf.close()
    # for filename in [ 'README.txt', 'notthere.txt' ]:
    #     try:
    #         data = zf.read(filename)
    #     except KeyError:
    #         print 'ERROR: Did not find %s in zip file' % filename
    #     else:
    #         print filename, ':'
    #         print repr(data)
    #     print
    return outdir

def libfix(url="http://147.228.240.61/queetech/install/ITK%2bSkelet3D_dll.zip"):
    outdir = download_and_unzip(url)

    dest_dir = get_conda_dir()

    for file in glob.glob(r'ITK+Skelet3D_dll/*.dll'):
        shutil.copy(file, dest_dir)
        print "copy %s into %s" % (file, dest_dir)

    try:
        shutil.rmtree(outdir)
    except:
        import traceback
        traceback.print_exc()

def libfix_linux_conda(url="http://147.228.240.61/queetech/install/Skelet3D_so.zip"):
    outdir = download_and_unzip(url)

    dest_dir = os.path.join(get_conda_dir(), "lib")

    for file in glob.glob(r'Skelet3D_so/*.so'):
        shutil.copy(file, dest_dir)
        print "copy %s into %s" % (file, dest_dir)

    try:
        shutil.rmtree(outdir)
    except:
        import traceback
        traceback.print_exc()


def get_conda_dir():
    dstdir = ''
    try:
        import subprocess
        import re
        # cond info --root work only for root environment
        # p = subprocess.Popen(['conda', 'info', '--root'], stdout=subprocess.PIPE,  stderr=subprocess.PIPE)
        p = subprocess.Popen(['conda', 'info', '-e'], stdout=subprocess.PIPE,  stderr=subprocess.PIPE)
        out, err = p.communicate()

        import ipdb; ipdb.set_trace()
        dstdir = out.strip()
        dstdir = re.search("\*(.*)(\n|$)", dstdir).group(1).strip()
    except:
        import traceback
        traceback.print_exc()
        print 'out\n', out

    from os.path import expanduser
    home = expanduser("~")
    if op.isdir(dstdir):
        pass
    # elif op.isdir(op.join(home, "anaconda")):
    #     dstdir = op.join(home, "anaconda")
    # elif op.isdir(op.join(home, "miniconda")):
    #     dstdir = op.join(home, "miniconda")
    # elif op.isdir(op.join(home, "miniconda2")):
    #     dstdir = op.join(home, "miniconda2")
    # elif op.isdir("c:\miniconda2"):
    #     dstdir = "c:\miniconda2"
    # elif op.isdir("c:\miniconda"):
    #     dstdir = "c:\miniconda"
    # elif op.isdir("c:\anaconda2"):
    #     dstdir = "c:\anaconda2"
    # elif op.isdir("c:\anaconda"):
    #     dstdir = "c:\anaconda"
    else:
        print "Cannot find anaconda/miniconda directory"
        dstdir = None

    return dstdir

def main():
    libfix()

if '__main__' == __name__:
    main()
