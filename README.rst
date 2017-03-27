===================
PEP 484: Type Hints
===================

This GitHub repo is used for development of the ``typing`` module
defined by PEP 484.  The module is available in Python since version
3.5.0 on a provisional basis until Python 3.7.0.

Authors
-------

* Guido van Rossum

* Jukka Lehtosalo

* Łukasz Langa

BDFL-Delegate
-------------

The BDFL-Delegate is Mark Shannon.  He was the final reviewer of PEP 484
and ultimately accepted it on May 22, 2014.

Important dates
---------------

* May 24, 2015: Python 3.5.0 beta 1 -- PEP 484 accepted, ``typing``
  checked into the CPython repo

* September 13, 2015: Python 3.5.0 final release; ``typing`` is
  available on a provisional basis

* December 23, 2016: Python 3.6.0 final release; ``typing`` stays
  provisional for the course of the 3.6 releases

* January 29, 2018: Python 3.7.0 beta 1, feature freeze for the release,
  including the ``typing`` module

* June 15, 2018: Python 3.7.0 final release, the ``typing`` module is no
  longer provisional

The dates for Python 3.7 are based on PEP 537 and may still change.

Important URLs
--------------

The python.org rendering of PEP 484 lives at
https://www.python.org/dev/peps/pep-0484/.

Two related informational PEPs exist:

* An explanation of the theory behind type hints can be found in
  https://www.python.org/dev/peps/pep-0483/.

* A literature review is at https://www.python.org/dev/peps/pep-0482/.

The python.org site automatically updates (with a slight delay,
typically in the order of 5-60 minutes) whenever the python/peps repo is
updated.

Workflow
--------

* The typing.py module and its unittests are edited in the src
  subdirectory of this repo. The python2 subdirectory contains the
  Python 2 backport.

* The PEPs 484, 483, and 482 are edited in the GitHub python/peps repo.

* Use the GitHub issue tracker for this repo to collect concerns and
  TO DO items for PEPs 484, 483, and 482 as well as for typing.py.

* Accumulate changes in the GitHub repo, closing issues as they are
  either decided and described in PEP 484, or implemented in
  typing.py, or both, as befits the issue.  (Some issues will be
  closed as "won't fix" after a decision is reached not to take
  action.)

* Make frequent small commits with clear descriptions. Preferably use
  a separate commit for each functional change, so the edit history is
  clear, merge conflicts are unlikely, and it's easy to roll back a
  change when further discussion reverts an earlier tentative decision
  that was already written up and/or implemented.

* Push to GitHub frequently.

* Pull from GitHub frequently, rebasing conflicts carefully (or
  merging, if a conflicting change was already pushed).

* At reasonable checkpoints: post current versions of PEPs
  to python-dev, making sure to update the
  Post-History header in python/peps repo. This is typically done by Guido.

Tracker labels
--------------

* bug: Needs to be fixed in typing.py.

* to do: Editing task for PEP 484 or for this repo.

* enhancement: Proposed new feature.

* postponed: Idea up for discussion.

* out of scope: Somebody else's problem.

Workflow for mypy changes
-------------------------

* Use the GitHub issue tracker for the mypy repo (python/mypy). The mypy
  core developers accept pull requests at their discretion.

* mypy uses ``typing.py`` from the available standard library when ran
  on Python 3.5+ and uses the `PyPI version
  <https://pypi.python.org/pypi/typing>`_ for older Python versions

* The full list of mypy issues marked as PEP 484 compatibility issues is
  here: https://github.com/python/mypy/labels/topic-pep-484

Workflow for CPython changes
----------------------------

* At Guido's discretion, he will from time to time copy typing.py and
  test_typing.py from the python/typing GitHub repo to the cpython repo.

* This process includes merging changes made directly in the cpython
  repo by other core developers.

* The changes are merged in three branches (3.5, 3.6, default) due to
  the module's provisional status.

Workflow for PyPI releases
--------------------------

* Run tests under all supported versions. As of March 2017 this includes
  2.7, 3.3, 3.4, 3.5, 3.6.

* On macOS, you can use `pyenv <https://github.com/pyenv/pyenv>`_ to
  manage multiple Python installations. Long story short:

  * ``xcode-select --install``
  * ``brew install pyenv``
  * ``echo 'eval "$(pyenv init -)"' >> ~/.bash_profile``
  * Open a new shell
  * ``pyenv install 3.5.3``
  * ``pyenv install 3.4.6``
  * ``pyenv install 3.3.6``
  * (assuming you already have 2.7.13 and 3.6.1 from Homebrew)
  * ``pyenv global system 3.5.3 3.4.6 3.3.6``

* You can use ``tox`` to automate running tests.

* Update the version number in ``setup.py``.

* Build a source distribution. Install it locally and test (if you
  were using ``tox``, you already tested source distributions).

* Run ``twine upload dist/typing-3.x.y.tar.gz``.
