#!/usr/bin/env python3
"""Technical figures, node views and A3 / A0 drawings for one submission - offline and free.

    python scripts/make_figures.py submissions/<github-login>/<proposal-slug>

Reads only your own geometry/, metrics.json and manifest.json plus the site package. Writes:

    figures/fig-01-structure.png        whole site: the five systems           (scale 1)
    figures/fig-02-master-plan.png      your master design area                 (scale 2)
    figures/fig-03-land-use-density.png land use, floors, recomputed metrics
    figures/fig-04-movement.png         people / machine / shared networks and every interface
    figures/fig-05-open-space-water.png open space, shade, channels
    figures/fig-06-phasing.png          three phases and their triggers
    figures/fig-07-metrics.png          every declared metric with its evidence tag
    figures/node-<id>-plan.png | -aerial.png | -eye.png   for each of your three nodes (scale 3)
    drawings/a3-booklet.pdf             public presentation in the required reading order
    drawings/a3-technical-appendix.pdf controls, accounts, sections and disclosure
    drawings/presentation-index.json  main section page ranges and document page counts
    drawings/a0-board.pdf               one A0 board
    figures/stamp.json                  what the figures were drawn from (GATE-G10 checks it)

Every figure carries a title, legend, scale bar, north arrow, sources, the script version and a
hash of the inputs. Nothing on a drawing comes from anywhere but your own files: if a figure looks
empty, the geometry is empty.
"""
import argparse
import datetime
import json
import re
import math
import os
import sys
import textwrap
import warnings

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np                                                  # noqa: E402
import matplotlib                                                   # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                     # noqa: E402
from matplotlib import font_manager                                 # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages                # noqa: E402
from matplotlib.patches import Polygon as MPoly, Rectangle, FancyArrow  # noqa: E402
from matplotlib.lines import Line2D                                 # noqa: E402
from matplotlib.path import Path as MPath                           # noqa: E402
from matplotlib.patches import PathPatch                            # noqa: E402
from matplotlib.patheffects import withStroke                        # noqa: E402
from shapely.geometry.polygon import orient                         # noqa: E402
from PIL import Image                                               # noqa: E402
from shapely.geometry import Point, LineString, box                 # noqa: E402
from shapely.ops import unary_union                                 # noqa: E402
import presentation
import xcity_common as xc                                           # noqa: E402

# ------------------------------------------------------------------------------- style
PAPER = "#F7F5F0"
INK = "#1E1D1B"
MUTED = "#7A756C"
GOLD = "#B08F45"
RED = "#C0392B"
WATER = "#4F8DBF"
SYSTEM_COLORS = {
    "energy_compute": "#C9A961", "agri_production": "#7FA85C", "living": "#C96B5C",
    "industry": "#5A5F66", "port": "#5C9BC9", "reserve": "#B9B2A3",
}
SYSTEM_LABEL = {
    "energy_compute": "Energy + compute", "agri_production": "Agri-production", "living": "Living + public life",
    "industry": "Industry + automation", "port": "Trade + port", "reserve": "Reserve",
}
USE_COLORS = {
    "residential": "#E3B29E", "mixed_use": "#D98C6E", "civic": "#B5617A", "compute": "#C9A961",
    "energy": "#E6D39A", "industry": "#8C9096", "logistics": "#A7AAB0", "agriculture": "#B7CF97",
    "open_space": "#8FBF7A", "infrastructure": "#CFCBC2", "reserve": "#DDD6C8",
}
NET_STYLE = {
    "people": dict(color="#C96B5C", lw=1.6, ls="-"),
    "machine": dict(color="#3F4650", lw=2.0, ls="-"),
    "shared": dict(color="#7D5BA6", lw=1.8, ls="--"),
}
PHASE_COLORS = {1: "#C96B5C", 2: "#E0A458", 3: "#E9D8A6"}
FLOOR_H = 3.5

A3 = (16.54, 11.69)
A0 = (46.81, 33.11)

_CJK = None


def setup_fonts():
    global _CJK
    names = {f.name for f in font_manager.fontManager.ttflist}
    for cand in ("Noto Sans CJK SC", "Noto Sans SC", "Source Han Sans SC", "PingFang SC", "Hiragino Sans GB",
                 "Microsoft YaHei", "SimHei", "WenQuanYi Zen Hei", "Noto Sans CJK JP"):
        if cand in names:
            _CJK = cand
            break
    plt.rcParams["font.family"] = ["DejaVu Sans"] + ([_CJK] if _CJK else [])
    plt.rcParams["font.size"] = 9
    plt.rcParams["axes.edgecolor"] = MUTED
    if not _CJK:
        print("note: no CJK font found - Chinese text is left out of the drawings "
              "(install fonts-noto-cjk to include it)")


def T(s):
    """Text safe for the available fonts."""
    if s is None:
        return ""
    s = str(s)
    if _CJK:
        return s
    return "".join(ch for ch in s if ord(ch) < 0x2E80).strip()


# ------------------------------------------------------------------------------- data
class Pkg:
    def __init__(self, path):
        self.dir, self.login, self.slug = xc.find_package(path)
        self.man = xc.load_json(os.path.join(self.dir, "manifest.json"))
        mp = os.path.join(self.dir, "metrics.json")
        self.metrics_doc = xc.load_json(mp) if os.path.exists(mp) else {"metrics": []}
        self.metrics = xc.metric_map(self.metrics_doc)
        self.geo_ll = xc.load_geometry(self.dir)
        self.computed = xc.compute_metrics(self.dir, self.geo_ll)
        u = xc.to_utm
        self.geo = {k: [(p, u(g)) for p, g in v] for k, v in self.geo_ll.items()}
        self.site = u(xc.site_boundary())
        self.parcels = [(p, u(g)) for p, g in xc.features(os.path.join(xc.SITE, "boundaries", "parcels_9_13.geojson"))]
        self.lead = u(xc.pilot_area())
        self.channels = [(p, u(g)) for p, g in xc.channels()]
        ts = xc.site_json("terrain/terrain_summary_9_13.json")["files"]
        self.hs = np.array(Image.open(os.path.join(xc.SITE, "terrain", ts["hillshade_utm"])))
        self.hs_bounds = ts["hillshade_utm_bounds_m"]
        self.dem = np.array(Image.open(os.path.join(xc.SITE, "terrain", ts["dem_png"]))).astype("float32")
        self.master = unary_union([g for _, g in self.geo["master_area"]]) if self.geo["master_area"] else None
        self.nodes = {str(p.get("node_id")): (p, g) for p, g in self.geo["nodes"]}
        self.input_hash = xc.figure_input_hash(self.dir)
        self.title = self.man.get("title") or self.slug
        self.title_zh = self.man.get("title_zh") or ""
        self.node_meta = {n["id"]: n for n in xc.site_json("nodes/design_nodes.json")["nodes"]}
        ip = os.path.join(self.dir, "image_provenance.json")
        self.prov = xc.load_json(ip).get("images", []) if os.path.exists(ip) else []
        rs = os.path.join(self.dir, "renders", "stamp.json")
        self.renders = xc.load_json(rs) if os.path.exists(rs) else {}
        self.renders_ok = bool(self.renders) and self.renders.get("input_sha256") == xc.scene_input_hash(self.dir)
        if self.renders and not self.renders_ok:
            print("note: renders/ are out of date with the geometry and are not used - run scripts/render_views.py")

    def dem_smooth(self, x, y):
        """Bilinear DEM sample, for sections (dem_at is nearest-cell, for maps)."""
        x0, y0, x1, y1 = self.hs_bounds
        h, w = self.dem.shape
        c = np.clip((np.asarray(x, float) - x0) / (x1 - x0) * w - 0.5, 0, w - 1.001)
        r = np.clip((y1 - np.asarray(y, float)) / (y1 - y0) * h - 0.5, 0, h - 1.001)
        c0, r0 = np.floor(c).astype(int), np.floor(r).astype(int)
        fc, fr = c - c0, r - r0
        d = self.dem
        return (d[r0, c0] * (1 - fc) * (1 - fr) + d[r0, c0 + 1] * fc * (1 - fr)
                + d[r0 + 1, c0] * (1 - fc) * fr + d[r0 + 1, c0 + 1] * fc * fr)

    def dem_at(self, x, y):
        x0, y0, x1, y1 = self.hs_bounds
        h, w = self.dem.shape
        c = (np.asarray(x) - x0) / (x1 - x0) * w
        r = (y1 - np.asarray(y)) / (y1 - y0) * h
        c = np.clip(c.astype(int), 0, w - 1)
        r = np.clip(r.astype(int), 0, h - 1)
        return self.dem[r, c]


# ------------------------------------------------------------------------------- map primitives
def _polys(g):
    if g is None or g.is_empty:
        return []
    if g.geom_type == "Polygon":
        return [g]
    if g.geom_type in ("MultiPolygon", "GeometryCollection"):
        return [p for p in g.geoms if p.geom_type == "Polygon"]
    return []


def _lines(g):
    if g is None or g.is_empty:
        return []
    if g.geom_type == "LineString":
        return [g]
    if g.geom_type in ("MultiLineString", "GeometryCollection"):
        return [l for l in g.geoms if l.geom_type == "LineString"]
    if g.geom_type in ("Polygon", "MultiPolygon"):
        return [LineString(p.exterior.coords) for p in _polys(g)]
    return []


def _path(p):
    p = orient(p, 1.0)
    verts, codes = [], []
    for ring in [p.exterior] + list(p.interiors):
        xy = np.asarray(ring.coords)[:, :2]
        verts.extend(xy.tolist())
        codes.extend([MPath.MOVETO] + [MPath.LINETO] * (len(xy) - 2) + [MPath.CLOSEPOLY])
    return MPath(verts, codes)


def fill(ax, g, fc, ec="none", lw=0.0, alpha=1.0, z=2, hatch=None, ls="-"):
    for p in _polys(g):
        ax.add_patch(PathPatch(_path(p), fc=fc, ec=ec, lw=lw, alpha=alpha, zorder=z, hatch=hatch, ls=ls))


def outline(ax, g, color=INK, lw=1.0, ls="-", z=5, alpha=1.0):
    for l in _lines(g):
        xy = np.asarray(l.coords)
        ax.plot(xy[:, 0], xy[:, 1], color=color, lw=lw, ls=ls, zorder=z, alpha=alpha, solid_capstyle="round")


def hillshade(ax, pkg, alpha=0.55):
    x0, y0, x1, y1 = pkg.hs_bounds
    # The topographic shading belongs to the issued competition land only.
    # Retain a paper background outside it; never manufacture a grey raster rectangle.
    ax._xc_bg = matplotlib.colors.to_rgb(PAPER)
    ax.set_facecolor(PAPER)
    image = ax.imshow(pkg.hs, cmap="gray", vmin=0, vmax=255, extent=[x0, x1, y0, y1], alpha=alpha, zorder=0,
                      interpolation="bilinear")
    site_path = MPath.make_compound_path(*[_path(p) for p in _polys(pkg.site)])
    image.set_clip_path(PathPatch(site_path, transform=ax.transData))


def channels(ax, pkg, window=None, primary=True, z=3):
    for p, g in pkg.channels:
        if window is not None and not g.intersects(window):
            continue
        main = p.get("class") == "main"
        if not main and not primary:
            continue
        outline(ax, g, color=WATER, lw=1.4 if main else 0.6, z=z, alpha=0.9)


def frame(ax, bounds, pad=0.04):
    x0, y0, x1, y1 = bounds
    dx, dy = x1 - x0, y1 - y0
    ax.set_xlim(x0 - dx * pad, x1 + dx * pad)
    ax.set_ylim(y0 - dy * pad, y1 + dy * pad)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_color("#CFCBC2")
        s.set_linewidth(0.6)
    ax.set_facecolor(getattr(ax, "_xc_bg", PAPER))


def fit_aspect(bounds, aspect):
    """Grow bounds so width/height == aspect, keeping the centre."""
    x0, y0, x1, y1 = bounds
    w, h = x1 - x0, y1 - y0
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    if w / max(h, 1e-9) < aspect:
        w = h * aspect
    else:
        h = w / aspect
    return (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)


def nice_length(target):
    exp = 10 ** math.floor(math.log10(max(target, 1)))
    for m in (1, 2, 5, 10):
        if m * exp >= target:
            return m * exp
    return 10 * exp


def scalebar_north(ax, fs=8):
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    w, h = x1 - x0, y1 - y0
    L = nice_length(w / 6)
    bx, by = x0 + w * 0.04, y0 + h * 0.05
    seg = L / 4
    for i in range(4):
        ax.add_patch(Rectangle((bx + i * seg, by), seg, h * 0.008, fc=INK if i % 2 == 0 else PAPER, ec=INK,
                               lw=0.6, zorder=20))
    lab = ("%g km" % (L / 1000)) if L >= 1000 else ("%g m" % L)
    ax.text(bx, by + h * 0.016, "0", fontsize=fs - 1, color=INK, zorder=20, ha="center")
    ax.text(bx + L, by + h * 0.016, lab, fontsize=fs - 1, color=INK, zorder=20, ha="center")
    nx, ny = x1 - w * 0.05, y1 - h * 0.13
    ax.add_patch(FancyArrow(nx, ny, 0, h * 0.06, width=w * 0.004, head_width=w * 0.016, head_length=h * 0.025,
                            length_includes_head=True, fc=INK, ec=INK, zorder=20))
    ax.text(nx, ny + h * 0.068, "N", ha="center", va="bottom", fontsize=fs + 1, color=INK, zorder=20,
            fontweight="bold")


def legend(ax, items, title=None, loc="upper left", ncol=1, fs=8):
    handles = []
    for kind, color, label, *extra in items:
        if kind == "patch":
            handles.append(Rectangle((0, 0), 1, 1, fc=color, ec=extra[0] if extra else "none", lw=.6, label=T(label)))
        elif kind == "line":
            st = extra[0] if extra else {}
            handles.append(Line2D([0], [0], color=color, lw=st.get("lw", 1.5), ls=st.get("ls", "-"), label=T(label)))
        elif kind == "marker":
            handles.append(Line2D([0], [0], marker="o", color="none", markerfacecolor=color, markeredgecolor=INK,
                                  markersize=6, label=T(label)))
    leg = ax.legend(handles=handles, loc=loc, frameon=False, fontsize=fs, title=T(title) if title else None,
                    title_fontsize=fs + 1, ncol=ncol, alignment="left")
    return leg


def building(ax, p, g, color, z=7, alpha=0.92, ec="none", lw=0.0):
    """Solid footprint, or a hatched roof for form = canopy (roof on posts, no floor area)."""
    if p.get("form") == "canopy":
        fill(ax, g, "#EFE6CF", ec="#8A7440", lw=0.4, z=z - 0.5, hatch="////", alpha=0.9)
    else:
        fill(ax, g, color, ec=ec, lw=lw, z=z, alpha=alpha)


def site_context(ax, pkg, lead=True):
    fill(ax, pkg.site, "#FFFFFF", alpha=0.25, z=1)
    outline(ax, pkg.site, color=RED, lw=1.4, z=8)
    if lead:
        fill(ax, pkg.lead, "#E4C87A", ec="#8A7440", lw=0.6, alpha=0.9, z=7, hatch="////")


# ------------------------------------------------------------------------------- pages
def new_page(pkg, size, num, title, subtitle=""):
    fig = plt.figure(figsize=size, facecolor=PAPER)
    fs = 1.0 if size == A3 else 2.4
    fig.text(0.03, 0.965, "XCITY AI COMPETITION  ·  1,656 KM²  ·  SAN JUAN, ARGENTINA", fontsize=8 * fs,
             color=GOLD, fontweight="bold")
    t = T(pkg.title)
    fig.text(0.03, 0.935, t, fontsize=15 * fs, color=INK, va="top", fontweight="bold")
    if num:
        fig.text(0.97, 0.965, "%s  ·  %s" % (num, T(title)), fontsize=8.5 * fs, color=GOLD, ha="right",
                 fontweight="bold")
        if subtitle:
            fig.text(0.97, 0.895, T(subtitle), fontsize=8.5 * fs, color=MUTED, ha="right", va="top")
    footer(fig, pkg, fs)
    return fig


def footer(fig, pkg, fs=1.0):
    a = pkg.man.get("author", {})
    ag = pkg.man.get("agent", {})
    au = pkg.man.get("autonomy", {})
    left = "submissions/%s/%s  ·  %s  ·  agent: %s (%s)  ·  autonomy: %s" % (
        pkg.login, pkg.slug, T(a.get("responsible_party", "")), T(ag.get("name", "")), T(ag.get("model", "")),
        au.get("class", ""))
    right = "scripts/make_figures.py v%s  ·  input %s" % (xc.SCRIPT_VERSION, pkg.input_hash[:12])
    src = ("Sources: parcels and pilot area - XCITY (owner KML); terrain and channels - produced using Copernicus "
           "WorldDEM-30 (c) DLR e.V. 2010-2014 and (c) Airbus Defence and Space GmbH 2014-2018 provided under COPERNICUS "
           "by the European Union and ESA; all rights reserved; roads (c) OpenStreetMap contributors. Everything else: "
           "this submission's own geometry.")
    fig.text(0.03, 0.028, textwrap.shorten(left, 150, placeholder=" ..."), fontsize=6.5 * fs, color=MUTED)
    fig.text(0.97, 0.028, right, fontsize=6.5 * fs, color=MUTED, ha="right")
    fig.text(0.03, 0.012, src, fontsize=5.5 * fs, color=MUTED)


def side_text(ax, blocks, fs=8.5, width=58):
    """blocks: list of (heading, text). Draw top-down in an axis-free panel."""
    ax.set_axis_off()
    h_in = ax.get_position().height * ax.figure.get_size_inches()[1]
    step = (fs * 1.42 / 72) / max(h_in, 0.1)
    y = 1.0
    for head, body in blocks:
        if head:
            for hl in textwrap.wrap(T(head), width=max(20, int(width * 0.9))) or [""]:
                ax.text(0, y, hl, fontsize=fs + .5, fontweight="bold", color=INK, va="top", transform=ax.transAxes)
                y -= step * 1.08
            y -= step * 0.15
        for para in (body or "").split("\n"):
            lines = textwrap.wrap(T(para), width=width) or [""]
            for ln in lines:
                ax.text(0, y, ln, fontsize=fs, color=INK, va="top", transform=ax.transAxes)
                y -= step
        y -= step * 0.7
    return y


def metric_value(pkg, key):
    m = pkg.metrics.get(key)
    if not m:
        return None
    return m.get("value")


def fmt(v, unit=""):
    if v is None:
        return "-"
    if isinstance(v, dict):
        return ", ".join("%s %s" % (k, fmt(x)) for k, x in v.items())
    if isinstance(v, (int, float)):
        if isinstance(v, float) and abs(v) < 10 and v != int(v):
            s = "%.2f" % v
        else:
            s = "{:,.0f}".format(v)
        return s + ((" " + unit) if unit else "")
    return T(v)


# ------------------------------------------------------------------------------- panels (draw into an axes)
def panel_structure(pkg, ax, compact=False):
    hillshade(ax, pkg)
    site_context(ax, pkg)
    base=[(p,g) for p,g in pkg.geo['structure'] if p.get('plan_role')=='base_zoning']
    shown=base or pkg.geo['structure']
    use_colors={'housing':'#C96B5C','mixed_use':'#BA5B43','agriculture':'#D4B567','solar_agriculture':'#E0C86D','compute':'#3F8398','industry':'#8B75A8','logistics':'#43836F','ecology':'#A8BC99','reserve':'#CBC7BA','fixed_context':'#E8D699'}
    for p,g in shown:
        color=use_colors.get(p.get('primary_use'),SYSTEM_COLORS.get(p.get('system','reserve'),'#999999'))
        fill(ax,g.intersection(pkg.site),color,ec='white',lw=.5,alpha=.78,z=3)
        if base and not compact:
            q=g.representative_point()
            ax.text(q.x,q.y,p.get('district_id',''),fontsize=7,color=INK,ha='center',zorder=10)
    # Draw submitted roads; the renderer must not omit the whole-site skeleton.
    classes={'primary':(INK,2.0),'secondary':('#685E4C',1.15),'local':('#A39B8B',0.45)}
    road_classes=set()
    for props, route in pkg.geo['movement']:
        if route.geom_type not in ('LineString','MultiLineString'):continue
        level=props.get('road_class')
        if level in classes:
            color,width=classes[level];road_classes.add(level)
            outline(ax,route.intersection(pkg.site),color=color,lw=width,z=7)
        elif props.get('network') in ('shared','machine'):
            outline(ax,route.intersection(pkg.site),color='#A7A29A',lw=.35,z=6)
    if not any(p.get('plan_role')=='base_zoning' for p,g in pkg.geo['structure']):
        ax.text(.01,.985,'SYSTEM OVERLAY ONLY - FULL-SITE BASE ZONING MISSING',transform=ax.transAxes,
                va='top',fontsize=7 if not compact else 10,color=RED,zorder=20,
                bbox=dict(facecolor=PAPER,edgecolor='none',alpha=.9))
    channels(ax, pkg, primary=not compact, z=4)
    if pkg.master is not None:
        outline(ax, pkg.master, color=INK, lw=1.6, ls="--", z=9)
    for nid, (p, g) in pkg.nodes.items():
        c = g.centroid
        ax.plot(c.x, c.y, marker="o", ms=7 if not compact else 10, mfc=GOLD, mec=INK, zorder=12)
        ax.text(c.x, c.y, "  " + nid, fontsize=8 if not compact else 14, color=INK, zorder=12, va="center",
                fontweight="bold")
    for p, g in pkg.parcels:
        c = g.representative_point()
        ax.text(c.x, c.y, p.get("name_en", ""), fontsize=8 if not compact else 14, color=RED,
                alpha=.8, zorder=11, ha="center")
    frame(ax, fit_aspect(pkg.site.bounds, ax_aspect(ax)), pad=0.03)
    scalebar_north(ax, 8 if not compact else 16)
    km2 = pkg.computed["structure_km2"]
    items = [("patch", SYSTEM_COLORS.get(s, "#999"), "%s  %s km²" % (SYSTEM_LABEL.get(s, s), fmt(round(v, 1))))
             for s, v in sorted(km2.items(), key=lambda kv: -kv[1])]
    if base:
        uses={}
        for props,area in base:
            key=props.get('primary_use','reserve');uses[key]=uses.get(key,0)+area.intersection(pkg.site).area/1e6
        items=[('patch',use_colors.get(key,'#999999'),key.replace('_',' ').title()+'  '+fmt(round(area,1))+' km²') for key,area in sorted(uses.items(),key=lambda row:-row[1])]
    if 'primary' in road_classes:items += [('line', INK, 'Proposed primary road', {'lw':2})]
    if 'secondary' in road_classes:items += [('line', '#685E4C', 'Proposed secondary road', {'lw':1.15})]
    items += [("line", RED, "Site boundary (1,656 km²)", {"lw": 1.4}),
              ("patch", "#E4C87A", "Pilot area - fixed, not designed", "#8A7440"),
              ("line", INK, "Master design area", {"lw": 1.6, "ls": "--"}),
              ("line", WATER, "Seasonal channels (DEM-derived)", {"lw": 1.2}),
              ("marker", GOLD, "Key nodes")]
    return items


def ax_aspect(ax):
    bb = ax.get_position()
    fw, fh = ax.figure.get_size_inches()
    return (bb.width * fw) / (bb.height * fh)


def master_window(pkg, ax, pad=600):
    if pkg.master is None:
        return pkg.site.bounds
    return fit_aspect(pkg.master.buffer(pad).bounds, ax_aspect(ax))


def panel_master(pkg, ax, compact=False, window=None):
    win = window if window is not None else master_window(pkg, ax)
    W = box(*win)
    hillshade(ax, pkg, alpha=0.35)
    site_context(ax, pkg)
    for p, g in pkg.geo["land_use"]:
        if g.intersects(W):
            fill(ax, g, USE_COLORS.get(p.get("use"), "#DDD"), ec="white", lw=0.3, alpha=0.9, z=3)
    channels(ax, pkg, window=W, z=4)
    for p, g in pkg.geo["movement"]:
        if g.geom_type.endswith("LineString") and g.intersects(W):
            st = NET_STYLE.get(p.get("network"), NET_STYLE["people"])
            outline(ax, g, color=st["color"], lw=st["lw"] * .7, ls=st["ls"], z=6, alpha=.85)
    for p, g in pkg.geo["buildings"]:
        if g.intersects(W):
            building(ax, p, g, "#2B2A28", z=7)
    if pkg.master is not None:
        outline(ax, pkg.master, color=INK, lw=1.4, ls="--", z=9)
    for nid, (p, g) in pkg.nodes.items():
        if g.intersects(W):
            outline(ax, g, color=GOLD, lw=1.6, z=10)
            c = g.centroid
            ax.text(c.x, c.y, nid, fontsize=9 if not compact else 18, color=GOLD, fontweight="bold", zorder=11,
                    ha="center", va="center", path_effects=[withStroke(linewidth=2.5, foreground="white")])
    frame(ax, win, pad=0)
    label_places(pkg, ax, W, compact)
    dimension_city(pkg, ax, compact)
    scalebar_north(ax, 8 if not compact else 16)
    uses = sorted({p.get("use") for p, g in pkg.geo["land_use"] if g.intersects(W)} - {None})
    items = [("patch", USE_COLORS.get(u, "#DDD"), u.replace("_", " ").capitalize()) for u in uses]
    items += [("patch", "#2B2A28", "Buildings (figure-ground)"),
              ("line", INK, "Master design area", {"lw": 1.4, "ls": "--"}),
              ("line", GOLD, "Key node", {"lw": 1.6}),
              ("line", WATER, "Seasonal channel", {"lw": 1.2})]
    return items


def label_places(pkg, ax, W, compact=False, limit=18):
    """Name the places: every land-use name that is not repeated more than twice, biggest first, not crowded."""
    from collections import Counter
    named = []
    for p, g in pkg.geo["land_use"]:
        n = str(p.get("name") or "").split(":")[0].split(" - ")[0].split(" (")[0].strip()
        if n and g.intersects(W):
            named.append((n, g.intersection(W)))
    cnt = Counter(n for n, _ in named)
    x0, y0, x1, y1 = W.bounds
    gap = max(x1 - x0, y1 - y0) * 0.055
    placed = []
    (ax0, ax1), (ay0, ay1) = ax.get_xlim(), ax.get_ylim()
    view = box(ax0 + (ax1 - ax0) * 0.06, ay0 + (ay1 - ay0) * 0.04, ax1 - (ax1 - ax0) * 0.06, ay1 - (ay1 - ay0) * 0.04)
    for n, g in sorted(named, key=lambda t: -t[1].area):
        if cnt[n] > 2 or n in [q for q, _ in placed] or g.is_empty:
            continue
        g = g.intersection(view)
        if g.is_empty:
            continue
        c = g.representative_point()
        if any(c.distance(q) < gap for _, q in placed):
            continue
        ax.text(c.x, c.y, textwrap.fill(T(n), 20), fontsize=6.3 if not compact else 12, ha="center", va="center",
                color=INK, zorder=13, linespacing=0.95, path_effects=[withStroke(linewidth=2.2, foreground="white")])
        placed.append((n, c))
        if len(placed) >= limit:
            break


def dimension_city(pkg, ax, compact=False):
    """Overall dimensions of the built-up area (homes and shops) and of one block, as dimension lines."""
    town = [g for p, g in pkg.geo["buildings"] if p.get("use") in ("residential", "mixed_use")]
    if len(town) < 4:
        return
    x0, y0, x1, y1 = unary_union(town).bounds
    off = max(x1 - x0, y1 - y0) * 0.05
    fs = 7 if not compact else 14
    kw = dict(arrowprops=dict(arrowstyle="<->", color=INK, lw=0.8), zorder=14)
    ax.annotate("", xy=(x0, y0 - off), xytext=(x1, y0 - off), **kw)
    ax.text((x0 + x1) / 2, y0 - off * 1.25, "%s m" % fmt(round((x1 - x0) / 10) * 10), ha="center", va="top",
            fontsize=fs, color=INK, zorder=14, path_effects=[withStroke(linewidth=2, foreground="white")])
    ax.annotate("", xy=(x0 - off, y0), xytext=(x0 - off, y1), **kw)
    ax.text(x0 - off * 1.25, (y0 + y1) / 2, "%s m" % fmt(round((y1 - y0) / 10) * 10), ha="right", va="center",
            rotation=90, fontsize=fs, color=INK, zorder=14, path_effects=[withStroke(linewidth=2, foreground="white")])


def core_window(pkg, ax, pad=220):
    """The settlement core: residential and mixed-use buildings (falls back to the master area)."""
    tall = [g for p, g in pkg.geo["buildings"] if p.get("use") in ("residential", "mixed_use")]
    if not tall:
        return master_window(pkg, ax)
    return fit_aspect(unary_union(tall).buffer(pad).bounds, ax_aspect(ax))


FLOOR_BANDS = [(0, 1, "#F1E3C8", "1 floor"), (2, 3, "#E2B98B", "2-3 floors"), (4, 6, "#C98763", "4-6 floors"),
               (7, 999, "#8E4E3A", "7+ floors")]


def floor_color(f):
    for lo, hi, c, _ in FLOOR_BANDS:
        if lo <= f <= hi:
            return c
    return FLOOR_BANDS[0][2]


def panel_density(pkg, ax, compact=False):
    win = core_window(pkg, ax)
    W = box(*win)
    hillshade(ax, pkg, alpha=0.25)
    for p, g in pkg.geo["land_use"]:
        if g.intersects(W):
            fill(ax, g, USE_COLORS.get(p.get("use"), "#DDD"), alpha=0.35, z=2)
    for p, g in pkg.geo["buildings"]:
        if g.intersects(W):
            f = int(round(float(p.get("floors", 1) or 1)))
            building(ax, p, g, floor_color(f), z=6, alpha=1.0, ec="#5A4636", lw=0.25)
    if pkg.master is not None:
        outline(ax, pkg.master, color=INK, lw=1.4, ls="--", z=9)
    frame(ax, win, pad=0)
    scalebar_north(ax, 8 if not compact else 16)
    label_places(pkg, ax, W, compact=compact, limit=14)
    return [("patch", c, lab, "#5A4636") for _, _, c, lab in FLOOR_BANDS] + \
           [("line", INK, "Master design area", {"lw": 1.4, "ls": "--"})]


def panel_movement(pkg, ax, compact=False, window=None):
    win = window or master_window(pkg, ax)
    W = box(*win)
    hillshade(ax, pkg, alpha=0.25)
    for p, g in pkg.geo["land_use"]:
        if g.intersects(W):
            fill(ax, g, "#E9E5DC", ec="white", lw=.3, z=2)
    for p, g in pkg.geo["buildings"]:
        if g.intersects(W):
            building(ax, p, g, "#BDB7AC", z=3, alpha=1.0)
    for p, g in pkg.geo["movement"]:
        if g.geom_type.endswith("LineString") and g.intersects(W):
            st = NET_STYLE.get(p.get("network"), NET_STYLE["people"])
            outline(ax, g, color=st["color"], lw=st["lw"] * (1.0 if not compact else 2.2), ls=st["ls"], z=6)
    k = 0
    for p, g in pkg.geo["movement"]:
        if p.get("kind") == "interface" and g.geom_type == "Point":
            k += 1
            if g.intersects(W):
                ax.plot(g.x, g.y, "o", ms=9 if not compact else 18, mfc="white", mec=RED, mew=1.4, zorder=9)
                ax.text(g.x, g.y, str(k), fontsize=6 if not compact else 11, ha="center", va="center", color=RED,
                        zorder=10, fontweight="bold")
    if pkg.master is not None:
        outline(ax, pkg.master, color=INK, lw=1.2, ls="--", z=8)
    frame(ax, win, pad=0)
    scalebar_north(ax, 8 if not compact else 16)
    nk = pkg.computed["network_km"]
    return [("line", NET_STYLE["people"]["color"], "People  %s km" % fmt(round(nk["people"], 1)), NET_STYLE["people"]),
            ("line", NET_STYLE["machine"]["color"], "Machines + goods  %s km" % fmt(round(nk["machine"], 1)),
             NET_STYLE["machine"]),
            ("line", NET_STYLE["shared"]["color"], "Shared  %s km" % fmt(round(nk["shared"], 1)), NET_STYLE["shared"]),
            ("marker", "white", "Human-machine interface (%d)" % pkg.computed["human_machine_interfaces"])]


def panel_open(pkg, ax, compact=False):
    win = master_window(pkg, ax)
    W = box(*win)
    hillshade(ax, pkg, alpha=0.3)
    for p, g in pkg.channels:
        if g.intersects(W):
            fill(ax, g.buffer(250 if p.get("class") == "main" else 100), "#CFE0EE", alpha=0.7, z=2)
    for p, g in pkg.geo["land_use"]:
        if g.intersects(W):
            u = p.get("use")
            if u == "open_space":
                fill(ax, g, USE_COLORS["open_space"], ec="white", lw=.3, z=3)
            elif u == "agriculture":
                fill(ax, g, USE_COLORS["agriculture"], alpha=.6, z=3)
            else:
                fill(ax, g, "#ECE8E0", z=3)
    for p, g in pkg.geo["buildings"]:
        if g.intersects(W):
            building(ax, p, g, "#BDB7AC", z=4, alpha=1.0)
    channels(ax, pkg, window=W, z=5)
    for p, g in pkg.geo["movement"]:
        if g.geom_type.endswith("LineString") and g.intersects(W) and p.get("network") in ("people", "shared"):
            outline(ax, g, color="#2E7D32" if p.get("shaded") else "#B0A898", lw=2.2 if p.get("shaded") else 1.0,
                    z=6)
    if pkg.master is not None:
        outline(ax, pkg.master, color=INK, lw=1.2, ls="--", z=8)
    frame(ax, win, pad=0)
    scalebar_north(ax, 8 if not compact else 16)
    c = pkg.computed
    return [("patch", USE_COLORS["open_space"], "Open space  %s%%" % fmt(round(c["open_space_pct"], 1))),
            ("patch", USE_COLORS["agriculture"], "Agriculture"),
            ("line", "#2E7D32", "Shaded walking  %s%%" % fmt(round(c["shaded_pedestrian_pct"], 1)), {"lw": 2.2}),
            ("line", "#B0A898", "Unshaded walking", {"lw": 1.0}),
            ("line", WATER, "Seasonal channel", {"lw": 1.2}),
            ("patch", "#CFE0EE", "Flood corridor shown at 250 m / 100 m")]


def panel_phasing(pkg, ax, compact=False):
    hillshade(ax, pkg, alpha=0.45)
    site_context(ax, pkg)
    ph = sorted(pkg.geo["phasing"], key=lambda pg: -int(pg[0].get("phase", 0) or 0))
    for p, g in ph:
        n = int(p.get("phase", 0) or 0)
        fill(ax, g, PHASE_COLORS.get(n, "#DDD"), ec=INK, lw=0.5, alpha=0.85, z=3 + (4 - n))
        c = g.representative_point()
        ax.text(c.x, c.y, str(n)+( " · "+str(p["zone_id"]) if p.get("zone_id") else ""), fontsize=11 if not compact else 22, fontweight="bold", color=INK, zorder=10,
                ha="center", va="center")
    channels(ax, pkg, primary=False, z=9)
    allg = unary_union([g for _, g in pkg.geo["phasing"]] + ([pkg.master] if pkg.master is not None else []))
    b = allg.buffer(3000).bounds if not allg.is_empty else pkg.site.bounds
    hb = pkg.hs_bounds
    b = (max(b[0], hb[0]), max(b[1], hb[1]), min(b[2], hb[2]), min(b[3], hb[3]))
    frame(ax, fit_aspect(b, ax_aspect(ax)), pad=0)
    scalebar_north(ax, 8 if not compact else 16)
    items = []
    for n in (1, 2, 3):
        a = sum(xc.geodesic_km2(xc.to_lonlat(g)) for p, g in pkg.geo["phasing"] if int(p.get("phase", 0) or 0) == n)
        items.append(("patch", PHASE_COLORS[n], "Phase %d  %s km²" % (n, fmt(round(a, 2))), INK))
    return items


def phase_triggers(pkg):
    out = []
    for p, g in sorted(pkg.geo["phasing"], key=lambda pg: int(pg[0].get("phase", 0) or 0)):
        n = int(p.get("phase", 0) or 0)
        t = p.get("trigger") or ("Phase one: no trigger." if n == 1 else "")
        nm = T(p.get("name", ""))
        out.append((nm if nm.lower().startswith("phase") else "Phase %d - %s" % (n, nm), T(t)))
    return out


def panel_metrics(pkg, ax, compact=False):
    ax.set_axis_off()
    rows = pkg.metrics_doc.get("metrics", [])
    comp = pkg.computed
    head = ["Metric", "Declared", "Unit", "Evidence", "Basis / check"]
    data = []
    for m in rows:
        k = m.get("key", "")
        v = m.get("value")
        ev = m.get("evidence", "")
        basis = m.get("computed_from") or m.get("source") or m.get("assumption") or ""
        if ev == "computed" and k in comp:
            cv = comp[k]
            if isinstance(cv, dict):
                basis = "recomputed: per system"
            else:
                basis = "recomputed %s" % fmt(cv)
        data.append([k, fmt(v) if not isinstance(v, dict) else "per system", m.get("unit", ""), ev, T(basis)[:42]])
    n = max(len(data), 1)
    fs = (7.2 if n <= 30 else 6.0) * (1 if not compact else 2.2)
    tab = ax.table(cellText=data or [["-"] * 5], colLabels=head, loc="upper left", cellLoc="left",
                   colWidths=[0.30, 0.16, 0.10, 0.12, 0.32])
    tab.auto_set_font_size(False)
    tab.set_fontsize(fs)
    tab.scale(1, 1.18 if not compact else 1.0)
    for (r, c), cell in tab.get_celld().items():
        cell.set_edgecolor("#DAD5CB")
        cell.set_linewidth(0.4)
        if r == 0:
            cell.set_facecolor("#ECE6D8")
            cell.set_text_props(fontweight="bold")
        else:
            cell.set_facecolor(PAPER)
            if c == 3:
                ev = data[r - 1][3] if data else ""
                cell.set_facecolor({"computed": "#DCEBD3", "sourced": "#D6E4F0", "assumed": "#F4E3C6",
                                    "indicative": "#EADDF0"}.get(ev, PAPER))
    return [("patch", "#DCEBD3", "computed - recomputed from your geometry"),
            ("patch", "#D6E4F0", "sourced - cited in sources.json"),
            ("patch", "#F4E3C6", "assumed - declared in assumptions.json"),
            ("patch", "#EADDF0", "indicative - organiser's indicative material")]


# ------------------------------------------------------------------------------- perspective renderer
class Camera:
    def __init__(self, pos, target, hfov_deg, aspect):
        self.p = np.asarray(pos, float)
        f = np.asarray(target, float) - self.p
        self.f = f / np.linalg.norm(f)
        up = np.array([0, 0, 1.0])
        r = np.cross(self.f, up)
        if np.linalg.norm(r) < 1e-6:
            r = np.array([1.0, 0, 0])
        self.r = r / np.linalg.norm(r)
        self.u = np.cross(self.r, self.f)
        self.k = 1 / math.tan(math.radians(hfov_deg) / 2)
        self.aspect = aspect
        self.near = 0.5

    def cam(self, P):
        d = np.asarray(P, float) - self.p
        return np.stack([d @ self.r, d @ self.u, d @ self.f], axis=-1)

    def proj(self, C):
        return np.stack([self.k * C[:, 0] / C[:, 2], self.k * C[:, 1] / C[:, 2]], axis=-1)


def clip_near(C, near):
    """Sutherland-Hodgman clip of a polygon (camera coords) against z > near."""
    out = []
    n = len(C)
    for i in range(n):
        a, b = C[i], C[(i + 1) % n]
        ia, ib = a[2] > near, b[2] > near
        if ia:
            out.append(a)
        if ia != ib:
            t = (near - a[2]) / (b[2] - a[2])
            out.append(a + t * (b - a))
    return np.array(out) if len(out) >= 3 else None


def shade(hex_color, k):
    c = np.array(matplotlib.colors.to_rgb(hex_color))
    return tuple(np.clip(c * k, 0, 1))


SUN = np.array([0.25, 0.55, 0.80])     # from the north-north-east, high: southern-hemisphere midday
SUN = SUN / np.linalg.norm(SUN)


def soft(hex_color, k=0.55, base="#E6DCC8"):
    """Ground tint: land-use colour pulled towards desert sand, so buildings read against it."""
    a = np.array(matplotlib.colors.to_rgb(hex_color))
    b = np.array(matplotlib.colors.to_rgb(base))
    return tuple(a * (1 - k) + b * k)


def _no_holes(poly):
    """Polygons without interiors, for the painter's renderer."""
    if not poly.interiors:
        return [poly]
    try:
        from shapely import constrained_delaunay_triangles
        tris = constrained_delaunay_triangles(poly)
        return [t for t in tris.geoms if t.area > 0]
    except ImportError:
        from shapely.ops import triangulate
        return [t for t in triangulate(poly) if poly.contains(t.representative_point())]


def scene(pkg, centre, radius):
    """Ground polygons and building prisms within radius of centre (UTM)."""
    W = Point(centre).buffer(radius)
    ground = []
    for p, g in pkg.geo["land_use"]:
        if g.intersects(W):
            for poly in _polys(g.intersection(W)):
                for piece in _no_holes(poly):
                    ground.append((np.asarray(piece.exterior.coords)[:, :2], soft(USE_COLORS.get(p.get("use"), "#DDD")), 0))
    widths = {"people": 4, "machine": 7, "shared": 9}
    for p, g in pkg.geo["movement"]:
        if g.geom_type.endswith("LineString") and g.intersects(W):
            w = widths.get(p.get("network"), 5)
            col = {"people": "#E8DCCB", "machine": "#6E7279", "shared": "#B9AFC9"}.get(p.get("network"), "#CCC")
            for ln in _lines(g.intersection(W)):
                c = list(ln.coords)
                for a, b in zip(c[:-1], c[1:]):
                    seg = LineString([a, b]).buffer(w / 2, cap_style=2, join_style=2)
                    ground.append((np.asarray(seg.exterior.coords)[:, :2], col, 1))
    for p, g in pkg.channels:
        if g.intersects(W):
            for poly in _polys(g.intersection(W).buffer(18 if p.get("class") == "main" else 8)):
                ground.append((np.asarray(poly.exterior.coords)[:, :2], "#BFD3E2", 1))
    prisms = []
    for p, g in pkg.geo["buildings"]:
        if g.intersects(W):
            h = float(p.get("height_m") or 0) or max(1.0, float(p.get("floors", 1) or 1)) * FLOOR_H
            col = USE_COLORS.get(p.get("use"), "#D9D2C5")
            canopy = p.get("form") == "canopy"
            for poly in _polys(g):
                prisms.append((np.asarray(poly.exterior.coords)[:-1, :2], h, "#B7A27A" if canopy else col, canopy))
    return ground, prisms


def render(pkg, ax, cam, ground, prisms, horizon=True, title=None):
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1 / cam.aspect, 1 / cam.aspect)
    ax.set_aspect("equal")
    ax.set_axis_off()
    # sky gradient
    sky = np.linspace(0, 1, 64)[:, None]
    skyc = np.dstack([0.90 - 0.38 * sky, 0.93 - 0.24 * sky, 0.97 - 0.10 * sky])
    ax.imshow(skyc, extent=[-1, 1, -1 / cam.aspect, 1 / cam.aspect], origin="lower", zorder=0, aspect="auto")
    # distant terrain silhouette from the DEM
    if horizon:
        az0 = math.atan2(cam.f[1], cam.f[0])
        half = math.atan(1 / cam.k) * 1.05
        angs = np.linspace(az0 + half, az0 - half, 160)
        dists = np.linspace(400, 60000, 220)
        cz = float(pkg.dem_at(cam.p[0], cam.p[1]))
        pts = []
        for a in angs:
            xs = cam.p[0] + np.cos(a) * dists
            ys = cam.p[1] + np.sin(a) * dists
            z = pkg.dem_at(xs, ys) - cz - (dists ** 2) / (2 * 6.371e6) * 0.87
            P = np.stack([xs, ys, z + 0.0], axis=1)
            C = cam.cam(P)
            ok = C[:, 2] > 1
            if not ok.any():
                continue
            S = cam.proj(C[ok])
            pts.append((S[:, 0].mean(), S[:, 1].max()))
        if pts:
            pts = np.array(pts)
            poly = np.vstack([[pts[0, 0], -1 / cam.aspect], pts, [pts[-1, 0], -1 / cam.aspect]])
            ax.add_patch(MPoly(poly, closed=True, fc="#B9A98F", ec="none", zorder=1, alpha=0.9))
    # base ground plane
    R = 30000
    base = np.array([[cam.p[0] - R, cam.p[1] - R], [cam.p[0] + R, cam.p[1] - R], [cam.p[0] + R, cam.p[1] + R],
                     [cam.p[0] - R, cam.p[1] + R]])
    faces = []

    def add_ground(xy, col, layer, z=0.0):
        P = np.column_stack([xy, np.full(len(xy), z)])
        C = clip_near(cam.cam(P), cam.near)
        if C is not None:
            faces.append((-1e12 + layer, cam.proj(C), col, 0, []))

    add_ground(base, "#D8CBB2", -2)
    for xy, col, layer in ground:
        add_ground(xy, col, layer, z=0.05 * (layer + 1))
    for xy, h, col, canopy in prisms:
        n = len(xy)
        if canopy:
            # a roof on posts: the slab, seen from above or below, and its posts
            P = np.column_stack([xy, np.full(n, h)])
            C = clip_near(cam.cam(P), cam.near)
            if C is not None:
                k = 1.0 if cam.p[2] > h else 0.72
                posts = []
                for q in xy:
                    Lc = cam.cam(np.array([[q[0], q[1], 0.0], [q[0], q[1], h]]))
                    if (Lc[:, 2] > cam.near).all():
                        posts.append(cam.proj(Lc))
                faces.append((float(np.mean(C[:, 2])), cam.proj(C), shade(col, k), 1, posts))
            continue
        ccw = (np.sum(xy[:, 0] * np.roll(xy[:, 1], -1) - np.roll(xy[:, 0], -1) * xy[:, 1]) > 0)
        for i in range(n):
            a, b = xy[i], xy[(i + 1) % n]
            e = b - a
            nrm = np.array([e[1], -e[0], 0.0]) if ccw else np.array([-e[1], e[0], 0.0])
            nn = np.linalg.norm(nrm)
            if nn < 1e-6:
                continue
            nrm /= nn
            mid = np.array([(a[0] + b[0]) / 2, (a[1] + b[1]) / 2, h / 2])
            if np.dot(nrm, cam.p - mid) <= 0:
                continue
            P = np.array([[a[0], a[1], 0], [b[0], b[1], 0], [b[0], b[1], h], [a[0], a[1], h]])
            C = clip_near(cam.cam(P), cam.near)
            if C is None:
                continue
            k = 0.62 + 0.38 * max(0.0, float(np.dot(nrm, SUN)))
            lines = []
            for fl in np.arange(FLOOR_H, h - 0.5, FLOOR_H):
                Lc = cam.cam(np.array([[a[0], a[1], fl], [b[0], b[1], fl]]))
                if (Lc[:, 2] > cam.near).all():
                    lines.append(cam.proj(Lc))
            faces.append((float(np.mean(C[:, 2])), cam.proj(C), shade(col, k), 1, lines))
        if cam.p[2] > h:
            P = np.column_stack([xy, np.full(n, h)])
            C = clip_near(cam.cam(P), cam.near)
            if C is not None:
                faces.append((float(np.mean(C[:, 2])) - 0.01, cam.proj(C), shade(col, 1.05), 1, []))
    ground_faces = sorted([f for f in faces if f[3] == 0], key=lambda f: f[0])
    solid = sorted([f for f in faces if f[3] == 1], key=lambda f: -f[0])
    for _, S, col, _, _ in ground_faces:
        ax.add_patch(MPoly(S, closed=True, fc=col, ec="none", zorder=2))
    for i, (_, S, col, _, lines) in enumerate(solid):
        ax.add_patch(MPoly(S, closed=True, fc=col, ec="#3B3631", lw=0.25, zorder=3 + i * 1e-6))
        for Lp in lines:
            ax.plot(Lp[:, 0], Lp[:, 1], color="#3B3631", lw=0.2, alpha=0.45, zorder=3 + i * 1e-6 + 5e-7)
    if title:
        ax.text(-0.98, 1 / cam.aspect - 0.03, T(title), fontsize=8, color=INK, va="top", zorder=5,
                bbox=dict(fc=PAPER, ec="none", alpha=.8, pad=2))


def node_cameras(pkg, nid, aspect):
    p, g = pkg.nodes[nid]
    c = np.array([g.centroid.x, g.centroid.y])
    rad = max(80.0, math.sqrt(max(g.area, 1)) * 0.75)
    # aerial: from north-north-west, about 35 degrees down
    if p.get("aerial_from"):
        pos = np.array(xc.to_utm(Point(*p["aerial_from"])).coords[0])
        apos = np.array([pos[0], pos[1], float(p.get("aerial_height_m", rad * 1.6))])
    else:
        d = rad * 2.6
        apos = np.array([c[0] - 0.42 * d, c[1] + 0.88 * d, d * 0.75])
    aerial = Camera(apos, [c[0], c[1], 0], 55, aspect)
    # eye level: on the walking network inside the node, looking at the centre
    if p.get("eye_from"):
        e = np.array(xc.to_utm(Point(*p["eye_from"])).coords[0])
        tgt = np.array(xc.to_utm(Point(*p["eye_to"])).coords[0]) if p.get("eye_to") else c
    else:
        e, tgt = None, c
        best = None
        for q, l in pkg.geo["movement"]:
            if q.get("network") in ("people", "shared") and l.geom_type.endswith("LineString") and l.intersects(g):
                seg = l.intersection(g.buffer(rad * 0.3))
                for ln in _lines(seg):
                    for frac in np.linspace(0.05, 0.95, 19):
                        pt = ln.interpolate(frac, normalized=True)
                        dd = pt.distance(Point(c))
                        score = abs(dd - rad * 0.55)
                        if best is None or score < best[0]:
                            best = (score, np.array([pt.x, pt.y]))
        if best is not None:
            e = best[1]
        else:
            b = g.exterior.interpolate(0.5, normalized=True)
            e = np.array([b.x, b.y])
    epos = np.array([e[0], e[1], 1.6])
    if np.linalg.norm(tgt - e) < 5:
        tgt = e + np.array([0, 50.0])
    eye = Camera(epos, [tgt[0], tgt[1], 6.0], 75, aspect)
    return aerial, eye, c, rad


def panel_node_plan(pkg, ax, nid, compact=False):
    p, g = pkg.nodes[nid]
    win = fit_aspect(g.buffer(max(60, math.sqrt(g.area) * 0.25)).bounds, ax_aspect(ax))
    W = box(*win)
    if pkg.lead.intersects(W):
        fill(ax, pkg.lead.intersection(W), "#E4C87A", ec="#8A7440", lw=0.6, alpha=0.9, z=1.5, hatch="////")
    outline(ax, pkg.site, color=RED, lw=1.2, z=9)
    for q, lu in pkg.geo["land_use"]:
        if lu.intersects(W):
            fill(ax, lu, USE_COLORS.get(q.get("use"), "#DDD"), ec="white", lw=.4, alpha=.9, z=2)
    channels(ax, pkg, window=W, z=3)
    for q, l in pkg.geo["movement"]:
        if l.geom_type.endswith("LineString") and l.intersects(W):
            st = NET_STYLE.get(q.get("network"), NET_STYLE["people"])
            outline(ax, l, color=st["color"], lw=st["lw"] * 1.4, ls=st["ls"], z=5)
    for q, b in pkg.geo["buildings"]:
        if b.intersects(W) and q.get("form") == "canopy":
            fill(ax, b, "#E2D3B0", ec="#8A7440", lw=0.5, z=6, hatch="////")
            continue
        if b.intersects(W):
            fill(ax, b, "#3A3632", z=6)
            if b.area > 150:
                c = b.representative_point()
                ax.text(c.x, c.y, str(int(round(float(q.get("floors", 1) or 1)))), fontsize=6 if not compact else 12,
                        color="white", ha="center", va="center", zorder=7)
    for q, pt in pkg.geo["movement"]:
        if q.get("kind") == "interface" and pt.geom_type == "Point" and pt.intersects(W):
            ax.plot(pt.x, pt.y, "o", ms=8, mfc="white", mec=RED, mew=1.4, zorder=8)
    outline(ax, g, color=GOLD, lw=2.0, z=9)
    frame(ax, win, pad=0)
    scalebar_north(ax, 8 if not compact else 16)


# ------------------------------------------------------------------------------- rendered views
def view_image(pkg, view_id):
    """Best image of a named view: a registered media/ image made from it (control_image), else the massing render
    in renders/ if it matches the geometry. Returns (path, credit) or (None, None)."""
    for im in pkg.prov:
        if im.get("control_image") == "renders/%s.png" % view_id:
            p = os.path.join(pkg.dir, str(im.get("path", "")))
            if os.path.isfile(p):
                return p, "%s · rendered with %s from the massing view %s · illustrates the geometry, not evidence" % (
                    view_id, im.get("model", "an image model"), view_id)
    if pkg.renders_ok and (view_id + ".png") in (pkg.renders.get("files") or {}):
        p = os.path.join(pkg.dir, "renders", view_id + ".png")
        if os.path.isfile(p):
            return p, "%s · massing view drawn from the geometry by render_views.py" % view_id
    return None, None


def view_ids(pkg, prefix):
    return sorted(f[:-4] for f in (pkg.renders.get("files") or {}) if f.startswith(prefix)) if pkg.renders_ok else []


def show_image(ax, path, credit=None, fs=6.5, max_w=1800):
    """Fill the axes with the image, cropped to the axes' shape (no distortion)."""
    im = Image.open(path).convert("RGB")
    ar = ax_aspect(ax)
    w, h = im.size
    if w / h > ar:
        nw = int(round(h * ar))
        x0 = (w - nw) // 2
        im = im.crop((x0, 0, x0 + nw, h))
    else:
        nh = int(round(w / ar))
        y0 = (h - nh) // 2
        im = im.crop((0, y0, w, y0 + nh))
    if im.width > max_w:
        im = im.resize((max_w, int(round(im.height * max_w / im.width))), Image.LANCZOS)
    ax.imshow(np.asarray(im), interpolation="none", aspect="auto")
    ax.set_xlim(-0.5, im.width - 0.5)
    ax.set_ylim(im.height - 0.5, -0.5)
    ax.set_axis_off()
    if credit:
        # wrap the credit to the width of the image so it never runs past the edge
        import textwrap
        width_pt = ax.get_position().width * ax.figure.get_figwidth() * 72
        chars = max(30, int(width_pt * 0.95 / (fs * 0.56)))
        ax.text(0.008, 0.012, textwrap.fill(T(credit), chars), transform=ax.transAxes, fontsize=fs, color="white",
                va="bottom", linespacing=1.25,
                bbox=dict(facecolor=(0, 0, 0, 0.42), edgecolor="none", pad=2.0), zorder=20)


def draw_node_views(pkg, nid, ax_aerial, ax_eye):
    pa, ca = view_image(pkg, "%s-aerial" % nid)
    pe, ce = view_image(pkg, "%s-eye-day" % nid)
    if pa and pe:
        show_image(ax_aerial, pa, ca)
        show_image(ax_eye, pe, ce)
        return
    _draw_node_views_massing(pkg, nid, ax_aerial, ax_eye)


def _draw_node_views_massing(pkg, nid, ax_aerial, ax_eye):
    aspect_a = ax_aspect(ax_aerial)
    aspect_e = ax_aspect(ax_eye)
    a1, _, c, rad = node_cameras(pkg, nid, aspect_a)
    _, e1, _, _ = node_cameras(pkg, nid, aspect_e)
    ground, prisms = scene(pkg, c, rad * 4)
    render(pkg, ax_aerial, a1, ground, prisms, horizon=True, title="Aerial - massing from geometry")
    ground2, prisms2 = scene(pkg, c, rad * 6)
    render(pkg, ax_eye, e1, ground2, prisms2, horizon=True, title="Eye level, 1.6 m - massing from geometry")


# ------------------------------------------------------------------------------- figure pages
FIGS = [
    ("fig-01-structure", "01", "Overall study - the five systems across the whole site", "Scale 1 · structural",
     panel_structure),
    ("fig-02-master-plan", "02", "Master design area - plan", "Scale 2 · figure-ground and land use", panel_master),
    ("fig-03-land-use-density", "03", "Land use and density", "Floors from buildings.geojson; metrics recomputed",
     panel_density),
    ("fig-04-movement", "04", "Movement - people, machines, shared", "Every human-machine interface numbered",
     panel_movement),
    ("fig-05-open-space-water", "05", "Open space, shade and water", "Channels are DEM-derived flow lines",
     panel_open),
    ("fig-06-phasing", "06", "Phasing - three phases and their triggers", "Observable triggers, not dates",
     panel_phasing),
    ("fig-07-metrics", "07", "Metrics and evidence", "Every declared figure with its evidence tag", panel_metrics),
]


def side_for(pkg, key, items):
    c = pkg.computed
    blocks = []
    if key == "fig-01-structure":
        blocks = [("Why the structure sits where it does", pkg.man.get("summary", ""))]
    elif key == "fig-02-master-plan":
        blocks = [("Master design area", "%s km² · drawn by the entrant" % fmt(round(c["master_area_km2"], 2))),
                  ("Recomputed", "Site coverage %s%% · FAR %s · GFA %s m²" % (
                      fmt(round(c["site_coverage_pct"], 1)), fmt(round(c["far"], 2)), fmt(round(c["gfa_m2"]))))]
    elif key == "fig-03-land-use-density":
        lu = c["land_use_ha"]
        blocks = [("Land use in the master area (ha)",
                   "\n".join("%s  %s" % (k.replace("_", " "), fmt(v)) for k, v in sorted(lu.items(), key=lambda kv: -kv[1]))),
                  ("Recomputed from geometry", "Coverage %s%% · FAR %s · open space %s%%" % (
                      fmt(round(c["site_coverage_pct"], 1)), fmt(round(c["far"], 2)), fmt(round(c["open_space_pct"], 1))))]
    elif key == "fig-04-movement":
        rule = metric_value(pkg, "machine_traffic_rule")
        blocks = [("Machine traffic rule", T(rule or "-")),
                  ("Interfaces", "%d at-grade points where people and machines meet" % c["human_machine_interfaces"])]
    elif key == "fig-06-phasing":
        blocks = phase_triggers(pkg)
    elif key == "fig-07-metrics":
        blocks = [("Gate G4", "Every metric tagged computed is recomputed from geometry/ by the self-check; a declared "
                              "value more than 2% away fails.")]
    return blocks


def draw_fig(pkg, key, num, title, sub, panel, size=A3):
    fig = new_page(pkg, size, "FIGURE " + num, title, sub)
    if key == "fig-07-metrics":
        ax = fig.add_axes([0.03, 0.07, 0.70, 0.80])
        items = panel(pkg, ax)
        side = fig.add_axes([0.76, 0.07, 0.21, 0.80])
        side.set_axis_off()
        legend(side, items, "Evidence tags")
        sa = fig.add_axes([0.76, 0.07, 0.21, 0.45])
        side_text(sa, side_for(pkg, key, items), width=40)
        return fig
    ax = fig.add_axes([0.03, 0.07, 0.68, 0.81])
    items = panel(pkg, ax)
    side = fig.add_axes([0.735, 0.47, 0.24, 0.41])
    side.set_axis_off()
    legend(side, items, "Legend")
    inset = None
    if key == "fig-04-movement":
        pts = [g for p, g in pkg.geo["movement"] if p.get("kind") == "interface" and g.geom_type == "Point"]
        if len(pts) >= 2:
            x0, x1 = ax.get_xlim()
            ib = unary_union(pts).buffer(120).bounds
            if (ib[2] - ib[0]) < 0.35 * (x1 - x0):
                inset = fig.add_axes([0.735, 0.07, 0.24, 0.24])
                panel_movement(pkg, inset, window=fit_aspect(ib, ax_aspect(inset)))
                inset.set_title("Interfaces, enlarged", fontsize=8, loc="left", color=INK)
                outline(ax, box(*inset.get_xlim()[:1] + inset.get_ylim()[:1] + inset.get_xlim()[1:] +
                                inset.get_ylim()[1:]), color=RED, lw=0.8, ls=":", z=12)
    sa = fig.add_axes([0.735, 0.33 if inset else 0.07, 0.24, 0.13 if inset else 0.38])
    side_text(sa, side_for(pkg, key, items), width=46)
    return fig


def draw_node_sheet(pkg, nid, size=A3):
    meta = pkg.node_meta.get(nid, {})
    p, g = pkg.nodes[nid]
    fig = new_page(pkg, size, "NODE " + nid, meta.get("en", nid),
                   p.get("name", "") or "Scale 3 · detailed design")
    pa, _ = view_image(pkg, "%s-aerial" % nid)
    pe, _ = view_image(pkg, "%s-eye-day" % nid)
    if not (pa and pe):        # no renders: the massing drawn here, as before
        axp = fig.add_axes([0.03, 0.07, 0.45, 0.81])
        panel_node_plan(pkg, axp, nid)
        axa = fig.add_axes([0.50, 0.49, 0.47, 0.39])
        axe = fig.add_axes([0.50, 0.07, 0.47, 0.39])
        draw_node_views(pkg, nid, axa, axe)
        reason = p.get("why") or pkg.man.get("nodes_reason", "")
        fig.text(0.03, 0.895, textwrap.shorten(T(reason), 150), fontsize=8, color=MUTED, va="top")
        return fig
    axp = fig.add_axes([0.03, 0.33, 0.33, 0.55])
    panel_node_plan(pkg, axp, nid)
    axp.set_title("Plan · floors marked on each building · interfaces circled", fontsize=7.5, color=MUTED, loc="left")
    tx = fig.add_axes([0.03, 0.07, 0.33, 0.23])
    side_text(tx, [(p.get("name", nid), p.get("why", ""))], fs=8.5, width=62)
    axa = fig.add_axes([0.385, 0.475, 0.585, 0.405])
    show_image(axa, pa, view_image(pkg, "%s-aerial" % nid)[1])
    others = [v for v in view_ids(pkg, "%s-eye-" % nid) if v != "%s-eye-day" % nid]
    pe2 = view_image(pkg, others[0]) if others else (None, None)
    if pe2[0]:
        axe = fig.add_axes([0.385, 0.07, 0.29, 0.39])
        show_image(axe, pe, view_image(pkg, "%s-eye-day" % nid)[1], fs=5.5)
        axn = fig.add_axes([0.68, 0.07, 0.29, 0.39])
        show_image(axn, pe2[0], pe2[1], fs=5.5)
    else:
        axe = fig.add_axes([0.385, 0.07, 0.585, 0.39])
        show_image(axe, pe, view_image(pkg, "%s-eye-day" % nid)[1])
    return fig


def save_node_images(pkg, nid, out, dpi):
    paths = {}
    f = plt.figure(figsize=(9, 9), facecolor=PAPER)
    ax = f.add_axes([0.02, 0.02, 0.96, 0.96])
    panel_node_plan(pkg, ax, nid)
    paths["plan"] = os.path.join(out, "node-%s-plan.png" % nid)
    f.savefig(paths["plan"], dpi=dpi, facecolor=PAPER)
    plt.close(f)
    for mode in ("aerial", "eye"):
        f = plt.figure(figsize=(12, 7.5), facecolor=PAPER)
        ax = f.add_axes([0, 0, 1, 1])
        ip, cr = view_image(pkg, "%s-%s" % (nid, "aerial" if mode == "aerial" else "eye-day"))
        if ip:
            show_image(ax, ip, cr, fs=8)
            paths[mode] = os.path.join(out, "node-%s-%s.png" % (nid, mode))
            f.savefig(paths[mode], dpi=dpi, facecolor=PAPER)
            plt.close(f)
            continue
        a, e, c, rad = node_cameras(pkg, nid, ax_aspect(ax))
        if mode == "aerial":
            gr, pr = scene(pkg, c, rad * 4)
            render(pkg, ax, a, gr, pr, title="%s · aerial · massing rendered from geometry by make_figures.py" % nid)
        else:
            gr, pr = scene(pkg, c, rad * 6)
            render(pkg, ax, e, gr, pr, title="%s · eye level 1.6 m · massing rendered from geometry by make_figures.py" % nid)
        paths[mode] = os.path.join(out, "node-%s-%s.png" % (nid, mode))
        f.savefig(paths[mode], dpi=dpi, facecolor=PAPER)
        plt.close(f)
    return paths


# ------------------------------------------------------------------------------- node depth: plan, section, a day
SEC_DEPTH = 45.0          # metres of elevation drawn beyond the cut
_SCENE = {}
# tree silhouettes as the 3D scene draws them (scripts/scene/scene.js): trunk height, crown centre, crown w / h
TREE_DIMS = {0: (3.4, 4.9, 5.0, 4.6), 1: (3.0, 7.2, 2.6, 10.0), 2: (1.3, 2.3, 2.8, 2.6)}


def scene_data(pkg):
    """The 3D scene's own entourage (trees, people, robots, vehicles), so plans and sections show what the
    renders show. Used only when visual/index.html is current with the geometry."""
    if pkg.dir in _SCENE:
        return _SCENE[pkg.dir]
    d = None
    p = os.path.join(pkg.dir, "visual", "index.html")
    if os.path.exists(p):
        t = open(p, encoding="utf-8").read()
        k = "window.XCITY_SCENE="
        if k in t:
            i = t.index(k) + len(k)
            try:
                d = json.loads(t[i:t.index(";</script>", i)])
            except ValueError:
                d = None
    if d and d.get("input_sha256") != xc.scene_input_hash(pkg.dir):
        d = None
    _SCENE[pkg.dir] = d
    return d


def entourage(pkg, key):
    """Scene items as an array whose first two columns are UTM x, y."""
    d = scene_data(pkg)
    if not d or not d.get(key):
        return np.zeros((0, 2))
    a = np.array([r[:6] + [0] * (6 - len(r[:6])) for r in d[key]], dtype=float)
    a[:, 0] += d["origin_utm"][0]
    a[:, 1] += d["origin_utm"][1]
    return a


def b_height(p):
    if p.get("height_m"):
        return float(p["height_m"])
    return max(1.0, float(p.get("floors", 1) or 1)) * FLOOR_H + 0.6


def node_section_lines(pkg, nid):
    """Section lines: nodes.geojson `section` (and `section_b`) as [[lon, lat], [lon, lat]], else one line
    east-west through the middle of the node, at most 260 m long."""
    p, g = pkg.nodes[nid]
    out = []
    for key in ("section", "section_b"):
        v = p.get(key)
        if isinstance(v, list) and len(v) == 2:
            out.append(xc.to_utm(LineString(v)))
    if not out:
        c = g.centroid
        x0, y0, x1, y1 = g.bounds
        hx, hy = min((x1 - x0) / 2 + 15, 90), min((y1 - y0) / 2 + 15, 90)
        out.append(LineString([(c.x - hx, c.y), (c.x + hx, c.y)]))
        out.append(LineString([(c.x, c.y + hy), (c.x, c.y - hy)]))
    return out


def node_numbers(pkg, nid):
    """Counts and areas inside the node, recomputed from the geometry (and the scene, for trees)."""
    p, g = pkg.nodes[nid]
    area = g.area
    foot = gfa = canopy = 0.0
    n = 0
    by_use, by_floors = {}, {}
    for q, b in pkg.geo["buildings"]:
        if not b.intersects(g):
            continue
        part = b.intersection(g)
        if q.get("form") == "canopy":
            canopy += part.area
            continue
        f = xc._floors(q) or 1
        n += 1
        foot += part.area
        gfa += part.area * f
        by_use[q.get("use", "-")] = by_use.get(q.get("use", "-"), 0) + part.area * f
        fk = int(round(f))
        by_floors[fk] = by_floors.get(fk, 0) + 1
    os_parts = [lu.intersection(g) for q, lu in pkg.geo["land_use"] if q.get("use") == "open_space" and lu.intersects(g)]
    opn = unary_union(os_parts).area if os_parts else 0.0
    nets, shaded, inter = {}, 0.0, 0
    for q, l in pkg.geo["movement"]:
        if q.get("kind") == "interface":
            if l.geom_type == "Point" and g.buffer(3).contains(l):
                inter += 1
            continue
        if not l.geom_type.endswith("LineString") or not l.intersects(g):
            continue
        ln = l.intersection(g).length
        nets[q.get("network", "-")] = nets.get(q.get("network", "-"), 0) + ln
        if q.get("network") == "people" and q.get("shaded"):
            shaded += ln
    trees = entourage(pkg, "trees")
    nt = int(sum(1 for x, y in trees[:, :2] if g.contains(Point(x, y)))) if len(trees) else None
    return dict(area=area, n=n, foot=foot, gfa=gfa, canopy=canopy, far=gfa / area if area else 0,
                cover=foot / area if area else 0, open=opn / area if area else 0, by_use=by_use,
                by_floors=by_floors, nets=nets, shaded=(shaded / nets["people"]) if nets.get("people") else None,
                inter=inter, trees=nt)


def numbers_text(pkg, nid):
    k = node_numbers(pkg, nid)
    fl = ", ".join("%d x %dF" % (v, f) for f, v in sorted(k["by_floors"].items()))
    use = ", ".join("%s %s m²" % (u.replace("_", " "), fmt(round(a / 100) * 100)) for u, a in
                    sorted(k["by_use"].items(), key=lambda t: -t[1]))
    nets = ", ".join("%s %s m" % (nm, fmt(round(v))) for nm, v in sorted(k["nets"].items()))
    lines = ["Node area %s m² (%s ha)" % (fmt(round(k["area"] / 10) * 10), fmt(round(k["area"] / 1e4, 1))),
             "Buildings %d  ·  footprint %s m²  ·  floor area %s m²" % (k["n"], fmt(round(k["foot"] / 10) * 10),
                                                                        fmt(round(k["gfa"] / 10) * 10)),
             "Coverage %s%%  ·  FAR %s  ·  open space %s%%" % (fmt(round(k["cover"] * 100, 1)), fmt(round(k["far"], 2)),
                                                            fmt(round(k["open"] * 100, 1))),
             "Floors: " + (fl or "-"),
             "Floor area by use: " + (use or "-")]
    if k["canopy"]:
        lines.append("Canopies (roof on posts, no floor area) %s m²" % fmt(round(k["canopy"] / 10) * 10))
    lines.append("Networks in the node: " + (nets or "-"))
    if k["shaded"] is not None:
        lines.append("Shaded share of the walking network %s%%" % fmt(round(k["shaded"] * 100)))
    lines.append("Human-machine interfaces %d" % k["inter"])
    if k["trees"] is not None:
        lines.append("Trees %s (as placed in the 3D scene)" % fmt(k["trees"]))
    return "\n".join(lines)


def dim_line(ax, a, b, text, off, fs=6.5, color=INK):
    """A dimension line from a to b, offset by off (metres, perpendicular), with the length written on it."""
    (x0, y0), (x1, y1) = a, b
    L = math.hypot(x1 - x0, y1 - y0) or 1.0
    nx, ny = -(y1 - y0) / L * off, (x1 - x0) / L * off
    ax.annotate("", xy=(x0 + nx, y0 + ny), xytext=(x1 + nx, y1 + ny),
                arrowprops=dict(arrowstyle="<->", color=color, lw=0.7, shrinkA=0, shrinkB=0), zorder=14)
    for (x, y) in ((x0, y0), (x1, y1)):
        ax.plot([x, x + nx * 1.15], [y, y + ny * 1.15], color=color, lw=0.4, zorder=14)
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
    if ang > 90 or ang < -90:
        ang += 180
    ax.text((x0 + x1) / 2 + nx * 1.35, (y0 + y1) / 2 + ny * 1.35, text, fontsize=fs, color=color, ha="center",
            va="center", rotation=ang, zorder=15, path_effects=[withStroke(linewidth=2, foreground=PAPER)])


def panel_node_detail_plan(pkg, ax, nid, lines):
    """The node plan with overall dimensions, street widths, numbered interfaces and the section lines."""
    panel_node_plan(pkg, ax, nid)
    p, g = pkg.nodes[nid]
    (wx0, wx1), (wy0, wy1) = ax.get_xlim(), ax.get_ylim()
    W = box(wx0, wy0, wx1, wy1)
    x0, y0, x1, y1 = g.bounds
    off = (wx1 - wx0) * 0.025
    dim_line(ax, (x0, y0), (x1, y0), "%s m" % fmt(round(x1 - x0)), -off)
    dim_line(ax, (x0, y0), (x0, y1), "%s m" % fmt(round(y1 - y0)), off)
    # street widths, once per named line, where it crosses the node
    seen = set()
    for q, l in pkg.geo["movement"]:
        if not l.geom_type.endswith("LineString") or not q.get("width_m") or not l.intersects(g):
            continue
        part = l.intersection(g)
        if part.is_empty or part.length < 30:
            continue
        key = (q.get("network"), q.get("width_m"))
        c = part.interpolate(0.5, normalized=True)
        if any(c.distance(s) < (wx1 - wx0) * 0.12 for s in seen):
            continue
        seen.add(c)
        ax.text(c.x, c.y, "%s %s m" % (q.get("network", ""), fmt(q["width_m"])), fontsize=5.6, color=INK,
                ha="center", va="center", zorder=16, path_effects=[withStroke(linewidth=2.2, foreground="white")])
    # interfaces, numbered
    k = 0
    for q, pt in pkg.geo["movement"]:
        if q.get("kind") == "interface" and pt.geom_type == "Point" and W.contains(pt):
            k += 1
            ax.plot(pt.x, pt.y, "o", ms=11, mfc="white", mec=RED, mew=1.3, zorder=16.5)
            ax.text(pt.x, pt.y, str(k), fontsize=6.5, color=RED, ha="center", va="center", zorder=17, fontweight="bold")
    # section lines
    for i, ln in enumerate(lines):
        lab = "AB"[i] if i < 2 else str(i + 1)
        xs, ys = ln.xy
        ax.plot(xs, ys, color=INK, lw=0.9, ls=(0, (8, 3, 1, 3)), zorder=16)
        for (x, y), t in (((xs[0], ys[0]), lab), ((xs[-1], ys[-1]), lab + "'")):
            ax.text(x, y, t, fontsize=8, fontweight="bold", color="white", ha="center", va="center", zorder=18,
                    bbox=dict(boxstyle="circle,pad=0.25", fc=INK, ec="none"))


def draw_section(pkg, ax, ln, label="A"):
    """A section along ln, drawn at true scale from the geometry: terrain from the DEM, buildings cut in black
    (floors x 3.5 m or height_m), buildings and trees beyond in grey up to SEC_DEPTH m, people for scale."""
    (xa, ya), (xb, yb) = ln.coords[0], ln.coords[-1]
    L = ln.length
    ux, uy = (xb - xa) / L, (yb - ya) / L
    nx, ny = -uy, ux                     # looking to the left of A -> A'
    S = lambda x, y: (np.asarray(x) - xa) * ux + (np.asarray(y) - ya) * uy
    D = lambda x, y: (np.asarray(x) - xa) * nx + (np.asarray(y) - ya) * ny
    ss = np.linspace(0, L, max(20, int(L / 2)))
    zz = pkg.dem_smooth(xa + ss * ux, ya + ss * uy).astype(float)
    # land-use polygons may carry level_m (a sunken court at -3, a raised terrace at +1.5)
    for q, lu in pkg.geo["land_use"]:
        lv = q.get("level_m")
        if lv in (None, "", 0) or not lu.intersects(ln):
            continue
        part = lu.intersection(ln)
        for seg in getattr(part, "geoms", [part]):
            if seg.length < 1:
                continue
            s0, s1 = sorted(float(v) for v in S(*seg.xy))
            zz = np.where((ss >= s0) & (ss <= s1), zz + float(lv), zz)
    zg = lambda s: float(np.interp(s, ss, zz))
    band = Polygon_from_band(xa, ya, ux, uy, nx, ny, L, SEC_DEPTH)
    items = []                           # (distance, kind, payload)
    zmax = float(zz.max())
    for q, b in pkg.geo["buildings"]:
        if not b.intersects(band) and not b.intersects(ln):
            continue
        h = b_height(q)
        cut = b.intersection(ln)
        if not cut.is_empty and cut.length > 0.2:
            for seg in getattr(cut, "geoms", [cut]):
                s0, s1 = sorted(float(v) for v in S(*seg.xy))
                items.append((-1.0, "cut", (q, s0, s1, h)))
                zmax = max(zmax, zg((s0 + s1) / 2) + h)
            continue
        xs, ys = b.exterior.xy
        dd = D(xs, ys)
        if dd.max() <= 0:
            continue
        s = S(xs, ys)
        s0, s1 = float(max(0, s.min())), float(min(L, s.max()))
        if s1 - s0 < 0.5:
            continue
        items.append((float(max(0.0, dd.min())), "far", (q, s0, s1, h)))
        zmax = max(zmax, zg((s0 + s1) / 2) + h)
    for r in entourage(pkg, "trees"):
        d, s = float(D(r[0], r[1])), float(S(r[0], r[1]))
        if -3 < d < SEC_DEPTH and 0 <= s <= L:
            items.append((max(d, -0.5), "tree", (s, r[2], int(r[4]))))
    for r in entourage(pkg, "people"):
        d, s = float(D(r[0], r[1])), float(S(r[0], r[1]))
        if -2 < d < 12 and 0 <= s <= L:
            items.append((max(d, -0.4), "person", (s, r[5] or 1.0)))
    items.sort(key=lambda t: -t[0])
    for d, kind, pl in items:
        fade = min(1.0, max(0.0, d / SEC_DEPTH))
        if kind == "far":
            q, s0, s1, h = pl
            z0 = zg((s0 + s1) / 2)
            col = soft("#B9B1A2", 0.25 + 0.6 * fade, base=PAPER)
            if q.get("form") == "canopy":
                ax.add_patch(Rectangle((s0, z0 + h - 0.6), s1 - s0, 0.6, fc=col, ec="#8C8576", lw=0.3, zorder=2))
            else:
                ax.add_patch(Rectangle((s0, z0), s1 - s0, h, fc=col, ec="#8C8576", lw=0.3, zorder=2))
        elif kind == "tree":
            s, size, typ = pl
            th, cz, cw, chh = TREE_DIMS.get(typ, TREE_DIMS[0])
            z0 = zg(s)
            col = "#5E7D4E" if d < 3 else soft("#7E9A6A", 0.2 + 0.6 * fade, base=PAPER)
            ax.plot([s, s], [z0, z0 + th * size], color=soft("#5B4B3A", 0.6 * fade, base=PAPER), lw=0.8, zorder=3)
            from matplotlib.patches import Ellipse
            ax.add_patch(Ellipse((s, z0 + cz * size), cw * size, chh * size, fc=col, ec="none", alpha=0.95, zorder=3))
        elif kind == "person":
            s, sc = pl
            z0 = zg(s)
            hh = 1.7 * (sc if 0.6 < sc < 1.4 else 1.0)
            ax.plot([s, s], [z0, z0 + hh * 0.82], color=INK, lw=0.9, zorder=6, solid_capstyle="round")
            ax.plot([s], [z0 + hh * 0.92], "o", ms=1.6, color=INK, zorder=6)
        elif kind == "cut":
            q, s0, s1, h = pl
            z0 = zg((s0 + s1) / 2)
            if q.get("form") == "canopy":
                ax.add_patch(Rectangle((s0, z0 + h - 0.7), s1 - s0, 0.7, fc=INK, ec="none", zorder=5))
                for sp in np.arange(s0 + 1, s1, 12.0):
                    ax.plot([sp, sp], [z0, z0 + h - 0.7], color=INK, lw=0.8, zorder=5)
                ax.text((s0 + s1) / 2, z0 + h + 1.0, "canopy %s m" % fmt(round(h, 1)), fontsize=5.6, color=INK,
                        ha="center", va="bottom", zorder=8)
            else:
                ax.add_patch(Rectangle((s0, z0), s1 - s0, h, fc=INK, ec="none", zorder=5))
                if s1 - s0 > 5:
                    ax.text((s0 + s1) / 2, z0 + h + 0.8, "%dF  %s m" % (int(round(xc._floors(q) or 1)), fmt(round(h, 1))),
                            fontsize=5.4, color=INK, ha="center", va="bottom", zorder=8)
    # ground
    zmin = float(zz.min())
    ax.fill_between(ss, zz, zmin - 6, color="#E3DBCB", zorder=4, lw=0)
    ax.plot(ss, zz, color=INK, lw=1.4, zorder=7)
    # land uses and networks along the cut
    taken = []
    for q, lu in sorted(pkg.geo["land_use"], key=lambda t: t[1].area):
        if not lu.intersects(ln):
            continue
        part = lu.intersection(ln)
        for seg in getattr(part, "geoms", [part]):
            if seg.length < 14:
                continue
            s0, s1 = sorted(float(v) for v in S(*seg.xy))
            name = str(q.get("name") or q.get("use") or "").split(" (")[0].split(":")[0].split(" - ")[0]
            lab = textwrap.shorten(T(name), max(8, int((s1 - s0) / 3.2)), placeholder="…")
            half = len(lab) * 1.55 / 2
            mid = (s0 + s1) / 2
            if any(not (mid + half < a or mid - half > b) for a, b in taken):
                continue
            taken.append((mid - half, mid + half))
            ax.text(mid, zg(mid) - 2.2, lab, fontsize=5.2, color=MUTED, ha="center", va="top", zorder=8)
            ax.plot([s0, s0], [zg(s0) - 0.8, zg(s0) - 1.6], color=MUTED, lw=0.4, zorder=8)
    for q, l in pkg.geo["movement"]:
        if q.get("kind") == "interface" or not l.geom_type.endswith("LineString") or not l.intersects(ln):
            continue
        x = l.intersection(ln)
        for pt in getattr(x, "geoms", [x]):
            if pt.geom_type != "Point":
                continue
            s = float(S(pt.x, pt.y))
            st = NET_STYLE.get(q.get("network"), NET_STYLE["people"])
            ax.plot([s], [zg(s)], marker="v", ms=4.5, color=st["color"], zorder=9)
            if q.get("width_m"):
                ax.text(s, zg(s) - 4.6, "%s %s m" % (q.get("network", ""), fmt(q["width_m"])), fontsize=5,
                        color=st["color"], ha="center", va="top", zorder=9)
    ax.set_xlim(-4, L + 4)
    ax.set_ylim(zmin - 8, zmax + 6)
    ax.set_aspect("equal")
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    for sp in ("left", "bottom"):
        ax.spines[sp].set_color("#CFCBC2")
    ax.tick_params(labelsize=5.5, colors=MUTED, length=2)
    ax.set_xticks(np.arange(0, L + 1, 20 if L < 300 else 50))
    ax.set_ylabel("m a.s.l.", fontsize=6, color=MUTED)
    ax.text(0, zmax + 5, "%s" % label, fontsize=9, fontweight="bold", color="white", ha="center", va="top",
            bbox=dict(boxstyle="circle,pad=0.25", fc=INK, ec="none"), zorder=10)
    ax.text(L, zmax + 5, "%s'" % label, fontsize=9, fontweight="bold", color="white", ha="center", va="top",
            bbox=dict(boxstyle="circle,pad=0.25", fc=INK, ec="none"), zorder=10)


def section_extent(pkg, ln):
    """(length, lowest ground, highest roof) of a section, so the sheet can give it the height it needs."""
    (xa, ya), (xb, yb) = ln.coords[0], ln.coords[-1]
    L = ln.length
    ux, uy = (xb - xa) / L, (yb - ya) / L
    ss = np.linspace(0, L, 40)
    zz = pkg.dem_smooth(xa + ss * ux, ya + ss * uy).astype(float)
    lv = [float(q.get("level_m")) for q, lu in pkg.geo["land_use"]
          if q.get("level_m") not in (None, "", 0) and lu.intersects(ln)]
    band = Polygon_from_band(xa, ya, ux, uy, -uy, ux, L, SEC_DEPTH)
    hmax = max([b_height(q) for q, b in pkg.geo["buildings"] if b.intersects(band)] + [12.0])
    return L, float(zz.min()) + min(lv + [0.0]), float(zz.max()) + max(lv + [0.0]) + hmax


def street_section_lines(pkg, nid, maxn=3):
    """Short cuts across the node's streets, one per kind of street (network and width), at the middle of its
    longest stretch inside the node: the street, the buildings either side, the trees and the people."""
    p, g = pkg.nodes[nid]
    best = {}
    for q, l in pkg.geo["movement"]:
        if not l.geom_type.endswith("LineString") or not q.get("width_m") or not l.intersects(g):
            continue
        part = l.intersection(g)
        for piece in getattr(part, "geoms", [part]):
            if piece.geom_type != "LineString" or piece.length < 20:
                continue
            key = (q.get("network"), float(q["width_m"]))
            if piece.length > best.get(key, (0,))[0]:
                best[key] = (piece.length, piece, q)
    out = []
    for key, (_, piece, q) in sorted(best.items(), key=lambda kv: (-kv[0][1], kv[0][0] or ""))[:maxn]:
        c = piece.interpolate(0.5, normalized=True)
        a = piece.interpolate(max(0, piece.length / 2 - 2))
        b = piece.interpolate(min(piece.length, piece.length / 2 + 2))
        dx, dy = b.x - a.x, b.y - a.y
        n = math.hypot(dx, dy) or 1
        half = key[1] / 2 + 16
        out.append((LineString([(c.x + dy / n * half, c.y - dx / n * half), (c.x - dy / n * half, c.y + dx / n * half)]), q))
    return out


def Polygon_from_band(xa, ya, ux, uy, nx, ny, L, depth):
    from shapely.geometry import Polygon
    return Polygon([(xa, ya), (xa + ux * L, ya + uy * L), (xa + ux * L + nx * depth, ya + uy * L + ny * depth),
                    (xa + nx * depth, ya + ny * depth)])


def draw_node_detail(pkg, nid, size=A3):
    """Second node sheet: the plan with dimensions and numbers, the sections cut through it, and a cut across each
    kind of street in it."""
    meta = pkg.node_meta.get(nid, {})
    p, g = pkg.nodes[nid]
    lines = node_section_lines(pkg, nid)
    streets = street_section_lines(pkg, nid)
    fig = new_page(pkg, size, "NODE " + nid, "%s · plan and section" % meta.get("en", nid),
                   "Scale 3 · dimensions and sections from the geometry")
    axp = fig.add_axes([0.03, 0.30, 0.40, 0.58])
    panel_node_detail_plan(pkg, axp, nid, lines)
    for ln, q in streets:
        xs, ys = ln.xy
        axp.plot(xs, ys, color=INK, lw=0.8, zorder=16)
    axp.set_title("Plan · overall dimensions, street widths, interfaces numbered, section lines",
                  fontsize=7.5, color=MUTED, loc="left")
    tx = fig.add_axes([0.03, 0.06, 0.40, 0.21])
    side_text(tx, [("Numbers in the node · recomputed from the geometry", numbers_text(pkg, nid))], fs=7.6, width=92)
    fw, fh = fig.get_size_inches()
    W = 0.50
    y = 0.885
    street_h = 0.20 if streets else 0.0
    avail = y - 0.08 - street_h
    exts = [section_extent(pkg, ln) for ln in lines]
    need = [W * fw * (z1 - z0 + 14) / (L + 8) / fh for L, z0, z1 in exts]
    scale = min(1.0, (avail - 0.045 * len(lines)) / max(sum(need), 1e-6))
    for i, (ln, h) in enumerate(zip(lines, need)):
        lab = "AB"[i] if i < 2 else str(i + 1)
        hh = h * scale
        y -= 0.03
        ax = fig.add_axes([0.47 + (W - W * scale) / 2, y - hh, W * scale, hh])
        draw_section(pkg, ax, ln, lab)
        ax.set_title("Section %s-%s' · %s m · true scale, looking left of the cut" % (lab, lab, fmt(round(ln.length))),
                     fontsize=7.5, color=MUTED, loc="left")
        y -= hh + 0.012
    if streets:
        n = len(streets)
        sw = (W - 0.02 * (n - 1)) / n
        for i, (ln, q) in enumerate(streets):
            ax = fig.add_axes([0.47 + i * (sw + 0.02), max(0.075, y - 0.035 - 0.16), sw, 0.16])
            draw_section(pkg, ax, ln, "S%d" % (i + 1))
            ax.set_title("%s street · %s m%s" % (str(q.get("network", "")).capitalize(), fmt(q.get("width_m")),
                         " · shaded" if q.get("shaded") else ""), fontsize=7, color=MUTED, loc="left")
    fig.text(0.47, 0.045, "Cut buildings in black (floors x %.1f m, or height_m); beyond the cut, buildings and trees "
             "within %d m in grey; trees and people as placed in the 3D scene; terrain from the DEM." % (FLOOR_H, SEC_DEPTH),
             fontsize=6.2, color=MUTED)
    return fig


def panel_human_machine(pkg, ax, nid):
    """Who and what moves through the node: the three networks, numbered interfaces, and the people, robots
    and vehicles the 3D scene places there."""
    p, g = pkg.nodes[nid]
    win = fit_aspect(g.buffer(max(40, math.sqrt(g.area) * 0.12)).bounds, ax_aspect(ax))
    W = box(*win)
    for q, lu in pkg.geo["land_use"]:
        if lu.intersects(W):
            fill(ax, lu, soft(USE_COLORS.get(q.get("use"), "#DDD"), 0.55, base=PAPER), ec="white", lw=.3, z=2)
    for q, b in pkg.geo["buildings"]:
        if b.intersects(W):
            fill(ax, b, "#D9D2C4" if q.get("form") != "canopy" else "#EFE6CF", z=3)
    for q, l in pkg.geo["movement"]:
        if l.geom_type.endswith("LineString") and l.intersects(W):
            st = NET_STYLE.get(q.get("network"), NET_STYLE["people"])
            outline(ax, l, color=st["color"], lw=st["lw"] * 1.7, ls=st["ls"], z=5)
    pe = entourage(pkg, "people")
    if len(pe):
        m = np.array([W.contains(Point(x, y)) for x, y in pe[:, :2]])
        if m.any():
            ax.plot(pe[m, 0], pe[m, 1], "o", ms=1.6, color="#C96B5C", alpha=0.8, zorder=6)
    ro = entourage(pkg, "robots")
    if len(ro):
        m = np.array([W.contains(Point(x, y)) for x, y in ro[:, :2]])
        if m.any():
            ax.plot(ro[m, 0], ro[m, 1], "s", ms=2.6, mfc="white", mec="#3F4650", mew=0.8, zorder=7)
    tr = entourage(pkg, "trucks")
    if len(tr):
        m = np.array([W.contains(Point(x, y)) for x, y in tr[:, :2]])
        for kind, mk, col in ((0, "D", "#3F4650"), (1, "s", "#8C9096")):
            mm = m & (tr[:, 3] == kind) if tr.shape[1] > 3 else m
            if mm.any():
                ax.plot(tr[mm, 0], tr[mm, 1], mk, ms=3.6, mfc=col, mec="white", mew=0.5, zorder=7)
    k = 0
    names = []
    for q, pt in pkg.geo["movement"]:
        if q.get("kind") == "interface" and pt.geom_type == "Point" and W.contains(pt):
            k += 1
            ax.plot(pt.x, pt.y, "o", ms=12, mfc="white", mec=RED, mew=1.3, zorder=8)
            ax.text(pt.x, pt.y, str(k), fontsize=7, color=RED, ha="center", va="center", zorder=9, fontweight="bold")
            names.append("%d  %s" % (k, q.get("name", "interface")))
    outline(ax, g, color=GOLD, lw=1.6, z=9)
    frame(ax, win, pad=0)
    scalebar_north(ax, 8)
    handles = [Line2D([], [], color=NET_STYLE[n]["color"], lw=2.2, ls=NET_STYLE[n]["ls"], label=lab) for n, lab in
               (("people", "People"), ("machine", "Machines + goods"), ("shared", "Shared at walking pace"))]
    handles += [Line2D([], [], marker="o", ls="", ms=4, color="#C96B5C", label="People (scene)"),
                Line2D([], [], marker="s", ls="", ms=4, mfc="white", mec="#3F4650", label="Delivery robots"),
                Line2D([], [], marker="D", ls="", ms=4, color="#3F4650", label="Driverless shuttles"),
                Line2D([], [], marker="o", ls="", ms=7, mfc="white", mec=RED, label="Human-machine interface")]
    return names, handles


def draw_node_day(pkg, nid, size=A3):
    """Third node sheet: a day in the node, hour by hour, people and machines side by side."""
    meta = pkg.node_meta.get(nid, {})
    p, g = pkg.nodes[nid]
    day = p.get("day") if isinstance(p.get("day"), list) else []
    fig = new_page(pkg, size, "NODE " + nid, "%s · a day of use" % meta.get("en", nid),
                   "People and machines through one day")
    axm = fig.add_axes([0.47, 0.36, 0.50, 0.52])
    names, handles = panel_human_machine(pkg, axm, nid)
    axl = fig.add_axes([0.47, 0.07, 0.17, 0.12])
    axl.set_axis_off()
    axl.legend(handles=handles, loc="upper left", fontsize=6.2, frameon=False, ncol=1)
    axm.set_title("Who and what moves here: networks, interfaces, and the people, robots and shuttles of the 3D scene",
                  fontsize=7.5, color=MUTED, loc="left")
    if day:
        ax = fig.add_axes([0.03, 0.07, 0.41, 0.81])
        ax.set_axis_off()
        ax.text(0, 1.0, "A day here", fontsize=10, fontweight="bold", color=INK, va="top", transform=ax.transAxes)
        ax.text(0.16, 0.965, "People", fontsize=7.5, fontweight="bold", color="#C96B5C", va="top", transform=ax.transAxes)
        ax.text(0.58, 0.965, "Machines", fontsize=7.5, fontweight="bold", color="#3F4650", va="top", transform=ax.transAxes)
        h_in = ax.get_position().height * fig.get_size_inches()[1]
        step = (7.2 * 1.38 / 72) / h_in
        y = 0.935
        for row in day[:9]:
            pl = textwrap.wrap(T(str(row.get("people", ""))), 46) or [""]
            ml = textwrap.wrap(T(str(row.get("machines", ""))), 42) or [""]
            ax.plot([0, 1], [y + step * 0.5, y + step * 0.5], color="#E2DCCF", lw=0.6, transform=ax.transAxes)
            ax.text(0, y, T(str(row.get("time", ""))), fontsize=8.5, fontweight="bold", color=GOLD, va="top",
                    transform=ax.transAxes)
            for i, t in enumerate(pl):
                ax.text(0.16, y - i * step, t, fontsize=7.2, color=INK, va="top", transform=ax.transAxes)
            for i, t in enumerate(ml):
                ax.text(0.58, y - i * step, t, fontsize=7.2, color=INK, va="top", transform=ax.transAxes)
            y -= step * (max(len(pl), len(ml)) + 0.9)
    else:
        tx = fig.add_axes([0.03, 0.07, 0.41, 0.81])
        side_text(tx, [(p.get("name", nid), p.get("why", "")), ("Numbers in the node", numbers_text(pkg, nid))],
                  fs=8, width=70)
    if names:
        tx = fig.add_axes([0.47, 0.20, 0.17, 0.12])
        side_text(tx, [("Interfaces in view", "\n".join(names[:8]))], fs=6.6, width=40)
    pe, ce = view_image(pkg, "%s-eye-day" % nid)
    others = [v for v in view_ids(pkg, "%s-eye-" % nid) if v != "%s-eye-day" % nid]
    pn, cn = view_image(pkg, others[0]) if others else (None, None)
    if pe:
        ax = fig.add_axes([0.655, 0.07, 0.155, 0.25] if pn else [0.655, 0.07, 0.315, 0.25])
        show_image(ax, pe, "day", fs=5.5)
    if pn:
        ax = fig.add_axes([0.815, 0.07, 0.155, 0.25])
        show_image(ax, pn, others[0].split("-")[-1], fs=5.5)
    return fig


def section_pages(pkg,section):
    """Optional authored page images replace a public section; checked figures remain separate."""
    configured=booklet_cfg(pkg).get('section_pages') or {}
    if section not in configured:return None
    pages=configured[section]
    if not isinstance(pages,list) or not pages:raise ValueError('booklet.section_pages.'+section+' must contain page images')
    figs=[]
    for page in pages:
        rel=page.get('path','') if isinstance(page,dict) else ''
        path=os.path.realpath(os.path.join(pkg.dir,rel))
        if os.path.commonpath([os.path.realpath(pkg.dir),path])!=os.path.realpath(pkg.dir) or not os.path.isfile(path):
            raise ValueError('Custom section page must be an existing image inside the package: '+rel)
        fig=new_page(pkg,A3,section,page.get('title') or section,page.get('subtitle',''))
        ax=fig.add_axes([.03,.07,.94,.81]);show_image(ax,path)
        figs.append(fig)
    return figs


def booklet_cfg(pkg):
    b = pkg.man.get("booklet") if isinstance(pkg.man.get("booklet"), dict) else {}
    return b


def cover_choice(pkg):
    """manifest.booklet.cover: any image in the package (media/, renders/, pages/); else the city aerial."""
    c = booklet_cfg(pkg).get("cover")
    if c:
        path = os.path.normpath(os.path.join(pkg.dir, c))
        if path.startswith(pkg.dir) and os.path.isfile(path):
            reg = {i.get("path"): i for i in pkg.prov}
            im = reg.get(c)
            credit = None
            if im:
                credit = "%s · %s from %s · illustrates the geometry, not evidence" % (
                    os.path.splitext(os.path.basename(c))[0], im.get("model", ""), im.get("control_image", ""))
            return path, credit
        print("warning: manifest.booklet.cover %s not found in the package - using the default cover" % c)
    hero = view_image(pkg, "city-aerial")
    return hero if hero[0] else view_image(pkg, "master-aerial")


def the_idea(pkg, size=A3):
    """The idea on one page: the thesis in large type, what the scheme gives up, and its three scales side by side."""
    m = pkg.man
    thesis = m.get("thesis") or m.get("summary", "")
    to = m.get("tradeoff", {})
    fig = new_page(pkg, size, "THE IDEA", "One sentence, three scales", "")
    ax = fig.add_axes([0.03, 0.07, 0.36, 0.81])
    ax.set_axis_off()
    y = 1.0
    big = len(thesis) < 160
    for ln in textwrap.wrap(T(thesis), 30 if big else 40)[:10]:
        ax.text(0, y, ln, fontsize=20 if big else 15, color=INK, va="top", transform=ax.transAxes, fontweight="bold")
        y -= 0.066 if big else 0.052
    y -= 0.03
    side = fig.add_axes([0.03, 0.07, 0.36, max(0.05, 0.81 * y - 0.02)])
    nodes = "\n".join("%s  %s - %s" % (n, pkg.node_meta.get(n, {}).get("en", ""), textwrap.shorten(
        T(pkg.nodes[n][0].get("name", "")) if n in pkg.nodes else "", 60)) for n in m.get("nodes", []))
    side_text(side, [("What it gives up", "%s. %s" % (to.get("objective", ""), to.get("why", ""))),
                     ("Who carries the cost", to.get("who_bears", "")),
                     ("Three key nodes", nodes)], fs=8.6, width=70)
    a1 = fig.add_axes([0.42, 0.50, 0.27, 0.38])
    panel_structure(pkg, a1, compact=False)
    a1.set_title("1  The whole site · structure", fontsize=8, color=INK, loc="left", fontweight="bold")
    a2 = fig.add_axes([0.71, 0.50, 0.26, 0.38])
    panel_master(pkg, a2, compact=False)
    a2.set_title("2  The master design · drawn by the entrant", fontsize=8, color=INK, loc="left", fontweight="bold")
    nn = [n for n in m.get("nodes", []) if n in pkg.nodes][:3]
    w = (0.55 - 0.01 * (len(nn) - 1)) / max(1, len(nn))
    for i, n in enumerate(nn):
        ax = fig.add_axes([0.42 + i * (w + 0.01), 0.09, w, 0.33])
        pa, ca = view_image(pkg, "%s-aerial" % n)
        if pa:
            show_image(ax, pa, None)
        else:
            panel_node_plan(pkg, ax, n, compact=True)
        ax.set_title(("3  " if i == 0 else "") + "%s %s" % (n, pkg.node_meta.get(n, {}).get("en", "")), fontsize=8,
                     color=INK, loc="left", fontweight="bold")
    return fig


def brief_alignment(pkg, size=A3):
    """Where the scheme answers each of the twelve mandatory requirements and the eight agent tasks."""
    req = xc.load_json(os.path.join(xc.ROOT, "brief", "requirements.json")).get("mandatory", [])
    tasks = xc.load_json(os.path.join(xc.ROOT, "brief", "agent_taskbook.json")).get("tasks", [])
    cm_p = os.path.join(pkg.dir, "compliance_matrix.json")
    cm = {i.get("id"): i for i in (xc.load_json(cm_p).get("items", []) if os.path.exists(cm_p) else [])}
    heads = {}
    pm = os.path.join(pkg.dir, "proposal.md")
    if os.path.exists(pm):
        for h in xc.proposal_headings(open(pm, encoding="utf-8").read()):
            mm = re.match(r"^(##\s+\d+\.)\s*(.*)$", h)
            if mm:
                heads[mm.group(1).replace("  ", " ")] = mm.group(2)
    fig = new_page(pkg, size, "BRIEF", "How the scheme answers the brief", "Every mandatory requirement and agent task")

    def table(ax, rows, cols, widths, title):
        ax.set_axis_off()
        ax.set_title(title, fontsize=9, color=INK, loc="left", fontweight="bold")
        tb = ax.table(cellText=rows, colLabels=cols, colWidths=widths, loc="upper left", cellLoc="left")
        tb.auto_set_font_size(False)
        tb.set_fontsize(7.2)
        tb.scale(1, 1.95)
        for (r, c), cell in tb.get_celld().items():
            cell.set_edgecolor("#E2DCCF")
            cell.set_linewidth(0.5)
            cell.set_facecolor("#ECE6D8" if r == 0 else PAPER)
            if r == 0:
                cell.set_text_props(fontweight="bold")
    rows = []
    for r in req:
        keys = r.get("metric") if isinstance(r.get("metric"), list) else ([r["metric"]] if r.get("metric") else [])
        vals = []
        for k in keys:
            v = metric_value(pkg, k)
            if v is not None:
                unit = (pkg.metrics.get(k) or {}).get("unit", "") if len(keys) > 1 else r.get("unit", "")
                vals.append(("%s %s" % (fmt(v), "" if unit in ("enum", "count") else unit or "")).strip())
        it = cm.get(r["id"], {})
        sec = it.get("section", "")
        tags = sorted({str((pkg.metrics.get(k) or {}).get("evidence", "")) for k in keys if pkg.metrics.get(k)} - {""})
        rows.append([r["id"], textwrap.shorten(T(r.get("title", "")), 40),
                     textwrap.shorten(" · ".join(vals), 34) if vals else "stated in the text",
                     ", ".join(tags) or "-",
                     textwrap.shorten(T("%s %s" % (sec.replace("## ", "§"), heads.get(sec, ""))), 36)])
    table(fig.add_axes([0.03, 0.33, 0.56, 0.53]), rows, ["", "Mandatory requirement", "This scheme", "Evidence", "Answered in"],
          [0.05, 0.34, 0.24, 0.11, 0.26], "Twelve mandatory requirements (M1-M12), phase one at full occupancy")
    must = [(r["id"], r.get("must_state", "")) for r in req if r.get("must_state")]
    if must:
        tx2 = fig.add_axes([0.03, 0.07, 0.90, 0.20])
        side_text(tx2, [("What each answer must state (brief/requirements.json)",
                         "\n".join("%s  %s" % (i, textwrap.shorten(s, 230)) for i, s in must[:12]))], fs=6.4, width=250)
    rows = []
    for tk in tasks:
        it = cm.get(tk["id"], {})
        sec = it.get("section", tk.get("answers_in", ""))
        rows.append([tk["id"].replace("agent.", "A"), textwrap.shorten(T(tk.get("title", "")), 36),
                     textwrap.shorten(T("%s %s" % (sec.replace("## ", "§"), heads.get(sec, ""))), 38)])
    table(fig.add_axes([0.62, 0.48, 0.35, 0.38]), rows, ["", "Agent task", "Answered in"], [0.09, 0.45, 0.46],
          "Eight agent tasks")
    tx = fig.add_axes([0.62, 0.33, 0.35, 0.12])
    side_text(tx, [("How to read this page", "Values come from metrics.json with their evidence tags (figure 07); "
                    "sections are the headings of proposal.md. The self-check (gate G6) confirms each answer points at a "
                    "real heading; it does not judge the answer.")], fs=7.8, width=70)
    return fig


def extra_pages(pkg, after):
    """Pages the entrant made, placed where manifest.booklet.pages says (after: cover, idea, views, brief, figures,
    a node id, nodes, day, end). Each is an image inside the package, drawn full width under its own title."""
    out = []
    for i, pg in enumerate(booklet_cfg(pkg).get("pages") or []):
        if str(pg.get("after", "end")) != after:
            continue
        rel = str(pg.get("path", ""))
        path = os.path.normpath(os.path.join(pkg.dir, rel))
        if not (path.startswith(pkg.dir) and os.path.isfile(path)):
            print("warning: booklet page %s not found in the package - skipped" % rel)
            continue
        fig = new_page(pkg, A3, "PAGE", pg.get("title", ""), pg.get("subtitle", "Drawn by the entrant"))
        show_fit(fig.add_axes([0.03, 0.07, 0.94, 0.81]), path)
        out.append(fig)
    return out


def show_fit(ax, path):
    """The whole image, letterboxed rather than cropped: an entrant's page must not lose its edges."""
    im = Image.open(path).convert("RGB")
    ax.imshow(np.asarray(im), interpolation="antialiased")
    ax.set_axis_off()
    ax.set_aspect("equal")


def cover(pkg, size=A3):
    hero = cover_choice(pkg)
    if hero[0]:
        return cover_image(pkg, hero, size)
    fig = new_page(pkg, size, "", "")
    m = pkg.man
    ax = fig.add_axes([0.52, 0.08, 0.45, 0.80])
    panel_structure(pkg, ax)
    tx = fig.add_axes([0.03, 0.08, 0.46, 0.80])
    a = m.get("author", {})
    ag = m.get("agent", {})
    au = m.get("autonomy", {})
    to = m.get("tradeoff", {})
    keys = [("hourly_cfe_match_pct", "%"), ("peak_it_load_mw", "MW"), ("annual_water_demand_m3", "m³/yr"),
            ("wue_l_per_kwh", "L/kWh"), ("jobs_phase1", "jobs"), ("residents_phase1", "residents")]
    km = " · ".join("%s %s" % (fmt(metric_value(pkg, k)), u) for k, u in keys if metric_value(pkg, k) is not None)
    nodes = ", ".join("%s %s" % (n, pkg.node_meta.get(n, {}).get("en", "")) for n in m.get("nodes", []))
    side_text(tx, [
        ("Summary", m.get("summary", "")),
        ("Key nodes", nodes),
        ("Declared trade-off", "%s - %s" % (to.get("objective", ""), to.get("who_bears", ""))),
        ("Key figures", km),
        ("Recomputed from geometry", "Master area %s km² · coverage %s%% · FAR %s · open space %s%% · %d interfaces" % (
            fmt(round(pkg.computed["master_area_km2"], 2)), fmt(round(pkg.computed["site_coverage_pct"], 1)),
            fmt(round(pkg.computed["far"], 2)), fmt(round(pkg.computed["open_space_pct"], 1)),
            pkg.computed["human_machine_interfaces"])),
        ("Responsible party", "%s  (GitHub: %s)" % (a.get("responsible_party", ""), a.get("github", ""))),
        ("Agent", "%s · %s · %s" % (ag.get("name", ""), ag.get("model", ""), ag.get("runtime", ""))),
        ("Autonomy", "%s - %s" % (au.get("class", ""), au.get("human_role", ""))),
        ("Drawn", "%s · scripts/make_figures.py v%s · input %s" % (datetime.date.today().isoformat(),
                                                                   xc.SCRIPT_VERSION, pkg.input_hash[:16])),
    ], fs=9.5, width=70)
    return fig


def cover_image(pkg, hero, size=A3):
    fig = new_page(pkg, size, "", "")
    m = pkg.man
    ax = fig.add_axes([0.03, 0.31, 0.94, 0.585])
    show_image(ax, hero[0], hero[1], fs=7)
    s1 = fig.add_axes([0.03, 0.07, 0.40, 0.215])
    side_text(s1, [("The scheme", m.get("summary", ""))], fs=9, width=88)
    keys = [("residents_phase1", "residents, phase one"), ("jobs_phase1", "jobs in the city"),
            ("peak_it_load_mw", "MW of compute"), ("pv_capacity_mwp", "MWp of PV"),
            ("annual_water_demand_m3", "m³ of water a year"), ("hourly_cfe_match_pct", "% hourly carbon-free")]
    vals = [(fmt(metric_value(pkg, k)), lab) for k, lab in keys if metric_value(pkg, k) is not None]
    c = pkg.computed
    vals += [(fmt(round(c["master_area_km2"], 1)), "km² master design"), ("%d" % c["human_machine_interfaces"], "human-machine interfaces")]
    for i, (v, lab) in enumerate(vals[:8]):
        x = 0.46 + (i % 4) * 0.105
        y = 0.255 - (i // 4) * 0.095
        fig.text(x, y, v, fontsize=17, fontweight="bold", color=INK, va="top")
        fig.text(x, y - 0.045, T(lab), fontsize=7.5, color=MUTED, va="top")
    to = m.get("tradeoff", {})
    nodes = "  ·  ".join("%s %s" % (n, pkg.node_meta.get(n, {}).get("en", "")) for n in m.get("nodes", []))
    fig.text(0.46, 0.075, T("Key nodes: " + nodes), fontsize=8, color=INK)
    fig.text(0.46, 0.058, textwrap.shorten(T("Declared trade-off: " + to.get("objective", "")), 120), fontsize=8, color=INK)
    return fig


def city_spread(pkg, size=A3):
    """The city seen whole: the master design aerial and the city at evening, if rendered."""
    views = [v for v in ("master-aerial", "city-evening") if view_image(pkg, v)[0]]
    if not views:
        return None
    fig = new_page(pkg, size, "VIEWS", "The city as built in phase one", "Scale 2 · rendered from the geometry")
    if len(views) == 1:
        show_image(fig.add_axes([0.03, 0.07, 0.94, 0.81]), *view_image(pkg, views[0]))
        return fig
    show_image(fig.add_axes([0.03, 0.07, 0.465, 0.81]), *view_image(pkg, views[0]))
    show_image(fig.add_axes([0.505, 0.07, 0.465, 0.81]), *view_image(pkg, views[1]))
    return fig


def day_to_night(pkg, size=A3):
    """Eye-level views ordered from day to evening to night: how the places are used over a day."""
    order = {"day": 0, "evening": 1, "night": 2}
    eyes = [v for v in [v for v in view_ids(pkg, "") if v[:1] in "ABC"] if "-eye-" in v]
    eyes.sort(key=lambda v: (order.get(v.rsplit("-", 1)[1], 9), v))
    eyes = [v for v in eyes if view_image(pkg, v)[0]][:6]
    if len(eyes) < 2:
        return None
    fig = new_page(pkg, size, "A DAY", "From day to night at eye level", "The same places, used through a day")
    n = len(eyes)
    cols = 3 if n > 4 else 2
    rows = int(math.ceil(n / cols))
    W, H = 0.94, 0.80
    gw, gh = W / cols, H / rows
    for k, v in enumerate(eyes):
        r, cidx = divmod(k, cols)
        ax = fig.add_axes([0.03 + cidx * gw + 0.004, 0.07 + (rows - 1 - r) * gh + 0.03, gw - 0.008, gh - 0.035])
        show_image(ax, view_image(pkg, v)[0], None)
        nid, _, time = v.partition("-eye-")
        lab = "%s  %s · %s" % (nid, pkg.node_meta.get(nid, {}).get("en", ""), time)
        fig.text(0.03 + cidx * gw + 0.004, 0.07 + (rows - 1 - r) * gh + 0.012, T(lab), fontsize=8, color=INK, fontweight="bold")
    return fig


def image_groups(prov):
    """One paragraph per model and process, listing its images, instead of repeating the same note for each."""
    groups = {}
    for i in prov:
        k = (i.get("model", ""), i.get("post_processing", ""), i.get("post_processing_note", ""))
        groups.setdefault(k, []).append(i)
    out = []
    for (model, post, note), items in groups.items():
        files = ", ".join("%s (control %s)" % (os.path.basename(i.get("path", "")),
                                                os.path.basename(i.get("control_image") or "-")) for i in items)
        out.append("%s - %d image%s, post-processing %s. %s Files in media/: %s. Full prompts in image_provenance.json."
                   % (model, len(items), "" if len(items) == 1 else "s", post or "-", note, files))
    return out


def disclosure(pkg, size=A3):
    """Assumptions, sources and AI disclosure, flowed over two columns and as many pages as needed."""
    d = pkg.dir
    rd = lambda rel, key: (xc.load_json(os.path.join(d, rel)).get(key, []) if os.path.exists(os.path.join(d, rel)) else [])
    asm, src, prov = rd("assumptions.json", "assumptions"), rd("sources.json", "sources"), rd("image_provenance.json", "images")
    au, ag = pkg.man.get("autonomy", {}), pkg.man.get("agent", {})
    blocks = [("Assumptions", ["%s  %s: %s - %s" % (a.get("id"), a.get("topic", ""), a.get("value", ""), a.get("basis", ""))
                               for a in asm] or ["-"]),
              ("Sources", ["%s  %s - %s %s" % (x.get("id"), x.get("title", ""), x.get("publisher", ""), x.get("url", ""))
                           for x in src] or ["-"]),
              ("AI disclosure", ["Agent %s, model %s, runtime %s. Autonomy: %s. %s" % (
                  ag.get("name", ""), ag.get("model", ""), ag.get("runtime", ""), au.get("class", ""),
                  au.get("human_role", ""))]),
              ("Images", ["%d images registered in image_provenance.json. Views in this booklet are, in order of "
                          "preference: an image made with an image model from a massing view of the geometry (model, prompt "
                          "and control image registered), the massing view itself (scripts/render_views.py), or a massing "
                          "drawing by scripts/make_figures.py. All of them explain the geometry; none is evidence." % len(prov)]
                          + image_groups(prov))]
    fs, width = 7.5, 92
    lines = []
    for head, paras in blocks:
        lines.append(("h", T(head)))
        for para in paras:
            for ln in textwrap.wrap(T(para), width=width) or [""]:
                lines.append(("p", ln))
            lines.append(("g", ""))
        lines.append(("g", ""))
    cols = [[0.03, 0.07, 0.45, 0.81], [0.52, 0.07, 0.45, 0.81]]
    figs, fig, col, y, step = [], None, 2, 0, 0
    for kind, text in lines:
        if fig is None or y < step:
            col += 1
            if fig is None or col > 1:
                fig = new_page(pkg, size, "SOURCES", "Assumptions, sources and AI disclosure"
                               + ("" if not figs else " (continued)"))
                figs.append(fig)
                col = 0
            ax = fig.add_axes(cols[col])
            ax.set_axis_off()
            h_in = ax.get_position().height * fig.get_size_inches()[1]
            step = (fs * 1.42 / 72) / h_in
            y = 1.0
            if kind == "g":
                continue
        if kind == "h":
            ax.text(0, y, text, fontsize=fs + 1, fontweight="bold", color=INK, va="top", transform=ax.transAxes)
            y -= step * 1.25
        elif kind == "p":
            ax.text(0, y, text, fontsize=fs, color=INK, va="top", transform=ax.transAxes)
            y -= step
        else:
            y -= step * 0.45
    return figs


def panel_a0_phase_story(ax, programme):
    """A board explains sequence; full per-zone accounts stay in the appendix/JSON."""
    ax.clear(); ax.set_axis_off()
    phases = sorted(programme.get('phases', []), key=lambda p: p.get('phase', 0))
    phases = [p for p in phases if p.get('phase') in (1, 2, 3)]
    if not phases:
        ax.text(0, .9, 'Construction sequence: define the stages and their operating conditions.',
                transform=ax.transAxes, fontsize=16, color=INK, va='top')
        return
    width = .30
    for i, phase in enumerate(phases):
        x = i * .34
        values = [z.get('new_residents') for z in phase.get('zones', [])]
        if values and all(isinstance(v, (int, float, dict)) and not isinstance(v, bool) for v in values):
            low = sum(v.get('min', 0) if isinstance(v, dict) else v for v in values)
            high = sum(v.get('max', 0) if isinstance(v, dict) else v for v in values)
            count = ('%s - %s' % (fmt(low), fmt(high))) if low != high else fmt(low)
            label = count + ' additional residents (scenario)'
        else:
            label = 'Capacity: see scoped programme'
        ax.text(x, .98, 'STAGE ' + str(phase['phase']), transform=ax.transAxes,
                fontsize=18, fontweight='bold', color=INK, va='top')
        ax.text(x, .75, textwrap.fill(T(phase.get('objective', '')), 46),
                transform=ax.transAxes, fontsize=13, color=INK, va='top', linespacing=1.2)
        ax.text(x, .33, label, transform=ax.transAxes, fontsize=12, color=MUTED, va='top')
        if i < len(phases) - 1:
            ax.annotate('', xy=(x + .33, .91), xytext=(x + width, .91), xycoords='axes fraction',
                        arrowprops=dict(arrowstyle='->', color=MUTED, lw=1.3))
    ax.text(0, .02, 'Conditional sequence; full district capacities, periods, works and triggers: technical appendix / phasing_programme.json.',
            transform=ax.transAxes, fontsize=11, color=MUTED, va='bottom')


def a0_board(pkg):
    # Entrant-authored presentation board; checked geometry/figures are still generated.
    authored = booklet_cfg(pkg).get("a0_page")
    if authored:
        path = os.path.realpath(os.path.join(pkg.dir, str(authored)))
        if os.path.commonpath([os.path.realpath(pkg.dir), path]) != os.path.realpath(pkg.dir) or not os.path.isfile(path):
            raise ValueError("booklet.a0_page must be an existing image inside the package")
        fig = plt.figure(figsize=A0, facecolor=PAPER)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.imshow(Image.open(path).convert("RGB"))
        ax.set_axis_off()
        return fig
    fig = new_page(pkg, A0, "A0 BOARD", "Overall study · master design · key nodes")
    ax1 = fig.add_axes([0.03, 0.40, 0.30, 0.49])
    it1 = panel_structure(pkg, ax1, compact=True)
    lg = fig.add_axes([0.335, 0.40, 0.105, 0.49])
    lg.set_axis_off()
    legend(lg, it1, "Overall study", fs=13, ncol=1)
    ax2 = fig.add_axes([0.45, 0.55, 0.30, 0.34])
    panel_master(pkg, ax2, compact=True)
    ax3 = fig.add_axes([0.77, 0.72, 0.20, 0.17])
    panel_movement(pkg, ax3, compact=True)
    ax4 = fig.add_axes([0.77, 0.53, 0.20, 0.17])
    panel_phasing(pkg, ax4, compact=True)
    ax4.set_title("PHASE 1 / 2 / 3 · construction zones and sequence", fontsize=13, loc="left")
    ax5 = fig.add_axes([0.45, 0.39, 0.52, 0.14])
    ax5.set_axis_off()
    m = pkg.man
    side_text(ax5, [("Summary", m.get("summary", "")),
                    ("Declared trade-off", "%s. Why: %s. Who bears it: %s" % (
                        m.get("tradeoff", {}).get("objective", ""), m.get("tradeoff", {}).get("why", ""),
                        m.get("tradeoff", {}).get("who_bears", "")))], fs=17, width=150)
    programme_path = os.path.join(pkg.dir, 'phasing_programme.json')
    if os.path.isfile(programme_path):
        panel_a0_phase_story(ax5, xc.load_json(programme_path))
    nodes = list(pkg.nodes)[:3]
    for i, nid in enumerate(nodes):
        x = 0.03 + i * 0.32
        axa = fig.add_axes([x, 0.20, 0.30, 0.17])
        axe = fig.add_axes([x, 0.055, 0.30, 0.135])
        draw_node_views(pkg, nid, axa, axe)
        fig.text(x, 0.375, "%s  %s" % (nid, T(pkg.node_meta.get(nid, {}).get("en", ""))), fontsize=20,
                 fontweight="bold", color=INK)
    return fig


def compress_pdf_images_pypdf(path, quality=80, min_side=400):
    """Default pure-Python compression; leave original control files untouched."""
    from pypdf import PdfWriter
    writer=PdfWriter(clone_from=path)
    seen=set()
    for page in writer.pages:
        # Inspect object references before decoding: Matplotlib may share one image dictionary
        # across every page. Repeatedly decoding/replacing it is slow and degrades the image.
        for name in page.images.keys():
            try:
                parts=[name] if isinstance(name,str) else name
                objects=page['/Resources']['/XObject']
                for i,part in enumerate(parts):
                    raw=objects[part].get_object()
                    if i<len(parts)-1:objects=raw['/Resources']['/XObject']
                ref=raw.indirect_reference
                identity=(ref.idnum,ref.generation) if ref is not None else id(raw)
                if identity in seen:continue
                seen.add(identity)
                if '/SMask' in raw or any(f in str(raw.get('/Filter','')) for f in ('DCTDecode','JPXDecode')):continue
                image=page.images[name]
                if image.image.mode in ('RGB','L') and min(image.image.size)>=min_side:
                    image.replace(image.image,quality=quality)
            except (KeyError,ValueError,NotImplementedError):
                continue
    writer.compress_identical_objects(remove_duplicates=True,remove_unreferenced=True)
    tmp=path+'.compressed'
    writer.write(tmp)
    os.replace(tmp,path)
    return True


def compress_pdf_images(path, quality=80, min_side=400):
    """Re-encode embedded raster images so both PDFs stay within the package size limit (pikepdf, or pypdf;
    without it the PDF is left as matplotlib wrote it)."""
    try:
        import io
        import pikepdf
        from pikepdf import PdfImage, Name
    except ImportError:
        return compress_pdf_images_pypdf(path,quality,min_side)
    pdf = pikepdf.open(path, allow_overwriting_input=True)
    seen = set()
    for page in pdf.pages:
        for name, raw in page.images.items():
            if raw.objgen in seen:
                continue
            seen.add(raw.objgen)
            try:
                if raw.get("/Filter") == Name.DCTDecode or min(int(raw.Width), int(raw.Height)) < min_side:
                    continue
                if "/SMask" in raw:
                    continue
                pil = PdfImage(raw).as_pil_image().convert("RGB")
                buf = io.BytesIO()
                pil.save(buf, "JPEG", quality=quality, optimize=True)
                raw.write(buf.getvalue(), filter=Name.DCTDecode)
                raw.ColorSpace = Name.DeviceRGB
                raw.BitsPerComponent = 8
                for k in ("/DecodeParms", "/Decode"):
                    if k in raw:
                        del raw[k]
            except Exception:
                continue
    pdf.save(path, deterministic_id=True)
    return True


# ------------------------------------------------------------------------------- public presentation structure
def node_location_text(pkg, nid):
    p, g = pkg.nodes[nid]
    c, m = g.centroid, pkg.master.centroid
    dx, dy = c.x-m.x, c.y-m.y
    direction = ('north' if dy >= 0 else 'south') + ('-east' if dx >= 0 else '-west')
    return '%s of the master-area centre, %.2f km; node area %.2f ha. See the shared locator for access and connections.' % (direction, c.distance(m)/1000, g.area/10000)


def node_locator(pkg, size=A3):
    fig = new_page(pkg, size, 'LOCATOR', 'Whole-site locator and independent node locations',
                   'The same node IDs are used on the plans, images and technical evidence')
    a=fig.add_axes([.03,.31,.32,.55]);panel_structure(pkg,a)
    a.set_title('Whole-site location of the master design area',fontsize=8,loc='left')
    b=fig.add_axes([.38,.31,.59,.55])
    extent=unary_union([pkg.master]+[g for _,g in pkg.nodes.values()]).buffer(600)
    panel_master(pkg,b,window=fit_aspect(extent.bounds,ax_aspect(b)))
    b.set_title('Combined locator extent; not a single district or construction boundary',fontsize=8,loc='left')
    for i,nid in enumerate(pkg.man.get('nodes',[])):
        p,g=pkg.nodes[nid];c=g.representative_point()
        ax=fig.add_axes([.03+i*.32,.07,.30,.19])
        side_text(ax,[(nid+' | '+pkg.node_meta.get(nid,{}).get('en',nid),node_location_text(pkg,nid)),
                      ('Role and connections',p.get('why') or pkg.man.get('nodes_reason',''))],fs=7.5,width=65)
    fig.text(.38,.285,'Network colours: people / salmon; machines / charcoal; shared / purple. Follow the submitted networks; no extra direct links are invented.',fontsize=6.5,color=MUTED)
    return fig


def public_node_sheet(pkg,nid):
    fig=draw_node_sheet(pkg,nid)
    fig.text(.03,.91,T('Location: '+node_location_text(pkg,nid)),fontsize=7,color=MUTED,va='top')
    finished=all(any(im.get('control_image')=='renders/%s-%s.png'%(nid,v) and os.path.isfile(os.path.join(pkg.dir,str(im.get('path','')))) for im in pkg.prov) for v in ['aerial','eye-day'])
    if not finished:
        fig.text(.03,.047,'MASSING-ONLY FALLBACK: one or more finished concept views are unavailable. Controls are not finished images; see technical appendix and tool disclosure.',fontsize=7,color=RED)
    return fig


def key_indicators(pkg,size=A3):
    fig=new_page(pkg,size,'INDICATORS','Key indicators: scope, phase and evidence','Full accounts and checks are in the separate technical appendix')
    keys=[('master_area_km2','Master design area','Master area'),('residents_phase1','Residents','Phase 1'),('jobs_phase1','Jobs','Phase 1'),('dwellings_phase1','Homes','Phase 1'),('far','Floor area ratio','Master area'),('open_space_pct','Open space','Master area'),('annual_water_demand_m3','Annual water demand','Phase 1'),('peak_it_load_mw','Compute load','Phase 1'),('hourly_cfe_match_pct','Hourly clean energy match','Phase 1'),('water_reuse_pct','Water reuse','Phase 1'),('waste_heat_reuse_pct','Waste heat reuse','Phase 1')]
    rows=[]
    for key,title,scope in keys:
        metric=pkg.metrics.get(key,{})
        value=metric.get('value')
        if value is None and key in pkg.computed:value=pkg.computed[key]
        rows.append([title,fmt(value) if value is not None else 'Not declared',metric.get('unit',''),scope,metric.get('evidence','computed' if key in pkg.computed else '-')])
    ax=fig.add_axes([.03,.21,.94,.65]);ax.set_axis_off()
    tb=ax.table(cellText=rows,colLabels=['Indicator','Value','Unit','Scope / phase','Evidence'],colWidths=[.30,.18,.16,.18,.18],loc='upper left',cellLoc='left');tb.auto_set_font_size(False);tb.set_fontsize(9);tb.scale(1,2.3)
    for (row,col),cell in tb.get_celld().items():cell.set_edgecolor('#E2DCCF');cell.set_facecolor('#ECE6D8' if row==0 else PAPER)
    ax=fig.add_axes([.03,.07,.94,.12]);side_text(ax,[('Reading these figures','The whole site is 1,656 km²; master-area figures are not whole-site totals. Phase 1 means full build-out and occupancy unless stated otherwise. Evidence tags describe the basis, not approval. Full system land accounts, assumptions and calculations remain in the appendix and metrics.json.')],fs=8,width=210)
    return fig


def control_comparison(pkg,nid,size=A3):
    fig=new_page(pkg,size,'TECHNICAL / '+nid,'Geometry controls and presentation comparison','Control images remain evidence; concept images illustrate the submitted geometry')
    for i,(view,label) in enumerate([('aerial','Aerial'),('eye-day','Eye level')]):
        ax=fig.add_axes([.03+i*.48,.49,.45,.37]);path=os.path.join(pkg.dir,'renders',nid+'-'+view+'.png')
        if pkg.renders_ok and os.path.isfile(path):show_image(ax,path,'GEOMETRY CONTROL / '+label)
        else:
            a,e,c,rad=node_cameras(pkg,nid,ax_aspect(ax));ground,prisms=scene(pkg,c,rad*(4 if i==0 else 6));render(pkg,ax,a if i==0 else e,ground,prisms,title='GEOMETRY CONTROL / '+label)
        path,credit=view_image(pkg,nid+'-'+view)
        ax=fig.add_axes([.03+i*.48,.07,.45,.37])
        if path:show_image(ax,path,credit)
        else:ax.set_axis_off();ax.text(.03,.8,'No separate finished image supplied.\nMassing-only fallback is disclosed in the main booklet.',fontsize=10,transform=ax.transAxes)
    return fig


# ------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("package", help="submissions/<github-login>/<proposal-slug>")
    ap.add_argument("--dpi", type=int, default=110, help="PNG resolution (default 110; the PDFs are vector)")
    ap.add_argument("--skip-a0", action="store_true",
                    help="drafts only: skip the A0 board. Gate G10 needs both PDFs from the same run - "
                         "run without this flag (or finalize_submission.py --redraw) before submitting")
    args = ap.parse_args()
    setup_fonts()
    pkg = Pkg(args.package)
    probs = xc.geometry_problems(pkg.geo_ll)
    if probs:
        raise SystemExit("fix the geometry first (gate G1 would fail):\n  " + "\n  ".join(probs))
    missing = [k for k in ("structure", "master_area", "land_use", "buildings", "movement", "phasing", "nodes")
               if not pkg.geo[k]]
    if missing:
        raise SystemExit("geometry is empty: %s - nothing to draw. See docs/submission-guide.md section 4."
                         % ", ".join("geometry/%s.geojson" % m for m in missing))
    if len(pkg.nodes) != 3:
        print("warning: geometry/nodes.geojson has %d nodes; the brief asks for exactly three" % len(pkg.nodes))
    fdir = os.path.join(pkg.dir, "figures")
    ddir = os.path.join(pkg.dir, "drawings")
    os.makedirs(fdir, exist_ok=True)
    os.makedirs(ddir, exist_ok=True)
    written = []
    # Preserve all standalone checked drawings, independently of the public reading order.
    for key,num,title,sub,panel in FIGS:
        f=draw_fig(pkg,key,num,title,sub,panel);path=os.path.join(fdir,key+'.png')
        f.savefig(path,dpi=args.dpi,facecolor=PAPER);plt.close(f);written.append(path)
    f=node_locator(pkg);path=os.path.join(fdir,'fig-08-node-location.png')
    f.savefig(path,dpi=args.dpi,facecolor=PAPER);plt.close(f);written.append(path)
    for nid in pkg.nodes:
        written.extend(save_node_images(pkg,nid,fdir,args.dpi).values())
    counters={'main':0,'technical':0};sections=[]
    paths={'main':'drawings/a3-booklet.pdf','technical':'drawings/a3-technical-appendix.pdf'}
    def figure(key):
        args=next(row for row in FIGS if row[0]==key)
        return draw_fig(pkg,*args)
    for document in ('main','technical'):
        with PdfPages(os.path.join(pkg.dir,paths[document])) as pdf:
            def put(f,section=None):
                if f is None:return
                custom=section_pages(pkg,section) if section and document=='main' else None
                if custom is not None:
                    plt.close(f);start=counters[document]+1
                    for own_page in custom:put(own_page)
                    sections.append({'id':section,'document':document,'pages':list(range(start,counters[document]+1))})
                    return
                pdf.savefig(f,facecolor=PAPER);plt.close(f);counters[document]+=1
                if section:sections.append({'id':section,'document':document,'pages':[counters[document]]})
            def extras(after):
                for f in extra_pages(pkg,after):put(f)
            if document=='main':
                put(cover(pkg));extras('cover');extras('idea')
                put(figure('fig-01-structure'),'whole_site');extras('whole_site')
                put(node_locator(pkg),'node_locator');extras('node_locator')
                put(figure('fig-02-master-plan'));extras('views')
                for key in ['fig-03-land-use-density','fig-04-movement','fig-05-open-space-water']:put(figure(key))
                for nid in pkg.man.get('nodes',[]):
                    put(public_node_sheet(pkg,nid),'node:'+nid);put(draw_node_detail(pkg,nid));extras(nid)
                extras('nodes')
                put(figure('fig-06-phasing'),'phasing');extras('phasing')
                put(key_indicators(pkg),'key_metrics');extras('key_metrics');extras('end')
            else:
                put(brief_alignment(pkg));extras('brief')
                for key in ['fig-07-metrics']:put(figure(key))
                extras('figures')
                for nid in pkg.man.get('nodes',[]):
                    put(control_comparison(pkg,nid));put(draw_node_day(pkg,nid))
                put(day_to_night(pkg));extras('day')
                for f in disclosure(pkg):put(f)
            info=pdf.infodict();info['Title']=pkg.title+(' - Public presentation' if document=='main' else ' - Technical appendix')
            info['Keywords']='input-sha256:%s make_figures:%s presentation:1'%(pkg.input_hash,xc.SCRIPT_VERSION)
            info['CreationDate']=None;info['ModDate']=None
        path=os.path.join(pkg.dir,paths[document]);compress_pdf_images(path);written.append(path)
        print('  '+paths[document])
    index={'schema_version':1,'layout_version':1,'documents':{key:{'path':paths[key],'pages':counters[key]} for key in counters},'sections':sections,'note':'Page-order and file checks only; design quality and image/geometry agreement require independent review.'}
    path=os.path.join(pkg.dir,presentation.INDEX);xc.write_json(path,index);written.append(path)
    if not args.skip_a0:
        with PdfPages(os.path.join(ddir, "a0-board.pdf")) as pdf:
            f = a0_board(pkg)
            pdf.savefig(f, facecolor=PAPER)
            plt.close(f)
            d = pdf.infodict()
            d["Title"] = "%s - A0 board" % pkg.title
            d["Keywords"] = "input-sha256:%s make_figures:%s" % (pkg.input_hash, xc.SCRIPT_VERSION)
            d["CreationDate"] = None
            d["ModDate"] = None
        compress_pdf_images(os.path.join(ddir, "a0-board.pdf"))
        written.append(os.path.join(ddir, "a0-board.pdf"))
        print("  drawings/a0-board.pdf")
    # node figures left over from nodes the package no longer has (a scheme that changed its three nodes)
    import glob
    for old in glob.glob(os.path.join(fdir, "node-*-*.png")):
        if old not in written:
            os.remove(old)
            print("  removed stale %s" % os.path.relpath(old, pkg.dir))
    stamp = {
        "script": "scripts/make_figures.py", "script_version": xc.SCRIPT_VERSION, "input_sha256": pkg.input_hash,
        "files": {os.path.relpath(p, pkg.dir).replace(os.sep, "/"): xc.sha256_file(p) for p in written},
    }
    xc.write_json(os.path.join(fdir, "stamp.json"), stamp)
    print("done: %d files, input %s" % (len(written), pkg.input_hash[:12]))


if __name__ == "__main__":
    main()
