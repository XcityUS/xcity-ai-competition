#!/usr/bin/env python3
"""Build the full, illustrated English and Chinese Design Briefs (31 pages each).

Sources and dependencies: scripts/practice-brief/README.md.
"""
from pathlib import Path
import subprocess
import sys
ROOT = Path(__file__).resolve().parent
for language in ("en", "zh"):
    subprocess.run([sys.executable, str(ROOT / "practice-brief" / f"build_{language}.py")], check=True)
