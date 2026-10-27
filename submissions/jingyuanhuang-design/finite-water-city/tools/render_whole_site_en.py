"""English presentation of existing V3 review geometry; never rewrites geometry or node locations."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch as LegendPatch
from matplotlib.font_manager import FontProperties
from shapely.geometry import shape, LineString
from shapely.ops import transform, unary_union, nearest_points
from pyproj import Transformer
P = Path(__file__).resolve().parents[1]
R = P.parents[2]
S = R / 'brief/site-package'
O = P / 'reviews/whole-site-v3'
OUT = O
t = Transformer.from_crs(4326, 32719, always_xy=True).transform

def load(path):
    return [(f['properties'], transform(t, shape(f['geometry']))) for f in json.loads(path.read_text())['features']]

def source(path):
    return unary_union([g for (_, g) in load(S / path)])
scope = source('boundaries/scope_9_13.geojson')
boundary_record=json.loads((S/'boundaries/boundary-revision.json').read_text())
seam_patch=transform(t,shape(boundary_record['open_seam_patch']))
pilot = source('pilot-area/pilot_area.geojson')
living = source('pilot-area/pilot_living_area.geojson')
flood = source('water/flood_sensitive_dem.geojson').intersection(scope)
channels = source('water/channels_dem.geojson').intersection(scope)
zones = [(g, p['system'], p.get('name', '')) for (p, g) in load(O / 'structure.geojson')]
routes = [(g, p) for (p, g) in load(O / 'corridors.geojson')]
C = {p['id']: g for (p, g) in load(O / 'centres.geojson')}
master = unary_union([g for (_, g) in load(O / 'master_study.geojson')])
urban = {str(i): g for (i, (g, k, _)) in enumerate(zones) if k == 'town'}
compute = {str(i): g for (i, (g, k, _)) in enumerate(zones) if k == 'compute'}
gateway = unary_union([g for (g, k, _) in zones if k == 'gateway'])
roads = load(S / 'access/roads_osm.geojson')
rn40 = unary_union([g for (p, g) in roads if '40' in str(p)])
regional = nearest_points(C['A'], rn40)[1]
boundary = nearest_points(C['A'], LineString([C['A'], regional]).intersection(scope.boundary))[1]
qa = json.loads((O / 'qa.json').read_text())
h = (O / 'geometry.sha256').read_text().strip()
font = FontProperties(family='DejaVu Sans')
plt.rcParams['axes.unicode_minus'] = False
BG = '#F8F6F0'
INK = '#263D44'
COL = {'protect': '#C9C9B9', 'wash': '#7B9992', 'floodstudy': '#F0EEE4', 'fixed_agri': '#748951', 'fixed_living': '#A25447', 'town': '#C58B6C', 'compute': '#536E7C', 'gateway': '#AC7884', 'localindustry': '#B49B88', 'energy': '#DFCA84', 'agri': '#B9C69D', 'dry': '#E8E3D7'}

def text(ax, x, y, s, size=12, **kw):
    return ax.text(x, y, s, fontproperties=font, fontsize=size, color=kw.pop('color', INK), **kw)

def polygons(g):
    if g.geom_type == 'Polygon':
        yield g
    elif hasattr(g, 'geoms'):
        for q in g.geoms:
            yield from polygons(q)

def fill(ax, g, color, alpha=1, lw=0, edge=None, hatch=None):
    from matplotlib.path import Path as MPath
    from matplotlib.patches import PathPatch
    from shapely.geometry.polygon import orient
    for q in polygons(g):
        q = orient(q, sign=1)
        vs = []
        codes = []
        for ring in [q.exterior, *q.interiors]:
            a = np.asarray(ring.coords) / 1000
            vs.extend(a)
            codes.extend([MPath.MOVETO] + [MPath.LINETO] * (len(a) - 2) + [MPath.CLOSEPOLY])
        ax.add_patch(PathPatch(MPath(vs, codes), facecolor=color, edgecolor=edge or color, lw=lw, alpha=alpha, hatch=hatch))

def lines(ax, g, c, lw=1, style='-', alpha=1):
    if g.is_empty:
        return
    if g.geom_type in ['LineString', 'LinearRing']:
        a = np.array(g.coords) / 1000
        ax.plot(a[:, 0], a[:, 1], color=c, lw=lw, ls=style, alpha=alpha)
    elif hasattr(g, 'geoms'):
        for q in g.geoms:
            lines(ax, q, c, lw, style, alpha)
    elif g.geom_type == 'Polygon':
        lines(ax, g.boundary, c, lw, style, alpha)

def basemap(ax, mode):
    ax.set_facecolor(BG)
    for (g, k, n) in zones:
        fill(ax, g, COL[k] if mode != 'geometry' else '#D9DDD7' if k == 'protect' else '#F8F6F0', edge='#B6C4BA' if k == 'floodstudy' else '#A0A8A4' if mode == 'geometry' else None, lw=0.25 if mode == 'geometry' else 0, hatch='....' if k == 'floodstudy' else None)
    fill(ax,seam_patch,'#D5D5CB',edge='#85877C',lw=0.3,hatch='///')
    lines(ax, channels, '#7D9B9A', 0.6, alpha=0.7)
    lines(ax, scope.boundary, INK, 1.7)
    lines(ax, pilot.boundary, '#52683B', 1.5)
    lines(ax, living.boundary, '#8C4037', 1.6)
    ax.set(xlim=(559, 634), ylim=(6540, 6610))
    ax.set_aspect('equal')
    ax.axis('off')
    ax.annotate('', xy=(629, 6605), xytext=(629, 6600), arrowprops=dict(arrowstyle='-|>', color=INK, lw=1.4))
    text(ax, 629, 6606, 'Grid N', 10, ha='center')
    ax.plot([563, 573], [6541.5] * 2, color=INK, lw=2)
    ax.plot([563, 568, 573], [6541.5] * 3, '|', color=INK)
    text(ax, 568, 6542.5, '0       5       10 km', 9, ha='center')

def routeplot(ax, mode):
    for (g, p) in routes:
        col = '#B76F40' if p['phase'] == 'P1' else '#496F78'
        lines(ax, g, col, 2.7 if p['phase'] == 'P1' else 1.7, '-' if p['phase'] == 'P1' else '--')
        if mode == 'network':
            lines(ax, g.intersection(flood), '#BA4C42', 3.3)
    for (k, p) in C.items():
        (x, y) = (p.x / 1000, p.y / 1000)
        ax.scatter(x, y, s=60 if k in 'ABCDE' else 40, c=INK, edgecolors=BG, zorder=8)
        text(ax, x + 0.65, y + 0.5, {'A': 'A · Southwest town', 'B': 'B · Northwest settlement', 'C': 'C · Northern service town', 'D': 'D · Eastern service town', 'E': 'E · Eastern gateway', 'K1': 'K1', 'K2': 'K2'}[k], 11, weight='bold', bbox=dict(facecolor=BG, edgecolor='none', pad=1))
    lines(ax, LineString([regional, boundary]), '#AD8E74', 1.1, ':')
    text(ax, 559.5, 6553, 'Western approach toward RN40\nAlignment and rights unverified', 9, ha='left')

def panel(ax, mode):
    ax.axis('off')
    ax.set(xlim=(0, 1), ylim=(0, 1))
    if mode == 'planning':
        text(ax, 0, 0.98, 'One site, phased delivery', 20, va='top')
        text(ax, 0, 0.89, '1,656 km² whole-site framework · V3 review', 12)
        blocks = [('01  Start beside fixed systems', 'Retain fixed fields and living quarter. Secure access,\nmaintenance, water and public services for the southwest.'), ('02  Towns on western low slopes', 'A southwest town; B northwest settlement;\nC northern farm-service town. Productive land separates them.'), ('03  Productive corridors, inhabited places', 'K1/K2 cluster compute, repair and heat use.\nEnergy/production links avoid mountains and channels.'), ('04  Route around the range; defer the gateway', 'D eastern service town links to E gateway/industry.\nStudy the northern low slopes, not a mountain shortcut.')]
        y = 0.8
        for (a, b) in blocks:
            text(ax, 0, y, a, 15)
            text(ax, 0, y - 0.045, b, 11, va='top', linespacing=1.6)
            y -= 0.15
        text(ax, 0, 0.16, 'Study extent ≠ built capacity', 15)
        text(ax, 0, 0.115, 'Colours show priorities and conditional reservations,\nnot whole-site building, irrigation or secured resources.', 11, va='top', linespacing=1.6)
    elif mode == 'network':
        text(ax, 0, 0.98, 'Trace links; expose risks', 20, va='top')
        text(ax, 0, 0.88, 'Regional corridors: potential power, communications and water', 12)
        y = 0.78
        for (title, body) in [('P1  Connect fixed life and production first', 'Orange: initial access and living-quarter links.\nThe sloping-quarter connection needs specialist study.'), ('P2  Western towns and production spine', 'Blue-grey dashed: phased sections. Initial residents\nmust not depend on completion of the distant spine.'), ('P3  Eastern gateway corridor', 'Connect D and E north of the range only after\ntrade demand, utilities and road studies support it.'), ('Red: links inside flood screening', 'Study crossings and route alternatives.\nA continuous line does not establish engineering feasibility.')]:
            text(ax, 0, y, title, 15)
            text(ax, 0, y - 0.045, body, 11, va='top', linespacing=1.6)
            y -= 0.17
        total = sum((p['length_km'] for (_, p) in routes))
        wetlen = sum((p['flood_band_km'] for (_, p) in routes))
        text(ax, 0, 0.09, f'Candidate links: {total:.1f} km; inside flood screening: {wetlen:.1f} km', 11)
    else:
        text(ax, 0, 0.98, 'Verify before construction', 20, va='top')
        text(ax, 0, 0.88, 'Separate source geometry from proposed planning', 12)
        y = 0.77
        for (title, body) in [('Fixed context', 'Dark line: owner-derived competition boundary.\nGreen/red outlines: fixed fields/living quarter.'), ('Terrain and drainage', 'Grey: regional slopes; dots: flood screening.\nNarrow dark-green bands: channel-conveyance studies.'), ('This proposal', 'A–E towns/gateway and K1/K2 compute reservations.\nDashed links still require engineering verification.'), ('Southwest detailed study extent', 'Around the northern field edge, southwest town and access;\nclipped by the site, terrain and drainage screening.\nIt is not phase-one built area.')]:
            text(ax, 0, y, title, 15)
            text(ax, 0, y - 0.045, body, 11, va='top', linespacing=1.6)
            y -= 0.17
        text(ax, 0, 0.06, f'Detailed study envelope: {master.area / 1000000.0:.1f} km²; verify each section', 11)
legendnames = {'protect': 'Mountain/slope conservation study', 'wash': 'Channel-conveyance study', 'floodstudy': 'Flood screening (unverified)', 'fixed_agri': 'Fixed agrivoltaic fields', 'fixed_living': 'Fixed living-quarter outline', 'town': 'Town reservation', 'compute': 'Compute/maintenance reserve', 'gateway': 'Gateway/export industry', 'localindustry': 'Initial processing/repair', 'energy': 'Energy-led production', 'agri': 'Low-slope production study', 'dry': 'Retained dryland'}
for (mode, filename, title) in [('planning', '01_whole_site_plan', 'AGUA FINITA / Whole-site structure'), ('network', '02_corridors_and_phases', 'AGUA FINITA / Towns, corridors and delivery'), ('geometry', '03_source_geometry', 'AGUA FINITA / Source boundary and planning extents')]:
    fig = plt.figure(figsize=(20, 12), facecolor=BG)
    ax = fig.add_axes([0.025, 0.15, 0.67, 0.73])
    pa = fig.add_axes([0.72, 0.17, 0.26, 0.69])
    basemap(ax, mode)
    routeplot(ax, mode)
    panel(pa, mode)
    if mode == 'geometry':
        lines(ax, master.boundary, '#C88C58', 1.8, '--')
        for g in [*urban.values(), *compute.values(), gateway]:
            lines(ax, g.boundary, '#647D83', 1)
    else:
        text(ax, 576.2, 6552.2, 'First district', 10, ha='left')
        text(ax, 569, 6546, 'Fixed agrivoltaic fields', 10, ha='center', bbox=dict(facecolor=BG, edgecolor='none', pad=1))
        text(ax, 584.5, 6543.5, 'Fixed living-quarter outline', 10, ha='center')
        text(ax, 602, 6557, 'Pie de Palo\nMountain conservation', 14, ha='center', color='#68776A')
        text(ax, 594, 6583, 'Energy–compute\nProduction corridor', 12, ha='center', color='#786739')
        text(ax, 573, 6597, 'Northwest production study', 11, ha='center')
        text(ax, 605, 6570, 'Eastern production study', 11, ha='center')
    text(fig, 0.04, 0.95, title, 28, transform=fig.transFigure)
    text(fig, 0.04, 0.912, 'XCITY OPEN AGENT CALL  ·  Jingyuan Huang  ·  2026-10-26  ·  V3 REVIEW', 11, transform=fig.transFigure)
    if mode != 'geometry':
        handles = [LegendPatch(facecolor=COL[k], label=legendnames[k]) for k in COL]
        leg = fig.legend(handles=handles, loc='lower left', bbox_to_anchor=(0.04, 0.055), ncol=6, frameon=False, prop=FontProperties(fname=font.get_file(), size=11), columnspacing=1.8)
    text(fig, 0.04, 0.025, 'Sources: XCITY c60cd1d; competition boundary, fixed pilots, 60 m Copernicus DEM and derived drainage screening. Reservations are concepts; 300 m corridor routing is not road engineering.', 9, transform=fig.transFigure)
    for ext in ['png', 'svg']:
        fig.savefig(OUT / (filename + '.' + ext), dpi=180, facecolor=BG)
        fig.savefig(O / (filename + '.' + ext), dpi=180, facecolor=BG)
    plt.close(fig)
print(json.dumps(qa, ensure_ascii=False, indent=2))
print('OUTPUT', OUT, 'HASH', h)
