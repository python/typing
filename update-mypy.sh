#!/bin/sh -xe

case $# in
    0) echo "Please supply a commit message as argument(s)"; exit 2;;
esac

HERE=$PWD

cd ~/src/mypy
git co master
git pull

cp $HERE/src/typing.py lib-typing/3.2/typing.py
cp $HERE/src/test_typing.py lib-typing/3.2/test_typing.py

cp $HERE/python2/typing.py lib-typing/2.7/typing.py
cp $HERE/python2/test_typing.py lib-typing/2.7/test_typing.py

git ci lib-typing -m "$@"
