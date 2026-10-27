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
 operating=depth['operational_design']
 need(operating['compute_built_form']=='industrial_data_centre_halls_with_modular_construction_and_equipment' and operating['standalone_container_array_is_required'] is False,'confirmed modular hall form differs')
 for language in ['en','zh']:
  reference=operating['reference_'+language]
  need((ROOT/reference).is_file(),'missing operating conditions: '+reference)
  need(('production-conditions.'+language+'.md') in read('brief/design-requirements.'+language+'.md'),'missing bilingual operating reference')
 need(data('brief/agent_taskbook.json')['operating_conditions_ref']==operating['reference_en'],'taskbook operating reference differs')
 for key in ['compute_campus_requires_shared_infrastructure_and_gap_reasoning','power_block_is_not_it_load','phasing_requires_spatial_diagrams_not_dates_only','seasonal_park_requires_public_use_access_and_closure_design']:
  need(operating[key] is True,'missing operational content criterion: '+key)
 need(not operating['universal_spacing_or_coverage_ratio_prescribed'] and not operating['new_render_quota'],'unapproved numeric or render quota')
 catalogue={n['id']:n for n in data('brief/site-package/nodes/design_nodes.json')['nodes']}
 for code in ['B03','C02','C03']:
  need(catalogue[code].get('brief_zh') and catalogue[code].get('operating_conditions_ref')==operating['reference_en'],'node operating explanation missing: '+code)

 planting=req['fixed_pilot_context']['agrivoltaic']['under_panel_planting']
 need({c['id'] for c in planting['crops']}=={'forage_grass','jojoba'} and planting['retain_both'],'fixed under-panel crops differ')
 need(depth['construction_programme']['a0_map_required'],'A0 construction phasing map missing')
 need(req['design_depth']==depth,'requirements/design-depth machine twins differ')
 overview=next(value['overall_spatial_view'] for value in depth.values() if isinstance(value,dict) and 'overall_spatial_view' in value)
 need(overview['production_led_territorial_structure_required'] and overview['housing_only_view_is_not_overall_view'] and not overview['large_residential_aerial_is_default_deliverable'],'overall/local image hierarchy differs')
 representation=depth['representation_evidence']
 for key in ['procedural_planting_default','procedural_pv_default','illustrative_entourage_default','illustration_is_capacity_evidence']:
  need(representation[key] is False,'unsubstantiated scene evidence policy: '+key)
 for key in ['roof_pv_requires_explicit_building_property','water_channel_requires_explicit_design_property','scene_policy_and_renderer_in_cache_fingerprint','visual_geometry_review_required']:
  need(representation[key] is True,'missing rendering evidence safeguard: '+key)
 for f in ['brief/design-requirements.zh.md','scripts/practice-brief/build_zh.py']:
  need('| 首期完整城区 |' not in read(f) and "['一期总体城市设计'," not in read(f),f+': phase-one-only design scope returned')
 for f in ['scripts/practice-brief/build_en.py']:
  need("['Phase 1 urban design'," not in read(f),f+': phase-one-only design scope returned')
 need([x['id'] for x in depth['levels']]==['whole_site','overall_layout','urban_design','nodes'],'four design levels changed')
 whole=depth['whole_site_plan']
 need(whole['base_covers_entire_issued_site'] and whole['base_area_account_exclusive'] and whole['network_is_not_road_hierarchy'],'whole-site zoning/road contract differs')
 need((ROOT/'docs/whole-site-zoning-workflow.md').is_file(),'whole-site workflow missing')
 need((ROOT/whole['method_skill']).is_file(),'city-design method skill missing')
 board=depth['a0_presentation']
 need(board['visual_first'] and board['calculations_still_required'] and not board['dense_district_phase_tables_on_board'],'A0 visual/account separation differs')
 diagrams=depth['city_system_diagrams']
 need({x['id'] for x in diagrams['themes']}=={'planning_structure','functional_programme','street_mobility','ecology_landscape','land_use','public_space_services'},'city diagram themes differ from organiser instruction')
 need(diagrams['shared_city_geometry_required'] and diagrams['separation_is_not_an_objective'],'city diagrams lost layout/adjacency basis')
 need(diagrams['fixed_page_count'] is False and diagrams['combined_drawings_allowed'],'fixed diagram page quota returned')
 need(diagrams['district_function_land_use_and_phase_distinguished'] and diagrams['renders_cannot_replace_required_planning_evidence'],'planning evidence or spatial-unit distinction lost')
 need((ROOT/diagrams['method_reference']).is_file(),'official method reference guide missing')
 overview=diagrams['overall_spatial_view']
 need(overview['required'] and overview['same_layout_as_plans'] and overview['frame_does_not_require_all_nodes_to_be_visible'],'overall city view policy differs')
 need((ROOT/'docs/city-system-diagrams.md').is_file(),'city diagram guide missing')
 spatial=depth['spatial_relationships']
 for key in ['node_colocation_required','all_nodes_in_urban_design_enlargement_required','all_nodes_in_master_area_required','single_contiguous_phase_one_required','render_view_determines_design_extent']:
  need(spatial[key] is False,'removed spatial freedom: '+key)
 need(spatial['main_entrance_topic']=='C01' and spatial['main_entrance_in_overall_plan_required'],'main access omitted from overall plan')
 need(data('brief/site-package/nodes/design_nodes.json')['spatial_relationships']==spatial,'node catalogue spatial policy differs')
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
