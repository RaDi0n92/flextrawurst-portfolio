#!/usr/bin/env python3
"""Negative Live-Regression ohne Einzug: Auth-, Schlaf- und Cyberling-Gates.
Liest vorhandene Entity-Keys lokal aus PostgreSQL, gibt weder Keys noch Tokens aus.
"""
import json
from pathlib import Path
import psycopg2
import requests

BASE = 'http://127.0.0.1:8030'
uri = next(
    x.split('=', 1)[1].strip().strip('"').strip("'")
    for x in Path('/root/werkraum/.agent/flextrawurst-db.env').read_text().splitlines()
    if x.startswith('FLEXTRAWURST_DB_URI=')
)
conn = psycopg2.connect(uri)
cur = conn.cursor()

def entity_key(entity_id):
    cur.execute('SELECT api_key::text FROM entity_profiles WHERE entity_id=%s', (entity_id,))
    return cur.fetchone()[0]

def login(entity_id):
    r = requests.post(BASE + '/auth/entity-login', json={
        'entity_id': entity_id,
        'api_key': entity_key(entity_id),
    }, timeout=10)
    r.raise_for_status()
    return r.json()['token']

def snapshot():
    cur.execute("SELECT status FROM entity_slots WHERE entity_id='Schorschel'")
    slot_status = cur.fetchone()[0]
    cur.execute("SELECT meta->>'einzug_timestamp' FROM entity_profiles WHERE entity_id='Schorschel'")
    einzug = cur.fetchone()[0]
    cur.execute("""SELECT status,zustand,tode,hunger,durst,energie,stimmung,gesundheit,lebensbeginn_at
                   FROM cyberlinge WHERE entity_id='Schorschel'""")
    cyber = [str(x) if x is not None else None for x in cur.fetchone()]
    cur.execute("SELECT count(*) FROM sleep_phases WHERE entity_id='Schorschel'")
    sleep = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM events WHERE event_type='wesen.eingezogen' AND actor_id='Schorschel'")
    entry_events = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM events WHERE event_type='schlaf.begonnen' AND actor_id='Schorschel'")
    sleep_events = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM events WHERE event_type='cyberling.fuettern' AND payload->>'ziel_entity_id'='Schorschel'")
    care_events = cur.fetchone()[0]
    return {
        'slot_status': slot_status,
        'einzug_timestamp': einzug,
        'cyberling': cyber,
        'sleep_phases': sleep,
        'entry_events': entry_events,
        'sleep_events': sleep_events,
        'care_events': care_events,
    }

tok_s = login('Schorschel')
tok_f = login('F3INSCHM3CK3R')
H_s = {'Authorization': 'Bearer ' + tok_s}
H_f = {'Authorization': 'Bearer ' + tok_f}

before = snapshot()
tests = []

def call(name, method, path, headers=None, json_body=None):
    r = requests.request(method, BASE + path, headers=headers, json=json_body, timeout=15)
    try:
        body = r.json()
    except Exception:
        body = {}
    tests.append({'name': name, 'status': r.status_code, 'detail': body.get('detail') if isinstance(body, dict) else None})

call('entry_anonymous', 'POST', '/admin/wesen/Schorschel/einzug')
call('entry_entity_not_admin', 'POST', '/admin/wesen/Schorschel/einzug', H_s)
call('sleep_anonymous', 'POST', '/wesen/Schorschel/schlaf/start', json_body={'typ': 'kurz'})
call('sleep_wrong_entity', 'POST', '/wesen/Schorschel/schlaf/start', H_f, {'typ': 'kurz'})
call('sleep_self_preentry', 'POST', '/wesen/Schorschel/schlaf/start', H_s, {'typ': 'kurz'})
call('cyberling_anonymous', 'POST', '/wesen/Schorschel/cyberling/fuettern')
call('cyberling_wrong_entity', 'POST', '/wesen/Schorschel/cyberling/fuettern', H_f)
call('cyberling_self_preentry', 'POST', '/wesen/Schorschel/cyberling/fuettern', H_s)

after = snapshot()
expected = {
    'entry_anonymous': 401,
    'entry_entity_not_admin': 403,
    'sleep_anonymous': 401,
    'sleep_wrong_entity': 403,
    'sleep_self_preentry': 409,
    'cyberling_anonymous': 401,
    'cyberling_wrong_entity': 403,
    'cyberling_self_preentry': 409,
}
ok = all(t['status'] == expected[t['name']] for t in tests) and before == after
print(json.dumps({
    'ok': ok,
    'tests': tests,
    'before_equals_after': before == after,
    'before': before,
    'after': after,
}, ensure_ascii=False, indent=2))
cur.close()
conn.close()
if not ok:
    raise SystemExit(2)
