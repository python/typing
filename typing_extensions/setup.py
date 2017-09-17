#!/usr/bin/env python
# coding: utf-8

import sys
from distutils.core import setup

if sys.version_info < (2, 7, 0) or (3, 0, 0) <= sys.version_info < (3, 3, 0):
    sys.stderr.write('ERROR: You need Python 2.7 or 3.3+ '
                     'to install the typing package.\n')
    exit(1)

version = '3.6.2'
description = 'Backported and Experimental Type Hints for Python 3.5+'
long_description = '''\
Typing Extensions -- Backported and Experimental Type Hints for Python

The ``typing`` module was added to the standard library in Python 3.5 on
a provisional basis and will no longer be provisional in Python 3.7. However,
this means users of Python 3.5 - 3.6 who are unable to upgrade will not be
able to take advantage of new types added to the ``typing`` module, such as
``typing.Text`` or ``typing.Coroutine``.

The ``typing_extensions`` module contains both backports of these changes
as well as experimental types that will eventually be added to the ``typing``
module, such as ``Protocol``.

Users of other Python versions should continue to install and use
the ``typing`` module from PyPi instead of using this one unless specifically
writing code that must be compatible with multiple Python versions or requires
experimental types.
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
    install_requires.append('typing >= 3.6.2')

setup(name='typing_extensions',
      version=version,
      description=description,
      long_description=long_description,
      author='Guido van Rossum, Jukka Lehtosalo, Lukasz Langa, Michael Lee',
      author_email='levkivskyi@gmail.com',
      url='https://github.com/python/typing',
      license='PSF',
      keywords='typing function annotations type hints hinting checking '
               'checker typehints typehinting typechecking backport',
      package_dir={'': package_dir},
      py_modules=['typing_extensions'],
      classifiers=classifiers,
      install_requires=install_requires)
