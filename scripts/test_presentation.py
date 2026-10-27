import json,tempfile,unittest
from pathlib import Path
from pypdf import PdfWriter
from presentation import index_errors,applies,POLICY,ROOT
class PresentationTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.p=Path(self.tmp.name);(self.p/'drawings').mkdir();self.nodes=['B03','C03','A03']
  for name,count in [('a3-booklet.pdf',9),('a3-technical-appendix.pdf',2)]:
   w=PdfWriter()
   for _ in range(count):w.add_blank_page(width=842,height=595)
   w.write(self.p/'drawings'/name)
  self.d={'schema_version':1,'documents':{'main':{'path':'drawings/a3-booklet.pdf','pages':9},'technical':{'path':'drawings/a3-technical-appendix.pdf','pages':2}},'sections':[{'id':n,'document':'main','pages':[i+2]} for i,n in enumerate(['whole_site','node_locator']+['node:'+n for n in self.nodes]+['phasing','key_metrics'])]}
 def tearDown(self):self.tmp.cleanup()
 def check(self):
  (self.p/'drawings/presentation-index.json').write_text(json.dumps(self.d));return index_errors(self.p,self.nodes)
 def test_valid_and_missing_section(self):
  self.assertEqual(self.check(),[]);self.d['sections'].pop(1);self.assertTrue(any('node_locator' in e for e in self.check()))
 def test_reordered_nodes_or_overlapping_pages_fail(self):
  self.d['sections'][2]['pages']=[7];self.assertTrue(any('order' in e for e in self.check()))
 def test_counts_checked_against_real_pdfs(self):
  self.d['documents']['main']['pages']=100;self.assertTrue(any('count' in e for e in self.check()))
 def test_corrupt_pdf_reported_not_crash(self):
  (self.p/'drawings/a3-booklet.pdf').write_bytes(b'not a PDF');self.assertTrue(self.check())
 def test_legacy_is_exact_path_not_self_declared(self):
  self.assertFalse(applies(ROOT/POLICY['legacy_submissions'][0]));self.assertTrue(applies(self.p));self.assertTrue(applies(ROOT/'submissions/EXAMPLE-agent/other-scheme'))

class CustomPageTests(unittest.TestCase):
 def test_custom_page_changes_are_hashed_and_paths_are_confined(self):
  from PIL import Image
  from types import SimpleNamespace
  import xcity_common as xc
  import make_figures as mf
  with tempfile.TemporaryDirectory() as directory:
   p=Path(directory);(p/'pages').mkdir();Image.new('RGB',(160,100),'white').save(p/'pages/locator.png')
   man={'booklet':{'section_pages':{'node_locator':[{'path':'pages/locator.png','title':'My locator'}]}}};(p/'manifest.json').write_text(json.dumps(man))
   before=xc.figure_input_hash(str(p));Image.new('RGB',(160,100),'gold').save(p/'pages/locator.png');self.assertNotEqual(before,xc.figure_input_hash(str(p)))
   pkg=SimpleNamespace(dir=str(p),man=man,title='QA',title_zh='',login='QA',slug='custom',input_hash='0'*64)
   figures=mf.section_pages(pkg,'node_locator');self.assertEqual(len(figures),1)
   for fig in figures:mf.plt.close(fig)
   man['booklet']['section_pages']['node_locator']=[{'path':'../outside.png'}]
   with self.assertRaises(ValueError):mf.section_pages(pkg,'node_locator')

if __name__=='__main__':unittest.main()
