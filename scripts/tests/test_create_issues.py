import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import create_issues


class CreateIssuesTests(unittest.TestCase):
    def setUp(self):
        self.issue = {"title": "📋 Missing note", "body": "Add note.md", "labels": ["needs-indexing"]}

    def test_existing_unicode_title_is_not_duplicated(self):
        with patch.object(create_issues.subprocess, "run", return_value=Mock(
            stdout=json.dumps([{"title": self.issue["title"]}])
        )) as run:
            create_issues.publish({"issues": [self.issue]})
        self.assertEqual(run.call_count, 1)

    def test_new_finding_is_created_with_structured_arguments(self):
        with patch.object(create_issues.subprocess, "run", return_value=Mock(stdout="[]")) as run:
            create_issues.publish({"issues": [self.issue]})
        self.assertEqual(run.call_count, 2)
        self.assertEqual(run.call_args.args[0], [
            "gh", "issue", "create", "--title", self.issue["title"],
            "--body", self.issue["body"], "--label", "needs-indexing",
        ])
        self.assertTrue(run.call_args.kwargs["check"])

    def test_lookup_failure_never_creates_an_issue(self):
        with patch.object(create_issues.subprocess, "run", side_effect=subprocess.CalledProcessError(
            1, "gh issue list"
        )) as run:
            with self.assertRaises(subprocess.CalledProcessError):
                create_issues.publish({"issues": [self.issue]})
        self.assertEqual(run.call_count, 1)


if __name__ == "__main__":
    unittest.main()
