"""Shared helpers for the XCITY AI Competition scripts.

Everything here runs offline. Dependencies: shapely >= 2, pyproj, numpy (see requirements.txt).
"""
import hashlib
import json
import os
from pathlib import Path
import re

from pyproj import Geod, Transformer
from shapely.geometry import shape, mapping
from shapely.ops import transform, unary_union
from shapely import make_valid

ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
SITE = os.path.join(ROOT, "brief", "site-package")
SCRIPT_VERSION = "1.4.0"

GEOD = Geod(ellps="WGS84")
_TO_UTM = Transformer.from_crs("EPSG:4326", "EPSG:32719", always_xy=True)
_TO_LL = Transformer.from_crs("EPSG:32719", "EPSG:4326", always_xy=True)

# Required parts of a submission package (paths relative to the package directory).
REQUIRED_FILES = [
    "manifest.json", "proposal.md", "metrics.json", "compliance_matrix.json",
    "assumptions.json", "sources.json", "image_provenance.json", "changelog.md",
    "geometry/structure.geojson", "geometry/master_area.geojson", "geometry/land_use.geojson",
    "geometry/buildings.geojson", "geometry/movement.geojson", "geometry/phasing.geojson",
    "geometry/nodes.geojson",
    "report/proposal.html", "report/copyright_statement.md",
    "drawings/a3-booklet.pdf", "drawings/a0-board.pdf",
    "figures/stamp.json",
]
REQUIRED_FIGURES = [
    "figures/fig-01-structure.png", "figures/fig-02-master-plan.png", "figures/fig-03-land-use-density.png",
    "figures/fig-04-movement.png", "figures/fig-05-open-space-water.png", "figures/fig-06-phasing.png",
    "figures/fig-07-metrics.png",
]
GEOMETRY_FILES = [f for f in REQUIRED_FILES if f.startswith("geometry/")]
SELF_CHECK = "self_check.json"


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(path, obj):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def site_json(rel):
    return load_json(os.path.join(SITE, rel))


def to_utm(geom):
    projected = transform(lambda x, y, z=None: _TO_UTM.transform(x, y), geom)
    # Projection can turn touching polygon rings into floating-point self-intersections.
    # Repair the derived display/check geometry only; never rewrite submitted coordinates.
    if projected.geom_type in ("Polygon", "MultiPolygon") and not projected.is_valid:
        projected = make_valid(projected)
    return projected


def to_lonlat(geom):
    return transform(lambda x, y, z=None: _TO_LL.transform(x, y), geom)


def geodesic_km2(geom):
    """Area on the WGS 84 ellipsoid, km2. geom is lon/lat."""
    if geom is None or geom.is_empty:
        return 0.0
    return abs(GEOD.geometry_area_perimeter(geom)[0]) / 1e6


def geodesic_m2(geom):
    return geodesic_km2(geom) * 1e6


def geodesic_length_m(geom):
    if geom is None or geom.is_empty:
        return 0.0
    return GEOD.geometry_length(geom)


def features(path):
    """Read a GeoJSON FeatureCollection; return a list of (properties, shapely geometry)."""
    fc = load_json(path)
    out = []
    for f in fc.get("features", []):
        g = f.get("geometry")
        if not g:
            continue
        geom = shape(g)
        if geom.geom_type in ("Polygon", "MultiPolygon") and not geom.is_valid:
            geom = make_valid(geom)
        out.append((f.get("properties") or {}, geom))
    return out


def site_boundary():
    """Union of the two parcels (the whole site), lon/lat."""
    return unary_union([g for _, g in features(os.path.join(SITE, "boundaries", "scope_9_13.geojson"))])


def pilot_parts():
    """Separate fixed agrivoltaic and living outlines, lon/lat."""
    d = os.path.join(SITE, "pilot-area")
    return {key: unary_union([g for _, g in features(os.path.join(d, name))])
            for key, name in (("agrivoltaic", "pilot_area.geojson"),
                              ("living", "pilot_living_area.geojson"))}


def pilot_area():
    """Both fixed pilot parts; neither is open to new design."""
    return unary_union(list(pilot_parts().values()))


PILOT_LAND_USES = {key: set(value["land_use_labels"]) for key, value in
                   load_json(os.path.join(ROOT, "brief", "requirements.json"))["fixed_pilot_context"].items()}


def pilot_land_use_conflicts(use, geometry_utm, parts_utm, legacy=False):
    """Labels describe fixed context, not permission for new construction."""
    return [part for part, outline in parts_utm.items()
            if use not in (PILOT_LAND_USES[part] | ({"agriculture"} if legacy and part == "living" else set())) and geometry_utm.intersection(outline).area > 100]


def channels():
    return features(os.path.join(SITE, "water", "channels_dem.geojson"))


def polygons_only(geom):
    if geom.geom_type in ("Polygon", "MultiPolygon"):
        return geom
    if geom.geom_type == "GeometryCollection":
        return unary_union([g for g in geom.geoms if g.geom_type in ("Polygon", "MultiPolygon")])
    return None


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def package_files(pkg):
    """All files in the package, relative, sorted; excludes self_check.json and OS junk."""
    out = []
    for dp, dn, fn in os.walk(pkg):
        dn[:] = sorted(d for d in dn if not d.startswith("."))
        for n in sorted(fn):
            if n.startswith(".") or n == SELF_CHECK:
                continue
            out.append(os.path.relpath(os.path.join(dp, n), pkg).replace(os.sep, "/"))
    return sorted(out)


def package_sha256(pkg):
    """Fingerprint of a submission directory: sha256 over 'path\\0sha256(file)\\n' lines, sorted by path.
    self_check.json is excluded because it records this value."""
    h = hashlib.sha256()
    for rel in package_files(pkg):
        h.update(rel.encode("utf-8") + b"\0" + sha256_file(os.path.join(pkg, rel)).encode() + b"\n")
    return h.hexdigest()


def figure_input_hash(pkg):
    """Everything the drawings print: geometry/, metrics, assumptions, sources, image provenance, the renders and
    media images placed on the sheets, and the manifest fields on the sheets. figures/stamp.json records it; GATE-G10 recomputes it, so stale drawings fail."""
    h = hashlib.sha256()
    for rel in GEOMETRY_FILES + ["metrics.json", "assumptions.json", "sources.json", "image_provenance.json"]:
        p = os.path.join(pkg, rel)
        h.update(rel.encode() + b"\0")
        if os.path.exists(p):
            h.update(open(p, "rb").read())
    matrix_path = os.path.join(pkg, 'design_depth_matrix.json')
    if os.path.exists(matrix_path) and load_json(matrix_path).get('schema_version') == 2:
        for rel in ['design_depth_matrix.json', 'brief/design-depth.json', 'brief/site-package/boundaries/boundary-revision.json', 'brief/site-package/datapackage.json']:
            path = os.path.join(pkg if rel == 'design_depth_matrix.json' else ROOT, rel)
            h.update(rel.encode() + b'\0' + open(path, 'rb').read())
        for path in sorted(Path(pkg).glob('context/*.geojson')):
            h.update(str(path.relative_to(pkg)).encode() + b'\0' + path.read_bytes())
    # the drawings place the massing renders and the registered media images, so they are inputs too
    rs = os.path.join(pkg, "renders", "stamp.json")
    if os.path.exists(rs):
        h.update(b"renders/stamp.json\0" + open(rs, "rb").read())
    ip = os.path.join(pkg, "image_provenance.json")
    if os.path.exists(ip):
        for im in sorted(load_json(ip).get("images", []), key=lambda i: str(i.get("path"))):
            mp = os.path.join(pkg, str(im.get("path") or ""))
            if im.get("path") and os.path.isfile(mp):
                h.update(str(im["path"]).encode() + b"\0" + sha256_file(mp).encode())
    man = load_json(os.path.join(pkg, "manifest.json"))
    shown = {k: man.get(k) for k in ("title", "title_zh", "slug", "summary", "thesis", "nodes", "nodes_reason", "author",
                                      "agent", "autonomy", "tradeoff", "booklet")}
    h.update(json.dumps(shown, sort_keys=True, ensure_ascii=False).encode())
    booklet=man.get('booklet') if isinstance(man.get('booklet'),dict) else {}
    custom=booklet.get('section_pages') if isinstance(booklet.get('section_pages'),dict) else {}
    for section,pages in sorted(custom.items()):
        for page in pages if isinstance(pages,list) else []:
            rel=page.get('path') if isinstance(page,dict) else None
            path=os.path.join(pkg,str(rel or ''))
            if rel and os.path.isfile(path):h.update(('booklet.section_pages:'+section+':'+rel).encode()+b'\0'+sha256_file(path).encode())
    # the brief page prints the compliance matrix and the proposal's headings; the booklet places the entrant's pages
    cm = os.path.join(pkg, "compliance_matrix.json")
    if os.path.exists(cm):
        h.update(b"compliance_matrix.json\0" + open(cm, "rb").read())
    pm = os.path.join(pkg, "proposal.md")
    if os.path.exists(pm):
        h.update(json.dumps(proposal_headings(open(pm, encoding="utf-8").read()), ensure_ascii=False).encode())
    b = man.get("booklet") if isinstance(man.get("booklet"), dict) else {}
    for rel in [b.get("cover"), b.get("a0_page")] + [pg.get("path") for pg in (b.get("pages") or []) if isinstance(pg, dict)]:
        fp = os.path.join(pkg, str(rel or ""))
        if rel and os.path.isfile(fp):
            h.update(str(rel).encode() + b"\0" + sha256_file(fp).encode())
    return h.hexdigest()


def scene_input_hash(pkg):
    """What the 3D scene and its renders are drawn from: geometry/ and the manifest's title and render note.
    visual/index.html and renders/stamp.json record it; GATE-G10 recomputes it."""
    h = hashlib.sha256()
    for source in ['scripts/make_scene.py','scripts/scene/scene.js']:
        path=os.path.join(ROOT,source)
        if os.path.isfile(path):h.update(source.encode()+b'\0'+Path(path).read_bytes())

    for rel in GEOMETRY_FILES:
        p = os.path.join(pkg, rel)
        h.update(rel.encode() + b"\0")
        if os.path.exists(p):
            h.update(open(p, "rb").read())
    man = load_json(os.path.join(pkg, "manifest.json"))
    field_ref = (man.get("scene_generation") or {}).get("territorial_field_geometry")
    if field_ref:
        field_path = os.path.realpath(os.path.join(pkg, field_ref))
        if not field_path.startswith(os.path.realpath(pkg) + os.sep):
            raise ValueError("territorial field geometry must stay inside the submission")
        h.update(str(field_ref).encode() + b"\0")
        if os.path.isfile(field_path):h.update(Path(field_path).read_bytes())
    h.update(json.dumps({k: man.get(k) for k in ("title", "render_note", "scene_seed", "scene_generation")}, sort_keys=True,
                        ensure_ascii=False).encode())
    return h.hexdigest()


def proposal_headings(text):
    """Return heading lines ('## 3. Energy ...') in proposal.md."""
    return [l.strip() for l in text.splitlines() if re.match(r"^#{1,6}\s", l)]


def find_package(path):
    """Accept submissions/<login>/<slug> (relative to cwd or ROOT); return (abs path, login, slug)."""
    p = os.path.realpath(path)
    if not os.path.isdir(p):
        alt = os.path.join(ROOT, path)
        if os.path.isdir(alt):
            p = os.path.realpath(alt)
    if not os.path.isdir(p):
        raise SystemExit("not a directory: %s" % path)
    slug = os.path.basename(p)
    login = os.path.basename(os.path.dirname(p))
    return p, login, slug


# ---------------------------------------------------------------------------------------------
# Metrics recomputed from geometry (GATE-G4). make_figures.py draws the same numbers.

GEOMETRY_TYPES = {"structure": ("Polygon", "MultiPolygon"), "master_area": ("Polygon", "MultiPolygon"),
                  "land_use": ("Polygon", "MultiPolygon"), "buildings": ("Polygon", "MultiPolygon"),
                  "movement": ("LineString", "MultiLineString", "Point", "MultiPoint"),
                  "phasing": ("Polygon", "MultiPolygon"), "nodes": ("Polygon", "MultiPolygon")}
TYPE_HINT = ("Clipping often leaves a GeometryCollection (polygons plus line or point slivers). Keep only the polygon "
             "parts, e.g. shapely: unary_union([p for p in g.geoms if p.geom_type in ('Polygon', 'MultiPolygon')]), "
             "or g.buffer(0) for an invalid polygon.")


def geometry_problems(geo):
    """Wrong geometry types or empty geometry, with a fix hint. [] if fine."""
    out = []
    for name, feats in geo.items():
        for i, (p, g) in enumerate(feats):
            if g.is_empty:
                out.append("geometry/%s.geojson feature %d is empty" % (name, i))
            elif g.geom_type not in GEOMETRY_TYPES.get(name, (g.geom_type,)):
                out.append("geometry/%s.geojson feature %d: %s is not allowed here (allowed: %s). %s"
                           % (name, i, g.geom_type, ", ".join(GEOMETRY_TYPES[name]), TYPE_HINT))
    return out


def load_geometry(pkg):
    """All geometry files of a package, lon/lat. Missing files give empty lists; a missing geometry/ stops."""
    if not os.path.isdir(os.path.join(pkg, "geometry")):
        raise SystemExit("no geometry/ folder in %s - is the package path right?" % pkg)
    g = {}
    for rel in GEOMETRY_FILES:
        name = os.path.splitext(os.path.basename(rel))[0]
        p = os.path.join(pkg, rel)
        g[name] = features(p) if os.path.exists(p) else []
    return g


def _floors(props):
    try:
        return max(0.0, float(props.get("floors", 0) or 0))
    except (TypeError, ValueError):
        return 0.0


def compute_metrics(pkg, geo=None):
    geo = geo or load_geometry(pkg)
    master = unary_union([g for _, g in geo["master_area"]]) if geo["master_area"] else None
    m_m2 = geodesic_m2(master) if master is not None else 0.0
    solid = [(p, g) for p, g in geo["buildings"] if p.get("form") != "canopy"]   # canopies: roof on posts, no floor area
    outside_solid = []
    matrix_path = os.path.join(pkg, 'design_depth_matrix.json')
    modern = os.path.exists(matrix_path) and load_json(matrix_path).get('schema_version') == 2
    if modern and master is not None:
        outside_solid = [(p, g.difference(master)) for p, g in solid if not master.covers(g)]
        solid = [(p, g.intersection(master)) for p, g in solid]
    fp = sum(geodesic_m2(g) for _, g in solid)
    gfa = sum(geodesic_m2(g) * _floors(p) for p, g in solid)
    land = {}
    for p, g in geo["land_use"]:
        u = str(p.get("use", "unknown"))
        land[u] = land.get(u, 0.0) + geodesic_m2(g)
    structure = {}
    for p, g in geo["structure"]:
        s = str(p.get("system", "unknown"))
        structure[s] = structure.get(s, 0.0) + geodesic_km2(g)
    nets = {"people": 0.0, "machine": 0.0, "shared": 0.0}
    shaded = 0.0
    walk_total = 0.0
    interfaces = 0
    for p, g in geo["movement"]:
        if g.geom_type in ("Point", "MultiPoint"):
            if p.get("kind") == "interface":
                interfaces += 1 if g.geom_type == "Point" else len(g.geoms)
            continue
        if g.geom_type not in ("LineString", "MultiLineString"):
            continue
        L = geodesic_length_m(g)
        n = p.get("network")
        if n in nets:
            nets[n] += L
        if n in ("people", "shared"):
            walk_total += L
            if p.get("shaded") is True:
                shaded += L
    out = {
        "master_area_km2": round(m_m2 / 1e6, 4),
        "footprint_m2": round(fp, 1),
        "site_coverage_pct": round(100 * fp / m_m2, 3) if m_m2 else 0.0,
        "gfa_m2": round(gfa, 1),
        "far": round(gfa / m_m2, 4) if m_m2 else 0.0,
        "open_space_pct": round(100 * land.get("open_space", 0.0) / m_m2, 3) if m_m2 else 0.0,
        "human_machine_interfaces": interfaces,
        "shaded_pedestrian_pct": round(100 * shaded / walk_total, 3) if walk_total else 0.0,
        "structure_km2": {k: round(v, 3) for k, v in sorted(structure.items())},
        "land_use_ha": {k: round(v / 1e4, 2) for k, v in sorted(land.items())},
        "network_km": {k: round(v / 1000, 3) for k, v in nets.items()},
    }
    out['metric_scope'] = 'master_area_clipped_v2' if modern else 'legacy_package_buildings_over_master_area'
    out['outside_master_gfa_m2'] = round(sum(geodesic_m2(g) * _floors(p) for p,g in outside_solid),1) if modern else None
    return out


COMPUTED_KEYS = ("master_area_km2", "site_coverage_pct", "gfa_m2", "far", "open_space_pct",
                 "human_machine_interfaces", "shaded_pedestrian_pct", "structure_km2")
REQUIRED_COMPUTED = ("master_area_km2", "site_coverage_pct", "far", "open_space_pct",
                     "human_machine_interfaces", "structure_km2")


def metric_map(metrics_doc):
    return {m.get("key"): m for m in metrics_doc.get("metrics", []) if isinstance(m, dict)}
