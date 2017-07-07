#!/usr/bin/env python
# coding: utf-8

import sys
from distutils.core import setup

if sys.version_info < (2, 7, 0) or (3, 0, 0) <= sys.version_info < (3, 3, 0):
    sys.stderr.write('ERROR: You need Python 2.7 or 3.3+ '
                     'to install the typing package.\n')
    exit(1)

version = '3.6.1'
description = 'Type Hint backports for Python 3.5+'
long_description = '''\
Typing -- Type Hints for Python

This is a backport of the 'typing' module, which was provisionally added
to the standard library in Python 3.5. The typing module has seen
several changes since it was first added in Python 3.5.0, which means
people who are using 3.5+ but are unable to upgrade to the latest
version of Python cannot take advantage of some new features of the
typing library, such as typing.Type or typing.Coroutine.

This module allows those users to use the latest additions to the typing
module without worrying about naming conflicts with the standard library.
Users of Python 2.7, 3.3, and 3.4 should install the typing module
from PyPi and use that directly, except when writing code that needs to
be compatible across multiple versions of Python.
'''

classifiers = [
    'Development Status :: 3 - Alpha',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: Python Software Foundation License',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Topic :: Software Development',
]

if sys.version_info.major == 2:
    package_dir = 'src_py2'
elif sys.version_info.major == 3:
    package_dir = 'src_py3'
else:
    raise AssertionError()

install_requires = []
if sys.version_info < (3, 5):
    install_requires.append('typing >= 3.6.1')

setup(name='typing_extensions',
      version=version,
      description=description,
      long_description=long_description,
      author='Guido van Rossum, Jukka Lehtosalo, Lukasz Langa, Michael Lee',
      author_email='jukka.lehtosalo@iki.fi',
      url='https://github.com/python/typing',
      license='PSF',
      keywords='typing function annotations type hints hinting checking '
               'checker typehints typehinting typechecking backport',
      package_dir={'': package_dir},
      py_modules=['typing_extensions'],
      classifiers=classifiers,
      install_requires=install_requires)
