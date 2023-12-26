"""
Classes that abstract differences between type checkers.
"""

from abc import ABC, abstractmethod
import json
from pathlib import Path
from subprocess import PIPE, run
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
    def install(self) -> None:
        """
        Ensures that the latest version of the type checker is installed.
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

    def install(self) -> None:
        run("pip install mypy --upgrade", shell=True)

    def get_version(self) -> str:
        proc = run("mypy --version", stdout=PIPE, text=True, shell=True)
        version = proc.stdout.strip()

        # Remove the " (compiled)" if it's present.
        version = version.split(" (")[0]
        return version

    def run_tests(self, test_files: Sequence[str]) -> dict[str, str]:
        command = f"mypy . --disable-error-code empty-body"
        proc = run(command, stdout=PIPE, text=True, shell=True)
        lines = proc.stdout.split('\n')

        # Add results to a dictionary keyed by the file name.
        results_dict: dict[str, str] = {}
        for line in lines:
            file_name = line.split(':')[0].strip()
            results_dict[file_name] = results_dict.get(file_name, '') + line + '\n'
            
        return results_dict


class PyrightTypeChecker(TypeChecker):
    @property
    def name(self) -> str:
        return "pyright"

    def install(self) -> None:
        # Install the Python wrapper if it's not installed.
        run("pip install pyright", shell=True)

        # Force the Python wrapper to install node if needed
        # and download the latest version of pyright.
        self.get_version()

    def get_version(self) -> str:
        proc = run("pyright --version", stdout=PIPE, text=True, shell=True)
        return proc.stdout.strip()

    def run_tests(self, test_files: Sequence[str]) -> dict[str, str]:
        command = f"pyright . --outputjson"
        proc = run(command, stdout=PIPE, text=True, shell=True)
        output_json = json.loads(proc.stdout)
        diagnostics = output_json['generalDiagnostics']

        # Add results to a dictionary keyed by the file name.
        results_dict: dict[str, str] = {}
        for diagnostic in diagnostics:
            file_path = Path(diagnostic.get('file', ''))
            file_name = file_path.name
            line_number = diagnostic['range']['start']['line'] + 1
            col_number = diagnostic['range']['start']['character'] + 1
            severity = diagnostic['severity']
            message = diagnostic['message']
            rule = f" ({diagnostic['rule']})" if 'rule' in diagnostic else ''
            
            line_text = f'{file_name}:{line_number}:{col_number} - {severity}: {message}{rule}\n'
            results_dict[file_name] = results_dict.get(file_name, '') + line_text
            
        return results_dict

class PyreTypeChecker(TypeChecker):
    @property
    def name(self) -> str:
        return "pyre"

    def install(self) -> None:
        run("pip install pyre-check --upgrade", shell=True)

        # Generate a default config file.
        pyre_config = '{"site_package_search_strategy": "pep561", "source_directories": ["."]}\n'
        with open('.pyre_configuration', 'w') as f:
            f.write(pyre_config)

    def get_version(self) -> str:
        proc = run("pyre --version", stdout=PIPE, text=True, shell=True)
        version = proc.stdout.strip()
        version = version.replace('Client version:', 'pyre')
        return version

    def run_tests(self, test_files: Sequence[str]) -> dict[str, str]:
        command = f"pyre check"
        proc = run(command, stdout=PIPE, text=True, shell=True)
        lines = proc.stdout.split('\n')

        # Add results to a dictionary keyed by the file name.
        results_dict: dict[str, str] = {}
        for line in lines:
            file_name = line.split(':')[0].strip()
            results_dict[file_name] = results_dict.get(file_name, '') + line + '\n'
            
        return results_dict


TYPE_CHECKERS: Sequence[TypeChecker] = (
    MypyTypeChecker(),
    PyrightTypeChecker(),
    PyreTypeChecker(),
)
