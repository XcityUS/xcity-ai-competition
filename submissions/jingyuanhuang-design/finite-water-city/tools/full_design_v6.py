"""Author original design diagrams and connect them to the current entry, no repo policy edits."""
import json, sys, textwrap
from pathlib import Path
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Polygon as Patch, Rectangle, FancyArrowPatch
from shapely.geometry import shape, box, LineString, Point
from shapely.ops import transform, unary_union
from pyproj import Transformer
P = Path(__file__).resolve().parents[1]
R = P.parents[2]
O = P / 'reviews/full-v6'
O.mkdir(exist_ok=True)
sys.path.insert(0, str(R / 'scripts'))
import xcity_common as xc
T = Transformer.from_crs(4326, 32719, always_xy=True).transform
I = Transformer.from_crs(32719, 4326, always_xy=True).transform
load = lambda f: [(x['properties'], transform(T, shape(x['geometry']))) for x in json.loads(f.read_text())['features']]
S = R / 'brief/site-package'
land = load(P / 'geometry/land_use.geojson')
build = load(P / 'geometry/buildings.geojson')
move = load(P / 'geometry/movement.geojson')
nodes = {p['node_id']: (p, g) for (p, g) in load(P / 'geometry/nodes.geojson')}
scope = xc.to_utm(xc.site_boundary())
flood = unary_union([g for (p, g) in load(S / 'water/flood_sensitive_dem.geojson')])
channels = unary_union([g for (p, g) in load(S / 'water/channels_dem.geojson')])
fixed = xc.to_utm(xc.pilot_area())
phases = load(P / 'geometry/phasing.geojson')
metrics = xc.metric_map(json.loads((P / 'metrics.json').read_text()))
computed = xc.compute_metrics(str(P))
FONT = FontProperties(family='DejaVu Sans')
BG = '#F8F6F0'
INK = '#263D44'
MUT = '#697A77'
COL = {'residential': '#E1D0B3', 'civic': '#C5947E', 'compute': '#A5B5BE', 'industry': '#BCBDA8', 'energy': '#D7C383', 'agriculture': '#B5C399', 'open_space': '#E5E1D6', 'reserve': '#EAE7DE'}
colors = {'B03': '#526F7A', 'C03': '#72896B', 'A03': '#B97657'}

def tx(ax, x, y, s, size=12, **kw):
    return ax.text(x, y, s, fontproperties=FONT, fontsize=size, color=kw.pop('color', INK), **kw)

def fill(ax, g, color, lw=0, edge=None, alpha=1):
    if g.is_empty:
        return
    if g.geom_type == 'Polygon':
        from matplotlib.path import Path as MP
        from matplotlib.patches import PathPatch
        from shapely.geometry.polygon import orient
        g = orient(g, sign=1)
        vs = []
        codes = []
        for ring in [g.exterior, *g.interiors]:
            a = np.array(ring.coords)
            vs.extend(a)
            codes.extend([MP.MOVETO] + [MP.LINETO] * (len(a) - 2) + [MP.CLOSEPOLY])
        ax.add_patch(PathPatch(MP(vs, codes), facecolor=color, edgecolor=edge or color, lw=lw, alpha=alpha))
    elif hasattr(g, 'geoms'):
        for q in g.geoms:
            fill(ax, q, color, lw, edge, alpha)

def line(ax, g, color=INK, lw=1, ls='-'):
    if g.is_empty:
        return
    if g.geom_type in ['LineString', 'LinearRing']:
        ax.plot(*g.xy, color=color, lw=lw, ls=ls)
    elif g.geom_type == 'Polygon':
        line(ax, g.boundary, color, lw, ls)
    elif hasattr(g, 'geoms'):
        for q in g.geoms:
            line(ax, q, color, lw, ls)

def page(title, subtitle):
    f = plt.figure(figsize=(16, 10), facecolor=BG)
    tx(f, .045, .94, title, 24, transform=f.transFigure)
    tx(f, .045, .895, '\n'.join(textwrap.wrap(subtitle, 135)), 11.5, transform=f.transFigure, va='top')
    tx(f, .045, .035, 'AGUA FINITA | Jingyuan Huang | 2026-10-26 | Concept design; own geometry and declared assumptions, not survey or approval.', 9, transform=f.transFigure, color=MUT)
    return f

def save(f, name):
    f.savefig(O / (name + '.png'), dpi=160, facecolor=BG)
    plt.close(f)

def mapbase(ax, bounds, showbuild=True):
    win = box(*bounds)
    for (p, g) in land:
        fill(ax, g.intersection(win), COL.get(p['use'], BG))
    line(ax, flood.intersection(win).boundary, '#B8C8BF', 0.7)
    for (p, g) in move:
        if g.geom_type in ['LineString', 'MultiLineString']:
            line(ax, g.intersection(win), '#BD845E' if p.get('network') == 'people' else '#8C989A', 1 if p.get('network') == 'people' else 0.7)
    if showbuild:
        for (p, g) in build:
            fill(ax, g.intersection(win), '#8B9A9B' if p.get('form') == 'canopy' else '#5E6E70', lw=0.2)
    ax.set(xlim=(bounds[0], bounds[2]), ylim=(bounds[1], bounds[3]))
    ax.set_aspect('equal')
    ax.axis('off')

def scale(ax, x, y, length):
    ax.plot([x, x + length], [y, y], color=INK, lw=2)
    tx(ax, x, y - 45, f'0                 {length:g} m', 9, va='top')

def explain(ax, items):
    ax.axis('off')
    prepared=[(textwrap.wrap(title, 35), [v for line in body.split('\n') for v in textwrap.wrap(line, 43)]) for title,body in items]
    units=sum(len(head)*1.5+len(body)+1.3 for head,body in prepared)
    step=min(.05,.92/max(units,1));y=.97
    for head,body in prepared:
        for line in head:
            tx(ax,0,y,line,12.5,va='top');y-=step*1.5
        for line in body:
            tx(ax,0,y,line,10.5,va='top');y-=step
        y-=step*1.3

f = page('Read the site before shaping the city', 'Separate fixed context, terrain screening and regional links; screening is not a lake.')
a = f.add_axes([0.035, 0.13, 0.63, 0.71])
fill(a, scope, '#EAE6DB', 1, INK)
raw = np.array(Image.open(S / 'terrain/dem_9_13_utm19s_60m.png')).astype(float)
(dy, dx) = np.gradient(raw, 60)
sl = np.hypot(dx, dy) * 100
xx = np.linspace(559572.4, 631512.4, raw.shape[1])
yy = np.linspace(6608973.7, 6541053.7, raw.shape[0])
extent = [559572.4, 631512.4, 6541053.7, 6608973.7]
from shapely import contains_xy
cx=extent[0]+(np.arange(raw.shape[1])+.5)*(extent[1]-extent[0])/raw.shape[1]
cy=extent[3]-(np.arange(raw.shape[0])+.5)*(extent[3]-extent[2])/raw.shape[0]
mask=contains_xy(scope,*np.meshgrid(cx,cy))
a.imshow(np.ma.array(raw,mask=~mask), cmap='Greys', extent=extent, alpha=0.13, vmin=600, vmax=1600)
fill(a, flood.intersection(scope), '#DCE5DB', 0.3, '#A7BAAA', 0.7)
line(a, channels.intersection(scope), '#668F8D', 0.8)
fill(a, fixed, '#A2AE83', 0.7, INK)
line(a, scope.boundary, INK, 1.6)
a.set(xlim=(560000, 632000), ylim=(6540500, 6608000), aspect='equal')
a.axis('off')
b = f.add_axes([0.71, 0.17, 0.25, 0.65])
explain(b, [('Fixed starting conditions', 'Fixed fields and the living quarter occupy different places. Verify access and demand separately.'), ('Screening is not a no-build boundary', 'DEM channels and about 503 km² of screening; surveyed flood limits and design flows are absent.'), ('Terrain shapes the eastern route', 'Study the northern low-slope approach; do not invent a shortcut through the mountains.'), ('Access is a project in itself', 'No national/provincial route enters the supplied site extract. External alignment, rights and crossings remain unverified.')])
save(f, '01-site-reading')
f = page('Why start in the southwest rather than at the eastern gateway?', 'Compare fixed systems, complete daily life, access and secured resources; no invented aggregate scores.')
a = f.add_axes([0.05, 0.16, 0.9, 0.67])
a.axis('off')
rows = [['Decision', 'Southwest first district (selected)', 'West-central compute corridor (conditional)', 'Eastern gateway (later)'], ['Fixed systems', 'Near fixed fields; connect separately to the living quarter', 'Potential energy and maintenance clusters', 'Far from initial public services'], ['Daily life', 'Housing, school and clinic start together', 'Production and servicing first', 'An export park cannot replace a complete neighbourhood'], ['Terrain and channels', 'Buildings on eastern terraces; retreat from channels', 'Screen successive low-slope areas outside sensitivity bands', 'Route north of the range; verify eastern terraces'], ['Resource limits', 'Verify initial water rights and electricity first', 'Capacity and contracted demand trigger expansion', 'Start only when trade, engineering and resources align'], ['Accepted trade-off', 'Give up the image of simultaneous whole-site development', 'Long productive gaps between settlements', 'The indicative 7 km² still requires land verification']]
rows = [['\n'.join(textwrap.wrap(value, [18, 34, 34, 34][column])) for column,value in enumerate(row)] for row in rows]
tab = a.table(cellText=rows, cellLoc='left', colWidths=[0.14, 0.29, 0.29, 0.28], bbox=[0, 0, 1, 1])
tab.auto_set_font_size(False)
tab.set_fontsize(11)
for ((r, c), cell) in tab.get_celld().items():
    cell.set_text_props(fontproperties=FONT, color=INK)
    cell.set_edgecolor('#D5D6C9')
    cell.set_facecolor('#E6E4D8' if r == 0 else BG)
save(f, '02-siting-tradeoff')
f = page('Five systems are more than five unrelated colours', 'Energy and compute support production; secured water, services and maintenance govern growth.')
a = f.add_axes([0.045, 0.2, 0.91, 0.61])
a.set(xlim=(0, 12), ylim=(0, 7))
a.axis('off')
boxes = [(0, 4.5, 2.6, 1.5, 'Energy + storage', '#D7C383'), (4, 4.5, 2.6, 1.5, 'Compute + maintenance', '#A5B5BE'), (8.5, 4.5, 2.8, 1.5, 'Processing, export\n+ gateway', '#BAA5AA'), (0, 1, 2.6, 1.5, 'Agriculture\n+ agrivoltaics', '#B5C399'), (4, 1, 2.6, 1.5, 'Residents\n+ public life', '#D5AF94'), (8.5, 1, 2.8, 1.5, 'Water, audit\n+ governance', '#B7CBC8')]
for (x, y, w, h, t, c) in boxes:
    a.add_patch(Rectangle((x, y), w, h, facecolor=c, edgecolor='none'))
    tx(a, x + w / 2, y + h / 2, t, 15, ha='center', va='center')
for (p, q, label) in [((2.6, 5.25), (4, 5.25), 'Power'), ((6.6, 5.25), (8.5, 5.25), 'Production services'), ((1.3, 2.5), (1.3, 4.5), 'Shared land'), ((5.3, 4.5), (5.3, 2.5), 'Heat + services'), ((8.5, 1.75), (6.6, 1.75), 'Basic needs first'), ((8.5, 4.5), (10, 2.5), 'Revenue + responsibility')]:
    a.annotate('', xy=q, xytext=p, arrowprops=dict(arrowstyle='->', color=INK, lw=1.8))
    tx(a, (p[0] + q[0]) / 2 + 0.1, (p[1] + q[1]) / 2 + 0.15, label, 11, ha='center', bbox=dict(fc=BG, ec='none', pad=2))
tx(f, 0.06, 0.12, 'Sequence: verify lawful water, power and services → contract interruptible production → audit before expansion.', 15, transform=f.transFigure)
save(f, '03-five-systems')
f = page('First district: homes, public life and production interfaces', 'Building positions are unchanged; wider reservations are not completed urban design.')
a = f.add_axes([0.035, 0.12, 0.64, 0.72])
bounds = (572700, 6552000, 575150, 6554900)
mapbase(a, bounds)
for (nid, (p, g)) in nodes.items():
    line(a, g.intersection(box(*bounds)).boundary, colors[nid], 1.5)
for (x, y, label) in [(573850, 6553920, 'Housing'), (574470, 6554050, 'School / clinic / civic uses'), (573900, 6552850, 'Processing, repair + servicing'), (574000, 6552350, 'Compute + dry heat rejection'), (574950, 6554500, 'PV + storage'), (573750, 6554600, 'Limited irrigation trial')]:
    tx(a, x, y, label, 11, ha='center', bbox=dict(fc=BG, ec='none', pad=2))
scale(a, 572850, 6552100, 500)
b = f.add_axes([0.71, 0.19, 0.25, 0.61])
explain(b, [('Complete daily life first', 'Model targets: 960 homes and 2,400 new residents. School, clinic and daily shops open together.'), ('Public routes link daily needs', 'Homes → public kitchen / library → shade. Walking does not cut through compute service yards.'), ('Jobs along the production edge', 'Compute, processing, repairs and water maintenance provide initial jobs; machines enter from the service edge.'), ('Separate initial and study extents', 'The roughly 40 km² study envelope includes conditional reserves not yet designed as blocks.')])
save(f, '04-first-neighbourhood')
f = page('Housing clusters: from front door to public route', 'Three-storey bars and continuous shaded routes: a tested block fragment, not a standard sale product.')
a = f.add_axes([0.04, 0.2, 0.55, 0.64])
bounds = (573350, 6553120, 573850, 6553650)
mapbase(a, bounds)
scale(a, 573390, 6553160, 100)
for y in [6553200, 6553248]:
    a.annotate('', xy=(573450, y - 8), xytext=(573492, y - 8), arrowprops=dict(arrowstyle='|-|', color=INK))
    tx(a, 573471, y - 20, '42 m', 10, ha='center')
b = f.add_axes([0.66, 0.19, 0.29, 0.65])
explain(b, [('Housing dimensions', 'Typical bar: 42 × 16 m, three floors, 10 homes. 96 × 10 = 960 homes; assume 2.5 people per home.'), ('People and shared space', 'Ground space supports shared activity and arrival. Route shade does not replace indoor heat refuge.'), ('Servicing and quiet edges', 'Delivery, emergency access and repair enter at the edge. Doors, accessibility and parking need further design.'), ('Further design tests', 'Counts alone do not establish housing quality. Test doors, service routes, thermal comfort and maintenance.')])
save(f, '05-housing-enlargement')
f = page('Heights and interfaces: low-rise forms and light shade roofs', 'Seismic, heat and maintenance considerations; shown heights come from submitted building attributes.')
a = f.add_axes([0.06, 0.3, 0.87, 0.46])
a.set(xlim=(0, 510), ylim=(-1, 18))
a.axhline(0, color=INK, lw=1.2)
for x in [30, 130, 230, 330, 430]:
    a.add_patch(Rectangle((x, 0), 42, 10.5, facecolor='#C8B69B', edgecolor=INK, lw=0.7))
    tx(a, x + 21, 11.4, '3 floors / 10.5 m', 10, ha='center')
a.set_yticks([0, 5, 10, 15])
a.set_ylabel('m')
a.set_xlabel('m')
a.spines[['top', 'right']].set_visible(False)
tx(a, 250, 16, 'Housing height and spacing study (not structural drawings)', 13, ha='center')
tx(f, 0.06, 0.18, 'Regular lateral systems + replaceable light roofs + low-glare lighting + accessible indoor heat refuges', 16, transform=f.transFigure)
tx(f, 0.06, 0.11, 'Modelled heights do not resolve drift, seismic joints, foundations, roof spans or fire evacuation.', 12, transform=f.transFigure, color=MUT)
save(f, '06-height-interface')
f = page('People and machines: locate every registered interface', 'Machines use regional/service routes; at-grade meetings with public paths are registered.')
a = f.add_axes([0.035, 0.16, 0.64, 0.66])
bounds = (572850, 6552000, 575100, 6554900)
mapbase(a, bounds, False)
for (p, g) in move:
    if p.get('kind') == 'interface':
        a.scatter(g.x, g.y, s=65, color='#B36B50', edgecolor=BG, zorder=10)
scale(a, 573000, 6552100, 500)
b = f.add_axes([0.71, 0.19, 0.25, 0.6])
explain(b, [('Seven registered interfaces', 'Current geometry count, not a risk score. Check stops, loading points and service entrances too.'), ('People first; accountable control', 'Gates, yielding and on-site manual release. AI cannot override pedestrian priority or emergency rules.'), ('Regional links are not local streets', 'The fixed-quarter connection is transport, not a substitute for local everyday services.'), ('Check real doors and access', 'Verify accessible paths, service turns, emergency stops and engineered gradients.')])
save(f, '07-human-machine')
node_titles = {'B03': 'Compute and waste heat', 'C03': 'Seasonal river park', 'A03': 'Public space in heat and wind'}
for (nid, (p, g)) in nodes.items():
    f = page(nid + ' · ' + node_titles[nid] + ': detailed plan and decisive section', 'Formal plans explain spatial decisions; raw controls and extra checks stay in the technical appendix.')
    a = f.add_axes([0.035, 0.27, 0.57, 0.55])
    (x0, y0, x1, y1) = g.bounds
    pad = 80
    bounds = (x0 - pad, y0 - pad, x1 + pad, y1 + pad)
    mapbase(a, bounds)
    line(a, g.boundary, colors[nid], 1.5)
    sectiony = {'B03': 6552267.5, 'C03': 6554455, 'A03': 6553650}[nid]
    section = LineString([(x0, sectiony), (x1, sectiony)])
    line(a, section, colors[nid], 1.4, '--')
    tx(a, x0, sectiony + 25, 'A', 12)
    tx(a, x1, sectiony + 25, "A'", 12)
    scale(a, x0 + 20, y0 + 20, 200 if nid != 'A03' else 50)
    b = f.add_axes([0.65, 0.3, 0.31, 0.52])
    items = {'B03': [('Production layout', 'Three 180 × 75 m halls, one floor, 9 m high. Repair and processing lie to the north.'), ('Heat needs a receiver', 'A 70 × 35 m drying / heat receiver is modelled. Verify network temperature, losses and operating hours.'), ('Do not trade water for peak efficiency', 'Assumed targets: WUE 0.02 L/kWh, PUE 1.25. Dry rejection accepts hot-hour energy costs and curtailment.')], 'C03': [('Everyday use on higher ground', 'An 80 × 30 m field classroom occupies the eastern high ground. Paths observe dry channels, not a permanent lake.'), ('A clear retreat in storms', 'Close low seasonal paths; preserve flood conveyance. Duty staff manage warning, closure and reopening.'), ('A section is not flood certification', 'Ground comes from a 60 m DEM with vertical exaggeration. Design levels, flows and small washes are unverified.')], 'A03': [('Occupied edges and cross-site links', 'Approx. 270 × 152 m outer frame; 12 m edge roofs. Central covered walking links homes and civic facilities.'), ('A large court is not fully shaded', 'Shade prioritises routes and occupied edges. Open-court activities follow heatwave operating rules.'), ('Services sustain everyday use', 'Kitchen, library and training/community uses are adjacent. Drinking water, maintenance and indoor refuge remain essential.')]}
    explain(b, items[nid])
    ax = f.add_axes([0.08, 0.115, 0.82, 0.11])
    L = section.length
    s = np.linspace(0, L, 160)
    px = x0 + s
    py = np.full_like(s, sectiony)
    rr = np.clip(((6608973.7 - py) / 60).astype(int), 0, raw.shape[0] - 1)
    cc = np.clip(((px - 559572.4) / 60).astype(int), 0, raw.shape[1] - 1)
    z = raw[rr, cc]
    base = float(z.min())
    ground = z - base
    ve = 3 if nid == 'C03' else 1
    ax.plot(s, ground * ve, color=INK, lw=1)
    for (bp, bg) in build:
        cut = bg.intersection(section)
        if cut.is_empty or cut.length < 0.2:
            continue
        for seg in list(cut.geoms) if hasattr(cut, 'geoms') else [cut]:
            if seg.geom_type != 'LineString':
                continue
            (a0, b0) = (seg.bounds[0] - x0, seg.bounds[2] - x0)
            gz = float(np.interp((a0 + b0) / 2, s, ground))
            h = float(bp.get('height_m', float(bp.get('floors', 1)) * 3.5))
            ax.add_patch(Rectangle((a0, gz * ve), b0 - a0, h * ve, facecolor=colors[nid], edgecolor='none', alpha=0.8))
    ax.set(xlim=(0, L), ylim=(-1, max(18, float(ground.max() + 11) * ve)))
    ax.spines[['top', 'right']].set_visible(False)
    ax.tick_params(labelsize=8)
    tx(ax, 0.01, 1.04, "A–A'  Geometry / DEM section; vertical ×" + str(ve), 10, transform=ax.transAxes)
    save(f, nid + '-plan-section')
    f = page(nid + ' · Use and operation: normal, extreme and recovery', 'Everyday use and abnormal operation constrain one another; unverified performance is not claimed as achieved.')
    a = f.add_axes([0.05, 0.22, 0.9, 0.59])
    a.axis('off')
    records = {'B03': [('Early morning', 'Maintenance, handover and drying preparation', 'Machines use the service edge; visitors follow separate paths.'), ('Hot afternoon', 'Protect basic services first', 'Curtail flexible compute by contract, without extra cooling abstraction.'), ('Water shortage', 'Stop discretionary irrigation and ornamental uses first', 'Protect essential resident demand and the fixed systems.'), ('Equipment / operator exit', 'Transfer maintenance and assets', 'Keep public utilities, metering and service funds available.')], 'C03': [('Dry everyday use', 'Observation, walking and water education', 'The classroom is on high ground; channels retain their dry landscape.'), ('Upstream warning', 'Close low paths and guide retreat', 'Duty staff control closure; do not wait for rain at the site.'), ('During floods', 'Low areas closed', 'No design flow is supplied; the model does not certify protection.'), ('After recession', 'Inspect erosion, sediment and path damage', 'Maintenance staff inspect before reopening; no automatic unlock.')], 'A03': [('Early morning', 'Walking, shopping and meeting', 'Use connected shade roofs and the public kitchen.'), ('Heat / strong dust winds', 'Reduce outdoor stays', 'Shade does not guarantee safety; move to accessible indoor refuge.'), ('Evening', 'Public activity, reading and care', 'Low-glare route lighting; no large screens or uplighting.'), ('Outage / equipment failure', 'Keep basic access and manual service', 'Manual controls, emergency drinking water and staff takeover.')]}
    for (i, (time, activity, rule)) in enumerate(records[nid]):
        x = i * 0.25
        a.add_patch(Rectangle((x, 0.05), 0.23, 0.9, facecolor=['#E4E5DA', '#DCE4E2', '#E9DCCC', '#DFE5DA'][i], edgecolor='none'))
        tx(a, x + 0.015, 0.86, '\n'.join(textwrap.wrap(time, 20)), 15)
        tx(a, x + 0.015, 0.65, '\n'.join(textwrap.wrap(activity, 31)), 11.5)
        for (j, l) in enumerate(textwrap.wrap(rule, 33)):
            tx(a, x + 0.015, 0.45 - j * 0.075, l, 11)
    tx(f, 0.06, 0.11, 'In every state: locate users, name the shutdown authority, provide help and verify before restarting.', 16, transform=f.transFigure)
    save(f, nid + '-operation')
f = page('Water budget: protect daily life before expanding production', 'Assumed gross use: 1,000,000 m³/yr. Reuse is internal transfer, not another external water source.')
a = f.add_axes([0.06, 0.3, 0.57, 0.49])
a.axis('off')
parts = [('Agriculture + cleaning', 778263.2, '#A9B98C'), ('Residents + civic services', 140160, '#B5856F'), ('Industry', 60000, '#A4B5BA'), ('Landscape', 20000, '#D9C78E'), ('Compute make-up', 1576.8, '#788F99')]
x = 0
for (name, value, c) in parts:
    a.barh([0.7], value / 1000000, left=x, height=0.2, color=c)
    x += value / 1000000
for (i, (name, value, c)) in enumerate(parts):
    tx(a, 0.01, 0.49 - i * 0.075, f'{name}   {value:,.1f} m³/yr', 13, color=c)
a.set(xlim=(0, 1), ylim=(0, 1))
b = f.add_axes([0.69, 0.23, 0.26, 0.56])
explain(b, [('External input', '840,000 m³ fresh input less 40,000 losses: 800,000 reaches use, plus 200,000 internal reuse.'), ('Protect the fixed agriculture allowance', '600,000 m³ is an unverified pilot allowance. If actual use is higher, reduce new discretionary uses first.'), ('What a 30% shortfall costs', 'Cut landscape by 20,000; new irrigation/cleaning by 178,263.2; industry by 40,000; non-essential domestic use by 61,736.8 m³.'), ('An unresolved demand gap', 'Fixed living-quarter demand is absent. This budget does not cover the entire future city.')])
tx(f, 0.06, 0.13, 'If basic demand cannot be met, secure emergency water or delay occupancy; arithmetic does not supply water.', 16, transform=f.transFigure)
save(f, '08-water-budget')
import csv
r = list(csv.DictReader((P / 'tools/hourly_dispatch.csv').open()))
hours = np.array([int(v['hour']) for v in r])
pv = np.array([float(v['pv_mw']) for v in r])
loadarr = np.array([float(v['load_mw']) for v in r])
grid = np.array([float(v['grid_mw']) for v in r])
idx = np.arange(24 * 35, 24 * 38)
f = page('Energy: night tests the promise more than daylight', 'An 8,760-hour synthetic scenario, not measured weather, a grid agreement or achieved performance.')
a = f.add_axes([0.07, 0.3, 0.59, 0.49])
a.plot(idx / 24, pv[idx], color='#B49745', label='PV')
a.plot(idx / 24, loadarr[idx], color=INK, label='Load')
a.fill_between(idx / 24, 0, grid[idx], color='#B7826B', alpha=0.5, label='Unmatched grid')
a.set(xlabel='Day in synthetic model', ylabel='MW')
a.spines[['top', 'right']].set_visible(False)
a.legend(frameon=False)
b = f.add_axes([0.72, 0.28, 0.23, 0.5])
explain(b, [('62.432%', 'Share of hours fully matched by clean supply; not the annual clean-energy share.'), ('72.993%', 'Separate clean-energy share. Unverified grid imports receive no clean credit.'), ('Model inputs', 'Assume 40 MW PV, 480 MWh storage, 12 MW peak IT and PUE 1.25.')])
tx(f, 0.06, 0.14, 'Storage starts at its protected reserve: 216 MWh deliverable emergency energy is not free initial clean supply.', 14, transform=f.transFigure)
save(f, '09-energy-dispatch')
f = page('Who authorises growth and pays for downtime and maintenance?', 'Critical city utilities must survive any single compute operator.')
a = f.add_axes([0.05, 0.2, 0.9, 0.6])
a.axis('off')
items = [('Public utility + community trust', 'Retain land, utilities, metering and public access. Publish aggregate water, power, storage and compute accounts.'), ('Compute operator', 'Contract interruptible service and maintain equipment. Provide transferable interfaces and safe exit arrangements.'), ('Residents, workers + independent audit', 'Participate in service priorities and appeals without personal tracking. Independent audit checks meters, calculations and growth conditions.')]
for (i, (title, body)) in enumerate(items):
    y = 0.88 - i * 0.29
    tx(a, 0, y, title, 19, color=['#526F7A', '#B97657', '#72896B'][i])
    tx(a, 0, y - 0.08, body, 14, va='top', linespacing=1.6)
tx(f, 0.06, 0.1, 'AI advises dispatch; it cannot authorise expansion, alter essential water allocations or override pedestrian priority.', 16, transform=f.transFigure)
save(f, '10-governance')
for (nid, (p, g)) in nodes.items():
    f = page(nid + ' · ' + node_titles[nid] + ': aerial and eye-level views', 'Concept views illustrate submitted space; they are not survey, capacity verification or built facts.')
    a = f.add_axes([0.035, 0.16, 0.57, 0.65])
    a.imshow(Image.open(P / 'media' / (nid + '-aerial-v6.png')))
    a.axis('off')
    b = f.add_axes([0.63, 0.28, 0.335, 0.48])
    b.imshow(Image.open(P / 'media' / (nid + '-eye-day.png')))
    b.axis('off')
    tx(f, 0.64, 0.18, {'B03': 'Southern production edge: compute, repair and heat receivers.', 'C03': 'Northwest channel edge: dry everyday use and flood retreat.', 'A03': 'Civic core east of housing: shade, services and interaction.'}[nid], 12, transform=f.transFigure)
    save(f, nid + '-finished')
prov = json.loads((P / 'image_provenance.json').read_text())
prov['images'] = [v for v in prov['images'] if not v.get('path', '').startswith('reviews/full-v6/')]
for file in sorted(O.glob('*.png')):
    prov['images'].append(dict(path=str(file.relative_to(P)), model='Python matplotlib / Shapely; deterministic authored diagram', prompt='Run tools/full_design_v6.py: read the submitted geometry, source DEM, movement, metrics and declared assumptions. Make legible, purpose-specific urban design plans, sections and system diagrams. No geometry or measured facts inferred from imagery.', generated_at='2026-10-26', post_processing='Original vector planning drawing and editorial composition', reference_images='own_work', reference_images_note='Own submitted geometry and registered concept images; organiser site data attribution in sources.json.', caption='Authored design evidence or presentation page; not survey or approval.'))
for id in ['B03', 'C03', 'A03']:
    entry = json.loads((P / 'tools' / (id + '-aerial-v6-provenance.json')).read_text())
    prov['images'] = [v for v in prov['images'] if v['path'] != entry['path']] + [entry]
cover = json.loads((P / 'tools/cover-render-v5-provenance.json').read_text())
prov['images'] = [v for v in prov['images'] if v['path'] != cover['path']] + [cover]
(P / 'image_provenance.json').write_text(json.dumps(prov, ensure_ascii=False, indent=2))
m = json.loads((P / 'manifest.json').read_text())
m['booklet'] = {'cover': 'media/cover-render-v5.png', 'pages': [], 'section_pages': {}}

def pg(name, title):
    return dict(path='reviews/full-v6/' + name + '.png', title=title)
m['booklet']['section_pages']['whole_site'] = [dict(path='reviews/whole-site-v3/01_whole_site_plan.png', title='Whole-site spatial structure')]
m['booklet']['section_pages']['node_locator'] = [dict(path='reviews/presentation-v4/node-locator.png', title='Whole site → first district → three nodes')]
for (name, title) in [('01-site-reading', 'Site evidence and constraints'), ('02-siting-tradeoff', 'Initial siting trade-offs'), ('03-five-systems', 'Five-system relationships')]:
    m['booklet']['pages'].append(dict(**pg(name, title), after='whole_site'))
for (name, title) in [('04-first-neighbourhood', 'First-district master plan'), ('05-housing-enlargement', 'Housing clusters and public routes'), ('06-height-interface', 'Heights and spatial interfaces'), ('07-human-machine', 'Human-machine routes and registered interfaces')]:
    m['booklet']['pages'].append(dict(**pg(name, title), after='views'))
for nid in m['nodes']:
    m['booklet']['section_pages']['node:' + nid] = [pg(nid + '-finished', nid + ' · ' + node_titles[nid])]
    for (typ, title) in [('plan-section', 'Detailed plan and section'), ('operation', 'Use and operating scenarios')]:
        m['booklet']['pages'].append(dict(**pg(nid + '-' + typ, nid + ' ' + title), after=nid))
for (name, title) in [('08-water-budget', 'Water budget and shortage'), ('09-energy-dispatch', 'Hourly energy scenario'), ('10-governance', 'Assets, accountability and growth governance')]:
    m['booklet']['pages'].append(dict(**pg(name, title), after='key_metrics'))
m['language'] = 'en'
m['title_zh'] = ''
(P / 'manifest.json').write_text(json.dumps(m, ensure_ascii=False, indent=2))
