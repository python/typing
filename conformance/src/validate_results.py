"""
Validate invariants for conformance result files.
"""

from pathlib import Path
import sys
import tomllib
from typing import Any


def main() -> int:
    results_dir = Path(__file__).resolve().parent.parent / "results"
    issues: list[str] = []
    checked = 0

    for type_checker_dir in sorted(results_dir.iterdir()):
        if not type_checker_dir.is_dir():
            continue
        for file in sorted(type_checker_dir.iterdir()):
            if file.name == "version.toml":
                continue
            checked += 1
            try:
                with file.open("rb") as f:
                    info = tomllib.load(f)
            except Exception as e:
                issues.append(f"{file.relative_to(results_dir)}: failed to parse TOML ({e})")
                continue

            issues.extend(_validate_result(file, results_dir, info))

    if issues:
        print(f"Found {len(issues)} invariant violation(s) across {checked} file(s):")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print(f"Validated {checked} conformance result file(s); no invariant violations found.")
    return 0


def _validate_result(file: Path, results_dir: Path, info: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    rel_path = file.relative_to(results_dir)

    automated = info.get("conformance_automated")
    if automated not in {"Pass", "Fail"}:
        issues.append(
            f"{rel_path}: conformance_automated must be 'Pass' or 'Fail' (got {automated!r})"
        )
        return issues
    automated_is_pass = automated == "Pass"

    conformant = info.get("conformant")
    if conformant is None:
        if automated_is_pass:
            conformant_is_pass = True
        else:
            issues.append(
                f"{rel_path}: conformant is required when conformance_automated is 'Fail'"
            )
            return issues
    elif isinstance(conformant, str):
        if conformant not in ("Pass", "Partial", "Unsupported"):
            issues.append(f"{rel_path}: invalid conformance status {conformant!r}")
        conformant_is_pass = conformant == "Pass"
    else:
        issues.append(f"{rel_path}: conformant must be a string when present")
        return issues

    if conformant_is_pass != automated_is_pass:
        issues.append(
            f"{rel_path}: conformant={conformant!r} does not match "
            f"conformance_automated={automated!r}"
        )

    if not conformant_is_pass:
        notes = info.get("notes", "")
        if not isinstance(notes, str) or not notes.strip():
            issues.append(
                f"{rel_path}: notes must be present when checker is not fully conformant"
            )

    return issues


if __name__ == "__main__":
    raise SystemExit(main())
