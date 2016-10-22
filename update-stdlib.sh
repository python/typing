#!/bin/sh -xe

case $# in
    0) echo "Please supply a commit message as argument(s)"; exit 2;;
esac

HERE=$PWD

cd ~/src/cpython35
hg pull -u
cp $HERE/src/typing.py Lib/typing.py
cp $HERE/src/test_typing.py Lib/test/test_typing.py
hg ci -m "$@"

cd ~/src/cpython36
hg pull -u ../cpython35
hg merge 3.5
hg ci -m "$@ (3.5->3.6)"

cd ~/src/cpython37
hg pull -u ../cpython36
hg merge 3.6
hg ci -m "$@ (3.6->3.7)"
