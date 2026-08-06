"""Nightly integrity check for daily-learning repo.

Checks:
  1. Stale .txt files (should be .md with template)
  2. Notes missing from INDEX.md
  3. INDEX.md entries pointing to deleted files (broken links)
  4. 7-day inactivity warning
"""

import json
import re
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

TIL_DIRS = ["til/ai", "til/python", "til/devops", "til/sys-design"]
PAPERS_DIR = "papers"
LEETCODE_DIRS = [
    "leetcode/array", "leetcode/dp", "leetcode/tree",
    "leetcode/stack-queue", "leetcode/sliding-window", "leetcode/math",
]
INACTIVITY_DAYS = 7


def run_git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", "-C", str(REPO_ROOT)] + args,
        capture_output=True, text=True,
    )
    result.check_returncode()
    return result.stdout.strip()


def find_md_notes(dirs: list[str]) -> list[Path]:
    """Find actual .md notes in dirs (exclude template.md)."""
    notes = []
    for d in dirs:
        folder = REPO_ROOT / d
        if not folder.exists():
            continue
        for f in folder.glob("*.md"):
            if f.name == "template.md":
                continue
            notes.append(f)
    return sorted(notes)


def find_txt_files() -> list[Path]:
    """Find any .txt files — these should be converted."""
    txt_files = []
    for root_dir in ["til", "leetcode", "papers"]:
        folder = REPO_ROOT / root_dir
        if folder.exists():
            txt_files.extend(folder.rglob("*.txt"))
    return sorted(txt_files)


def parse_index_entries() -> set[str]:
    """Extract all filenames mentioned in INDEX.md as links."""
    index = REPO_ROOT / "INDEX.md"
    if not index.exists():
        return set()

    text = index.read_text(encoding="utf-8")
    # Match markdown links: [text](path/to/file.md)
    pattern = r'\]\(([^)]+\.md)\)'
    entries = set()
    for m in re.finditer(pattern, text):
        path = m.group(1)
        entries.add(Path(path).name)
    return entries


def check_inactivity() -> int | None:
    """Return days since last commit, or None if error."""
    try:
        last_commit = run_git(["log", "-1", "--format=%ct"])
        last_ts = datetime.fromtimestamp(int(last_commit), tz=timezone.utc)
        now = datetime.now(tz=timezone.utc)
        return (now - last_ts).days
    except Exception:
        return None


def main() -> int:
    issues: list[dict] = []

    # ---- 1. Stale .txt files ----
    txt_files = find_txt_files()
    if txt_files:
        issues.append({
            "title": f"📝 {len(txt_files)} `.txt` file(s) need migration to `.md`",
            "body": "These should be converted to markdown with the TIL/paper template:\n\n"
                    + "\n".join(f"- `{f.relative_to(REPO_ROOT)}`" for f in txt_files),
            "labels": ["needs-formatting"],
        })

    # ---- 2. Notes missing from INDEX.md ----
    note_dirs = TIL_DIRS + [PAPERS_DIR] + LEETCODE_DIRS
    md_notes = find_md_notes(note_dirs)
    index_entries = parse_index_entries()

    missing_from_index = [
        n for n in md_notes
        if n.name not in index_entries
    ]
    if missing_from_index:
        issues.append({
            "title": f"📋 {len(missing_from_index)} note(s) missing from INDEX.md",
            "body": "Add these to INDEX.md:\n\n"
                    + "\n".join(f"- `{f.relative_to(REPO_ROOT)}`" for f in missing_from_index),
            "labels": ["needs-indexing"],
        })

    # ---- 3. Broken INDEX.md links (stale entries) ----
    note_names = {n.name for n in md_notes}
    broken = index_entries - note_names
    if broken:
        issues.append({
            "title": f"🔗 {len(broken)} broken link(s) in INDEX.md",
            "body": "These files are referenced in INDEX.md but don't exist:\n\n"
                    + "\n".join(f"- `{f}`" for f in sorted(broken)),
            "labels": ["needs-cleanup"],
        })

    # ---- 4. Inactivity check ----
    days = check_inactivity()
    if days is not None and days >= INACTIVITY_DAYS:
        issues.append({
            "title": f"⏰ No commits for {days} days",
            "body": "Time to write something. Even one TIL note or one LeetCode problem counts.",
            "labels": ["motivation"],
        })

    # ---- Output ----
    output = {
        "check_time": datetime.now(tz=timezone.utc).isoformat(),
        "issue_count": len(issues),
        "issues": issues,
    }

    print(json.dumps(output, indent=2, ensure_ascii=False))

    if issues:
        # Also output in GitHub Actions ::notice format
        for issue in issues:
            print(f"::notice title={issue['title']}::{issue['body'].split(chr(10))[0]}")

    return 0 if not issues else 1


if __name__ == "__main__":
    sys.exit(main())
