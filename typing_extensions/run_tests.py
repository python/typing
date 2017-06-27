#!/usr/bin/env python

from typing import List, Iterator, Tuple
from contextlib import contextmanager
import glob
import os
import os.path
import shutil
import subprocess
import sys
import textwrap

CORE_FILES_2 = [
    "./src_py2/typing_extensions.py",
    "./src_py2/test_typing_extensions.py"
]
CORE_FILES_3 = [
    "./src_py3/typing_extensions.py",
    "./src_py3/test_typing_extensions.py"
]
TEST_DIR = "test_data"

if sys.platform.startswith('win32'):
    PYTHON2 = "py -2.7"
    PYTHON3 = "py -3.6"
else:
    PYTHON2 = "python"
    PYTHON3 = "python3"


def get_test_dirs() -> List[str]:
    """Get all folders to test inside TEST_DIR."""
    return list(glob.glob(os.path.join(TEST_DIR, "*")))


@contextmanager
def temp_copy(src_files: List[str], dest_dir: str) -> Iterator[None]:
    """
    A context manager that temporarily copies the given files to the
    given destination directory, and deletes those temp files upon
    exiting.
    """
    # Copy
    for src_path in src_files:
        shutil.copy(src_path, dest_dir)

    yield

    # Delete
    for src_path in src_files:
        dst_path = os.path.join(dest_dir, os.path.basename(src_path))
        os.remove(dst_path)


@contextmanager
def change_directory(dir_path: str) -> Iterator[None]:
    """
    A context manager that temporarily changes the working directory
    to the specified directory, and changes back to the original
    upon exiting.
    """
    original = os.getcwd()
    os.chdir(dir_path)

    yield

    os.chdir(original)


def run_shell(command: str) -> Tuple[bool, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = ":".join([os.getcwd(), env["PYTHONPATH"], env["PATH"]])
    out = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
        env=env)
    success = out.returncode == 0
    stdout = '' if out.stdout is None else out.stdout.decode('utf-8')
    return (success, stdout)


def main() -> int:
    test_dirs = get_test_dirs()
    exit_code = 0
    for test_dir in test_dirs:
        _, version_number = test_dir.split('-')
        py2 = version_number.startswith("2")
        print("Testing Python {}".format(version_number))

        core_files = CORE_FILES_2 if py2 else CORE_FILES_3
        python_exe = PYTHON2 if py2 else PYTHON3

        with temp_copy(core_files, test_dir), change_directory(test_dir):
            success, output = run_shell("{} {} {}".format(
                python_exe,
                "test_typing_extensions.py",
                "PYVERSION.{}".format(version_number)))
            if success:
                print("   All tests passed!")
            else:
                print(textwrap.indent(output, "    "))
                exit_code = 1
    return exit_code


if __name__ == '__main__':
    sys.exit(main())
