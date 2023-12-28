# Type System Conformance

## Motivation

[PEP 729](https://peps.python.org/pep-0729/) provides a structured and documented way to specify and evolve the Python type system. In support of this effort, an official [Python typing spec](https://github.com/python/typing/tree/main/docs/spec) has been drafted. This spec consolidates details from various historical typing-related PEPs. The spec will be modified over time to clarify unspecified and under-specified parts of the type system. It will also be extended to cover new features of the type system.

Accompanying the typing specification is this conformance test suite which validates the behavior of static type checkers against the specification.

## Structure & Name

This project contains test cases for behaviors defined in the Python typing spec. Tests are structured and grouped in accordance with the specification's chapter headings.

* [concepts](https://typing.readthedocs.io/en/latest/spec/concepts.html)
* [annotations](https://typing.readthedocs.io/en/latest/spec/annotations.html)
* [specialtypes](https://typing.readthedocs.io/en/latest/spec/special-types.html)
* [generics](https://typing.readthedocs.io/en/latest/spec/generics.html)
* [qualifiers](https://typing.readthedocs.io/en/latest/spec/qualifiers.html)
* [classes](https://typing.readthedocs.io/en/latest/spec/class-compat.html)
* [aliases](https://typing.readthedocs.io/en/latest/spec/aliases.html)
* [literals](https://typing.readthedocs.io/en/latest/spec/literal.html)
* [protocols](https://typing.readthedocs.io/en/latest/spec/protocol.html)
* [callables](https://typing.readthedocs.io/en/latest/spec/callables.html)
* [overloads](https://typing.readthedocs.io/en/latest/spec/overload.html)
* [dataclasses](https://typing.readthedocs.io/en/latest/spec/dataclasses.html)
* [typeddicts](https://typing.readthedocs.io/en/latest/spec/typeddict.html)
* [narrowing](https://typing.readthedocs.io/en/latest/spec/narrowing.html)
* [directives](https://typing.readthedocs.io/en/latest/spec/directives.html)
* [distribution](https://typing.readthedocs.io/en/latest/spec/distributing.html)
* [historical](https://typing.readthedocs.io/en/latest/spec/historical.html)

A test file is a ".py" file. The file name should start with one of the above names followed by a description of the test (with words separated by underscores). For example, `generics_paramspec_basic_usage.py` would contain the basic usage tests for `ParamSpec`. Each test file can contain multiple individual unit tests, but these tests should be related to each other. If the number of unit tests in a single test file exceeds ten, it may be desirable to split it into separate test files. This will help maintain a consistent level of granularity across tests.

## Notes About Tests

Tests are designed to run on all current and future static type checkers. They must therefore be type-checker agnostic and should not rely on functionality or behaviors that are specific to one type checker or another.

Test cases are meant to be human readable. They should include comments that help explain their purpose (what is being tested, whether an error should be generated, etc.). They should also contain links to the typing spec, discussions, and issue trackers.

The test suite focuses on static type checking not general Python semantics. Tests should therefore focus on static analysis behaviors, not runtime behaviors.

## Running the Conformance Test Tool

To run the conformance test suite:
* Clone the https://github.com/python/typing repo.
* Create and activate a Python 3.12 virtual environment.
* Switch to the `conformance` subdirectory and install all dependencies (`pip install -r requirements.txt`).
* Switch to the `src` subdirectory and run `python main.py`.

Note that some type checkers may not run on some platforms. For example, pytype cannot be installed on Windows. If a type checker fails to install, tests will be skipped for that type checker.

## Reporting Conformance Results

Different type checkers report errors in different ways (with different wording in error messages and different line numbers or character ranges for errors). This variation makes it difficult to fully automate test validation given that tests will want to check for both false positive and false negative type errors. Some level of manual inspection will therefore be needed to determine whether a type checker is fully conformant with all tests in any given test file. This "scoring" process is required only when the output of a test changes — e.g. when a new version of that type checker is released and the tests are rerun. We assume that the output of a type checker will be the same from one run to the next unless/until a new version is released that fixes or introduces a bug. In this case, the output will need to be manually inspected and the conformance results re-scored for those tests whose output has changed.

Conformance results are reported and summarized for each supported type checker. Initially, results will be reported for mypy and pyright. It is the goal and desire to add additional type checkers over time.

## Adding a New Test Case

To add a new test, create a new ".py" file in the `tests` directory. Its name must begin with one of the above test group names followed by an underscore. Write the contents of the test including a module docstring describing the purpose of the test. Next, run the conformance test tool. This will generate a new `.toml` file in the `results` subdirectory corresponding each type checker. Manually review the output from each type checker and determine whether it conforms to the specification. If so, add `conformant = "Pass"` to the `.toml` file. If it does not fully comply, add `conformant = "Partial"` and a `notes` section detailing where it is not compliant. If the type checker doesn't support the feature in the test add `conformant = "Unsupported"`. Once the conformance status has been updated, rerun the conformance test tool to regenerate the summary report.

## Updating a Test Case

If a test is updated (augmented or fixed), the process is similar to when adding a new test. Run the conformance test tool to generate new results and manually examine the output of each supported type checker. Then update the conformance status accordingly. Once the conformance status has been updated, rerun the conformance test tool to regenerate the summary report.

## Updating a Type Checker

If a new version of a type checker is released, re-run the test tool with the new version. If the type checker output has changed for any test cases, the tool will supply the old and new outputs. Examine these to determine whether the conformance status has changed. Once the conformance status has been updated, re-run the test tool again to regenerate the summary report.

## Contributing

Contributions are welcome!
