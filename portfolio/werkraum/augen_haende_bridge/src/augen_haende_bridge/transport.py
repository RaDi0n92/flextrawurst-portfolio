"""Loopback-only first-contact relay. No desktop input or shell execution.

Credentials and grants are supplied by the operator, never by peer messages.
This is a transport foundation, NOT public pairing or a Windows adapter.
"""
from __future__ import annotations

import argparse
import asyncio
import base64
import hashlib
import hmac
import json
import os
import re
import sqlite3
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

from websockets.asyncio.server import serve
from websockets.exceptions import ConnectionClosed

MAX_WIRE = 1_500_000
IDENTIFIER = re.compile(r"[A-Za-z0-9_.:-]{1,96}\Z")

# Terminal des ersten Körpers: die Bridge startet die Sitzung auf dem VPS und hält sie (BE01/BE02).
TERMINAL_STATES = ("starting", "running", "paused", "exited", "failed")  # paused: Prozessgruppe angehalten (G09), die Sitzung lebt
DESKTOP_TERMINAL_KINDS = frozenset({"terminal_list_request", "terminal_start", "terminal_close",
                                    "terminal_input", "terminal_resize", "terminal_audio", "terminal_attach",
                                    "anzeigeorte_request", "terminal_umziehen", "terminal_ziel", "ziel_zustand", "terminal_steuern", "haende_ergebnis", "weltdom_ergebnis", "raute_tippen_ergebnis", "ablauf_steuern", "regie_spruch", "lage"})
STEUER_AKTIONEN = ("pause", "fortsetzen")
LAUNCHER_TERMINAL_KINDS = frozenset({"terminal_list", "terminal_state", "terminal_output", "raute_say", "raute_tippen",
                                     "sprache_text", "anzeigeorte", "terminal_ort", "haende_auftrag", "weltdom_auftrag", "ablauf_stand", "regie_ergebnis", "bild_sofort"})
# G06: Anzeigeort (wo Raute, Terminal und Chat stehen) und Zielort (was der Agent sieht und bedient) sind getrennt.
ZIEL_ZUSTAENDE = ("ok", "verdeckt", "minimiert", "inaktiv", "weg", "unbekannt")
ZIEL_FAEHIGKEITEN = ("frisch", "fremde_pixel", "letztes_bild", "keine_aufnahme", "unbekannt")  # fremde_pixel: das Bild enthält auch Fenster, die das Ziel verdecken
# Live und verlustbehaftet gewollt: kein Journal, keine Quittung, keine Tastenaufzeichnung.
STREAM_KINDS = frozenset({"terminal_output", "terminal_input", "terminal_resize", "terminal_audio", "terminal_attach"})
MAX_TERMINAL_CHUNK = 65_536
MAX_TERMINAL_INPUT = 8_192
MAX_RAUTE_TIPPEN = 500  # Zeichen, die ein Agent mit seinen Händen in sein Eingabefeld tippen darf
MAX_AUDIO_BYTES = 1_000_000  # eine Äußerung als WAV (16 kHz, mono, 16 Bit): höchstens etwa 30 s
MAX_SPRACHE_TEXT = 4_000


class ProtocolError(ValueError):
    pass


def identifier(value):
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value):
        raise ProtocolError("invalid_identifier")
    return value


def decode(raw):
    if not isinstance(raw, str) or len(raw.encode()) > MAX_WIRE:
        raise ProtocolError("invalid_message")
    try:
        value = json.loads(raw)
    except (ValueError, RecursionError):
        raise ProtocolError("invalid_json") from None
    if not isinstance(value, dict) or type(value.get("v")) is not int or value["v"] != 1:
        raise ProtocolError("unsupported_protocol")
    return value


@dataclass(frozen=True)
class Principal:
    session_id: str
    token: str
    peer_id: str
    target_id: str
    can_publish_frames: bool = False
    can_request_inventory: bool = False
    can_publish_inventory: bool = False
    can_control_terminals: bool = False
    can_serve_terminals: bool = False


class Journal:
    """Private local metadata journal. Never stores tokens, text or image bytes."""

    def __init__(self, path: str | Path):
        self.db = sqlite3.connect(str(path))
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS messages (
                sender TEXT NOT NULL, message_id TEXT NOT NULL,
                fingerprint TEXT NOT NULL, status TEXT NOT NULL,
                PRIMARY KEY(sender, message_id));
            CREATE TABLE IF NOT EXISTS events (
                sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                at_ms INTEGER NOT NULL, kind TEXT NOT NULL,
                session_id TEXT NOT NULL, message_id TEXT, status TEXT NOT NULL);
        """)

    def event(self, kind, session_id, message_id=None, status=""):
        with self.db:
            self.db.execute("INSERT INTO events(at_ms,kind,session_id,message_id,status) VALUES(?,?,?,?,?)",
                            (int(time.time()*1000), kind, session_id, message_id, status))

    def reserve(self, sender, message_id, fingerprint):
        old = self.db.execute("SELECT fingerprint,status FROM messages WHERE sender=? AND message_id=?",
                              (sender, message_id)).fetchone()
        if old:
            if old[0] != fingerprint:
                raise ProtocolError("id_conflict")
            return old[1]
        with self.db:
            self.db.execute("INSERT INTO messages VALUES(?,?,?,?)", (sender, message_id, fingerprint, "accepted"))
        self.event("message.accepted", sender, message_id, "accepted")
        return None

    def status(self, sender, message_id, status):
        with self.db:
            self.db.execute("UPDATE messages SET status=? WHERE sender=? AND message_id=?",
                            (status, sender, message_id))
        self.event("message." + status, sender, message_id, status)

    def close(self):
        self.db.close()


@dataclass
class Connection:
    socket: object
    principal: Principal
    epoch: str


class Relay:
    def __init__(self, principals, journal: Journal, *, auth_timeout=5.0, receipt_ttl=30.0):
        self.principals = tuple(principals)
        if not self.principals:
            raise ValueError("principals_required")
        ids = set()
        tokens = set()
        for p in self.principals:
            identifier(p.session_id); identifier(p.peer_id); identifier(p.target_id)
            if not isinstance(p.token, str) or len(p.token) < 32 or p.token in tokens or p.session_id in ids:
                raise ValueError("unique_sessions_and_strong_distinct_tokens_required")
            ids.add(p.session_id); tokens.add(p.token)
        for p in self.principals:
            if p.peer_id not in ids or p.peer_id == p.session_id:
                raise ValueError("invalid_peer_grant")
        self.journal = journal
        self.connections = {}
        self.pending = {}
        self.lock = asyncio.Lock()
        self.auth_timeout = auth_timeout
        self.receipt_ttl = receipt_ttl

    async def send(self, ws, data):
        await asyncio.wait_for(ws.send(json.dumps({"v": 1, **data}, ensure_ascii=False)), 2.0)

    async def handler(self, ws):
        conn = None
        try:
            hello = decode(await asyncio.wait_for(ws.recv(), self.auth_timeout))
            if set(hello) != {"v", "kind", "token"} or hello["kind"] != "hello" or not isinstance(hello["token"], str):
                raise ProtocolError("authentication_required")
            principal = next((p for p in self.principals
                              if hmac.compare_digest(p.token.encode(), hello["token"].encode())), None)
            if principal is None:
                raise ProtocolError("authentication_failed")
            if principal.session_id in self.connections:
                raise ProtocolError("session_already_connected")
            conn = Connection(ws, principal, uuid.uuid4().hex)
            self.connections[principal.session_id] = conn
            self.journal.event("session.connected", principal.session_id)
            capabilities = ["say", "receipt"]
            if principal.can_publish_frames:
                capabilities.append("frame")
            if principal.can_request_inventory:
                capabilities.append("target_inventory_request")
            if principal.can_publish_inventory:
                capabilities.append("target_inventory")
            if principal.can_control_terminals:
                capabilities.append("terminal_control")
            if principal.can_serve_terminals:
                capabilities.append("terminal_serve")
            if principal.can_control_terminals or principal.can_serve_terminals:
                capabilities.append("anzeigeorte")  # G06: dieser Relay versteht Anzeigeorte (ältere Körper kennen die Fähigkeit nicht und senden nichts davon)
            await self.send(ws, {"kind": "welcome", "session_id": principal.session_id,
                                 "epoch": conn.epoch, "target_id": principal.target_id,
                                 "peer_id": principal.peer_id, "capabilities": capabilities})
            async for raw in ws:
                try:
                    data = decode(raw)
                    async with self.lock:
                        await self.route(conn, data)
                except ProtocolError as error:
                    self.journal.event("request.denied", principal.session_id, status=str(error))
                    await self.send(ws, {"kind": "error", "reason": str(error)})
        except (ProtocolError, asyncio.TimeoutError) as error:
            try:
                await self.send(ws, {"kind": "error", "reason": str(error) or "timeout"})
                await ws.close(code=1008, reason="handshake_or_transport_failed")
            except (ConnectionClosed, asyncio.TimeoutError):
                pass
        except ConnectionClosed:
            pass
        finally:
            if conn is not None:
                self.connections.pop(conn.principal.session_id, None)
                self.journal.event("session.disconnected", conn.principal.session_id)
                # Receipts from an old connection must not confirm a new delivery.
                for key, item in list(self.pending.items()):
                    if conn in (item[0], item[1]):
                        del self.pending[key]

    @staticmethod
    def _bounded_int(value, low, high, reason):
        if type(value) is not int or not low <= value <= high:
            raise ProtocolError(reason)
        return value

    @staticmethod
    def _bounded_text(value, limit, reason):
        if not isinstance(value, str) or not 1 <= len(value) <= limit:
            raise ProtocolError(reason)
        return value

    @staticmethod
    def _bytes_field(value, limit, reason):
        if not isinstance(value, str):
            raise ProtocolError(reason)
        try:
            blob = base64.b64decode(value, validate=True)
        except ValueError:
            raise ProtocolError("invalid_base64") from None
        if not 1 <= len(blob) <= limit:
            raise ProtocolError(reason)
        return blob

    def terminal_payload(self, kind, value):
        """Strict shapes for the bridge-owned terminal; unknown fields are rejected."""
        size = self._bounded_int
        if kind == "terminal_list_request":
            if value:
                raise ProtocolError("invalid_terminal_list_request")
            return value
        if kind == "terminal_start":
            if set(value) != {"start_id", "rows", "cols"}:
                raise ProtocolError("invalid_terminal_start")
            identifier(value["start_id"])
            size(value["rows"], 1, 1000, "invalid_terminal_size")
            size(value["cols"], 1, 1000, "invalid_terminal_size")
            return value
        if kind == "terminal_close":
            if set(value) != {"terminal_id"}:
                raise ProtocolError("invalid_terminal_close")
            identifier(value["terminal_id"])
            return value
        if kind == "terminal_steuern":  # G09: Daniel hält die Prozessgruppe eines Agenten an oder lässt sie weiterlaufen
            if set(value) != {"terminal_id", "aktion"} or value["aktion"] not in STEUER_AKTIONEN:
                raise ProtocolError("invalid_terminal_steuern")
            identifier(value["terminal_id"])
            return value
        if kind == "haende_auftrag":  # G10: der Starter reicht einen Hände-Auftrag eines Agenten an den Desktop des Ziels
            if set(value) != {"terminal_id", "auftrag_id", "ziel", "lease", "lease_bis_ms", "seq", "aktion"}:
                raise ProtocolError("invalid_haende_auftrag")
            identifier(value["terminal_id"])
            identifier(value["auftrag_id"])
            identifier(value["lease"])
            if not isinstance(value["ziel"], str) or not 1 <= len(value["ziel"]) <= 160:
                raise ProtocolError("invalid_haende_auftrag")
            size(value["lease_bis_ms"], 0, 2**53, "invalid_haende_auftrag")
            if value["seq"] is not None:
                size(value["seq"], 0, 2**53, "invalid_haende_auftrag")
            if not isinstance(value["aktion"], dict) or len(json.dumps(value["aktion"])) > 2000:
                raise ProtocolError("invalid_haende_auftrag")
            return value
        if kind == "ablauf_steuern":  # G12: Daniel steuert Abläufe (starten, pausieren, fortsetzen, abbrechen, Zweig, Freigaben, Lernen)
            felder = {"aktion", "lauf_id", "ablauf_id", "terminal_id", "checkpoint", "frage_id", "modi", "an", "seed_id", "loop_id"}
            if not set(value) <= felder or "aktion" not in value or value["aktion"] not in ("start", "pausieren", "fortsetzen", "abbrechen", "zweig", "freigeben", "verweigern", "lernen", "bereich",
                                                                                           "seed_zurueckziehen", "loop_stoppen"):
                raise ProtocolError("invalid_ablauf_steuern")
            for k in ("lauf_id", "ablauf_id", "terminal_id", "checkpoint", "frage_id", "seed_id", "loop_id"):
                if value.get(k) is not None:
                    identifier(value[k])
            if value.get("an") is not None and type(value["an"]) is not bool:
                raise ProtocolError("invalid_ablauf_steuern")
            if value.get("modi") is not None and (not isinstance(value["modi"], list) or len(value["modi"]) > 6 or any(not isinstance(m, str) or len(m) > 24 for m in value["modi"])):
                raise ProtocolError("invalid_ablauf_steuern")
            return value
        if kind == "regie_spruch":  # G12: ein Regiespruch mit der Frage, was er wirklich bewirkt
            if set(value) != {"terminal_id", "spruch"} or not isinstance(value["spruch"], str) or not 1 <= len(value["spruch"]) <= 60:
                raise ProtocolError("invalid_regie_spruch")
            identifier(value["terminal_id"])
            return value
        if kind == "ablauf_stand":  # G12: der Stand der Abläufe für die Oberfläche (begrenzt)
            if set(value) - {"seeds"} != {"laeufe", "offen", "lernen", "ablaeufe"} or (value.get("seeds") is not None and (not isinstance(value["seeds"], list) or len(value["seeds"]) > 20)) or type(value["lernen"]) is not bool or not all(isinstance(value[k], list) for k in ("laeufe", "offen", "ablaeufe")) \
                    or len(value["laeufe"]) > 20 or len(value["offen"]) > 10 or len(value["ablaeufe"]) > 20 or len(json.dumps(value)) > 60_000:
                raise ProtocolError("invalid_ablauf_stand")
            return value
        if kind == "regie_ergebnis":
            if set(value) != {"terminal_id", "spruch", "wirkung", "aktion", "hinweis", "zugestellt"} or type(value["zugestellt"]) is not bool:
                raise ProtocolError("invalid_regie_ergebnis")
            identifier(value["terminal_id"])
            for k, n in (("spruch", 60), ("wirkung", 20), ("aktion", 40), ("hinweis", 400)):
                if not isinstance(value[k], str) or len(value[k]) > n:
                    raise ProtocolError("invalid_regie_ergebnis")
            return value
        if kind == "weltdom_auftrag":  # G11: ein Befehl des Agenten an den WorldDOM des Zielfensters
            if set(value) != {"terminal_id", "auftrag_id", "befehl", "ziel", "lease_bis_ms", "seq", "args"}:
                raise ProtocolError("invalid_weltdom_auftrag")
            identifier(value["terminal_id"])
            identifier(value["auftrag_id"])
            if value["befehl"] not in ("liste", "aktion", "zeige", "anker_neu", "anker_weg", "profil_speichern", "profil_laden", "profil_liste", "profil_weg", "markiert") or not isinstance(value["ziel"], str) or not 1 <= len(value["ziel"]) <= 160:
                raise ProtocolError("invalid_weltdom_auftrag")
            size(value["lease_bis_ms"], 0, 2**53, "invalid_weltdom_auftrag")
            if value["seq"] is not None:
                size(value["seq"], 0, 2**53, "invalid_weltdom_auftrag")
            if not isinstance(value["args"], dict) or len(json.dumps(value["args"])) > 2500:
                raise ProtocolError("invalid_weltdom_auftrag")
            return value
        if kind == "weltdom_ergebnis":  # G11: was aus dem Befehl wurde (Knoten, Quellen, Rücklese …), begrenzt
            if set(value) != {"terminal_id", "auftrag_id", "status", "daten"}:
                raise ProtocolError("invalid_weltdom_ergebnis")
            identifier(value["terminal_id"])
            identifier(value["auftrag_id"])
            if not isinstance(value["status"], str) or not 1 <= len(value["status"]) <= 30 or not isinstance(value["daten"], dict) or len(json.dumps(value["daten"])) > 200_000:
                raise ProtocolError("invalid_weltdom_ergebnis")
            return value
        if kind == "haende_ergebnis":  # G10: der Körper meldet, was aus dem Auftrag wurde (zugelassen, übergeben, beobachtet, protokolliert getrennt)
            if set(value) != {"terminal_id", "auftrag_id", "status", "grund", "accepted", "delivered", "observed", "dauer_ms", "audited"}:
                raise ProtocolError("invalid_haende_ergebnis")
            identifier(value["terminal_id"])
            identifier(value["auftrag_id"])
            if value["status"] not in ("ausgefuehrt", "abgelehnt", "abgebrochen", "fehler") or not isinstance(value["grund"], str) or len(value["grund"]) > 60:
                raise ProtocolError("invalid_haende_ergebnis")
            if type(value["accepted"]) is not bool or type(value["audited"]) is not bool or not isinstance(value["observed"], dict) or len(json.dumps(value["observed"])) > 600:
                raise ProtocolError("invalid_haende_ergebnis")
            size(value["delivered"], 0, 1_000_000, "invalid_haende_ergebnis")
            size(value["dauer_ms"], 0, 10_000_000, "invalid_haende_ergebnis")
            return value
        if kind == "terminal_attach":  # die Bridge nimmt eine laufende Sitzung wieder auf: der Starter spielt die letzte Ausgabe noch einmal
            if set(value) != {"terminal_id"}:
                raise ProtocolError("invalid_terminal_attach")
            identifier(value["terminal_id"])
            return value
        if kind == "anzeigeorte_request":
            if value:
                raise ProtocolError("invalid_anzeigeorte_request")
            return value
        if kind in ("terminal_umziehen", "terminal_ziel"):
            if set(value) != {"terminal_id", "ort"}:
                raise ProtocolError("invalid_" + kind)
            identifier(value["terminal_id"])
            identifier(value["ort"])
            return value
        if kind == "ziel_zustand":
            if set(value) != {"terminal_id", "target_id", "zustand", "faehigkeit", "seit_ms"}:
                raise ProtocolError("invalid_ziel_zustand")
            identifier(value["terminal_id"])
            if value["target_id"] is not None:
                self._bounded_text(value["target_id"], 512, "invalid_ziel_zustand")
            if value["zustand"] not in ZIEL_ZUSTAENDE or value["faehigkeit"] not in ZIEL_FAEHIGKEITEN:
                raise ProtocolError("invalid_ziel_zustand")
            size(value["seit_ms"], 0, 2**53, "invalid_ziel_zustand")
            return value
        if kind == "lage":  # das Lagebild eines Agenten (lage.py): Lampen mit Funktion, Farbe, Wort, Behebung und Gruppe
            from . import lage as lagebild

            if set(value) != {"terminal_id", "lampen"} or not lagebild.gueltig(value) or len(value["lampen"]) > lagebild.MAX_LAMPEN:
                raise ProtocolError("invalid_lage")
            identifier(value["terminal_id"])
            return value
        if kind == "anzeigeorte":
            if set(value) != {"orte"} or not isinstance(value["orte"], list) or not 1 <= len(value["orte"]) <= 16:
                raise ProtocolError("invalid_anzeigeorte")
            for ort in value["orte"]:
                if not isinstance(ort, dict) or set(ort) != {"ort", "name", "online"} or type(ort["online"]) is not bool:
                    raise ProtocolError("invalid_anzeigeorte")
                identifier(ort["ort"])
                self._bounded_text(ort["name"], 60, "invalid_anzeigeorte")
            return value
        if kind == "terminal_ort":
            pflicht = {"terminal_id", "laufort", "anzeigeort", "zielort", "aktiv", "pid", "gestartet", "ziel", "grund"}
            if set(value) != pflicht or type(value["aktiv"]) is not bool:
                raise ProtocolError("invalid_terminal_ort")
            identifier(value["terminal_id"])
            for feld in ("laufort", "anzeigeort", "zielort"):
                self._bounded_text(value[feld], 40, "invalid_terminal_ort")
            size(value["pid"], 0, 2**31, "invalid_terminal_ort")
            size(value["gestartet"], 0, 2**41, "invalid_terminal_ort")
            ziel = value["ziel"]
            if (not isinstance(ziel, dict) or set(ziel) != {"target_id", "zustand", "faehigkeit"}
                    or ziel["zustand"] not in ZIEL_ZUSTAENDE or ziel["faehigkeit"] not in ZIEL_FAEHIGKEITEN
                    or (ziel["target_id"] is not None and (not isinstance(ziel["target_id"], str) or len(ziel["target_id"]) > 512))):
                raise ProtocolError("invalid_terminal_ort")
            if not isinstance(value["grund"], str) or len(value["grund"]) > 80:
                raise ProtocolError("invalid_terminal_ort")
            return value
        if kind == "terminal_resize":
            if set(value) != {"terminal_id", "rows", "cols"}:
                raise ProtocolError("invalid_terminal_resize")
            identifier(value["terminal_id"])
            size(value["rows"], 1, 1000, "invalid_terminal_size")
            size(value["cols"], 1, 1000, "invalid_terminal_size")
            return value
        if kind == "terminal_input":
            if set(value) != {"terminal_id", "data"}:
                raise ProtocolError("invalid_terminal_input")
            identifier(value["terminal_id"])
            self._bytes_field(value["data"], MAX_TERMINAL_INPUT, "invalid_terminal_input")
            return value
        if kind == "terminal_output":
            pflicht = {"terminal_id", "seq", "data"}
            if not pflicht <= set(value) <= pflicht | {"replay"} or ("replay" in value and value["replay"] is not True):
                raise ProtocolError("invalid_terminal_output")  # "replay": true steht nur am ersten Stück einer Wiederaufnahme
            identifier(value["terminal_id"])
            size(value["seq"], 0, 2**53, "invalid_terminal_sequence")
            self._bytes_field(value["data"], MAX_TERMINAL_CHUNK, "invalid_terminal_output")
            return value
        if kind == "raute_say":
            if set(value) != {"terminal_id", "text"}:
                raise ProtocolError("invalid_raute_say")
            identifier(value["terminal_id"])
            self._bounded_text(value["text"], 8000, "invalid_text")
            return value
        if kind == "terminal_audio":
            if set(value) != {"terminal_id", "mime", "data", "dauer_ms"}:
                raise ProtocolError("invalid_terminal_audio")
            identifier(value["terminal_id"])
            if value["mime"] != "audio/wav":
                raise ProtocolError("invalid_terminal_audio")
            size(value["dauer_ms"], 1, 120_000, "invalid_terminal_audio")
            blob = self._bytes_field(value["data"], MAX_AUDIO_BYTES, "invalid_terminal_audio")
            if not blob.startswith(b"RIFF"):
                raise ProtocolError("invalid_audio_signature")
            return value
        if kind == "sprache_text":
            if set(value) != {"terminal_id", "text", "dauer_ms", "modell"}:
                raise ProtocolError("invalid_sprache_text")
            identifier(value["terminal_id"])
            self._bounded_text(value["text"], MAX_SPRACHE_TEXT, "invalid_text")
            size(value["dauer_ms"], 0, 120_000, "invalid_sprache_text")
            self._bounded_text(value["modell"], 60, "invalid_sprache_text")
            return value
        if kind == "bild_sofort":
            if set(value) != {"terminal_id"}:
                raise ProtocolError("invalid_bild_sofort")
            identifier(value["terminal_id"])
            return
        if kind == "raute_tippen":
            if set(value) not in ({"terminal_id", "text"}, {"terminal_id", "text", "request_id"}):
                raise ProtocolError("invalid_raute_tippen")
            identifier(value["terminal_id"])
            if "request_id" in value:
                identifier(value["request_id"])
            self._bounded_text(value["text"], MAX_RAUTE_TIPPEN, "invalid_text")
            return value
        if kind == "raute_tippen_ergebnis":
            if set(value) != {"terminal_id", "request_id", "ok", "grund"} or type(value["ok"]) is not bool:
                raise ProtocolError("invalid_raute_tippen_ergebnis")
            identifier(value["terminal_id"])
            identifier(value["request_id"])
            if not isinstance(value["grund"], str) or len(value["grund"]) > 80:
                raise ProtocolError("invalid_raute_tippen_ergebnis")
            return value
        if kind == "terminal_state":
            if set(value) != {"terminal_id", "start_id", "name", "state", "exit_code", "reason"}:
                raise ProtocolError("invalid_terminal_state")
            identifier(value["terminal_id"])
            identifier(value["start_id"])
            self._bounded_text(value["name"], 120, "invalid_terminal_state")
            if value["state"] not in TERMINAL_STATES:
                raise ProtocolError("invalid_terminal_state")
            if value["exit_code"] is not None:
                size(value["exit_code"], -2**31, 2**31, "invalid_terminal_state")
            if not isinstance(value["reason"], str) or len(value["reason"]) > 200:
                raise ProtocolError("invalid_terminal_state")
            return value
        # terminal_list
        if set(value) != {"request_id", "starts", "terminals"}:
            raise ProtocolError("invalid_terminal_list")
        identifier(value["request_id"])
        starts, terminals = value["starts"], value["terminals"]
        if not isinstance(starts, list) or not isinstance(terminals, list) or len(starts) > 64 or len(terminals) > 64:
            raise ProtocolError("invalid_terminal_list")
        seen = set()
        for start in starts:
            if not isinstance(start, dict) or set(start) != {"start_id", "name", "ort", "ordner", "programm"}:
                raise ProtocolError("invalid_terminal_list")
            identifier(start["start_id"])
            if start["start_id"] in seen:
                raise ProtocolError("duplicate_start_id")
            seen.add(start["start_id"])
            self._bounded_text(start["name"], 120, "invalid_terminal_list")
            self._bounded_text(start["ort"], 40, "invalid_terminal_list")
            if any(not isinstance(start[f], str) or len(start[f]) > 512 for f in ("ordner", "programm")):
                raise ProtocolError("invalid_terminal_list")
        for terminal in terminals:
            if (not isinstance(terminal, dict) or not {"terminal_id", "start_id", "name", "state", "rows", "cols"} <= set(terminal)
                    <= {"terminal_id", "start_id", "name", "state", "rows", "cols", "pid", "gestartet"}):
                raise ProtocolError("invalid_terminal_list")
            identifier(terminal["terminal_id"])
            identifier(terminal["start_id"])
            self._bounded_text(terminal["name"], 120, "invalid_terminal_list")
            if terminal["state"] not in TERMINAL_STATES:
                raise ProtocolError("invalid_terminal_list")
            size(terminal["rows"], 1, 1000, "invalid_terminal_size")
            size(terminal["cols"], 1, 1000, "invalid_terminal_size")
            if "pid" in terminal:  # Identität der Sitzung: Prozess und Startzeit (Sekunden), damit eine neue Shell erkennbar ist
                size(terminal["pid"], 0, 2**31, "invalid_terminal_list")
                size(terminal["gestartet"], 0, 2**41, "invalid_terminal_list")
        return value

    def payload(self, conn, kind, value):
        if not isinstance(value, dict):
            raise ProtocolError("invalid_payload")
        if kind == "say":
            if set(value) != {"text"} or not isinstance(value["text"], str) or not 1 <= len(value["text"]) <= 8000:
                raise ProtocolError("invalid_text")
            return value
        if kind == "target_inventory_request":
            if not conn.principal.can_request_inventory:
                raise ProtocolError("unsupported_capability")
            if set(value) != {"scope"} or value["scope"] != "terminals":
                raise ProtocolError("invalid_inventory_request")
            return value
        if kind == "target_inventory":
            if not conn.principal.can_publish_inventory:
                raise ProtocolError("unsupported_capability")
            required = {"request_id", "status", "captured_at_ms", "targets"}
            if set(value) != required:
                raise ProtocolError("invalid_inventory")
            if not isinstance(value["request_id"], str) or not IDENTIFIER.fullmatch(value["request_id"]):
                raise ProtocolError("invalid_inventory_request_id")
            if value["status"] not in ("ok", "degraded", "error", "unavailable"):
                raise ProtocolError("invalid_inventory_status")
            if type(value["captured_at_ms"]) is not int or value["captured_at_ms"] < 0:
                raise ProtocolError("invalid_inventory_time")
            targets = value["targets"]
            if not isinstance(targets, list) or len(targets) > 64:
                raise ProtocolError("invalid_inventory_targets")
            required_target = {"id", "kind", "host", "label", "source", "availability", "capture_method", "identity"}
            seen_target_ids = set()
            for target in targets:
                if not isinstance(target, dict) or set(target) != required_target:
                    raise ProtocolError("invalid_inventory_target")
                if any(not isinstance(target[field], str) for field in required_target):
                    raise ProtocolError("invalid_inventory_target")
                if not IDENTIFIER.fullmatch(target["id"]):
                    raise ProtocolError("invalid_inventory_target_id")
                if target["id"] in seen_target_ids:
                    raise ProtocolError("duplicate_inventory_target_id")
                seen_target_ids.add(target["id"])
                if target["kind"] != "linux.terminal":
                    raise ProtocolError("invalid_inventory_target_kind")
                if target["availability"] not in ("available", "unavailable", "remote-reported"):
                    raise ProtocolError("invalid_inventory_availability")
                if any(len(target[field]) > 512 for field in
                       ("host", "label", "source", "availability", "capture_method")):
                    raise ProtocolError("inventory_target_field_too_long")
                if len(target["identity"]) > 512:
                    raise ProtocolError("invalid_inventory_identity")
            return value
        if kind in DESKTOP_TERMINAL_KINDS:
            if not conn.principal.can_control_terminals:
                raise ProtocolError("unsupported_capability")
            return self.terminal_payload(kind, value)
        if kind in LAUNCHER_TERMINAL_KINDS:
            if not conn.principal.can_serve_terminals:
                raise ProtocolError("unsupported_capability")
            return self.terminal_payload(kind, value)
        if kind != "frame" or not conn.principal.can_publish_frames:
            raise ProtocolError("unsupported_capability")
        frame_fields = {"mime", "data", "source", "captured_at_ms", "width", "height"}
        if not frame_fields <= set(value) <= frame_fields | {"terminal_id", "aufnahme", "fallback_grund", "seq"}:
            raise ProtocolError("invalid_frame")
        if "aufnahme" in value and value["aufnahme"] not in ("fenster", "ausschnitt", "markiert"):
            raise ProtocolError("invalid_frame_aufnahme")
        if "fallback_grund" in value and (not isinstance(value["fallback_grund"], str) or len(value["fallback_grund"]) > 80):
            raise ProtocolError("invalid_frame_grund")
        if "seq" in value and (type(value["seq"]) is not int or not 0 <= value["seq"] <= 2**53):
            raise ProtocolError("invalid_frame_seq")
        if "terminal_id" in value:
            identifier(value["terminal_id"])
        if value["mime"] not in ("image/png", "image/jpeg") or value["source"] not in ("capture", "file", "synthetic"):
            raise ProtocolError("invalid_frame_metadata")
        if any(type(value[k]) is not int or not 1 <= value[k] <= 8192 for k in ("width", "height")):
            raise ProtocolError("invalid_dimensions")
        if type(value["captured_at_ms"]) is not int or value["captured_at_ms"] < 0:
            raise ProtocolError("invalid_capture_time")
        if not isinstance(value["data"], str) or len(value["data"]) > 1_400_000:
            raise ProtocolError("frame_too_large")
        try:
            blob = base64.b64decode(value["data"], validate=True)
        except ValueError:
            raise ProtocolError("invalid_base64") from None
        signature = b"\x89PNG\r\n\x1a\n" if value["mime"] == "image/png" else b"\xff\xd8\xff"
        if not blob.startswith(signature):
            raise ProtocolError("invalid_image_signature")
        # Metadata is sender-declared, not proof of capture or decoded dimensions.
        return {**value, "sha256": hashlib.sha256(blob).hexdigest(), "metadata_verified": False}

    async def route(self, conn, data):
        if data.get("epoch") != conn.epoch:
            raise ProtocolError("stale_connection")
        now = time.monotonic()
        self.pending = {key: value for key, value in self.pending.items() if value[3] > now}
        if data.get("kind") == "receipt":
            if set(data) != {"v", "kind", "epoch", "delivery_id"}:
                raise ProtocolError("invalid_receipt")
            delivery = identifier(data["delivery_id"])
            item = self.pending.get(delivery)
            if not item or item[1] is not conn:
                raise ProtocolError("unknown_delivery")
            sender, _, message_id, _ = self.pending.pop(delivery)
            self.journal.status(sender.principal.session_id, message_id, "received")
            await self.send(conn.socket, {"kind": "receipt_recorded", "delivery_id": delivery})
            if self.connections.get(sender.principal.session_id) is sender:
                try:
                    await self.send(sender.socket, {"kind": "result", "id": message_id, "status": "received"})
                except (ConnectionClosed, asyncio.TimeoutError):
                    pass
            return
        if set(data) != {"v", "kind", "epoch", "id", "recipient", "target_id", "payload"}:
            raise ProtocolError("invalid_envelope")
        message_id = identifier(data["id"])
        if data["recipient"] != conn.principal.peer_id or data["target_id"] != conn.principal.target_id:
            raise ProtocolError("grant_denied")
        payload = self.payload(conn, data["kind"], data["payload"])
        if data["kind"] in STREAM_KINDS:
            await self.forward_stream(conn, data, payload)
            return
        fingerprint = hashlib.sha256(json.dumps({k: v for k, v in data.items() if k != "epoch"},
                                                sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        old = self.journal.reserve(conn.principal.session_id, message_id, fingerprint)
        if old is not None:
            await self.send(conn.socket, {"kind": "result", "id": message_id, "status": old, "duplicate": True})
            return
        peer = self.connections.get(conn.principal.peer_id)
        status = "peer_offline"
        if peer and peer.principal.target_id == conn.principal.target_id:
            if len(self.pending) >= 128:
                status = "backpressure"
            else:
                delivery_id = uuid.uuid4().hex
                self.pending[delivery_id] = (conn, peer, message_id, now + self.receipt_ttl)
                try:
                    await self.send(peer.socket, {"kind": "event", "event_kind": data["kind"],
                        "id": message_id, "delivery_id": delivery_id, "sender": conn.principal.session_id,
                        "recipient": peer.principal.session_id, "target_id": conn.principal.target_id,
                        "received_at_ms": int(time.time()*1000), "payload": payload})
                    status = "forwarded"
                except (ConnectionClosed, asyncio.TimeoutError):
                    self.pending.pop(delivery_id, None)
                    status = "delivery_unknown"
        self.journal.status(conn.principal.session_id, message_id, status)
        await self.send(conn.socket, {"kind": "result", "id": message_id, "status": status, "duplicate": False})

    async def forward_stream(self, conn, data, payload):
        """Terminal bytes are live: no journal row, no receipt, no result for the sender.

        Nobody watching means the bytes are dropped; the launcher keeps the screen state itself.
        """
        peer = self.connections.get(conn.principal.peer_id)
        if peer is None or peer.principal.target_id != conn.principal.target_id:
            return
        try:
            await self.send(peer.socket, {"kind": "event", "event_kind": data["kind"],
                "id": data["id"], "sender": conn.principal.session_id,
                "recipient": peer.principal.session_id, "target_id": conn.principal.target_id,
                "received_at_ms": int(time.time()*1000), "payload": payload})
        except (ConnectionClosed, asyncio.TimeoutError):
            pass

    def listen(self, port=0, *, origins=None):
        # Deliberately no public bind option until TLS/pairing/rate limits exist.
        return serve(self.handler, "127.0.0.1", port, origins=[None] if origins is None else origins,
                     max_size=MAX_WIRE, max_queue=4, compression=None,
                     ping_interval=20, ping_timeout=10, close_timeout=2)


async def main_async(args):
    journal = Journal(args.journal)
    try:
        relay = Relay([
            Principal("desktop", os.environ["BRIDGE_DESKTOP_TOKEN"], "agent", "desktop-main",
                      can_publish_frames=True, can_request_inventory=True),
            Principal("agent", os.environ["BRIDGE_AGENT_TOKEN"], "desktop", "desktop-main",
                      can_publish_inventory=True),
        ], journal)
        async with relay.listen(args.port) as server:
            print(f"Bridge local transport: ws://127.0.0.1:{server.sockets[0].getsockname()[1]}", flush=True)
            await asyncio.Future()
    finally:
        journal.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--journal", required=True, type=Path)
    parser.add_argument("--port", type=int, default=0)
    args = parser.parse_args()
    try:
        asyncio.run(main_async(args))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
