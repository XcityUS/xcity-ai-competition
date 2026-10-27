#!/usr/bin/env python3
"""Build an offline 3D scene of a submission: visual/index.html (three.js, no network).

    python scripts/make_scene.py submissions/<github-login>/<proposal-slug>

The scene is made only from the package's own geometry plus the site package's terrain:
buildings are extruded from buildings.geojson (floors x 3.5 m or height_m), ground from land_use.geojson,
streets from movement.geojson, and the sun is computed for San Juan. Roof PV and water channels
require explicit source properties; a shaded route does not imply a canal. Procedural planting,
PV tables and illustrative people/vehicles require separate manifest.scene_generation opt-ins.
Such additions are illustrative, never measured assets, agronomic evidence or installed capacity.

Open visual/index.html in any browser to orbit the scene and save views. To render the named views as
PNG files for the drawings, run scripts/render_views.py.
"""
import argparse
import base64
import datetime
import hashlib
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np                                         # noqa: E402
from PIL import Image                                      # noqa: E402
from shapely.geometry import Point, Polygon, LineString, box, mapping   # noqa: E402
from shapely.ops import unary_union                        # noqa: E402
from shapely.strtree import STRtree                        # noqa: E402
import xcity_common as xc                                  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
VENDOR = os.path.join(HERE, "vendor", "three-r147")
FLOOR_H = 3.5
LAT, LON, UTC_OFFSET = -30.85, -68.1, -3
TIMES = {"day": (2026, 10, 21, 15, 0), "evening": (2026, 10, 21, 18, 50), "night": (2026, 10, 21, 21, 30)}
WIDTH = {"people": 4.0, "shared": 9.0, "machine": 8.0}


# ------------------------------------------------------------------------- sun (NOAA)
def sun_position(y, mo, d, hh, mm, lat=LAT, lon=LON, tz=UTC_OFFSET):
    t = datetime.datetime(y, mo, d, hh, mm) - datetime.timedelta(hours=tz)
    jd = (t - datetime.datetime(2000, 1, 1, 12)).total_seconds() / 86400.0 + 2451545.0
    jc = (jd - 2451545.0) / 36525.0
    L0 = (280.46646 + jc * (36000.76983 + jc * 0.0003032)) % 360
    M = 357.52911 + jc * (35999.05029 - 0.0001537 * jc)
    e = 0.016708634 - jc * (0.000042037 + 0.0000001267 * jc)
    C = (math.sin(math.radians(M)) * (1.914602 - jc * (0.004817 + 0.000014 * jc)) +
         math.sin(math.radians(2 * M)) * (0.019993 - 0.000101 * jc) + math.sin(math.radians(3 * M)) * 0.000289)
    lam = L0 + C - 0.00569 - 0.00478 * math.sin(math.radians(125.04 - 1934.136 * jc))
    eps = 23 + (26 + (21.448 - jc * (46.815 + jc * (0.00059 - jc * 0.001813))) / 60) / 60
    eps += 0.00256 * math.cos(math.radians(125.04 - 1934.136 * jc))
    dec = math.degrees(math.asin(math.sin(math.radians(eps)) * math.sin(math.radians(lam))))
    yv = math.tan(math.radians(eps / 2)) ** 2
    eot = 4 * math.degrees(yv * math.sin(2 * math.radians(L0)) - 2 * e * math.sin(math.radians(M)) +
                           4 * e * yv * math.sin(math.radians(M)) * math.cos(2 * math.radians(L0)) -
                           0.5 * yv * yv * math.sin(4 * math.radians(L0)) - 1.25 * e * e * math.sin(2 * math.radians(M)))
    tst = (t.hour * 60 + t.minute + eot + 4 * lon) % 1440
    ha = tst / 4 - 180 if tst / 4 >= 0 else tst / 4 + 180
    zen = math.degrees(math.acos(math.sin(math.radians(lat)) * math.sin(math.radians(dec)) +
                                 math.cos(math.radians(lat)) * math.cos(math.radians(dec)) * math.cos(math.radians(ha))))
    az = math.degrees(math.acos(max(-1, min(1, ((math.sin(math.radians(lat)) * math.cos(math.radians(zen))) -
                                                 math.sin(math.radians(dec))) /
                                                (math.cos(math.radians(lat)) * math.sin(math.radians(zen)))))))
    az = (az + 180) % 360 if ha > 0 else (540 - az) % 360
    return round(az, 1), round(90 - zen, 1)


# ------------------------------------------------------------------------- helpers
def rings(poly, o):
    ox, oy = o
    def r(c):
        pts = [(round(x - ox, 2), round(y - oy, 2)) for x, y in list(c)[:-1]]
        return pts
    return {"outer": r(poly.exterior.coords), "holes": [r(h.coords) for h in poly.interiors]}


def polys(g):
    if g is None or g.is_empty:
        return []
    if g.geom_type == "Polygon":
        return [g]
    return [p for p in getattr(g, "geoms", []) if p.geom_type == "Polygon"]


def lines(g):
    if g is None or g.is_empty:
        return []
    if g.geom_type == "LineString":
        return [g]
    return [l for l in getattr(g, "geoms", []) if l.geom_type == "LineString"]


def b64grid(arr):
    a = np.round(arr * 10).astype("<i2")
    return base64.b64encode(a.tobytes()).decode()


class Scene:
    def __init__(self, pkg_path):
        self.pkg, self.login, self.slug = xc.find_package(pkg_path)
        self.man = xc.load_json(os.path.join(self.pkg, "manifest.json"))
        geo = xc.load_geometry(self.pkg)
        probs = xc.geometry_problems(geo)
        if probs:
            raise SystemExit("fix the geometry first:\n  " + "\n  ".join(probs))
        self.geo = {k: [(p, xc.to_utm(g)) for p, g in v] for k, v in geo.items()}
        if not self.geo["master_area"]:
            raise SystemExit("geometry/master_area.geojson is empty")
        self.master = unary_union([g for _, g in self.geo["master_area"]])
        self.site = xc.to_utm(xc.site_boundary())
        c = self.master.centroid
        self.o = (round(c.x), round(c.y))
        self.near = self.master.buffer(2500).envelope
        # Trees, people and vehicles are placed at random but reproducibly: the same package gives the same scene on
        # any machine. manifest.scene_seed (an integer) picks another arrangement; otherwise the seed comes from the
        # package's login and slug.
        seed = self.man.get("scene_seed")
        if not isinstance(seed, int):
            seed = int(hashlib.sha256(("%s/%s" % (self.login, self.slug)).encode()).hexdigest()[:8], 16) ^ 0x5EED
        self.rand = random.Random(seed)
        ts = xc.site_json("terrain/terrain_summary_9_13.json")["files"]
        self.dem = np.array(Image.open(os.path.join(xc.SITE, "terrain", ts["dem_png"]))).astype("float32")
        self.db = ts["hillshade_utm_bounds_m"]
        self.buildings = [g for p, g in self.geo["buildings"] if p.get("form") != "canopy"]
        self.btree = STRtree(self.buildings) if self.buildings else None

    def L(self, x, y):
        return (round(x - self.o[0], 2), round(y - self.o[1], 2))

    def free(self, pt, clearance=1.5):
        if self.btree is None:
            return True
        q = pt.buffer(clearance)
        return not any(self.buildings[i].intersects(q) for i in self.btree.query(q))

    # --------------------------------------------------------------- terrain
    def terrain(self, bounds, step):
        x0, y0, x1, y1 = self.db
        h, w = self.dem.shape
        bx0, by0, bx1, by1 = bounds
        xs = np.arange(bx0, bx1 + step, step)
        ys = np.arange(by1, by0 - step, -step)
        cx = np.clip(((xs - x0) / (x1 - x0) * w).astype(int), 0, w - 1)
        cy = np.clip(((y1 - ys) / (y1 - y0) * h).astype(int), 0, h - 1)
        grid = self.dem[np.ix_(cy, cx)] - self.z0
        return {"x0": float(xs[0] - self.o[0]), "x1": float(xs[-1] - self.o[0]), "y0": float(ys[-1] - self.o[1]),
                "y1": float(ys[0] - self.o[1]), "w": len(xs), "h": len(ys), "heights_b64": b64grid(grid)}

    def build(self):
        x0, y0, x1, y1 = self.db
        h, w = self.dem.shape
        cx = int((self.o[0] - x0) / (x1 - x0) * w)
        cy = int((y1 - self.o[1]) / (y1 - y0) * h)
        self.z0 = float(self.dem[min(max(cy, 0), h - 1), min(max(cx, 0), w - 1)])
        far = self.terrain((x0 + 60, y0 + 60, x1 - 60, y1 - 60), 180.0)
        near = self.terrain(self.near.bounds, 60.0)
        nb = self.near.bounds
        d = {"seed": 11, "origin_utm": list(self.o), "z0": self.z0, "terrain": far, "terrain_near": near,
             "near": [nb[0] - self.o[0], nb[1] - self.o[1], nb[2] - self.o[0], nb[3] - self.o[1]],
             "pv_tilt": 18}
        d["suns"] = {}
        for k, tt in TIMES.items():
            az, el = sun_position(*tt)
            d["suns"][k] = {"azimuth": az, "elevation": el,
                            "label": "%02d:%02d, 21 October, sun %s deg up" % (tt[3], tt[4], el) if el > 0 else
                            "%02d:%02d, 21 October, night" % (tt[3], tt[4])}
        W = self.site.union(self.near)
        # Keep all submitted territorial works; near only controls terrain sampling detail.
        # ground
        ground = []
        for p, g in self.geo["land_use"]:
            for pg in polys(g.intersection(W)):
                r = rings(pg, self.o)
                r["use"] = p.get("use")
                nm = str(p.get("name", "")).lower()
                r["plaza"] = any(k in nm for k in ("plaza", "square", "arcade", "spine", "广场"))
                ground.append(r)
        d["ground"] = ground
        # washes
        wash = []
        for p, g in xc.channels():
            gu = xc.to_utm(g)
            if gu.intersects(W):
                wash += [rings(pg, self.o) for pg in polys(gu.intersection(W).buffer(25 if p.get("class") == "main" else 12))]
        d["washes"] = wash
        # Whole-site annotations remain source geometry, not designed water or a fence.
        d["site_boundary"] = [rings(pg, self.o) for pg in polys(self.site)]
        d["source_channels"] = [[self.L(x, y) for x, y in ln.coords]
                                for _, g in xc.channels()
                                for ln in lines(xc.to_utm(g).intersection(self.site))]
        # roads
        roads = []
        for net in ("machine", "people", "shared"):
            segs = []
            for p, g in self.geo["movement"]:
                if p.get("network") != net or not g.geom_type.endswith("LineString"):
                    continue
                wd = float(p.get("width_m") or WIDTH[net])
                for ln in lines(g.intersection(W.buffer(500))):
                    segs.append(ln.buffer(wd / 2, cap_style=2, join_style=2))
            u = unary_union(segs) if segs else None
            for pg in polys(u):
                r = rings(pg.simplify(0.3), self.o)
                r["net"] = net
                roads.append(r)
        d["roads"] = roads
        d["tables"] = [rings(g.buffer(4, cap_style=3), self.o) for p, g in self.geo["movement"]
                       if p.get("kind") == "interface" and g.geom_type == "Point"]
        # buildings
        bl = []
        for p, g in self.geo["buildings"]:
            if not g.intersects(W):
                continue
            hgt = float(p.get("height_m") or 0) or max(1.0, float(p.get("floors", 1) or 1)) * FLOOR_H + 0.6
            for pg in polys(g):
                r = rings(pg.simplify(0.05), self.o)
                r.update({"use": p.get("use"), "h": round(hgt, 2), "form": p.get("form", ""),
                          "ground_shop": p.get("use") == "mixed_use", "name": p.get("name", ""), "roof_pv": bool(p.get("roof_pv", False))})
                if p.get("form") == "canopy":
                    r["h"] = float(p.get("height_m") or 4.5)
                    r["pv"] = "pv" in str(p.get("name", "")).lower()
                    posts = []
                    ring = LineString(pg.exterior.coords)
                    n = max(4, int(ring.length / 9))
                    for k in range(n):
                        q = ring.interpolate(k / n, normalized=True)
                        c = pg.centroid
                        v = np.array([c.x - q.x, c.y - q.y])
                        v = v / (np.linalg.norm(v) or 1) * 0.6
                        posts.append(self.L(q.x + v[0], q.y + v[1]))
                    r["posts"] = posts
                bl.append(r)
        d["buildings"] = bl
        # PV tables: energy land in the master area plus energy_compute structure within 1.5 km
        pv_area = [g for p, g in self.geo["land_use"] if p.get("use") == "energy"]
        ring = self.master.buffer(1500).difference(self.master)
        pv_area += [g.intersection(ring) for p, g in self.geo["structure"] if p.get("system") == "energy_compute"]
        if not self.man.get("scene_generation", {}).get("procedural_pv", False):
            pv_area = []  # Explicit opt-in only: energy land is not a module layout.
        bu = unary_union(self.buildings).buffer(6) if self.buildings else None
        roads_u = unary_union([g.buffer(WIDTH.get(p.get("network"), 5)) for p, g in self.geo["movement"]
                               if g.geom_type.endswith("LineString")])
        rows = []
        for area in pv_area:
            for pg in polys(area):
                pg = pg.difference(roads_u)
                if bu is not None:
                    pg = pg.difference(bu)
                if pg.is_empty:
                    continue
                bx0, by0, bx1, by1 = pg.bounds
                L = 120.0 if not self.master.buffer(50).intersects(pg) else 40.0
                x = bx0 + 3
                while x < bx1:
                    y = by0
                    while y < by1:
                        seg = LineString([(x, y), (x, min(y + L, by1))]).intersection(pg)
                        for s in lines(seg):
                            if s.length > 8:
                                mid = s.interpolate(0.5, normalized=True)
                                rows.append([round(mid.x - self.o[0], 1), round(mid.y - self.o[1], 1), round(s.length - 2, 1)])
                        y += L + 4
                    x += 6.5
                if len(rows) > 60000:
                    break
        d["pv_rows"] = rows[:60000]
        # Roof PV is shown only when the submitted building explicitly declares it.
        for b in d["buildings"]:
            if b.get("form") != "canopy":
                u = b.get("use")
                b["roof_pv"] = bool(b.get("roof_pv", False))  # No random installations.
        # trees: [x, y, size, rotation, type]  type 0 broad shade tree, 1 poplar windbreak, 2 olive / orchard
        R = self.rand
        trees, shrubs = [], []
        bfoot = unary_union(self.buildings).buffer(2.5) if self.buildings else Polygon()
        bhard = unary_union(self.buildings).buffer(0.8) if self.buildings else Polygon()
        canopies = unary_union([g for p, g in self.geo["buildings"] if p.get("form") == "canopy"])
        if not canopies.is_empty:
            bfoot = bfoot.union(canopies.buffer(4))
        moving = unary_union([g.buffer((float(p.get("width_m") or WIDTH.get(p.get("network"), 5))) / 2)
                              for p, g in self.geo["movement"] if g.geom_type.endswith("LineString")])
        centre = Point(self.o)

        def add(x, y, size, typ):
            trees.append([*self.L(x, y), round(size, 2), round(R.random() * 6, 2), typ])

        if self.man.get("scene_generation", {}).get("procedural_planting", False):
            for p, g in self.geo["movement"]:
                if p.get("network") in ("people", "shared") and p.get("shaded") and g.geom_type.endswith("LineString"):
                    wd = float(p.get("width_m") or WIDTH[p["network"]])
                    offs = [1.2] if wd < 12 else [wd / 2 - 2.2, wd / 2 - 6.5] if wd >= 30 else [wd / 2 - 2.2]
                    step = 8.0 if wd >= 12 else 9.0
                    for ln in lines(g):
                        n = int(ln.length // step)
                        for k in range(1, n):
                            a = ln.interpolate(k * step)
                            b = ln.interpolate(min(ln.length, k * step + 1))
                            dx, dy = b.x - a.x, b.y - a.y
                            nn = math.hypot(dx, dy) or 1
                            for off in offs:
                                for sgn in ((-1, 1) if wd >= 12 else ((-1,) if k % 2 else (1,))):
                                    q = Point(a.x - dy / nn * off * sgn, a.y + dx / nn * off * sgn)
                                    if not bfoot.contains(q) or (wd < 12 and not bhard.contains(q)):
                                        add(q.x, q.y, (0.85 if wd >= 12 else 0.62) + R.random() * 0.3, 0)
            washes = unary_union([xc.to_utm(g).buffer(60 if p.get("class") == "main" else 30) for p, g in xc.channels()])
            for p, g in self.geo["land_use"]:
                use, nm = p.get("use"), str(p.get("name", "")).lower()
                for pg in polys(g.intersection(W)):
                    bx0, by0, bx1, by1 = pg.bounds
                    near = pg.centroid.distance(centre) < 3500
                    if use == "agriculture" and any(k in nm for k in ("orchard", "olive", "pistachio", "vine")):
                        sx, sy = (7.0, 6.0) if near else (14.0, 12.0)
                        for xx in np.arange(bx0 + 3, bx1, sx):
                            for yy in np.arange(by0 + 3, by1, sy):
                                if pg.contains(Point(xx, yy)) and len(trees) < 90000:
                                    add(xx, yy, 0.6 + R.random() * 0.15, 2)
                    elif any(k in nm for k in ("alameda", "windbreak", "tree belt")):
                        # poplar rows parallel to the long side, every 4 m along, rows 5 m apart
                        long_ns = (by1 - by0) >= (bx1 - bx0)
                        if "slope" in nm:      # a belt along the top edge of a slope park
                            band = box(bx0, by1 - 30, bx1, by1) if not long_ns else box(bx0, by0, bx0 + 30, by1)
                            band = band.intersection(pg)
                        else:
                            band = pg
                        b0 = band.bounds if not band.is_empty else pg.bounds
                        for r_ in range(4):
                            for t_ in np.arange(0, (b0[3] - b0[1]) if long_ns else (b0[2] - b0[0]), 4.0):
                                xx = (b0[0] + 6 + r_ * 5) if long_ns else (b0[0] + t_)
                                yy = (b0[1] + t_) if long_ns else (b0[3] - 6 - r_ * 5)
                                q = Point(xx, yy)
                                if band.contains(q) and not moving.contains(q):
                                    add(xx, yy, 0.9 + R.random() * 0.25, 1)
                        if "slope" in nm:
                            for _ in range(int(pg.area / 900)):
                                q = Point(R.uniform(bx0, bx1), R.uniform(by0, by1))
                                if pg.contains(q) and not moving.contains(q):
                                    add(q.x, q.y, 0.8 + R.random() * 0.5, 0)
                    elif any(k in nm for k in ("paved", "sunken", "hard", "sports")):
                        continue
                    elif use in ("open_space", "civic") or (use in ("residential", "mixed_use") and near):
                        dense = any(k in nm for k in ("plaza", "square", "grove", "patio", "garden", "yard", "court"))
                        if use in ("residential", "mixed_use"):
                            spacing = 110.0      # gardens and courtyards between the houses
                        elif dense:
                            spacing = 150.0
                        elif "sport" in nm or "bluff" in nm or "river" in nm:
                            spacing = 700.0
                        else:
                            spacing = 400.0
                        n = int(pg.area / spacing)
                        tries = 0
                        while n > 0 and tries < n * 6 and len(trees) < 90000:
                            tries += 1
                            q = Point(R.uniform(bx0, bx1), R.uniform(by0, by1))
                            if pg.contains(q) and not bfoot.contains(q) and not moving.contains(q) and not washes.contains(q):
                                add(q.x, q.y, 0.75 + R.random() * 0.6, 0)
                                n -= 1
            desert = self.master.buffer(1500).difference(self.master).union(
                unary_union([g for p, g in self.geo["land_use"] if p.get("use") == "reserve"]))
            bx0, by0, bx1, by1 = desert.bounds
            for _ in range(14000):
                q = Point(R.uniform(bx0, bx1), R.uniform(by0, by1))
                if desert.contains(q) and not bfoot.contains(q):
                    shrubs.append([*self.L(q.x, q.y), round(0.6 + R.random() * 1.1, 2)])
        d["trees"], d["shrubs"] = trees[:90000], shrubs
        # acequias: 0.8 m channels along both sides of the shaded shared streets
        aceq = []
        for p, g in self.geo["movement"]:
            if p.get("water_channel_design") is True and g.geom_type.endswith("LineString"):
                wd = float(p.get("width_m") or WIDTH["shared"])
                for ln in lines(g.intersection(W)):
                    for sgn in (-1, 1):
                        try:
                            o = ln.parallel_offset(sgn * (wd / 2 - 3.6), join_style=2)
                        except Exception:
                            continue
                        for pg in polys(o.buffer(0.4, cap_style=2, join_style=2).difference(bfoot)):
                            aceq.append(rings(pg, self.o))
        d["acequias"] = aceq
        # people, robots, vehicles, lamps; pp = [x, y, heading, pose, colour, scale]
        people, robots, trucks, lamps = [], [], [], []
        nodes = unary_union([g for p, g in self.geo["nodes"]]) if self.geo["nodes"] else Polygon()
        civic = unary_union([g for p, g in self.geo["land_use"] if p.get("use") in ("civic", "open_space", "mixed_use")
                             and g.intersects(self.master)])
        town = unary_union([g for p, g in self.geo["buildings"] if p.get("use") in ("residential", "mixed_use", "civic")])
        hot = nodes.union(civic.buffer(20) if not civic.is_empty else Polygon())

        def person(x, y, heading, child=False):
            people.append([*self.L(x, y), round(heading, 2), R.randrange(2), R.randrange(10),
                           round(R.uniform(0.62, 0.72) if child else R.uniform(0.92, 1.06), 2)])

        for p, g in self.geo["movement"]:
            if not g.geom_type.endswith("LineString"):
                continue
            net = p.get("network")
            wd = float(p.get("width_m") or WIDTH.get(net, 5))
            for ln in lines(g.intersection(W.buffer(800))):
                step = 7.0 if net in ("people", "shared") else 60.0
                n = int(ln.length // step)
                for k in range(n):
                    a = ln.interpolate(k * step + R.uniform(0, step))
                    b = ln.interpolate(min(ln.length, k * step + 1))
                    dx, dy = b.x - a.x, b.y - a.y
                    nn = math.hypot(dx, dy) or 1
                    ang = math.atan2(dx, dy)
                    inside = hot.contains(a)
                    near_town = (not town.is_empty) and town.distance(a) < 60
                    if net in ("people", "shared"):
                        if R.random() < (0.5 if inside else 0.16 if near_town else 0.02):
                            off = R.uniform(-wd / 2 + 1.0, wd / 2 - 1.0)
                            q = Point(a.x - dy / nn * off, a.y + dx / nn * off)
                            person(q.x, q.y, ang + (math.pi if R.random() < 0.5 else 0))
                            if R.random() < 0.3:      # walking together; sometimes with a child
                                person(q.x + dy / nn * 0.7, q.y - dx / nn * 0.7, ang, child=R.random() < 0.35)
                        if net == "shared" and R.random() < 0.06:
                            robots.append([*self.L(a.x - dy / nn * (wd / 2 - 5), a.y + dx / nn * (wd / 2 - 5)), round(ang, 2)])
                        if k % 3 == 0 and (inside or near_town):
                            lamps.append([*self.L(a.x - dy / nn * (wd / 2 - 1), a.y + dx / nn * (wd / 2 - 1))])
                    elif net == "machine" and (self.master.contains(a) or R.random() < 0.3):
                        if R.random() < 0.35:
                            nm = str(p.get("name", "")).lower()
                            kind = 1 if any(k in nm for k in ("arrival", "freight", "service", "access", "logistic")) and R.random() < 0.6 else 0
                            off = (wd / 4) * (1 if R.random() < 0.5 else -1)
                            trucks.append([*self.L(a.x - dy / nn * off, a.y + dx / nn * off),
                                           round(ang + (0 if off > 0 else math.pi), 2), kind])
        # gatherings in squares, gardens and yards
        for p, g in self.geo["land_use"]:
            nm = str(p.get("name", "")).lower()
            if p.get("use") in ("open_space", "civic") and g.intersects(hot) and any(
                    k in nm for k in ("plaza", "square", "grove", "patio", "garden", "yard", "court", "arrival")):
                bx0, by0, bx1, by1 = g.bounds
                n = int(min(260, g.area / 120))
                for _ in range(n):
                    q = Point(R.uniform(bx0, bx1), R.uniform(by0, by1))
                    if g.contains(q) and not bfoot.contains(q):
                        person(q.x, q.y, R.uniform(0, 6.28), child=R.random() < 0.25)
                        if R.random() < 0.5:
                            person(q.x + R.uniform(-1.2, 1.2), q.y + R.uniform(-1.2, 1.2), R.uniform(0, 6.28))
        # keep the foreground of every eye-level camera clear: nothing within 9 m, no people in the first 18 m ahead
        eyes = []
        for p, g in self.geo["nodes"]:
            e, t = self.eye(p, g)
            eyes.append((self.L(*e), self.L(*t)))

        def clear(it, ahead=0.0):
            for (ex, ey), (tx, ty) in eyes:
                dx, dy = it[0] - ex, it[1] - ey
                if dx * dx + dy * dy < 81:
                    return False
                if ahead:
                    vx, vy = tx - ex, ty - ey
                    n = math.hypot(vx, vy) or 1
                    along = (dx * vx + dy * vy) / n
                    side = abs(dx * vy - dy * vx) / n
                    if 0 < along < ahead and side < 3.5:
                        return False
            return True

        people = [q for q in people if clear(q, 18.0)]
        lamps = [q for q in lamps if clear(q, 12.0)]
        d["trees"] = [q for q in d["trees"] if clear(q, 10.0)]
        if not self.man.get("scene_generation", {}).get("illustrative_entourage", False):
            people, robots, trucks, lamps = [], [], [], []
        d["people"], d["robots"], d["trucks"], d["lamps"] = people[:600], robots[:150], trucks[:80], lamps[:1000]
        d["views"] = self.views()
        return d

    # --------------------------------------------------------------- cameras
    def views(self):
        """Named camera views. A node may set aerial_from [lon, lat], eye_from and eye_to in nodes.geojson."""
        out = []
        az_day = sun_position(*TIMES["day"])[0]
        az_eve = sun_position(*TIMES["evening"])[0]
        town = unary_union([g for p, g in self.geo["buildings"] if p.get("use") in ("residential", "mixed_use")])
        built = unary_union(self.buildings) if self.buildings else self.master
        if town.is_empty:
            town = built

        def ext(g):
            x0, y0, x1, y1 = g.bounds
            return max(x1 - x0, y1 - y0)

        def aerial(cx, cy, r, vid, label, time="day", az=None, pitch=33.0, fov=40.0):
            a = math.radians(az if az is not None else az_day - 40)
            dist = r / math.tan(math.radians(fov / 2)) * 1.05
            hz = dist * math.sin(math.radians(pitch))
            hd = dist * math.cos(math.radians(pitch))
            px, py = cx + math.sin(a) * hd, cy + math.cos(a) * hd
            out.append({"id": vid, "label": label, "time": time, "fov": fov,
                        "pos": [*self.L(px, py), round(hz, 1)], "target": [*self.L(cx, cy), 0],
                        "shadow_radius": round(min(6000, r * 1.8))})

        sc = self.site.envelope.centroid
        bx0, by0, bx1, by1 = self.site.bounds
        radius = math.hypot(bx1 - bx0, by1 - by0) * 0.58
        aerial(sc.x, sc.y, radius, "whole-site-aerial",
               "Whole issued site / source boundary and seasonal-channel annotations / proposed works only", pitch=55, fov=42)
        bc = built.convex_hull.centroid
        aerial(bc.x, bc.y, ext(built.convex_hull) * 0.42, "master-aerial", "Local built-work envelope - not the whole-site overview", pitch=30, fov=40)
        tc = town.convex_hull.centroid
        aerial(tc.x, tc.y, ext(town.convex_hull) * 0.36, "city-aerial", "Residential / mixed-use enlargement - not the whole-site overview", pitch=24, fov=42)
        aerial(tc.x, tc.y, ext(town.convex_hull) * 0.3, "city-evening", "All proposed urban geometry - hypothetical evening", time="evening",
               az=az_eve - 25, pitch=20, fov=44)
        for p, g in self.geo["nodes"]:
            nid = str(p.get("node_id"))
            inb = [b for b in self.buildings if b.intersects(g)]
            gc = unary_union(inb).convex_hull.centroid if inb else g.centroid
            r = max(110.0, min(450.0, math.sqrt(g.area) * 0.62))
            if p.get("aerial_from"):
                af = xc.to_utm(Point(*p["aerial_from"]))
                az = math.degrees(math.atan2(af.x - gc.x, af.y - gc.y))
            else:
                az = None
            aerial(gc.x, gc.y, r, "%s-aerial" % nid, "%s - aerial" % nid, az=az, pitch=36)
            e, t = self.eye(p, g)
            for time in ("day", "evening" if nid != self.night_node() else "night"):
                out.append({"id": "%s-eye-%s" % (nid, time), "label": "%s - eye level, %s" % (nid, time), "time": time,
                            "fov": 60.0, "pos": [*self.L(*e), 1.6], "target": [*self.L(*t), 3.0],
                            "shadow_radius": 450})
        return out

    def night_node(self):
        for p, g in self.geo["nodes"]:
            if any(b.intersects(g) for q, b in self.geo["buildings"] if q.get("use") in ("residential", "mixed_use")):
                return str(p.get("node_id"))
        return ""

    def eye(self, p, g):
        if p.get("eye_from"):
            e = xc.to_utm(Point(*p["eye_from"]))
            t = xc.to_utm(Point(*p["eye_to"])) if p.get("eye_to") else g.centroid
            return (e.x, e.y), (t.x, t.y)
        c = g.centroid
        best = None
        for q, ln in self.geo["movement"]:
            if q.get("network") in ("people", "shared") and ln.geom_type.endswith("LineString") and ln.intersects(g):
                for s in lines(ln.intersection(g)):
                    for f in np.linspace(0.05, 0.95, 19):
                        pt = s.interpolate(f, normalized=True)
                        sc = abs(pt.distance(c) - math.sqrt(g.area) * 0.35)
                        if best is None or sc < best[0]:
                            best = (sc, (pt.x, pt.y))
        e = best[1] if best else (g.exterior.interpolate(0.5, normalized=True).x, g.exterior.interpolate(0.5, normalized=True).y)
        return e, (c.x, c.y)


def page(pkg_title, data):
    vend = lambda n: open(os.path.join(VENDOR, n), encoding="utf-8").read()
    scene_js = open(os.path.join(HERE, "scene", "scene.js"), encoding="utf-8").read()
    import html
    return ("<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            "<title>" + html.escape(pkg_title) + " - 3D scene</title><style>"
            "html,body{margin:0;height:100%;background:#0d0d0e;color:#f2efe9;font:13px -apple-system,Segoe UI,Helvetica,Arial,sans-serif}"
            "#view{position:absolute;inset:0}#ui{position:absolute;left:12px;top:12px;right:12px;display:flex;flex-wrap:wrap;gap:6px;align-items:center}"
            "#ui h1{font-size:14px;margin:0 10px 0 0;font-weight:600}#views button{background:rgba(13,13,14,.72);color:#f2efe9;border:1px solid rgba(201,169,97,.45);"
            "padding:5px 9px;cursor:pointer;margin:0 4px 4px 0}#views button.save{border-color:#c9a961;color:#c9a961}"
            "#cap{position:absolute;left:12px;bottom:10px;opacity:.8}#note{position:absolute;right:12px;bottom:10px;opacity:.6;max-width:50ch;text-align:right}"
            "</style></head><body><div id=\"view\"></div><div id=\"ui\"><h1>" + html.escape(pkg_title) + "</h1><div id=\"views\"></div></div>"
            "<div id=\"cap\"></div><div id=\"note\">Rendered offline from this submission's geometry. Trees, people, vehicles and PV "
            "tables are generated from it to show scale and use; they are not evidence. Terrain: produced using Copernicus "
            "WorldDEM-30 (c) DLR e.V. 2010-2014 and (c) Airbus Defence and Space GmbH 2014-2018 provided under COPERNICUS by "
            "the European Union and ESA; all rights reserved. three.js (MIT).</div>"
            "<script>" + vend("three.min.js") + "</script><script>" + vend("OrbitControls.js") + "</script><script>" + vend("Sky.js")
            + "</script><script>window.XCITY_SCENE=" + json.dumps(data, separators=(",", ":")) + ";</script><script>"
            + scene_js + "</script></body></html>")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("package")
    a = ap.parse_args()
    sc = Scene(a.package)
    data = sc.build()
    data["input_sha256"] = xc.scene_input_hash(sc.pkg)
    out = os.path.join(sc.pkg, "visual", "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    doc = page(sc.man.get("title", sc.slug), data)
    open(out, "w", encoding="utf-8").write(doc)
    print("wrote %s (%d KB): %d buildings, %d PV tables, %d trees, %d people, %d views"
          % (os.path.relpath(out, xc.ROOT), len(doc.encode()) // 1024, len(data["buildings"]), len(data["pv_rows"]),
             len(data["trees"]), len(data["people"]), len(data["views"])))


if __name__ == "__main__":
    main()
