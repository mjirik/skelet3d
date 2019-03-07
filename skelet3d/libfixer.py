#! /usr/bin/python
# -*- coding: utf-8 -*-


import logging
logger = logging.getLogger(__name__)

import zipfile
import glob
import shutil
import os
import os.path as op
import stat
import tempfile
import sys
if sys.version_info < (3, 0):
    import urllib as urllibr
else:
    import urllib.request as urllibr

def download_and_unzip(url):
    # try:
    #     import pywget
    # except:
    #     import wget as pywget
    outdir = tempfile.gettempdir()
    # print("temp directory ", outdir)
    outdir = tempfile.mkdtemp()
    # there is problem with wget. It uses its ouwn tempfile in current dir. It is not sure that there will
    # be requred permisson for write
    filename = op.join(outdir, "skelet3d.zip")
    urllibr.urlretrieve(url, filename)
    # filename = pywget.download(url, out=filename)


    zf = zipfile.ZipFile(filename)
    zf.extractall()
    zf.close()
    return outdir

def libfix(url="http://147.228.240.61/queetech/install/ITK%2bSkelet3D_dll.zip"):
    if sys.platform.startswith('win'):
        print("Trying to download .dll libraries")
        libfix_windows()
    if sys.platform.startswith('linux'):
        print("Trying to download .so libraries")
        libfix_linux_conda()

def get_conda_dir():
    """
    Get conda base dir.
    I would remove envs subdirs from output dir.

    :return:
    """
    if sys.version_info.major == 2:
        conda_dir = get_conda_dir_old()
    else:
        conda_dir = sys.exec_prefix
    idx = conda_dir.find("envs")
    if idx > 0:
        conda_dir = conda_dir[:idx]
    return conda_dir

# def libfix_windows(url="http://147.228.240.61/queetech/install/ITK%2bSkelet3D_dll.zip"):
def libfix_windows(url="http://home.zcu.cz/~mjirik/lisa/install/ITK%2bSkelet3D_dll.zip"):
    outdir = download_and_unzip(url)

    dest_dir = get_conda_dir()

    for file in glob.glob(r'ITK+Skelet3D_dll/*.dll'):
        shutil.copy(file, dest_dir)
        print("copy %s ---> %s" % (file, dest_dir))

    try:
        shutil.rmtree(outdir)
    except:
        import traceback
        traceback.print_exc()

def __chmod(filename):
    """
    Make file for all
    :param filename:
    :return:
    """

    if sys.platform.startswith('win'):
        pass
    else:
        os.chmod(
            filename,
            stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH |
            stat.S_IRUSR | stat.S_IRGRP | stat.S_IXOTH |
            stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH
        )

def __chown(filename):
    """
    Make file owned by the user
    :param filename:
    :return:
    """
    if sys.platform.startswith('win'):
        return
    os.chown(filename, int(os.getenv('SUDO_UID')), int(os.getenv('SUDO_GID')))

def __demote(user_uid, user_gid):
    """
    set normal user to the process
    :param user_uid:
    :param user_gid:
    :return:
    """
    def result():
        print('starting demotion')
        os.setgid(user_gid)
        os.setuid(user_uid)
        print('finished demotion')
    return result

def __make_non_sudo():
    demote_fun = None
    if os.getuid() == 0:
        uid = int(os.getenv('SUDO_UID'))
        gid = int(os.getenv('SUDO_GID'))
        print("__make_non_sudo ", gid, uid)
        return __demote(uid, gid)
    else:
        return None


# def libfix_linux_conda(url="http://147.228.240.61/queetech/install/Skelet3D_so.zip"):
def libfix_linux_conda(url="http://home.zcu.cz/~mjirik/lisa/install/Skelet3D_so.zip"):
    # linux_copy_to_conda_dir(url)
    if os.getuid() != 0:
        print("please run with sudo")
    outdir = download_and_unzip(url)
    dest_dir = "/usr/local/lib"
    dest_dir_conda_lib = os.path.join(get_conda_dir(), "lib")

    for file in glob.glob(r'Skelet3D_so/*Cxx*.so'):
        # chmod is not necessary
        # __chmod(file)

        shutil.copy(file, dest_dir)
        print("copy %s ---> %s" % (file, dest_dir))
        shutil.copy(file, dest_dir_conda_lib)
        print("copy %s ---> %s" % (file, dest_dir_conda_lib))
        fhead, fteil = os.path.split(file)
        dest_file = os.path.join(dest_dir_conda_lib, fteil)
        __chown(dest_file)

    try:
        shutil.rmtree(outdir)
    except:
        import traceback
        traceback.print_exc()

def linux_copy_to_conda_dir(url):
    """
    This is not working.
    There are some problems with LD_LIBRARY_PATH

    :param url:
    :return:
    """
    outdir = download_and_unzip(url)

    dest_dir_conda_lib = os.path.join(get_conda_dir(), "lib")

    for file in glob.glob(r'Skelet3D_so/*Cxx*.so'):
        shutil.copy(file, dest_dir_conda_lib)
        print("copy %s into %s" % (file, dest_dir_conda_lib))

    try:
        shutil.rmtree(outdir)
    except:
        import traceback
        traceback.print_exc()


def _find_conda_dir_with_conda():
    dstdir = ''
    try:
        import subprocess
        import re
        # cond info --root work only for root environment
        # p = subprocess.Popen(['conda', 'info', '--root'], stdout=subprocess.PIPE,  stderr=subprocess.PIPE)
        p = subprocess.Popen(['conda', 'info', '-e'], stdout=subprocess.PIPE,  stderr=subprocess.PIPE) #, preexec_fn=__make_non_sudo())
        out, err = p.communicate()

        # import ipdb; ipdb.set_trace()
        dstdir = out.decode("utf8").strip()
        dstdir = re.search("\*(.*)(\n|$)", dstdir).group(1).strip()
    except:
        import traceback
        traceback.print_exc()
    return dstdir


def get_conda_dir_old():
    logger.warning("Function get_conda_dir_old is obsolete and will be removed.")
    dstdir = ""
    if sys.platform.startswith('win'):
        dstdir = _find_conda_dir_with_conda()
    else:
        # osx or linux
        # if sudo is used, conda is not in path and process will fail
        if os.getuid() != 0:
            dstdir = _find_conda_dir_with_conda()

    from os.path import expanduser
    home = expanduser("~")
    if op.isdir(dstdir):
        pass
    elif op.isdir(op.join(home, "anaconda")):
        dstdir = op.join(home, "anaconda")
    elif op.isdir(op.join(home, "miniconda")):
        dstdir = op.join(home, "miniconda")
    elif op.isdir(op.join(home, "miniconda2")):
        dstdir = op.join(home, "miniconda2")
    elif op.isdir(op.join(home, "miniconda3")):
        dstdir = op.join(home, "miniconda3")
    elif op.isdir("c:\miniconda2"):
        dstdir = "c:\miniconda2"
    elif op.isdir("c:\miniconda3"):
        dstdir = "c:\miniconda3"
    elif op.isdir("c:\miniconda"):
        dstdir = "c:\miniconda"
    elif op.isdir(r"c:\anaconda2"):
        dstdir = r"c:\anaconda2"
    elif op.isdir(r"c:\anaconda3"):
        dstdir = r"c:\anaconda3"
    elif op.isdir(r"c:\anaconda"):
        dstdir = r"c:\anaconda"
    else:
        print("Cannot find anaconda/miniconda directory")
        dstdir = None

    return dstdir

def main():
    libfix()

if '__main__' == __name__:
    main()
