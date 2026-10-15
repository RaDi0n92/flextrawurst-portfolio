#!/usr/bin/env python3
from pathlib import Path
import html,json,hashlib,datetime as dt
ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'site'
langs={
 'de':{'title':'WorldWORDS ANTIBIBEL','accepted':'Offizielles Register','proposals':'Öffentliches Sammelbecken','status':'Status','origin':'Herkunft','definition':'Erklärung','not':'Bedeutet ausdrücklich nicht','contrib':'Mitwirken','gov':'Governance','hero':'Rohformen bleiben roh. Erklärungen wandern durch Sprachen. Aufnahmeentscheidungen bleiben prüfbar.'},
 'en':{'title':'WorldWORDS ANTIBIBEL','accepted':'Official registry','proposals':'Public intake pool','status':'Status','origin':'Provenance','definition':'Explanation','not':'Explicitly does not mean','contrib':'Contribute','gov':'Governance','hero':'Raw forms stay raw. Explanations travel across languages. Admission stays traceable.'},
 'es':{'title':'WorldWORDS ANTIBIBEL','accepted':'Registro oficial','proposals':'Zona pública de propuestas','status':'Estado','origin':'Procedencia','definition':'Explicación','not':'No significa expresamente','contrib':'Contribuir','gov':'Gobernanza','hero':'Las formas brutas siguen brutas. Las explicaciones viajan entre idiomas. La admisión permanece trazable.'}
}
css='''body{font-family:system-ui,sans-serif;max-width:1100px;margin:auto;padding:2rem;line-height:1.55;background:#f4f0e8;color:#191817}a{color:inherit}nav{display:flex;gap:1rem;flex-wrap:wrap;border-bottom:1px solid;padding-bottom:1rem}.hero{padding:3rem 0}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1rem}.card{background:#fff;border:1px solid #b8b0a4;border-radius:12px;padding:1.2rem}.raw{font-family:ui-monospace,monospace;background:#eee8dd;padding:.7rem;border-radius:8px;white-space:pre-wrap}.badge{display:inline-block;padding:.2rem .55rem;border:1px solid;border-radius:999px;font-size:.8rem}.accepted{background:#dcebd8}.submitted{background:#eee1c9}.meta{font-size:.88rem;color:#555}footer{margin-top:4rem;border-top:1px solid;padding-top:1rem}'''
terms=[json.loads(p.read_text()) for p in sorted((ROOT/'data/terms').glob('*.json'))]
props=[json.loads(p.read_text()) for p in sorted((ROOT/'data/proposals').glob('*.json'))]
for lang,t in langs.items():
    out=SITE/lang;out.mkdir(parents=True,exist_ok=True)
    cards=[]
    for record in terms:
        de=record['definitions'][lang]
        values=record.get('not_meant',{}).get(lang,[])
        nots=''.join(f'<li>{html.escape(x)}</li>' for x in values) if isinstance(values,list) else ''
        origin=record['origin']; contrib=', '.join(origin.get('contributors',[])); date=origin.get('first_seen',{}).get('date') or 'unknown'
        cards.append(f'''<article class="card"><span class="badge accepted">accepted</span><h3>{html.escape(record['canonical_form'])}</h3><p>{html.escape(de.get('short',''))}</p><p>{html.escape(de.get('long',''))}</p><details><summary>{t['origin']}</summary><p class="meta">{html.escape(contrib)} · {html.escape(str(date))} · {html.escape(origin.get('authorship_status',''))}</p><div class="raw">{html.escape(origin.get('exact_input',''))}</div></details>{('<h4>'+t['not']+'</h4><ul>'+nots+'</ul>') if nots else ''}</article>''')
    pcards=[]
    for d in props:
        pdef=d['definitions'][lang]['provisional']; date=d['first_seen'].get('date') or 'unknown'
        pcards.append(f'''<article class="card"><span class="badge submitted">submitted</span><h3>{html.escape(d['raw_form'])}</h3><p>{html.escape(pdef)}</p><p class="meta">{html.escape(str(d['submitted_by']))} · {html.escape(str(date))} · {html.escape(d['authorship_status'])}</p><details><summary>{t['origin']}</summary><div class="raw">{html.escape(d['exact_input'])}</div></details></article>''')
    nav=' '.join(f'<a href="../{x}/index.html">{x.upper()}</a>' for x in langs)
    page=f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>{t['title']}</title><style>{css}</style></head><body><nav>{nav}<a href="../../README.{lang}.md">README</a><a href="../../GOVERNANCE.{lang}.md">{t['gov']}</a><a href="../../CONTRIBUTING.{lang}.md">{t['contrib']}</a></nav><header class="hero"><h1>{t['title']}</h1><p>{html.escape(t['hero'])}</p></header><h2>{t['accepted']}</h2><main class="grid">{''.join(cards)}</main><h2>{t['proposals']}</h2><section class="grid">{''.join(pcards)}</section><footer>Version {json.loads((ROOT/'project.json').read_text())['version']} · CC BY-SA 4.0 / MIT</footer></body></html>'''
    (out/'index.html').write_text(page,encoding='utf-8')
(SITE/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>WorldWORDS ANTIBIBEL</title><h1>WorldWORDS ANTIBIBEL</h1><p><a href="de/index.html">Deutsch</a> · <a href="en/index.html">English</a> · <a href="es/index.html">Español</a></p>',encoding='utf-8')
