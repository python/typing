"""
Classes that abstract differences between type checkers.
"""

from abc import ABC, abstractmethod
import json
from pathlib import Path
import re
from subprocess import PIPE, run
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


class MypyTypeChecker(TypeChecker):
    @property
    def name(self) -> str:
        return "mypy"

    def install(self) -> bool:
        try:
            run(f"{sys.executable} -m pip install mypy --upgrade", check=True, shell=True)
            return True
        except:
            print('Unable to install mypy')
            return False

    def get_version(self) -> str:
        proc = run(
            f"{sys.executable} -m mypy --version", stdout=PIPE, text=True, shell=True
        )
        version = proc.stdout.strip()

        # Remove the " (compiled)" if it's present.
        version = version.split(" (")[0]
        return version

    def run_tests(self, test_files: Sequence[str]) -> dict[str, str]:
        command = f"{sys.executable} -m mypy . --disable-error-code empty-body"
        proc = run(command, stdout=PIPE, text=True, shell=True)
        lines = proc.stdout.split("\n")

        # Add results to a dictionary keyed by the file name.
        results_dict: dict[str, str] = {}
        for line in lines:
            file_name = line.split(":")[0].strip()
            results_dict[file_name] = results_dict.get(file_name, "") + line + "\n"

        return results_dict


class PyrightTypeChecker(TypeChecker):
    @property
    def name(self) -> str:
        return "pyright"

    def install(self) -> bool:
        try:
            # Install the Python wrapper if it's not installed.
            run(f"{sys.executable} -m pip install pyright --upgrade", check=True, shell=True)

            # Force the Python wrapper to install node if needed
            # and download the latest version of pyright.
            self.get_version()
            return True
        except:
            print('Unable to install pyright')
            return False

    def get_version(self) -> str:
        proc = run(
            f"{sys.executable} -m pyright --version", stdout=PIPE, text=True, shell=True
        )
        return proc.stdout.strip()

    def run_tests(self, test_files: Sequence[str]) -> dict[str, str]:
        command = f"{sys.executable} -m pyright . --outputjson"
        proc = run(command, stdout=PIPE, text=True, shell=True)
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


class PyreTypeChecker(TypeChecker):
    @property
    def name(self) -> str:
        return "pyre"

    def install(self) -> bool:
        try:
            run(f"{sys.executable} -m pip install pyre-check --upgrade", check=True, shell=True)

            # Generate a default config file.
            pyre_config = (
                '{"site_package_search_strategy": "pep561", "source_directories": ["."]}\n'
            )
            with open(".pyre_configuration", "w") as f:
                f.write(pyre_config)

            return True
        except:
            print('Unable to install pyre')
            return False

    def get_version(self) -> str:
        proc = run("pyre --version", stdout=PIPE, text=True, shell=True)
        version = proc.stdout.strip()
        version = version.replace("Client version:", "pyre")
        return version

    def run_tests(self, test_files: Sequence[str]) -> dict[str, str]:
        proc = run("pyre check", stdout=PIPE, text=True, shell=True)
        lines = proc.stdout.split("\n")

        # Add results to a dictionary keyed by the file name.
        results_dict: dict[str, str] = {}
        for line in lines:
            file_name = line.split(":")[0].strip()
            results_dict[file_name] = results_dict.get(file_name, "") + line + "\n"

        return results_dict


class PytypeTypeChecker(TypeChecker):
    @property
    def name(self) -> str:
        return "pytype"

    def install(self) -> bool:
        try:
            run(f"{sys.executable} -m pip install pytype --upgrade", check=True, shell=True)
            return True
        except:
            print('Unable to install pytype on this platform')
            return False

    def get_version(self) -> str:
        proc = run(
            f"{sys.executable} -m pytype --version", stdout=PIPE, text=True, shell=True
        )
        version = proc.stdout.strip()
        return f"pytype {version}"

    def run_tests(self, test_files: Sequence[str]) -> dict[str, str]:
        # Specify 3.11 for now to work around the fact that pytype
        # currently doesn't support 3.12 and emits an error when
        # running on 3.12.
        command = f"{sys.executable} -m pytype -V 3.11 -k *.py"
        proc = run(command, stdout=PIPE, text=True, shell=True)
        lines = proc.stdout.split("\n")

        # Add results to a dictionary keyed by the file name.
        results_dict: dict[str, str] = {}
        accumulated_lines: list[str] = []
        file_name: str | None = None

        def log_accumulated():
            if file_name is not None:
                results_dict[file_name] = (
                    results_dict.get(file_name, "") + "".join(accumulated_lines) + "\n"
                )

        for line in lines:
            match = re.search(r'File "(.*?)",', line)

            if not match or match.start() != 0:
                # An empty line precedes the summary for the file. Ignore
                # everything after that line until we see diagnostics for
                # the next file.
                if line.strip() == "":
                    log_accumulated()
                    file_name = None
                    accumulated_lines = []
                elif file_name is not None:
                    accumulated_lines.append("\n" + line)
            else:
                log_accumulated()

                file_path = Path(match.group(1))
                file_name = file_path.name

                # Replace the full file path with the file name.
                line = f'File "{file_name}",{line[match.end():]}'
                accumulated_lines = [line]

        # Log the final accumulated lines.
        log_accumulated()

        return results_dict


TYPE_CHECKERS: Sequence[TypeChecker] = (
    MypyTypeChecker(),
    PyrightTypeChecker(),
    PyreTypeChecker(),
    PytypeTypeChecker(),
)
