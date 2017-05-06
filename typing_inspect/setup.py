#!/usr/bin/env python

# NOTE: This package must support Python 2.7 in addition to Python 3.x

from distutils.core import setup

version = '0.1.0-dev'
description = 'Runtime inspection utilities for typing module.'
long_description = '''
Typing Inspect
==============

The "typing_inspect" module defines experimental API for runtime
inspection of types defined in the standard "typing" module.
'''.lstrip()

classifiers = [
    'Development Status :: 3 - Alpha',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: Python Software Foundation License',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Topic :: Software Development',
]

setup(
    name='typing_inspect',
    version=version,
    description=description,
    long_description=long_description,
    author='Ivan Levkivskyi',
    author_email='levkivskyi@gmail.com',
    url='https://github.com/python/typing',
    license='PSF',
    keywords='typing function annotations type hints hinting checking '
             'checker typehints typehinting typechecking inspect reflection',
    py_modules=['typing_inspect'],
    classifiers=classifiers,
)
