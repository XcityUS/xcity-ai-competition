"""Register actual custom-authoring outputs and inputs; never impersonates make_figures.py."""
from pathlib import Path
import json,hashlib,shutil,sys
from pypdf import PdfReader,PdfWriter
P=Path(__file__).resolve().parents[1];R=P.parents[2];O=P/'reviews/redesign-v2';D=O/'diagrams';sys.path.insert(0,str(R/'scripts'));import xcity_common as xc
figmap={'fig-01-structure.png':'whole-site.png','fig-02-master-plan.png':'city-composite.png','fig-03-land-use-density.png':'city-composite.png','fig-04-movement.png':'city-mobility.png','fig-05-open-space-water.png':'city-landscape.png','fig-06-phasing.png':'city-phasing.png','fig-08-node-location.png':'system-layout.png'}
for dest,src in figmap.items():shutil.copy2(D/src,P/'figures'/dest)
for nid in ['A01','B03','C02']:
 shutil.copy2(D/(nid+'-plan.png'),P/'figures'/f'node-{nid}-plan.png')
 for view in ['aerial','eye']:shutil.copy2(P/'media/v2'/f'{nid}-{view}.png',P/'figures'/f'node-{nid}-{view}.png')
# Report text and root metadata are completed before this input identity is calculated.
h=xc.figure_input_hash(str(P));outputs=xc.REQUIRED_FIGURES+['figures/fig-08-node-location.png','drawings/a3-booklet.pdf','drawings/a0-board.pdf','drawings/a3-technical-appendix.pdf','drawings/presentation-index.json']+[f'figures/node-{n}-{v}.png' for n in ['A01','B03','C02'] for v in ['plan','aerial','eye']]
for rel in ['drawings/a3-booklet.pdf','drawings/a0-board.pdf','drawings/a3-technical-appendix.pdf']:
 path=P/rel;reader=PdfReader(path);writer=PdfWriter();writer.append_pages_from_reader(reader);writer.add_metadata({**dict(reader.metadata or {}),'/Keywords':'input-sha256:'+h+' custom-authoring:Everyday-City-V2','/Subject':'Geometry-linked public preview; design content not independently assessed'});tmp=path.with_suffix('.tmp.pdf');writer.write(tmp);tmp.replace(path)
record=dict(script='tools/register_artifacts_v2.py',script_version='Everyday-City-V2',input_sha256=h,generated_at='2026-10-27',actual_authoring_scripts=['tools/redesign_v2.py','tools/diagrams_v2.py','tools/scene_v2.py','scripts/render_views.py','tools/publish_v2.py'],note='Actual custom drawing/PDF output provenance. No claim that organiser make_figures.py authored the design; no design approval.',files={r:xc.sha256_file(str(P/r)) for r in outputs})
(P/'figures/stamp.json').write_text(json.dumps(record,indent=2));(O/'artifact-build-record.json').write_text(json.dumps(record,indent=2))
out=R.parents[1]/'outputs/everyday-city-v2'
for rel,name in [('drawings/a3-booklet.pdf','everyday-city-v2-booklet.pdf'),('drawings/a0-board.pdf','everyday-city-v2-a0.pdf'),('drawings/a3-technical-appendix.pdf','everyday-city-v2-technical-appendix.pdf')]:shutil.copy2(P/rel,out/name)
print('Registered actual custom-authoring input',h)
