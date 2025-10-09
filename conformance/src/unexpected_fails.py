"""

Helper script to find test cases where the automated and manual
conformance results differ.

"""

from pathlib import Path
import tomllib

results_dir = Path(__file__).resolve().parent.parent / "results"

for type_checker_dir in sorted(results_dir.iterdir()):
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
                new_pass = info["conformance_automated"] == "Pass"
                if new_pass and "conformant" not in info:
                    previous_pass = True
                else:
                    previous_pass = info["conformant"] == "Pass"
            except KeyError as e:
                raise Exception(f"Missing key in {file}") from e
            if previous_pass != new_pass:
                print(f"{file.relative_to(results_dir)}: {info['conformant']} vs. {info['conformance_automated']}")
