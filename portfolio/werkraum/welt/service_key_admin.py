"""Local service-key provisioning/rotation. Output contains identifiers only.

Run using the API virtualenv with FLEXTRAWURST_DB_URI configured.
Private keys stay in the ignored, owner-only service key directory.
"""
import argparse
import fcntl
import json
import os
import stat
from pathlib import Path
from uuid import UUID, uuid4

from service_tokens import KEY_DIRECTORY, read_private_file, service_directory
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import psycopg2
from psycopg2.extras import Json


def private_directory(path):
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    info = path.lstat()
    if not stat.S_ISDIR(info.st_mode) or info.st_mode & 0o077 or info.st_uid != os.geteuid():
        raise PermissionError("key directory must be owner-only")


def private_write(path, data):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "wb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())


def provision(conn, name, *, rotate=False, overlap_seconds=300, root=KEY_DIRECTORY):
    if not 0 <= overlap_seconds <= 3600:
        raise ValueError("rotation overlap must be between zero and one hour")
    directory = service_directory(name, root)
    private_directory(root)
    private_directory(directory)
    fd = os.open(directory / "rotation.lock", os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "r+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        with conn.cursor() as cur:
            cur.execute("SELECT is_active FROM auth_service_principals WHERE name=%s", (name,))
            row = cur.fetchone()
            if not row or not row[0]:
                raise ValueError("service must already exist and be active")
        current = directory / "current.json"
        if current.exists() and not rotate:
            kid = str(UUID(json.loads(read_private_file(current))["kid"]))
            private = serialization.load_pem_private_key(
                read_private_file(directory / (kid + ".pem")), password=None)
            public = private.public_key().public_bytes(
                serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo).decode()
            with conn.cursor() as cur:
                cur.execute("SELECT public_key FROM auth_service_keys WHERE kid=%s AND principal=%s "
                            "AND is_active AND not_before<=now() AND (not_after IS NULL OR not_after>now())",
                            (kid, name))
                row = cur.fetchone()
            if not row or row[0] != public:
                raise ValueError("current key does not match an active registration; explicit rotation required")
            conn.rollback()
            return kid

        kid = str(uuid4())
        private = Ed25519PrivateKey.generate()
        private_write(directory / (kid + ".pem"), private.private_bytes(
            serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
        public = private.public_key().public_bytes(
            serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo).decode()
        pending = directory / (kid + ".json")
        private_write(pending, json.dumps({"kid": kid}).encode())
        # Register before publishing the pointer. A failure cannot make clients
        # use an unregistered key; old keys are bounded only after publication.
        try:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO auth_service_keys(kid,principal,public_key) VALUES (%s,%s,%s)",
                            (kid, name, public))
                cur.execute("INSERT INTO events(event_type,actor_type,actor_id,payload,visibility_layer) "
                            "VALUES ('auth.service_key_registered','system','service-key-admin',%s,'internal')",
                            (Json({"service": name, "kid": kid}),))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        os.replace(pending, current)
        try:
            with conn.cursor() as cur:
                cur.execute("UPDATE auth_service_keys SET not_after=LEAST(COALESCE(not_after, "
                            "now() + %s * interval '1 second'), now() + %s * interval '1 second') "
                            "WHERE principal=%s AND kid<>%s AND is_active",
                            (overlap_seconds, overlap_seconds, name, kid))
                cur.execute("INSERT INTO events(event_type,actor_type,actor_id,payload,visibility_layer) "
                            "VALUES ('auth.service_key_rotated','system','service-key-admin',%s,'internal')",
                            (Json({"service": name, "kid": kid, "overlap_seconds": overlap_seconds}),))
            conn.commit()
        except Exception:
            conn.rollback()
            raise RuntimeError("new key published but old-key expiry failed; inspect registry") from None
        return kid


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("bootstrap", "rotate", "seal-legacy"))
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--name")
    target.add_argument("--all", action="store_true")
    parser.add_argument("--overlap-seconds", type=int, default=300)
    args = parser.parse_args()
    conn = psycopg2.connect(os.environ["FLEXTRAWURST_DB_URI"], connect_timeout=5,
                            options="-c statement_timeout=5000")
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT name FROM auth_service_principals WHERE is_active ORDER BY name")
            names = [row[0] for row in cur.fetchall()]
        if args.name:
            if args.name not in names: raise ValueError("unknown or inactive service")
            names = [args.name]
        conn.rollback()
        if args.action == "seal-legacy":
            with conn.cursor() as cur:
                cur.execute("UPDATE auth_service_principals SET legacy_hs256_until=NULL "
                            "WHERE name=ANY(%s)", (names,))
                cur.execute("INSERT INTO events(event_type,actor_type,actor_id,payload,visibility_layer) "
                            "VALUES ('auth.service_legacy_sealed','system','service-key-admin',%s,'internal')",
                            (Json({"services": names}),))
            conn.commit()
            print("Legacy service JWTs disabled:", len(names))
        else:
            for name in names:
                kid = provision(conn, name, rotate=args.action == "rotate", overlap_seconds=args.overlap_seconds)
                print(name, kid)
    finally:
        conn.close()


if __name__ == "__main__": main()
