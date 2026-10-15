"""Per-service Ed25519 signing. Never imports or reads the human JWT secret."""
import json
import os
import re
import stat
import time
from pathlib import Path
from uuid import UUID, uuid4

from service_crypto_runtime import enable_crypto
enable_crypto()
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import jwt

ISSUER = "flextrawurst-service"
AUDIENCE = "flextrawurst-api"
TOKEN_SECONDS = 300
KEY_DIRECTORY = Path("/root/werkraum/.agent/service-keys")


def service_directory(name: str, root: Path | None = None) -> Path:
    if not isinstance(name, str) or not re.fullmatch(r"[a-z][a-z0-9-]{0,99}", name):
        raise ValueError("invalid service name")
    return (root if root is not None else KEY_DIRECTORY) / name


def read_private_file(path: Path) -> bytes:
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, "rb") as handle:
        info = os.fstat(handle.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_mode & 0o077 or info.st_uid != os.geteuid():
            raise PermissionError("service key file must be owner-only")
        return handle.read(16384)


def create_service_token(name: str, legacy_role: str | None = None) -> str:
    # Compatibility with existing local _admin_token helpers. This argument
    # cannot grant a role: every issued token has role=service.
    if legacy_role not in (None, "admin", "service"):
        raise ValueError("invalid service role")
    directory = service_directory(name)
    manifest = json.loads(read_private_file(directory / "current.json"))
    kid = str(UUID(manifest["kid"]))
    private_key = serialization.load_pem_private_key(
        read_private_file(directory / (kid + ".pem")), password=None)
    if not isinstance(private_key, Ed25519PrivateKey):
        raise ValueError("expected an Ed25519 service key")
    now = int(time.time())
    return jwt.encode({"iss": ISSUER, "aud": AUDIENCE, "sub": name,
                       "role": "service", "iat": now, "nbf": now,
                       "exp": now + TOKEN_SECONDS, "jti": str(uuid4())},
                      private_key, algorithm="EdDSA", headers={"kid": kid})
