# Type System Conformance

## Motivation

[PEP 729](https://peps.python.org/pep-0729/) provides a structured and documented way to specify and evolve the Python type system. In support of this effort, an official [Python typing spec](https://typing.python.org/en/latest/spec/) has been drafted. This spec consolidates details from various historical typing-related PEPs. The spec will be modified over time to clarify unspecified and under-specified parts of the type system. It will also be extended to cover new features of the type system.

Accompanying the typing specification is this conformance test suite which validates the behavior of static type checkers against the specification.

## Structure & Name

This project contains test cases for behaviors defined in the Python typing spec. Tests are structured and grouped in accordance with the specification's chapter headings.

* [concepts](https://typing.python.org/en/latest/spec/concepts.html)
* [annotations](https://typing.python.org/en/latest/spec/annotations.html)
* [specialtypes](https://typing.python.org/en/latest/spec/special-types.html)
* [generics](https://typing.python.org/en/latest/spec/generics.html)
* [qualifiers](https://typing.python.org/en/latest/spec/qualifiers.html)
* [classes](https://typing.python.org/en/latest/spec/class-compat.html)
* [aliases](https://typing.python.org/en/latest/spec/aliases.html)
* [literals](https://typing.python.org/en/latest/spec/literal.html)
* [protocols](https://typing.python.org/en/latest/spec/protocol.html)
* [callables](https://typing.python.org/en/latest/spec/callables.html)
* [constructors](https://typing.python.org/en/latest/spec/constructors.html)
* [overloads](https://typing.python.org/en/latest/spec/overload.html)
* [dataclasses](https://typing.python.org/en/latest/spec/dataclasses.html)
* [typeddicts](https://typing.python.org/en/latest/spec/typeddict.html)
* [tuples](https://typing.python.org/en/latest/spec/tuples.html)
* [namedtuples](https://typing.python.org/en/latest/spec/namedtuples.html)
* [narrowing](https://typing.python.org/en/latest/spec/narrowing.html)
* [directives](https://typing.python.org/en/latest/spec/directives.html)
* [distribution](https://typing.python.org/en/latest/spec/distributing.html)
* [historical](https://typing.python.org/en/latest/spec/historical.html)

A test file is a ".py" file. The file name should start with one of the above names followed by a description of the test (with words separated by underscores). For example, `generics_paramspec_basic_usage.py` would contain the basic usage tests for `ParamSpec`. Each test file can contain multiple individual unit tests, but these tests should be related to each other. If the number of unit tests in a single test file exceeds ten, it may be desirable to split it into separate test files. This will help maintain a consistent level of granularity across tests.

## Notes About Tests

Tests are designed to run on all current and future static type checkers. They must therefore be type-checker agnostic and should not rely on functionality or behaviors that are specific to one type checker or another.

Test cases are meant to be human readable. They should include comments that help explain their purpose (what is being tested, whether an error should be generated, etc.). They should also contain links to the typing spec, discussions, and issue trackers.

The test suite focuses on static type checking not general Python semantics. Tests should therefore focus on static analysis behaviors, not runtime behaviors.

Test cases use the following conventions:

* Lines that are expected to produce a type checker error should have a comment starting with # E",
  either by itself or followed by an explanation after a colon (e.g., "# E: int is not a subtype
  of str"). Such explanatory comments are purely for human understanding, but type checkers are not
  expected to use their exact wording.
* Lines that may produce an error (e.g., because the spec allows multiple behaviors) should be
  marked with "# E?" instead of "# E".
* If a test case tests conformance with a specific passage in the spec, that passage should be
  quoted in a comment prefixed with "# > ".

## Running the Conformance Test Tool

To run the conformance test suite:
* Clone the https://github.com/python/typing repo.
* Create and activate a Python 3.12 virtual environment.
* Switch to the `conformance` subdirectory and install all dependencies (`pip install -r requirements.txt`).
* Switch to the `src` subdirectory and run `python main.py`.

Note that some type checkers may not run on some platforms. If a type checker fails to install, tests will be skipped for that type checker.

## Reporting Conformance Results

Different type checkers report errors in different ways (with different wording in error messages and different line numbers or character ranges for errors). This variation makes it difficult to fully automate test validation given that tests will want to check for both false positive and false negative type errors. Some level of manual inspection will therefore be needed to determine whether a type checker is fully conformant with all tests in any given test file. This "scoring" process is required only when the output of a test changes — e.g. when a new version of that type checker is released and the tests are rerun. We assume that the output of a type checker will be the same from one run to the next unless/until a new version is released that fixes or introduces a bug. In this case, the output will need to be manually inspected and the conformance results re-scored for those tests whose output has changed.

Conformance results are reported and summarized for each supported type checker. Currently, results are reported for mypy, pyre, pyright, and pytype. It is the goal and desire to add additional type checkers over time.

## Adding a New Test Case

To add a new test, create a new ".py" file in the `tests` directory. Its name must begin with one of the above test group names followed by an underscore. Write the contents of the test including a module docstring describing the purpose of the test. Next, run the conformance test tool. This will generate a new `.toml` file in the `results` subdirectory corresponding each type checker. Manually review the output from each type checker and determine whether it conforms to the specification. If so, add `conformant = "Pass"` to the `.toml` file. If it does not fully comply, add `conformant = "Partial"` and a `notes` section detailing where it is not compliant. If the type checker doesn't support the feature in the test add `conformant = "Unsupported"`. Once the conformance status has been updated, rerun the conformance test tool to regenerate the summary report.

## Updating a Test Case

If a test is updated (augmented or fixed), the process is similar to when adding a new test. Run the conformance test tool to generate new results and manually examine the output of each supported type checker. Then update the conformance status accordingly. Once the conformance status has been updated, rerun the conformance test tool to regenerate the summary report.

## Updating a Type Checker

If a new version of a type checker is released, re-run the test tool with the new version. If the type checker output has changed for any test cases, the tool will supply the old and new outputs. Examine these to determine whether the conformance status has changed. Once the conformance status has been updated, re-run the test tool again to regenerate the summary report.

## Automated Conformance Checking

In addition to manual scoring, we provide an experimental tool that automatically checks type checkers for conformance. This tool relies on the "# E" comments present in the stubs and on parsing type checker output. This logic is run automatically as part of the conformance test tool. It produces the following fields in the `.toml` output files:

* `errors_diff`: a string describing all issues found with the type checker's behavior: either expected errors that were not emitted, or extra errors that the conformance test suite does not allow.
* `conformance_automated`: either "Pass" or "Fail" based on whether there are any discrepancies with the expected behavior.

This tool does not yet work reliably on all test cases. The script `conformance/src/unexpected_fails.py` can be run to find all test cases where the automated tool's conformance judgment differs from the manual judgment entered in the `.toml` files.

Some common problems with automated checks:

* Sometimes the spec is imprecise or allows multiple options. In this case, use "# E?" to mark an error as optional.
* Type checkers may produce additional errors for issues unrelated to the topic being tested. In this case, add an extra field `ignore_errors` in the type checker's `.toml` file that contains the text of the irrelevant errors. Any error message that contains a substring in the `ignore_errors` list is ignored. For example, if `ignore_errors = ["Too many arguments"]`, then a mypy error `dataclasses_usage.py:127: error: Too many arguments for "DC7"  [call-arg]` will be ignored.
* Type checkers may differ in the line on which they report an error. In this case, on each of the lines where an error could
  reasonably be shown, write `# E[<tag>]`, where `<tag>` is an arbitrary string that is unique in the file. The test will be marked as passing if the type checker produces an error on exactly one of the lines where this tag appears.

## Contributing

Contributions are welcome!
