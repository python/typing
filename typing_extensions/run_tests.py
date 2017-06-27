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

CORE_FILES = [
    "./src_py3/typing_extensions.py",
    "./src_py3/test_typing_extensions.py"
]
TEST_DIR = "test_data"


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
        test_version = tuple(map(int, version_number.split('.')))

        if sys.version_info[0] != test_version[0]:
            print("Skipping Python {}".format(version_number))
            continue
        else:
            print("Testing Python {}".format(version_number))

        with temp_copy(CORE_FILES, test_dir), change_directory(test_dir):
            success, output = run_shell("{} {} {}".format(
                sys.executable,
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
