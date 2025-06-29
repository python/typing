"""
Type system conformance test for static type checkers.
"""

import os
from pathlib import Path
import re
import sys
from time import time
from typing import Sequence

import tomli
import tomlkit

from options import parse_options
from reporting import generate_summary
from test_groups import get_test_cases, get_test_groups
from type_checker import TYPE_CHECKERS, TypeChecker


def run_tests(
    root_dir: Path,
    type_checker: TypeChecker,
    test_cases: Sequence[Path],
    skip_timing: bool = False,
):
    print(f"Running tests for {type_checker.name}")

    test_start_time = time()
    tests_output = type_checker.run_tests([file.name for file in test_cases])
    test_duration = time() - test_start_time

    for _, output in tests_output.items():
        type_checker.parse_errors(output.splitlines())

    results_dir = root_dir / "results" / type_checker.name

    for test_case in test_cases:
        update_output_for_test(
            type_checker, results_dir, test_case, tests_output.get(test_case.name, "")
        )

    update_type_checker_info(type_checker, root_dir, test_duration, skip_timing=skip_timing)


def get_expected_errors(test_case: Path) -> tuple[
    dict[int, tuple[int, int]],
    dict[str, tuple[list[int], bool]],
]:
    """Return the line numbers where type checkers are expected to produce an error.

    The return value is a tuple of two dictionaries:
    - The format of the first is {line number: (number of required errors, number of optional errors)}.
    - The format of the second is {error tag: ([lines where the error may appear], allow multiple}.
      If allow multiple is True, the error may appear on multiple lines; otherwise, it must
      appear exactly once.

    For example, the following test case:

        x: int = "x"  # E
        y: int = "y"  # E?
        @final  # E[final]
        def f(): pass  # E[final]

    will return:

        (
            {1: (1, 0), 2: (0, 1)},
            {"final": ([3, 4], False)}
        )
    """
    with open(test_case, "r", encoding="utf-8") as f:
        lines = f.readlines()
    output: dict[int, tuple[int, int]] = {}
    groups: dict[str, tuple[list[int], bool]] = {}
    for i, line in enumerate(lines, start=1):
        line_without_comment, *_ = line.split("#")
        # Ignore lines with no non-comment content. This allows commenting out test cases.
        if not line_without_comment.strip():
            continue
        required = 0
        optional = 0
        for match in re.finditer(r"# E\??(?=:|$| )", line):
            if match.group() == "# E":
                required += 1
            else:
                optional += 1
        if required or optional:
            output[i] = (required, optional)
        for match in re.finditer(r"# E\[([^\]]+)\]", line):
            tag = match.group(1)
            if tag.endswith("+"):
                allow_multiple = True
                tag = tag[:-1]
            else:
                allow_multiple = False
            if tag not in groups:
                groups[tag] = ([i], allow_multiple)
            else:
                if groups[tag][1] != allow_multiple:
                    raise ValueError(f"Error group {tag} has inconsistent allow_multiple value in {test_case}")
                groups[tag][0].append(i)
    for group, linenos in groups.items():
        if len(linenos) == 1:
            raise ValueError(f"Error group {group} only appears on a single line in {test_case}")
    return output, groups


def diff_expected_errors(
    type_checker: TypeChecker,
    test_case: Path,
    output: str,
    ignored_errors: Sequence[str],
) -> str:
    """Return a list of errors that were expected but not produced by the type checker."""
    expected_errors, error_groups = get_expected_errors(test_case)
    errors = type_checker.parse_errors(output.splitlines())
    if ignored_errors:
        errors = {
            lineno: [
                error
                for error in errors_list
                if not any(ignored in error for ignored in ignored_errors)]
            for lineno, errors_list in errors.items()
        }
        errors = {lineno: errors_list for lineno, errors_list in errors.items() if errors_list}

    differences: list[str] = []
    for expected_lineno, (expected_count, _) in expected_errors.items():
        if expected_lineno not in errors and expected_count > 0:
            differences.append(f"Line {expected_lineno}: Expected {expected_count} errors")
        # We don't report an issue if the count differs, because type checkers may produce
        # multiple error messages for a single line.
    linenos_used_by_groups: set[int] = set()
    for group, (linenos, allow_multiple) in error_groups.items():
        num_errors = sum(1 for lineno in linenos if lineno in errors)
        if num_errors == 0:
            differences.append(f"Lines {', '.join(map(str, linenos))}: Expected error (tag {group!r})")
        elif num_errors == 1 or allow_multiple:
            linenos_used_by_groups.update(linenos)
        else:
            differences.append(f"Lines {', '.join(map(str, linenos))}: Expected exactly one error (tag {group!r})")
    for actual_lineno, actual_errors in errors.items():
        if actual_lineno not in expected_errors and actual_lineno not in linenos_used_by_groups:
            differences.append(f"Line {actual_lineno}: Unexpected errors {actual_errors}")
    return "".join(f"{diff}\n" for diff in differences)


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
    should_write = False

    # Read the existing results file if present.
    try:
        with open(results_file, "rb") as f:
            existing_results = tomli.load(f)
    except FileNotFoundError:
        should_write = True
        existing_results = {}
    except tomli.TOMLDecodeError:
        print(f"Error decoding {results_file}")
        existing_results = {}

    ignored_errors = existing_results.get("ignore_errors", [])
    errors_diff = "\n" + diff_expected_errors(type_checker, test_case, output, ignored_errors)
    old_errors_diff = "\n" + existing_results.get("errors_diff", "")

    if errors_diff != old_errors_diff:
        should_write = True
        print(f"Result changed for {test_name} when running {type_checker.name}")
        print(f"Old output: {old_errors_diff}")
        print(f"New output: {errors_diff}")
        print("")

    conformance_automated = "Fail" if errors_diff.strip() else "Pass"
    if existing_results.get("conformance_automated") != conformance_automated:
        should_write = True
        existing_results["conformance_automated"] = conformance_automated

    old_output = existing_results.get("output", "")
    old_output = f"\n{old_output}"

    # Did the type checker output change since last time the
    # test was run?
    if old_output != output:
        should_write = True
        print(f"Output changed for {test_name} when running {type_checker.name}")
        print(f"Old output: {old_output}")
        print(f"New output: {output}")
        print("")

        # Use multiline formatting for any strings that contain newlines.
        for key, value in existing_results.items():
            if isinstance(value, str) and "\n" in value:
                existing_results[key] = tomlkit.string(f"\n{value}", multiline=True)

    if should_write:
        # Always reapply tomlkit.string, or it will turn into a single line.
        existing_results["errors_diff"] = tomlkit.string(errors_diff, multiline=True)
        existing_results["output"] = tomlkit.string(output, multiline=True)
        if "notes" in existing_results:
            notes = existing_results["notes"]
            if not notes.startswith("\n"):
                notes = "\n" + notes
            existing_results["notes"] = tomlkit.string(notes, multiline=True)
        results_file.parent.mkdir(parents=True, exist_ok=True)
        with open(results_file, "w", encoding="utf-8") as f:
            tomlkit.dump(existing_results, f)


def update_type_checker_info(
    type_checker: TypeChecker, root_dir: Path, test_duration: float, skip_timing: bool = False
):
    # Record the version of the type checker used for the latest run.
    version_file = root_dir / "results" / type_checker.name / "version.toml"

    # Read the existing version file if present.
    try:
        with open(version_file, "rb") as f:
            existing_info = tomli.load(f)
    except FileNotFoundError:
        existing_info = {}
    except tomli.TOMLDecodeError:
        print(f"Error decoding {version_file}")
        existing_info = {}

    existing_info["version"] = type_checker.get_version()
    if not skip_timing:
        existing_info["test_duration"] = round(test_duration, 1)

    version_file.parent.mkdir(parents=True, exist_ok=True)
    with open(version_file, "w") as f:
        tomlkit.dump(existing_info, f)


def main():
    # Some tests cover features that are available only in the
    # latest version of Python (3.12), so we need this version.
    assert sys.version_info >= (3, 12)

    options = parse_options(sys.argv[1:])

    root_dir = Path(__file__).resolve().parent.parent

    if not options.report_only:
        tests_dir = root_dir / "tests"
        assert tests_dir.is_dir()

        test_groups = get_test_groups(root_dir)
        test_cases = get_test_cases(test_groups, tests_dir)

        # Switch to the tests directory.
        os.chdir(tests_dir)

        # Run each test case with each type checker.
        for type_checker in TYPE_CHECKERS:
            if not type_checker.install():
                print(f"Skipping tests for {type_checker.name}")
            else:
                run_tests(root_dir, type_checker, test_cases, skip_timing=options.skip_timing)

    # Generate a summary report.
    generate_summary(root_dir)


if __name__ == "__main__":
    main()
