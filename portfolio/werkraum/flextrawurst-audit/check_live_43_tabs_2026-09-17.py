#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright

mode = sys.argv[1] if len(sys.argv) > 1 else 'anon'
token_path = Path('/tmp/ftw_audit_admin_token.txt')
out_path = Path(f'/root/werkraum/flextrawurst-audit/live_43_{mode}_runtime_2026-09-17.json')

page_errors=[]
console_errors=[]
responses=[]

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True)
    page=browser.new_page(viewport={'width':1440,'height':1000})
    page.on('pageerror', lambda e: page_errors.append({'error':str(e)}))
    page.on('console', lambda m: console_errors.append({'text':m.text}) if m.type=='error' else None)
    def on_response(r):
        u=r.url
        if '127.0.0.1' in u or 'flextrawurst.de' in u:
            responses.append({
                'url':u,
                'status':r.status,
                'method':r.request.method,
                'resourceType':r.request.resource_type,
            })
    page.on('response', on_response)
    if mode == 'admin':
        token=token_path.read_text(encoding='utf-8').strip()
        if not token:
            raise RuntimeError('admin token missing')
        # Python-Playwright add_init_script akzeptiert kein separates arg wie evaluate().
        # Token wird nur lokal in das Init-Script serialisiert und niemals ausgegeben.
        token_js = json.dumps(token)
        page.add_init_script(f"""
          (() => {{
            const token = {token_js};
            localStorage.setItem('ftw_token','Bearer '+token);
            localStorage.setItem('ftw_role','admin');
            localStorage.setItem('ftw_user','audit-admin');
            localStorage.setItem('ftw_user_id','audit-admin');
          }})();
        """)
    page.goto('http://127.0.0.1:8787/flextrawurst_surface.html', wait_until='domcontentloaded', timeout=30000)
    page.wait_for_timeout(800)
    tabs=page.locator('a.v-tab').evaluate_all("""as => as.map(a=>({label:(a.textContent||'').replace(/\\s+/g,' ').trim(),view:a.dataset.view||'',hidden:getComputedStyle(a).display==='none'}))""")
    out=[]
    for i,tab in enumerate(tabs, start=1):
        pe0=len(page_errors); ce0=len(console_errors); rq0=len(responses)
        click_error=None
        try:
            page.evaluate("""v=>{const a=[...document.querySelectorAll('a.v-tab')].find(x=>x.dataset.view===v); if(!a)throw new Error('tab missing'); a.click();}""", tab['view'])
        except Exception as e:
            click_error=str(e)
        page.wait_for_timeout(500)
        state=page.evaluate("""v=>{
          const el=document.getElementById('view-'+v)||document.getElementById('v-'+v);
          if(!el)return {exists:false};
          const txt=(el.innerText||'').replace(/\\s+/g,' ').trim();
          return {exists:true,display:getComputedStyle(el).display,active:el.classList.contains('active'),chars:txt.length,preview:txt.slice(0,800),iframes:el.querySelectorAll('iframe').length,links:el.querySelectorAll('a').length,buttons:el.querySelectorAll('button').length,forms:el.querySelectorAll('form').length};
        }""", tab['view'])
        rs=[x for x in responses[rq0:] if x['resourceType'] in ('fetch','xhr','document')]
        out.append({'n':i,**tab,**state,'hash':page.evaluate('location.hash'),'clickError':click_error,'pageErrors':page_errors[pe0:],'consoleErrors':console_errors[ce0:],'responses':rs})
    report={'mode':mode,'at':datetime.now(timezone.utc).isoformat(),'pageUrl':page.url,'tabs':out,'allPageErrors':page_errors,'allConsoleErrors':console_errors,'responseCount':len(responses)}
    out_path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    summary={
      'mode':mode,'count':len(tabs),'pageErrors':len(page_errors),'consoleErrors':len(console_errors),
      'tabs':[{'n':t['n'],'label':t['label'],'view':t['view'],'hidden':t['hidden'],'active':t.get('active'),'chars':t.get('chars'),
               'httpBad':[{'status':r['status'],'url':r['url']} for r in t['responses'] if r['status']>=400],
               'requests':[{'status':r['status'],'method':r['method'],'url':r['url']} for r in t['responses']],
               'preview':(t.get('preview') or '')[:120]} for t in out]
    }
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    browser.close()
