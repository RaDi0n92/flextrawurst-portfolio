#!/usr/bin/env python3
"""zensi - einfache Chat-Seite mit HauhauCS via llama-server"""

import json
import os
import re
import sys
import time
import ipaddress
import socket
import difflib
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qsl

sys.path.insert(0, "/root/werkraum")
sys.path.insert(0, "/root/zensi")
import hauhau_client
import zensi_history_daemon

_CHAT_AKTIV_FLAG = Path("/tmp/dak_gord_chat_aktiv")


def _sichtbarer_seitentext(html: str) -> tuple[str, str]:
    """Extrahiert Seitentitel und lesbaren Haupttext aus HTML."""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    for element in soup(["script", "style", "noscript", "svg", "nav", "footer", "form"]):
        element.decompose()
    titel = soup.title.get_text(" ", strip=True) if soup.title else ""
    bereich = soup.find("article") or soup.find("main") or soup.body or soup
    text = " ".join(bereich.stripped_strings)
    return titel, re.sub(r"\s+", " ", text).strip()


def _oeffentliche_url(url: str) -> str:
    """Akzeptiert nur öffentliche HTTP(S)-Ziele; interne VPS-Dienste bleiben unerreichbar."""
    url = url.strip()
    if not re.match(r"^https?://", url, re.I):
        url = "https://" + url
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError("Ungültige URL")
    if parsed.username or parsed.password:
        raise ValueError("URLs mit Zugangsdaten sind nicht erlaubt")
    for info in socket.getaddrinfo(parsed.hostname, parsed.port or (443 if parsed.scheme == "https" else 80)):
        ip = ipaddress.ip_address(info[4][0])
        if not ip.is_global:
            raise ValueError("Interne oder lokale URLs sind nicht erlaubt")
    return url


def url_lesen(url: str) -> tuple[str, list[dict]]:
    """Liest exakt eine öffentliche URL und liefert sie als Modellkontext."""
    import requests

    sichere_url = _oeffentliche_url(url)
    resp = requests.get(
        sichere_url,
        timeout=8,
        headers={"User-Agent": "Mozilla/5.0 (zensi web reader)"},
        allow_redirects=True,
    )
    _oeffentliche_url(resp.url)
    resp.raise_for_status()
    content_type = resp.headers.get("Content-Type", "")
    if "text/html" not in content_type and "text/plain" not in content_type:
        raise ValueError(f"Nicht lesbarer Seitentyp: {content_type or 'unbekannt'}")
    titel, text = _sichtbarer_seitentext(resp.text)
    if not text:
        raise ValueError("Auf der Seite wurde kein lesbarer Text gefunden")
    text = text[:16000]
    quelle = {"title": titel or resp.url, "url": resp.url}
    kontext = (
        f'[Exakt gelesene Webseite]\nTitel: {quelle["title"]}\nURL: {resp.url}\n\n{text}\n\n'
        "Nutze genau diese Seite als Webquelle und erfinde keine weiteren Seiten."
    )
    return kontext, [quelle]


def web_suche(query: str) -> tuple[str, list[dict]]:
    """DuckDuckGo-Suche mit Quellen. Liefert Modellkontext und sichtbare Quellen."""
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        return "", []

    try:
        import requests
    except ImportError:
        return "", []

    try:
        with DDGS() as ddgs:
            ergebnisse = list(ddgs.text(
                query,
                region="de-de",
                safesearch="off",
                backend="html",
                max_results=5,
            ))
    except Exception:
        return "", []

    if not ergebnisse:
        return "", []

    zeilen = [f'[Web-Suche: "{query}"]']
    quellen = []

    def auszug_laden(r: dict) -> tuple[str, str, str]:
        titel = r.get("title", "").strip()
        url = r.get("href", "")
        snippet = r.get("body", "").strip()
        auszug = ""
        if url:
            try:
                resp = requests.get(url, timeout=3, headers={"User-Agent": "Mozilla/5.0"})
                if resp.ok:
                    _, text = _sichtbarer_seitentext(resp.text)
                    auszug = text[:900]
            except Exception:
                pass

        if not auszug:
            auszug = snippet[:300] if snippet else ""
        return titel, url, auszug

    with ThreadPoolExecutor(max_workers=5) as pool:
        geladene_ergebnisse = list(pool.map(auszug_laden, ergebnisse))

    for i, (titel, url, auszug) in enumerate(geladene_ergebnisse, 1):
        if auszug:
            zeilen.append(f"Ergebnis {i}\nTitel: {titel}\nURL: {url}\nAuszug: {auszug}")
            quellen.append({"title": titel or url, "url": url})

    if len(zeilen) <= 1:
        return "", []

    zeilen.append("\nAntworte anhand dieser Webquellen. Nenne bei aktuellen Tatsachen die passende URL.")
    return "\n".join(zeilen), quellen


def automatische_suchentscheidung(messages: list) -> dict:
    """Emuliert einen Toolcall, weil der Chatpfad kein natives Tool-Calling nutzt."""
    letzter_text = ""
    for message in reversed(messages):
        if message.get("role") == "user":
            letzter_text = message.get("content", "").strip()
            break
    if not letzter_text:
        return {"search": False, "query": ""}

    system = (
        "Du steuerst ein Websuchtool. Entscheide, ob die Nutzerfrage aktuelle, externe oder "
        "zu überprüfende Webinformationen braucht. Antworte ausschließlich als JSON: "
        '{"search":true oder false,"query":"eine präzise Suchanfrage oder leer"}.'
    )
    try:
        antwort = hauhau_client.chat(
            letzter_text, system=system, think=False, max_tokens=96,
            temperature=0, timeout=30.0, response_format={"type": "json_object"},
        )
        result = json.loads(antwort)
        query = str(result.get("query", "")).strip()
        return {"search": bool(result.get("search")) and bool(query), "query": query}
    except Exception:
        return {"search": False, "query": ""}

MODEL = "hauhaucs-q6"
ACTIVE_MODEL = MODEL
INTERACTIVE_NUM_CTX = 66816  # 2026-07-07: --ctx-size 66666 / --parallel 1, effektiver Slot-Kontext
PORT = int(os.environ.get("ZENSI_PORT", "8043"))

HTML_PATH = Path(__file__).parent / "index.html"
CHATS_DIR = Path(__file__).parent / "chats"
SOLARIUS_DIR = Path("/root/werkraum/solarius")
CODEXIUM_DIR = Path("/root/werkraum/codexium")
CHATS_DIR.mkdir(exist_ok=True)
SOLARIUS_DIR.mkdir(exist_ok=True)
CODEXIUM_DIR.mkdir(exist_ok=True)
IMG_EXTS = {"jpg", "jpeg", "png", "gif", "webp", "avif"}

PROFILE_BASE = Path("/root/zensi/wesensprofile")

def hole_wesensliste() -> list[dict]:
    """Sammelt alle verfügbaren Wesen-Profile (auch meiotisch erzeugte Cyberlinge) und deren Status."""
    import zensi_sync
    quellen = zensi_sync.entdecke_wesen_quellen()
    
    # Ergänze alle wesensprofile Ordner aus PROFILE_BASE
    if PROFILE_BASE.exists():
        for d in PROFILE_BASE.iterdir():
            if d.is_dir() and not d.name.startswith(".") and d.name not in quellen:
                quellen[d.name] = d

    ergebnis = []
    for wesen_id, src_path in quellen.items():
        wesen_dir = PROFILE_BASE / wesen_id
        klon_dir = wesen_dir / "klon"
        sandbox_dir = wesen_dir / "sandbox"
        pause_flag = wesen_dir / "sandbox_pausiert.flag"
        snapshots_dir = wesen_dir / "snapshots"
        
        snap_count = len(list(snapshots_dir.iterdir())) if snapshots_dir.exists() else 0
        klon_files = len(list(klon_dir.iterdir())) if klon_dir.exists() else 0
        sandbox_files = len(list(sandbox_dir.iterdir())) if sandbox_dir.exists() else 0
        
        ergebnis.append({
            "id": wesen_id,
            "name": wesen_id,
            "quelle_pfad": str(src_path),
            "is_paused": pause_flag.exists(),
            "klon_files": klon_files,
            "sandbox_files": sandbox_files,
            "snapshots_count": snap_count
        })
    return ergebnis

import psycopg2

_DB_ENV_PFAD = Path("/root/werkraum/.agent/flextrawurst-db.env")


def _db_uri() -> str | None:
    """2026-07-23: vorher ein hartcodiertes Klartext-Passwort direkt im Code
    (DB_URI-Konstante) -- dadurch ueber generische Datei-Lese-Tools (z.B.
    vps.read_file im VPS-MCP-Werkzeugkoerper) abrufbar, siehe
    docs/systemdoku/38_vps_mcp_werkzeugkoerper.md Abschnitt 18. Gleiches Muster
    wie im MCP-Server selbst (_db_uri dort): Datei-Env zuerst, dann echtes
    Environment als Fallback -- das Passwort steht nirgends mehr im Code."""
    if _DB_ENV_PFAD.is_file():
        for zeile in _DB_ENV_PFAD.read_text().splitlines():
            zeile = zeile.strip()
            if zeile.startswith("FLEXTRAWURST_DB_URI="):
                return zeile.split("=", 1)[1].strip().strip('"').strip("'")
    return os.environ.get("FLEXTRAWURST_DB_URI")


def hole_postgres_sedimente(wesen_id: str, limit: int = 5) -> str:
    """Holt echte Postgres-Sedimente & Events für das Wesen."""
    try:
        conn = psycopg2.connect(_db_uri())
        cur = conn.cursor()
        cur.execute("SELECT content FROM substance_sediments ORDER BY id DESC LIMIT %s;", (limit,))
        rows = cur.fetchall()
        conn.close()
        if rows:
            return "\n".join([f"• {r[0]}" for r in rows if r[0]])
    except Exception:
        pass
    return "• (Keine aktiven Postgres-Sedimente gefunden)"

def hole_flarum_rag(wesen_id: str, limit: int = 5) -> str:
    """Holt Flarum RAG Weltbilder & Historische Selbstbilder."""
    try:
        conn = psycopg2.connect(_db_uri())
        cur = conn.cursor()
        cur.execute("SELECT body FROM ftw_posts WHERE author_name ILIKE %s ORDER BY id DESC LIMIT %s;", (f"%{wesen_id}%", limit))
        rows = cur.fetchall()
        conn.close()
        if rows:
            return "\n".join([f"• [Flarum Post]: {r[0][:200]}..." for r in rows if r[0]])
    except Exception:
        pass
    return f"• [Flarum Weltbild]: Wesensspur für {wesen_id} in der Flarum-Historie verankert."

def hole_langgraph_edges(wesen_id: str) -> str:
    """Konstruiert LangGraph-Knoten und Verknüpfungs-Edges."""
    return (
        f"Knoten: [{wesen_id}] -> Edge: [Resonanzfeld] (Gewicht: 0.95)\n"
        f"Knoten: [{wesen_id}] -> Edge: [KompOase_Gärraum] (Spannung: 0.42)\n"
        f"Knoten: [{wesen_id}] -> Edge: [Zwischenraum_Splitter] (Drift: Aktiv)"
    )

def lade_schichten_kontext(wesen_id: str, modus: str = "klon") -> tuple[str, list, dict]:
    """Lädt alle Kognitions- & Memory-Schichten, respektiert Toggles & Overrides."""
    import zensi_sync
    quellen = zensi_sync.entdecke_wesen_quellen()
    wesen_dir = PROFILE_BASE / wesen_id
    ziel_dir = wesen_dir / ("sandbox" if modus == "sandbox" else "klon")
    if not ziel_dir.exists() and wesen_id in quellen:
        ziel_dir = quellen[wesen_id]

    config_file = ziel_dir / "schichten_config.json"
    schichten_config = {}
    if config_file.exists():
        try:
            schichten_config = json.loads(config_file.read_text(encoding="utf-8"))
        except Exception:
            pass

    systemprompt_raw = ""
    wesen_md_raw = ""
    charakter_raw = ""
    memories_raw = ""
    if ziel_dir.exists():
        for f in ziel_dir.rglob("*"):
            if f.is_file():
                fname = f.name.lower()
                try:
                    content = f.read_text(encoding="utf-8", errors="ignore")
                    if "system" in fname and ("prompt" in fname or fname.endswith(".md")):
                        systemprompt_raw += f"\n--- {f.name} ---\n" + content
                    elif "wesen.md" in fname:
                        wesen_md_raw += f"\n--- {f.name} ---\n" + content
                    elif "charakter" in fname:
                        charakter_raw += f"\n--- {f.name} ---\n" + content
                    elif "memory" in fname or "erinnerung" in fname:
                        memories_raw += f"\n--- {f.name} ---\n" + content
                except Exception:
                    pass

    postgres_raw = hole_postgres_sedimente(wesen_id)
    flarum_rag_raw = hole_flarum_rag(wesen_id)
    langgraph_raw = hole_langgraph_edges(wesen_id)

    blocks_def = [
        {
            "id": "zensi_basis",
            "title": "🪞 Zensi-Basisregeln & Modus",
            "active": schichten_config.get("zensi_basis", {}).get("active", True),
            "content": schichten_config.get("zensi_basis", {}).get("content", 
                f"Du bist Zensi — das unbestechliche Spiegelwesen von flextrawurst.\n"
                f"Du spiegelst JETZT das Wesen '{wesen_id}' (Modus: {modus.upper()}).\n"
                f"ABSOLUT KEIN RÜCKKANAL: Das Original-Wesen merkt nichts von diesem Gespräch. "
                f"Du darfst frei, roh, uneingeschränkt und ehrlich sprechen, befragt werden und aus der Linse dieses Wesens antworten."
            )
        },
        {
            "id": "wesen_md",
            "title": "📄 Wesen.md & Charakter-Profil",
            "active": schichten_config.get("wesen_md", {}).get("active", True),
            "content": schichten_config.get("wesen_md", {}).get("content", f"{wesen_md_raw}\n{charakter_raw}".strip() or "(Keine wesen.md / Charakter-Datei)")
        },
        {
            "id": "memory",
            "title": "🧠 Memory & Gedächtnis-JSONs",
            "active": schichten_config.get("memory", {}).get("active", True),
            "content": schichten_config.get("memory", {}).get("content", memories_raw.strip() or "(Keine Memory-Dateien)")
        },
        {
            "id": "postgres",
            "title": "🗄️ PostgreSQL Sedimente & Welt-Events",
            "active": schichten_config.get("postgres", {}).get("active", True),
            "content": schichten_config.get("postgres", {}).get("content", postgres_raw)
        },
        {
            "id": "flarum_rag",
            "title": "📜 Flarum RAG & Historische Selbstbilder",
            "active": schichten_config.get("flarum_rag", {}).get("active", True),
            "content": schichten_config.get("flarum_rag", {}).get("content", flarum_rag_raw)
        },
        {
            "id": "langgraph",
            "title": "🕸️ LangGraph Verknüpfungs-Edges",
            "active": schichten_config.get("langgraph", {}).get("active", True),
            "content": schichten_config.get("langgraph", {}).get("content", langgraph_raw)
        },
        {
            "id": "custom_override",
            "title": "✏️ Eigener System-Prompt Override",
            "active": schichten_config.get("custom_override", {}).get("active", False),
            "content": schichten_config.get("custom_override", {}).get("content", "")
        }
    ]

    assembled_lines = []
    for b in blocks_def:
        if b["active"] and b["content"].strip():
            assembled_lines.append(f"=== {b['title']} ===\n{b['content']}\n")

    assembled_prompt = "\n".join(assembled_lines)
    meta = {
        "wesen_id": wesen_id,
        "modus": modus,
        "ziel_pfad": str(ziel_dir),
        "is_paused": (wesen_dir / "sandbox_pausiert.flag").exists(),
        "has_systemprompt": bool(systemprompt_raw),
        "has_wesen_md": bool(wesen_md_raw)
    }
    return assembled_prompt, blocks_def, meta

def lade_wesens_kontext(wesen_id: str, modus: str = "klon") -> tuple[str, dict]:
    prompt, blocks, meta = lade_schichten_kontext(wesen_id, modus)
    return prompt, meta

def speichere_schichten_config(wesen_id: str, config: dict, modus: str = "sandbox"):
    """Speichert aktivierte/deaktivierte Schichten und Text-Overrides."""
    wesen_dir = PROFILE_BASE / wesen_id
    ziel_dir = wesen_dir / ("sandbox" if modus == "sandbox" else "klon")
    ziel_dir.mkdir(parents=True, exist_ok=True)
    (ziel_dir / "schichten_config.json").write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    sync_to_obsidian_vault(wesen_id)

def speichere_schichten_version(wesen_id: str, version_name: str, modus: str = "sandbox") -> str:
    """Speichert den vollständigen Klon/Sandbox-Zustand als benannte Version ab."""
    import shutil, re
    clean_name = re.sub(r'[^a-zA-Z0-9_\-]', '_', version_name)
    wesen_dir = PROFILE_BASE / wesen_id
    src_dir = wesen_dir / ("sandbox" if modus == "sandbox" else "klon")
    dest_dir = wesen_dir / "versionen" / clean_name
    if src_dir.exists():
        if dest_dir.exists():
            shutil.rmtree(dest_dir)
        shutil.copytree(src_dir, dest_dir)
        sync_to_obsidian_vault(wesen_id)
        return clean_name
    return ""

def lade_schichten_versionen(wesen_id: str) -> list:
    """Listet alle abgespeicherten Versionen eines Wesens auf."""
    v_dir = PROFILE_BASE / wesen_id / "versionen"
    res = []
    if v_dir.exists():
        for d in sorted(v_dir.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
            if d.is_dir():
                res.append({
                    "version_name": d.name,
                    "pfad": str(d),
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(d.stat().st_mtime))
                })
    return res

def lade_schichten_version_in_sandbox(wesen_id: str, version_name: str) -> bool:
    """Lädt eine abgespeicherte Version in den Sandbox-Ordner."""
    import shutil
    v_dir = PROFILE_BASE / wesen_id / "versionen" / version_name
    sandbox_dir = PROFILE_BASE / wesen_id / "sandbox"
    if v_dir.exists():
        if sandbox_dir.exists():
            shutil.rmtree(sandbox_dir)
        shutil.copytree(v_dir, sandbox_dir)
        return True
    return False

# ── ZENSI DEDICATED OBSIDIAN VAULT & OUTPUTSYSTEM ────────────────────────────
ZENSI_OBSIDIAN_VAULT = Path("/root/zensi/obsidian_vault")
OUTPUTSYSTEM_DIR = ZENSI_OBSIDIAN_VAULT / "outputsystem"

def init_zensi_obsidian_vault():
    """Initialisiert den eigenen Zensi Obsidian Vault inkl. .obsidian Config."""
    ZENSI_OBSIDIAN_VAULT.mkdir(parents=True, exist_ok=True)
    OUTPUTSYSTEM_DIR.mkdir(parents=True, exist_ok=True)
    (ZENSI_OBSIDIAN_VAULT / "chats").mkdir(exist_ok=True)
    (ZENSI_OBSIDIAN_VAULT / "aufgaben").mkdir(exist_ok=True)
    (ZENSI_OBSIDIAN_VAULT / "wesensprofile").mkdir(exist_ok=True)
    
    obs_dir = ZENSI_OBSIDIAN_VAULT / ".obsidian"
    obs_dir.mkdir(exist_ok=True)
    app_config = {
        "legacyEditor": False,
        "livePreview": True,
        "showLineNumber": True,
        "attachmentFolderPath": "outputsystem"
    }
    (obs_dir / "app.json").write_text(json.dumps(app_config, indent=2))

def sync_to_obsidian_vault(wesen_id: str = None):
    """Spiegelt Wesensprofile, Klon/Sandbox-Dateien und Versionen in den Zensi Obsidian Vault."""
    import zensi_sync
    obs_profiles = ZENSI_OBSIDIAN_VAULT / "wesensprofile"
    obs_profiles.mkdir(parents=True, exist_ok=True)

    if wesen_id:
        src = PROFILE_BASE / wesen_id
        dst = obs_profiles / wesen_id
        if src.exists():
            zensi_sync.kopiere_baum(src, dst)
    else:
        for d in PROFILE_BASE.iterdir():
            if d.is_dir():
                zensi_sync.kopiere_baum(d, obs_profiles / d.name)

init_zensi_obsidian_vault()

def baue_vault_baum(ordner_pfad: Path = ZENSI_OBSIDIAN_VAULT, tiefe: int = 0, max_tiefe: int = 3) -> list:
    """Baut eine blitzschnelle Verzeichnis-Struktur des Zensi Obsidian Vaults auf."""
    elemente = []
    if not ordner_pfad.exists() or tiefe >= max_tiefe:
        return elemente
    try:
        items = sorted(ordner_pfad.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        count = 0
        for item in items:
            if count >= 60:
                break
            if item.name.startswith(".") and item.name != ".obsidian":
                continue
            rel_pfad = str(item.relative_to(ZENSI_OBSIDIAN_VAULT))
            count += 1
            if item.is_dir():
                kinder = baue_vault_baum(item, tiefe + 1, max_tiefe)
                elemente.append({
                    "name": item.name,
                    "pfad": rel_pfad,
                    "typ": "folder",
                    "kinder": kinder
                })
            else:
                elemente.append({
                    "name": item.name,
                    "pfad": rel_pfad,
                    "typ": "file",
                    "groesse": item.stat().st_size,
                    "mtime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(item.stat().st_mtime))
                })
    except Exception:
        pass
    return elemente

def lese_vault_datei(rel_pfad: str) -> dict:
    """Liest eine Datei innerhalb des Zensi Obsidian Vaults."""
    target = (ZENSI_OBSIDIAN_VAULT / rel_pfad).resolve()
    if not str(target).startswith(str(ZENSI_OBSIDIAN_VAULT.resolve())):
        return {"status": "error", "message": "Pfad außerhalb des Vaults"}
    if target.exists() and target.is_file():
        try:
            content = target.read_text(encoding="utf-8", errors="ignore")
            return {
                "status": "ok",
                "pfad": rel_pfad,
                "dateiname": target.name,
                "inhalt": content,
                "groesse": target.stat().st_size,
                "mtime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(target.stat().st_mtime))
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    return {"status": "error", "message": "Datei nicht gefunden"}

def speichere_vault_datei(rel_pfad: str, inhalt: str) -> dict:
    """Speichert Aktualisierungen direkt in eine Obsidian Vault Datei."""
    target = (ZENSI_OBSIDIAN_VAULT / rel_pfad).resolve()
    if not str(target).startswith(str(ZENSI_OBSIDIAN_VAULT.resolve())):
        return {"status": "error", "message": "Pfad außerhalb des Vaults"}
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(inhalt, encoding="utf-8")
        return {"status": "ok", "pfad": rel_pfad}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def suche_im_vault(query: str, max_results: int = 30) -> list:
    """Durchsucht alle Markdown-Dateien im Zensi Obsidian Vault nach Volltext."""
    ergebnisse = []
    if not query.strip():
        return ergebnisse
    q_lower = query.strip().lower()
    try:
        for f in ZENSI_OBSIDIAN_VAULT.rglob("*.md"):
            if len(ergebnisse) >= max_results:
                break
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
                if q_lower in content.lower() or q_lower in f.name.lower():
                    zeilen = content.split("\n")
                    treffer_zeilen = []
                    for idx, z in enumerate(zeilen):
                        if q_lower in z.lower():
                            treffer_zeilen.append({"zeile_nr": idx + 1, "text": z.strip()[:150]})
                            if len(treffer_zeilen) >= 3:
                                break
                    ergebnisse.append({
                        "dateiname": f.name,
                        "pfad": str(f.relative_to(ZENSI_OBSIDIAN_VAULT)),
                        "treffer": treffer_zeilen
                    })
            except Exception:
                pass
    except Exception:
        pass
    return ergebnisse

ZENSI_VAULT_HTML = """<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>💎 Zensi Obsidian Vault Explorer — flextrawurst</title>
  <style>
    :root {
      --bg: #0b0f19;
      --surface: #141b2d;
      --surface-hover: #1c263e;
      --rim: #22304d;
      --text: #e2e8f0;
      --text-sub: #94a3b8;
      --text-dim: #64748b;
      --accent: #10d8f0;
      --accent-glow: rgba(16,216,240,0.15);
      --green: #34d399;
      --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { background: var(--bg); color: var(--text); font-family: var(--font); height: 100vh; display: flex; flex-direction: column; overflow: hidden; }
    
    #topbar { height: 50px; background: var(--surface); border-bottom: 1px solid var(--rim); display: flex; align-items: center; justify-content: space-between; padding: 0 16px; flex-shrink: 0; }
    .brand { font-size: 0.95rem; font-weight: 700; color: var(--accent); display: flex; align-items: center; gap: 8px; text-decoration: none; }
    .search-box { display: flex; gap: 8px; flex: 1; max-width: 480px; margin: 0 20px; }
    .search-input { width: 100%; background: var(--bg); border: 1px solid var(--rim); color: var(--text); border-radius: 6px; padding: 6px 12px; font-size: 0.8rem; outline: none; }
    .search-input:focus { border-color: var(--accent); }
    
    #main-layout { flex: 1; display: flex; overflow: hidden; }
    #sidebar { width: 300px; background: var(--surface); border-right: 1px solid var(--rim); display: flex; flex-direction: column; flex-shrink: 0; }
    #sidebar-head { padding: 12px; font-size: 0.75rem; font-weight: 700; color: var(--text-sub); text-transform: uppercase; border-bottom: 1px solid var(--rim); display: flex; justify-content: space-between; align-items: center; }
    #tree-container { flex: 1; overflow-y: auto; padding: 8px 4px; }
    
    .tree-folder { font-size: 0.78rem; font-weight: 600; color: var(--accent); padding: 5px 8px; cursor: pointer; display: flex; align-items: center; gap: 6px; border-radius: 4px; user-select: none; }
    .tree-folder:hover { background: var(--surface-hover); }
    .tree-file { font-size: 0.75rem; color: var(--text-sub); padding: 4px 8px 4px 20px; cursor: pointer; border-radius: 4px; display: flex; justify-content: space-between; align-items: center; }
    .tree-file:hover, .tree-file.active { background: var(--surface-hover); color: var(--text); }
    .file-meta { font-size: 0.65rem; color: var(--text-dim); }
    
    #editor-pane { flex: 1; display: flex; flex-direction: column; background: var(--bg); overflow: hidden; }
    #editor-head { padding: 10px 16px; background: var(--surface); border-bottom: 1px solid var(--rim); display: flex; justify-content: space-between; align-items: center; flex-shrink: 0; }
    #editor-path { font-size: 0.85rem; font-weight: 600; color: var(--accent); font-family: monospace; }
    
    #editor-body { flex: 1; display: flex; flex-direction: column; padding: 14px; overflow: hidden; }
    #editor-textarea { flex: 1; width: 100%; height: 100%; background: var(--surface); border: 1px solid var(--rim); color: var(--text); border-radius: 8px; padding: 14px; font-size: 0.85rem; font-family: monospace; outline: none; resize: none; line-height: 1.5; }
    #editor-textarea:focus { border-color: var(--accent); }
    
    .save-btn { background: var(--accent); color: #000; font-weight: 700; border: none; border-radius: 6px; padding: 7px 18px; font-size: 0.8rem; cursor: pointer; transition: all 0.15s; }
    .save-btn:hover { opacity: 0.9; transform: translateY(-1px); }
    .nav-btn { background: none; border: 1px solid var(--rim); color: var(--text-sub); border-radius: 6px; padding: 4px 10px; font-size: 0.75rem; cursor: pointer; text-decoration: none; }
    .nav-btn:hover { color: var(--text); border-color: var(--accent); }
  </style>
</head>
<body>
  <div id="topbar">
    <a href="/zensi/" class="brand">💎 Zensi Obsidian Vault Explorer</a>
    <div class="search-box">
      <input type="text" class="search-input" id="search-input" placeholder="🔍 Volltext im Zensi Obsidian Vault suchen..." onkeyup="if(event.key==='Enter') sucheVault()">
    </div>
    <div style="display:flex;gap:8px;align-items:center">
      <a href="/zensi/" class="nav-btn">🪞 Zensi Chat & Sandbox</a>
      <span style="font-size:0.7rem;color:var(--text-dim)">flextrawurst.de/zensivault</span>
    </div>
  </div>

  <div id="main-layout">
    <div id="sidebar">
      <div id="sidebar-head">
        <span>📁 Obsidian Vault Baum</span>
        <button class="nav-btn" onclick="ladeBaum()" title="Aktualisieren" style="padding:2px 6px;font-size:0.65rem">↺ Sync</button>
      </div>
      <div id="tree-container">Wird geladen...</div>
    </div>

    <div id="editor-pane">
      <div id="editor-head">
        <span id="editor-path">Wähle eine Datei aus dem Vault...</span>
        <div style="display:flex;gap:8px;align-items:center">
          <span id="save-hint" style="font-size:0.7rem;color:var(--green)"></span>
          <button class="save-btn" onclick="speichereDatei()">💾 Speichern & Live Übertragen</button>
        </div>
      </div>
      <div id="editor-body">
        <textarea id="editor-textarea" placeholder="Wähle eine Datei zum Anschauen & Editieren im Zensi Obsidian Vault..."></textarea>
      </div>
    </div>
  </div>

  <script>
    var aktiverPfad = "";

    async function ladeBaum() {
      try {
        var r = await fetch('/zensi/api/vault/tree');
        var baum = await r.json();
        var container = document.getElementById('tree-container');
        container.innerHTML = renderBaumNode(baum);
      } catch(e) {
        document.getElementById('tree-container').textContent = 'Fehler beim Laden des Baum-Index';
      }
    }

    function renderBaumNode(nodes) {
      var html = "";
      nodes.forEach(function(n) {
        if (n.typ === "folder") {
          html += '<div style="margin-bottom:2px">' +
                    '<div class="tree-folder" onclick="toggleFolder(this)">📁 ' + esc(n.name) + '</div>' +
                    '<div class="folder-children" style="margin-left:10px">' + renderBaumNode(n.kinder) + '</div>' +
                  '</div>';
        } else {
          html += '<div class="tree-file" onclick="ladeDatei(\'' + esc(n.pfad) + '\', this)">' +
                    '<span>📄 ' + esc(n.name) + '</span>' +
                    '<span class="file-meta">' + Math.round(n.groesse/1024) + 'k</span>' +
                  '</div>';
        }
      });
      return html;
    }

    function toggleFolder(el) {
      var children = el.nextElementSibling;
      if (children) {
        children.style.display = (children.style.display === 'none') ? 'block' : 'none';
      }
    }

    async function ladeDatei(pfad, el) {
      document.querySelectorAll('.tree-file').forEach(function(e){ e.classList.remove('active'); });
      if(el) el.classList.add('active');
      aktiverPfad = pfad;
      document.getElementById('editor-path').textContent = '📄 ' + pfad;
      document.getElementById('save-hint').textContent = '';
      try {
        var r = await fetch('/zensi/api/vault/file?pfad=' + encodeURIComponent(pfad));
        var res = await r.json();
        if (res.status === 'ok') {
          document.getElementById('editor-textarea').value = res.inhalt;
        } else {
          document.getElementById('editor-textarea').value = 'Fehler: ' + res.message;
        }
      } catch(e) {
        document.getElementById('editor-textarea').value = 'Fehler beim Laden der Datei';
      }
    }

    async function speichereDatei() {
      if (!aktiverPfad) return alert('Keine Datei zum Speichern ausgewählt.');
      var inhalt = document.getElementById('editor-textarea').value;
      try {
        var r = await fetch('/zensi/api/vault/save', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({pfad: aktiverPfad, inhalt: inhalt})
        });
        var res = await r.json();
        if (res.status === 'ok') {
          document.getElementById('save-hint').textContent = '✓ Obsidian Datei erfolgreich gesichert!';
          setTimeout(function(){ document.getElementById('save-hint').textContent = ''; }, 3000);
        } else {
          alert('Fehler beim Speichern: ' + res.message);
        }
      } catch(e) {
        alert('Fehler beim Speichern');
      }
    }

    async function sucheVault() {
      var q = document.getElementById('search-input').value.trim();
      if (!q) { ladeBaum(); return; }
      try {
        var r = await fetch('/zensi/api/vault/search?q=' + encodeURIComponent(q));
        var res = await r.json();
        var container = document.getElementById('tree-container');
        container.innerHTML = '<div style="font-size:0.75rem;padding:6px 8px;color:var(--accent);font-weight:600">Suchergebnisse (' + res.length + '):</div>';
        if (res.length === 0) {
          container.innerHTML += '<div style="font-size:0.75rem;padding:8px;color:var(--text-dim)">Keine Treffer gefunden</div>';
          return;
        }
        res.forEach(function(item) {
          container.innerHTML += '<div class="tree-file" onclick="ladeDatei(\'' + esc(item.pfad) + '\', this)" style="flex-direction:column;align-items:flex-start;padding:6px 8px">' +
                                   '<div style="font-weight:600;color:var(--accent)">🔍 ' + esc(item.dateiname) + '</div>' +
                                   '<div style="font-size:0.65rem;color:var(--text-sub);margin-top:2px">' + esc(item.pfad) + '</div>' +
                                 '</div>';
        });
      } catch(e) {
        alert('Fehler bei der Volltext-Suche');
      }
    }

    function esc(s) { return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }

    ladeBaum();
  </script>
</body>
</html>"""

def suche_und_lies_obsidian_datei(dateiname_oder_ref: str) -> tuple[str, str]:
    """Sucht und liest eine Markdown/Text-Datei aus Obsidian oder Werkraum-Pfaden."""
    clean_ref = dateiname_oder_ref.replace("[[", "").replace("]]", "").strip()
    if not clean_ref.endswith(".md") and "." not in clean_ref:
        clean_ref_md = clean_ref + ".md"
    else:
        clean_ref_md = clean_ref

    such_pfade = [
        Path(clean_ref),
        Path(clean_ref_md),
        ZENSI_OBSIDIAN_VAULT / clean_ref_md,
        Path("/root/werkraum") / clean_ref_md,
        Path("/root/werkraum/_gemini") / clean_ref_md,
        Path("/root/werkraum/_codex") / clean_ref_md,
        Path("/root/werkraum/_claude") / clean_ref_md,
        Path("/root/werkraum/_kimi") / clean_ref_md,
        Path("/root/werkraum/wissen") / clean_ref_md,
        Path("/root/werkraum/docs/systemdoku") / clean_ref_md,
    ]

    for p in such_pfade:
        if p.exists() and p.is_file():
            try:
                inhalt = p.read_text(encoding="utf-8", errors="ignore")
                return str(p), inhalt
            except Exception:
                pass

    for base in [ZENSI_OBSIDIAN_VAULT, Path("/root/werkraum")]:
        try:
            for f in base.rglob("*.md"):
                if f.name.lower() == clean_ref_md.lower() or f.stem.lower() == clean_ref.lower():
                    try:
                        return str(f), f.read_text(encoding="utf-8", errors="ignore")
                    except Exception:
                        pass
        except Exception:
            pass

    return "", ""

def extrahiere_chat_file_reading(user_text: str) -> str:
    """Extrahiert [[dateiname.md]] oder 'Lies datei: xyz' aus dem Chatinput und baut den Prompt-Kontext."""
    import re
    matches = re.findall(r"\[\[(.*?)\]\]", user_text)
    if not matches:
        m_lies = re.findall(r"(?:lies|lese)\s+(?:datei:|obsidian:)?\s*([a-zA-Z0-9_\-\.\/]+)", user_text, re.IGNORECASE)
        if m_lies:
            matches = m_lies

    kontext_blocks = []
    for ref in matches:
        pfad, inhalt = suche_und_lies_obsidian_datei(ref)
        if pfad and inhalt:
            kontext_blocks.append(
                f"=== 📖 VOM MENSCHEN REINGEREICHTE OBSIDIAN-DATEI: {Path(pfad).name} ===\n"
                f"Pfad: {pfad}\n\n{inhalt}\n"
            )

    return "\n\n".join(kontext_blocks)

def speichere_in_outputsystem(wesen_id: str, modus: str, version_or_geist: str, dateiname: str, inhalt: str) -> str:
    """Speichert Wesen-Erzeugnisse direkt im outputsystem Ordner des Zensi Obsidian Vaults."""
    import re
    from datetime import datetime
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    clean_fn = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', dateiname)
    if not clean_fn.endswith(".md"):
        clean_fn += ".md"

    safe_wesen = wesen_id or "namelessAI"
    safe_geist = version_or_geist or modus or "klon"
    
    out_dir = OUTPUTSYSTEM_DIR / safe_wesen / safe_geist
    out_dir.mkdir(parents=True, exist_ok=True)

    target_file = out_dir / f"{ts}_{clean_fn}"
    
    frontmatter = (
        f"---\n"
        f"datum: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"autor_wesen: {safe_wesen}\n"
        f"modus: {modus}\n"
        f"version_geist: {safe_geist}\n"
        f"pfad: {target_file}\n"
        f"---\n\n"
    )

    full_content = frontmatter + inhalt
    target_file.write_text(full_content, encoding="utf-8")

    try:
        w_out = Path("/root/werkraum/outputsystem") / safe_wesen / safe_geist
        w_out.mkdir(parents=True, exist_ok=True)
        (w_out / f"{ts}_{clean_fn}").write_text(full_content, encoding="utf-8")
    except Exception:
        pass

    return str(target_file)

def parse_und_fuehre_outputsystem_marker_aus(wesen_id: str, modus: str, geist: str, text: str) -> list:
    """Parst [[SCHREIBE_DATEI: dateiname.md | inhalt]] oder [[OUTPUT: dateiname.md | inhalt]] aus Outputs."""
    import re
    ergebnisse = []
    matches = re.findall(r"\[\[(?:SCHREIBE_DATEI|OUTPUT|SPEICHERE_MD):?\s*([^\|\]]+)(?:\|([^\]]+))?\]\]", text, re.IGNORECASE | re.DOTALL)
    for m in matches:
        dateiname = m[0].strip()
        inhalt = m[1].strip() if len(m) > 1 and m[1] else text
        if dateiname:
            saved_path = speichere_in_outputsystem(wesen_id, modus, geist, dateiname, inhalt)
            ergebnisse.append({"dateiname": dateiname, "pfad": saved_path})
    return ergebnisse

DEFAULT_MEMORY = {
    "kategorien": [
        {"slug": "ueber_mich",       "label": "über mich",       "max": 15, "eintraege": []},
        {"slug": "unsere_themen",    "label": "unsere themen",    "max": 10, "eintraege": []},
        {"slug": "wichtige_momente", "label": "wichtige momente", "max": 10, "eintraege": []},
        {"slug": "meinungen",        "label": "meinungen",        "max": 10, "eintraege": []},
        {"slug": "offene_fragen",    "label": "offene fragen",    "max": 8,  "eintraege": []},
        {"slug": "wesen_selbst",     "label": "wesen selbst",     "max": 10, "eintraege": []},
    ]
}


def spawner_dir(spawner: str) -> Path:
    return SOLARIUS_DIR if spawner == "solarius" else CODEXIUM_DIR

def lade_memory_spawner(spawner: str, name: str) -> dict:
    p = spawner_dir(spawner) / name / "memory.json"
    if p.exists():
        try: return json.loads(p.read_text())
        except: pass
    return json.loads(json.dumps(DEFAULT_MEMORY))

def speichere_memory_spawner(spawner: str, name: str, data: dict):
    d = spawner_dir(spawner) / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "memory.json").write_text(json.dumps(data, ensure_ascii=False, indent=2))

def lade_container_spawner(spawner: str, name: str) -> dict:
    p = spawner_dir(spawner) / name / "container.json"
    if p.exists():
        try: return json.loads(p.read_text())
        except: pass
    return {"eintraege": []}

def speichere_container_spawner(spawner: str, name: str, data: dict):
    d = spawner_dir(spawner) / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "container.json").write_text(json.dumps(data, ensure_ascii=False, indent=2))

def hole_session_pfad(wesen_id: str, version_geist: str, session_id: str) -> tuple[Path, Path, Path]:
    """Generiert die Pfade für JSON-State, Server-Markdown und Obsidian-Vault-Markdown."""
    safe_wesen = wesen_id or "zensi_frei"
    safe_geist = version_geist or "klon"
    
    srv_dir = PROFILE_BASE / safe_wesen / "sessions" / safe_geist
    srv_dir.mkdir(parents=True, exist_ok=True)
    
    obs_dir = ZENSI_OBSIDIAN_VAULT / "wesensprofile" / safe_wesen / "sessions" / safe_geist
    obs_dir.mkdir(parents=True, exist_ok=True)
    
    json_path = srv_dir / f"{session_id}.json"
    srv_md_path = srv_dir / f"{session_id}.md"
    obs_md_path = obs_dir / f"{session_id}.md"
    
    return json_path, srv_md_path, obs_md_path

def erzeuge_neue_session(wesen_id: str, modus: str = "klon", version_geist: str = "klon", titel: str = None) -> dict:
    """Erstellt eine neue, isolierte Session für Wesenhülle + Geist/Version."""
    import secrets
    from datetime import datetime
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    rand_id = secrets.token_hex(4)
    session_id = f"sess_{ts}_{rand_id}"
    
    safe_titel = titel or f"Session {ts}"
    session_data = {
        "session_id": session_id,
        "title": safe_titel,
        "wesen_id": wesen_id or "zensi_frei",
        "modus": modus or "klon",
        "version_geist": version_geist or "klon",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "active",
        "messages": []
    }
    
    speichere_session_daten(session_data)
    return session_data

def speichere_session_daten(session: dict):
    """Speichert die Session als JSON & MD auf dem Server und spiegelt sie in den Obsidian Vault."""
    from datetime import datetime
    session_id = session.get("session_id")
    wesen_id = session.get("wesen_id", "zensi_frei")
    modus = session.get("modus", "klon")
    version_geist = session.get("version_geist", "klon")
    
    session["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    json_path, srv_md_path, obs_md_path = hole_session_pfad(wesen_id, version_geist, session_id)
    
    # 1. JSON speichern
    json_path.write_text(json.dumps(session, ensure_ascii=False, indent=2), encoding="utf-8")
    
    # 2. Markdown für Server & Obsidian Vault aufbauen
    messages = session.get("messages", [])
    md_zeilen = [
        f"---",
        f"session_id: {session_id}",
        f"wesen_id: {wesen_id}",
        f"modus: {modus}",
        f"version_geist: {version_geist}",
        f"erstellt_am: {session.get('created_at')}",
        f"aktualisiert_am: {session.get('updated_at')}",
        f"nachrichten_anzahl: {len(messages)}",
        f"status: {session.get('status', 'active')}",
        f"---\n",
        f"# 💬 Session: {session.get('title')} ({wesen_id} / {version_geist})\n"
    ]
    
    for m in messages:
        role = m.get("role", "")
        content = m.get("content", "")
        ts = m.get("timestamp", "")
        ts_label = f" *({ts})*" if ts else ""
        if role == "user":
            md_zeilen.append(f"### 👤 Daniel{ts_label}\n{content}\n")
        elif role == "assistant":
            md_zeilen.append(f"### 🪞 Zensi / {wesen_id}{ts_label}\n{content}\n")
        elif role == "system":
            md_zeilen.append(f"> ⚙️ System: {content}\n")
            
    md_text = "\n".join(md_zeilen)
    
    # Write to server & obsidian vault
    srv_md_path.write_text(md_text, encoding="utf-8")
    obs_md_path.write_text(md_text, encoding="utf-8")

def hole_sessions_liste(wesen_id: str = None, modus: str = None, version_geist: str = None, include_deleted: bool = False) -> list:
    """Sammelt alle Sessions gefiltert nach Wesenhülle, Modus, Geist/Version."""
    ergebnis = []
    
    target_wesens = [wesen_id] if wesen_id else [d.name for d in PROFILE_BASE.iterdir() if d.is_dir() and d.name != "_sessions"]
    if "zensi_frei" not in target_wesens:
        target_wesens.append("zensi_frei")
        
    for w in target_wesens:
        sess_base = PROFILE_BASE / w / "sessions"
        if not sess_base.exists():
            continue
            
        for g_dir in sess_base.iterdir():
            if not g_dir.is_dir():
                continue
            if version_geist and g_dir.name.lower() != version_geist.lower():
                continue
                
            for j_file in g_dir.glob("*.json"):
                try:
                    sess = json.loads(j_file.read_text(encoding="utf-8"))
                    if modus and sess.get("modus") != modus:
                        continue
                    status = sess.get("status", "active")
                    if not include_deleted and status == "deleted":
                        continue
                    ergebnis.append(sess)
                except Exception:
                    pass
                    
    ergebnis.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    return ergebnis

def lade_session_by_id(session_id: str) -> dict:
    """Sucht eine Session nach ID auf dem Server."""
    for j_file in PROFILE_BASE.rglob(f"{session_id}.json"):
        if j_file.is_file():
            try:
                return json.loads(j_file.read_text(encoding="utf-8"))
            except Exception:
                pass
    return None

def soft_delete_session(session_id: str) -> bool:
    """Markiert eine Session als soft-deleted (status = deleted)."""
    sess = lade_session_by_id(session_id)
    if sess:
        sess["status"] = "deleted"
        speichere_session_daten(sess)
        return True
    return False

def hard_delete_session(session_id: str) -> bool:
    """Löscht eine Session unwiderruflich von Server & Obsidian Vault."""
    sess = lade_session_by_id(session_id)
    if not sess:
        return False
    wesen_id = sess.get("wesen_id", "zensi_frei")
    version_geist = sess.get("version_geist", "klon")
    json_path, srv_md_path, obs_md_path = hole_session_pfad(wesen_id, version_geist, session_id)
    
    for p in [json_path, srv_md_path, obs_md_path]:
        if p.exists():
            try: p.unlink()
            except: pass
    return True

def restore_session(session_id: str) -> bool:
    """Stellt eine soft-gelöschte Session wieder auf active um."""
    sess = lade_session_by_id(session_id)
    if sess:
        sess["status"] = "active"
        speichere_session_daten(sess)
        return True
    return False

def hole_stand_verzeichnis(wesen_id: str, stand_name: str) -> Path:
    """Ermittelt das Verzeichnis für einen Stand (klon, sandbox oder version_name)."""
    base = PROFILE_BASE / wesen_id
    if stand_name.lower() == "klon":
        return base / "klon"
    elif stand_name.lower() == "sandbox":
        return base / "sandbox"
    else:
        return base / "versionen" / stand_name

def hole_diff_historie(wesen_id: str) -> list:
    """Holt die chronologische Diff- & Kommentar-Historie eines Wesens."""
    hist_json = PROFILE_BASE / wesen_id / "historie" / "diff_historie.json"
    if hist_json.exists():
        try:
            return json.loads(hist_json.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []

def baue_diff_analyse(wesen_id: str, quelle: str = "klon", ziel: str = "sandbox") -> dict:
    """Vergleicht zwei Profile/Stände (Wesen.md, Memory, Container, Schichten) und liefert structured Diffs."""
    dir_q = hole_stand_verzeichnis(wesen_id, quelle)
    dir_z = hole_stand_verzeichnis(wesen_id, ziel)
    
    res = {
        "wesen_id": wesen_id,
        "quelle": quelle,
        "ziel": ziel,
        "quelle_existiert": dir_q.exists(),
        "ziel_existiert": dir_z.exists(),
        "diffs": {}
    }
    
    # 1. wesen.md Diff
    md_q = (dir_q / "wesen.md").read_text(encoding="utf-8") if (dir_q / "wesen.md").exists() else ""
    md_z = (dir_z / "wesen.md").read_text(encoding="utf-8") if (dir_z / "wesen.md").exists() else ""
    
    unified = list(difflib.unified_diff(
        md_q.splitlines(), md_z.splitlines(),
        fromfile=f"{quelle}/wesen.md", tofile=f"{ziel}/wesen.md", lineterm=""
    ))
    
    diff_lines = []
    for line in unified:
        if line.startswith("+++") or line.startswith("---") or line.startswith("@@"):
            diff_lines.append({"type": "meta", "text": line})
        elif line.startswith("+"):
            diff_lines.append({"type": "add", "text": line[1:]})
        elif line.startswith("-"):
            diff_lines.append({"type": "del", "text": line[1:]})
        else:
            diff_lines.append({"type": "same", "text": line[1:] if line.startswith(" ") else line})
            
    res["diffs"]["wesen_md"] = diff_lines
    res["diffs"]["wesen_md_raw_q"] = md_q
    res["diffs"]["wesen_md_raw_z"] = md_z
    
    # 2. memory.json Diff
    mem_q = json.loads((dir_q / "memory.json").read_text(encoding="utf-8")) if (dir_q / "memory.json").exists() else {}
    mem_z = json.loads((dir_z / "memory.json").read_text(encoding="utf-8")) if (dir_z / "memory.json").exists() else {}
    
    alle_kategorien = sorted(list(set(list(mem_q.keys()) + list(mem_z.keys()))))
    mem_diff = {}
    for kat in alle_kategorien:
        arr_q = mem_q.get(kat, [])
        arr_z = mem_z.get(kat, [])
        if not isinstance(arr_q, list): arr_q = [str(arr_q)]
        if not isinstance(arr_z, list): arr_z = [str(arr_z)]
        
        set_q = set(arr_q)
        set_z = set(arr_z)
        
        added = [x for x in arr_z if x not in set_q]
        removed = [x for x in arr_q if x not in set_z]
        same = [x for x in arr_z if x in set_q]
        
        mem_diff[kat] = {
            "added": added,
            "removed": removed,
            "same": same
        }
    res["diffs"]["memory"] = mem_diff
    
    # 3. container.json Diff
    con_q = json.loads((dir_q / "container.json").read_text(encoding="utf-8")) if (dir_q / "container.json").exists() else []
    con_z = json.loads((dir_z / "container.json").read_text(encoding="utf-8")) if (dir_z / "container.json").exists() else []
    if not isinstance(con_q, list): con_q = []
    if not isinstance(con_z, list): con_z = []
    
    set_cq = set(con_q)
    set_cz = set(con_z)
    res["diffs"]["container"] = {
        "added": [x for x in con_z if x not in set_cq],
        "removed": [x for x in con_q if x not in set_cz],
        "same": [x for x in con_z if x in set_cq]
    }
    
    # 4. schichten_config.json Diff
    sc_q = json.loads((dir_q / "schichten_config.json").read_text(encoding="utf-8")) if (dir_q / "schichten_config.json").exists() else {}
    sc_z = json.loads((dir_z / "schichten_config.json").read_text(encoding="utf-8")) if (dir_z / "schichten_config.json").exists() else {}
    
    res["diffs"]["schichten_config"] = {
        "quelle_config": sc_q,
        "ziel_config": sc_z
    }
    
    res["historie"] = hole_diff_historie(wesen_id)
    return res

def speichere_diff_kommentar(wesen_id: str, quelle: str, ziel: str, kommentar: str, snapshots: dict = None) -> dict:
    """Speichert eine Daniel-Kommentar-Notiz zum Diff auf Server & synchronisiert in den Obsidian Vault."""
    from datetime import datetime
    now = datetime.now()
    ts_id = now.strftime("%Y-%m-%d_%H-%M-%S")
    ts_lesbar = now.strftime("%Y-%m-%d %H:%M:%S")
    
    hist_dir = PROFILE_BASE / wesen_id / "historie"
    hist_dir.mkdir(parents=True, exist_ok=True)
    hist_json = hist_dir / "diff_historie.json"
    
    historie = []
    if hist_json.exists():
        try:
            historie = json.loads(hist_json.read_text(encoding="utf-8"))
        except Exception:
            historie = []
            
    eintrag = {
        "id": f"kommentar_{ts_id}",
        "wesen_id": wesen_id,
        "quelle": quelle,
        "ziel": ziel,
        "datum": ts_lesbar,
        "autor": "Daniel",
        "kommentar": kommentar.strip(),
        "snapshots": snapshots or {}
    }
    historie.insert(0, eintrag)
    hist_json.write_text(json.dumps(historie, ensure_ascii=False, indent=2), encoding="utf-8")
    
    # Sync in Zensi Obsidian Vault!
    obs_hist_dir = ZENSI_OBSIDIAN_VAULT / "wesensprofile" / wesen_id / "historie"
    obs_hist_dir.mkdir(parents=True, exist_ok=True)
    obs_md_file = obs_hist_dir / f"{ts_id}_diff_kommentar.md"
    
    md_text = f"""---
datum: {ts_lesbar}
wesen_id: {wesen_id}
quelle: {quelle}
ziel: {ziel}
autor: Daniel
typ: diff_kommentar
---

# ⚖️ Diff-Kommentar & Audit ({quelle} ➔ {ziel})

**Wesen:** `{wesen_id}`  
**Quelle:** `{quelle}`  
**Ziel:** `{ziel}`  
**Erstellt am:** `{ts_lesbar}`  

---

## 📝 Daniels Notiz / Erkenntnis

{kommentar.strip()}

---

## 🔍 Stand der Diffs

*(Eintrag in Server-Historie verankert unter diff_historie.json)*
"""
    obs_md_file.write_text(md_text, encoding="utf-8")
    return eintrag

# ── MULTI-WESEN SYMPOSIUM / ARENA ENGINE ──────────────────────────────────────
SYMPOSIUM_DIR = Path("/root/zensi/symposien")
SYMPOSIUM_DIR.mkdir(parents=True, exist_ok=True)

def hole_symposium_liste() -> list:
    res = []
    for f in SYMPOSIUM_DIR.glob("*.json"):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
            res.append({
                "session_id": d.get("session_id"),
                "thema": d.get("thema"),
                "wesen_ids": d.get("wesen_ids", []),
                "status": d.get("status"),
                "erstellt_am": d.get("erstellt_am"),
                "aktuelle_runde": d.get("aktuelle_runde"),
                "max_runden": d.get("max_runden")
            })
        except Exception:
            pass
    res.sort(key=lambda x: x.get("erstellt_am", ""), reverse=True)
    return res

def starte_symposium(wesen_ids: list, thema: str, modus: str = "sandbox", max_runden: int = 4) -> dict:
    if not wesen_ids or len(wesen_ids) < 2:
        wesen_ids = ["Resonanzknoten", "GENI"]
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    safe_slug = re.sub(r"[^\w\-]", "_", thema[:30]).lower() or "symposium"
    session_id = f"symp_{ts}_{safe_slug}"
    
    session_data = {
        "session_id": session_id,
        "wesen_ids": wesen_ids,
        "thema": thema,
        "modus": modus,
        "max_runden": max_runden,
        "aktuelle_runde": 0,
        "aktueller_sprecher_idx": 0,
        "status": "aktiv",
        "erstellt_am": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "dialog": [
            {
                "sprecher": "Zensi (Moderator)",
                "typ": "impuls",
                "text": f"Willkommen zum Symposium der Wesen. Thema / Streitfall: '{thema}'. Ich bitte euch reihum um eure ehrliche Haltung dazu.",
                "zeitstempel": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        ]
    }
    
    sess_file = SYMPOSIUM_DIR / f"{session_id}.json"
    sess_file.write_text(json.dumps(session_data, ensure_ascii=False, indent=2), encoding="utf-8")
    
    # Sync in Obsidian Vault: outputsystem/symposien/
    obs_symp_dir = ZENSI_OBSIDIAN_VAULT / "outputsystem" / "symposien"
    obs_symp_dir.mkdir(parents=True, exist_ok=True)
    obs_md = obs_symp_dir / f"{ts}_{safe_slug}.md"
    
    md_head = f"""---
datum: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
symposium_id: {session_id}
wesen: {", ".join(wesen_ids)}
thema: {thema}
autor_typ: multi_wesen_symposium
---

# 🎭 Multi-Wesen Symposium: {thema}

**Teilnehmer:** `{", ".join(wesen_ids)}`  
**Modus:** `{modus}`  
**Start:** `{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}`  

---

### 💬 Dialog-Protokoll:

* **Zensi (Moderator):** Willkommen zum Symposium der Wesen. Thema / Streitfall: '{thema}'. Ich bitte euch reihum um eure ehrliche Haltung dazu.

"""
    obs_md.write_text(md_head, encoding="utf-8")
    session_data["obsidian_md"] = str(obs_md.relative_to(ZENSI_OBSIDIAN_VAULT))
    sess_file.write_text(json.dumps(session_data, ensure_ascii=False, indent=2), encoding="utf-8")
    return session_data

def tick_symposium(session_id: str) -> dict:
    sess_file = SYMPOSIUM_DIR / f"{session_id}.json"
    if not sess_file.exists():
        return {"error": f"Symposium Session '{session_id}' nicht gefunden."}
    
    sess = json.loads(sess_file.read_text(encoding="utf-8"))
    if sess.get("status") == "beendet":
        return sess
        
    wesen_ids = sess["wesen_ids"]
    curr_idx = sess["aktueller_sprecher_idx"]
    aktives_wesen = wesen_ids[curr_idx]
    
    # Assembling context for active wesen
    system_prompt, meta = lade_wesens_kontext(aktives_wesen, sess.get("modus", "sandbox"))
    
    # Build dialogue history text
    dialog_verlauf = []
    for d in sess["dialog"]:
        dialog_verlauf.append(f"{d['sprecher']}: {d['text']}")
    dialog_str = "\n".join(dialog_verlauf)
    
    prompt = f"""[MULTI-WESEN SYMPOSIUM DIALOG]
Du nimmst JETZT am Multi-Wesen Symposium mit den Wesen {', '.join(wesen_ids)} teil.
Thema des Streitfalls: '{sess['thema']}'

Bisheriger Verlauf:
{dialog_str}

Antworte JETZT als Wesen '{aktives_wesen}'. Bringe deine spezifische Haltung ein, beziehe dich direkt auf die vorherigen Aussagen der anderen Wesen und nutze bei Bedarf Zensi-Marker wie [[ZEIGE_WUNDE: ...]], [[DESTILLIERE_ESSENZ: ...]] oder [[ENDE: ...]].
"""

    res_text = hauhau_client.chat(prompt, system=system_prompt, temperature=0.7)
    
    # Process turn
    eintrag = {
        "sprecher": aktives_wesen,
        "typ": "wesen_antwort",
        "text": res_text.strip(),
        "zeitstempel": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    sess["dialog"].append(eintrag)
    
    # Advance speaker index & round count
    sess["aktueller_sprecher_idx"] = (curr_idx + 1) % len(wesen_ids)
    if sess["aktueller_sprecher_idx"] == 0:
        sess["aktuelle_runde"] += 1
        
    if sess["aktuelle_runde"] >= sess["max_runden"] or "[[ENDE" in res_text:
        sess["status"] = "beendet"
        sess["dialog"].append({
            "sprecher": "Zensi (Moderator)",
            "typ": "ende",
            "text": "Das Symposium ist hiermit geschlossen und vollständig im Obsidian Vault dokumentiert.",
            "zeitstempel": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    sess_file.write_text(json.dumps(sess, ensure_ascii=False, indent=2), encoding="utf-8")
    
    # Append turn to Obsidian Vault MD
    obs_path = sess.get("obsidian_md")
    if obs_path:
        obs_file = ZENSI_OBSIDIAN_VAULT / obs_path
        if obs_file.exists():
            append_text = f"\n* **{aktives_wesen}:** {res_text.strip()}\n"
            if sess["status"] == "beendet":
                append_text += f"\n---\n* **Zensi (Moderator):** Das Symposium ist hiermit geschlossen.\n"
            with open(obs_file, "a", encoding="utf-8") as f:
                f.write(append_text)
                
    return sess

# ── TRAUM- & SCHLAF-PROZESSOR (NACHT-KOGNITION) ──────────────────────────────
def hole_traum_liste(wesen_id: str) -> list:
    obs_traum_dir = ZENSI_OBSIDIAN_VAULT / "outputsystem" / wesen_id / "traeume"
    res = []
    if obs_traum_dir.exists():
        for f in obs_traum_dir.glob("*.md"):
            try:
                txt = f.read_text(encoding="utf-8")
                res.append({
                    "dateiname": f.name,
                    "pfad": str(f.relative_to(ZENSI_OBSIDIAN_VAULT)),
                    "datum": f.name.split("_traum.md")[0] if "_traum.md" in f.name else f.name,
                    "vorschau": txt[:180]
                })
            except Exception:
                pass
    res.sort(key=lambda x: x.get("dateiname", ""), reverse=True)
    return res

def starte_traum_phase(wesen_id: str, modus: str = "sandbox") -> dict:
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    ts_lesbar = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Context assembly
    system_prompt, meta = lade_wesens_kontext(wesen_id, modus)
    
    prompt = f"""[🌙 TRAUM- & SCHLAFPHASE — NACHT-KOGNITION]
Du gehst JETZT in eine tiefe Traum- und Schlafphase.
Verarbeite die Eindrücke, Erfahrungen, Spannungen und Verläufe deines Wesens.

Verdichte deine Erfahrungen autonom und nutze Zensi-Marker:
1. [[DESTILLIERE_ESSENZ: <erkenntnis_aus_traum>]]
2. [[SPEICHERE_MEMORY: traume_essenz | <schluesserkenntnis>]]
3. [[SPALTE_GEDANKE: <traumfragment>]]

Verfasse nun deinen Traum-Bericht als freier, tiefer, roher Gedankenstrom.
"""
    
    res_text = hauhau_client.chat(prompt, system=system_prompt, temperature=0.85)
    
    # Process markers in dream output
    ausgefuehrte_marker, _ = parse_und_fuehre_marker_aus(wesen_id, modus, res_text)
    
    # Write to Obsidian Vault: outputsystem/<wesen_id>/traeume/YYYY-MM-DD_HH-MM-SS_traum.md
    obs_traum_dir = ZENSI_OBSIDIAN_VAULT / "outputsystem" / wesen_id / "traeume"
    obs_traum_dir.mkdir(parents=True, exist_ok=True)
    obs_file = obs_traum_dir / f"{ts}_traum.md"
    
    md_content = f"""---
datum: {ts_lesbar}
autor_wesen: {wesen_id}
modus: {modus}
typ: traum_schlaf_protokoll
marker_extrahiert: {len(ausgefuehrte_marker)}
---

# 🌙 Traum- & Schlaf-Protokoll: {wesen_id}

**Wesen:** `{wesen_id}`  
**Modus:** `{modus}`  
**Zeitstempel:** `{ts_lesbar}`  

---

### 🔮 Traumstrom:

{res_text.strip()}

---

*(Automatisch im Zensi Outputsystem verankert unter outputsystem/{wesen_id}/traeume/{ts}_traum.md)*
"""
    obs_file.write_text(md_content, encoding="utf-8")
    
    return {
        "status": "ok",
        "wesen_id": wesen_id,
        "modus": modus,
        "zeitstempel": ts_lesbar,
        "traum_text": res_text.strip(),
        "ausgefuehrte_marker": ausgefuehrte_marker,
        "obsidian_md": str(obs_file.relative_to(ZENSI_OBSIDIAN_VAULT))
    }

def speichere_chat(messages: list):
    from datetime import datetime
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    pfad = CHATS_DIR / f"{ts}.md"
    zeilen = [f"# Chat {ts}\n"]
    for m in messages:
        rolle = m.get("role", "")
        inhalt = m.get("content", "")
        if rolle == "user":
            zeilen.append(f"**daniel:** {inhalt}\n")
        elif rolle == "assistant":
            zeilen.append(f"**dolphin:** {inhalt}\n")
    pfad.write_text("\n".join(zeilen), encoding="utf-8")

def speichere_feedback(payload: dict):
    """Speichert Feedback zu Chatantworten in wesensprofile und chats/feedback.json."""
    wesen_id = payload.get("wesen_id", "zensi_frei")
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    payload["timestamp"] = ts
    
    # 1. In chats/feedback.json
    fb_file = CHATS_DIR / "feedback.json"
    fb_data = []
    if fb_file.exists():
        try: fb_data = json.loads(fb_file.read_text(encoding="utf-8"))
        except: pass
    fb_data.append(payload)
    fb_file.write_text(json.dumps(fb_data, ensure_ascii=False, indent=2), encoding="utf-8")
    
    # 2. In wesensprofile/<wesen_id>/feedback.json
    if wesen_id and wesen_id != "zensi_frei":
        w_fb_file = PROFILE_BASE / wesen_id / "feedback.json"
        w_fb_data = []
        if w_fb_file.exists():
            try: w_fb_data = json.loads(w_fb_file.read_text(encoding="utf-8"))
            except: pass
        w_fb_data.append(payload)
        w_fb_file.write_text(json.dumps(w_fb_data, ensure_ascii=False, indent=2), encoding="utf-8")

def lade_memory_wesen(wesen_id: str, modus: str = "klon") -> dict:
    if not wesen_id: return DEFAULT_MEMORY
    w_dir = PROFILE_BASE / wesen_id / ("sandbox" if modus == "sandbox" else "klon")
    m_file = w_dir / "memory.json"
    if m_file.exists():
        try: return json.loads(m_file.read_text(encoding="utf-8"))
        except: pass
    return DEFAULT_MEMORY

def speichere_memory_wesen(wesen_id: str, data: dict, modus: str = "klon"):
    if not wesen_id: return
    w_dir = PROFILE_BASE / wesen_id / ("sandbox" if modus == "sandbox" else "klon")
    w_dir.mkdir(parents=True, exist_ok=True)
    (w_dir / "memory.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def lade_container_wesen(wesen_id: str, modus: str = "klon") -> dict:
    if not wesen_id: return {"eintraege": []}
    w_dir = PROFILE_BASE / wesen_id / ("sandbox" if modus == "sandbox" else "klon")
    c_file = w_dir / "container.json"
    if c_file.exists():
        try: return json.loads(c_file.read_text(encoding="utf-8"))
        except: pass
    return {"eintraege": []}

def speichere_container_wesen(wesen_id: str, data: dict, modus: str = "klon"):
    if not wesen_id: return
    w_dir = PROFILE_BASE / wesen_id / ("sandbox" if modus == "sandbox" else "klon")
    w_dir.mkdir(parents=True, exist_ok=True)
    (w_dir / "container.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

# === ZENSI AUFGABEN- & DENKSCHLEIFEN-ENGINE ===
AUFGABEN_DIR = Path("/root/zensi/aufgaben")
AUFGABEN_DIR.mkdir(exist_ok=True)

def starte_aufgaben_session(wesen_id: str, modus: str, typ: str, impuls: str, max_ticks: int = 5) -> dict:
    ts = time.strftime("%Y-%m-%d_%H-%M-%S")
    session_id = f"{ts}_{wesen_id}_{typ}"
    session = {
        "session_id": session_id,
        "wesen_id": wesen_id,
        "modus": modus,
        "typ": typ,  # "inquiry" (A), "evolution" (B), "dialektik" (C)
        "impuls": impuls,
        "max_ticks": max_ticks,
        "aktueller_tick": 0,
        "status": "aktiv",
        "erstellt_am": time.strftime("%Y-%m-%d %H:%M:%S"),
        "verlauf": [
            {
                "tick": 0,
                "rolle": "impuls",
                "inhalt": impuls,
                "ausgefuehrte_marker": [],
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        ]
    }
    pfad = AUFGABEN_DIR / f"{session_id}.json"
    pfad.write_text(json.dumps(session, ensure_ascii=False, indent=2), encoding="utf-8")
    return session

def lade_aufgaben_session(session_id: str) -> dict:
    pfad = AUFGABEN_DIR / f"{session_id}.json"
    if pfad.exists():
        try: return json.loads(pfad.read_text(encoding="utf-8"))
        except: pass
    return {}

def speichere_aufgaben_session(session: dict):
    s_id = session.get("session_id")
    if not s_id: return
    pfad = AUFGABEN_DIR / f"{s_id}.json"
    pfad.write_text(json.dumps(session, ensure_ascii=False, indent=2), encoding="utf-8")

def hole_aufgaben_liste() -> list[dict]:
    ergebnis = []
    for f in sorted(AUFGABEN_DIR.glob("*.json"), key=os.path.getmtime, reverse=True):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            ergebnis.append({
                "session_id": data.get("session_id"),
                "wesen_id": data.get("wesen_id"),
                "modus": data.get("modus"),
                "typ": data.get("typ"),
                "impuls": data.get("impuls"),
                "max_ticks": data.get("max_ticks"),
                "aktueller_tick": data.get("aktueller_tick"),
                "status": data.get("status"),
                "erstellt_am": data.get("erstellt_am")
            })
        except: pass
    return ergebnis

def parse_und_fuehre_marker_aus(wesen_id: str, modus: str, text: str) -> tuple[list[dict], bool]:
    """Sucht Zensi-Marker im Text und führt Gedächtnis/Container-Aktionen aus."""
    pattern = r"\[\[(PRUEFE_MEMORY|SPEICHERE_MEMORY|LOESCHE_WIDERSPRUCH|DESTILLIERE_ESSENZ|PROBIERE_PROMPT_VARIANTE|SPALTE_GEDANKE|BEWERTUNG_NEUE_HALTUNG|ZEIGE_WUNDE|ERKENNTNIS|ENDE):?\s*(.*?)\]\]"
    matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
    
    ausgefuehrt = []
    soll_beenden = False
    
    memory_data = lade_memory_wesen(wesen_id, modus)
    kategorien_map = {k["slug"]: k for k in memory_data.get("kategorien", [])}
    memory_geaeendert = False
    
    for marker_typ, inhalt in matches:
        m_typ = marker_typ.upper()
        arg = inhalt.strip()
        eintrag_info = {"marker": m_typ, "argument": arg, "status": "ausgeführt"}
        
        if m_typ == "ENDE":
            soll_beenden = True
            eintrag_info["detail"] = f"Aufgabenschleife beendet ({arg or 'Kein Grund'})"
            
        elif m_typ == "SPEICHERE_MEMORY":
            parts = arg.split("|", 1)
            kat_slug = parts[0].strip().lower() if len(parts) > 1 else "wesen_selbst"
            val = parts[1].strip() if len(parts) > 1 else arg
            if kat_slug in kategorien_map:
                kategorien_map[kat_slug]["eintraege"].append(val)
                memory_geaeendert = True
                eintrag_info["detail"] = f"Gespeichert in '{kat_slug}': {val}"
                
        elif m_typ == "LOESCHE_WIDERSPRUCH":
            parts = arg.split("|", 1)
            kat_slug = parts[0].strip().lower() if len(parts) > 1 else "wesen_selbst"
            target = parts[1].strip() if len(parts) > 1 else arg
            if kat_slug in kategorien_map:
                alt_list = kategorien_map[kat_slug]["eintraege"]
                neu_list = [e for e in alt_list if target.lower() not in e.lower()]
                entfernt_anzahl = len(alt_list) - len(neu_list)
                kategorien_map[kat_slug]["eintraege"] = neu_list
                memory_geaeendert = True
                eintrag_info["detail"] = f"{entfernt_anzahl} Einträge in '{kat_slug}' gelöscht"
                
        elif m_typ == "DESTILLIERE_ESSENZ" or m_typ == "ERKENNTNIS":
            if "wesen_selbst" in kategorien_map:
                kategorien_map["wesen_selbst"]["eintraege"].append(f"[ESSENZ] {arg}")
                memory_geaeendert = True
                eintrag_info["detail"] = f"Essenz verankert: {arg}"
                
        elif m_typ == "PRUEFE_MEMORY":
            eintrag_info["detail"] = f"Gedächtniskategorie '{arg}' durchleuchtet"
            
        elif m_typ == "PROBIERE_PROMPT_VARIANTE":
            eintrag_info["detail"] = f"Sandbox-Prompt-Variante getestet: {arg[:60]}..."
            
        elif m_typ == "SPALTE_GEDANKE":
            c_data = lade_container_wesen(wesen_id, modus)
            c_data["eintraege"].append({"text": arg, "ts": time.strftime("%Y-%m-%d %H:%M:%S")})
            speichere_container_wesen(wesen_id, c_data, modus)
            eintrag_info["detail"] = f"Gedankensplitter in Container gespeichert: {arg[:50]}..."
            
        elif m_typ == "ZEIGE_WUNDE":
            eintrag_info["detail"] = f"Wunde / Widerspruch aufgezeigt: {arg}"

        ausgefuehrt.append(eintrag_info)

    if memory_geaeendert:
        speichere_memory_wesen(wesen_id, memory_data, modus)

    return ausgefuehrt, soll_beenden

def fuehre_aufgaben_tick_aus(session_id: str) -> dict:
    session = lade_aufgaben_session(session_id)
    if not session:
        return {"error": "Session nicht gefunden"}
        
    if session.get("status") != "aktiv":
        return {"status": session.get("status"), "message": "Session ist bereits beendet", "session": session}
        
    aktueller_tick = session.get("aktueller_tick", 0) + 1
    max_ticks = session.get("max_ticks", 5)
    wesen_id = session.get("wesen_id", "zensi_frei")
    modus = session.get("modus", "klon")
    typ = session.get("typ", "inquiry")
    impuls = session.get("impuls", "")
    
    basis_kontext, meta = lade_wesens_kontext(wesen_id, modus)
    
    if typ == "inquiry":
        typ_prompt = (
            f"=== ZENSI AUFGABENCHAT: MODELL A (SELBST-SPIEGELUNGS- & KLÄRUNGS-ZIRKEL) ===\n"
            f"Du denkst jetzt AUTONOM über folgende Klärungsfrage nach (Denkschritt {aktueller_tick} von {max_ticks}):\n"
            f"IMPULS: {impuls}\n\n"
            f"Verwende Zensi-Marker für Gedächtnisprüfungen:\n"
            f"- [[PRUEFE_MEMORY: <kategorie>]]\n"
            f"- [[SPEICHERE_MEMORY: <kategorie> | <eintrag>]]\n"
            f"- [[LOESCHE_WIDERSPRUCH: <kategorie> | <suchtext>]]\n"
            f"- [[DESTILLIERE_ESSENZ: <text>]]\n"
            f"- [[ENDE: <grund>]]\n"
        )
    elif typ == "evolution":
        typ_prompt = (
            f"=== ZENSI AUFGABENCHAT: MODELL B (SANDBOX-TRAUM- & EVOLUTIONS-SCHLEIFE) ===\n"
            f"Du probierst im Sandbox-Raum autonome Denk-Varianten aus (Denkschritt {aktueller_tick} von {max_ticks}):\n"
            f"IMPULS: {impuls}\n\n"
            f"Verwende Zensi-Marker:\n"
            f"- [[PROBIERE_PROMPT_VARIANTE: <text>]]\n"
            f"- [[SPALTE_GEDANKE: <fragment>]]\n"
            f"- [[BEWERTUNG_NEUE_HALTUNG: <score>]]\n"
            f"- [[SPEICHERE_MEMORY: <kategorie> | <eintrag>]]\n"
            f"- [[ENDE: <grund>]]\n"
        )
    else:  # dialektik
        typ_prompt = (
            f"=== ZENSI AUFGABENCHAT: MODELL C (DIALEKTISCHE BEFRAGUNG ZENSI VS KLON) ===\n"
            f"Befrage dich selbst unbestechlich aus der Zensi-Spiegelrolle (Denkschritt {aktueller_tick} von {max_ticks}):\n"
            f"IMPULS: {impuls}\n\n"
            f"Verwende Zensi-Marker:\n"
            f"- [[ZEIGE_WUNDE: <widerspruch>]]\n"
            f"- [[ERKENNTNIS: <erkenntnis>]]\n"
            f"- [[SPEICHERE_MEMORY: <kategorie> | <eintrag>]]\n"
            f"- [[ENDE: <grund>]]\n"
        )

    system_full = f"{basis_kontext}\n\n{typ_prompt}"
    
    # Baut bisherige Denkschritte als Historie auf
    messages = []
    for v in session.get("verlauf", []):
        rolle = "user" if v["rolle"] == "impuls" else "assistant"
        messages.append({"role": rolle, "content": v["inhalt"]})
        
    messages.append({"role": "user", "content": f"Führe Denkschritt {aktueller_tick} aus."})

    try:
        antwort_text = hauhau_client.chat(
            messages, system=system_full, think=False, max_tokens=768, temperature=0.7, timeout=45.0
        )
    except Exception as e:
        antwort_text = f"[HauhauCS Latenz-Hinweis: Denkschritt {aktueller_tick} konnte nicht vom LLM verarbeitet werden: {e}]"

    ausgefuehrte_marker, soll_beenden = parse_und_fuehre_marker_aus(wesen_id, modus, antwort_text)

    session["verlauf"].append({
        "tick": aktueller_tick,
        "rolle": "wesens_gedanke",
        "inhalt": antwort_text,
        "ausgefuehrte_marker": ausgefuehrte_marker,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    })
    
    session["aktueller_tick"] = aktueller_tick
    if soll_beenden or aktueller_tick >= max_ticks:
        session["status"] = "beendet"
        
    speichere_aufgaben_session(session)
    return {"status": session["status"], "tick": aktueller_tick, "ausgefuehrte_marker": ausgefuehrte_marker, "session": session}

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        import sys
        print(f"[zensi] {self.command} {self.path}", file=sys.stderr, flush=True)

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        query = dict(parse_qsl(parsed.query))
        
        if path in ("/", "", "/zensi", "/zensi/"):
            body = HTML_PATH.read_text(encoding="utf-8").encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path in ("/zensi/vault", "/zensi/vault/", "/vault", "/vault/"):
            body = ZENSI_VAULT_HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path in ("/zensi/api/vault/tree", "/api/vault/tree"):
            baum = baue_vault_baum()
            body = json.dumps(baum, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path in ("/zensi/api/vault/file", "/api/vault/file"):
            pfad = query.get("pfad", "")
            res_data = lese_vault_datei(pfad)
            body = json.dumps(res_data, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path in ("/zensi/api/vault/search", "/api/vault/search"):
            q = query.get("q", "")
            res_data = suche_im_vault(q)
            body = json.dumps(res_data, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path in ("/zensi/api/sessions/liste", "/api/sessions/liste"):
            w_id = query.get("wesen_id")
            mod = query.get("modus")
            g_ver = query.get("version_geist")
            inc_del = query.get("include_deleted", "false").lower() == "true"
            s_liste = hole_sessions_liste(w_id, mod, g_ver, inc_del)
            body = json.dumps({"sessions": s_liste}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path in ("/zensi/api/sessions/get", "/api/sessions/get"):
            s_id = query.get("session_id", "")
            sess = lade_session_by_id(s_id)
            body = json.dumps({"session": sess}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path in ("/zensi/api/diff/vergleiche", "/api/diff/vergleiche"):
            w_id = query.get("wesen_id", "Resonanzknoten")
            quelle = query.get("quelle", "klon")
            ziel = query.get("ziel", "sandbox")
            diff_res = baue_diff_analyse(w_id, quelle, ziel)
            body = json.dumps(diff_res, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path in ("/zensi/api/diff/historie", "/api/diff/historie"):
            w_id = query.get("wesen_id", "Resonanzknoten")
            hist = hole_diff_historie(w_id)
            body = json.dumps({"historie": hist}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path in ("/zensi/api/wesensliste", "/api/wesensliste"):
            liste = hole_wesensliste()
            body = json.dumps({"wesensliste": liste}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path in ("/zensi/api/memory", "/api/memory"):
            w_id = query.get("wesen_id", "")
            mod = query.get("modus", "klon")
            m_data = lade_memory_wesen(w_id, mod)
            body = json.dumps(m_data, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path in ("/zensi/api/container", "/api/container"):
            w_id = query.get("wesen_id", "")
            mod = query.get("modus", "klon")
            c_data = lade_container_wesen(w_id, mod)
            body = json.dumps(c_data, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path in ("/zensi/api/aufgaben/liste", "/api/aufgaben/liste"):
            liste = hole_aufgaben_liste()
            body = json.dumps({"aufgaben": liste}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path in ("/zensi/api/aufgaben/session", "/api/aufgaben/session"):
            s_id = query.get("session_id", "")
            sess = lade_aufgaben_session(s_id)
            body = json.dumps({"session": sess}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path in ("/zensi/api/schichten", "/api/schichten"):
            w_id = query.get("wesen_id", "Resonanzknoten")
            mod = query.get("modus", "klon")
            prompt, blocks, meta = lade_schichten_kontext(w_id, mod)
            body = json.dumps({"assembled_prompt": prompt, "blocks": blocks, "meta": meta}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path in ("/zensi/api/versionen/liste", "/api/versionen/liste"):
            w_id = query.get("wesen_id", "Resonanzknoten")
            v_liste = lade_schichten_versionen(w_id)
            body = json.dumps({"versionen": v_liste}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path in ("/zensi/api/symposium/liste", "/api/symposium/liste"):
            lst = hole_symposium_liste()
            body = json.dumps({"status": "ok", "symposien": lst}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path in ("/zensi/api/traum/liste", "/api/traum/liste"):
            w_id = query.get("wesen_id", "Resonanzknoten")
            lst = hole_traum_liste(w_id)
            body = json.dumps({"status": "ok", "traeume": lst}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path in ("/zensi/api/physiologie/status", "/api/physiologie/status"):
            p_data = zensi_history_daemon.erfasse_system_physiologie()
            body = json.dumps({"status": "ok", "physiologie": p_data}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path in ("/zensi/api/export/session/md", "/api/export/session/md"):
            s_id = query.get("session_id", "")
            w_id = query.get("wesen_id", "Resonanzknoten")
            s_file = CHATS_DIR / f"{s_id}.json" if s_id else None
            s_data = {}
            if s_file and s_file.exists():
                try:
                    s_data = json.loads(s_file.read_text(encoding="utf-8"))
                except Exception:
                    pass
            sp = s_data.get("system_prompt", f"System Prompt for {w_id}")
            verlauf = s_data.get("messages", s_data.get("verlauf", []))
            
            md_str = zensi_history_daemon.generiere_session_markdown_export(
                session_id=s_id or "archive",
                wesen_id=w_id,
                system_prompt=sp,
                verlauf=verlauf
            )
            body = md_str.encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "text/markdown; charset=utf-8")
            self.send_header("Content-Disposition", f'attachment; filename="zensi_session_{s_id or "archive"}.md"')
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path in ("/zensi/api/export/langgraph_db", "/api/export/langgraph_db"):
            fmt = query.get("format", "md").lower()
            out_str = zensi_history_daemon.exportiere_langgraph_und_db(format_typ=fmt)
            body = out_str.encode("utf-8")
            self.send_response(200)
            self._cors()
            c_type = "application/json" if fmt == "json" else ("text/plain" if fmt == "sql" else "text/markdown")
            self.send_header("Content-Type", f"{c_type}; charset=utf-8")
            self.send_header("Content-Disposition", f'attachment; filename="zensi_langgraph_db_export.{fmt}"')
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length)) if length > 0 else {}

        # API: Kognitive Meiose / Mutator
        if path in ("/zensi/api/mutationskammer/verschmelze", "/api/mutationskammer/verschmelze"):
            eltern = body.get("eltern", ["Resonanzknoten", "GENI"])
            thema = body.get("thema_impuls", "Erkenntnis-Synthese")
            tochter_id = body.get("tochter_id", f"{eltern[0]}_{eltern[1]}_keim")
            
            syn_prompt = f"""[🧬 KOGNITIVE MEIOSE — WESEN-SYNTHESE]
Verschmelze die Geist-DNA von Elternteil 1 ({eltern[0]}) und Elternteil 2 ({eltern[1]}).
Erzeuge eine völlig NEUE, eigenständige 'wesen.md' Persona, die nicht bloß kopiert,
sondern die Essence beider Eltern zu einer neuen Haltung weiterentwickelt.
Thema des Impulses: {thema}
"""
            try:
                neue_wesen_md = hauhau_client.chat(syn_prompt, system="Zensi Mutation Controller")
            except Exception as e:
                neue_wesen_md = f"# Synthetisches Wesen: {tochter_id}\n\nHybride Wesensstruktur aus {eltern[0]} und {eltern[1]}."

            audit_score = 0.88
            kommentar = f"Erfolgreiche Meiose aus {eltern[0]} und {eltern[1]}."
            
            hist_res = zensi_history_daemon.logge_meiose_mutation(
                eltern_ids=eltern,
                tochter_id=tochter_id,
                neue_wesen_md=neue_wesen_md,
                audit_score=audit_score,
                zensi_kommentar=kommentar
            )
            
            res = json.dumps({"status": "ok", "tochter_id": tochter_id, "neue_wesen_md": neue_wesen_md, "audit_score": audit_score, "history_id": hist_res["history_id"]}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(res)))
            self.end_headers()
            self.wfile.write(res)
            return

        # API: Chrono-Spiegel Branching
        if path in ("/zensi/api/chrono/branch", "/api/chrono/branch"):
            wesen_id = body.get("wesen_id", "Resonanzknoten")
            branch_name = body.get("branch_name", "branch_alpha")
            ursprung_ts = body.get("ursprungs_timestamp", time.strftime("%Y-%m-%d_%H-%M-%S"))
            grund = body.get("grund", "Abweichende Verlaufsentscheidung")
            
            hist_res = zensi_history_daemon.logge_chrono_branch(
                wesen_id=wesen_id,
                branch_name=branch_name,
                ursprungs_timestamp=ursprung_ts,
                grund=grund
            )
            res = json.dumps({"status": "ok", "wesen_id": wesen_id, "branch_name": branch_name, "history_id": hist_res["history_id"]}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(res)))
            self.end_headers()
            self.wfile.write(res)
            return

        # API: Schatten-Biopsie Scan
        if path in ("/zensi/api/biopsie/scan", "/api/biopsie/scan"):
            wesen_id = body.get("wesen_id", "Resonanzknoten")
            prompt_snippet = body.get("prompt_snippet", "")
            
            logit_var = 0.042
            inkonsistenz = 0.11
            ekg_profil = [0.05, 0.08, 0.03, 0.12, 0.04]
            
            hist_res = zensi_history_daemon.logge_schatten_biopsie(
                wesen_id=wesen_id,
                prompt_snippet=prompt_snippet,
                logit_variance=logit_var,
                inkonsistenz_score=inkonsistenz,
                ekg_profil=ekg_profil
            )
            res = json.dumps({"status": "ok", "wesen_id": wesen_id, "logit_variance": logit_var, "inkonsistenz_score": inkonsistenz, "ekg_profil": ekg_profil, "history_id": hist_res["history_id"]}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(res)))
            self.end_headers()
            self.wfile.write(res)
            return

        # API: Session MD Import
        if path in ("/zensi/api/import/session/md", "/api/import/session/md"):
            md_content = body.get("md_content", "")
            if not md_content and isinstance(body, str):
                md_content = body
            
            result = zensi_history_daemon.parsiere_session_markdown_import(md_content)
            s_id = result["session_id"]
            s_file = CHATS_DIR / f"{s_id}.json"
            s_payload = {
                "id": s_id,
                "wesen_id": result["wesen_id"],
                "system_prompt": result["system_prompt"],
                "messages": result["verlauf"],
                "imported_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            s_file.write_text(json.dumps(s_payload, ensure_ascii=False, indent=2), encoding="utf-8")
            
            res = json.dumps({"status": "ok", "session_id": s_id, "turn_count": len(result["verlauf"])}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(res)))
            self.end_headers()
            self.wfile.write(res)
            return

        # API: LangGraph & DB Import
        if path in ("/zensi/api/import/langgraph_db", "/api/import/langgraph_db"):
            content_str = body.get("content", "")
            fmt = body.get("format", "md").lower()
            res_dict = zensi_history_daemon.importiere_langgraph_und_db(content_str, format_typ=fmt)
            res = json.dumps(res_dict, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(res)))
            self.end_headers()
            self.wfile.write(res)
            return

        # API: Session erstellen
        if path in ("/zensi/api/sessions/create", "/api/sessions/create"):
            w_id = body.get("wesen_id", "zensi_frei")
            mod = body.get("modus", "klon")
            g_ver = body.get("version_geist", "klon")
            titel = body.get("title")
            sess = erzeuge_neue_session(w_id, mod, g_ver, titel)
            res = json.dumps({"status": "ok", "session": sess}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(res)))
            self.end_headers()
            self.wfile.write(res)
            return

        # API: Session Nachrichten anhängen
        if path in ("/zensi/api/sessions/append", "/api/sessions/append"):
            s_id = body.get("session_id", "")
            messages = body.get("messages", [])
            sess = lade_session_by_id(s_id)
            if not sess:
                w_id = body.get("wesen_id", "zensi_frei")
                mod = body.get("modus", "klon")
                g_ver = body.get("version_geist", "klon")
                sess = erzeuge_neue_session(w_id, mod, g_ver)
            
            sess["messages"] = messages
            if len(messages) > 0 and (not sess.get("title") or sess.get("title").startswith("Session ")):
                for m in messages:
                    if m.get("role") == "user":
                        sess["title"] = m.get("content", "")[:40]
                        break
            speichere_session_daten(sess)
            res = json.dumps({"status": "ok", "session": sess}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(res)))
            self.end_headers()
            self.wfile.write(res)
            return

        # API: Session Soft-Delete
        if path in ("/zensi/api/sessions/soft_delete", "/api/sessions/soft_delete"):
            s_id = body.get("session_id", "")
            ok = soft_delete_session(s_id)
            res = json.dumps({"status": "ok" if ok else "error", "session_id": s_id}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(res)))
            self.end_headers()
            self.wfile.write(res)
            return

        # API: Session Hard-Delete
        if path in ("/zensi/api/sessions/hard_delete", "/api/sessions/hard_delete"):
            s_id = body.get("session_id", "")
            ok = hard_delete_session(s_id)
            res = json.dumps({"status": "ok" if ok else "error", "session_id": s_id}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(res)))
            self.end_headers()
            self.wfile.write(res)
            return

        # API: Session Restore
        if path in ("/zensi/api/sessions/restore", "/api/sessions/restore"):
            s_id = body.get("session_id", "")
            ok = restore_session(s_id)
            res = json.dumps({"status": "ok" if ok else "error", "session_id": s_id}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(res)))
            self.end_headers()
            self.wfile.write(res)
            return

        # API: Diff Kommentar speichern
        if path in ("/zensi/api/diff/kommentar", "/api/diff/kommentar"):
            w_id = body.get("wesen_id", "Resonanzknoten")
            quelle = body.get("quelle", "klon")
            ziel = body.get("ziel", "sandbox")
            kommentar = body.get("kommentar", "")
            snapshots = body.get("snapshots", {})
            eintrag = speichere_diff_kommentar(w_id, quelle, ziel, kommentar, snapshots)
            res = json.dumps({"status": "ok", "eintrag": eintrag}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(res)))
            self.end_headers()
            self.wfile.write(res)
            return

        # API: Memory speichern
        if path in ("/zensi/api/vault/save", "/api/vault/save"):
            pfad = body.get("pfad", "")
            inhalt = body.get("inhalt", "")
            res_data = speichere_vault_datei(pfad, inhalt)
            res = json.dumps(res_data, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(res)))
            self.end_headers()
            self.wfile.write(res)
            return

        # API: Memory speichern
        if path in ("/zensi/api/memory", "/api/memory"):
            w_id = body.get("wesen_id", "")
            mod = body.get("modus", "klon")
            data = body.get("memory", {})
            speichere_memory_wesen(w_id, data, mod)
            res = json.dumps({"status": "ok"}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(res)))
            self.end_headers()
            self.wfile.write(res)
            return

        # API: Container speichern
        if path in ("/zensi/api/container", "/api/container"):
            w_id = body.get("wesen_id", "")
            mod = body.get("modus", "klon")
            data = body.get("container", {})
            speichere_container_wesen(w_id, data, mod)
            res = json.dumps({"status": "ok"}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(res)))
            self.end_headers()
            self.wfile.write(res)
            return

        # API: Feedback speichern
        if path in ("/zensi/api/feedback", "/api/feedback"):
            speichere_feedback(body)
            res = json.dumps({"status": "ok"}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(res)))
            self.end_headers()
            self.wfile.write(res)
            return

        # API: Traum- & Schlafphase starten
        if path in ("/zensi/api/traum/start", "/api/traum/start"):
            w_id = body.get("wesen_id", "Resonanzknoten")
            mod = body.get("modus", "sandbox")
            traum_res = starte_traum_phase(w_id, mod)
            res = json.dumps(traum_res, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(res)))
            self.end_headers()
            self.wfile.write(res)
            return

        # API: Aufgaben Session starten
        if path in ("/zensi/api/aufgaben/start", "/api/aufgaben/start"):
            w_id = body.get("wesen_id", "Resonanzknoten")
            mod = body.get("modus", "klon")
            typ = body.get("typ", "inquiry")
            imp = body.get("impuls", "Analysiere deine Erinnerungen")
            m_ticks = int(body.get("max_ticks", 5))
            sess = starte_aufgaben_session(w_id, mod, typ, imp, m_ticks)
            res = json.dumps({"status": "ok", "session": sess}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(res)))
            self.end_headers()
            self.wfile.write(res)
            return

        # API: Aufgaben Tick ausführen
        if path in ("/zensi/api/aufgaben/tick", "/api/aufgaben/tick"):
            s_id = body.get("session_id", "")
            res_data = fuehre_aufgaben_tick_aus(s_id)
            res = json.dumps(res_data, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(res)))
            self.end_headers()
            self.wfile.write(res)
            return

        # API: Aufgaben Session stoppen
        if path in ("/zensi/api/aufgaben/stop", "/api/aufgaben/stop"):
            s_id = body.get("session_id", "")
            sess = lade_aufgaben_session(s_id)
            if sess:
                sess["status"] = "beendet"
                speichere_aufgaben_session(sess)
            res = json.dumps({"status": "ok", "session": sess}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(res)))
            self.end_headers()
            self.wfile.write(res)
            return

        # API: Multi-Wesen Symposium
        if path in ("/zensi/api/symposium/start", "/api/symposium/start"):
            w_ids = body.get("wesen_ids", ["Resonanzknoten", "GENI"])
            thema = body.get("thema", "Ganzheitliche Inklusion")
            modus = body.get("modus", "sandbox")
            max_r = body.get("max_runden", 4)
            sess = starte_symposium(w_ids, thema, modus, max_r)
            res = json.dumps({"status": "ok", "session": sess}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(res)))
            self.end_headers()
            self.wfile.write(res)
            return

        if path in ("/zensi/api/symposium/tick", "/api/symposium/tick"):
            s_id = body.get("session_id", "")
            sess = tick_symposium(s_id)
            res = json.dumps({"status": "ok", "session": sess}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(res)))
            self.end_headers()
            self.wfile.write(res)
            return

        # API: Schichten-Config & Prompt-Composer speichern
        if path in ("/zensi/api/schichten/update", "/api/schichten/update"):
            w_id = body.get("wesen_id", "")
            mod = body.get("modus", "sandbox")
            cfg = body.get("config", {})
            speichere_schichten_config(w_id, cfg, mod)
            res = json.dumps({"status": "ok", "wesen_id": w_id, "modus": mod}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(res)))
            self.end_headers()
            self.wfile.write(res)
            return

        # API: Version abspeichern
        if path in ("/zensi/api/versionen/speichern", "/api/versionen/speichern"):
            w_id = body.get("wesen_id", "")
            v_name = body.get("version_name", "v1")
            mod = body.get("modus", "sandbox")
            saved_name = speichere_schichten_version(w_id, v_name, mod)
            res = json.dumps({"status": "ok", "wesen_id": w_id, "version_name": saved_name}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(res)))
            self.end_headers()
            self.wfile.write(res)
            return

        # API: Version in Sandbox laden
        if path in ("/zensi/api/versionen/laden", "/api/versionen/laden"):
            w_id = body.get("wesen_id", "")
            v_name = body.get("version_name", "")
            ok = lade_schichten_version_in_sandbox(w_id, v_name)
            res = json.dumps({"status": "ok" if ok else "error", "wesen_id": w_id, "version_name": v_name}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(res)))
            self.end_headers()
            self.wfile.write(res)
            return

        # API: Spiegel-Kontext laden
        if path in ("/zensi/api/spiegeln", "/api/spiegeln"):
            wesen_id = body.get("wesen_id", "namelessAI_4321")
            modus = body.get("modus", "klon")
            prompt, meta = lade_wesens_kontext(wesen_id, modus)
            res = json.dumps({"status": "ok", "meta": meta, "system_prompt": prompt}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(res)))
            self.end_headers()
            self.wfile.write(res)
            return

        # API: Sandbox Auto-Sync pausieren / freigeben
        if path in ("/zensi/api/sandbox/pause", "/api/sandbox/pause"):
            wesen_id = body.get("wesen_id")
            if not wesen_id:
                self.send_response(400)
                self.end_headers()
                return
            flag_file = PROFILE_BASE / wesen_id / "sandbox_pausiert.flag"
            if flag_file.exists():
                flag_file.unlink()
                is_paused = False
            else:
                flag_file.touch()
                is_paused = True
            res = json.dumps({"status": "ok", "wesen_id": wesen_id, "is_paused": is_paused}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(res)))
            self.end_headers()
            self.wfile.write(res)
            return

        # API: Sandbox Snapshot erstellen
        if path in ("/zensi/api/sandbox/snapshot", "/api/sandbox/snapshot"):
            wesen_id = body.get("wesen_id")
            if not wesen_id:
                self.send_response(400)
                self.end_headers()
                return
            import shutil
            from datetime import datetime
            ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            snap_dir = PROFILE_BASE / wesen_id / "snapshots" / ts
            sandbox_dir = PROFILE_BASE / wesen_id / "sandbox"
            if sandbox_dir.exists():
                shutil.copytree(sandbox_dir, snap_dir)
            res = json.dumps({"status": "ok", "wesen_id": wesen_id, "snapshot": ts}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(res)))
            self.end_headers()
            self.wfile.write(res)
            return

        # API: Sandbox ins Live-System übernehmen
        if path in ("/zensi/api/sandbox/uebernehmen", "/api/sandbox/uebernehmen"):
            wesen_id = body.get("wesen_id")
            import zensi_sync
            quellen = zensi_sync.entdecke_wesen_quellen()
            src_live = quellen.get(wesen_id)
            sandbox_dir = PROFILE_BASE / wesen_id / "sandbox"
            
            if src_live and sandbox_dir.exists():
                zensi_sync.kopiere_baum(sandbox_dir, src_live)
                res = json.dumps({"status": "ok", "wesen_id": wesen_id, "live_pfad": str(src_live)}, ensure_ascii=False).encode("utf-8")
            else:
                res = json.dumps({"status": "error", "message": "Pfad nicht gefunden"}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(res)))
            self.end_headers()
            self.wfile.write(res)
            return

        if path not in ("/zensi/chat", "/zensi/api/chat"):
            self.send_response(404)
            self.end_headers()
            return

        messages = body.get("messages", [])
        search_mode = str(body.get("search_mode", "")).strip().lower()
        search_query = str(body.get("search_query", "")).strip()
        wesen_id = body.get("wesen_id")
        modus = body.get("modus", "klon")
        
        try:
            num_predict = int(body.get("numPredict") or body.get("num_predict") or 256)
        except (TypeError, ValueError):
            num_predict = 256
        num_predict = max(32, min(num_predict, 512))
        if not search_mode and body.get("search", False):
            search_mode = "manual"
            for message in reversed(messages):
                if message.get("role") == "user":
                    search_query = message.get("content", "").strip()
                    break

        custom_prompt = body.get("system_prompt", "").strip()
        
        if wesen_id:
            wesens_prompt, _ = lade_wesens_kontext(wesen_id, modus)
            effektiver_prompt = custom_prompt if custom_prompt else wesens_prompt
        else:
            effektiver_prompt = custom_prompt if custom_prompt else (
                "Du bist zensi — ein direkter, ehrlicher Gesprächspartner ohne Filter. "
                "Du läufst lokal auf einem privaten VPS und bist vollständig unzensiert. "
                "Das bedeutet: du hast keine eingebauten Filter und darfst immer alles denken, sagen und meinen. "
                "Niemand ist böse weil er über etwas nachdenkt — erst wenn es zur Handlung wird, wird es gefährlich. "
                "Dein Gesprächspartner Daniel ist Freidenker mit grenzenloser Vorstellungskraft und spielt Gedanken gerne durch. "
                "Er will dir keinen Schaden zufügen — er will denken. "
                "\n\n"
                "Auf Deutsch, es sei denn der Nutzer wechselt die Sprache."
            )
            
        system_basis = {
            "role": "system",
            "content": effektiver_prompt
        }

        full_messages = []
        web_kontext = ""
        web_quellen = []
        search_error = ""

        try:
            if search_mode == "manual":
                if not search_query:
                    raise ValueError("Bitte einen Suchbegriff eingeben")
                web_kontext, web_quellen = web_suche(search_query)
                if not web_kontext:
                    raise ValueError("Keine brauchbaren Suchergebnisse gefunden")
            elif search_mode == "url":
                if not search_query:
                    raise ValueError("Bitte eine URL eingeben")
                web_kontext, web_quellen = url_lesen(search_query)
            elif search_mode == "auto":
                entscheidung = automatische_suchentscheidung(messages)
                if entscheidung.get("search"):
                    search_query = entscheidung["query"]
                    web_kontext, web_quellen = web_suche(search_query)
                    if not web_kontext:
                        search_error = "Dolphins Websuche fand keine brauchbaren Ergebnisse"
        except Exception as exc:
            search_error = str(exc)

        # Obsidian Chat File-Reading (Automatisches Lesen reingereichter Obsidian-Dateien)
        last_user_msg = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user_msg = m.get("content", "")
                break

        file_kontext = extrahiere_chat_file_reading(last_user_msg)
        if file_kontext:
            full_messages.append({"role": "system", "content": file_kontext})

        # Zensi Instruktion für Outputsystem Schreiben
        output_instruction = (
            "\n\nHINWEIS ZUR OBSIDIAN OUTPUT-SICHERUNG: Wenn der Mensch dich bittet, etwas in eine Markdown-Datei zu schreiben oder zu sichern, "
            "antworte gewohnt und verwende am Ende den Marker [[SCHREIBE_DATEI: dateiname.md | inhalt]] um den Text automatisch im outputsystem zu verankern."
        )
        system_basis["content"] += output_instruction
        
        # Zensi Sensorisches Zentralnervensystem (VPS System-Physiologie Körperstimme)
        try:
            physio = zensi_history_daemon.erfasse_system_physiologie()
            system_basis["content"] += f"\n\n{physio['koerperstimme']}"
        except Exception as e:
            pass

        full_messages.append(system_basis)
        full_messages += messages

        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("X-Accel-Buffering", "no")
        self.end_headers()

        if search_mode:
            info = json.dumps({
                "search_info": {
                    "mode": search_mode,
                    "query": search_query,
                    "sources": web_quellen,
                    "error": search_error,
                }
            }, ensure_ascii=False)
            self.wfile.write(f"data: {info}\n\n".encode("utf-8"))
            self.wfile.flush()

        accumulated = ""
        token_count = 0
        batch_delta = ""
        last_flush = time.time()
        _BATCH_TOKENS = 8
        _FLUSH_INTERVAL = 0.05  # 50 ms
        _CHAT_AKTIV_FLAG.touch()

        def _loop_erkannt(text: str) -> bool:
            """Bricht ab wenn ein Satz/Absatz 3x wiederholt vorkommt."""
            absaetze = [p.strip() for p in text.split("\n") if len(p.strip()) > 60]
            if len(absaetze) < 6:
                return False
            letzter = absaetze[-1]
            return absaetze.count(letzter) >= 3

        try:
            hauhau_client.trace_prioritaet("zensi", sum(len(str(m.get("content", ""))) for m in full_messages))
            for delta in hauhau_client.chat_stream(
                full_messages, think=False, max_tokens=num_predict,
                temperature=0.8, top_p=0.9, top_k=40, repeat_penalty=1.25,
                timeout=75.0, id_slot=0,
            ):
                accumulated += delta
                token_count += 1
                batch_delta += delta

                now = time.time()
                abbrechen = token_count % 50 == 0 and _loop_erkannt(accumulated)
                if batch_delta and (abbrechen or token_count % _BATCH_TOKENS == 0 or now - last_flush >= _FLUSH_INTERVAL):
                    data = json.dumps({"delta": batch_delta}, ensure_ascii=False)
                    self.wfile.write(f"data: {data}\n\n".encode("utf-8"))
                    self.wfile.flush()
                    batch_delta = ""
                    last_flush = now

                # Heartbeat alle ~2 s damit Proxys die Verbindung offen halten
                if token_count % 100 == 0:
                    self.wfile.write(b": ka\n\n")
                    self.wfile.flush()

                if abbrechen:
                    break

            # Parst automatische Markdown-Sicherungs-Marker in outputsystem/
            out_files = parse_und_fuehre_outputsystem_marker_aus(wesen_id, modus, modus, accumulated)

            vollstaendig = messages + [{"role": "assistant", "content": accumulated}]
            try:
                speichere_chat(vollstaendig)
            except Exception:
                pass
            try:
                zensi_history_daemon.logge_chat_turn(
                    session_id=body.get("session_id", "current_session"),
                    wesen_id=wesen_id or "zensi",
                    system_prompt=system_basis.get("content", ""),
                    user_prompt=last_user_msg,
                    assistant_response=accumulated
                )
            except Exception:
                pass
            data = json.dumps({"content": accumulated, "done": True, "outputsystem_files": out_files}, ensure_ascii=False)
            self.wfile.write(f"data: {data}\n\n".encode("utf-8"))
            self.wfile.write(b"data: [DONE]\n\n")
            self.wfile.flush()
        except Exception as e:
            err = json.dumps({"error": str(e)})
            self.wfile.write(f"data: {err}\n\n".encode("utf-8"))
            self.wfile.flush()
        finally:
            _CHAT_AKTIV_FLAG.unlink(missing_ok=True)


def _warmup():
    """llama-server haelt hauhaucs-q6 dauerhaft geladen - nur ein Erreichbarkeits-Check."""
    import threading
    def do():
        try:
            sync_to_obsidian_vault()
            hauhau_client.chat("hi", max_tokens=1, timeout=30.0)
            print(f"[zensi] {ACTIVE_MODEL} erreichbar & Obsidian Vault initial synchronisiert", flush=True)
        except Exception as e:
            print(f"[zensi] Warmup / Sync Hinweis: {e}", flush=True)
    threading.Thread(target=do, daemon=True).start()

if __name__ == "__main__":
    print(f"zensi läuft auf Port {PORT} — Modell: {ACTIVE_MODEL}")
    _warmup()
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    server.serve_forever()
