#!/usr/bin/env python3
import json
import re
from pathlib import Path
import psycopg2

API = Path('/root/werkraum/welt/api.py')
DB_ENV = Path('/root/werkraum/.agent/flextrawurst-db.env')

uri = None
for line in DB_ENV.read_text(encoding='utf-8').splitlines():
    if line.startswith('FLEXTRAWURST_DB_URI='):
        uri = line.split('=', 1)[1].strip().strip('"').strip("'")
        break
if not uri:
    raise RuntimeError('FLEXTRAWURST_DB_URI fehlt')

src = API.read_text(encoding='utf-8')
# Drei bekannte Post->Fürsorge-Pfade müssen jeweils Testmaterial explizit ausschließen:
# /resonanz, legacy /schattenkommentar, /welt/posts/{id}/schatten.
guard = 'post_meta.get("provenienz_klasse") != "testmaterial"'
guard_count = src.count(guard)
if guard_count != 3:
    raise AssertionError(f'erwartet 3 Testmaterial-Fürsorgeguards, gefunden {guard_count}')

conn = psycopg2.connect(uri)
try:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT count(*) AS total,
                   count(*) FILTER (WHERE ist_voreinzug IS TRUE) AS voreinzug,
                   count(*) FILTER (WHERE sichtbarkeit='public') AS public_count,
                   count(*) FILTER (WHERE meta->>'provenienz_klasse'='testmaterial') AS marked,
                   count(*) FILTER (WHERE (meta->>'testmaterial_ohne_inhaltliche_bedeutung')::boolean IS TRUE) AS no_significance
            FROM ftw_posts
        """)
        total, voreinzug, public_count, marked, no_significance = cur.fetchone()
        assert (total, voreinzug, public_count, marked, no_significance) == (46, 46, 46, 46, 46)

        cur.execute("""
            SELECT count(*) AS total,
                   count(*) FILTER (WHERE sk.entity_id IS NOT NULL AND p.autor_type='entity') AS entity_targets,
                   count(*) FILTER (WHERE sk.entity_id IS NULL AND p.autor_type='human') AS human_null,
                   count(*) FILTER (WHERE sk.entity_id IS NOT NULL AND sk.entity_id='GORD_prime') AS gord_prime_targets
            FROM schattenkommentare sk
            JOIN ftw_posts p ON p.id=sk.post_id
        """)
        shadows = cur.fetchone()
        assert shadows == (19, 9, 10, 2), shadows

        # Regressionsbeweis ohne neue Nutzerinteraktion: aktueller historische Fürsorgebestand
        # wird nur gemessen. Der Test selbst schreibt nichts in wesen_fuersorge.
        cur.execute("SELECT count(*) FROM wesen_fuersorge")
        care_count = cur.fetchone()[0]
finally:
    conn.close()

print(json.dumps({
    'ok': True,
    'api_guard_occurrences': guard_count,
    'posts': {
        'total': total,
        'voreinzug': voreinzug,
        'public': public_count,
        'testmaterial_marked': marked,
        'no_content_significance': no_significance,
    },
    'shadows': {
        'total': shadows[0],
        'entity_targets': shadows[1],
        'human_target_null': shadows[2],
        'gord_prime_test_targets': shadows[3],
    },
    'wesen_fuersorge_rows_observed': care_count,
    'db_writes_by_regression': 0,
}, ensure_ascii=False, indent=2))
