"""
Generates a summary of the type checker conformant tests.
"""

from pathlib import Path

import tomli

from test_groups import get_test_cases, get_test_groups
from type_checker import TYPE_CHECKERS


def generate_summary(root_dir: Path):
    print('Generating summary report')
    template_file = root_dir / "src" / "results_template.html"
    with open(template_file, "r") as f:
        template = f.read()

    summary = template.replace("{{summary}}", generate_summary_html(root_dir))

    results_file = root_dir / "results" / "results.html"

    with open(results_file, "w") as f:
        f.write(summary)


def generate_summary_html(root_dir: Path):
    test_groups = get_test_groups(root_dir)
    test_cases = get_test_cases(test_groups, root_dir / "tests")

    summary_html = ""

    for type_checker in TYPE_CHECKERS:
        # Load the version file for the type checker.
        version_file = root_dir / "results" / type_checker.name / "version.toml"

        try:
            with open(version_file, "rb") as f:
                existing_info = tomli.load(f)
        except FileNotFoundError:
            existing_info = {}

        version = existing_info["version"] or "Unknown version"
        test_duration = existing_info.get("test_duration")

        summary_html += f"<div class='tc-header'><span class='tc-name'>{version}"
        if test_duration is not None:
            summary_html += f"<span class='tc-time'>({test_duration:.2f}sec)</span>\n"
        summary_html += '</div>\n'
        summary_html += '<div class="table_container"><table>\n'
        summary_html += '<tr><th class="column spacer" colspan="4"></th></tr>\n'

        for test_group_name, test_group in test_groups.items():
            tests_in_group = [
                case
                for case in test_cases
                if case.name.startswith(f"{test_group_name}_")
            ]
            
            tests_in_group.sort(key=lambda x: x.name)

            # Are there any test cases in this group?
            if len(tests_in_group) > 0:
                summary_html += '<tr><th class="column" colspan="4">\n'
                summary_html += f'<a class="test_group" href="{test_group.href}">{test_group.name}</a>'
                summary_html += "</th></tr>\n"

                for test_case in tests_in_group:
                    test_case_name = test_case.stem

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
                    notes = results.get("notes", "").replace("\n", "<br>")

                    conformance_class = (
                        "conformant"
                        if conformance == "Pass"
                        else "partially-conformant"
                        if conformance == "Partial"
                        else "not-conformant"
                    )

                    summary_html += f"<tr><th>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</th>"
                    summary_html += f'<th class="column col1">{test_case_name}</th>'
                    summary_html += f'<th class="column col2 {conformance_class}">{conformance}</th>'
                    summary_html += f'<th class="column col3">{notes}</th></tr>\n'

                # Add spacer row after this group to help with readability.
                summary_html += '<tr><th class="column spacer" colspan="4"></th></tr>\n'

        summary_html += "</table></div>\n"

    return summary_html
