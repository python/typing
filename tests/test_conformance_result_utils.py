"""Tests for conformance result utilities.

Covers ``conformance/src/unexpected_fails.py`` and
``conformance/src/validate_results.py`` — 0% coverage before this file.
See https://github.com/python/typing/issues/2337
"""

import sys
from pathlib import Path

import pytest

# Make ``conformance/src`` importable when tests run from repo root.
_SRC = Path(__file__).resolve().parents[1] / "conformance" / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import unexpected_fails  # noqa: E402
import validate_results  # noqa: E402


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _write_toml(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _make_results(tmp_path: Path, files: dict[str, str]) -> Path:
    """Create a fake ``results/`` tree from ``{relative_path: toml_content}``."""
    results = tmp_path / "results"
    for rel, content in files.items():
        _write_toml(results / rel, content)
    return results


# ---------------------------------------------------------------------------
# unexpected_fails – matching / mismatch
# ---------------------------------------------------------------------------

class TestUnexpectedFailsMatching:
    def test_matching_automated_pass_implied(self, tmp_path):
        results = _make_results(
            tmp_path,
            {"mypy/foo.toml": 'conformance_automated = "Pass"\n'},
        )
        assert unexpected_fails.find_unexpected_fails(results) == []

    def test_matching_automated_pass_explicit(self, tmp_path):
        results = _make_results(
            tmp_path,
            {
                "mypy/foo.toml": (
                    'conformance_automated = "Pass"\nconformant = "Pass"\n'
                )
            },
        )
        assert unexpected_fails.find_unexpected_fails(results) == []

    def test_matching_automated_fail_partial(self, tmp_path):
        results = _make_results(
            tmp_path,
            {
                "mypy/foo.toml": (
                    'conformance_automated = "Fail"\n'
                    'conformant = "Partial"\n'
                    'notes = "some reason"\n'
                )
            },
        )
        assert unexpected_fails.find_unexpected_fails(results) == []

    def test_matching_automated_fail_unsupported(self, tmp_path):
        results = _make_results(
            tmp_path,
            {
                "mypy/foo.toml": (
                    'conformance_automated = "Fail"\n'
                    'conformant = "Unsupported"\n'
                )
            },
        )
        assert unexpected_fails.find_unexpected_fails(results) == []


class TestUnexpectedFailsMismatch:
    def test_detects_pass_vs_partial(self, tmp_path):
        results = _make_results(
            tmp_path,
            {
                "mypy/generics_basic.toml": (
                    'conformance_automated = "Pass"\n'
                    'conformant = "Partial"\n'
                )
            },
        )
        mism = unexpected_fails.find_unexpected_fails(results)
        assert len(mism) == 1
        assert "Partial vs. Pass" in mism[0]

    def test_detects_fail_vs_pass(self, tmp_path):
        results = _make_results(
            tmp_path,
            {
                "pyright/foo.toml": (
                    'conformance_automated = "Fail"\nconformant = "Pass"\n'
                )
            },
        )
        mism = unexpected_fails.find_unexpected_fails(results)
        assert len(mism) == 1
        assert "Pass vs. Fail" in mism[0]

    def test_multiple_files_mixed(self, tmp_path):
        results = _make_results(
            tmp_path,
            {
                "mypy/a.toml": 'conformance_automated = "Pass"\n',
                "mypy/b.toml": (
                    'conformance_automated = "Pass"\nconformant = "Partial"\n'
                ),
                "mypy/c.toml": (
                    'conformance_automated = "Fail"\nconformant = "Pass"\n'
                ),
            },
        )
        mism = unexpected_fails.find_unexpected_fails(results)
        assert len(mism) == 2

    def test_version_toml_is_skipped(self, tmp_path):
        results = _make_results(
            tmp_path,
            {
                "mypy/version.toml": 'version = "1.0"\n',
                "mypy/foo.toml": 'conformance_automated = "Pass"\n',
            },
        )
        assert unexpected_fails.find_unexpected_fails(results) == []


class TestUnexpectedFailsErrors:
    def test_malformed_toml_raises(self, tmp_path):
        results = _make_results(
            tmp_path, {"mypy/bad.toml": 'conformance_automated = "Pass\n'}
        )
        with pytest.raises(Exception, match="Error decoding"):
            unexpected_fails.find_unexpected_fails(results)

    def test_missing_conformance_automated_raises(self, tmp_path):
        results = _make_results(
            tmp_path, {"mypy/bad.toml": 'conformant = "Pass"\n'}
        )
        with pytest.raises(Exception, match="Missing key"):
            unexpected_fails.find_unexpected_fails(results)

    def test_missing_conformant_when_fail_raises(self, tmp_path):
        # automated Fail + no conformant -> KeyError path in _check_file
        results = _make_results(
            tmp_path, {"mypy/bad.toml": 'conformance_automated = "Fail"\n'}
        )
        with pytest.raises(Exception, match="Missing key"):
            unexpected_fails.find_unexpected_fails(results)

    def test_check_file_returns_none_on_match(self, tmp_path):
        results = _make_results(
            tmp_path, {"mypy/foo.toml": 'conformance_automated = "Pass"\n'}
        )
        file = results / "mypy" / "foo.toml"
        assert unexpected_fails._check_file(file, results) is None

    def test_check_file_returns_string_on_mismatch(self, tmp_path):
        results = _make_results(
            tmp_path,
            {
                "mypy/foo.toml": (
                    'conformance_automated = "Pass"\nconformant = "Partial"\n'
                )
            },
        )
        file = results / "mypy" / "foo.toml"
        msg = unexpected_fails._check_file(file, results)
        assert msg is not None
        assert "mypy/foo.toml" in msg

    def test_main_prints_mismatches(self, tmp_path, capsys):
        results = _make_results(
            tmp_path,
            {
                "mypy/foo.toml": (
                    'conformance_automated = "Pass"\nconformant = "Partial"\n'
                )
            },
        )
        rc = unexpected_fails.main(results)
        assert rc == 0
        out = capsys.readouterr().out
        assert "Partial vs. Pass" in out

    def test_main_no_output_when_no_mismatch(self, tmp_path, capsys):
        results = _make_results(
            tmp_path, {"mypy/foo.toml": 'conformance_automated = "Pass"\n'}
        )
        rc = unexpected_fails.main(results)
        assert rc == 0
        assert capsys.readouterr().out == ""


# ---------------------------------------------------------------------------
# validate_results – valid files
# ---------------------------------------------------------------------------

class TestValidateAcceptsValid:
    def test_accepts_pass_no_conformant(self, tmp_path):
        results = tmp_path / "results"
        file = results / "mypy" / "foo.toml"
        info = {"conformance_automated": "Pass"}
        assert validate_results._validate_result(file, results, info) == []

    def test_accepts_pass_with_pass(self, tmp_path):
        results = tmp_path / "results"
        file = results / "mypy" / "foo.toml"
        info = {"conformance_automated": "Pass", "conformant": "Pass"}
        assert validate_results._validate_result(file, results, info) == []

    def test_accepts_fail_with_partial_and_notes(self, tmp_path):
        results = tmp_path / "results"
        file = results / "mypy" / "foo.toml"
        info = {
            "conformance_automated": "Fail",
            "conformant": "Partial",
            "notes": "does not support X",
        }
        assert validate_results._validate_result(file, results, info) == []

    def test_accepts_fail_with_unsupported_no_notes(self, tmp_path):
        results = tmp_path / "results"
        file = results / "mypy" / "foo.toml"
        info = {
            "conformance_automated": "Fail",
            "conformant": "Unsupported",
        }
        assert validate_results._validate_result(file, results, info) == []

    def test_accepts_fail_with_partial_and_allowed_keys(self, tmp_path):
        results = tmp_path / "results"
        file = results / "mypy" / "foo.toml"
        info = {
            "conformance_automated": "Fail",
            "conformant": "Partial",
            "notes": "reason",
            "output": "err",
            "errors_diff": "diff",
            "ignore_errors": [],
        }
        assert validate_results._validate_result(file, results, info) == []


class TestValidateUnknownKeys:
    def test_rejects_single_unknown_key(self, tmp_path):
        results = tmp_path / "results"
        file = results / "mypy" / "foo.toml"
        info = {"conformance_automated": "Pass", "foo": "bar"}
        issues = validate_results._validate_result(file, results, info)
        assert any("unrecognized key" in i and "foo" in i for i in issues)

    def test_rejects_multiple_unknown_keys(self, tmp_path):
        results = tmp_path / "results"
        file = results / "mypy" / "foo.toml"
        info = {
            "conformance_automated": "Pass",
            "conformant": "Pass",
            "unknown1": 1,
            "unknown2": 2,
        }
        issues = validate_results._validate_result(file, results, info)
        assert any("unknown1" in i and "unknown2" in i for i in issues)


class TestValidateAutomatedValues:
    @pytest.mark.parametrize("bad", ["Maybe", "pass", "", None, 123])
    def test_rejects_invalid_automated(self, tmp_path, bad):
        results = tmp_path / "results"
        file = results / "mypy" / "foo.toml"
        info: dict = {"conformance_automated": bad}
        issues = validate_results._validate_result(file, results, info)
        assert any("conformance_automated must be" in i for i in issues)

    def test_missing_automated(self, tmp_path):
        results = tmp_path / "results"
        file = results / "mypy" / "foo.toml"
        info: dict = {}
        issues = validate_results._validate_result(file, results, info)
        assert any("conformance_automated must be" in i for i in issues)


class TestValidateConformantValues:
    @pytest.mark.parametrize("bad", ["Fail", "Maybe", "PASS", ""])
    def test_rejects_invalid_conformant_string(self, tmp_path, bad):
        results = tmp_path / "results"
        file = results / "mypy" / "foo.toml"
        info = {"conformance_automated": "Pass", "conformant": bad}
        issues = validate_results._validate_result(file, results, info)
        assert any("invalid conformance status" in i for i in issues)

    def test_rejects_non_string_conformant(self, tmp_path):
        results = tmp_path / "results"
        file = results / "mypy" / "foo.toml"
        for bad in [123, True, None, 3.14]:
            # None is the missing case, handled separately; skip it here
            if bad is None:
                continue
            info: dict = {
                "conformance_automated": "Pass",
                "conformant": bad,  # type: ignore[dict-item]
            }
            issues = validate_results._validate_result(file, results, info)
            assert any("conformant must be a string" in i for i in issues)

    def test_missing_conformant_when_pass_ok(self, tmp_path):
        results = tmp_path / "results"
        file = results / "mypy" / "foo.toml"
        info = {"conformance_automated": "Pass"}
        assert validate_results._validate_result(file, results, info) == []

    def test_missing_conformant_when_fail_error(self, tmp_path):
        results = tmp_path / "results"
        file = results / "mypy" / "foo.toml"
        info = {"conformance_automated": "Fail"}
        issues = validate_results._validate_result(file, results, info)
        assert any("conformant is required" in i for i in issues)


class TestValidateMismatchAndNotes:
    def test_mismatch_pass_vs_partial(self, tmp_path):
        results = tmp_path / "results"
        file = results / "mypy" / "foo.toml"
        info = {
            "conformance_automated": "Pass",
            "conformant": "Partial",
            "notes": "reason",
        }
        issues = validate_results._validate_result(file, results, info)
        assert any("does not match" in i for i in issues)

    def test_mismatch_fail_vs_pass(self, tmp_path):
        results = tmp_path / "results"
        file = results / "mypy" / "foo.toml"
        info = {"conformance_automated": "Fail", "conformant": "Pass"}
        issues = validate_results._validate_result(file, results, info)
        assert any("does not match" in i for i in issues)

    def test_mismatch_pass_vs_unsupported(self, tmp_path):
        results = tmp_path / "results"
        file = results / "mypy" / "foo.toml"
        info = {"conformance_automated": "Pass", "conformant": "Unsupported"}
        issues = validate_results._validate_result(file, results, info)
        assert any("does not match" in i for i in issues)

    def test_partial_requires_notes_missing(self, tmp_path):
        results = tmp_path / "results"
        file = results / "mypy" / "foo.toml"
        info = {
            "conformance_automated": "Fail",
            "conformant": "Partial",
        }
        issues = validate_results._validate_result(file, results, info)
        assert any("notes must be present" in i for i in issues)

    @pytest.mark.parametrize("bad_notes", ["", "   ", " \n\t "])
    def test_partial_requires_notes_empty_or_whitespace(
        self, tmp_path, bad_notes
    ):
        results = tmp_path / "results"
        file = results / "mypy" / "foo.toml"
        info = {
            "conformance_automated": "Fail",
            "conformant": "Partial",
            "notes": bad_notes,
        }
        issues = validate_results._validate_result(file, results, info)
        assert any("notes must be present" in i for i in issues)

    def test_partial_requires_notes_non_string(self, tmp_path):
        results = tmp_path / "results"
        file = results / "mypy" / "foo.toml"
        info: dict = {
            "conformance_automated": "Fail",
            "conformant": "Partial",
            "notes": 123,  # type: ignore[dict-item]
        }
        issues = validate_results._validate_result(file, results, info)
        assert any("notes must be present" in i for i in issues)

    def test_partial_with_valid_notes_ok(self, tmp_path):
        results = tmp_path / "results"
        file = results / "mypy" / "foo.toml"
        info = {
            "conformance_automated": "Fail",
            "conformant": "Partial",
            "notes": " valid notes ",
        }
        assert validate_results._validate_result(file, results, info) == []


class TestValidateMain:
    def test_main_accepts_valid_files(self, tmp_path, capsys):
        results = _make_results(
            tmp_path,
            {
                "mypy/a.toml": 'conformance_automated = "Pass"\n',
                "pyright/b.toml": (
                    'conformance_automated = "Fail"\n'
                    'conformant = "Partial"\n'
                    'notes = "reason"\n'
                ),
            },
        )
        rc = validate_results.main(results)
        assert rc == 0
        assert "no invariant violations" in capsys.readouterr().out

    def test_main_rejects_unknown_key(self, tmp_path, capsys):
        results = _make_results(
            tmp_path,
            {
                "mypy/a.toml": (
                    'conformance_automated = "Pass"\nunknown = "x"\n'
                )
            },
        )
        rc = validate_results.main(results)
        assert rc == 1
        out = capsys.readouterr().out
        assert "unrecognized key" in out
        assert "unknown" in out

    def test_main_handles_malformed_toml(self, tmp_path, capsys):
        results = _make_results(
            tmp_path,
            {
                "mypy/bad.toml": 'conformance_automated = "Pass\n',
                "mypy/good.toml": 'conformance_automated = "Pass"\n',
            },
        )
        rc = validate_results.main(results)
        assert rc == 1
        assert "failed to parse TOML" in capsys.readouterr().out

    def test_main_handles_missing_keys(self, tmp_path, capsys):
        results = _make_results(
            tmp_path,
            {
                "mypy/bad.toml": 'conformant = "Pass"\n',
            },
        )
        rc = validate_results.main(results)
        assert rc == 1
        assert "conformance_automated must be" in capsys.readouterr().out

    def test_main_skips_version_toml(self, tmp_path, capsys):
        results = _make_results(
            tmp_path,
            {
                "mypy/version.toml": 'version = "1.0"\n',
                "mypy/a.toml": 'conformance_automated = "Pass"\n',
            },
        )
        rc = validate_results.main(results)
        assert rc == 0
        assert "Validated 1" in capsys.readouterr().out

    def test_main_validates_notes_for_partial(self, tmp_path, capsys):
        results = _make_results(
            tmp_path,
            {
                "mypy/a.toml": (
                    'conformance_automated = "Fail"\n'
                    'conformant = "Partial"\n'
                    'notes = ""\n'
                )
            },
        )
        rc = validate_results.main(results)
        assert rc == 1
        assert "notes must be present" in capsys.readouterr().out

    def test_main_reports_invalid_automated(self, tmp_path, capsys):
        results = _make_results(
            tmp_path,
            {
                "mypy/a.toml": 'conformance_automated = "Maybe"\n',
            },
        )
        rc = validate_results.main(results)
        assert rc == 1
        assert "conformance_automated must be" in capsys.readouterr().out

    def test_main_reports_invalid_conformant(self, tmp_path, capsys):
        results = _make_results(
            tmp_path,
            {
                "mypy/a.toml": (
                    'conformance_automated = "Pass"\nconformant = "Fail"\n'
                )
            },
        )
        rc = validate_results.main(results)
        assert rc == 1
        assert "invalid conformance status" in capsys.readouterr().out

    def test_main_counts_files(self, tmp_path, capsys):
        results = _make_results(
            tmp_path,
            {
                "mypy/a.toml": 'conformance_automated = "Pass"\n',
                "mypy/b.toml": 'conformance_automated = "Pass"\n',
                "pyright/c.toml": 'conformance_automated = "Pass"\n',
            },
        )
        rc = validate_results.main(results)
        assert rc == 0
        assert "Validated 3" in capsys.readouterr().out
