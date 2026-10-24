#!/usr/bin/env python3
"""Print the metrics the self-check recomputes from your geometry - copy them into metrics.json.

    python scripts/compute_metrics.py submissions/<github-login>/<proposal-slug>

Also lists geometry problems that would fail gate G1, with a fix hint.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import xcity_common as xc  # noqa: E402


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    pkg, login, slug = xc.find_package(sys.argv[1])
    geo = xc.load_geometry(pkg)
    empty = [k for k, v in geo.items() if not v]
    if len(empty) == len(geo):
        raise SystemExit("every geometry file under %s/geometry is empty - nothing to compute" % os.path.relpath(pkg, xc.ROOT))
    probs = xc.geometry_problems(geo)
    c = xc.compute_metrics(pkg, geo)
    print(json.dumps({k: c[k] for k in xc.COMPUTED_KEYS} | {"land_use_ha": c["land_use_ha"], "network_km": c["network_km"]},
                     ensure_ascii=False, indent=2))
    for k in empty:
        print("note: geometry/%s.geojson has no features" % k, file=sys.stderr)
    for p in probs:
        print("problem: " + p, file=sys.stderr)
    sys.exit(1 if probs else 0)


if __name__ == "__main__":
    main()
