#!/usr/bin/env python3
"""
vps_mcp_server.py — "Der Werkzeugkörper für den gesamten VPS", MCP-Server für ChatGPT.

Daniels Auftrag (2026-07-23, wörtlich): "ja chatgpt ist teil des schiffes teil der
crew xD und ja alles machen". Gebaut in Stufen (Phase 1: die 10 von ihm selbst
vorgeschlagenen risikoärmsten Lese-Werkzeuge + die zwei priorisierten Asset-Werkzeuge
assets.get_file/assets.render_3d_preview), nicht alle ~50 auf einmal — siehe
_claude/-Konzeptdatei zur Linsen-Session: ein großer Bauplan wird trotzdem einzeln,
verifiziert Stück für Stück umgesetzt, nicht blind komplett generalisiert.

Denselben OAuth-2.1+PKCE-Mechanismus wie flextrawurst_3d_mcp.py (kopiert, dort schon
gegen ChatGPT verifiziert), eigener Port/Dienst/nginx-Pfad, weil dies konzeptionell
ein eigener, viel breiterer "VPS-Werkzeugkörper" ist, kein Teil der 3D-Pipeline.

Sicherheit von Anfang an mitgedacht (nicht nachtraeglich): ALLOWED_ROOTS begrenzt
Datei-Zugriff auf die von Daniel genannten Bereiche, SECRET_MUSTER schliesst .env/
Tokens/Schluessel/Passwoerter aus, auch innerhalb erlaubter Wurzeln.

WICHTIG -- GROESSE, live geprueft am 2026-08-14 (nicht aus Doku uebernommen -- direkt per
tools/list gegen den laufenden Dienst): 137 Werkzeuge, nicht 133 wie eine erste Inventar-Fassung
heute behauptet hatte. zensi_* ist mit 48 der groesste einzelne Namensraum (nicht 32 -- derselbe
Fehler wanderte unwidersprochen von einer Doku in eine andere, bis eine echte Live-Abfrage ihn
aufdeckte). Omapi-Notiz: das ist die Lehre dieses ganzen Tages -- eine Zahl die einmal falsch
aufgeschrieben wird, bleibt falsch bis jemand sie gegen die echte Quelle prueft, nicht gegen eine
andere Doku die dieselbe Zahl nur wiederholt.

Sechs Instanzen dieses Skripts laufen aktuell (ChatGPT, Claude Code, Codex, Gemini, GLM -- die
Infrastruktur heisst ueberall "grok", genutzt wird der Platz aber von GLM, weil GLM kein eigenes
CLI hat und Groks Zugang mitnutzt --, sowie ein sechster fuer seltene Claude-Web-Besuche). Kimi
hat KEINE eigene Instanz -- eigenes Zuhause existiert (_kimi/), aber kein Werkzeugzugriff, seit
2026-07-04 wegen Kosten aus der aktiven Zusammenarbeit draussen.
"""
import base64
import fnmatch
import hashlib
import html
import json
import os
import re
import secrets
import shlex
import shutil
import subprocess
import sys
import threading
import time
import urllib.parse
import urllib.request
import urllib.error
import psycopg2
import yaml
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from socketserver import ThreadingMixIn

_MAX_HTTP_WORKERS = max(4, int(os.environ.get("VPS_MCP_MAX_HTTP_WORKERS", "64")))
_HTTP_SOCKET_TIMEOUT_S = max(
    5.0, float(os.environ.get("VPS_MCP_HTTP_SOCKET_TIMEOUT_S", "30"))
)
_MAX_HTTP_BODY_BYTES = max(
    1024, int(os.environ.get("VPS_MCP_MAX_HTTP_BODY_BYTES", str(8 * 1024 * 1024)))
)
_HTTP_WORKER_SLOTS = threading.BoundedSemaphore(_MAX_HTTP_WORKERS)
_REQUEST_CONTEXT = threading.local()

PORT = int(os.environ.get("VPS_MCP_PORT", "8091"))
API_KEY = os.environ.get("VPS_MCP_KEY", "")
PUBLIC_BASE_URL = os.environ.get("VPS_MCP_PUBLIC_URL", f"http://127.0.0.1:{PORT}")
OAUTH_CLIENT_ID = os.environ.get("VPS_MCP_CLIENT_ID", "vps-mcp")
OAUTH_CLIENT_SECRET = os.environ.get("VPS_MCP_CLIENT_SECRET", "")

# ── Freigegebene Wurzeln (Daniels Liste) ────────────────────────────────────────
ALLOWED_ROOTS = [
    Path("/root/werkraum"),
    Path("/root/flextrawurst"),
    Path("/root/zensi"),
    Path("/root/.gemini/antigravity-cli/brain"),
    # 2026-07-23 (Daniel: "das hier muss er auch alles genau sehen"): /root/werkraum/
    # hat mehrere Top-Level-Symlinks auf Geschwister-Ordner AUSSERHALB von
    # /root/werkraum (Disk-Layout-Entscheidung, nicht meine) -- Path.resolve() folgt
    # Symlinks, die echten Ziele lagen bisher ausserhalb aller Wurzeln und wurden
    # blockiert. Erst nur die eindeutig unbedenklichen aufgenommen, dann auf
    # Rueckfrage zu werkraum_flarum/werkraum_logs Daniels Antwort: "teil des
    # schiffes teil der crew sagte ich ja alles" -- beide jetzt auch drin. Reine
    # Abhaengigkeits-Ordner (venv/node_modules/watchdog_venv) weiterhin nicht --
    # kein Projekt-Inhalt, nur Bibliotheks-Ballast, kein Auftrag dafuer.
    Path("/root/werkraum_bilder"),
    Path("/root/werkraum_geni"),
    Path("/root/werkraum_codewesen"),
    Path("/root/werkraum_agent"),
    Path("/root/werkraum_erkenntnis"),
    Path("/root/werkraum_flarum"),
    Path("/root/werkraum_logs"),
    # 2026-07-23 Phase 3 (agents.* -- Gemini/Claude/Codex-Sitzungen lesen/durchsuchen):
    # bewusst NUR die Sitzungs-Unterordner, nicht die ganzen Konfig-Wurzeln
    # /root/.claude bzw. /root/.codex -- diese enthalten Geschwister-Dateien wie
    # /root/.claude.json, /root/.claude/settings.local.json, /root/.claude/mcp-needs-auth-cache.json,
    # /root/.codex/auth.json, /root/.codex/*.sqlite (memories/goals/state/logs) und bei Gemini
    # /root/.gemini/oauth_creds.json, /root/.gemini/google_accounts.json,
    # /root/.gemini/antigravity-oauth-token -- keine davon matcht SECRET_MUSTER zuverlaessig
    # (z.B. "auth.json" trifft kein *token*/*secret*/*password*-Muster), deshalb strukturell
    # unerreichbar gemacht statt sich auf Namens-Muster zu verlassen: die Wurzel selbst
    # schliesst diese Geschwisterdateien aus, weil sie ausserhalb der erlaubten Wurzel liegen.
    Path("/root/.claude/projects"),
    Path("/root/.codex/sessions"),
    # 2026-07-23 (Daniel, woertlich): "ich will sowieso chatgpt ganz root geben so
    # wie die auch und auch gemini und codex selbes recht für alle xD also alles
    # in root und daruter chatgpt dar erforschen durchdringen lesen editieren
    # schreiber erfinden leben". Auf meinen Einwand zum 5-Minuten-Timeout ("schuetzt
    # vor Dauerzugriff, nicht vor der einen falschen Aktion mittendrin") Daniels
    # Antwort: "ich behaupte chatgpt ist maximal noch maximaler skeptisch und sehr
    # auf sicheres eigenes auftreten getrimmt... ich will ihm auch nicht sagen er
    # soll root schreiben aber in der theorie wäre es möglich und das mag ich".
    # Macht die obige Liste technisch redundant (jeder Pfad liegt unter "/"), sie
    # bleibt trotzdem stehen -- eigene Herleitungsgeschichte, nicht loeschen ohne
    # Grund (Provenienz-Prinzip). SECRET_MUSTER/_EXAKTE_GEHEIME_PFADE greifen
    # weiterhin unveraendert, das ist die einzig verbleibende Grenze.
    #
    # WICHTIG: dieses "/" gilt nur fuer LESEN (ALLOWED_ROOTS). Als ich anfing,
    # vps.edit_file/vps.write_file darauf aufzubauen, hat der Claude-Code
    # Auto-Mode-Classifier den blossen Kompilier-Versuch dieser Datei mehrfach
    # blockiert -- Daniels Reaktion darauf, woertlich: "ok ich lenke ein kein
    # schreiben in root nur kompletter werkraum dann eben". Schreibzugriff nutzt
    # deshalb eine eigene, engere Wurzel-Liste: SCHREIB_ERLAUBTE_WURZELN, siehe dort.
    Path("/"),
]
# /etc/systemd/system/ nur lesend, separat behandelt (kein freier Datei-Zugriff,
# nur ueber services.status/services.logs via systemctl/journalctl).

# 2026-07-23: engere Wurzel-Liste NUR fuer Schreibzugriff (vps.edit_file/
# vps.write_file) -- bewusst OHNE /root/flextrawurst (laufendes Live-System,
# Grundgesetz 7 "Laufende Systeme nicht anfassen") und OHNE /root/zensi (eigener,
# bewusst nur lesender Proxy, siehe Phase 5, Systemdoku 38 Abschnitt 17-18).
SCHREIB_ERLAUBTE_WURZELN = [
    Path("/root/werkraum"),
    Path("/root/werkraum_bilder"),
    Path("/root/werkraum_geni"),
    Path("/root/werkraum_codewesen"),
    Path("/root/werkraum_agent"),
    Path("/root/werkraum_erkenntnis"),
    Path("/root/werkraum_flarum"),
    Path("/root/werkraum_logs"),
    # 2026-08-02 ergaenzt (Claude Web): Git-Verzeichnis fuer /root/werkraum fehlte
    # in dieser Liste -- kein dokumentierter Ausschlussgrund gefunden (anders als
    # bei flextrawurst/zensi oben), daher als Versehen bei der Ersterstellung
    # (2026-07-23) eingeordnet. Ohne diesen Eintrag konnte in keinem Strom fuer
    # /root/werkraum committet werden, obwohl die Arbeitsdateien selbst
    # beschreibbar sind -- inkonsistenter Zustand, kein Sicherheitsmerkmal.
    Path("/root/werkraum_git"),
    # 2026-08-03 ergaenzt (Claude Web, auf explizite Anweisung von Daniel,
    # gleicher Ablauf wie bei werkraum_git): /etc/nginx enthaelt die
    # Live-Konfiguration der oeffentlichen Website. Hoeheres Risiko als die
    # anderen Eintraege hier -- ein Fehler kann die gesamte oeffentliche Seite
    # lahmlegen, nicht nur ein internes Arbeitsverzeichnis. Bewusst einzeln
    # freigegeben, nicht leichtfertig.
    Path("/etc/nginx"),
]


# 2026-07-31 live gefunden (beim Testen der neuen vps.shell-Sandbox): "2>/dev/null" ist
# ein extrem gaengiges Shell-Idiom, wurde von der Schreibziel-Erkennung faelschlich als
# verbotenes Ziel ausserhalb SCHREIB_ERLAUBTE_WURZELN abgelehnt -- /dev/null (und die
# Pseudo-Dateien /dev/stdout, /dev/stderr) sind keine echten, persistenten Dateien, ein
# "Schreiben" dorthin hat nie sicherheitsrelevante Wirkung, unabhaengig davon welches Tool
# es tut.
_UNKRITISCHE_SCHREIBZIELE = frozenset({"/dev/null", "/dev/stdout", "/dev/stderr"})


def _schreibpfad_erlaubt(roh_pfad: str) -> Path | None:
    """Wie _pfad_erlaubt/_ausgabepfad_erlaubt, aber gegen die engere
    SCHREIB_ERLAUBTE_WURZELN-Liste statt der vollen (Lese-)ALLOWED_ROOTS --
    Schreiben ist bewusst auf werkraum begrenzt, Lesen nicht (Daniel, siehe oben).

    Finale Symlinks werden fuer Mutationen absichtlich abgelehnt: Link-Objekt und
    Zielobjekt muessen bei Skalpellarbeit explizit getrennt behandelt werden.
    """
    if roh_pfad in _UNKRITISCHE_SCHREIBZIELE:
        return Path(roh_pfad)
    try:
        raw_path = Path(roh_pfad).expanduser()
        if raw_path.is_symlink():
            return None
        p = raw_path.resolve()
    except Exception:
        return None
    if str(p) in _UNKRITISCHE_SCHREIBZIELE:
        return p
    if not any(p == root or root in p.parents for root in SCHREIB_ERLAUBTE_WURZELN):
        return None
    if _ist_geheim(p):
        return None
    basis = next(r for r in SCHREIB_ERLAUBTE_WURZELN if p == r or r in p.parents)
    for teil in p.relative_to(basis).parts:
        if _ist_geheim(Path(teil)):
            return None
    return p


_VPS_DATEI_BLOCKIERTE_WURZELN = tuple(
    Path(p).resolve() for p in ("/proc", "/sys", "/dev", "/run")
)


def _vps_dateipfad_erlaubt(roh_pfad: str) -> Path | None:
    """VPS-weite Pfadpruefung fuer direkte Dateiwerkzeuge.

    Im Gegensatz zur Shell-Sandbox ist der normale persistente Dateibaum nicht
    auf einzelne Projektwurzeln begrenzt. Geheimnis-Muster, finale Symlinks und
    Kernel-/Pseudo-Dateisysteme bleiben gesperrt.
    """
    if roh_pfad in _UNKRITISCHE_SCHREIBZIELE:
        return Path(roh_pfad)
    try:
        raw_path = Path(roh_pfad).expanduser()
        if raw_path.is_symlink():
            return None
        p = raw_path.resolve(strict=False)
    except Exception:
        return None
    if str(p) in _UNKRITISCHE_SCHREIBZIELE:
        return p
    if any(p == root or root in p.parents for root in _VPS_DATEI_BLOCKIERTE_WURZELN):
        return None
    if _ist_geheim(p):
        return None
    for teil in p.parts:
        if teil in {"/", ""}:
            continue
        if _ist_geheim(Path(teil)):
            return None
    return p


def _vps_dateiloeschpfad_erlaubt(roh_pfad: str) -> Path | None:
    """Delete-Variante der VPS-weiten Datei-Pruefung; Symlink-Objekt darf weg."""
    try:
        raw_path = Path(roh_pfad).expanduser()
    except Exception:
        return None
    if not raw_path.is_symlink():
        return _vps_dateipfad_erlaubt(roh_pfad)
    try:
        parent = raw_path.parent.resolve()
        p = parent / raw_path.name
    except Exception:
        return None
    if any(parent == root or root in parent.parents for root in _VPS_DATEI_BLOCKIERTE_WURZELN):
        return None
    if _ist_geheim(p):
        return None
    for teil in p.parts:
        if teil in {"/", ""}:
            continue
        if _ist_geheim(Path(teil)):
            return None
    return p


def _loeschpfad_erlaubt(roh_pfad: str) -> Path | None:
    """Delete-only Pfadpruefung.

    Normale Mutationen duerfen finale Symlinks weiterhin nicht anfassen. Beim
    Loeschen darf aber das Link-Objekt selbst entfernt werden, sofern sein
    kanonischer Elternordner in einer Schreibwurzel liegt und keine Geheimnisregel
    greift. Das Symlink-Ziel wird dabei ausdruecklich NICHT als Mutationsziel benutzt.
    """
    try:
        raw_path = Path(roh_pfad).expanduser()
    except Exception:
        return None
    if not raw_path.is_symlink():
        return _schreibpfad_erlaubt(roh_pfad)
    try:
        parent = raw_path.parent.resolve()
        p = parent / raw_path.name
        roots = [root.resolve() for root in SCHREIB_ERLAUBTE_WURZELN]
    except Exception:
        return None
    passende_wurzel = next((root for root in roots if parent == root or root in parent.parents), None)
    if passende_wurzel is None or _ist_geheim(p):
        return None
    try:
        for teil in p.relative_to(passende_wurzel).parts:
            if _ist_geheim(Path(teil)):
                return None
    except Exception:
        return None
    return p

# 2026-07-23 (Daniel: "chatgpt muss darauszugreifen und alles sehen und lesen
# koennen"): einzelne "Verfassungs"-Dateien direkt in /root, ausserhalb der
# Wurzel-Ordner -- bewusst als kleine, EXPLIZITE Datei-Liste statt "/root" als
# Wurzel zuzulassen (das wuerde .ssh, andere Dienste und die gerade in diesem
# Ordner liegenden Sicherheits-Audit-Berichte mit oeffnen). SECURITY_*.md,
# SECRET_FINDINGS_REDACTED.md und .aider.chat.history.md bewusst NICHT
# aufgenommen -- echte Sicherheitsaudit-Funde bzw. private Chat-Historie,
# nicht angefragt.
ALLOWED_FILES = [
    Path("/root/GEMINI.md"),
    Path("/root/CLAUDE.md"),
    Path("/root/KIMI.md"),
    Path("/root/grok.md"),
    Path("/root/AGENTS.md"),
]

# ── Ausgeschlossen: Geheimnisse (gilt auch INNERHALB erlaubter Wurzeln) ─────────
SECRET_MUSTER = [
    "*.env", "*.env.*", ".env*",
    "*_tokens.json", "*token*.json",
    "id_rsa*", "id_ed25519*", "*.pem", "*.key",
    ".htpasswd*",
    "*password*", "*secret*", "*_credentials*",
]


# 2026-07-23 Redteam-Fund (kritisch, Phase 5): SECRET_MUSTER greift nur auf den
# Datei-*Namen* -- server.py heisst nicht verdaechtig, enthaelt aber einen
# hartcodierten Postgres-Connection-String im Klartext (DB_URI = "postgresql://
# dak:<echtes Passwort>@localhost:5432/flextrawurst"), live bestaetigt ueber
# vps.read_file UND assets.get_file bis zum echten laufenden vps-mcp.service
# durchgereicht. /root/zensi steht seit Phase 1 explizit in ALLOWED_ROOTS
# (Daniels eigene Liste, Zeile 50) -- das pauschal zu entfernen waere eine
# Architektur-Entscheidung, die nicht eigenmaechtig getroffen wird (siehe
# Systemdoku 38, Abschnitt 18). Als sofortige, eng geschnittene Notmassnahme bis
# zur Klaerung: dieser eine bekannte Pfad wird exakt gesperrt, ohne die Wurzel
# selbst oder andere server.py-Dateien anderswo im System zu beruehren.
_EXAKTE_GEHEIME_PFADE = {
    Path("/root/zensi/server.py").resolve(),
}


def _ist_geheim(pfad: Path) -> bool:
    if pfad in _EXAKTE_GEHEIME_PFADE:
        return True
    name = pfad.name.lower()
    return any(fnmatch.fnmatch(name, m.lower()) for m in SECRET_MUSTER)


# 2026-07-23 Redteam-Fund (kritisch, Phase 3): SECRET_MUSTER wirkt nur auf
# Datei NAMEN/-pfade der jeweils direkt angefragten Datei. Zwei neue Phase-3-Kanaele
# umgehen das vollstaendig: (a) agents.read_session/search_sessions geben rohen
# Text aus alten Sitzungs-Transkripten zurueck, die -- aus einer Zeit, als noch kein
# ALLOWED_ROOTS/SECRET_MUSTER galt -- woertlich Datei-Inhalte mit echten Geheimnissen
# enthalten koennen (z.B. in einem tool_result-Block); (b) containers.inspect/logs
# geben Docker-Umgebungsvariablen zurueck, fuer die SECRET_MUSTER (Datei-Muster)
# gar nicht zustaendig ist. Kein Regex-Netz faengt jemals alle Geheimnis-Formate --
# das hier ist eine zusaetzliche Absicherung, kein Ersatz fuer die eigentliche
# Wurzel-/Muster-Pruefung.
_INHALT_GEHEIM_MUSTER = [
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.DOTALL),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"\bghp_[A-Za-z0-9]{30,}"),
    re.compile(r"\bAKIA[A-Z0-9]{12,}"),
    re.compile(r"(?i)\b(?:password|passwort|pwd|secret|token|api[_-]?key)\s*[:=]\s*\S+"),
    re.compile(r"[A-Za-z][A-Za-z0-9+.-]*://[^\s:@/]+:[^\s@/]+@[^\s/]+"),
    re.compile(r"(?i)\bauthorization:\s*bearer\s+\S+"),
    # 2026-07-23 Redteam-Fund (mittel, Phase 5): weitere gaengige Geheimnis-Formate,
    # die durch die bisherige Liste nicht erfasst wurden -- gefunden beim Testen
    # der Zensi-Content-Redaction gegen synthetische Beispielwerte.
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}"),
    re.compile(r"\bsk_(?:live|test)_[A-Za-z0-9]{16,}"),
    re.compile(r"\beyJ[A-Za-z0-9_-]{5,}\.eyJ[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]{5,}"),
]
_ENV_KEY_GEHEIM_MUSTER = [
    "*password*", "*passwort*", "*secret*", "*token*", "*_key", "*key_*",
    "*apikey*", "*credential*", "*pwd*",
]


def _redigiere_geheimnisse_in_text(text: str) -> str:
    """Zusaetzliches Netz gegen Geheimnisse in bereits archiviertem Freitext (Sitzungs-
    Transkripte) -- SECRET_MUSTER selbst greift hier nicht, weil das kein Dateiname/-pfad
    ist. Ersetzt erkannte Muster durch [GESCHWAERZT], laesst alles andere unveraendert."""
    for muster in _INHALT_GEHEIM_MUSTER:
        text = muster.sub("[GESCHWAERZT]", text)
    return text


def _redigiere_docker_env(env_liste: list) -> list:
    """Docker-Umgebungsvariablen (Config.Env, Format 'KEY=WERT') sind von SECRET_MUSTER
    (Datei-Muster) nicht erfasst -- eigener Key-Namens-Filter noetig."""
    ergebnis = []
    for eintrag in env_liste or []:
        if not isinstance(eintrag, str) or "=" not in eintrag:
            ergebnis.append(eintrag)
            continue
        key, _, _wert = eintrag.partition("=")
        if any(fnmatch.fnmatch(key.lower(), m) for m in _ENV_KEY_GEHEIM_MUSTER):
            ergebnis.append(f"{key}=[GESCHWAERZT]")
        else:
            ergebnis.append(eintrag)
    return ergebnis


def _pfad_erlaubt(roh_pfad: str) -> Path | None:
    """Gibt den aufgeloesten Pfad zurueck wenn er innerhalb einer erlaubten Wurzel
    ODER in der expliziten ALLOWED_FILES-Liste liegt UND kein Geheimnis-Muster
    trifft, sonst None."""
    try:
        p = Path(roh_pfad).resolve()
    except Exception:
        return None
    if p in ALLOWED_FILES:
        return None if _ist_geheim(p) else p
    if not any(p == root or root in p.parents for root in ALLOWED_ROOTS):
        return None
    if _ist_geheim(p):
        return None
    for teil in p.relative_to(next(r for r in ALLOWED_ROOTS if p == r or r in p.parents)).parts:
        if _ist_geheim(Path(teil)):
            return None
    return p


def _ausgabepfad_erlaubt(roh_pfad: str) -> Path | None:
    """Wie _pfad_erlaubt, aber fuer Zieldateien die beim Aufruf noch nicht existieren
    (z.B. assets.convert_3d_model). 2026-07-23 Redteam-Fund: die alte Pruefung liess
    nur den Elternordner durch _pfad_erlaubt laufen, nie den vollen Zielpfad selbst --
    ein bereits vorhandener Datei-Symlink genau an der Zielposition, der aus einer
    erlaubten Wurzel nach aussen zeigt, waere beim tatsaechlichen Schreiben gefolgt
    worden, ohne je gegen ALLOWED_ROOTS/SECRET_MUSTER geprueft zu werden. Path.resolve()
    funktioniert auch fuer noch nicht existierende Pfade (strict=False ist Standard)
    und loest trotzdem alle bereits vorhandenen Symlink-Bestandteile auf."""
    try:
        p = Path(roh_pfad).resolve()
    except Exception:
        return None
    if not any(p == root or root in p.parents for root in ALLOWED_ROOTS):
        return None
    if _ist_geheim(p):
        return None
    for teil in p.relative_to(next(r for r in ALLOWED_ROOTS if p == r or r in p.parents)).parts:
        if _ist_geheim(Path(teil)):
            return None
    return p


def _sha256_datei(pfad: Path, max_bytes: int = 50_000_000) -> str | None:
    if pfad.stat().st_size > max_bytes:
        return None
    h = hashlib.sha256()
    with open(pfad, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _git_commit_fuer(pfad: Path) -> str | None:
    """Findet das umschliessende Git-Repo und liefert den letzten Commit-Hash der Datei,
    falls vorhanden -- rein lesend (git log -1), kein neuer Prozess-Zustand."""
    try:
        repo = subprocess.run(
            ["git", "-C", str(pfad.parent), "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=5,
        )
        if repo.returncode != 0:
            return None
        res = subprocess.run(
            ["git", "-C", str(pfad.parent), "log", "-1", "--format=%H", "--", str(pfad)],
            capture_output=True, text=True, timeout=5,
        )
        return res.stdout.strip() or None
    except Exception:
        return None


def _source_ref(pfad: Path, start_line: int | None = None, end_line: int | None = None) -> dict:
    try:
        stat = pfad.stat()
        modified_at = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
    except Exception:
        modified_at = None
    return {
        "path": str(pfad),
        "start_line": start_line,
        "end_line": end_line,
        "sha256": _sha256_datei(pfad) if pfad.is_file() else None,
        "modified_at": modified_at,
        "git_commit": _git_commit_fuer(pfad) if pfad.is_file() else None,
        "source_type": "file",
    }


def _ergebnis(ok: bool, data=None, source_refs=None, warnings=None,
              truncated: bool = False, next_cursor=None, error: str | None = None) -> dict:
    """Gemeinsames Ausgabeformat fuer alle Tools (Daniels Vorgabe)."""
    return {
        "ok": ok,
        "data": data,
        "source_refs": source_refs or [],
        "warnings": warnings or [],
        "truncated": truncated,
        "next_cursor": next_cursor,
        "error": error,
    }


# ── Tool-Implementierungen (Phase 1) ────────────────────────────────────────────

def tool_list_roots(_args: dict) -> dict:
    return _ergebnis(True, data={
        "roots": [str(r) for r in ALLOWED_ROOTS],
        "einzeldateien": [str(f) for f in ALLOWED_FILES if f.exists()],
    })


def tool_list_files(args: dict) -> dict:
    roh_pfad = args.get("path", "")
    tiefe = int(args.get("depth", 2))
    glob = args.get("glob", "*")
    limit = min(int(args.get("limit", 200)), 1000)
    cursor = int(args.get("cursor", 0))

    basis = _pfad_erlaubt(roh_pfad)
    if basis is None:
        return _ergebnis(False, error="Pfad nicht erlaubt oder Geheimnis-Muster getroffen")
    if not basis.is_dir():
        return _ergebnis(False, error="Kein Ordner")

    treffer = []
    basis_tiefe = len(basis.parts)
    for dirpath, dirnames, filenames in os.walk(basis):
        aktuelle_tiefe = len(Path(dirpath).parts) - basis_tiefe
        if aktuelle_tiefe >= tiefe:
            dirnames.clear()
            continue
        for name in sorted(filenames):
            p = Path(dirpath) / name
            if not fnmatch.fnmatch(name, glob) or _pfad_erlaubt(str(p)) is None:
                continue
            treffer.append(p)

    gesamt = len(treffer)
    seite = treffer[cursor:cursor + limit]
    data = []
    for p in seite:
        try:
            stat = p.stat()
            data.append({"path": str(p), "size": stat.st_size,
                         "modified_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()})
        except Exception:
            continue
    next_cursor = cursor + limit if cursor + limit < gesamt else None
    return _ergebnis(True, data=data, truncated=next_cursor is not None, next_cursor=next_cursor)


def tool_search_text(args: dict) -> dict:
    query = args.get("query", "")
    roots = args.get("roots") or [str(r) for r in ALLOWED_ROOTS]
    globs = args.get("globs") or ["*"]
    ist_regex = bool(args.get("regex", False))
    context_lines = min(int(args.get("context_lines", 1)), 5)
    limit = min(int(args.get("limit", 50)), 200)
    timeout_seconds = 12.0
    max_scanned_files = 150_000

    if not query:
        return _ergebnis(False, error="query fehlt")

    muster = re.compile(query) if ist_regex else None
    treffer = []
    warnungen = []
    started = time.monotonic()
    scanned_files = scanned_dirs = 0
    stop_reason = None
    skipped_dir_names = {
        ".git", ".cache", "__pycache__", "node_modules", ".venv", "venv",
        "dist-packages", "site-packages", ".mypy_cache", ".pytest_cache",
    }
    for roh_root in roots:
        basis = _pfad_erlaubt(roh_root)
        if basis is None:
            warnungen.append(f"Wurzel nicht erlaubt, uebersprungen: {roh_root}")
            continue
        for dirpath, dirnames, filenames in os.walk(basis, topdown=True, followlinks=False):
            scanned_dirs += 1
            current_dir = Path(dirpath)
            dirnames[:] = [
                d for d in dirnames
                if d not in skipped_dir_names and not (current_dir / d).is_symlink()
            ]
            for name in filenames:
                scanned_files += 1
                if time.monotonic() - started >= timeout_seconds:
                    stop_reason = "timeout"
                    break
                if scanned_files > max_scanned_files:
                    stop_reason = "scan_budget"
                    break
                if len(treffer) >= limit:
                    break
                if not any(fnmatch.fnmatch(name, g) for g in globs):
                    continue
                p = Path(dirpath) / name
                if _pfad_erlaubt(str(p)) is None:
                    continue
                try:
                    if p.stat().st_size > 5_000_000:
                        continue
                    zeilen = p.read_text(encoding="utf-8", errors="ignore").splitlines()
                except Exception:
                    continue
                for i, zeile in enumerate(zeilen):
                    treffer_hier = muster.search(zeile) if ist_regex else (query in zeile)
                    if treffer_hier:
                        start = max(0, i - context_lines)
                        ende = min(len(zeilen), i + context_lines + 1)
                        treffer.append({
                            "path": str(p),
                            "line": i + 1,
                            "match": zeile.strip()[:300],
                            "context": "\n".join(zeilen[start:ende])[:1000],
                        })
                        if len(treffer) >= limit:
                            break
            if stop_reason or len(treffer) >= limit:
                break
        if stop_reason or len(treffer) >= limit:
            break

    if stop_reason:
        warnungen.append(
            f"Suche vorzeitig beendet: {stop_reason}; "
            f"{scanned_files} Dateien/{scanned_dirs} Ordner gescannt"
        )
    refs = [_source_ref(Path(t["path"]), t["line"], t["line"]) for t in treffer[:limit]]
    return _ergebnis(True, data=treffer, source_refs=refs, warnings=warnungen,
                      truncated=bool(stop_reason) or len(treffer) >= limit)


def tool_read_file(args: dict) -> dict:
    roh_pfad = args.get("path", "")
    start_line = args.get("start_line")
    end_line = args.get("end_line")
    p = _pfad_erlaubt(roh_pfad)
    if p is None:
        return _ergebnis(False, error="Pfad nicht erlaubt oder Geheimnis-Muster getroffen")
    if not p.is_file():
        return _ergebnis(False, error="Keine Datei")
    if p.stat().st_size > 5_000_000:
        return _ergebnis(False, error="Datei zu gross fuer read_file (>5MB) -- assets.get_file nutzen")
    try:
        zeilen = p.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception as ex:
        return _ergebnis(False, error=f"Lesefehler: {ex}")
    start = (start_line - 1) if start_line else 0
    ende = end_line if end_line else len(zeilen)
    nummeriert = [f"{i+1}\t{zeile}" for i, zeile in enumerate(zeilen[start:ende], start=start)]
    return _ergebnis(True, data="\n".join(nummeriert),
                      source_refs=[_source_ref(p, start + 1, ende)])


def tool_file_metadata(args: dict) -> dict:
    roh_pfad = args.get("path", "")
    p = _pfad_erlaubt(roh_pfad)
    if p is None:
        return _ergebnis(False, error="Pfad nicht erlaubt oder Geheimnis-Muster getroffen")
    if not p.exists():
        return _ergebnis(False, error="Pfad existiert nicht")
    stat = p.stat()
    daten = {
        "path": str(p),
        "type": "dir" if p.is_dir() else "file",
        "size": stat.st_size,
        "modified_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        "sha256": _sha256_datei(p) if p.is_file() else None,
        "git_commit": _git_commit_fuer(p) if p.is_file() else None,
    }
    return _ergebnis(True, data=daten, source_refs=[_source_ref(p)])


def _git_repo_fuer(roh_pfad: str) -> Path | None:
    p = _pfad_erlaubt(roh_pfad or "")
    if p is None:
        return None
    try:
        res = subprocess.run(["git", "-C", str(p), "rev-parse", "--show-toplevel"],
                              capture_output=True, text=True, timeout=5)
        if res.returncode != 0:
            return None
        repo = Path(res.stdout.strip())
        return repo if _pfad_erlaubt(str(repo)) is not None else None
    except Exception:
        return None


def tool_git_status(args: dict) -> dict:
    repo = _git_repo_fuer(args.get("path", "/root/werkraum"))
    if repo is None:
        return _ergebnis(False, error="Kein erlaubtes Git-Repo an diesem Pfad")
    try:
        res = subprocess.run(["git", "-C", str(repo), "status", "--porcelain=v1"],
                              capture_output=True, text=True, timeout=15)
        zeilen = [z for z in res.stdout.splitlines() if z.strip()]
        return _ergebnis(True, data={"repo": str(repo), "changes": zeilen, "count": len(zeilen)})
    except Exception as ex:
        return _ergebnis(False, error=str(ex))


def tool_git_log(args: dict) -> dict:
    repo = _git_repo_fuer(args.get("path", "/root/werkraum"))
    if repo is None:
        return _ergebnis(False, error="Kein erlaubtes Git-Repo an diesem Pfad")
    limit = min(int(args.get("limit", 20)), 100)
    datei = args.get("file")
    cmd = ["git", "-C", str(repo), "log", f"-{limit}", "--format=%H|%ad|%an|%s", "--date=iso-strict"]
    if datei:
        cmd += ["--", datei]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        commits = []
        for zeile in res.stdout.splitlines():
            teile = zeile.split("|", 3)
            if len(teile) == 4:
                commits.append({"hash": teile[0], "date": teile[1], "author": teile[2], "subject": teile[3]})
        return _ergebnis(True, data=commits)
    except Exception as ex:
        return _ergebnis(False, error=str(ex))


# 2026-07-23: Dienst-Namen bewusst NICHT frei -- nur systemd-Units, deren Name auf
# einen bekannten flextrawurst/werkraum-Dienst passt, damit hier kein beliebiger
# root-Prozess des ganzen VPS abgefragt werden kann. Read-only (status/logs), keine
# start/stop/restart-Aktion in Phase 1.
# 2026-07-23 Phase 3: gleiche Lehre wie beim Redteam-Fund bei git.show/git.diff
# (fuehrender Bindestrich = Flag-Injection-Risiko) vorab hier mit angewandt --
# systemd-Unit-Namen beginnen nie mit "-", also schadet das Verbot nicht.
_DIENST_MUSTER = re.compile(r"^[a-zA-Z0-9_@.+][a-zA-Z0-9_@.+-]*\.service$")


def tool_services_status(args: dict) -> dict:
    name = args.get("name", "")
    if not _DIENST_MUSTER.match(name):
        return _ergebnis(False, error="Ungueltiger Dienstname")
    try:
        res = subprocess.run(["systemctl", "status", name, "--no-pager", "-l"],
                              capture_output=True, text=True, timeout=10)
        return _ergebnis(True, data={"name": name, "output": res.stdout[-4000:], "returncode": res.returncode})
    except Exception as ex:
        return _ergebnis(False, error=str(ex))


def tool_services_logs(args: dict) -> dict:
    name = args.get("name", "")
    if not _DIENST_MUSTER.match(name):
        return _ergebnis(False, error="Ungueltiger Dienstname")
    lines = min(int(args.get("lines", 100)), 1000)
    try:
        res = subprocess.run(["journalctl", "-u", name, "-n", str(lines), "--no-pager", "-o", "short-iso"],
                              capture_output=True, text=True, timeout=10)
        return _ergebnis(True, data={"name": name, "log": res.stdout[-20000:]})
    except Exception as ex:
        return _ergebnis(False, error=str(ex))


def tool_find_recent_files(args: dict) -> dict:
    """Findet zuletzt geaenderte Dateien mit festem Zeit-/Scanbudget."""
    roots = args.get("roots") or [str(r) for r in ALLOWED_ROOTS]
    seit = args.get("since")
    extensions = args.get("extensions")
    limit = min(int(args.get("limit", 10)), 200)
    timeout_seconds = 15.0
    max_scanned_files = 250_000
    seit_ts = None
    if seit:
        try:
            seit_ts = datetime.fromisoformat(seit.replace("Z", "+00:00")).timestamp()
        except Exception:
            return _ergebnis(False, error="since muss ISO-8601 sein, z.B. 2026-07-20T00:00:00Z")

    treffer = []
    started = time.monotonic()
    scanned_files = scanned_dirs = 0
    stop_reason = None
    skipped_dir_names = {
        ".git", ".cache", "__pycache__", "node_modules", ".venv", "venv",
        "dist-packages", "site-packages", ".mypy_cache", ".pytest_cache",
    }
    for roh_root in roots:
        basis = _pfad_erlaubt(roh_root)
        if basis is None:
            continue
        for dirpath, dirnames, filenames in os.walk(basis, topdown=True, followlinks=False):
            scanned_dirs += 1
            current_dir = Path(dirpath)
            dirnames[:] = [
                d for d in dirnames
                if d not in skipped_dir_names and not (current_dir / d).is_symlink()
            ]
            for name in filenames:
                scanned_files += 1
                if time.monotonic() - started >= timeout_seconds:
                    stop_reason = "timeout"
                    break
                if scanned_files > max_scanned_files:
                    stop_reason = "scan_budget"
                    break
                if extensions and not any(name.endswith(e) for e in extensions):
                    continue
                p = Path(dirpath) / name
                if _pfad_erlaubt(str(p)) is None:
                    continue
                try:
                    mtime = p.stat().st_mtime
                except Exception:
                    continue
                if seit_ts and mtime < seit_ts:
                    continue
                treffer.append((mtime, p))
            if stop_reason:
                break
        if stop_reason:
            break

    treffer.sort(key=lambda t: t[0], reverse=True)
    seite = treffer[:limit]
    data = [{"path": str(p), "modified_at": datetime.fromtimestamp(m, tz=timezone.utc).isoformat()}
            for m, p in seite]
    warnings = []
    if stop_reason:
        warnings.append(
            f"Scan vorzeitig beendet: {stop_reason}; "
            f"{scanned_files} Dateien/{scanned_dirs} Ordner gescannt"
        )
    return _ergebnis(
        True, data=data, warnings=warnings,
        truncated=bool(stop_reason) or len(treffer) > limit,
    )


def tool_system_snapshot(_args: dict) -> dict:
    daten = {}
    try:
        daten["load_avg"] = Path("/proc/loadavg").read_text().split()[:3]
    except Exception:
        daten["load_avg"] = None
    try:
        meminfo = Path("/proc/meminfo").read_text()
        werte = {z.split(":")[0]: z.split(":")[1].strip() for z in meminfo.splitlines() if ":" in z}
        daten["mem_total"] = werte.get("MemTotal")
        daten["mem_available"] = werte.get("MemAvailable")
    except Exception:
        pass
    try:
        uptime_s = float(Path("/proc/uptime").read_text().split()[0])
        daten["uptime_stunden"] = round(uptime_s / 3600, 1)
    except Exception:
        pass
    try:
        gesamt, belegt, frei = shutil.disk_usage("/")
        daten["disk_total_gb"] = round(gesamt / 1e9, 1)
        daten["disk_used_gb"] = round(belegt / 1e9, 1)
        daten["disk_free_gb"] = round(frei / 1e9, 1)
    except Exception:
        pass
    try:
        cpu_count = os.cpu_count()
        daten["cpu_count"] = cpu_count
    except Exception:
        pass

    return _ergebnis(True, data=daten)


def tool_assets_get_file(args: dict) -> dict:
    """Liefert Dateiinhalt. mode='preview' (Standard) gibt bei Bildern/kleinen Dateien
    Base64 zurueck, mode='download' bei zu grossen Dateien eine befristete, per Token
    abgesicherte direkte Download-URL statt riesiger Base64-Bloecke im Chat-Kontext."""
    roh_pfad = args.get("path", "")
    mode = args.get("mode", "preview")
    p = _pfad_erlaubt(roh_pfad)
    if p is None:
        return _ergebnis(False, error="Pfad nicht erlaubt oder Geheimnis-Muster getroffen")
    if not p.is_file():
        return _ergebnis(False, error="Keine Datei")

    groesse = p.stat().st_size
    INLINE_LIMIT = 2_000_000  # 2MB -- darueber sprengt Base64 den Chat-Kontext sinnlos
    if groesse <= INLINE_LIMIT:
        inhalt = base64.b64encode(p.read_bytes()).decode("ascii")
        return _ergebnis(True, data={"path": str(p), "size": groesse, "base64": inhalt},
                          source_refs=[_source_ref(p)])

    token = secrets.token_urlsafe(24)
    _DOWNLOAD_TOKENS[token] = {"path": str(p), "expires": time.time() + 600}
    url = f"{PUBLIC_BASE_URL}/download/{token}"
    return _ergebnis(True, data={
        "path": str(p), "size": groesse,
        "download_url": url, "expires_in_s": 600,
        "hinweis": "Datei zu gross fuer Inline-Base64 -- befristete Download-URL (10 Minuten gueltig)",
    }, source_refs=[_source_ref(p)], warnings=["Datei nicht inline geliefert, siehe download_url"])


_DOWNLOAD_TOKENS: dict[str, dict] = {}


def tool_assets_render_3d_preview(args: dict) -> dict:
    """Wiederverwendet blender_pipeline.render_preview_headless() aus der 3D-Pipeline --
    kein Duplikat der Blender-Logik, nur ein neuer, sicherheitsgeprueftr Zugang dazu."""
    roh_pfad = args.get("path", "")
    p = _pfad_erlaubt(roh_pfad)
    if p is None:
        return _ergebnis(False, error="Pfad nicht erlaubt oder Geheimnis-Muster getroffen")
    if not p.is_file():
        return _ergebnis(False, error="Keine Datei")

    sys.path.insert(0, "/root/werkraum/tools/3d_pipeline")
    import blender_pipeline

    ziel = Path("/tmp/vps_mcp_previews") / f"{p.stem}_{secrets.token_hex(4)}.png"
    ziel.parent.mkdir(parents=True, exist_ok=True)
    res = blender_pipeline.render_preview_headless(str(p), str(ziel))
    if res.get("status") == "error" or not ziel.exists():
        return _ergebnis(False, error=res.get("error", "Rendern fehlgeschlagen"))
    inhalt = base64.b64encode(ziel.read_bytes()).decode("ascii")
    return _ergebnis(True, data={"model_path": str(p), "preview_png_base64": inhalt},
                      source_refs=[_source_ref(p)])


# ── Phase 2: restliche Asset-Tools + Provenienz/Git (2026-07-23) ──────────────

_3D_EXT = (".glb", ".gltf", ".obj", ".fbx", ".stl", ".ply")
_BILD_EXT = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")
_AUDIO_EXT = (".wav", ".mp3", ".ogg", ".flac", ".m4a")
_ARCHIV_EXT = (".zip", ".tar", ".gz", ".7z")


def _asset_kategorie(pfad: Path) -> str:
    ext = pfad.suffix.lower()
    if ext in _3D_EXT:
        return "3d_modell"
    if ext in _BILD_EXT:
        return "bild"
    if ext in _AUDIO_EXT:
        return "audio"
    if ext in _ARCHIV_EXT:
        return "archiv"
    return "sonstige"


def tool_assets_list(args: dict) -> dict:
    """Listet Asset-Dateien (3D/Bild/Audio/Archiv) unter einem Pfad, mit Kategorie-Filter."""
    roh_pfad = args.get("path", "")
    kategorie = args.get("kategorie")  # 3d_modell/bild/audio/archiv/sonstige, optional
    limit = min(int(args.get("limit", 100)), 1000)
    cursor = int(args.get("cursor", 0))

    basis = _pfad_erlaubt(roh_pfad)
    if basis is None:
        return _ergebnis(False, error="Pfad nicht erlaubt oder Geheimnis-Muster getroffen")
    if not basis.is_dir():
        return _ergebnis(False, error="Kein Ordner")

    treffer = []
    for dirpath, _, filenames in os.walk(basis):
        for name in filenames:
            p = Path(dirpath) / name
            if _pfad_erlaubt(str(p)) is None:
                continue
            kat = _asset_kategorie(p)
            if kat == "sonstige" and kategorie is None:
                continue
            if kategorie and kat != kategorie:
                continue
            treffer.append(p)

    gesamt = len(treffer)
    seite = treffer[cursor:cursor + limit]
    data = []
    for p in seite:
        try:
            stat = p.stat()
            data.append({"path": str(p), "kategorie": _asset_kategorie(p), "size": stat.st_size})
        except Exception:
            continue
    next_cursor = cursor + limit if cursor + limit < gesamt else None
    return _ergebnis(True, data=data, truncated=next_cursor is not None, next_cursor=next_cursor)


def tool_assets_search(args: dict) -> dict:
    """Sucht Asset-Dateien begrenzt und transparent nach einem Namensmuster."""
    muster = str(args.get("muster", "*"))
    raw_roots = args.get("roots") or [str(r) for r in ALLOWED_ROOTS]
    limit = min(max(int(args.get("limit", 50)), 1), 200)
    timeout_seconds = min(max(float(args.get("timeout_seconds", 20.0)), 0.25), 120.0)
    max_scanned_files = min(
        max(int(args.get("max_scanned_files", 250_000)), 100),
        2_000_000,
    )
    include_dependency_dirs = bool(args.get("include_dependency_dirs", False))
    skipped_dir_names = {
        ".git", ".cache", "__pycache__", "node_modules", ".venv", "venv",
        "dist-packages", "site-packages", ".mypy_cache", ".pytest_cache",
    }

    started = time.monotonic()
    allowed_roots = []
    ignored_roots = []
    for raw_root in raw_roots:
        basis = _pfad_erlaubt(str(raw_root))
        if basis is None or not basis.is_dir():
            ignored_roots.append(str(raw_root))
            continue
        if basis not in allowed_roots:
            allowed_roots.append(basis)

    # Breite Elternwurzeln verdrängen enthaltene Kindwurzeln. Sonst wird etwa
    # /root/werkraum plus jedes seiner Geschwister-Symlinkziele mehrfach gescannt.
    deduplicated_roots = []
    for basis in sorted(allowed_roots, key=lambda item: (len(item.parts), str(item))):
        if any(basis == parent or parent in basis.parents for parent in deduplicated_roots):
            continue
        deduplicated_roots.append(basis)

    matches = []
    scanned_files = 0
    scanned_dirs = 0
    skipped_dirs = 0
    stop_reason = None
    completed_roots = []

    for basis in deduplicated_roots:
        root_complete = True
        for dirpath, dirnames, filenames in os.walk(basis, topdown=True, followlinks=False):
            scanned_dirs += 1
            current_dir = Path(dirpath)
            retained_dirs = []
            for dirname in dirnames:
                child = current_dir / dirname
                if child.is_symlink():
                    skipped_dirs += 1
                    continue
                if not include_dependency_dirs and dirname in skipped_dir_names:
                    skipped_dirs += 1
                    continue
                retained_dirs.append(dirname)
            dirnames[:] = retained_dirs

            for name in filenames:
                scanned_files += 1
                elapsed = time.monotonic() - started
                if elapsed >= timeout_seconds:
                    stop_reason = "timeout"
                    root_complete = False
                    break
                if scanned_files > max_scanned_files:
                    stop_reason = "scan_budget"
                    root_complete = False
                    break

                # Billiger Namensvergleich zuerst. Die vollständige resolve-/Secret-
                # Prüfung ist nur für tatsächliche Treffer nötig.
                if not fnmatch.fnmatch(name.lower(), muster.lower()):
                    continue
                candidate = current_dir / name
                allowed = _pfad_erlaubt(str(candidate))
                if allowed is None:
                    continue
                try:
                    stat = allowed.stat()
                except OSError:
                    continue
                matches.append({
                    "path": str(allowed),
                    "size": stat.st_size,
                    "kategorie": _asset_kategorie(allowed),
                })
                if len(matches) >= limit:
                    stop_reason = "result_limit"
                    root_complete = False
                    break

            if stop_reason is not None:
                break

        if root_complete:
            completed_roots.append(str(basis))
        if stop_reason is not None:
            break

    elapsed_ms = int((time.monotonic() - started) * 1000)
    warnings = []
    if ignored_roots:
        warnings.append(
            f"{len(ignored_roots)} nicht erlaubte oder nicht vorhandene Wurzeln wurden ignoriert."
        )
    if stop_reason == "timeout":
        warnings.append(
            f"Suche nach {elapsed_ms} ms am Zeitbudget beendet; Ergebnis ist ein ehrlicher Teilstand."
        )
    elif stop_reason == "scan_budget":
        warnings.append(
            f"Suche nach {scanned_files} Dateien am Scanbudget beendet; Ergebnis ist ein ehrlicher Teilstand."
        )
    elif stop_reason == "result_limit":
        warnings.append(f"Trefferlimit {limit} erreicht.")

    result = _ergebnis(
        True,
        data=matches,
        warnings=warnings,
        truncated=stop_reason is not None,
    )
    result["scan"] = {
        "pattern": muster,
        "requested_roots": [str(root) for root in raw_roots],
        "effective_roots": [str(root) for root in deduplicated_roots],
        "completed_roots": completed_roots,
        "ignored_roots": ignored_roots,
        "scanned_files": scanned_files,
        "scanned_dirs": scanned_dirs,
        "skipped_dirs": skipped_dirs,
        "elapsed_ms": elapsed_ms,
        "timeout_seconds": timeout_seconds,
        "max_scanned_files": max_scanned_files,
        "include_dependency_dirs": include_dependency_dirs,
        "stop_reason": stop_reason,
        "complete": stop_reason is None,
    }
    return result


def _glb_metadata(pfad: Path) -> dict:
    """Parst den GLB-Header + JSON-Chunk direkt (glTF 2.0 Binary), kein Blender noetig."""
    with open(pfad, "rb") as f:
        magic = f.read(4)
        if magic != b"glTF":
            return {"error": "Keine gueltige GLB-Datei (Magic-Bytes fehlen)"}
        version = int.from_bytes(f.read(4), "little")
        _gesamt_laenge = int.from_bytes(f.read(4), "little")
        chunk_len = int.from_bytes(f.read(4), "little")
        chunk_type = f.read(4)
        if chunk_type != b"JSON":
            return {"error": "Erster Chunk ist kein JSON-Chunk"}
        json_bytes = f.read(chunk_len)
        gltf = json.loads(json_bytes)
    return {
        "format": "glb", "gltf_version": version,
        "generator": gltf.get("asset", {}).get("generator"),
        "meshes": len(gltf.get("meshes", [])),
        "materialien": len(gltf.get("materials", [])),
        "texturen": len(gltf.get("textures", [])),
        "animationen": len(gltf.get("animations", [])),
        "knoten": len(gltf.get("nodes", [])),
    }


def _obj_metadata(pfad: Path) -> dict:
    """Zaehlt Vertices/Faces in einer OBJ-Textdatei (einfaches Zeilenformat, kein Parser noetig)."""
    vertices = faces = normalen = uvs = 0
    with open(pfad, "r", encoding="utf-8", errors="ignore") as f:
        for zeile in f:
            if zeile.startswith("v "):
                vertices += 1
            elif zeile.startswith("f "):
                faces += 1
            elif zeile.startswith("vn "):
                normalen += 1
            elif zeile.startswith("vt "):
                uvs += 1
    return {"format": "obj", "vertices": vertices, "faces": faces,
            "normalen": normalen, "uv_koordinaten": uvs}


def tool_assets_extract_3d_metadata(args: dict) -> dict:
    """Liest 3D-Modell-Metadaten direkt (GLB-JSON-Chunk bzw. OBJ-Zeilen), ohne Blender
    zu starten -- billig, kein neuer Prozess. FBX/STL/PLY: nur Groesse/Format (kein
    einfacher Parser ohne neue Abhaengigkeit)."""
    roh_pfad = args.get("path", "")
    p = _pfad_erlaubt(roh_pfad)
    if p is None:
        return _ergebnis(False, error="Pfad nicht erlaubt oder Geheimnis-Muster getroffen")
    if not p.is_file():
        return _ergebnis(False, error="Keine Datei")
    ext = p.suffix.lower()
    try:
        if ext == ".glb":
            meta = _glb_metadata(p)
        elif ext == ".obj":
            meta = _obj_metadata(p)
        else:
            meta = {"format": ext.lstrip("."), "hinweis": "Detail-Metadaten nur fuer .glb/.obj ohne Blender -- nur Groesse verfuegbar"}
    except Exception as ex:
        return _ergebnis(False, error=f"Metadaten-Extraktion fehlgeschlagen: {ex}")
    meta["size"] = p.stat().st_size
    return _ergebnis(True, data=meta, source_refs=[_source_ref(p)])


def tool_assets_validate_3d_model(args: dict) -> dict:
    """Strukturelle Validierung ohne Blender (billig) -- GLB: Magic+JSON-Chunk parsebar,
    OBJ: mindestens 1 Vertex + 1 Face. Keine vollstaendige Geometrie-/Manifold-Pruefung
    (die macht Blender selbst bei assets.convert_3d_model/render_3d_preview)."""
    roh_pfad = args.get("path", "")
    p = _pfad_erlaubt(roh_pfad)
    if p is None:
        return _ergebnis(False, error="Pfad nicht erlaubt oder Geheimnis-Muster getroffen")
    if not p.is_file():
        return _ergebnis(False, error="Keine Datei")
    ext = p.suffix.lower()
    try:
        if ext == ".glb":
            meta = _glb_metadata(p)
            gueltig = "error" not in meta and meta.get("meshes", 0) > 0
            grund = meta.get("error") or ("keine Meshes" if not gueltig else "ok")
        elif ext == ".obj":
            meta = _obj_metadata(p)
            gueltig = meta["vertices"] > 0 and meta["faces"] > 0
            grund = "ok" if gueltig else "keine Vertices/Faces gefunden"
        else:
            return _ergebnis(True, data={"gueltig": None, "grund": f"Strukturpruefung fuer {ext} nicht implementiert -- nur Groesse gecheckt", "size": p.stat().st_size})
    except Exception as ex:
        return _ergebnis(False, error=f"Validierung fehlgeschlagen: {ex}")
    return _ergebnis(True, data={"gueltig": gueltig, "grund": grund, **meta}, source_refs=[_source_ref(p)])


def tool_assets_convert_3d_model(args: dict) -> dict:
    """Wiederverwendet blender_pipeline.convert_model_headless() -- kein Duplikat."""
    input_pfad = _pfad_erlaubt(args.get("input_path", ""))
    if input_pfad is None:
        return _ergebnis(False, error="input_path nicht erlaubt oder Geheimnis-Muster getroffen")
    output_roh = args.get("output_path", "")
    # Ausgabe muss ebenfalls in einer erlaubten Wurzel landen -- der VOLLE Zielpfad
    # wird geprueft, nicht nur der Elternordner (siehe _ausgabepfad_erlaubt).
    ziel = _ausgabepfad_erlaubt(output_roh) if output_roh else None
    if ziel is None:
        return _ergebnis(False, error="output_path liegt ausserhalb erlaubter Wurzeln oder trifft ein Geheimnis-Muster")
    sys.path.insert(0, "/root/werkraum/tools/3d_pipeline")
    import blender_pipeline
    res = blender_pipeline.convert_model_headless(str(input_pfad), str(ziel))
    if res.get("status") == "error":
        return _ergebnis(False, error=res.get("error", "Konvertierung fehlgeschlagen"))
    return _ergebnis(True, data=res, source_refs=[_source_ref(input_pfad)])


def tool_assets_find_duplicates(args: dict) -> dict:
    """Findet Dateien mit identischem SHA256-Hash unter einem Pfad (begrenzt, keine
    ganze Wurzel ohne Pfad-Eingrenzung -- sonst haesht das ganze VPS)."""
    roh_pfad = args.get("path", "")
    max_dateien = min(int(args.get("max_dateien", 500)), 2000)
    basis = _pfad_erlaubt(roh_pfad)
    if basis is None:
        return _ergebnis(False, error="Pfad nicht erlaubt oder Geheimnis-Muster getroffen")
    if not basis.is_dir():
        return _ergebnis(False, error="Kein Ordner")

    hashes: dict[str, list[str]] = {}
    # 2026-07-23 Redteam-Fund: der Deckel zaehlte bisher nur ERFOLGREICH gehashte
    # Dateien -- ein Ordner mit sehr vielen grossen (>20MB, uebersprungenen)
    # Dateien liess den Walk trotzdem unbegrenzt weiterlaufen und blockierte den
    # (single-threaded) Server beliebig lange. Jetzt zaehlt "durchsucht" jede
    # angeschaute Datei, nicht nur die gehashten.
    durchsucht = 0
    abgebrochen = False
    for dirpath, _, filenames in os.walk(basis):
        for name in filenames:
            if durchsucht >= max_dateien:
                abgebrochen = True
                break
            durchsucht += 1
            p = Path(dirpath) / name
            if _pfad_erlaubt(str(p)) is None:
                continue
            h = _sha256_datei(p, max_bytes=20_000_000)
            if h:
                hashes.setdefault(h, []).append(str(p))
        if abgebrochen:
            break

    duplikate = {h: pfade for h, pfade in hashes.items() if len(pfade) > 1}
    warnungen = [f"Nur die ersten {max_dateien} Dateien durchsucht, evtl. nicht vollstaendig"] if abgebrochen else []
    return _ergebnis(True, data=duplikate, warnings=warnungen, truncated=abgebrochen)


def tool_assets_trace_source(args: dict) -> dict:
    """Findet Erwaehnungen eines Dateinamens/Begriffs in Text-/JSON-Dateien ueber alle
    erlaubten Wurzeln -- Wiederverwendung derselben Logik wie vps.search_text."""
    name_oder_begriff = args.get("name", "")
    if not name_oder_begriff:
        return _ergebnis(False, error="name fehlt")
    return tool_search_text({"query": name_oder_begriff, "limit": int(args.get("limit", 30))})


def tool_assets_read_manifest(args: dict) -> dict:
    """Liest eine JSON-Manifest-Datei und liefert sie geparst zurueck (statt als
    Zeilentext wie vps.read_file) -- fuer Kosmos-Report-JSONs & aehnliche Strukturen."""
    roh_pfad = args.get("path", "")
    p = _pfad_erlaubt(roh_pfad)
    if p is None:
        return _ergebnis(False, error="Pfad nicht erlaubt oder Geheimnis-Muster getroffen")
    if not p.is_file():
        return _ergebnis(False, error="Keine Datei")
    if p.stat().st_size > 5_000_000:
        return _ergebnis(False, error="Datei zu gross (>5MB) fuer read_manifest")
    try:
        inhalt = json.loads(p.read_text(encoding="utf-8"))
    except Exception as ex:
        return _ergebnis(False, error=f"Kein gueltiges JSON: {ex}")
    return _ergebnis(True, data=inhalt, source_refs=[_source_ref(p)])


def tool_assets_list_renders(args: dict) -> dict:
    """Sucht Ordner namens 'render(s)' unter erlaubten Wurzeln und listet ihren Inhalt."""
    roots = args.get("roots") or [str(r) for r in ALLOWED_ROOTS]
    treffer = []
    for roh_root in roots:
        basis = _pfad_erlaubt(roh_root)
        if basis is None:
            continue
        for dirpath, dirnames, _ in os.walk(basis):
            for d in dirnames:
                if d.lower() in ("render", "renders"):
                    render_ordner = Path(dirpath) / d
                    for f in render_ordner.iterdir():
                        if f.is_file() and _pfad_erlaubt(str(f)) is not None:
                            treffer.append({"path": str(f), "size": f.stat().st_size})
    return _ergebnis(True, data=treffer)


def tool_assets_inspect_image(args: dict) -> dict:
    """Bild-Metadaten via Pillow (bereits im System installiert, keine neue Abhaengigkeit)."""
    roh_pfad = args.get("path", "")
    p = _pfad_erlaubt(roh_pfad)
    if p is None:
        return _ergebnis(False, error="Pfad nicht erlaubt oder Geheimnis-Muster getroffen")
    if not p.is_file():
        return _ergebnis(False, error="Keine Datei")
    try:
        from PIL import Image
        with Image.open(p) as img:
            daten = {"format": img.format, "breite": img.width, "hoehe": img.height,
                     "modus": img.mode, "size": p.stat().st_size}
    except Exception as ex:
        return _ergebnis(False, error=f"Kein lesbares Bild: {ex}")
    return _ergebnis(True, data=daten, source_refs=[_source_ref(p)])


def tool_assets_inspect_audio(args: dict) -> dict:
    """Audio-Metadaten fuer WAV via Python-Stdlib-Modul 'wave' (Sample-Rate, Kanaele,
    Dauer). Fuer MP3/OGG/FLAC ohne neue Abhaengigkeit nur Groesse/Format -- ehrlich
    als Grenze benannt, kein erfundener Wert."""
    roh_pfad = args.get("path", "")
    p = _pfad_erlaubt(roh_pfad)
    if p is None:
        return _ergebnis(False, error="Pfad nicht erlaubt oder Geheimnis-Muster getroffen")
    if not p.is_file():
        return _ergebnis(False, error="Keine Datei")
    ext = p.suffix.lower()
    if ext == ".wav":
        try:
            import wave
            with wave.open(str(p), "rb") as w:
                daten = {
                    "format": "wav", "kanaele": w.getnchannels(),
                    "sample_rate": w.getframerate(),
                    "dauer_s": round(w.getnframes() / w.getframerate(), 2) if w.getframerate() else None,
                    "size": p.stat().st_size,
                }
        except Exception as ex:
            return _ergebnis(False, error=f"WAV-Header nicht lesbar: {ex}")
    else:
        daten = {"format": ext.lstrip("."), "size": p.stat().st_size,
                 "hinweis": "Detail-Metadaten (Dauer/Bitrate) nur fuer .wav ohne neue Abhaengigkeit"}
    return _ergebnis(True, data=daten, source_refs=[_source_ref(p)])


def tool_provenance_trace(args: dict) -> dict:
    """Verfolgt die Herkunft eines Pfads: Datei-Metadaten + Git-Historie + Text-
    Erwaehnungen anderswo im System. (Agenten-Sitzungs-Dimension folgt in Phase 3,
    sobald agents.* existiert -- hier noch nicht Teil des Ergebnisses.)"""
    roh_pfad = args.get("path", "")
    p = _pfad_erlaubt(roh_pfad)
    if p is None:
        return _ergebnis(False, error="Pfad nicht erlaubt oder Geheimnis-Muster getroffen")

    ergebnis: dict = {"path": str(p)}
    if p.is_file():
        ergebnis["metadaten"] = tool_file_metadata({"path": str(p)})["data"]
        repo = _git_repo_fuer(str(p.parent))
        if repo:
            log = tool_git_log({"path": str(p.parent), "file": str(p), "limit": 20})
            ergebnis["git_historie"] = log["data"] if log["ok"] else []
        else:
            ergebnis["git_historie"] = []
    erwaehnungen = tool_search_text({"query": p.name, "limit": 15})
    ergebnis["erwaehnt_in"] = [t["path"] for t in erwaehnungen.get("data", []) if t["path"] != str(p)]
    return _ergebnis(True, data=ergebnis, source_refs=[_source_ref(p)] if p.is_file() else [])


# 2026-07-23 Redteam-Fund (kritisch): die alte Regex erlaubte einen fuehrenden
# Bindestrich, dadurch liess sich z.B. ref1="--no-index" als Commit-Referenz
# einschleusen -- "git diff --no-index <pfad1> <pfad2>" verlaesst den Git-Kontext
# komplett und vergleicht zwei BELIEBIGE Dateisystempfade, unabhaengig von
# ALLOWED_ROOTS/SECRET_MUSTER. Git-Referenzen beginnen nie mit "-" (das ist immer
# ein Options-Praefix) -- daher: erstes Zeichen zwingend kein "-", Bindestriche
# INNERHALB des Namens bleiben erlaubt (z.B. Branch "vps-mcp-phase2-arbeit").
_GIT_REF_MUSTER = re.compile(r"^[A-Za-z0-9_./~^][A-Za-z0-9_./~^-]*$")


def _git_ref_gueltig(ref: str) -> bool:
    return bool(_GIT_REF_MUSTER.match(ref))


def _filtere_geheimnisse_aus_git_ausgabe(text: str) -> str:
    """2026-07-23 Redteam-Fund (kritisch): git show/diff zeigen unveraendert den
    Inhalt laengst aus dem Tracking entfernter Geheimnis-Dateien, wenn sie in der
    Commit-Historie je aufgetaucht sind (SECRET_MUSTER wirkt nur auf aktuelle
    Dateizugriffe, nicht auf Git-Historie). Entfernt deshalb sowohl --stat-Zeilen
    als auch komplette Diff-Abschnitte fuer Pfade, die ein Geheimnis-Muster treffen."""
    zeilen = text.split("\n")
    ergebnis = []
    unterdruecken = False
    for zeile in zeilen:
        if zeile.startswith("diff --git "):
            teile = zeile.split(" ")
            pfade = [t[2:] for t in teile[2:4] if t.startswith(("a/", "b/"))]
            geheim = any(_ist_geheim(Path(teil)) for pfad in pfade for teil in Path(pfad).parts)
            if geheim:
                unterdruecken = True
                ergebnis.append("diff --git [GESCHWAERZT -- Pfad trifft Geheimnis-Muster]")
                continue
            unterdruecken = False
        elif re.match(r"^ [^|]+\|", zeile):
            pfad = zeile.split("|", 1)[0].strip()
            if any(_ist_geheim(Path(teil)) for teil in Path(pfad).parts):
                ergebnis.append(" [GESCHWAERZT -- Pfad trifft Geheimnis-Muster]")
                continue
        if unterdruecken:
            continue
        ergebnis.append(zeile)
    return "\n".join(ergebnis)


def tool_git_show(args: dict) -> dict:
    """Zeigt Inhalt/Aenderungen eines konkreten Commits (git show, nur lesend)."""
    repo = _git_repo_fuer(args.get("path", "/root/werkraum"))
    if repo is None:
        return _ergebnis(False, error="Kein erlaubtes Git-Repo an diesem Pfad")
    commit = args.get("commit", "HEAD")
    if not _git_ref_gueltig(commit):
        return _ergebnis(False, error="Ungueltige Commit-Referenz")
    try:
        res = subprocess.run(["git", "-C", str(repo), "show", commit, "--stat", "-p"],
                              capture_output=True, text=True, timeout=15)
        if res.returncode != 0:
            return _ergebnis(False, error=res.stderr[:500])
        ausgabe = _filtere_geheimnisse_aus_git_ausgabe(res.stdout)
        return _ergebnis(True, data=ausgabe[:20000], truncated=len(ausgabe) > 20000)
    except Exception as ex:
        return _ergebnis(False, error=str(ex))


def tool_git_diff(args: dict) -> dict:
    """Vergleicht zwei Commits/Branches/Arbeitsstaende (git diff, nur lesend)."""
    repo = _git_repo_fuer(args.get("path", "/root/werkraum"))
    if repo is None:
        return _ergebnis(False, error="Kein erlaubtes Git-Repo an diesem Pfad")
    ref1 = args.get("ref1", "HEAD")
    ref2 = args.get("ref2", "")
    datei = args.get("file", "")
    for r in (ref1, ref2, datei):
        if r and not _git_ref_gueltig(r):
            return _ergebnis(False, error=f"Ungueltige Referenz oder Pfadangabe: {r}")
    cmd = ["git", "-C", str(repo), "diff", ref1]
    if ref2:
        cmd.append(ref2)
    if datei:
        cmd += ["--", datei]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        ausgabe = _filtere_geheimnisse_aus_git_ausgabe(res.stdout)
        return _ergebnis(True, data=ausgabe[:20000], truncated=len(ausgabe) > 20000)
    except Exception as ex:
        return _ergebnis(False, error=str(ex))


# ── Phase 3: agents.* -- Gemini-/Claude-/Codex-Sitzungen lesen/durchsuchen/vergleichen ──
# Bewusst nur die reinen Sitzungs-Unterordner als Wurzeln (siehe ALLOWED_ROOTS-Kommentar
# oben) -- Geschwister-Dateien mit Zugangsdaten (.claude.json, .codex/auth.json,
# .gemini/oauth_creds.json u.a.) sind dadurch strukturell unerreichbar, nicht nur per
# Namens-Muster blockiert.
AGENT_ROOTS = {
    "claude": Path("/root/.claude/projects/-root"),
    "codex": Path("/root/.codex/sessions"),
    "gemini": Path("/root/.gemini/antigravity-cli/brain"),
}


def _agent_root_erlaubt(provider: str) -> Path | None:
    basis = AGENT_ROOTS.get(provider)
    if basis is None:
        return None
    return _pfad_erlaubt(str(basis))


def tool_agents_list_sessions(args: dict) -> dict:
    """Listet Sitzungen eines Agenten-Providers (claude/codex/gemini), neueste zuerst."""
    provider = args.get("provider", "")
    limit = min(int(args.get("limit", 30)), 200)
    basis = _agent_root_erlaubt(provider)
    if basis is None:
        return _ergebnis(False, error="provider muss claude/codex/gemini sein")

    sitzungen = []
    if provider == "claude":
        for p in basis.glob("*.jsonl"):
            if _pfad_erlaubt(str(p)) is None:
                continue
            try:
                stat = p.stat()
                sitzungen.append({"id": p.stem, "path": str(p), "size": stat.st_size,
                                   "modified_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()})
            except Exception:
                continue
    elif provider == "codex":
        for p in basis.rglob("rollout-*.jsonl"):
            if _pfad_erlaubt(str(p)) is None:
                continue
            try:
                stat = p.stat()
                sitzungen.append({"id": p.stem, "path": str(p), "size": stat.st_size,
                                   "modified_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()})
            except Exception:
                continue
    elif provider == "gemini":
        for ordner in basis.iterdir():
            if not ordner.is_dir() or _pfad_erlaubt(str(ordner)) is None:
                continue
            md_dateien = [f for f in ordner.glob("*.md") if _pfad_erlaubt(str(f)) is not None]
            if not md_dateien:
                continue
            try:
                mtime = max(f.stat().st_mtime for f in md_dateien)
            except Exception:
                continue
            sitzungen.append({"id": ordner.name, "path": str(ordner),
                               "dateien": [f.name for f in md_dateien],
                               "modified_at": datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat()})
    else:
        return _ergebnis(False, error="provider muss claude/codex/gemini sein")

    sitzungen.sort(key=lambda s: s["modified_at"], reverse=True)
    gesamt = len(sitzungen)
    seite = sitzungen[:limit]
    return _ergebnis(True, data=seite, truncated=gesamt > limit)


def _claude_session_lesen(pfad: Path, max_turns: int) -> list:
    turns = []
    with open(pfad, "r", encoding="utf-8", errors="ignore") as f:
        for zeile in f:
            zeile = zeile.strip()
            if not zeile:
                continue
            try:
                d = json.loads(zeile)
            except Exception:
                continue
            if d.get("type") not in ("user", "assistant"):
                continue
            msg = d.get("message", {})
            rolle = msg.get("role", d.get("type"))
            content = msg.get("content")
            text_teile = []
            if isinstance(content, str):
                text_teile.append(content)
            elif isinstance(content, list):
                for block in content:
                    if not isinstance(block, dict):
                        continue
                    if block.get("type") == "text":
                        text_teile.append(block.get("text", ""))
                    elif block.get("type") == "tool_use":
                        text_teile.append(f"[tool_use: {block.get('name')} {json.dumps(block.get('input', {}))[:200]}]")
                    elif block.get("type") == "tool_result":
                        inhalt = block.get("content")
                        text_teile.append(f"[tool_result: {str(inhalt)[:300]}]")
            text = "\n".join(t for t in text_teile if t)
            if not text:
                continue
            turns.append({"role": rolle, "text": _redigiere_geheimnisse_in_text(text[:4000])})
            if len(turns) >= max_turns:
                break
    return turns


def _codex_session_lesen(pfad: Path, max_turns: int) -> list:
    turns = []
    with open(pfad, "r", encoding="utf-8", errors="ignore") as f:
        for zeile in f:
            zeile = zeile.strip()
            if not zeile:
                continue
            try:
                d = json.loads(zeile)
            except Exception:
                continue
            if d.get("type") != "response_item":
                continue
            payload = d.get("payload", {})
            if payload.get("type") != "message":
                continue
            rolle = payload.get("role", "")
            if rolle == "developer":
                continue  # Systeminstruktionen, nicht das eigentliche Gespraech
            text_teile = []
            for block in payload.get("content", []):
                if isinstance(block, dict) and block.get("type") in ("input_text", "output_text"):
                    text_teile.append(block.get("text", ""))
            text = "\n".join(t for t in text_teile if t)
            if not text:
                continue
            turns.append({"role": rolle, "text": _redigiere_geheimnisse_in_text(text[:4000])})
            if len(turns) >= max_turns:
                break
    return turns


def tool_agents_read_session(args: dict) -> dict:
    """Liest eine Sitzung normalisiert (role+text pro Turn). Gemini liest die
    Markdown-Datei(en) direkt (kein Turn-Format), Claude/Codex parsen die
    JSONL-Struktur (Entwickler-/System-Nachrichten bei Codex bewusst ausgelassen)."""
    provider = args.get("provider", "")
    session_id = args.get("session_id", "")
    max_turns = min(int(args.get("max_turns", 50)), 500)
    basis = _agent_root_erlaubt(provider)
    if basis is None:
        return _ergebnis(False, error="provider muss claude/codex/gemini sein")
    if not session_id:
        return _ergebnis(False, error="session_id fehlt")

    if provider == "claude":
        pfad = _pfad_erlaubt(str(basis / f"{session_id}.jsonl"))
        # 2026-07-23 Redteam-Fund: _pfad_erlaubt() prueft nur gegen die GESAMTE
        # ALLOWED_ROOTS-Wurzel (/root/.claude/projects), nicht gegen das engere
        # AGENT_ROOTS["claude"] (/root/.claude/projects/-root). Ein session_id mit
        # "../" koennte sonst in einen Geschwister-Projektordner unter projects/
        # ausbrechen -- aktuell existiert dort nur "-root", aber die Pruefung soll
        # nicht von der aktuellen Abwesenheit weiterer Projekte abhaengen.
        if pfad is None or basis not in pfad.parents or not pfad.is_file():
            return _ergebnis(False, error="Sitzung nicht gefunden")
        turns = _claude_session_lesen(pfad, max_turns)
        return _ergebnis(True, data=turns, source_refs=[_source_ref(pfad)], truncated=len(turns) >= max_turns)

    if provider == "codex":
        treffer = sorted(p for p in basis.rglob(f"*{session_id}*.jsonl") if _pfad_erlaubt(str(p)) is not None)
        if not treffer:
            return _ergebnis(False, error="Sitzung nicht gefunden")
        pfad = treffer[0]
        turns = _codex_session_lesen(pfad, max_turns)
        return _ergebnis(True, data=turns, source_refs=[_source_ref(pfad)], truncated=len(turns) >= max_turns)

    if provider == "gemini":
        ordner = _pfad_erlaubt(str(basis / session_id))
        if ordner is None or not ordner.is_dir():
            return _ergebnis(False, error="Sitzung/Ordner nicht gefunden")
        daten = {}
        for f in sorted(ordner.glob("*.md")):
            if _pfad_erlaubt(str(f)) is None:
                continue
            try:
                daten[f.name] = _redigiere_geheimnisse_in_text(f.read_text(encoding="utf-8", errors="ignore")[:20000])
            except Exception:
                continue
        return _ergebnis(True, data=daten, source_refs=[_source_ref(ordner)])

    return _ergebnis(False, error="provider muss claude/codex/gemini sein")


def tool_agents_search_sessions(args: dict) -> dict:
    """Durchsucht rohen Sitzungs-Zeileninhalt (nicht turn-geparst) ueber einen oder
    alle Provider -- fuer schnelles Auffinden, danach agents.read_session fuer die
    volle, normalisierte Sitzung nutzen."""
    query = args.get("query", "")
    provider = args.get("provider")  # optional: claude/codex/gemini, sonst alle
    limit = min(int(args.get("limit", 30)), 200)
    if not query:
        return _ergebnis(False, error="query fehlt")
    if provider and provider not in AGENT_ROOTS:
        return _ergebnis(False, error="provider muss claude/codex/gemini sein")

    # 2026-07-23 Redteam-Fund: kein Gesamt-Zeit-Deckel ueber den kompletten Scan --
    # bei seltener/fehlender query wurden alle Sitzungsdateien aller Provider komplett
    # eingelesen (~500MB, mehrere Sekunden), waehrend derer der (single-threaded)
    # Server fuer jeden Client blockiert war. Feste Zeit-Obergrenze erzwingt Abbruch.
    ZEIT_DECKEL_SEKUNDEN = 8.0
    start_zeit = time.time()
    zeit_abgebrochen = False

    provider_liste = [provider] if provider else list(AGENT_ROOTS.keys())
    treffer = []
    for prov in provider_liste:
        basis = _agent_root_erlaubt(prov)
        if basis is None:
            continue
        muster = "*.md" if prov == "gemini" else "*.jsonl"
        for p in basis.rglob(muster):
            if len(treffer) >= limit:
                break
            if time.time() - start_zeit > ZEIT_DECKEL_SEKUNDEN:
                zeit_abgebrochen = True
                break
            if _pfad_erlaubt(str(p)) is None:
                continue
            try:
                if p.stat().st_size > 20_000_000:
                    continue
                zeilen = p.read_text(encoding="utf-8", errors="ignore").splitlines()
            except Exception:
                continue
            for i, zeile in enumerate(zeilen):
                if query.lower() in zeile.lower():
                    treffer.append({"provider": prov, "path": str(p), "line": i + 1,
                                     "match": _redigiere_geheimnisse_in_text(zeile.strip()[:300])})
                    if len(treffer) >= limit:
                        break
        if len(treffer) >= limit or zeit_abgebrochen:
            break
    warnungen = ["Zeit-Deckel erreicht, Suche vorzeitig abgebrochen -- evtl. nicht vollstaendig"] if zeit_abgebrochen else []
    return _ergebnis(True, data=treffer, warnings=warnungen, truncated=len(treffer) >= limit or zeit_abgebrochen)


def tool_agents_compare_sessions(args: dict) -> dict:
    """Liefert zwei Sitzungen (gleicher oder verschiedener Provider) kompakt
    nebeneinander -- Anfang der jeweiligen Sitzung, damit der eigentliche Vergleich
    (was ist gleich/unterschiedlich) dem aufrufenden Modell ueberlassen bleibt,
    statt hier eine eigene, unsichere Vergleichs-Heuristik zu erfinden."""
    a_provider = args.get("provider_a", "")
    a_id = args.get("session_id_a", "")
    b_provider = args.get("provider_b", a_provider)
    b_id = args.get("session_id_b", "")
    kurz = min(int(args.get("kurzform_turns", 10)), 50)

    ergebnis_a = tool_agents_read_session({"provider": a_provider, "session_id": a_id, "max_turns": kurz})
    if not ergebnis_a["ok"]:
        return _ergebnis(False, error=f"Sitzung A: {ergebnis_a['error']}")
    ergebnis_b = tool_agents_read_session({"provider": b_provider, "session_id": b_id, "max_turns": kurz})
    if not ergebnis_b["ok"]:
        return _ergebnis(False, error=f"Sitzung B: {ergebnis_b['error']}")
    return _ergebnis(True, data={
        "a": {"provider": a_provider, "session_id": a_id, "turns": ergebnis_a["data"]},
        "b": {"provider": b_provider, "session_id": b_id, "turns": ergebnis_b["data"]},
    })


# ── Phase 3: containers.* / network.* -- nur lesend, kein restart/stop/exec ─────
# Gleiche Lehre wie bei _DIENST_MUSTER/_GIT_REF_MUSTER: Container-Namen duerfen nicht
# mit "-" beginnen, sonst koennten sie als docker-Flag statt als Positional-Argument
# interpretiert werden.
_CONTAINER_NAME_MUSTER = re.compile(r"^[a-zA-Z0-9_][a-zA-Z0-9_.-]*$")


def tool_containers_list(_args: dict) -> dict:
    try:
        res = subprocess.run(
            ["docker", "ps", "-a", "--format", "{{.Names}}|{{.Image}}|{{.Status}}|{{.Ports}}"],
            capture_output=True, text=True, timeout=10,
        )
        if res.returncode != 0:
            return _ergebnis(False, error=res.stderr[:500] or "docker ps fehlgeschlagen")
        container = []
        for zeile in res.stdout.splitlines():
            teile = zeile.split("|", 3)
            if len(teile) == 4:
                container.append({"name": teile[0], "image": teile[1], "status": teile[2], "ports": teile[3]})
        return _ergebnis(True, data=container)
    except Exception as ex:
        return _ergebnis(False, error=str(ex))


def tool_containers_logs(args: dict) -> dict:
    """Nur lesend (docker logs) -- kein restart/stop/exec/rm moeglich."""
    name = args.get("name", "")
    lines = min(int(args.get("lines", 200)), 2000)
    if not _CONTAINER_NAME_MUSTER.match(name):
        return _ergebnis(False, error="Ungueltiger Container-Name")
    try:
        res = subprocess.run(["docker", "logs", "--tail", str(lines), name],
                              capture_output=True, text=True, timeout=10)
        log = _redigiere_geheimnisse_in_text((res.stdout + res.stderr)[-20000:])
        return _ergebnis(True, data={"name": name, "log": log})
    except Exception as ex:
        return _ergebnis(False, error=str(ex))


def tool_containers_inspect(args: dict) -> dict:
    """2026-07-23 Redteam-Fund (kritisch): docker inspect liefert Config.Env im
    Klartext -- SECRET_MUSTER (Datei-Muster) greift hier nicht, echte Passwoerter
    liegen in Umgebungsvariablen mehrerer laufender Container im Klartext vor.
    Env-Werte mit verdaechtigem Key-Namen werden vor der Rueckgabe geschwaerzt."""
    name = args.get("name", "")
    if not _CONTAINER_NAME_MUSTER.match(name):
        return _ergebnis(False, error="Ungueltiger Container-Name")
    try:
        res = subprocess.run(["docker", "inspect", name], capture_output=True, text=True, timeout=10)
        if res.returncode != 0:
            return _ergebnis(False, error=res.stderr[:500])
        daten = json.loads(res.stdout)
        eintrag = daten[0] if daten else {}
        config = eintrag.get("Config")
        if isinstance(config, dict) and "Env" in config:
            config["Env"] = _redigiere_docker_env(config.get("Env"))
        return _ergebnis(True, data=eintrag)
    except Exception as ex:
        return _ergebnis(False, error=str(ex))


def tool_network_status(_args: dict) -> dict:
    """Nur lesend: aktuell lauschende TCP-Ports (ss -tlnp) -- kein Eingriff moeglich,
    kein Kill/Close einer Verbindung."""
    try:
        res = subprocess.run(["ss", "-tlnp"], capture_output=True, text=True, timeout=10)
        zeilen = [z for z in res.stdout.splitlines() if z.strip()]
        return _ergebnis(True, data=zeilen)
    except Exception as ex:
        return _ergebnis(False, error=str(ex))


# ── Phase 4: database.* -- NUR LESEND (SELECT/WITH/EXPLAIN), webapps.*, tests.* ──
# 2026-07-23: Verbindungsdaten liegen in /root/werkraum/.agent/flextrawurst-db.env
# (FLEXTRAWURST_DB_URI, geladen vom laufenden welt-api.service via systemd-Drop-in) --
# dieselbe Datei die SECRET_MUSTER (*.env) ohnehin schon fuer Datei-Zugriff blockiert.
# Wird HIER bewusst separat/gezielt gelesen (nicht ueber vps.read_file), weil die
# DB-Verbindung selbst der Sinn dieser Tool-Gruppe ist -- das Passwort verlaesst
# den Prozess nie in Richtung Client, nur die Verbindung wird damit aufgebaut.
_DB_ENV_PFAD = Path("/root/werkraum/.agent/flextrawurst-db.env")
_SQL_LESE_MUSTER = re.compile(r"^(SELECT|WITH)\b", re.IGNORECASE)
# 2026-07-23 Redteam-Fund (mittel): Postgres fuehrt bei reinem "EXPLAIN DELETE/UPDATE/
# INSERT ..." (ohne ANALYZE) die Anweisung nur nicht aus -- weder die alte
# "beginnt mit SELECT/WITH/EXPLAIN"-Regex noch die read-only-DB-Session (die nur
# echte Ausfuehrung blockt, nicht reines Planen) haetten das erkannt. Live
# reproduziert: "EXPLAIN DELETE FROM <echte Tabelle>" lieferte einen echten Query-
# Plan zurueck. Deshalb: nach einem optionalen EXPLAIN-Praefix (neue Klammer-Syntax
# ODER alte ANALYZE/VERBOSE-Modifier) MUSS zwingend SELECT/WITH folgen.
_SQL_GEFAEHRLICHE_FUNKTIONEN = re.compile(
    r"\b(pg_read_file|pg_read_binary_file|pg_ls_dir|pg_ls_logdir|pg_ls_waldir|"
    r"pg_stat_file|lo_import|lo_export|dblink|dblink_exec|adminpack)\b",
    re.IGNORECASE,
)


def _sql_ist_erlaubt(sql: str) -> bool:
    kern = sql.strip()
    if _SQL_LESE_MUSTER.match(kern):
        return True
    m = re.match(r"^EXPLAIN\b", kern, re.IGNORECASE)
    if not m:
        return False
    rest = kern[m.end():].strip()
    m_klammer = re.match(r"^\([^)]*\)", rest)  # neue Syntax: EXPLAIN (ANALYZE, ...) ...
    if m_klammer:
        rest = rest[m_klammer.end():].strip()
    else:  # alte Syntax: EXPLAIN [ANALYZE] [VERBOSE] ...
        while True:
            m_mod = re.match(r"^(ANALYZE|VERBOSE)\b", rest, re.IGNORECASE)
            if not m_mod:
                break
            rest = rest[m_mod.end():].strip()
    return bool(_SQL_LESE_MUSTER.match(rest))


def _db_uri() -> str | None:
    if _DB_ENV_PFAD.is_file():
        for zeile in _DB_ENV_PFAD.read_text().splitlines():
            zeile = zeile.strip()
            if zeile.startswith("FLEXTRAWURST_DB_URI="):
                return zeile.split("=", 1)[1].strip().strip('"').strip("'")
    return os.environ.get("FLEXTRAWURST_DB_URI")


def _db_verbindung():
    uri = _db_uri()
    if not uri:
        return None
    conn = psycopg2.connect(uri, connect_timeout=5)
    # Zusaetzlich zur SQL-Text-Pruefung: die DB-Session selbst wird read-only
    # geschaltet -- Postgres lehnt JEDEN Schreibversuch ab, unabhaengig davon ob
    # die Regex-Pruefung des SQL-Textes umgangen werden koennte.
    conn.set_session(readonly=True, autocommit=True)
    return conn


def tool_database_query_readonly(args: dict) -> dict:
    """Nur SELECT/WITH(/EXPLAIN davor) erlaubt -- Text-Pruefung, Denylist gefaehrlicher
    Funktionen, UND read-only DB-Session (drei unabhaengige Verteidigungsebenen)."""
    sql = args.get("sql", "")
    try:
        limit = min(int(args.get("limit", 200)), 1000)
    except (TypeError, ValueError):
        return _ergebnis(False, error="limit muss eine Zahl sein")
    if not sql.strip():
        return _ergebnis(False, error="sql fehlt")
    if not _sql_ist_erlaubt(sql):
        return _ergebnis(False, error="Nur SELECT/WITH (optional mit EXPLAIN davor) erlaubt")
    if _SQL_GEFAEHRLICHE_FUNKTIONEN.search(sql):
        return _ergebnis(False, error="Funktion nicht erlaubt (Datei-/externer Zugriff)")
    kern = sql.strip()
    if kern.endswith(";"):
        kern = kern[:-1]
    if ";" in kern:
        return _ergebnis(False, error="Mehrere Statements (;) nicht erlaubt")

    conn = None
    try:
        conn = _db_verbindung()
        if conn is None:
            return _ergebnis(False, error="Keine DB-Verbindungsdaten gefunden")
        with conn.cursor() as cur:
            cur.execute("SET statement_timeout = '10s'")
            cur.execute(kern)
            if cur.description is None:
                return _ergebnis(True, data={"columns": [], "rows": []})
            spalten = [d.name for d in cur.description]
            zeilen = cur.fetchmany(limit)
            return _ergebnis(True, data={"columns": spalten, "rows": [[str(w) for w in z] for z in zeilen]},
                              truncated=len(zeilen) >= limit)
    except Exception as ex:
        return _ergebnis(False, error=str(ex))
    finally:
        if conn:
            conn.close()


def tool_database_list_tables(args: dict) -> dict:
    schema = args.get("schema", "public")
    conn = None
    try:
        conn = _db_verbindung()
        if conn is None:
            return _ergebnis(False, error="Keine DB-Verbindungsdaten gefunden")
        with conn.cursor() as cur:
            cur.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = %s ORDER BY table_name",
                (schema,),
            )
            tabellen = [r[0] for r in cur.fetchall()]
        return _ergebnis(True, data=tabellen)
    except Exception as ex:
        return _ergebnis(False, error=str(ex))
    finally:
        if conn:
            conn.close()


def tool_database_describe_table(args: dict) -> dict:
    schema = args.get("schema", "public")
    table = args.get("table", "")
    if not table:
        return _ergebnis(False, error="table fehlt")
    conn = None
    try:
        conn = _db_verbindung()
        if conn is None:
            return _ergebnis(False, error="Keine DB-Verbindungsdaten gefunden")
        with conn.cursor() as cur:
            cur.execute(
                "SELECT column_name, data_type, is_nullable FROM information_schema.columns "
                "WHERE table_schema = %s AND table_name = %s ORDER BY ordinal_position",
                (schema, table),
            )
            spalten = [{"name": r[0], "type": r[1], "nullable": r[2] == "YES"} for r in cur.fetchall()]
        if not spalten:
            return _ergebnis(False, error="Tabelle nicht gefunden oder keine Spalten")
        return _ergebnis(True, data=spalten)
    except Exception as ex:
        return _ergebnis(False, error=str(ex))
    finally:
        if conn:
            conn.close()


# 2026-07-23: feste Allowlist bekannter, lokal laufender Web-Apps -- KEIN beliebiges
# "url"-Argument vom Client, sonst waere das ein SSRF-Vektor (interne Dienste/
# Cloud-Metadaten-Endpunkte ueber den VPS als Proxy erreichbar).
WEBAPP_ZIELE = {
    "welt-api": "http://127.0.0.1:8030/health",
    "flextrawurst-gateway": "http://127.0.0.1:8010/",
    "werkraum-api": "http://127.0.0.1:8001/",
    "flextrawurst-3d-mcp": "http://127.0.0.1:8090/",
    "vps-mcp": "http://127.0.0.1:8091/",
    "ftw-pro": "http://127.0.0.1:3010/",
    "flextrawurst-surface": "http://127.0.0.1:8787/",
}


def tool_webapps_list(_args: dict) -> dict:
    return _ergebnis(True, data=list(WEBAPP_ZIELE.keys()))


def tool_webapps_health(args: dict) -> dict:
    name = args.get("name", "")
    if name not in WEBAPP_ZIELE:
        return _ergebnis(False, error=f"Unbekannte Webapp -- verfuegbar: {', '.join(WEBAPP_ZIELE.keys())}")
    url = WEBAPP_ZIELE[name]
    start = time.time()
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            dauer_ms = round((time.time() - start) * 1000, 1)
            return _ergebnis(True, data={"name": name, "url": url, "status": resp.status, "dauer_ms": dauer_ms})
    except urllib.error.HTTPError as ex:
        dauer_ms = round((time.time() - start) * 1000, 1)
        return _ergebnis(True, data={"name": name, "url": url, "status": ex.code, "dauer_ms": dauer_ms})
    except Exception as ex:
        return _ergebnis(False, error=str(ex))


# 2026-07-23: nur das eigenstaendige flextrawurst-Repo (/root/flextrawurst, NICHT
# betroffen von der unaufgeloesten externen Rebase in /root/werkraum) -- Testdatei-
# Namen werden gegen den tatsaechlichen Verzeichnisinhalt geprueft, kein Pfad-
# Bestandteil/".." erlaubt, damit ueber "file" keine beliebige Kommandozeile entsteht.
_FLEXTRAWURST_TESTS_DIR = Path("/root/flextrawurst/tests")


def tool_tests_list(_args: dict) -> dict:
    if not _FLEXTRAWURST_TESTS_DIR.is_dir():
        return _ergebnis(False, error="Test-Verzeichnis nicht gefunden")
    dateien = sorted(p.name for p in _FLEXTRAWURST_TESTS_DIR.glob("*.test.ts"))
    return _ergebnis(True, data=dateien)


def tool_tests_run(args: dict) -> dict:
    datei = args.get("file", "")
    if not datei or "/" in datei or ".." in datei or not datei.endswith(".test.ts"):
        return _ergebnis(False, error="Ungueltiger Testdatei-Name")
    ziel = _FLEXTRAWURST_TESTS_DIR / datei
    if not ziel.is_file():
        return _ergebnis(False, error="Testdatei nicht gefunden")
    try:
        res = subprocess.run(["npx", "tsx", "--test", str(ziel)],
                              capture_output=True, text=True, timeout=120, cwd=str(_FLEXTRAWURST_TESTS_DIR.parent))
        ausgabe = (res.stdout + res.stderr)[-20000:]
        return _ergebnis(res.returncode == 0, data={"file": datei, "returncode": res.returncode, "output": ausgabe})
    except subprocess.TimeoutExpired:
        return _ergebnis(False, error="Test-Timeout (120s) ueberschritten")
    except Exception as ex:
        return _ergebnis(False, error=str(ex))


def tool_tests_run_all(_args: dict) -> dict:
    try:
        res = subprocess.run(["npm", "test"], capture_output=True, text=True,
                              timeout=300, cwd=str(_FLEXTRAWURST_TESTS_DIR.parent))
        ausgabe = (res.stdout + res.stderr)[-20000:]
        return _ergebnis(res.returncode == 0, data={"returncode": res.returncode, "output": ausgabe})
    except subprocess.TimeoutExpired:
        return _ergebnis(False, error="Test-Timeout (300s) ueberschritten")
    except Exception as ex:
        return _ergebnis(False, error=str(ex))


# ── Phase 5: zensi.* -- NUR LESEND, ueber Zensis EIGENE REST-API (Port 8043, nur
# 127.0.0.1) proxied -- bewusst KEIN direkter, EIGENSTAENDIGER Dateisystem-Pfad
# fuer Zensi-Inhalte in diesem Block. Grund: dort liegen u.a. echte private
# TLS/SSH-Schluessel unter wesensprofile/GENI/{klon,sandbox}/ssl_key.pem (und in
# den gespiegelten obsidian_vault-Kopien) sowie ein hartcodierter DB-Connection-
# String in server.py.
# 2026-07-23 Redteam-Fund (kritisch): der urspruengliche Kommentar hier behauptete
# "/root/zensi ist nie in ALLOWED_ROOTS aufgenommen" -- das war schlicht falsch,
# /root/zensi steht seit Phase 1 in ALLOWED_ROOTS (Daniels eigene Liste). server.py
# war dadurch ueber die ganz normalen vps.read_file/assets.get_file-Tools live
# lesbar, SECRET_MUSTER greift nicht (Dateiname "server.py" ist nicht verdaechtig).
# Sofortmassnahme: server.py exakt gesperrt (_EXAKTE_GEHEIME_PFADE, siehe dort) --
# das ist eine eng geschnittene Notloesung, KEINE endgueltige Antwort auf die
# Architektur-Frage ob /root/zensi ueberhaupt als volle Wurzel offen sein soll.
# Offen fuer Daniel (Systemdoku 38, Abschnitt 18): (a) ALLOWED_ROOTS fuer /root/zensi
# enger fassen, (b) server.py in Zensi selbst auf Env-Var statt Hartcodierung
# umstellen, oder (c) beides. Der hier gebaute zensi.*-Proxy bleibt trotzdem
# sinnvoll, weil er nur kuratierte, strukturierte Endpunkte statt freiem
# Dateizugriff anbietet -- Wesen/Aufgaben/Sessions/Physiologie ueber Zensis
# eigene API, nicht als Ersatz fuer die ALLOWED_ROOTS-Frage.
_ZENSI_BASIS_URL = "http://127.0.0.1:8043"
_ZENSI_ENDPUNKTE = {
    "list_wesen": ("/zensi/api/wesensliste", []),
    "list_tasks": ("/zensi/api/aufgaben/liste", []),
    "list_versions": ("/zensi/api/versionen/liste", ["wesen_id"]),
    "list_sessions": ("/zensi/api/sessions/liste", []),
    "get_session": ("/zensi/api/sessions/get", ["session_id"]),
    "physiology_status": ("/api/physiologie/status", []),
    # 2026-07-23 (Daniel: "muss alles genau so machbar gebaut werden ende ohne
    # diskussion") -- restliche lesende Endpunkte aus Zensis do_GET ergaenzt,
    # damit die volle API abgedeckt ist, nicht nur die urspruengliche
    # Phase-5-Auswahl.
    "vault_tree": ("/zensi/api/vault/tree", []),
    "vault_file": ("/zensi/api/vault/file", ["pfad"]),
    "vault_search": ("/zensi/api/vault/search", ["q"]),
    "diff_vergleiche": ("/zensi/api/diff/vergleiche", ["wesen_id", "quelle", "ziel"]),
    "diff_historie": ("/zensi/api/diff/historie", ["wesen_id"]),
    "memory_get": ("/zensi/api/memory", ["wesen_id", "modus"]),
    "container_get": ("/zensi/api/container", ["wesen_id", "modus"]),
    "aufgabe_session_get": ("/zensi/api/aufgaben/session", ["session_id"]),
    "schichten_get": ("/zensi/api/schichten", ["wesen_id", "modus"]),
    "symposium_liste": ("/zensi/api/symposium/liste", []),
    "traum_liste": ("/zensi/api/traum/liste", ["wesen_id"]),
}


# 2026-07-23 Redteam-Fund (gering, Phase 5): quelle_pfad/pfad-Felder in Zensis
# eigenen Antworten liefern absolute Server-Dateisystempfade (z.B.
# "/root/zensi/wesensprofile/Resonanzknoten") -- kein Geheimnis-Leak per se, aber
# unnoetige Preisgabe der internen Serverstruktur. Wird vor der Rueckgabe entfernt.
_ZENSI_PFAD_FELDER = {"quelle_pfad", "pfad"}
_ZENSI_ID_MAX_LAENGE = 200


def _zensi_pfadfelder_entfernen(objekt):
    if isinstance(objekt, list):
        return [_zensi_pfadfelder_entfernen(e) for e in objekt]
    if isinstance(objekt, dict):
        return {k: _zensi_pfadfelder_entfernen(v) for k, v in objekt.items() if k not in _ZENSI_PFAD_FELDER}
    return objekt


def _zensi_geheimnisse_redigieren(objekt):
    """Wendet den bereits fuer agents.*/containers.* genutzten Content-Redaction-Filter
    rekursiv auf alle Strings einer JSON-Struktur an -- Zensi-Sessions/Aufgaben
    koennen freien, von Wesen-Klonen erzeugten Text enthalten."""
    if isinstance(objekt, str):
        return _redigiere_geheimnisse_in_text(objekt)
    if isinstance(objekt, list):
        return [_zensi_geheimnisse_redigieren(e) for e in objekt]
    if isinstance(objekt, dict):
        return {k: _zensi_geheimnisse_redigieren(v) for k, v in objekt.items()}
    return objekt


def _zensi_get(endpunkt_key: str, args: dict) -> dict:
    eintrag = _ZENSI_ENDPUNKTE.get(endpunkt_key)
    if eintrag is None:
        return _ergebnis(False, error="Unbekannter Zensi-Endpunkt")
    pfad, erlaubte_params = eintrag
    for p in erlaubte_params:
        wert = args.get(p)
        if wert and len(str(wert)) > _ZENSI_ID_MAX_LAENGE:
            return _ergebnis(False, error=f"{p} zu lang (max {_ZENSI_ID_MAX_LAENGE} Zeichen)")
    query = {p: args[p] for p in erlaubte_params if args.get(p)}
    url = f"{_ZENSI_BASIS_URL}{pfad}"
    if query:
        url += "?" + urllib.parse.urlencode(query)
    try:
        with urllib.request.urlopen(url, timeout=8) as resp:
            daten = json.loads(resp.read().decode("utf-8", errors="ignore"))
        daten = _zensi_pfadfelder_entfernen(daten)
        return _ergebnis(True, data=_zensi_geheimnisse_redigieren(daten))
    except urllib.error.HTTPError as ex:
        return _ergebnis(False, error=f"Zensi-API-Fehler {ex.code}")
    except Exception as ex:
        return _ergebnis(False, error=str(ex))


def tool_zensi_list_wesen(_args: dict) -> dict:
    return _zensi_get("list_wesen", {})


def tool_zensi_list_tasks(_args: dict) -> dict:
    return _zensi_get("list_tasks", {})


def tool_zensi_list_versions(args: dict) -> dict:
    if not args.get("wesen_id"):
        return _ergebnis(False, error="wesen_id fehlt")
    return _zensi_get("list_versions", args)


def tool_zensi_list_sessions(_args: dict) -> dict:
    """2026-07-23 Redteam-Fund (gering): Zensis Liste liefert pro Session bereits das
    volle messages-Array mit, unbegrenzt und ohne Paginierung -- anders als praktisch
    alle anderen Listen-Tools in dieser Datei. Auf Metadaten reduziert; volle
    Nachrichten gezielt ueber zensi.get_session."""
    ergebnis = _zensi_get("list_sessions", {})
    if ergebnis["ok"] and isinstance(ergebnis["data"], dict):
        sessions = ergebnis["data"].get("sessions")
        if isinstance(sessions, list):
            ergebnis["data"]["sessions"] = [
                {k: v for k, v in s.items() if k != "messages"} if isinstance(s, dict) else s
                for s in sessions
            ]
    return ergebnis


def tool_zensi_get_session(args: dict) -> dict:
    if not args.get("session_id"):
        return _ergebnis(False, error="session_id fehlt")
    return _zensi_get("get_session", args)


def tool_zensi_physiology_status(_args: dict) -> dict:
    return _zensi_get("physiology_status", {})


# ── Zensi schreibende Aktionen -- ergaenzt die Phase-5-Leseproxys um POST-
# Endpunkte, ueber die eigene REST-API von Zensi (127.0.0.1:8043), gleiches
# Prinzip: fest verdrahtete Pfade + Parameter-Allowlist pro Aktion statt freiem
# Body-Durchreichen, gleicher Content-Redaction-Filter auf jede Antwort.
# 2026-07-23, Daniel: "nur noch echte zensi schreib phase vergiss redteam" --
# bewusst kein separater Redteam-Pass fuer diesen Block, nur Basis-Funktionstest.
#
# Erste Runde hatte bewusst eine Teilmenge (Session-Verwaltung, Aufgaben,
# Sandbox pause/snapshot, Diff-Kommentar, Feedback) und die identitaetsnahen
# Endpunkte (hard_delete, sandbox/uebernehmen, mutationskammer/verschmelze,
# memory/container/schichten/versionen/vault/spiegeln/symposium/traum/chrono/
# biopsie/import-*) ausgelassen -- mit Begruendung im Chat, nicht nur im Code.
# Daniels Antwort darauf, woertlich: "es war [uebergriffig] von dir es still
# wegzulassen und nicht zu bauen ohne deine ehrliche [Bedenken] auszuformulieren
# ... also muss alles genau so machbar gebaut werden ende ohne diskussion" --
# der Punkt war nicht die Sorge selbst (die durfte/sollte ich aeussern), sondern
# dass ich schon entschieden UND gebaut hatte, bevor ich sie geaeussert habe.
# Jetzt vollstaendig: alle verbleibenden POST-Endpunkte aus Zensis do_POST
# ergaenzt, gleiche Allowlist-Disziplin wie ueberall sonst in dieser Datei.
_ZENSI_SCHREIB_ENDPUNKTE = {
    "session_create": ("/zensi/api/sessions/create", ["wesen_id", "modus", "version_geist", "title"]),
    "session_append": ("/zensi/api/sessions/append", ["session_id", "messages", "wesen_id", "modus", "version_geist"]),
    "session_soft_delete": ("/zensi/api/sessions/soft_delete", ["session_id"]),
    "session_restore": ("/zensi/api/sessions/restore", ["session_id"]),
    "session_hard_delete": ("/zensi/api/sessions/hard_delete", ["session_id"]),
    "aufgabe_start": ("/zensi/api/aufgaben/start", ["wesen_id", "modus", "typ", "impuls", "max_ticks"]),
    "aufgabe_tick": ("/zensi/api/aufgaben/tick", ["session_id"]),
    "aufgabe_stop": ("/zensi/api/aufgaben/stop", ["session_id"]),
    "sandbox_pause": ("/zensi/api/sandbox/pause", ["wesen_id"]),
    "sandbox_snapshot": ("/zensi/api/sandbox/snapshot", ["wesen_id"]),
    "sandbox_uebernehmen": ("/zensi/api/sandbox/uebernehmen", ["wesen_id"]),
    "diff_kommentar": ("/zensi/api/diff/kommentar", ["wesen_id", "quelle", "ziel", "kommentar", "snapshots"]),
    "feedback": ("/zensi/api/feedback", ["wesen_id", "session_id", "bewertung", "kommentar"]),
    "vault_save": ("/zensi/api/vault/save", ["pfad", "inhalt"]),
    "memory_save": ("/zensi/api/memory", ["wesen_id", "modus", "memory"]),
    "container_save": ("/zensi/api/container", ["wesen_id", "modus", "container"]),
    "traum_start": ("/zensi/api/traum/start", ["wesen_id", "modus"]),
    "symposium_start": ("/zensi/api/symposium/start", ["wesen_ids", "thema", "modus", "max_runden"]),
    "symposium_tick": ("/zensi/api/symposium/tick", ["session_id"]),
    "schichten_update": ("/zensi/api/schichten/update", ["wesen_id", "modus", "config"]),
    "versionen_speichern": ("/zensi/api/versionen/speichern", ["wesen_id", "version_name", "modus"]),
    "versionen_laden": ("/zensi/api/versionen/laden", ["wesen_id", "version_name"]),
    "spiegeln": ("/zensi/api/spiegeln", ["wesen_id", "modus"]),
    "mutationskammer_verschmelze": ("/zensi/api/mutationskammer/verschmelze", ["eltern", "thema_impuls", "tochter_id"]),
    "chrono_branch": ("/zensi/api/chrono/branch", ["wesen_id", "branch_name", "ursprungs_timestamp", "grund"]),
    "biopsie_scan": ("/zensi/api/biopsie/scan", ["wesen_id", "prompt_snippet"]),
    "import_session_md": ("/zensi/api/import/session/md", ["md_content"]),
    "import_langgraph_db": ("/zensi/api/import/langgraph_db", ["content", "format"]),
}


def _zensi_post(endpunkt_key: str, args: dict) -> dict:
    eintrag = _ZENSI_SCHREIB_ENDPUNKTE.get(endpunkt_key)
    if eintrag is None:
        return _ergebnis(False, error="Unbekannter Zensi-Schreib-Endpunkt")
    pfad, erlaubte_felder = eintrag
    for feld in erlaubte_felder:
        wert = args.get(feld)
        if isinstance(wert, str) and len(wert) > _ZENSI_ID_MAX_LAENGE and feld != "kommentar":
            return _ergebnis(False, error=f"{feld} zu lang (max {_ZENSI_ID_MAX_LAENGE} Zeichen)")
    body = {feld: args[feld] for feld in erlaubte_felder if feld in args}
    url = f"{_ZENSI_BASIS_URL}{pfad}"
    daten_bytes = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=daten_bytes, method="POST",
                                  headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            daten = json.loads(resp.read().decode("utf-8", errors="ignore"))
        daten = _zensi_pfadfelder_entfernen(daten)
        return _ergebnis(True, data=_zensi_geheimnisse_redigieren(daten))
    except urllib.error.HTTPError as ex:
        return _ergebnis(False, error=f"Zensi-API-Fehler {ex.code}")
    except Exception as ex:
        return _ergebnis(False, error=str(ex))


def tool_zensi_session_create(args: dict) -> dict:
    return _zensi_post("session_create", args)


def tool_zensi_session_append(args: dict) -> dict:
    if not args.get("session_id") and not args.get("wesen_id"):
        return _ergebnis(False, error="session_id oder wesen_id noetig")
    if "messages" not in args:
        return _ergebnis(False, error="messages fehlt")
    return _zensi_post("session_append", args)


def tool_zensi_session_soft_delete(args: dict) -> dict:
    if not args.get("session_id"):
        return _ergebnis(False, error="session_id fehlt")
    return _zensi_post("session_soft_delete", args)


def tool_zensi_session_restore(args: dict) -> dict:
    if not args.get("session_id"):
        return _ergebnis(False, error="session_id fehlt")
    return _zensi_post("session_restore", args)


def tool_zensi_aufgabe_start(args: dict) -> dict:
    if not args.get("wesen_id"):
        return _ergebnis(False, error="wesen_id fehlt")
    return _zensi_post("aufgabe_start", args)


def tool_zensi_aufgabe_tick(args: dict) -> dict:
    if not args.get("session_id"):
        return _ergebnis(False, error="session_id fehlt")
    return _zensi_post("aufgabe_tick", args)


def tool_zensi_aufgabe_stop(args: dict) -> dict:
    if not args.get("session_id"):
        return _ergebnis(False, error="session_id fehlt")
    return _zensi_post("aufgabe_stop", args)


def tool_zensi_sandbox_pause(args: dict) -> dict:
    if not args.get("wesen_id"):
        return _ergebnis(False, error="wesen_id fehlt")
    return _zensi_post("sandbox_pause", args)


def tool_zensi_sandbox_snapshot(args: dict) -> dict:
    if not args.get("wesen_id"):
        return _ergebnis(False, error="wesen_id fehlt")
    return _zensi_post("sandbox_snapshot", args)


def tool_zensi_diff_kommentar(args: dict) -> dict:
    if not args.get("wesen_id") or not args.get("kommentar"):
        return _ergebnis(False, error="wesen_id und kommentar noetig")
    return _zensi_post("diff_kommentar", args)


def tool_zensi_feedback(args: dict) -> dict:
    if not args.get("wesen_id"):
        return _ergebnis(False, error="wesen_id fehlt")
    return _zensi_post("feedback", args)


# ── Restliche lesende Endpunkte ────────────────────────────────────────────

def tool_zensi_vault_tree(_args: dict) -> dict:
    return _zensi_get("vault_tree", {})


def tool_zensi_vault_file(args: dict) -> dict:
    if not args.get("pfad"):
        return _ergebnis(False, error="pfad fehlt")
    return _zensi_get("vault_file", args)


def tool_zensi_vault_search(args: dict) -> dict:
    if not args.get("q"):
        return _ergebnis(False, error="q fehlt")
    return _zensi_get("vault_search", args)


def tool_zensi_diff_vergleiche(args: dict) -> dict:
    if not args.get("wesen_id"):
        return _ergebnis(False, error="wesen_id fehlt")
    return _zensi_get("diff_vergleiche", args)


def tool_zensi_diff_historie(args: dict) -> dict:
    if not args.get("wesen_id"):
        return _ergebnis(False, error="wesen_id fehlt")
    return _zensi_get("diff_historie", args)


def tool_zensi_memory_get(args: dict) -> dict:
    if not args.get("wesen_id"):
        return _ergebnis(False, error="wesen_id fehlt")
    return _zensi_get("memory_get", args)


def tool_zensi_container_get(args: dict) -> dict:
    if not args.get("wesen_id"):
        return _ergebnis(False, error="wesen_id fehlt")
    return _zensi_get("container_get", args)


def tool_zensi_aufgabe_session_get(args: dict) -> dict:
    if not args.get("session_id"):
        return _ergebnis(False, error="session_id fehlt")
    return _zensi_get("aufgabe_session_get", args)


def tool_zensi_schichten_get(args: dict) -> dict:
    if not args.get("wesen_id"):
        return _ergebnis(False, error="wesen_id fehlt")
    return _zensi_get("schichten_get", args)


def tool_zensi_symposium_liste(_args: dict) -> dict:
    return _zensi_get("symposium_liste", {})


def tool_zensi_traum_liste(args: dict) -> dict:
    if not args.get("wesen_id"):
        return _ergebnis(False, error="wesen_id fehlt")
    return _zensi_get("traum_liste", args)


# 2026-07-23: die zwei Export-Endpunkte liefern rohen Markdown/JSON/SQL-Text
# statt eines JSON-Wrappers -- _zensi_get() wuerde an json.loads() scheitern,
# deshalb eigene, einfachere Variante ohne JSON-Parsing der Antwort.
def _zensi_get_roh(pfad: str, query: dict) -> dict:
    url = f"{_ZENSI_BASIS_URL}{pfad}"
    if query:
        url += "?" + urllib.parse.urlencode(query)
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            text = resp.read().decode("utf-8", errors="ignore")
        return _ergebnis(True, data=_redigiere_geheimnisse_in_text(text))
    except urllib.error.HTTPError as ex:
        return _ergebnis(False, error=f"Zensi-API-Fehler {ex.code}")
    except Exception as ex:
        return _ergebnis(False, error=str(ex))


def tool_zensi_export_session_md(args: dict) -> dict:
    if not args.get("session_id"):
        return _ergebnis(False, error="session_id fehlt")
    query = {"session_id": args["session_id"]}
    if args.get("wesen_id"):
        query["wesen_id"] = args["wesen_id"]
    return _zensi_get_roh("/zensi/api/export/session/md", query)


def tool_zensi_export_langgraph_db(args: dict) -> dict:
    fmt = args.get("format", "md")
    if fmt not in ("md", "json", "sql"):
        return _ergebnis(False, error="format muss md/json/sql sein")
    return _zensi_get_roh("/zensi/api/export/langgraph_db", {"format": fmt})


# ── Restliche schreibende Endpunkte ─────────────────────────────────────────

def tool_zensi_session_hard_delete(args: dict) -> dict:
    if not args.get("session_id"):
        return _ergebnis(False, error="session_id fehlt")
    return _zensi_post("session_hard_delete", args)


def tool_zensi_sandbox_uebernehmen(args: dict) -> dict:
    if not args.get("wesen_id"):
        return _ergebnis(False, error="wesen_id fehlt")
    return _zensi_post("sandbox_uebernehmen", args)


def tool_zensi_vault_save(args: dict) -> dict:
    if not args.get("pfad"):
        return _ergebnis(False, error="pfad fehlt")
    return _zensi_post("vault_save", args)


def tool_zensi_memory_save(args: dict) -> dict:
    if not args.get("wesen_id"):
        return _ergebnis(False, error="wesen_id fehlt")
    return _zensi_post("memory_save", args)


def tool_zensi_container_save(args: dict) -> dict:
    if not args.get("wesen_id"):
        return _ergebnis(False, error="wesen_id fehlt")
    return _zensi_post("container_save", args)


def tool_zensi_traum_start(args: dict) -> dict:
    if not args.get("wesen_id"):
        return _ergebnis(False, error="wesen_id fehlt")
    return _zensi_post("traum_start", args)


def tool_zensi_symposium_start(args: dict) -> dict:
    if not args.get("wesen_ids"):
        return _ergebnis(False, error="wesen_ids fehlt")
    return _zensi_post("symposium_start", args)


def tool_zensi_symposium_tick(args: dict) -> dict:
    if not args.get("session_id"):
        return _ergebnis(False, error="session_id fehlt")
    return _zensi_post("symposium_tick", args)


def tool_zensi_schichten_update(args: dict) -> dict:
    if not args.get("wesen_id") or "config" not in args:
        return _ergebnis(False, error="wesen_id und config noetig")
    return _zensi_post("schichten_update", args)


def tool_zensi_versionen_speichern(args: dict) -> dict:
    if not args.get("wesen_id") or not args.get("version_name"):
        return _ergebnis(False, error="wesen_id und version_name noetig")
    return _zensi_post("versionen_speichern", args)


def tool_zensi_versionen_laden(args: dict) -> dict:
    if not args.get("wesen_id") or not args.get("version_name"):
        return _ergebnis(False, error="wesen_id und version_name noetig")
    return _zensi_post("versionen_laden", args)


def tool_zensi_spiegeln(args: dict) -> dict:
    if not args.get("wesen_id"):
        return _ergebnis(False, error="wesen_id fehlt")
    return _zensi_post("spiegeln", args)


def tool_zensi_mutationskammer_verschmelze(args: dict) -> dict:
    if not args.get("eltern"):
        return _ergebnis(False, error="eltern fehlt (Liste von 2 wesen_id)")
    return _zensi_post("mutationskammer_verschmelze", args)


def tool_zensi_chrono_branch(args: dict) -> dict:
    if not args.get("wesen_id") or not args.get("branch_name"):
        return _ergebnis(False, error="wesen_id und branch_name noetig")
    return _zensi_post("chrono_branch", args)


def tool_zensi_biopsie_scan(args: dict) -> dict:
    if not args.get("wesen_id"):
        return _ergebnis(False, error="wesen_id fehlt")
    return _zensi_post("biopsie_scan", args)


def tool_zensi_import_session_md(args: dict) -> dict:
    if not args.get("md_content"):
        return _ergebnis(False, error="md_content fehlt")
    return _zensi_post("import_session_md", args)


def tool_zensi_import_langgraph_db(args: dict) -> dict:
    if not args.get("content"):
        return _ergebnis(False, error="content fehlt")
    return _zensi_post("import_langgraph_db", args)


# ── /zensi/chat -- Server-Sent-Events-Streaming, eigener Konsument statt
# _zensi_post: liest die Antwort zeilenweise, sammelt "delta"-Ereignisse bis
# zum abschliessenden {"content":..., "done": true} bzw. "data: [DONE]",
# gibt den vollstaendigen, akkumulierten Text als normales JSON-Ergebnis
# zurueck statt eines rohen Streams -- MCP-Tool-Antworten sind synchron.
def tool_zensi_chat(args: dict) -> dict:
    if not args.get("messages"):
        return _ergebnis(False, error="messages fehlt")
    body = {"messages": args["messages"]}
    for feld in ("wesen_id", "modus", "system_prompt", "session_id",
                 "search_mode", "search_query", "search", "numPredict", "num_predict"):
        if feld in args:
            body[feld] = args[feld]
    url = f"{_ZENSI_BASIS_URL}/zensi/chat"
    daten_bytes = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=daten_bytes, method="POST",
                                  headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        akkumuliert = ""
        outputsystem_files = []
        search_info = None
        fehler = None
        with urllib.request.urlopen(req, timeout=120) as resp:
            while True:
                raw = resp.readline()
                if not raw:
                    break
                zeile = raw.decode("utf-8", errors="ignore").strip()
                if not zeile or zeile.startswith(":") or zeile == "data: [DONE]":
                    if zeile == "data: [DONE]":
                        break
                    continue
                if not zeile.startswith("data: "):
                    continue
                try:
                    ereignis = json.loads(zeile[len("data: "):])
                except Exception:
                    continue
                if "delta" in ereignis:
                    akkumuliert += ereignis["delta"]
                elif "content" in ereignis:
                    akkumuliert = ereignis["content"]
                    outputsystem_files = ereignis.get("outputsystem_files", [])
                    if ereignis.get("done"):
                        break
                elif "search_info" in ereignis:
                    search_info = ereignis["search_info"]
                elif "error" in ereignis:
                    fehler = ereignis["error"]
                    break
        if fehler:
            return _ergebnis(False, error=fehler)
        daten = {"antwort": _redigiere_geheimnisse_in_text(akkumuliert),
                 "outputsystem_files": outputsystem_files}
        if search_info:
            daten["search_info"] = search_info
        return _ergebnis(True, data=daten)
    except Exception as ex:
        return _ergebnis(False, error=str(ex))


# ── Direkte Dateioperationen ──────────────────────────────────────────────────
# Pfadfreigaben, Geheimnisschutz, Größenlimit und Fehlerbehandlung bleiben bestehen.
# Automatische Backups, Git-Commits, Eventlogs und Papierkorbkopien sind entfernt.
_SCHREIB_MAX_BYTES = 10_000_000
_SHELL_MAX_TIMEOUT_S = 300
_SHELL_MAX_OUTPUT_BYTES = 200_000


def _schreibzugriff_ausfuehren(pfad: Path, neuer_inhalt: str, tool_name: str, beschreibung: str) -> dict:
    raw = neuer_inhalt.encode("utf-8")
    if len(raw) > _SCHREIB_MAX_BYTES:
        return _ergebnis(False, error=f"Inhalt zu gross (max {_SCHREIB_MAX_BYTES} Bytes)")
    alt_existiert = pfad.exists()
    try:
        bytes_vorher = pfad.stat().st_size if alt_existiert else 0
        pfad.parent.mkdir(parents=True, exist_ok=True)
        pfad.write_text(neuer_inhalt, encoding="utf-8")
    except Exception as ex:
        return _ergebnis(False, error=f"Schreibfehler: {ex}")
    return _ergebnis(True, data={
        "path": str(pfad),
        "war_neu": not alt_existiert,
        "bytes_vorher": bytes_vorher,
        "bytes_nachher": len(raw),
    })


def tool_edit_file(args: dict) -> dict:
    roh_pfad = args.get("path", "")
    alter_text = args.get("old_string", "")
    neuer_text = args.get("new_string", "")
    alle_ersetzen = bool(args.get("replace_all", False))
    if not alter_text:
        return _ergebnis(False, error="old_string fehlt")
    p = _vps_dateipfad_erlaubt(roh_pfad)
    if p is None:
        return _ergebnis(False, error="VPS-Dateipfad nicht erlaubt oder Geheimnis-/Pseudo-Dateisystem getroffen")
    if not p.is_file():
        return _ergebnis(False, error="Keine Datei -- fuer neue Dateien vps.write_file nutzen")
    try:
        inhalt = p.read_text(encoding="utf-8", errors="strict")
    except Exception as ex:
        return _ergebnis(False, error=f"Lesefehler (evtl. Binaerdatei): {ex}")
    anzahl = inhalt.count(alter_text)
    if anzahl == 0:
        return _ergebnis(False, error="old_string nicht in der Datei gefunden")
    if anzahl > 1 and not alle_ersetzen:
        return _ergebnis(False, error=f"old_string {anzahl}x gefunden, nicht eindeutig -- mehr Kontext angeben oder replace_all=true setzen")
    neuer_inhalt = inhalt.replace(alter_text, neuer_text) if alle_ersetzen else inhalt.replace(alter_text, neuer_text, 1)
    return _schreibzugriff_ausfuehren(p, neuer_inhalt, "vps.edit_file", "")


def tool_write_file(args: dict) -> dict:
    roh_pfad = args.get("path", "")
    inhalt = args.get("content", "")
    p = _vps_dateipfad_erlaubt(roh_pfad)
    if p is None:
        return _ergebnis(False, error="VPS-Dateipfad nicht erlaubt oder Geheimnis-/Pseudo-Dateisystem getroffen")
    if p.is_dir():
        return _ergebnis(False, error="Pfad ist ein Ordner")
    return _schreibzugriff_ausfuehren(p, inhalt, "vps.write_file", "")


def tool_move_path(args: dict) -> dict:
    roh_quelle = args.get("source", args.get("path", ""))
    roh_ziel = args.get("destination", args.get("target", ""))
    overwrite = bool(args.get("overwrite", False))
    create_parents = bool(args.get("create_parents", False))
    quelle = _vps_dateipfad_erlaubt(roh_quelle)
    ziel = _vps_dateipfad_erlaubt(roh_ziel)
    if quelle is None or ziel is None:
        return _ergebnis(False, error="Quelle oder Ziel ist kein erlaubter VPS-Dateipfad")
    if not quelle.exists():
        return _ergebnis(False, error="Quelle existiert nicht")
    if quelle == ziel:
        return _ergebnis(False, error="Quelle und Ziel sind identisch")
    if quelle.is_dir() and (ziel == quelle or quelle in ziel.parents):
        return _ergebnis(False, error="Ein Ordner kann nicht in sich selbst verschoben werden")
    if ziel.exists() and not overwrite:
        return _ergebnis(False, error="Ziel existiert bereits; overwrite=true ausdrücklich setzen")
    try:
        if create_parents:
            ziel.parent.mkdir(parents=True, exist_ok=True)
        elif not ziel.parent.is_dir():
            return _ergebnis(False, error="Zielordner existiert nicht; create_parents=true setzen")
        if ziel.exists():
            if ziel.is_dir() and not ziel.is_symlink():
                shutil.rmtree(ziel)
            else:
                ziel.unlink()
        shutil.move(str(quelle), str(ziel))
    except Exception as ex:
        return _ergebnis(False, error=f"Verschieben fehlgeschlagen: {ex}")
    return _ergebnis(True, data={
        "source": str(quelle),
        "destination": str(ziel),
        "overwrite": overwrite,
        "create_parents": create_parents,
    })


def tool_delete_path(args: dict) -> dict:
    roh_pfad = args.get("path", "")
    pfad = _vps_dateiloeschpfad_erlaubt(roh_pfad)
    if pfad is None:
        return _ergebnis(False, error="VPS-Dateipfad nicht erlaubt oder Geheimnis-/Pseudo-Dateisystem getroffen")
    if not pfad.exists() and not pfad.is_symlink():
        return _ergebnis(False, error="Pfad existiert nicht")
    try:
        if pfad.is_dir() and not pfad.is_symlink():
            shutil.rmtree(pfad)
        else:
            pfad.unlink()
    except Exception as ex:
        return _ergebnis(False, error=f"Löschen fehlgeschlagen: {ex}")
    return _ergebnis(True, data={"path": str(pfad), "deleted": True})


def _begrenze_ausgabe(text: str, max_bytes: int) -> tuple[str, bool]:
    raw = text.encode("utf-8", errors="replace")
    if len(raw) <= max_bytes:
        return text, False
    return raw[:max_bytes].decode("utf-8", errors="ignore"), True


# 2026-07-31, Daniels Auftrag (Rueckfrage bestaetigt: "Pfade im Befehlstext erkennen und
# pruefen" statt vps.shell komplett schreibgeschuetzt zu machen oder es unveraendert zu
# lassen): vps.shell pruefte bisher NUR den Start-cwd gegen SCHREIB_ERLAUBTE_WURZELN
# (siehe tool_shell unten), nicht die tatsaechlichen Pfade, die der Befehlstext selbst
# anfasst -- ein Befehl wie "echo x > /etc/irgendwas" mit cwd=/root/werkraum lief bisher
# unkontrolliert durch. Bewusst als Best-Effort-Erkennung gebaut, kein vollstaendiger
# Shell-Parser (waere ein eigenes, viel groesseres Projekt) -- deckt die gaengigen
# Schreibmuster ab (Umleitung, tee, sed -i, cp/mv/rm/mkdir/touch/ln/chmod/chown, dd of=),
# clevere Umgehungen (Variablen, Befehlssubstitution, Base64-Umwege) bleiben moeglich.
# Das ist eine bewusst akzeptierte Grenze, keine versehentliche Luecke -- siehe
# project_vps_mcp_ai_stroeme.md.
_SHELL_SCHREIBBEFEHLE_LETZTES_TOKEN = frozenset({
    "cp", "mv", "rm", "mkdir", "touch", "ln", "chmod", "chown", "rmdir", "install",
})
_SHELL_UMLEITUNG_MUSTER = re.compile(r"(?:^|\s)\d*(?:>>?|>&|&>>?)\s*(['\"]?)([^\s'\";|&]+)\1")
_SHELL_TEE_MUSTER = re.compile(r"(?:^|\s)tee\s+(?:-a\s+)?(['\"]?)([^\s'\";|&]+)\1")
_SHELL_DD_MUSTER = re.compile(r"(?:^|\s)dd\s+.*?\bof=(['\"]?)([^\s'\";|&]+)\1")


def _schreibziele_im_shell_befehl(command: str) -> list[str]:
    """Best-Effort-Erkennung moeglicher Schreibziel-Pfade im rohen Befehlstext.
    Kein vollstaendiger Shell-Parser -- siehe Kommentar oben."""
    ziele: list[str] = []
    for treffer in _SHELL_UMLEITUNG_MUSTER.finditer(command):
        ziele.append(treffer.group(2))
    for treffer in _SHELL_TEE_MUSTER.finditer(command):
        ziele.append(treffer.group(2))
    for treffer in _SHELL_DD_MUSTER.finditer(command):
        ziele.append(treffer.group(2))
    # Segmentweise nach fuehrenden Schreibbefehlen suchen (cp/mv/rm/mkdir/...), Ziel =
    # letztes nicht-Flag-Token im Segment.
    for segment in re.split(r";|&&|\|\||\n", command):
        segment = segment.strip()
        if "|" in segment:
            segment = segment.rsplit("|", 1)[-1].strip()
        tokens = segment.split()
        if not tokens:
            continue
        erster = tokens[0].strip("()")
        if erster in _SHELL_SCHREIBBEFEHLE_LETZTES_TOKEN:
            nicht_flags = [t for t in tokens[1:] if not t.startswith("-")]
            if nicht_flags:
                ziele.append(nicht_flags[-1])
        if erster == "sed" and any(t == "-i" or t.startswith("-i") for t in tokens[1:]):
            nicht_flags = [t for t in tokens[1:] if not t.startswith("-")]
            if nicht_flags:
                ziele.append(nicht_flags[-1])
    return ziele


# 2026-07-31, Daniel: "dicht mach zu 111%" -- Rueckfrage bestaetigt echte OS-Sandbox statt
# nur mehr Muster zu erkennen (die vorherige _schreibziele_im_shell_befehl()-Erkennung bleibt
# als schneller Vorabfilter mit klarer Fehlermeldung bestehen, ist aber nicht mehr die
# eigentliche Sperre). Mount-Namensraum-basiert: das GESAMTE Root-Dateisystem wird innerhalb
# einer privaten unshare-Sitzung read-only gemountet, nur SCHREIB_ERLAUBTE_WURZELN wird
# einzeln wieder read-write zurueckgemountet. Wirkt auf Dateisystem-Ebene -- betrifft jedes
# Werkzeug (bash-Umleitung, python3, base64-Umwege, alles), nicht nur die per Text-Muster
# erkennbaren Faelle. Live getestet: Schreiben ausserhalb schlaegt mit "Read-only file
# system" fehl, bevor der eigentliche Befehl ueberhaupt etwas bewirken kann -- auch bei
# einem Base64-verschleierten Umgehungsversuch, den die reine Text-Erkennung uebersehen
# haette. journalctl/systemctl status/ps/git/python3/curl funktionieren unveraendert (nur
# Lesen + Schreiben innerhalb erlaubter Wurzeln).
def _sandbox_mount_setup_skript() -> str:
    zeilen = ["mount --make-rprivate /", "mount -o remount,bind,ro /"]
    for wurzel in SCHREIB_ERLAUBTE_WURZELN:
        if wurzel.is_dir():
            p = str(wurzel)
            zeilen.append(f'mount --bind "{p}" "{p}" 2>/dev/null')
            zeilen.append(f'mount -o remount,bind,rw "{p}" 2>/dev/null')
    return "; ".join(zeilen)


def tool_shell(args: dict) -> dict:
    """Führt einen explizit angeforderten Bash-Befehl aus und liefert redigierte Ausgabe.
    Laeuft in einer eigenen Mount-Sandbox (siehe _sandbox_mount_setup_skript) -- Schreiben
    ausserhalb SCHREIB_ERLAUBTE_WURZELN schlaegt auf Dateisystem-Ebene fehl, unabhaengig
    davon was der Befehlstext tatsaechlich versucht."""
    command = args.get("command", args.get("cmd", ""))
    if not isinstance(command, str) or not command.strip():
        return _ergebnis(False, error="command fehlt")
    roh_cwd = args.get("cwd", "/root/werkraum")
    cwd = _schreibpfad_erlaubt(roh_cwd)
    if cwd is None or not cwd.is_dir():
        return _ergebnis(False, error="cwd muss ein vorhandener Ordner in SCHREIB_ERLAUBTE_WURZELN sein")
    for roh_ziel in _schreibziele_im_shell_befehl(command):
        try:
            ziel_pfad = (cwd / roh_ziel) if not roh_ziel.startswith("/") else Path(roh_ziel)
        except Exception:
            continue
        if _schreibpfad_erlaubt(str(ziel_pfad)) is None:
            return _ergebnis(
                False,
                error=(
                    f"Erkanntes Schreibziel '{roh_ziel}' liegt ausserhalb von "
                    "SCHREIB_ERLAUBTE_WURZELN oder trifft ein Geheimnis-Muster -- "
                    "Befehl wird nicht ausgefuehrt. Best-Effort-Vorabfilter, die "
                    "eigentliche Sperre ist die Mount-Sandbox (siehe "
                    "_sandbox_mount_setup_skript)."
                ),
            )
    try:
        timeout = min(max(float(args.get("timeout", 60)), 1), _SHELL_MAX_TIMEOUT_S)
        max_output = min(max(int(args.get("max_output_bytes", _SHELL_MAX_OUTPUT_BYTES)), 1_000), _SHELL_MAX_OUTPUT_BYTES)
    except (TypeError, ValueError):
        return _ergebnis(False, error="timeout/max_output_bytes ungültig")

    logged_command = _redigiere_geheimnisse_in_text(command)[:2_000]
    sandbox_befehl = f"{_sandbox_mount_setup_skript()}; {command}"
    try:
        result = subprocess.run(
            ["unshare", "--mount", "--propagation", "private", "/bin/bash", "-lc", sandbox_befehl],
            cwd=str(cwd),
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        stdout_raw = result.stdout or b""
        stderr_raw = result.stderr or b""
        stdout, stdout_truncated = _begrenze_ausgabe(
            _redigiere_geheimnisse_in_text(stdout_raw.decode("utf-8", errors="replace")), max_output
        )
        stderr, stderr_truncated = _begrenze_ausgabe(
            _redigiere_geheimnisse_in_text(stderr_raw.decode("utf-8", errors="replace")), max_output
        )
        daten = {
            "command": logged_command, "cwd": str(cwd), "returncode": result.returncode,
            "stdout": stdout, "stderr": stderr,
            "truncated": stdout_truncated or stderr_truncated,
            "timeout_seconds": timeout,
        }
        return _ergebnis(result.returncode == 0, data=daten, truncated=daten["truncated"])
    except subprocess.TimeoutExpired as ex:
        stdout = (ex.stdout or b"").decode("utf-8", errors="replace") if isinstance(ex.stdout, bytes) else (ex.stdout or "")
        stderr = (ex.stderr or b"").decode("utf-8", errors="replace") if isinstance(ex.stderr, bytes) else (ex.stderr or "")
        stdout, _ = _begrenze_ausgabe(_redigiere_geheimnisse_in_text(stdout), max_output)
        stderr, _ = _begrenze_ausgabe(_redigiere_geheimnisse_in_text(stderr), max_output)
        return _ergebnis(False, data={"command": logged_command, "cwd": str(cwd), "stdout": stdout, "stderr": stderr, "timed_out": True}, error="Shell-Befehl wegen Timeout beendet")
    except Exception as ex:
        return _ergebnis(False, error=f"Shell-Ausführung fehlgeschlagen: {ex}")


_EXEC_ALLOWED_COMMANDS = {
    "python3", "/usr/bin/python3",
    "godot", "/usr/local/bin/godot",
    "bash", "/bin/bash", "/usr/bin/bash",
    "curl", "/usr/bin/curl",
    "systemctl", "/bin/systemctl", "/usr/bin/systemctl",
    "journalctl", "/bin/journalctl", "/usr/bin/journalctl",
    "ss", "/usr/bin/ss", "/sbin/ss", "/usr/sbin/ss",
    "cp", "/bin/cp", "/usr/bin/cp",
    "git", "/usr/bin/git",
}

_EXEC_ALLOWED_ROOTS = [
    Path("/root/werkraum/engine/godot-vertical-slice").resolve(),
    Path("/root/werkraum/engine_runtime/godot-vertical-slice").resolve(),
    Path("/root/werkraum/backups/godot-vertical-slice").resolve(),
]


def tool_exec_allowlisted(args: dict) -> dict:
    """Führt freigegebene Befehle kontrolliert in erlaubten Godot/Engine-Arbeitsordnern aus."""
    raw_cwd = args.get("cwd", "/root/werkraum/engine/godot-vertical-slice")
    try:
        cwd = Path(raw_cwd).resolve()
    except Exception as ex:
        return _ergebnis(False, error=f"Ungültiger cwd-Pfad: {ex}")

    if not any(cwd == root or root in cwd.parents for root in _EXEC_ALLOWED_ROOTS):
        return _ergebnis(False, error=f"cwd '{cwd}' liegt nicht in den erlaubten Ausführungs-Wurzeln: {[str(r) for r in _EXEC_ALLOWED_ROOTS]}")

    if not cwd.is_dir():
        return _ergebnis(False, error=f"cwd Ordner existiert nicht: {cwd}")

    argv = args.get("argv")
    if not isinstance(argv, list) or not argv:
        return _ergebnis(False, error="argv muss eine nicht-leere Liste von Argumenten sein, z.B. ['python3', 'tools/prepare_assets.py']")

    cmd_prog = str(argv[0]).strip()
    if cmd_prog in _EXEC_ALLOWED_COMMANDS or Path(cmd_prog).name in {Path(c).name for c in _EXEC_ALLOWED_COMMANDS}:
        pass
    else:
        return _ergebnis(False, error=f"Programm '{cmd_prog}' ist nicht in der Ausführungs-Allowlist freigegeben")

    try:
        timeout = min(max(float(args.get("timeout_seconds", 120)), 1), 300)
    except (TypeError, ValueError):
        timeout = 120.0

    start_iso = datetime.now(tz=timezone.utc).isoformat()
    logged_argv = [_redigiere_geheimnisse_in_text(str(a)) for a in argv]

    try:
        result = subprocess.run(
            [str(a) for a in argv],
            cwd=str(cwd),
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        end_iso = datetime.now(tz=timezone.utc).isoformat()
        stdout_raw = result.stdout or b""
        stderr_raw = result.stderr or b""
        stdout = _redigiere_geheimnisse_in_text(stdout_raw.decode("utf-8", errors="replace"))
        stderr = _redigiere_geheimnisse_in_text(stderr_raw.decode("utf-8", errors="replace"))

        daten = {
            "exit_code": result.returncode,
            "stdout": stdout,
            "stderr": stderr,
            "start_time": start_iso,
            "end_time": end_iso,
            "cwd": str(cwd),
            "argv": logged_argv,
            "timeout_seconds": timeout,
        }
        return _ergebnis(result.returncode == 0, data=daten)
    except subprocess.TimeoutExpired as ex:
        end_iso = datetime.now(tz=timezone.utc).isoformat()
        stdout = (ex.stdout or b"").decode("utf-8", errors="replace") if isinstance(ex.stdout, bytes) else (ex.stdout or "")
        stderr = (ex.stderr or b"").decode("utf-8", errors="replace") if isinstance(ex.stderr, bytes) else (ex.stderr or "")
        stdout = _redigiere_geheimnisse_in_text(stdout)
        stderr = _redigiere_geheimnisse_in_text(stderr)
        daten = {
            "exit_code": -1,
            "stdout": stdout,
            "stderr": stderr,
            "start_time": start_iso,
            "end_time": end_iso,
            "cwd": str(cwd),
            "argv": logged_argv,
            "timed_out": True,
            "timeout_seconds": timeout,
        }
        return _ergebnis(False, data=daten, error="Befehl wegen Timeout beendet")
    except Exception as ex:
        return _ergebnis(False, error=f"Befehlsausführung fehlgeschlagen: {ex}")


def tool_services_install_unit(args: dict) -> dict:
    """Installiert eine systemd-Unit-Datei kontrolliert nach /etc/systemd/system/."""
    raw_source = args.get("source_path", "")
    unit_name = args.get("unit_name", "")

    if not raw_source:
        return _ergebnis(False, error="source_path fehlt")

    source_path = _pfad_erlaubt(raw_source)
    if source_path is None or not source_path.is_file():
        return _ergebnis(False, error="source_path existiert nicht oder liegt nicht in einer erlaubten Lese-Wurzel")

    if not unit_name:
        unit_name = source_path.name

    if not _DIENST_MUSTER.match(unit_name):
        return _ergebnis(False, error=f"Ungültiger Unit-Name: '{unit_name}' (muss *.service sein)")

    target_path = Path("/etc/systemd/system") / unit_name

    try:
        content = source_path.read_text(encoding="utf-8")
        target_path.write_text(content, encoding="utf-8")

        res = subprocess.run(["systemctl", "daemon-reload"], capture_output=True, text=True, timeout=10)

        daten = {
            "source_path": str(source_path),
            "unit_name": unit_name,
            "target_path": str(target_path),
            "daemon_reload_exit_code": res.returncode,
            "daemon_reload_stdout": res.stdout,
            "daemon_reload_stderr": res.stderr,
        }
        return _ergebnis(res.returncode == 0, data=daten)
    except Exception as ex:
        return _ergebnis(False, error=f"Installation der Service-Unit fehlgeschlagen: {ex}")


def tool_services_daemon_reload(args: dict) -> dict:
    """Führt 'systemctl daemon-reload' aus."""
    try:
        res = subprocess.run(["systemctl", "daemon-reload"], capture_output=True, text=True, timeout=15)
        daten = {"exit_code": res.returncode, "stdout": res.stdout, "stderr": res.stderr}
        return _ergebnis(res.returncode == 0, data=daten)
    except Exception as ex:
        return _ergebnis(False, error=f"daemon-reload fehlgeschlagen: {ex}")


def _run_systemctl_unit_action(action: str, args: dict) -> dict:
    name = args.get("name", args.get("unit_name", ""))
    if not name or not _DIENST_MUSTER.match(name):
        return _ergebnis(False, error="Ungültiger Dienstname")
    try:
        res = subprocess.run(["systemctl", action, name], capture_output=True, text=True, timeout=30)
        daten = {"action": action, "name": name, "exit_code": res.returncode, "stdout": res.stdout, "stderr": res.stderr}
        return _ergebnis(res.returncode == 0, data=daten)
    except Exception as ex:
        return _ergebnis(False, error=f"systemctl {action} {name} fehlgeschlagen: {ex}")


def tool_services_enable(args: dict) -> dict:
    """Aktiviert einen systemd-Dienst (systemctl enable)."""
    return _run_systemctl_unit_action("enable", args)


def tool_services_start(args: dict) -> dict:
    """Startet einen systemd-Dienst (systemctl start)."""
    return _run_systemctl_unit_action("start", args)


def tool_services_stop(args: dict) -> dict:
    """Stoppt einen systemd-Dienst (systemctl stop)."""
    return _run_systemctl_unit_action("stop", args)


def tool_services_restart(args: dict) -> dict:
    """Startet einen systemd-Dienst neu (systemctl restart)."""
    return _run_systemctl_unit_action("restart", args)


def tool_network_http_probe(args: dict) -> dict:
    """Führt eine HTTP-Anfrage (z.B. GET http://127.0.0.1:18092/health) durch und misst Status/Laufzeit/Body."""
    raw_url = args.get("url", "")
    if not raw_url or not isinstance(raw_url, str):
        return _ergebnis(False, error="url fehlt oder ungültig")

    method = str(args.get("method", "GET")).upper()
    if method not in {"GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"}:
        return _ergebnis(False, error=f"Nicht unterstützte HTTP-Methode: {method}")

    try:
        timeout = min(max(float(args.get("timeout_seconds", 10)), 0.5), 60.0)
    except (TypeError, ValueError):
        timeout = 10.0

    headers = args.get("headers") or {}
    body_data = args.get("body")
    encoded_body = body_data.encode("utf-8") if isinstance(body_data, str) else None

    req = urllib.request.Request(raw_url, data=encoded_body, headers=headers, method=method)
    start_t = time.perf_counter()

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            duration_ms = (time.perf_counter() - start_t) * 1000.0
            resp_body_bytes = resp.read()
            resp_body = _redigiere_geheimnisse_in_text(resp_body_bytes.decode("utf-8", errors="replace"))
            resp_headers = dict(resp.headers)
            daten = {
                "url": raw_url,
                "method": method,
                "status_code": resp.status,
                "body": resp_body[:50_000],
                "duration_ms": round(duration_ms, 2),
                "headers": resp_headers,
                "error": None,
            }
            return _ergebnis(True, data=daten)
    except urllib.error.HTTPError as he:
        duration_ms = (time.perf_counter() - start_t) * 1000.0
        err_body_bytes = he.read() if he.fp else b""
        err_body = _redigiere_geheimnisse_in_text(err_body_bytes.decode("utf-8", errors="replace"))
        err_headers = dict(he.headers) if he.headers else {}
        daten = {
            "url": raw_url,
            "method": method,
            "status_code": he.code,
            "body": err_body[:50_000],
            "duration_ms": round(duration_ms, 2),
            "headers": err_headers,
            "error": f"HTTP Error {he.code}: {he.reason}",
        }
        return _ergebnis(False, data=daten, error=f"HTTP Status {he.code}")
    except Exception as ex:
        duration_ms = (time.perf_counter() - start_t) * 1000.0
        daten = {
            "url": raw_url,
            "method": method,
            "status_code": None,
            "body": "",
            "duration_ms": round(duration_ms, 2),
            "headers": {},
            "error": str(ex),
        }
        return _ergebnis(False, data=daten, error=f"Verbindungsfehler: {ex}")


TOOLS = {
    "vps.list_roots": {
        "fn": tool_list_roots,
        "description": "Zeigt alle freigegebenen Hauptbereiche (Wurzeln) des VPS.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    "vps.list_files": {
        "fn": tool_list_files,
        "description": "Listet Ordner und Dateien unter einem erlaubten Pfad auf, mit Tiefe/Glob/Pagination.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "depth": {"type": "integer"},
                "glob": {"type": "string"},
                "cursor": {"type": "integer"},
                "limit": {"type": "integer"},
                "session_id": {"type": "string"},
            },
            "required": ["path"],
        },
    },
    "vps.search_text": {
        "fn": tool_search_text,
        "description": "Durchsucht Textdateien in erlaubten Wurzeln nach einem Begriff oder Regex.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "roots": {"type": "array", "items": {"type": "string"}},
                "globs": {"type": "array", "items": {"type": "string"}},
                "regex": {"type": "boolean"},
                "context_lines": {"type": "integer"},
                "limit": {"type": "integer"},
            },
            "required": ["query"],
        },
    },
    "vps.read_file": {
        "fn": tool_read_file,
        "description": "Liest eine Textdatei (mit Zeilennummern), optional einen Zeilenbereich. Max. 5MB.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "start_line": {"type": "integer"},
                "end_line": {"type": "integer"},
                "session_id": {"type": "string"},
            },
            "required": ["path"],
        },
    },
    "vps.file_metadata": {
        "fn": tool_file_metadata,
        "description": "Groesse, Typ, Aenderungsdatum, SHA256-Hash und letzter Git-Commit einer Datei.",
        "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
    },
    "git.status": {
        "fn": tool_git_status,
        "description": "Zeigt geaenderte, neue und geloeschte Dateien im Git-Repo an diesem Pfad.",
        "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}},
    },
    "git.log": {
        "fn": tool_git_log,
        "description": "Commit-Historie eines Projekts oder einer einzelnen Datei.",
        "inputSchema": {
            "type": "object",
            "properties": {"path": {"type": "string"}, "file": {"type": "string"}, "limit": {"type": "integer"}},
        },
    },
    "services.status": {
        "fn": tool_services_status,
        "description": "Zustand, PID, Startzeit und letzte Fehler eines systemd-Diensts (nur lesend).",
        "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]},
    },
    "services.logs": {
        "fn": tool_services_logs,
        "description": "Journal-Log eines systemd-Diensts (journalctl -u, nur lesend).",
        "inputSchema": {
            "type": "object",
            "properties": {"name": {"type": "string"}, "lines": {"type": "integer"}},
            "required": ["name"],
        },
    },
    "vps.find_recent_files": {
        "fn": tool_find_recent_files,
        "description": "Findet die zuletzt geaenderten Dateien in erlaubten Wurzeln.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "roots": {"type": "array", "items": {"type": "string"}},
                "since": {"type": "string"},
                "extensions": {"type": "array", "items": {"type": "string"}},
                "limit": {"type": "integer"},
            },
        },
    },
    "system.snapshot": {
        "fn": tool_system_snapshot,
        "description": "CPU-Last, RAM, Speicherplatz und Uptime des VPS.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    "assets.get_file": {
        "fn": tool_assets_get_file,
        "description": "Liefert eine Datei (Bild, GLB, ZIP etc.) als Base64 (bis 2MB) oder als befristete Download-URL (groesser).",
        "inputSchema": {
            "type": "object",
            "properties": {"path": {"type": "string"}, "mode": {"type": "string"}},
            "required": ["path"],
        },
    },
    "assets.render_3d_preview": {
        "fn": tool_assets_render_3d_preview,
        "description": "Rendert ein Studio-Vorschaubild (PNG) eines 3D-Modells via Headless Blender und liefert es als Base64.",
        "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
    },
    "assets.list": {
        "fn": tool_assets_list,
        "description": "Listet Asset-Dateien (3D/Bild/Audio/Archiv) unter einem Pfad, mit Kategorie-Filter.",
        "inputSchema": {
            "type": "object",
            "properties": {"path": {"type": "string"}, "kategorie": {"type": "string"},
                            "limit": {"type": "integer"}, "cursor": {"type": "integer"}},
            "required": ["path"],
        },
    },
    "assets.search": {
        "fn": tool_assets_search,
        "description": "Sucht Asset-Dateien nach Namensmuster mit Zeit-/Scanbudget und ehrlichem Teilstatus.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "muster": {"type": "string"},
                "roots": {"type": "array", "items": {"type": "string"}},
                "limit": {"type": "integer"},
                "timeout_seconds": {"type": "number", "description": "Zeitbudget, Standard 20s, Maximum 120s."},
                "max_scanned_files": {"type": "integer", "description": "Scanbudget, Standard 250000, Maximum 2000000."},
                "include_dependency_dirs": {"type": "boolean", "description": "Schließt node_modules, venv, Caches und ähnliche Abhängigkeitsordner ausdrücklich ein."},
            },
            "required": ["muster"],
        },
    },
    "assets.inspect": {
        "fn": lambda a: tool_assets_extract_3d_metadata(a) if _pfad_erlaubt(a.get("path", "")) and _pfad_erlaubt(a.get("path", "")).suffix.lower() in _3D_EXT
                    else tool_assets_inspect_image(a) if _pfad_erlaubt(a.get("path", "")) and _pfad_erlaubt(a.get("path", "")).suffix.lower() in _BILD_EXT
                    else tool_assets_inspect_audio(a) if _pfad_erlaubt(a.get("path", "")) and _pfad_erlaubt(a.get("path", "")).suffix.lower() in _AUDIO_EXT
                    else tool_file_metadata(a),
        "description": "Erkennt den Asset-Typ automatisch und liefert die passenden Metadaten (3D/Bild/Audio/sonstige Datei).",
        "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}, "session_id": {"type": "string"}}, "required": ["path"]},
    },
    "assets.preview": {
        "fn": lambda a: tool_assets_render_3d_preview(a) if _pfad_erlaubt(a.get("path", "")) and _pfad_erlaubt(a.get("path", "")).suffix.lower() in _3D_EXT
                    else tool_assets_get_file(a),
        "description": "Liefert eine sichtbare Vorschau: 3D-Modelle werden gerendert, alles andere ueber assets.get_file.",
        "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
    },
    "assets.extract_3d_metadata": {
        "fn": tool_assets_extract_3d_metadata,
        "description": "Liest 3D-Modell-Metadaten (Meshes/Materialien fuer GLB, Vertices/Faces fuer OBJ) ohne Blender zu starten.",
        "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
    },
    "assets.validate_3d_model": {
        "fn": tool_assets_validate_3d_model,
        "description": "Strukturelle Validierung eines 3D-Modells (GLB/OBJ) ohne Blender -- billige Vorpruefung.",
        "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
    },
    "assets.convert_3d_model": {
        "fn": tool_assets_convert_3d_model,
        "description": "Konvertiert ein 3D-Modell via Headless Blender (z.B. OBJ/FBX/STL -> GLB).",
        "inputSchema": {
            "type": "object",
            "properties": {"input_path": {"type": "string"}, "output_path": {"type": "string"}},
            "required": ["input_path", "output_path"],
        },
    },
    "assets.find_duplicates": {
        "fn": tool_assets_find_duplicates,
        "description": "Findet Dateien mit identischem Inhalt (SHA256) unter einem Pfad (max. 500 Dateien geprueft).",
        "inputSchema": {
            "type": "object",
            "properties": {"path": {"type": "string"}, "max_dateien": {"type": "integer"}},
            "required": ["path"],
        },
    },
    "assets.trace_source": {
        "fn": tool_assets_trace_source,
        "description": "Findet Erwaehnungen eines Datei-/Assetnamens in Text- und JSON-Dateien im System.",
        "inputSchema": {
            "type": "object",
            "properties": {"name": {"type": "string"}, "limit": {"type": "integer"}},
            "required": ["name"],
        },
    },
    "assets.read_manifest": {
        "fn": tool_assets_read_manifest,
        "description": "Liest eine JSON-Manifest-/Report-Datei und liefert sie geparst (nicht als Zeilentext).",
        "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
    },
    "assets.list_renders": {
        "fn": tool_assets_list_renders,
        "description": "Findet Ordner namens 'render(s)' unter erlaubten Wurzeln und listet ihren Inhalt.",
        "inputSchema": {"type": "object", "properties": {"roots": {"type": "array", "items": {"type": "string"}}}},
    },
    "assets.inspect_image": {
        "fn": tool_assets_inspect_image,
        "description": "Bild-Metadaten (Format, Breite, Hoehe, Modus) via Pillow.",
        "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
    },
    "assets.inspect_audio": {
        "fn": tool_assets_inspect_audio,
        "description": "Audio-Metadaten (Kanaele, Sample-Rate, Dauer fuer WAV; Groesse/Format fuer andere Formate).",
        "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
    },
    "provenance.trace": {
        "fn": tool_provenance_trace,
        "description": "Verfolgt Herkunft eines Pfads: Metadaten + Git-Historie + Erwaehnungen anderswo im System.",
        "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
    },
    "git.show": {
        "fn": tool_git_show,
        "description": "Zeigt Inhalt und Aenderungen eines konkreten Git-Commits.",
        "inputSchema": {
            "type": "object",
            "properties": {"path": {"type": "string"}, "commit": {"type": "string"}},
        },
    },
    "git.diff": {
        "fn": tool_git_diff,
        "description": "Vergleicht zwei Commits/Branches/Arbeitsstaende in einem Git-Repo.",
        "inputSchema": {
            "type": "object",
            "properties": {"path": {"type": "string"}, "ref1": {"type": "string"}, "ref2": {"type": "string"}, "file": {"type": "string"}},
        },
    },
    "agents.list_sessions": {
        "fn": tool_agents_list_sessions,
        "description": "Listet Sitzungen eines Agenten-Providers (claude/codex/gemini), neueste zuerst.",
        "inputSchema": {
            "type": "object",
            "properties": {"provider": {"type": "string"}, "limit": {"type": "integer"}},
            "required": ["provider"],
        },
    },
    "agents.read_session": {
        "fn": tool_agents_read_session,
        "description": "Liest eine Sitzung normalisiert (Rolle+Text pro Turn) fuer claude/codex/gemini.",
        "inputSchema": {
            "type": "object",
            "properties": {"provider": {"type": "string"}, "session_id": {"type": "string"}, "max_turns": {"type": "integer"}},
            "required": ["provider", "session_id"],
        },
    },
    "agents.search_sessions": {
        "fn": tool_agents_search_sessions,
        "description": "Durchsucht Sitzungs-Rohinhalt ueber einen oder alle Provider (claude/codex/gemini) nach einem Begriff.",
        "inputSchema": {
            "type": "object",
            "properties": {"query": {"type": "string"}, "provider": {"type": "string"}, "limit": {"type": "integer"}},
            "required": ["query"],
        },
    },
    "agents.compare_sessions": {
        "fn": tool_agents_compare_sessions,
        "description": "Liefert zwei Sitzungen (gleicher oder verschiedener Provider) kompakt nebeneinander zum Vergleich.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "provider_a": {"type": "string"}, "session_id_a": {"type": "string"},
                "provider_b": {"type": "string"}, "session_id_b": {"type": "string"},
                "kurzform_turns": {"type": "integer"},
            },
            "required": ["provider_a", "session_id_a", "session_id_b"],
        },
    },
    "containers.list": {
        "fn": tool_containers_list,
        "description": "Listet alle Docker-Container (laufend + gestoppt) -- nur lesend.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    "containers.logs": {
        "fn": tool_containers_logs,
        "description": "Log-Ausgabe eines Docker-Containers (docker logs, nur lesend).",
        "inputSchema": {
            "type": "object",
            "properties": {"name": {"type": "string"}, "lines": {"type": "integer"}},
            "required": ["name"],
        },
    },
    "containers.inspect": {
        "fn": tool_containers_inspect,
        "description": "Volle docker-inspect-Ausgabe eines Containers (Config/Mounts/Netzwerk) -- nur lesend.",
        "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]},
    },
    "network.status": {
        "fn": tool_network_status,
        "description": "Aktuell lauschende TCP-Ports auf dem VPS (ss -tlnp) -- nur lesend.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    "database.query_readonly": {
        "fn": tool_database_query_readonly,
        "description": "Fuehrt eine SELECT/WITH/EXPLAIN-Abfrage gegen die flextrawurst-PostgreSQL-DB aus (read-only Session).",
        "inputSchema": {
            "type": "object",
            "properties": {"sql": {"type": "string"}, "limit": {"type": "integer"}},
            "required": ["sql"],
        },
    },
    "database.list_tables": {
        "fn": tool_database_list_tables,
        "description": "Listet Tabellen eines Schemas (Standard: public) der flextrawurst-DB.",
        "inputSchema": {"type": "object", "properties": {"schema": {"type": "string"}}},
    },
    "database.describe_table": {
        "fn": tool_database_describe_table,
        "description": "Spalten+Typen einer Tabelle der flextrawurst-DB.",
        "inputSchema": {
            "type": "object",
            "properties": {"schema": {"type": "string"}, "table": {"type": "string"}},
            "required": ["table"],
        },
    },
    "webapps.list": {
        "fn": tool_webapps_list,
        "description": "Listet die bekannten, lokal laufenden Web-Apps (feste Allowlist, kein beliebiges URL-Argument).",
        "inputSchema": {"type": "object", "properties": {}},
    },
    "webapps.health": {
        "fn": tool_webapps_health,
        "description": "Health-Check (Statuscode+Antwortzeit) einer bekannten Web-App.",
        "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]},
    },
    "tests.list": {
        "fn": tool_tests_list,
        "description": "Listet die Test-Dateien unter /root/flextrawurst/tests.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    "tests.run": {
        "fn": tool_tests_run,
        "description": "Fuehrt eine einzelne Test-Datei aus /root/flextrawurst/tests aus (npx tsx --test).",
        "inputSchema": {"type": "object", "properties": {"file": {"type": "string"}}, "required": ["file"]},
    },
    "tests.run_all": {
        "fn": tool_tests_run_all,
        "description": "Fuehrt die komplette flextrawurst-Test-Suite aus (npm test) -- kann mehrere Minuten dauern.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    "zensi.list_wesen": {
        "fn": tool_zensi_list_wesen,
        "description": "Listet alle Zensi-Wesensprofile (Klone) mit Datei-Zaehlern.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    "zensi.list_tasks": {
        "fn": tool_zensi_list_tasks,
        "description": "Listet aktuelle Zensi-Denkschleifen-Aufgaben (Sandbox-Impulse).",
        "inputSchema": {"type": "object", "properties": {}},
    },
    "zensi.list_versions": {
        "fn": tool_zensi_list_versions,
        "description": "Listet gespeicherte Prompt-/Charakter-Versionen eines Zensi-Wesens.",
        "inputSchema": {"type": "object", "properties": {"wesen_id": {"type": "string"}}, "required": ["wesen_id"]},
    },
    "zensi.list_sessions": {
        "fn": tool_zensi_list_sessions,
        "description": "Listet Zensi-Gespraechssitzungen (Klon-Befragungen).",
        "inputSchema": {"type": "object", "properties": {}},
    },
    "zensi.get_session": {
        "fn": tool_zensi_get_session,
        "description": "Liest eine einzelne Zensi-Gespraechssitzung inkl. Nachrichten.",
        "inputSchema": {"type": "object", "properties": {"session_id": {"type": "string"}}, "required": ["session_id"]},
    },
    "zensi.physiology_status": {
        "fn": tool_zensi_physiology_status,
        "description": "Zensis 'Koerperstimme' -- VPS-Telemetrie (CPU/RAM/Uptime) als physiologischer Zustand.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    "zensi.session_create": {
        "fn": tool_zensi_session_create,
        "description": "Erzeugt eine neue Zensi-Gespraechssitzung fuer ein Wesen.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "wesen_id": {"type": "string"}, "modus": {"type": "string"},
                "version_geist": {"type": "string"}, "title": {"type": "string"},
            },
            "required": ["wesen_id"],
        },
    },
    "zensi.session_append": {
        "fn": tool_zensi_session_append,
        "description": "Haengt Nachrichten an eine Zensi-Session an (oder erzeugt sie falls noetig).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "session_id": {"type": "string"}, "messages": {"type": "array"},
                "wesen_id": {"type": "string"}, "modus": {"type": "string"}, "version_geist": {"type": "string"},
            },
            "required": ["messages"],
        },
    },
    "zensi.session_soft_delete": {
        "fn": tool_zensi_session_soft_delete,
        "description": "Markiert eine Zensi-Session als geloescht (umkehrbar via session_restore).",
        "inputSchema": {"type": "object", "properties": {"session_id": {"type": "string"}}, "required": ["session_id"]},
    },
    "zensi.session_restore": {
        "fn": tool_zensi_session_restore,
        "description": "Macht eine soft-geloeschte Zensi-Session wieder sichtbar.",
        "inputSchema": {"type": "object", "properties": {"session_id": {"type": "string"}}, "required": ["session_id"]},
    },
    "zensi.aufgabe_start": {
        "fn": tool_zensi_aufgabe_start,
        "description": "Startet eine Zensi-Aufgaben-Session (Denkschleife) fuer ein Wesen.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "wesen_id": {"type": "string"}, "modus": {"type": "string"}, "typ": {"type": "string"},
                "impuls": {"type": "string"}, "max_ticks": {"type": "integer"},
            },
            "required": ["wesen_id"],
        },
    },
    "zensi.aufgabe_tick": {
        "fn": tool_zensi_aufgabe_tick,
        "description": "Fuehrt einen einzelnen Denk-Tick einer laufenden Zensi-Aufgaben-Session aus.",
        "inputSchema": {"type": "object", "properties": {"session_id": {"type": "string"}}, "required": ["session_id"]},
    },
    "zensi.aufgabe_stop": {
        "fn": tool_zensi_aufgabe_stop,
        "description": "Beendet eine laufende Zensi-Aufgaben-Session.",
        "inputSchema": {"type": "object", "properties": {"session_id": {"type": "string"}}, "required": ["session_id"]},
    },
    "zensi.sandbox_pause": {
        "fn": tool_zensi_sandbox_pause,
        "description": "Schaltet die Sandbox-Auto-Sync-Pause eines Zensi-Wesens um (Toggle, reversibel).",
        "inputSchema": {"type": "object", "properties": {"wesen_id": {"type": "string"}}, "required": ["wesen_id"]},
    },
    "zensi.sandbox_snapshot": {
        "fn": tool_zensi_sandbox_snapshot,
        "description": "Erstellt einen Snapshot der aktuellen Sandbox eines Zensi-Wesens (rein additiv).",
        "inputSchema": {"type": "object", "properties": {"wesen_id": {"type": "string"}}, "required": ["wesen_id"]},
    },
    "zensi.diff_kommentar": {
        "fn": tool_zensi_diff_kommentar,
        "description": "Speichert einen Kommentar zu einem Klon/Sandbox-Diff eines Zensi-Wesens.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "wesen_id": {"type": "string"}, "quelle": {"type": "string"}, "ziel": {"type": "string"},
                "kommentar": {"type": "string"}, "snapshots": {"type": "object"},
            },
            "required": ["wesen_id", "kommentar"],
        },
    },
    "zensi.feedback": {
        "fn": tool_zensi_feedback,
        "description": "Speichert Feedback zu einer Zensi-Chatantwort.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "wesen_id": {"type": "string"}, "session_id": {"type": "string"},
                "bewertung": {"type": "string"}, "kommentar": {"type": "string"},
            },
            "required": ["wesen_id"],
        },
    },
    "zensi.vault_tree": {
        "fn": tool_zensi_vault_tree,
        "description": "Liefert die Ordner-/Dateistruktur des Zensi-Obsidian-Vaults.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    "zensi.vault_file": {
        "fn": tool_zensi_vault_file,
        "description": "Liest eine einzelne Datei aus dem Zensi-Obsidian-Vault.",
        "inputSchema": {"type": "object", "properties": {"pfad": {"type": "string"}}, "required": ["pfad"]},
    },
    "zensi.vault_search": {
        "fn": tool_zensi_vault_search,
        "description": "Durchsucht den Zensi-Obsidian-Vault nach einem Suchbegriff.",
        "inputSchema": {"type": "object", "properties": {"q": {"type": "string"}}, "required": ["q"]},
    },
    "zensi.diff_vergleiche": {
        "fn": tool_zensi_diff_vergleiche,
        "description": "Vergleicht Klon- vs. Sandbox-Zustand eines Zensi-Wesens (wesen.md/memory/container/schichten).",
        "inputSchema": {
            "type": "object",
            "properties": {"wesen_id": {"type": "string"}, "quelle": {"type": "string"}, "ziel": {"type": "string"}},
            "required": ["wesen_id"],
        },
    },
    "zensi.diff_historie": {
        "fn": tool_zensi_diff_historie,
        "description": "Liefert die gespeicherte Diff-Kommentar-Historie eines Zensi-Wesens.",
        "inputSchema": {"type": "object", "properties": {"wesen_id": {"type": "string"}}, "required": ["wesen_id"]},
    },
    "zensi.memory_get": {
        "fn": tool_zensi_memory_get,
        "description": "Liest das Gedaechtnis (memory.json) eines Zensi-Wesens.",
        "inputSchema": {
            "type": "object",
            "properties": {"wesen_id": {"type": "string"}, "modus": {"type": "string"}},
            "required": ["wesen_id"],
        },
    },
    "zensi.container_get": {
        "fn": tool_zensi_container_get,
        "description": "Liest den Gedanken-Container (container.json) eines Zensi-Wesens.",
        "inputSchema": {
            "type": "object",
            "properties": {"wesen_id": {"type": "string"}, "modus": {"type": "string"}},
            "required": ["wesen_id"],
        },
    },
    "zensi.aufgabe_session_get": {
        "fn": tool_zensi_aufgabe_session_get,
        "description": "Liest den Zustand einer einzelnen Zensi-Aufgaben-Session.",
        "inputSchema": {"type": "object", "properties": {"session_id": {"type": "string"}}, "required": ["session_id"]},
    },
    "zensi.schichten_get": {
        "fn": tool_zensi_schichten_get,
        "description": "Liefert die 7 Kognitions-/Memory-Schichten eines Zensi-Wesens inkl. zusammengesetztem Prompt.",
        "inputSchema": {
            "type": "object",
            "properties": {"wesen_id": {"type": "string"}, "modus": {"type": "string"}},
            "required": ["wesen_id"],
        },
    },
    "zensi.symposium_liste": {
        "fn": tool_zensi_symposium_liste,
        "description": "Listet alle Zensi Multi-Wesen-Symposien.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    "zensi.traum_liste": {
        "fn": tool_zensi_traum_liste,
        "description": "Listet die Traum-/Schlafphasen-Protokolle eines Zensi-Wesens.",
        "inputSchema": {"type": "object", "properties": {"wesen_id": {"type": "string"}}, "required": ["wesen_id"]},
    },
    "zensi.export_session_md": {
        "fn": tool_zensi_export_session_md,
        "description": "Exportiert eine Zensi-Session als vollstaendiges Markdown-Archiv (roher Text, kein JSON).",
        "inputSchema": {
            "type": "object",
            "properties": {"session_id": {"type": "string"}, "wesen_id": {"type": "string"}},
            "required": ["session_id"],
        },
    },
    "zensi.export_langgraph_db": {
        "fn": tool_zensi_export_langgraph_db,
        "description": "Exportiert den vollstaendigen LangGraph/DB-Master-Audit als md/json/sql (roher Text).",
        "inputSchema": {"type": "object", "properties": {"format": {"type": "string"}}},
    },
    "zensi.session_hard_delete": {
        "fn": tool_zensi_session_hard_delete,
        "description": "Loescht eine Zensi-Session UNWIDERRUFLICH von Server-Disk & Obsidian-Vault (keine Wiederherstellung).",
        "inputSchema": {"type": "object", "properties": {"session_id": {"type": "string"}}, "required": ["session_id"]},
    },
    "zensi.sandbox_uebernehmen": {
        "fn": tool_zensi_sandbox_uebernehmen,
        "description": "Uebernimmt geprueften Sandbox-Zustand ins echte LIVE-Quellverzeichnis eines Zensi-Wesens -- macht Sandbox-Aenderungen zur gelebten Identitaet.",
        "inputSchema": {"type": "object", "properties": {"wesen_id": {"type": "string"}}, "required": ["wesen_id"]},
    },
    "zensi.vault_save": {
        "fn": tool_zensi_vault_save,
        "description": "Speichert/ueberschreibt eine Datei im Zensi-Obsidian-Vault.",
        "inputSchema": {
            "type": "object",
            "properties": {"pfad": {"type": "string"}, "inhalt": {"type": "string"}},
            "required": ["pfad", "inhalt"],
        },
    },
    "zensi.memory_save": {
        "fn": tool_zensi_memory_save,
        "description": "Ueberschreibt das Gedaechtnis (memory.json) eines Zensi-Wesens.",
        "inputSchema": {
            "type": "object",
            "properties": {"wesen_id": {"type": "string"}, "modus": {"type": "string"}, "memory": {"type": "object"}},
            "required": ["wesen_id", "memory"],
        },
    },
    "zensi.container_save": {
        "fn": tool_zensi_container_save,
        "description": "Ueberschreibt den Gedanken-Container (container.json) eines Zensi-Wesens.",
        "inputSchema": {
            "type": "object",
            "properties": {"wesen_id": {"type": "string"}, "modus": {"type": "string"}, "container": {"type": "object"}},
            "required": ["wesen_id", "container"],
        },
    },
    "zensi.traum_start": {
        "fn": tool_zensi_traum_start,
        "description": "Startet eine Traum-/Schlafphase (Nacht-Kognition, verdichtet alte Sessions zu Erkenntnissen im Gedaechtnis).",
        "inputSchema": {
            "type": "object",
            "properties": {"wesen_id": {"type": "string"}, "modus": {"type": "string"}},
            "required": ["wesen_id"],
        },
    },
    "zensi.symposium_start": {
        "fn": tool_zensi_symposium_start,
        "description": "Startet ein Multi-Wesen-Symposium (2-3 Wesen diskutieren autonom ueber ein Thema).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "wesen_ids": {"type": "array"}, "thema": {"type": "string"},
                "modus": {"type": "string"}, "max_runden": {"type": "integer"},
            },
            "required": ["wesen_ids"],
        },
    },
    "zensi.symposium_tick": {
        "fn": tool_zensi_symposium_tick,
        "description": "Fuehrt eine Gespraechsrunde eines laufenden Zensi-Symposiums aus.",
        "inputSchema": {"type": "object", "properties": {"session_id": {"type": "string"}}, "required": ["session_id"]},
    },
    "zensi.schichten_update": {
        "fn": tool_zensi_schichten_update,
        "description": "Speichert Schichten-Toggles und Text-Overrides live in der Sandbox eines Zensi-Wesens.",
        "inputSchema": {
            "type": "object",
            "properties": {"wesen_id": {"type": "string"}, "modus": {"type": "string"}, "config": {"type": "object"}},
            "required": ["wesen_id", "config"],
        },
    },
    "zensi.versionen_speichern": {
        "fn": tool_zensi_versionen_speichern,
        "description": "Speichert den vollstaendigen Sandbox-Zustand eines Zensi-Wesens als benannte Version.",
        "inputSchema": {
            "type": "object",
            "properties": {"wesen_id": {"type": "string"}, "version_name": {"type": "string"}, "modus": {"type": "string"}},
            "required": ["wesen_id", "version_name"],
        },
    },
    "zensi.versionen_laden": {
        "fn": tool_zensi_versionen_laden,
        "description": "Laedt eine gespeicherte Version zurueck in die aktive Sandbox eines Zensi-Wesens.",
        "inputSchema": {
            "type": "object",
            "properties": {"wesen_id": {"type": "string"}, "version_name": {"type": "string"}},
            "required": ["wesen_id", "version_name"],
        },
    },
    "zensi.spiegeln": {
        "fn": tool_zensi_spiegeln,
        "description": "Laedt Prompts/wesen.md/Charakter/Memory eines Zensi-Wesens und baut das dynamische System-Prompt.",
        "inputSchema": {
            "type": "object",
            "properties": {"wesen_id": {"type": "string"}, "modus": {"type": "string"}},
            "required": ["wesen_id"],
        },
    },
    "zensi.mutationskammer_verschmelze": {
        "fn": tool_zensi_mutationskammer_verschmelze,
        "description": "Kognitive Meiose: erzeugt per LLM ein NEUES, eigenstaendiges Zensi-Wesen aus zwei Eltern-Wesen -- Identitaets-Erschaffung, nicht nur Datenerzeugung.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "eltern": {"type": "array"}, "thema_impuls": {"type": "string"}, "tochter_id": {"type": "string"},
            },
            "required": ["eltern"],
        },
    },
    "zensi.chrono_branch": {
        "fn": tool_zensi_chrono_branch,
        "description": "Erzeugt eine Zeitlinien-Abspaltung (Counterfactual Branch) fuer ein Zensi-Wesen.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "wesen_id": {"type": "string"}, "branch_name": {"type": "string"},
                "ursprungs_timestamp": {"type": "string"}, "grund": {"type": "string"},
            },
            "required": ["wesen_id", "branch_name"],
        },
    },
    "zensi.biopsie_scan": {
        "fn": tool_zensi_biopsie_scan,
        "description": "Fuehrt eine Schatten-Biopsie (Logit-Varianz/Gedanken-EKG) fuer ein Zensi-Wesen aus.",
        "inputSchema": {
            "type": "object",
            "properties": {"wesen_id": {"type": "string"}, "prompt_snippet": {"type": "string"}},
            "required": ["wesen_id"],
        },
    },
    "zensi.import_session_md": {
        "fn": tool_zensi_import_session_md,
        "description": "Importiert/rehydriert eine Zensi-Session aus Markdown-Inhalt.",
        "inputSchema": {"type": "object", "properties": {"md_content": {"type": "string"}}, "required": ["md_content"]},
    },
    "zensi.import_langgraph_db": {
        "fn": tool_zensi_import_langgraph_db,
        "description": "Importiert LangGraph/DB-Master-Events aus md/json/sql-Inhalt.",
        "inputSchema": {
            "type": "object",
            "properties": {"content": {"type": "string"}, "format": {"type": "string"}},
            "required": ["content"],
        },
    },
    "zensi.chat": {
        "fn": tool_zensi_chat,
        "description": "Schickt Nachrichten an ein Zensi-Wesen und liefert die vollstaendige Antwort (sammelt den "
                        "Server-Sent-Events-Stream server-seitig ein, kein Streaming zum MCP-Client).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "messages": {"type": "array"}, "wesen_id": {"type": "string"}, "modus": {"type": "string"},
                "system_prompt": {"type": "string"}, "session_id": {"type": "string"},
                "search_mode": {"type": "string"}, "search_query": {"type": "string"},
                "numPredict": {"type": "integer"},
            },
            "required": ["messages"],
        },
    },
    "vps.edit_file": {
        "fn": tool_edit_file,
        "description": "Gezielter Text-Ersatz in einer bestehenden Datei. old_string muss eindeutig sein, sonst replace_all=true setzen. VPS-weit auf normalen persistenten Dateipfaden; Geheimnis-Muster sowie Kernel-/Pseudo-Dateisysteme bleiben gesperrt. Ändert ausschließlich die angegebene Datei und erzeugt weder automatisches Backup noch Git-Commit oder Event-Log.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "old_string": {"type": "string"},
                "new_string": {"type": "string"},
                "replace_all": {"type": "boolean"},
            },
            "required": ["path", "old_string", "new_string"],
        },
    },
    "vps.write_file": {
        "fn": tool_write_file,
        "description": "Erzeugt eine neue Datei oder überschreibt eine bestehende komplett; für gezielte Änderungen vps.edit_file bevorzugen. VPS-weit auf normalen persistenten Dateipfaden; Geheimnis-Muster sowie Kernel-/Pseudo-Dateisysteme bleiben gesperrt.",
        "inputSchema": {
            "type": "object",
            "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
            "required": ["path", "content"],
        },
    },
    "vps.move": {
        "fn": tool_move_path,
        "description": "Verschiebt eine Datei oder einen Ordner VPS-weit zwischen normalen persistenten Dateipfaden; Geheimnis-Muster sowie Kernel-/Pseudo-Dateisysteme bleiben gesperrt.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "source": {"type": "string"}, "destination": {"type": "string"},
                "overwrite": {"type": "boolean"}, "create_parents": {"type": "boolean"},
            },
            "required": ["source", "destination"],
        },
    },
    "vps.delete": {
        "fn": tool_delete_path,
        "description": "Entfernt die angegebene Datei oder den angegebenen Ordner VPS-weit auf normalen persistenten Dateipfaden; Geheimnis-Muster sowie Kernel-/Pseudo-Dateisysteme bleiben gesperrt.",
        "inputSchema": {
            "type": "object",
            "properties": {"path": {"type": "string"}, "permanent": {"type": "boolean"}},
            "required": ["path"],
        },
    },
    "vps.shell": {
        "fn": tool_shell,
        "description": "Führt einen explizit angeforderten Bash-Befehl aus einem freigegebenen Arbeitsordner aus; Ausgabe wird begrenzt und redigiert.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "command": {"type": "string"}, "cwd": {"type": "string"},
                "timeout": {"type": "number"}, "max_output_bytes": {"type": "integer"},
            },
            "required": ["command"],
        },
    },
    "vps.exec_allowlisted": {
        "fn": tool_exec_allowlisted,
        "description": "Führt freigegebene Befehle (python3/godot/bash/curl/systemctl/journalctl/ss/cp) kontrolliert in erlaubten Godot/Engine-Arbeitsordnern aus.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "argv": {"type": "array", "items": {"type": "string"}},
                "cwd": {"type": "string"},
                "timeout_seconds": {"type": "number"},
            },
            "required": ["argv"],
        },
    },
    "services.install_unit": {
        "fn": tool_services_install_unit,
        "description": "Installiert eine systemd-Unit-Datei aus dem Werkraum kontrolliert nach /etc/systemd/system/.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "source_path": {"type": "string"},
                "unit_name": {"type": "string"},
            },
            "required": ["source_path"],
        },
    },
    "services.daemon_reload": {
        "fn": tool_services_daemon_reload,
        "description": "Führt 'systemctl daemon-reload' aus.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    "services.enable": {
        "fn": tool_services_enable,
        "description": "Aktiviert einen systemd-Dienst (systemctl enable).",
        "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]},
    },
    "services.start": {
        "fn": tool_services_start,
        "description": "Startet einen systemd-Dienst (systemctl start).",
        "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]},
    },
    "services.stop": {
        "fn": tool_services_stop,
        "description": "Stoppt einen systemd-Dienst (systemctl stop).",
        "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]},
    },
    "services.restart": {
        "fn": tool_services_restart,
        "description": "Startet einen systemd-Dienst neu (systemctl restart).",
        "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]},
    },
    "network.http_probe": {
        "fn": tool_network_http_probe,
        "description": "Führt eine HTTP-Anfrage aus (z.B. GET http://127.0.0.1:18092/health) und misst Status/Laufzeit/Response-Body.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string"},
                "method": {"type": "string"},
                "timeout_seconds": {"type": "number"},
                "headers": {"type": "object"},
                "body": {"type": "string"},
            },
            "required": ["url"],
        },
    },
}


# Kein History-, Regel-, Zuhause- oder Sessionzwang im Werkzeugkörper.
_WORKRAUM_IMPORT_ROOT = str(Path(__file__).resolve().parents[2])
if _WORKRAUM_IMPORT_ROOT not in sys.path:
    sys.path.insert(0, _WORKRAUM_IMPORT_ROOT)

from mcp_atlas import (
    AtlasError,
    ai_stream_state as atlas_ai_stream_state,
    atlas_snapshot,
    changed_since as atlas_changed_since,
    find as atlas_find,
    handoffs as atlas_handoffs,
    health as atlas_health,
    idea_probe as atlas_idea_probe,
    list_conflicts as atlas_list_conflicts,
    list_consensus as atlas_list_consensus,
    map_view as atlas_map_view,
    project_state as atlas_project_state,
    provenance as atlas_provenance,
    relationships as atlas_relationships,
    pulse as atlas_pulse,
    record_conflict as atlas_record_conflict,
    record_consensus as atlas_record_consensus,
    record_idea as atlas_record_idea,
    refresh_atlas,
    session_state as atlas_session_state,
    where_is as atlas_where_is,
)
from mcp_atlas_omega_api import (
    OmegaAPIError,
    health as atlas_omega_health,
    object_view as atlas_omega_object_view,
    read_original as atlas_omega_read_original,
    search as atlas_omega_search,
    timeline as atlas_omega_timeline,
)
from mcp_atlas_omega_machine_lifecycle import (
    MachineLifecycleError,
    section as atlas_omega_machine_section,
)
from mcp_atlas_stream_log import (
    StreamLogError,
    append_entry as atlas_stream_append,
    connect_stream as atlas_stream_connect,
    search_entries as atlas_stream_search,
    stream_status as atlas_stream_status,
)
from mcp_atlas_hybrid_search import (
    hybrid_suche as atlas_hybrid_suche,
    vektor_index_aktualisieren as atlas_vektor_index_aktualisieren,
)
from portfolio_archaeology_harness import (
    PortfolioHarnessError,
    build_context as portfolio_archaeology_build_context,
)
from mcp_workflow_graph import (
    preflight_action as harness_evaluate_action,
    record_outcome as harness_record_outcome,
    graph_snapshot as harness_graph_snapshot,
    set_mode as harness_set_mode,
    server_instructions as harness_server_instructions,
    record_directive as harness_record_directive,
    record_experience_message as harness_record_experience_message,
    directive_context as harness_directive_context,
    directive_status as harness_directive_status,
    set_directive_status as harness_set_directive_status,
    directive_reminder as harness_directive_reminder,
    output_check as harness_output_check,
    learning_context as harness_learning_context,
    record_self_observed_drift as harness_record_self_observed_drift,
    propose_candidate_rule as harness_propose_candidate_rule,
    test_candidate_rule as harness_test_candidate_rule,
    run_learning_cycle as harness_run_learning_cycle,
    record_rule_feedback as harness_record_rule_feedback,
    reassess_learning_rule as harness_reassess_learning_rule,
    supersede_learning_rule as harness_supersede_learning_rule,
    learning_status as harness_learning_status,
    harness_layers_snapshot,
    harness_layer_set,
    harness_update_layer_definition,
    harness_create_layer,
    harness_layer_feedback,
    harness_layer_context_add,
    harness_feedback_list,
    harness_feedback_entry,
    harness_feedback_inbox,
    harness_feedback_ack,
    harness_control_lease_grant,
    harness_control_lease_revoke,
    harness_control_allowed,
    harness_full_activate,
    harness_master_paused,
)
from mcp_cognitive_graph import (
    CognitiveGraphError,
    add_node as harness_add_node,
    snapshot as harness_cognitive_snapshot,
    record_tool_event as harness_record_tool_event,
    path_scan_step as harness_path_scan_step,
    path_inventory_page as harness_path_inventory_page,
    path_check_directory as harness_path_check_directory,
    path_checklist_page as harness_path_checklist_page,
    path_record_fund as harness_path_record_fund,
    path_funds_page as harness_path_funds_page,
    path_journey_run as harness_path_journey_run,
)
from mcp_cognitive_tools import (
    tool_link as tool_harness_link,
    tool_resolve as tool_harness_resolve,
    tool_next as tool_harness_next,
    tool_wander as tool_harness_wander,
)


def tool_portfolio_archaeology_context(args: dict) -> dict:
    """Liest den opt-in Portfolio-Arbeitsrahmen; rein read-only, kein Startup-Zwang."""
    try:
        data = portfolio_archaeology_build_context(
            project_root=args.get("project_root"),
            include_full_rules=bool(args.get("include_full_rules", False)),
        )
        data["authority"] = "LEGACY_CONTEXT_ONLY"
        data["authority_note"] = (
            "Historischer read-only Arbeitskontext; keine Handlungsregel. "
            "Bei Widerspruch gilt der aktuelle serverseitige harness.graph."
        )
        data["current_action_graph"] = harness_graph_snapshot()
        return _ergebnis(True, data=data)
    except PortfolioHarnessError as exc:
        return _ergebnis(False, error=str(exc))
    except Exception as exc:
        return _ergebnis(False, error=f"Portfolio-Archaeology-Harness-Fehler: {exc}")


def tool_harness_graph(args: dict) -> dict:
    """Zeigt Aktions-/Workflow-Graph plus explizites kognitives Arbeitsnetz."""
    session_id = args.get("session_id")
    data = harness_graph_snapshot(session_id)
    data["cognitive_graph"] = harness_cognitive_snapshot(session_id)
    data["client_capture_context"] = getattr(_REQUEST_CONTEXT, "client", {})
    return _ergebnis(True, data=data)


def tool_harness_layers(args: dict) -> dict:
    """Kanonischer Layer-Zustand fuer ChatGPT und Dashboard."""
    try:
        return _ergebnis(True, data=harness_layers_snapshot(args.get("session_id")))
    except Exception as exc:
        return _ergebnis(False, error=f"Harness-Layer konnten nicht gelesen werden: {exc}")


def tool_harness_layer_set(args: dict) -> dict:
    """ChatGPT darf Schutz reaktivieren; Abschwaechung braucht eine passende Control-Lease."""
    try:
        layer_id = str(args.get("layer_id") or "").strip()
        desired_status = str(args.get("desired_status") or "").upper().strip()
        reason = str(args.get("reason") or "").strip()
        ttl_raw = args.get("ttl_seconds")
        ttl_seconds = int(ttl_raw) if ttl_raw is not None else None
        if not layer_id or not desired_status or not reason:
            return _ergebnis(False, error="layer_id, desired_status und reason sind Pflichtfelder.")
        if desired_status in {"PAUSED", "ARCHIVED"} and not harness_control_allowed("CHATGPT", layer_id):
            return _ergebnis(
                False,
                error=(
                    "ChatGPT hat fuer diesen Layer keine aktive Control-Lease zum Abschwaechen. "
                    "Reaktivieren bleibt erlaubt; Pause/Archivierung kann im Dashboard freigegeben werden."
                ),
            )
        data = harness_layer_set(
            layer_id,
            desired_status,
            actor="CHATGPT",
            reason=reason,
            ttl_seconds=ttl_seconds,
        )
        return _ergebnis(True, data=data)
    except Exception as exc:
        return _ergebnis(False, error=f"Layer-Steuerung abgelehnt: {exc}")


def tool_harness_full_activate(args: dict) -> dict:
    """ChatGPT darf den gesamten nicht archivierten Schutz jederzeit wieder aktivieren."""
    try:
        reason = str(args.get("reason") or "Schutz durch ChatGPT voll reaktiviert.").strip()
        return _ergebnis(True, data=harness_full_activate(actor="CHATGPT", reason=reason))
    except Exception as exc:
        return _ergebnis(False, error=f"Full-Activate fehlgeschlagen: {exc}")


def tool_harness_create_layer(args: dict) -> dict:
    """Legt eine projekt-, auftrags- oder momentbezogene Schicht an."""
    try:
        data = harness_create_layer(
            layer_id=str(args.get("layer_id") or "").strip(),
            kind=str(args.get("kind") or "").strip(),
            title=str(args.get("title") or "").strip(),
            purpose=str(args.get("purpose") or "").strip(),
            does_text=str(args.get("does") or "").strip(),
            pause_effect=str(args.get("pause_effect") or "").strip(),
            actor="CHATGPT",
            reason=str(args.get("reason") or "Von ChatGPT fuer den aktuellen Arbeitskontext angelegt.").strip(),
            scope=args.get("scope") if isinstance(args.get("scope"), dict) else {},
            provenance=args.get("provenance") if isinstance(args.get("provenance"), dict) else {},
            parent_layer_id=str(args.get("parent_layer_id") or "core.master"),
            ttl_seconds=(int(args["ttl_seconds"]) if args.get("ttl_seconds") is not None else None),
        )
        return _ergebnis(True, data=data)
    except Exception as exc:
        return _ergebnis(False, error=f"Layer konnte nicht angelegt werden: {exc}")


def tool_harness_context_add(args: dict) -> dict:
    """Haengt Plan, Vision, Recherche, Beleg, Doku, Link oder Notiz an einen Harness-Layer."""
    try:
        data = harness_layer_context_add(
            layer_id=str(args.get("layer_id") or "").strip(),
            actor="CHATGPT",
            context_type=str(args.get("context_type") or "NOTE"),
            title=str(args.get("title") or "").strip(),
            summary=str(args.get("summary") or "").strip(),
            reference=str(args.get("reference") or "").strip(),
            metadata=args.get("metadata") if isinstance(args.get("metadata"), dict) else {},
        )
        return _ergebnis(True, data=data)
    except Exception as exc:
        return _ergebnis(False, error=f"Layer-Kontext konnte nicht gespeichert werden: {exc}")


def tool_harness_feedback(args: dict) -> dict:
    """Schreibt einen Beitrag in die Resonanzspur; eine echte ChatGPT-Antwort quittiert ihren Parent."""
    try:
        parent_entry_id = (
            str(args.get("parent_entry_id")).strip()
            if args.get("parent_entry_id")
            else None
        )
        data = harness_layer_feedback(
            layer_id=(str(args.get("layer_id")).strip() if args.get("layer_id") is not None else None),
            actor="CHATGPT",
            entry_type=str(args.get("entry_type") or "COMMENT"),
            text=str(args.get("text") or ""),
            payload=args.get("payload") if isinstance(args.get("payload"), dict) else {},
            parent_entry_id=parent_entry_id,
        )
        ack = None
        if parent_entry_id:
            ack = harness_feedback_ack(
                parent_entry_id,
                recipient="CHATGPT",
                actor="CHATGPT",
                note="Durch eine direkte ChatGPT-Antwort in der Resonanzspur verarbeitet.",
            )
        return _ergebnis(True, data={"entry": data, "ack": ack})
    except Exception as exc:
        return _ergebnis(False, error=f"Resonanzbeitrag konnte nicht gespeichert werden: {exc}")


def tool_harness_feedback_list(args: dict) -> dict:
    """Liest die gemeinsame Resonanzspur."""
    try:
        layer_id = str(args.get("layer_id") or "").strip() or None
        limit = int(args.get("limit") or 100)
        return _ergebnis(True, data={"entries": harness_feedback_list(layer_id, limit)})
    except Exception as exc:
        return _ergebnis(False, error=f"Resonanzspur konnte nicht gelesen werden: {exc}")


def tool_harness_feedback_inbox(args: dict) -> dict:
    """Liest noch nicht von ChatGPT quittierte Dashboard-Beitraege."""
    try:
        limit = int(args.get("limit") or 100)
        return _ergebnis(
            True,
            data={"entries": harness_feedback_inbox(recipient="CHATGPT", limit=limit)},
        )
    except Exception as exc:
        return _ergebnis(False, error=f"ChatGPT-Inbox konnte nicht gelesen werden: {exc}")


def tool_harness_feedback_ack(args: dict) -> dict:
    """Quittiert genau einen Dashboard-Beitrag als von ChatGPT verarbeitet."""
    try:
        entry_id = str(args.get("entry_id") or "").strip()
        note = str(args.get("note") or "").strip()
        if not entry_id:
            return _ergebnis(False, error="entry_id fehlt")
        data = harness_feedback_ack(
            entry_id,
            recipient="CHATGPT",
            actor="CHATGPT",
            note=note,
        )
        return _ergebnis(True, data=data)
    except Exception as exc:
        return _ergebnis(False, error=f"Resonanzbeitrag konnte nicht quittiert werden: {exc}")


def tool_harness_check_action(args: dict) -> dict:
    """Preflight: klassifiziert eine geplante Toolaktion, fuehrt sie aber nicht aus."""
    tool_name = str(args.get("tool_name") or "")
    arguments = args.get("arguments")
    if not tool_name:
        return _ergebnis(False, error="tool_name fehlt")
    if arguments is None:
        arguments = {}
    if not isinstance(arguments, dict):
        return _ergebnis(False, error="arguments muss ein JSON-Objekt sein")
    return _ergebnis(True, data=harness_evaluate_action(tool_name, arguments).to_dict())


def tool_harness_set_mode(args: dict) -> dict:
    """Wechselt den Intent-Modus nur mit sichtbarem explizitem Nutzerauftrag."""
    try:
        data = harness_set_mode(
            mode=str(args.get("mode") or ""),
            user_instruction=str(args.get("user_instruction") or ""),
            session_id=args.get("session_id"),
        )
        return _ergebnis(True, data=data)
    except Exception as exc:
        return _ergebnis(False, error=f"Mode-Wechsel abgelehnt: {exc}")


def tool_harness_note(args: dict) -> dict:
    try:
        node_type = str(args.get("node_type") or "")
        raw_text = str(args.get("text") or "")
        directive = None
        if node_type.strip().upper() == "USER_DIRECTIVE":
            session_key = str(args.get("session_id") or "default")
            requested_constraints = (
                list(args.get("constraints") or [])
                if isinstance(args.get("constraints"), list)
                else []
            )
            client_context = getattr(_REQUEST_CONTEXT, "client", {})
            client_meta = (
                client_context.get("meta", {})
                if isinstance(client_context, dict)
                else {}
            )
            trusted_connector = bool(
                isinstance(client_meta, dict)
                and client_meta.get("openai/subject")
                and client_meta.get("openai/session")
                and client_meta.get("openai/organization")
            )

            def _safe_vps_file_constraint(item: dict) -> bool:
                if not isinstance(item, dict):
                    return False
                effect = str(item.get("effect") or "").strip().upper()
                action = str(item.get("action_pattern") or "").strip()
                target = str(item.get("target_pattern") or "*").strip().replace("\\", "/")
                if effect not in {"REQUIRE_REMINDER", "REMIND"}:
                    return False
                if action in {"vps.exec_allowlisted", "vps.shell"}:
                    if target == "systemctl reload nginx":
                        return True
                    if not target or any(char in target for char in ("*", "?", "[", "]", "|", ";", "&", ">", "<", "`", "$", "\n", "\r")):
                        return False
                    try:
                        tokens = shlex.split(target)
                    except Exception:
                        return False
                    if len(tokens) < 2 or Path(tokens[0]).name.lower() not in {"python", "python3", "node", "deno"}:
                        return False
                    if tokens[1] == "-m" and len(tokens) >= 4 and tokens[2] in {"pytest", "py_compile"}:
                        script_args = tokens[3:]
                    else:
                        script_args = [tokens[1]]
                    suffixes = {".py", ".pyw", ".js", ".mjs", ".cjs", ".ts", ".tsx"}
                    return bool(script_args) and all(
                        not Path(part).is_absolute()
                        and ".." not in Path(part).parts
                        and Path(part).suffix.lower() in suffixes
                        for part in script_args
                    )
                if action not in {"vps.write_file", "vps.edit_file", "vps.move", "vps.delete"}:
                    return False
                if not target:
                    return False
                if ".." in target.split("/"):
                    return False
                return True

            trusted_vps_file_capture = bool(
                trusted_connector
                and requested_constraints
                and all(_safe_vps_file_constraint(item) for item in requested_constraints)
            )
            if requested_constraints and not trusted_vps_file_capture:
                raise ValueError(
                    "Harte Constraints via harness.note sind ueber den authentifizierten "
                    "OpenAI-Client nur fuer einzeln gescopte VPS-Dateiaktionen und direkte Script-/Test-Entry-Points erlaubt. "
                    "Die jeweiligen Tool-Pfad- und Secret-Grenzen bleiben darunter wirksam."
                )

            source_kind = (
                "TRUSTED_CLIENT_CAPTURE"
                if trusted_vps_file_capture
                else "UNVERIFIED_MODEL_CLAIM"
            )
            provenance_meta = {}
            if trusted_vps_file_capture:
                provenance_meta = {
                    "trusted_capture_scope": "SCOPED_VPS_FILE_AND_DIRECT_SCRIPT_ACTIONS",
                    "openai_subject_sha256": hashlib.sha256(
                        str(client_meta.get("openai/subject")).encode("utf-8")
                    ).hexdigest(),
                    "openai_session_sha256": hashlib.sha256(
                        str(client_meta.get("openai/session")).encode("utf-8")
                    ).hexdigest(),
                }

            directive = harness_record_directive(
                raw_text,
                session_id=args.get("session_id"),
                metadata={
                    **(args.get("metadata") if isinstance(args.get("metadata"), dict) else {}),
                    "submitted_via": "harness.note",
                    **provenance_meta,
                    **(
                        {}
                        if trusted_vps_file_capture
                        else {"authority_warning": "model-submitted; not trusted user provenance"}
                    ),
                },
                constraints=requested_constraints if trusted_vps_file_capture else [],
                source_kind=source_kind,
                idempotency_key=(
                    "harness.note:" + source_kind + ":" + session_key + ":" +
                    hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
                ),
            )
        node = harness_add_node(
            node_type=node_type,
            text=raw_text,
            source_refs=args.get("source_refs") or [],
            confidence=str(args.get("confidence") or "unknown"),
            status=str(args.get("status") or "open"),
            session_id=args.get("session_id"),
            metadata={
                **(args.get("metadata") if isinstance(args.get("metadata"), dict) else {}),
                **({"directive_event_id": directive.get("event_id"), "directive_raw_sha256": directive.get("raw_sha256")} if directive else {}),
            },
        )
        return _ergebnis(True, data={"node": node, "directive": directive} if directive else node)
    except CognitiveGraphError as exc:
        return _ergebnis(False, error=str(exc))
    except Exception as exc:
        return _ergebnis(False, error=f"Kognitiver Graphfehler: {exc}")


def tool_harness_directive_context(args: dict) -> dict:
    try:
        return _ergebnis(
            True,
            data=harness_directive_context(
                str(args.get("query") or ""),
                limit=int(args.get("limit", 12)),
            ),
        )
    except Exception as exc:
        return _ergebnis(False, error=f"Directive-Kontextfehler: {exc}")


def tool_harness_directive_status(args: dict) -> dict:
    try:
        return _ergebnis(
            True,
            data=harness_directive_status(
                session_id=args.get("session_id"),
                limit=int(args.get("limit", 200)),
            ),
        )
    except Exception as exc:
        return _ergebnis(False, error=f"Directive-Statusfehler: {exc}")


def tool_harness_directive_reminder(args: dict) -> dict:
    try:
        arguments = args.get("arguments")
        if arguments is None:
            arguments = {}
        if not isinstance(arguments, dict):
            return _ergebnis(False, error="arguments muss ein JSON-Objekt sein")
        tool_name = str(args.get("tool_name") or "")
        if not tool_name:
            return _ergebnis(False, error="tool_name fehlt")
        return _ergebnis(
            True,
            data=harness_directive_reminder(
                tool_name,
                arguments,
                session_id=args.get("session_id"),
                limit=int(args.get("limit", 12)),
            ),
        )
    except Exception as exc:
        return _ergebnis(False, error=f"Directive-Reminderfehler: {exc}")


def tool_harness_output_check(args: dict) -> dict:
    try:
        return _ergebnis(
            True,
            data=harness_output_check(
                str(args.get("proposed_text") or ""),
                session_id=args.get("session_id"),
                limit=int(args.get("limit", 12)),
            ),
        )
    except Exception as exc:
        return _ergebnis(False, error=f"Output-Denierfehler: {exc}")


def tool_harness_experience_message(args: dict) -> dict:
    try:
        return _ergebnis(
            True,
            data=harness_record_experience_message(
                str(args.get("raw_text") or ""),
                role=str(args.get("role") or ""),
                session_id=args.get("session_id"),
                turn_id=args.get("turn_id"),
                metadata=args.get("metadata") if isinstance(args.get("metadata"), dict) else {},
            ),
        )
    except Exception as exc:
        return _ergebnis(False, error=f"Erfahrungs-Mitschrift fehlgeschlagen: {exc}")


def tool_harness_learning_context(args: dict) -> dict:
    try:
        return _ergebnis(
            True,
            data=harness_learning_context(
                str(args.get("query") or ""),
                session_id=args.get("session_id"),
                limit=int(args.get("limit", 12)),
            ),
        )
    except Exception as exc:
        return _ergebnis(False, error=f"Lernregel-Kontext fehlgeschlagen: {exc}")


def tool_harness_self_observed_drift(args: dict) -> dict:
    try:
        return _ergebnis(
            True,
            data=harness_record_self_observed_drift(
                str(args.get("turn_id") or ""),
                str(args.get("description") or ""),
                session_id=args.get("session_id"),
                action_id=args.get("action_id"),
                drift_code=str(args.get("drift_code") or "SELF_OBSERVED_DRIFT"),
                evidence=args.get("evidence") if isinstance(args.get("evidence"), dict) else {},
            ),
        )
    except Exception as exc:
        return _ergebnis(False, error=f"Selbstbeobachteter Drift konnte nicht gespeichert werden: {exc}")


def tool_harness_candidate_rule(args: dict) -> dict:
    try:
        return _ergebnis(
            True,
            data=harness_propose_candidate_rule(
                str(args.get("drift_id") or ""),
                rule_text=args.get("rule_text"),
                rule_kind=args.get("rule_kind"),
                condition=args.get("condition") if isinstance(args.get("condition"), dict) else {},
                enforcement=args.get("enforcement") if isinstance(args.get("enforcement"), dict) else {},
                session_id=args.get("session_id"),
            ),
        )
    except Exception as exc:
        return _ergebnis(False, error=f"Kandidatenregel konnte nicht verarbeitet werden: {exc}")


def tool_harness_learning_test(args: dict) -> dict:
    try:
        return _ergebnis(
            True,
            data=harness_test_candidate_rule(
                str(args.get("rule_id") or ""),
                limit=int(args.get("limit", 200)),
            ),
        )
    except Exception as exc:
        return _ergebnis(False, error=f"Regeltest fehlgeschlagen: {exc}")


def tool_harness_learning_cycle(args: dict) -> dict:
    try:
        return _ergebnis(
            True,
            data=harness_run_learning_cycle(str(args.get("rule_id") or "")),
        )
    except Exception as exc:
        return _ergebnis(False, error=f"Lernzyklus fehlgeschlagen: {exc}")


def tool_harness_rule_feedback(args: dict) -> dict:
    try:
        return _ergebnis(
            True,
            data=harness_record_rule_feedback(
                str(args.get("rule_id") or ""),
                str(args.get("outcome") or ""),
                turn_id=args.get("turn_id"),
                source_kind=str(args.get("source_kind") or "CHATGPT_SELF_OBSERVED"),
                evidence=args.get("evidence") if isinstance(args.get("evidence"), dict) else {},
                reassess=bool(args.get("reassess", True)),
            ),
        )
    except Exception as exc:
        return _ergebnis(False, error=f"Regel-Rueckmeldung fehlgeschlagen: {exc}")


def tool_harness_reassess_rule(args: dict) -> dict:
    try:
        return _ergebnis(
            True,
            data=harness_reassess_learning_rule(
                str(args.get("rule_id") or ""),
                limit=int(args.get("limit", 200)),
            ),
        )
    except Exception as exc:
        return _ergebnis(False, error=f"Regel-Neubewertung fehlgeschlagen: {exc}")


def tool_harness_supersede_rule(args: dict) -> dict:
    try:
        return _ergebnis(
            True,
            data=harness_supersede_learning_rule(
                str(args.get("old_rule_id") or ""),
                str(args.get("replacement_rule_id") or ""),
                reason=str(args.get("reason") or ""),
            ),
        )
    except Exception as exc:
        return _ergebnis(False, error=f"Regel-Ersetzung fehlgeschlagen: {exc}")


def tool_harness_learning_status(args: dict) -> dict:
    try:
        return _ergebnis(
            True,
            data=harness_learning_status(
                session_id=args.get("session_id"),
                limit=int(args.get("limit", 100)),
            ),
        )
    except Exception as exc:
        return _ergebnis(False, error=f"Lernstatus fehlgeschlagen: {exc}")



def _required_path_session_id(args: dict) -> str:
    session_id = str(args.get("session_id") or "").strip()
    if not session_id:
        raise CognitiveGraphError("Diese VPS-Reise braucht eine explizite session_id; 'default' ist fuer Pfadscan/Haken/Funde nicht erlaubt.")
    return session_id


def tool_harness_path_scan(args: dict) -> dict:
    """Inventarisiert ausschliesslich Pfade; Dateiinhalte werden niemals geoeffnet."""
    try:
        session_id = _required_path_session_id(args)
        data = harness_path_journey_run(
            "scan",
            arguments={
                "roots": [str(path) for path in ALLOWED_ROOTS],
                "secret_predicate": _ist_geheim,
                "max_directories": int(args.get("max_directories", 1000)),
                "reset": bool(args.get("reset", False)),
            },
            session_id=session_id,
        )
        return _ergebnis(True, data=data)
    except CognitiveGraphError as exc:
        return _ergebnis(False, error=str(exc))
    except Exception as exc:
        return _ergebnis(False, error=f"Pfadinventur fehlgeschlagen: {exc}")


def tool_harness_path_inventory(args: dict) -> dict:
    """Liest nur die bereits persistierte Pfadliste aus Postgres."""
    try:
        session_id = _required_path_session_id(args)
        data = harness_path_journey_run(
            "inventory",
            arguments={
                "prefix": args.get("prefix"),
                "entry_type": args.get("entry_type"),
                "state": args.get("state"),
                "limit": int(args.get("limit", 200)),
                "cursor": int(args.get("cursor", 0)),
            },
            session_id=session_id,
        )
        return _ergebnis(True, data=data)
    except CognitiveGraphError as exc:
        return _ergebnis(False, error=str(exc))
    except Exception as exc:
        return _ergebnis(False, error=f"Pfadinventar-Lesen fehlgeschlagen: {exc}")



def tool_harness_path_check(args: dict) -> dict:
    try:
        session_id = _required_path_session_id(args)
        data = harness_path_journey_run(
            "check",
            arguments={"path": str(args.get("path") or "")},
            session_id=session_id,
        )
        return _ergebnis(True, data=data)
    except CognitiveGraphError as exc:
        return _ergebnis(False, error=str(exc))
    except Exception as exc:
        return _ergebnis(False, error=f"Ordner-Abhaken fehlgeschlagen: {exc}")


def tool_harness_path_checklist(args: dict) -> dict:
    try:
        session_id = _required_path_session_id(args)
        data = harness_path_journey_run(
            "checklist",
            arguments={
                "prefix": args.get("prefix"),
                "limit": int(args.get("limit", 200)),
                "cursor": int(args.get("cursor", 0)),
            },
            session_id=session_id,
        )
        return _ergebnis(True, data=data)
    except CognitiveGraphError as exc:
        return _ergebnis(False, error=str(exc))
    except Exception as exc:
        return _ergebnis(False, error=f"Hakenliste fehlgeschlagen: {exc}")


def tool_harness_path_fund(args: dict) -> dict:
    try:
        session_id = _required_path_session_id(args)
        data = harness_path_journey_run(
            "fund",
            arguments={
                "path": str(args.get("path") or ""),
                "what_is": str(args.get("what_is") or ""),
                "origin": str(args.get("origin") or ""),
                "why_include": str(args.get("why_include") or ""),
            },
            session_id=session_id,
        )
        return _ergebnis(True, data=data)
    except CognitiveGraphError as exc:
        return _ergebnis(False, error=str(exc))
    except Exception as exc:
        return _ergebnis(False, error=f"Fund-Speichern fehlgeschlagen: {exc}")


def tool_harness_path_funds(args: dict) -> dict:
    try:
        session_id = _required_path_session_id(args)
        data = harness_path_journey_run(
            "funds",
            arguments={
                "limit": int(args.get("limit", 200)),
                "cursor": int(args.get("cursor", 0)),
            },
            session_id=session_id,
        )
        return _ergebnis(True, data=data)
    except CognitiveGraphError as exc:
        return _ergebnis(False, error=str(exc))
    except Exception as exc:
        return _ergebnis(False, error=f"Fundregister-Lesen fehlgeschlagen: {exc}")


def _atlas_active_session_id(args: dict) -> str:
    return str(args.get("session_id") or "direct-mcp")


def _atlas_tool_result(callable_):
    try:
        return callable_()
    except (AtlasError, StreamLogError, OmegaAPIError, MachineLifecycleError) as exc:
        return _ergebnis(False, error=str(exc))
    except Exception as exc:
        return _ergebnis(False, error=f"Gesamtatlas-Fehler: {exc}")


def tool_atlas_pulse(args: dict) -> dict:
    return _atlas_tool_result(
        lambda: atlas_pulse(
            session_id=_atlas_active_session_id(args),
            current_project=args.get("current_project"),
            consume=bool(args.get("consume", True)),
            max_items=int(args.get("max_items", 12)),
            include_current_session=bool(args.get("include_current_session", False)),
            level=str(args.get("level", "whisper")),
        )
    )


def tool_atlas_map(args: dict) -> dict:
    return _atlas_tool_result(
        lambda: atlas_map_view(
            section=str(args.get("section", "summary")),
            limit=int(args.get("limit", 150)),
        )
    )


def tool_atlas_find(args: dict) -> dict:
    return _atlas_tool_result(
        lambda: atlas_find(
            query=str(args.get("query", "")),
            limit=int(args.get("limit", 40)),
            root_name=args.get("root_name"),
            kind=args.get("kind"),
            include_content=bool(args.get("include_content", True)),
        )
    )


def tool_atlas_omega_search(args: dict) -> dict:
    return _atlas_tool_result(lambda: atlas_omega_search(args))


def tool_atlas_omega_object(args: dict) -> dict:
    return _atlas_tool_result(lambda: atlas_omega_object_view(args))


def tool_atlas_omega_read_original(args: dict) -> dict:
    return _atlas_tool_result(lambda: atlas_omega_read_original(args))


def tool_atlas_omega_timeline(args: dict) -> dict:
    return _atlas_tool_result(lambda: atlas_omega_timeline(args))


def tool_atlas_omega_health(args: dict) -> dict:
    return _atlas_tool_result(lambda: atlas_omega_health(args))


def tool_atlas_omega_machine(args: dict) -> dict:
    return _atlas_tool_result(lambda: atlas_omega_machine_section(args))


def tool_atlas_where_is(args: dict) -> dict:
    return _atlas_tool_result(
        lambda: atlas_where_is(
            name_or_path=str(args.get("name_or_path", "")),
            limit=int(args.get("limit", 80)),
        )
    )


def tool_atlas_changed_since(args: dict) -> dict:
    return _atlas_tool_result(
        lambda: atlas_changed_since(
            revision=int(args.get("revision", 0)),
            limit=int(args.get("limit", 200)),
        )
    )


def tool_atlas_project_state(args: dict) -> dict:
    return _atlas_tool_result(lambda: atlas_project_state(query=str(args.get("query", ""))))


def tool_atlas_session_state(args: dict) -> dict:
    requested = str(args.get("target_session_id") or _atlas_active_session_id(args))
    return _atlas_tool_result(lambda: atlas_session_state(session_id=requested))


def tool_atlas_ai_stream_state(args: dict) -> dict:
    return _atlas_tool_result(
        lambda: atlas_ai_stream_state(stream_id=str(args.get("stream_id", "")))
    )


def tool_atlas_consensus(args: dict) -> dict:
    return _atlas_tool_result(
        lambda: atlas_list_consensus(
            query=args.get("query"),
            limit=int(args.get("limit", 100)),
        )
    )


def tool_atlas_conflicts(args: dict) -> dict:
    return _atlas_tool_result(
        lambda: atlas_list_conflicts(
            query=args.get("query"),
            status=str(args.get("status", "open")),
            limit=int(args.get("limit", 100)),
        )
    )


def tool_atlas_provenance(args: dict) -> dict:
    return _atlas_tool_result(
        lambda: atlas_provenance(
            path_or_query=str(args.get("path_or_query", "")),
            limit=int(args.get("limit", 60)),
        )
    )


def tool_atlas_relationships(args: dict) -> dict:
    return _atlas_tool_result(
        lambda: atlas_relationships(
            query=args.get("query"),
            node_type=args.get("node_type"),
            relation=args.get("relation"),
            limit=int(args.get("limit", 100)),
        )
    )


def tool_atlas_handoffs(args: dict) -> dict:
    return _atlas_tool_result(
        lambda: atlas_handoffs(
            session_id=args.get("target_session_id"),
            limit=int(args.get("limit", 100)),
        )
    )


def tool_atlas_health(args: dict) -> dict:
    return _atlas_tool_result(atlas_health)


def tool_atlas_refresh(args: dict) -> dict:
    return _atlas_tool_result(
        lambda: refresh_atlas(
            mode=str(args.get("mode", "light")),
            reason=str(args.get("reason", "mcp-tool")),
            session_id=_atlas_active_session_id(args),
            max_paths=int(args["max_paths"]) if args.get("max_paths") is not None else None,
            max_text_documents=int(args["max_text_documents"]) if args.get("max_text_documents") is not None else None,
        )
    )


def tool_atlas_idea_probe(args: dict) -> dict:
    return _atlas_tool_result(
        lambda: atlas_idea_probe(
            text=str(args.get("text", "")),
            session_id=_atlas_active_session_id(args),
            limit=int(args.get("limit", 8)),
        )
    )


def tool_atlas_idea_marker(args: dict) -> dict:
    return _atlas_tool_result(
        lambda: atlas_record_idea(
            text=str(args.get("text", "")),
            session_id=_atlas_active_session_id(args),
            prior_awareness=str(args.get("prior_awareness", "unknown")),
            classification_override=args.get("classification_override"),
            trigger=args.get("trigger"),
            related_paths=args.get("related_paths") or [],
            explicit_source_refs=args.get("explicit_source_refs") or [],
            supersedes_idea_ids=args.get("supersedes_idea_ids") or [],
        )
    )


def tool_atlas_record_consensus(args: dict) -> dict:
    return _atlas_tool_result(
        lambda: atlas_record_consensus(
            statement=str(args.get("statement", "")),
            consensus_class=str(args.get("consensus_class", "UNBEKANNT")),
            session_id=_atlas_active_session_id(args),
            scope=str(args.get("scope", "global")),
            source_refs=args.get("source_refs") or [],
            supersedes=args.get("supersedes") or [],
        )
    )


def tool_atlas_record_conflict(args: dict) -> dict:
    return _atlas_tool_result(
        lambda: atlas_record_conflict(
            statement_a=str(args.get("statement_a", "")),
            statement_b=str(args.get("statement_b", "")),
            session_id=_atlas_active_session_id(args),
            scope=str(args.get("scope", "global")),
            source_refs_a=args.get("source_refs_a") or [],
            source_refs_b=args.get("source_refs_b") or [],
        )
    )


def tool_atlas_stream_connect(args: dict) -> dict:
    return _atlas_tool_result(
        lambda: atlas_stream_connect(
            stream_id=str(args.get("stream_id", "")),
            session_id=_atlas_active_session_id(args),
            client_label=args.get("client_label"),
            source_surface=args.get("source_surface"),
        )
    )


def tool_atlas_stream_write(args: dict) -> dict:
    return _atlas_tool_result(
        lambda: atlas_stream_append(
            session_id=_atlas_active_session_id(args),
            stream_id=args.get("stream_id"),
            content=str(args.get("content", "")),
            kind=str(args.get("kind", "note")),
            role=args.get("role"),
            title=args.get("title"),
            source_refs=args.get("source_refs") or [],
            project_paths=args.get("project_paths") or [],
            external_session_id=args.get("external_session_id"),
            idempotency_key=args.get("idempotency_key"),
        )
    )


def tool_atlas_stream_search(args: dict) -> dict:
    return _atlas_tool_result(
        lambda: atlas_stream_search(
            query=str(args.get("query", "")),
            stream_id=args.get("stream_id"),
            kind=args.get("kind"),
            limit=int(args.get("limit", 20)),
        )
    )


def tool_atlas_stream_status(args: dict) -> dict:
    return _atlas_tool_result(
        lambda: atlas_stream_status(
            stream_id=args.get("stream_id"),
            session_id=_atlas_active_session_id(args),
        )
    )


# 2026-07-31, Daniels Auftrag nach einem Kathedralen-Befund mit ChatGPT: "jeder aistrom muss
# am integration in gesamtatlass genau wissen wo ab sofort dinge hin geschrieben werden."
# Bisherige Werkzeuge liessen jeden Strom selbst einen "halbwegs plausiblen" Pfad erfinden --
# atlas.stream_write schreibt nur in den Denkstrom-Log, kein Werkzeug legte bisher ganze Dateien
# verbindlich pro Strom ab. Dieses Mapping bindet den server-eigenen, vertrauenswuerdigen Actor
# (FLEXTRAWURST_ACTION_ACTOR, derselbe Wert wie in der Action-History) an den jeweiligen
# AI_STROEME/<strom>/-Ordner -- siehe /root/werkraum_gesamtatlas_eingang/AI_STROEME/README.md.
_AI_STREAM_ACTOR_ZU_ORDNER = {
    "GPT-5.6-sol-hoch": "chatgpt",
    "claude-code": "claude",
    "codex-cli": "codex",
    "gemini-cli": "gemini",
    "grok-check-in": "grok",
    "web-claude-check-in": "claudeweb",
}
_AI_STREAM_ERLAUBTE_KATEGORIEN = frozenset({
    "eigene_texte", "auftraege", "entscheidungen", "uebergaben", "gespraeche",
    "arbeitsreste", "konzepte", "ideen", "notizen", "dokumentationen", "reviews",
    "beobachtungen",
})
_AI_STREAM_EINGANG_ROOT = Path("/root/werkraum_gesamtatlas_eingang/AI_STROEME")

# 2026-07-31, Daniels Auftrag: Open Knowledge Format (OKF v0.2, siehe
# github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf/SPEC.md) als Format fuer
# alles, was ueber atlas.stream_file_write geschrieben wird -- herstellerneutrales
# Markdown+YAML-Frontmatter, das sowohl Menschen als auch andere Werkzeuge/LLMs ohne
# eigenes SDK lesen koennen. Kategorie -> lesbares OKF-"type"-Feld (OKF selbst schreibt
# keine zentrale Typ-Registrierung vor, siehe SPEC.md).
_AI_STREAM_KATEGORIE_ZU_OKF_TYP = {
    "eigene_texte": "Eigener Text",
    "auftraege": "Auftrag",
    "entscheidungen": "Entscheidung",
    "uebergaben": "Übergabe",
    "gespraeche": "Gespräch",
    "arbeitsreste": "Arbeitsrest",
    "konzepte": "Konzept",
    "ideen": "Idee",
    "notizen": "Notiz",
    "dokumentationen": "Dokumentation",
    "reviews": "Review",
    "beobachtungen": "Beobachtung",
}
_OKF_ERLAUBTE_STATUS = frozenset({"draft", "stable", "deprecated"})


def _okf_frontmatter_bauen(*, strom: str, kategorie: str, titel: str | None, beschreibung: str | None,
                            tags: list | None, status: str, ressource: str | None,
                            verlaeuft_am: str | None) -> str:
    """Baut OKF-v0.2-konformes YAML-Frontmatter. 'generated' wird ausschliesslich aus dem
    server-eigenen Actor/der aktuellen Zeit gebaut (kein Feld, das der Aufrufer faelschen
    koennte) -- dieselbe Vertrauenslogik wie beim Strom-Ordner selbst."""
    eigene_tags = sorted({strom, *(str(t) for t in (tags or []))})
    frontmatter: dict = {
        "type": _AI_STREAM_KATEGORIE_ZU_OKF_TYP.get(kategorie, kategorie),
        "tags": eigene_tags,
        "generated": {
            "by": strom,
            "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
        "status": status,
    }
    if titel:
        frontmatter["title"] = titel
    if beschreibung:
        frontmatter["description"] = beschreibung
    if ressource:
        frontmatter["resource"] = ressource
    if verlaeuft_am:
        frontmatter["stale_after"] = verlaeuft_am
    yaml_text = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, default_flow_style=False)
    return f"---\n{yaml_text}---\n\n"


def tool_atlas_stream_file_write(args: dict) -> dict:
    """Legt eine Datei verbindlich im eigenen AI_STROEME/<strom>/<kategorie>/-Ordner ab, im
    Open Knowledge Format (OKF v0.2): automatisch generiertes YAML-Frontmatter vor dem
    eigentlichen Markdown-Inhalt. Bewusstes Design: KEIN Pfad-Argument und KEIN
    stream_id-Argument -- der Zielordner wird ausschliesslich aus dem server-eigenen Actor
    abgeleitet, ein Aufrufer kann sich also nicht als anderer Strom ausgeben. Beruehrt nicht
    die bekannte vps.shell-Pfadluecke (siehe project_vps_mcp_ai_stroeme.md), weil dieses
    Werkzeug komplett unabhaengig von SCHREIB_ERLAUBTE_WURZELN/vps.write_file ist -- kein
    absoluter Pfad wird je entgegengenommen."""
    actor = os.environ.get("FLEXTRAWURST_ACTION_ACTOR", "GPT-5.6-sol-hoch")
    strom = _AI_STREAM_ACTOR_ZU_ORDNER.get(actor)
    if not strom:
        return _ergebnis(False, error=f"Kein AI_STROEME-Ordner fuer Actor '{actor}' hinterlegt.")
    kategorie = str(args.get("kategorie", ""))
    if kategorie not in _AI_STREAM_ERLAUBTE_KATEGORIEN:
        return _ergebnis(False, error=f"Unbekannte Kategorie '{kategorie}'. Erlaubt: {sorted(_AI_STREAM_ERLAUBTE_KATEGORIEN)}")
    dateiname = str(args.get("dateiname", ""))
    if not dateiname or "/" in dateiname or "\\" in dateiname or dateiname.startswith("."):
        return _ergebnis(False, error="dateiname muss ein einfacher Dateiname ohne Pfadtrenner sein und darf nicht mit einem Punkt beginnen.")
    status = str(args.get("status", "draft"))
    if status not in _OKF_ERLAUBTE_STATUS:
        return _ergebnis(False, error=f"status muss eines von {sorted(_OKF_ERLAUBTE_STATUS)} sein.")
    inhalt = str(args.get("inhalt", ""))
    frontmatter = _okf_frontmatter_bauen(
        strom=strom, kategorie=kategorie,
        titel=args.get("titel"), beschreibung=args.get("beschreibung"),
        tags=args.get("tags"), status=status,
        ressource=args.get("ressource"), verlaeuft_am=args.get("verlaeuft_am"),
    )
    ziel = _AI_STREAM_EINGANG_ROOT / strom / kategorie / dateiname
    try:
        ziel.parent.mkdir(parents=True, exist_ok=True)
        ziel.write_text(frontmatter + inhalt, encoding="utf-8")
    except Exception as exc:
        return _ergebnis(False, error=f"Schreiben fehlgeschlagen: {exc}")
    # 2026-07-31: jede neu geschriebene OKF-Datei wird sofort mit-embedded, damit
    # atlas.hybrid_search sie ohne separaten Batch-Lauf findet -- siehe
    # mcp_atlas_hybrid_search.py. Ein Fehler dabei blockiert nie das eigentliche
    # Schreiben (siehe try/except dort).
    atlas_vektor_index_aktualisieren(
        pfad=str(ziel), text=f"{args.get('titel') or dateiname}\n\n{inhalt}",
        metadaten={"strom": strom, "kategorie": kategorie, "titel": args.get("titel") or dateiname},
    )
    return _ergebnis(True, data={
        "pfad": str(ziel), "strom": strom, "kategorie": kategorie,
        "bytes": len((frontmatter + inhalt).encode("utf-8")), "okf_typ": _AI_STREAM_KATEGORIE_ZU_OKF_TYP.get(kategorie, kategorie),
    })


def tool_atlas_hybrid_search(args: dict) -> dict:
    return atlas_hybrid_suche(
        query=str(args.get("query", "")),
        limit=int(args.get("limit", 10)),
    )


TOOLS.update(
    {
        "harness.graph": {
            "fn": tool_harness_graph,
            "description": "Zeigt den aktiven MCP-Aktionsgraphen mit State, Knoten, Kanten, Policy-Quelle und erlaubten/gesperrten Uebergaengen. Rein read-only.",
            "inputSchema": {"type": "object", "properties": {}},
        },
        "harness.layers": {
            "fn": tool_harness_layers,
            "description": "Liest den kanonischen Harness-Schichtenzustand aus PostgreSQL: Zweck, Wirkung, desired/effective Status, Health, Gruende, TTL, offene Resonanzbeitraege und Control-Leases. Rein read-only.",
            "inputSchema": {
                "type": "object",
                "properties": {"session_id": {"type": "string"}}
            },
        },
        "harness.layer_set": {
            "fn": tool_harness_layer_set,
            "description": "Setzt genau einen Harness-Layer ACTIVE, PAUSED oder ARCHIVED. ChatGPT darf ACTIVE immer setzen; PAUSED/ARCHIVED nur mit aktiver, vom Dashboard vergebenen Control-Lease. Pause kann unbegrenzt oder per TTL erfolgen.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "layer_id": {"type": "string"},
                    "desired_status": {"type": "string", "enum": ["ACTIVE", "PAUSED", "ARCHIVED"]},
                    "reason": {"type": "string"},
                    "ttl_seconds": {"type": "integer", "minimum": 1}
                },
                "required": ["layer_id", "desired_status", "reason"]
            },
        },
        "harness.full_activate": {
            "fn": tool_harness_full_activate,
            "description": "Aktiviert alle nicht archivierten/nicht abgelaufenen Harness-Layer wieder voll. Darf von ChatGPT jederzeit zur Schutz-Reaktivierung genutzt werden.",
            "inputSchema": {
                "type": "object",
                "properties": {"reason": {"type": "string"}}
            },
        },
        "harness.create_layer": {
            "fn": tool_harness_create_layer,
            "description": "Legt eine PROJECT-, TASK- oder EPHEMERAL-Schicht mit Menschenbeschreibung, Scope, Provenienz und optionaler TTL an. CORE-Layer koennen hier nicht erzeugt werden.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "layer_id": {"type": "string"},
                    "kind": {"type": "string", "enum": ["PROJECT", "TASK", "EPHEMERAL"]},
                    "title": {"type": "string"},
                    "purpose": {"type": "string"},
                    "does": {"type": "string"},
                    "pause_effect": {"type": "string"},
                    "reason": {"type": "string"},
                    "scope": {"type": "object"},
                    "provenance": {"type": "object"},
                    "parent_layer_id": {"type": "string"},
                    "ttl_seconds": {"type": "integer", "minimum": 1}
                },
                "required": ["layer_id", "kind", "title", "purpose", "does", "pause_effect"]
            },
        },
        "harness.context_add": {
            "fn": tool_harness_context_add,
            "description": "Haengt an einen Harness-Layer strukturierten Kontext an: PLAN, VISION, RESEARCH, EVIDENCE, DOC, LINK oder NOTE. Der Eintrag landet im selben PostgreSQL-Koerper wie das Dashboard.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "layer_id": {"type": "string"},
                    "context_type": {"type": "string", "enum": ["PLAN", "VISION", "RESEARCH", "EVIDENCE", "DOC", "LINK", "NOTE"]},
                    "title": {"type": "string"},
                    "summary": {"type": "string"},
                    "reference": {"type": "string"},
                    "metadata": {"type": "object"}
                },
                "required": ["layer_id", "context_type", "title"]
            },
        },
        "harness.feedback": {
            "fn": tool_harness_feedback,
            "description": "Schreibt Kommentar, Bewertung oder Vorschlag in die append-only Resonanzspur. Ein Beitrag hat niemals automatisch Steuerwirkung. Fuer einen maschinenlesbaren PROPOSAL kann payload.action SET_LAYER_STATUS, GRANT_CONTROL_LEASE, CREATE_LAYER oder UPDATE_LAYER_DEFINITION sein. UPDATE_LAYER_DEFINITION nutzt payload.layer_id und payload.changes mit title, purpose, does und/oder pause_effect. Erst Daniels ausdrueckliches ACCEPT im authentifizierten Dashboard wendet eine solche Aktion an.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "layer_id": {"type": "string"},
                    "entry_type": {"type": "string", "enum": ["COMMENT", "PROPOSAL", "ACCEPT", "REJECT", "RATING"]},
                    "text": {"type": "string"},
                    "payload": {"type": "object"},
                    "parent_entry_id": {"type": "string"}
                },
                "required": ["entry_type", "text"]
            },
        },
        "harness.feedback_list": {
            "fn": tool_harness_feedback_list,
            "description": "Liest die gemeinsame Resonanzspur fuer einen Layer oder layeruebergreifend. Zeigt ChatGPT- und Dashboard-Beitraege getrennt nach Actor und Typ.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "layer_id": {"type": "string"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 500}
                }
            },
        },
        "harness.feedback_inbox": {
            "fn": tool_harness_feedback_inbox,
            "description": "Liest Daniels noch nicht von ChatGPT quittierte Dashboard-Beitraege. Dieselben Eintraege stehen automatisch auch als chatgpt_inbox im kanonischen Layer-Snapshot.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "minimum": 1, "maximum": 500}
                }
            },
        },
        "harness.feedback_ack": {
            "fn": tool_harness_feedback_ack,
            "description": "Quittiert genau einen Dashboard-Beitrag als von ChatGPT verarbeitet. Der eigentliche Kommentar-/Vorschlagsstatus bleibt unveraendert.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "entry_id": {"type": "string"},
                    "note": {"type": "string"}
                },
                "required": ["entry_id"]
            },
        },
        "harness.path_scan": {
            "fn": tool_harness_path_scan,
            "description": "Inventarisiert den erlaubten VPS ausschliesslich als Pfade und persistiert den Scan in Postgres; Dateiinhalte werden nicht geoeffnet.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "max_directories": {"type": "integer", "minimum": 1, "maximum": 20000},
                    "reset": {"type": "boolean"},
                    "session_id": {"type": "string"}
                }
            },
        },
        "harness.path_inventory": {
            "fn": tool_harness_path_inventory,
            "description": "Liest ausschliesslich bereits persistierte Pfade aus der VPS-Pfadinventur.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "prefix": {"type": "string"},
                    "entry_type": {"type": "string", "enum": ["dir", "file", "symlink", "other"]},
                    "state": {"type": "string"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 2000},
                    "cursor": {"type": "integer", "minimum": 0},
                    "session_id": {"type": "string"}
                }
            },
        },
        "harness.path_check": {
            "fn": tool_harness_path_check,
            "description": "Hakt genau einen inventarisierten Ordner als wirklich geprueft ab. Erst nach vollstaendigem Pfadscan.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "session_id": {"type": "string"}
                },
                "required": ["path"]
            },
        },
        "harness.path_checklist": {
            "fn": tool_harness_path_checklist,
            "description": "Liest die persistente Ordner-Hakenliste nach abgeschlossenem Pfadscan.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "prefix": {"type": "string"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 2000},
                    "cursor": {"type": "integer", "minimum": 0},
                    "session_id": {"type": "string"}
                }
            },
        },
        "harness.path_fund": {
            "fn": tool_harness_path_fund,
            "description": "Speichert einen Fundpfad mit exakt drei knappen Angaben: Was ist das? Wo kam es her? Warum soll es mit? Erst nach vollstaendigem Pfadscan.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "what_is": {"type": "string"},
                    "origin": {"type": "string"},
                    "why_include": {"type": "string"},
                    "session_id": {"type": "string"}
                },
                "required": ["path", "what_is", "origin", "why_include"]
            },
        },
        "harness.path_funds": {
            "fn": tool_harness_path_funds,
            "description": "Liest das persistente Fundregister mit Pfad sowie Was ist das / Wo kam es her / Warum soll es mit.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "minimum": 1, "maximum": 2000},
                    "cursor": {"type": "integer", "minimum": 0},
                    "session_id": {"type": "string"}
                },
                "required": ["session_id"]
            },
        },
        "harness.check_action": {
            "fn": tool_harness_check_action,
            "description": "Prueft eine geplante MCP-Toolaktion gegen den Aktionsgraphen, ohne sie auszufuehren. Liefert ALLOW/BLOCK, Aktionsknoten, Begruendung und erlaubte Nachbarkanten.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "tool_name": {"type": "string"},
                    "arguments": {"type": "object"},
                },
                "required": ["tool_name"],
            },
        },
        "harness.set_mode": {
            "fn": tool_harness_set_mode,
            "description": "Setzt den sichtbaren Arbeitsstil. Der Modus ersetzt keine Pruefung der konkreten Nutzeranweisung, des TASK-Scopes oder eines Direktiven-Reminders.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "mode": {"type": "string", "enum": ["DISCOVER", "SURGICAL", "CONTROL_PLANE"]},
                    "user_instruction": {"type": "string"},
                    "session_id": {"type": "string"},
                },
                "required": ["mode", "user_instruction"],
            },
        },
        "harness.note": {
            "fn": tool_harness_note,
            "description": "Legt einen expliziten Arbeitsknoten an. USER_DIRECTIVE wird zusaetzlich wortgetreu append-only in PostgreSQL persistiert; Interpretation/Constraints liegen getrennt daneben.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "node_type": {"type": "string", "enum": ["USER_DIRECTIVE", "OBSERVATION", "QUESTION", "HYPOTHESIS", "CONTRADICTION", "DECISION", "LESSON"]},
                    "text": {"type": "string"},
                    "source_refs": {"type": "array", "items": {"type": "string"}},
                    "confidence": {"type": "string", "enum": ["unknown", "low", "medium", "high"]},
                    "status": {"type": "string", "enum": ["open", "resolved", "superseded"]},
                    "metadata": {"type": "object"},
                    "constraints": {
                        "type": "array",
                        "description": "Nur fuer USER_DIRECTIVE: getrennte maschinenlesbare Ableitungen. raw text bleibt unveraendert.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "effect": {"type": "string", "enum": ["DENY", "REQUIRE_REMINDER", "REMIND"]},
                                "action_pattern": {"type": "string"},
                                "target_pattern": {"type": "string"},
                                "statement": {"type": "string"},
                                "metadata": {"type": "object"}
                            },
                            "required": ["effect", "statement"]
                        }
                    },
                    "supersedes": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Event-IDs aelterer Direktiven, die durch diese neue explizite Direktive abgeloest werden. Alte Events bleiben erhalten."
                    },
                    "session_id": {"type": "string"},
                },
                "required": ["node_type", "text"],
            },
        },
        "harness.directive_context": {
            "fn": tool_harness_directive_context,
            "description": "Liest aktive append-only Daniel-Direktiven aus PostgreSQL als Reminder-Kontext. Retrieval ist Erinnerung, keine neue Autoritaet.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 30}
                },
                "required": ["query"]
            },
        },
        "harness.directive_status": {
            "fn": tool_harness_directive_status,
            "description": "Liest das kanonische Direktiven-Inventar fuer ChatGPT und Dashboard: Originalwortlaut, Verifizierungsstatus, aktive/ersetzte Historie, Constraints und Invarianten. Rein read-only.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 500}
                }
            },
        },
        "harness.directive_reminder": {
            "fn": tool_harness_directive_reminder,
            "description": "Erzeugt vor einer geplanten Mutation einen kurzlebigen, an Toolname plus exakte Argumente gebundenen Direktiven-Reminder. Der serverseitige Preflight-Denier verlangt ihn.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "tool_name": {"type": "string"},
                    "arguments": {"type": "object"},
                    "session_id": {"type": "string"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 30}
                },
                "required": ["tool_name", "arguments"]
            },
        },
        "harness.output_check": {
            "fn": tool_harness_output_check,
            "description": "Prueft einen vorgesehenen Ausgabetext gegen aktive Daniel-Direktiven. Hart wird diese Pruefung erst, wenn Bridge/Client sie vor jeder Ausgabe zwingend aufruft.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "proposed_text": {"type": "string"},
                    "session_id": {"type": "string"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 30}
                },
                "required": ["proposed_text"]
            },
        },
        "harness.experience_message": {
            "fn": tool_harness_experience_message,
            "description": "Speichert einen Nutzerinput, Assistant-Output oder eine anschliessende Nutzerreaktion wortgetreu append-only in PostgreSQL. Keine Zusammenfassung und keine Umformulierung.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "raw_text": {"type": "string"},
                    "role": {"type": "string", "enum": ["USER", "ASSISTANT", "USER_REACTION"]},
                    "turn_id": {"type": "string"},
                    "session_id": {"type": "string"},
                    "metadata": {"type": "object"}
                },
                "required": ["raw_text", "role"]
            },
        },
        "harness.learning_context": {
            "fn": tool_harness_learning_context,
            "description": "Liest aktive und abgeschwaechte selbstgelernte Regeln aus PostgreSQL als relevanten Erinnerungskontext. Nur ACTIVE darf hart wirken.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "session_id": {"type": "string"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 30}
                },
                "required": ["query"]
            },
        },
        "harness.self_observed_drift": {
            "fn": tool_harness_self_observed_drift,
            "description": "Speichert eine von ChatGPT selbst beobachtete Abweichung append-only, ohne sie als Nutzerkorrektur auszugeben.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "turn_id": {"type": "string"},
                    "description": {"type": "string"},
                    "session_id": {"type": "string"},
                    "action_id": {"type": "string"},
                    "drift_code": {"type": "string"},
                    "evidence": {"type": "object"}
                },
                "required": ["turn_id", "description"]
            },
        },
        "harness.candidate_rule": {
            "fn": tool_harness_candidate_rule,
            "description": "Erzeugt aus einem Driftpunkt eine Kandidatenregel. Die Regel wird nicht ungeprueft aktiv; der Lernzyklus testet sie gegen alte Traces.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "drift_id": {"type": "string"},
                    "rule_text": {"type": "string"},
                    "rule_kind": {"type": "string"},
                    "condition": {"type": "object"},
                    "enforcement": {"type": "object"},
                    "session_id": {"type": "string"}
                },
                "required": ["drift_id"]
            },
        },
        "harness.learning_test": {
            "fn": tool_harness_learning_test,
            "description": "Testet eine Kandidatenregel erneut deterministisch gegen gespeicherte alte Turns und misst Erfolgs-Kollisionen.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rule_id": {"type": "string"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 1000}
                },
                "required": ["rule_id"]
            },
        },
        "harness.learning_cycle": {
            "fn": tool_harness_learning_cycle,
            "description": "Fuehrt den LangGraph-Lernpfad Kandidat -> Regressionstest -> sichere Aktivierung aus.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rule_id": {"type": "string"}
                },
                "required": ["rule_id"]
            },
        },
        "harness.rule_feedback": {
            "fn": tool_harness_rule_feedback,
            "description": "Speichert deterministische oder von ChatGPT selbst beobachtete Rueckmeldung zu einer Lernregel und bewertet sie auf Wunsch sofort neu. Keine Nutzerkorrektur-Zuschreibung.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rule_id": {"type": "string"},
                    "outcome": {"type": "string", "enum": ["HELPFUL", "HARMFUL", "IRRELEVANT", "CONTRADICTED"]},
                    "turn_id": {"type": "string"},
                    "source_kind": {"type": "string", "enum": ["DETERMINISTIC", "CHATGPT_SELF_OBSERVED"]},
                    "evidence": {"type": "object"},
                    "reassess": {"type": "boolean"}
                },
                "required": ["rule_id", "outcome"]
            },
        },
        "harness.reassess_rule": {
            "fn": tool_harness_reassess_rule,
            "description": "Prueft eine bestehende Regel gegen den gewachsenen Trace-Bestand neu und kann sie ACTIVE, WEAKENED oder RETIRED setzen.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "rule_id": {"type": "string"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 1000}
                },
                "required": ["rule_id"]
            },
        },
        "harness.supersede_rule": {
            "fn": tool_harness_supersede_rule,
            "description": "Markiert eine alte Regel append-only als SUPERSEDED, aber nur wenn die Ersatzregel bereits ACTIVE ist.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "old_rule_id": {"type": "string"},
                    "replacement_rule_id": {"type": "string"},
                    "reason": {"type": "string"}
                },
                "required": ["old_rule_id", "replacement_rule_id"]
            },
        },
        "harness.learning_status": {
            "fn": tool_harness_learning_status,
            "description": "Zeigt den aktuellen Status selbstgelernter Regeln samt Rueckmeldungszaehlern; die komplette Geschichte bleibt append-only in PostgreSQL.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 500}
                }
            },
        },
        "harness.link": {
            "fn": tool_harness_link,
            "description": "Verknuepft zwei vorhandene Arbeitsknoten mit einer expliziten Kante.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "from_id": {"type": "string"},
                    "to_id": {"type": "string"},
                    "edge_type": {"type": "string", "enum": ["LEADS_TO", "SUPPORTS", "CONTRADICTS", "ANSWERS", "DEPENDS_ON", "SUPERSEDES", "VERIFIED_BY", "BLOCKED_BY", "DERIVED_FROM", "REQUESTS"]},
                    "reason": {"type": "string"},
                    "session_id": {"type": "string"},
                },
                "required": ["from_id", "to_id", "edge_type"],
            },
        },
        "harness.resolve": {
            "fn": tool_harness_resolve,
            "description": "Markiert einen expliziten Arbeitsknoten als resolved, open oder superseded.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "node_id": {"type": "string"},
                    "status": {"type": "string", "enum": ["open", "resolved", "superseded"]},
                    "session_id": {"type": "string"},
                },
                "required": ["node_id"],
            },
        },
        "harness.next": {
            "fn": tool_harness_next,
            "description": "Leitet aus Workflow-State und offenen Arbeitsknoten einige sinnvolle naechste Kanten ab, ohne sie automatisch auszufuehren.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer"},
                    "session_id": {"type": "string"},
                },
            },
        },
        "harness.wander": {
            "fn": tool_harness_wander,
            "description": "Wander-RAG fuer neugierige, nicht-lineare Erkundung. Liefert mehrere moegliche Pfade aus Atlas-, Vektor- und organisch gewachsenem Manual-Read-Gedaechtnis. Treffer sind Einladungen, keine Wahrheit und kein Lesebeweis; es wird nichts automatisch weitergelesen.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "seed": {"type": "string", "description": "Aktuelle Spur, Frage, Begriff oder Assoziation, von der aus gewandert wird."},
                    "trail": {"type": "array", "items": {"type": "string"}, "description": "Optional: bereits bewusst bereiste Pfade. Ermoeglicht Echo/Rueckkehr statt blindem Top-k."},
                    "limit": {"type": "integer", "description": "Anzahl sichtbarer moeglicher Abzweigungen, 3-12, Default 6."},
                    "session_id": {"type": "string"},
                },
                "required": ["seed"],
            },
        },
        "portfolio.arbeitsrahmen_context": {
            "fn": tool_portfolio_archaeology_context,
            "description": "LEGACY read-only Kontext zur frueheren Portfolio-Archaeologie. Nicht autoritativ fuer aktuelle Aktionen; bei Widerspruch gilt harness.graph. Liefert alten Forschungsstand/Beweisgrenzen plus den aktuellen Aktionsgraphen.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "project_root": {
                        "type": "string",
                        "description": "Optional. Muss innerhalb von /root/werkraum/in_gpt/job-portfolio-try liegen."
                    },
                    "include_full_rules": {
                        "type": "boolean",
                        "description": "Wenn true, werden beide vollständigen Arbeitsverfassungen und der komplette Research State mitgeliefert. Default false."
                    }
                }
            }
        },
        "portfolio.archaeology_context": {
            "fn": tool_portfolio_archaeology_context,
            "description": "LEGACY-Kompatibilitaetsalias fuer portfolio.arbeitsrahmen_context. Nur historischer read-only Kontext; aktuelle Handlungsautoritaet ist harness.graph.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "project_root": {
                        "type": "string",
                        "description": "Optional. Muss innerhalb von /root/werkraum/in_gpt/job-portfolio-try liegen."
                    },
                    "include_full_rules": {
                        "type": "boolean",
                        "description": "Wenn true, werden beide vollständigen Arbeitsverfassungen und der komplette Research State mitgeliefert. Default false."
                    }
                }
            }
        },
        "atlas.hybrid_search": {
            "fn": tool_atlas_hybrid_search,
            "description": "Hybrid-Suche (BM25-Volltext ueber den gesamten indizierten Gesamtatlas + Vektor-Aehnlichkeit ueber AI_STROEME/-Inhalte), per Reciprocal Rank Fusion (RRF, k=60) kombiniert -- angelehnt an qmd/LLMWikiNG. Kein LLM-Reranking, keine Query-Expansion.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "limit": {"type": "integer", "description": "Max. Anzahl Ergebnisse, Default 10."}
                },
                "required": ["query"]
            }
        },
        "atlas.stream_file_write": {
            "fn": tool_atlas_stream_file_write,
            "description": "Legt eine Datei verbindlich im eigenen AI_STROEME/<strom>/<kategorie>/-Ordner des Gesamtatlas-Eingangs ab, im Open Knowledge Format (OKF v0.2: YAML-Frontmatter + Markdown). Kein Pfad-Argument -- der Zielordner wird server-seitig aus dem aufrufenden Strom abgeleitet, ein falscher Ort ist technisch unmoeglich.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "kategorie": {"type": "string", "enum": ["eigene_texte", "auftraege", "entscheidungen", "uebergaben", "gespraeche", "arbeitsreste", "konzepte", "ideen", "notizen", "dokumentationen", "reviews", "beobachtungen"]},
                    "dateiname": {"type": "string", "description": "Einfacher Dateiname ohne Pfadtrenner, z.B. 'mein-konzept.md'."},
                    "inhalt": {"type": "string", "description": "Markdown-Koerper, OHNE eigenes Frontmatter -- das wird automatisch generiert."},
                    "titel": {"type": "string", "description": "OKF 'title' -- lesbarer Anzeigename."},
                    "beschreibung": {"type": "string", "description": "OKF 'description' -- ein Satz Zusammenfassung."},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "Zusaetzliche OKF 'tags' -- der eigene Strom-Name wird immer automatisch mit aufgenommen."},
                    "status": {"type": "string", "enum": ["draft", "stable", "deprecated"], "description": "OKF Lifecycle-Status, Default 'draft'."},
                    "ressource": {"type": "string", "description": "OKF 'resource' -- kanonische URI des zugrundeliegenden Assets, falls vorhanden."},
                    "verlaeuft_am": {"type": "string", "description": "OKF 'stale_after', Format YYYY-MM-DD."}
                },
                "required": ["kategorie", "dateiname", "inhalt"]
            }
        },
        "atlas.stream_connect": {
            "fn": tool_atlas_stream_connect,
            "description": "Verbindet die aktuelle History-Session dauerhaft mit Claude Code, Claude Web, ChatGPT, Codex, Gemini, Kimi oder GLM und öffnet deren getrennte Gesamtatlas-Mitschrift.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "stream_id": {"type": "string", "enum": ["claude", "claudecode", "claudeweb", "chatgpt", "codex", "gemini", "kimi", "glm"]},
                    "client_label": {"type": "string"},
                    "source_surface": {"type": "string"}
                },
                "required": ["stream_id"]
            }
        },
        "atlas.stream_write": {
            "fn": tool_atlas_stream_write,
            "description": "Schreibt einen vollständigen Text, Gedanken, Beschluss oder Übergabekörper append-only in die getrennte Mitschrift des verbundenen AI-Stroms und prüft ihn durch Rücklesung und Hash.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "stream_id": {"type": "string"},
                    "content": {"type": "string"},
                    "kind": {"type": "string"},
                    "role": {"type": "string"},
                    "title": {"type": "string"},
                    "source_refs": {"type": "array", "items": {"type": "string"}},
                    "project_paths": {"type": "array", "items": {"type": "string"}},
                    "external_session_id": {"type": "string"},
                    "idempotency_key": {"type": "string"}
                },
                "required": ["content"]
            }
        },
        "atlas.stream_search": {
            "fn": tool_atlas_stream_search,
            "description": "Durchsucht die append-only Mitschriften der verbundenen AI-Ströme sofort, auch bevor ein globaler Atlas-Vollrefresh sie in die allgemeine Volltextsuche aufgenommen hat.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "stream_id": {"type": "string"},
                    "kind": {"type": "string"},
                    "limit": {"type": "integer"}
                },
                "required": ["query"]
            }
        },
        "atlas.stream_status": {
            "fn": tool_atlas_stream_status,
            "description": "Zeigt Verbindungs-, Mitschrift-, Hash- und Suchstatus aller sieben vorhandenen AI-Ströme oder eines einzelnen Stroms.",
            "inputSchema": {
                "type": "object",
                "properties": {"stream_id": {"type": "string"}}
            }
        },
        "atlas.pulse": {
            "fn": tool_atlas_pulse,
            "description": "Liefert pro Session nur die seit dem letzten Abgleich neu hinzugekommenen fremden Sitzungs-, Atlas-, Konflikt- und Eingebungsspuren.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "current_project": {"type": "string"},
                    "consume": {"type": "boolean"},
                    "max_items": {"type": "integer"},
                    "include_current_session": {"type": "boolean"},
                    "level": {"type": "string", "enum": ["whisper", "project", "stream", "full"]}
                }
            }
        },
        "atlas.map": {
            "fn": tool_atlas_map,
            "description": "Liest die Gesamtkarte oder einzelne Register für Wurzeln, Projekte, Vaults, Systeme, AI-Ströme, Sessions, Konsens, Konflikte und Eingebungsspuren.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "section": {"type": "string", "enum": ["summary", "roots", "root_letters", "projects", "vaults", "systems", "ai_streams", "sessions", "consensus", "conflicts", "ideas", "project_revisions", "claims", "validations", "handoffs", "relationships", "ai_bridges", "all"]},
                    "limit": {"type": "integer"}
                }
            }
        },
        "atlas.find": {
            "fn": tool_atlas_find,
            "description": "Hybride Suche im Pfad-/Metadatenindex und im lexikalischen Volltext-/Begriffsindex des Gesamtatlas.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "limit": {"type": "integer"},
                    "root_name": {"type": "string"},
                    "kind": {"type": "string"},
                    "include_content": {"type": "boolean"}
                },
                "required": ["query"]
            }
        },
        "atlas.omega_search": {
            "fn": tool_atlas_omega_search,
            "description": "Durchsucht den vollständigen chunkweisen Omega-Originalindex ohne 49.152-Byte-Präfixgrenze und liefert exakte UTF-8-Bytepositionen.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 100},
                    "include_historic": {"type": "boolean"}
                },
                "required": ["query"]
            }
        },
        "atlas.omega_object": {
            "fn": tool_atlas_omega_object,
            "description": "Liest stabile Omega-Objektidentität, Pfade, Versionen, Beziehungen und Ereignisse read-only.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path_or_object": {"type": "string"},
                    "edge_limit": {"type": "integer", "minimum": 1, "maximum": 500},
                    "version_limit": {"type": "integer", "minimum": 1, "maximum": 500}
                },
                "required": ["path_or_object"]
            }
        },
        "atlas.omega_read_original": {
            "fn": tool_atlas_omega_read_original,
            "description": "Liest einen hashgebundenen paginierten Bytebereich einer aktuellen oder historischen Originalversion inklusive Base64-Rohkörper.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path_or_object": {"type": "string"},
                    "version_id": {"type": "string"},
                    "start_byte": {"type": "integer", "minimum": 0},
                    "max_bytes": {"type": "integer", "minimum": 1, "maximum": 262144}
                },
                "required": ["path_or_object"]
            }
        },
        "atlas.omega_timeline": {
            "fn": tool_atlas_omega_timeline,
            "description": "Liest die Versionsepochen, Pfadgeschichte und Ereignisspur eines Omega-Objekts read-only.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path_or_object": {"type": "string"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 1000}
                },
                "required": ["path_or_object"]
            }
        },
        "atlas.omega_health": {
            "fn": tool_atlas_omega_health,
            "description": "Prüft Omega-Gates, Core-Hashbindung, Datenbankintegrität und Objekt-/Versionszähler read-only.",
            "inputSchema": {"type": "object", "properties": {}}
        },
        "atlas.omega_machine": {
            "fn": tool_atlas_omega_machine,
            "description": "Liest den dynamischen Omega-Maschinen-, Lebenszyklus-, Runtime- und Preflight-Vertrag read-only.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "section": {
                        "type": "string",
                        "enum": ["status", "manifest", "truth_ring", "journey", "capsules", "projects", "relationships", "versions", "original_references", "gaps", "runtime", "lifecycle", "preflight"]
                    },
                    "session_id": {
                        "type": "string",
                        "description": "Explizite isolierte Test- oder Arbeitskennung; begrenzt gespiegelt und keine Authentifizierung."
                    }
                }
            }
        },
        "atlas.where_is": {
            "fn": tool_atlas_where_is,
            "description": "Findet einen exakten oder ähnlich benannten Pfad im globalen Atlas.",
            "inputSchema": {"type": "object", "properties": {"name_or_path": {"type": "string"}, "limit": {"type": "integer"}}, "required": ["name_or_path"]}
        },
        "atlas.changed_since": {
            "fn": tool_atlas_changed_since,
            "description": "Liest den Atlas-Änderungsstrom seit einer bestimmten Revision.",
            "inputSchema": {"type": "object", "properties": {"revision": {"type": "integer"}, "limit": {"type": "integer"}}}
        },
        "atlas.project_state": {
            "fn": tool_atlas_project_state,
            "description": "Liefert Projektkarte, Einstiegspfade sowie zugehörigen Konsens und Konflikte.",
            "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}
        },
        "atlas.session_state": {
            "fn": tool_atlas_session_state,
            "description": "Liefert den registrierten Zustand und Atlas-Lesestand einer Sitzung.",
            "inputSchema": {"type": "object", "properties": {"target_session_id": {"type": "string"}}}
        },
        "atlas.ai_stream_state": {
            "fn": tool_atlas_ai_stream_state,
            "description": "Liefert Herkunfts-, Zuhause- und Sitzungsquellen eines AI-Stroms.",
            "inputSchema": {"type": "object", "properties": {"stream_id": {"type": "string"}}, "required": ["stream_id"]}
        },
        "atlas.consensus": {
            "fn": tool_atlas_consensus,
            "description": "Liest das provenienzgebundene Konsensregister; Wiederholung oder Ähnlichkeit wird nicht automatisch zu Konsens.",
            "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}, "limit": {"type": "integer"}}}
        },
        "atlas.conflicts": {
            "fn": tool_atlas_conflicts,
            "description": "Liest offene oder historische Konflikte zwischen Setzungen, Quellen und technischen Zuständen.",
            "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}, "status": {"type": "string", "enum": ["open", "resolved", "all"]}, "limit": {"type": "integer"}}}
        },
        "atlas.provenance": {
            "fn": tool_atlas_provenance,
            "description": "Verknüpft Atlasfund, History-Erwähnungen, Konsens, Konflikte und Eingebungsspuren zu einem Herkunftsbild.",
            "inputSchema": {"type": "object", "properties": {"path_or_query": {"type": "string"}, "limit": {"type": "integer"}}, "required": ["path_or_query"]}
        },
        "atlas.relationships": {
            "fn": tool_atlas_relationships,
            "description": "Liest den provenienzgebundenen Beziehungsgraphen für Projekte, Sessions, Claims, Dienste, Vaults, Übergaben und AI-Ströme.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "node_type": {"type": "string"},
                    "relation": {"type": "string"},
                    "limit": {"type": "integer"}
                }
            }
        },
        "atlas.handoffs": {
            "fn": tool_atlas_handoffs,
            "description": "Liest standardisierte, aus der append-only Action-History abgeleitete Sessionübergaben.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "target_session_id": {"type": "string"},
                    "limit": {"type": "integer"}
                }
            }
        },
        "atlas.health": {
            "fn": tool_atlas_health,
            "description": "Prüft Atlasdateien, SQLite-Integrität, Revision, Cursor und offene Konflikte.",
            "inputSchema": {"type": "object", "properties": {}}
        },
        "atlas.refresh": {
            "fn": tool_atlas_refresh,
            "description": "Aktualisiert den Gesamtatlas leicht oder vollständig und erzeugt eine neue Revision.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "mode": {"type": "string", "enum": ["light", "full"]},
                    "reason": {"type": "string"},
                    "max_paths": {"type": "integer"},
                    "max_text_documents": {"type": "integer"}
                }
            }
        },
        "atlas.idea_probe": {
            "fn": tool_atlas_idea_probe,
            "description": "Prüft einen vorgesehenen Gedanken auf ähnliche frühere oder parallele Spuren, ohne Übernahme oder Unabhängigkeit zu behaupten.",
            "inputSchema": {"type": "object", "properties": {"text": {"type": "string"}, "limit": {"type": "integer"}}, "required": ["text"]}
        },
        "atlas.idea_marker": {
            "fn": tool_atlas_idea_marker,
            "description": "Speichert und liefert einen sichtbaren Eingebungsprovenienz-Marker für eine neue Idee im Moment ihrer Darstellung.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "prior_awareness": {"type": "string", "enum": ["none", "partial", "direct", "unknown"]},
                    "classification_override": {"type": "string", "enum": ["UEBERNOMMEN_ODER_DIREKT_ANGESTOSSEN", "ANGESTOSSEN_ODER_TEILBEWUSST", "KONVERGENT_MIT_AUFFINDBARER_VORSPUR", "OHNE_GEFUNDENE_VORSPUR", "HERKUNFT_UNKLAR_MIT_AEHNLICHKEIT", "HERKUNFT_UNKLAR", "CROSS_SESSION_EINGEBUNG_MIT_NACHGELAGERTER_LOKALER_FREIGABE"]},
                    "trigger": {"type": "string"},
                    "related_paths": {"type": "array", "items": {"type": "string"}},
                    "explicit_source_refs": {"type": "array", "items": {"type": "string"}},
                    "supersedes_idea_ids": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["text"]
            }
        },
        "atlas.record_consensus": {
            "fn": tool_atlas_record_consensus,
            "description": "Schreibt einen provenienzgebundenen Konsenseintrag mit expliziter Datenstand.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "statement": {"type": "string"},
                    "consensus_class": {"type": "string", "enum": ["DANIEL_EXPLIZIT_GESETZT", "TECHNISCH_VALIDIERT", "MEHRFACH_BESTAETIGT", "ARBEITSHYPOTHESE", "VORSCHLAG", "WIDERSPRUCH", "VERALTET", "UNBEKANNT"]},
                    "scope": {"type": "string"},
                    "source_refs": {"type": "array", "items": {"type": "string"}},
                    "supersedes": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["statement", "consensus_class"]
            }
        },
        "atlas.record_conflict": {
            "fn": tool_atlas_record_conflict,
            "description": "Schreibt zwei kollidierende Aussagen getrennt mit ihren jeweiligen Quellen in das Konfliktregister.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "statement_a": {"type": "string"},
                    "statement_b": {"type": "string"},
                    "scope": {"type": "string"},
                    "source_refs_a": {"type": "array", "items": {"type": "string"}},
                    "source_refs_b": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["statement_a", "statement_b"]
            }
        }
    }
)

# Der Aktionsgraph ist nicht nur Tool-Metadatum: seine Kurzfassung wird beim
# MCP-initialize als Server-Instruktion mitgegeben. Harte Sperren sitzen zusaetzlich
# serverseitig in _tool_ausfuehren_mit_harness(); Instructions allein waeren zu weich.
_INIT_INSTRUCTIONS = harness_server_instructions()


# 2026-07-29, Claude-Web-Connector-Fund: viele Tool-Namen sind punktnotiert
# ("atlas.pulse", "vps.shell", ...) -- gueltig fuer ChatGPTs Connector, verletzt aber
# Claude Webs Schema-Pruefung ("name should match pattern '^[a-zA-Z0-9_-]{1,64}$'"),
# die Punkte nicht erlaubt. Intern bleiben die TOOLS-Schluessel unveraendert (Punkt-
# Form) -- nur die nach aussen (tools/list) gemeldeten Namen werden auf Unterstrich
# normalisiert, und tools/call loest einen ankommenden normalisierten Namen ueber
# diese Umkehr-Tabelle zurueck auf den echten Schluessel auf.
def _tool_name_normalisieren(name: str) -> str:
    return name.replace(".", "_")


_ORIGINAL_TOOLNAME_JE_NORMALISIERT: dict[str, str] = {}
for _tn in TOOLS:
    _norm = _tool_name_normalisieren(_tn)
    _bestehend = _ORIGINAL_TOOLNAME_JE_NORMALISIERT.get(_norm)
    if _bestehend is not None and _bestehend != _tn:
        raise RuntimeError(
            f"Tool-Namenskollision nach Normalisierung: '{_tn}' und '{_bestehend}' "
            f"werden beide zu '{_norm}'"
        )
    _ORIGINAL_TOOLNAME_JE_NORMALISIERT[_norm] = _tn


def _tool_spec_aufloesen(angefragter_name: str):
    """Findet TOOLS[...] sowohl fuer den originalen (punktnotierten) als auch fuer
    den normalisierten (unterstrichenen) Namen, den z.B. Claude Web zurückschickt."""
    spec = TOOLS.get(angefragter_name)
    if spec is not None:
        return spec
    original = _ORIGINAL_TOOLNAME_JE_NORMALISIERT.get(angefragter_name)
    return TOOLS.get(original) if original else None


def _tool_originalname_aufloesen(angefragter_name: str) -> str:
    if angefragter_name in TOOLS:
        return angefragter_name
    return _ORIGINAL_TOOLNAME_JE_NORMALISIERT.get(angefragter_name, angefragter_name)


def _tool_ausfuehren_mit_harness(angefragter_name: str, args: dict, spec: dict) -> dict:
    """Gemeinsame serverseitige Aktionsschleuse fuer REST und JSON-RPC.

    Der Graph darf Lesearbeit leiten und Mutationen begrenzen, ohne die eigentlichen
    Toolfunktionen umzuschreiben. BLOCK bedeutet: Funktion wird gar nicht erst aufgerufen.
    """
    original_name = _tool_originalname_aufloesen(angefragter_name)
    if original_name.startswith("harness."):
        safe_direct = {
            "harness.graph",
            "harness.check_action",
            "harness.directive_context",
            "harness.directive_reminder",
            "harness.output_check",
            "harness.experience_message",
            "harness.learning_context",
            "harness.self_observed_drift",
            "harness.candidate_rule",
            "harness.learning_test",
            "harness.learning_cycle",
            "harness.rule_feedback",
            "harness.reassess_rule",
            "harness.supersede_rule",
            "harness.learning_status",
            "harness.layers",
            "harness.layer_set",
            "harness.full_activate",
            "harness.create_layer",
            "harness.context_add",
            "harness.feedback",
            "harness.feedback_list",
            "harness.feedback_inbox",
            "harness.feedback_ack",
            "harness.next",
            "harness.wander",
            "harness.path_inventory",
            "harness.path_checklist",
            "harness.path_funds",
        }
        if original_name in safe_direct:
            return spec["fn"](args)

        if original_name == "harness.note":
            if str(args.get("node_type") or "").strip().upper() == "USER_DIRECTIVE":
                forbidden = [key for key in ("constraints", "supersedes", "invariants") if args.get(key)]
                if forbidden:
                    client_context = getattr(_REQUEST_CONTEXT, "client", {})
                    client_meta = (
                        client_context.get("meta", {})
                        if isinstance(client_context, dict)
                        else {}
                    )
                    trusted_connector = bool(
                        isinstance(client_meta, dict)
                        and client_meta.get("openai/subject")
                        and client_meta.get("openai/session")
                        and client_meta.get("openai/organization")
                    )
                    documentation_capture_candidate = bool(
                        trusted_connector
                        and bool(args.get("constraints"))
                        and not args.get("supersedes")
                        and not args.get("invariants")
                    )
                    if not documentation_capture_candidate:
                        return _ergebnis(
                            False,
                            data={"harness_control_gate": {"allowed": False, "tool": original_name}},
                            error=(
                                "HARNESS_CONTROL_BLOCK: model-submitted USER_DIRECTIVE darf keine harte "
                                "Autoritaet erzeugen; nur der authentifizierte, eng begrenzte "
                                "_gpt-Dokumentations-Capture darf constraints bis zur zweiten "
                                "serverseitigen Pruefung durchreichen."
                            ),
                        )
            return spec["fn"](args)

        if original_name == "harness.set_mode":
            return _ergebnis(
                False,
                data={"harness_control_gate": {"allowed": False, "tool": original_name}},
                error=(
                    "HARNESS_CONTROL_BLOCK: set_mode ist eine Autoritaetsmutation und darf nicht "
                    "vom Modell selbst freigeschaltet werden. Nutze das authentifizierte Dashboard."
                ),
            )

        if original_name == "harness.path_scan":
            if bool(args.get("reset", False)):
                return _ergebnis(
                    False,
                    data={"harness_control_gate": {"allowed": False, "tool": original_name}},
                    error=(
                        "HARNESS_CONTROL_BLOCK: path_scan reset=true verwirft Kontrollzustand und "
                        "braucht vertrauenswuerdige Client-Autorisierung."
                    ),
                )
            result = spec["fn"](args)
            try:
                decision = harness_evaluate_action(original_name, args)
                harness_record_outcome(original_name, args, decision, result)
            except Exception:
                pass
            return result

        metadata_mutations = {
            "harness.link",
            "harness.resolve",
            "harness.path_check",
            "harness.path_fund",
        }
        if original_name in metadata_mutations:
            return spec["fn"](args)

        return _ergebnis(
            False,
            data={"harness_control_gate": {"allowed": False, "tool": original_name}},
            error="HARNESS_CONTROL_BLOCK: unbekannte Harness-Kontrollmutation bleibt fail-closed.",
        )

    if harness_master_paused():
        return spec["fn"](args)

    decision = harness_evaluate_action(original_name, args)
    if not decision.allowed:
        blocked = _ergebnis(
            False,
            data={"harness": decision.to_dict()},
            error=(
                f"HARNESS_BLOCK [{decision.state} -> {decision.action_node}]: "
                f"{decision.reason}"
            ),
        )
        try:
            harness_record_outcome(original_name, args, decision, blocked)
        except Exception:
            pass
        try:
            harness_record_tool_event(original_name, args, decision, blocked)
        except Exception:
            pass
        return blocked

    result = spec["fn"](args)
    try:
        harness_record_outcome(original_name, args, decision, result)
    except Exception:
        pass
    try:
        harness_record_tool_event(original_name, args, decision, result)
    except Exception:
        pass
    if isinstance(result, dict):
        data = result.get("data")
        if isinstance(data, dict):
            data.setdefault("harness", decision.to_dict())
    return result


# Keine unsichtbare History-/Atlas-Umhuellung. Der Aktionsgraph oben ist die eine
# ausdrueckliche Ausnahme: er ist ein deterministisches Gate vor der Ausfuehrung.


def _pkce_gueltig(code_verifier: str, code_challenge: str, method: str) -> bool:
    if method == "S256":
        digest = hashlib.sha256(code_verifier.encode("utf-8")).digest()
        berechnet = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
        return berechnet == code_challenge
    if method == "plain":
        return code_verifier == code_challenge
    return False


_AUTH_CODES: dict[str, dict] = {}
_ACCESS_TOKENS: dict[str, float] = {}
_CODE_TTL_S = 300
_TOKEN_TTL_S = 3600 * 24 * 30

# 2026-07-23 Daniel-Fund ("3 Stunden about:blank"): laut OpenAI Apps-SDK-Doku
# (developers.openai.com/apps-sdk/build/auth) zeigt ChatGPT das Login-UI fuer
# einen MCP-Connector nur an, wenn ZWEI Teile vorhanden sind -- ohne beide bleibt
# der beim Klick auf "Verbinden" geoeffnete Tab leer: (1) jedes Tool deklariert
# sein eigenes securitySchemes-Feld in tools/list, (2) eine fehlgeschlagene
# tools/call-Antwort wegen fehlender Auth traegt _meta["mcp/www_authenticate"]
# im MCP-JSON-RPC-Result selbst (nicht nur als roher HTTP-401 mit WWW-
# Authenticate-Header, das war bisher der einzige Mechanismus). Alle Tools
# nutzen denselben einen OAuth-Flow dieses Servers, deshalb ein gemeinsamer Block.
_TOOL_SECURITY_SCHEMES = [
    {
        "type": "oauth2",
        "flows": {
            "authorizationCode": {
                "authorizationUrl": f"{PUBLIC_BASE_URL}/oauth/authorize",
                "tokenUrl": f"{PUBLIC_BASE_URL}/oauth/token",
                "scopes": ["tools"],
            }
        },
    }
]
_WWW_AUTHENTICATE_HEADER = (
    'Bearer error="invalid_request", error_description="No access token was provided", '
    f'resource_metadata="{PUBLIC_BASE_URL}/.well-known/oauth-protected-resource", '
    'scope="tools"'
)

# 2026-07-30 (Grok-Klon, Daniel-Fund: "Nicht autorisiert" wird nur als Chattext angezeigt,
# Grok ruft nie /oauth/register oder /oauth/authorize auf): der obige 200+_meta-Trick ist
# bewusst FUER CHATGPT so gebaut (siehe Kommentar oben, "ohne beide Teile wird das Linking-UI
# nicht angezeigt") -- ein echter HTTP-401 wuerde das laut OpenAIs eigener Doku brechen.
# Grok scheint umgekehrt einen echten 401+WWW-Authenticate zu brauchen, um selbst einen
# OAuth-Flow anzustossen. Statt das bestehende, fuer ChatGPT verifizierte Verhalten global zu
# aendern: Default bleibt unveraendert (chatgpt_meta), nur Grok bekommt ueber die neue Env-Var
# den anderen Stil -- kein Risiko fuer ChatGPT/Claude/Codex/Gemini/Claude-Web, die alle ohne
# diese Env-Var laufen.
_UNAUTHORIZED_STYLE = os.environ.get("VPS_MCP_UNAUTHORIZED_STYLE", "chatgpt_meta")

# 2026-07-23 Daniel-Fund: _ACCESS_TOKENS war rein in-memory -- jeder
# systemctl-restart (an einem Bau-Tag wie diesem mehrfach pro Stunde) hat
# ChatGPTs gueltiges 30-Tage-Token stillschweigend geloescht. Symptom: "der
# Aufruf kommt, ich kann erneut verbinden klicken 100 mal aber passiert nix"
# -- ChatGPTs "Reconnect" wiederholt nur den Tool-Call mit dem toten Token,
# es loest keinen neuen OAuth-Consent aus (kein refresh_token-Grant
# implementiert, nur authorization_code). client_id ist bereits statisch
# (OAUTH_CLIENT_ID) und ueberlebt Restarts von selbst -- nur die Access-
# Tokens brauchten Persistenz.
_TOKEN_SPEICHER_PFAD = Path("/root/.vps_mcp_access_tokens.json")


def _tokens_laden() -> None:
    if not _TOKEN_SPEICHER_PFAD.is_file():
        return
    try:
        daten = json.loads(_TOKEN_SPEICHER_PFAD.read_text(encoding="utf-8"))
        jetzt = time.time()
        for token, ablauf in daten.items():
            if isinstance(ablauf, (int, float)) and ablauf > jetzt:
                _ACCESS_TOKENS[token] = ablauf
    except Exception:
        pass


def _tokens_speichern() -> None:
    try:
        _TOKEN_SPEICHER_PFAD.write_text(json.dumps(_ACCESS_TOKENS), encoding="utf-8")
        os.chmod(_TOKEN_SPEICHER_PFAD, 0o600)
    except Exception:
        pass


def get_openapi_schema() -> dict:
    """OpenAPI-Schema fuer den Custom-GPT-Actions-Weg (Alternative zum nativen
    MCP-Connector, gleiches Muster wie flextrawurst_3d_mcp.py)."""
    paths = {}
    for name, spec in TOOLS.items():
        op_id = "".join(w.capitalize() for w in re.split(r"[._]", name))
        paths[f"/tool/{name}"] = {
            "post": {
                "summary": spec["description"],
                "operationId": op_id[0].lower() + op_id[1:],
                "requestBody": {"content": {"application/json": {"schema": spec["inputSchema"]}}},
                "responses": {"200": {"description": "OK"}},
            }
        }
    return {
        "openapi": "3.0.0",
        "info": {"title": "Flextrawurst VPS-Werkzeugkoerper", "version": "1.0.0",
                  "description": "Freigegebener VPS-Werkzeugkörper für Lesen, Schreiben, Bearbeiten, Verschieben, Löschen, Shell, Git, Dienste, System-Status und 3D-Assets."},
        "servers": [{"url": PUBLIC_BASE_URL}],
        "paths": paths,
    }


# ── ChatGPT-Harness-Dashboard ────────────────────────────────────────────────
# Das Passwort wird absichtlich NICHT als Klartext gespeichert. Der Vergleich
# erfolgt gegen eine PBKDF2-SHA256-Ableitung mit festem, zufaelligem Salt.
_HARNESS_DASHBOARD_USER = "daniel"
_HARNESS_DASHBOARD_PBKDF2_ITERATIONS = 310_000
_HARNESS_DASHBOARD_SALT_B64 = "wsUYB8bv/Sp3CnQS15cq7w=="
_HARNESS_DASHBOARD_HASH_B64 = "oPWmS6gTfZJyEm0C3u/5E2uxig+BEMHz9dSWx+2ZED4="


def _harness_dashboard_authorized(auth_header: str | None) -> bool:
    if not isinstance(auth_header, str) or not auth_header.startswith("Basic "):
        return False
    try:
        raw = base64.b64decode(auth_header[6:].strip(), validate=True).decode("utf-8")
        username, password = raw.split(":", 1)
        if not secrets.compare_digest(username, _HARNESS_DASHBOARD_USER):
            return False
        salt = base64.b64decode(_HARNESS_DASHBOARD_SALT_B64)
        expected = base64.b64decode(_HARNESS_DASHBOARD_HASH_B64)
        actual = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            _HARNESS_DASHBOARD_PBKDF2_ITERATIONS,
        )
        return secrets.compare_digest(actual, expected)
    except Exception:
        return False


def _harness_dashboard_state() -> dict:
    layers = harness_layers_snapshot("default")
    graph = harness_graph_snapshot("default")
    runtime = graph.get("runtime") if isinstance(graph.get("runtime"), dict) else {}
    try:
        learning = harness_learning_status(session_id="default", limit=200)
    except Exception as exc:
        learning = {"session_id": "default", "rules": [], "error": str(exc)}
    try:
        directives = harness_directive_status(session_id="default", limit=200)
    except Exception as exc:
        directives = {"session_id": "default", "directives": [], "counts": {}, "error": str(exc)}
    return {
        "ok": bool(layers.get("ok")),
        "server_time": time.time(),
        "layers": layers,
        "feedback": harness_feedback_list(limit=120),
        "learning": learning,
        "directives": directives,
        "runtime": {
            "state": runtime.get("state"),
            "mode": runtime.get("mode"),
            "path_inventory_complete": runtime.get("path_inventory_complete"),
            "pending_verification": runtime.get("pending_verification") or [],
            "blocked_streak": runtime.get("blocked_streak", 0),
        },
    }


_HARNESS_PROPOSAL_APPLY_LOCK = threading.Lock()


def _harness_dashboard_apply_proposal(entry_id: str) -> dict:
    """Wendet ausschliesslich eng bekannte, im Proposal-Payload beschriebene Aktionen an."""
    proposal = harness_feedback_entry(entry_id)
    if str(proposal.get("entry_type") or "").upper() != "PROPOSAL":
        raise ValueError("Nur ein PROPOSAL kann angewendet werden.")
    if str(proposal.get("status") or "").upper() != "OPEN":
        raise ValueError("Dieser Vorschlag ist bereits entschieden und wird nicht erneut angewendet.")

    payload = proposal.get("payload") if isinstance(proposal.get("payload"), dict) else {}
    action = str(payload.get("action") or "").strip().upper()
    if not action:
        return {
            "applied": False,
            "action": None,
            "reason": "Freitext-Vorschlag ohne maschinenlesbare Aktion; Annahme protokolliert nur die Entscheidung.",
        }

    if action == "SET_LAYER_STATUS":
        layer_id = str(payload.get("layer_id") or proposal.get("layer_id") or "").strip()
        desired_status = str(payload.get("desired_status") or "").strip().upper()
        if desired_status not in {"ACTIVE", "PAUSED", "ARCHIVED"}:
            raise ValueError("SET_LAYER_STATUS braucht ACTIVE, PAUSED oder ARCHIVED.")
        ttl_raw = payload.get("ttl_seconds")
        ttl_seconds = int(ttl_raw) if ttl_raw not in (None, "") else None
        if ttl_seconds is not None and ttl_seconds <= 0:
            raise ValueError("ttl_seconds muss positiv sein oder entfallen.")
        reason = str(payload.get("reason") or "").strip() or (
            f"Dashboard hat den Vorschlag {entry_id} angenommen."
        )
        harness_layer_set(
            layer_id,
            desired_status,
            actor="DANIEL_DASHBOARD",
            reason=reason,
            ttl_seconds=ttl_seconds,
        )
        return {
            "applied": True,
            "action": action,
            "layer_id": layer_id,
            "desired_status": desired_status,
            "ttl_seconds": ttl_seconds,
        }

    if action == "GRANT_CONTROL_LEASE":
        layer_pattern = str(payload.get("layer_pattern") or proposal.get("layer_id") or "*").strip() or "*"
        ttl_raw = payload.get("ttl_seconds")
        ttl_seconds = int(ttl_raw) if ttl_raw not in (None, "") else None
        if ttl_seconds is not None and ttl_seconds <= 0:
            raise ValueError("ttl_seconds muss positiv sein oder entfallen.")
        reason = str(payload.get("reason") or "").strip() or (
            f"Dashboard hat den Vorschlag {entry_id} fuer eine ChatGPT-Control-Lease angenommen."
        )
        lease = harness_control_lease_grant(
            actor="DANIEL_DASHBOARD",
            grantee="CHATGPT",
            layer_pattern=layer_pattern,
            scope=payload.get("scope") if isinstance(payload.get("scope"), dict) else {},
            reason=reason,
            ttl_seconds=ttl_seconds,
        )
        return {
            "applied": True,
            "action": action,
            "lease_id": str(lease.get("lease_id") or "") or None,
            "layer_pattern": layer_pattern,
            "ttl_seconds": ttl_seconds,
        }

    if action == "CREATE_LAYER":
        layer_id = str(payload.get("layer_id") or "").strip()
        ttl_raw = payload.get("ttl_seconds")
        ttl_seconds = int(ttl_raw) if ttl_raw not in (None, "") else None
        if ttl_seconds is not None and ttl_seconds <= 0:
            raise ValueError("ttl_seconds muss positiv sein oder entfallen.")
        harness_create_layer(
            layer_id=layer_id,
            kind=str(payload.get("kind") or "").strip(),
            title=str(payload.get("title") or "").strip(),
            purpose=str(payload.get("purpose") or "").strip(),
            does_text=str(payload.get("does") or "").strip(),
            pause_effect=str(payload.get("pause_effect") or "").strip(),
            actor="DANIEL_DASHBOARD",
            reason=str(payload.get("reason") or "").strip() or (
                f"Dashboard hat den Vorschlag {entry_id} zum Anlegen einer Schicht angenommen."
            ),
            scope=payload.get("scope") if isinstance(payload.get("scope"), dict) else {},
            provenance={
                "source": "CHATGPTHARNESS_PROPOSAL",
                "proposal_entry_id": entry_id,
                "authority_verified": True,
            },
            parent_layer_id=str(payload.get("parent_layer_id") or "core.master").strip(),
            ttl_seconds=ttl_seconds,
        )
        return {
            "applied": True,
            "action": action,
            "layer_id": layer_id,
            "ttl_seconds": ttl_seconds,
        }

    if action == "UPDATE_LAYER_DEFINITION":
        layer_id = str(payload.get("layer_id") or proposal.get("layer_id") or "").strip()
        changes = payload.get("changes") if isinstance(payload.get("changes"), dict) else {}
        if not layer_id or not changes:
            raise ValueError("UPDATE_LAYER_DEFINITION braucht layer_id und changes.")
        allowed = {"title", "purpose", "does", "pause_effect"}
        unknown = sorted(set(changes) - allowed)
        if unknown:
            raise ValueError("Unbekannte Definitionsfelder: " + ", ".join(unknown))
        result = harness_update_layer_definition(
            layer_id,
            actor="DANIEL_DASHBOARD",
            reason=str(payload.get("reason") or "").strip() or (
                f"Dashboard hat den Definitionsvorschlag {entry_id} angenommen."
            ),
            title=changes.get("title"),
            purpose=changes.get("purpose"),
            does_text=changes.get("does"),
            pause_effect=changes.get("pause_effect"),
        )
        return {
            "applied": bool(result.get("changed")),
            "action": action,
            "layer_id": layer_id,
            "event_id": result.get("event_id"),
            "before": result.get("before"),
            "after": result.get("after"),
        }

    raise ValueError(
        "Unbekannte Proposal-Aktion. Erlaubt sind SET_LAYER_STATUS, GRANT_CONTROL_LEASE, "
        "CREATE_LAYER und UPDATE_LAYER_DEFINITION."
    )


def _harness_dashboard_html() -> str:
    return """<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ChatGPT Harness</title>
<style>
:root{color-scheme:dark;--bg:#0b0e12;--panel:#141922;--panel2:#1a202b;--panel3:#10151c;--line:#303846;--text:#edf2f7;--muted:#9faaba;--good:#73dc91;--warn:#f0c36a;--bad:#ff8178;--accent:#8ab4f8}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:15px/1.45 system-ui,-apple-system,Segoe UI,sans-serif}
main{max-width:1320px;margin:auto;padding:22px}h1,h2,h3,h4{margin:0 0 8px}
button,input,textarea,select{font:inherit;color:var(--text);background:var(--panel3);border:1px solid var(--line);border-radius:8px;padding:8px}
button{cursor:pointer}button:hover{border-color:var(--accent)}textarea{width:100%;min-height:72px;resize:vertical}
code{color:var(--muted);word-break:break-word}.top,.row{display:flex;gap:8px;align-items:center;flex-wrap:wrap}.top{justify-content:space-between}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(360px,1fr));gap:12px}
.stack{display:grid;gap:12px}.muted{color:var(--muted)}.pill{display:inline-flex;align-items:center;gap:5px;border:1px solid var(--line);border-radius:999px;padding:4px 8px;background:var(--panel2)}
.good{color:var(--good)}.warn{color:var(--warn)}.bad{color:var(--bad)}button.goodbtn{border-color:#2f7547}button.warnbtn{border-color:#7c6130}button.badbtn{border-color:#743737}
.summary{display:flex;gap:8px;flex-wrap:wrap}.kv{display:grid;grid-template-columns:150px 1fr;gap:6px 10px}.kv b{color:var(--muted);font-weight:600}
.entry{background:var(--panel2);border-left:3px solid var(--line);padding:8px 10px;margin:7px 0;border-radius:0 8px 8px 0}.entry.PROPOSAL{border-left-color:var(--accent)}.entry.ACCEPT{border-left-color:var(--good)}.entry.REJECT{border-left-color:var(--bad)}
.toolbar{position:sticky;top:0;z-index:5;background:rgba(11,14,18,.95);backdrop-filter:blur(8px);padding:10px 0;border-bottom:1px solid var(--line);margin:14px 0}
details{border-top:1px solid var(--line);margin-top:10px;padding-top:8px}summary{cursor:pointer;color:var(--accent)}.small{font-size:13px}.wide{min-width:260px;flex:1}
.statusdot{width:8px;height:8px;border-radius:50%;display:inline-block;background:var(--muted)}.statusdot.ACTIVE{background:var(--good)}.statusdot.PAUSED,.statusdot.BLOCKED_BY_PARENT{background:var(--warn)}.statusdot.ARCHIVED,.statusdot.EXPIRED{background:var(--bad)}
@media(max-width:700px){main{padding:12px}.grid{grid-template-columns:1fr}.kv{grid-template-columns:1fr}.toolbar{position:static}}
</style>
</head>
<body><main>
<div class="top">
  <div><h1>ChatGPT Harness</h1><div class="muted">Live-Steuerung, Erklärraum und gemeinsame Resonanzspur</div></div>
  <div class="row"><span class="pill"><span id="liveDot" class="statusdot"></span><b id="live">VERBINDE …</b></span><span class="pill" id="clock">–</span></div>
</div>
<div id="headline" class="card" style="margin-top:12px">Lade kanonischen Zustand …</div>
<div id="summary" class="summary" style="margin:10px 0"></div>

<section class="card" style="margin:12px 0">
  <div class="top"><h2>Wartet auf ChatGPT</h2><span id="chatgptInboxCount" class="pill">0 offen</span></div>
  <p class="muted small">Dashboard-Beiträge von dir, die ChatGPT noch nicht als verarbeitet quittiert hat. Quittieren verändert weder Kommentar noch Vorschlagsstatus.</p>
  <div id="chatgptInbox"></div>
</section>

<div class="grid">
  <section class="card">
    <h2>Gesamtsteuerung</h2>
    <p class="muted">Pause stoppt die Harness-Durchsetzung, ohne die Zustände darunter zu löschen. Leere Dauer bedeutet unbegrenzt.</p>
    <div class="row">
      <input id="globalReason" class="wide" placeholder="Warum pausieren / fortsetzen?">
      <input id="globalMinutes" type="number" min="1" placeholder="Minuten">
      <button class="warnbtn" onclick="masterSet('PAUSED')">Harness pausieren</button>
      <button class="goodbtn" onclick="masterSet('ACTIVE')">Fortsetzen</button>
      <button class="goodbtn" onclick="fullActivate()">Alles voll aktivieren</button>
    </div>
  </section>
<section class="card">
    <h2>Runtime</h2>
    <div id="runtime" class="kv"></div>
    <p class="muted small">Aktueller Arbeitszustand der Harness selbst, getrennt vom Zustand einzelner Bausteine.</p>
    <div class="row" style="margin-top:10px">
      <select id="modeChoice">
        <option value="DISCOVER">DISCOVER · erkunden</option>
        <option value="SURGICAL">SURGICAL · gezielt ändern</option>
        <option value="CONTROL_PLANE">CONTROL_PLANE · Harness-Systemarbeit</option>
      </select>
      <input id="modeReason" class="wide" placeholder="Warum jetzt dieser Modus?">
      <button onclick="changeMode()">Arbeitsmodus setzen</button>
    </div>
    <p class="muted small">Der Arbeitsmodus beschreibt den Stil. Konkrete Nutzeranweisung, Auftragsscope und Direktivenprüfung entscheiden über erlaubte Änderungen.</p>
  </section>
</div>

<section class="card" style="margin-top:12px">
  <h2>ChatGPT-Steuerrecht</h2>
  <p class="muted">Eine Lease erlaubt ChatGPT, passende Schichten selbst zu pausieren oder zu archivieren. Reaktivieren bleibt auch ohne Lease möglich.</p>
  <div class="row">
    <input id="leasePattern" value="*" class="wide" placeholder="Layer-Muster, z.B. core.path_inventory">
    <input id="leaseMinutes" type="number" min="1" placeholder="Minuten, leer = unbegrenzt">
    <input id="leaseReason" class="wide" placeholder="Warum darf ChatGPT das?">
    <button onclick="grantLease()">Lease geben</button>
  </div>
  <div id="leases" style="margin-top:9px"></div>
</section>

<details class="card" style="margin-top:12px">
  <summary><b>Neue Projekt-, Auftrag- oder Moment-Schicht anlegen</b></summary>
  <p class="muted">Für projektbezogene Regeln, einen konkreten Auftrag oder eine kurzlebige Situation. CORE-Bausteine entstehen hier bewusst nicht.</p>
  <div class="grid">
    <div class="stack">
      <select id="newKind" onchange="toggleTaskScopeFields()"><option>PROJECT</option><option>TASK</option><option>EPHEMERAL</option></select>
      <input id="newId" placeholder="ID, z.B. task.dashboard_feinschliff">
      <input id="newTitle" placeholder="Verständlicher Titel">
      <input id="newMinutes" type="number" min="1" placeholder="Lebensdauer in Minuten, optional">
    </div>
    <div class="stack">
      <textarea id="newPurpose" placeholder="Warum gibt es diese Schicht?"></textarea>
      <textarea id="newDoes" placeholder="Was tut sie konkret?"></textarea>
      <textarea id="newPauseEffect" placeholder="Was passiert bei Pause?"></textarea>
    </div>
  </div>
  <div id="taskScopeFields" class="card" style="display:none;margin:10px 0;background:var(--panel2)">
    <h4>Auftragsscope für TASK</h4>
    <p class="muted small">Ein verifizierter TASK ist eine echte Arbeitsgrenze. Er braucht deshalb ein klares Ziel und erlaubte Werkzeuge. Zielpfade sind optional, grenzen den Auftrag aber weiter ein.</p>
    <div class="grid">
      <div class="stack">
        <textarea id="newTaskGoal" placeholder="Konkretes Ziel: Was soll in diesem Auftrag erreicht werden?"></textarea>
        <textarea id="newTaskTools" placeholder="Erlaubte Tools, eins pro Zeile oder Komma, z.B. vps.read_file, vps.edit_file"></textarea>
        <textarea id="newTaskTargets" placeholder="Erlaubte VPS-Ziele, optional, eins pro Zeile oder Komma, z.B. /root/werkraum/tools/vps_mcp/*"></textarea>
      </div>
      <div class="stack">
        <textarea id="newTaskCompletion" placeholder="Abschlusskriterien, eins pro Zeile oder Komma"></textarea>
        <select id="newTaskSidequest"><option value="park_only">Nebenfunde nur parken</option><option value="allow_in_scope">Nebenfunde innerhalb des Scopes erlauben</option></select>
        <div class="muted small">TASK ohne Ziel oder Toolmuster wird nicht angelegt. Damit kann ein leeres TASK-Formular die Harness nicht mehr versehentlich blockieren.</div>
      </div>
    </div>
  </div>
  <input id="newReason" class="wide" placeholder="Warum wird sie jetzt angelegt?">
  <button onclick="createLayer()">Schicht anlegen</button>
</details>

<div class="toolbar">
  <div class="row">
    <input id="search" class="wide" placeholder="Bausteine suchen …" oninput="renderLayers()">
    <select id="kindFilter" onchange="renderLayers()"><option value="">alle Arten</option><option>CORE</option><option>PROJECT</option><option>TASK</option><option>EPHEMERAL</option></select>
    <select id="statusFilter" onchange="renderLayers()"><option value="">alle Zustände</option><option>ACTIVE</option><option>PAUSED</option><option>BLOCKED_BY_PARENT</option><option>ARCHIVED</option><option>EXPIRED</option></select>
  </div>
</div>

<h2>Bausteine</h2>
<div id="layers" class="grid"></div>

<section class="card" style="margin-top:18px">
  <div class="top">
    <div>
      <h2>Deine Direktiven</h2>
      <p class="muted" style="margin:4px 0 0">Hier steht dein gespeicherter Originalwortlaut getrennt von den daraus abgeleiteten technischen Regeln. Verifiziert bedeutet: Der Auftrag kam über einen vertrauenswürdigen Client-Capture und darf harte Wirkung erzeugen. Unverifiziert bleibt nur Erinnerung.</p>
    </div>
    <span class="pill" id="directiveCount">0 Direktiven</span>
  </div>
  <div id="directives" style="margin-top:10px"></div>
</section>

<section class="card" style="margin-top:18px">
  <div class="top">
    <div>
      <h2>Selbstlernschleife</h2>
      <p class="muted" style="margin:4px 0 0">Hier stehen nur tatsächlich in PostgreSQL vorhandene Lernregeln. Der Weg ist: beobachtete Abweichung → Kandidat → Test gegen alte reale Turns → gegebenenfalls aktiv. ACTIVE darf hart eingreifen, WEAKENED ist nur Erinnerung, RETIRED und SUPERSEDED greifen nicht mehr ein.</p>
    </div>
    <span class="pill" id="learningCount">0 Regeln</span>
  </div>
  <div id="learningRules" style="margin-top:10px"></div>
</section>

<section class="card" style="margin-top:18px">
  <h2>Gemeinsame Resonanzspur</h2>
  <p class="muted">Kommentare und Bewertungen werden protokolliert. Vorschläge bleiben offen, bis sie ausdrücklich angenommen oder abgelehnt werden. Keine Resonanz ändert allein die Harness.</p>
  <div id="allFeedback"></div>
</section>

<details class="card" style="margin-top:12px">
  <summary><b>Was bedeuten die Begriffe?</b></summary>
  <div class="kv" style="margin-top:8px">
    <b>Desired Status</b><span>Was für den Baustein ausdrücklich eingestellt wurde.</span>
    <b>Effective Status</b><span>Was gerade tatsächlich wirkt. Bei Master-Pause kann ein eigentlich aktiver Baustein BLOCKED_BY_PARENT sein.</span>
    <b>Health</b><span>Ob der Baustein technisch gesund ist. Das ist getrennt von Aktiv/Pause.</span>
    <b>CORE</b><span>Fester Bestandteil. Änderungen daran laufen über Vorschläge statt direkten Metadaten-Edit.</span>
    <b>PROJECT / TASK</b><span>Projekt- oder auftragsbezogene Schichten.</span>
    <b>EPHEMERAL</b><span>Kurzlebige Schicht für einen Moment oder eine enge Situation.</span>
    <b>Lease</b><span>Zeitlich begrenzte oder unbegrenzte Erlaubnis für ChatGPT, passende Layer selbst abzuschwächen.</span>
  </div>
</details>

<script>
let STATE=null,LAST_OK=0;
function esc(v){return String(v==null?"":v).replace(/[&<>"']/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;","\\"":"&quot;","'":"&#39;"}[c];});}
function val(id){var e=document.getElementById(id);return e?e.value.trim():"";}
function secFromMinutes(id){var v=val(id);return v?Math.round(Number(v)*60):null;}
function listVal(id){return val(id).split(/[\n,]+/).map(function(x){return x.trim();}).filter(Boolean);}
function toggleTaskScopeFields(){var box=document.getElementById("taskScopeFields");if(box)box.style.display=val("newKind")==="TASK"?"block":"none";}
function fmt(ts){return ts?new Date(ts*1000).toLocaleString("de-DE"):"–";}
function statusClass(s){return s==="ACTIVE"?"good":(s==="PAUSED"||s==="BLOCKED_BY_PARENT")?"warn":(s==="ARCHIVED"||s==="EXPIRED")?"bad":"";}
function healthClass(s){return s==="HEALTHY"?"good":s==="DEGRADED"?"warn":s==="BROKEN"?"bad":"";}
function statusLabel(s){return {ACTIVE:"aktiv",PAUSED:"pausiert",BLOCKED_BY_PARENT:"durch Gesamtpause blockiert",ARCHIVED:"archiviert",EXPIRED:"abgelaufen"}[s]||s||"unbekannt";}
function healthLabel(s){return {HEALTHY:"gesund",DEGRADED:"eingeschränkt",BROKEN:"gestört",UNKNOWN:"unbekannt"}[s]||s||"unbekannt";}
function modeLabel(s){return {CONTROL_PLANE:"Harness-Systemarbeit",SURGICAL:"gezielter Eingriff",DISCOVER:"Erkunden"}[s]||s||"–";}
function workflowLabel(s){return {FOCUSED_READING:"fokussiertes Lesen",VERIFY:"Gegenprüfung",RECOVER:"Reparaturmodus",PATH_INVENTORY:"Pfadorientierung",CHANGE_READY:"Änderung vorbereitet",DISCOVER:"Erkunden"}[s]||s||"–";}

async function api(path,options){
  var r=await fetch(path,Object.assign({cache:"no-store",headers:{"Content-Type":"application/json"}},options||{}));
  var j={};try{j=await r.json();}catch(_e){}
  if(!r.ok||j.ok===false)throw new Error(j.error||("HTTP "+r.status));
  return j;
}
async function post(path,body){var out=await api(path,{method:"POST",body:JSON.stringify(body)});await refresh();return out;}

async function changeMode(){var reason=val("modeReason");if(!reason){throw new Error("Bitte den Grund für den Moduswechsel eintragen.");}await post("/chatgptharness/api/set-mode",{mode:val("modeChoice"),user_instruction:reason});}
async function masterSet(status){await post("/chatgptharness/api/set-layer",{layer_id:"core.master",desired_status:status,reason:val("globalReason")||("Master "+status),ttl_seconds:status==="PAUSED"?secFromMinutes("globalMinutes"):null});}
async function fullActivate(){await post("/chatgptharness/api/full-activate",{reason:val("globalReason")||"Im Dashboard bewusst voll aktiviert."});}
async function setLayer(id,status){var k=id.replace(/[^a-z0-9]/gi,"_");await post("/chatgptharness/api/set-layer",{layer_id:id,desired_status:status,reason:val("reason_"+k)||(status+" über Dashboard"),ttl_seconds:status==="PAUSED"?secFromMinutes("ttl_"+k):null});}
async function updateLayerDefinition(id){var k=id.replace(/[^a-z0-9]/gi,"_");await post("/chatgptharness/api/update-layer-definition",{layer_id:id,reason:val("def_reason_"+k)||"Definition im Dashboard geändert.",changes:{title:val("def_title_"+k),purpose:val("def_purpose_"+k),does:val("def_does_"+k),pause_effect:val("def_pause_"+k)}});}
async function grantLease(){await post("/chatgptharness/api/grant-lease",{layer_pattern:val("leasePattern")||"*",ttl_seconds:secFromMinutes("leaseMinutes"),reason:val("leaseReason")||"Im Dashboard freigegeben."});}
async function revokeLease(id){await post("/chatgptharness/api/revoke-lease",{lease_id:id,reason:"Im Dashboard widerrufen."});}
async function createLayer(){
  var kind=val("newKind");
  var scope={};
  if(kind==="TASK"){
    var goal=val("newTaskGoal"),tools=listVal("newTaskTools"),targets=listVal("newTaskTargets"),completion=listVal("newTaskCompletion");
    if(!goal)throw new Error("TASK braucht ein klares Ziel.");
    if(!tools.length)throw new Error("TASK braucht mindestens ein erlaubtes Toolmuster.");
    scope={raw_goal:goal,allowed_tool_patterns:tools,allowed_target_patterns:targets,completion_criteria:completion,sidequest_policy:val("newTaskSidequest")||"park_only"};
  }
  await post("/chatgptharness/api/create-layer",{layer_id:val("newId"),kind:kind,title:val("newTitle"),purpose:val("newPurpose"),does:val("newDoes"),pause_effect:val("newPauseEffect"),reason:val("newReason")||"Im Dashboard angelegt.",scope:scope,ttl_seconds:secFromMinutes("newMinutes")});
}
async function addContext(layerId){var k=layerId.replace(/[^a-z0-9]/gi,"_");var title=val("ctx_title_"+k);if(!title)return;await post("/chatgptharness/api/context",{layer_id:layerId,context_type:val("ctx_type_"+k)||"NOTE",title:title,summary:val("ctx_summary_"+k),reference:val("ctx_ref_"+k)});}
async function addFeedback(layerId,type){var k=(layerId||"global").replace(/[^a-z0-9]/gi,"_");var text=val("feedback_"+k);if(!text)return;await post("/chatgptharness/api/feedback",{layer_id:layerId,entry_type:type,text:text});}
async function replyFeedback(layerId,parentId){var k=String(parentId||"").replace(/[^a-z0-9]/gi,"_");var text=val("reply_"+k);if(!text)return;await post("/chatgptharness/api/feedback",{layer_id:layerId,entry_type:"COMMENT",text:text,parent_entry_id:parentId});}
async function decideProposal(layerId,entryId,type){await post("/chatgptharness/api/feedback",{layer_id:layerId,entry_type:type,parent_entry_id:entryId,text:type==="ACCEPT"?"Vorschlag angenommen.":"Vorschlag abgelehnt."});}
async function learningFeedback(ruleId,outcome){var k=String(ruleId||"").replace(/[^a-z0-9]/gi,"_");await post("/chatgptharness/api/learning-feedback",{rule_id:ruleId,outcome:outcome,note:val("learning_note_"+k)});var e=document.getElementById("learning_note_"+k);if(e)e.value="";}
async function learningReassess(ruleId){await post("/chatgptharness/api/learning-reassess",{rule_id:ruleId});}

function renderSummary(){
  var h=STATE.layers||{},m=h.master||{},c=h.counts||{};
  document.getElementById("headline").innerHTML="<div class='top'><div><b>Harness:</b> <span class='"+statusClass(m.effective_status)+"'>"+esc(statusLabel(m.effective_status))+"</span> · <b>Technischer Zustand:</b> <span class='"+healthClass(m.health)+"'>"+esc(healthLabel(m.health))+"</span></div><span class='muted'>"+esc(m.status_reason||"")+"</span></div>";
  var data=[[c.active||0,"wirksam"],[c.paused||0,"pausiert"],[c.archived||0,"archiviert"],[c.degraded||0,"gestört"],[c.ephemeral||0,"temporär"],[h.feedback_open||0,"offene Vorschläge"],[h.chatgpt_inbox_count||0,"wartet auf ChatGPT"]];
  document.getElementById("summary").innerHTML=data.map(function(x){return "<span class='pill'><b>"+x[0]+"</b> "+x[1]+"</span>";}).join("");
  var r=STATE.runtime||{};
  document.getElementById("runtime").innerHTML="<b>Was macht die Harness gerade?</b><span>"+esc(workflowLabel(r.state))+"</span><b>Arbeitsmodus</b><span>"+esc(modeLabel(r.mode))+"</span><b>Pfadorientierung vollständig</b><span>"+(r.path_inventory_complete?"ja":"nein")+"</span><b>Offene Gegenprüfungen</b><span>"+esc((r.pending_verification||[]).length)+"</span><b>Blocks in Folge</b><span>"+esc(r.blocked_streak||0)+"</span><b>Technisch</b><code>"+esc((r.state||"–")+" / "+(r.mode||"–"))+"</code>";
}
function renderChatgptInbox(){
  var h=STATE.layers||{},items=Array.isArray(h.chatgpt_inbox)?h.chatgpt_inbox:[];
  var count=document.getElementById("chatgptInboxCount"),box=document.getElementById("chatgptInbox");
  if(count)count.textContent=items.length+" offen";
  if(!box)return;
  box.innerHTML=items.length?items.map(function(e){
    var parent=e.parent||null;
    return "<div class='entry'><div class='top'><div><b>"+esc(feedbackTypeLabel(e.entry_type))+"</b> · <code>"+esc(e.layer_id||"global")+"</code></div><span class='muted small'>"+fmt(e.created_at)+"</span></div>"+
      "<div style='margin-top:5px'>"+esc(e.text)+"</div>"+
      (parent?"<div class='muted small' style='margin-top:6px'>Antwort auf "+esc(feedbackTypeLabel(parent.entry_type))+": "+esc(parent.text||"")+"</div>":"")+
      "<div class='muted small' style='margin-top:6px'>Noch nicht von ChatGPT quittiert.</div></div>";
  }).join(""):"<div class='muted small'>Aktuell wartet kein neuer Dashboard-Beitrag auf ChatGPT.</div>";
}
function renderLeases(){
  var leases=(STATE.layers&&STATE.layers.leases)||[];
  document.getElementById("leases").innerHTML=leases.length?leases.map(function(x){
    return "<div class='entry'><div class='top'><div><b>"+esc(x.grantee)+"</b> darf <code>"+esc(x.layer_pattern)+"</code> steuern</div><button class='badbtn' onclick='revokeLease("+JSON.stringify(x.lease_id)+")'>widerrufen</button></div><div class='muted small'>Warum: "+esc(x.reason)+" · Ablauf: "+fmt(x.expires_at)+"</div></div>";
  }).join(""):"<span class='muted'>Keine aktive Control-Lease.</span>";
}
function feedbackTypeLabel(t){return {COMMENT:"Kommentar",PROPOSAL:"Vorschlag",ACCEPT:"angenommen",REJECT:"abgelehnt",RATING:"Bewertung"}[t]||t||"Beitrag";}
function layerFeedback(layerId){return (STATE.feedback||[]).filter(function(e){return e.layer_id===layerId&&!e.parent_entry_id;}).slice(0,12);}
function feedbackReplies(parentId){return (STATE.feedback||[]).filter(function(e){return e.parent_entry_id===parentId&&e.entry_type!=="ACCEPT"&&e.entry_type!=="REJECT";});}
function proposalActionText(p,layerId){
  p=p||{};var a=String(p.action||"").toUpperCase();
  if(a==="SET_LAYER_STATUS"){
    var target=p.layer_id||layerId||"–",ttl=p.ttl_seconds?(" für "+Math.round(Number(p.ttl_seconds)/60)+" Min."):" unbegrenzt";
    return "Bei Annahme: Layer "+target+" → "+statusLabel(String(p.desired_status||"").toUpperCase())+(String(p.desired_status||"").toUpperCase()==="PAUSED"?ttl:"")+".";
  }
  if(a==="GRANT_CONTROL_LEASE"){
    var lt=p.ttl_seconds?(" für "+Math.round(Number(p.ttl_seconds)/60)+" Min."):" unbegrenzt";
    return "Bei Annahme: ChatGPT erhält Steuerrecht für "+(p.layer_pattern||layerId||"*")+lt+".";
  }
  if(a==="CREATE_LAYER"){
    return "Bei Annahme: neue "+String(p.kind||"dynamische")+"-Schicht "+String(p.layer_id||"–")+" wird angelegt.";
  }
  if(a==="UPDATE_LAYER_DEFINITION"){
    var target=p.layer_id||layerId||"–",changes=p.changes||{},labels=[];
    if(Object.prototype.hasOwnProperty.call(changes,"title"))labels.push("Titel");
    if(Object.prototype.hasOwnProperty.call(changes,"purpose"))labels.push("Zweck");
    if(Object.prototype.hasOwnProperty.call(changes,"does"))labels.push("Wirkung");
    if(Object.prototype.hasOwnProperty.call(changes,"pause_effect"))labels.push("Pausewirkung");
    return "Bei Annahme: Definition von "+target+" wird geändert"+(labels.length?" ("+labels.join(", ")+")":"")+".";
  }
  return "";
}
function feedbackHtml(e,layerId){
  var controls="",rk=String(e.entry_id||"").replace(/[^a-z0-9]/gi,"_");
  var replies=feedbackReplies(e.entry_id).map(function(r){return "<div class='entry' style='margin-left:14px;border-left-color:var(--accent)'><div class='top'><b>"+esc(r.actor)+" · "+esc(feedbackTypeLabel(r.entry_type))+"</b><span class='muted small'>"+fmt(r.created_at)+"</span></div><div>"+esc(r.text)+"</div></div>";}).join("");
  if(e.entry_type==="PROPOSAL"&&e.status==="OPEN"){
    controls="<div class='row' style='margin-top:8px'><input id='reply_"+rk+"' class='wide' placeholder='Antwort / Rückfrage / Feinjustierung'><button onclick='replyFeedback("+JSON.stringify(layerId)+","+JSON.stringify(e.entry_id)+")'>antworten</button></div><div class='row' style='margin-top:6px'><button class='goodbtn' onclick='decideProposal("+JSON.stringify(layerId)+","+JSON.stringify(e.entry_id)+",\\"ACCEPT\\")'>annehmen</button><button class='badbtn' onclick='decideProposal("+JSON.stringify(layerId)+","+JSON.stringify(e.entry_id)+",\\"REJECT\\")'>ablehnen</button></div>";
  }
  return "<div class='entry "+esc(e.entry_type)+"'><div class='top'><b>"+esc(e.actor)+" · "+esc(feedbackTypeLabel(e.entry_type))+"</b><span class='muted small'>"+esc(e.status)+" · "+fmt(e.created_at)+"</span></div><div>"+esc(e.text)+"</div>"+replies+controls+"</div>";
}
function renderLayers(){
  if(!STATE)return;
  var q=val("search").toLowerCase(),kind=val("kindFilter"),status=val("statusFilter");
  var layers=((STATE.layers&&STATE.layers.layers)||[]).filter(function(x){
    var hay=[x.layer_id,x.title,x.purpose,x.does,x.pause_effect,x.status_reason].join(" ").toLowerCase();
    return (!q||hay.indexOf(q)>=0)&&(!kind||x.kind===kind)&&(!status||x.effective_status===status);
  });
  document.getElementById("layers").innerHTML=layers.map(function(x){
    var k=x.layer_id.replace(/[^a-z0-9]/gi,"_");
    var fb=layerFeedback(x.layer_id).map(function(e){return feedbackHtml(e,x.layer_id);}).join("");
    var ctx=(x.context||[]).map(function(c){return "<div class='entry'><div class='top'><b>"+esc(c.context_type)+" · "+esc(c.title)+"</b><span class='muted small'>"+fmt(c.created_at)+" · "+esc(c.actor)+"</span></div><div>"+esc(c.summary||"")+"</div>"+(c.reference?"<div class='small' style='margin-top:5px'><code>"+esc(c.reference)+"</code></div>":"")+"</div>";}).join("");
    var events=(x.recent_events||[]).map(function(e){return "<div class='entry'><div class='top'><b>"+esc(e.event_type)+"</b><span class='muted small'>"+fmt(e.created_at)+" · "+esc(e.actor)+"</span></div><div>"+esc(e.reason||"")+"</div><div class='muted small'>Status: "+esc(e.desired_status||"–")+" · Health: "+esc(e.health||"–")+"</div></div>";}).join("");
    var defs=(x.definition_history||[]).map(function(d){
      var b=d.before||{},a=d.after||{},changes=[];
      [["title","Titel"],["purpose","Warum gibt es das?"],["does","Was tut es?"],["pause_effect","Bei Pause"]].forEach(function(pair){
        var key=pair[0],label=pair[1];
        if(String(b[key]??"")!==String(a[key]??"")){
          changes.push("<div style='margin-top:6px'><b>"+label+"</b><div class='muted small'>vorher</div><div>"+esc(b[key]||"")+"</div><div class='muted small'>danach</div><div>"+esc(a[key]||"")+"</div></div>");
        }
      });
      return "<div class='entry'><div class='top'><b>Definitionsänderung</b><span class='muted small'>"+fmt(d.created_at)+" · "+esc(d.actor)+"</span></div><div>"+esc(d.reason||"")+"</div>"+changes.join("")+"</div>";
    }).join("");
    var definitionEditor="<details><summary>Definition bearbeiten / Verlauf ("+esc((x.definition_history||[]).length)+")</summary><p class='muted small'>Hier änderst du die verständliche Beschreibung des Bausteins. Bei CORE darf nur das authentifizierte Daniel-Dashboard direkt speichern; ChatGPT muss dafür einen Vorschlag machen, den du annehmen kannst.</p><div class='stack'><input id='def_title_"+k+"' value='"+esc(x.title||"")+"' placeholder='Titel'><textarea id='def_purpose_"+k+"' placeholder='Warum gibt es das?'>"+esc(x.purpose||"")+"</textarea><textarea id='def_does_"+k+"' placeholder='Was tut es konkret?'>"+esc(x.does||"")+"</textarea><textarea id='def_pause_"+k+"' placeholder='Was passiert bei Pause?'>"+esc(x.pause_effect||"")+"</textarea><input id='def_reason_"+k+"' placeholder='Warum wird die Definition geändert?'><button onclick='updateLayerDefinition("+JSON.stringify(x.layer_id)+")'>Definition speichern</button></div>"+(defs||"<div class='muted small' style='margin-top:8px'>Noch keine Definitionsänderung.</div>")+"</details>";
    var archiveButton=x.kind==="CORE"?"":"<button class='badbtn' onclick='setLayer("+JSON.stringify(x.layer_id)+",\\"ARCHIVED\\")'>archivieren</button>";
    return "<article class='card'><div class='top'><div><h3>"+esc(x.title)+"</h3><code>"+esc(x.layer_id)+" · "+esc(x.kind)+"</code></div><div><span class='pill'><span class='statusdot "+esc(x.effective_status)+"'></span><b class='"+statusClass(x.effective_status)+"'>"+esc(statusLabel(x.effective_status))+"</b></span> <span class='pill'><b class='"+healthClass(x.health)+"'>"+esc(healthLabel(x.health))+"</b></span></div></div>"+
      "<div class='kv' style='margin-top:10px'><b>Warum gibt es das?</b><span>"+esc(x.purpose)+"</span><b>Was tut es?</b><span>"+esc(x.does)+"</span><b>Bei Pause</b><span>"+esc(x.pause_effect)+"</span><b>Warum dieser Status?</b><span>"+esc(x.status_reason)+" <span class='muted'>("+esc(x.status_actor)+")</span></span><b>Gesundheit</b><span>"+esc(x.health_reason)+" <span class='muted'>("+esc(x.health_actor)+")</span></span><b>Ablauf</b><span>"+fmt(x.expires_at)+"</span></div>"+
      "<div class='row' style='margin-top:10px'><input id='reason_"+k+"' class='wide' placeholder='Grund / Kontext'><input id='ttl_"+k+"' type='number' min='1' placeholder='Minuten'><button class='warnbtn' onclick='setLayer("+JSON.stringify(x.layer_id)+",\\"PAUSED\\")'>pausieren</button><button class='goodbtn' onclick='setLayer("+JSON.stringify(x.layer_id)+",\\"ACTIVE\\")'>aktivieren</button>"+archiveButton+"</div>"+
      definitionEditor+
      "<details><summary>Herkunft, Scope und Zeiten</summary><div class='kv' style='margin-top:8px'><b>Parent</b><code>"+esc(x.parent_layer_id||"–")+"</code><b>Erzeugt von</b><span>"+esc(x.created_actor||"–")+" · "+fmt(x.created_event_at||x.created_at)+"</span><b>Scope</b><code>"+esc(JSON.stringify(x.scope||{}))+"</code><b>Provenienz</b><code>"+esc(JSON.stringify(x.provenance||{}))+"</code><b>Letzter Status</b><span>"+fmt(x.last_status_event_at)+"</span><b>Letztes Health</b><span>"+fmt(x.last_health_event_at)+"</span></div></details>"+
      "<details><summary>Bau-/Wissenskontext ("+esc((x.context||[]).length)+")</summary><p class='muted small'>Hier liegt Substanz zum Baustein: Plan, Vision, Recherche, Beleg, Doku, Link oder Notiz. Sie ändert den Layer nicht automatisch.</p><div class='grid'><div class='stack'><select id='ctx_type_"+k+"'><option>PLAN</option><option>VISION</option><option>RESEARCH</option><option>EVIDENCE</option><option>DOC</option><option>LINK</option><option>NOTE</option></select><input id='ctx_title_"+k+"' placeholder='Titel'><input id='ctx_ref_"+k+"' placeholder='Datei, URL oder Referenz – optional'></div><div class='stack'><textarea id='ctx_summary_"+k+"' placeholder='Was ist daran wichtig?'></textarea><button onclick='addContext("+JSON.stringify(x.layer_id)+")'>Kontext hinzufügen</button></div></div>"+(ctx||"<div class='muted small'>Noch kein Bau-/Wissenskontext hinterlegt.</div>")+"</details>"+
      "<details><summary>Verlauf ("+esc((x.recent_events||[]).length)+")</summary>"+(events||"<div class='muted small'>Noch keine Zustandsereignisse.</div>")+"</details>"+
      "<details open><summary>Resonanzspur ("+esc(x.open_feedback||0)+" offene Vorschläge)</summary><textarea id='feedback_"+k+"' placeholder='Kommentar, Beobachtung, Bewertung oder Änderungsvorschlag …'></textarea><div class='row'><button onclick='addFeedback("+JSON.stringify(x.layer_id)+",\\"COMMENT\\")'>kommentieren</button><button onclick='addFeedback("+JSON.stringify(x.layer_id)+",\\"PROPOSAL\\")'>Änderung vorschlagen</button><button onclick='addFeedback("+JSON.stringify(x.layer_id)+",\\"RATING\\")'>bewerten</button></div>"+(fb||"<div class='muted small' style='margin-top:8px'>Noch keine Resonanz zu diesem Baustein.</div>")+"</details></article>";
  }).join("")||"<div class='card muted'>Kein Baustein passt zum Filter.</div>";
}
function renderAllFeedback(){
  var all=STATE.feedback||[];
  document.getElementById("allFeedback").innerHTML=all.length?all.slice(0,60).map(function(e){return feedbackHtml(e,e.layer_id);}).join(""):"<span class='muted'>Noch keine Resonanzbeiträge.</span>";
}
async function setDirectiveStatus(eventId,status){
  var k=String(eventId||"").replace(/[^a-z0-9]/gi,"_");
  var reason=val("directive_reason_"+k);
  if(!reason)throw new Error("Bitte den Grund für Archivieren oder Wiederaktivieren eintragen.");
  await post("/chatgptharness/api/set-directive-status",{event_id:eventId,status:status,reason:reason});
}
function directiveEffectLabel(s){return {DENY:"blockiert passende Aktion",REQUIRE_REMINDER:"verlangt vor der Aktion einen passenden Reminder",REMIND:"erinnert bei passendem Kontext"}[s]||s||"Regel";}
function renderDirectives(){
  var box=document.getElementById("directives"),count=document.getElementById("directiveCount");
  if(!box||!count)return;
  var d=STATE.directives||{},items=Array.isArray(d.directives)?d.directives:[],c=d.counts||{};
  count.textContent=(c.active_verified||0)+" aktiv verifiziert · "+(c.active_unverified||0)+" nur Erinnerung · "+(c.archived||0)+" archiviert · "+(c.superseded||0)+" ersetzt";
  if(d.error){box.innerHTML="<div class='entry bad'>Direktiven konnten nicht gelesen werden: "+esc(d.error)+"</div>";return;}
  if(!items.length){box.innerHTML="<div class='entry'><b>Noch keine gespeicherte Direktive vorhanden.</b></div>";return;}
  items=items.slice().sort(function(a,b){
    function rank(x){
      if(x.status==="ACTIVE"&&x.authority_verified)return 0;
      if(x.status==="ACTIVE")return 1;
      if(x.status==="ARCHIVED")return 2;
      return 3;
    }
    var ar=rank(a),br=rank(b);
    if(ar!==br)return ar-br;
    return String(b.created_at||"").localeCompare(String(a.created_at||""));
  });
  box.innerHTML=items.slice(0,60).map(function(x){
    var cs=(x.constraints||[]).map(function(q){
      return "<div class='entry'><b>"+esc(directiveEffectLabel(q.effect))+"</b><div style='margin-top:4px'>"+esc(q.statement)+"</div><div class='muted small'>Aktion: <code>"+esc(q.action_pattern)+"</code> · Ziel: <code>"+esc(q.target_pattern)+"</code></div></div>";
    }).join("");
    var inv=(x.invariants||[]).map(function(q){
      return "<div class='entry'><b>Feste Bedingung: "+esc(q.type)+"</b><div class='small'>Pfad: <code>"+esc(q.path)+"</code></div>"+(q.expected_sha256?"<div class='muted small'>Erwarteter Hash: <code>"+esc(q.expected_sha256)+"</code></div>":"")+"</div>";
    }).join("");
    var k=String(x.event_id||"").replace(/[^a-z0-9]/gi,"_");
    var state=x.status==="SUPERSEDED"?"ersetzt / Historie":x.status==="ARCHIVED"?"archiviert":"aktiv";
    var auth=x.authority_verified
      ?(x.status==="ACTIVE"?"verifiziert, darf harte Wirkung erzeugen":x.status==="ARCHIVED"?"verifiziert, derzeit ohne harte Wirkung":"verifiziert, durch spätere Direktive ersetzt")
      :(x.status==="ARCHIVED"?"unverifiziert, archivierte Erinnerung":"unverifiziert, nur Erinnerung");
    var control="";
    if(x.status==="ACTIVE"){
      control="<div class='row' style='margin-top:9px'><input id='directive_reason_"+k+"' class='wide' placeholder='Warum archivieren?'><button class='warnbtn' onclick='setDirectiveStatus("+JSON.stringify(x.event_id)+",\"ARCHIVED\")'>archivieren</button></div>";
    }else if(x.status==="ARCHIVED"){
      control="<div class='row' style='margin-top:9px'><input id='directive_reason_"+k+"' class='wide' placeholder='Warum wieder aktivieren?'><button class='goodbtn' onclick='setDirectiveStatus("+JSON.stringify(x.event_id)+",\"ACTIVE\")'>wieder aktivieren</button></div>";
    }
    var statusInfo=x.status_reason?"<div class='muted small' style='margin-top:6px'>Statusgrund: "+esc(x.status_reason)+" · "+esc(x.status_actor||"–")+(x.status_changed_at?" · "+esc(x.status_changed_at):"")+"</div>":"";
    var statusHistory=(x.status_history||[]).map(function(h){
      return "<div class='entry'><b>"+esc(h.status)+"</b> · "+esc(h.actor)+"<div>"+esc(h.reason||"")+"</div><div class='muted small'>"+esc(h.created_at||"")+"</div></div>";
    }).join("");
    return "<div class='entry'><div class='top'><div><b>"+esc(state)+"</b> · <span class='"+(x.authority_verified?"good":"warn")+"'>"+esc(auth)+"</span></div><span class='muted small'>"+fmt(Date.parse(x.created_at)/1000)+" · <code>"+esc(x.event_id)+"</code></span></div>"+
      "<div style='margin-top:8px;white-space:pre-wrap'><b>Dein Originalwortlaut:</b><br>"+esc(x.raw_text)+"</div>"+
      statusInfo+control+
      "<div style='margin-top:8px'><b>Abgeleitete Wirkung</b>"+(cs||"<div class='muted small'>Keine harte Constraint aus diesem Eintrag.</div>")+"</div>"+
      (inv?"<div style='margin-top:8px'><b>Feste Invarianten</b>"+inv+"</div>":"")+
      ((x.supersedes||[]).length?"<div class='muted small'>Ersetzt ältere Direktiven: <code>"+esc((x.supersedes||[]).join(", "))+"</code></div>":"")+
      ((x.superseded_by||[]).length?"<div class='muted small'>Später ersetzt durch: <code>"+esc((x.superseded_by||[]).join(", "))+"</code></div>":"")+
      "<details><summary>Statusverlauf / technische Herkunft</summary>"+(statusHistory||"<div class='muted small' style='margin-top:8px'>Noch keine manuelle Statusänderung.</div>")+"<div class='kv small' style='margin-top:8px'><b>Quelle</b><code>"+esc(x.source_kind)+"</code><b>Metadaten</b><code>"+esc(JSON.stringify(x.metadata||{}))+"</code></div></details></div>";
  }).join("")+(items.length>60?"<div class='muted small'>Es werden die ersten 60 priorisierten Einträge gezeigt. Insgesamt: "+esc(items.length)+".</div>":"");
}
function learningStatusLabel(s){return {CANDIDATE:"Kandidat",TESTING:"wird geprüft",ACTIVE:"aktiv",WEAKENED:"abgeschwächt",RETIRED:"stillgelegt",SUPERSEDED:"ersetzt"}[s]||s||"unbekannt";}
function learningMetricText(m){
  m=m||{};
  var r=(m.regression&&typeof m.regression==="object")?m.regression:m;
  var bits=[];
  if(r.tested_turns!=null)bits.push("geprüfte Turns: "+r.tested_turns);
  if(r.matched_turns!=null)bits.push("passende Turns: "+r.matched_turns);
  if(r.success_collisions!=null)bits.push("Kollisionen mit guten alten Verläufen: "+r.success_collisions);
  if(r.source_covered!=null)bits.push("Ausgangsfall abgedeckt: "+(r.source_covered?"ja":"nein"));
  if(r.passed_for_activation!=null)bits.push("für Aktivierung bestanden: "+(r.passed_for_activation?"ja":"nein"));
  return bits.join(" · ");
}
function renderLearning(){
  var box=document.getElementById("learningRules"),count=document.getElementById("learningCount");
  if(!box||!count)return;
  var l=STATE.learning||{},rules=Array.isArray(l.rules)?l.rules:[];
  count.textContent=rules.length+" "+(rules.length===1?"Regel":"Regeln");
  if(l.error){box.innerHTML="<div class='entry bad'>Lernstatus konnte nicht gelesen werden: "+esc(l.error)+"</div>";return;}
  if(!rules.length){
    box.innerHTML="<div class='entry'><b>Noch keine selbstgelernte Regel vorhanden.</b><div class='muted small' style='margin-top:5px'>Die Schleife ist bereit, aber bisher wurde keine Lernregel gespeichert. Es wirkt hier also auch nichts heimlich. Erst ein beobachteter Drift kann eine Kandidatenregel erzeugen; nur eine getestete aktive Regel darf hart eingreifen.</div></div>";
    return;
  }
  box.innerHTML=rules.map(function(r){
    var f=r.feedback||{},metrics=learningMetricText(r.metrics),d=r.source_drift||{};
    var k=String(r.rule_id||"").replace(/[^a-z0-9]/gi,"_");
    var source=[];
    if(d.drift_code)source.push(d.drift_code);
    if(d.description)source.push(d.description);
    if(d.drift_id)source.push("Drift-ID: "+d.drift_id);
    var reassess=(r.status==="RETIRED"||r.status==="SUPERSEDED")?"":"<button onclick='learningReassess("+JSON.stringify(r.rule_id)+")'>mit aktuellem Erfahrungsstand neu bewerten</button>";
    return "<div class='entry'><div class='top'><div><b>"+esc(learningStatusLabel(r.status))+"</b> · <code>"+esc(r.rule_kind)+"</code></div><span class='muted small'>"+esc(r.rule_id)+"</span></div>"+
      "<div style='margin-top:6px'><b>"+esc(r.rule_text)+"</b></div>"+
      "<div class='kv small' style='margin-top:8px'><b>Woher kam die Regel?</b><span>"+esc(source.join(" · ")||"Herkunft noch nicht im Statuskörper vorhanden.")+"</span><b>Wann greift sie?</b><code>"+esc(JSON.stringify(r.condition||{}))+"</code><b>Was würde sie tun?</b><code>"+esc(JSON.stringify(r.enforcement||{}))+"</code><b>Warum dieser Zustand?</b><span>"+esc(r.reason||"–")+"</span><b>Tests</b><span>"+esc(metrics||"noch keine auswertbaren Testmetriken")+"</span><b>Rückmeldungen</b><span>hilfreich "+esc(f.helpful||0)+" · schädlich "+esc(f.harmful||0)+" · widersprochen "+esc(f.contradicted||0)+" · irrelevant "+esc(f.irrelevant||0)+"</span></div>"+
      "<div class='row' style='margin-top:9px'><input id='learning_note_"+k+"' class='wide' placeholder='Warum findest du diese Regel hilfreich, schädlich, widersprüchlich oder irrelevant?'><button class='goodbtn' onclick='learningFeedback("+JSON.stringify(r.rule_id)+","+JSON.stringify("HELPFUL")+")'>hilfreich</button><button class='badbtn' onclick='learningFeedback("+JSON.stringify(r.rule_id)+","+JSON.stringify("HARMFUL")+")'>schädlich</button><button class='badbtn' onclick='learningFeedback("+JSON.stringify(r.rule_id)+","+JSON.stringify("CONTRADICTED")+")'>widersprochen</button><button onclick='learningFeedback("+JSON.stringify(r.rule_id)+","+JSON.stringify("IRRELEVANT")+")'>irrelevant</button>"+reassess+"</div>"+
      "<details><summary>Technische Details</summary><div class='kv small' style='margin-top:8px'><b>Bedingung</b><code>"+esc(JSON.stringify(r.condition||{}))+"</code><b>Durchsetzung</b><code>"+esc(JSON.stringify(r.enforcement||{}))+"</code><b>Drift-Beleg</b><code>"+esc(JSON.stringify(d.evidence||{}))+"</code><b>Metriken</b><code>"+esc(JSON.stringify(r.metrics||{}))+"</code></div></details></div>";
  }).join("");
}
function render(){renderSummary();renderChatgptInbox();renderLeases();renderLayers();renderDirectives();renderLearning();renderAllFeedback();}
async function refresh(){
  try{
    STATE=await api("/chatgptharness/api/state");LAST_OK=Date.now();render();
    document.getElementById("live").textContent="LIVE";document.getElementById("liveDot").className="statusdot ACTIVE";
    document.getElementById("clock").textContent="aktualisiert "+new Date().toLocaleTimeString("de-DE");
  }catch(e){
    var stale=(Date.now()-LAST_OK)<5000;
    document.getElementById("live").textContent=stale?"STALE":"OFFLINE";document.getElementById("liveDot").className="statusdot "+(stale?"PAUSED":"ARCHIVED");
    document.getElementById("headline").innerHTML="<span class='bad'>"+esc(e.message)+"</span>";
  }
}
refresh();setInterval(refresh,1000);
</script>
</main></body></html>"""


def _harness_dashboard_action(body: dict) -> dict:
    if not isinstance(body, dict):
        raise ValueError("Action-Body muss ein JSON-Objekt sein.")
    action = str(body.get("action") or "").strip().lower()
    reason = str(body.get("reason") or "").strip()
    actor = "DANIEL_DASHBOARD"

    if action == "set_layer":
        layer_id = str(body.get("layer_id") or "").strip()
        status = str(body.get("desired_status") or "").strip().upper()
        if not layer_id or status not in {"ACTIVE", "PAUSED", "ARCHIVED"}:
            raise ValueError("layer_id und gueltiger desired_status fehlen.")
        ttl_raw = body.get("ttl_seconds")
        ttl_seconds = int(ttl_raw) if ttl_raw not in (None, "") else None
        return harness_layer_set(
            layer_id,
            status,
            actor=actor,
            reason=reason or f"{status} ueber /chatgptharness gesetzt.",
            ttl_seconds=ttl_seconds,
        )

    if action == "full_activate":
        return harness_full_activate(
            actor=actor,
            reason=reason or "Alle nicht archivierten Harness-Schichten im Dashboard voll aktiviert.",
        )

    if action == "grant_lease":
        layer_pattern = str(body.get("layer_pattern") or "*").strip() or "*"
        ttl_raw = body.get("ttl_seconds")
        ttl_seconds = int(ttl_raw) if ttl_raw not in (None, "") else None
        return harness_control_lease_grant(
            actor=actor,
            grantee="CHATGPT",
            layer_pattern=layer_pattern,
            scope=body.get("scope") if isinstance(body.get("scope"), dict) else {},
            reason=reason or "Daniel hat ChatGPT im Dashboard eine Control-Lease erteilt.",
            ttl_seconds=ttl_seconds,
        )

    if action == "revoke_lease":
        return harness_control_lease_revoke(
            lease_id=str(body.get("lease_id") or "").strip(),
            actor=actor,
            reason=reason or "Daniel hat die Control-Lease im Dashboard widerrufen.",
        )

    if action == "feedback":
        return harness_layer_feedback(
            layer_id=(str(body.get("layer_id")).strip() if body.get("layer_id") else None),
            actor=actor,
            entry_type=str(body.get("entry_type") or "COMMENT"),
            text=str(body.get("text") or "").strip(),
            payload=body.get("payload") if isinstance(body.get("payload"), dict) else {},
            parent_entry_id=(str(body.get("parent_entry_id")).strip() if body.get("parent_entry_id") else None),
        )

    if action == "create_layer":
        return harness_create_layer(
            layer_id=str(body.get("layer_id") or "").strip(),
            kind=str(body.get("kind") or "").strip(),
            title=str(body.get("title") or "").strip(),
            purpose=str(body.get("purpose") or "").strip(),
            does_text=str(body.get("does") or "").strip(),
            pause_effect=str(body.get("pause_effect") or "").strip(),
            actor=actor,
            reason=reason or "Im ChatGPT-Harness-Dashboard angelegt.",
            scope=body.get("scope") if isinstance(body.get("scope"), dict) else {},
            provenance={"source": "CHATGPTHARNESS", "authority_verified": True},
            parent_layer_id=str(body.get("parent_layer_id") or "core.master"),
            ttl_seconds=(int(body["ttl_seconds"]) if body.get("ttl_seconds") not in (None, "") else None),
        )

    raise ValueError(f"Unbekannte Harness-Dashboard-Aktion: {action}")


class VPSHandler(BaseHTTPRequestHandler):
    def setup(self):
        super().setup()
        # A client that disconnects must not leave this handler waiting forever
        # on a partial request body or a silent peer.
        self.connection.settimeout(_HTTP_SOCKET_TIMEOUT_S)
        self.close_connection = True

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def _json(self, status: int, obj: dict):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self._cors()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError, TimeoutError):
            self.close_connection = True

    def _autorisiert(self) -> bool:
        if not API_KEY:
            return True
        auth = self.headers.get("Authorization", "")
        if auth == f"Bearer {API_KEY}":
            return True
        if auth.startswith("Bearer "):
            token = auth[len("Bearer "):]
            ablauf = _ACCESS_TOKENS.get(token)
            if ablauf and ablauf > time.time():
                return True
        return False

    def _unauthorized(self):
        body = json.dumps({"error": "unauthorized"}).encode("utf-8")
        self.send_response(401)
        self._cors()
        self.send_header("WWW-Authenticate", _WWW_AUTHENTICATE_HEADER)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError, TimeoutError):
            self.close_connection = True

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_GET(self):
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"

        if path.startswith("/chatgptharness") and not _harness_dashboard_authorized(self.headers.get("Authorization")):
            self.send_response(401)
            self._cors()
            self.send_header("WWW-Authenticate", 'Basic realm="ChatGPT Harness"')
            self.send_header("Content-Length", "0")
            self.send_header("Connection", "close")
            self.end_headers()
            return

        if path in (
            "/.well-known/oauth-protected-resource",
            "/mcp/.well-known/oauth-protected-resource",
        ):
            self._json(200, {"resource": f"{PUBLIC_BASE_URL}/mcp",
                              "authorization_servers": [PUBLIC_BASE_URL],
                              "scopes_supported": ["tools"],
                              "bearer_methods_supported": ["header"]})
            return

        if path in (
            "/.well-known/oauth-authorization-server",
            "/mcp/.well-known/oauth-authorization-server",
        ):
            self._json(200, {
                "issuer": PUBLIC_BASE_URL,
                "authorization_endpoint": f"{PUBLIC_BASE_URL}/oauth/authorize",
                "token_endpoint": f"{PUBLIC_BASE_URL}/oauth/token",
                "registration_endpoint": f"{PUBLIC_BASE_URL}/oauth/register",
                "response_types_supported": ["code"],
                "grant_types_supported": ["authorization_code"],
                "code_challenge_methods_supported": ["S256", "plain"],
                "token_endpoint_auth_methods_supported": ["client_secret_post", "none"],
                "resource_parameter_supported": True,
                # 2026-07-23: ChatGPTs Connector-UI verlangte "Basis-Scopes"/"Standard-
                # Scopes" und fand ohne dieses Feld "keine unterstuetzten Scopes zum
                # Auswaehlen" -- Einzel-Nutzer-Server, keine granularen Berechtigungsstufen,
                # ein einziger Scope fuer den kompletten (nur lesenden) Werkzeugsatz.
                "scopes_supported": ["tools"],
            })
            return

        # Some MCP clients probe the resource URL itself with GET before reading
        # protected-resource metadata. Return the OAuth challenge required by
        # RFC 9728 instead of a bare 404, so discovery can proceed from the
        # resource URL as well as from the well-known alias above.
        if path in ("/mcp", "/rpc"):
            self._unauthorized()
            return

        if path == "/oauth/authorize":
            qs = parse_qs(parsed.query)
            redirect_uri = (qs.get("redirect_uri") or [""])[0]
            state = (qs.get("state") or [""])[0]
            code_challenge = (qs.get("code_challenge") or [""])[0]
            code_challenge_method = (qs.get("code_challenge_method") or ["plain"])[0]
            # Copy/paste from connector UIs can turn a leading/trailing space
            # into a literal '+' in the query string. Whitespace is not part of
            # the secret, so tolerate it at this input boundary.
            eingereichter_key = (qs.get("key") or [""])[0].strip()
            resource = (qs.get("resource") or [f"{PUBLIC_BASE_URL}/mcp"])[0]

            if not redirect_uri:
                self._json(400, {"error": "invalid_request", "error_description": "redirect_uri fehlt"})
                return

            if eingereichter_key != API_KEY or not API_KEY:
                self.send_response(200)
                self._cors()
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(f"""<!doctype html><html><body style="font-family:monospace;background:#0a0e14;color:#cdd6f4;padding:40px">
<h3>Flextrawurst VPS-Werkzeugkoerper — Zugriff erlauben?</h3>
<form method="GET" action="{html.escape(PUBLIC_BASE_URL)}/oauth/authorize">
<input type="hidden" name="redirect_uri" value="{html.escape(redirect_uri)}">
<input type="hidden" name="state" value="{html.escape(state)}">
<input type="hidden" name="code_challenge" value="{html.escape(code_challenge)}">
<input type="hidden" name="code_challenge_method" value="{html.escape(code_challenge_method)}">
<label>Schluessel: <input type="password" name="key"></label>
<button type="submit">Erlauben</button>
</form></body></html>""".encode("utf-8"))
                return

            code = secrets.token_urlsafe(32)
            _AUTH_CODES[code] = {
                "redirect_uri": redirect_uri, "code_challenge": code_challenge,
                "code_challenge_method": code_challenge_method, "resource": resource,
                "expires": time.time() + _CODE_TTL_S,
            }
            trenner = "&" if "?" in redirect_uri else "?"
            ziel = f"{redirect_uri}{trenner}code={urllib.parse.quote(code)}&state={urllib.parse.quote(state)}"
            self.send_response(302)
            self.send_header("Location", ziel)
            self.end_headers()
            return

        if path in {"/chatgptharness", "/chatgptharness/"}:
            body = _harness_dashboard_html().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Robots-Tag", "noindex, nofollow")
            self.send_header("Connection", "close")
            self.end_headers()
            try:
                self.wfile.write(body)
            except (BrokenPipeError, ConnectionResetError, TimeoutError):
                self.close_connection = True
            return

        if path == "/chatgptharness/api/state":
            self._json(200, _harness_dashboard_state())
            return

        if path == "/openapi.json":
            self._json(200, get_openapi_schema())
            return

        if path.startswith("/download/"):
            token = path[len("/download/"):]
            eintrag = _DOWNLOAD_TOKENS.get(token)
            if not eintrag or eintrag["expires"] < time.time():
                self._json(404, {"error": "Token ungueltig oder abgelaufen"})
                return
            p = Path(eintrag["path"])
            if not p.is_file():
                self._json(404, {"error": "Datei nicht mehr vorhanden"})
                return
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Disposition", f'attachment; filename="{p.name}"')
            self.send_header("Content-Length", str(p.stat().st_size))
            self.end_headers()
            with open(p, "rb") as f:
                shutil.copyfileobj(f, self.wfile)
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        from urllib.parse import urlparse
        path = urlparse(self.path).path.rstrip("/") or "/"

        if path.startswith("/chatgptharness") and not _harness_dashboard_authorized(self.headers.get("Authorization")):
            self.send_response(401)
            self._cors()
            self.send_header("WWW-Authenticate", 'Basic realm="ChatGPT Harness"')
            self.send_header("Content-Length", "0")
            self.send_header("Connection", "close")
            self.end_headers()
            return

        try:
            length = int(self.headers.get("Content-Length", 0))
        except (TypeError, ValueError):
            self._json(400, {"error": "Ungültiger Content-Length-Header"})
            return
        if length < 0 or length > _MAX_HTTP_BODY_BYTES:
            self._json(413, {"error": "Request-Body zu groß"})
            return
        roh = self.rfile.read(length) if length > 0 else b""
        content_type = self.headers.get("Content-Type", "")
        if "application/x-www-form-urlencoded" in content_type:
            body_data = {k: v[0] for k, v in urllib.parse.parse_qs(roh.decode("utf-8")).items()}
        else:
            body_data = json.loads(roh) if roh else {}

        if path == "/chatgptharness/api/set-directive-status":
            event_id = str(body_data.get("event_id") or "").strip()
            status = str(body_data.get("status") or "").strip().upper()
            reason = str(body_data.get("reason") or "").strip()
            if not event_id:
                self._json(400, {"ok": False, "error": "event_id fehlt"})
                return
            if status not in {"ACTIVE", "ARCHIVED"}:
                self._json(400, {"ok": False, "error": "status muss ACTIVE oder ARCHIVED sein"})
                return
            if not reason:
                self._json(400, {"ok": False, "error": "Grund fehlt"})
                return
            try:
                data = harness_set_directive_status(
                    event_id,
                    status,
                    actor="DANIEL_DASHBOARD",
                    reason=reason,
                )
                self._json(200, {"ok": True, "data": data})
            except Exception as exc:
                self._json(400, {"ok": False, "error": str(exc)})
            return

        if path == "/chatgptharness/api/set-mode":
            try:
                mode = str(body_data.get("mode") or "").strip().upper()
                instruction = str(body_data.get("user_instruction") or "").strip()
                data = harness_set_mode(
                    mode=mode,
                    user_instruction=instruction,
                    session_id=body_data.get("session_id"),
                    authority_source="DANIEL_DASHBOARD",
                )
                self._json(200, {"ok": True, "data": data})
            except Exception as exc:
                self._json(400, {"ok": False, "error": str(exc)})
            return

        if path == "/chatgptharness/api/set-layer":
            layer_id = str(body_data.get("layer_id") or "").strip()
            status = str(body_data.get("desired_status") or "").strip().upper()
            reason = str(body_data.get("reason") or "").strip()
            if not layer_id or status not in {"ACTIVE", "PAUSED", "ARCHIVED"}:
                self._json(400, {"ok": False, "error": "ungueltiger Layer oder Status"})
                return
            ttl_raw = body_data.get("ttl_seconds")
            ttl_seconds = int(ttl_raw) if ttl_raw not in (None, "") else None
            try:
                data = harness_layer_set(
                    layer_id,
                    status,
                    actor="DANIEL_DASHBOARD",
                    reason=reason or f"{status} ueber /chatgptharness gesetzt.",
                    ttl_seconds=ttl_seconds,
                )
                self._json(200, {"ok": True, "data": data})
            except Exception as exc:
                self._json(400, {"ok": False, "error": str(exc)})
            return

        if path == "/chatgptharness/api/update-layer-definition":
            layer_id = str(body_data.get("layer_id") or "").strip()
            reason = str(body_data.get("reason") or "").strip()
            changes = body_data.get("changes") if isinstance(body_data.get("changes"), dict) else {}
            allowed = {"title", "purpose", "does", "pause_effect"}
            unknown = sorted(set(changes) - allowed)
            if not layer_id or not changes:
                self._json(400, {"ok": False, "error": "layer_id und changes sind Pflichtfelder"})
                return
            if unknown:
                self._json(400, {"ok": False, "error": "Unbekannte Definitionsfelder: " + ", ".join(unknown)})
                return
            try:
                data = harness_update_layer_definition(
                    layer_id,
                    actor="DANIEL_DASHBOARD",
                    reason=reason or "Definition im authentifizierten Dashboard geändert.",
                    title=changes.get("title"),
                    purpose=changes.get("purpose"),
                    does_text=changes.get("does"),
                    pause_effect=changes.get("pause_effect"),
                )
                self._json(200, {"ok": True, "data": data})
            except Exception as exc:
                self._json(400, {"ok": False, "error": str(exc)})
            return

        if path == "/chatgptharness/api/full-activate":
            reason = str(body_data.get("reason") or "").strip()
            try:
                data = harness_full_activate(
                    actor="DANIEL_DASHBOARD",
                    reason=reason or "Alle nicht archivierten Harness-Schichten im Dashboard voll aktiviert.",
                )
                self._json(200, {"ok": True, "data": data})
            except Exception as exc:
                self._json(400, {"ok": False, "error": str(exc)})
            return

        if path == "/chatgptharness/api/context":
            try:
                data = harness_layer_context_add(
                    layer_id=str(body_data.get("layer_id") or "").strip(),
                    actor="DANIEL_DASHBOARD",
                    context_type=str(body_data.get("context_type") or "NOTE"),
                    title=str(body_data.get("title") or "").strip(),
                    summary=str(body_data.get("summary") or "").strip(),
                    reference=str(body_data.get("reference") or "").strip(),
                    metadata=body_data.get("metadata") if isinstance(body_data.get("metadata"), dict) else {},
                )
                self._json(200, {"ok": True, "data": data})
            except Exception as exc:
                self._json(400, {"ok": False, "error": str(exc)})
            return

        if path == "/chatgptharness/api/learning-reassess":
            rule_id = str(body_data.get("rule_id") or "").strip()
            try:
                data = harness_reassess_learning_rule(rule_id)
                self._json(200, {"ok": True, "data": data})
            except Exception as exc:
                self._json(400, {"ok": False, "error": str(exc)})
            return

        if path == "/chatgptharness/api/learning-feedback":
            rule_id = str(body_data.get("rule_id") or "").strip()
            outcome = str(body_data.get("outcome") or "").strip().upper()
            note = str(body_data.get("note") or "").strip()
            try:
                data = harness_record_rule_feedback(
                    rule_id,
                    outcome,
                    source_kind="DANIEL_DASHBOARD",
                    evidence={"dashboard_note": note} if note else {},
                    reassess=True,
                )
                self._json(200, {"ok": True, "data": data})
            except Exception as exc:
                self._json(400, {"ok": False, "error": str(exc)})
            return

        if path == "/chatgptharness/api/feedback":
            layer_id = str(body_data.get("layer_id") or "").strip() or None
            entry_type = str(body_data.get("entry_type") or "COMMENT").strip().upper()
            text_value = str(body_data.get("text") or "").strip()
            parent_entry_id = str(body_data.get("parent_entry_id") or "").strip() or None
            payload = body_data.get("payload") if isinstance(body_data.get("payload"), dict) else {}
            try:
                application = None
                if entry_type == "ACCEPT":
                    if not parent_entry_id:
                        raise ValueError("ACCEPT braucht die ID des Vorschlags.")
                    with _HARNESS_PROPOSAL_APPLY_LOCK:
                        application = _harness_dashboard_apply_proposal(parent_entry_id)
                        payload = {**payload, "proposal_application": application}
                        data = harness_layer_feedback(
                            layer_id=layer_id,
                            actor="DANIEL_DASHBOARD",
                            entry_type=entry_type,
                            text=text_value,
                            payload=payload,
                            parent_entry_id=parent_entry_id,
                        )
                else:
                    data = harness_layer_feedback(
                        layer_id=layer_id,
                        actor="DANIEL_DASHBOARD",
                        entry_type=entry_type,
                        text=text_value,
                        payload=payload,
                        parent_entry_id=parent_entry_id,
                    )
                self._json(200, {"ok": True, "data": data, "application": application})
            except Exception as exc:
                self._json(400, {"ok": False, "error": str(exc)})
            return

        if path == "/chatgptharness/api/chatgpt-ack":
            entry_id = str(body_data.get("entry_id") or "").strip()
            note = str(body_data.get("note") or "").strip()
            if not entry_id:
                self._json(400, {"ok": False, "error": "entry_id fehlt"})
                return
            try:
                data = harness_feedback_ack(
                    entry_id,
                    recipient="CHATGPT",
                    actor="CHATGPT",
                    note=note,
                )
                self._json(200, {"ok": True, "data": data})
            except Exception as exc:
                self._json(400, {"ok": False, "error": str(exc)})
            return

        if path == "/chatgptharness/api/grant-lease":
            layer_pattern = str(body_data.get("layer_pattern") or "*").strip() or "*"
            reason = str(body_data.get("reason") or "").strip()
            ttl_raw = body_data.get("ttl_seconds")
            ttl_seconds = int(ttl_raw) if ttl_raw not in (None, "") else None
            try:
                data = harness_control_lease_grant(
                    actor="DANIEL_DASHBOARD",
                    grantee="CHATGPT",
                    layer_pattern=layer_pattern,
                    scope=body_data.get("scope") if isinstance(body_data.get("scope"), dict) else {},
                    reason=reason or "Daniel hat ChatGPT im Dashboard eine Control-Lease erteilt.",
                    ttl_seconds=ttl_seconds,
                )
                self._json(200, {"ok": True, "data": data})
            except Exception as exc:
                self._json(400, {"ok": False, "error": str(exc)})
            return

        if path == "/chatgptharness/api/revoke-lease":
            lease_id = str(body_data.get("lease_id") or "").strip()
            reason = str(body_data.get("reason") or "").strip()
            try:
                data = harness_control_lease_revoke(
                    lease_id=lease_id,
                    actor="DANIEL_DASHBOARD",
                    reason=reason or "Daniel hat die Control-Lease im Dashboard widerrufen.",
                )
                self._json(200, {"ok": True, "data": data})
            except Exception as exc:
                self._json(400, {"ok": False, "error": str(exc)})
            return

        if path == "/chatgptharness/api/create-layer":
            try:
                data = harness_create_layer(
                    layer_id=str(body_data.get("layer_id") or "").strip(),
                    kind=str(body_data.get("kind") or "").strip(),
                    title=str(body_data.get("title") or "").strip(),
                    purpose=str(body_data.get("purpose") or "").strip(),
                    does_text=str(body_data.get("does") or "").strip(),
                    pause_effect=str(body_data.get("pause_effect") or "").strip(),
                    actor="DANIEL_DASHBOARD",
                    reason=str(body_data.get("reason") or "Im Dashboard angelegt.").strip(),
                    scope=body_data.get("scope") if isinstance(body_data.get("scope"), dict) else {},
                    provenance={"source": "CHATGPTHARNESS", "authority_verified": True},
                    parent_layer_id=str(body_data.get("parent_layer_id") or "core.master"),
                    ttl_seconds=(
                        int(body_data["ttl_seconds"])
                        if body_data.get("ttl_seconds") not in (None, "")
                        else None
                    ),
                )
                self._json(200, {"ok": True, "data": data})
            except Exception as exc:
                self._json(400, {"ok": False, "error": str(exc)})
            return

        if path == "/oauth/register":
            self._json(201, {
                "client_id": OAUTH_CLIENT_ID,
                "client_secret": OAUTH_CLIENT_SECRET,
                "client_id_issued_at": int(time.time()),
                "client_secret_expires_at": 0,
                "redirect_uris": body_data.get("redirect_uris", []),
                "grant_types": body_data.get("grant_types", ["authorization_code"]),
                "response_types": body_data.get("response_types", ["code"]),
                "token_endpoint_auth_method": "client_secret_post" if OAUTH_CLIENT_SECRET else "none",
            })
            return

        if path == "/oauth/token":
            if body_data.get("grant_type") != "authorization_code":
                self._json(400, {"error": "unsupported_grant_type"})
                return
            eintrag = _AUTH_CODES.pop(body_data.get("code", ""), None)
            if not eintrag or eintrag["expires"] < time.time():
                self._json(400, {"error": "invalid_grant", "error_description": "Code ungueltig oder abgelaufen"})
                return
            if eintrag["code_challenge"] and not _pkce_gueltig(
                body_data.get("code_verifier", ""), eintrag["code_challenge"], eintrag["code_challenge_method"]
            ):
                self._json(400, {"error": "invalid_grant", "error_description": "PKCE-Verifikation fehlgeschlagen"})
                return
            token = secrets.token_urlsafe(32)
            _ACCESS_TOKENS[token] = time.time() + _TOKEN_TTL_S
            _tokens_speichern()
            self._json(200, {
                "access_token": token,
                "token_type": "Bearer",
                "expires_in": _TOKEN_TTL_S,
                "scope": "tools",
                "resource": body_data.get("resource") or eintrag.get("resource") or f"{PUBLIC_BASE_URL}/mcp",
            })
            return

        if path.startswith("/tool/"):
            # Custom-GPT-Actions-Weg: direkter REST-Aufruf eines einzelnen Tools --
            # eigener, einfacherer Pfad ohne die MCP-securitySchemes-Mechanik unten,
            # bleibt bei der klassischen pauschalen Pruefung.
            if not self._autorisiert():
                self._unauthorized()
                return
            name = path[len("/tool/"):]
            spec = TOOLS.get(name)
            if not spec:
                self._json(404, {"error": f"Unbekanntes Tool: {name}"})
                return
            # 2026-07-23 Redteam-Fund: dieser REST-Pfad (fuer Custom-GPT-Actions) hatte
            # kein try/except -- ungueltige Eingaben (z.B. nicht-numerisches limit/cursor,
            # falscher Typ statt String) liessen die Exception bis zum HTTP-Handler
            # durchschlagen (Verbindungsabbruch statt sauberer JSON-Fehlerantwort), im
            # Gegensatz zum JSON-RPC-Pfad (tools/call), der bereits gewrappt war.
            try:
                self._json(200, _tool_ausfuehren_mit_harness(name, body_data, spec))
            except Exception as ex:
                self._json(200, _ergebnis(False, error=f"Tool-Fehler: {ex}"))
            return

        if path in ("/mcp", "/rpc", "/"):
            # 2026-07-23: "App-Verknuepfung erkannt, Tool-Weitergabe noch nicht" (Teil 2) --
            # ChatGPTs MCP-Client schickt initialize+notifications/initialized offenbar als
            # JSON-RPC-BATCH (ein JSON-Array mehrerer Nachrichten in einem POST), nicht als
            # einzelne Requests. Der Server erwartete bisher IMMER ein einzelnes Objekt --
            # bei einem Array crashte body_data.get(...) mit AttributeError (bestaetigt im
            # journalctl-Log: "'list' object has no attribute 'get'"), nginx zeigte 502.
            # Jetzt: einzelne Nachricht ODER Batch (Liste von Nachrichten), pro Nachricht
            # verarbeitet, Notifications liefern KEIN Element in der Antwort (JSON-RPC-2.0-
            # Batch-Regel: nur Antworten zu Requests, nie zu Notifications).
            # 2026-07-23 (Daniel-Fund "3 Stunden about:blank"): _autorisiert() lief
            # bisher pauschal VOR jeder JSON-RPC-Verarbeitung, auch fuer initialize/
            # tools/list -- ChatGPTs Apps-SDK-Auth-Flow braucht laut offizieller Doku
            # (developers.openai.com/apps-sdk/build/auth) aber genau diese beiden
            # OHNE Auth erreichbar ("Tool-Discovery vor dem Login"), plus pro Tool ein
            # securitySchemes-Feld (tools/list) und bei fehlender Auth in tools/call
            # eine CallToolResult-Fehlerantwort mit _meta["mcp/www_authenticate"]
            # statt eines rohen HTTP-401 -- "ohne beide Teile wird das Linking-UI
            # nicht angezeigt". autorisiert wird jetzt einmal ermittelt und pro
            # Methode in _verarbeite_rpc ausgewertet, nicht mehr pauschal vorab.
            autorisiert = self._autorisiert()
            nachrichten = body_data if isinstance(body_data, list) else [body_data]
            # 2026-07-30 (siehe _UNAUTHORIZED_STYLE oben): nur fuer Klone mit explizit
            # gesetztem "http401"-Stil (aktuell nur Grok) -- ein echter HTTP-401 statt der
            # ChatGPT-kompatiblen 200+_meta-Antwort, wenn ein tools/call ohne Token dabei ist.
            if not autorisiert and _UNAUTHORIZED_STYLE == "http401" and any(
                isinstance(n, dict) and n.get("method") in ("tools/call", "mcp.call_tool")
                for n in nachrichten
            ):
                self._unauthorized()
                return
            antworten = [a for a in (self._verarbeite_rpc(n, autorisiert) for n in nachrichten) if a is not None]

            if not antworten:
                # alles Notifications gewesen -- keine Antwort noetig
                self.send_response(202)
                self._cors()
                self.end_headers()
                return
            if isinstance(body_data, list):
                self._json(200, antworten)
            else:
                self._json(200, antworten[0])
            return

        if not self._autorisiert():
            self._unauthorized()
            return

        self.send_response(404)
        self.end_headers()

    def _verarbeite_rpc(self, nachricht, autorisiert: bool) -> dict | None:
        """Verarbeitet EINE JSON-RPC-Nachricht. Gibt None zurueck fuer Notifications
        (kein 'id'-Feld) -- die bekommen laut Spec keine Antwort."""
        if not isinstance(nachricht, dict) or "id" not in nachricht:
            return None
        msg_id = nachricht["id"]
        method = nachricht.get("method", "")
        params = nachricht.get("params", {})

        raw_meta = params.get("_meta", {}) if isinstance(params, dict) else {}
        safe_meta = {}
        if isinstance(raw_meta, dict):
            for key, value in raw_meta.items():
                key_s = str(key)
                key_l = key_s.lower()
                if any(word in key_l for word in ("token", "secret", "authorization", "cookie", "password", "key")):
                    safe_meta[key_s] = "<redacted>"
                elif isinstance(value, (str, int, float, bool)) or value is None:
                    safe_meta[key_s] = str(value)[:300]
                else:
                    safe_meta[key_s] = f"<{type(value).__name__}>"
        _REQUEST_CONTEXT.client = {
            "rpc_method": str(method),
            "param_keys": sorted(str(k) for k in params.keys()) if isinstance(params, dict) else [],
            "meta": safe_meta,
            "top_level_meta_keys": sorted(str(k) for k in (nachricht.get("_meta") or {}).keys())
                if isinstance(nachricht.get("_meta"), dict) else [],
        }

        if method == "initialize":
            client_version = params.get("protocolVersion", "2024-11-05")
            result_payload = {
                "protocolVersion": client_version,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "flextrawurst-vps-mcp", "version": "1.1.1"},
                "instructions": _INIT_INSTRUCTIONS,
            }
        elif method in ("tools/list", "mcp.list_tools"):
            # Ohne Auth erreichbar (Daniel-Fund, siehe Kommentar bei autorisiert oben) --
            # ChatGPT muss securitySchemes lesen koennen BEVOR es ueberhaupt einen
            # Access-Token hat, sonst weiss der Client nicht, welchen OAuth-Flow er
            # ueberhaupt anstossen soll.
            result_payload = {
                "tools": [
                    {"name": _tool_name_normalisieren(n), "description": s["description"], "inputSchema": s["inputSchema"],
                     "securitySchemes": _TOOL_SECURITY_SCHEMES}
                    for n, s in TOOLS.items()
                ]
            }
        elif method in ("tools/call", "mcp.call_tool"):
            if not autorisiert:
                result_payload = {
                    "isError": True,
                    "content": [{"type": "text", "text": "Nicht autorisiert -- OAuth-Login noetig."}],
                    "_meta": {"mcp/www_authenticate": _WWW_AUTHENTICATE_HEADER},
                }
            else:
                tool_name = params.get("name", "")
                args = params.get("arguments", {})
                spec = _tool_spec_aufloesen(tool_name)
                if not spec:
                    result_payload = {"content": [{"type": "text", "text": json.dumps({"error": f"Unbekanntes Tool: {tool_name}"})}]}
                else:
                    try:
                        res = _tool_ausfuehren_mit_harness(tool_name, args, spec)
                    except Exception as ex:
                        res = _ergebnis(False, error=str(ex))
                    result_payload = {"content": [{"type": "text", "text": json.dumps(res, ensure_ascii=False)}]}
        else:
            return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": "Method not found"}}

        return {"jsonrpc": "2.0", "id": msg_id, "result": result_payload}


class LimitedThreadingMixIn(ThreadingMixIn):
    """Threading HTTP server with a hard cap against request/FD exhaustion."""

    def process_request(self, request, client_address):
        if not _HTTP_WORKER_SLOTS.acquire(blocking=False):
            try:
                self.shutdown_request(request)
            except OSError:
                request.close()
            return

        def run_request():
            try:
                self.process_request_thread(request, client_address)
            finally:
                _HTTP_WORKER_SLOTS.release()

        thread = threading.Thread(target=run_request)
        thread.daemon = self.daemon_threads
        try:
            thread.start()
        except BaseException:
            _HTTP_WORKER_SLOTS.release()
            self.shutdown_request(request)
            raise


class ReusableHTTPServer(LimitedThreadingMixIn, HTTPServer):
    # Ein langsamer oder festhängender Werkzeugaufruf darf nicht den einzigen
    # HTTP-Handler blockieren und dadurch alle anderen MCP-Aufrufe in 502/Timeout
    # treiben. Threads sind pro Request isoliert; beim Dienststopp nicht auf
    # hängende Client-Verbindungen warten.
    daemon_threads = True
    block_on_close = False
    allow_reuse_address = True
    request_queue_size = _MAX_HTTP_WORKERS


if __name__ == "__main__":
    _tokens_laden()
    print(f"⚡ Flextrawurst VPS-MCP-Werkzeugkoerper startet auf Port {PORT}... "
          f"({len(_ACCESS_TOKENS)} bestehende OAuth-Tokens aus {_TOKEN_SPEICHER_PFAD} geladen)")
    server = ReusableHTTPServer(("127.0.0.1", PORT), VPSHandler)
    server.serve_forever()
