#!/usr/bin/env python
# coding: utf-8

import sys
from distutils.core import setup

if sys.version_info < (2, 7, 0) or (3, 0, 0) <= sys.version_info < (3, 3, 0):
    sys.stderr.write('ERROR: You need Python 2.7 or 3.3+ '
                     'to install the typing package.\n')
    exit(1)

version = '3.6.1'
description = 'Backported and Experimental Type Hints for Python 3.5+'
long_description = '''\
Typing Extensions -- Backported and Experimental Type Hints for Python

This module contains both backports of changes made to the ``typing``
module since Python 3.5.0 as well as experimental types that will be
eventually added to the ``typing`` module once stabilized.

This module is intended to be used by people who:

1. Are using Python 3.5+ and cannot upgrade to newer versions of Python.
   Since the ``typing`` module was (provisionally) added to the Python standard
   library in 3.5, users who are unable to upgrade cannot take advantage of
   new additions to typing such as ``typing.Text`` or ``typing.Coroutine``.
2. Are interested in using experimental additions to the ``typing`` module.

Users of other Python versions should continue to install and use
use the ``typing`` module from PyPi instead of using this one unless
specifically writing code that must be compatible with multiple Python
versions or requires experimental types.
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
