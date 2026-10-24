#!/usr/bin/env python3
"""CI: a pull request may change only submissions/<its author's login>/.

    python scripts/check_pr_paths.py --author <github-login> --base origin/main

Prints the package directories that changed (one per line, for the next CI step) and exits non-zero
if anything outside submissions/<author>/ changed. Maintainers' pull requests are not run through this.
"""
import argparse
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import xcity_common as xc  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--author", required=True)
    ap.add_argument("--base", default="origin/main")
    ap.add_argument("--out", help="write changed package paths to this file")
    a = ap.parse_args()
    files = subprocess.run(["git", "diff", "--name-only", "--diff-filter=ACMRTD", "%s...HEAD" % a.base],
                           cwd=xc.ROOT, capture_output=True, text=True, check=True).stdout.split()
    prefix = "submissions/%s/" % a.author
    bad = [f for f in files if not f.lower().startswith(prefix.lower())]
    pkgs = sorted({"/".join(f.split("/")[:3]) for f in files if f.lower().startswith(prefix.lower())
                   and len(f.split("/")) > 3})
    if a.out:
        with open(a.out, "w") as fh:
            fh.write("\n".join(pkgs) + ("\n" if pkgs else ""))
    for p in pkgs:
        print(p)
    if bad:
        print("\nGATE-G2: this pull request changes files outside %s:" % prefix, file=sys.stderr)
        for f in bad[:50]:
            print("  " + f, file=sys.stderr)
        sys.exit(1)
    if not pkgs:
        print("no submission package changed", file=sys.stderr)


if __name__ == "__main__":
    main()
