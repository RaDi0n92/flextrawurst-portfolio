import json, pathlib, uuid, requests, psycopg2, psycopg2.extras

BASE='http://127.0.0.1:8030'
DB_ENV=pathlib.Path('/root/werkraum/.agent/flextrawurst-db.env')
DB_URI=None
for line in DB_ENV.read_text(encoding='utf-8').splitlines():
    if line.startswith('FLEXTRAWURST_DB_URI='):
        DB_URI=line.split('=',1)[1].strip().strip('"').strip("'")
        break
if not DB_URI:
    raise RuntimeError('FLEXTRAWURST_DB_URI missing')

conn=psycopg2.connect(DB_URI, cursor_factory=psycopg2.extras.RealDictCursor)
conn.autocommit=True
pub=uuid.uuid4(); hidden=uuid.uuid4()
r_pub_hidden=uuid.uuid4(); r_hidden_pub=uuid.uuid4(); r_external=uuid.uuid4()
marker='__AUDIT_REL_VIS_20260916__'
results={}

try:
    with conn.cursor() as cur:
        cur.execute('SELECT COUNT(*) AS n FROM post_relationen')
        baseline=int(cur.fetchone()['n'])
        results['baseline_relation_count']=baseline
        cur.execute('''
            INSERT INTO ftw_posts
              (id, autor_type, autor_id, content, post_type, sichtbarkeit, titel, meta, ist_voreinzug)
            VALUES
              (%s, 'system', 'audit', %s, 'audit', 'public', %s, '{}'::jsonb, true),
              (%s, 'system', 'audit', %s, 'audit', 'internal', %s, '{}'::jsonb, true)
        ''', (str(pub), marker+' PUBLIC_CONTENT', marker+' PUBLIC_TITLE',
              str(hidden), marker+' HIDDEN_CONTENT', marker+' HIDDEN_TITLE'))
        cur.execute('''
            INSERT INTO post_relationen
              (id, von_post_id, rel_typ, ziel_typ, ziel_id, zu_post_id, erstellt_von_type, erstellt_von_id, notiz, meta)
            VALUES
              (%s, %s, 'echoes', 'post', %s, %s, 'system', 'audit', %s, '{}'::jsonb),
              (%s, %s, 'echoes', 'post', %s, %s, 'system', 'audit', %s, '{}'::jsonb),
              (%s, %s, 'echoes', 'flarum_origin', %s, NULL, 'system', 'audit', %s, '{}'::jsonb)
        ''', (
            str(r_pub_hidden), str(pub), str(hidden), str(hidden), marker+' PUB_TO_HIDDEN_NOTE',
            str(r_hidden_pub), str(hidden), str(pub), str(pub), marker+' HIDDEN_TO_PUB_NOTE',
            str(r_external), str(pub), marker+' EXTERNAL_TARGET', marker+' EXTERNAL_NOTE'
        ))

    rel=requests.get(f'{BASE}/welt/posts/{pub}/relationen', timeout=10)
    rel.raise_for_status(); relj=rel.json(); reltxt=json.dumps(relj, ensure_ascii=False)
    results['relationen_http']=rel.status_code
    results['relationen_payload']=relj
    assert marker+' HIDDEN_CONTENT' not in reltxt
    assert marker+' HIDDEN_TITLE' not in reltxt
    assert marker+' PUB_TO_HIDDEN_NOTE' not in reltxt
    assert marker+' HIDDEN_TO_PUB_NOTE' not in reltxt
    assert marker+' EXTERNAL_TARGET' in reltxt
    assert marker+' EXTERNAL_NOTE' in reltxt
    results['relationen_hidden_post_filtered']=True
    results['relationen_nonpost_preserved']=True

    spur=requests.get(f'{BASE}/welt/posts/{pub}/spur?richtung=beide&tiefe=3', timeout=10)
    spur.raise_for_status(); spurj=spur.json(); spurtxt=json.dumps(spurj, ensure_ascii=False)
    results['spur_http']=spur.status_code
    results['spur_payload']=spurj
    assert marker+' HIDDEN_CONTENT' not in spurtxt
    assert marker+' HIDDEN_TITLE' not in spurtxt
    assert marker+' PUB_TO_HIDDEN_NOTE' not in spurtxt
    assert marker+' HIDDEN_TO_PUB_NOTE' not in spurtxt
    assert marker+' EXTERNAL_TARGET' in spurtxt
    assert marker+' EXTERNAL_NOTE' in spurtxt
    results['spur_hidden_post_filtered']=True
    results['spur_nonpost_preserved']=True

finally:
    with conn.cursor() as cur:
        cur.execute('DELETE FROM post_relationen WHERE id = ANY(%s::uuid[])', ([str(r_pub_hidden),str(r_hidden_pub),str(r_external)],))
        cur.execute('DELETE FROM ftw_posts WHERE id = ANY(%s::uuid[])', ([str(pub),str(hidden)],))
        cur.execute('SELECT COUNT(*) AS n FROM post_relationen')
        after=int(cur.fetchone()['n'])
        results['after_cleanup_relation_count']=after
    conn.close()

assert results['after_cleanup_relation_count']==results['baseline_relation_count'], results
print(json.dumps(results, ensure_ascii=False, indent=2, default=str))
