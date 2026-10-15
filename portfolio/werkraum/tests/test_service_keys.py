"""Synthetic Ed25519 keys: issuer binding, claim validation and private file policy."""
import ast
import json
import os
import sys
import tempfile
import time
import types
import unittest
from pathlib import Path
from unittest.mock import patch
from uuid import UUID, uuid4

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'welt'))
from service_crypto_runtime import enable_crypto
enable_crypto()
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import service_tokens as signer
from service_token_verifier import verify_service_token


class ServiceKeyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.name = 'synthetic-service'
        self.kid = str(uuid4())
        self.key = Ed25519PrivateKey.generate()
        self.public = self.key.public_key().public_bytes(
            serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo).decode()
        self.grants = {'splitter:create': {'origin_types':['synthetic'], 'entity_ids':[None]}}
        self.row = (self.name, self.public, self.grants)
        self.queries = []
        self.closed = 0
        directory = self.root / self.name
        directory.mkdir(mode=0o700)
        self.private_path = directory / (self.kid + '.pem')
        for path, data in [(self.private_path,self.key.private_bytes(serialization.Encoding.PEM,
                           serialization.PrivateFormat.PKCS8,serialization.NoEncryption())),
                           (directory/'current.json',json.dumps({'kid':self.kid}).encode())]:
            with os.fdopen(os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600),'wb') as f: f.write(data)
        outer = self
        class Conn:
            def cursor(self): return self
            def __enter__(self): return self
            def __exit__(self,*args): pass
            def execute(self,sql,params): outer.queries.append((sql,params))
            def fetchone(self): return outer.row
            def close(self): outer.closed += 1
        self.driver = types.SimpleNamespace(connect=lambda *a, **k: Conn())
        self.patches = [patch.dict(sys.modules,{'psycopg2':self.driver}),
                        patch.object(signer,'KEY_DIRECTORY',self.root)]
        for p in self.patches: p.start(); self.addCleanup(p.stop)
        self.token = signer.create_service_token(self.name)
        self.payload = jwt.decode(self.token,self.key.public_key(),algorithms=['EdDSA'],audience=signer.AUDIENCE)

    def encode(self, changes=None, omit=(), key=None, header=None):
        payload = {**self.payload, **(changes or {})}
        for k in omit: payload.pop(k,None)
        return jwt.encode(payload,key or self.key,algorithm='EdDSA',headers=header or {'kid':self.kid})

    def test_real_signer_and_verifier_preserve_identity_and_live_grants(self):
        claims = verify_service_token(self.token)
        self.assertEqual(claims['role'],'service')
        self.assertEqual(claims['user_id'],self.name)
        self.assertEqual(claims['grants'],self.grants)
        self.assertEqual(self.queries[-1][1],(self.kid,))
        self.assertEqual(self.closed,1)
        self.grants.clear()
        self.assertEqual(verify_service_token(self.token)['grants'],{})

    def test_service_key_cannot_impersonate_other_service_or_human(self):
        for changes in ({'sub':'other-service'}, {'sub':str(uuid4()),'role':'admin'},
                        {'role':'entity'}, {'role':'admin'}, {'user_id':str(uuid4())},
                        {'human_id':str(uuid4())}, {'grants':{'admin':True}}):
            with self.subTest(changes=changes), self.assertRaises(jwt.InvalidTokenError):
                verify_service_token(self.encode(changes))

    def test_wrong_private_key_cannot_use_registered_kid(self):
        with self.assertRaises(jwt.InvalidTokenError):
            verify_service_token(self.encode(key=Ed25519PrivateKey.generate()))

    def test_missing_and_invalid_claims(self):
        for name in ('iss','aud','sub','role','iat','nbf','exp','jti'):
            with self.subTest(missing=name), self.assertRaises(jwt.InvalidTokenError):
                verify_service_token(self.encode(omit=(name,)))
        for changes in ({'iss':'other'}, {'aud':'other'}, {'aud':[signer.AUDIENCE,'other']},
                        {'jti':'invalid'}, {'exp':self.payload['iat']+301},
                        {'iat':str(self.payload['iat'])}, {'nbf':self.payload['iat']-1},
                        {'iat':True}, {'exp':int(time.time())-1}):
            with self.subTest(changes=changes), self.assertRaises(jwt.InvalidTokenError):
                verify_service_token(self.encode(changes))

    def test_bad_header_is_rejected_before_lookup(self):
        for header in ({'kid':'invalid'}, {'kid':self.kid,'typ':'other'},
                       {'kid':self.kid,'crit':['unexpected']}):
            with self.assertRaises(jwt.InvalidTokenError): verify_service_token(self.encode(header=header))
        with self.assertRaises(jwt.InvalidTokenError):
            verify_service_token(jwt.encode(self.payload,b'not-a-private-key',algorithm='HS256'))
        self.assertEqual(self.queries,[])

    def test_revoked_or_unknown_key_is_denied(self):
        self.row = None
        with self.assertRaises(jwt.InvalidTokenError): verify_service_token(self.token)

    def test_database_outage_is_not_a_cached_success(self):
        verify_service_token(self.token)
        def offline(*a,**kw): raise ConnectionError('synthetic')
        self.driver.connect = offline
        with self.assertRaises(ConnectionError): verify_service_token(self.token)

    def test_private_key_permissions_and_symlink_are_checked(self):
        self.private_path.chmod(0o644)
        with self.assertRaises(PermissionError): signer.create_service_token(self.name)
        self.private_path.chmod(0o600)
        link = self.root/'link.pem'
        link.symlink_to(self.private_path)
        with self.assertRaises(OSError): signer.read_private_file(link)
        for name in ('../other','/tmp/key','x/y','x\\y','x\n'):
            with self.assertRaises(ValueError): signer.create_service_token(name)

    def test_general_auth_rejects_service_even_with_valid_signature(self):
        scope = dict(jwt=jwt,UUID=UUID,os=os,_SECRET='synthetic-human-secret-at-least-32-bytes',
                     _ALGORITHM='HS256',verify_service_token=verify_service_token)
        tree = ast.parse((ROOT/'welt/auth.py').read_text())
        nodes = [n for n in tree.body if isinstance(n,ast.FunctionDef)
                 and n.name in ('verify_token','_current_human_account','_current_service_account')]
        exec(compile(ast.Module(body=nodes,type_ignores=[]),'actual_auth','exec'),scope)
        with self.assertRaises(jwt.InvalidTokenError): scope['verify_token'](self.token)
        self.assertEqual(scope['verify_token'](self.token,allow_service=True)['role'],'service')


if __name__ == '__main__': unittest.main()
