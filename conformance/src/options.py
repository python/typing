"""
Command-line options for the test tool.
"""

import argparse
from dataclasses import dataclass

from type_checker import TYPE_CHECKERS


@dataclass
class _Options:
    report_only: bool | None
    only_run: str | None
    skip_install_check: bool | None


def parse_options(argv: list[str]) -> _Options:
    parser = argparse.ArgumentParser()
    reporting_group = parser.add_argument_group("reporting")
    reporting_group.add_argument(
        "--report-only",
        action="store_true",
        help="regenerates the test suite report from past results",
    )
    reporting_group.add_argument(
        "--only-run",
        help="Only runs the type checker",
        choices=[tc.name for tc in TYPE_CHECKERS],
    )
    reporting_group.add_argument(
        "--skip-install-check",
        action="store_true",
        help="Skips the check for whether type checkers are installed",
    )

    ret = _Options(**vars(parser.parse_args(argv)))
    return ret
