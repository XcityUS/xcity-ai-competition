# -*- coding: utf-8 -*-
"""The example's own geometry generator for 'Terrace Oasis' (written by the agent, not part of the competition tools).
Run from the repository root:
    python submissions/EXAMPLE-agent/sample-scheme/tools/gen_geometry.py submissions/EXAMPLE-agent/sample-scheme
Everything is built in UTM 19S (metres) and written as lon/lat GeoJSON.

Scale 1  the whole site: a chain of oasis cities on one corridor ("the Line"), fields on the flats, PV and compute
         on the fans, mountain and washes kept as reserve.
Scale 2  the first city, on the flat lower terrace directly east of the pilot area: a 300 m superblock grid of
         low courtyard housing, machines on a 600 m grid, acequia streets fed by gravity from a tank on the bluff.
Scale 3  C01 arrival along the first fields, A01 a housing superblock, A03 the main square in heat and Zonda.
"""
import json, math, os, re, sys, random
import numpy as np
sys.path.insert(0, "scripts")
import xcity_common as xc
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image
from shapely.geometry import Point, Polygon, LineString, MultiPolygon, box, mapping, shape
from shapely.ops import unary_union, nearest_points
from shapely import make_valid
import shapely

PKG = sys.argv[1]
GEO = os.path.join(PKG, "geometry")
RND = random.Random(913)

SITE = xc.to_utm(xc.site_boundary())
LEAD = xc.to_utm(xc.pilot_area())
CH = [(p, xc.to_utm(g)) for p, g in xc.channels()]
FLOOD = unary_union([xc.to_utm(shape(f["geometry"])) for f in
                     xc.site_json("water/flood_sensitive_dem.geojson")["features"]])
IND = xc.site_json("zoning/indicative_systems_9_13.json")["systems"]
U = lambda lon, lat: np.array(xc.to_utm(Point(lon, lat)).coords[0])
LL = lambda x, y: list(xc.to_lonlat(Point(x, y)).coords[0])

# ---------------------------------------------------------------- terrain masks
ts = xc.site_json("terrain/terrain_summary_9_13.json")["files"]
dem = np.array(Image.open(os.path.join(xc.SITE, "terrain", ts["dem_png"]))).astype(float)
x0, y0, x1, y1 = ts["hillshade_utm_bounds_m"]
R = (x1 - x0) / dem.shape[1]
gy, gx = np.gradient(dem, R, R)
slope = np.hypot(gx, gy) * 100


def box_mean(a, k):
    p = k // 2
    b = np.pad(a, p, mode="edge")
    c = np.pad(b.cumsum(0).cumsum(1), ((1, 0), (1, 0)))
    return (c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]) / (k * k)


slope_s = box_mean(slope, 7)


def mask_polys(mask, min_area=2e5):
    X = x0 + (np.arange(mask.shape[1]) + .5) * R
    Y = y1 - (np.arange(mask.shape[0]) + .5) * R
    fig, ax = plt.subplots()
    cs = ax.contourf(X, Y, mask.astype(float), levels=[0.5, 1.5])
    polys = []
    for path in cs.get_paths():
        for ring in path.to_polygons():
            if len(ring) >= 4:
                polys.append(Polygon(ring))
    plt.close(fig)
    g = Polygon()
    for p in sorted(polys, key=lambda p: -p.area):
        g = g.symmetric_difference(make_valid(p))
    g = make_valid(g).buffer(0)
    return unary_union([p for p in getattr(g, "geoms", [g]) if p.geom_type == "Polygon" and p.area >= min_area])


def clean(g, min_area=5e4):
    g = make_valid(g).buffer(0)
    parts = [p for p in getattr(g, "geoms", [g]) if p.geom_type == "Polygon" and p.area >= min_area]
    return unary_union(parts)


def z(x, y):
    return float(dem[int((y1 - y) / R), int((x - x0) / R)])


MOUNTAIN = mask_polys(slope_s >= 6.0).intersection(SITE)
FLAT = mask_polys(slope_s < 2.0, 1e6).intersection(SITE).difference(FLOOD).difference(MOUNTAIN)
FAN = mask_polys((slope_s >= 2.0) & (slope_s < 4.5), 1e6).intersection(SITE).difference(FLOOD).difference(MOUNTAIN)

# ================================================================ scale 2: the first city
X0, Y0, S = 572400.0, 6549450.0, 300.0           # superblock grid origin (south-west corner) and pitch
NI, NJ = 7, 6                                      # 7 columns x 6 rows of 300 m on the lower terrace
XE, YN = X0 + NI * S, Y0 + NJ * S                   # 574500, 6551250


def sb(i, j):
    return box(X0 + i * S, Y0 + j * S, X0 + (i + 1) * S, Y0 + (j + 1) * S)


MASTER = box(571500, 6547700, 578600, 6554300).intersection(SITE).difference(LEAD.buffer(15))
MASTER = clean(MASTER, 1e6)

land, bldg, move = [], [], []


def L(use, geom, name="", level=None):
    geom = geom.intersection(MASTER)
    if not geom.is_empty and geom.area > 50:
        p = {"use": use, "name": name}
        if level is not None:
            p["level_m"] = level
        land.append((p, geom))


def Bd(geom, floors, use, name="", h=None, form=None):
    p = {"floors": int(floors), "use": use}
    if form:
        p["form"] = form
    if name:
        p["name"] = name
    if h:
        p["height_m"] = h
    bldg.append((p, geom))


def M(net, geom, name="", shaded=None, width=None):
    p = {"network": net, "name": name}
    if shaded is not None:
        p["shaded"] = shaded
    if width:
        p["width_m"] = width
    move.append((p, geom))


# ---- program of the 7 x 6 superblocks: (i, j) -> kind
K = {}
for i in range(NI):
    for j in range(NJ):
        K[(i, j)] = "housing"
for j in range(NJ):
    K[(0, j)] = "orchard_edge"
K[(0, 0)] = "arrival"
K[(0, 5)] = "water"
K[(2, 2)] = "civic"
K[(2, 3)] = "plaza"
K[(3, 2)] = "market"
K[(5, 0)] = "workshops"
K[(6, 0)] = "industry"
K[(6, 1)] = "industry"
for j in (2, 3, 4, 5):
    K[(6, j)] = "bluff_park"
K[(4, 5)] = "sports"
NODE_HOUSING = (4, 4)

STREET = 20.0      # superblock edge streets (machine or shared), full width
LANE = 10.0        # people-only lanes inside a superblock
DEPTH = 11.0       # depth of the courtyard bars


def blocks_of(i, j):
    """3 x 3 blocks inside superblock (i, j), separated by lanes; returns {(a, b): box}."""
    bx0, by0 = X0 + i * S + STREET / 2, Y0 + j * S + STREET / 2
    w = (S - STREET - 2 * LANE) / 3.0
    out = {}
    for a in range(3):
        for b in range(3):
            xa = bx0 + a * (w + LANE)
            yb = by0 + b * (w + LANE)
            out[(a, b)] = box(xa, yb, xa + w, yb + w)
    return out


def courtyard(blk, floors_fn, use, name, gap=6.0, pieces=3, arcade_side=None):
    """Perimeter courtyard block: four bars, each cut into pieces with passages; floors per piece."""
    bx0, by0, bx1, by1 = blk.bounds
    d = DEPTH
    sides = [("s", box(bx0, by0, bx1, by0 + d)), ("n", box(bx0, by1 - d, bx1, by1)),
             ("w", box(bx0, by0 + d, bx0 + d, by1 - d)), ("e", box(bx1 - d, by0 + d, bx1, by1 - d))]
    for side, bar in sides:
        sx0, sy0, sx1, sy1 = bar.bounds
        horiz = side in ("s", "n")
        length = (sx1 - sx0) if horiz else (sy1 - sy0)
        n = pieces if horiz else max(1, pieces - 1)
        seg = (length - gap * (n - 1)) / n
        for k in range(n):
            a = k * (seg + gap)
            piece = box(sx0 + a, sy0, sx0 + a + seg, sy1) if horiz else box(sx0, sy0 + a, sx1, sy0 + a + seg)
            Bd(piece, floors_fn(side, k), use, name)


def rows(blk, use, name, floors=2, depth=9.0, garden=12.0, seg=28.0, gap=4.0):
    """East-west rows of family houses with private gardens to the south (casa-patio rows)."""
    bx0, by0, bx1, by1 = blk.bounds
    y = by0 + 2
    while y + depth <= by1 - 1:
        x = bx0
        while x + 8 <= bx1:
            x2 = min(x + seg, bx1)
            Bd(box(x, y, x2, y + depth), floors + (1 if RND.random() < 0.15 else 0), use, name)
            x = x2 + gap
        y += depth + garden


def bars(blk, use, name, floors=4, depth=12.0):
    """Two north-south bars with a shared shaded court between them; short ends broken for air."""
    bx0, by0, bx1, by1 = blk.bounds
    for xa in (bx0, bx1 - depth):
        Bd(box(xa, by0 + 4, xa + depth, by0 + (by1 - by0) / 2 - 3), floors, use, name)
        Bd(box(xa, by0 + (by1 - by0) / 2 + 3, xa + depth, by1 - 4), floors - (1 if RND.random() < 0.4 else 0), use, name)


def typology(i, j):
    """Urban near the avenue and the centre, lower towards the edges of the city."""
    if j == 3 or i == 3:
        return "court_urban"
    if i in (1, 5) or j in (0, 5):
        return "rows" if (i + j) % 2 == 0 else "court"
    return "bars" if (i + j) % 2 == 1 else "court"


def court_floors(base):
    def f(side, k):
        r = RND.random()
        return base + (1 if r < 0.30 else 0) + (1 if (side in ("s", "n") and k == 0 and r < 0.6) else 0)
    return f


# ---- superblock by superblock
for (i, j), kind in sorted(K.items()):
    S_ = sb(i, j)
    B = blocks_of(i, j)
    if kind == "housing":
        avenue = (j == 3 or i == 3)               # blocks on the two main streets carry shops and an extra floor
        for (a, b), blk in B.items():
            if (a, b) == (1, 1):
                L("open_space", blk, "Patio garden (shade grove, cistern, play)")
                if (i, j) == NODE_HOUSING:
                    Bd(box(blk.centroid.x - 14, blk.centroid.y - 14, blk.centroid.x + 14, blk.centroid.y + 14), 1, "open_space",
                       "Patio pergola (PV)", h=5, form="canopy")
                continue
            if (a, b) == (2, 0) and (i + j) % 2 == 0:
                L("civic", blk, "Kindergarten and health post")
                bx0, by0, bx1, by1 = blk.bounds
                Bd(box(bx0 + 6, by0 + 6, bx1 - 6, by0 + 26), 1, "civic", "Kindergarten", h=5)
                Bd(box(bx0 + 6, by1 - 24, bx0 + 40, by1 - 6), 2, "civic", "Health post")
                continue
            if (a, b) == (0, 2) and (i + j) % 3 == 0:
                L("mixed_use", blk, "Workshop block (makers, repair, robot depot)")
                courtyard(blk, lambda s, k: 2, "mixed_use", "Workshops and studios", pieces=2)
                continue
            ty = typology(i, j)
            use = "mixed_use" if (avenue and (a, b) in ((0, 0), (1, 0), (2, 0), (0, 2), (1, 2), (2, 2))) else "residential"
            if ty == "rows" and use == "residential":
                L(use, blk, "Family row houses with gardens")
                rows(blk, use, "Row houses")
            elif ty == "bars" and use == "residential":
                L(use, blk, "Shaded-court flats")
                bars(blk, use, "Flats around a shaded court", floors=4)
            else:
                L(use, blk, "Courtyard housing" if use == "residential" else "Courtyard housing over shops")
                courtyard(blk, court_floors((3 if use == "mixed_use" else 2) + (1 if ty == "court_urban" else 0)), use,
                          "Courtyard houses" if use == "residential" else "Arcade houses over shops")
    elif kind == "orchard_edge":
        L("agriculture", S_, "Orchard edge: olive, pistachio and vine on reclaimed water")
    elif kind == "arrival":
        L("civic", S_, "Arrival square and mobility hub")
    elif kind == "water":
        L("infrastructure", S_, "Water reclamation and store")
    elif kind == "civic":
        L("civic", S_, "Civic quarter: town hall and open-data office, library, clinic")
    elif kind == "plaza":
        L("open_space", S_, "Plaza del Agua - main square (paved)")
    elif kind == "market":
        L("civic", S_, "Market hall and school")
    elif kind == "workshops":
        L("industry", S_, "Workshops: PV and robot maintenance, fabrication")
    elif kind == "industry":
        L("industry" if j == 0 else "logistics", S_, "Agri-processing" if j == 0 else "Freight cross-dock and fleet depot")
    elif kind == "bluff_park":
        L("open_space", S_, "Bluff park - foot of the escarpment")
    elif kind == "sports":
        L("open_space", S_, "Sports grounds under shade")

# ---- the arrival hub (C01), superblock (0, 0)
hx0, hy0 = X0, Y0
Bd(box(hx0 + 40, hy0 + 150, hx0 + 160, hy0 + 178), 2, "civic", "Arrival hall and visitor centre", h=11)
Bd(box(hx0 + 14, hy0 + 40, hx0 + 120, hy0 + 64), 1, "infrastructure", "Coach and shuttle canopy (PV)", h=7, form="canopy")
Bd(box(hx0 + 180, hy0 + 40, hx0 + 286, hy0 + 110), 1, "civic", "Market hall of the fields", h=10)
Bd(box(hx0 + 196, hy0 + 150, hx0 + 286, hy0 + 286), 3, "mixed_use", "Guesthouse over shops")
Bd(box(hx0 + 40, hy0 + 200, hx0 + 160, hy0 + 286), 3, "mixed_use", "Arrival block: offices over shops")
Bd(box(hx0 + 14, hy0 + 76, hx0 + 70, hy0 + 132), 1, "infrastructure", "Bike, robot and drone dock", h=6)
L("open_space", box(hx0 + 30, hy0 + 112, hx0 + 180, hy0 + 148), "Arrival square (shaded)")
Bd(box(hx0 + 60, hy0 + 118, hx0 + 160, hy0 + 142), 1, "open_space", "Arrival square canopy (PV)", h=6, form="canopy")
# ---- civic quarter, superblock (2, 2)
cx0, cy0 = X0 + 2 * S, Y0 + 2 * S
Bd(box(cx0 + 20, cy0 + 236, cx0 + 140, cy0 + 280), 3, "civic", "Town hall and open-data office")
Bd(box(cx0 + 160, cy0 + 236, cx0 + 280, cy0 + 280), 3, "civic", "Library and media school")
Bd(box(cx0 + 20, cy0 + 20, cx0 + 120, cy0 + 90), 2, "civic", "Clinic")
Bd(box(cx0 + 140, cy0 + 20, cx0 + 280, cy0 + 60), 2, "civic", "Training college (robotics, agronomy, water)")
Bd(box(cx0 + 200, cy0 + 90, cx0 + 280, cy0 + 200), 3, "mixed_use", "Civic quarter housing over shops")
L("open_space", box(cx0 + 20, cy0 + 110, cx0 + 180, cy0 + 220), "Civic garden")
# ---- market and school, superblock (3, 2)
mx0, my0 = X0 + 3 * S, Y0 + 2 * S
Bd(box(mx0 + 20, my0 + 200, mx0 + 160, my0 + 280), 1, "civic", "Covered market", h=10)
Bd(box(mx0 + 180, my0 + 230, mx0 + 280, my0 + 280), 3, "mixed_use", "Market housing over shops")
Bd(box(mx0 + 20, my0 + 20, mx0 + 150, my0 + 44), 2, "civic", "School - classrooms (south)")
Bd(box(mx0 + 20, my0 + 44, mx0 + 44, my0 + 150), 2, "civic", "School - classrooms (west)")
Bd(box(mx0 + 170, my0 + 20, mx0 + 280, my0 + 90), 1, "civic", "School hall and canteen", h=8)
L("open_space", box(mx0 + 60, my0 + 60, mx0 + 160, my0 + 180), "School yard (shaded)")
# ---- Plaza del Agua (A03), superblock (2, 3)
px0, py0 = X0 + 2 * S, Y0 + 3 * S
Bd(box(px0 + 12, py0 + 20, px0 + 30, py0 + 280), 3, "civic",
   "Wind gallery: arcaded hall on the windward side (culture, assembly)", h=13)
Bd(box(px0 + 60, py0 + 236, px0 + 290, py0 + 280), 4, "mixed_use", "North arcade: shops, cafes, homes above")
Bd(box(px0 + 236, py0 + 20, px0 + 288, py0 + 120), 2, "civic", "Cultural hall", h=11)
Bd(box(px0 + 60, py0 + 80, px0 + 210, py0 + 190), 1, "open_space", "Plaza canopy (PV, 9 m)", h=9, form="canopy")
L("open_space", box(px0 + 110, py0 + 115, px0 + 160, py0 + 155), "Sunken court (-3 m, Zonda refuge, under the canopy)",
  level=-3)
L("open_space", box(px0 + 36, py0 + 24, px0 + 84, py0 + 228), "Shade grove behind the wind gallery")
L("open_space", box(px0 + 84, py0 + 196, px0 + 232, py0 + 228), "Shade grove along the north arcade")
L("open_space", box(px0 + 214, py0 + 130, px0 + 232, py0 + 196), "Water table (acequia basin, paved edges)")
# ---- workshops (5, 0), industry (6, 0), logistics (6, 1)
wx0, wy0 = X0 + 5 * S, Y0
for k, (a, b, c, d) in enumerate([(20, 20, 140, 90), (160, 20, 280, 90), (20, 120, 140, 200), (160, 120, 280, 200),
                                  (20, 220, 280, 280)]):
    Bd(box(wx0 + a, wy0 + b, wx0 + c, wy0 + d), 1, "industry",
       ["PV and robot maintenance", "Fabrication workshop", "Battery and electronics repair",
        "Makers' hall", "Workshop row"][k], h=9)
ix0, iy0 = X0 + 6 * S, Y0
Bd(box(ix0 + 20, iy0 + 20, ix0 + 200, iy0 + 110), 1, "industry", "Agri-processing (olive, pistachio, jojoba)", h=10)
Bd(box(ix0 + 20, iy0 + 150, ix0 + 140, iy0 + 270), 1, "industry", "Cold store and packing", h=9)
Bd(box(ix0 + 20, iy0 + S + 40, ix0 + 220, iy0 + S + 120), 1, "logistics", "Freight cross-dock", h=10)
Bd(box(ix0 + 20, iy0 + S + 160, ix0 + 220, iy0 + S + 230), 1, "logistics", "Autonomous fleet depot and charging", h=8)
# ---- water (0, 5)
ox0, oy0 = X0, Y0 + 5 * S
Bd(box(ox0 + 30, oy0 + 40, ox0 + 150, oy0 + 100), 1, "infrastructure", "Membrane bioreactor (wastewater)", h=8)
Bd(box(ox0 + 180, oy0 + 40, ox0 + 270, oy0 + 130), 1, "infrastructure", "Reclaimed water store (covered)", h=7)
Bd(box(ox0 + 30, oy0 + 150, ox0 + 140, oy0 + 200), 1, "infrastructure", "Pumping and control", h=6)
# ---- sports (4, 5)
sx0, sy0 = X0 + 4 * S, Y0 + 5 * S
Bd(box(sx0 + 30, sy0 + 30, sx0 + 270, sy0 + 50), 1, "open_space", "Grandstand canopy", h=7, form="canopy")
Bd(box(sx0 + 30, sy0 + 220, sx0 + 140, sy0 + 270), 2, "civic", "Sports hall", h=12)

# ---- the edge with the pilot area: alameda windbreak strip and orchards
EDGE = box(572190, 6549000, X0, 6550780).difference(LEAD.buffer(15))
L("open_space", EDGE, "Alameda: poplar windbreak and arrival walk along the first fields")
L("agriculture", box(571500, 6547700, 572700, 6549000).difference(LEAD.buffer(15)),
  "Orchards between the fields and the arrival road")
L("agriculture", box(572400, 6548000, 574500, Y0 - 12).difference(LEAD.buffer(15)),
  "Arrival orchards: olive and pistachio south of the city")
# ---- the bluff, upper terrace: tank, PV, compute
TANK = box(575400, 6550260, 575520, 6550440)
Bd(TANK, 1, "infrastructure", "Bluff tank: covered head reservoir, 60,000 m3 (feeds the acequias by gravity)", h=8)
L("infrastructure", TANK.buffer(40, cap_style=3), "Bluff tank")
CAMPUS = box(576550, 6549650, 577450, 6550350)
L("compute", CAMPUS, "Compute campus (terrace)")
for k in range(2):
    Bd(box(576650, 6549720 + k * 300, 576830, 6549790 + k * 300), 2, "compute", "Data hall %d (20 MW IT)" % (k + 1), h=15)
    Bd(box(576850, 6549720 + k * 300, 576930, 6549790 + k * 300), 1, "compute", "Dry-cooler deck %d" % (k + 1), h=7)
Bd(box(577000, 6549700, 577120, 6549800), 1, "infrastructure", "Substation 33 kV", h=9)
Bd(box(577150, 6549700, 577380, 6549725), 1, "infrastructure", "Battery hall A (500 MWh)", h=6)
Bd(box(577150, 6549760, 577380, 6549785), 1, "infrastructure", "Battery hall B (500 MWh)", h=6)
Bd(box(577000, 6550150, 577160, 6550220), 2, "civic", "Operations and training centre")
Bd(box(576700, 6550200, 576900, 6550290), 1, "infrastructure", "Heat plant: waste heat to the greenhouses and the city's hot water", h=9)
GREEN = box(575200, 6549500, 575700, 6549950)
L("agriculture", GREEN, "Greenhouses heated by the campus")
for k in range(4):
    Bd(box(575230, 6549520 + k * 105, 575670, 6549600 + k * 105), 1, "agriculture", "Greenhouse %d" % (k + 1), h=6)
PVLAND = box(575000, 6549300, 578600, 6552300).intersection(MASTER).difference(CAMPUS.buffer(60)) \
    .difference(GREEN.buffer(40)).difference(TANK.buffer(80)).difference(MOUNTAIN.buffer(40)).difference(FLOOD)
PVLAND = clean(PVLAND, 2e5)
L("energy", PVLAND, "PV fields on the upper terrace (single-axis trackers)")
# ---- north slope and north terrace, river park, hills
NSLOPE = box(572600, YN, 574600, 6552500).difference(FLOOD.buffer(30))
L("open_space", NSLOPE, "North slope park: tree belt against the north-west wind, paths, terraces")
NTER = box(572900, 6552500, 574900, 6554300).difference(FLOOD.buffer(30)).difference(MOUNTAIN)
L("agriculture", clean(NTER, 1e5), "North terrace: jojoba and algarrobo on establishment water; the upper town in phase two")
RIVER = FLOOD.intersection(MASTER).buffer(30).intersection(MASTER)
L("reserve", RIVER, "Seasonal river park: the flood corridor, never built")
taken = unary_union([g for p, g in land])
L("reserve", clean(MASTER.difference(taken), 2e4), "Bluff, hills and open desert (kept)")

# ---------------------------------------------------------------- movement
# machine grid every 600 m, shared acequia streets on the 300 m lines, people-only lanes inside superblocks
MX = [X0, X0 + 2 * S, X0 + 4 * S, X0 + 6 * S]
MY = [Y0, Y0 + 2 * S, Y0 + 4 * S, YN]
for x in MX:
    M("machine", LineString([(x, Y0), (x, YN)]), "Machine street (freight, shuttles, service), x=%d" % (x - X0), width=12)
for y in MY:
    M("machine", LineString([(X0, y), (XE, y)]), "Machine street (freight, shuttles, service), y=%d" % (y - Y0), width=12)
for i in (1, 3, 5):
    x = X0 + i * S
    M("shared", LineString([(x, Y0), (x, YN)]), "Acequia street (people, bikes, robots at walking pace)",
      shaded=True, width=20)
for j in (1, 3, 5):
    y = Y0 + j * S
    nm = "Avenida del Agua: main acequia from the bluff tank to the orchards" if j == 3 else \
        "Acequia street (people, bikes, robots at walking pace)"
    M("shared", LineString([(X0, y), (XE, y)]), nm, shaded=True, width=34 if j == 3 else 20)
# lanes: people only, inside each built superblock, stopping short of the superblock edge streets
for (i, j), kind in K.items():
    if kind in ("housing", "civic", "market", "plaza"):
        bx0, by0 = X0 + i * S, Y0 + j * S
        w = (S - STREET - 2 * LANE) / 3.0
        for t in (1, 2):
            off = STREET / 2 + t * w + (t - 0.5) * LANE
            M("people", LineString([(bx0 + off, by0 + 12), (bx0 + off, by0 + S - 12)]), "Shaded lane", shaded=True, width=LANE)
            M("people", LineString([(bx0 + 12, by0 + off), (bx0 + S - 12, by0 + off)]), "Shaded lane", shaded=True, width=LANE)
# the alameda walk along the first fields, and the stairs and path up the bluff
M("people", LineString([(572300, 6547300), (572300, 6550760)]), "Alameda walk along the first fields", shaded=True, width=6)
M("people", LineString([(XE, Y0 + 3 * S), (575000, Y0 + 3 * S), (575380, Y0 + 3 * S)]),
  "Bluff stairs and ramp to the tank lookout", shaded=False, width=6)
M("people", LineString([(573000, YN), (573300, 6551900), (573800, 6552400), (574400, 6552450)]),
  "North slope path", shaded=False, width=4)
M("people", LineString([(572600, YN - 20), (572450, 6551700), (571900, 6552400), (571700, 6553500)]),
  "River park path", shaded=False, width=4)
# arrival road from the south-west boundary towards RN 20: between field 1 and the boundary, then up the edge
ls = LineString([(569114, 6544869), (572125, 6547041)])
bs = LineString([(569042, 6544740), (572288, 6547147)])
mid = [((ls.interpolate(t, normalized=True).x + bs.interpolate(t, normalized=True).x) / 2,
        (ls.interpolate(t, normalized=True).y + bs.interpolate(t, normalized=True).y) / 2) for t in (0.03, 0.5, 1.0)]
ARR = LineString(mid + [(572230, 6547700), (572270, 6548400), (572280, 6549000), (572300, 6549450), (X0, Y0)])
M("machine", ARR, "Arrival road: from the south-west gate towards RN 20 (40.7 km beyond the site) along the first fields",
  width=14)
M("machine", LineString([(XE, Y0), (574800, Y0), (575100, 6549520), (576550, 6549600), (577000, 6549650)]),
  "Service road up the bluff: greenhouses, campus", width=10)
M("machine", LineString([(XE, Y0 + 2 * S), (575150, 6550000), (575400, 6550250)]), "Tank access ramp", width=6)
M("machine", LineString([(575700, 6549560), (575700, 6551900)]), "PV maintenance track", width=6)
M("machine", LineString([(576550, 6550000), (578400, 6550000)]), "PV maintenance track", width=6)

# ---------------------------------------------------------------- interfaces: machine x people/shared
mach = unary_union([g for p, g in move if p["network"] == "machine"])
walk = [g for p, g in move if p["network"] in ("people", "shared")]
pts = []
for w in walk:
    x = mach.intersection(w)
    for q in getattr(x, "geoms", [x]):
        if q.geom_type == "Point" and not any(q.distance(o) < 8 for o in pts):
            pts.append(q)
# shuttle stops on the machine grid count too (M6)
for q in [Point(X0 + 2 * S, Y0 + 3 * S + 40), Point(X0 + 4 * S, Y0 + 3 * S + 40), Point(X0 + 40, Y0)]:
    pts.append(q)
inter = [({"kind": "interface", "name": ("Raised table crossing %d" % (k + 1)) if k < len(pts) - 3 else
          "Driverless shuttle stop %d" % (k - len(pts) + 4)}, q) for k, q in enumerate(pts)]

# ---------------------------------------------------------------- checks on the design itself
dropped = []
for p, g in list(bldg):
    if g.intersects(LEAD) or g.intersects(FLOOD) or not MASTER.contains(g):
        dropped.append(p.get("name"))
        bldg.remove((p, g))
if dropped:
    print("dropped buildings (pilot area, flood band or outside the master area):", dropped[:5], len(dropped))
for p, g in move:
    if g.intersects(LEAD.buffer(-1)):
        print("WARNING route enters the pilot area:", p["name"])

# ================================================================ scale 1: the whole site
def rect_ll(lon, lat, w, h):
    c = U(lon, lat)
    return box(c[0] - w / 2, c[1] - h / 2, c[0] + w / 2, c[1] + h / 2)


OASES = [("Oasis 1 - Terrace (this master design; upper town in phase two)",
          box(572100, 6549300, 575000, 6554300)),
         ("Oasis 2 - North-west plain", rect_ll(*IND["living"]["points_lonlat"][2], 3200, 3600)),
         ("Oasis 3 - North-centre", rect_ll(*IND["living"]["points_lonlat"][1], 3400, 3000)),
         ("Oasis 4 - East wing, beside the port", rect_ll(*IND["living"]["points_lonlat"][3], 3000, 2800))]
reserve_base = unary_union([MOUNTAIN, FLOOD])
living = unary_union([g for _, g in OASES]).intersection(SITE).difference(FLOOD).difference(MOUNTAIN).difference(LEAD)
# the Line: one corridor for power, water, data and autonomous freight, linking the oases, the campuses and the port
P1 = U(*IND["living"]["points_lonlat"][2]); P2 = U(*IND["living"]["points_lonlat"][1])
P3 = U(*IND["living"]["points_lonlat"][3]); PORT = U(*IND["port"]["points_lonlat"][0])
C1 = U(*IND["compute"]["points_lonlat"][0]); C2 = U(*IND["compute"]["points_lonlat"][1])
LINE = LineString([(572300, 6549450), (571300, 6553000), (570300, 6556000), (570100, 6560500), (P1[0], P1[1] - 1900),
                   (P1[0] + 2600, P1[1] + 3000), (C1[0], C1[1]), (P2[0] - 1800, P2[1]), (P2[0] + 3000, P2[1] - 2500),
                   (P3[0] - 1700, P3[1] + 1000), (P3[0] + 1600, P3[1] - 1500), (PORT[0], PORT[1] + 900),
                   (627800, 6557600)])
LINE_C = LINE.buffer(150).intersection(SITE)
gateway = rect_ll(*IND["industry"]["points_lonlat"][0], 2600, 2000)
port = rect_ll(*IND["port"]["points_lonlat"][0], 2400, 2200).difference(gateway)
settle_ind = unary_union([box(574500, 6549300, 575000, 6549900)] +
                         [Point(*U(*IND["living"]["points_lonlat"][k])).buffer(1, cap_style=3).buffer(0)
                          for k in ()] +
                         [rect_ll(IND["living"]["points_lonlat"][k][0] + 0.022, IND["living"]["points_lonlat"][k][1],
                                  1200, 1400) for k in (2, 1, 3)])
industry = unary_union([gateway, settle_ind, LINE_C]).intersection(SITE).difference(reserve_base.difference(LINE_C)) \
    .difference(living).difference(LEAD)
port = port.intersection(SITE).difference(reserve_base).difference(industry)
camp = unary_union([Point(*C1).buffer(1, cap_style=3).buffer(1800, cap_style=3, join_style=2),
                    Point(*C2).buffer(1, cap_style=3).buffer(1800, cap_style=3, join_style=2)])
pv_fans = FAN.intersection(unary_union([box(574800, 6548500, 590000, 6556000),
                                        Point(*C1).buffer(9000), Point(*C2).buffer(9000)]))
energy = unary_union([camp, pv_fans, PVLAND, CAMPUS]).intersection(SITE).difference(reserve_base) \
    .difference(living).difference(industry).difference(port).difference(LEAD)
taken = unary_union([reserve_base, living, industry, port, energy])
agri = unary_union([FLAT.difference(taken), LEAD]).intersection(SITE)
reserve = SITE.difference(unary_union([living, industry, port, energy, agri]))
structure = []
for sysname, g, nm in [("living", living, "Four oasis cities on the Line (long term)"),
                       ("industry", industry, "The Line (power, water, data, autonomous freight), settlement and gateway industry"),
                       ("port", port, "Port of entry and free-trade yards (east wing)"),
                       ("energy_compute", energy, "PV on the fans, compute campuses"),
                       ("agri_production", agri, "Agrivoltaics and irrigated fields on the flats, including the pilot area"),
                       ("reserve", reserve, "Pie de Palo, the washes as river parks, steep ground and open desert")]:
    g = clean(g, 3e4)
    if not g.is_empty:
        structure.append(({"system": sysname, "name": nm}, g.simplify(20)))

# ---------------------------------------------------------------- phasing
road_c = ARR.buffer(40)
ph1 = clean(unary_union([box(571500, 6547700, 578600, 6552500).intersection(MASTER), road_c]).intersection(SITE)
            .difference(LEAD), 1e4)
ph2_parts = [box(572100, 6552500, 575000, 6554300), OASES[1][1].buffer(1500),
             LINE.intersection(box(560000, 6549000, 600000, 6600000)).buffer(400),
             Point(*C1).buffer(2500)]
ph2 = clean(unary_union(ph2_parts).intersection(SITE).difference(ph1).difference(MOUNTAIN).difference(LEAD), 1e5)
ph3 = clean(unary_union([OASES[2][1].buffer(1500), OASES[3][1].buffer(1500), gateway.buffer(1500), port.buffer(1500),
                         LINE.buffer(400), Point(*C2).buffer(2500)]).intersection(SITE)
            .difference(ph1).difference(ph2).difference(MOUNTAIN).difference(LEAD), 1e5)
phasing = [
    ({"phase": 1, "name": "Terrace Oasis: the first city, its fields, PV and campus, and the arrival road"}, ph1.simplify(10)),
    ({"phase": 2, "name": "Upper town on the north terrace; the Line north to Oasis 2; second campus",
      "trigger": "Lower terrace above 85% occupied for 12 consecutive months AND wellfield drawdown below 0.5 m a year for "
                 "24 months AND a second abstraction licence granted AND the open-data office has published 24 monthly "
                 "water and power accounts"}, ph2.simplify(25)),
    ({"phase": 3, "name": "East: Oasis 3 and 4, port of entry, gateway industry, the Line to RP 510",
      "trigger": "Access corridor to RP 510 financed AND committed export throughput above 40,000 t a year AND phase-two "
                 "population above 40,000"}, ph3.simplify(25)),
]

# ---------------------------------------------------------------- nodes
hb = sb(*NODE_HOUSING)
nodes = [
    ({"node_id": "C01", "name": "Arriving along the first fields",
      "why": "Everyone arrives the same way: 3.5 km beside the agrivoltaic fields the city grew out of, then under one "
             "canopy where the coach stops and the city begins on foot. If arrival is a car park, the city has lied "
             "about what it is.",
      "eye_from": LL(572500, 6549468), "eye_to": LL(572512, 6549640),
      "aerial_from": LL(571200, 6547400),
      "section": [LL(572250, 6549505), LL(572700, 6549505)],
      "section_b": [LL(572500, 6549440), LL(572500, 6549760)],
      "day": [
          {"time": "05:30", "people": "Field crews for the PV and jojoba shifts meet under the canopy; the arrival hall "
                                      "opens its cafe.",
           "machines": "Panel-cleaning robots finish their night pass on the trackers; the first driverless coach leaves "
                       "for San Juan."},
          {"time": "07:30", "people": "People from San Juan and the valley step off the coach and walk in on foot; "
                                      "children cycle along the alameda to school.",
           "machines": "Coaches and shuttles stop under the canopy; freight stays on the machine street to the cross-dock."},
          {"time": "11:00", "people": "Visitors start at the arrival hall: the model of the city, guides, bikes for hire.",
           "machines": "Delivery robots take luggage to the guesthouse; the dock rebalances bicycles and charges drones."},
          {"time": "15:00", "people": "The hottest hours: people wait under the canopy and in the hall, and walk in "
                                      "the shade of the poplars.",
           "machines": "The canopy's PV runs at its peak and charges the hub's batteries; fewer coaches run."},
          {"time": "19:00", "people": "The market hall sells the fields' oil, nuts and vegetables; families meet "
                                      "arriving relatives on the square.",
           "machines": "Robots bring crates from the agri-processing yard to the stalls along the shared street."},
          {"time": "22:00", "people": "The last coach; the square is lit low and warm, and the sky over the fields "
                                      "is kept dark.",
           "machines": "Freight moves only on the machine street; drones land at the dock for the night."}],
      "render_note": "Arrival by driverless electric coach on a straight road between the agrivoltaic fields (single-axis "
                     "solar trackers over jojoba, rosemary and grazing alpacas) and a double row of tall Lombardy poplars "
                     "with olive orchards; ahead, a long solar canopy over the coach stop, a two-storey arrival hall of "
                     "rammed earth and timber, a market hall, people walking into the city with luggage and bicycles."},
     box(571900, 6548300, 572700, 6549760).difference(LEAD.buffer(15))),
    ({"node_id": "A01", "name": "A superblock of courtyard houses",
      "why": "Housing is where heat, earthquakes, water and robots meet every day. If a family can live here in January "
             "and in a Zonda week without a car or an air-conditioner running all day, the rest of the city follows.",
      "eye_from": LL(hb.bounds[0] + 101.7, hb.bounds[1] + 30), "eye_to": LL(hb.bounds[0] + 101.7, hb.bounds[1] + 200),
      "section": [LL(hb.bounds[0] - 10, hb.bounds[1] + 185), LL(hb.bounds[0] + 310, hb.bounds[1] + 185)],
      "section_b": [LL(hb.bounds[0] + 150, hb.bounds[1] + 310), LL(hb.bounds[0] + 150, hb.bounds[1] - 10)],
      "day": [
          {"time": "06:00", "people": "Windows open to let the night air through the courts; the first walks and "
                                      "the bakery on the corner.",
           "machines": "The night's deliveries wait at the drop point on the acequia street; no machine enters a lane."},
          {"time": "08:00", "people": "Children walk in groups down the lanes to the kindergarten and the school.",
           "machines": "Machines on the nearby machine streets are held at the crossings at school time."},
          {"time": "13:00", "people": "Shutters closed, lunch and siesta indoors; the bottom of each court stays in "
                                      "shade.",
           "machines": "Roof PV pergolas run at their peak and charge the block's batteries; robots wait in the shade."},
          {"time": "17:00", "people": "People who work from home come out to the patio garden; neighbours share "
                                      "tools and food.",
           "machines": "Delivery robots bring parcels and groceries from the drop point to the doors at walking pace."},
          {"time": "20:00", "people": "The patio garden is the cool place at dusk: play, dinners outside, the "
                                      "acequia running.",
           "machines": "The block's water is metered and the next day's channel flow is scheduled from it."},
          {"time": "Zonda", "people": "On a Zonda day families stay in the courts and the lanes, out of the "
                                      "north-west wind.",
           "machines": "Air intakes switch to filtered mode; panel cleaning is booked for the day after."}],
      "render_note": "Low courtyard houses two and three storeys high with thick walls in lime-washed render and rammed "
                     "earth in warm whites and pale ochres, deep window reveals with timber shutters and lattice screens, "
                     "roof terraces with solar panels and pergolas; shaded paved lanes with algarrobo and mulberry trees "
                     "and a narrow open irrigation channel; children playing, neighbours at their doors, a small white "
                     "delivery robot."},
     hb),
    ({"node_id": "A03", "name": "Plaza del Agua: a square for 45 degrees and the Zonda",
      "why": "A desert city needs one room where everyone can be outside at once. Here it has to work at 45 C and in a "
             "hot north-west wind, with water that is never wasted.",
      "eye_from": LL(X0 + 2 * S + 205, Y0 + 3 * S + 55), "eye_to": LL(X0 + 2 * S + 70, Y0 + 3 * S + 170),
      "section": [LL(X0 + 2 * S - 10, Y0 + 3 * S + 125), LL(X0 + 2 * S + 310, Y0 + 3 * S + 125)],
      "section_b": [LL(X0 + 2 * S + 135, Y0 + 3 * S + 310), LL(X0 + 2 * S + 135, Y0 + 3 * S - 10)],
      "day": [
          {"time": "07:00", "people": "The market sets up under the canopy; older people walk the square before the "
                                      "heat.",
           "machines": "Robots bring produce from the cross-dock to the stalls; the acequia gate opens for the morning."},
          {"time": "10:00", "people": "Classes and assemblies in the wind gallery; cafes fill along the north arcade.",
           "machines": "The canopy's PV feeds the arcade and the cultural hall."},
          {"time": "14:00", "people": "At 45 C people sit under the canopy and in the grove; the sunken court is the "
                                      "coolest floor in the city.",
           "machines": "Water reaches the trees by drip at night, not now: only the basin runs, slowly."},
          {"time": "19:00", "people": "The square is full: families, music, the market's second shift.",
           "machines": "Shuttles stop on the machine street at the north-west corner; robots keep to the shared streets."},
          {"time": "23:00", "people": "Lights low under the canopy; the last cafes close.",
           "machines": "Cleaning robots sweep the square; the channel is flushed to the orchards."},
          {"time": "Zonda", "people": "In a Zonda people go down into the sunken court or behind the gallery; the "
                                      "market moves inside.",
           "machines": "Stall awnings are stowed; the basin is drained to keep dust out of the water."}],
      "render_note": "A large public square under a light steel solar canopy 9 m high casting dappled shade, a sunken "
                     "court with stone steps and benches, a shallow stone water channel and basin, groves of algarrobo "
                     "trees, a long arcaded three-storey hall on the west side acting as a wind wall, four-storey "
                     "arcades with cafes along the north side; market stalls, families, older people on benches, "
                     "people with bicycles."},
     sb(2, 3)),
]


# ---------------------------------------------------------------- write
def polyonly(g):
    """Keep only polygon parts (clipping leaves line and point slivers in a GeometryCollection)."""
    if g.geom_type in ("Polygon", "MultiPolygon"):
        return g
    ps = []
    for q in getattr(g, "geoms", []):
        if q.geom_type == "Polygon":
            ps.append(q)
        elif q.geom_type == "MultiPolygon":
            ps.extend(q.geoms)
    return unary_union(ps)


def fc(name, feats):
    out = []
    for p, g in feats:
        if name not in ("movement",):
            g = polyonly(g)
            if g.is_empty:
                continue
        if name != "movement":
            g = polyonly(make_valid(g)).buffer(0)
        gl = xc.to_lonlat(g)
        if name != "movement":
            gl = polyonly(make_valid(gl))
        try:
            gl = shapely.set_precision(gl, 1e-7)
        except shapely.errors.GEOSException:
            gl = shapely.set_precision(gl.buffer(0), 1e-7)
        if name != "movement" and (not gl.is_valid or gl.geom_type not in ("Polygon", "MultiPolygon")):
            gl = polyonly(make_valid(gl))
        out.append({"type": "Feature", "properties": p, "geometry": json.loads(json.dumps(mapping(gl)))})
    s = json.dumps({"type": "FeatureCollection", "name": name, "features": out}, ensure_ascii=False)
    s = re.sub(r"(-?\d+\.\d{7})\d+", r"\1", s)
    with open(os.path.join(GEO, name + ".geojson"), "w", encoding="utf-8") as f:
        f.write(s + "\n")


os.makedirs(GEO, exist_ok=True)
fc("structure", structure)
fc("master_area", [({"name": "Terrace Oasis - master design area"}, MASTER)])
fc("land_use", land)
fc("buildings", bldg)
fc("movement", move + inter)
fc("phasing", phasing)
fc("nodes", nodes)
print("structure", {p["system"]: round(g.area / 1e6, 1) for p, g in structure})
print("master %.2f km2, land %d, buildings %d, movement %d (+%d interfaces)" % (MASTER.area / 1e6, len(land),
                                                                                 len(bldg), len(move), len(inter)))
print("phases", [round(g.area / 1e6, 1) for p, g in phasing])
print("arrival road inside site km", round(ARR.intersection(SITE).length / 1000, 2),
      "crosses pilot area:", ARR.intersection(LEAD.buffer(-1)).length)
halls = [g for p, g in bldg if p.get("name", "").startswith("Data hall")]
homes = [g for p, g in bldg if p["use"] == "residential"]
print("halls to nearest homes m", round(min(h.distance(f) for h in halls for f in homes)))
print("terrace elevation range m", round(z(X0 + 10, Y0 + 10)), round(z(XE - 10, YN - 10)), "tank", round(z(575460, 6550350)))
