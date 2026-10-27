#!/usr/bin/env python3
"""Cross-file contracts; validates explicit references, never design quality."""
import json,re,hashlib
from pathlib import Path
import jsonschema
ROOT=Path(__file__).resolve().parents[1]
def read(rel):return (ROOT/rel).read_text()
def data(rel):return json.loads(read(rel))
def check():
 errors=[]
 def need(ok,msg):
  if not ok:errors.append(msg)
 for schema_file in (ROOT/'schema').glob('*.json'):
  try:jsonschema.Draft202012Validator.check_schema(json.loads(schema_file.read_text()))
  except (ValueError,jsonschema.SchemaError) as e:errors.append(schema_file.name+': '+str(e))
 depth=data('brief/design-depth.json');req=data('brief/requirements.json')
 need(req['design_depth']==depth,'requirements/design-depth machine twins differ')
 need([x['id'] for x in depth['levels']]==['whole_site','phase_one','urban_design','nodes'],'four design levels changed')
 for payload,schema in [('brief/requirements.json','schema/requirements.schema.json'),('brief/agent_taskbook.json','schema/agent_taskbook.schema.json'),('templates/design_depth_matrix.json','schema/design_depth_matrix.schema.json'),('brief/site-package/evidence-index.json','schema/site-evidence.schema.json')]:
  for e in jsonschema.Draft202012Validator(data(schema)).iter_errors(data(payload)):errors.append(payload+': '+e.message)
 p=data('brief/practice-schedule.json')
 need(p['registration_deadline']=='2026-12-31T23:59:59Z' and p['application_deadline']=='2027-01-31T23:59:59Z','practice deadlines differ from organiser decision')
 need(p['initial_ideas_max_pages']==10,'ideas page limit differs')
 need(p['materials_submission']=='private_online_application','practice materials flow is not private online link')
 for f in ['agent.html','practice.html']:
  text=read(f);need('id="interestForm"' not in text and '<section id="next"' not in text,f+': duplicate updates entry')
 need(read('index.html').count('name="tracks"')==2,'homepage must offer two update preferences')
 text=read('agent.html');need('带讲解的成果对照' not in text,'removed public reference button returned');need('express-grid' in text,'presentation grid wrapper missing')
 for old in ['自行划定</span>','Drawn by you</span>','the area you draw yourself']:
  need(old not in text,'ambiguous whole-site scope phrase: '+old)
 for f in ['AGENTS.md','docs/submission-guide.md','skills/xcity-agent-submission/SKILL.md','brief/design-requirements.en.md']:
  need(not re.search(r'at least (?:1,500|1500) words',read(f)),f+': removed minimum word count returned')
 sources={x['id'] for x in data('brief/site-package/sources.json')['sources']}
 for r in data('brief/site-package/evidence-index.json')['resources']:
  need((ROOT/'brief/site-package'/r['path']).is_file(),'missing evidence resource '+r['path'])
  need(set(r['source_ids'])<=sources,'unknown source in '+r['path'])
 need('agriculture' not in req['fixed_pilot_context']['living']['land_use_labels'],'living pilot mislabelled agriculture')
 nodes=data('brief/site-package/nodes/design_nodes.json')
 need(len(nodes['groups'])==3,'node groups not three')
 expected={'A01','A02','A03','B01','B02','B03','C01','C02','C03','C04'}
 need({n['id'] for n in nodes['nodes']}==expected,'node catalogue differs from A/B/C policy')
 need('legacy_submissions' not in nodes,'removed node-selection compatibility returned')
 for f in ['AGENTS.md','README.md','docs/submission-guide.md','brief/public-brief.en.md','brief/design-requirements.en.md']:
  need('retain the previous any-three' not in read(f),f+': removed node-selection exception returned')
 need(data('schema/manifest.schema.json')['properties']['language'].get('const')=='en','final public submission language must be English')
 need(req.get('public_submission_language',{}).get('code')=='en','machine language policy missing')
 for f in ['agent.html','gallery.html']:
  for card in re.findall(r'<a class="gc".*?</a>',read(f),re.S):
   need(not re.search('[\u4e00-\u9fff]',card),f+': public scheme card is not English-only')
 for f in ['public-brief','design-requirements']:
  need((ROOT/('brief/'+f+'.zh.md')).is_file(),'missing Chinese counterpart '+f)
 return errors
if __name__=='__main__':
 errors=check()
 print('\n'.join('FAIL: '+e for e in errors) if errors else 'PASS: bilingual entry points, scope policy, schedules, schema, pilot semantics, metadata and update preferences agree.')
 raise SystemExit(bool(errors))
