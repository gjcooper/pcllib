# coding: utf-8
import os
import argparse
import re

deploy_hdr = '''# IMPORTANT NOTICE
# --------------------------------
# This pcl file has been deployed from
# the pcllib package available at:
# https://github.com/gjcooper/pcllib
#
# Note, it will attempt to add itself
# to any .gitignore file found, and thus
# any local edits to it may not be saved
# to your local repository.
#
# To add features to the pcllib files
# add them in the source directory and
# consider creating a pull request in github.
# ---------------------------------
'''

__version__ = '0.0.1'
__package__ = 'pcllib'


def check_for_includes(pclfile):
    with open(pclfile, 'r') as fileobj:
        pclcode = fileobj.read()
    expr = r'include(?:_one)??\s*"(.*)??\.pcl"'
    return re.findall(expr, pclcode)


def augment_libraries(src_dir, libs_selected):
    final_libs = set()
    for lib in libs_selected:
        final_libs.add(libfile(src_dir, lib))
    processed = 0
    while (len(final_libs) > processed):
        new_libs = set()
        for lib in final_libs:
            for include in check_for_includes(lib):
                new_libs.add(include)
        processed = len(final_libs)
        for new in new_libs:
            final_libs.add(libfile(src_dir, new))
    return final_libs


def append_if_exists(path, flags):
    return os.open(path, os.O_APPEND | os.O_WRONLY)


def deploy():
    parser = argparse.ArgumentParser(description='{} - deploy {} - Deploy pcl files to a project directory'.format(__package__, __version__))
    parser.add_argument('destination', help='The directory to deploy pcl file[s] to')
    parser.add_argument('libraries', help='The pcl libraries to send to the destination', nargs='+')
    parser.add_argument('--source-dir', '-s', help='For an alternate source directory')
    parser.add_argument('--version', action='version', version='deploy {}'.format(__version__))

    args = parser.parse_args()

    # Check and/or set source directory
    if not args.source_dir:
        args.source_dir = os.getcwd()
    elif not os.path.isdir(args.source_dir):
        print('Source directory: {source_dir} not found'.format(**vars(args)))
        return

    # Check destination directory
    if not os.path.isdir(args.destination):
        print('Destination directory {destination} not found'.format(**vars(args)))
        return

    # Augment libraries if includes found in files
    try:
        final_libs = augment_libraries(args.source_dir, args.libraries)
    except NameError as nerr:
        print(nerr)
        return

    # Send the needed libraries to the destination directory
    for lib in final_libs:
        name = os.path.basename(lib)
        try:
            with open(os.path.join(args.destination, name), 'x') as destfile:
                with open(lib, 'r') as srcfile:
                    destfile.write(deploy_hdr + srcfile.read())
        except FileExistsError:
            print('{} already found in destination directory, ignoring...'.format(name))
    gitignore = os.path.join(args.destination, '.gitignore')
    try:
        with open(gitignore, 'a+', opener=append_if_exists) as ignore_file:
            ignore_file.write('\n# Added auomatically by lib_build.py' + '\n'.join(['/' + os.path.basename(f) for f in final_libs]))
    except IOError as e:
        print(e)
        print('WARNING: .gitignore file not found: {}'.format(os.path.join(args.destination, '.gitignore')))
        pass


def libfile(sourcedir, libname):
    lfname = os.path.join(sourcedir, libname + '.pcl')
    if not os.path.isfile(lfname):
        raise NameError('library module not found: ' + libname)
    return lfname


if __name__ == '__main__':
    deploy()
