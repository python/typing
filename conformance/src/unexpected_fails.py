"""

Helper script to find test cases where the automated and manual
conformance results differ.

"""

from pathlib import Path
import tomllib

root_dir = Path(__file__).resolve().parent.parent

for type_checker_dir in sorted((root_dir / "results").iterdir()):
    if type_checker_dir.is_dir():
        for file in sorted(type_checker_dir.iterdir()):
            if file.name == "version.toml":
                continue
            with file.open("rb") as f:
                try:
                    info = tomllib.load(f)
                except Exception as e:
                    raise Exception(f"Error decoding {file}") from e
            try:
                previous_pass = info["conformant"] == "Pass"
                new_pass = info["conformance_automated"] == "Pass"
            except KeyError as e:
                raise Exception(f"Missing key in {file}") from e
            if previous_pass != new_pass:
                print(f"{file}: {info['conformant']} vs. {info['conformance_automated']}")
