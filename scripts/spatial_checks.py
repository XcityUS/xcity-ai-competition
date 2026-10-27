"""Deterministic geometry checks. No suitability or urban-design quality inference."""
from pathlib import Path
import json
import jsonschema
from shapely.ops import unary_union
import xcity_common as xc

def modern(package):
    try:return json.loads((Path(package)/'design_depth_matrix.json').read_text()).get('schema_version') == 2
    except (OSError, ValueError, AttributeError):return False

def partition_problems(geo):
    errors=[]
    if not geo.get('master_area') or not geo.get('land_use'):return errors
    master=xc.to_utm(unary_union([g for _,g in geo['master_area']]))
    pieces=[xc.to_utm(g) for _,g in geo['land_use']]
    # Vector bookkeeping tolerance, not survey accuracy: 100 m² or 0.01% of master area.
    tolerance=max(100.,master.area*0.0001)
    combined=unary_union(pieces)
    overlap=sum(g.area for g in pieces)-combined.area
    missing=master.difference(combined).area
    if overlap>tolerance:errors.append('land_use partition overlaps by %.1f m² (bookkeeping tolerance %.1f m²)'%(overlap,tolerance))
    if missing>tolerance:errors.append('land_use partition omits %.1f m² of master area (bookkeeping tolerance %.1f m²)'%(missing,tolerance))
    return errors

def context_errors(package):
    errors=[];p=Path(package)
    for file in sorted((p/'context').glob('*.geojson')):
        try:
            d=json.loads(file.read_text())
            schema=json.loads((Path(xc.ROOT)/'schema/context.schema.json').read_text())
            for issue in jsonschema.Draft202012Validator(schema).iter_errors(d):errors.append(file.name+': context schema: '+issue.message)
            if d.get('type')!='FeatureCollection' or not isinstance(d.get('features'),list):raise ValueError('expected FeatureCollection')
            for i,f in enumerate(d['features']):
                props=f.get('properties') or {}
                if props.get('status')!='study_only' or props.get('authority')!='not_secured':errors.append(f'{file.name} feature {i}: context must be study_only / not_secured')
                if not props.get('basis'):errors.append(f'{file.name} feature {i}: explain the evidence or assumption in basis')
                from shapely.geometry import shape
                g=shape(f['geometry'])
                if g.is_empty or not g.is_valid:errors.append(f'{file.name} feature {i}: invalid context geometry')
        except (OSError,ValueError,TypeError,KeyError,AttributeError) as e:errors.append(file.name+': unreadable context: '+str(e))
    return errors
