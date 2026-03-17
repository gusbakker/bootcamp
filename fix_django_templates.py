#!/usr/bin/env python3
"""
Collapses multiline Django template tags into single lines.

Usage:
    python fix_django_templates.py                  # fix all templates in ./templates
    python fix_django_templates.py path/to/file.html
    python fix_django_templates.py path/to/dir
"""

import re
import sys
from pathlib import Path


def fix_template_tags(source: str) -> str:
    """Collapse newlines/extra spaces inside {{ }} and {% %} blocks."""
    def collapse(match: re.Match) -> str:
        inner = match.group(0)
        # Replace any whitespace sequences (including newlines) with a single space
        collapsed = re.sub(r"\s+", " ", inner)
        # Clean up spaces right after opening and before closing tags: {{ x }} → {{x}}
        collapsed = re.sub(r"(\{\{)\s+", "{{", collapsed)
        collapsed = re.sub(r"\s+(\}\})", "}}", collapsed)
        collapsed = re.sub(r"(\{%)\s+", "{% ", collapsed)
        collapsed = re.sub(r"\s+(%\})", " %}", collapsed)
        return collapsed

    # Match {{ ... }} or {% ... %} potentially spanning multiple lines
    pattern = re.compile(r"\{\{.*?\}\}|\{%.*?%\}", re.DOTALL)
    return pattern.sub(collapse, source)


def process_file(path: Path, dry_run: bool = False) -> bool:
    """Fix a single file. Returns True if changes were made."""
    original = path.read_text(encoding="utf-8")
    fixed = fix_template_tags(original)

    if fixed == original:
        return False

    if dry_run:
        print(f"[dry-run] Would fix: {path}")
    else:
        path.write_text(fixed, encoding="utf-8")
        print(f"Fixed: {path}")

    return True


def process_path(target: Path, dry_run: bool = False):
    extensions = {".html", ".txt"}  # add more if needed

    if target.is_file():
        files = [target]
    elif target.is_dir():
        files = [f for f in target.rglob("*") if f.suffix in extensions]
    else:
        print(f"Path not found: {target}")
        sys.exit(1)

    changed = sum(process_file(f, dry_run) for f in files)
    total = len(files)
    print(f"\nDone. {changed}/{total} file(s) updated.")


if __name__ == "__main__":
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    args = [a for a in args if a != "--dry-run"]

    target = Path(args[0]) if args else Path("bootcamp/templates")
    process_path(target, dry_run=dry_run)