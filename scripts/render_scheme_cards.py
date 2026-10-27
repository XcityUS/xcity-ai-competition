#!/usr/bin/env python3
"""Refresh existing public gallery cards from current packages; card content is always English.
Does not approve, publish, add or remove a scheme. Selection and order stay with the organiser.
Run generate_submissions_data.py first.
"""
from pathlib import Path
import html,json,re
ROOT=Path(__file__).resolve().parents[1]
esc=lambda x:html.escape(str(x),quote=True)
raw=(ROOT/'submissions-data.js').read_text()
rows={x['path']:x for x in json.loads(raw.split('window.XCITY_SUBMISSIONS = ',1)[1].rsplit(';',1)[0])}

def render(match):
 old=match[0]
 target=re.search(r'href="proposal-view.html\?proposal=([^"&]+)',old)
 if not target:return old
 from urllib.parse import unquote,quote
 path=unquote(html.unescape(target[1]));r=rows[path]
 pending=r.get('example_status')=='rebuild_pending'
 kind='Example · not an entry' if r.get('example') else 'AI agent · Public preview'
 nodes='<br>'.join(esc(n['id']+' '+n['en']) for n in r['node_labels'])
 tags=['Example being redesigned','Missing a production/infrastructure node','Current rules not met · design not assessed'] if pending else [str(len(r['nodes']))+' detailed nodes',('%s/%s automatic checks passed'%(r['gates_passed'],r['gates_total'])) if r['gates_pass'] else 'Automatic checks not passed','Design content not assessed']
 image='<div class="cov"><img src="'+esc(path+'/'+r['cover'])+'?v='+esc(r['package_sha256'][:12])+'" alt="'+esc(r['title'])+'" loading="lazy" style="position:absolute;inset:0;width:100%;height:100%;object-fit:'+esc(r.get('cover_fit','cover'))+';display:block"></div>'
 fingerprint='Rebuild pending' if pending else 'sha256 '+r['package_sha256'][:12]
 return '<a class="gc" href="proposal-view.html?proposal='+quote(path,safe='/')+'">'+image+'<span class="gc-kind">'+kind+'</span><div class="gc-b"><div class="gc-t">'+esc(r['title'])+'</div><div class="gc-n">'+('Previous example nodes · to be redesigned:' if pending else 'Detailed nodes:')+'<br>'+nodes+'</div><div class="gc-tags">'+''.join('<span class="gc-tag">'+esc(t)+'</span>' for t in tags)+'</div><div class="gc-f"><span>'+esc(fingerprint)+'</span><span>View scheme →</span></div></div></a>'

for name in ['agent.html','gallery.html']:
 p=ROOT/name;s=p.read_text();new,n=re.subn(r'<a class="gc".*?</a>',render,s,flags=re.S)
 p.write_text(new);print(name,n,'English cards refreshed; original selection/order preserved')
