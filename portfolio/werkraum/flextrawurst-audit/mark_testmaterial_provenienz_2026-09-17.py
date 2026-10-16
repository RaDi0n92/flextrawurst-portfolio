import json
from datetime import datetime, timezone
from pathlib import Path
import psycopg2
import psycopg2.extras

uri = None
for line in Path('/root/werkraum/.agent/flextrawurst-db.env').read_text(encoding='utf-8').splitlines():
    if line.startswith('FLEXTRAWURST_DB_URI='):
        uri = line.split('=', 1)[1].strip().strip('"').strip("'")
        break
if not uri:
    raise RuntimeError('FLEXTRAWURST_DB_URI fehlt')

conn = psycopg2.connect(uri, cursor_factory=psycopg2.extras.RealDictCursor)
conn.autocommit = False
result = {}
try:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT count(*) AS total,
                   count(*) FILTER (WHERE autor_type='entity') AS entity_posts,
                   count(*) FILTER (WHERE autor_type='human') AS human_posts,
                   count(*) FILTER (WHERE ist_voreinzug IS TRUE) AS voreinzug,
                   count(*) FILTER (WHERE COALESCE(meta->>'provenienz_klasse','')='testmaterial') AS already_marked
            FROM ftw_posts
        """)
        before = dict(cur.fetchone())
        result['before'] = before
        expected = {'total': 46, 'entity_posts': 19, 'human_posts': 27, 'voreinzug': 46}
        for key, value in expected.items():
            if int(before[key]) != value:
                raise RuntimeError(f'Abbruch: {key}={before[key]}, erwartet {value}')

        marker = {
            'provenienz_klasse': 'testmaterial',
            'testmaterial_ohne_inhaltliche_bedeutung': True,
            'provenienz_bestaetigung': 'user_confirmed',
            'provenienz_korrektur_at': datetime.now(timezone.utc).isoformat(),
        }
        cur.execute("""
            UPDATE ftw_posts
            SET meta = COALESCE(meta, '{}'::jsonb) || %s
            WHERE COALESCE(meta->>'provenienz_klasse','') IS DISTINCT FROM 'testmaterial'
        """, (psycopg2.extras.Json(marker),))
        result['updated'] = cur.rowcount

        cur.execute("""
            SELECT count(*) AS total,
                   count(*) FILTER (WHERE meta->>'provenienz_klasse'='testmaterial') AS marked,
                   count(*) FILTER (WHERE (meta->>'testmaterial_ohne_inhaltliche_bedeutung')::boolean IS TRUE) AS no_content_significance,
                   count(*) FILTER (WHERE ist_voreinzug IS TRUE) AS voreinzug,
                   count(*) FILTER (WHERE sichtbarkeit='public') AS public_count
            FROM ftw_posts
        """)
        after = dict(cur.fetchone())
        result['after'] = after
        if not (int(after['total']) == int(after['marked']) == int(after['no_content_significance']) == int(after['voreinzug']) == int(after['public_count']) == 46):
            raise RuntimeError(f'Abbruch: Nachzustand unerwartet: {after}')

    conn.commit()
    result['committed'] = True
except Exception:
    conn.rollback()
    result['committed'] = False
    raise
finally:
    conn.close()

print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
