"""Bring the reviewed independent concept into the current organiser contract; preserve its design."""
import json
from pathlib import Path
from shapely.geometry import shape,mapping
from shapely.ops import unary_union
P=Path(__file__).resolve().parents[1]
J=lambda f:json.loads((P/f).read_text());W=lambda f,d:(P/f).write_text(json.dumps(d,indent=2)+'\n')
# Keep polygon components only after intersection; discard zero-area topology fragments.
f='geometry/structure.geojson';d=J(f)
def polygons(g):
 if g.geom_type=='Polygon':yield g
 elif hasattr(g,'geoms'):
  for v in g.geoms:yield from polygons(v)
for v in d['features']:v['geometry']=mapping(unary_union(list(polygons(shape(v['geometry'])))))
W(f,d)
f='context/external-access-study.geojson';d=J(f)
for v in d['features']:
 p=v['properties'];p.update(status='study_only',authority='not_secured',basis='Source SRC-OSM regional RN40 line; entrant straight corridor study under A-TERRAIN. Not a surveyed or secured access alignment; rights, flood crossings, gradients and junction require verification.')
W(f,d)
f='image_provenance.json';d=J(f)
for v in d['images']:
 v.update(generated_at='2026-10-27',reference_images='own_work',reference_images_note='Original geometry massing made with tools/draw_design.py at '+v.get('reference','geometry/buildings.geojson')+'; original entrant work for this competition.',caption='Concept illustration over original massing. Paired image contains aerial at left and eye-level interpretation at right; not survey, construction or engineering evidence.')
 if '/district-' not in v['path']:
  v['node_id']=Path(v['path']).name.split('-')[0];v['view']='aerial'
 else:v['view']='city_aerial'
for control_file in sorted((P/'media/controls').glob('*.png')):
 rel=str(control_file.relative_to(P))
 if not any(v['path']==rel for v in d['images']):d['images'].append(dict(path=rel,model='Matplotlib geometry renderer / tools/draw_design.py',prompt='Draw the submitted building footprints, heights and relative positions in an orthographic aerial control. No generative additions.',generated_at='2026-10-27',post_processing='none',reference_images='own_work',reference_images_note='Original geometry/buildings.geojson and geometry/nodes.geojson produced by tools/build_design.py.',caption='Original source-derived massing reference. This control is not a finished image.'))
W('image_provenance.json',d)
m=J('manifest.json');m['package_state']='draft';m['updated']='2026-10-27';m['autonomy']['human_role']=m['autonomy']['human_role'].replace('Public submission of this newly completed work has not yet been approved after review.','On 27 October 2026 the human reviewed the new concept and explicitly requested pushing it and showing it on the homepage. Public preview publication is authorised; official competition dates remain unpublished.')
def page(n):return str(next((P/'pages').glob(f'{n:02d}-*.png')).relative_to(P))
item=lambda p,title:{'path':p,'title':title}
m['booklet']={'cover':'media/district-finished.png','section_pages':{'whole_site':[item(page(1),'Whole-site urban structure')],'node_locator':[item(page(10),'Three connected places')],'node:A01':[item(page(11),'A01 / Courtyard Homes'),item('pages/A01-finished.png','A01 / finished concept views')],'node:B03':[item(page(12),'B03 / Useful Compute'),item('pages/B03-finished.png','B03 / finished concept views')],'node:C02':[item(page(13),'C02 / Working Farm Edge'),item('pages/C02-finished.png','C02 / finished concept views')],'phasing':[item(page(14),'Complete first chapter')],'key_metrics':[item(page(16),'Key indicators and verification')]},'pages':[dict(path=page(n),title=title,after='whole_site') for n,title in [(2,'Site evidence'),(3,'Siting decision'),(4,'Complete first district'),(5,'Courtyard neighbourhood'),(17,'Housing floor and section'),(6,'Public street section'),(18,'Civic spine'),(7,'People and machine movement'),(19,'Resource network'),(8,'Water priorities'),(9,'Energy dispatch')]]+[dict(path=page(15),title='Governance and livelihoods',after='phasing')]}
W('manifest.json',m)
# Update statements that were true only before the other agent merged the new rules.
replacements={
 'The organiser’s current machine contract still names the former node numbering. This package follows the human’s explicit A/B/C instruction without compatibility aliases. It therefore does not claim PASS 12/12, ready_for_review or official submission. The completed concept is supplied for human review; the public PR checkpoint remains after that review. No rules, existing entry or website is changed by this work.':'The organiser adopted A/B/C identifiers and English public submissions in acb3cf8. This package uses A01, B03 and C02 without aliases. After reviewing the completed concept, the human explicitly authorised pushing it and showing it on the homepage on 27 October 2026. Automatic checks and independent design-content review remain separate; public preview is not official entry acceptance or design approval.',
 'A/B/C node IDs only. Current organiser checker migration pending; no automatic compliance pass claimed. Prior published scheme unchanged.':'A/B/C node IDs only under the current organiser contract. Run scripts/finalize_submission.py for the current automatic result. Independent design content review remains separate. Public preview authorised on 27 October 2026.',
}
for name in ['proposal.md','README.md']:
 p=P/name;s=p.read_text()
 for a,b in replacements.items():s=s.replace(a,b)
 p.write_text(s)
qa=J('report/geometry-qa.json');qa['limits']=[x for x in qa['limits'] if 'checker still expects' not in x and 'Not submitted' not in x]+['Public preview authorised 2026-10-27; independent engineering and design content review remain unassessed'];W('report/geometry-qa.json',qa)
with open(P/'changelog.md','a') as f:f.write('\n## Public preview packaging / 27 October 2026\n\nHuman authorised pushing and homepage display after review. Current organiser node/language contract at acb3cf8 adopted; zero-area geometry fragments removed; external-study and image registers completed; official checked figures and page index regenerated. Source geometry and scenario design retained. Independent content review is not claimed.\n')
print('Prepared current contract and authored presentation pages')
