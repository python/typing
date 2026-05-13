"""
Generates a summary of the type checker conformant tests.
"""

import operator
import tomllib
from pathlib import Path

from test_groups import get_test_cases, get_test_groups
from type_checker import TYPE_CHECKERS


def generate_summary(root_dir: Path):
    print("Generating summary report")
    template_file = root_dir / "src" / "results_template.html"
    with open(template_file, "r") as f:
        template = f.read()

    summary = template.replace("{{summary}}", generate_summary_html(root_dir))

    results_file = root_dir / "results" / "results.html"

    with open(results_file, "w") as f:
        f.write(summary)


def generate_summary_html(root_dir: Path) -> str:
    type_checkers = sorted(TYPE_CHECKERS, key=operator.attrgetter("name"))
    column_count = len(type_checkers) + 1
    test_groups = get_test_groups(root_dir)
    test_cases = get_test_cases(test_groups, root_dir / "tests")

    summary_html = [
        "<colgroup>",
        '<col class="col1" span="1">',
        f'<col class="col2" span="{column_count - 1}">',
        "</colgroup>",
        "<thead>",
        "<tr>",
        "<th></th>",
    ]

    for type_checker in type_checkers:
        # Load the version file for the type checker.
        version_file = root_dir / "results" / type_checker.name / "version.toml"

        try:
            with open(version_file, "rb") as f:
                existing_info = tomllib.load(f)
        except FileNotFoundError:
            existing_info = {}
        except tomllib.TOMLDecodeError:
            print(f"Error decoding {version_file}")
            existing_info = {}

        version = existing_info["version"] or "Unknown version"

        summary_html.append(f"<th>{version}</th>")

    summary_html.extend(["</tr>", "</thead>", "<tbody>"])

    for test_group_name, test_group in test_groups.items():
        tests_in_group = [
            case for case in test_cases if case.name.startswith(f"{test_group_name}_")
        ]

        tests_in_group.sort(key=lambda x: x.name)

        # Are there any test cases in this group?
        if len(tests_in_group) > 0:
            summary_html.append(f'<tr><th colspan="{column_count}">')
            summary_html.append(
                f'<a class="test_group" href="{test_group.href}">{test_group.name}</a>'
            )
            summary_html.append("</th></tr>")

            for test_case in tests_in_group:
                test_case_name = test_case.stem

                summary_html.append(f"<tr><th>{test_case_name}</th>")

                for type_checker in type_checkers:
                    try:
                        results_file = (
                            root_dir
                            / "results"
                            / type_checker.name
                            / f"{test_case_name}.toml"
                        )
                        with open(results_file, "rb") as f:
                            results = tomllib.load(f)
                    except FileNotFoundError:
                        results = {}

                    raw_notes = results.get("notes", "").strip()
                    conformance = results.get("conformant", "Unknown")
                    if conformance == "Unknown":
                        # Try to look up the automated test results and use
                        # that if the test passes
                        automated = results.get("conformance_automated")
                        if automated == "Pass":
                            conformance = "Pass"
                    notes = "".join(
                        [f"<p>{note}</p>" for note in raw_notes.split("\n")]
                    )

                    conformance_classes = (
                        "conformant"
                        if conformance == "Pass"
                        else "partially-conformant"
                        if conformance == "Partial"
                        else "not-conformant"
                    )

                    # Add an asterisk if there are notes to display for a "Pass".
                    if raw_notes != "" and conformance == "Pass":
                        conformance = "Pass*"

                    conformance_cell = f"{conformance}"
                    if raw_notes != "":
                        conformance_classes = f"{conformance_classes} tooltip"
                        conformance_cell = f'{conformance_cell}<div class="notes">{notes}</div>'

                    summary_html.append(f'<td class="{conformance_classes}">{conformance_cell}</td>')

                summary_html.append("</tr>")

    summary_html.append("</tbody>")

    return "\n".join(summary_html)
