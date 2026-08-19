"""

Helper script to find test cases where the automated and manual
conformance results differ.

"""

from pathlib import Path
import tomllib


def _check_file(file: Path, results_dir: Path) -> str | None:
    """Check a single result file for automated/manual mismatch.

    Returns a formatted mismatch string if the automated and manual
    verdicts differ, otherwise None.

    Raises:
        Exception: if the file is not valid TOML or a required key is missing.
    """
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
        # ``conformant`` may be absent when automated is Pass (implied Pass)
        conformant_val = info.get("conformant", "Pass (implied)")
        return (
            f"{file.relative_to(results_dir)}: "
            f"{conformant_val} vs. {info['conformance_automated']}"
        )
    return None


def find_unexpected_fails(results_dir: Path) -> list[str]:
    """Scan ``results_dir`` and return all automated/manual mismatches."""
    mismatches: list[str] = []
    for type_checker_dir in sorted(results_dir.iterdir()):
        if not type_checker_dir.is_dir():
            continue
        for file in sorted(type_checker_dir.iterdir()):
            if file.name == "version.toml":
                continue
            msg = _check_file(file, results_dir)
            if msg is not None:
                mismatches.append(msg)
    return mismatches


def main(results_dir: Path | None = None) -> int:
    """Print mismatches and return 0 (mismatches are informational)."""
    if results_dir is None:
        results_dir = Path(__file__).resolve().parent.parent / "results"
    for line in find_unexpected_fails(results_dir):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
