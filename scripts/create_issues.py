"""Publish an integrity report using gh, preserving exact-title deduplication."""

import json
import subprocess
import sys
from pathlib import Path


def publish(report: dict) -> None:
    for issue in report["issues"]:
        title = issue["title"]
        result = subprocess.run(
            ["gh", "issue", "list", "--state", "open", "--search", title, "--json", "title"],
            capture_output=True, text=True, check=True,
        )
        existing = json.loads(result.stdout)
        if any(item["title"] == title for item in existing):
            continue
        command = ["gh", "issue", "create", "--title", title, "--body", issue["body"]]
        if issue.get("labels"):
            command.extend(["--label", ",".join(issue["labels"])])
        subprocess.run(command, check=True)


def main() -> None:
    report = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    publish(report)


if __name__ == "__main__":
    main()
