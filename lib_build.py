# coding: utf-8
from os import path
from shutil import copy2 as copy
import sys

def libfile(sourcedir, libname):
    lfname = path.join(sourcedir, libname + '.pcl')
    if not path.isfile(lfname):
        raise NameError('library module not found: ' + libname)
    return lfname

if __name__=='__main__':
    source = sys.argv[1]
    dest = sys.argv[2]
    utilsets = sys.argv[3:]
    if 'parameters' in utilsets and 'string' not in utilsets:
        utilsets.append('string')
    for lib in utilsets:
        copy(libfile(source, lib), dest)
