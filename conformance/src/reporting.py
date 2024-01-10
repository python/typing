"""
Generates a summary of the type checker conformant tests.
"""

from pathlib import Path

import tomli

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


def generate_summary_html(root_dir: Path):
    column_count = len(TYPE_CHECKERS) + 1
    test_groups = get_test_groups(root_dir)
    test_cases = get_test_cases(test_groups, root_dir / "tests")

    summary_html = '<div class="table_container"><table><tbody>'
    summary_html += '<tr><th class="col1">&nbsp;</th>'

    for type_checker in TYPE_CHECKERS:
        # Load the version file for the type checker.
        version_file = root_dir / "results" / type_checker.name / "version.toml"

        try:
            with open(version_file, "rb") as f:
                existing_info = tomli.load(f)
        except FileNotFoundError:
            existing_info = {}
        except tomli.TOMLDecodeError:
            print(f"Error decoding {version_file}")
            existing_info = {}

        version = existing_info["version"] or "Unknown version"
        test_duration = existing_info.get("test_duration")

        summary_html += f"<th class='tc-header'><div class='tc-name'>{version}</div>"
        if test_duration is not None:
            summary_html += f"<div class='tc-time'>{test_duration:.2f}sec</div>"
        summary_html += f"</th>"

    summary_html += f"</tr>"

    for test_group_name, test_group in test_groups.items():
        tests_in_group = [
            case for case in test_cases if case.name.startswith(f"{test_group_name}_")
        ]

        tests_in_group.sort(key=lambda x: x.name)

        # Are there any test cases in this group?
        if len(tests_in_group) > 0:
            summary_html += f'<tr><th class="column" colspan="{column_count}">'
            summary_html += (
                f'<a class="test_group" href="{test_group.href}">{test_group.name}</a>'
            )
            summary_html += "</th></tr>"

            for test_case in tests_in_group:
                test_case_name = test_case.stem

                summary_html += f'<tr><th class="column col1">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{test_case_name}</th>'

                for type_checker in TYPE_CHECKERS:
                    try:
                        results_file = (
                            root_dir
                            / "results"
                            / type_checker.name
                            / f"{test_case_name}.toml"
                        )
                        with open(results_file, "rb") as f:
                            results = tomli.load(f)
                    except FileNotFoundError:
                        results = {}

                    conformance = results.get("conformant", "Unknown")
                    notes = "".join(
                        [
                            f"<p>{note}</p>"
                            for note in results.get("notes", "").split("\n")
                        ]
                    )

                    conformance_class = (
                        "conformant"
                        if conformance == "Pass"
                        else "partially-conformant"
                        if conformance == "Partial"
                        else "not-conformant"
                    )

                    conformance_cell = f"{conformance}"
                    if conformance != "Pass":
                        conformance_cell = f'<div class="hover-text">{conformance_cell}<span class="tooltip-text" id="bottom">{notes}</span></div>'

                    summary_html += f'<th class="column col2 {conformance_class}">{conformance_cell}</th>'

                summary_html += f"</tr>"

    summary_html += "</tbody></table></div>\n"

    return summary_html
