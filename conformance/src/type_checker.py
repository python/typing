"""
Classes that abstract differences between type checkers.
"""

from abc import ABC, abstractmethod
import json
from pathlib import Path
import os
import re
import shutil
from subprocess import PIPE, CalledProcessError, run
import sys
from typing import Sequence


class TypeChecker(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """
        Returns the name of the type checker.
        """
        raise NotImplementedError

    @abstractmethod
    def install(self) -> bool:
        """
        Ensures that the latest version of the type checker is installed.
        Returns False if installation fails.
        """
        raise NotImplementedError

    @abstractmethod
    def get_version(self) -> str:
        """
        Returns the current version string for the type checker.
        """
        raise NotImplementedError

    @abstractmethod
    def run_tests(self, test_files: Sequence[str]) -> dict[str, str]:
        """
        Runs the type checker on the specified test file and
        returns the output.
        """
        raise NotImplementedError

    @abstractmethod
    def parse_errors(self, output: Sequence[str]) -> dict[int, list[str]]:
        """
        Parses type checker output to summarize the lines on which errors occurred.
        """
        raise NotImplementedError


class MypyTypeChecker(TypeChecker):
    @property
    def name(self) -> str:
        return "mypy"

    def install(self) -> bool:
        try:
            # Delete the cache for consistent timings.
            shutil.rmtree(".mypy_cache")
        except (shutil.Error, OSError):
            # Ignore any errors here.
            pass

        try:
            # Uninstall any existing version if present.
            run(
                [sys.executable, "-m", "pip", "uninstall", "mypy", "-y"],
                check=True,
            )

            # Install the latest version.
            run(
                [sys.executable, "-m", "pip", "install", "mypy"],
                check=True,
            )

            # Run "mypy --version" to ensure that it's installed and to work
            # around timing issues caused by malware scanners on some systems.
            self.get_version()

            return True
        except CalledProcessError:
            print("Unable to install mypy")
            return False

    def get_version(self) -> str:
        proc = run([sys.executable, "-m", "mypy", "--version"], stdout=PIPE, text=True)
        version = proc.stdout.strip()

        # Remove the " (compiled)" if it's present.
        version = version.split(" (")[0]
        return version

    def run_tests(self, test_files: Sequence[str]) -> dict[str, str]:
        command = [
            sys.executable,
            "-m",
            "mypy",
            ".",
            "--disable-error-code",
            "empty-body",
            "--enable-error-code",
            "deprecated",
        ]
        proc = run(command, stdout=PIPE, text=True, encoding="utf-8")
        lines = proc.stdout.split("\n")

        # Add results to a dictionary keyed by the file name.
        results_dict: dict[str, str] = {}
        for line in lines:
            file_name = line.split(":")[0].strip()
            results_dict[file_name] = results_dict.get(file_name, "") + line + "\n"

        return results_dict

    def parse_errors(self, output: Sequence[str]) -> dict[int, list[str]]:
        # narrowing_typeguard.py:102: error: TypeGuard functions must have a positional argument  [valid-type]
        line_to_errors: dict[int, list[str]] = {}
        for line in output:
            if line.count(":") < 3:
                continue
            _, lineno, kind, _ = line.split(":", maxsplit=3)
            kind = kind.strip()
            if kind != "error":
                continue
            line_to_errors.setdefault(int(lineno), []).append(line)
        return line_to_errors


class PyrightTypeChecker(TypeChecker):
    @property
    def name(self) -> str:
        return "pyright"

    def install(self) -> bool:
        try:
            # Uninstall any old version if present.
            run(
                [sys.executable, "-m", "pip", "uninstall", "pyright", "-y"],
                check=True,
            )

            # Install the latest version.
            run(
                [sys.executable, "-m", "pip", "install", "pyright"],
                check=True,
            )

            # Force the Python wrapper to install node if needed
            # and download the latest version of pyright.
            self.get_version()
            return True
        except CalledProcessError:
            print("Unable to install pyright")
            return False

    def get_version(self) -> str:
        proc = run(
            [sys.executable, "-m", "pyright", "--version"], stdout=PIPE, text=True
        )
        return proc.stdout.strip()

    def run_tests(self, test_files: Sequence[str]) -> dict[str, str]:
        command = [sys.executable, "-m", "pyright", ".", "--outputjson"]
        proc = run(command, stdout=PIPE, text=True, encoding="utf-8")
        output_json = json.loads(proc.stdout)
        diagnostics = output_json["generalDiagnostics"]

        # Add results to a dictionary keyed by the file name.
        results_dict: dict[str, str] = {}
        for diagnostic in diagnostics:
            file_path = Path(diagnostic.get("file", ""))
            file_name = file_path.name
            line_number = diagnostic["range"]["start"]["line"] + 1
            col_number = diagnostic["range"]["start"]["character"] + 1
            severity = diagnostic["severity"]
            message = diagnostic["message"]
            rule = f" ({diagnostic['rule']})" if "rule" in diagnostic else ""

            line_text = f"{file_name}:{line_number}:{col_number} - {severity}: {message}{rule}\n"
            results_dict[file_name] = results_dict.get(file_name, "") + line_text

        return results_dict

    def parse_errors(self, output: Sequence[str]) -> dict[int, list[str]]:
        # narrowing_typeguard.py:102:9 - error: User-defined type guard functions and methods must have at least one input parameter (reportGeneralTypeIssues)
        line_to_errors: dict[int, list[str]] = {}
        for line in output:
            # Ignore indented notes
            if not line or line[0].isspace():
                continue
            assert line.count(":") >= 3, f"Failed to parse line: {line!r}"
            _, lineno, kind, _ = line.split(":", maxsplit=3)
            kind = kind.split()[-1]
            if kind not in ("error", "warning"):
                continue
            line_to_errors.setdefault(int(lineno), []).append(line)
        return line_to_errors


class PyreTypeChecker(TypeChecker):
    @property
    def name(self) -> str:
        return "pyre"

    def install(self) -> bool:
        try:
            # Delete the cache for consistent timings.
            shutil.rmtree(".pyre")
        except (shutil.Error, OSError):
            # Ignore any errors here.
            pass

        try:
            # Uninstall any existing version if present.
            run(
                [sys.executable, "-m", "pip", "uninstall", "pyre-check", "-y"],
                check=True,
            )

            # Install the latest version.
            run(
                [sys.executable, "-m", "pip", "install", "pyre-check"],
                check=True,
            )

            # Generate a default config file.
            pyre_config = '{"site_package_search_strategy": "pep561", "source_directories": ["."]}\n'
            with open(".pyre_configuration", "w") as f:
                f.write(pyre_config)

            return True
        except CalledProcessError:
            print("Unable to install pyre")
            return False

    def get_version(self) -> str:
        proc = run(["pyre", "--version"], stdout=PIPE, text=True)
        version = proc.stdout.strip()
        version = version.replace("Client version:", "pyre")
        return version

    def run_tests(self, test_files: Sequence[str]) -> dict[str, str]:
        proc = run(["pyre", "check"], stdout=PIPE, text=True, encoding="utf-8")
        lines = proc.stdout.split("\n")

        # Add results to a dictionary keyed by the file name.
        results_dict: dict[str, str] = {}
        for line in lines:
            file_name = line.split(":")[0].strip()
            results_dict[file_name] = results_dict.get(file_name, "") + line + "\n"

        return results_dict

    def parse_errors(self, output: Sequence[str]) -> dict[int, list[str]]:
        # narrowing_typeguard.py:17:33 Incompatible parameter type [6]: In call `typing.GenericMeta.__getitem__`, for 1st positional argument, expected `Type[Variable[_T_co](covariant)]` but got `Tuple[Type[str], Type[str]]`.
        line_to_errors: dict[int, list[str]] = {}
        for line in output:
            # Ignore multi-line errors
            if ".py:" not in line and ".pyi:" not in line:
                continue
            # Ignore reveal_type errors
            if "Revealed type [-1]" in line:
                continue
            assert line.count(":") >= 2, f"Failed to parse line: {line!r}"
            _, lineno, _ = line.split(":", maxsplit=2)
            line_to_errors.setdefault(int(lineno), []).append(line)
        return line_to_errors

class ZubanLSTypeChecker(MypyTypeChecker):
    @property
    def name(self) -> str:
        return "zuban"

    def install(self) -> bool:
        try:
            # Uninstall any existing version if present.
            run(
                [sys.executable, "-m", "pip", "uninstall", "zuban", "-y"],
                check=True,
            )

            # Install the latest version.
            run(
                [sys.executable, "-m", "pip", "install", "zuban"],
                check=True,
            )
            return True
        except CalledProcessError:
            print("Unable to install zuban")
            return False

    def get_version(self) -> str:
        proc = run(["zuban", "--version"], stdout=PIPE, text=True)
        return proc.stdout.strip()

    def run_tests(self, test_files: Sequence[str]) -> dict[str, str]:
        command = [
            "zuban",
            "check",
            ".",
            "--disable-error-code",
            "empty-body",
            "--enable-error-code",
            "deprecated",
            "--no-warn-unreachable",
            "--hide-error-codes",
        ]
        proc = run(command, stdout=PIPE, text=True, encoding="utf-8")
        lines = proc.stdout.split("\n")

        # Add results to a dictionary keyed by the file name.
        results_dict: dict[str, str] = {}
        for line in lines:
            file_name = line.split(":")[0].strip()
            results_dict[file_name] = results_dict.get(file_name, "") + line + "\n"

        return results_dict

    def parse_errors(self, output: Sequence[str]) -> dict[int, list[str]]:
        # narrowing_typeguard.py:102: error: TypeGuard functions must have a positional argument  [valid-type]
        line_to_errors: dict[int, list[str]] = {}
        for line in output:
            if line.count(":") < 3:
                continue
            _, lineno, kind, _ = line.split(":", maxsplit=3)
            kind = kind.strip()
            if kind != "error":
                continue
            line_to_errors.setdefault(int(lineno), []).append(line)
        return line_to_errors



TYPE_CHECKERS: Sequence[TypeChecker] = (
    MypyTypeChecker(),
    PyrightTypeChecker(),
    *([] if os.name == "nt" else [PyreTypeChecker()]),
    ZubanLSTypeChecker(),
)
