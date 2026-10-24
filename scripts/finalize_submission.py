#!/usr/bin/env python3
"""Make a package ready for review: redraw if needed, render the HTML, mark it ready, run the gates.

    python scripts/finalize_submission.py submissions/<github-login>/<proposal-slug>

Steps
  1. If figures/stamp.json does not match the current geometry, metrics and manifest, run make_figures.py.
  2. Render report/proposal.html from proposal.md.
  3. Set manifest.package_state = "ready_for_review" and manifest.updated = today.
  4. Run the twelve gates and write self_check.json.
Exits non-zero if any gate fails - fix what it says and run it again. Open the pull request only on PASS.
"""
import argparse
import datetime
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import xcity_common as xc  # noqa: E402
import self_check_submission as sc  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def run(*args):
    print("$ python " + " ".join(os.path.relpath(a, xc.ROOT) if os.path.isabs(a) else a for a in args))
    r = subprocess.run([sys.executable] + list(args), cwd=xc.ROOT)
    if r.returncode:
        raise SystemExit(r.returncode)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("package")
    ap.add_argument("--redraw", action="store_true", help="redraw the figures even if they are current")
    a = ap.parse_args()
    pkg, login, slug = xc.find_package(a.package)
    man_p = os.path.join(pkg, "manifest.json")
    man = xc.load_json(man_p)
    man["package_state"] = "ready_for_review"
    man["updated"] = datetime.date.today().isoformat()
    xc.write_json(man_p, man)
    stamp_p = os.path.join(pkg, "figures", "stamp.json")
    stale = a.redraw or not os.path.exists(stamp_p)
    if not stale:
        st = xc.load_json(stamp_p)
        files = st.get("files") or {}
        need = xc.REQUIRED_FIGURES + ["drawings/a3-booklet.pdf", "drawings/a0-board.pdf"]
        stale = (st.get("input_sha256") != xc.figure_input_hash(pkg) or any(r not in files for r in need)
                 or any(not os.path.exists(os.path.join(pkg, r)) or xc.sha256_file(os.path.join(pkg, r)) != h
                        for r, h in files.items()))
    if stale:
        run(os.path.join(HERE, "make_figures.py"), pkg)
    else:
        print("figures are current (input %s)" % xc.figure_input_hash(pkg)[:12])
    run(os.path.join(HERE, "render_proposal_html.py"), pkg)
    r = sc.check(pkg, write=True)
    sc.report(r)
    if r["pass"]:
        print("\nready: open a pull request that changes only submissions/%s/%s/" % (login, slug))
    sys.exit(0 if r["pass"] else 1)


if __name__ == "__main__":
    main()
