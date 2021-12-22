#!/usr/bin/env python3

"""
Generate a summary of last week's issues tagged with "topic: feature".

The summary will include a list of new and changed issues and is sent each
Monday at 0200 CE(S)T to the typing-sig mailing list. Due to limitation
with GitHub Actions, the mail is sent from a private server, currently
maintained by @srittau.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import Any, Iterable, Sequence

import requests

ISSUES_API_URL = "https://api.github.com/repos/python/typing/issues"
ISSUES_URL = "https://github.com/python/typing/issues?q=label%3A%22topic%3A+feature%22"
ISSUES_LABEL = "topic: feature"
SENDER_EMAIL = "Typing Bot <noreply@python.org>"
RECEIVER_EMAIL = "typing-sig@python.org"


@dataclass
class Issue:
    number: int
    title: str
    url: str
    created: datetime.datetime
    user: str
    pull_request: bool = False


def main() -> None:
    since = previous_week_start()
    issues = fetch_issues(since)
    new, updated = split_issues(issues, since)
    print_summary(since, new, updated)


def previous_week_start() -> datetime.date:
    today = datetime.date.today()
    return today - datetime.timedelta(days=today.weekday() + 7)


def fetch_issues(since: datetime.date) -> list[Issue]:
    """Return (new, updated) issues."""
    j = requests.get(
        ISSUES_API_URL,
        params={
            "labels": ISSUES_LABEL,
            "since": f"{since:%Y-%m-%d}T00:00:00Z",
            "per_page": "100",
            "state": "open",
        },
        headers={"Accept": "application/vnd.github.v3+json"},
    ).json()
    assert isinstance(j, list)
    return [parse_issue(j_i) for j_i in j]


def parse_issue(j: Any) -> Issue:
    number = j["number"]
    title = j["title"]
    url = j["html_url"]
    created_at = datetime.datetime.fromisoformat(j["created_at"][:-1])
    user = j["user"]["login"]
    pull_request = "pull_request" in j
    assert isinstance(number, int)
    assert isinstance(title, str)
    assert isinstance(url, str)
    assert isinstance(user, str)
    return Issue(number, title, url, created_at, user, pull_request)


def split_issues(
    issues: Iterable[Issue], since: datetime.date
) -> tuple[list[Issue], list[Issue]]:
    new = []
    updated = []
    for issue in issues:
        if issue.created.date() >= since:
            new.append(issue)
        else:
            updated.append(issue)
    new.sort(key=lambda i: i.number)
    updated.sort(key=lambda i: i.number)
    return new, updated


def print_summary(
    since: datetime.date, new: Sequence[Issue], changed: Sequence[Issue]
) -> None:
    print(f"From: {SENDER_EMAIL}")
    print(f"To: {RECEIVER_EMAIL}")
    print(f"Subject: Opened and changed typing issues week {since:%G-W%V}")
    print()
    print(generate_mail(new, changed))


def generate_mail(new: Sequence[Issue], changed: Sequence[Issue]) -> str:
    if len(new) == 0 and len(changed) == 0:
        s = (
            "No issues or pull requests with the label 'topic: feature' were opened\n"
            "or updated last week in the typing repository on GitHub.\n\n"
        )
    else:
        s = (
            "The following is an overview of all issues and pull requests in the\n"
            "typing repository on GitHub with the label 'topic: feature'\n"
            "that were opened or updated last week, excluding closed issues.\n\n"
            "---------------------------------------------------\n\n"
        )
    if len(new) > 0:
        s += "The following issues and pull requests were opened last week: \n\n"
        s += "".join(generate_issue_text(issue) for issue in new)
        s += "\n---------------------------------------------------\n\n"
    if len(changed) > 0:
        s += "The following issues and pull requests were updated last week: \n\n"
        s += "".join(generate_issue_text(issue) for issue in changed)
        s += "\n---------------------------------------------------\n\n"
    s += (
        "All issues and pull requests with the label 'topic: feature'\n"
        "can be viewed under the following URL:\n\n"
    )
    s += ISSUES_URL
    return s


def generate_issue_text(issue: Issue) -> str:
    s = f"#{issue.number:<5} "
    if issue.pull_request:
        s += "[PR] "
    s += f"{issue.title}\n"
    s += f"       opened by @{issue.user}\n"
    s += f"       {issue.url}\n"
    return s


if __name__ == "__main__":
    main()
