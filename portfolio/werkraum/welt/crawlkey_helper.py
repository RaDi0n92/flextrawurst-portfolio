#!/usr/bin/env python3
"""Small root-owned capability for crawl-key rotation.

The Welt API must not be able to write /root/.claude or /etc/nginx directly.
This helper exposes only the five known key stores over a permissioned Unix
socket and performs an atomic write plus nginx validation/reload for the three
Nginx-backed keys.
"""

from __future__ import annotations

import argparse
import datetime as _datetime
import json
import os
import re
import secrets
import socketserver
import stat
import subprocess
import tempfile
from pathlib import Path


SOCKET_PATH = os.environ.get(
    "FLEXTRAWURST_CRAWLKEY_SOCKET",
    "/run/flextrawurst-crawlkey-helper.sock",
)
SOCKET_GROUP = os.environ.get("FLEXTRAWURST_CRAWLKEY_SOCKET_GROUP", "flextrawurst-api")

KEY_STORES = {
    "claudelive": {
        "kind": "nginx",
        "key_path": Path("/root/.claude/.env_claudelive_crawl_key"),
        "nginx_path": Path("/etc/nginx/conf.d/claudelive-crawl-key.conf"),
    },
    "codexlive": {
        "kind": "nginx",
        "key_path": Path("/root/.claude/.env_codexlive_crawl_key"),
        "nginx_path": Path("/etc/nginx/conf.d/codexlive-crawl-key.conf"),
    },
    "geminilive": {
        "kind": "nginx",
        "key_path": Path("/root/.claude/.env_geminilive_crawl_key"),
        "nginx_path": Path("/etc/nginx/conf.d/geminilive-crawl-key.conf"),
    },
    "kompoase": {
        "kind": "nginx",
        "key_path": Path("/root/kompoase/.env_crawl_key"),
        "nginx_path": Path("/etc/nginx/conf.d/kompoase-crawl-key.conf"),
    },
    "toolbox": {
        "kind": "tts_nginx",
        "key_path": Path("/root/werkraum/welt/.env.tts_crawl_key"),
        "nginx_path": Path("/etc/nginx/conf.d/tts-crawl-key.conf"),
    },
    "crawlschluessel": {
        "kind": "json",
        "key_path": Path("/root/.claude/.crawlschluessel_state.json"),
    },
    "archkey": {
        "kind": "json",
        "key_path": Path("/root/.claude/.archaeologie_crawlschluessel_state.json"),
    },
}


class CrawlKeyHelperError(RuntimeError):
    """Expected, client-safe helper failure."""


def _read_key(spec: dict) -> str:
    path = spec["key_path"]
    try:
        if spec["kind"] == "json":
            value = json.loads(path.read_text(encoding="utf-8"))
            return str(value.get("schluessel", ""))
        return path.read_text(encoding="utf-8").strip()
    except (FileNotFoundError, OSError, ValueError, TypeError):
        return ""


def _atomic_write(path: Path, payload: bytes, mode: int) -> None:
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def _snapshot(path: Path) -> tuple[bool, bytes, int]:
    try:
        return True, path.read_bytes(), stat.S_IMODE(path.stat().st_mode)
    except FileNotFoundError:
        return False, b"", 0o600


def _restore(path: Path, existed: bool, payload: bytes, mode: int) -> None:
    if existed:
        _atomic_write(path, payload, mode)
    else:
        try:
            path.unlink()
        except FileNotFoundError:
            pass


def _rotate_json(spec: dict, new_key: str) -> None:
    path = spec["key_path"]
    existed, _old_payload, old_mode = _snapshot(path)
    payload = json.dumps(
        {
            "schluessel": new_key,
            "rotiert_am": _datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        },
        ensure_ascii=False,
        indent=2,
    ).encode("utf-8")
    _atomic_write(path, payload, old_mode if existed else 0o600)


def _rotate_nginx(spec: dict, new_key: str) -> None:
    key_path = spec["key_path"]
    nginx_path = spec["nginx_path"]
    key_existed, old_key_payload, old_key_mode = _snapshot(key_path)
    nginx_existed, old_nginx_payload, old_nginx_mode = _snapshot(nginx_path)
    if not nginx_existed:
        raise CrawlKeyHelperError(f"Nginx-Konfiguration fehlt: {nginx_path}")

    old_nginx_text = old_nginx_payload.decode("utf-8")
    if spec["kind"] == "tts_nginx":
        old_key = old_key_payload.decode("utf-8").strip()
        new_nginx_text = old_nginx_text.replace(f'"{old_key}" 1;', f'"{new_key}" 1;', 1)
        replacements = int(new_nginx_text != old_nginx_text)
    else:
        new_nginx_text, replacements = re.subn(
            r'(default 0;\n)\s*"[^"]*"\s*1;',
            r'\1    "' + new_key + r'" 1;',
            old_nginx_text,
            count=1,
        )
    if replacements != 1:
        raise CrawlKeyHelperError(f"Schlüsselzeile nicht eindeutig: {nginx_path}")

    try:
        _atomic_write(key_path, (new_key + "\n").encode("utf-8"), old_key_mode if key_existed else 0o600)
        _atomic_write(nginx_path, new_nginx_text.encode("utf-8"), old_nginx_mode)
        subprocess.run(["nginx", "-t"], check=True, capture_output=True, text=True, timeout=15)
        subprocess.run(["systemctl", "reload", "nginx"], check=True, timeout=15)
    except Exception as exc:
        rollback_errors = []
        try:
            _restore(key_path, key_existed, old_key_payload, old_key_mode)
            _restore(nginx_path, nginx_existed, old_nginx_payload, old_nginx_mode)
        except Exception as rollback_exc:
            rollback_errors.append(str(rollback_exc))
        if not rollback_errors:
            try:
                subprocess.run(["nginx", "-t"], check=True, capture_output=True, text=True, timeout=15)
                subprocess.run(["systemctl", "reload", "nginx"], check=True, timeout=15)
            except Exception as reload_exc:
                rollback_errors.append(str(reload_exc))
        suffix = f"; Rollback-Fehler: {' | '.join(rollback_errors)}" if rollback_errors else ""
        raise CrawlKeyHelperError(f"Rotation zurückgerollt: {exc}{suffix}") from exc


def _rotate(system: str) -> str:
    spec = KEY_STORES[system]
    new_key = secrets.token_urlsafe(24)
    if spec["kind"] == "json":
        _rotate_json(spec, new_key)
    else:
        _rotate_nginx(spec, new_key)
    return new_key


class _RequestHandler(socketserver.StreamRequestHandler):
    def handle(self) -> None:
        raw = self.rfile.readline(4097)
        if not raw or len(raw) > 4096:
            self._respond({"ok": False, "error": "request too large"})
            return
        try:
            request = json.loads(raw.decode("utf-8"))
            system = request.get("system")
            action = request.get("action")
            if system not in KEY_STORES or action not in {"read", "rotate"}:
                raise CrawlKeyHelperError("ungültige Anfrage")
            if action == "read":
                result = {"key": _read_key(KEY_STORES[system])}
            else:
                result = {"key": _rotate(system)}
            self._respond({"ok": True, **result})
        except Exception as exc:
            self._respond({"ok": False, "error": str(exc)[:300]})

    def _respond(self, payload: dict) -> None:
        self.wfile.write((json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8"))


class _ThreadingUnixServer(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    daemon_threads = True


def _serve(socket_path: str, socket_group: str) -> None:
    path = Path(socket_path)
    if path.exists():
        if not stat.S_ISSOCK(path.stat().st_mode):
            raise RuntimeError(f"Socket-Pfad ist keine Socket-Datei: {path}")
        path.unlink()
    server = _ThreadingUnixServer(str(path), _RequestHandler)
    os.chmod(path, 0o660)
    if socket_group:
        import grp

        os.chown(path, os.getuid(), grp.getgrnam(socket_group).gr_gid)
    try:
        server.serve_forever()
    finally:
        server.server_close()
        try:
            path.unlink()
        except FileNotFoundError:
            pass


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--socket", default=SOCKET_PATH)
    parser.add_argument("--socket-group", default=SOCKET_GROUP)
    args = parser.parse_args()
    _serve(args.socket, args.socket_group)


if __name__ == "__main__":
    main()
