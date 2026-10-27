#!/usr/bin/env python3
"""Create an empty submission package from templates/.

    python scripts/scaffold_submission.py --login <github-login> --slug <proposal-slug> \
        --title "Scheme title" --nodes B03 C03 A03

Creates submissions/<github-login>/<proposal-slug>/ with every required file in place. Nothing is
overwritten: if the directory exists the script stops.
"""
import argparse
import datetime
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import xcity_common as xc  # noqa: E402
from node_selection import selection_errors  # noqa: E402

GEOMETRY_NOTES = {
    "structure": "Scale 1, the whole site. Polygons covering the whole site at structural level. "
                 "properties.system: energy_compute | agri_production | living | industry | port | reserve. "
                 "Required base zones: plan_role=base_zoning, district_id, name, primary_use, basis_ref; cover the full issued site without overlap. Optional overlapping system relations use plan_role=system_overlay. See docs/whole-site-zoning-workflow.md.",
    "master_area": "Scale 2. Exactly one Polygon (or MultiPolygon): the master design area you drew. Inside the site.",
    "land_use": "Scale 2. Polygons inside the master area. properties.use: residential | mixed_use | civic | compute | "
                "energy | industry | logistics | agriculture | open_space | infrastructure | reserve.",
    "buildings": "Scale 2 and 3. Building footprints. properties.floors (integer >= 1), properties.use; optional height_m, "
                 "name, and form: canopy for a roof on posts (drawn hatched, excluded from footprint and GFA).",
    "movement": "LineStrings with properties.network: people | machine | shared, optional shaded: true|false, name. "
                "Add road_class: primary | secondary | local; primary and secondary full-site routes are required. network describes users, not road hierarchy. Points with properties.kind: interface mark every at-grade human-machine interface (M6).",
    "phasing": "Polygons with properties.phase: 1 | 2 | 3, name, and trigger (observable condition) for phases 2 and 3.",
    "nodes": "Exactly three Polygons, one node per group, properties.node_id: A01-A03, B01-B03, C01-C04 (brief/site-package/nodes/design_nodes.json), "
             "name, why. Optional camera hints: eye_from [lon, lat], eye_to [lon, lat], aerial_from [lon, lat], "
             "aerial_height_m.",
}


def fill(text, ctx):
    for k, v in ctx.items():
        text = text.replace("{{%s}}" % k, v)
    return text


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--login", required=True, help="your GitHub login (case as on GitHub)")
    ap.add_argument("--slug", required=True, help="lowercase-with-hyphens, 3-64 characters")
    ap.add_argument("--title", default="Untitled scheme")
    ap.add_argument("--nodes", nargs=3, default=["C01", "A01", "B01"], metavar="NODE_ID",
                    help="one node from each group; see brief/site-package/nodes/design_nodes.json")
    a = ap.parse_args()
    if not re.match(r"^[a-z0-9][a-z0-9-]{2,63}$", a.slug):
        raise SystemExit("slug must be lowercase letters, digits and hyphens, 3-64 characters")
    errors = selection_errors(a.nodes)
    if errors:
        raise SystemExit("--nodes: " + " ".join(errors))
    pkg = os.path.join(xc.ROOT, "submissions", a.login, a.slug)
    if os.path.exists(pkg):
        raise SystemExit("already exists: %s" % os.path.relpath(pkg, xc.ROOT))
    today = datetime.date.today().isoformat()
    ctx = {"title": a.title, "slug": a.slug, "github": a.login, "today": today,
           "node_1": a.nodes[0], "node_2": a.nodes[1], "node_3": a.nodes[2],
           "responsible_party": "(fill in)"}
    tpl = os.path.join(xc.ROOT, "templates")
    for d in ("geometry", "figures", "drawings", "report", "media"):
        os.makedirs(os.path.join(pkg, d), exist_ok=True)
    for name in ("manifest.json", "metrics.json", "compliance_matrix.json", "assumptions.json", "sources.json",
                 "image_provenance.json", "changelog.md", "design_depth_matrix.json", "phasing_programme.json"):
        with open(os.path.join(tpl, name), encoding="utf-8") as f:
            text = fill(f.read(), ctx)
        with open(os.path.join(pkg, name), "w", encoding="utf-8") as f:
            f.write(text)
    with open(os.path.join(tpl, "proposal.template.md"), encoding="utf-8") as f:
        text = fill(f.read(), ctx)
    with open(os.path.join(pkg, "proposal.md"), "w", encoding="utf-8") as f:
        f.write(text)
    with open(os.path.join(tpl, "copyright_statement.md"), encoding="utf-8") as f:
        text = fill(f.read(), ctx)
    with open(os.path.join(pkg, "report", "copyright_statement.md"), "w", encoding="utf-8") as f:
        f.write(text)
    with open(os.path.join(tpl, "presentation.template.md"), encoding="utf-8") as f:
        with open(os.path.join(pkg, "report", "presentation-plan.md"), "w", encoding="utf-8") as out:
            out.write(f.read())
    for name, note in GEOMETRY_NOTES.items():
        xc.write_json(os.path.join(pkg, "geometry", name + ".geojson"),
                      {"type": "FeatureCollection", "name": name, "_note": note, "features": []})
    open(os.path.join(pkg, "media", ".gitkeep"), "w").close()
    print("created %s" % os.path.relpath(pkg, xc.ROOT))
    print("next: write geometry/, then python scripts/compute_metrics.py %s; fill metrics.json, assumptions.json,"
          " sources.json, manifest.json, report/copyright_statement.md and proposal.md - see AGENTS.md"
          % os.path.relpath(pkg, xc.ROOT))


if __name__ == "__main__":
    main()
