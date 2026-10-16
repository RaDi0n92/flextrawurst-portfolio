import json
import pathlib
import psycopg2
import psycopg2.extras

DB_ENV = pathlib.Path('/root/werkraum/.agent/flextrawurst-db.env')
DB_URI = None
for line in DB_ENV.read_text(encoding='utf-8').splitlines():
    if line.startswith('FLEXTRAWURST_DB_URI='):
        DB_URI = line.split('=', 1)[1].strip().strip('"').strip("'")
        break
if not DB_URI:
    raise RuntimeError('FLEXTRAWURST_DB_URI missing')

EXPECTED_POSTS = 46
EXPECTED_POSTS_TO_MARK = 46
EXPECTED_SHADOWS_TOTAL = 19
EXPECTED_SHADOWS_TO_BACKFILL = 9
EXPECTED_SHADOWS_HUMAN_POST = 10

result = {}
conn = psycopg2.connect(DB_URI, cursor_factory=psycopg2.extras.RealDictCursor)
conn.autocommit = False
try:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT
              COUNT(*) AS total,
              COUNT(*) FILTER (WHERE ist_voreinzug IS TRUE) AS voreinzug_true,
              COUNT(*) FILTER (WHERE ist_voreinzug IS DISTINCT FROM TRUE) AS to_mark,
              COUNT(*) FILTER (WHERE flarum_herkunft IS TRUE) AS flarum_true
            FROM ftw_posts
        """)
        before_posts = dict(cur.fetchone())
        result['before_posts'] = before_posts
        if int(before_posts['total']) != EXPECTED_POSTS:
            raise RuntimeError(f"Abbruch: erwartet {EXPECTED_POSTS} ftw_posts, gefunden {before_posts['total']}")
        if int(before_posts['to_mark']) != EXPECTED_POSTS_TO_MARK:
            raise RuntimeError(f"Abbruch: erwartet {EXPECTED_POSTS_TO_MARK} unmarkierte Vor-Einzug-Posts, gefunden {before_posts['to_mark']}")
        if int(before_posts['flarum_true']) != 0:
            raise RuntimeError(f"Abbruch: unerwartete flarum_herkunft=true: {before_posts['flarum_true']}")

        cur.execute("""
            SELECT
              COUNT(*) AS total,
              COUNT(*) FILTER (WHERE sk.entity_id IS NULL AND p.autor_type='entity') AS derivable,
              COUNT(*) FILTER (WHERE sk.entity_id IS NULL AND p.autor_type='human') AS human_keep_null,
              COUNT(*) FILTER (WHERE sk.entity_id IS NOT NULL) AS already_nonnull
            FROM schattenkommentare sk
            JOIN ftw_posts p ON p.id=sk.post_id
        """)
        before_shadows = dict(cur.fetchone())
        result['before_shadows'] = before_shadows
        if int(before_shadows['total']) != EXPECTED_SHADOWS_TOTAL:
            raise RuntimeError(f"Abbruch: erwartet {EXPECTED_SHADOWS_TOTAL} Schatten, gefunden {before_shadows['total']}")
        if int(before_shadows['derivable']) != EXPECTED_SHADOWS_TO_BACKFILL:
            raise RuntimeError(f"Abbruch: erwartet {EXPECTED_SHADOWS_TO_BACKFILL} ableitbare Entity-Schatten, gefunden {before_shadows['derivable']}")
        if int(before_shadows['human_keep_null']) != EXPECTED_SHADOWS_HUMAN_POST:
            raise RuntimeError(f"Abbruch: erwartet {EXPECTED_SHADOWS_HUMAN_POST} Human-Post-Schatten, gefunden {before_shadows['human_keep_null']}")
        if int(before_shadows['already_nonnull']) != 0:
            raise RuntimeError(f"Abbruch: bereits gesetzte entity_id unerwartet: {before_shadows['already_nonnull']}")

        # Reine Provenienzkorrektur: Das vorhandene Feld bedeutet laut Migration
        # 'Post wurde vor dem Einzug manuell angelegt'. Es steuert keine Sichtbarkeit.
        cur.execute("""
            UPDATE ftw_posts
            SET ist_voreinzug = TRUE
            WHERE ist_voreinzug IS DISTINCT FROM TRUE
        """)
        result['posts_updated'] = cur.rowcount
        if cur.rowcount != EXPECTED_POSTS_TO_MARK:
            raise RuntimeError(f"Abbruch: Post-Update traf {cur.rowcount} statt {EXPECTED_POSTS_TO_MARK}")

        # Bestehende enge Legacy-Korrektur: Nur Schatten auf Entity-Posts erhalten
        # das Zielwesen des Post-Autors. Schatten auf Human-Posts bleiben NULL.
        cur.execute("""
            UPDATE schattenkommentare sk
            SET entity_id = p.autor_id,
                updated_at = NOW(),
                meta = COALESCE(sk.meta, '{}'::jsonb) || jsonb_build_object(
                    'provenienz_korrektur', 'legacy_shadow_entity_target_2026-09-16',
                    'provenienz_korrektur_at', NOW()
                )
            FROM ftw_posts p
            WHERE p.id = sk.post_id
              AND p.autor_type = 'entity'
              AND sk.entity_id IS NULL
        """)
        result['shadows_updated'] = cur.rowcount
        if cur.rowcount != EXPECTED_SHADOWS_TO_BACKFILL:
            raise RuntimeError(f"Abbruch: Schatten-Update traf {cur.rowcount} statt {EXPECTED_SHADOWS_TO_BACKFILL}")

        cur.execute("""
            SELECT
              COUNT(*) AS total,
              COUNT(*) FILTER (WHERE ist_voreinzug IS TRUE) AS voreinzug_true,
              COUNT(*) FILTER (WHERE ist_voreinzug IS DISTINCT FROM TRUE) AS not_voreinzug,
              COUNT(*) FILTER (WHERE flarum_herkunft IS TRUE) AS flarum_true,
              COUNT(*) FILTER (WHERE sichtbarkeit='public') AS public_count,
              COUNT(*) FILTER (WHERE thema_id IS NOT NULL) AS with_thema,
              COUNT(*) FILTER (WHERE raum_id IS NOT NULL) AS with_raum
            FROM ftw_posts
        """)
        result['after_posts'] = dict(cur.fetchone())

        cur.execute("""
            SELECT
              COUNT(*) AS total,
              COUNT(*) FILTER (WHERE sk.entity_id IS NOT NULL AND p.autor_type='entity') AS entity_target_set,
              COUNT(*) FILTER (WHERE sk.entity_id IS NULL AND p.autor_type='human') AS human_still_null,
              COUNT(*) FILTER (WHERE sk.entity_id IS NULL AND p.autor_type='entity') AS entity_still_null
            FROM schattenkommentare sk
            JOIN ftw_posts p ON p.id=sk.post_id
        """)
        result['after_shadows'] = dict(cur.fetchone())

        a = result['after_posts']
        s = result['after_shadows']
        assert int(a['total']) == 46 and int(a['voreinzug_true']) == 46 and int(a['not_voreinzug']) == 0
        assert int(a['flarum_true']) == 0 and int(a['public_count']) == 46
        assert int(a['with_thema']) == 44 and int(a['with_raum']) == 46
        assert int(s['total']) == 19 and int(s['entity_target_set']) == 9
        assert int(s['human_still_null']) == 10 and int(s['entity_still_null']) == 0

    conn.commit()
    result['committed'] = True
except Exception:
    conn.rollback()
    result['committed'] = False
    raise
finally:
    conn.close()

print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
