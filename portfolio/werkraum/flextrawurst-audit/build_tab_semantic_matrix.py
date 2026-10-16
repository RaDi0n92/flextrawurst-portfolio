from bs4 import BeautifulSoup
from pathlib import Path
import json,re

html_path=Path('/tmp/ftw-surface-patched/out/process_camera/flextrawurst_surface_public.html')
h=html_path.read_text(encoding='utf-8',errors='replace')
soup=BeautifulSoup(h,'html.parser')
admin={'admin','leitstand','weltstrom','raume','suche','splitter','zitate','schatten','gruppen','vaulteinblick','codegeil','guardianstyle'}
entityadmin={'gordslider','gespraech','rag'}
loginuser={'meinewelt'}
arch={'codearchaeologie','codegeil','guardianstyle','systemweitearchaeologie'}
rows=[]
for i,a in enumerate(soup.select('a.v-tab'),1):
    v=a.get('data-view') or ''
    label=' '.join(a.stripped_strings)
    el=soup.find(id='view-'+v) or soup.find(id='v-'+v)
    txt=' '.join(el.stripped_strings) if el else ''
    scripts='\n'.join((sc.string or sc.get_text() or '') for sc in el.find_all('script')) if el else ''
    fetches=[]
    for m in re.finditer(r"fetch\(([^\n;]{1,240})",scripts):
        frag=m.group(1).strip()
        if frag not in fetches: fetches.append(frag)
    hrefs=[]
    if el:
      for x in el.find_all('a',href=True):
        href=x.get('href','')
        if href and href not in hrefs: hrefs.append(href)
    iframes=[]
    if el:
      for x in el.find_all('iframe'):
        src=x.get('src','')
        if src: iframes.append(src)
    access='PUBLIC'
    if v in admin: access='ADMIN_OR_KEY'
    elif v in entityadmin: access='ENTITY_OR_ADMIN'
    elif v in loginuser: access='LOGIN_USER'
    elif v in arch: access='ARCH_PUBLIC'
    status_terms=[]
    for term in ['LIVE','VOR-EINZUG','BLOCKIERT','GEPLANT','AKTIV','inaktiv','Test','Archiv','experimentell','EXPERIMENTELL']:
      if term.lower() in txt.lower(): status_terms.append(term)
    rows.append({
      'n':i,'label':label,'view':v,'tab_href':a.get('href'),'inline_display':a.get('style',''),
      'access':access,'static_chars':len(txt),'text_preview':txt[:1500],
      'headings':[' '.join(x.stripped_strings) for x in el.find_all(['h1','h2','h3'])][:20] if el else [],
      'links_count':len(el.find_all('a')) if el else 0,'hrefs':hrefs[:80],
      'buttons':len(el.find_all('button')) if el else 0,'forms':len(el.find_all('form')) if el else 0,
      'iframes':iframes,'fetch_fragments':fetches[:80],'status_terms':status_terms,
      'has_real_tab_url': bool((a.get('href') or '').startswith('/') or (a.get('href') or '').startswith('http')),
    })
out={'source':str(html_path),'count':len(rows),'tabs':rows}
Path('/root/werkraum/flextrawurst-audit/tab_semantic_raw.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print('count',len(rows))
for r in rows:
  print(f"{r['n']:02d} {r['label'][:30]:30} {r['view']:<22} {r['access']:<16} chars={r['static_chars']:6} links={r['links_count']:3} fetch={len(r['fetch_fragments']):2} iframe={len(r['iframes']):1} href={r['tab_href']}")
