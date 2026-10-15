"""Verify service JWTs against public keys and live grants, never private keys."""
import os
from uuid import UUID

from service_crypto_runtime import enable_crypto
enable_crypto()
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
import jwt
from db_runtime import DB_URI


def verify_service_token(token: str) -> dict:
    header = jwt.get_unverified_header(token)
    if header.get("alg") != "EdDSA" or header.get("typ") != "JWT" or header.get("crit"):
        raise jwt.InvalidTokenError("invalid service token header")
    try:
        kid = str(UUID(header["kid"]))
    except (KeyError, ValueError, TypeError, AttributeError):
        raise jwt.InvalidTokenError("invalid service key identifier")
    import psycopg2
    conn = psycopg2.connect(
        DB_URI,
        connect_timeout=5, options="-c statement_timeout=5000")
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT k.principal, k.public_key, p.grants FROM auth_service_keys k "
                "JOIN auth_service_principals p ON p.name=k.principal "
                "WHERE k.kid=%s AND k.is_active AND p.is_active "
                "AND k.not_before <= now() AND (k.not_after IS NULL OR k.not_after > now())",
                (kid,))
            row = cur.fetchone()
    finally:
        conn.close()
    if not row or not isinstance(row[2], dict):
        raise jwt.InvalidTokenError("service key is unavailable")
    public_key = serialization.load_pem_public_key(row[1].encode("ascii"))
    if not isinstance(public_key, Ed25519PublicKey):
        raise jwt.InvalidTokenError("invalid service public key")
    decoded = jwt.decode(token, public_key, algorithms=["EdDSA"],
                         audience="flextrawurst-api", issuer="flextrawurst-service",
                         options={"require": ["iss", "aud", "sub", "role", "iat", "nbf", "exp", "jti"]})
    if (decoded["sub"] != row[0] or decoded["role"] != "service"
            or decoded["aud"] != "flextrawurst-api"
            or any(type(decoded[k]) is not int for k in ("iat", "nbf", "exp"))
            or not 0 < decoded["exp"] - decoded["iat"] <= 300
            or decoded["nbf"] < decoded["iat"]
            or any(k in decoded for k in ("user_id", "human_id", "grants"))):
        raise jwt.InvalidTokenError("invalid service claims")
    try:
        UUID(decoded["jti"])
    except (ValueError, TypeError, AttributeError):
        raise jwt.InvalidTokenError("invalid service token identifier")
    return {"user_id": row[0], "username": row[0], "role": "service", "grants": row[2], "kid": kid}
