"""
Type system conformance test for static type checkers.
"""

import os
from pathlib import Path
import sys
from time import time
from typing import Sequence

import tomli
import tomlkit

from reporting import generate_summary
from test_groups import get_test_cases, get_test_groups
from type_checker import TYPE_CHECKERS, TypeChecker


def run_tests(
    root_dir: Path,
    type_checker: TypeChecker,
    test_cases: Sequence[Path],
):
    print(f"Running tests for {type_checker.name}")

    test_start_time = time()
    tests_output = type_checker.run_tests([file.name for file in test_cases])
    test_duration = time() - test_start_time

    results_dir = root_dir / "results" / type_checker.name

    for test_case in test_cases:
        update_output_for_test(
            type_checker, results_dir, test_case, tests_output.get(test_case.name, "")
        )

    update_type_checker_info(type_checker, root_dir, test_duration)


def update_output_for_test(
    type_checker: TypeChecker,
    results_dir: Path,
    test_case: Path,
    output: str,
):
    test_name = test_case.stem
    output = f"\n{output}"

    results_file = results_dir / f"{test_name}.toml"
    results_file.parent.mkdir(parents=True, exist_ok=True)

    # Read the existing results file if present.
    try:
        with open(results_file, "rb") as f:
            existing_results = tomli.load(f)
    except FileNotFoundError:
        existing_results = {}

    old_output = existing_results.get("output", None)
    old_output = f"\n{old_output}"

    # Did the type checker output change since last time the
    # test was run?
    if old_output != output:
        print(f"Output changed for {test_name} when running {type_checker.name}")
        print(f"Old output: {old_output}")
        print(f"New output: {output}")
        print("")

        # Use multiline formatting for any strings that contain newlines.
        for key, value in existing_results.items():
            if isinstance(value, str) and "\n" in value:
                existing_results[key] = tomlkit.string(f"\n{value}", multiline=True)

        existing_results["output"] = tomlkit.string(output, multiline=True)

        results_file.parent.mkdir(parents=True, exist_ok=True)
        with open(results_file, "w") as f:
            tomlkit.dump(existing_results, f)


def update_type_checker_info(type_checker: TypeChecker, root_dir: Path, test_duration: float):
    # Record the version of the type checker used for the latest run.
    version_file = root_dir / "results" / type_checker.name / "version.toml"

    # Read the existing version file if present.
    try:
        with open(version_file, "rb") as f:
            existing_info = tomli.load(f)
    except FileNotFoundError:
        existing_info = {}

    existing_info["version"] = type_checker.get_version()
    existing_info["test_duration"] = test_duration

    version_file.parent.mkdir(parents=True, exist_ok=True)
    with open(version_file, "w") as f:
        tomlkit.dump(existing_info, f)


def main():
    # Some tests cover features that are available only in the
    # latest version of Python (3.12), so we need this version.
    assert sys.version_info >= (3, 12)

    root_dir = Path(__file__).resolve().parent.parent

    tests_dir = root_dir / "tests"
    assert tests_dir.is_dir()

    test_groups = get_test_groups(root_dir)
    test_cases = get_test_cases(test_groups, tests_dir)

    # Switch to the tests directory.
    os.chdir(tests_dir)

    # Run each test case with each type checker.
    for type_checker in TYPE_CHECKERS:
        if not type_checker.install():
            print(f'Skipping tests for {type_checker.name}')
        else:
            run_tests(root_dir, type_checker, test_cases)

    # Generate a summary report.
    generate_summary(root_dir)


if __name__ == "__main__":
    main()
