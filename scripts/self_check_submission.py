#!/usr/bin/env python3
"""The twelve gates, run locally and in CI.

    python scripts/self_check_submission.py submissions/<github-login>/<proposal-slug>
    python scripts/self_check_submission.py --all            # every package under submissions/

Writes self_check.json into the package (unless --no-write) and exits non-zero if any gate fails.
Gates are defined in brief/evaluation.json; requirements in brief/requirements.json.
"""
import argparse
import datetime
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import presentation
import spatial_checks
import design_depth
import xcity_common as xc  # noqa: E402
from node_selection import selection_errors  # noqa: E402
from shapely.geometry import Point  # noqa: E402
from shapely.ops import unary_union  # noqa: E402

REQ = xc.load_json(os.path.join(xc.ROOT, "brief", "requirements.json"))
EVAL = xc.load_json(os.path.join(xc.ROOT, "brief", "evaluation.json"))
TASKS = xc.load_json(os.path.join(xc.ROOT, "brief", "agent_taskbook.json"))
NODE_IDS = {n["id"] for n in xc.site_json("nodes/design_nodes.json")["nodes"]}
SITE_SRC = {s["id"] for s in xc.site_json("sources.json")["sources"]}
EVIDENCE = set(REQ["evidence_tags"])
SYSTEMS = set(REQ["systems"])
USES = set(REQ["land_uses"])
NETWORKS = set(REQ["networks"])
AUTONOMY = set(EVAL["autonomy_classes"]["classes"])
TOL = 0.02
EXAMPLE_DIR = os.path.join(xc.ROOT, "submissions", "EXAMPLE-agent")
SECRET_PATTERNS = [
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "a private key block"),
    (r"\bAKIA[0-9A-Z]{16}\b", "an AWS access key id"),
    (r"\bgh[pousr]_[A-Za-z0-9]{36,}\b", "a GitHub credential"),
    (r"\bsk-[A-Za-z0-9]{32,}\b", "an API secret key"),
    (r"\bxox[abpr]-[A-Za-z0-9-]{10,}\b", "a Slack credential"),
]
NETWORK_PATTERNS = [
    (r"""<(?:script|img|iframe|source|video|audio|embed|track)\b[^>]*\bsrc\s*=\s*["']?\s*(?:https?:)?//""", "loads a remote src"),
    (r"""<link\b[^>]*\bhref\s*=\s*["']?\s*(?:https?:)?//""", "links a remote stylesheet or font"),
    (r"""url\(\s*["']?\s*(?:https?:)?//""", "CSS url() to the network"),
    (r"""@import\s+(?:url\()?\s*["']?\s*(?:https?:)?//""", "CSS @import from the network"),
    (r"""\bfetch\s*\(\s*["'`]\s*(?:https?:)?//""", "fetch() to the network"),
    (r"""\bXMLHttpRequest\b""", "XMLHttpRequest"),
    (r"""\bnew\s+WebSocket\b""", "WebSocket"),
    (r"""<iframe\b""", "an iframe"),
    (r"""\bimport\s[^;]*?from\s*["']https?://""", "an ES module import from the network"),
]


class Gate:
    def __init__(self, gid):
        g = next(x for x in EVAL["gates"] if x["id"] == gid)
        self.id, self.title, self.msgs, self.ok, self.notes = gid, g["title"], [], True, []

    def fail(self, msg):
        self.ok = False
        self.msgs.append(msg)

    def note(self, msg):
        self.notes.append(msg)

    def out(self):
        d = {"id": self.id, "title": self.title, "pass": self.ok, "messages": self.msgs}
        if self.notes:
            d["notes"] = self.notes
        return d


def jload(pkg, rel, gate):
    p = os.path.join(pkg, rel)
    if not os.path.exists(p):
        return None
    try:
        return xc.load_json(p)
    except Exception as e:  # noqa: BLE001
        gate.fail("%s is not valid JSON: %s" % (rel, e))
        return None


def nonempty(v, n=1):
    return isinstance(v, str) and len(v.strip()) >= n and "{{" not in v


def close(a, b):
    if isinstance(b, int) and not isinstance(b, bool) and isinstance(a, (int, float)) and float(a).is_integer():
        return int(a) == b
    try:
        a, b = float(a), float(b)
    except (TypeError, ValueError):
        return False
    if b == 0:
        return abs(a) < 1e-9
    return abs(a - b) <= TOL * abs(b)


def check(pkg_path, write=True):
    pkg, login, slug = xc.find_package(pkg_path)
    G = {g["id"]: Gate(g["id"]) for g in EVAL["gates"]}
    g1, g2, g3, g4, g5, g6 = (G[k] for k in ("GATE-G1-PACKAGE", "GATE-G2-PATH", "GATE-G3-SAMPLE-DATA",
                                             "GATE-G4-RECONCILE", "GATE-G5-OFFLINE", "GATE-G6-TASKBOOK"))
    g7, g8, g9, g10, g11, g12 = (G[k] for k in ("GATE-G7-EVIDENCE", "GATE-G8-DISCLOSURE", "GATE-G9-BOUNDARIES",
                                                "GATE-G10-FIGURES", "GATE-G11-TRADEOFF", "GATE-G12-DEPTH"))
    warnings = []

    # ---------------------------------------------------------------- G1 package
    for rel in xc.REQUIRED_FILES + xc.REQUIRED_FIGURES:
        if not os.path.exists(os.path.join(pkg, rel)):
            g1.fail("missing %s" % rel)
    man = jload(pkg, "manifest.json", g1) or {}
    mdoc = jload(pkg, "metrics.json", g1) or {}
    comp = jload(pkg, "compliance_matrix.json", g1) or {}
    asm = jload(pkg, "assumptions.json", g1) or {}
    src = jload(pkg, "sources.json", g1) or {}
    prov = jload(pkg, "image_provenance.json", g1) or {}
    for k in ("title", "slug", "summary", "language"):
        if not nonempty(man.get(k)):
            g1.fail("manifest.json: '%s' is missing or still a placeholder" % k)
    if man.get("language") != "en":
        g1.fail("Final public submissions must use English (manifest.language must be en).")
    g1.note("English is required for the public title, narrative, summary, booklet, drawing labels and legends; the language of raster images needs human review.")
    if man.get("summary") and len(man["summary"]) > 700:
        g1.fail("manifest.json: summary is longer than 700 characters")
    tman_p = os.path.join(xc.ROOT, "templates", "manifest.json")
    tman = xc.load_json(tman_p) if os.path.exists(tman_p) else {}
    for k in ("summary", "nodes_reason"):
        if not nonempty(man.get(k), 20) or man.get(k) == tman.get(k):
            g1.fail("manifest.json: '%s' is missing, too short or still the template text" % k)
    for k in ("author", "agent", "autonomy", "tradeoff", "design_depth"):
        if not isinstance(man.get(k), dict):
            g1.fail("manifest.json: '%s' must be an object" % k)
    if not isinstance(mdoc.get("metrics"), list):
        g1.fail("metrics.json: 'metrics' must be a list")
    if not isinstance(comp.get("items"), list):
        g1.fail("compliance_matrix.json: 'items' must be a list")
    if not isinstance(asm.get("assumptions"), list):
        g1.fail("assumptions.json: 'assumptions' must be a list")
    if not isinstance(src.get("sources"), list):
        g1.fail("sources.json: 'sources' must be a list")
    if not isinstance(prov.get("images"), list):
        g1.fail("image_provenance.json: 'images' must be a list")
    geo = {}
    expect = {"structure": ("Polygon", "MultiPolygon"), "master_area": ("Polygon", "MultiPolygon"),
              "land_use": ("Polygon", "MultiPolygon"), "buildings": ("Polygon", "MultiPolygon"),
              "movement": ("LineString", "MultiLineString", "Point", "MultiPoint"),
              "phasing": ("Polygon", "MultiPolygon"), "nodes": ("Polygon", "MultiPolygon")}
    for rel in xc.GEOMETRY_FILES:
        name = os.path.splitext(os.path.basename(rel))[0]
        p = os.path.join(pkg, rel)
        if not os.path.exists(p):
            geo[name] = []
            continue
        try:
            fc = xc.load_json(p)
            assert fc.get("type") == "FeatureCollection", "not a FeatureCollection"
            geo[name] = xc.features(p)
        except Exception as e:  # noqa: BLE001
            g1.fail("%s: %s" % (rel, e))
            geo[name] = []
            continue
        if not geo[name]:
            g1.fail("%s has no features" % rel)
        for i, (props, g) in enumerate(geo[name]):
            if g.geom_type not in expect[name]:
                g1.fail("%s feature %d: %s is not allowed here. %s" % (rel, i, g.geom_type, xc.TYPE_HINT))
            elif g.is_empty:
                g1.fail("%s feature %d is empty" % (rel, i))
            elif g.bounds[0] < -180 or g.bounds[2] > 180 or g.bounds[1] < -90 or g.bounds[3] > 90:
                g1.fail("%s feature %d: coordinates are not lon/lat (EPSG:4326)" % (rel, i))
    for i, (p, g) in enumerate(geo.get("structure", [])):
        if p.get("system") not in SYSTEMS:
            g1.fail("structure.geojson feature %d: system %r is not one of %s" % (i, p.get("system"), sorted(SYSTEMS)))
    for i, (p, g) in enumerate(geo.get("land_use", [])):
        if p.get("use") not in USES:
            g1.fail("land_use.geojson feature %d: use %r is not one of %s" % (i, p.get("use"), sorted(USES)))
    for i, (p, g) in enumerate(geo.get("buildings", [])):
        try:
            f = float(p.get("floors"))
            assert f >= 1
        except Exception:  # noqa: BLE001
            g1.fail("buildings.geojson feature %d: floors must be a number >= 1" % i)
    for i, (p, g) in enumerate(geo.get("movement", [])):
        if g.geom_type.endswith("LineString") and p.get("network") not in NETWORKS:
            g1.fail("movement.geojson feature %d: network %r is not one of %s" % (i, p.get("network"), sorted(NETWORKS)))
        if g.geom_type.endswith("Point") and p.get("kind") != "interface":
            g1.fail("movement.geojson feature %d: a Point must have kind = interface" % i)
    phases = set()
    for i, (p, g) in enumerate(geo.get("phasing", [])):
        try:
            n = int(p.get("phase"))
            assert n in (1, 2, 3)
            phases.add(n)
            if n > 1 and not nonempty(p.get("trigger"), 10):
                g1.fail("phasing.geojson feature %d: phase %d needs an observable trigger" % (i, n))
        except Exception:  # noqa: BLE001
            g1.fail("phasing.geojson feature %d: phase must be 1, 2 or 3" % i)
    if geo.get("phasing") and phases != {1, 2, 3}:
        g1.fail("phasing.geojson must contain phases 1, 2 and 3 (found %s)" % sorted(phases))
    if len(geo.get("master_area", [])) != 1:
        g1.fail("master_area.geojson must contain exactly one feature (found %d)" % len(geo.get("master_area", [])))
    # proposal
    prop_path = os.path.join(pkg, "proposal.md")
    prop = open(prop_path, encoding="utf-8").read() if os.path.exists(prop_path) else ""
    heads = xc.proposal_headings(prop)
    for n in range(1, 15):
        if not any(h.startswith("## %d." % n) for h in heads):
            g1.fail("proposal.md: numbered section '## %d.' is missing" % n)
    if "{{" in prop:
        g1.fail("proposal.md still contains template placeholders {{...}}")
    tmpl = os.path.join(xc.ROOT, "templates", "proposal.template.md")
    guide = {l.strip() for l in open(tmpl, encoding="utf-8") if l.startswith("> ") and "{{" not in l} if os.path.exists(tmpl) else set()
    leftover = [l for l in prop.splitlines() if l.strip() in guide]
    if leftover:
        g1.fail("proposal.md still contains %d template guidance lines (starting with '>')" % len(leftover))
    tlines = {l.strip() for l in open(tmpl, encoding="utf-8")} if os.path.exists(tmpl) else set()
    own = "\n".join(l for l in prop.splitlines() if l.strip() not in tlines and not l.strip().startswith("!["))
    if not own.strip():
        g1.fail("proposal.md has no entrant-authored explanation; a word count is not a design-depth test")
    if re.search(r"^> (XCITY AI Competition · San Juan, 1,656 km²|Write this as an urban design statement)", prop, re.M):
        g1.fail("proposal.md still contains the template header lines starting with '>'")
    cs = os.path.join(pkg, "report", "copyright_statement.md")
    if os.path.exists(cs):
        t = open(cs, encoding="utf-8").read()
        if "(fill in)" in t or "{{" in t:
            g1.fail("report/copyright_statement.md still has placeholders - name the responsible party")
    html = os.path.join(pkg, "report", "proposal.html")
    if os.path.exists(html) and os.path.exists(prop_path):
        m = re.search(r'name="xcity-source-sha256" content="([0-9a-f]{64})"', open(html, encoding="utf-8").read())
        if not m or m.group(1) != xc.sha256_file(prop_path):
            g1.fail("report/proposal.html is out of date - run scripts/render_proposal_html.py")
    # secrets anywhere in text files
    for rel in xc.package_files(pkg):
        if rel.lower().endswith((".md", ".json", ".geojson", ".html", ".js", ".css", ".txt", ".csv", ".svg")):
            text = open(os.path.join(pkg, rel), encoding="utf-8", errors="ignore").read()
            for pat, what in SECRET_PATTERNS:
                if re.search(pat, text):
                    g1.fail("%s appears to contain %s - remove it and rotate it" % (rel, what))
        size = os.path.getsize(os.path.join(pkg, rel))
        if size > 25 * 1024 * 1024:
            g1.fail("%s is %.0f MB; keep each file under 25 MB" % (rel, size / 1048576))

    # ---------------------------------------------------------------- G2 path
    rel_pkg = os.path.relpath(pkg, xc.ROOT).replace(os.sep, "/")
    parts = rel_pkg.split("/")
    if len(parts) != 3 or parts[0] != "submissions":
        g2.fail("package must sit at submissions/<github-login>/<proposal-slug>/ (found %s)" % rel_pkg)
    if not re.match(r"^[a-z0-9][a-z0-9-]{2,63}$", slug):
        g2.fail("proposal-slug %r: use lowercase letters, digits and hyphens, 3-64 characters" % slug)
    if man.get("slug") != slug:
        g2.fail("manifest.slug %r does not match the directory name %r" % (man.get("slug"), slug))
    gh = (man.get("author") or {}).get("github", "")
    if str(gh).lower() != login.lower():
        g2.fail("manifest.author.github %r does not match the directory %r" % (gh, login))
    g2.note("In a pull request, CI also checks that nothing outside this directory changed (scripts/check_pr_paths.py).")

    # ---------------------------------------------------------------- G3 sample / indicative data
    if os.path.isdir(EXAMPLE_DIR) and not pkg.startswith(os.path.realpath(EXAMPLE_DIR) + os.sep):
        ex_hashes = {}
        for dp, dn, fn in os.walk(EXAMPLE_DIR):
            for n in fn:
                if n.endswith((".geojson", ".md")) and n != "changelog.md":
                    ex_hashes[xc.sha256_file(os.path.join(dp, n))] = os.path.relpath(os.path.join(dp, n), xc.ROOT)
        for rel in xc.GEOMETRY_FILES + ["proposal.md"]:
            p = os.path.join(pkg, rel)
            if os.path.exists(p) and xc.sha256_file(p) in ex_hashes:
                g3.fail("%s is identical to the example %s - the example is not an entry" % (rel, ex_hashes[xc.sha256_file(p)]))
        ex_b = os.path.join(EXAMPLE_DIR, "sample-scheme", "geometry", "buildings.geojson")
        if os.path.exists(ex_b) and geo.get("buildings"):
            key = lambda g: (round(g.centroid.x, 5), round(g.centroid.y, 5))
            ex = {key(g) for _, g in xc.features(ex_b)}
            same = sum(1 for _, g in geo["buildings"] if key(g) in ex)
            if same >= max(5, 0.3 * len(geo["buildings"])):
                g3.fail("%d of %d buildings sit exactly where the example's do - the example is not an entry"
                        % (same, len(geo["buildings"])))
    mm = xc.metric_map(mdoc)
    for k, m in mm.items():
        if m.get("source") == "SRC-XCITY-INDICATIVE" and m.get("evidence") != "indicative":
            g3.fail("metric %s cites the organiser's indicative zoning but is tagged %r - tag it 'indicative'"
                    % (k, m.get("evidence")))
    if re.search(r"\b(approved by|endorsed by|已获批|已批准|已获.*支持)", prop, re.I):
        g3.note("proposal.md uses approval language - make sure no official approval or endorsement is claimed")

    # ---------------------------------------------------------------- G4 reconcile
    computed = xc.compute_metrics(pkg)
    for k in xc.REQUIRED_COMPUTED:
        if k not in mm:
            g4.fail("metrics.json must declare %s (evidence: computed)" % k)
    for k, m in mm.items():
        if k in xc.COMPUTED_KEYS and m.get("evidence") == "computed":
            cv, dv = computed[k], m.get("value")
            if isinstance(cv, dict):
                if not isinstance(dv, dict):
                    g4.fail("%s must be an object {system: km2}" % k)
                    continue
                for sy in sorted(set(cv) | set(dv)):
                    try:
                        d_, c_ = float(dv.get(sy, 0) or 0), float(cv.get(sy, 0))
                    except (TypeError, ValueError):
                        g4.fail("%s.%s must be a number" % (k, sy))
                        continue
                    if not close(d_, c_) and abs(d_ - c_) > 0.05:
                        g4.fail("%s.%s declared %s, recomputed %s" % (k, sy, dv.get(sy), cv.get(sy)))
            elif not close(dv, cv):
                g4.fail("%s declared %s, recomputed from geometry %s" % (k, dv, cv))
        elif k in xc.COMPUTED_KEYS and k != "shaded_pedestrian_pct":
            g4.fail("%s can be recomputed from geometry, so its evidence must be 'computed'" % k)
    parts_w = REQ["mandatory"][2]["breakdown"]
    if "annual_water_demand_m3" in mm and all(p in mm for p in parts_w):
        try:
            tot = float(mm["annual_water_demand_m3"]["value"])
            s = sum(float(mm[p]["value"]) for p in parts_w)
            if not close(s, tot):
                g4.fail("water breakdown adds up to %s but annual_water_demand_m3 is %s" % (s, tot))
        except (TypeError, ValueError):
            g4.fail("water figures must be numbers")
    if geo.get("master_area"):
        master = unary_union([g for _, g in geo["master_area"]])
        mu = xc.to_utm(master).buffer(5)
        out = [i for i, (p, g) in enumerate(geo.get("land_use", [])) if not mu.contains(xc.to_utm(g))]
        if out:
            g4.fail("land_use.geojson features %s lie outside the master area" % out[:10])
        outb = [i for i, (p, g) in enumerate(geo.get("buildings", [])) if not mu.contains(xc.to_utm(g))]
        if outb:
            g4.note("%d buildings lie outside the master area; their treatment follows the declared metric version; v2 clips master-area metrics and reports outside buildings separately" % len(outb))

    if spatial_checks.modern(pkg):
        for problem in spatial_checks.partition_problems(geo):
            g4.fail(problem)
    for problem in spatial_checks.context_errors(pkg):
        g9.fail(problem)

    # ---------------------------------------------------------------- G5 offline
    for rel in xc.package_files(pkg):
        if rel.lower().endswith((".html", ".htm", ".svg", ".js", ".css")):
            text = open(os.path.join(pkg, rel), encoding="utf-8", errors="ignore").read()
            for pat, what in NETWORK_PATTERNS:
                m = re.search(pat, text, re.I)
                if m:
                    g5.fail("%s %s: %s" % (rel, what, m.group(0)[:80]))

    # ---------------------------------------------------------------- G6 taskbook + mandatory
    want = [t["id"] for t in TASKS["tasks"]] + [m["id"] for m in REQ["mandatory"]]
    items = {i.get("id"): i for i in comp.get("items", []) if isinstance(i, dict)}
    for w in want:
        it = items.get(w)
        if not it:
            g6.fail("compliance_matrix.json: %s is missing" % w)
            continue
        st = it.get("status")
        if st not in ("answered", "partial"):
            g6.fail("%s: status %r - every task and mandatory requirement must be 'answered' or 'partial' "
                    "(the template starts at 'not_answered')" % (w, st))
        if st == "partial" and not nonempty(it.get("note"), 10):
            g6.fail("%s: a partial answer needs a note saying what is missing" % w)
        sec = str(it.get("section", "")).strip()
        m = re.match(r"^##\s*(\d+)\.", sec)
        if not m or not any(h.startswith("## %s." % m.group(1)) for h in heads):
            g6.fail("%s: section %r does not point at a numbered heading in proposal.md" % (w, sec))

    # ---------------------------------------------------------------- G7 evidence
    asm_ids = {a.get("id") for a in asm.get("assumptions", []) if isinstance(a, dict)}
    src_ids = {s.get("id") for s in src.get("sources", []) if isinstance(s, dict)} | SITE_SRC
    for a in asm.get("assumptions", []):
        if not (nonempty(a.get("value")) and nonempty(a.get("basis"), 10)) or "Why this value" in str(a.get("basis")):
            g7.fail("assumptions.json %s: needs a value and a basis" % a.get("id"))
    keys = [m.get("key") for m in mdoc.get("metrics", []) if isinstance(m, dict)]
    dup = {k for k in keys if keys.count(k) > 1}
    if dup:
        g7.fail("metrics.json declares %s more than once" % sorted(dup))
    for m in mdoc.get("metrics", []):
        k = m.get("key")
        if m.get("value") is None or m.get("value") == "":
            g7.fail("metric %s has no value" % k)
        if not nonempty(m.get("unit")):
            g7.fail("metric %s has no unit" % k)
        ev = m.get("evidence")
        if ev not in EVIDENCE:
            g7.fail("metric %s: evidence %r is not one of %s" % (k, ev, sorted(EVIDENCE)))
        elif ev == "sourced" and m.get("source") not in src_ids:
            g7.fail("metric %s: source %r is not in sources.json" % (k, m.get("source")))
        elif ev == "assumed" and m.get("assumption") not in asm_ids:
            g7.fail("metric %s: assumption %r is not in assumptions.json" % (k, m.get("assumption")))
        elif ev == "computed" and not os.path.exists(os.path.join(pkg, str(m.get("computed_from", "")))):
            g7.fail("metric %s: computed_from %r does not exist" % (k, m.get("computed_from")))
        elif ev == "indicative" and not m.get("source"):
            g7.fail("metric %s: indicative values name their source (e.g. SRC-XCITY-INDICATIVE)" % k)
        elif ev == "declared" and not (nonempty(m.get("note"), 15) and "{{" not in str(m.get("note"))
                                       and not str(m.get("note")).startswith("How the scheme arrives")):
            g7.fail("metric %s: a declared design figure needs a note saying how the scheme arrives at it" % k)
    for r in REQ["mandatory"]:
        ks = r["metric"] if isinstance(r["metric"], list) else ([r["metric"]] if r["metric"] else [])
        ks += r.get("breakdown", [])
        for k in ks:
            if k not in mm:
                g7.fail("%s requires metric %s in metrics.json" % (r["id"], k))
    rule = (mm.get("machine_traffic_rule") or {}).get("value")
    if rule is not None and rule not in REQ["mandatory"][6]["values"]:
        g7.fail("machine_traffic_rule must be one of %s" % REQ["mandatory"][6]["values"])

    # ---------------------------------------------------------------- G8 disclosure
    ag, au, au_ = man.get("agent") or {}, man.get("autonomy") or {}, man.get("author") or {}
    tag = (tman.get("agent") or {})
    for k in ("name", "model", "runtime"):
        if not nonempty(ag.get(k), 2) or "e.g." in str(ag.get(k)) or ag.get(k) == tag.get(k):
            g8.fail("manifest.agent.%s is missing or still a placeholder" % k)
    if au.get("class") not in AUTONOMY:
        g8.fail("manifest.autonomy.class must be one of %s" % sorted(AUTONOMY))
    elif au.get("class") != "autonomous" and (not nonempty(au.get("human_role"), 20) or "Required unless" in str(au.get("human_role"))):
        g8.fail("manifest.autonomy.human_role must describe what the human did (class %s)" % au.get("class"))
    if not nonempty(au_.get("responsible_party"), 2) or "The person or organisation" in str(au_.get("responsible_party")):
        g8.fail("manifest.author.responsible_party must name the responsible person or organisation (named track)")

    # ---------------------------------------------------------------- G9 boundaries
    site_u = xc.to_utm(xc.site_boundary()).buffer(50)
    pilot_parts_u = {key: xc.to_utm(g) for key, g in xc.pilot_parts().items()}
    pilot_u = unary_union(list(pilot_parts_u.values()))
    for name, feats in geo.items():
        for i, (p, g) in enumerate(feats):
            gu = xc.to_utm(g)
            if not site_u.contains(gu):
                over = gu.difference(site_u)
                amt = (over.area / 1e6) if over.area else over.length / 1000
                g9.fail("%s feature %d lies outside the site (by %.3f %s)" % (name, i, amt, "km²" if over.area else "km"))
    for i, (p, g) in enumerate(geo.get("buildings", [])):
        if xc.to_utm(g).intersection(pilot_u).area > 1:
            g9.fail("buildings feature %d is on the pilot area, which is not open to design" % i)
    for i, (p, g) in enumerate(geo.get("land_use", [])):
        for part in xc.pilot_land_use_conflicts(p.get("use"), xc.to_utm(g), pilot_parts_u, legacy=not spatial_checks.modern(pkg)):
            g9.fail("land_use feature %d (%s) conflicts with fixed %s pilot context; allowed labels: %s. "
                    "These labels do not permit new buildings or redesign." %
                    (i, p.get("use"), part, ", ".join(sorted(xc.PILOT_LAND_USES[part]))))
    for part, expected in (("agrivoltaic", "agri_production"), ("living", "living")):
        for p, g in geo.get("structure", []):
            if p.get("system") != expected and xc.to_utm(g).intersection(pilot_parts_u[part]).area > 100:
                g9.note("Fixed %s pilot context is labelled %s in structure.geojson; expected %s. "
                        "Context classification requires content review; do not redesign its interior." %
                        (part, p.get("system"), expected))
    ch = [(p, xc.to_utm(g).buffer(30 if p.get("class") == "main" else 15)) for p, g in xc.channels()]
    hits = 0
    for i, (p, g) in enumerate(geo.get("buildings", [])):
        gu = xc.to_utm(g)
        if any(gu.intersects(c) for _, c in ch):
            hits += 1
    fl_p = os.path.join(xc.SITE, "water", "flood_sensitive_dem.geojson")
    if os.path.exists(fl_p):
        fl = unary_union([xc.to_utm(g) for _, g in xc.features(fl_p)])
        inb = sum(1 for p, g in geo.get("buildings", []) if p.get("form") != "canopy" and xc.to_utm(g).intersects(fl))
        if inb:
            g9.note("%d buildings are inside the DEM-derived flood-sensitive band - listed for the reviewers; say in "
                    "proposal.md how they are protected" % inb)
    crossing = sum(1 for p, g in geo.get("movement", []) if g.geom_type.endswith("LineString")
                   and xc.to_utm(g).intersection(pilot_u).length > 20)
    if crossing:
        g9.note("%d movement lines run across the pilot area - listed for the reviewers; the pilot area is not open to "
                "design" % crossing)
    if hits:
        g9.note("%d buildings touch a DEM-derived channel - listed for the reviewers; the brief forbids permanent "
                "construction on a dry channel" % hits)
    ids = [str(p.get("node_id")) for p, g in geo.get("nodes", [])]
    if len(ids) != 3 or len(set(ids)) != 3 or not set(ids) <= NODE_IDS:
        g9.fail("nodes.geojson must hold three different node_id values from A01-A03, B01-B03, C01-C04 (found %s)" % ids)
    if set(ids) != set(man.get("nodes") or []):
        g9.fail("nodes.geojson ids %s do not match manifest.nodes %s" % (sorted(ids), man.get("nodes")))
    for error in selection_errors(ids, pkg):
        g9.fail(error)
    g9.note("Content review by the organiser completes this gate (prohibited items B1-B5).")

    # ---------------------------------------------------------------- G10 figures
    stamp = jload(pkg, "figures/stamp.json", g10)
    if stamp:
        if stamp.get("input_sha256") != xc.figure_input_hash(pkg):
            g10.fail("drawings are out of date with the package (geometry, metrics, assumptions, sources, image provenance or manifest) - run scripts/make_figures.py")
        for rel, h in (stamp.get("files") or {}).items():
            p = os.path.join(pkg, rel)
            if not os.path.exists(p):
                g10.fail("%s is listed in figures/stamp.json but missing" % rel)
            elif xc.sha256_file(p) != h:
                g10.fail("%s was changed after make_figures.py drew it" % rel)
        for rel in xc.REQUIRED_FIGURES + ["drawings/a3-booklet.pdf", "drawings/a0-board.pdf"] + presentation.required_outputs(pkg):
            if rel not in (stamp.get("files") or {}):
                g10.fail("%s was not produced by make_figures.py" % rel)
    else:
        g10.fail("figures/stamp.json missing - run scripts/make_figures.py")
    reg = {i.get("path"): i for i in prov.get("images", []) if isinstance(i, dict)}
    media = [r for r in xc.package_files(pkg) if r.startswith("media/")]
    for rel in media:
        it = reg.get(rel)
        if not it:
            g10.fail("%s is not registered in image_provenance.json" % rel)
            continue
        for k in ("model", "prompt", "generated_at", "post_processing", "reference_images", "caption"):
            if not nonempty(str(it.get(k, "")), 2):
                g10.fail("image_provenance %s: '%s' is missing" % (rel, k))
        if it.get("reference_images") not in ("none_text_only_prompt", "own_work", "third_party"):
            g10.fail("image_provenance %s: reference_images must be none_text_only_prompt | own_work | third_party" % rel)
        elif it.get("reference_images") != "none_text_only_prompt" and not nonempty(it.get("reference_images_note"), 10):
            g10.fail("image_provenance %s: say what the reference image was and under what licence" % rel)
    for rel in reg:
        if rel and not os.path.exists(os.path.join(pkg, rel)):
            g10.fail("image_provenance lists %s, which does not exist" % rel)
    # the 3D scene and the massing renders must match the geometry they claim to show
    sh = xc.scene_input_hash(pkg)
    vis = os.path.join(pkg, "visual", "index.html")
    if os.path.exists(vis) and ('"input_sha256":"%s"' % sh) not in open(vis, encoding="utf-8", errors="ignore").read():
        g10.fail("visual/index.html is out of date with the geometry - run scripts/make_scene.py")
    rstamp = {}
    if os.path.exists(os.path.join(pkg, "renders", "stamp.json")):
        rstamp = jload(pkg, "renders/stamp.json", g10) or {}
        if rstamp.get("input_sha256") != sh:
            g10.fail("renders/ are out of date with the geometry - run scripts/render_views.py")
        for f, meta in (rstamp.get("files") or {}).items():
            p = os.path.join(pkg, "renders", f)
            if not os.path.exists(p):
                g10.fail("renders/%s is listed in renders/stamp.json but missing" % f)
            elif xc.sha256_file(p) != (meta or {}).get("sha256"):
                g10.fail("renders/%s was changed after render_views.py drew it" % f)
    for rel, it in reg.items():
        ci = (it or {}).get("control_image")
        if ci:
            if not ci.startswith("renders/") or os.path.basename(ci) not in (rstamp.get("files") or {}):
                g10.fail("image_provenance %s: control_image %s is not a render made by render_views.py" % (rel, ci))
    if any(r.startswith("media/") for r in xc.package_files(pkg)) and not any((i or {}).get("control_image") for i in reg.values()):
        g10.note("media/ images have no control_image: they are not tied to a view of the geometry")
    if not any(r.startswith("media/") and r.lower().endswith((".jpg", ".jpeg", ".png", ".webp")) for r in xc.package_files(pkg)):
        g10.note("no finished images in media/: the cover, the gallery card and the node sheets show massing renders. "
                 "If you or your human can make images, see AGENTS.md checkpoint 2 and docs/visual-guide.md section 3")

    # ---------------------------------------------------------------- G11 trade-off
    to = man.get("tradeoff") or {}
    for k in ("objective", "why", "consequence", "who_bears"):
        v = to.get(k)
        if not nonempty(v, 15) or v in ("Why", "What follows from it", "Who bears the cost") or v.startswith("The one objective"):
            g11.fail("manifest.tradeoff.%s is missing, too short or still a placeholder" % k)
    if not any(h.startswith("## 13.") for h in heads):
        g11.fail("proposal.md has no section 13 (declared trade-off)")

    g9.note("DEM flood sensitivity is a screening layer, not a surveyed design-flood boundary or a blanket no-build zone.")

    # ---------------------------------------------------------------- G12 depth
    depth_assessment = design_depth.assess(pkg, man.get("nodes") or [])
    for problem in depth_assessment["automatic"]["errors"]:
        g12.fail(problem)
    for problem in presentation.index_errors(pkg, man.get("nodes") or []):
        g12.fail(problem)
    dd = man.get("design_depth") or {}
    for tier in ("tier1_structure", "tier2_master"):
        ev = (dd.get(tier) or {}).get("evidence") or []
        if not ev:
            g12.fail("design_depth.%s.evidence is empty" % tier)
        for rel in ev:
            if not os.path.exists(os.path.join(pkg, rel)):
                g12.fail("design_depth.%s points at %s, which does not exist" % (tier, rel))
    t3 = dd.get("tier3_nodes") or {}
    if set(t3) != set(man.get("nodes") or []):
        g12.fail("design_depth.tier3_nodes %s must match manifest.nodes %s" % (sorted(t3), man.get("nodes")))
    for nid, ev in t3.items():
        for view in ("plan", "aerial", "eye_level"):
            rel = (ev or {}).get(view)
            if not rel:
                g12.fail("node %s: no %s view declared" % (nid, view))
            elif not os.path.exists(os.path.join(pkg, rel)):
                g12.fail("node %s: %s view %s does not exist" % (nid, view, rel))
            elif rel.startswith("media/") and rel not in reg:
                g12.fail("node %s: %s is not registered in image_provenance.json" % (nid, rel))

    import phasing_programme
    for error in phasing_programme.assess(pkg):
        g12.fail(error)

    g12.note("Checks evidence references (paths, metric keys and proposal headings), disclosed gap plans and presentation packaging/page order only; not readability, design adequacy or finished-image quality. Settlement hierarchy, coordinated city-system diagrams, the overall axonometric/birdseye view, system locations and scales, transport, resource infrastructure and phasing require independent design content review; diagram paths alone do not establish their usefulness or fidelity.")
    gates = [G[g["id"]].out() for g in EVAL["gates"]]
    result = {
        "script": "scripts/self_check_submission.py", "script_version": xc.SCRIPT_VERSION,
        "checked_at": datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat(),
        "package": rel_pkg, "package_sha256": xc.package_sha256(pkg),
        "gates_total": len(gates), "gates_passed": sum(1 for g in gates if g["pass"]),
        "pass": all(g["pass"] for g in gates),
        "automated_compliance_status": "passed" if all(g["pass"] for g in gates) else "failed",
        "design_content_review": {"status": "not_assessed", "note": "Automated gates do not establish design adequacy or organiser approval."},
        "design_depth_assessment": depth_assessment,
        "further_work": depth_assessment["further_work"],
        "recomputed": {k: computed[k] for k in xc.COMPUTED_KEYS},
        "gates": gates,
    }
    if write:
        xc.write_json(os.path.join(pkg, xc.SELF_CHECK), result)
    return result


def report(r):
    print("%s  %d/%d gates  %s" % ("PASS" if r["pass"] else "FAIL", r["gates_passed"], r["gates_total"], r["package"]))
    print("  Automated compliance only; design content review: NOT ASSESSED (not approval).")
    print("  Further work: %s (entrant disclosure; not automatically resolved)." % r.get("further_work", {}).get("status", "not_declared"))
    for g in r["gates"]:
        print("  [%s] %s  %s" % ("x" if g["pass"] else " ", g["id"], g["title"]))
        for m in g["messages"][:12]:
            print("        - " + m)
        if len(g["messages"]) > 12:
            print("        ... %d more" % (len(g["messages"]) - 12))
        for m in g.get("notes", []):
            print("        note: " + m)
    print("  package sha256 %s" % r["package_sha256"])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("package", nargs="*", help="submissions/<github-login>/<proposal-slug>")
    ap.add_argument("--all", action="store_true", help="check every package under submissions/")
    ap.add_argument("--no-write", action="store_true", help="do not write self_check.json")
    ap.add_argument("--json", action="store_true", help="print the result as JSON")
    a = ap.parse_args()
    paths = list(a.package)
    if a.all:
        base = os.path.join(xc.ROOT, "submissions")
        for login in sorted(os.listdir(base)) if os.path.isdir(base) else []:
            for slug in sorted(os.listdir(os.path.join(base, login))) if os.path.isdir(os.path.join(base, login)) else []:
                if os.path.isfile(os.path.join(base, login, slug, "manifest.json")):
                    package_rel = "submissions/%s/%s" % (login, slug)
                    status_path = os.path.join(xc.ROOT, "gallery/example-status.json")
                    examples = xc.load_json(status_path).get("examples", []) if os.path.isfile(status_path) else []
                    withdrawn = any(x.get("path") == package_rel and x.get("status") == "rebuild_pending" for x in examples)
                    if login == "EXAMPLE-agent" and withdrawn:
                        print("NOT ACTIVE: %s — organiser example withdrawn for redesign; not checked or approved. Explicit path checks still apply every gate." % package_rel)
                        continue
                    paths.append(os.path.join(base, login, slug))
    if not paths:
        ap.error("give a package path or --all")
    ok = True
    for p in paths:
        r = check(p, write=not a.no_write)
        ok = ok and r["pass"]
        print(json.dumps(r, ensure_ascii=False, indent=2)) if a.json else report(r)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
