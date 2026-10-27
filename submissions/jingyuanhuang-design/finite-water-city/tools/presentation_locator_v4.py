"""Presentation map only. Read the accepted geometry without altering it."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Polygon as PG
from shapely.geometry import shape
from shapely.ops import transform, unary_union
from pyproj import Transformer
P = Path(__file__).resolve().parents[1]
R = P.parents[2]
O = P / 'reviews/presentation-v4'
O.mkdir(exist_ok=True)
t = Transformer.from_crs(4326, 32719, always_xy=True).transform
load = lambda path: [(f['properties'], transform(t, shape(f['geometry']))) for f in json.loads(path.read_text())['features']]
S = R / 'brief/site-package'
scope = unary_union([g for (p, g) in load(S / 'boundaries/scope_9_13.geojson')])
fixed = load(S / 'pilot-area/pilot_area.geojson') + load(S / 'pilot-area/pilot_living_area.geojson')
land = load(P / 'geometry/land_use.geojson')
nodes = load(P / 'geometry/nodes.geojson')
buildings = load(P / 'geometry/buildings.geojson')
movement = load(P / 'geometry/movement.geojson')
flood = unary_union([g for (p, g) in load(S / 'water/flood_sensitive_dem.geojson')])
font = FontProperties(family='DejaVu Sans')
INK = '#263D44'
BG = '#F8F6F0'
colors = {'B03': '#526F7A', 'C03': '#72896B', 'A03': '#B97657'}
names = {'B03': 'Compute and waste heat', 'C03': 'Seasonal river park', 'A03': 'Public space in heat and wind'}

def text(ax, x, y, s, size=12, **kw):
    return ax.text(x, y, s, fontproperties=font, fontsize=size, color=kw.pop('color', INK), **kw)

def fill(ax, g, c, edge=None, lw=0.5, alpha=1):
    if g.geom_type == 'Polygon':
        ax.add_patch(PG([(x / 1000, y / 1000) for (x, y) in g.exterior.coords], facecolor=c, edgecolor=edge or c, lw=lw, alpha=alpha))
    elif hasattr(g, 'geoms'):
        for v in g.geoms:
            fill(ax, v, c, edge, lw, alpha)

def line(ax, g, c, lw=1, ls='-'):
    if g.geom_type in ['LineString', 'LinearRing']:
        (x, y) = g.xy
        ax.plot([v / 1000 for v in x], [v / 1000 for v in y], c=c, lw=lw, ls=ls)
    elif g.geom_type == 'Polygon':
        line(ax, g.exterior, c, lw, ls)
    elif hasattr(g, 'geoms'):
        for v in g.geoms:
            line(ax, v, c, lw, ls)
fig = plt.figure(figsize=(16, 9), facecolor=BG)
a = fig.add_axes([0.035, 0.21, 0.26, 0.66])
b = fig.add_axes([0.36, 0.21, 0.6, 0.66])
for ax in [a, b]:
    ax.set_aspect('equal')
    ax.axis('off')
fill(a, scope, '#E4E1D8', INK, 1)
for (p, g) in fixed:
    fill(a, g, '#8B9F6C')
for (p, g) in nodes:
    fill(a, g, colors[p['node_id']])
a.set(xlim=(559, 632), ylim=(6540, 6609))
text(a, 562, 6606, 'Whole site / approx. 1,656 km²', 12)
a.annotate('First district: all three nodes are here', xy=(573.5, 6553.5), xytext=(577, 6566), fontproperties=font, fontsize=11, color=INK, arrowprops=dict(arrowstyle='->', color=INK, lw=1.2), bbox=dict(facecolor=BG, edgecolor='none', pad=3))
text(a, 567, 6541, 'Fixed agrivoltaic fields', 9)
text(a, 584, 6544, 'Fixed living quarter', 9)
window = __import__('shapely').geometry.box(571700, 6552000, 575100, 6554950)
fill(b, window, '#ECE6D8')
for (p, g) in land:
    q = g.intersection(window)
    fill(b, q, {'residential': '#E4D3B5', 'civic': '#D7AE99', 'industry': '#C5C1AD', 'compute': '#B0BEC2', 'energy': '#D9C68C', 'agriculture': '#B6C49B', 'open_space': '#E7E4D8', 'reserve': '#E9E5D9'}.get(p['use'], BG))
line(b, flood.intersection(window), '#B5C4BB', 0.7)
for (p, g) in movement:
    if p.get('network') == 'people':
        line(b, g, '#AA8C63', 0.8)
    elif p.get('network') == 'machine':
        line(b, g, '#8E9899', 0.65)
for (p, g) in buildings:
    if p.get('form') != 'canopy':
        fill(b, g, '#6F7470')
loc = []
for (p, g) in nodes:
    n = p['node_id']
    line(b, g.boundary, colors[n], 2.2)
    c = g.centroid
    xy = {'B03': (574.9, 6552.18), 'C03': (572.15, 6554.98), 'A03': (575.05, 6553.9)}[n]
    b.annotate(n + '  ' + names[n], xy=(c.x / 1000, c.y / 1000), xytext=xy, fontproperties=font, fontsize=13, color=colors[n], ha='right' if n == 'A03' else 'center', arrowprops=dict(arrowstyle='-', color=colors[n], lw=1.4), bbox=dict(facecolor=BG, edgecolor='none', pad=4))
    loc.append(dict(node_id=n, name=names[n], centroid_utm=[c.x, c.y], bounds_utm=list(g.bounds)))
b.set(xlim=(571.7, 575.3), ylim=(6551.9, 6555.2))
text(b, 573.5, 6555.35, 'First district: production, channels and daily life', 13, ha='center')
b.plot([571.9, 572.4], [6552.1] * 2, color=INK, lw=2)
text(b, 572.15, 6552.0, '0            500 m', 9, ha='center')
b.annotate('', xy=(575.1, 6554.85), xytext=(575.1, 6554.5), arrowprops=dict(arrowstyle='-|>', color=INK))
text(b, 575.1, 6554.93, 'Grid N', 9, ha='center')
text(fig, 0.04, 0.95, 'Where are the three nodes?', 26, transform=fig.transFigure)
text(fig, 0.04, 0.9, 'Whole site → southwest first district → three connected design tests', 13, transform=fig.transFigure)
text(fig, 0.04, 0.12, 'B03 · Southern production edge', 14, transform=fig.transFigure, color=colors['B03'])
text(fig, 0.04, 0.075, 'Compute, repair and heat receivers are adjacent.', 11, transform=fig.transFigure)
text(fig, 0.36, 0.12, 'C03 · Northwest seasonal channel', 14, transform=fig.transFigure, color=colors['C03'])
text(fig, 0.36, 0.075, 'Keep the dry channel; public use retreats uphill.', 11, transform=fig.transFigure)
text(fig, 0.7, 0.12, 'A03 · Civic core east of housing', 14, transform=fig.transFigure, color=colors['A03'])
text(fig, 0.7, 0.075, 'Kitchen, library and shade sustain everyday use.', 11, transform=fig.transFigure)
for ext in ['png', 'svg']:
    fig.savefig(O / ('node-locator.' + ext), dpi=180, facecolor=BG)
(O / 'node-locations.json').write_text(json.dumps(loc, ensure_ascii=False, indent=2))
print(O / 'node-locator.png')
