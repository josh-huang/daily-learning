import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import check_integrity


class IntegrityOutputTests(unittest.TestCase):
    def test_findings_leave_stdout_as_one_json_document(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "til/python").mkdir(parents=True)
            (root / "til/python/unindexed.md").write_text("A note")
            output, notices = io.StringIO(), io.StringIO()
            with patch.object(check_integrity, "REPO_ROOT", root), patch.object(
                check_integrity, "check_inactivity", return_value=None
            ), contextlib.redirect_stdout(output), contextlib.redirect_stderr(notices):
                code = check_integrity.main()
            self.assertEqual(code, 1)
            report = json.loads(output.getvalue())
            self.assertEqual(report["issue_count"], 1)
            self.assertIn("::notice", notices.getvalue())


if __name__ == "__main__":
    unittest.main()
