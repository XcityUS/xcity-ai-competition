"""Presentation packaging checks; never a design-quality assessment."""
import json
from pypdf import PdfReader
from pypdf.errors import PyPdfError
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
POLICY=json.loads((ROOT/'brief/presentation-requirements.json').read_text())
INDEX='drawings/presentation-index.json'
APPENDIX='drawings/a3-technical-appendix.pdf'
LOCATOR='figures/fig-08-node-location.png'

def applies(package):
 p=Path(package).resolve()
 return p not in {(ROOT/x).resolve() for x in POLICY['legacy_submissions']} or (p/INDEX).exists()

def required_outputs(package):
 return [APPENDIX,INDEX,LOCATOR] if applies(package) else []

def index_errors(package,nodes):
 p=Path(package).resolve()
 if not applies(p):return []
 errors=[]
 try:
  doc=json.loads((p/INDEX).read_text())
  if not isinstance(doc,dict) or doc.get('schema_version')!=1:raise ValueError('unsupported presentation index')
  counts={}
  for key,rel in [('main','drawings/a3-booklet.pdf'),('technical',APPENDIX)]:
   item=doc.get('documents',{}).get(key,{})
   if item.get('path')!=rel:errors.append('presentation index must identify '+rel)
   counts[key]=len(PdfReader(p/rel).pages)
   if type(item.get('pages')) is not int or item['pages']!=counts[key]:errors.append(rel+': indexed page count does not match PDF')
  sections=doc.get('sections',[])
  if not isinstance(sections,list):raise ValueError('sections must be a list')
  required=['whole_site','node_locator']+['node:'+n for n in nodes]+['phasing','key_metrics']
  last=0
  for name in required:
   found=[x for x in sections if isinstance(x,dict) and x.get('id')==name]
   if len(found)!=1:errors.append('presentation needs exactly one section '+name);continue
   item=found[0];pages=item.get('pages')
   if item.get('document')!='main' or not isinstance(pages,list) or not pages or any(type(n)is not int or n<1 or n>counts['main'] for n in pages):
    errors.append(name+': invalid main-booklet page range');continue
   if pages!=sorted(set(pages)) or pages[0]<=last:errors.append(name+': section pages must follow the required reading order without overlap')
   last=max(pages)
 except (OSError,ValueError,TypeError,AttributeError,KeyError,PyPdfError) as e:
  errors.append('presentation index/PDF cannot be read: '+str(e))
 return errors
