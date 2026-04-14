#!/usr/bin/env python3
"""
Update the conformance checker versions in uv.lock to the latest releases.
"""

from pathlib import Path
from subprocess import CalledProcessError, run


TYPE_CHECKERS = ("mypy", "pyright", "zuban", "pyrefly")


def main() -> int:
    root_dir = Path(__file__).resolve().parents[1]
    lock_command = ["uv", "lock", "--python", "3.12"]
    for checker in TYPE_CHECKERS:
        lock_command.extend(["--upgrade-package", checker])

    try:
        print("+", " ".join(lock_command))
        run(lock_command, cwd=root_dir, check=True)
    except CalledProcessError as exc:
        print(f"Failed with exit code {exc.returncode}")
        return exc.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
