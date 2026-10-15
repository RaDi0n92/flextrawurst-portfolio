"""Explicit host integration check; every change is rolled back, never committed.

Run with the API virtualenv and FLEXTRAWURST_DB_URI in the environment.
Uses synthetic signing keys; never reads production JWT secrets.
"""
import ast
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch
from uuid import UUID
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'welt'))
from service_crypto_runtime import enable_crypto
enable_crypto()
import jwt
import psycopg2
import psycopg2.extras
from fastapi import FastAPI, Header, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'welt'))
from service_auth import register_service_admin_routes
from service_token_verifier import verify_service_token
from service_key_admin import provision
import service_tokens

SECRET = 'synthetic-db-service-policy-test-secret-32-plus-bytes'


def main():
    raw = psycopg2.connect(os.environ['FLEXTRAWURST_DB_URI'])
    checks = 0

    def check(condition, label):
        nonlocal checks
        if not condition: raise AssertionError(label)
        checks += 1

    class Connection:
        def __init__(self, dict_rows=False): self.dict_rows = dict_rows
        def cursor(self):
            return raw.cursor(cursor_factory=psycopg2.extras.RealDictCursor) if self.dict_rows else raw.cursor()
        def close(self): pass
        def commit(self): pass  # NEVER commit this test transaction.
        def rollback(self): pass  # The outer connection alone owns rollback.

    def token(subject, role='admin'):
        return jwt.encode({'sub':subject,'role':role,
                           'exp': datetime.now(timezone.utc)+timedelta(minutes=3)},
                          SECRET, algorithm='HS256')

    try:
        with raw.cursor() as cur:
            cur.execute((ROOT / 'welt/migrate_service_principals_20260918.sql').read_text())
            cur.execute((ROOT / 'welt/migrate_service_keys_20260918.sql').read_text())
            # Exercise bounded migration compatibility, never production policy.
            cur.execute("UPDATE auth_service_principals SET legacy_hs256_until=now()+interval '5 minutes'")
            cur.execute("SELECT id FROM human_users WHERE is_active AND role='admin' LIMIT 1")
            admin = str(cur.fetchone()[0])
            cur.execute("SELECT name, grants FROM auth_service_principals WHERE meta->>'migration'='20260918'")
            policies = cur.fetchall()
            check(len(policies) == 10, 'ten seeded service policies')

        scope = dict(UUID=UUID, os=os, jwt=jwt, _SECRET=SECRET, _ALGORITHM='HS256',
                     app=FastAPI(), Header=Header, HTTPException=HTTPException,
                     BaseModel=BaseModel, psycopg2=psycopg2,
                     get_conn=lambda: Connection(True), verify_service_token=verify_service_token)
        tree = ast.parse((ROOT / 'welt/auth.py').read_text())
        nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef)
                 and n.name in ('verify_token', '_current_human_account', '_current_service_account')]
        exec(compile(ast.Module(body=nodes, type_ignores=[]), 'actual_auth_functions', 'exec'), scope)
        tree = ast.parse((ROOT / 'welt/api.py').read_text())
        names = {'_require_auth', '_require_admin', '_require_splitter_writer',
                 'admin_splitter_erstellen', 'splitter_einsammeln', 'SplitterCreate'}
        nodes = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names]
        exec(compile(ast.Module(body=nodes, type_ignores=[]), 'actual_api_functions', 'exec'), scope)
        app = scope['app']
        register_service_admin_routes(app, scope['get_conn'], scope['_require_admin'])

        @app.get('/admin/probe')
        def admin_probe(authorization: str | None = Header(None)):
            scope['_require_admin'](authorization)
            return {'ok':True}

        @app.get('/auth/probe')
        def auth_probe(authorization: str | None = Header(None)):
            scope['_require_auth'](authorization)
            return {'ok':True}

        with patch.object(psycopg2, 'connect', lambda *a, **k: Connection()), TestClient(app) as client:
            admin_headers = {'Authorization':'Bearer '+token(admin)}
            check(client.get('/admin/auth/services', headers=admin_headers).status_code == 200, 'human admin list')
            check(client.get('/admin/auth/services').status_code == 401, 'anonymous list denied')
            for name, grants in policies:
                headers = {'Authorization':'Bearer '+token(name)}
                grant = grants['splitter:create']
                body = dict(origin_type=grant['origin_types'][0], entity_id=grant['entity_ids'][0],
                            essenz='synthetic rollback-only service check')
                response = client.post('/admin/splitter', headers=headers, json=body)
                check(response.status_code == 200, name+' approved creation')
                with raw.cursor() as cur:
                    cur.execute('SELECT meta FROM splitter WHERE id=%s', (response.json()['id'],))
                    check(cur.fetchone()[0]['service_principal'] == name, name+' stored provenance')
                    cur.execute("SELECT count(*) FROM events WHERE event_type='splitter.service_created' "
                                "AND actor_id=%s AND payload->>'splitter_id'=%s",
                                (name, response.json()['id']))
                    check(cur.fetchone()[0] == 1, name+' transactional event')
                for path in ('/admin/probe', '/auth/probe', '/admin/auth/services'):
                    check(client.get(path, headers=headers).status_code == 401, name+' denied '+path)
                check(client.put('/admin/auth/services/'+name, headers=headers,
                                 json={'is_active':True}).status_code == 401, name+' cannot grant itself rights')
                check(client.post('/zwischenraum/splitter/'+response.json()['id']+'/einsammeln',
                                  headers=headers).status_code == 401, name+' no collection activation')
                for key, value in [('origin_type','other-origin'), ('entity_id','other-identity'), ('human_id',admin)]:
                    check(client.post('/admin/splitter', headers=headers, json={**body,key:value}).status_code == 403,
                          name+' rejects '+key)

            name = 'codex-abwurf'
            headers = {'Authorization':'Bearer '+token(name)}
            body = {'origin_type':'codex_abwurf','entity_id':'codex','essenz':'rollback only'}
            policy = {'is_active':False, 'origin_types':['codex_abwurf'], 'entity_ids':['codex']}
            check(client.put('/admin/auth/services/'+name, headers=admin_headers, json=policy).status_code == 200,
                  'admin revokes service')
            check(client.post('/admin/splitter', headers=headers, json=body).status_code == 401,
                  'already signed token revoked')
            with raw.cursor() as cur:
                cur.execute((ROOT / 'welt/migrate_service_principals_20260918.sql').read_text())
                cur.execute('SELECT is_active FROM auth_service_principals WHERE name=%s', (name,))
                check(cur.fetchone()[0] is False, 'repeated migration does not reactivate')
            policy.update(is_active=True, origin_types=[])
            check(client.put('/admin/auth/services/'+name, headers=admin_headers, json=policy).status_code == 200,
                  'admin changes grants')
            check(client.post('/admin/splitter', headers=headers, json=body).status_code == 403,
                  'same token reflects removed grant')
            check(client.post('/admin/splitter', headers={'Authorization':'Bearer '+token('unregistered-service')},
                              json=body).status_code == 401, 'unknown service denied')
            check(client.post('/admin/splitter', headers=admin_headers, json=body).status_code == 200,
                  'human admin still creates')
            with raw.cursor() as cur:
                cur.execute('UPDATE auth_service_principals SET legacy_hs256_until=NULL')
            for name, _ in policies:
                check(client.post('/admin/splitter', headers={'Authorization':'Bearer '+token(name)},
                                  json=body).status_code == 401, name+' legacy cutoff enforced')
            with TemporaryDirectory() as directory, patch.object(service_tokens, 'KEY_DIRECTORY', Path(directory)):
                for name, grants in policies:
                    with raw.cursor() as cur:
                        cur.execute('UPDATE auth_service_principals SET grants=%s WHERE name=%s',
                                    (psycopg2.extras.Json(grants), name))
                    first = provision(Connection(), name, root=Path(directory))
                    check(provision(Connection(), name, root=Path(directory)) == first, 'bootstrap idempotent')
                    signed = service_tokens.create_service_token(name)
                    headers = {'Authorization':'Bearer '+signed}
                    grant = grants['splitter:create']
                    body = dict(origin_type=grant['origin_types'][0], entity_id=grant['entity_ids'][0],
                                essenz='Ed25519 rollback-only check')
                    check(client.post('/admin/splitter', headers=headers, json=body).status_code == 200,
                          name+' Ed25519 creation')
                    check(client.get('/admin/probe', headers=headers).status_code == 401, 'no admin escalation')
                    second = provision(Connection(), name, rotate=True, root=Path(directory))
                    check(first != second and verify_service_token(signed) is not None, 'rotation overlap')
                    response = client.post('/admin/auth/services/'+name+'/keys/'+first+'/revoke', headers=admin_headers)
                    check(response.status_code == 200, 'admin key revocation')
                    check(client.post('/admin/splitter', headers=headers, json=body).status_code == 401,
                          'old signed token revoked immediately')
                    fresh = service_tokens.create_service_token(name)
                    check(verify_service_token(fresh) is not None, 'replacement key valid')
                    with raw.cursor() as cur:
                        cur.execute("UPDATE auth_service_keys SET not_after=now() WHERE kid=%s", (second,))
                    check(client.post('/admin/splitter', headers={'Authorization':'Bearer '+fresh}, json=body).status_code == 401,
                          'expired key rejected')
        print(f'{checks} PostgreSQL/HTTP assertions passed; rollback follows')
    finally:
        raw.rollback()
        raw.close()
        print('Transaction rolled back; no test content or policy changes committed')


if __name__ == '__main__': main()
