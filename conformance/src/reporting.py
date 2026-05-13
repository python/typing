"""
Generates a summary of the type checker conformant tests.
"""

import operator
import tomllib
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

import jinja2
import markdown
import markupsafe

from test_groups import get_test_cases, get_test_groups
from type_checker import TYPE_CHECKERS, TypeChecker


@dataclass(frozen=True, kw_only=True, slots=True)
class TestResult:
    type_checker: str
    conformance: str
    notes: list[markupsafe.Markup] = field(default_factory=list)


@dataclass(frozen=True, kw_only=True, slots=True)
class TestCase:
    name: str
    results: list[TestResult] = field(default_factory=list)


@dataclass(frozen=True, kw_only=True, slots=True)
class TestGroup:
    slug: str
    name: str
    href: str
    paths: list[Path] = field(default_factory=list)
    cases: list[TestCase] = field(default_factory=list)


def generate_summary(root_dir: Path):
    print("Generating summary report")

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(root_dir.joinpath("src/templates")),
        autoescape=jinja2.select_autoescape(),
    )
    env.filters["conformance_class"] = _conformance_class

    template = env.get_template("base.html")

    type_checkers = sorted(TYPE_CHECKERS, key=operator.attrgetter("name"))

    results = template.render(
        groups=_get_groups(root_dir, type_checkers),
        versions=_get_versions(root_dir, type_checkers),
    )

    root_dir.joinpath("results", "results.html").write_text(results)


def _conformance_class(value: str) -> str:
    if value == "Pass":
        return "conformant"
    if value == "Partial":
        return "partially-conformant"
    return "not-conformant"


def _get_groups(
    root_dir: Path,
    type_checkers: Sequence[TypeChecker],
) -> list[TestGroup]:
    test_groups = get_test_groups(root_dir)
    test_cases = get_test_cases(test_groups, root_dir / "tests")

    groups = []

    for test_group_slug, test_group in test_groups.items():
        paths = sorted(
            [
                case
                for case in test_cases
                if case.name.startswith(f"{test_group_slug}_")
            ],
            key=operator.attrgetter("name"),
        )

        # Skip if there are no test cases in the group.
        if not paths:
            continue

        group = TestGroup(
            slug=test_group_slug,
            name=test_group.name,
            href=test_group.href,
            paths=paths,
        )
        groups.append(group)

        for path in group.paths:
            case = TestCase(name=path.stem)
            group.cases.append(case)

            for type_checker in type_checkers:
                result_path = (
                    root_dir / "results" / type_checker.name / f"{case.name}.toml"
                )
                try:
                    with result_path.open("rb") as f:
                        data = tomllib.load(f)
                except FileNotFoundError:
                    data = {}

                conformance = data.get("conformant")
                if not conformance:
                    # Try to look up the automated test results and use that if the test passes.
                    automated = data.get("conformance_automated")
                    conformance = "Pass" if automated == "Pass" else "Unknown"

                notes = [
                    markupsafe.Markup(
                        markdown.markdown(note, output_format="html")
                        .removeprefix("<p>")
                        .removesuffix("</p>")
                    )
                    for note in data.get("notes", "").strip().splitlines()
                ]

                result = TestResult(
                    type_checker=type_checker.name,
                    conformance=conformance,
                    notes=notes,
                )
                case.results.append(result)

    return groups


def _get_versions(
    root_dir: Path,
    type_checkers: Sequence[TypeChecker],
) -> list[str]:
    versions = []

    for type_checker in type_checkers:
        name = type_checker.name

        try:
            with root_dir.joinpath("results", name, "version.toml").open("rb") as f:
                data = tomllib.load(f)
        except (FileNotFoundError, tomllib.TOMLDecodeError):
            version = None
        else:
            version = data.get("version") or None

        # If version file cannot be found or has missing/invalid content, fall back to name.
        if version is None:
            version = f"{type_checker.name} ?.?.?"

        versions.append(version)

    return versions
