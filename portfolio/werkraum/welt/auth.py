"""Auth-Utilities: bcrypt + JWT für das Menschenprofil-System."""

import os
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import UUID

from service_crypto_runtime import enable_crypto
enable_crypto()
import bcrypt
import jwt
from service_token_verifier import verify_service_token

_SECRET_FILE = Path(__file__).parent / ".jwt_secret"
_TOKEN_DAYS = 7
_ALGORITHM = "HS256"


def _load_secret() -> str:
    env = os.environ.get("WELT_JWT_SECRET")
    if env:
        return env
    if _SECRET_FILE.exists():
        return _SECRET_FILE.read_text(encoding="utf-8").strip()
    secret = secrets.token_hex(32)
    _SECRET_FILE.write_text(secret, encoding="utf-8")
    _SECRET_FILE.chmod(0o600)
    return secret


_SECRET = _load_secret()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), hash.encode())


def create_token(user_id: str, role: str) -> str:
    if role != "entity":
        try:
            UUID(str(user_id))
        except (ValueError, TypeError, AttributeError):
            raise ValueError("named services must use create_service_token")
    payload = {
        "sub": user_id,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(days=_TOKEN_DAYS),
    }
    return jwt.encode(payload, _SECRET, algorithm=_ALGORITHM)


def verify_token(token: str, *, allow_service: bool = False) -> dict:
    algorithm = jwt.get_unverified_header(token).get("alg")
    if algorithm == "EdDSA":
        if not allow_service:
            raise jwt.InvalidTokenError("service token is not allowed here")
        return verify_service_token(token)
    if algorithm != _ALGORITHM:
        raise jwt.InvalidTokenError("invalid token algorithm")
    decoded = jwt.decode(token, _SECRET, algorithms=[_ALGORITHM])
    claims = {
        "user_id": decoded.get("user_id") or decoded["sub"],
        "role": decoded["role"],
        "username": decoded["sub"],
    }
    if claims["role"] != "entity":
        try:
            UUID(str(claims["user_id"]))
        except (ValueError, TypeError, AttributeError):
            # Named internal tokens never inherit general admin privileges.
            # Opt-in belongs to the one route that understands service grants.
            if not allow_service:
                raise jwt.InvalidTokenError("service token is not allowed here")
            return _current_service_account(claims)
    return _current_human_account(claims)


def _current_service_account(claims: dict) -> dict:
    import psycopg2

    conn = psycopg2.connect(
        os.environ.get(
            "FLEXTRAWURST_DB_URI",
            "dbname=__flextrawurst_db_uri_required__ user=__missing_runtime_config__",
        ),
        connect_timeout=5,
        options="-c statement_timeout=5000",
    )
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT is_active, grants FROM auth_service_principals WHERE name = %s "
                        "AND legacy_hs256_until > now()",
                        (str(claims["user_id"]),))
            row = cur.fetchone()
    finally:
        conn.close()
    if not row or not row[0] or not isinstance(row[1], dict):
        raise jwt.InvalidTokenError("service is missing or inactive")
    return {**claims, "role": "service", "grants": row[1]}


def _current_human_account(claims: dict) -> dict:
    """Refresh human UUID accounts on every verification, without a stale cache.

    Entity tokens and existing named service identities have separate lifecycles.
    This check does not certify or change their existing authorization policy.
    """
    if claims["role"] == "entity":
        return claims
    try:
        user_id = str(UUID(str(claims["user_id"])))
    except (ValueError, TypeError, AttributeError):
        # Legacy internal issuers use names, not human_users UUIDs.
        return claims

    import psycopg2

    conn = psycopg2.connect(
        os.environ.get(
            "FLEXTRAWURST_DB_URI",
            "dbname=__flextrawurst_db_uri_required__ user=__missing_runtime_config__",
        ),
        connect_timeout=5,
    )
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT role, is_active FROM human_users WHERE id = %s", (user_id,))
            row = cur.fetchone()
    finally:
        conn.close()
    if not row or not row[1]:
        raise jwt.InvalidTokenError("human account is missing or inactive")
    return {**claims, "user_id": user_id, "role": row[0]}
