"""
Classes that abstract differences between type checkers.
"""

from abc import ABC, abstractmethod
import json
from pathlib import Path
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
        Ensures that the type checker is available in the current environment.
        Returns False if it cannot be executed.
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
            # Run "mypy --version" to ensure that it's available and to work
            # around timing issues caused by malware scanners on some systems.
            self.get_version()
            return True
        except (CalledProcessError, FileNotFoundError):
            print(
                "Unable to run mypy. Install conformance dependencies with "
                "'uv sync --frozen' from the conformance directory."
            )
            return False

    def get_version(self) -> str:
        proc = run(
            [sys.executable, "-m", "mypy", "--version"],
            check=True,
            stdout=PIPE,
            text=True,
        )
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
            # Force the Python wrapper to install node if needed
            # and use the locked version of pyright.
            self.get_version()
            return True
        except (CalledProcessError, FileNotFoundError):
            print(
                "Unable to run pyright. Install conformance dependencies with "
                "'uv sync --frozen' from the conformance directory."
            )
            return False

    def get_version(self) -> str:
        proc = run(
            [sys.executable, "-m", "pyright", "--version"],
            check=True,
            stdout=PIPE,
            text=True,
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


class ZubanLSTypeChecker(MypyTypeChecker):
    @property
    def name(self) -> str:
        return "zuban"

    def install(self) -> bool:
        try:
            self.get_version()
            return True
        except (CalledProcessError, FileNotFoundError):
            print(
                "Unable to run zuban. Install conformance dependencies with "
                "'uv sync --frozen' from the conformance directory."
            )
            return False

    def get_version(self) -> str:
        proc = run(["zuban", "--version"], check=True, stdout=PIPE, text=True)
        return proc.stdout.strip()

    def run_tests(self, test_files: Sequence[str]) -> dict[str, str]:
        command = [
            "zuban",
            "check",
            ".",
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


class PyreflyTypeChecker(TypeChecker):
    @property
    def name(self) -> str:
        return "pyrefly"

    def install(self) -> bool:
        try:
            self.get_version()
            return True
        except (CalledProcessError, FileNotFoundError):
            print(
                "Unable to run pyrefly. Install conformance dependencies with "
                "'uv sync --frozen' from the conformance directory."
            )
            return False

    def get_version(self) -> str:
        proc = run(["pyrefly", "--version"], check=True, stdout=PIPE, text=True)
        version = proc.stdout.strip()
        return version

    def run_tests(self, test_files: Sequence[str]) -> dict[str, str]:
        proc = run(
            ["pyrefly", "check", "--output-format", "min-text", "--summary=none"],
            stdout=PIPE,
            text=True,
            encoding="utf-8",
        )
        lines = proc.stdout.split("\n")

        # Add results to a dictionary keyed by the file name.
        results_dict: dict[str, str] = {}
        for line in lines:
            if not line.strip():
                continue
            if line.startswith(" INFO "):
                continue
            # Extract the absolute path reported by pyrefly and convert it to a
            # stable relative path (filename only) so results are consistent.
            # Example input line:
            #   "ERROR /abs/.../conformance/tests/foo.py:12:3-5: message [code]"
            # We replace the absolute path with just "foo.py".
            try:
                abs_path = line.split(":", 1)[0].strip().split(" ", 1)[1].strip()
            except IndexError:
                # If parsing fails, fall back to original line and grouping.
                abs_path = ""
            file_name = Path(abs_path).name if abs_path else line.split(":")[0]

            # Replace only the first occurrence to avoid touching the message text.
            display_line = line.replace(abs_path, file_name, 1) if abs_path else line
            results_dict[file_name] = (
                results_dict.get(file_name, "") + display_line + "\n"
            )
        return results_dict

    def parse_errors(self, output: Sequence[str]) -> dict[int, list[str]]:
        line_to_errors: dict[int, list[str]] = {}
        for line in output:
            # Ignore multi-line errors
            if ".py:" not in line and ".pyi:" not in line:
                continue
            # Ignore reveal_type errors
            if "revealed type: " in line:
                continue
            assert line.count(":") >= 3, f"Failed to parse line: {line!r}"
            _, lineno, _, error_msg = line.split(":", maxsplit=3)
            line_to_errors.setdefault(int(lineno), []).append(error_msg.strip())
        return line_to_errors


TYPE_CHECKERS: Sequence[TypeChecker] = (
    MypyTypeChecker(),
    PyrightTypeChecker(),
    ZubanLSTypeChecker(),
    PyreflyTypeChecker(),
)
