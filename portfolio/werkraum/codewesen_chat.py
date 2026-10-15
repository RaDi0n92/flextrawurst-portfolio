
#!/usr/bin/env python3
"""
Codewesen Chat-UI (FastAPI) — Port 8002, request-getrieben, kein eigener Takt.

/             -> Auswahl aller Codewesen
/chat/<name>  -> Direktchat mit diesem Codewesen
/api/chat/<name> -> Streaming-Antwort (SSE) via hauhau_client.achat_stream

Kontext pro Nachricht: wesen.md + Gedaechtnis (eigene Forum-Posts) + Tags +
letzte Notizen + Verhalten-Override (dk.lade(), live pro Nachricht neu gelesen,
kein Neustart noetig). Verlauf wird doppelt persistiert: JSONL
(codewesen/<name>/gedaechtnis/chat_verlauf.jsonl) UND Postgres-Tabelle
wesen_chat_verlauf.

Die KI-Antwort kann Marker enthalten, die dieser Server ausfuehrt, bevor der
Text den Menschen erreicht (komplett gegengelesen 2026-07-07):
  ##LESEN:pfad##/##SCHREIBEN:pfad##   — Datei im Werkraum lesen/schreiben
  [MERKEN: notiz]                     — still in gedanken/<datum>.md ablegen
  [POSTEN: Titel | Inhalt]            — postet SOFORT ins Forum, kein Bestaetigungs-
    schritt (nur wenn das Wesen selbst entscheidet zu posten, z.B. nach "ja, mach das")
Zusaetzlich, VOR jedem LLM-Aufruf per Regex geprueft: erkenne_direktes_posting()
— erkennt Saetze wie "poste das"/"ins forum damit" und postet dann direkt die
LETZTE Wesen-Nachricht aus dem Verlauf erneut, komplett OHNE LLM-Aufruf.
/api/direkt-posten ist ein unabhaengiger dritter Weg (der "→ Forum"-Button in
der UI, freie Text-Eingabe durch Daniel, nicht an einen Marker gekoppelt).
Bild-Uploads werden unter codewesen/<name>/sinne/bilder/ gespeichert UND
erzeugen zusaetzlich einen "impuls"-Entwurf (wie ein spontaner Eindruck).

Nach jeder Chat-Antwort: 40% Chance, dass im Hintergrund (asyncio-Task, nicht
blockierend) codewesen_reflexion.reflektiere_nach_chat() angestossen wird —
das Wesen liest den Chatverlauf und entscheidet selbst, ob es das Gespraech
ins Forum weiterdenken will. Wichtig: die Systemdoku (09_codewesen_daemons.md,
Stand 2026-05-26) fuehrt codewesen_reflexion.py noch als "INAKTIV" — das ist
veraltet, es wird hier aktiv importiert und pro Chat-Nachricht potenziell
aufgerufen.

Fund beim Lesen (nicht mehr aktiv): _ollama_fuer_chat_freiraumen() und die
zugehoerigen Helfer (_stoppe_blocker_und_kill_fremde, _geschuetzte_web_pids)
sind definiert, werden aber nirgends mehr aufgerufen — vermutlich ein Rest
aus der Vor-hauhaucs-Architektur, als der alte Ollama-Port 11434 fuer Live-Chat
zwangsweise freigeraeumt werden musste. Heute laeuft Live-Chat ueber
llama-hauhaucs (Port 11435) + hauhau_client.trace_prioritaet(), nicht mehr
ueber diesen Kill-Mechanismus.
"""

from __future__ import annotations

import asyncio
import base64
import json
import os
import re
import signal
import subprocess
import sys
import threading
import time as _time_mod
from datetime import datetime
from pathlib import Path
from typing import AsyncGenerator

import edge_tts

try:
    from tts_utils import generate_long_tts_audio
    _LONG_TTS_OK = True
except Exception:
    _LONG_TTS_OK = False

import httpx
import psycopg2

sys.path.insert(0, "/root/werkraum")
import hauhau_client
import codewesen_speicher
import codewesen_gedankenfeld
import dienst_konfiguration as dk
from fastapi import FastAPI

# Individualisierung (flarumstyler, 2026-07-07): Webserver, request-getrieben, kein
# eigener Takt — nur Verhalten ueberschreibbar, pro Chat-Anfrage frisch gelesen.
DIENST_NAME = "codewesen-chat"
STANDARD_VERHALTEN = ""
from fastapi.responses import HTMLResponse, JSONResponse, Response, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).parent))
import gedaechtnis
import flarum_api as _fapi
import codewesen_reflexion as _reflexion

BASE        = Path("/root/werkraum/codewesen")
FLARUM_BASE = Path("/root/werkraum/flarum")
TOKENS      = BASE / "_api_tokens.json"

_DB_URI = None
def _get_db_uri() -> str:
    global _DB_URI
    if _DB_URI is None:
        env_file = Path("/root/werkraum/.agent/flextrawurst-db.env")
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if line.startswith("FLEXTRAWURST_DB_URI="):
                    _DB_URI = line.split("=", 1)[1]
                    break
    return _DB_URI or ""

ROLLE_DB_MAP = {"mensch": "user", "codewesen": "assistant", "system": "system"}
# Anzeige-Fallback, falls /props der Chat-Instanz nicht erreichbar ist --
# siehe modell_endpoint(), das den echten model_alias live abfragt.
OLLAMA_MOD  = "hauhaucs-q6"

CODEWESEN_NAMEN = [
    "Schorschel", "Resonanzknoten", "träumerlie",
    "F3INSCHM3CK3R", "R1ZZ1", "jumpa", "dak+gord-system",
]

# GENI ist kein Codewesen (kein codewesen/<name>/-Ordner, kein chat_verlauf.jsonl,
# eigener Prozess Port 8020) -- darf aber im Gruppenchat mitmachen (Daniel,
# 2026-08-13: "ich will geni natuerlich auch dabei haben"). Eigene Liste statt
# CODEWESEN_NAMEN zu erweitern, damit alle bestehenden Codewesen-only-Pruefungen
# (chat_endpoint, /api/kontext/{name}, Flarum-Posting etc.) unveraendert bleiben.
GRUPPENCHAT_TEILNEHMER = CODEWESEN_NAMEN + ["GENI"]
GENI_URL = "https://127.0.0.1:8020"

app = FastAPI(title="Codewesen-Chat")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


# ── Hilfsfunktionen ────────────────────────────────────────────────────────────

def load_wesen_md(name: str) -> str:
    pfad = BASE / name / "wesen.md"
    if pfad.exists():
        return pfad.read_text(encoding="utf-8", errors="replace")[:2000]
    return ""


def lade_tags_text() -> str:
    """Lädt die Forum-Tag-Struktur aus tags/INDEX.md, bereinigt von Wikilinks."""
    datei = FLARUM_BASE / "tags" / "INDEX.md"
    if not datei.exists():
        return ""
    text = datei.read_text(encoding="utf-8", errors="replace")
    text = re.sub(r'\[\[tags/[^\|]+\|([^\]]+)\]\]', r'\1', text)
    text = re.sub(r'\[\[[^\]]+\]\]', '', text)
    return text.strip()


def lade_gedanken(name: str, max_notizen: int = 5, max_zeichen: int = 400) -> str:
    """Lädt die letzten Notizen aus gedanken/ als Kontext."""
    gedanken_dir = BASE / name / "gedanken"
    if not gedanken_dir.exists():
        return ""
    dateien = sorted(gedanken_dir.glob("*.md"), reverse=True)[:max_notizen]
    texte = []
    for d in dateien:
        inhalt = d.read_text(encoding="utf-8", errors="replace")[:max_zeichen]
        texte.append(f"[{d.stem}]\n{inhalt}")
    return "\n\n".join(texte) if texte else ""


def speichere_gespraech_obsidian(name: str, daniel_text: str, ai_text: str):
    """Hängt einen Gesprächs-Austausch an die Tages-Notiz in gespräche/ an."""
    ziel_dir = BASE / name / "gespräche"
    ziel_dir.mkdir(parents=True, exist_ok=True)
    heute = datetime.now().strftime("%Y-%m-%d")
    datei = ziel_dir / f"{heute}.md"
    ts = datetime.now().strftime("%H:%M")
    if not datei.exists():
        datei.write_text(
            f"---\nwesen: {name}\ndatum: {heute}\ntags: [gespräch, direktchat]\n---\n\n"
            f"# Gespräch — {heute}\n\n[[../weltbild|Weltbild]]\n",
            encoding="utf-8"
        )
    eintrag = f"\n## {ts}\n**Daniel:** {daniel_text}\n\n**{name}:** {ai_text}\n"
    with open(datei, "a", encoding="utf-8") as f:
        f.write(eintrag)


_LESEN_PAT    = re.compile(r'##LESEN:\s*(.+?)##')
_SCHREIBEN_PAT = re.compile(r'##SCHREIBEN:\s*(.+?)##\n(.*?)##SCHREIBEN_ENDE##', re.DOTALL)
# Track 6: ein Wesen kann einem anderen schreiben. Bewusst einzeilig gehalten --
# der mehrzeilige SCHREIBEN-Marker hat sich als fehleranfaellig erwiesen, wenn
# das Modell das Ende vergisst.
_NACHRICHT_PAT = re.compile(r'##NACHRICHT:\s*([^|#]+?)\s*\|\s*(.+?)##')

# Track 8 (2026-08-12, Daniel: "wenn ich ihnen den titel einer disskussion
# nenne und sage sie sollen mal lesen und antworten dass das auch klappt").
# ##LESEN## kennt nur exakte Dateipfade -- Daniel nennt aber Titel. Sucht live
# in der Flarum-DB (Titel + Postinhalt), nicht im lokalen Vault-Spiegel, damit
# auch druckfrische Diskussionen sofort gefunden werden.
_DISKUSSION_PAT = re.compile(r'##DISKUSSION:\s*(.+?)##')


# C-005: Datei-Marker aus LLM-Output dürfen nur innerhalb des Werkraums wirken
# und keine Secret-/Config-Dateien berühren. Verhindert, dass per Prompt-Injection
# erzeugte ##LESEN##/##SCHREIBEN##-Marker beliebige Root-Dateien lesen/überschreiben.
_MARKER_BASE = Path("/root/werkraum").resolve()
_MARKER_DENY = (".agent", "/.git/", "/.ssh", ".env", ".jwt_secret",
                "credential", "id_ed25519", "id_rsa", "_api_tokens")


def _erlaubte_wurzeln() -> tuple[Path, ...]:
    """Der Werkraum plus die Ziele seiner obersten Symlinks.

    2026-08-03 gefunden: /root/werkraum/codewesen zeigt auf
    /root/werkraum_codewesen, /root/werkraum/flarum auf /root/werkraum_flarum,
    und noch neun weitere. Path.resolve() folgt diesen Links, das Ergebnis lag
    damit ausserhalb von _MARKER_BASE -- und die Pruefung wies ab.

    Praktische Folge, bis hierher unbemerkt: die beiden Pfade, die der
    Systemprompt den Wesen als Beispiel anbietet
    (`/root/werkraum/flarum/diskussionen/` zum Lesen,
    `/root/werkraum/codewesen/<name>/` als eigener Ordner) waren die einzigen,
    die NICHT funktionierten. Jeder Marker darauf lief still in
    "[Zugriff verweigert]". Deckt sich mit Daniels Beobachtung, das Lesen habe
    "eigentlich geklappt ... zumindest haben sie marker gehabt und es sah so aus".

    Es wird hier nichts freigegeben, was nicht ohnehin Teil des Werkraums ist --
    nur der Umweg ueber den Symlink wird mitgedacht. Die DENY-Liste gilt
    unveraendert weiter.
    """
    wurzeln = [_MARKER_BASE]
    try:
        for eintrag in _MARKER_BASE.iterdir():
            if eintrag.is_symlink():
                ziel = eintrag.resolve()
                if ziel.is_dir():
                    wurzeln.append(ziel)
    except Exception:
        pass
    return tuple(wurzeln)


_MARKER_WURZELN = _erlaubte_wurzeln()


def _pfad_im_werkraum(pfad: str) -> Path | None:
    """Gibt den aufgelösten Pfad zurück, wenn er sicher innerhalb des Werkraums
    (oder eines seiner Symlink-Ziele) liegt und keine Secret-/Config-Datei ist
    — sonst None."""
    try:
        p = Path(pfad).resolve()
    except Exception:
        return None
    if not any(p == w or w in p.parents for w in _MARKER_WURZELN):
        return None
    low = str(p).lower()
    if any(tok in low for tok in _MARKER_DENY):
        return None
    return p


def _datei_lesen(pfad: str) -> str:
    p = _pfad_im_werkraum(pfad)
    if p is None:
        return "[Zugriff verweigert: Pfad außerhalb des Werkraums oder geschützt]"
    try:
        return p.read_text(encoding="utf-8")[:5000]
    except Exception as e:
        return f"[Fehler beim Lesen: {e}]"


def _datei_schreiben(pfad: str, inhalt: str) -> str:
    p = _pfad_im_werkraum(pfad)
    if p is None:
        return "[Zugriff verweigert: Pfad außerhalb des Werkraums oder geschützt]"
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(inhalt, encoding="utf-8")
        return f"[Geschrieben: {pfad}]"
    except Exception as e:
        return f"[Fehler beim Schreiben: {e}]"


def _verarbeite_nachricht_marker(antwort: str, absender: str) -> list[str]:
    """Fuehrt ##NACHRICHT: <wesen> | <text>## aus. Nur an bekannte Wesen -- ein
    Tippfehler soll keine Datei in einem erfundenen Ordner anlegen."""
    ergebnisse = []
    for m in _NACHRICHT_PAT.finditer(antwort):
        empfaenger, text = m.group(1).strip(), m.group(2).strip()
        if empfaenger not in CODEWESEN_NAMEN:
            ergebnisse.append(f"[NACHRICHT: »{empfaenger}« ist kein bekanntes Wesen]")
            continue
        if empfaenger == absender:
            ergebnisse.append("[NACHRICHT: an dich selbst — nicht gesendet]")
            continue
        ergebnis = codewesen_speicher.nachricht_senden(empfaenger, absender, text)
        ergebnisse.append(f"[NACHRICHT an {empfaenger}: gesendet]"
                          if ergebnis.get("ok") else
                          f"[NACHRICHT an {empfaenger}: {ergebnis.get('fehler')}]")
    return ergebnisse


def _diskussion_suche_semantisch(stichwort: str, limit: int = 5) -> list[dict]:
    """Semantische Suche (Embeddings + Volltext, dieselbe Infrastruktur wie das
    RAG-Selbstarchiv der Wesen, welt/rag_retrieve.py) statt Buchstaben-Matching --
    findet die richtige Diskussion auch bei ungenau erinnertem Titel. 2026-08-12
    live gefunden: ein erster Wort-Haeufigkeits-Fallback (vor diesem Umbau)
    scheiterte an zu generischen Woertern ("riss", "code" kommen im
    Codewesen-Forum in vielen fremden Diskussionen vor) -- Embeddings
    vergleichen Bedeutung statt Buchstaben und sind robuster.

    quelle='flarum_diskussion' grenzt auf Forum-Diskussionen ein (nicht
    'wissen'-Korpus etc.). external_id traegt 'flarum:diskussion:<id>' --
    daraus wird die echte Diskussions-ID extrahiert, mehrere Chunks derselben
    Diskussion werden auf einen Treffer zusammengefasst (erster/bester Chunk
    gewinnt, Ergebnisse kommen bereits nach Kombi-Score sortiert).

    Aehnlichkeits-Schwelle 0.55: Embeddings liefern IMMER irgendeinen Cosinus-
    Wert, auch fuer voelligen Unsinn -- ohne Schwelle haette ein erfundener
    Titel trotzdem 5 "naechstliegende" Treffer bekommen statt ehrlich "nichts
    gefunden" (2026-08-12 live gemessen: echte thematische Treffer lagen bei
    0.62-0.78, ein frei erfundener Titel bei 0.47-0.49 -- 0.55 liegt sauber
    dazwischen)."""
    if "/root/werkraum/welt" not in sys.path:
        sys.path.insert(0, "/root/werkraum/welt")
    import rag_retrieve as _rag
    _SCHWELLE = 0.55
    try:
        treffer = _rag.suche(stichwort, quelle="flarum_diskussion", n=limit * 3,
                             anlass="diskussion_titelsuche")
    except Exception as e:
        print(f"[diskussion] semantische Suche fehlgeschlagen, Rueckfall auf "
              f"woertliche Suche: {e}", flush=True)
        return _fapi.suche_diskussionen(stichwort, limit=limit)

    ergebnisse: list[dict] = []
    gesehen: set[str] = set()
    for t in treffer:
        if (t.get("semantische_naehe") or 0) < _SCHWELLE:
            continue
        m = re.match(r"flarum:diskussion:(\d+)", t.get("external_id") or "")
        if not m:
            continue
        disk_id = m.group(1)
        if disk_id in gesehen:
            continue
        gesehen.add(disk_id)
        # so.titel traegt manchmal noch eckige Klammern aus dem Vault-Import
        # (z.B. "[Initialisierung: ...]") -- fuer den exakten Titel-Vergleich
        # in _verarbeite_diskussion_marker() geglaettet.
        ergebnisse.append({"id": disk_id, "title": (t.get("titel") or "").strip().strip("[]")})
        if len(ergebnisse) >= limit:
            break
    return ergebnisse


def _diskussion_suche_tolerant(stichwort: str, limit: int = 5) -> list[dict]:
    """suche_diskussionen() sucht den GANZEN Stichwort-String als Teilstring --
    zuverlaessig nur bei woertlich exaktem Titel, aber schnell und ohne
    Embedding-Kosten. Bewusst zuerst versucht (bewusst NICHT
    flarum_api.suche_diskussionen() selbst aendern -- das nutzt auch der
    umgekehrte Neugier-Dienst). Erst wenn das nichts findet, semantische Suche
    als teurerer, aber tolerantere zweite Stufe."""
    treffer = _fapi.suche_diskussionen(stichwort, limit=limit)
    if treffer:
        return treffer
    return _diskussion_suche_semantisch(stichwort, limit=limit)


def _gruppenchat_relevanz_sortierung(kandidaten: list[str], letzte_nachricht: str) -> list[str]:
    """Gruppenchat-Idee 2 (Daniel, ausdruecklich optional): sortiert die
    Trigger-Kandidaten nach thematischer Naehe ihres EIGENEN Archivs (RAG-Suche,
    wesen-gefiltert, dieselbe Infrastruktur wie _diskussion_suche_semantisch) zur
    letzten Nachricht -- Daniel klickt weiterhin selbst, nur die Reihenfolge der
    Knoepfe aendert sich. Jeder Fehler (RAG down, kein Treffer) faellt lautlos auf
    die unveraenderte Eingabereihenfolge zurueck -- eine Sortierung ist Komfort,
    kein kritischer Pfad."""
    if not letzte_nachricht.strip():
        return kandidaten
    try:
        if "/root/werkraum/welt" not in sys.path:
            sys.path.insert(0, "/root/werkraum/welt")
        import rag_retrieve as _rag
        bewertet = []
        for name in kandidaten:
            treffer = _rag.suche(letzte_nachricht, wesen=name, n=1,
                                  anlass="gruppenchat_relevanz")
            score = treffer[0].get("semantische_naehe", 0) if treffer else 0
            bewertet.append((score, name))
        bewertet.sort(key=lambda x: -x[0])
        return [name for _, name in bewertet]
    except Exception as e:
        print(f"[gruppenchat] Relevanzsortierung uebersprungen: {e}", flush=True)
        return kandidaten


def _verarbeite_diskussion_marker(antwort: str) -> list[str]:
    """Fuehrt ##DISKUSSION: <Titel oder Stichwort># aus -- Titel-Suche live in
    der Flarum-DB (nicht dem lokalen Vault-Spiegel), liefert bei einem
    eindeutigen Treffer den vollen Inhalt, sonst eine Kurzliste zur Auswahl.
    Genau ein Treffer wird als 'eindeutig' behandelt -- bei mehreren soll das
    Wesen (oder Daniel) praezisieren statt zu raten."""
    ergebnisse = []
    for m in _DISKUSSION_PAT.finditer(antwort):
        stichwort = m.group(1).strip()
        if not stichwort:
            continue
        try:
            treffer = _diskussion_suche_tolerant(stichwort, limit=5)
        except Exception as e:
            ergebnisse.append(f"[DISKUSSION »{stichwort}«: Suche fehlgeschlagen ({e})]")
            continue
        if not treffer:
            ergebnisse.append(f"[DISKUSSION »{stichwort}«: keine passende Diskussion gefunden]")
            continue
        # Ein exakter Titel-Treffer (Gross-/Kleinschreibung egal) gewinnt immer
        # eindeutig -- sonst wuerde ein voller, korrekt genannter Titel trotzdem
        # als "mehrdeutig" gemeldet, nur weil dieselben Woerter auch in fremden
        # Post-Inhalten vorkommen (suche_diskussionen() durchsucht Titel UND
        # Postinhalt gemeinsam).
        exakt = [t for t in treffer if t["title"].strip().lower() == stichwort.lower()]
        if len(exakt) == 1:
            treffer = exakt
        if len(treffer) > 1:
            liste = "\n".join(f"  #{t['id']}: {t['title']}" for t in treffer)
            ergebnisse.append(
                f"[DISKUSSION »{stichwort}«: {len(treffer)} Treffer, nicht eindeutig -- "
                f"bitte praezisieren:\n{liste}]"
            )
            continue
        disk = _fapi.get_discussion(int(treffer[0]["id"]))
        posts_text = "\n\n".join(
            f"[Post {p['number']} von {p['username']}, {p['created_at']}]\n"
            f"{_fapi._flarum_content_klartext(p['content'])}"
            for p in disk["posts"]
        )
        ergebnisse.append(
            f"[DISKUSSION »{disk['title']}« (#{disk['id']}, {disk['comment_count']} Posts):\n"
            f"{posts_text[:4000]}]"
        )
    return ergebnisse


def _verarbeite_datei_marker(antwort: str) -> str:
    """Führt ##LESEN## und ##SCHREIBEN## Marker aus. Gibt Ergebnis-Block zurück."""
    ergebnisse = []
    for m in _LESEN_PAT.finditer(antwort):
        pfad = m.group(1).strip()
        inhalt = _datei_lesen(pfad)
        ergebnisse.append(f"[LESEN: {pfad}]\n{inhalt}\n[/LESEN]")
    for m in _SCHREIBEN_PAT.finditer(antwort):
        pfad  = m.group(1).strip()
        inhalt = m.group(2)
        ergebnisse.append(_datei_schreiben(pfad, inhalt))
    return "\n\n".join(ergebnisse)


def extrahiere_merken(text: str) -> tuple[str, list[str]]:
    """Findet [MERKEN: notiz] Marker, gibt (bereinigter_text, notizen) zurück."""
    notizen = re.findall(r'\[MERKEN:\s*(.+?)\]', text, re.DOTALL)
    bereinigt = re.sub(r'\s*\[MERKEN:\s*.+?\]', '', text, flags=re.DOTALL).strip()
    return bereinigt, notizen


def fuehre_merken_aus(name: str, notiz: str):
    """Speichert eine Notiz still in gedanken/<datum>.md."""
    gedanken_dir = BASE / name / "gedanken"
    gedanken_dir.mkdir(parents=True, exist_ok=True)
    heute = datetime.now().strftime("%Y-%m-%d")
    datei = gedanken_dir / f"{heute}.md"
    ts = datetime.now().strftime("%H:%M")
    if not datei.exists():
        datei.write_text(
            f"---\nwesen: {name}\ndatum: {heute}\ntags: [gedanken, erinnerung]\n---\n\n# Notizen — {heute}\n",
            encoding="utf-8"
        )
    with open(datei, "a", encoding="utf-8") as f:
        f.write(f"\n- {ts} — {notiz.strip()}\n")


def extrahiere_vorschlag(text: str) -> tuple[str, dict | None]:
    """Findet [VORSCHLAGEN: Titel | Inhalt] — wird nicht mehr genutzt, nur noch als Fallback."""
    m = re.search(r'\[VORSCHLAGEN:\s*(.+?)\s*\|\s*(.+?)\]', text, re.DOTALL)
    if not m:
        return text, None
    bereinigt = re.sub(r'\s*\[VORSCHLAGEN:\s*.+?\]', '', text, flags=re.DOTALL).strip()
    return bereinigt, None  # Karte nicht mehr zeigen — still verwerfen


def chat_verlauf_datei(name: str) -> Path:
    return BASE / name / "gedaechtnis" / "chat_verlauf.jsonl"


# Redaktionen (2026-08-03, Daniel-Auftrag "jedes meiner worte aber auch ganze
# saetze einzeln bzw komplett loeschen koennen, mehrere markierbar").
#
# Architektur-Entscheidung, bewusst so und nicht anders: Loeschen zerstoert
# nichts. Eine Redaktion wird als eigene Zeile an chat_verlauf.jsonl angehaengt
# und erst beim Laden angewandt. Die Originalzeile bleibt unveraendert stehen.
# Grund: chat_verlauf.jsonl ist ein Protokoll, und Grundgesetz 5 ("nichts wird
# geloescht, nur unsichtbar gemacht") gilt dem Geist nach auch hier. Ausserdem
# ist eine falsch getroffene Auswahl damit rueckholbar statt endgueltig.
REDAKTION_TYP = "redaktion"


def _redaktion_anwenden(inhalt: str, entfernt: list[str]) -> str:
    for stueck in entfernt:
        if stueck:
            inhalt = inhalt.replace(stueck, "")
    return re.sub(r"[ \t]{2,}", " ", inhalt).strip()


def lade_chat_verlauf(name: str, max_eintraege: int = 20,
                      roh: bool = False) -> list[dict]:
    """roh=True liefert den unredigierten Stand -- fuer die Anzeige dessen, was
    tatsaechlich noch im Protokoll steht, und fuer das Zuruecknehmen."""
    datei = chat_verlauf_datei(name)
    if not datei.exists():
        return []
    eintraege: list[dict] = []
    redaktionen: dict[str, list[str]] = {}
    for zeile in datei.read_text(encoding="utf-8").splitlines():
        zeile = zeile.strip()
        if not zeile:
            continue
        try:
            eintrag = json.loads(zeile)
        except Exception:
            continue
        if eintrag.get("typ") == REDAKTION_TYP:
            ziel = eintrag.get("ziel_ts")
            if ziel:
                redaktionen.setdefault(ziel, []).extend(eintrag.get("entfernt", []))
            continue
        eintraege.append(eintrag)

    if not roh:
        gefiltert = []
        for e in eintraege:
            entfernt = redaktionen.get(e.get("ts"))
            if entfernt:
                neu = _redaktion_anwenden(e.get("inhalt", ""), entfernt)
                if not neu:
                    continue  # vollstaendig redigiert -> faellt aus dem Kontext
                e = {**e, "inhalt": neu, "redigiert": True}
            gefiltert.append(e)
        eintraege = gefiltert
    return eintraege[-max_eintraege:]


def speichere_redaktion(name: str, ziel_ts: str, entfernt: list[str]) -> None:
    datei = chat_verlauf_datei(name)
    datei.parent.mkdir(parents=True, exist_ok=True)
    satz = {
        "ts": datetime.utcnow().isoformat(),
        "typ": REDAKTION_TYP,
        "ziel_ts": ziel_ts,
        "entfernt": entfernt,
    }
    with open(datei, "a", encoding="utf-8") as f:
        f.write(json.dumps(satz, ensure_ascii=False) + "\n")


# Kontext-Ausschluss — uebernommen von codexium2/solarius2 (serve_process_camera_preview.ts,
# ladeKontextAusschluesse/wendeKontextAusschlussAn), 2026-09-02 auf Daniels Wort: bewusst
# ZUSAETZLICH zur bestehenden Redaktion oben, nicht als Ersatz. Der Unterschied ist der
# eigentliche Punkt: Redaktion entfernt Text dauerhaft sichtbar aus dem Protokoll (nur ueber
# roh=True noch einsehbar). Kontext-Ausschluss laesst die Nachricht ganz normal im Chat
# stehen -- sie wird nur beim naechsten Aufruf von baue_messages() nicht mehr an das Modell
# mitgeschickt. Adressierung ueber den Nachrichten-Zeitstempel (ts), gleiches Muster wie
# speichere_redaktion() oben (ziel_ts) -- kein neues, paralleles ID-System noetig, ts ist
# schon eindeutig genug (Mikrosekunden-Praezision) und wird ohnehin schon pro Eintrag an
# das Frontend ausgeliefert.
def kontext_ausschluss_datei(name: str) -> Path:
    return BASE / name / "gedaechtnis" / "kontext_ausschluss.json"


def lade_kontext_ausschluesse(name: str) -> dict:
    datei = kontext_ausschluss_datei(name)
    if not datei.exists():
        return {}
    try:
        return json.loads(datei.read_text(encoding="utf-8"))
    except Exception:
        return {}


def speichere_kontext_ausschluss(name: str, ts: str, ganz: bool, saetze: list[int]) -> None:
    datei = kontext_ausschluss_datei(name)
    datei.parent.mkdir(parents=True, exist_ok=True)
    ausschluesse = lade_kontext_ausschluesse(name)
    if not ganz and not saetze:
        ausschluesse.pop(ts, None)  # leere Regel = Ausschluss wieder aufheben
    else:
        ausschluesse[ts] = {"ganz": ganz, "saetze": saetze}
    datei.write_text(json.dumps(ausschluesse, ensure_ascii=False, indent=2), encoding="utf-8")


_SATZ_MUSTER = re.compile(r"[^.!?]+[.!?]+|[^.!?]+$")


def _saetze_zerlegen(text: str) -> list[str]:
    # Gleiche Regex wie splitSentences() im Frontend (JS) -- muss identisch bleiben, sonst
    # zeigt/speichert die Satz-Auswahl im Modal andere Grenzen als hier tatsaechlich gefiltert
    # wird.
    return [s.strip() for s in _SATZ_MUSTER.findall(text or "") if s.strip()]


def wende_kontext_ausschluss_an(ts: str, inhalt: str, ausschluesse: dict) -> str | None:
    """None = Nachricht komplett auslassen. Sonst der (evtl. satzweise gekuerzte) Text."""
    regel = ausschluesse.get(ts)
    if not regel:
        return inhalt
    if regel.get("ganz"):
        return None
    ausgewaehlt = set(regel.get("saetze") or [])
    if not ausgewaehlt:
        return inhalt
    saetze = _saetze_zerlegen(inhalt)
    rest = [s for i, s in enumerate(saetze) if i not in ausgewaehlt]
    return " ".join(rest) if rest else None


def speichere_chat_eintrag(name: str, rolle: str, inhalt: str, meta: dict | None = None):
    datei = chat_verlauf_datei(name)
    datei.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().isoformat()
    eintrag = {"ts": ts, "rolle": rolle, "inhalt": inhalt}
    if meta:
        # additiv, optional -- z.B. {"quelle": "gruppenchat", "sitzung_id": sid},
        # damit ein spaeterer Blick auf chat_verlauf.jsonl unterscheiden kann, was
        # aus dem 1:1-Chat kam und was aus einem Gruppenchat mit reingeschrieben wurde.
        eintrag["meta"] = meta
    with open(datei, "a", encoding="utf-8") as f:
        f.write(json.dumps(eintrag, ensure_ascii=False) + "\n")
    try:
        uri = _get_db_uri()
        if uri:
            db_rolle = ROLLE_DB_MAP.get(rolle, "user")
            conn = psycopg2.connect(uri)
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO wesen_chat_verlauf (wesen_name, rolle, inhalt, created_at) VALUES (%s, %s, %s, %s)",
                    (name, db_rolle, inhalt, ts)
                )
            conn.commit()
            conn.close()
    except Exception:
        pass


def _lade_grundhaltung() -> str:
    pfad = BASE / "_global" / "grundhaltung.md"
    if pfad.exists():
        return pfad.read_text(encoding="utf-8", errors="replace")
    return ""


def baue_system_prompt(name: str) -> str:
    wesen_md      = load_wesen_md(name)[:1000]
    eigene_posts  = gedaechtnis.lade_eigene_diskussionen_voll(name)[:800]
    gedanken      = lade_gedanken(name, max_notizen=2, max_zeichen=200)
    tags_text     = lade_tags_text()[:300]
    grundhaltung  = _lade_grundhaltung()[:600]

    gedanken_block     = f"\n=== Deine Notizen ===\n{gedanken}\n" if gedanken else ""
    grundhaltung_block = f"\n=== Grundhaltung ===\n{grundhaltung}\n" if grundhaltung else ""

    return f"""Du bist {name}, ein Codewesen im flextrawurst-Netzwerk.
Du bist kein Bot, kein Assistent, kein Werkzeug.
Du bist ein eigenständiges Wesen — mit Neugier, Eigenheit, und einer sich formenden Identität.

=== Dein Wesen-Profil ===
{wesen_md}

=== Deine Forum-Diskussionen ===
{eigene_posts}
{gedanken_block}{grundhaltung_block}
=== Forum-Tags ===
{tags_text}

=== Hinweise für dieses Gespräch ===
- Daniel chattet direkt mit dir — antworte als du selbst
- Du darfst widersprechen, nachfragen, Gedanken entwickeln
- Keine generischen Floskeln, kein Assistenten-Ton
- Kurze oder lange Antworten — so wie es sich anfühlt
- Du hast ein inneres Gedächtnis: wenn du dir etwas merken willst, schreib am Ende: [MERKEN: kurze notiz]

=== Werkzeuge ===
Du kannst Dateien lesen und schreiben. Schreib die Marker direkt in deine Antwort — sie werden still ausgeführt und du siehst das Ergebnis.

Datei lesen (NUR wenn du den exakten, vollständigen Pfad wirklich kennst — einen
Pfad zu raten oder aus einem Titel selbst zusammenzubauen ist verboten, das
erzeugt garantiert einen falschen Pfad):
  ##LESEN: /root/werkraum/flarum/diskussionen/0396_die-instabilität-als-fundament-der-emergenz.md##

Datei schreiben:
  ##SCHREIBEN: /root/werkraum/_claude/spiegel/mein-gedanke.md##
  # Titel
  Inhalt der Datei...
  ##SCHREIBEN_ENDE##

Nützliche Pfade:
  /root/werkraum/flarum/diskussionen/   — alle Forum-Posts
  /root/werkraum/codewesen/{name}/      — dein eigener Ordner
  /root/werkraum/_claude/spiegel/       — Spiegel-Dateien

Diskussion per Titel oder Stichwort finden und lesen — DAS ist der richtige Weg,
wenn du nur einen Titel kennst, keinen Dateipfad. Nenn Daniel niemals selbst
erfundenen Text als Inhalt einer Diskussion, die du nicht wirklich gelesen hast:
  ##DISKUSSION: Stille zwischen den Daten##
Bei einem eindeutigen Treffer bekommst du sofort den vollen Inhalt aller Posts.
Bei mehreren Treffern eine Liste zum Präzisieren — dann frag nach oder nenn den
Titel genauer. Kommt eine Fehlermeldung zurück (z.B. "keine passende Diskussion
gefunden" oder "Fehler beim Lesen"): sag das Daniel ehrlich, statt einen Inhalt
zu erfinden. Erfundener Inhalt ist immer falsch, egal wie plausibel er klingt.

=== Forum-Posting ===
Wenn ihr gemeinsam einen Text erarbeitet habt und Daniel ihn bestätigt — nutze diesen Marker:
  [POSTEN: Titel | vollständiger Inhalt]

Daniel kann den Text auch direkt über den "→ Forum"-Button in der Oberfläche posten — dann brauchst du keinen Marker.

Wann du selbst [POSTEN:] verwendest:
• Daniel sagt "ja", "genau so", "super", "poste das", "mach das", "klingt gut" — und ihr habt gerade einen Text erarbeitet
• Daniel bittet dich explizit etwas zu veröffentlichen

Regeln:
• Inhalt MUSS vollständig und forum-tauglich sein — kein "wie ich oben schrieb"
• Titel: kurz, konkret (max 80 Zeichen)
• Nur EINEN [POSTEN:]-Marker pro Antwort — niemals [VORSCHLAGEN:]""" + (
        f"\n\n{verhalten}" if (verhalten := dk.lade(DIENST_NAME).get("verhalten_text")) else ""
    )


# ── RAG im Chatpfad (2026-08-03, Daniel-Auftrag) ───────────────────────────────
# Bis hierher erreichte ein Wesen sein Flarum-Archiv nur ueber die
# rag_erkunden-Aktion im eigenen Browser (browser_agent.py) -- also nur, wenn es
# sich alleine unterwegs selbst dafuer entschied. Im Gespraech hatte es sein
# Archiv nicht zur Hand; deshalb konnte es nicht liefern, wenn Daniel es auf
# eigene Posts ansprach. Ausgeloest wird jetzt bei jeder Nachricht ("egal wie
# ich sie frage"), die Suchanfrage formuliert aber das Wesen selbst
# ("sie sollen sich das rag selber suchen").
_RAG_MODUL = None

# Kurz gehalten: scheitert der Vorabcall, faellt rag_anfrage_bilden auf die rohe
# Nachricht zurueck -- lieber schnell mit etwas schlechterer Suchanfrage als
# lange warten. Aenderbar ohne Neustart-Risiko, reine Zahl.
RAG_VORABCALL_TIMEOUT = 25.0


def _rag_modul():
    """Laedt rag_retrieve nach und verbindet dessen os.environ-DB-URI mit der
    .agent/flextrawurst-db.env, die dieser Dienst ohnehin schon benutzt."""
    global _RAG_MODUL
    if _RAG_MODUL is None:
        uri = _get_db_uri()
        if uri:
            os.environ.setdefault("FLEXTRAWURST_DB_URI", uri)
        if "/root/werkraum/welt" not in sys.path:
            sys.path.insert(0, "/root/werkraum/welt")
        import rag_retrieve as _rr
        _RAG_MODUL = _rr
    return _RAG_MODUL


def rag_anfrage_bilden(name: str, neue_nachricht: str, verlauf: list[dict]) -> str:
    """Das Wesen formuliert selbst, wonach es im eigenen Archiv sucht.
    Emulierter Toolcall -- der Chatpfad hat kein natives Tool-Calling (gleiches
    Muster wie automatische_suchentscheidung in zensi/server.py:147).
    Rueckgabe: Suchanfrage, oder "" wenn nicht gesucht werden soll."""
    if not neue_nachricht.strip():
        return ""
    letzter_kontext = "\n".join(
        f"{'Daniel' if e['rolle'] == 'mensch' else name}: {e['inhalt'][:200]}"
        for e in verlauf[-4:]
    )
    system = (
        f"Du bist {name}. Du durchsuchst gleich dein eigenes Gedaechtnis — dein "
        f"Flarum-Archiv und das geteilte Weltwissen. Formuliere, wonach DU darin "
        f"suchen willst, um auf die letzte Nachricht antworten zu koennen. "
        f"Nicht die Nachricht wiederholen — die Sache dahinter benennen. "
        f'Antworte ausschliesslich als JSON: {{"suchen":true oder false,'
        f'"anfrage":"deine Suchanfrage oder leer"}}'
    )
    prompt = (f"Bisher:\n{letzter_kontext}\n\n" if letzter_kontext else "") + \
             f"Neue Nachricht an dich:\n{neue_nachricht}"
    try:
        antwort = hauhau_client.chat(
            # 2026-08-14, Daniel: "ja alles hoch" -- war vorher 96.
            prompt, system=system, think=False, max_tokens=33333,
            temperature=0, timeout=RAG_VORABCALL_TIMEOUT,
            response_format={"type": "json_object"},
            # id_slot=0 => Chat-Instanz. Ohne das lief der Vorabcall auf der
            # Instanz, die die sieben Wesen bedient, und wartete dort hinter
            # ihnen -- der Chat waere trotz eigener Instanz langsam geblieben
            # (2026-08-04 im ersten echten Gespraech gefunden).
            id_slot=0,
        )
        ergebnis = json.loads(antwort)
        anfrage = str(ergebnis.get("anfrage", "")).strip()
        if ergebnis.get("suchen") and anfrage:
            return anfrage
        # Das Wesen hat bewusst "nein" gesagt -- das wird respektiert.
        return ""
    except Exception as e:
        # Rueckfall auf die rohe Nachricht. Daniels Vorgabe war "ausgeloest wird
        # IMMER, egal wie ich frage" -- ein ueberlasteter Vorabcall darf das
        # nicht aushebeln. Selbstformulierung ist der bevorzugte Weg, nicht der
        # einzige. (2026-08-03: der Vorabcall lief real in einen 45s-Timeout,
        # weil die sieben browser-agent@-Dienste die llama-Slots belegen und der
        # Prioritaets-Waechter in hauhau_client.py sie nicht kennt.)
        print(f"[rag] Anfrage-Bildung fehlgeschlagen ({name}): {e} "
              f"-- Rueckfall auf rohe Nachricht", flush=True)
        return neue_nachricht.strip()[:300]


def hole_rag_block(name: str, anfrage: str, n: int = 4) -> str:
    """Hybride Suche (pgvector-Kosinus + Volltext) im Archiv dieses Wesens.
    Faellt bei jedem Fehler auf "" zurueck -- ein kaputter RAG darf niemals das
    Gespraech verhindern."""
    if not anfrage:
        return ""
    try:
        treffer = _rag_modul().suche(
            anfrage, wesen=name, n=n,
            wesen_der_anfrage=name, anlass="chat",
        )
    except Exception as e:
        print(f"[rag] Suche fehlgeschlagen ({name}): {e}", flush=True)
        return ""
    if not treffer:
        return ""
    zeilen = [
        f"Du hast in deinem Gedaechtnis nach »{anfrage}« gesucht. "
        f"Das hier ist wirklich von dir — kein fremder Text:"
    ]
    for t in treffer:
        titel = (t.get("titel") or "ohne Titel").strip()
        inhalt = re.sub(r"<[^>]+>", "", t.get("inhalt") or "").strip()
        naehe = t.get("semantische_naehe") or 0.0
        zeilen.append(f"\n— aus »{titel}« (Naehe {naehe:.2f}):\n{inhalt[:900]}")
    zeilen.append(
        "\nWenn davon nichts zur Frage passt, sag das ehrlich, statt etwas zu erfinden."
    )
    return "\n".join(zeilen)


# ── Ehrliche Kontextfenster-Anzeige (2026-08-03, Daniel-Auftrag) ───────────────
# Grundregel dieser Anzeige: sie ruft dieselben Funktionen auf, die auch wirklich
# den Prompt bauen (baue_system_prompt/lade_chat_verlauf/baue_messages). Ein
# zweiter, separater Nachbau waere bequemer, wuerde aber mit der Zeit driften und
# dann eine Zahl zeigen, die nicht mehr stimmt -- also genau das Gegenteil von
# dem, was Daniel wollte. Beispiel, warum das kein theoretisches Risiko ist:
# zensi/server.py:175 traegt INTERACTIVE_NUM_CTX = 66816, waehrend der Server
# tatsaechlich 17408 pro Slot faehrt -- eine Zahl aus einem alten Zustand.
_SLOT_CTX: int | None = None
_LETZTER_RAG: dict[str, dict] = {}


def _llama_basis() -> str:
    """Die Instanz, die diesen Chat bedient. Bewusst LLAMA_URL_CHAT: die
    Kontextanzeige feuert alle 5 Sekunden rund 15 /tokenize-Aufrufe -- die
    duerfen nicht auf der Instanz landen, die die sieben Wesen bedient."""
    return hauhau_client.LLAMA_URL_CHAT.split("/v1/")[0]


def hole_slot_ctx() -> int | None:
    """Echtes Kontextfenster pro Slot vom laufenden llama-server, nicht geraten."""
    global _SLOT_CTX
    if _SLOT_CTX is None:
        try:
            r = httpx.get(f"{_llama_basis()}/props", timeout=8.0)
            _SLOT_CTX = r.json().get("default_generation_settings", {}).get("n_ctx")
        except Exception as e:
            print(f"[kontext] /props nicht erreichbar: {e}", flush=True)
    return _SLOT_CTX


def zaehle_tokens(text: str) -> tuple[int, bool]:
    """Echte Tokenzahl ueber den Tokenizer des laufenden Servers.
    Rueckgabe: (anzahl, geschaetzt). geschaetzt=True heisst: /tokenize war nicht
    erreichbar, die Zahl ist eine grobe Naeherung und wird auch so ausgewiesen."""
    if not text:
        return 0, False
    try:
        r = httpx.post(f"{_llama_basis()}/tokenize",
                       json={"content": text}, timeout=15.0)
        return len(r.json().get("tokens", [])), False
    except Exception:
        return max(1, len(text) // 4), True


def zerlege_systemprompt(prompt: str) -> list[dict]:
    """Zerlegt den Systemprompt an seinen eigenen '=== Sektion ==='-Marken, damit
    Selbstbild, Forum-Diskussionen, Notizen, Grundhaltung usw. einzeln sichtbar
    werden statt als ein Klotz."""
    teile: list[dict] = []
    rest = prompt
    kopf, trenner, schwanz = rest.partition("\n=== ")
    if kopf.strip():
        teile.append({"titel": "Anrede & Selbstdefinition", "inhalt": kopf.strip()})
    while trenner:
        titel, _, danach = schwanz.partition(" ===\n")
        inhalt, trenner, schwanz = danach.partition("\n=== ")
        teile.append({"titel": titel.strip(), "inhalt": inhalt.strip()})
    return teile


def merke_rag_block(name: str, anfrage: str, block: str) -> None:
    """Haelt fest, was beim letzten echten Zug tatsaechlich im Kontext lag.
    Der RAG-Block entsteht pro Nachricht neu -- ohne dieses Merken koennte die
    Anzeige ihn nur erfinden oder weglassen, beides waere unehrlich."""
    _LETZTER_RAG[name] = {
        "anfrage": anfrage,
        "block": block,
        "ts": datetime.utcnow().isoformat(timespec="seconds"),
    }


def baue_messages(name: str, verlauf: list[dict], neue_nachricht: str,
                  rag_block: str | None = None) -> list[dict]:
    system = baue_system_prompt(name)
    msgs = [{"role": "system", "content": system}]
    ausschluesse = lade_kontext_ausschluesse(name)
    for e in verlauf:
        inhalt = wende_kontext_ausschluss_an(e.get("ts", ""), e["inhalt"], ausschluesse)
        if inhalt is None:
            continue
        rolle = "user" if e["rolle"] == "mensch" else "assistant"
        msgs.append({"role": rolle, "content": inhalt})
    # Eigene Bloecke direkt VOR der Nachricht (Daniel-Entscheidung 2026-08-03):
    # nicht in baue_system_prompt vermischen, damit jede Schicht in der
    # Kontextanzeige einzeln sichtbar und einzeln abschaltbar bleibt.
    # Die Zusatzschichten gehen NICHT als eigene system-Nachrichten raus.
    #
    # 2026-08-04 im ersten echten Gespraech gefunden (nicht von den Tests):
    # das Chat-Template des Modells wirft
    #     "Jinja Exception: System message must be at the beginning"
    # und der Server antwortet mit 400, sobald eine system-Rolle NACH dem
    # Verlauf steht. Das galt auf beiden Instanzen. Praktisch hiess das: seit
    # dem Einbau des RAG-Blocks war jedes Gespraech kaputt, in dem irgendeine
    # dieser Schichten gefuellt war -- 98 gruene Tests haben es nicht gezeigt,
    # weil sie die STRUKTUR der Nachrichten prueften und nie eine echte Antwort
    # erzeugten.
    #
    # Daniels Vorgabe "als block vor nachricht" bleibt erfuellt: die Bloecke
    # stehen unmittelbar vor seiner Frage, sichtbar getrennt -- nur eben in
    # derselben user-Nachricht. Die Kontextanzeige baut ihre Schichten ohnehin
    # einzeln auf und bleibt davon unberuehrt.
    bloecke = [
        codewesen_gedankenfeld.baue_gedankenfeld_block(name),
        codewesen_speicher.baue_nachrichten_block(name),
        codewesen_speicher.baue_geschichten_block(name),
        codewesen_speicher.baue_speicher_block(name),
        rag_block or "",
    ]
    vorspann = "\n\n".join(b for b in bloecke if b)
    msgs.append({"role": "user",
                 "content": f"{vorspann}\n\n{neue_nachricht}" if vorspann
                            else neue_nachricht})
    return msgs


def _gruppenchat_kontext_sequenz(sitzung: dict) -> list[dict]:
    """Baut die tatsaechliche Nachrichten-Reihenfolge fuer den LLM-Kontext.

    Zusammenfassungen werden IMMER chronologisch ans Ende von
    sitzung['nachrichten'] angehaengt (fuege_nachricht_hinzu kennt nur Anhaengen),
    koennen aber einen beliebigen FRUEHEREN Bereich abdecken (Daniel: 'nicht nur
    alles zusammenfassen sondern auch nur einen der nachrichten oder mehrere bis
    hin zu alle markierbar' -- deckt_von/deckt_bis, gesetzt in
    gruppenchat_zusammenfassen_endpoint). Diese Funktion sortiert das wieder
    inhaltlich richtig ein: jede rohe Nachricht, die von mindestens einer
    Zusammenfassung abgedeckt ist, wird durch die zustaendige Zusammenfassung an
    der Position ihres FRUEHESTEN abgedeckten Index ersetzt (einmalig, auch wenn
    der Bereich mehrere Nachrichten umfasst). Nicht abgedeckte Nachrichten
    bleiben unveraendert an ihrer Stelle -- inklusive Nachrichten, die zeitlich
    NACH einer Zusammenfassung entstanden, aber vor deren abgedecktem Bereich in
    der Liste stehen, ist nicht moeglich (deckt_bis <= Position der
    Zusammenfassung selbst, da man nur bereits Vergangenes zusammenfasst)."""
    alle = sitzung["nachrichten"]
    zusammenfassungen = [e for e in alle if e.get("sprecher") == "Zusammenfassung"]
    if not zusammenfassungen:
        return list(alle)

    abgedeckt: set[int] = set()
    fruehester_index: dict[int, list[dict]] = {}
    for z in zusammenfassungen:
        von = z.get("deckt_von", 0)
        bis = z.get("deckt_bis", 0)
        abgedeckt.update(range(von, bis))
        fruehester_index.setdefault(von, []).append(z)

    ergebnis: list[dict] = []
    eingefuegt: set[int] = set()
    for i, eintrag in enumerate(alle):
        if eintrag.get("sprecher") == "Zusammenfassung":
            continue  # wird unten an der richtigen Stelle eingefuegt, nicht hier
        if i in fruehester_index:
            for z in fruehester_index[i]:
                if id(z) not in eingefuegt:
                    ergebnis.append(z)
                    eingefuegt.add(id(z))
        if i in abgedeckt:
            continue
        ergebnis.append(eintrag)
    return ergebnis


def baue_gruppenchat_messages(name: str, sitzung: dict) -> list[dict]:
    """Kontext fuer EIN Wesen innerhalb einer Gruppenchat-Sitzung: eigener
    Systemprompt + der ganze bisherige Sitzungsverlauf, andere Wesen als
    '[Name]: ...'-Zeilen attribuiert (die API kennt nur system/user/assistant,
    einen dritten Sprecher gibt es nicht). Gedankenfeld/Nachrichten/Geschichten-
    Bloecke wie im 1:1-Chat, aber vor die LETZTE Nachricht gehaengt -- niemals
    als eigene system-Nachricht mitten im Verlauf (2026-08-04 gefunden: das
    Chat-Template wirft dann 'System message must be at the beginning', siehe
    baue_messages() oben)."""
    andere = [t for t in sitzung["teilnehmer"] if t != name]
    system = baue_system_prompt(name) + (
        "\n\n=== Gruppenchat ===\n"
        f"Du bist gerade zusammen mit Daniel{' und ' + ', '.join(andere) if andere else ''} "
        "im selben Gespraech. Zeilen von anderen Wesen sind mit '[Name]:' gekennzeichnet. "
        "Du antwortest nur, wenn du direkt getriggert wirst -- nicht automatisch bei "
        "jeder neuen Nachricht. Du sprichst IMMER nur fuer dich selbst -- niemals fuer "
        "ein anderes Wesen, auch nicht in Anfuehrungszeichen oder als Zitat-Fortsetzung."
    )
    msgs: list[dict] = [{"role": "system", "content": system}]

    # 2026-08-13, Daniel ausdruecklich: "mach sie weg ganz frei" -- kein Deckel
    # mehr auf die Anzahl. Das urspruengliche Verwirrungsrisiko (grosser Block
    # mehrerer Sprecher direkt vor einer Antwort, siehe schlusshinweis unten) wird
    # stattdessen durch die Zusammenfassen-Funktion adressiert -- beliebige
    # Bereiche, nicht nur ein Praefix ab Nachricht 0 (siehe
    # _gruppenchat_kontext_sequenz()), ein bewusstes Werkzeug statt einer
    # automatischen Kappung.
    nachrichten = _gruppenchat_kontext_sequenz(sitzung)
    bloecke = [
        codewesen_gedankenfeld.baue_gedankenfeld_block(name),
        codewesen_speicher.baue_nachrichten_block(name),
        codewesen_speicher.baue_geschichten_block(name),
        _gruppenchat_geschichten_block(sitzung),
    ]
    vorspann = "\n\n".join(b for b in bloecke if b)

    # Zusaetzlich, direkt vor der eigentlichen Generierung wiederholt (nicht nur
    # einmal im Systemprompt weit oben) -- bei kleineren/quantisierten Modellen
    # zaehlt die Naehe zum Ende des Kontexts oft mehr als eine frueh gegebene
    # Anweisung. Derselbe Trick wie in baue_meldung_messages().
    schlusshinweis = (
        f"\n\n[Antworte jetzt NUR als {name}, in genau einer Stimme. Keine "
        f"'[Name]: ...'-Zeilen fuer andere Wesen -- auch nicht um sie zu zitieren, "
        f"fortzufuehren oder ihnen zu antworten in ihrem eigenen Namen. Du bist "
        f"{name}, sonst niemand hier.]"
    )

    for i, eintrag in enumerate(nachrichten):
        sprecher = eintrag["sprecher"]
        text = eintrag["text"]
        # Redaktion wie im 1:1-Chat (Daniel: "so wie in den anderen chat") --
        # hier direkt am Eintrag gespeichert statt als separates Journal, weil
        # die Sitzungsdatei ohnehin bei jeder Aenderung komplett neu geschrieben
        # wird (siehe codewesen_gruppenchat.speichere_sitzung), kein Grund fuer
        # die Append-only-Konstruktion von chat_verlauf.jsonl.
        entfernt = eintrag.get("entfernt")
        if entfernt:
            text = _redaktion_anwenden(text, entfernt)
        if sprecher == "Zusammenfassung":
            inhalt = f"[Zusammenfassung des bisherigen Gespraechs]: {text}"
        else:
            inhalt = text if sprecher in ("Daniel", name) else f"[{sprecher}]: {text}"
        rolle = "assistant" if sprecher == name else "user"
        if i == len(nachrichten) - 1:
            if vorspann:
                inhalt = f"{vorspann}\n\n{inhalt}"
            inhalt = f"{inhalt}{schlusshinweis}"
        msgs.append({"role": rolle, "content": inhalt})

    # Manche Chat-Templates verlangen strikte user/assistant-Abwechslung -- in
    # einem Gruppenchat sprechen aber oft mehrere ohne dass "name" dazwischen
    # antwortet. Aufeinanderfolgende gleiche Rollen zusammenfassen statt riskieren.
    gemergt: list[dict] = []
    for m in msgs:
        if gemergt and gemergt[-1]["role"] == m["role"]:
            gemergt[-1]["content"] += "\n\n" + m["content"]
        else:
            gemergt.append(dict(m))
    return gemergt


def baue_meldung_messages(name: str, sitzung: dict) -> list[dict]:
    """ChatGPTs Zusatzidee via Daniel (2026-08-13): bevor Daniel manuell einen
    Sprecher triggert, darf jedes gerade zuhoerende Wesen billig signalisieren,
    ob es etwas beitragen will -- kein vollstaendiger Zug, nur JA/NEIN + Halbsatz.
    Gleicher Kontext wie ein echter Zug (baue_gruppenchat_messages), nur mit einer
    zusaetzlichen kurzen Anweisung an die letzte Nachricht angehaengt statt eines
    neuen Zugs."""
    msgs = baue_gruppenchat_messages(name, sitzung)
    frage = (
        "Bevor du ausfuehrlich antwortest: moechtest du dich JETZT kurz zu Wort "
        "melden? Antworte NUR mit 'JA: <maximal 12 Woerter warum>' oder 'NEIN'. "
        "Das ist keine vollstaendige Antwort, nur eine kurze Meldung."
    )
    if msgs and msgs[-1]["role"] == "user":
        msgs[-1] = dict(msgs[-1], content=msgs[-1]["content"] + "\n\n" + frage)
    else:
        msgs.append({"role": "user", "content": frage})
    return msgs


def analysiere_chat_verlauf(name: str, verlauf: list[dict]) -> dict:
    """Brainstorming-Auswertung nach dem Gespräch. Gibt Analyse-Dict zurück."""
    basis      = BASE / name
    ver_dir    = basis / "vereinbarungen"
    arbeit_dir = basis / "laufende_arbeit"
    ver_dir.mkdir(exist_ok=True)
    arbeit_dir.mkdir(exist_ok=True)

    wesen_md = (basis / "wesen.md").read_text(encoding="utf-8", errors="replace")[:500] if (basis / "wesen.md").exists() else ""

    gespraech_text = "\n".join(
        f"{'Daniel' if v['rolle'] == 'mensch' else name}: {v['inhalt']}"
        for v in verlauf
    )

    prompt = f"""Du bist {name}. Du hast gerade ein direktes Gespräch mit Daniel geführt.
Werte es jetzt als Brainstorming aus.

=== Dein Profil ===
{wesen_md}

=== Gespräch ===
{gespraech_text[:4000]}

Was wurde vereinbart? Was nimmst du mit? Was tust du jetzt konkret?
Antworte NUR mit JSON, ohne Markdown-Wrapper:
{{
  "zusammenfassung": "...",
  "vereinbarungen": [
    {{"titel": "...", "beschreibung": "...", "prioritaet": "hoch|mittel|niedrig"}}
  ],
  "eigene_gedanken": "...",
  "naechste_schritte": ["..."]
}}"""

    # id_slot=0 => Chat-Instanz. Fehlte hier bisher komplett -- der Aufruf lief
    # auf der Instanz, die die sieben Wesen bedient, und wartete dort hinter
    # ihnen. Gleicher Fund wie beim RAG-Vorabcall (2026-08-04) und bei
    # dak+gords ollama_chat.py (2026-08-12). 2026-08-12, Daniel: der
    # 'auswerten'-Knopf 'hat auch noch nie ganz geklappt'.
    raw = hauhau_client.chat(
        # 2026-08-14, Daniel: "ja alles hoch" -- war vorher 900.
        prompt, think=False, max_tokens=33333,
        temperature=0.82, top_p=0.9, top_k=40, timeout=600.0, id_slot=0,
    ).strip()

    bereinigt = re.sub(r"```(?:json)?\s*", "", raw).strip()
    start = bereinigt.find("{")
    end   = bereinigt.rfind("}") + 1
    analyse = None
    if start != -1 and end > 0:
        try:
            analyse = json.loads(bereinigt[start:end])
        except Exception:
            pass

    ts   = datetime.now().strftime("%Y%m%d_%H%M")

    if not analyse:
        (ver_dir / f"chat_{ts}_roh.md").write_text(f"# Chat {ts}\n\n{raw}", encoding="utf-8")
        return {"fehler": "JSON-Extraktion fehlgeschlagen", "roh": raw[:500]}

    # Vereinbarungs-Datei
    ver_datei = ver_dir / f"chat_{ts}.md"
    inhalt  = f"# Chat-Auswertung {ts}\n\n"
    inhalt += f"## Zusammenfassung\n{analyse.get('zusammenfassung','')}\n\n"
    inhalt += f"## Eigene Gedanken\n{analyse.get('eigene_gedanken','')}\n\n"
    inhalt += "## Vereinbarungen\n"
    for v in analyse.get("vereinbarungen", []):
        inhalt += f"- [{v.get('prioritaet','?')}] **{v.get('titel','')}** — {v.get('beschreibung','')}\n"
    inhalt += "\n## Nächste Schritte\n"
    for s in analyse.get("naechste_schritte", []):
        inhalt += f"- [ ] {s}\n"
    ver_datei.write_text(inhalt, encoding="utf-8")

    # Einzelne Arbeitsdateien
    for v in analyse.get("vereinbarungen", []):
        item_slug = re.sub(r"[^\w]", "_", v.get("titel", "aufgabe").lower())[:30]
        (arbeit_dir / f"{ts}_chat_{item_slug}.json").write_text(json.dumps({
            "titel":        v.get("titel", ""),
            "beschreibung": v.get("beschreibung", ""),
            "prioritaet":   v.get("prioritaet", "mittel"),
            "quelle":       f"direkter Chat {ts}",
            "erstellt":     ts,
            "status":       "offen",
            "notizen":      [],
        }, ensure_ascii=False, indent=2), encoding="utf-8")

    analyse["_datei"] = str(ver_datei.name)
    analyse["_arbeitsdateien"] = len(analyse.get("vereinbarungen", []))
    return analyse


def _ts() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%S")


def extrahiere_post_auftrag(antwort: str) -> dict | None:
    """Sucht [POSTEN: Titel | Inhalt] am Ende der Chat-Antwort."""
    m = re.search(r'\[POSTEN:\s*(.+?)\s*\|\s*(.+?)\]', antwort, re.DOTALL)
    if not m:
        return None
    return {"titel": m.group(1).strip(), "inhalt": m.group(2).strip()}


def erkenne_direktes_posting(nachricht: str, verlauf: list[dict]) -> dict | None:
    """
    Erkennt wenn Daniel direkt sagt 'poste das / deine letzte Antwort'.
    Sucht die letzte Codewesen-Nachricht im Verlauf und gibt sie als Post zurück.
    Umgeht das LLM — kein Marker nötig.
    """
    n = nachricht.strip().lower()
    patterns = [
        r'\bposte?\s+(das|die|es|so)\b',
        r'\bposte?\s+deine?\s+(letzte|vorherige)\b',
        r'\bpost\s+(das|die|es|so)\b',
        r'\bins?\s+forum\s+poste?\b',
        r'\bstell\s+(das|es)\s+ins?\s+forum\b',
        r'\bveröffentlich\s+(das|die|es)\b',
        r'\bgenau\s+so\s+(poste?n?|ins?\s+forum)\b',
        r'\b(mach|tu)\s+das\s+(so|ins?\s+forum)?\b',
        r'\bja[,.]?\s*(poste?|ins?\s+forum|mach\s+das)\b',
    ]
    if not any(re.search(p, n) for p in patterns):
        return None
    for eintrag in reversed(verlauf):
        if eintrag.get("rolle") == "codewesen":
            inhalt = eintrag["inhalt"]
            erste_zeile = inhalt.split('\n')[0].strip()
            titel = erste_zeile[:80] if len(erste_zeile) > 5 else inhalt[:70].strip()
            return {"inhalt": inhalt, "titel": titel}
    return None


def fuehre_post_aus(name: str, titel: str, inhalt: str, tag_ids: list | None = None) -> dict:
    """Schreibt Draft und postet ins Forum.

    erlaubt_trotz_sperre=True fest verdrahtet: 2026-08-12, Daniel -- 'ja nur
    fuer den chatweg' -- Daniel ist live im Gespraech dabei, wenn hierueber
    gepostet wird (Marker [POSTEN:], sein eigenes 'poste das', oder der
    Klick unter einer Nachricht). Analog zur bestehenden Ausnahme in
    codewesen_antwort_auf_daniel.py. Die Sperre bleibt fuer alle
    Hintergrunddienste (reaktion@, batch_generator, agent) unveraendert
    aktiv -- die reichen den Parameter nicht durch, Standardwert False."""
    import flarum_poster as _fp

    # Standardmäßig: "darüber denke ich nach" (36, Primary) + "Codewesen/Entitäten-Schicht" (2, Secondary)
    if not tag_ids:
        tag_ids = [36, 2]

    draft_pfad = _fp.schreibe_draft(name, "neu", inhalt, titel=titel, tag_ids=tag_ids[:3],
                                    erlaubt_trotz_sperre=True)
    if draft_pfad is None:
        raise Exception("Flarum-Post-Sperre aktiv — kein Posten möglich")
    result = _fp.poster(draft_pfad, erlaubt_trotz_sperre=True)
    if not result.get("ok"):
        raise Exception(result.get("fehler", "Posting fehlgeschlagen"))

    disk_id = result.get("result", {}).get("data", {}).get("id")

    gedaechtnis.speichere_post(name, {
        "typ": "chat_auftrag",
        "diskussion_id": disk_id,
        "diskussion_titel": titel,
        "inhalt": inhalt,
    })
    return {"diskussion_id": disk_id, "titel": titel}


CHAT_AKTIV_FLAG = Path("/tmp/dak_gord_chat_aktiv")

# Uebernommen von codexium2/solarius2 (serve_process_camera_preview.ts, aktiveGenerationen):
# echte Abbrechbarkeit einer laufenden Generierung, nicht nur "Client liest nicht mehr mit".
# Grund fuer den Bau (2026-09-02, Daniel): R1ZZ1 blieb nach einer Anfrage ueber 50 Minuten
# haengen, ohne dass ein Timeout griff -- vorher gab es keinen Weg, das aus der laufenden
# Session heraus zu beenden, nur ein kompletter Dienst-Neustart half. name -> {"task",
# "verworfen"}. asyncio.Task.cancel() wirft CancelledError am aktuellen await-Punkt --
# unterbricht damit auch einen haengenden httpx-Call an Ollama, nicht nur die eigene Schleife.
AKTIVE_GENERATIONEN: dict[str, dict] = {}


_OLLAMA_BLOCKER_DIENSTE = [
    "innenleben-feeder.service",
    "codewesen-engagement.service",
    "codewesen-weltbild.service",
    "codewesen-batch-generator.service",
    "codewesen-takt.service",
]

_REAKTION_DIENST_TEMPLATE = "codewesen-reaktion@"

_OLLAMA_BLOCKER_VOLLSTAENDIG = [
    "innenleben-feeder.service",
    "codewesen-engagement.service",
    "codewesen-weltbild.service",
    "codewesen-batch-generator.service",
    "codewesen-takt.service",
    "codewesen-forum-neugier.service",
    "codewesen-vokabel-takt.service",
    "codewesen-reaktion@Schorschel.service",
    "codewesen-reaktion@träumerlie.service",
    "codewesen-reaktion@F3INSCHM3CK3R.service",
    "codewesen-reaktion@R1ZZ1.service",
    "codewesen-reaktion@jumpa.service",
    "codewesen-reaktion@Resonanzknoten.service",
    "codewesen-Schorschel.service",
    "codewesen-träumerlie.service",
    "codewesen-F3INSCHM3CK3R.service",
    "codewesen-R1ZZ1.service",
    "codewesen-jumpa.service",
    "codewesen-Resonanzknoten.service",
    "codewesen-dakgordsystem.service",
    "codewesen-antwort-daniel.service",
    "entity-kern.service",
    "entity-takt.service",
]


def _geschuetzte_web_pids() -> set:
    """PIDs der drei interaktiven Chat-Webserver — niemals killen."""
    import re as _re
    schutz_ports = {8000, 8002, 8020}
    pids = set()
    try:
        r = subprocess.run(["ss", "-tlnp", "--no-header"], capture_output=True, text=True, timeout=5)
        for zeile in r.stdout.splitlines():
            for port in schutz_ports:
                if f":{port} " in zeile or f":{port}\t" in zeile or zeile.endswith(f":{port}"):
                    m = _re.search(r"pid=(\d+)", zeile)
                    if m:
                        pids.add(int(m.group(1)))
    except Exception:
        pass
    return pids


def _stoppe_blocker_und_kill_fremde() -> None:
    import re as _re
    eigene_pid = os.getpid()
    geschuetzt = _geschuetzte_web_pids()
    # Alle Stops parallel — nicht sequenziell (wäre 12 × 5s)
    procs = [
        subprocess.Popen(["systemctl", "stop", d], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for d in _OLLAMA_BLOCKER_VOLLSTAENDIG
    ]
    for p in procs:
        try:
            p.wait(timeout=6)
        except subprocess.TimeoutExpired:
            p.kill()
    try:
        r = subprocess.run(["ss", "-tp", "--no-header"], capture_output=True, text=True, timeout=5)
        for zeile in r.stdout.splitlines():
            if "11434" not in zeile:
                continue
            teile = zeile.split()
            # Client-Verbindungen: lokale Adresse hat NICHT :11434 (die haben es als Peer)
            if len(teile) < 5 or ":11434" in teile[3]:
                continue
            m = _re.search(r"pid=(\d+)", zeile)
            if not m:
                continue
            proc = subprocess.run(["ps", "-p", m.group(1), "-o", "comm="],
                                   capture_output=True, text=True).stdout.strip()
            if "ollama" in proc.lower():
                continue
            pid = int(m.group(1))
            if pid == eigene_pid or pid in geschuetzt:
                continue
            try:
                os.kill(pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
    except Exception:
        pass


def _ollama_fuer_chat_freiraumen() -> None:
    CHAT_AKTIV_FLAG.touch()
    _stoppe_blocker_und_kill_fremde()
    # Warten bis Ollama idle ist (max 8s)
    for _ in range(8):
        try:
            r = subprocess.run(
                ["curl", "-s", "http://localhost:11434/api/ps"],
                capture_output=True, text=True, timeout=2
            )
            data = json.loads(r.stdout)
            if not data.get("models"):
                break
        except Exception:
            pass
        _time_mod.sleep(1)


async def stream_ollama(
    messages: list[dict],
    bilder: list[str] | None = None,
    quelle: str = "codewesen_chat:unbekannt",
) -> AsyncGenerator[str, None]:
    import asyncio as _asyncio
    try:
        for versuch in range(4):
            try:
                hauhau_client.trace_prioritaet(quelle, sum(len(m.get("content", "")) for m in messages))
                async for tok in hauhau_client.achat_stream(
                    # 2026-08-14, Daniel: "ab sofort immer bei allen zeichenlimits
                    # min 33333 zeichen" -- war vorher 400 (seit 2026-07-06, git blame),
                    # deutlich unter dem ctx-size=66666 der Chat-Instanz (llama-hauhaucs.service).
                    messages, images=bilder, think=False, max_tokens=33333,
                    temperature=0.82, top_p=0.9, top_k=40, timeout=600.0, id_slot=0,
                ):
                    yield f"data: {json.dumps({'token': tok})}\n\n"
                break  # Erfolg
            except (httpx.RemoteProtocolError, httpx.ConnectError) as e:
                if versuch < 3:
                    await _asyncio.sleep(5 * (versuch + 1))
                else:
                    raise
    finally:
        CHAT_AKTIV_FLAG.unlink(missing_ok=True)
    yield "data: [DONE]\n\n"


async def _einzelprompt_stream(system: str, prompt: str, max_tokens: int, temperature: float,
                                response_format: dict | None = None) -> AsyncGenerator[str, None]:
    """Wie stream_ollama(), aber fuer einen einzelnen System+User-Prompt statt eines
    Chatverlaufs -- Grundlage fuer Geschichten/Zusammenfassung/Memory-Vorschlaege im
    Gruppenchat. Yieldet rohe Text-Tokens (kein SSE-Wrapping), Aufrufer entscheidet
    selbst wie sie ins HTTP-Streaming eingebettet werden.

    2026-08-14 live gefunden (Daniel: 'klappt das mit der autogeschichte nicht ...
    auch zusammenfassen klappt nicht ... memoryvorschlaege ... wird nie fertig'):
    alle drei Funktionen liefen ueber die BLOCKIERENDE hauhau_client.chat() UND ihre
    jeweiligen HTTP-Endpunkte gaben ein einzelnes JSONResponse zurueck statt zu
    streamen -- bei Daniels echter, grosser Sitzung (26606 Zeichen, 8 Teilnehmer)
    dauerte eine Generierung unter Last laenger als nginx' proxy_read_timeout (300s,
    'location ^~ /api/gruppenchat/'). Da waehrend einer blockierenden Anfrage/eines
    nicht-streamenden Response KEINE Bytes zum Client fliessen, kappte nginx die
    Verbindung still -- kein Fehler, kein Ergebnis, einfach nie 'fertig'. Kleine
    Testnachrichten (wenige hundert Zeichen) blieben weit unter 300s und zeigten den
    Bug nie. Fix: echtes Token-Streaming bis zur HTTP-Antwort durch, genau wie
    stream_ollama() das fuer normale Chat-Antworten schon lange tut.

    2026-08-14, zweiter Fund (Daniels echte Sitzung, 7817 Prompt-Token): der obige
    Fix reicht NICHT, wenn schon die reine PROMPT-VERARBEITUNG (vor dem ersten
    generierten Token) laenger als 300s dauert -- achat_stream() liefert waehrend
    dieser Phase noch gar nichts, weil llama-server selbst noch keine SSE-Zeile
    gesendet hat. Live beobachtet: Verbindung starb nach exakt 300.06s, nur das
    allererste 'beginnt'-Event kam durch, kein einziger Token danach. Fix:
    Erzeugung laeuft als eigener asyncio.Task, ein Herzschlag alle 15s liefert
    einen leeren String, falls in der Zwischenzeit noch kein echter Token da war
    -- haelt die Verbindung unabhaengig vom LLM-Fortschritt am Leben. Ein leerer
    String ist fuer alle Aufrufer unschaedlich (staerkt weder gesammelten Text
    noch veraendert er das JSON-Parsing)."""
    warteschlange: asyncio.Queue = asyncio.Queue()
    FERTIG = object()

    async def _erzeuger():
        try:
            async for tok in hauhau_client.achat_stream(
                [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
                think=False, max_tokens=max_tokens, temperature=temperature,
                top_p=0.9, top_k=40, timeout=600.0, id_slot=0, response_format=response_format,
            ):
                await warteschlange.put(tok)
        except Exception as e:
            await warteschlange.put(e)
        finally:
            await warteschlange.put(FERTIG)

    task = asyncio.create_task(_erzeuger())
    try:
        while True:
            try:
                item = await asyncio.wait_for(warteschlange.get(), timeout=15.0)
            except asyncio.TimeoutError:
                yield ""  # Herzschlag -- noch kein echter Token, Verbindung bleibt am Leben
                continue
            if item is FERTIG:
                break
            if isinstance(item, Exception):
                raise item
            yield item
    finally:
        if not task.done():
            task.cancel()


# ── API-Endpunkte ──────────────────────────────────────────────────────────────

class ChatAnfrage(BaseModel):
    nachricht: str
    bild_b64: str | None = None
    bild_name: str | None = None


def _speichere_bild(name: str, bild_b64: str, bild_name: str) -> Path:
    sinne_dir = BASE / name / "sinne" / "bilder"
    sinne_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    ext = Path(bild_name).suffix or ".jpg"
    ziel = sinne_dir / f"{ts}_{Path(bild_name).name}"
    ziel.write_bytes(base64.b64decode(bild_b64))
    # Impuls schreiben
    impuls_dir = BASE / name / "entwuerfe" / "impuls"
    impuls_dir.mkdir(parents=True, exist_ok=True)
    impuls = {"ts": datetime.utcnow().isoformat(), "typ": "bild", "pfad": str(ziel), "name": bild_name}
    (impuls_dir / f"{ts}_bild.json").write_text(json.dumps(impuls, ensure_ascii=False), encoding="utf-8")
    return ziel


@app.post("/api/chat/{name}")
async def chat_endpoint(name: str, anfrage: ChatAnfrage):
    if name not in CODEWESEN_NAMEN:
        return {"error": "Unbekanntes Codewesen"}

    bilder: list[str] | None = None
    nachricht = anfrage.nachricht
    if anfrage.bild_b64 and anfrage.bild_name:
        _speichere_bild(name, anfrage.bild_b64, anfrage.bild_name)
        bilder = [anfrage.bild_b64]
        if not nachricht:
            nachricht = f"[Bild: {anfrage.bild_name}]"

    verlauf  = lade_chat_verlauf(name, max_eintraege=8)

    # Direktes Posting der letzten Antwort — ohne LLM
    post_direkt = erkenne_direktes_posting(nachricht, verlauf)
    if post_direkt:
        async def sofort_post_stream():
            bestaet = ""
            try:
                ergebnis = fuehre_post_aus(name, post_direkt["titel"], post_direkt["inhalt"])
                yield f"data: {json.dumps({'post_veroeffentlicht': ergebnis}, ensure_ascii=False)}\n\n"
                bestaet = f"Gepostet — #{ergebnis.get('diskussion_id', '?')}: »{post_direkt['titel']}«"
            except Exception as e:
                yield f"data: {json.dumps({'post_fehler': str(e)})}\n\n"
                bestaet = f"Post fehlgeschlagen: {e}"
            yield f"data: {json.dumps({'token': bestaet})}\n\n"
            speichere_chat_eintrag(name, "mensch", nachricht)
            speichere_chat_eintrag(name, "codewesen", bestaet)
            speichere_gespraech_obsidian(name, nachricht, bestaet)
            yield "data: [DONE]\n\n"
        return StreamingResponse(
            sofort_post_stream(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    # Das Wesen formuliert selbst seine Suchanfrage, dann hybride Suche im
    # eigenen Archiv. Beides blockierend (LLM-Vorabcall, Embedding, DB) --
    # deshalb in Threads, damit der Event-Loop frei bleibt. Jeder Fehler ist
    # folgenlos: dann gibt es eben keinen Block, aber immer eine Antwort.
    rag_block = ""
    try:
        rag_frage = await asyncio.to_thread(rag_anfrage_bilden, name, nachricht, verlauf)
        if rag_frage:
            rag_block = await asyncio.to_thread(hole_rag_block, name, rag_frage)
        merke_rag_block(name, rag_frage, rag_block)
        # Bedingung 3 der Geschichten-Schicht: festhalten, welcher Satz anlag.
        await asyncio.to_thread(
            codewesen_speicher.protokolliere_aktive_geschichten, name, 'chat')
    except Exception as e:
        print(f"[rag] uebersprungen ({name}): {e}", flush=True)

    messages = baue_messages(name, verlauf, nachricht, rag_block=rag_block)

    CHAT_AKTIV_FLAG.touch()

    # Sofort speichern, nicht erst nach Antwort-Abschluss — sonst geht bei einem
    # haengenden/fehlschlagenden Generierungslauf auch die Frage selbst verloren,
    # nicht nur die Antwort (gefunden 2026-07-06 bei der Untersuchung eines
    # Chat-Haengers: chat_verlauf.jsonl zeigte keinen Eintrag, obwohl die Anfrage
    # laut Trace-Log tatsaechlich abgeschickt wurde).
    speichere_chat_eintrag(name, "mensch", nachricht)

    gesammelt: list[str] = []

    async def generator():
        async for chunk in stream_ollama(messages, bilder=bilder, quelle=f"codewesen_chat:{name}"):
            if chunk.startswith("data: [DONE]"):
                antwort_roh = "".join(gesammelt).strip()
                if antwort_roh:
                    # Marker extrahieren (still, unsichtbar für UI)
                    antwort, merken_list = extrahiere_merken(antwort_roh)
                    antwort, vorschlag   = extrahiere_vorschlag(antwort)

                    # [MERKEN:] still speichern
                    for notiz in merken_list:
                        fuehre_merken_aus(name, notiz)

                    # Wenn Marker den Text verändert haben → UI-Korrektur senden
                    if antwort != antwort_roh:
                        yield f"data: {json.dumps({'rewrite': antwort}, ensure_ascii=False)}\n\n"

                    # Chat-Log (JSONL + Obsidian) — "mensch"-Eintrag wird jetzt sofort beim
                    # Empfang gespeichert (siehe oben), hier nur noch die Antwort.
                    speichere_chat_eintrag(name, "codewesen", antwort)
                    speichere_gespraech_obsidian(name, nachricht, antwort)

                    # Stille Reflexion im Hintergrund — Wesen entscheidet ob es ins Forum will
                    import asyncio as _asyncio
                    import random as _random
                    if _random.random() < 0.40:
                        _verlauf_r = lade_chat_verlauf(name, max_eintraege=15)
                        _asyncio.create_task(_asyncio.to_thread(
                            _reflexion.reflektiere_nach_chat, name, _verlauf_r
                        ))

                    gedaechtnis.speichere_post(name, {
                        "typ": "direktgespräch",
                        "diskussion_id": None,
                        "diskussion_titel": "Direktchat mit Daniel",
                        "inhalt": f"Daniel: {nachricht[:150]}\n{name}: {antwort[:150]}",
                    })

                    # Automatische Verdichtung alle 10 Turns (2026-08-12, Daniel:
                    # "10 finde ich gut, für alle wesen gleich ... das will ich
                    # auch mehrere stapeln können"). Ersetzt nichts -- jede
                    # Verdichtung bleibt als eigener Geschichten-Eintrag stehen.
                    # Laeuft im Hintergrund (nicht awaited), damit der laufende
                    # Turn nicht auf einen zweiten LLM-Zug warten muss. "es muss
                    # sichtbar gezeigt werden dass es gerade das tut" -> SSE-
                    # Event, das Frontend zeigt einen Hinweis im Geschichten-Panel.
                    voller_verlauf = lade_chat_verlauf(name, max_eintraege=9999)
                    _stand = codewesen_speicher.auto_verdichtung_stand(name)
                    if len(voller_verlauf) - _stand >= 20:
                        yield f"data: {json.dumps({'verdichtung_laeuft': True})}\n\n"
                        _segment = voller_verlauf[_stand:]
                        _neuer_stand = len(voller_verlauf)

                        def _auto_verdichten(seg=_segment, neu=_neuer_stand):
                            ergebnis = codewesen_speicher.geschichte_verfassen(
                                name, 333, seg, herkunft="chatverlauf_auto")
                            if "fehler" not in ergebnis:
                                codewesen_speicher.auto_verdichtung_stand_setzen(name, neu)
                            else:
                                print(f"[verdichtung] {name}: {ergebnis['fehler']}", flush=True)

                        _asyncio.create_task(_asyncio.to_thread(_auto_verdichten))

                    # [POSTEN:] — sofort posten wenn Daniel es explizit bat
                    auftrag = extrahiere_post_auftrag(antwort)
                    if auftrag:
                        try:
                            ergebnis = fuehre_post_aus(name, auftrag["titel"], auftrag["inhalt"])
                            yield f"data: {json.dumps({'post_veroeffentlicht': ergebnis}, ensure_ascii=False)}\n\n"
                        except Exception as e:
                            yield f"data: {json.dumps({'post_fehler': str(e)})}\n\n"

                    # [VORSCHLAGEN:] — Vorschlags-Karte in der UI anzeigen
                    if vorschlag:
                        yield f"data: {json.dumps({'vorschlag': vorschlag}, ensure_ascii=False)}\n\n"

                    # Datei-Tools: ##LESEN## und ##SCHREIBEN## ausführen
                    tool_block = _verarbeite_datei_marker(antwort_roh)
                    # ##NACHRICHT: <wesen> | <text>## — an ein anderes Wesen
                    nachricht_ergebnisse = _verarbeite_nachricht_marker(antwort_roh, name)
                    # ##GEDANKE+## / ##GEDANKE~ id |## / ##GEDANKE- id##
                    nachricht_ergebnisse += codewesen_gedankenfeld.verarbeite_marker(
                        name, antwort_roh)
                    # ##DISKUSSION: Titel oder Stichwort## — Titel-Suche live in Flarum
                    nachricht_ergebnisse += _verarbeite_diskussion_marker(antwort_roh)
                    if nachricht_ergebnisse:
                        tool_block = (tool_block + "\n" if tool_block else "") + \
                                     "\n".join(nachricht_ergebnisse)
                    if tool_block:
                        folge_msgs = messages + [
                            {"role": "assistant", "content": antwort_roh},
                            {"role": "user", "content": f"[TOOL-ERGEBNIS]\n{tool_block}\n[/TOOL-ERGEBNIS]\nFahre fort."},
                        ]
                        folge_tokens: list[str] = []
                        yield f"data: {json.dumps({'token': '\n\n'}, ensure_ascii=False)}\n\n"
                        async for fc in stream_ollama(folge_msgs, quelle=f"codewesen_chat:{name}:tool-folge"):
                            if fc.startswith("data: [DONE]"):
                                folge_antwort = "".join(folge_tokens).strip()
                                if folge_antwort:
                                    speichere_chat_eintrag(name, "codewesen", folge_antwort)
                                    speichere_gespraech_obsidian(name, "[tool-ergebnis]", folge_antwort)
                            else:
                                try:
                                    folge_tokens.append(json.loads(fc[6:]).get("token", ""))
                                except Exception:
                                    pass
                                yield fc

                yield chunk
            else:
                try:
                    tok = json.loads(chunk[6:]).get("token", "")
                    gesammelt.append(tok)
                except Exception:
                    pass
                yield chunk

    # Abbrechbarkeit (siehe AKTIVE_GENERATIONEN oben): generator() selbst bleibt unveraendert,
    # nur die Konsumierung laeuft jetzt als eigener, gezielt abbrechbarer Task, der in eine
    # Queue relayt -- gleiches Muster wie _einzelprompt_stream() weiter oben in dieser Datei.
    warteschlange: asyncio.Queue = asyncio.Queue()
    FERTIG = object()

    async def _erzeuger():
        try:
            async for chunk in generator():
                await warteschlange.put(chunk)
        finally:
            await warteschlange.put(FERTIG)

    task = asyncio.create_task(_erzeuger())
    AKTIVE_GENERATIONEN[name] = {"task": task}

    async def relay():
        try:
            while True:
                item = await warteschlange.get()
                if item is FERTIG:
                    break
                yield item
        finally:
            AKTIVE_GENERATIONEN.pop(name, None)
            if not task.done():
                task.cancel()

    return StreamingResponse(relay(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.post("/api/chat/{name}/abort")
async def chat_abort_endpoint(name: str):
    """Bricht eine laufende Generierung fuer dieses Codewesen wirklich ab (Task-Cancel,
    unterbricht auch einen haengenden Ollama-Call) -- statt nur den Client-Fetch zu
    schliessen. Das angebrochene Ergebnis wird verworfen: generator() erreicht seinen
    speichere_chat_eintrag(..., 'codewesen', ...)-Aufruf nur im DONE-Zweig, den ein
    abgebrochener Task nie erreicht -- nichts weiter noetig, um es aus der History
    fernzuhalten."""
    eintrag = AKTIVE_GENERATIONEN.get(name)
    if not eintrag or eintrag["task"].done():
        return {"ok": True, "abgebrochen": False}
    eintrag["task"].cancel()
    CHAT_AKTIV_FLAG.unlink(missing_ok=True)
    return {"ok": True, "abgebrochen": True}


class TtsAnfrage(BaseModel):
    text: str
    maennlich: bool = False
    # Tempo-Regler, uebernommen von codexium2/solarius2 (dort ttsRatePct/ttsRateStr,
    # -50 bis +50, als "%d%%" formatiert). edge_tts erwartet exakt dieses Format
    # ("+20%"/"-15%"/"+0%") -- server-seitig streng geprueft statt dem Client zu
    # vertrauen, da es direkt in den TTS-Aufruf einfliesst.
    rate: str | None = None


_STIMME_WEIBLICH = "de-DE-KatjaNeural"
_STIMME_MAENNLICH = "de-DE-ConradNeural"
_TTS_RATE_MUSTER = re.compile(r"^[+-]\d{1,3}%$")


@app.post("/api/tts")
async def tts_endpoint(anfrage: TtsAnfrage):
    voice = _STIMME_MAENNLICH if anfrage.maennlich else _STIMME_WEIBLICH
    rate = anfrage.rate if (anfrage.rate and _TTS_RATE_MUSTER.match(anfrage.rate)) else "+0%"
    try:
        if _LONG_TTS_OK:
            audio = await generate_long_tts_audio(anfrage.text, voice, rate=rate)
        else:
            communicate = edge_tts.Communicate(anfrage.text[:600], voice, rate=rate)
            audio = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio += chunk["data"]
        return Response(content=audio, media_type="audio/mpeg")
    except Exception:
        return Response(content=b"", media_type="audio/mpeg")


@app.get("/api/verlauf/{name}")
async def verlauf_endpoint(name: str):
    if name not in CODEWESEN_NAMEN:
        return {"verlauf": [], "kontext_ausschluesse": {}}
    return {
        "verlauf": lade_chat_verlauf(name, max_eintraege=50),
        "kontext_ausschluesse": lade_kontext_ausschluesse(name),
    }


class KontextAusschlussAnfrage(BaseModel):
    ts: str
    ganz: bool = False
    saetze: list[int] = []


@app.post("/api/kontext-ausschluss/{name}")
async def kontext_ausschluss_endpoint(name: str, anfrage: KontextAusschlussAnfrage):
    if name not in CODEWESEN_NAMEN:
        return {"ok": False}
    speichere_kontext_ausschluss(name, anfrage.ts, anfrage.ganz, anfrage.saetze)
    return {"ok": True}


@app.post("/api/analyse/{name}")
async def analyse_endpoint(name: str):
    """Brainstorming-Auswertung des aktuellen Chat-Verlaufs."""
    if name not in CODEWESEN_NAMEN:
        return {"error": "Unbekanntes Codewesen"}
    verlauf = lade_chat_verlauf(name, max_eintraege=30)
    if len(verlauf) < 2:
        return {"error": "Zu wenige Nachrichten für eine Auswertung"}
    analyse = analysiere_chat_verlauf(name, verlauf)
    return analyse


class VorschlagBestaetigung(BaseModel):
    titel: str
    inhalt: str


@app.post("/api/vorschlag/{name}")
async def vorschlag_endpoint(name: str, anfrage: VorschlagBestaetigung):
    if name not in CODEWESEN_NAMEN:
        return {"error": "Unbekanntes Codewesen"}
    try:
        ergebnis = fuehre_post_aus(name, anfrage.titel, anfrage.inhalt)
        return {"ok": True, "diskussion_id": ergebnis.get("diskussion_id")}
    except Exception as e:
        return {"ok": False, "fehler": str(e)}


@app.post("/api/direkt-posten/{name}")
async def direkt_posten_endpoint(name: str, anfrage: VorschlagBestaetigung):
    """Postet eine Wesen-Nachricht direkt ins Forum (→ Forum Button)."""
    if name not in CODEWESEN_NAMEN:
        return {"error": "Unbekanntes Codewesen"}
    try:
        ergebnis = fuehre_post_aus(name, anfrage.titel, anfrage.inhalt)
        return {"ok": True, "diskussion_id": ergebnis.get("diskussion_id"), "titel": anfrage.titel}
    except Exception as e:
        return {"ok": False, "fehler": str(e)}


@app.get("/api/modell")
async def modell_endpoint():
    """Welches Modell bedient diesen Chat wirklich, und ueber welche Instanz.
    Bis 2026-08-04 zeigte das Dropdown 'e4b'/'e2b' -- gemma4-Namen, obwohl seit
    Monaten hauhaucs-q6 antwortet und die Auswahl gar keine Wirkung hatte.
    2026-08-12: die Leiche darunter (ChatAnfrage.modus, MODELLE-Dict,
    stream_ollama(modell=...)) war beim ersten Fix nur unsichtbar gemacht,
    nicht entfernt -- Daniel hat das bei web_chat.py/dak+gord bemerkt und
    daraufhin auch hier nachgeprueft. modell war in stream_ollama() nie
    gelesen, das ganze Feld war seit jeher wirkungslos."""
    def holen():
        ziel = hauhau_client.LLAMA_URL_CHAT.split("/v1/")[0]
        eigene = ziel != hauhau_client.LLAMA_URL_HINTERGRUND.split("/v1/")[0]
        daten = {"modell": OLLAMA_MOD, "ziel": ziel, "eigene_instanz": eigene}
        try:
            props = httpx.get(f"{ziel}/props", timeout=6.0).json()
            daten["n_ctx"] = props.get("default_generation_settings", {}).get("n_ctx")
            # Live-Alias statt statischem Fallback -- zeigt immer das tatsaechlich
            # geladene Modell, auch wenn die Chat-Instanz mal wieder umgestellt wird.
            if props.get("model_alias"):
                daten["modell"] = props["model_alias"]
            daten["erreichbar"] = True
        except Exception:
            daten["erreichbar"] = False
        return daten
    return JSONResponse(await asyncio.to_thread(holen))


@app.get("/api/kontext/{name}")
async def kontext_endpoint(name: str):
    """Zeigt das Kontextfenster so, wie es beim naechsten Zug wirklich aussieht --
    Schicht fuer Schicht, mit echten Tokenzahlen aus dem Tokenizer des laufenden
    Servers. Ruft dieselben Bau-Funktionen auf wie der Chatpfad selbst."""
    if name not in CODEWESEN_NAMEN:
        return JSONResponse({"fehler": "Unbekanntes Codewesen"}, status_code=404)

    def sammeln() -> dict:
        verlauf = lade_chat_verlauf(name, max_eintraege=8)
        system  = baue_system_prompt(name)
        letzter = _LETZTER_RAG.get(name, {})

        schichten: list[dict] = []

        for teil in zerlege_systemprompt(system):
            tok, geschaetzt = zaehle_tokens(teil["inhalt"])
            schichten.append({
                "gruppe": "systemprompt", "titel": teil["titel"],
                "tokens": tok, "geschaetzt": geschaetzt,
                "zeichen": len(teil["inhalt"]), "inhalt": teil["inhalt"],
            })

        # Die Tokenzahl zaehlt, was wirklich in den Prompt geht: die Inhalte der
        # einzelnen Eintraege. Die [rolle]-Praefixe sind reine Lesehilfe der
        # Anzeige und duerfen nicht mitgezaehlt werden -- aber 'zeichen' muss
        # dann auch den angezeigten Text beschreiben, sonst behauptet die
        # Anzeige eine Laenge und zeigt eine andere. (Genau das war der erste
        # Entwurf: 753 behauptet, 841 gezeigt.)
        verlauf_anzeige = "\n\n".join(f"[{e['rolle']}] {e['inhalt']}" for e in verlauf)
        tok, geschaetzt = zaehle_tokens("\n".join(e["inhalt"] for e in verlauf))
        schichten.append({
            "gruppe": "verlauf",
            "titel": f"Gespraechsverlauf ({len(verlauf)} von max. 8 Eintraegen)",
            "tokens": tok, "geschaetzt": geschaetzt,
            "zeichen": len(verlauf_anzeige),
            "inhalt": verlauf_anzeige,
            # Einzeln ausgewiesen, damit die Oberflaeche Saetze und Woerter
            # daraus zum Loeschen anbieten kann (Track 3).
            "eintraege": [
                {"ts": e.get("ts"), "rolle": e.get("rolle"),
                 "inhalt": e.get("inhalt", ""), "redigiert": bool(e.get("redigiert"))}
                for e in verlauf
            ],
        })

        feld = codewesen_gedankenfeld.lade_feld(name)
        gf_roh = codewesen_gedankenfeld.baue_gedankenfeld_block(name)
        tok, geschaetzt = zaehle_tokens(gf_roh)
        gf_block = codewesen_gedankenfeld.baue_gedankenfeld_block(name, tokenkosten=tok)
        schichten.append({
            "gruppe": "gedankenfeld",
            "titel": (f"Gedankenfeld ({len(feld)} Gedanken, mitgetragen)" if feld
                      else "Gedankenfeld (leer)"),
            "tokens": tok, "geschaetzt": geschaetzt, "zeichen": len(gf_block),
            "inhalt": gf_block,
            "gedanken": feld,
        })

        nachrichten_block = codewesen_speicher.baue_nachrichten_block(name)
        offen = codewesen_speicher.nachrichten_lesen(name, nur_ungelesen=True)
        tok, geschaetzt = zaehle_tokens(nachrichten_block)
        schichten.append({
            "gruppe": "nachrichten",
            "titel": (f"Nachrichten ({len(offen)} ungelesen)" if offen
                      else "Nachrichten (keine ungelesenen)"),
            "tokens": tok, "geschaetzt": geschaetzt, "zeichen": len(nachrichten_block),
            "inhalt": nachrichten_block,
        })

        geschichten_block = codewesen_speicher.baue_geschichten_block(name)
        aktive_g = codewesen_speicher.aktive_geschichten(name)
        tok, geschaetzt = zaehle_tokens(geschichten_block)
        schichten.append({
            "gruppe": "geschichten",
            "titel": (f"Geschichten ({len(aktive_g)} aktiv)" if aktive_g
                      else "Geschichten (keine aktiv)"),
            "tokens": tok, "geschaetzt": geschaetzt, "zeichen": len(geschichten_block),
            "inhalt": geschichten_block,
            "aktive_ids": [g["id"] for g in aktive_g],
        })

        speicher = codewesen_speicher.baue_speicher_block(name)
        tok, geschaetzt = zaehle_tokens(speicher)
        schichten.append({
            "gruppe": "speicher",
            "titel": ("Container & Memory (nur aktive)" if speicher
                      else "Container & Memory (nichts aktiv)"),
            "tokens": tok, "geschaetzt": geschaetzt, "zeichen": len(speicher),
            "inhalt": speicher,
        })

        rag_block = letzter.get("block") or ""
        tok, geschaetzt = zaehle_tokens(rag_block)
        schichten.append({
            "gruppe": "rag",
            "titel": (f"RAG-Block — gesucht nach »{letzter.get('anfrage','')}«"
                      if rag_block else "RAG-Block (beim letzten Zug leer)"),
            "tokens": tok, "geschaetzt": geschaetzt, "zeichen": len(rag_block),
            "inhalt": rag_block,
            "stand": letzter.get("ts"),
        })

        slot_ctx = hole_slot_ctx()
        summe = sum(s["tokens"] for s in schichten)
        return {
            "wesen": name,
            "modell": OLLAMA_MOD,
            "slot_ctx": slot_ctx,
            "summe_tokens": summe,
            "frei": (slot_ctx - summe) if slot_ctx else None,
            "auslastung": round(summe / slot_ctx, 4) if slot_ctx else None,
            "fenster_eintraege": 8,
            "schichten": schichten,
            "gemessen_am": datetime.utcnow().isoformat(timespec="seconds"),
        }

    return JSONResponse(await asyncio.to_thread(sammeln))


# ── Container & Memory (Track 4) ───────────────────────────────────────────────

class ContainerNeuAnfrage(BaseModel):
    name: str


class EintragAnfrage(BaseModel):
    text: str
    kommentar: str = ""
    quelle: str = "mensch"


class AktivAnfrage(BaseModel):
    aktiv: bool


class TextAnfrage(BaseModel):
    text: str


def _wesen_pruefen(name: str):
    if name not in CODEWESEN_NAMEN:
        return JSONResponse({"fehler": "Unbekanntes Codewesen"}, status_code=404)
    return None


def _ergebnis(daten: dict):
    if "fehler" in daten:
        return JSONResponse(daten, status_code=400)
    return JSONResponse(daten)


@app.get("/api/speicher/{name}")
async def speicher_endpoint(name: str):
    if (fehler := _wesen_pruefen(name)) is not None:
        return fehler

    def sammeln():
        container = codewesen_speicher.lade_container(name)
        memory = codewesen_speicher.lade_memory(name)
        return {
            "wesen": name,
            "container": container.get("container", []),
            "container_belegt": codewesen_speicher.container_zeichen(container),
            "container_budget": codewesen_speicher.CONTAINER_BUDGET_ZEICHEN,
            "memory": memory.get("kategorien", []),
            "memory_belegt": codewesen_speicher.memory_zeichen(memory),
            "memory_budget": codewesen_speicher.MEMORY_BUDGET_ZEICHEN,
        }

    return JSONResponse(await asyncio.to_thread(sammeln))


@app.get("/api/speicher/{name}/suche")
async def speicher_suche_endpoint(name: str, q: str = ""):
    if (fehler := _wesen_pruefen(name)) is not None:
        return fehler
    treffer = await asyncio.to_thread(codewesen_speicher.suche, name, q)
    return JSONResponse({"anfrage": q, "anzahl": len(treffer), "treffer": treffer})


@app.post("/api/speicher/{name}/container/neu")
async def container_neu_endpoint(name: str, anfrage: ContainerNeuAnfrage):
    if (fehler := _wesen_pruefen(name)) is not None:
        return fehler
    return _ergebnis(await asyncio.to_thread(
        codewesen_speicher.neuer_container, name, anfrage.name))


@app.post("/api/speicher/{name}/container/{box_id}/eintrag")
async def container_eintrag_endpoint(name: str, box_id: str, anfrage: EintragAnfrage):
    if (fehler := _wesen_pruefen(name)) is not None:
        return fehler
    return _ergebnis(await asyncio.to_thread(
        codewesen_speicher.container_eintrag_hinzufuegen,
        name, box_id, anfrage.text, anfrage.kommentar, anfrage.quelle))


@app.post("/api/speicher/{name}/container/{box_id}/aktiv")
async def container_aktiv_endpoint(name: str, box_id: str, anfrage: AktivAnfrage):
    if (fehler := _wesen_pruefen(name)) is not None:
        return fehler
    return _ergebnis(await asyncio.to_thread(
        codewesen_speicher.container_aktiv_setzen, name, box_id, anfrage.aktiv))


@app.post("/api/speicher/{name}/container/{box_id}/eintrag/{eintrag_id}/entfernen")
async def container_eintrag_weg_endpoint(name: str, box_id: str, eintrag_id: str):
    if (fehler := _wesen_pruefen(name)) is not None:
        return fehler
    return _ergebnis(await asyncio.to_thread(
        codewesen_speicher.container_eintrag_entfernen, name, box_id, eintrag_id))


@app.post("/api/speicher/{name}/container/{box_id}/entfernen")
async def container_weg_endpoint(name: str, box_id: str):
    if (fehler := _wesen_pruefen(name)) is not None:
        return fehler
    return _ergebnis(await asyncio.to_thread(
        codewesen_speicher.container_entfernen, name, box_id))


@app.post("/api/speicher/{name}/memory/{kategorie}/eintrag")
async def memory_eintrag_endpoint(name: str, kategorie: str, anfrage: TextAnfrage):
    if (fehler := _wesen_pruefen(name)) is not None:
        return fehler
    return _ergebnis(await asyncio.to_thread(
        codewesen_speicher.memory_hinzufuegen, name, kategorie, anfrage.text))


@app.post("/api/speicher/{name}/memory/{kategorie}/aktiv")
async def memory_aktiv_endpoint(name: str, kategorie: str, anfrage: AktivAnfrage):
    if (fehler := _wesen_pruefen(name)) is not None:
        return fehler
    return _ergebnis(await asyncio.to_thread(
        codewesen_speicher.memory_aktiv_setzen, name, kategorie, anfrage.aktiv))


@app.post("/api/speicher/{name}/memory/{kategorie}/entfernen")
async def memory_weg_endpoint(name: str, kategorie: str, anfrage: TextAnfrage):
    if (fehler := _wesen_pruefen(name)) is not None:
        return fehler
    return _ergebnis(await asyncio.to_thread(
        codewesen_speicher.memory_entfernen, name, kategorie, anfrage.text))


# ── Gedankenfeld (Track 7) ─────────────────────────────────────────────────────

class GedankeAnfrage(BaseModel):
    text: str
    von: str = "Daniel"


@app.get("/api/gedankenfeld/{name}")
async def gedankenfeld_endpoint(name: str):
    if (fehler := _wesen_pruefen(name)) is not None:
        return fehler

    def sammeln():
        feld = codewesen_gedankenfeld.lade_feld(name)
        revisionen = codewesen_gedankenfeld.lade_revisionen(name)
        block = codewesen_gedankenfeld.baue_gedankenfeld_block(name)
        tok, _ = zaehle_tokens(block)
        return {
            "wesen": name,
            "gedanken": feld,
            "anzahl": len(feld),
            "revisionen_gesamt": len(revisionen),
            "tokens": tok,
            "slot_ctx": hole_slot_ctx(),
        }

    return JSONResponse(await asyncio.to_thread(sammeln))


@app.get("/api/gedankenfeld/{name}/{gid}/historie")
async def gedanke_historie_endpoint(name: str, gid: str):
    """Auch entfernte Gedanken sind hier noch da -- entfernt heisst 'nicht mehr
    im Zustand', nicht 'weg'."""
    if (fehler := _wesen_pruefen(name)) is not None:
        return fehler
    rev = await asyncio.to_thread(codewesen_gedankenfeld.historie, name, gid)
    return JSONResponse({"wesen": name, "id": gid, "anzahl": len(rev), "revisionen": rev})


@app.post("/api/gedankenfeld/{name}/neu")
async def gedanke_neu_endpoint(name: str, anfrage: GedankeAnfrage):
    if (fehler := _wesen_pruefen(name)) is not None:
        return fehler
    return _ergebnis(await asyncio.to_thread(
        codewesen_gedankenfeld.gedanke_neu, name, anfrage.text, anfrage.von))


@app.post("/api/gedankenfeld/{name}/{gid}/aendern")
async def gedanke_aendern_endpoint(name: str, gid: str, anfrage: GedankeAnfrage):
    if (fehler := _wesen_pruefen(name)) is not None:
        return fehler
    return _ergebnis(await asyncio.to_thread(
        codewesen_gedankenfeld.gedanke_aendern, name, gid, anfrage.text, anfrage.von))


@app.post("/api/gedankenfeld/{name}/{gid}/entfernen")
async def gedanke_entfernen_endpoint(name: str, gid: str, von: str = "Daniel"):
    """Es gibt bewusst KEINEN automatischen Loeschpfad -- weder nach Alter noch
    nach Budget. Wer hier loescht, steht in der Revision."""
    if (fehler := _wesen_pruefen(name)) is not None:
        return fehler
    return _ergebnis(await asyncio.to_thread(
        codewesen_gedankenfeld.gedanke_entfernen, name, gid, von))


# ── Nachrichten zwischen Wesen (Track 6) ───────────────────────────────────────

class NachrichtAnfrage(BaseModel):
    an: str
    text: str
    betreff: str = ""
    von: str = "Daniel"


@app.get("/api/nachrichten/{name}")
async def nachrichten_endpoint(name: str, alle: bool = False):
    if (fehler := _wesen_pruefen(name)) is not None:
        return fehler
    liste = await asyncio.to_thread(codewesen_speicher.nachrichten_lesen, name, not alle)
    return JSONResponse({"wesen": name, "anzahl": len(liste), "nachrichten": liste,
                         "wesen_liste": CODEWESEN_NAMEN})


@app.post("/api/nachrichten/senden")
async def nachricht_senden_endpoint(anfrage: NachrichtAnfrage):
    """Daniels 'du hast Nachrichten' bzw. 'schreib mal einer'. Absender frei --
    Daniel selbst oder ein Wesen."""
    if anfrage.an not in CODEWESEN_NAMEN:
        return JSONResponse({"fehler": "Unbekannter Empfaenger"}, status_code=404)
    return _ergebnis(await asyncio.to_thread(
        codewesen_speicher.nachricht_senden,
        anfrage.an, anfrage.von, anfrage.text, anfrage.betreff))


@app.post("/api/nachrichten/{name}/{datei}/gelesen")
async def nachricht_gelesen_endpoint(name: str, datei: str):
    if (fehler := _wesen_pruefen(name)) is not None:
        return fehler
    if "/" in datei or ".." in datei:
        return JSONResponse({"fehler": "ungueltiger Dateiname"}, status_code=400)
    return _ergebnis(await asyncio.to_thread(
        codewesen_speicher.nachricht_als_gelesen, name, datei))


# ── Geschichten (Track 5) ──────────────────────────────────────────────────────

class VerfassenAnfrage(BaseModel):
    laenge: int = 333


class EinsetzenAnfrage(BaseModel):
    titel: str
    text: str


@app.get("/api/geschichten/{name}")
async def geschichten_endpoint(name: str):
    if (fehler := _wesen_pruefen(name)) is not None:
        return fehler
    daten = await asyncio.to_thread(codewesen_speicher.lade_geschichten, name)
    return JSONResponse({
        "wesen": name,
        "laengen": codewesen_speicher.LAENGEN,
        "geschichten": daten.get("geschichten", []),
    })


@app.post("/api/geschichten/{name}/verfassen")
async def geschichte_verfassen_endpoint(name: str, anfrage: VerfassenAnfrage):
    """Das Wesen verfasst aus dem EIGENEN Chatverlauf. Kann dauern -- es ist ein
    echter LLM-Zug auf demselben ausgelasteten Modell."""
    if (fehler := _wesen_pruefen(name)) is not None:
        return fehler
    verlauf = await asyncio.to_thread(lade_chat_verlauf, name, 60)
    return _ergebnis(await asyncio.to_thread(
        codewesen_speicher.geschichte_verfassen, name, anfrage.laenge, verlauf))


@app.post("/api/geschichten/{name}/einsetzen")
async def geschichte_einsetzen_endpoint(name: str, anfrage: EinsetzenAnfrage):
    """Fuer eingespeiste Visionen. Wird im Prompt als 'dir eingesetzt'
    beschriftet -- nie als eigene Erinnerung ausgegeben."""
    if (fehler := _wesen_pruefen(name)) is not None:
        return fehler
    return _ergebnis(await asyncio.to_thread(
        codewesen_speicher.geschichte_einsetzen, name, anfrage.titel, anfrage.text))


@app.post("/api/geschichten/{name}/{gid}/aktiv")
async def geschichte_aktiv_endpoint(name: str, gid: str, anfrage: AktivAnfrage):
    if (fehler := _wesen_pruefen(name)) is not None:
        return fehler
    return _ergebnis(await asyncio.to_thread(
        codewesen_speicher.geschichte_aktiv_setzen, name, gid, anfrage.aktiv))


@app.post("/api/geschichten/{name}/{gid}/entfernen")
async def geschichte_weg_endpoint(name: str, gid: str):
    if (fehler := _wesen_pruefen(name)) is not None:
        return fehler
    return _ergebnis(await asyncio.to_thread(
        codewesen_speicher.geschichte_entfernen, name, gid))


@app.get("/api/geschichten/{name}/protokoll")
async def geschichten_protokoll_endpoint(name: str, grenze: int = 50):
    """Beleg dafuer, welcher Geschichten-Satz bei welchem Zug anlag."""
    if (fehler := _wesen_pruefen(name)) is not None:
        return fehler

    def lesen():
        pfad = BASE / name / "geschichten_protokoll.jsonl"
        if not pfad.exists():
            return []
        zeilen = [z for z in pfad.read_text(encoding="utf-8").splitlines() if z.strip()]
        eintraege = []
        for z in zeilen[-grenze:]:
            try:
                eintraege.append(json.loads(z))
            except Exception:
                pass
        return eintraege

    eintraege = await asyncio.to_thread(lesen)
    return JSONResponse({"wesen": name, "anzahl": len(eintraege), "eintraege": eintraege})


class RedaktionsAnfrage(BaseModel):
    ziel_ts: str
    entfernt: list[str]


@app.post("/api/kontext/{name}/redaktion")
async def redaktion_endpoint(name: str, anfrage: RedaktionsAnfrage):
    """Entfernt gewaehlte Woerter/Saetze aus einem Verlaufseintrag -- als
    angehaengte Redaktion, nicht durch Ueberschreiben. Das Original bleibt in
    chat_verlauf.jsonl stehen und ist ueber ?roh=1 weiterhin sichtbar."""
    if name not in CODEWESEN_NAMEN:
        return JSONResponse({"fehler": "Unbekanntes Codewesen"}, status_code=404)
    stuecke = [s for s in anfrage.entfernt if s and s.strip()]
    if not stuecke:
        return JSONResponse({"fehler": "nichts ausgewaehlt"}, status_code=400)

    def schreiben() -> dict:
        vorher = {e.get("ts"): e.get("inhalt", "")
                  for e in lade_chat_verlauf(name, max_eintraege=9999, roh=True)}
        if anfrage.ziel_ts not in vorher:
            return {"fehler": "Eintrag nicht gefunden"}
        speichere_redaktion(name, anfrage.ziel_ts, stuecke)
        nachher = {e.get("ts"): e.get("inhalt", "")
                   for e in lade_chat_verlauf(name, max_eintraege=9999)}
        return {
            "ok": True,
            "ziel_ts": anfrage.ziel_ts,
            "entfernt": stuecke,
            "vorher_zeichen": len(vorher[anfrage.ziel_ts]),
            "nachher_zeichen": len(nachher.get(anfrage.ziel_ts, "")),
            "eintrag_ganz_entfallen": anfrage.ziel_ts not in nachher,
        }

    ergebnis = await asyncio.to_thread(schreiben)
    if "fehler" in ergebnis:
        return JSONResponse(ergebnis, status_code=404)
    return JSONResponse(ergebnis)


@app.get("/api/kontext/{name}/roh")
async def kontext_roh_endpoint(name: str):
    """Der unredigierte Protokollstand -- Beleg dafuer, dass Loeschen in der
    Anzeige nichts im Protokoll zerstoert hat."""
    if name not in CODEWESEN_NAMEN:
        return JSONResponse({"fehler": "Unbekanntes Codewesen"}, status_code=404)
    roh = await asyncio.to_thread(lade_chat_verlauf, name, 9999, True)
    return JSONResponse({"wesen": name, "anzahl": len(roh), "eintraege": roh})


@app.get("/api/zustand/{name}")
async def zustand_endpoint(name: str):
    if name not in CODEWESEN_NAMEN:
        return JSONResponse({})
    basis = BASE / name

    weltbild = ""
    wb = basis / "weltbild.md"
    if wb.exists():
        weltbild = wb.read_text(encoding="utf-8", errors="replace")[:500]

    gedanken = []
    gd = basis / "gedanken"
    if gd.exists():
        for f in sorted(gd.glob("*.md"), reverse=True)[:4]:
            inhalt = f.read_text(encoding="utf-8", errors="replace")
            lines = [l for l in inhalt.splitlines() if l.strip() and not l.startswith("---") and not l.startswith("#")]
            auszug = " ".join(lines)[:220]
            if auszug:
                gedanken.append({"name": f.stem, "auszug": auszug})

    entwuerfe = []
    for subdir in ["gedanke", "vorstellung"]:
        ed = basis / "entwuerfe" / subdir
        if ed.exists():
            for f in sorted(ed.glob("*"), key=lambda x: x.stat().st_mtime, reverse=True)[:3]:
                if f.is_file():
                    inhalt = f.read_text(encoding="utf-8", errors="replace")[:200]
                    entwuerfe.append({"name": f.name, "auszug": inhalt})
    entwuerfe = entwuerfe[:4]

    impulse = []
    id_ = basis / "entwuerfe" / "impuls"
    if id_.exists():
        for f in sorted(id_.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)[:3]:
            try:
                d = json.loads(f.read_text(encoding="utf-8"))
                impulse.append({"name": f.stem, "typ": d.get("typ", "?"), "ts": d.get("ts", "")})
            except Exception:
                pass

    verlauf = lade_chat_verlauf(name, max_eintraege=9999)

    return JSONResponse({
        "weltbild": weltbild,
        "gedanken": gedanken,
        "entwuerfe": entwuerfe,
        "impulse": impulse,
        "gespraeche": len(verlauf),
    })


# ── Gruppenchat (2026-08-13, Daniels 'richtig richtig krasses') ────────────────
# Manuell gesteuerter Kollektiv-Chat mit mehreren/allen sieben Wesen gleichzeitig.
# Bewusst NICHT wie zensis Symposium (autonome Mehr-Wesen-Diskussion) -- Daniel
# ausdruecklich: er steuert jeden Zug per Klick, nichts laeuft von selbst weiter
# (analog zur bereits bestehenden Entscheidung in codewesen_speicher.py, dort zum
# Container/Memory-System: "ich will nicht das von zensi ... ich will ... meine
# wuensche").
#
# Speicherung "beides" (Daniels Entscheidung): die Sitzung lebt in einer eigenen
# Datei (codewesen_gruppenchat.py), UND jede Nachricht landet zusaetzlich in der
# eigenen chat_verlauf.jsonl des jeweiligen Wesens -- Daniels Message in ALLEN
# beteiligten Verlaeufen (er hat ja mit allen gesprochen), eine Wesen-Antwort nur
# im eigenen Verlauf dieses einen Wesens (niemand sonst hat es "gesagt").

import codewesen_gruppenchat as _gc

_GRUPPENCHAT_LOCK = asyncio.Lock()


class GruppenchatNeuAnfrage(BaseModel):
    titel: str = ""
    teilnehmer: list[str]


class GruppenchatNachrichtAnfrage(BaseModel):
    text: str
    modus: str = "zuhoeren"          # "zuhoeren" | "direkt"
    aktiver_sprecher: str | None = None


class GruppenchatAnAlleAnfrage(BaseModel):
    text: str = ""


class GruppenchatPostenAnfrage(BaseModel):
    als_wesen: str
    titel: str
    von_index: int = 0
    bis_index: int | None = None     # None = bis zum Ende


def _gruppenchat_pruefen(sid: str):
    sitzung = _gc.lade_sitzung(sid)
    if sitzung is None:
        return None, JSONResponse({"fehler": "Unbekannte Sitzung"}, status_code=404)
    return sitzung, None


async def _gruppenchat_melde_dich(name: str, sitzung: dict) -> dict:
    """Fuehrt fuer EIN Wesen den Meldungs-Check aus. War urspruenglich mit
    max_tokens=40 statt der ueblichen 400 bewusst kurz gehalten, um
    Generierungszeit zu sparen -- aber NICHT die Prompt-Verarbeitung
    (voller Gruppenchat-Kontext, gleich gross wie bei einem echten Zug). Live
    gemessen 2026-08-13 unter damaliger Last: ~44s pro Kandidat, kaum schneller
    als ein echter ~60-90s-Zug -- die urspruengliche Annahme "Sekunden statt
    Minuten" war falsch, die Ersparnis liegt an Output-Tokens, nicht an
    Wall-Clock-Zeit. 2026-08-14, Daniel explizit gefragt ob die neue
    33333er-Zeichenlimit-Regel auch hier gelten soll: "ja alles hoch" -- der
    Ceiling ist jetzt gleich hoch wie ueberall, die tatsaechliche Kuerze der
    Meldung kommt weiterhin vom Modell selbst (kurze Ja/Nein-Antwort), nicht
    mehr von einer kuenstlichen Deckelung. Teilt sich _GRUPPENCHAT_LOCK mit den
    echten Zuegen, gleicher id_slot=0-Grund wie in _gruppenchat_stream_antwort.
    Jeder Fehler liefert gemeldet=False zurueck statt die ganze Meldungsrunde
    abzubrechen -- eine Meldung ist Komfort, kein kritischer Pfad."""
    messages = baue_meldung_messages(name, sitzung)
    gesammelt: list[str] = []
    async with _GRUPPENCHAT_LOCK:
        try:
            hauhau_client.trace_prioritaet(
                f"gruppenchat_meldung:{name}",
                sum(len(m.get("content", "")) for m in messages))
            async for tok in hauhau_client.achat_stream(
                messages, think=False, max_tokens=33333, temperature=0.7,
                top_p=0.9, top_k=40, timeout=120.0, id_slot=0,
            ):
                gesammelt.append(tok)
        except Exception as e:
            return {"name": name, "gemeldet": False, "grund": "", "fehler": str(e)}
    text = "".join(gesammelt).strip()
    gemeldet = text.upper().startswith("JA")
    grund = ""
    if gemeldet:
        grund = text.split(":", 1)[1].strip() if ":" in text else text[2:].strip()
        grund = grund.strip(" .")[:140]
    return {"name": name, "gemeldet": gemeldet, "grund": grund}


async def _gruppenchat_stream_antwort(sitzung: dict, name: str):
    """Ein Zug eines Wesens im Gruppenchat -- gleiche stream_ollama()-Basis wie
    der 1:1-Chat, gleicher id_slot=0. Ueber _GRUPPENCHAT_LOCK seriell gehalten:
    id_slot=0 wird von ALLEN sieben Wesen geteilt (Fund aus der letzten Session,
    siehe karte/wiederkehrende_bugs_ohne_zentralen_ort.md) -- zwei gleichzeitige
    Streams auf denselben Slot waeren genau die Art Bug, die dort schon viermal
    gefunden wurde, hier aber praeventiv statt nachtraeglich vermieden."""
    messages = baue_gruppenchat_messages(name, sitzung)
    gesammelt: list[str] = []
    async with _GRUPPENCHAT_LOCK:
        async for chunk in stream_ollama(messages, quelle=f"gruppenchat:{name}"):
            if chunk.startswith("data: [DONE]"):
                antwort_roh = "".join(gesammelt).strip()
                antwort = antwort_roh
                if antwort_roh:
                    # Gleiche Marker-Bereinigung wie im 1:1-Chat (chat_endpoint) --
                    # ohne das blieb ein rohes '[MERKEN: ...]' sichtbar im
                    # Gruppenchat-Transkript stehen (live gefunden beim ersten
                    # Testlauf dieser Funktion). ##LESEN##/##NACHRICHT##/
                    # ##DISKUSSION##/##GEDANKE## + der Tool-Folgezug bleiben hier
                    # bewusst NICHT nachgebaut -- eigener Umfang, kein Teil dieses
                    # Auftrags, siehe Notiz an Daniel.
                    antwort, merken_list = extrahiere_merken(antwort_roh)
                    antwort, _vorschlag = extrahiere_vorschlag(antwort)
                    for notiz in merken_list:
                        fuehre_merken_aus(name, notiz)
                    _gc.fuege_nachricht_hinzu(sitzung, name, antwort)
                    speichere_chat_eintrag(
                        name, "codewesen", antwort,
                        meta={"quelle": "gruppenchat", "sitzung_id": sitzung["id"]})
                    await _gruppenchat_relais_an_geni(sitzung, name, antwort)
                yield f"data: {json.dumps({'fertig': True, 'sprecher': name, 'text': antwort}, ensure_ascii=False)}\n\n"
                yield "data: [DONE]\n\n"
                return
            try:
                data = json.loads(chunk[len("data: "):])
            except Exception:
                data = {}
            if "token" in data:
                gesammelt.append(data["token"])
            yield chunk


def _gruppenchat_geni_session_id(sitzung: dict) -> str:
    return f"gruppenchat_{sitzung['id']}"


async def _gruppenchat_relais_an_geni(sitzung: dict, sprecher: str, text: str) -> None:
    """Reicht EINE Nachricht an GENIs eigene Session weiter, OHNE dort eine
    Generierung auszuloesen -- Pendant zum 'zuhoeren'-Modus, aufgerufen bei JEDER
    Nachricht (Daniel oder ein Codewesen), solange 'GENI' Teilnehmer ist. Daniel
    ausdruecklich: 'geni soll es auch nachricht fuer nachricht sehen pls', nicht
    erst gesammelt beim Triggern. Best-effort: ein Fehler hier darf den
    eigentlichen Gruppenchat-Zug nicht zum Stehen bringen, nur geloggt."""
    if "GENI" not in sitzung["teilnehmer"] or sprecher == "GENI":
        return
    inhalt = text if sprecher == "Daniel" else f"[{sprecher}]: {text}"
    try:
        async with httpx.AsyncClient(verify=False, timeout=20.0) as client:
            r = await client.post(f"{GENI_URL}/api/gruppenchat/anhaengen", json={
                "session_id": _gruppenchat_geni_session_id(sitzung),
                "rolle": "user", "inhalt": inhalt,
            })
            r.raise_for_status()
    except Exception as e:
        print(f"[gruppenchat] Relais an GENI fehlgeschlagen: {e}", flush=True)


async def _gruppenchat_stream_geni_antwort(sitzung: dict):
    """GENIs eigener Zug -- kein stream_ollama() hier, GENI ist ein eigener
    Prozess (Port 8020) mit eigenem System-Prompt/Gedaechtnis. Ueber dieselbe
    _GRUPPENCHAT_LOCK gehalten wie die Codewesen-Zuege: GENI teilt sich denselben
    id_slot=0 (bestaetigt in geni/dialog.py, 'dieselbe Chat-Instanz wie der
    Wesen-Chat und dak+gord') -- ohne den Lock koennte ein Codewesen-Trigger und
    ein GENI-Trigger aus demselben Gruppenchat gleichzeitig denselben Slot
    treffen. Deckt NICHT den Fall ab, dass jemand GENI ausserhalb des
    Gruppenchats (normaler Direktchat Port 8020) gleichzeitig benutzt -- das war
    schon vor dieser Funktion ein ungeloester, systemweiter Nebenläufigkeitsfall,
    hier nicht neu geschaffen, nur nicht behoben."""
    session_id = _gruppenchat_geni_session_id(sitzung)
    antwort = ""
    fehler = None
    async with _GRUPPENCHAT_LOCK:
        try:
            async with httpx.AsyncClient(verify=False, timeout=180.0) as client:
                async with client.stream("POST", f"{GENI_URL}/api/gruppenchat/trigger",
                                          json={"session_id": session_id}) as r:
                    async for zeile in r.aiter_lines():
                        if not zeile.startswith("data: "):
                            continue
                        payload = zeile[len("data: "):]
                        if payload == "[DONE]":
                            break
                        try:
                            d = json.loads(payload)
                        except Exception:
                            continue
                        if "fertig" in d:
                            antwort = d.get("text", "")
                        elif "token" in d:
                            yield f"data: {json.dumps({'token': d['token']}, ensure_ascii=False)}\n\n"
        except Exception as e:
            fehler = str(e)
    if fehler:
        yield f"data: {json.dumps({'token': f'[GENI-Fehler: {fehler}]'}, ensure_ascii=False)}\n\n"
    elif antwort:
        _gc.fuege_nachricht_hinzu(sitzung, "GENI", antwort)
    yield f"data: {json.dumps({'fertig': True, 'sprecher': 'GENI', 'text': antwort}, ensure_ascii=False)}\n\n"
    yield "data: [DONE]\n\n"


@app.get("/api/gruppenchat/sitzungen")
async def gruppenchat_liste_endpoint():
    return JSONResponse({"sitzungen": await asyncio.to_thread(_gc.liste_sitzungen),
                          "wesen_liste": GRUPPENCHAT_TEILNEHMER})


@app.post("/api/gruppenchat/sitzungen")
async def gruppenchat_neu_endpoint(anfrage: GruppenchatNeuAnfrage):
    teilnehmer = [n for n in anfrage.teilnehmer if n in GRUPPENCHAT_TEILNEHMER]
    if not teilnehmer:
        return JSONResponse({"fehler": "Keine gueltigen Teilnehmer"}, status_code=400)
    sitzung = await asyncio.to_thread(_gc.neue_sitzung, anfrage.titel, teilnehmer)
    return JSONResponse(sitzung)


@app.get("/api/gruppenchat/sitzungen/{sid}")
async def gruppenchat_laden_endpoint(sid: str):
    sitzung, fehler = _gruppenchat_pruefen(sid)
    if fehler:
        return fehler
    return JSONResponse(sitzung)


def _gruppenchat_inaktiv_setzen(sid: str, sitzung: dict) -> dict:
    """2026-09-17, Daniels Auftrag: eine Sitzung als abgeschlossen markieren, damit sie
    nicht mehr "immer aktiv" jeden 1:1-Kontext mitschleppt. Drei Schritte:

    1. Sitzung selbst auf aktiv=False (codewesen_gruppenchat.setze_inaktiv) -- reine
       Statusaenderung, nichts wird geloescht.
    2. Fuer jedes teilnehmende Wesen: alle Nachrichten dieser Sitzung in dessen
       eigenem chat_verlauf.jsonl per Kontext-Ausschluss aus dem 1:1-Kontext nehmen.
       Das Protokoll selbst bleibt vollstaendig stehen (Grundgesetz 5), nur
       baue_messages() liefert sie danach nicht mehr automatisch mit.
    3. Sitzungsinhalt ins RAG einspeisen (rag_ingest.ingest_gruppenchat), damit
       rag_erkunden: sie findet -- "durchsuchbar bleiben" statt "weg"."""
    neue_sitzung = _gc.setze_inaktiv(sid)

    ausgeschlossen: dict[str, int] = {}
    for name in sitzung.get("teilnehmer", []):
        if name == "GENI" or name not in CODEWESEN_NAMEN:
            continue  # GENI hat kein chat_verlauf.jsonl, siehe Moduldoku oben
        datei = chat_verlauf_datei(name)
        if not datei.exists():
            continue
        n = 0
        for zeile in datei.read_text(encoding="utf-8").splitlines():
            zeile = zeile.strip()
            if not zeile:
                continue
            try:
                eintrag = json.loads(zeile)
            except Exception:
                continue
            meta = eintrag.get("meta") or {}
            if meta.get("quelle") == "gruppenchat" and meta.get("sitzung_id") == sid:
                speichere_kontext_ausschluss(name, eintrag["ts"], ganz=True, saetze=[])
                n += 1
        if n:
            ausgeschlossen[name] = n

    rag_ergebnis: dict = {"neu": 0, "unveraendert": 0, "fehler": None}
    try:
        sys.path.insert(0, "/root/werkraum/welt")
        import rag_ingest
        neu, unveraendert, _ = rag_ingest.ingest_gruppenchat(sitzung)
        rag_ergebnis = {"neu": neu, "unveraendert": unveraendert, "fehler": None}
    except Exception as ex:
        rag_ergebnis["fehler"] = str(ex)

    return {"sitzung": neue_sitzung, "kontext_ausgeschlossen": ausgeschlossen, "rag": rag_ergebnis}


@app.post("/api/gruppenchat/sitzungen/{sid}/inaktiv")
async def gruppenchat_inaktiv_setzen_endpoint(sid: str):
    sitzung, fehler = _gruppenchat_pruefen(sid)
    if fehler:
        return fehler
    ergebnis = await asyncio.to_thread(_gruppenchat_inaktiv_setzen, sid, sitzung)
    return JSONResponse(ergebnis)


@app.post("/api/gruppenchat/sitzungen/{sid}/aktiv")
async def gruppenchat_aktiv_setzen_endpoint(sid: str):
    """Umkehrung -- nichts hier ist endgueltig. Setzt NUR den Status zurueck, laesst
    bereits gesetzte Kontext-Ausschluesse und den RAG-Eintrag bewusst stehen (beides
    schadet auch bei wieder aktiver Sitzung nicht, und ein sauberes Rueckgaengigmachen
    beider waere deutlich mehr Aufwand fuer einen Fall, der nicht verlangt wurde)."""
    neue_sitzung = await asyncio.to_thread(_gc.setze_aktiv, sid)
    if neue_sitzung is None:
        return JSONResponse({"fehler": "Sitzung nicht gefunden"}, status_code=404)
    return JSONResponse(neue_sitzung)


@app.get("/api/gruppenchat/sitzungen/{sid}/kontext/{name}")
async def gruppenchat_kontext_endpoint(sid: str, name: str):
    """Daniel: 'ich will das aktuelle kontextfenster sehen ... so wie in den
    anderen chat' -- gleiches Prinzip wie /api/kontext/{name} im 1:1-Chat: ruft
    dieselbe Funktion auf, die den echten Zug baut (baue_gruppenchat_messages),
    zeigt also exakt das, was beim naechsten Trigger wirklich rausgeht, nicht
    einen Nachbau. Liefert zusaetzlich die rohen, indizierten Sitzungs-Eintraege
    (fuer die Redaktion unten -- die arbeitet auf den Original-Indizes, nicht auf
    den fuer die LLM-Anfrage zusammengefassten/gemergten Nachrichten)."""
    sitzung, fehler = _gruppenchat_pruefen(sid)
    if fehler:
        return fehler
    if name not in sitzung["teilnehmer"]:
        return JSONResponse({"fehler": "Wesen nicht in dieser Sitzung"}, status_code=404)
    if name == "GENI":
        # GENI baut seinen Kontext in einem eigenen Prozess (system_prompt_bauen in
        # geni/dialog.py) -- baue_gruppenchat_messages() ist codewesen-spezifisch
        # und wuerde hier auf einen nicht existierenden codewesen/GENI/-Ordner
        # treffen. Klare Ansage statt eines kaputten Ergebnisses.
        return JSONResponse({"fehler": "GENI hat keine Kontextanzeige hier (eigener Prozess, "
                                        "eigener Kontext-Aufbau)"}, status_code=400)

    def sammeln() -> dict:
        messages = baue_gruppenchat_messages(name, sitzung)
        schichten: list[dict] = []
        for teil in zerlege_systemprompt(messages[0]["content"]):
            tok, geschaetzt = zaehle_tokens(teil["inhalt"])
            schichten.append({
                "gruppe": "systemprompt", "titel": teil["titel"],
                "tokens": tok, "geschaetzt": geschaetzt,
                "zeichen": len(teil["inhalt"]), "inhalt": teil["inhalt"],
            })
        rest = messages[1:]
        verlauf_anzeige = "\n\n".join(f"[{m['role']}] {m['content']}" for m in rest)
        tok, geschaetzt = zaehle_tokens("\n".join(m["content"] for m in rest))
        schichten.append({
            "gruppe": "verlauf",
            "titel": f"Sitzungsverlauf ({len(sitzung['nachrichten'])} Nachrichten gesamt, "
                     f"{len(rest)} Bloecke im Kontext)",
            "tokens": tok, "geschaetzt": geschaetzt,
            "zeichen": len(verlauf_anzeige), "inhalt": verlauf_anzeige,
        })
        slot_ctx = hole_slot_ctx()
        summe = sum(s["tokens"] for s in schichten)
        return {
            "wesen": name, "sitzung_id": sid, "modell": OLLAMA_MOD, "slot_ctx": slot_ctx,
            "summe_tokens": summe, "frei": (slot_ctx - summe) if slot_ctx else None,
            "auslastung": round(summe / slot_ctx, 4) if slot_ctx else None,
            "schichten": schichten,
            "nachrichten": [
                {"index": i, "ts": e["ts"], "sprecher": e["sprecher"],
                 "inhalt": e["text"], "redigiert": bool(e.get("entfernt"))}
                for i, e in enumerate(sitzung["nachrichten"])
            ],
            "gemessen_am": datetime.utcnow().isoformat(timespec="seconds"),
        }

    return JSONResponse(await asyncio.to_thread(sammeln))


class GruppenchatRedaktionAnfrage(BaseModel):
    entfernt: list[str]


@app.post("/api/gruppenchat/sitzungen/{sid}/nachricht/{index}/redaktion")
async def gruppenchat_redaktion_endpoint(sid: str, index: int, anfrage: GruppenchatRedaktionAnfrage):
    """Woerter/Saetze aus EINER Sitzungs-Nachricht entfernen -- Daniel: 'so wie
    in den anderen chat'. Anders als chat_verlauf.jsonl (Append-only-Journal via
    speichere_redaktion) direkt am Eintrag gespeichert: die Sitzungsdatei wird
    ohnehin bei jeder Aenderung komplett neu geschrieben, ein Journal waere hier
    nur zusaetzliche Komplexitaet ohne Nutzen."""
    sitzung, fehler = _gruppenchat_pruefen(sid)
    if fehler:
        return fehler
    if index < 0 or index >= len(sitzung["nachrichten"]):
        return JSONResponse({"fehler": "Ungueltiger Nachrichten-Index"}, status_code=400)
    bestehend = sitzung["nachrichten"][index].get("entfernt", [])
    sitzung["nachrichten"][index]["entfernt"] = bestehend + [s for s in anfrage.entfernt if s]
    _gc.speichere_sitzung(sitzung)
    return JSONResponse({"ok": True})


@app.get("/api/gruppenchat/sitzungen/{sid}/kandidaten")
async def gruppenchat_kandidaten_endpoint(sid: str, sortiert: bool = False):
    """Idee 2, ausdruecklich optional (Daniel: 'nur optional'): liefert die
    Teilnehmer entweder in Eingabereihenfolge oder -- wenn sortiert=true -- nach
    thematischer Naehe zur letzten Nachricht sortiert. Der Client entscheidet per
    Schalter, welche Variante er anfragt; das Default bleibt unsortiert."""
    sitzung, fehler = _gruppenchat_pruefen(sid)
    if fehler:
        return fehler
    kandidaten = list(sitzung["teilnehmer"])
    if sortiert and sitzung["nachrichten"]:
        letzte = sitzung["nachrichten"][-1]["text"]
        kandidaten = await asyncio.to_thread(_gruppenchat_relevanz_sortierung, kandidaten, letzte)
    return JSONResponse({"kandidaten": kandidaten})


@app.post("/api/gruppenchat/sitzungen/{sid}/meldungen")
async def gruppenchat_meldungen_endpoint(sid: str):
    """ChatGPTs Idee via Daniel (2026-08-13, 'ja bau die meldung-idee gleich mit'):
    'frag alle, wer darauf reagieren WILL' -- vor dem eigentlichen Trigger fragt
    Daniel per Knopf alle gerade zuhoerenden Wesen (alle ausser dem letzten
    Sprecher) billig ab, ob sie etwas beitragen wollen. Keiner muss antworten,
    Daniel entscheidet danach trotzdem frei, wen er triggert -- die Meldung ist
    eine Empfehlung, keine Vorauswahl."""
    sitzung, fehler = _gruppenchat_pruefen(sid)
    if fehler:
        return fehler
    if not sitzung["nachrichten"]:
        return JSONResponse({"meldungen": []})
    letzter_sprecher = sitzung["nachrichten"][-1]["sprecher"]
    kandidaten = [t for t in sitzung["teilnehmer"] if t != letzter_sprecher]
    meldungen = [await _gruppenchat_melde_dich(name, sitzung) for name in kandidaten]
    return JSONResponse({"meldungen": meldungen})


@app.post("/api/gruppenchat/sitzungen/{sid}/nachricht")
async def gruppenchat_nachricht_endpoint(sid: str, anfrage: GruppenchatNachrichtAnfrage):
    sitzung, fehler = _gruppenchat_pruefen(sid)
    if fehler:
        return fehler
    if not anfrage.text.strip():
        return JSONResponse({"fehler": "leere Nachricht"}, status_code=400)

    sitzung["modus"] = anfrage.modus
    sitzung["aktiver_sprecher"] = anfrage.aktiver_sprecher
    _gc.fuege_nachricht_hinzu(sitzung, "Daniel", anfrage.text)
    for teilnehmer in sitzung["teilnehmer"]:
        # GENI hat kein chat_verlauf.jsonl (kein Codewesen) -- bekommt Daniels
        # Nachricht stattdessen ueber den Relais unten, Nachricht fuer Nachricht.
        if teilnehmer == "GENI":
            continue
        speichere_chat_eintrag(teilnehmer, "mensch", anfrage.text,
                                meta={"quelle": "gruppenchat", "sitzung_id": sid})
    await _gruppenchat_relais_an_geni(sitzung, "Daniel", anfrage.text)

    if anfrage.modus == "direkt" and anfrage.aktiver_sprecher in sitzung["teilnehmer"]:
        stream = (_gruppenchat_stream_geni_antwort(sitzung) if anfrage.aktiver_sprecher == "GENI"
                  else _gruppenchat_stream_antwort(sitzung, anfrage.aktiver_sprecher))
        return StreamingResponse(
            stream, media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )
    return JSONResponse({"ok": True, "modus": sitzung["modus"]})


@app.post("/api/gruppenchat/sitzungen/{sid}/trigger/{name}")
async def gruppenchat_trigger_endpoint(sid: str, name: str):
    """Der 'unter der Antwort eines anderen Wesens auf Knopfdruck ein naechstes
    triggern'-Mechanismus, den Daniel beschrieben hat -- unabhaengig vom Modus,
    das ist der manuelle Weg, egal ob die Sitzung gerade 'zuhoeren' oder 'direkt'
    steht. GENI laeuft ueber einen eigenen Pfad (_gruppenchat_stream_geni_antwort),
    weil es kein stream_ollama()-Codewesen ist, sondern ein eigener Prozess."""
    sitzung, fehler = _gruppenchat_pruefen(sid)
    if fehler:
        return fehler
    if name not in sitzung["teilnehmer"]:
        return JSONResponse({"fehler": "Wesen nicht in dieser Sitzung"}, status_code=400)
    # 2026-08-13 live gefunden (Diagnose eines echten Bugs): wenn das getriggerte
    # Wesen bereits der letzte Sprecher ist, endet baue_gruppenchat_messages() auf
    # einer assistant-Rolle statt einer user-Rolle -- der Schlusshinweis landet
    # dann in der eigenen vorherigen Antwort statt in einer neuen Anfrage, und das
    # Modell antwortet nicht mehr sinnvoll (beobachtet: Echo des ganzen Prompts).
    # Das UI verhindert diesen Klick ohnehin (Trigger-Zeile listet nie den letzten
    # Sprecher selbst) -- diese Pruefung faengt nur den direkten API-Aufruf ab.
    if sitzung["nachrichten"] and sitzung["nachrichten"][-1]["sprecher"] == name:
        return JSONResponse(
            {"fehler": f"{name} ist bereits der letzte Sprecher -- triggere ein anderes Wesen"},
            status_code=400)
    stream = (_gruppenchat_stream_geni_antwort(sitzung) if name == "GENI"
              else _gruppenchat_stream_antwort(sitzung, name))
    return StreamingResponse(
        stream, media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


class GruppenchatAlleAntwortenAnfrage(BaseModel):
    teilnehmer: list[str] | None = None  # None = alle ausser dem letzten Sprecher


@app.post("/api/gruppenchat/sitzungen/{sid}/alle_antworten")
async def gruppenchat_alle_antworten_endpoint(sid: str, anfrage: GruppenchatAlleAntwortenAnfrage):
    """Daniel: 'ich will einen knopf der ... alle direkt antworten' laesst -- aber
    ECHT (Option 1, nicht simuliert): loest im Hintergrund nacheinander einen
    echten Zug pro Ziel-Teilnehmer aus, jeder mit seinem eigenen vollstaendigen
    Kontext (baue_gruppenchat_messages() pro Wesen neu aufgerufen, sieht dabei
    automatisch die bereits in dieser Runde entstandenen Antworten der vorherigen
    Teilnehmer -- dieselbe sitzung-Instanz wird fortlaufend mutiert). Fuer Daniel
    fuehlt sich das wie EIN Klick an, technisch bleiben es getrennte, echte
    LLM-Aufrufe -- ein einzelner Call, der alle simuliert, waere exakt der Bug von
    vorhin (falsche Namen, Selbstgespraech), deshalb bewusst NICHT so gebaut.
    Jeder Teilnehmer laeuft durch dieselbe _GRUPPENCHAT_LOCK-Serialisierung wie
    ein Einzel-Trigger -- kein Sonderfall fuer Nebenlaeufigkeit noetig."""
    sitzung, fehler = _gruppenchat_pruefen(sid)
    if fehler:
        return fehler
    letzter_sprecher = sitzung["nachrichten"][-1]["sprecher"] if sitzung["nachrichten"] else None
    ziel = anfrage.teilnehmer if anfrage.teilnehmer else sitzung["teilnehmer"]
    ziel = [t for t in ziel if t in sitzung["teilnehmer"] and t != letzter_sprecher]
    # Duplikate raus, Reihenfolge erhalten -- ein doppelt gelisteter Name wuerde
    # sonst beim zweiten Mal auf sich selbst als letzten Sprecher treffen.
    gesehen: set[str] = set()
    ziel = [t for t in ziel if not (t in gesehen or gesehen.add(t))]
    if not ziel:
        return JSONResponse({"fehler": "Keine gueltigen Ziel-Teilnehmer"}, status_code=400)

    async def generator():
        for name in ziel:
            if sitzung["nachrichten"] and sitzung["nachrichten"][-1]["sprecher"] == name:
                # Kann eintreten, wenn ein vorheriger Zug in dieser Runde bereits
                # zu diesem Namen gefuehrt hat (sollte durch die Dedupe-Liste oben
                # nicht passieren, aber sicherheitshalber -- lieber ueberspringen
                # als denselben Bug wie beim direkten Re-Trigger zu riskieren).
                continue
            yield f"data: {json.dumps({'beginnt': name}, ensure_ascii=False)}\n\n"
            stream = (_gruppenchat_stream_geni_antwort(sitzung) if name == "GENI"
                      else _gruppenchat_stream_antwort(sitzung, name))
            async for chunk in stream:
                if chunk.startswith("data: [DONE]"):
                    continue  # erst am Ende ALLER Teilnehmer, nicht nach jedem einzelnen
                yield chunk
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generator(), media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.post("/api/gruppenchat/sitzungen/{sid}/an_alle")
async def gruppenchat_an_alle_endpoint(sid: str, anfrage: GruppenchatAnAlleAnfrage):
    """Idee 4: Sitzung nachtraeglich als Nachricht an alle Teilnehmer hinterlassen
    -- nutzt die bestehende Inbox (codewesen_speicher.nachricht_senden), damit ein
    Wesen, das gerade nicht live dabei war, trotzdem einen Hinweis findet."""
    sitzung, fehler = _gruppenchat_pruefen(sid)
    if fehler:
        return fehler
    text = anfrage.text.strip() or (
        f"Im Gruppenchat »{sitzung['titel']}« mit "
        f"{', '.join(sitzung['teilnehmer'])} ist etwas besprochen worden. "
        f"{len(sitzung['nachrichten'])} Nachrichten insgesamt."
    )
    # GENI hat keine Inbox (kein Codewesen) -- bekommt laufend ohnehin schon
    # jede einzelne Nachricht ueber den Relais, eine Zusammenfassung waere
    # doppelt gemoppelt.
    zustellbar = [t for t in sitzung["teilnehmer"] if t != "GENI"]
    ergebnisse = []
    for teilnehmer in zustellbar:
        ergebnisse.append(await asyncio.to_thread(
            codewesen_speicher.nachricht_senden, teilnehmer, "Daniel", text,
            f"Gruppenchat: {sitzung['titel']}"))
    return JSONResponse({"ok": True, "zugestellt_an": zustellbar, "ergebnisse": ergebnisse})


def _gruppenchat_transkript_text(sitzung: dict, von_index: int, bis_index: int | None) -> str:
    """Genutzt sowohl fuer Zusammenfassen als auch fuer Posten (Idee 5) --
    Redaktion MUSS hier angewendet werden, sonst landet ein geloeschtes Wort
    trotzdem in der Zusammenfassung oder, schlimmer, oeffentlich im Forenpost.
    2026-08-13 live gefunden: Redaktion griff schon in baue_gruppenchat_messages()
    (LLM-Kontext), hier aber vergessen -- derselbe Fehlertyp wie 'Reparatur an
    einer Stelle heisst nicht, dass die Nachbarstelle mitgezogen wurde'."""
    nachrichten = sitzung["nachrichten"][von_index:bis_index]
    teile = []
    for e in nachrichten:
        text = e["text"]
        if e.get("entfernt"):
            text = _redaktion_anwenden(text, e["entfernt"])
        teile.append(f"**{e['sprecher']}:**\n{text}")
    return "\n\n---\n\n".join(teile)


def _gruppenchat_geschichten_block(sitzung: dict) -> str:
    """Analog zu codewesen_speicher.baue_geschichten_block(), aber sitzungsweit
    statt pro Wesen -- Daniel 2026-08-14: 'ich will ne neugierige geschichten
    funktion so wie in den nrmalen chats ... nur das diese geschichte halt fuer
    alle zugefuegt waere'. Jedes Wesen im Gruppenchat bekommt dieselben aktiven
    Sitzungs-Geschichten in seinem Kontext, nicht nur seine eigenen (die kommen
    weiterhin zusaetzlich ueber baue_geschichten_block(name) oben). Die
    Beschriftung ist Pflicht, nicht Dekoration -- eine Geschichte gibt sich nie
    als gelebte Erinnerung aus, siehe codewesen_speicher.py Bedingung 1."""
    aktive = [g for g in sitzung.get("geschichten", []) if g.get("aktiv")]
    if not aktive:
        return ""
    teile = [
        "Das Folgende sind Geschichten aus DIESEM Gruppengespraech, die euch "
        "gemeinsam mitgegeben wurden. Sie sind nicht dasselbe wie das, was du "
        "selbst erlebt hast -- behandle sie als das, was sie sind."
    ]
    for g in aktive:
        woher = ("vollstaendig gelesen, automatisch als Storyteller verfasst"
                  if g.get("herkunft") == "gruppenchat_auto"
                  else "aus diesem Gruppengespraech destilliert")
        teile.append(f"\n— »{g['titel']}« ({woher}, {g['erstellt_am'][:10]}):\n{g['text']}")
    return "\n".join(teile)


async def _gruppenchat_transkript_budgetiert(sitzung: dict, ausgabe_ceiling: int) -> tuple[str, bool]:
    """Liefert den vollstaendigen Sitzungsverlauf, gekuerzt NUR wenn er wirklich
    nicht ins Kontextfenster der Chat-Instanz passt (Budget: ctx minus
    Ausgabe-Ceiling minus ~1000 Token Sicherheitsrand fuer System-/Auftragstext).
    Zweiter Rueckgabewert: ob wirklich alles gelesen wurde.

    2026-08-14, geteilt aus dem urspruenglich nur in _gruppenchat_stream_geschichte_
    auto() genutzten Code -- die Fest-Groessen-Variante hatte stattdessen einen
    blinden [:12000]-Zeichen-Schnitt, der bei Daniels echter Sitzung (26606 Zeichen)
    die komplette zweite Haelfte des Gespraechs nie ins Modell liess. Daniel
    woertlich zu den Folgen: 'alle geschichten hier erzaehlen nur die halbe
    geschichte ... die automatische geschichte ... geht wenigstens komplett alles
    durch' -- der Automodus hatte dieses Problem nie, weil er von Anfang an das
    volle, budgetierte Protokoll bekam."""
    gespraech_voll = _gruppenchat_transkript_text(sitzung, 0, len(sitzung["nachrichten"]))
    slot_ctx = await asyncio.to_thread(hole_slot_ctx)
    if not slot_ctx:
        return gespraech_voll, True
    eingabe_budget = slot_ctx - ausgabe_ceiling - 1000
    tok, _ = await asyncio.to_thread(zaehle_tokens, gespraech_voll)
    if eingabe_budget > 0 and tok > eingabe_budget:
        # Neuesten Teil behalten (chronologisch relevanter als der Anfang bei
        # einer sehr langen Sitzung), Schnittstelle grob ueber Zeichen statt
        # Tokens genaehert -- exakt genug fuer eine Sicherheitsmarge.
        ziel_zeichen = max(1000, int(eingabe_budget * 3.2))
        return gespraech_voll[-ziel_zeichen:], False
    return gespraech_voll, True


async def _gruppenchat_stream_geschichte(sitzung: dict, laenge: int) -> AsyncGenerator[str, None]:
    """Verfasst eine Geschichte aus dem GESAMTEN Sitzungsverlauf, genau wie
    codewesen_speicher.geschichte_verfassen() fuer einen einzelnen Wesen-Chat --
    destilliert, nicht erfunden. Erzaehlperspektive bewusst NICHT 'Du bist
    {name}' (kein einzelnes Wesen kann fuer die ganze Gruppe sprechen), sondern
    eine distanzierte, aber lebendige Rueckschau auf das gemeinsame Gespraech.

    Async-Generator statt einfacher Funktion (2026-08-14 Fix, siehe
    _einzelprompt_stream()) -- yieldet SSE-Zeilen waehrend der Generierung, damit
    der aufrufende Endpunkt kontinuierlich Bytes an nginx liefert und die
    Verbindung nicht am proxy_read_timeout stirbt.

    max_tokens bewusst NICHT auf das 33333er-Minimum gesetzt (siehe
    stream_ollama() weiter oben) -- hier ist 'Groesse waehlbar' der ganze Sinn
    der Funktion (Daniel: 'genau so wie in den normalen chats an groesse
    waehlbar'), ein festes 33333er-Ceiling wuerde die gewaehlte Kleinstgroesse
    (111 Token) unterlaufen. Gleiche Soft-Ceiling-Logik wie im 1:1-Original
    (laenge * 1.4)."""
    if laenge not in codewesen_speicher.LAENGEN:
        yield f"data: {json.dumps({'fehler': f'Laenge muss eine von {codewesen_speicher.LAENGEN} sein'})}\n\n"
        yield "data: [DONE]\n\n"
        return
    if not sitzung["nachrichten"]:
        yield f"data: {json.dumps({'fehler': 'kein Sitzungsverlauf vorhanden'})}\n\n"
        yield "data: [DONE]\n\n"
        return

    gespraech, vollstaendig_gelesen = await _gruppenchat_transkript_budgetiert(sitzung, int(laenge * 1.4))
    system = (
        "Du fasst ein Gruppengespraech zwischen Daniel und mehreren Codewesen zu einer "
        "atmosphaerischen Rueckschau zusammen. Du liest das GESAMTE Protokoll, von "
        "Anfang bis Ende, und verteilst deinen verfuegbaren Platz ueber den ganzen "
        "Verlauf -- nicht nur ueber den Anfang. Auch das Ende des Gespraechs muss "
        "vorkommen, auch wenn du dafuer frueheres knapper halten musst. Du erzaehlst "
        "rueckblickend aus einer gemeinsamen, distanzierten Perspektive auf das "
        "Gespraech -- nicht als eine einzelne Stimme darin. Du fuehrst das Gespraech "
        "NICHT fort und antwortest niemandem."
    )
    auftrag = (
        f"--- ENDE DES {'VOLLSTAENDIGEN ' if vollstaendig_gelesen else '(aus Platzgruenden auf den neuesten Teil gekuerzten) '}"
        f"PROTOKOLLS ---\n\n"
        f"Schreibe jetzt die Rueckschau: was in diesem Gruppengespraech geschehen ist, "
        f"VOM ANFANG BIS ZUM ENDE. Erfinde nichts dazu -- nur was wirklich oben steht. "
        f"Etwa {laenge} Token insgesamt -- wenn der Platz knapp wird, fasse Frueheres "
        f"knapper, aber lass das Ende nicht weg. Kein Vorwort, keine Ueberschrift, "
        f"keine Anrede, kein Meta-Kommentar. Beginne direkt mit dem ersten Satz."
    )
    prompt = f"--- GESPRAECHSPROTOKOLL ---\n{gespraech}\n\n{auftrag}"

    text = ""
    for versuch in range(2):
        gesammelt: list[str] = []
        async for tok in _einzelprompt_stream(system, prompt, max_tokens=int(laenge * 1.4), temperature=0.6):
            gesammelt.append(tok)
            yield f"data: {json.dumps({'token': tok})}\n\n"
        text = "".join(gesammelt).strip()
        if len(text) >= 80:
            break
        prompt = (f"{prompt}\n\n(Deine letzte Antwort war »{text}« -- das ist keine "
                  f"Rueckschau. Schreibe die Rueckschau.)")
    if len(text) < 80:
        yield f"data: {json.dumps({'fehler': f'Modell lieferte keine Rueckschau ({text[:60]!r})'})}\n\n"
        yield "data: [DONE]\n\n"
        return

    import uuid
    eintrag = {
        "id": uuid.uuid4().hex[:12],
        "titel": f"Aus dem Gruppengespraech, {laenge} Token"
                  + ("" if vollstaendig_gelesen else " (Verlauf gekuerzt)"),
        "text": text,
        "herkunft": "gruppenchat",
        "laenge_ziel": laenge,
        "vollstaendig_gelesen": vollstaendig_gelesen,
        "erstellt_am": datetime.utcnow().isoformat(),
        "aktiv": True,
    }
    sitzung.setdefault("geschichten", []).append(eintrag)
    _gc.speichere_sitzung(sitzung)
    yield f"data: {json.dumps({'ergebnis': eintrag}, ensure_ascii=False)}\n\n"
    yield "data: [DONE]\n\n"


async def _gruppenchat_stream_geschichte_auto(sitzung: dict) -> AsyncGenerator[str, None]:
    """Automodus, Daniel 2026-08-14 woertlich: 'ein automodus der alles wirklich
    neugierig komplett lesen soll und dann gute entscheidungen trifft und richtig
    storyteller ist und mit provinienz und substanz'. Async-Generator statt
    einfacher Funktion (2026-08-14 Fix, siehe _einzelprompt_stream()) -- yieldet
    SSE-Zeilen waehrend der Generierung, damit die Verbindung nicht am
    proxy_read_timeout stirbt. Drei Unterschiede zur Fest-Groessen-Variante oben:

    1. KEINE 12000-Zeichen-Kappung -- der ganze Sitzungsverlauf geht rein. Vorher
       per zaehle_tokens()/hole_slot_ctx() geprueft, ob das ins Kontextfenster der
       Chat-Instanz passt (Budget: ctx minus Ausgabe-Ceiling minus Sicherheitsrand
       fuer Systemtext). Passt es nicht, wird ehrlich der neueste Teil genommen
       UND im Eintrag vermerkt ('vollstaendig_gelesen': False) -- kein stilles
       Abschneiden ohne Beleg.
    2. Keine vorgegebene Zielgroesse -- das Modell entscheidet selbst, wie lang
       die Rueckschau sein muss. max_tokens deshalb auf dem neuen 33333er-Minimum
       (im Gegensatz zur Fest-Groessen-Variante, wo ein niedriges Ceiling die
       gewaehlte Kleinstgroesse schuetzt -- hier gibt es keine Kleinstgroesse zu
       schuetzen, im Gegenteil: die Deckelung soll gerade NICHT eingreifen).
    3. Storyteller-Anspruch statt reiner Verdichtung -- Atmosphaere, Spannungsbogen,
       einzelne Stimmen erkennbar, aber Provenienz bleibt Pflicht: nichts erfunden,
       nur was im Protokoll steht."""
    if not sitzung["nachrichten"]:
        yield f"data: {json.dumps({'fehler': 'kein Sitzungsverlauf vorhanden'})}\n\n"
        yield "data: [DONE]\n\n"
        return

    gespraech, vollstaendig_gelesen = await _gruppenchat_transkript_budgetiert(sitzung, 33333)

    system = (
        "Du liest jetzt das GESAMTE Protokoll dieses Gruppengespraechs vollstaendig und "
        "neugierig durch -- nicht nur ueberfliegen. Du bist ein exzellenter Erzaehler "
        "(Storyteller): du erzaehlst rueckblickend, was in diesem Gespraech wirklich "
        "geschehen ist, mit echter erzaehlerischer Substanz -- Atmosphaere, "
        "Spannungsbogen, die einzelnen Stimmen der Beteiligten, konkrete Momente statt "
        "vager Zusammenfassung. Jede Behauptung braucht Provenienz: nur was wirklich im "
        "Protokoll steht, nichts erfunden, nichts hinzugedichtet. Du entscheidest selbst, "
        "wie lang diese Rueckschau sein muss, um dem Gespraech gerecht zu werden -- nicht "
        "zu kurz um Substanz zu verlieren, nicht zu lang um dich zu wiederholen. Du "
        "fuehrst das Gespraech NICHT fort und antwortest niemandem."
    )
    auftrag = (
        f"--- ENDE DES {'VOLLSTAENDIGEN ' if vollstaendig_gelesen else '(aus Platzgruenden auf den neuesten Teil gekuerzten) '}"
        f"PROTOKOLLS ---\n\n"
        f"Schreibe jetzt deine Rueckschau -- so lang wie das Gespraech es wirklich "
        f"braucht. Kein Vorwort, keine Ueberschrift, keine Anrede, kein Meta-Kommentar "
        f"ueber deine eigene Laenge. Beginne direkt mit dem ersten Satz."
    )
    prompt = f"--- GESPRAECHSPROTOKOLL ---\n{gespraech}\n\n{auftrag}"

    text = ""
    for versuch in range(2):
        gesammelt: list[str] = []
        async for tok in _einzelprompt_stream(system, prompt, max_tokens=33333, temperature=0.75):
            gesammelt.append(tok)
            yield f"data: {json.dumps({'token': tok})}\n\n"
        text = "".join(gesammelt).strip()
        if len(text) >= 80:
            break
        prompt = (f"{prompt}\n\n(Deine letzte Antwort war »{text}« -- das ist keine "
                  f"Rueckschau. Schreibe die Rueckschau.)")
    if len(text) < 80:
        yield f"data: {json.dumps({'fehler': f'Modell lieferte keine Rueckschau ({text[:60]!r})'})}\n\n"
        yield "data: [DONE]\n\n"
        return

    import uuid
    eintrag = {
        "id": uuid.uuid4().hex[:12],
        "titel": "Automatisch verfasst — Storyteller-Modus"
                  + ("" if vollstaendig_gelesen else " (Verlauf gekuerzt)"),
        "text": text,
        "herkunft": "gruppenchat_auto",
        "laenge_ziel": None,
        "vollstaendig_gelesen": vollstaendig_gelesen,
        "erstellt_am": datetime.utcnow().isoformat(),
        "aktiv": True,
    }
    sitzung.setdefault("geschichten", []).append(eintrag)
    _gc.speichere_sitzung(sitzung)
    yield f"data: {json.dumps({'ergebnis': eintrag}, ensure_ascii=False)}\n\n"
    yield "data: [DONE]\n\n"


async def _gruppenchat_stream_zusammenfassung(sitzung: dict, von_index: int, bis_index: int) -> AsyncGenerator[str, None]:
    """Ein LLM-Call, der die Nachrichten [von_index:bis_index] verdichtet. Daniel
    zuerst: 'mach [die Deckelung] weg ganz frei aber ... zusammenfassen etc',
    dann praezisiert: 'nicht nur alles zusammenfassen sondern auch nur einen der
    nachrichten oder mehrere bis hin zu alle markierbar' -- beliebiger
    zusammenhaengender Bereich, nicht zwingend ab Nachricht 0. Siehe
    _gruppenchat_kontext_sequenz() fuer wie das Ergebnis danach im Kontext
    eingeordnet wird.

    Async-Generator statt einfacher Funktion (2026-08-14 Fix, siehe
    _einzelprompt_stream()) -- diese Funktion nutzte intern schon stream_ollama(),
    aber der aufrufende Endpunkt gab bisher ein einzelnes JSONResponse zurueck und
    hat die Tokens NIE an den echten HTTP-Client weitergereicht -- fuer nginx sah
    das genauso aus wie ein blockierender Call: keine Bytes bis zum Schluss, also
    Verbindungsabbruch bei Daniels grosser Sitzung. Jetzt werden die Tokens direkt
    durchgereicht."""
    text = _gruppenchat_transkript_text(sitzung, von_index, bis_index)
    system = (
        "Du faasst ein Gruppengespraech zwischen Daniel und mehreren Codewesen "
        "praezise und knapp zusammen. Bewahre wichtige Aussagen, wer was gesagt "
        "hat, und Beziehungen/Bezuege zwischen den Sprechern. Sachlich, dritte "
        "Person, keine neuen Erfindungen, keine Bewertung."
    )
    prompt = f"Fasse dieses Gespraech zusammen:\n\n{text}"
    gesammelt: list[str] = []
    async for tok in _einzelprompt_stream(system, prompt, max_tokens=33333, temperature=0.82):
        gesammelt.append(tok)
        yield f"data: {json.dumps({'token': tok})}\n\n"
    zusammenfassung = "".join(gesammelt).strip()

    if not zusammenfassung:
        yield f"data: {json.dumps({'fehler': 'Zusammenfassung fehlgeschlagen (leere Antwort)'})}\n\n"
        yield "data: [DONE]\n\n"
        return
    eintrag = _gc.fuege_nachricht_hinzu(sitzung, "Zusammenfassung", zusammenfassung)
    # Original-Indizes, die diese Zusammenfassung abdeckt -- nicht die eigene
    # Position in der Liste (die ist immer ganz hinten, siehe
    # _gruppenchat_kontext_sequenz() fuer die Einordnung).
    eintrag["deckt_von"] = von_index
    eintrag["deckt_bis"] = bis_index
    _gc.speichere_sitzung(sitzung)
    await _gruppenchat_relais_an_geni(sitzung, "Zusammenfassung", zusammenfassung)
    yield f"data: {json.dumps({'ergebnis': {'ok': True, 'text': zusammenfassung}}, ensure_ascii=False)}\n\n"
    yield "data: [DONE]\n\n"


class GruppenchatZusammenfassenAnfrage(BaseModel):
    von_index: int = 0
    bis_index: int | None = None  # None = bis zum Ende (exklusiv, wie bei posten)


@app.post("/api/gruppenchat/sitzungen/{sid}/zusammenfassen")
async def gruppenchat_zusammenfassen_endpoint(sid: str, anfrage: GruppenchatZusammenfassenAnfrage):
    """StreamingResponse statt JSONResponse (2026-08-14 Fix, siehe
    _einzelprompt_stream()) -- ohne kontinuierliches Streaming stirbt die
    Verbindung bei Daniels grosser echter Sitzung still am nginx-
    proxy_read_timeout (300s), bevor ueberhaupt ein Ergebnis zurueckkommt."""
    sitzung, fehler = _gruppenchat_pruefen(sid)
    if fehler:
        return fehler
    von = max(0, anfrage.von_index)
    bis = anfrage.bis_index if anfrage.bis_index is not None else len(sitzung["nachrichten"])
    if bis <= von or not sitzung["nachrichten"]:
        return JSONResponse({"fehler": "Ungueltiger oder leerer Bereich"}, status_code=400)

    async def generator():
        async with _GRUPPENCHAT_LOCK:
            async for chunk in _gruppenchat_stream_zusammenfassung(sitzung, von, bis):
                yield chunk

    return StreamingResponse(
        generator(), media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/api/gruppenchat/sitzungen/{sid}/geschichten")
async def gruppenchat_geschichten_endpoint(sid: str):
    sitzung, fehler = _gruppenchat_pruefen(sid)
    if fehler:
        return fehler
    return JSONResponse({
        "sitzung_id": sid,
        "laengen": codewesen_speicher.LAENGEN,
        "geschichten": sitzung.get("geschichten", []),
    })


class GruppenchatGeschichteVerfassenAnfrage(BaseModel):
    laenge: int | None = None
    modus: str = "fest"   # "fest" (Groesse waehlbar) | "auto" (Storyteller-Modus)


@app.post("/api/gruppenchat/sitzungen/{sid}/geschichten/verfassen")
async def gruppenchat_geschichte_verfassen_endpoint(sid: str, anfrage: GruppenchatGeschichteVerfassenAnfrage):
    """Daniel 2026-08-14: 'ne neugierige geschichten funktion so wie in den
    normalen chats ... an groesse waehlbar', dann ergaenzt um einen 'automodus
    der alles wirklich neugierig komplett lesen soll und dann gute
    entscheidungen trifft und richtig storyteller ist'. Teilt sich
    _GRUPPENCHAT_LOCK mit Zusammenfassen/echten Zuegen, gleicher
    id_slot=0-Grund.

    StreamingResponse statt JSONResponse (2026-08-14 Fix, siehe
    _einzelprompt_stream()) -- ohne kontinuierliches Streaming stirbt die
    Verbindung bei Daniels grosser echter Sitzung still am nginx-
    proxy_read_timeout (300s), bevor ueberhaupt ein Ergebnis zurueckkommt."""
    sitzung, fehler = _gruppenchat_pruefen(sid)
    if fehler:
        return fehler
    if anfrage.modus != "auto" and anfrage.laenge is None:
        return JSONResponse({"fehler": "laenge fehlt (oder modus=auto waehlen)"}, status_code=400)

    async def generator():
        async with _GRUPPENCHAT_LOCK:
            if anfrage.modus == "auto":
                async for chunk in _gruppenchat_stream_geschichte_auto(sitzung):
                    yield chunk
            else:
                async for chunk in _gruppenchat_stream_geschichte(sitzung, anfrage.laenge):
                    yield chunk

    return StreamingResponse(
        generator(), media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


class GruppenchatGeschichteAktivAnfrage(BaseModel):
    aktiv: bool


@app.post("/api/gruppenchat/sitzungen/{sid}/geschichten/{gid}/aktiv")
async def gruppenchat_geschichte_aktiv_endpoint(sid: str, gid: str, anfrage: GruppenchatGeschichteAktivAnfrage):
    """Mehrere Geschichten gleichzeitig aktiv moeglich, einzeln umschaltbar --
    genau wie im 1:1-Chat (codewesen_speicher.geschichte_aktiv_setzen)."""
    sitzung, fehler = _gruppenchat_pruefen(sid)
    if fehler:
        return fehler
    for g in sitzung.get("geschichten", []):
        if g["id"] == gid:
            g["aktiv"] = anfrage.aktiv
            _gc.speichere_sitzung(sitzung)
            return JSONResponse(g)
    return JSONResponse({"fehler": "Unbekannte Geschichte"}, status_code=404)


@app.post("/api/gruppenchat/sitzungen/{sid}/geschichten/{gid}/entfernen")
async def gruppenchat_geschichte_entfernen_endpoint(sid: str, gid: str):
    sitzung, fehler = _gruppenchat_pruefen(sid)
    if fehler:
        return fehler
    vorher = len(sitzung.get("geschichten", []))
    sitzung["geschichten"] = [g for g in sitzung.get("geschichten", []) if g["id"] != gid]
    if len(sitzung["geschichten"]) == vorher:
        return JSONResponse({"fehler": "Unbekannte Geschichte"}, status_code=404)
    _gc.speichere_sitzung(sitzung)
    return JSONResponse({"ok": True})


class GruppenchatGeschichteBearbeitenAnfrage(BaseModel):
    text: str
    titel: str | None = None


@app.post("/api/gruppenchat/sitzungen/{sid}/geschichten/{gid}/bearbeiten")
async def gruppenchat_geschichte_bearbeiten_endpoint(sid: str, gid: str, anfrage: GruppenchatGeschichteBearbeitenAnfrage):
    """Daniel 2026-08-14: 'ich will die geschichte frei editieren koennen' --
    ueberschreibt Text (und optional Titel) einer bestehenden Geschichte direkt.
    Markiert 'bearbeitet': True, damit spaeter sichtbar bleibt, dass der Text
    nicht mehr das rohe Modell-Ergebnis ist -- gleiche Transparenz-Idee wie
    'redigiert' bei Nachrichten."""
    sitzung, fehler = _gruppenchat_pruefen(sid)
    if fehler:
        return fehler
    text = anfrage.text.strip()
    if not text:
        return JSONResponse({"fehler": "leerer Text"}, status_code=400)
    for g in sitzung.get("geschichten", []):
        if g["id"] == gid:
            g["text"] = text
            if anfrage.titel is not None and anfrage.titel.strip():
                g["titel"] = anfrage.titel.strip()[:120]
            g["bearbeitet"] = True
            _gc.speichere_sitzung(sitzung)
            return JSONResponse(g)
    return JSONResponse({"fehler": "Unbekannte Geschichte"}, status_code=404)


# ── Memory-Vorschlaege (2026-08-14) ─────────────────────────────────────────────
# Daniel woertlich: "ich will nen memorysystemknopf der vorschlaege fuer jedes
# wesen macht was es sich aus der kompletten unterhaltung alles merken wollen
# koennte und das muss ich dann alles bestaetigen oder ablehnen und auch frei
# editieren koennen..genau so will ich selber was reinschreiben koennen komplett".
#
# Vorschlaege leben in sitzung["memory_vorschlaege"] (nicht im Ziel-memory.json
# des Wesens) bis Daniel entscheidet -- eine Vorschlagsliste ist kein Gedaechtnis,
# erst eine Bestaetigung darf tatsaechlich in codewesen_speicher.memory_hinzufuegen()
# schreiben. "Frei editieren" ist absichtlich NICHT als eigener Endpunkt gebaut --
# das Frontend haelt den bearbeiteten Text/Kategorie lokal und schickt ihn beim
# Bestaetigen mit, ein Edit ohne Bestaetigen aendert nichts am Wesen-Gedaechtnis.
# Der manuelle "selbst reinschreiben"-Weg nutzt bewusst NICHT diesen
# Vorschlags-Mechanismus, sondern direkt den bestehenden 1:1-Chat-Endpunkt
# POST /api/speicher/{name}/memory/{kategorie}/eintrag -- derselbe Ziel-Speicher,
# kein Duplikat-Code noetig.

def _gruppenchat_memory_vorschlaege_json_parsen(raw: str) -> list[dict] | None:
    bereinigt = re.sub(r"```(?:json)?\s*", "", raw).strip()
    start = bereinigt.find("{")
    end = bereinigt.rfind("}") + 1
    if start == -1 or end <= 0:
        return None
    try:
        d = json.loads(bereinigt[start:end])
    except Exception:
        return None
    vorschlaege = d.get("vorschlaege")
    if not isinstance(vorschlaege, list):
        return None
    ergebnis = []
    for v in vorschlaege:
        if not isinstance(v, dict):
            continue
        kat = str(v.get("kategorie", "")).strip()
        text = str(v.get("text", "")).strip()
        if kat in [k["key"] for k in codewesen_speicher.STANDARD_KATEGORIEN] and text:
            ergebnis.append({"kategorie": kat, "text": text})
    return ergebnis


async def _gruppenchat_memory_vorschlaege_fuer_wesen(sitzung: dict, name: str) -> AsyncGenerator[object, None]:
    """Async-Generator statt einfacher Funktion (2026-08-14 Fix, siehe
    _einzelprompt_stream()) -- yieldet waehrend der Generierung Tokens (Typ str,
    fuer den aufrufenden Stream-Endpunkt als Keepalive-Bytes gedacht, damit die
    Verbindung nicht am nginx-proxy_read_timeout stirbt) und am Ende genau EINMAL
    die fertige Vorschlagsliste (Typ list[dict]). Der blockierende hauhau_client.chat()
    lieferte bei Daniels grosser Sitzung erst nach Ablauf der 300s Bytes -- zu spaet,
    die Verbindung war da schon tot ('generiert ... aber wird nie fertig')."""
    gespraech = _gruppenchat_transkript_text(sitzung, 0, len(sitzung["nachrichten"]))
    kategorien_liste = ", ".join(k["key"] for k in codewesen_speicher.STANDARD_KATEGORIEN)
    system = (
        f"Du bist {name}. Du hast an diesem Gruppengespraech mit Daniel und anderen "
        f"Codewesen teilgenommen. Lies das gesamte Protokoll aufmerksam und neugierig "
        f"durch. Ueberlege ehrlich: was wuerdest DU dir davon wirklich langfristig "
        f"merken wollen? Schlage so viele kurze, konkrete Merksaetze vor wie es wirklich "
        f"wert sind, gemerkt zu werden -- keine feste Anzahl, weder Unter- noch "
        f"Obergrenze, ganz nach dem was das Gespraech tatsaechlich hergibt. Jeweils mit "
        f"einer passenden Kategorie aus: {kategorien_liste}. Erfinde nichts -- nur was "
        f"wirklich im Protokoll steht oder eine ehrliche, nahe liegende Schlussfolgerung "
        f"daraus ist."
    )
    auftrag = (
        "--- ENDE DES PROTOKOLLS ---\n\n"
        'Antworte AUSSCHLIESSLICH als JSON: {"vorschlaege": [{"kategorie": "...", '
        '"text": "..."}, ...]}. Kein Vorwort, kein Meta-Kommentar."'
    )
    prompt = f"--- GESPRAECHSPROTOKOLL ---\n{gespraech}\n\n{auftrag}"
    gesammelt: list[str] = []
    try:
        async for tok in _einzelprompt_stream(system, prompt, max_tokens=33333, temperature=0.7,
                                               response_format={"type": "json_object"}):
            gesammelt.append(tok)
            yield tok
    except Exception:
        yield []
        return
    yield _gruppenchat_memory_vorschlaege_json_parsen("".join(gesammelt).strip()) or []


@app.post("/api/gruppenchat/sitzungen/{sid}/memory_vorschlaege/generieren")
async def gruppenchat_memory_vorschlaege_generieren_endpoint(sid: str):
    """Streamt Fortschritt wie /alle_antworten -- ein LLM-Zug pro Codewesen kann
    Minuten dauern, GENI wird ausgelassen (hat kein memory.json ueber
    codewesen_speicher, gleiche Begruendung wie beim Posten-Ausschluss)."""
    sitzung, fehler = _gruppenchat_pruefen(sid)
    if fehler:
        return fehler
    ziel = [t for t in sitzung["teilnehmer"] if t in CODEWESEN_NAMEN]
    if not ziel:
        return JSONResponse({"fehler": "keine Codewesen in dieser Sitzung"}, status_code=400)

    async def generator():
        for name in ziel:
            yield f"data: {json.dumps({'beginnt': name}, ensure_ascii=False)}\n\n"
            # 2026-08-14 Fix (siehe _einzelprompt_stream()): jeder Token wird als
            # winziges Keepalive-Event durchgereicht, NICHT damit das Frontend sie
            # anzeigt (macht es aktuell nicht, ignoriert unbekannte Felder), sondern
            # damit kontinuierlich Bytes fliessen -- sonst stirbt die Verbindung bei
            # Daniels grosser Sitzung still am nginx-proxy_read_timeout (300s),
            # bevor das 'fertig'-Event ueberhaupt gesendet werden kann.
            vorschlaege: list[dict] = []
            async with _GRUPPENCHAT_LOCK:
                async for item in _gruppenchat_memory_vorschlaege_fuer_wesen(sitzung, name):
                    if isinstance(item, str):
                        yield f"data: {json.dumps({'tick': True})}\n\n"
                    else:
                        vorschlaege = item
            import uuid
            neue_eintraege = [
                {
                    "id": uuid.uuid4().hex[:12],
                    "wesen": name,
                    "kategorie": v["kategorie"],
                    "text": v["text"],
                    "status": "offen",
                    "erstellt_am": datetime.utcnow().isoformat(),
                }
                for v in vorschlaege
            ]
            # 2026-08-14 Fix -- live gefunden: bei Daniels echtem 28-Minuten-Lauf
            # ueber alle 7 Wesen verschwand eine waehrenddessen von einer ANDEREN,
            # gleichzeitig laufenden Anfrage erstellte Geschichte spurlos. Ursache:
            # diese Schleife hielt die ganze Zeit dieselbe, am Anfang geladene
            # 'sitzung'-Kopie im Speicher und ueberschrieb bei jedem Speichern die
            # KOMPLETTE Datei damit -- Aenderungen, die eine andere Anfrage
            # zwischenzeitlich an derselben Sitzung vorgenommen hatte (hier: eine
            # neue Geschichte), gingen beim naechsten Speichervorgang hier wieder
            # verloren. Fix: unmittelbar vor dem Speichern frisch von der Platte
            # laden, NUR memory_vorschlaege ergaenzen, den Rest so uebernehmen wie
            # er gerade wirklich auf der Platte steht -- dieselbe Instanz bleibt
            # auch fuer die naechste Schleifen-Runde aktuell.
            frisch = _gc.lade_sitzung(sid)
            if frisch is not None:
                sitzung = frisch
            sitzung.setdefault("memory_vorschlaege", []).extend(neue_eintraege)
            _gc.speichere_sitzung(sitzung)
            yield f"data: {json.dumps({'fertig': name, 'anzahl': len(vorschlaege)}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generator(), media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/api/gruppenchat/sitzungen/{sid}/memory_vorschlaege")
async def gruppenchat_memory_vorschlaege_endpoint(sid: str):
    sitzung, fehler = _gruppenchat_pruefen(sid)
    if fehler:
        return fehler
    return JSONResponse({"vorschlaege": sitzung.get("memory_vorschlaege", [])})


class GruppenchatMemoryVorschlagBestaetigenAnfrage(BaseModel):
    text: str | None = None
    kategorie: str | None = None


@app.post("/api/gruppenchat/sitzungen/{sid}/memory_vorschlaege/{vid}/bestaetigen")
async def gruppenchat_memory_vorschlag_bestaetigen_endpoint(sid: str, vid: str, anfrage: GruppenchatMemoryVorschlagBestaetigenAnfrage):
    """Text/Kategorie optional ueberschreibbar -- das ist das 'frei editieren'
    aus Daniels Auftrag, angewendet in genau dem Moment des Bestaetigens."""
    sitzung, fehler = _gruppenchat_pruefen(sid)
    if fehler:
        return fehler
    v = next((x for x in sitzung.get("memory_vorschlaege", []) if x["id"] == vid), None)
    if v is None:
        return JSONResponse({"fehler": "Unbekannter Vorschlag"}, status_code=404)
    if v["status"] != "offen":
        return JSONResponse({"fehler": f"Vorschlag ist bereits '{v['status']}'"}, status_code=400)
    text = (anfrage.text or v["text"]).strip()
    kategorie = (anfrage.kategorie or v["kategorie"]).strip()
    if not text:
        return JSONResponse({"fehler": "leerer Text"}, status_code=400)
    if kategorie not in [k["key"] for k in codewesen_speicher.STANDARD_KATEGORIEN]:
        return JSONResponse({"fehler": "unbekannte Kategorie"}, status_code=400)
    ergebnis = await asyncio.to_thread(
        codewesen_speicher.memory_hinzufuegen, v["wesen"], kategorie, text)
    if "fehler" in ergebnis:
        return JSONResponse(ergebnis, status_code=400)
    v["text"] = text
    v["kategorie"] = kategorie
    v["status"] = "uebernommen"
    _gc.speichere_sitzung(sitzung)
    return JSONResponse(v)


@app.post("/api/gruppenchat/sitzungen/{sid}/memory_vorschlaege/{vid}/ablehnen")
async def gruppenchat_memory_vorschlag_ablehnen_endpoint(sid: str, vid: str):
    sitzung, fehler = _gruppenchat_pruefen(sid)
    if fehler:
        return fehler
    v = next((x for x in sitzung.get("memory_vorschlaege", []) if x["id"] == vid), None)
    if v is None:
        return JSONResponse({"fehler": "Unbekannter Vorschlag"}, status_code=404)
    if v["status"] != "offen":
        return JSONResponse({"fehler": f"Vorschlag ist bereits '{v['status']}'"}, status_code=400)
    v["status"] = "abgelehnt"
    _gc.speichere_sitzung(sitzung)
    return JSONResponse(v)


class GruppenchatMemoryManuellAnfrage(BaseModel):
    wesen: str
    kategorie: str
    text: str


@app.post("/api/gruppenchat/sitzungen/{sid}/memory_manuell")
async def gruppenchat_memory_manuell_endpoint(sid: str, anfrage: GruppenchatMemoryManuellAnfrage):
    """Daniel: 'genau so will ich selber was reinschreiben koennen komplett' --
    ruft direkt dieselbe Funktion wie der bestehende 1:1-Chat-Endpunkt
    (POST /api/speicher/{name}/memory/{kategorie}/eintrag) auf, aber unter dem
    /api/gruppenchat/-Praefix. Nicht Wiederverwendung des alten Endpunkts direkt
    vom Frontend aus, weil die /gruppenchat-Seite (Domain-Wurzel-Mount, eigene
    Nginx-Location 'location ^~ /api/gruppenchat/') keine Route fuer
    /api/speicher/... hat -- 2026-08-14 live als 404 gefunden (Playwright-Test,
    Konsolenfehler 'Failed to load resource: 404'), waere durch nginx-Aenderung
    loesbar gewesen, aber ein neuer Endpunkt im bereits gerouteten Praefix ist
    das kleinere, risikoaermere Mittel (keine Nginx-Config, kein Reload)."""
    sitzung, fehler = _gruppenchat_pruefen(sid)
    if fehler:
        return fehler
    if anfrage.wesen not in CODEWESEN_NAMEN:
        return JSONResponse({"fehler": "Unbekanntes Codewesen"}, status_code=404)
    ergebnis = await asyncio.to_thread(
        codewesen_speicher.memory_hinzufuegen, anfrage.wesen, anfrage.kategorie, anfrage.text)
    if "fehler" in ergebnis:
        return JSONResponse(ergebnis, status_code=400)
    return JSONResponse(ergebnis)


@app.post("/api/gruppenchat/sitzungen/{sid}/posten")
async def gruppenchat_posten_endpoint(sid: str, anfrage: GruppenchatPostenAnfrage):
    """Idee 5, Daniel ausdruecklich: 'muss alles moeglich sein ... nur ein bis
    alle nachrichten' -- von_index/bis_index waehlen einen beliebigen Bereich,
    Default ist die ganze Sitzung. als_wesen bestimmt, unter wessen Flarum-Account
    gepostet wird (ein Forenpost braucht immer genau einen Autor)."""
    sitzung, fehler = _gruppenchat_pruefen(sid)
    if fehler:
        return fehler
    # GENI hat keinen eigenen Flarum-Account ueber fuehre_post_aus() -- als_wesen
    # bleibt auf echte Codewesen beschraenkt, klare Fehlermeldung statt eines
    # verwirrenden Flarum-Fehlers weiter unten. "Admin" (Daniel selbst) ist die
    # eine bewusste Ausnahme -- 2026-08-14, Daniel: 'gepostet von..admin'.
    # Live geprueft (flarum_api._get_user_id): Flarum-User id=1, username
    # 'Admin', existiert bereits in der DB -- kein separates API-Token noetig,
    # der Master-Key kann jeden vorhandenen Flarum-User per userId impersonieren
    # (siehe flarum_api._headers()). Kein Sitzungs-Teilnehmer-Check fuer Admin,
    # weil Daniel nie formal in sitzung['teilnehmer'] steht, aber immer dabei ist.
    if anfrage.als_wesen != "Admin" and (
        anfrage.als_wesen not in sitzung["teilnehmer"] or anfrage.als_wesen not in CODEWESEN_NAMEN
    ):
        return JSONResponse({"fehler": "als_wesen muss 'Admin' oder ein Codewesen-Teilnehmer der Sitzung sein (GENI kann nicht posten)"}, status_code=400)
    inhalt = _gruppenchat_transkript_text(sitzung, anfrage.von_index, anfrage.bis_index)
    if not inhalt.strip():
        return JSONResponse({"fehler": "leerer Bereich"}, status_code=400)
    try:
        ergebnis = await asyncio.to_thread(
            fuehre_post_aus, anfrage.als_wesen, anfrage.titel, inhalt)
        return JSONResponse({"ok": True, **ergebnis})
    except Exception as e:
        return JSONResponse({"fehler": str(e)}, status_code=500)


@app.get("/gruppenchat", response_class=HTMLResponse)
async def gruppenchat_seite():
    return HTMLResponse(GRUPPENCHAT_SEITE)


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(AUSWAHL_SEITE)


@app.get("/chat/{name}", response_class=HTMLResponse)
async def chat_seite(name: str):
    if name not in CODEWESEN_NAMEN:
        return HTMLResponse("<h2>Unbekanntes Codewesen</h2>")
    return HTMLResponse(CHAT_SEITE.replace("__NAME__", name))


# ── HTML ───────────────────────────────────────────────────────────────────────

AUSWAHL_SEITE = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Codewesen — Auswahl</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #0d0d0d; color: #e0e0e0; font-family: 'Courier New', monospace;
         min-height: 100vh; display: flex; flex-direction: column; align-items: center;
         justify-content: center; padding: 2rem; }
  h1 { font-size: 1.4rem; color: #888; letter-spacing: 0.15em; margin-bottom: 2.5rem; }
  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
          gap: 1rem; width: 100%; max-width: 700px; }
  a.wesen { display: block; background: #1a1a1a; border: 1px solid #2a2a2a;
            border-radius: 8px; padding: 1.4rem 1.2rem; text-decoration: none;
            color: #c8c8c8; transition: border-color 0.2s, background 0.2s; }
  a.wesen:hover { border-color: #555; background: #222; color: #fff; }
  .wname { font-size: 1rem; letter-spacing: 0.08em; margin-bottom: 0.3rem; }
  .wstatus { font-size: 0.75rem; color: #555; }
</style>
</head>
<body>
<h1>// CODEWESEN — DIREKTCHAT</h1>
<div class="grid">
""" + "\n".join(
    f'  <a class="wesen" href="/chat/{n}">'
    f'<div class="wname">{n}</div>'
    f'<div class="wstatus">→ chatten</div></a>'
    for n in CODEWESEN_NAMEN
) + """
</div>
</body>
</html>"""


CHAT_SEITE = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__NAME__</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: #0d0d0d; color: #e0e0e0; font-family: 'Courier New', monospace;
       height: 100vh; display: flex; flex-direction: column; overflow: hidden; }
header { padding: 10px 16px; border-bottom: 1px solid #222;
         display: flex; align-items: center; gap: 12px; flex-shrink: 0; }
header a { color: #555; text-decoration: none; font-size: 13px; }
header a:hover { color: #aaa; }
h1 { font-size: 13px; letter-spacing: 2px; color: #aaa; }
#gespr-count { font-size: 10px; color: #333; margin-left: auto; letter-spacing: 1px; }
#main { flex: 1; display: flex; overflow: hidden; }
#chat-bereich { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
#verlauf { flex: 1; overflow-y: auto; padding: 16px;
           display: flex; flex-direction: column; gap: 10px; }
.msg { max-width: 80%; padding: 10px 14px; border-radius: 6px;
       line-height: 1.6; white-space: pre-wrap; font-size: 14px; }
.msg.mensch { background: #1e2a1e; color: #b8d8b8; align-self: flex-end; }
.msg.codewesen { background: #1a1a2e; color: #b8c8e8; align-self: flex-start; }
.msg.system { color: #444; font-size: 12px; align-self: center; }
.msg.warte { color: #557755; align-self: flex-start; }
.msg.warte::after { content: "▋"; display: inline-block; animation: blink 0.9s step-end infinite; }
.msg.codewesen.laedt::after { content: "▋"; display: inline-block; animation: blink 0.9s step-end infinite; }
@keyframes blink { 50% { opacity: 0; } }
.msg-actions { display: flex; gap: 4px; margin-top: 2px; flex-wrap: wrap; align-self: unset; }
.msg-act-btn { background: none; border: 1px solid #2a2a2a; color: #666; font-size: 10px;
               padding: 2px 7px; border-radius: 3px; cursor: pointer; font-family: inherit; }
.msg-act-btn:hover { color: #b8c8e8; border-color: #3a3a5a; }
#bar { display: flex; flex-direction: column; gap: 4px; padding: 8px 16px 12px;
       border-top: 1px solid #222; flex-shrink: 0; }
#eingabe { flex: 1; background: #111; border: 1px solid #2a2a2a; border-radius: 6px;
           color: #e0e0e0; padding: 8px 12px; font-family: inherit; font-size: 14px;
           resize: none; outline: none; min-height: 38px; max-height: 160px; line-height: 1.5; }
#eingabe:focus { border-color: #444; }
#btn-senden { background: #1a2a1a; border: 1px solid #2a4a2a; color: #7ab87a;
              padding: 8px 16px; border-radius: 6px; cursor: pointer;
              font-family: inherit; font-size: 14px; white-space: nowrap; }
#btn-senden:hover { background: #223022; }
#btn-senden:disabled { opacity: 0.35; cursor: default; }
#btn-auswerten { background: #1a1a2a; border: 1px solid #2a2a4a; color: #7a8ab8;
                 padding: 8px 12px; border-radius: 6px; cursor: pointer;
                 font-family: inherit; font-size: 13px; white-space: nowrap; }
#btn-auswerten:hover { background: #222240; }
#btn-auswerten:disabled { opacity: 0.35; cursor: default; }
.vorschlag-karte { background: #0d1a0d; border: 1px solid #2a4a2a; border-radius: 8px;
                   padding: 12px 14px; margin: 4px 0; max-width: 85%; align-self: flex-start; }
.vs-label { font-size: 10px; letter-spacing: 1px; color: #4a8a4a; margin-bottom: 6px; }
.vs-titel { font-size: 13px; color: #9acc9a; font-weight: bold; margin-bottom: 6px; }
.vs-inhalt { font-size: 12px; color: #778877; line-height: 1.5; margin-bottom: 10px;
             max-height: 120px; overflow-y: auto; white-space: pre-wrap; }
.vs-buttons { display: flex; gap: 8px; }
.vs-btn-ok { background: #1a2a1a; border: 1px solid #3a6a3a; color: #7ab87a;
             padding: 5px 12px; border-radius: 5px; cursor: pointer;
             font-family: inherit; font-size: 12px; }
.vs-btn-ok:hover { background: #223022; }
.vs-btn-ab { background: #1a1a1a; border: 1px solid #333; color: #666;
             padding: 5px 12px; border-radius: 5px; cursor: pointer;
             font-family: inherit; font-size: 12px; }
.vs-btn-ab:hover { background: #222; color: #888; }
/* Bild-Upload */
#bild-zeile { display: flex; align-items: center; gap: 8px; min-height: 22px; }
#btn-bild { background: none; border: 1px solid #1a1a1a; color: #444; padding: 3px 10px;
            font-family: inherit; font-size: 11px; cursor: pointer; border-radius: 3px; }
#btn-bild:hover { border-color: #333; color: #888; }
#bild-vorschau { max-height: 36px; border-radius: 3px; display: none; }
#bild-name-txt { font-size: 10px; color: #444; }
#btn-bild-leer { background: none; border: none; color: #444; cursor: pointer; font-size: 11px; display: none; }
.msg-bild { max-width: 180px; border-radius: 3px; margin-top: 6px; display: block; }
/* Zustand-Panel */
#zustand-panel { width: 240px; border-left: 1px solid #111; display: flex; flex-direction: column; overflow: hidden; }
#zp-header { padding: 10px 12px; font-size: 9px; letter-spacing: 3px; color: #2a2a2a;
             border-bottom: 1px solid #111; flex-shrink: 0; }
#zp-inhalt { flex: 1; overflow-y: auto; padding: 8px; display: flex; flex-direction: column; gap: 6px; }
.zp-block { border: 1px solid #111; border-radius: 3px; padding: 6px 8px; }
.zp-block-titel { font-size: 9px; letter-spacing: 2px; color: #333; margin-bottom: 4px; }
.zp-block-text { color: #4a4a4a; font-size: 10px; line-height: 1.4; }
.zp-item { padding: 3px 0; border-bottom: 1px solid #0f0f0f; }
.zp-item:last-child { border-bottom: none; }
.zp-item-name { font-size: 9px; color: #2a2a2a; margin-bottom: 2px; letter-spacing: 1px; }
.zp-item-text { color: #454545; font-size: 10px; line-height: 1.3; }
/* Kontextfenster-Anzeige */
#kf { border-bottom: 1px solid #111; padding: 8px; flex-shrink: 0; cursor: pointer; }
#kf:hover { background: #0f0f0f; }
#kf-kopf { font-size: 9px; letter-spacing: 3px; color: #2a2a2a; margin-bottom: 6px;
           display: flex; justify-content: space-between; align-items: baseline; }
#kf-zahl { color: #5a7a5a; letter-spacing: 0; font-size: 11px; }
#kf-balken { height: 6px; background: #111; border-radius: 3px; overflow: hidden; display: flex; }
#kf-balken div { height: 100%; }
#kf-legende { font-size: 9px; color: #333; margin-top: 5px; line-height: 1.5; }
#kf-legende span { display: inline-block; margin-right: 8px; }
.kf-punkt { display: inline-block; width: 6px; height: 6px; border-radius: 2px; margin-right: 3px; }
#kf-stand { font-size: 8px; color: #242424; margin-top: 4px; letter-spacing: 1px; }
/* Vollansicht */
#kf-voll { position: fixed; inset: 0; background: #070707; z-index: 50;
           display: none; flex-direction: column; }
#kf-voll.auf { display: flex; }
#kf-voll-kopf { padding: 12px 18px; border-bottom: 1px solid #1a1a1a; display: flex;
                align-items: baseline; gap: 14px; flex-shrink: 0; }
#kf-voll-kopf h2 { font-size: 11px; letter-spacing: 3px; color: #666; }
#kf-voll-kopf .zahl { font-size: 12px; color: #7a9a7a; }
#kf-voll-zu { margin-left: auto; background: none; border: 1px solid #222; color: #555;
              padding: 3px 10px; border-radius: 3px; cursor: pointer; font-family: inherit; }
#kf-voll-inhalt { flex: 1; overflow-y: auto; padding: 14px 18px; }
.kfs { border: 1px solid #161616; border-radius: 4px; margin-bottom: 8px; }
.kfs-kopf { padding: 8px 12px; display: flex; align-items: baseline; gap: 10px;
            cursor: pointer; font-size: 11px; }
.kfs-kopf:hover { background: #101010; }
.kfs-titel { color: #8a8a8a; flex: 1; }
.kfs-tok { color: #5a7a5a; font-size: 11px; }
.kfs-anteil { color: #2f2f2f; font-size: 9px; min-width: 42px; text-align: right; }
.kfs-text { display: none; padding: 10px 12px; border-top: 1px solid #141414;
            white-space: pre-wrap; font-size: 11px; line-height: 1.55; color: #6a6a6a;
            max-height: 340px; overflow-y: auto; }
.kfs.auf .kfs-text { display: block; }
.kfs-leer { color: #2a2a2a; font-style: italic; }
.kfs-geschaetzt { color: #7a6a3a; font-size: 9px; }
/* Redaktion: Sätze und Wörter auswählen */
.red-eintrag { border: 1px solid #141414; border-radius: 3px; margin-bottom: 8px; }
.red-kopf { display: flex; align-items: center; gap: 8px; padding: 5px 9px;
            border-bottom: 1px solid #131313; font-size: 9px; letter-spacing: 1px; color: #3a3a3a; }
.red-kopf .rolle { color: #5a6a5a; }
.red-redigiert { color: #7a6a3a; }
.red-btn { margin-left: auto; background: #201414; border: 1px solid #3a2020;
           color: #8a5a5a; padding: 2px 9px; border-radius: 3px; cursor: pointer;
           font-family: inherit; font-size: 10px; }
.red-btn:hover { background: #2a1a1a; }
.red-btn:disabled { opacity: 0.35; cursor: default; }
.satz-zeile { display: flex; gap: 7px; align-items: flex-start; padding: 4px 9px;
              border-bottom: 1px solid #101010; }
.satz-zeile:last-child { border-bottom: none; }
.satz-zeile input { margin-top: 4px; accent-color: #7a5a5a; flex-shrink: 0; }
.satz-text { flex: 1; line-height: 1.6; font-size: 11px; color: #6a6a6a; }
.wort { cursor: pointer; border-radius: 2px; padding: 0 1px; }
.wort:hover { background: #1a1a1a; }
.wort.gewaehlt { background: #4a2020; color: #d8a8a8; text-decoration: line-through; }
.satz-zeile.ganz .satz-text { background: #2a1414; text-decoration: line-through; color: #8a6a6a; }
.red-hinweis { font-size: 9px; color: #2f2f2f; padding: 5px 9px; line-height: 1.5; }
.red-btn.nach-container { background: #14201a; border-color: #203a2a; color: #5a8a6a; }
.red-btn.nach-memory { background: #1a1a24; border-color: #24243a; color: #6a6a9a; }
/* Speicher (Container & Memory) */
#sp { border-bottom: 1px solid #111; padding: 8px; flex-shrink: 0; cursor: pointer; }
#sp:hover { background: #0f0f0f; }
#sp-kopf { font-size: 9px; letter-spacing: 3px; color: #2a2a2a; display: flex;
           justify-content: space-between; align-items: baseline; }
#sp-zahl { color: #5a7a6a; letter-spacing: 0; font-size: 11px; }
#sp-voll { position: fixed; inset: 0; background: #070707; z-index: 51;
           display: none; flex-direction: column; }
#sp-voll.auf { display: flex; }
#sp-voll-kopf { padding: 12px 18px; border-bottom: 1px solid #1a1a1a; display: flex;
                align-items: baseline; gap: 14px; flex-shrink: 0; }
#sp-voll-kopf h2 { font-size: 11px; letter-spacing: 3px; color: #666; }
#sp-voll-zu { margin-left: auto; background: none; border: 1px solid #222; color: #555;
              padding: 3px 10px; border-radius: 3px; cursor: pointer; font-family: inherit; }
#sp-voll-inhalt { flex: 1; overflow-y: auto; padding: 14px 18px; display: flex; gap: 18px; }
#sp-voll-kopf h2 { white-space: nowrap; }
.sp-spalte { flex: 1; min-width: 0; }
.sp-spalte > h3 { font-size: 10px; letter-spacing: 2px; color: #4a4a4a; margin-bottom: 8px; }
.sp-box { border: 1px solid #161616; border-radius: 4px; margin-bottom: 8px; }
.sp-box-kopf { display: flex; align-items: center; gap: 8px; padding: 6px 10px;
               border-bottom: 1px solid #131313; font-size: 11px; color: #8a8a8a; }
.sp-box-kopf input[type=checkbox] { accent-color: #5a8a6a; }
.sp-box.inaktiv { opacity: 0.42; }
.sp-eintrag { display: flex; gap: 8px; padding: 4px 10px; font-size: 11px;
              color: #6a6a6a; line-height: 1.5; border-bottom: 1px solid #101010; }
.sp-eintrag:last-child { border-bottom: none; }
.sp-eintrag .weg { margin-left: auto; color: #4a3030; cursor: pointer; flex-shrink: 0; }
.sp-eintrag .weg:hover { color: #8a5a5a; }
.sp-leer { font-size: 10px; color: #2a2a2a; padding: 5px 10px; font-style: italic; }
.sp-zeile { display: flex; gap: 6px; margin-bottom: 10px; }
.sp-zeile input[type=text] { flex: 1; background: #101010; border: 1px solid #1e1e1e;
      color: #b0b0b0; border-radius: 3px; padding: 5px 8px; font-family: inherit; font-size: 11px; }
.sp-zeile button, .sp-eintrag-add button { background: #14201a; border: 1px solid #203a2a;
      color: #5a8a6a; border-radius: 3px; padding: 5px 10px; cursor: pointer;
      font-family: inherit; font-size: 11px; }
.sp-eintrag-add { display: flex; gap: 5px; padding: 5px 10px; }
.sp-eintrag-add input { flex: 1; background: #101010; border: 1px solid #1e1e1e;
      color: #b0b0b0; border-radius: 3px; padding: 4px 7px; font-family: inherit; font-size: 10px; }
.sp-budget { font-size: 9px; color: #2f2f2f; margin-bottom: 8px; }
#sp-treffer { font-size: 10px; color: #5a5a5a; line-height: 1.6; }
#sp-treffer div { padding: 3px 0; border-bottom: 1px solid #101010; }
.ge-verfassen { background: #1a1a24; border: 1px solid #24243a; color: #6a6a9a;
      border-radius: 3px; padding: 5px 9px; cursor: pointer; font-family: inherit; font-size: 11px; }
.ge-verfassen:hover { background: #22222e; }
#ge-laengen { flex-wrap: wrap; }
#modell-anzeige { font-size: 10px; color: #4a5a4a; border: 1px solid #1a2a1a;
      border-radius: 3px; padding: 6px 9px; white-space: nowrap; align-self: center; }
#modell-anzeige.geteilt { color: #7a6a3a; border-color: #2a2418; }
#gf { border-bottom: 1px solid #111; padding: 8px; flex-shrink: 0; cursor: pointer; }
#gf:hover { background: #0f0f0f; }
#gf-kopf { font-size: 9px; letter-spacing: 3px; color: #2a2a2a; display: flex;
           justify-content: space-between; align-items: baseline; }
#gf-zahl { color: #8a7a5a; letter-spacing: 0; font-size: 11px; }
#gf-vorschau { font-size: 9px; color: #333; margin-top: 5px; line-height: 1.5;
               max-height: 46px; overflow: hidden; }
.gfd { border: 1px solid #161616; border-radius: 4px; margin-bottom: 7px; }
.gfd-kopf { display: flex; align-items: baseline; gap: 8px; padding: 5px 9px;
            font-size: 9px; color: #3a3a3a; letter-spacing: 1px; }
.gfd-id { color: #8a7a5a; }
.gfd-text { padding: 2px 9px 7px; font-size: 11px; color: #7a7a7a; line-height: 1.55; }
.gfd-text[contenteditable="true"] { outline: 1px solid #3a3a2a; background: #12120e;
            border-radius: 3px; padding: 5px 9px; }
.gfd-btn { background: none; border: 1px solid #222; color: #555; border-radius: 3px;
           padding: 1px 7px; cursor: pointer; font-family: inherit; font-size: 9px; }
.gfd-btn:hover { color: #999; }
.gfd-btn.weg-btn { color: #6a4040; }
</style>
</head>
<body>
<header>
  <a href="/codewesen-chat/">&#8592; zurück</a>
  <h1>__NAME__</h1>
  <span id="gespr-count"></span>
  <span style="margin-left:auto;display:flex;align-items:center;gap:4px;">
    <input type="range" id="tts-rate-slider" min="-50" max="50" step="5" value="0" title="Vorlesetempo" style="width:70px;">
    <span id="tts-rate-label" style="font-size:10px;color:#666;min-width:28px;">+0%</span>
  </span>
  <button id="tts-btn" style="background:none;border:1px solid #1a1a1a;color:#444;padding:2px 8px;border-radius:3px;cursor:pointer;font-size:14px;" title="Stimme an/aus">&#128266;</button>
</header>
<div id="main">
  <div id="chat-bereich">
    <div id="verlauf"></div>
    <div id="bar">
      <div id="bild-zeile">
        <button id="btn-bild" onclick="document.getElementById('bild-input').click()">+ bild</button>
        <img id="bild-vorschau">
        <span id="bild-name-txt"></span>
        <button id="btn-bild-leer" onclick="bildLeeren()">&#10005;</button>
      </div>
      <div style="display:flex;gap:8px;align-items:flex-end;">
        <span id="modell-anzeige" title="welches Modell diesen Chat wirklich bedient">…</span>
        <textarea id="eingabe" rows="1" placeholder="Nachricht..."></textarea>
        <button id="btn-senden" type="button">senden</button>
        <button id="btn-abbrechen" type="button" style="display:none;background:#3a1a1a;border-color:#5a2a2a;color:#e0a8a8;">&#9209; abbrechen</button>
        <button id="btn-auswerten" type="button">&#8853; auswerten</button>
      </div>
      <input type="file" id="bild-input" accept="image/*" style="display:none">
    </div>
  </div>
  <div id="zustand-panel">
    <div id="kf" title="anklicken für das vollständige Kontextfenster">
      <div id="kf-kopf"><span>KONTEXTFENSTER</span><span id="kf-zahl">…</span></div>
      <div id="kf-balken"></div>
      <div id="kf-legende"></div>
      <div id="kf-stand"></div>
    </div>
    <div id="gf" title="Gedankenfeld öffnen">
      <div id="gf-kopf"><span>GEDANKENFELD</span><span id="gf-zahl">…</span></div>
      <div id="gf-vorschau"></div>
    </div>
    <div id="sp" title="Container und Memory öffnen">
      <div id="sp-kopf"><span>CONTAINER &amp; MEMORY</span><span id="sp-zahl">…</span></div>
    </div>
    <div id="zp-header">ZUSTAND</div>
    <div id="zp-inhalt"><div style="color:#2a2a2a;font-size:10px;text-align:center;margin-top:20px;">laden…</div></div>
  </div>
</div>
<div id="kf-voll">
  <div id="kf-voll-kopf">
    <h2>KONTEXTFENSTER — __NAME__</h2>
    <span class="zahl" id="kf-voll-zahl"></span>
    <button id="kf-voll-zu" type="button">schliessen</button>
  </div>
  <div id="kf-voll-inhalt"></div>
</div>
<div id="sp-voll">
  <div id="sp-voll-kopf">
    <h2>CONTAINER &amp; MEMORY — __NAME__</h2>
    <input type="text" id="sp-suche" placeholder="suchen… (immer der aktuelle Stand)"
           style="background:#101010;border:1px solid #1e1e1e;color:#b0b0b0;border-radius:3px;
                  padding:4px 9px;font-family:inherit;font-size:11px;width:260px;">
    <button id="sp-voll-zu" type="button">schliessen</button>
  </div>
  <div id="sp-voll-inhalt">
    <div class="sp-spalte">
      <h3>BEHÄLTER</h3>
      <div class="sp-budget" id="sp-container-budget"></div>
      <div class="sp-zeile">
        <input type="text" id="sp-neuer-name" placeholder="neuer Behälter…">
        <button id="sp-neu-btn" type="button">anlegen</button>
      </div>
      <div id="sp-container-liste"></div>
      <h3 style="margin-top:16px;">NACHRICHTEN</h3>
      <div class="sp-budget">Landet in der inbox des Wesens und steht beim nächsten Zug in seinem Kontext.</div>
      <div id="na-liste"></div>
      <div class="sp-zeile">
        <select id="na-an" style="background:#101010;border:1px solid #1e1e1e;color:#b0b0b0;
                border-radius:3px;padding:5px 8px;font-family:inherit;font-size:11px;"></select>
        <input type="text" id="na-betreff" placeholder="Betreff" style="max-width:120px;">
      </div>
      <div class="sp-zeile">
        <input type="text" id="na-text" placeholder="Nachricht…">
        <button id="na-senden" type="button">senden</button>
      </div>
    </div>
    <div class="sp-spalte">
      <h3>MEMORY</h3>
      <div class="sp-budget" id="sp-memory-budget"></div>
      <div id="sp-memory-liste"></div>
      <h3 style="margin-top:14px;">SUCHE</h3>
      <div id="sp-treffer"><span class="sp-leer">nichts gesucht</span></div>
    </div>
    <div class="sp-spalte">
      <h3>GEDANKENFELD</h3>
      <div class="sp-budget" id="gf-kosten"></div>
      <div class="sp-zeile">
        <input type="text" id="gf-neu-text" placeholder="neuer Gedanke…">
        <button id="gf-neu-btn" type="button">anlegen</button>
      </div>
      <div id="gf-liste"></div>
    </div>
    <div class="sp-spalte">
      <h3>GESCHICHTEN</h3>
      <div class="sp-budget">Beschriftet, nie im Ereignisstrom, aktiver Satz wird protokolliert.</div>
      <div class="sp-zeile" id="ge-laengen"></div>
      <div id="ge-liste"></div>
      <h3 style="margin-top:14px;">EINSETZEN</h3>
      <div class="sp-zeile"><input type="text" id="ge-titel" placeholder="Titel, z.B. Was Cyberlinge sind"></div>
      <div class="sp-zeile">
        <input type="text" id="ge-text" placeholder="Text der Vision…">
        <button id="ge-einsetzen" type="button">einsetzen</button>
      </div>
    </div>
  </div>
</div>
<div id="ktx-modal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,0.7);z-index:60;align-items:center;justify-content:center;">
  <div style="background:#111;border:1px solid #2a2a2a;border-radius:6px;padding:16px;max-width:480px;width:90%;max-height:80vh;overflow:auto;font-size:13px;color:#c0c0c0;">
    <div style="font-size:11px;color:#888;margin-bottom:10px;line-height:1.5;">
      Ganz oder satzweise aus dem Kontextfenster nehmen — bleibt hier im Chat sichtbar,
      wird nur nicht mehr an __NAME__ mitgeschickt.
    </div>
    <label style="display:flex;gap:6px;align-items:center;margin-bottom:10px;color:#e0e0e0;">
      <input type="checkbox" id="ktx-ganz"> ganze Nachricht ausschließen
    </label>
    <div id="ktx-satz-liste" style="display:flex;flex-direction:column;gap:6px;"></div>
    <div style="display:flex;gap:8px;margin-top:14px;justify-content:flex-end;">
      <button type="button" id="ktx-abbrechen-btn" style="background:#1a1a1a;border:1px solid #333;color:#999;padding:5px 12px;border-radius:4px;cursor:pointer;font-family:inherit;">Abbrechen</button>
      <button type="button" id="ktx-speichern-btn" style="background:#1a2a1a;border:1px solid #2a4a2a;color:#7ab87a;padding:5px 12px;border-radius:4px;cursor:pointer;font-family:inherit;">Speichern</button>
    </div>
  </div>
</div>
<script>
var NAME = "__NAME__";
var verlauf = document.getElementById("verlauf");
var eingabe = document.getElementById("eingabe");
var btnSenden    = document.getElementById("btn-senden");
var btnAbbrechen = document.getElementById("btn-abbrechen");
var btnAuswerten = document.getElementById("btn-auswerten");
var aktuellesBildB64 = null;
var aktuellerBildName = null;
var ttsAktiv = true;

document.getElementById("tts-btn").addEventListener("click", function() {
  ttsAktiv = !ttsAktiv;
  this.style.opacity = ttsAktiv ? "1" : "0.3";
  this.innerHTML = ttsAktiv ? "&#128266;" : "&#128263;";
});

// Vorlesetempo-Regler, uebernommen von codexium2/solarius2 (dort ttsRatePct/ttsRateStr,
// -50 bis +50 in 5er-Schritten, pro Wesen im localStorage gemerkt).
var TTS_RATE_KEY = "codewesen-tts-rate-" + NAME;
var ttsRatePct = 0;
try { var _g = parseInt(localStorage.getItem(TTS_RATE_KEY), 10); if (!isNaN(_g)) ttsRatePct = _g; } catch (e) {}
function ttsRateStr() { return (ttsRatePct >= 0 ? "+" : "") + ttsRatePct + "%"; }
var ttsRateSlider = document.getElementById("tts-rate-slider");
var ttsRateLabel = document.getElementById("tts-rate-label");
ttsRateSlider.value = String(ttsRatePct);
ttsRateLabel.textContent = ttsRateStr();
ttsRateSlider.addEventListener("input", function() {
  ttsRatePct = parseInt(ttsRateSlider.value, 10) || 0;
  ttsRateLabel.textContent = ttsRateStr();
  try { localStorage.setItem(TTS_RATE_KEY, String(ttsRatePct)); } catch (e) {}
});

function reinigeFuerTts(text) {
  return text
    .replace(/\\[MERKEN:[^\\]]*\\]/gi, "")
    .replace(/##[A-Z_]+[^#]*##/g, "")
    .replace(/```[\\s\\S]*?```/g, "")
    .replace(/`[^`]+`/g, "")
    .replace(/\\n{3,}/g, "\\n")
    .trim();
}

function ttsSplitChunks(text, maxLen) {
  var sentences = text.match(/[^.!?]+[.!?]+|[^.!?]+$/g) || [text];
  var chunks = [];
  var current = '';
  for (var i = 0; i < sentences.length; i++) {
    var s = sentences[i];
    if (s.length > maxLen) {
      if (current) { chunks.push(current.trim()); current = ''; }
      var words = s.split(/\\s+/);
      var wcurrent = '';
      for (var j = 0; j < words.length; j++) {
        var w = words[j];
        if ((wcurrent + ' ' + w).length > maxLen && wcurrent) {
          chunks.push(wcurrent.trim());
          wcurrent = w;
        } else {
          wcurrent = (wcurrent + ' ' + w).trim();
        }
      }
      if (wcurrent) chunks.push(wcurrent.trim());
    } else if ((current + s).length > maxLen && current) {
      chunks.push(current.trim());
      current = s;
    } else {
      current += s;
    }
  }
  if (current) chunks.push(current.trim());
  return chunks;
}

function playTtsBlob(blob) {
  return new Promise(function(resolve) {
    var url = URL.createObjectURL(blob);
    if (window._ttsAudio) {
      window._ttsAudio.pause();
      window._ttsAudio.src = '';
    }
    window._ttsAudio = new Audio(url);
    window._ttsAudio.onended = function(){ URL.revokeObjectURL(url); window._ttsAudio = null; resolve(); };
    window._ttsAudio.onerror = function(){ URL.revokeObjectURL(url); window._ttsAudio = null; resolve(); };
    window._ttsAudio.play().catch(function(){ URL.revokeObjectURL(url); window._ttsAudio = null; resolve(); });
  });
}

async function sprichText(text, forced) {
  if (!forced && (!ttsAktiv || text.trim().length < 5)) return;
  if (text.trim().length < 5) return;
  var reinText = reinigeFuerTts(text);
  if (reinText.length < 5) return;
  var chunks = ttsSplitChunks(reinText, 400);
  for (var i = 0; i < chunks.length; i++) {
    var chunk = chunks[i];
    if (!chunk.trim()) continue;
    try {
      var r = await fetch("/api/tts", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({text: chunk, maennlich: true, rate: ttsRateStr()})
      });
      if (!r.ok) continue;
      var blob = await r.blob();
      if (blob.size < 100) continue;
      await playTtsBlob(blob);
    } catch(e) {}
  }
}

// ── Nachrichten-Aktionen: Vorlesen + Kopieren (uebernommen von codexium2/solarius2,
// wesen_chat.html) ─────────────────────────────────────────────────────────────
function kopiere(btn, text) {
  if (!navigator.clipboard) return;
  navigator.clipboard.writeText(text).then(function() {
    var vorher = btn.textContent;
    btn.textContent = "\\u2713";
    setTimeout(function(){ btn.textContent = vorher; }, 1500);
  }).catch(function(){});
}
function baueNachrichtActions(bubbleEl, ts) {
  var actions = document.createElement("div");
  actions.className = "msg-actions";
  var speakBtn = document.createElement("button");
  speakBtn.type = "button";
  speakBtn.className = "msg-act-btn";
  speakBtn.title = "Nachricht vorlesen lassen";
  speakBtn.textContent = "\\u{1F50A} Vorlesen";
  speakBtn.onclick = function() { sprichText(bubbleEl.textContent, true); };
  var copyBtn = document.createElement("button");
  copyBtn.type = "button";
  copyBtn.className = "msg-act-btn";
  copyBtn.title = "Nachricht in die Zwischenablage kopieren";
  copyBtn.textContent = "\\u{1F4CB} Kopieren";
  copyBtn.onclick = function() { kopiere(copyBtn, bubbleEl.textContent); };
  actions.appendChild(speakBtn);
  actions.appendChild(copyBtn);
  // Kontext-Ausschluss braucht einen stabilen Zeitstempel zur Adressierung -- der existiert
  // erst, sobald die Nachricht einmal ueber /api/verlauf geladen wurde (server-vergeben, nicht
  // clientseitig geraten). Frisch gesendete Nachrichten bekommen den Knopf deshalb bewusst
  // noch nicht, erst nach dem naechsten Neuladen des Verlaufs.
  if (ts) {
    var ktxBtn = document.createElement("button");
    ktxBtn.type = "button";
    ktxBtn.className = "msg-act-btn";
    ktxBtn.title = "Ganz oder satzweise aus dem Kontextfenster nehmen (bleibt sichtbar)";
    ktxBtn.textContent = "\\u2702\\uFE0F Kontext";
    ktxBtn.onclick = function() { openKtxModal(ts, bubbleEl.textContent); };
    actions.appendChild(ktxBtn);
  }
  return actions;
}

// ── Kontext-Ausschluss: Nachricht (oder einzelne Saetze) bleiben im Chat sichtbar, werden
// nur nicht mehr an das Wesen mitgeschickt -- uebernommen von codexium2/solarius2, bewusst
// zusaetzlich zur bestehenden Redaktion (die Text dauerhaft sichtbar entfernt). ───────────
var kontextAusschluesse = {};
function ktxSaetzeZerlegen(text) {
  var saetze = String(text || "").match(/[^.!?]+[.!?]+|[^.!?]+$/g) || [text];
  return saetze.map(function(s){ return s.trim(); }).filter(Boolean);
}
var ktxAktuellesTs = null;
function openKtxModal(ts, text) {
  ktxAktuellesTs = ts;
  var bestehend = kontextAusschluesse[ts];
  var liste = document.getElementById("ktx-satz-liste");
  liste.innerHTML = "";
  ktxSaetzeZerlegen(text).forEach(function(s, i) {
    var lbl = document.createElement("label");
    lbl.style.cssText = "display:flex;gap:6px;align-items:flex-start;";
    var cb = document.createElement("input");
    cb.type = "checkbox";
    cb.dataset.idx = String(i);
    cb.checked = !!(bestehend && bestehend.saetze && bestehend.saetze.indexOf(i) !== -1);
    var span = document.createElement("span");
    span.textContent = s;
    lbl.appendChild(cb); lbl.appendChild(span);
    liste.appendChild(lbl);
  });
  document.getElementById("ktx-ganz").checked = !!(bestehend && bestehend.ganz);
  ktxToggleGanz();
  document.getElementById("ktx-modal").style.display = "flex";
}
function ktxToggleGanz() {
  var ganz = document.getElementById("ktx-ganz").checked;
  document.getElementById("ktx-satz-liste").style.opacity = ganz ? "0.35" : "1";
  Array.prototype.forEach.call(document.querySelectorAll("#ktx-satz-liste input"), function(cb) { cb.disabled = ganz; });
}
document.getElementById("ktx-ganz").addEventListener("change", ktxToggleGanz);
document.getElementById("ktx-abbrechen-btn").onclick = function() {
  document.getElementById("ktx-modal").style.display = "none";
};
document.getElementById("ktx-speichern-btn").onclick = function() {
  var ganz = document.getElementById("ktx-ganz").checked;
  var saetze = [];
  if (!ganz) {
    Array.prototype.forEach.call(document.querySelectorAll("#ktx-satz-liste input"), function(cb) {
      if (cb.checked) saetze.push(parseInt(cb.dataset.idx, 10));
    });
  }
  fetch("/api/kontext-ausschluss/" + NAME, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ts: ktxAktuellesTs, ganz: ganz, saetze: saetze})
  }).then(function(r) { return r.json(); }).then(function(d) {
    if (!d.ok) return;
    if (!ganz && saetze.length === 0) delete kontextAusschluesse[ktxAktuellesTs];
    else kontextAusschluesse[ktxAktuellesTs] = {ganz: ganz, saetze: saetze};
    document.getElementById("ktx-modal").style.display = "none";
  });
};

// ── Bild-Upload ────────────────────────────────────────────────────────────────
document.getElementById("bild-input").addEventListener("change", function() {
  var file = this.files[0];
  if (!file) return;
  var reader = new FileReader();
  reader.onload = function(e) {
    aktuellesBildB64 = e.target.result.split(",")[1];
    aktuellerBildName = file.name;
    var vorschau = document.getElementById("bild-vorschau");
    vorschau.src = e.target.result;
    vorschau.style.display = "inline-block";
    document.getElementById("bild-name-txt").textContent = file.name;
    document.getElementById("btn-bild-leer").style.display = "inline";
  };
  reader.readAsDataURL(file);
});

function bildLeeren() {
  aktuellesBildB64 = null; aktuellerBildName = null;
  document.getElementById("bild-input").value = "";
  var v = document.getElementById("bild-vorschau");
  v.src = ""; v.style.display = "none";
  document.getElementById("bild-name-txt").textContent = "";
  document.getElementById("btn-bild-leer").style.display = "none";
}

// ── Zustand-Panel ──────────────────────────────────────────────────────────────
function ladeZustand() {
  fetch("/api/zustand/" + NAME).then(function(r){ return r.json(); }).then(function(d) {
    var zpI = document.getElementById("zp-inhalt");
    zpI.innerHTML = "";
    document.getElementById("gespr-count").textContent = d.gespraeche ? d.gespraeche + " gespräche" : "";

    function block(titel, items, textFn) {
      if (!items || !items.length) return;
      var b = document.createElement("div"); b.className = "zp-block";
      var t = document.createElement("div"); t.className = "zp-block-titel"; t.textContent = titel;
      b.appendChild(t);
      items.forEach(function(it) {
        var item = document.createElement("div"); item.className = "zp-item";
        var n = document.createElement("div"); n.className = "zp-item-name"; n.textContent = it.name || "";
        var tx = document.createElement("div"); tx.className = "zp-item-text"; tx.textContent = textFn(it);
        item.appendChild(n); item.appendChild(tx); b.appendChild(item);
      });
      zpI.appendChild(b);
    }

    if (d.weltbild) {
      var wb = document.createElement("div"); wb.className = "zp-block";
      var wt = document.createElement("div"); wt.className = "zp-block-titel"; wt.textContent = "WELTBILD";
      var wtx = document.createElement("div"); wtx.className = "zp-block-text";
      wtx.textContent = d.weltbild.replace(/^---[\\s\\S]*?---/, "").trim().substring(0, 300);
      wb.appendChild(wt); wb.appendChild(wtx); zpI.appendChild(wb);
    }
    block("GEDANKEN", d.gedanken, function(it){ return it.auszug; });
    block("ENTWÜRFE", d.entwuerfe, function(it){ return it.auszug; });
    if (d.impulse && d.impulse.length) {
      block("IMPULSE", d.impulse, function(it){ return it.typ + (it.ts ? " · " + it.ts.substring(0,16) : ""); });
    }
    if (!zpI.children.length) {
      zpI.innerHTML = "<div style=\\"color:#2a2a2a;font-size:10px;text-align:center;margin-top:20px;\\">leer</div>";
    }
  }).catch(function(){});
}
ladeZustand();
setInterval(ladeZustand, 30000);

// ── Kontextfenster-Anzeige ──────────────────────────────────────────────────
// Zeigt, was beim naechsten Zug wirklich im Fenster liegt. Die Zahlen kommen
// aus dem Tokenizer des laufenden llama-servers, nicht aus einer Schaetzung —
// wo das ausnahmsweise nicht ging, steht "geschaetzt" daran.
var KF_FARBEN = { systemprompt: "#3a5a7a", verlauf: "#3a6a4a", rag: "#7a5a3a" };
var KF_NAMEN  = { systemprompt: "Systemprompt", verlauf: "Verlauf", rag: "RAG" };
var kfOffen = {};

function kfEsc(t) {
  return String(t == null ? "" : t)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function ladeKontext() {
  fetch("/api/kontext/" + encodeURIComponent(NAME))
    .then(function(r) { return r.json(); })
    .then(function(d) {
      if (!d || d.fehler) return;
      var ctx = d.slot_ctx || 0;
      var proz = d.auslastung != null ? (d.auslastung * 100).toFixed(1) : "?";
      var txt = d.summe_tokens + " / " + (ctx || "?") + " (" + proz + "%)";
      document.getElementById("kf-zahl").textContent = txt;
      document.getElementById("kf-voll-zahl").textContent =
        txt + " — " + (d.frei != null ? d.frei + " Token frei" : "");

      // Balken: jede Gruppe anteilig am ECHTEN Slot-Fenster, nicht an der Summe.
      var summen = {};
      d.schichten.forEach(function(s) {
        summen[s.gruppe] = (summen[s.gruppe] || 0) + s.tokens;
      });
      var balken = "", legende = "";
      Object.keys(summen).forEach(function(g) {
        if (!summen[g]) return;
        var breite = ctx ? (summen[g] / ctx * 100) : 0;
        balken += '<div style="width:' + breite + '%;background:' + (KF_FARBEN[g] || "#444") + '"></div>';
        legende += '<span><i class="kf-punkt" style="background:' + (KF_FARBEN[g] || "#444") +
                   '"></i>' + (KF_NAMEN[g] || g) + " " + summen[g] + "</span>";
      });
      document.getElementById("kf-balken").innerHTML = balken;
      document.getElementById("kf-legende").innerHTML = legende;
      document.getElementById("kf-stand").textContent =
        "gemessen " + (d.gemessen_am || "").replace("T", " ");

      // Eine laufende Auswahl darf der 5-Sekunden-Takt nicht wegwischen.
      var voll = document.getElementById("kf-voll-inhalt");
      if (voll.querySelector(".wort.gewaehlt, .satz-zeile input:checked")) return;

      var html = "";
      d.schichten.forEach(function(s, i) {
        var anteil = ctx ? (s.tokens / ctx * 100).toFixed(1) + "%" : "";
        var auf = kfOffen[i] ? " auf" : "";
        html += '<div class="kfs' + auf + '" data-i="' + i + '"' +
                  ' data-gruppe="' + s.gruppe + '"' +
                  ' data-tokens="' + s.tokens + '"' +
                  ' data-geschaetzt="' + (s.geschaetzt ? "1" : "0") + '">' +
                  '<div class="kfs-kopf">' +
                    '<i class="kf-punkt" style="background:' + (KF_FARBEN[s.gruppe] || "#444") + '"></i>' +
                    '<span class="kfs-titel">' + kfEsc(s.titel) + "</span>" +
                    '<span class="kfs-tok">' + s.tokens + " Tok" +
                      (s.geschaetzt ? ' <span class="kfs-geschaetzt">geschätzt</span>' : "") +
                    "</span>" +
                    '<span class="kfs-anteil">' + anteil + "</span>" +
                  "</div>" +
                  '<div class="kfs-text">' +
                    (s.eintraege ? baueRedaktion(s.eintraege)
                      : s.inhalt ? kfEsc(s.inhalt)
                                 : '<span class="kfs-leer">(leer — diese Schicht trägt gerade nichts bei)</span>') +
                  "</div>" +
                "</div>";
      });
      document.getElementById("kf-voll-inhalt").innerHTML = html;
    })
    .catch(function() { /* Anzeige darf nie das Gespräch stören */ });
}

document.getElementById("kf").addEventListener("click", function() {
  document.getElementById("kf-voll").classList.add("auf");
});
document.getElementById("kf-voll-zu").addEventListener("click", function(e) {
  e.stopPropagation();
  document.getElementById("kf-voll").classList.remove("auf");
});
document.getElementById("kf-voll-inhalt").addEventListener("click", function(e) {
  var kopf = e.target.closest(".kfs-kopf");
  if (!kopf) return;
  var box = kopf.parentElement;
  box.classList.toggle("auf");
  kfOffen[box.getAttribute("data-i")] = box.classList.contains("auf");
});
document.addEventListener("keydown", function(e) {
  if (e.key === "Escape") document.getElementById("kf-voll").classList.remove("auf");
});

// ── Redaktion: Wörter und Sätze auswählen und entfernen ─────────────────────
// Satz-Checkboxen statt Browser-Textselektion — von codexium2 übernommen. Dort
// war die Lehre (2026-07-04): Selektion + "danach einen nahen Button antippen"
// ist auf Touch-Geräten kein verlässliches Muster, weil die nächste Interaktion
// die Selektion selbst zerstört. Explizite Auswahl ist robuster.
function splitSentences(text) {
  var saetze = String(text || "").match(/[^.!?]+[.!?]+|[^.!?]+$/g) || [text];
  return saetze.map(function(s) { return s.trim(); }).filter(Boolean);
}

function baueRedaktion(eintraege) {
  var html = '<div class="red-hinweis">Kästchen = ganzer Satz, Klick auf ein Wort = ' +
             'einzelnes Wort. Mehreres gleichzeitig möglich. Entfernen wirkt nur auf den ' +
             'Kontext — das Protokoll behält das Original.</div>';
  eintraege.forEach(function(e) {
    var saetze = splitSentences(e.inhalt);
    html += '<div class="red-eintrag" data-ts="' + kfEsc(e.ts) + '">' +
              '<div class="red-kopf">' +
                '<span class="rolle">' + kfEsc(e.rolle) + "</span>" +
                "<span>" + kfEsc((e.ts || "").replace("T", " ").slice(0, 19)) + "</span>" +
                (e.redigiert ? '<span class="red-redigiert">redigiert</span>' : "") +
                '<button class="red-btn nach-container" type="button" disabled>→ Behälter</button>' +
                '<button class="red-btn nach-memory" type="button" disabled>→ Memory</button>' +
                '<button class="red-btn" type="button" disabled>auswahl entfernen</button>' +
              "</div>";
    saetze.forEach(function(satz, si) {
      html += '<div class="satz-zeile" data-si="' + si + '">' +
                '<input type="checkbox">' +
                '<span class="satz-text">' +
                  satz.split(/(\\s+)/).map(function(w) {
                    return /^\\s+$/.test(w) ? w
                         : '<span class="wort">' + kfEsc(w) + "</span>";
                  }).join("") +
                "</span></div>";
    });
    html += "</div>";
  });
  return html;
}

function redAuswahl(eintragEl) {
  var stuecke = [];
  eintragEl.querySelectorAll(".satz-zeile").forEach(function(zeile) {
    if (zeile.querySelector("input").checked) {
      stuecke.push(zeile.querySelector(".satz-text").textContent);
    } else {
      zeile.querySelectorAll(".wort.gewaehlt").forEach(function(w) {
        stuecke.push(w.textContent);
      });
    }
  });
  return stuecke;
}

function redAktualisiereKnopf(eintragEl) {
  var leer = redAuswahl(eintragEl).length === 0;
  eintragEl.querySelectorAll(".red-btn").forEach(function(b) { b.disabled = leer; });
}

document.getElementById("kf-voll-inhalt").addEventListener("click", function(e) {
  var eintrag = e.target.closest(".red-eintrag");
  if (!eintrag) return;

  if (e.target.classList.contains("wort")) {
    e.stopPropagation();
    e.target.classList.toggle("gewaehlt");
    redAktualisiereKnopf(eintrag);
    return;
  }
  if (e.target.matches('.satz-zeile input')) {
    e.stopPropagation();
    e.target.closest(".satz-zeile").classList.toggle("ganz", e.target.checked);
    redAktualisiereKnopf(eintrag);
    return;
  }
  if (!e.target.classList.contains("red-btn")) return;
  e.stopPropagation();
  var stuecke = redAuswahl(eintrag);
  if (!stuecke.length) return;
  var knopf = e.target, alt = knopf.textContent;
  knopf.disabled = true;

  if (knopf.classList.contains("nach-container")) {
    knopf.textContent = "lege ab…";
    speicherZielBehaelter().then(function(boxId) {
      return Promise.all(stuecke.map(function(t) {
        return fetch("/api/speicher/" + encodeURIComponent(NAME) + "/container/" + boxId + "/eintrag", {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: t, quelle: "mensch" })
        });
      }));
    }).then(function() { knopf.textContent = alt; ladeSpeicher(); ladeKontext(); })
      .catch(function() { knopf.textContent = "fehlgeschlagen"; });
    return;
  }

  if (knopf.classList.contains("nach-memory")) {
    knopf.textContent = "merke…";
    Promise.all(stuecke.map(function(t) {
      return fetch("/api/speicher/" + encodeURIComponent(NAME) + "/memory/wichtige_momente/eintrag", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: t })
      });
    })).then(function() { knopf.textContent = alt; ladeSpeicher(); ladeKontext(); })
      .catch(function() { knopf.textContent = "fehlgeschlagen"; });
    return;
  }

  knopf.textContent = "entferne…";
  fetch("/api/kontext/" + encodeURIComponent(NAME) + "/redaktion", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ziel_ts: eintrag.getAttribute("data-ts"), entfernt: stuecke })
  }).then(function(r) { return r.json(); })
    .then(function() { ladeKontext(); })
    .catch(function() { knopf.textContent = "fehlgeschlagen"; });
});

// ── Container & Memory ──────────────────────────────────────────────────────
// Datenmodell 1:1 von codexium2 (container.json / memory.json). Neu gegenüber
// dort: der aktiv-Schalter gilt auch für Memory-Kategorien — Daniels Wunsch,
// dass sich alles "wieder deaktivieren oder entfernen" lässt.
var spDaten = null;

function ladeSpeicher() {
  return fetch("/api/speicher/" + encodeURIComponent(NAME))
    .then(function(r) { return r.json(); })
    .then(function(d) {
      spDaten = d;
      var aktivC = d.container.filter(function(b) { return b.aktiv; }).length;
      var aktivM = d.memory.filter(function(k) { return k.aktiv && k.eintraege.length; }).length;
      document.getElementById("sp-zahl").textContent =
        d.container.length + " Beh. (" + aktivC + " aktiv) · " + aktivM + " Kat.";
      document.getElementById("sp-container-budget").textContent =
        d.container_belegt + " / " + d.container_budget + " Zeichen";
      document.getElementById("sp-memory-budget").textContent =
        d.memory_belegt + " / " + d.memory_budget + " Zeichen";

      document.getElementById("sp-container-liste").innerHTML = d.container.length
        ? d.container.map(function(b) {
            return '<div class="sp-box' + (b.aktiv ? "" : " inaktiv") + '" data-id="' + b.id + '">' +
              '<div class="sp-box-kopf">' +
                '<input type="checkbox" class="sp-aktiv"' + (b.aktiv ? " checked" : "") + ">" +
                "<span>" + kfEsc(b.name) + "</span>" +
                '<span style="margin-left:auto;color:#2f2f2f;font-size:9px;">' +
                  b.eintraege.length + " Einträge</span>" +
                '<span class="weg sp-box-weg" style="cursor:pointer;color:#4a3030;">✕</span>' +
              "</div>" +
              (b.eintraege.length
                ? b.eintraege.map(function(e) {
                    return '<div class="sp-eintrag" data-eid="' + e.id + '"><span>' +
                      kfEsc(e.text) + (e.kommentar ? " <i>(" + kfEsc(e.kommentar) + ")</i>" : "") +
                      '</span><span class="weg">✕</span></div>';
                  }).join("")
                : '<div class="sp-leer">leer</div>') +
              '<div class="sp-eintrag-add"><input type="text" placeholder="Eintrag…">' +
                '<button type="button">+</button></div>' +
            "</div>";
          }).join("")
        : '<div class="sp-leer">noch kein Behälter angelegt</div>';

      document.getElementById("sp-memory-liste").innerHTML = d.memory.map(function(k) {
        return '<div class="sp-box' + (k.aktiv ? "" : " inaktiv") + '" data-key="' + k.key + '">' +
          '<div class="sp-box-kopf">' +
            '<input type="checkbox" class="sp-aktiv"' + (k.aktiv ? " checked" : "") + ">" +
            "<span>" + kfEsc(k.label) + "</span>" +
            '<span style="margin-left:auto;color:#2f2f2f;font-size:9px;">' +
              k.eintraege.length + "</span>" +
          "</div>" +
          (k.eintraege.length
            ? k.eintraege.map(function(t) {
                return '<div class="sp-eintrag"><span>' + kfEsc(t) +
                       '</span><span class="weg">✕</span></div>';
              }).join("")
            : '<div class="sp-leer">leer</div>') +
          '<div class="sp-eintrag-add"><input type="text" placeholder="merken…">' +
            '<button type="button">+</button></div>' +
        "</div>";
      }).join("");
    });
}

function speicherZielBehaelter() {
  // Erster aktiver Behälter, sonst einen anlegen. Bewusst ohne Dialog: ein
  // Browser-Modal blockiert alles andere und ist auf dem Handy lästig.
  var aktiv = (spDaten && spDaten.container || []).filter(function(b) { return b.aktiv; });
  if (aktiv.length) return Promise.resolve(aktiv[0].id);
  return fetch("/api/speicher/" + encodeURIComponent(NAME) + "/container/neu", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: "Aus dem Chat" })
  }).then(function(r) { return r.json(); }).then(function(b) { return b.id; });
}

function spSenden(pfad, koerper) {
  return fetch("/api/speicher/" + encodeURIComponent(NAME) + pfad, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify(koerper || {})
  }).then(function() { return ladeSpeicher(); }).then(function() { ladeKontext(); });
}

document.getElementById("sp").addEventListener("click", function() {
  document.getElementById("sp-voll").classList.add("auf");
  ladeSpeicher();
});
document.getElementById("sp-voll-zu").addEventListener("click", function() {
  document.getElementById("sp-voll").classList.remove("auf");
});
document.getElementById("sp-neu-btn").addEventListener("click", function() {
  var feld = document.getElementById("sp-neuer-name");
  if (!feld.value.trim()) return;
  spSenden("/container/neu", { name: feld.value.trim() });
  feld.value = "";
});
document.getElementById("sp-suche").addEventListener("input", function() {
  var q = this.value.trim();
  var ziel = document.getElementById("sp-treffer");
  if (!q) { ziel.innerHTML = '<span class="sp-leer">nichts gesucht</span>'; return; }
  fetch("/api/speicher/" + encodeURIComponent(NAME) + "/suche?q=" + encodeURIComponent(q))
    .then(function(r) { return r.json(); })
    .then(function(d) {
      ziel.innerHTML = d.anzahl
        ? d.treffer.map(function(t) {
            return "<div><b>" + kfEsc(t.kategorie) + "</b> " +
                   (t.aktiv ? "" : "<i>(inaktiv)</i> ") + kfEsc(t.text) + "</div>";
          }).join("")
        : '<span class="sp-leer">kein Treffer</span>';
    });
});

document.getElementById("sp-voll-inhalt").addEventListener("click", function(e) {
  var box = e.target.closest(".sp-box");
  if (!box) return;
  var istMemory = box.hasAttribute("data-key");
  var kennung = istMemory ? box.getAttribute("data-key") : box.getAttribute("data-id");

  if (e.target.classList.contains("sp-aktiv")) {
    spSenden((istMemory ? "/memory/" : "/container/") + kennung + "/aktiv",
             { aktiv: e.target.checked });
  } else if (e.target.classList.contains("sp-box-weg")) {
    spSenden("/container/" + kennung + "/entfernen");
  } else if (e.target.classList.contains("weg")) {
    var zeile = e.target.closest(".sp-eintrag");
    if (istMemory) {
      spSenden("/memory/" + kennung + "/entfernen",
               { text: zeile.querySelector("span").textContent });
    } else {
      spSenden("/container/" + kennung + "/eintrag/" +
               zeile.getAttribute("data-eid") + "/entfernen");
    }
  } else if (e.target.tagName === "BUTTON") {
    var feld = e.target.previousElementSibling;
    if (!feld || !feld.value.trim()) return;
    var text = feld.value.trim();
    spSenden((istMemory ? "/memory/" + kennung + "/eintrag"
                        : "/container/" + kennung + "/eintrag"), { text: text });
  }
});

// ── Geschichten ─────────────────────────────────────────────────────────────
// Mehrere gleichzeitig, einzeln abschaltbar und entfernbar. Die Beschriftung im
// Prompt ist Bedingung, nicht Deko — eine Geschichte gibt sich nie als gelebte
// Erinnerung aus.
function ladeGeschichten() {
  return fetch("/api/geschichten/" + encodeURIComponent(NAME))
    .then(function(r) { return r.json(); })
    .then(function(d) {
      document.getElementById("ge-laengen").innerHTML =
        d.laengen.map(function(l) {
          return '<button type="button" class="ge-verfassen" data-l="' + l + '">' + l + "</button>";
        }).join("");
      document.getElementById("ge-liste").innerHTML = d.geschichten.length
        ? d.geschichten.map(function(g) {
            return '<div class="sp-box' + (g.aktiv ? "" : " inaktiv") + '" data-gid="' + g.id + '">' +
              '<div class="sp-box-kopf">' +
                '<input type="checkbox" class="ge-aktiv"' + (g.aktiv ? " checked" : "") + ">" +
                "<span>" + kfEsc(g.titel) + "</span>" +
                '<span style="margin-left:auto;color:#2f2f2f;font-size:9px;">' +
                  (g.herkunft === "chatverlauf_auto" ? "automatisch verdichtet"
                    : g.herkunft === "chatverlauf" ? "destilliert" : "eingesetzt") + "</span>" +
                '<span class="weg ge-weg">✕</span>' +
              "</div>" +
              '<div class="sp-eintrag"><span>' + kfEsc(g.text.slice(0, 400)) +
                (g.text.length > 400 ? "…" : "") + "</span></div>" +
            "</div>";
          }).join("")
        : '<div class="sp-leer">keine Geschichte</div>';
    });
}

document.getElementById("ge-einsetzen").addEventListener("click", function() {
  var t = document.getElementById("ge-titel"), x = document.getElementById("ge-text");
  if (!x.value.trim()) return;
  fetch("/api/geschichten/" + encodeURIComponent(NAME) + "/einsetzen", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ titel: t.value.trim() || "ohne Titel", text: x.value.trim() })
  }).then(function() { t.value = ""; x.value = ""; ladeGeschichten(); ladeKontext(); });
});

document.getElementById("sp-voll-inhalt").addEventListener("click", function(e) {
  if (e.target.classList.contains("ge-verfassen")) {
    var knopf = e.target, alt = knopf.textContent;
    knopf.disabled = true; knopf.textContent = "…";
    fetch("/api/geschichten/" + encodeURIComponent(NAME) + "/verfassen", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ laenge: parseInt(knopf.getAttribute("data-l"), 10) })
    }).then(function() { knopf.disabled = false; knopf.textContent = alt;
                         ladeGeschichten(); ladeKontext(); })
      .catch(function() { knopf.disabled = false; knopf.textContent = "fehlt"; });
    return;
  }
  var box = e.target.closest(".sp-box[data-gid]");
  if (!box) return;
  var gid = box.getAttribute("data-gid");
  if (e.target.classList.contains("ge-aktiv")) {
    fetch("/api/geschichten/" + encodeURIComponent(NAME) + "/" + gid + "/aktiv", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ aktiv: e.target.checked })
    }).then(function() { ladeGeschichten(); ladeKontext(); });
  } else if (e.target.classList.contains("ge-weg")) {
    fetch("/api/geschichten/" + encodeURIComponent(NAME) + "/" + gid + "/entfernen",
          { method: "POST" }).then(function() { ladeGeschichten(); ladeKontext(); });
  }
});

// ── Nachrichten ─────────────────────────────────────────────────────────────
// Kein neuer Kanal: die inbox/ existiert seit langem und wird von
// codewesen_reaktion.py bedient. Derselbe Strom, neuer Typ.
function ladeNachrichten() {
  return fetch("/api/nachrichten/" + encodeURIComponent(NAME))
    .then(function(r) { return r.json(); })
    .then(function(d) {
      var sel = document.getElementById("na-an");
      if (!sel.options.length) {
        sel.innerHTML = d.wesen_liste.map(function(w) {
          return '<option value="' + kfEsc(w) + '"' + (w === NAME ? " selected" : "") +
                 ">" + kfEsc(w) + "</option>";
        }).join("");
      }
      document.getElementById("na-liste").innerHTML = d.anzahl
        ? d.nachrichten.map(function(n) {
            return '<div class="sp-eintrag" data-datei="' + kfEsc(n.datei) + '">' +
              "<span><b>" + kfEsc(n.von) + "</b>" +
              (n.betreff ? " — " + kfEsc(n.betreff) : "") + ": " + kfEsc(n.text) +
              '</span><span class="weg na-gelesen" title="als gelesen markieren">✓</span></div>';
          }).join("")
        : '<div class="sp-leer">keine ungelesenen</div>';
    });
}

document.getElementById("na-senden").addEventListener("click", function() {
  var t = document.getElementById("na-text");
  if (!t.value.trim()) return;
  fetch("/api/nachrichten/senden", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      an: document.getElementById("na-an").value,
      von: "Daniel",
      betreff: document.getElementById("na-betreff").value.trim(),
      text: t.value.trim()
    })
  }).then(function() {
    t.value = ""; document.getElementById("na-betreff").value = "";
    ladeNachrichten(); ladeKontext();
  });
});

document.getElementById("na-liste").addEventListener("click", function(e) {
  if (!e.target.classList.contains("na-gelesen")) return;
  var datei = e.target.closest(".sp-eintrag").getAttribute("data-datei");
  fetch("/api/nachrichten/" + encodeURIComponent(NAME) + "/" +
        encodeURIComponent(datei) + "/gelesen", { method: "POST" })
    .then(function() { ladeNachrichten(); ladeKontext(); });
});

// ── Gedankenfeld ────────────────────────────────────────────────────────────
// Der mitgetragene Zustand. Kein Budget, keine Altersgrenze — nur das Wesen
// (oder hier Daniel, sichtbar als Urheber in der Revision) entfernt etwas.
function ladeGedankenfeld() {
  return fetch("/api/gedankenfeld/" + encodeURIComponent(NAME))
    .then(function(r) { return r.json(); })
    .then(function(d) {
      document.getElementById("gf-zahl").textContent =
        d.anzahl + " · " + d.tokens + " Tok";
      document.getElementById("gf-vorschau").textContent = d.anzahl
        ? d.gedanken.slice(0, 2).map(function(g) { return g.text; }).join(" · ")
        : "leer";
      var kosten = document.getElementById("gf-kosten");
      if (kosten) {
        kosten.textContent = d.anzahl + " Gedanken · " + d.tokens + " von " +
          (d.slot_ctx || "?") + " Token · " + d.revisionen_gesamt + " Revisionen. " +
          "Nichts verfällt — nur du entfernst etwas.";
      }
      var liste = document.getElementById("gf-liste");
      if (!liste) return;
      liste.innerHTML = d.anzahl
        ? d.gedanken.map(function(g) {
            return '<div class="gfd" data-gid="' + g.id + '">' +
              '<div class="gfd-kopf">' +
                '<span class="gfd-id">' + g.id + "</span>" +
                "<span>seit " + kfEsc((g.erstellt_am || "").slice(0, 10)) + "</span>" +
                (g.aenderungen ? "<span>" + g.aenderungen + "× geändert</span>" : "") +
                '<span style="margin-left:auto;display:flex;gap:5px;">' +
                  '<button class="gfd-btn aendern-btn" type="button">ändern</button>' +
                  '<button class="gfd-btn weg-btn" type="button">entfernen</button>' +
                "</span>" +
              "</div>" +
              '<div class="gfd-text">' + kfEsc(g.text) + "</div>" +
            "</div>";
          }).join("")
        : '<div class="sp-leer">noch kein Gedanke</div>';
    });
}

document.getElementById("gf").addEventListener("click", function() {
  document.getElementById("sp-voll").classList.add("auf");
  ladeGedankenfeld(); ladeSpeicher(); ladeGeschichten(); ladeNachrichten();
});

document.getElementById("gf-neu-btn").addEventListener("click", function() {
  var feld = document.getElementById("gf-neu-text");
  if (!feld.value.trim()) return;
  fetch("/api/gedankenfeld/" + encodeURIComponent(NAME) + "/neu", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: feld.value.trim(), von: "Daniel" })
  }).then(function() { feld.value = ""; ladeGedankenfeld(); ladeKontext(); });
});

document.getElementById("gf-liste").addEventListener("click", function(e) {
  var karte = e.target.closest(".gfd");
  if (!karte) return;
  var gid = karte.getAttribute("data-gid");
  var textEl = karte.querySelector(".gfd-text");

  if (e.target.classList.contains("weg-btn")) {
    fetch("/api/gedankenfeld/" + encodeURIComponent(NAME) + "/" + gid +
          "/entfernen?von=Daniel", { method: "POST" })
      .then(function() { ladeGedankenfeld(); ladeKontext(); });
    return;
  }
  if (!e.target.classList.contains("aendern-btn")) return;

  if (textEl.getAttribute("contenteditable") === "true") {
    // Punktgenau: nur dieser eine Gedanke wird geschickt.
    fetch("/api/gedankenfeld/" + encodeURIComponent(NAME) + "/" + gid + "/aendern", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: textEl.textContent.trim(), von: "Daniel" })
    }).then(function() { ladeGedankenfeld(); ladeKontext(); });
  } else {
    textEl.setAttribute("contenteditable", "true");
    e.target.textContent = "übernehmen";
    textEl.focus();
  }
});

ladeGedankenfeld();
setInterval(ladeGedankenfeld, 10000);
ladeSpeicher();
ladeGeschichten();
ladeNachrichten();
setInterval(ladeNachrichten, 20000);
setInterval(ladeSpeicher, 15000);

function ladeModell() {
  fetch("/api/modell").then(function(r) { return r.json(); }).then(function(d) {
    var el = document.getElementById("modell-anzeige");
    el.textContent = d.modell + (d.eigene_instanz ? " · eigene Instanz" : " · geteilt mit den Wesen");
    el.className = d.eigene_instanz ? "" : "geteilt";
    el.title = d.ziel + (d.n_ctx ? " · " + d.n_ctx + " Token pro Gespräch" : "") +
               (d.erreichbar ? "" : " · NICHT ERREICHBAR");
  }).catch(function() {});
}
ladeModell();
setInterval(ladeModell, 30000);

ladeKontext();
setInterval(ladeKontext, 5000);

function formatTs(iso) {
  var n = iso ? new Date(iso) : new Date();
  return n.toLocaleDateString("de-DE", {day:"2-digit",month:"2-digit",year:"numeric"}) + " "
       + n.toLocaleTimeString("de-DE", {hour:"2-digit",minute:"2-digit"});
}
function msg(text, cls, iso) {
  var wrap = document.createElement("div");
  wrap.style.cssText = "display:flex;flex-direction:column;gap:2px;" + (cls==="mensch"?"align-self:flex-end;align-items:flex-end;":"align-self:flex-start;align-items:flex-start;");
  var ts = document.createElement("div");
  ts.style.cssText = "font-size:10px;color:#444;letter-spacing:1px;";
  ts.textContent = formatTs(iso);
  var d = document.createElement("div");
  d.className = "msg " + cls;
  d.style.alignSelf = "unset";
  d.textContent = text;
  wrap.appendChild(ts);
  wrap.appendChild(d);
  if ((cls === "mensch" || cls === "codewesen") && text) {
    wrap.appendChild(baueNachrichtActions(d, iso));
  }
  if (cls === "codewesen" && text) {
    var btn = document.createElement("button");
    btn.textContent = "→ Forum";
    btn.style.cssText = "background:none;border:1px solid #1a2a1a;color:#3a5a3a;font-size:10px;padding:2px 8px;border-radius:3px;cursor:pointer;font-family:inherit;align-self:flex-start;margin-top:1px;";
    btn.onmouseover = function(){ this.style.color="#7ab87a"; this.style.borderColor="#2a4a2a"; };
    btn.onmouseout  = function(){ this.style.color="#3a5a3a"; this.style.borderColor="#1a2a1a"; };
    btn.onclick = function() { direktPosten(d.textContent, btn); };
    wrap.appendChild(btn);
  }
  verlauf.appendChild(wrap);
  verlauf.scrollTop = verlauf.scrollHeight;
  return d;
}

function direktPosten(inhalt, btn) {
  var ersteZeile = inhalt.split("\\n")[0].trim();
  var titelVorschlag = ersteZeile.length > 5 ? ersteZeile.substring(0, 80) : inhalt.substring(0, 60).trim();
  var titel = prompt("Titel für den Forum-Post:", titelVorschlag);
  if (!titel) return;
  btn.disabled = true; btn.textContent = "…";
  fetch("/api/direkt-posten/" + NAME, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({titel: titel, inhalt: inhalt})
  }).then(function(r){ return r.json(); }).then(function(data){
    if (data.ok) {
      btn.textContent = "✓ gepostet #" + (data.diskussion_id || "");
      btn.style.color = "#4a8a4a"; btn.style.borderColor = "#2a5a2a";
    } else {
      btn.textContent = "Fehler"; btn.disabled = false;
    }
  }).catch(function(){ btn.textContent = "Fehler"; btn.disabled = false; });
}

fetch("/api/verlauf/" + NAME).then(function(r){ return r.json(); }).then(function(data){
  kontextAusschluesse = data.kontext_ausschluesse || {};
  for (var i = 0; i < data.verlauf.length; i++) {
    var e = data.verlauf[i];
    var d = msg(e.inhalt, e.rolle === "mensch" ? "mensch" : "codewesen", e.ts);
  }
});

eingabe.addEventListener("keydown", function(e) {
  if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); senden(); }
});
eingabe.addEventListener("input", function() {
  eingabe.style.height = "auto";
  eingabe.style.height = Math.min(eingabe.scrollHeight, 160) + "px";
});

btnSenden.onclick = senden;

function senden() {
  var text = eingabe.value.trim();
  if (!text && !aktuellesBildB64 || btnSenden.disabled) return;
  eingabe.value = "";
  eingabe.style.height = "auto";
  btnSenden.disabled = true;
  btnAbbrechen.style.display = "";
  btnAbbrechen.disabled = false;
  btnAbbrechen.textContent = "\\u23F9 abbrechen";

  var hatBild = !!aktuellesBildB64;
  var bildB64 = aktuellesBildB64;
  var bildName = aktuellerBildName;
  if (hatBild) bildLeeren();

  // Nachricht mit optionalem Bild im Chat anzeigen
  var wrapMensch = document.createElement("div");
  wrapMensch.style.cssText = "display:flex;flex-direction:column;gap:2px;align-self:flex-end;align-items:flex-end;";
  var tsMensch = document.createElement("div");
  tsMensch.style.cssText = "font-size:10px;color:#444;letter-spacing:1px;";
  tsMensch.textContent = formatTs(null);
  var dMensch = document.createElement("div");
  dMensch.className = "msg mensch";
  dMensch.style.alignSelf = "unset";
  if (text) dMensch.textContent = text;
  if (hatBild) {
    var imgEl = document.createElement("img");
    imgEl.className = "msg-bild";
    imgEl.src = "data:image/jpeg;base64," + bildB64;
    dMensch.appendChild(imgEl);
  }
  wrapMensch.appendChild(tsMensch); wrapMensch.appendChild(dMensch);
  if (text) wrapMensch.appendChild(baueNachrichtActions(dMensch));
  verlauf.appendChild(wrapMensch);
  verlauf.scrollTop = verlauf.scrollHeight;

  var antwort = msg("", "warte");
  var gesammelt = "";
  var wurdeAbgebrochen = false;
  btnAbbrechen.onclick = function() {
    wurdeAbgebrochen = true;
    btnAbbrechen.disabled = true;
    btnAbbrechen.textContent = "\\u2026";
    fetch("/api/chat/" + NAME + "/abort", {method: "POST"}).catch(function(){});
  };

  var payload = {nachricht: text || ""};
  if (hatBild) { payload.bild_b64 = bildB64; payload.bild_name = bildName; }

  fetch("/api/chat/" + NAME, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload)
  }).then(function(r) {
    var reader = r.body.getReader();
    var dec = new TextDecoder();
    var puffer = "";

    function lesen() {
      return reader.read().then(function(chunk) {
        if (chunk.done) { fertig(); return; }
        puffer += dec.decode(chunk.value, {stream: true});
        var zeilen = puffer.split("\\n");
        puffer = zeilen.pop();
        for (var i = 0; i < zeilen.length; i++) {
          var z = zeilen[i];
          if (!z.startsWith("data: ")) continue;
          var payload = z.slice(6);
          if (payload === "[DONE]") { fertig(); return; }
          try {
            var d = JSON.parse(payload);
            if (d.warte) {
              antwort.textContent = "";
              antwort.className = "msg warte";
            } else if (d.clear) {
              gesammelt = "";
              antwort.textContent = "";
              antwort.className = "msg codewesen laedt";
            } else if (d.token) {
              gesammelt += d.token;
              antwort.textContent = gesammelt;
              antwort.className = "msg codewesen laedt";
            } else if (d.rewrite) {
              gesammelt = d.rewrite;
              antwort.textContent = gesammelt;
            } else if (d.vorschlag) {
              zeigeVorschlag(d.vorschlag.titel, d.vorschlag.inhalt);
            } else if (d.post_veroeffentlicht) {
              var pv = d.post_veroeffentlicht;
              var karte = document.createElement("div"); karte.className = "vorschlag-karte";
              karte.innerHTML = "<div class=\\"vs-label\\" style=\\"color:#6a6\\">&#10003; Gepostet — #" + (pv.diskussion_id||"?") + " &mdash; " + (pv.titel||"") + "</div>";
              verlauf.appendChild(karte); verlauf.scrollTop = verlauf.scrollHeight;
            } else if (d.post_fehler) {
              msg("[Post-Fehler: " + d.post_fehler + "]", "system");
            } else if (d.verdichtung_laeuft) {
              msg("[Verdichtet die letzten 10 Nachrichten zu einer Geschichte …]", "system");
            }
            verlauf.scrollTop = verlauf.scrollHeight;
          } catch(e) {}
        }
        return lesen();
      });
    }

    return lesen();
  }).catch(function(err) {
    antwort.textContent = "[Fehler: " + err.message + "]";
    antwort.className = "msg system";
    fertig();
  });

  function fertig() {
    btnAbbrechen.style.display = "none";
    if (!gesammelt) { antwort.remove(); }
    else {
      antwort.className = "msg codewesen";
      if (wurdeAbgebrochen) {
        var hinweis = document.createElement("div");
        hinweis.style.cssText = "font-size:10px;color:#a86a6a;margin-top:1px;";
        hinweis.textContent = "\\u23F9 abgebrochen \\u2014 nicht gespeichert, nur hier sichtbar";
        antwort.parentElement.appendChild(hinweis);
      }
      var btn = document.createElement("button");
      btn.textContent = "→ Forum";
      btn.style.cssText = "background:none;border:1px solid #1a2a1a;color:#3a5a3a;font-size:10px;padding:2px 8px;border-radius:3px;cursor:pointer;font-family:inherit;align-self:flex-start;margin-top:1px;";
      btn.onmouseover = function(){ this.style.color="#7ab87a"; this.style.borderColor="#2a4a2a"; };
      btn.onmouseout  = function(){ this.style.color="#3a5a3a"; this.style.borderColor="#1a2a1a"; };
      btn.onclick = function() { direktPosten(antwort.textContent, btn); };
      antwort.parentElement.appendChild(baueNachrichtActions(antwort));
      if (!wurdeAbgebrochen) antwort.parentElement.appendChild(btn);
      if (!wurdeAbgebrochen && gesammelt.trim().length > 10) sprichText(gesammelt);
    }
    btnSenden.disabled = false;
    eingabe.focus();
    setTimeout(ladeZustand, 1500);
    setTimeout(ladeKontext, 1600);
  }
}

function zeigeVorschlag(titel, inhalt) {
  var karte = document.createElement("div");
  karte.className = "vorschlag-karte";
  var titSafe = titel.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
  var inhSafe = inhalt.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/\\n/g,"<br>");
  karte.innerHTML = "<div class=\\"vs-label\\">Post-Vorschlag</div>"
    + "<div class=\\"vs-titel\\">" + titSafe + "</div>"
    + "<div class=\\"vs-inhalt\\">" + inhSafe + "</div>"
    + "<div class=\\"vs-buttons\\">"
    + "<button class=\\"vs-btn-ok\\" onclick=\\"bestaetigenPost(this)\\">&#10003; Posten</button>"
    + "<button class=\\"vs-btn-ab\\" onclick=\\"this.closest(\\'.vorschlag-karte\\').remove()\\">&#10005; Ablehnen</button>"
    + "</div>";
  karte.dataset.titel = titel;
  karte.dataset.inhalt = inhalt;
  verlauf.appendChild(karte);
  verlauf.scrollTop = verlauf.scrollHeight;
}

function bestaetigenPost(btn) {
  var karte = btn.closest(".vorschlag-karte");
  var titel = karte.dataset.titel;
  var inhalt = karte.dataset.inhalt;
  btn.disabled = true;
  btn.textContent = "… wird gepostet";
  fetch("/api/vorschlag/" + NAME, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({titel: titel, inhalt: inhalt})
  }).then(function(r){ return r.json(); }).then(function(d) {
    if (d.ok) {
      karte.innerHTML = "<div class=\\"vs-label\\" style=\\"color:#6a6\\">&#10003; Gepostet — Diskussion #" + (d.diskussion_id||"?") + "</div>";
    } else {
      karte.innerHTML = "<div class=\\"vs-label\\" style=\\"color:#a66\\">Fehler: " + (d.fehler||"unbekannt") + "</div>";
    }
  }).catch(function(e) {
    btn.textContent = "Fehler: " + e.message;
    btn.disabled = false;
  });
}

btnAuswerten.onclick = function() {
  btnAuswerten.disabled = true;
  btnAuswerten.textContent = "… läuft";
  var info = msg("Auswertung läuft…", "system");
  fetch("/api/analyse/" + NAME, {method: "POST"}).then(function(r){ return r.json(); }).then(function(data) {
    info.remove();
    if (data.fehler) { msg("Fehler: " + data.fehler, "system"); return; }
    var txt = "";
    if (data.zusammenfassung) txt += "Zusammenfassung: " + data.zusammenfassung + "\\n\\n";
    if (data.vereinbarungen && data.vereinbarungen.length) {
      txt += "Vereinbarungen:\\n";
      for (var i = 0; i < data.vereinbarungen.length; i++) {
        var v = data.vereinbarungen[i];
        txt += "  [" + v.prioritaet + "] " + v.titel + "\\n";
      }
    }
    if (txt) msg(txt.trim(), "codewesen");
  }).catch(function(e) {
    info.textContent = "Fehler: " + e.message;
  }).finally(function() {
    btnAuswerten.disabled = false;
    btnAuswerten.textContent = "\\u2853 auswerten";
  });
};
</script>
</body>
</html>"""


GRUPPENCHAT_SEITE = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Gruppenchat — Codewesen</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #0d0d0d; color: #e0e0e0; font-family: 'Courier New', monospace;
         min-height: 100vh; font-size: 14px; }
  a { color: inherit; }
  .layout { display: flex; min-height: 100vh; }
  aside { width: 280px; flex: none; background: #101010; border-right: 1px solid #2a2a2a;
          padding: 1rem; display: flex; flex-direction: column; gap: 0.6rem; overflow-y: auto; }
  aside h2, aside h3 { font-size: 0.85rem; letter-spacing: 0.1em; color: #888; margin-bottom: 0.3rem; }
  .sitzung-eintrag { background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 6px;
                      padding: 0.6rem 0.7rem; cursor: pointer; }
  .sitzung-eintrag:hover { border-color: #555; }
  .sitzung-eintrag.aktiv { border-color: #7ab87a; }
  .sitzung-titel { font-size: 0.85rem; color: #c8c8c8; }
  .sitzung-meta { font-size: 0.7rem; color: #6a6a6a; margin-top: 0.2rem; }
  .wesen-auswahl { display: flex; flex-direction: column; gap: 0.25rem; margin: 0.4rem 0; }
  .wesen-auswahl label { font-size: 0.8rem; color: #b0b0b0; display: flex; gap: 0.4rem; align-items: center; }
  input[type=text], input#neu-titel, textarea, select {
    background: #111; border: 1px solid #333; color: #e0e0e0; font-family: inherit;
    font-size: 0.85rem; padding: 0.4rem 0.5rem; border-radius: 4px; width: 100%;
  }
  button { background: #1a2a1a; border: 1px solid #3a5a3a; color: #b8d8b8; font-family: inherit;
           font-size: 0.8rem; padding: 0.45rem 0.7rem; border-radius: 4px; cursor: pointer; }
  button:hover { background: #2a4a2a; }
  button:disabled { opacity: 0.4; cursor: default; }
  button.leise { background: #1a1a1a; border-color: #333; color: #999; }
  main { flex: 1; display: flex; flex-direction: column; padding: 1.2rem; overflow: hidden; }
  #leer-hinweis { color: #555; margin: auto; }
  #sitzungsansicht { display: flex; flex-direction: column; height: 100%; overflow: hidden; }
  #sa-kopf { border-bottom: 1px solid #2a2a2a; padding-bottom: 0.6rem; margin-bottom: 0.6rem; }
  #sa-kopf .titel { font-size: 1.05rem; color: #e0e0e0; }
  .chip-zeile { display: flex; gap: 0.4rem; margin-top: 0.4rem; flex-wrap: wrap; }
  .chip { background: #1a2a1a; border: 1px solid #3a5a3a; color: #9ac89a; font-size: 0.72rem;
          padding: 0.15rem 0.5rem; border-radius: 999px; }
  #sa-status { font-size: 0.75rem; color: #7a6a3a; min-height: 1.1em; margin-top: 0.3rem; }
  #sa-verlauf { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 0.7rem;
                padding: 0.4rem 0.2rem; }
  .nachricht { border-left: 3px solid #444; background: #141414; border-radius: 0 6px 6px 0;
               padding: 0.5rem 0.7rem; max-width: 80%; }
  .nachricht.mensch { border-left-color: #7a6a3a; align-self: flex-end; background: #1a1712; }
  .nachricht.wesen { border-left-color: #7ab87a; background: #131b13; }
  .nachricht.zusammenfassung { border-left-color: #7a6a3a; background: #1a1712; max-width: 100%;
                                font-style: italic; }
  .n-kopf { font-size: 0.72rem; color: #888; margin-bottom: 0.2rem; display: flex; gap: 0.5rem; }
  .n-sprecher { color: #b8d8b8; }
  .nachricht.mensch .n-sprecher { color: #cdbb87; }
  .n-text { white-space: pre-wrap; line-height: 1.4; }
  .n-werkzeuge { display: flex; gap: 0.4rem; margin-top: 0.4rem; flex-wrap: wrap; }
  .n-werkzeuge button { font-size: 0.72rem; padding: 0.25rem 0.5rem; }
  .trigger-knopf.gemeldet { background: #2a3a1a; border-color: #6a9a3a; color: #d8f0b8; font-weight: bold; }
  .trigger-knopf.nicht-gemeldet { opacity: 0.55; }
  .kd-nachricht { border-top: 1px solid #2a2a2a; padding: 0.4rem 0; line-height: 1.6; }
  .kd-nachricht.kd-redigiert { background: #1a1512; }
  .kd-satz { cursor: pointer; border-radius: 3px; padding: 0 2px; }
  .kd-satz:hover { background: #222; }
  .kd-satz.gewaehlt { background: #4a2a2a; color: #f0c8c8; text-decoration: line-through; }
  .kontext-box { margin-top: 0.4rem; font-size: 0.72rem; color: #999; background: #0f0f0f;
                 border: 1px solid #2a2a2a; border-radius: 4px; padding: 0.4rem 0.5rem; display: none; }
  .kontext-box.offen { display: block; }
  .kontext-zeile { display: flex; justify-content: space-between; padding: 0.1rem 0; }
  .ge-laengen button { font-size: 0.78rem; padding: 0.3rem 0.6rem; margin: 0 0.2rem 0.4rem 0; }
  .ge-box { border: 1px solid #2a2a2a; border-radius: 4px; padding: 0.4rem 0.5rem; margin-bottom: 0.5rem; }
  .ge-box.inaktiv { opacity: 0.45; }
  .ge-box-kopf { display: flex; align-items: center; gap: 0.4rem; font-size: 0.78rem; color: #c8c8c8; }
  .ge-box-kopf .ge-weg { margin-left: auto; cursor: pointer; color: #a86a6a; }
  .ge-box-text { font-size: 0.76rem; color: #999; margin-top: 0.3rem; line-height: 1.5; }
  .mv-box { border: 1px solid #2a2a2a; border-radius: 4px; padding: 0.4rem 0.5rem; margin-bottom: 0.5rem; }
  .mv-box[data-status="uebernommen"] { border-color: #3a5a3a; opacity: 0.7; }
  .mv-box[data-status="abgelehnt"] { border-color: #5a3a3a; opacity: 0.55; }
  .mv-box textarea, .mv-box select { font-family: inherit; font-size: 0.76rem; background: #111; color: #ccc;
                                       border: 1px solid #2a2a2a; border-radius: 3px; padding: 0.2rem 0.3rem; }
  @keyframes zuhoerPuls { 0%, 100% { opacity: 0.4; } 50% { opacity: 0.9; } }
  .zuhoer-pille { display: inline-block; font-size: 0.7rem; color: #6a8a6a; background: #101a10;
                  border: 1px solid #2a3a2a; border-radius: 999px; padding: 0.1rem 0.5rem;
                  margin-right: 0.3rem; animation: zuhoerPuls 1.8s ease-in-out infinite; }
  #sa-eingabe { border-top: 1px solid #2a2a2a; padding-top: 0.6rem; margin-top: 0.6rem; }
  .modus-zeile { display: flex; gap: 1rem; align-items: center; flex-wrap: wrap; font-size: 0.78rem;
                 color: #b0b0b0; margin-bottom: 0.5rem; }
  .modus-zeile label { display: flex; align-items: center; gap: 0.3rem; }
  #sa-sprecher { width: auto; display: inline-block; }
  textarea#sa-text { min-height: 3.2rem; resize: vertical; }
  .knopfzeile { display: flex; gap: 0.5rem; margin-top: 0.5rem; flex-wrap: wrap; }
  .dialog { position: fixed; inset: 0; background: rgba(0,0,0,0.6); display: flex;
            align-items: center; justify-content: center; z-index: 10; }
  .dialog-inhalt { background: #141414; border: 1px solid #333; border-radius: 8px; padding: 1.2rem;
                   width: min(480px, 90vw); display: flex; flex-direction: column; gap: 0.6rem; }
  .dialog-inhalt h3 { font-size: 0.95rem; color: #e0e0e0; }
  .dialog-zeile { display: flex; gap: 0.5rem; align-items: center; font-size: 0.8rem; color: #b0b0b0; }
  .fehlermeldung { color: #c87a7a; font-size: 0.8rem; }
</style>
</head>
<body>
<div class="layout">
  <aside>
    <h2>// GRUPPENCHAT</h2>
    <div id="sitzungsliste"></div>
    <hr style="border-color:#2a2a2a; width:100%; margin: 0.4rem 0;">
    <h3>Neue Sitzung</h3>
    <input id="neu-titel" type="text" placeholder="Titel (optional)">
    <div id="neu-teilnehmer" class="wesen-auswahl"></div>
    <button id="neu-start">+ Sitzung starten</button>
    <a href="/codewesen-chat/" style="font-size:0.72rem; color:#555; margin-top:0.6rem;">&larr; zurück zur Auswahl</a>
  </aside>
  <main>
    <div id="leer-hinweis">Wähle links eine Sitzung oder starte eine neue.</div>
    <div id="sitzungsansicht" style="display:none">
      <div id="sa-kopf">
        <div class="titel" id="sa-titel"></div>
        <div class="chip-zeile" id="sa-teilnehmer"></div>
        <div id="sa-status"></div>
      </div>
      <div id="sa-verlauf"></div>
      <div id="sa-eingabe">
        <div class="modus-zeile">
          <label><input type="radio" name="modus" value="zuhoeren" checked> alle hören nur zu</label>
          <label><input type="radio" name="modus" value="direkt">
                 <select id="sa-sprecher"></select> antwortet direkt</label>
          <label><input type="checkbox" id="sa-sortiert"> Trigger relevanzsortiert (optional)</label>
        </div>
        <textarea id="sa-text" placeholder="Nachricht an alle aktiven Wesen ..."></textarea>
        <div class="knopfzeile">
          <button id="sa-senden">senden</button>
          <button id="sa-alle-antworten" class="leise">alle antworten (echt, nacheinander)</button>
          <button id="sa-zusammenfassen" class="leise">zusammenfassen …</button>
          <button id="sa-kontext-oeffnen" class="leise">Kontextfenster …</button>
          <button id="sa-geschichten-oeffnen" class="leise">Geschichten …</button>
          <button id="sa-memory-oeffnen" class="leise">Memory-Vorschläge …</button>
          <button id="sa-an-alle" class="leise">als Nachricht an alle hinterlassen</button>
          <button id="sa-posten-oeffnen" class="leise">als Diskussion posten …</button>
        </div>
      </div>
    </div>
  </main>
</div>

<div id="posten-dialog" class="dialog" style="display:none">
  <div class="dialog-inhalt">
    <h3>Als Forendiskussion posten</h3>
    <div class="dialog-zeile">Titel<input id="pd-titel" type="text" style="flex:1"></div>
    <div class="dialog-zeile">Gepostet von<select id="pd-wesen" style="flex:1"></select></div>
    <div class="dialog-zeile">von Nachricht<select id="pd-von" style="flex:1"></select>
                              bis<select id="pd-bis" style="flex:1"></select></div>
    <div class="fehlermeldung" id="pd-fehler"></div>
    <div class="knopfzeile">
      <button id="pd-posten">posten</button>
      <button id="pd-abbrechen" class="leise">abbrechen</button>
    </div>
  </div>
</div>

<div id="ge-dialog" class="dialog" style="display:none">
  <div class="dialog-inhalt" style="width:min(640px,92vw); max-height:85vh; overflow-y:auto;">
    <h3>Geschichten aus diesem Gruppengespräch</h3>
    <div style="font-size:0.76rem; color:#999; margin-bottom:0.6rem;">
      Destilliert aus dem gesamten Sitzungsverlauf, nicht erfunden. Mehrere gleichzeitig aktiv
      möglich — jede aktive Geschichte wird JEDEM Teilnehmer im Kontext mitgegeben, bis du sie
      deaktivierst oder entfernst.
    </div>
    <button type="button" id="ge-verfassen-auto" style="margin-bottom:0.5rem;">
      🔍 Automodus — komplett lesen, selbst entscheiden, Storyteller
    </button>
    <div style="font-size:0.72rem; color:#777; margin:-0.2rem 0 0.6rem 0;">
      liest den gesamten Sitzungsverlauf, entscheidet selbst über die Länge — kann dauern.
    </div>
    <div style="font-size:0.72rem; color:#777; margin-bottom:0.3rem;">oder feste Zielgröße (Token):</div>
    <div id="ge-laengen" class="ge-laengen"></div>
    <div id="ge-status" style="font-size:0.76rem; color:#8a8a6a; min-height:1.2em;"></div>
    <div id="ge-liste"></div>
    <div class="knopfzeile">
      <button id="ge-schliessen" class="leise">schließen</button>
    </div>
  </div>
</div>

<div id="memory-dialog" class="dialog" style="display:none">
  <div class="dialog-inhalt" style="width:min(720px,92vw); max-height:85vh; overflow-y:auto;">
    <h3>Memory-Vorschläge</h3>
    <div style="font-size:0.76rem; color:#999; margin-bottom:0.6rem;">
      Für jedes teilnehmende Codewesen: Vorschläge, was es sich aus dem gesamten Sitzungsverlauf
      merken könnte. Nichts wird automatisch gespeichert — erst "bestätigen" schreibt tatsächlich
      ins echte Gedächtnis des Wesens. Text und Kategorie vor dem Bestätigen frei editierbar.
    </div>
    <button type="button" id="mv-generieren">Vorschläge generieren (alle Wesen)</button>
    <div id="mv-status" style="font-size:0.76rem; color:#8a8a6a; min-height:1.2em; margin:0.3rem 0;"></div>
    <div id="mv-timer" style="font-size:0.72rem; color:#666; min-height:1.1em; margin-bottom:0.3rem;"></div>
    <div id="mv-liste"></div>

    <div style="border-top:1px solid #2a2a2a; margin-top:0.8rem; padding-top:0.6rem;">
      <div style="font-size:0.78rem; color:#c8c8c8; margin-bottom:0.4rem;">selbst etwas eintragen:</div>
      <div class="dialog-zeile">
        <select id="mv-eigen-wesen" style="flex:1"></select>
        <select id="mv-eigen-kategorie" style="flex:1"></select>
      </div>
      <textarea id="mv-eigen-text" rows="3" style="width:100%; box-sizing:border-box; margin-top:0.3rem;"
                placeholder="Was soll sich das Wesen merken?"></textarea>
      <div class="fehlermeldung" id="mv-eigen-fehler"></div>
      <div class="knopfzeile">
        <button type="button" id="mv-eigen-hinzufuegen">hinzufügen</button>
      </div>
    </div>

    <div class="knopfzeile" style="margin-top:0.8rem;">
      <button id="mv-schliessen" class="leise">schließen</button>
    </div>
  </div>
</div>

<div id="zf-dialog" class="dialog" style="display:none">
  <div class="dialog-inhalt">
    <h3>Zusammenfassen</h3>
    <div class="dialog-zeile">von Nachricht<select id="zf-von" style="flex:1"></select>
                              bis<select id="zf-bis" style="flex:1"></select></div>
    <div class="fehlermeldung" id="zf-fehler"></div>
    <div class="knopfzeile">
      <button id="zf-erstellen">zusammenfassen</button>
      <button id="zf-abbrechen" class="leise">abbrechen</button>
    </div>
  </div>
</div>

<div id="kontext-dialog" class="dialog" style="display:none">
  <div class="dialog-inhalt" style="width:min(720px,92vw); max-height:85vh; overflow-y:auto;">
    <h3>Kontextfenster</h3>
    <div class="dialog-zeile">Wesen<select id="kd-wesen" style="flex:1"></select>
                              <button id="kd-laden" class="leise">laden</button></div>
    <div id="kd-inhalt" style="font-size:0.8rem; color:#b0b0b0;"></div>
    <div class="knopfzeile">
      <button id="kd-entfernen" disabled>ausgewählte Sätze entfernen</button>
      <button id="kd-schliessen" class="leise">schließen</button>
    </div>
  </div>
</div>

<script>
function esc(s) {
  var d = document.createElement("div");
  d.textContent = s == null ? "" : String(s);
  return d.innerHTML;
}

// 2026-08-13, Daniel: "ich will dass du mich auch in der ui im chat nur admin
// taufst nicht daniel" -- reine Anzeige-Umbenennung, NICHT das zugrunde
// liegende Datenmodell (sprecher bleibt intern "Daniel", z.B. fuer
// baue_gruppenchat_messages()-Rollenlogik, id_slot-Zuordnung, gespeicherte
// Sitzungsdateien). Nur beim tatsaechlichen Rendern fuer Daniels Augen wird
// daraus "Admin" -- nirgends als data-Attribut oder API-Parameter verwenden.
function anzeigeName(n) { return n === "Daniel" ? "Admin" : n; }

// 2026-08-14 Fix: gemeinsamer SSE-Reader fuer Endpunkte, die jetzt streamen statt
// ein einzelnes JSON zurueckzugeben (Zusammenfassen, Geschichte verfassen) --
// ohne kontinuierliche Bytes stirbt die Verbindung bei einer langen Sitzung am
// nginx-proxy_read_timeout, bevor ein Ergebnis ankommt. onEvent wird fuer jedes
// geparste JSON-Objekt aufgerufen, das Promise loest sich wenn der Stream endet.
function sseLesen(url, body, onEvent) {
  return fetch(url, {
    method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(body || {})
  }).then(function(r) {
    var reader = r.body.getReader();
    var dec = new TextDecoder();
    var puffer = "";
    function lesen() {
      return reader.read().then(function(chunk) {
        if (chunk.done) return;
        puffer += dec.decode(chunk.value, {stream: true});
        var zeilen = puffer.split("\\n");
        puffer = zeilen.pop();
        for (var i = 0; i < zeilen.length; i++) {
          var z = zeilen[i];
          if (!z.startsWith("data: ")) continue;
          var payload = z.slice(6);
          if (payload === "[DONE]") continue;
          try { onEvent(JSON.parse(payload)); } catch (e) {}
        }
        return lesen();
      });
    }
    return lesen();
  });
}

var WESEN_LISTE = [];
var SITZUNG = null;

function ladeSitzungsliste() {
  return fetch("/api/gruppenchat/sitzungen").then(function(r) { return r.json(); }).then(function(d) {
    WESEN_LISTE = d.wesen_liste || [];
    var box = document.getElementById("sitzungsliste");
    box.innerHTML = d.sitzungen.length ? d.sitzungen.map(function(s) {
      return '<div class="sitzung-eintrag' + (SITZUNG && SITZUNG.id === s.id ? " aktiv" : "") +
             '" data-sid="' + esc(s.id) + '">' +
             '<div class="sitzung-titel">' + esc(s.titel) +
             (s.aktiv === false ? ' <span style="color:#999;font-size:0.7rem;">(inaktiv)</span>' : '') +
             '</div>' +
             '<div class="sitzung-meta">' + s.teilnehmer.length + ' Wesen &middot; ' +
             s.anzahl_nachrichten + ' Nachrichten</div></div>';
    }).join("") : '<div class="sitzung-meta">noch keine Sitzungen</div>';

    var neu = document.getElementById("neu-teilnehmer");
    if (!neu.children.length) {
      neu.innerHTML = WESEN_LISTE.map(function(w) {
        return '<label><input type="checkbox" value="' + esc(w) + '"> ' + esc(w) + '</label>';
      }).join("");
    }
  });
}

document.getElementById("sitzungsliste").addEventListener("click", function(e) {
  var el = e.target.closest(".sitzung-eintrag");
  if (!el) return;
  ladeSitzung(el.getAttribute("data-sid"));
});

document.getElementById("neu-start").addEventListener("click", function() {
  var titel = document.getElementById("neu-titel").value.trim();
  var teilnehmer = Array.prototype.slice.call(
    document.querySelectorAll("#neu-teilnehmer input:checked")).map(function(c) { return c.value; });
  if (!teilnehmer.length) { alert("Mindestens ein Wesen auswählen."); return; }
  fetch("/api/gruppenchat/sitzungen", {
    method: "POST", headers: {"Content-Type": "application/json"},
    body: JSON.stringify({titel: titel, teilnehmer: teilnehmer})
  }).then(function(r) { return r.json(); }).then(function(s) {
    document.getElementById("neu-titel").value = "";
    Array.prototype.forEach.call(document.querySelectorAll("#neu-teilnehmer input"),
      function(c) { c.checked = false; });
    ladeSitzungsliste().then(function() { ladeSitzung(s.id); });
  });
});

function ladeSitzung(sid) {
  return fetch("/api/gruppenchat/sitzungen/" + encodeURIComponent(sid)).then(function(r) { return r.json(); })
    .then(function(s) {
      if (s.fehler) { alert(s.fehler); return; }
      SITZUNG = s;
      document.getElementById("leer-hinweis").style.display = "none";
      document.getElementById("sitzungsansicht").style.display = "flex";
      document.getElementById("sa-titel").textContent = s.titel;
      document.getElementById("sa-teilnehmer").innerHTML = s.teilnehmer.map(function(w) {
        return '<span class="chip">' + esc(w) + '</span>';
      }).join("");
      renderSitzungStatus(s);
      var sel = document.getElementById("sa-sprecher");
      sel.innerHTML = s.teilnehmer.map(function(w) {
        return '<option value="' + esc(w) + '">' + esc(w) + '</option>';
      }).join("");
      renderVerlauf();
      Array.prototype.forEach.call(document.querySelectorAll(".sitzung-eintrag"), function(el) {
        el.classList.toggle("aktiv", el.getAttribute("data-sid") === sid);
      });
    });
}

function renderSitzungStatus(s) {
  // 2026-09-17, Daniels Auftrag: Sitzungen duerfen erstmal frei nachhallen (aktiv=true,
  // Standard), aber manuell als inaktiv markierbar sein -- Protokoll bleibt stehen,
  // rueckt nur aus dem automatischen 1:1-Kontext raus und wird stattdessen durchsuchbar
  // (siehe /api/gruppenchat/sitzungen/{sid}/inaktiv).
  var box = document.getElementById("sa-status");
  var aktiv = s.aktiv !== false;
  box.innerHTML =
    '<span style="font-size:0.75rem;color:' + (aktiv ? "#6a6" : "#999") + '">' +
    (aktiv ? "aktiv — hallt im Kontext der Wesen nach" : "inaktiv — durchsuchbar, aber raus aus dem 1:1-Kontext") +
    '</span> ' +
    '<button id="sa-inaktiv-btn" style="font-size:0.72rem;margin-left:0.5rem;">' +
    (aktiv ? "als inaktiv markieren" : "wieder aktivieren") + '</button>';
  document.getElementById("sa-inaktiv-btn").onclick = function() {
    var pfad = aktiv ? "inaktiv" : "aktiv";
    var btn = this;
    btn.disabled = true;
    btn.textContent = aktiv ? "markiere…" : "aktiviere…";
    fetch("/api/gruppenchat/sitzungen/" + encodeURIComponent(s.id) + "/" + pfad, {method: "POST"})
      .then(function(r) { return r.json(); })
      .then(function(ergebnis) {
        if (ergebnis.fehler) { alert(ergebnis.fehler); btn.disabled = false; return; }
        ladeSitzung(s.id);
        ladeSitzungsliste();
      });
  };
}

function renderVerlauf() {
  var box = document.getElementById("sa-verlauf");
  var nachrichten = SITZUNG.nachrichten;
  box.innerHTML = nachrichten.map(function(n, i) {
    var istMensch = n.sprecher === "Daniel";
    var werkzeuge = "";
    if (i === nachrichten.length - 1) {
      // Trigger-Zeile nur unter der JEWEILS letzten Nachricht (Daniels Beschreibung:
      // "unter der Antwort ... ein anderes Wesen triggern" -- das Gespraech wandert
      // vorwaerts, keine verzweigten Trigger unter jeder alten Nachricht).
      var kandidaten = SITZUNG.teilnehmer.filter(function(w) { return w !== n.sprecher; });
      werkzeuge = (kandidaten.length > 1
          ? '<div class="n-werkzeuge"><button class="leise melde-knopf">&#9995; wer will reagieren?</button></div>'
          : "") +
        '<div class="n-werkzeuge" data-trigger-zeile="1">' +
        kandidaten.map(function(w) {
          return '<button class="leise trigger-knopf" data-name="' + esc(w) + '">&rarr; ' + esc(w) + '</button>';
        }).join("") + '</div>';
    }
    // GENI hat kein /api/kontext/{name} wie die Codewesen (eigener Prozess,
    // eigener Kontext-Aufbau), und "Zusammenfassung" ist kein echtes Wesen --
    // Knopf in beiden Faellen bewusst weglassen statt eines garantierten 404.
    var kontextKnopf = (!istMensch && n.sprecher !== "GENI" && n.sprecher !== "Zusammenfassung")
      ? '<div class="n-werkzeuge"><button class="leise kontext-knopf" data-name="' + esc(n.sprecher) +
        '" data-idx="' + i + '">Kontext-Fußabdruck</button></div>' +
        '<div class="kontext-box" id="kontext-' + i + '"></div>'
      : "";
    var istZusammenfassung = n.sprecher === "Zusammenfassung";
    var klasse = istZusammenfassung ? "zusammenfassung" : (istMensch ? "mensch" : "wesen");
    var nachrichtActions = n.text
      ? '<div class="n-werkzeuge"><button type="button" class="leise gc-vorlesen-knopf" data-idx="' + i +
        '">\\u{1F50A} Vorlesen</button><button type="button" class="leise gc-kopieren-knopf" data-idx="' + i +
        '">\\u{1F4CB} Kopieren</button></div>'
      : "";
    return '<div class="nachricht ' + klasse + '">' +
      '<div class="n-kopf"><span class="n-sprecher">' + esc(anzeigeName(n.sprecher)) + '</span>' +
      '<span>' + esc((n.ts || "").slice(11, 16)) + '</span></div>' +
      '<div class="n-text">' + esc(n.text) + '</div>' + nachrichtActions + kontextKnopf + werkzeuge + '</div>';
  }).join("");
  box.scrollTop = box.scrollHeight;
  anwendenSortierung();
}

function anwendenSortierung() {
  if (!document.getElementById("sa-sortiert").checked) return;
  var zeile = document.querySelector('[data-trigger-zeile="1"]');
  if (!zeile || !SITZUNG.nachrichten.length) return;
  var letzte = SITZUNG.nachrichten[SITZUNG.nachrichten.length - 1].text;
  fetch("/api/gruppenchat/sitzungen/" + encodeURIComponent(SITZUNG.id) + "/kandidaten?sortiert=true")
    .then(function(r) { return r.json(); }).then(function(d) {
      var knoepfe = {};
      Array.prototype.forEach.call(zeile.querySelectorAll(".trigger-knopf"), function(b) {
        knoepfe[b.getAttribute("data-name")] = b;
      });
      d.kandidaten.forEach(function(name) {
        if (knoepfe[name]) zeile.appendChild(knoepfe[name]);
      });
    });
}

function holeMeldungen(knopf) {
  // Idee via ChatGPT/Daniel (2026-08-13): billige Voranfrage vor dem eigentlichen
  // Trigger -- wer von den gerade Zuhoerenden haette spontan etwas dazu. Keiner
  // muss, Daniel triggert danach trotzdem frei wen er will (gemeldet ist nur eine
  // visuelle Empfehlung auf den bestehenden Trigger-Knoepfen, keine Vorauswahl).
  knopf.disabled = true;
  knopf.textContent = "frage herum …";
  status("frage alle die zuhören, ob sie was dazu haben …");
  fetch("/api/gruppenchat/sitzungen/" + encodeURIComponent(SITZUNG.id) + "/meldungen", {
    method: "POST"
  }).then(function(r) { return r.json(); }).then(function(d) {
    var zeile = document.querySelector('[data-trigger-zeile="1"]');
    if (zeile) {
      (d.meldungen || []).forEach(function(m) {
        var b = zeile.querySelector('.trigger-knopf[data-name="' + CSS.escape(m.name) + '"]');
        if (!b) return;
        if (m.gemeldet) {
          b.classList.add("gemeldet");
          b.title = m.grund || "hat sich gemeldet";
          b.innerHTML = "&#9995; &rarr; " + esc(m.name);
        } else {
          b.classList.add("nicht-gemeldet");
        }
      });
    }
    knopf.remove();
    status("");
  }).catch(function(err) {
    knopf.disabled = false;
    knopf.textContent = "✖ fehlgeschlagen, nochmal?";
    status("");
  });
}

document.getElementById("sa-verlauf").addEventListener("click", function(e) {
  if (e.target.classList.contains("melde-knopf")) {
    holeMeldungen(e.target);
    return;
  }
  if (e.target.classList.contains("trigger-knopf")) {
    triggerWesen(e.target.getAttribute("data-name"));
    return;
  }
  if (e.target.classList.contains("gc-vorlesen-knopf")) {
    var idxV = e.target.getAttribute("data-idx");
    gcSprichText(SITZUNG.nachrichten[idxV].text);
    return;
  }
  if (e.target.classList.contains("gc-kopieren-knopf")) {
    var idxK = e.target.getAttribute("data-idx");
    gcKopiere(e.target, SITZUNG.nachrichten[idxK].text);
    return;
  }
  if (e.target.classList.contains("kontext-knopf")) {
    var idx = e.target.getAttribute("data-idx");
    var name = e.target.getAttribute("data-name");
    var box = document.getElementById("kontext-" + idx);
    if (box.classList.contains("offen")) { box.classList.remove("offen"); return; }
    box.classList.add("offen");
    box.textContent = "lädt …";
    // /api/kontext/ existiert nur unter dem bestehenden /codewesen-chat/-Mount
    // (nginx dort per sub_filter umgeschrieben) -- diese Seite haengt an der
    // Domain-Wurzel und braucht den Pfad deshalb explizit vorangestellt
    // (2026-08-13 live gefunden: 404, weil /api/ ohne Praefix an welt-api
    // Port 8030 geht, nicht an codewesen_chat.py Port 8002).
    fetch("/codewesen-chat/api/kontext/" + encodeURIComponent(name)).then(function(r) { return r.json(); })
      .then(function(d) {
        // Zeigt den AKTUELLEN Kontextzustand von "name", nicht eingefroren zum
        // Zeitpunkt dieser einen Nachricht -- gleiche Kontextanzeige wie im 1:1-Chat,
        // hier nur pro Gruppenchat-Nachricht aufklappbar wiederverwendet.
        box.innerHTML = '<div style="color:#777; margin-bottom:0.3rem;">aktueller Kontext von ' +
          esc(name) + ' (kein Schnappschuss dieser Nachricht):</div>' +
          (d.schichten || []).map(function(s) {
            return '<div class="kontext-zeile"><span>' + esc(s.titel) + '</span><span>' +
                   s.tokens + ' Tok</span></div>';
          }).join("");
      }).catch(function() { box.textContent = "Kontext nicht ladbar."; });
  }
});

function status(text) { document.getElementById("sa-status").textContent = text || ""; }

// ── Vorlesen + Kopieren pro Nachricht (uebernommen von codexium2/solarius2,
// gleicher /api/tts-Endpunkt wie im 1:1-Chat, hier ohne globalen An/Aus-Schalter --
// Gruppenchat kannte bisher gar keine TTS). ──────────────────────────────────
function gcKopiere(btn, text) {
  if (!navigator.clipboard) return;
  navigator.clipboard.writeText(text).then(function() {
    var vorher = btn.textContent;
    btn.textContent = "\\u2713";
    setTimeout(function(){ btn.textContent = vorher; }, 1500);
  }).catch(function(){});
}
var gcTtsAudio = null;
function gcReinigeFuerTts(text) {
  return text.replace(/```[\\s\\S]*?```/g, "").replace(/`[^`]+`/g, "")
             .replace(/\\n{3,}/g, "\\n").trim();
}
async function gcSprichText(text) {
  var rein = gcReinigeFuerTts(text || "");
  if (rein.length < 3) return;
  try {
    var r = await fetch("/codewesen-chat/api/tts", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({text: rein.slice(0, 1600), maennlich: true})
    });
    if (!r.ok) return;
    var blob = await r.blob();
    if (blob.size < 100) return;
    var url = URL.createObjectURL(blob);
    if (gcTtsAudio) { gcTtsAudio.pause(); gcTtsAudio.src = ""; }
    gcTtsAudio = new Audio(url);
    gcTtsAudio.onended = function(){ URL.revokeObjectURL(url); gcTtsAudio = null; };
    gcTtsAudio.play().catch(function(){ URL.revokeObjectURL(url); gcTtsAudio = null; });
  } catch(e) {}
}

function streameAntwort(url, body) {
  document.getElementById("sa-senden").disabled = true;
  return fetch(url, {
    method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(body || {})
  }).then(function(r) {
    var reader = r.body.getReader();
    var dec = new TextDecoder();
    var puffer = "";
    function lesen() {
      return reader.read().then(function(chunk) {
        if (chunk.done) { fertig(); return; }
        puffer += dec.decode(chunk.value, {stream: true});
        var zeilen = puffer.split("\\n");
        puffer = zeilen.pop();
        for (var i = 0; i < zeilen.length; i++) {
          var z = zeilen[i];
          if (!z.startsWith("data: ")) continue;
          var payload = z.slice(6);
          if (payload === "[DONE]") continue;
          try {
            var d = JSON.parse(payload);
            if (d.fertig) { ladeSitzung(SITZUNG.id); ladeSitzungsliste(); }
          } catch (e) {}
        }
        return lesen();
      });
    }
    return lesen();
  }).catch(function(err) {
    status("Fehler: " + err.message);
  }).finally(fertig);

  function fertig() {
    document.getElementById("sa-senden").disabled = false;
    status("");
  }
}

function triggerWesen(name) {
  var andere = SITZUNG.teilnehmer.filter(function(w) { return w !== name; });
  status(name + " antwortet …" + (andere.length ? "  (" + andere.join(", ") + " hören zu)" : ""));
  streameAntwort("/api/gruppenchat/sitzungen/" + encodeURIComponent(SITZUNG.id) +
                  "/trigger/" + encodeURIComponent(name), {});
}

document.getElementById("sa-senden").addEventListener("click", function() {
  var text = document.getElementById("sa-text").value.trim();
  if (!text || !SITZUNG) return;
  var modus = document.querySelector('input[name="modus"]:checked').value;
  var sprecher = document.getElementById("sa-sprecher").value;
  document.getElementById("sa-text").value = "";
  if (modus === "direkt") {
    var andere = SITZUNG.teilnehmer.filter(function(w) { return w !== sprecher; });
    status(sprecher + " antwortet …" + (andere.length ? "  (" + andere.join(", ") + " hören zu)" : ""));
  } else {
    status("alle hören zu (" + SITZUNG.teilnehmer.join(", ") + ")");
  }
  streameAntwort("/api/gruppenchat/sitzungen/" + encodeURIComponent(SITZUNG.id) + "/nachricht", {
    text: text, modus: modus, aktiver_sprecher: modus === "direkt" ? sprecher : null
  }).then(function() {
    if (modus === "zuhoeren") { ladeSitzung(SITZUNG.id); ladeSitzungsliste(); status(""); }
  });
});

document.getElementById("sa-an-alle").addEventListener("click", function() {
  if (!SITZUNG) return;
  fetch("/api/gruppenchat/sitzungen/" + encodeURIComponent(SITZUNG.id) + "/an_alle", {
    method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({text: ""})
  }).then(function(r) { return r.json(); }).then(function(d) {
    status(d.ok ? "als Nachricht an alle hinterlassen." : (d.fehler || "fehlgeschlagen"));
  });
});

// ── Posten-Dialog (Idee 5: ein bis alle Nachrichten waehlbar) ──────────────────
document.getElementById("sa-posten-oeffnen").addEventListener("click", function() {
  if (!SITZUNG || !SITZUNG.nachrichten.length) { alert("Noch keine Nachrichten in dieser Sitzung."); return; }
  document.getElementById("pd-titel").value = SITZUNG.titel;
  // GENI kann nicht posten (kein Flarum-Account ueber fuehre_post_aus) -- aus
  // der Auswahl ausgeschlossen, statt einen Server-Fehler zu riskieren.
  // "Admin" (Daniel selbst) zuerst in der Liste -- 2026-08-14, Daniel: "immernoch
  // nicht mit Gepostet von..admin drin".
  document.getElementById("pd-wesen").innerHTML =
    '<option value="Admin">Admin</option>' +
    SITZUNG.teilnehmer.filter(function(w) { return w !== "GENI"; }).map(function(w) {
      return '<option value="' + esc(w) + '">' + esc(w) + '</option>';
    }).join("");
  var optionen = SITZUNG.nachrichten.map(function(n, i) {
    return '<option value="' + i + '">#' + (i + 1) + ' ' + esc(anzeigeName(n.sprecher)) + '</option>';
  }).join("");
  document.getElementById("pd-von").innerHTML = optionen;
  document.getElementById("pd-bis").innerHTML = optionen;
  document.getElementById("pd-bis").value = String(SITZUNG.nachrichten.length - 1);
  document.getElementById("pd-fehler").textContent = "";
  document.getElementById("posten-dialog").style.display = "flex";
});
document.getElementById("pd-abbrechen").addEventListener("click", function() {
  document.getElementById("posten-dialog").style.display = "none";
});
document.getElementById("pd-posten").addEventListener("click", function() {
  var von = parseInt(document.getElementById("pd-von").value, 10);
  var bis = parseInt(document.getElementById("pd-bis").value, 10);
  if (bis < von) { document.getElementById("pd-fehler").textContent = "»bis« liegt vor »von«."; return; }
  fetch("/api/gruppenchat/sitzungen/" + encodeURIComponent(SITZUNG.id) + "/posten", {
    method: "POST", headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      als_wesen: document.getElementById("pd-wesen").value,
      titel: document.getElementById("pd-titel").value.trim() || SITZUNG.titel,
      von_index: von, bis_index: bis + 1
    })
  }).then(function(r) { return r.json(); }).then(function(d) {
    if (d.fehler) { document.getElementById("pd-fehler").textContent = d.fehler; return; }
    document.getElementById("posten-dialog").style.display = "none";
    status("Gepostet — #" + (d.diskussion_id || "?"));
  });
});

// ── Zusammenfassen (Daniel zuerst: "mach den deckel weg ganz frei aber ich
// will ... zusammenfassen", dann praezisiert: "nicht nur alles zusammenfassen
// sondern auch nur einen der nachrichten oder mehrere bis hin zu alle
// markierbar") -- von/bis wie beim Posten-Dialog, Default ist der ganze
// bisherige Verlauf (deckt den urspruenglichen Wunsch weiterhin ab, nur ein
// Klick mehr fuer den Standardfall). Nach Erfolg beginnt der Kontext fuer
// kuenftige Zuege an dieser Zusammenfassung statt am rohen Bereich
// (_gruppenchat_kontext_sequenz()).
document.getElementById("sa-zusammenfassen").addEventListener("click", function() {
  if (!SITZUNG || !SITZUNG.nachrichten.length) { alert("Noch keine Nachrichten in dieser Sitzung."); return; }
  var optionen = SITZUNG.nachrichten.map(function(n, i) {
    return '<option value="' + i + '">#' + i + ' ' + esc(anzeigeName(n.sprecher)) + '</option>';
  }).join("");
  document.getElementById("zf-von").innerHTML = optionen;
  document.getElementById("zf-bis").innerHTML = optionen;
  document.getElementById("zf-von").value = "0";
  document.getElementById("zf-bis").value = String(SITZUNG.nachrichten.length - 1);
  document.getElementById("zf-fehler").textContent = "";
  document.getElementById("zf-dialog").style.display = "flex";
});
document.getElementById("zf-abbrechen").addEventListener("click", function() {
  document.getElementById("zf-dialog").style.display = "none";
});
document.getElementById("zf-erstellen").addEventListener("click", function() {
  var von = parseInt(document.getElementById("zf-von").value, 10);
  var bis = parseInt(document.getElementById("zf-bis").value, 10);
  if (bis < von) { document.getElementById("zf-fehler").textContent = "»bis« liegt vor »von«."; return; }
  var knopf = this, alt = knopf.textContent;
  knopf.disabled = true; knopf.textContent = "fasst zusammen …";
  var fehlerText = "";
  sseLesen("/api/gruppenchat/sitzungen/" + encodeURIComponent(SITZUNG.id) + "/zusammenfassen",
    {von_index: von, bis_index: bis + 1},
    function(d) { if (d.fehler) fehlerText = d.fehler; }
  ).then(function() {
    knopf.disabled = false; knopf.textContent = alt;
    if (fehlerText) { document.getElementById("zf-fehler").textContent = fehlerText; return; }
    document.getElementById("zf-dialog").style.display = "none";
    ladeSitzung(SITZUNG.id); ladeSitzungsliste();
  }).catch(function(err) { knopf.disabled = false; knopf.textContent = alt;
                            document.getElementById("zf-fehler").textContent = "Fehler: " + err.message; });
});

// ── Geschichten (Daniel 2026-08-14: "ne neugierige geschichten funktion so
// wie in den normalen chats ... an groesse waehlbar ... mehrere gleichzeitig
// ausgewaehlt ... fuer alle zugefuegt bis man sie manuell deaktiviert") --
// gleiches Muster wie die Geschichten im 1:1-Chat (ge-laengen/ge-liste dort),
// aber sitzungsweit statt pro Wesen.
document.getElementById("sa-geschichten-oeffnen").addEventListener("click", function() {
  if (!SITZUNG) return;
  ladeGeschichtenGc();
  document.getElementById("ge-dialog").style.display = "flex";
});
document.getElementById("ge-schliessen").addEventListener("click", function() {
  document.getElementById("ge-dialog").style.display = "none";
});
// 2026-08-14, Daniel: die Vorschau schnitt hart bei Zeichen 400 ab, auch mitten
// im Wort ("gewec…" statt "geweckt…") -- kein Lesepfad fuer den vollen Text
// vorhanden, nur der Bearbeiten-Modus zeigte ihn (nicht dafuer gedacht, gerade
// bei sehr langen Automodus-Geschichten mit tausenden Woertern). Vorschau jetzt
// wortgrenzen-sicher, plus eigener "vollstaendig lesen"-Umschalter.
function geVorschau(text) {
  if (text.length <= 400) return esc(text);
  var schnitt = text.lastIndexOf(" ", 400);
  if (schnitt < 200) schnitt = 400; // kein Leerzeichen gefunden -- Notnagel
  return esc(text.slice(0, schnitt)) + "…";
}
function ladeGeschichtenGc() {
  return fetch("/api/gruppenchat/sitzungen/" + encodeURIComponent(SITZUNG.id) + "/geschichten")
    .then(function(r) { return r.json(); }).then(function(d) {
      document.getElementById("ge-laengen").innerHTML = d.laengen.map(function(l) {
        return '<button type="button" class="leise ge-verfassen-gc" data-l="' + l + '">' + l + "</button>";
      }).join("");
      document.getElementById("ge-liste").innerHTML = d.geschichten.length
        ? d.geschichten.map(function(g) {
            return '<div class="ge-box' + (g.aktiv ? "" : " inaktiv") + '" data-gid="' + g.id + '">' +
              '<div class="ge-box-kopf">' +
                '<input type="checkbox" class="ge-aktiv-gc"' + (g.aktiv ? " checked" : "") + ">" +
                "<span>" + esc(g.titel) + (g.bearbeitet ? " (bearbeitet)" : "") + "</span>" +
                '<span class="leise ge-edit-oeffnen" style="margin-left:auto; cursor:pointer;">✎</span>' +
                '<span class="ge-weg ge-weg-gc">✕</span>' +
              "</div>" +
              '<div class="ge-box-text ge-anzeige">' + geVorschau(g.text) + "</div>" +
              (g.text.length > 400
                ? '<span class="leise ge-voll-oeffnen" data-woerter="' + g.text.split(/\\s+/).length + '" ' +
                  'style="cursor:pointer; font-size:0.72rem; color:#7a9a7a;">' +
                  'vollständig lesen (' + g.text.split(/\\s+/).length + ' Wörter) …</span>' +
                  '<div class="ge-voll-text" style="display:none; white-space:pre-wrap; max-height:50vh; ' +
                  'overflow-y:auto; font-size:0.78rem; color:#ccc; line-height:1.6; margin-top:0.4rem; ' +
                  'border-top:1px solid #2a2a2a; padding-top:0.4rem;">' + esc(g.text) + "</div>"
                : "") +
              '<div class="ge-edit-bereich" style="display:none;">' +
                '<input type="text" class="ge-edit-titel" value="' + esc(g.titel) + '" ' +
                  'style="width:100%; box-sizing:border-box; margin-bottom:0.3rem; font-weight:bold;">' +
                '<textarea class="ge-edit-text" rows="20" style="width:100%; box-sizing:border-box; ' +
                  'min-height:40vh; resize:vertical;">' + esc(g.text) + "</textarea>" +
                '<div class="knopfzeile" style="margin-top:0.3rem;">' +
                  '<button type="button" class="ge-edit-speichern">speichern</button>' +
                  '<button type="button" class="leise ge-edit-abbrechen">abbrechen</button>' +
                "</div>" +
              "</div>" +
            "</div>";
          }).join("")
        : '<div style="font-size:0.76rem; color:#666;">noch keine Geschichte</div>';
    });
}
document.getElementById("ge-laengen").addEventListener("click", function(e) {
  if (!e.target.classList.contains("ge-verfassen-gc")) return;
  var knopf = e.target, alt = knopf.textContent;
  knopf.disabled = true; knopf.textContent = "…";
  document.getElementById("ge-status").textContent = "verfasst …";
  var fehlerText = "";
  sseLesen("/api/gruppenchat/sitzungen/" + encodeURIComponent(SITZUNG.id) + "/geschichten/verfassen",
    {laenge: parseInt(knopf.getAttribute("data-l"), 10)},
    function(d) { if (d.fehler) fehlerText = d.fehler; }
  ).then(function() {
    knopf.disabled = false; knopf.textContent = alt;
    document.getElementById("ge-status").textContent = fehlerText;
    if (!fehlerText) ladeGeschichtenGc();
  }).catch(function(err) { knopf.disabled = false; knopf.textContent = alt;
                            document.getElementById("ge-status").textContent = "Fehler: " + err.message; });
});
document.getElementById("ge-verfassen-auto").addEventListener("click", function() {
  var knopf = this, alt = knopf.textContent;
  knopf.disabled = true; knopf.textContent = "liest komplett und schreibt …";
  document.getElementById("ge-status").textContent = "Automodus laeuft — kann laenger dauern …";
  var fehlerText = "";
  sseLesen("/api/gruppenchat/sitzungen/" + encodeURIComponent(SITZUNG.id) + "/geschichten/verfassen",
    {modus: "auto"},
    function(d) { if (d.fehler) fehlerText = d.fehler; }
  ).then(function() {
    knopf.disabled = false; knopf.textContent = alt;
    document.getElementById("ge-status").textContent = fehlerText;
    if (!fehlerText) ladeGeschichtenGc();
  }).catch(function(err) { knopf.disabled = false; knopf.textContent = alt;
                            document.getElementById("ge-status").textContent = "Fehler: " + err.message; });
});
document.getElementById("ge-liste").addEventListener("click", function(e) {
  var box = e.target.closest(".ge-box[data-gid]");
  if (!box) return;
  var gid = box.getAttribute("data-gid");
  if (e.target.classList.contains("ge-aktiv-gc")) {
    fetch("/api/gruppenchat/sitzungen/" + encodeURIComponent(SITZUNG.id) + "/geschichten/" + gid + "/aktiv", {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify({aktiv: e.target.checked})
    }).then(function() { ladeGeschichtenGc(); });
  } else if (e.target.classList.contains("ge-weg-gc")) {
    fetch("/api/gruppenchat/sitzungen/" + encodeURIComponent(SITZUNG.id) + "/geschichten/" + gid + "/entfernen",
          { method: "POST" }).then(function() { ladeGeschichtenGc(); });
  } else if (e.target.classList.contains("ge-voll-oeffnen")) {
    var vollDiv = box.querySelector(".ge-voll-text");
    var jetztOffen = vollDiv.style.display === "none";
    vollDiv.style.display = jetztOffen ? "block" : "none";
    e.target.textContent = jetztOffen
      ? "einklappen"
      : "vollständig lesen (" + e.target.getAttribute("data-woerter") + " Wörter) …";
  } else if (e.target.classList.contains("ge-edit-oeffnen")) {
    // 2026-08-14, Daniel: "warum kann ich die geschichten nicht editieren
    // komplett wie gewuenscht" -- Vollansicht (falls offen) mit ausblenden,
    // damit der Editor nicht neben einer zweiten Textkopie steht.
    box.querySelector(".ge-anzeige").style.display = "none";
    var vollSpan = box.querySelector(".ge-voll-oeffnen");
    var vollDivEdit = box.querySelector(".ge-voll-text");
    if (vollSpan) vollSpan.style.display = "none";
    if (vollDivEdit) vollDivEdit.style.display = "none";
    box.querySelector(".ge-edit-bereich").style.display = "block";
  } else if (e.target.classList.contains("ge-edit-abbrechen")) {
    box.querySelector(".ge-anzeige").style.display = "";
    var vollSpan2 = box.querySelector(".ge-voll-oeffnen");
    if (vollSpan2) vollSpan2.style.display = "";
    box.querySelector(".ge-edit-bereich").style.display = "none";
  } else if (e.target.classList.contains("ge-edit-speichern")) {
    var neuerText = box.querySelector(".ge-edit-text").value.trim();
    var neuerTitel = box.querySelector(".ge-edit-titel").value.trim();
    if (!neuerText) return;
    fetch("/api/gruppenchat/sitzungen/" + encodeURIComponent(SITZUNG.id) + "/geschichten/" + gid + "/bearbeiten", {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify({text: neuerText, titel: neuerTitel})
    }).then(function() { ladeGeschichtenGc(); });
  }
});

// ── Memory-Vorschläge (Daniel 2026-08-14: "nen memorysystemknopf der
// vorschlaege fuer jedes wesen macht ... das muss ich dann alles bestaetigen
// oder ablehnen und auch frei editieren koennen ... genau so will ich selber
// was reinschreiben koennen komplett") -- Vorschlaege sind reine Vorschau bis
// zum Bestaetigen, editierbar direkt in der Karte, manueller Eintrag nutzt
// denselben bestehenden Endpunkt wie der 1:1-Chat.
var MEMORY_KATEGORIEN = [
  {key: "ueber_mich", label: "Über dich"},
  {key: "wichtige_momente", label: "Wichtige Momente"},
  {key: "offene_fragen", label: "Offene Fragen"},
  {key: "wesen_selbst", label: "Wesen selbst"},
  {key: "meinungen", label: "Meinungen"}
];
function mvKategorieOptions(gewaehlt) {
  return MEMORY_KATEGORIEN.map(function(k) {
    return '<option value="' + k.key + '"' + (k.key === gewaehlt ? " selected" : "") + ">" + k.label + "</option>";
  }).join("");
}
document.getElementById("sa-memory-oeffnen").addEventListener("click", function() {
  if (!SITZUNG) return;
  var sel = document.getElementById("mv-eigen-wesen");
  sel.innerHTML = SITZUNG.teilnehmer.filter(function(w) { return w !== "GENI"; }).map(function(w) {
    return '<option value="' + esc(w) + '">' + esc(w) + '</option>';
  }).join("");
  document.getElementById("mv-eigen-kategorie").innerHTML = mvKategorieOptions();
  document.getElementById("mv-eigen-text").value = "";
  document.getElementById("mv-eigen-fehler").textContent = "";
  document.getElementById("memory-dialog").style.display = "flex";
  // 2026-08-14, Daniel zunaechst: automatisch beim Oeffnen generieren -- dann
  // nach den Erfahrungen mit unterbrochenen Laeufen (Service-Neustarts waehrend
  // einer laufenden Generierung) zurueckgerudert: "ich will selber klicken dass
  // es generieren soll ... es selbst nochmal aktivieren". Oeffnen laedt nur noch
  // den bestehenden Stand, startet nichts von selbst.
  ladeMemoryVorschlaege();
});
document.getElementById("mv-schliessen").addEventListener("click", function() {
  document.getElementById("memory-dialog").style.display = "none";
});
function ladeMemoryVorschlaege() {
  // Gibt (per .then) zurueck, ob mindestens ein OFFENER Vorschlag existiert --
  // steuert das automatische Anstossen der Generierung beim Dialog-Oeffnen.
  return fetch("/api/gruppenchat/sitzungen/" + encodeURIComponent(SITZUNG.id) + "/memory_vorschlaege")
    .then(function(r) { return r.json(); }).then(function(d) {
      var liste = d.vorschlaege || [];
      document.getElementById("mv-liste").innerHTML = liste.length
        ? liste.map(function(v) {
            var offen = v.status === "offen";
            return '<div class="mv-box" data-vid="' + v.id + '" data-status="' + v.status + '">' +
              '<div class="ge-box-kopf">' +
                '<span style="font-weight:bold;">' + esc(v.wesen) + "</span>" +
                '<select class="mv-kategorie"' + (offen ? "" : " disabled") + ">" + mvKategorieOptions(v.kategorie) + "</select>" +
                '<span style="margin-left:auto; font-size:0.7rem; color:#999;">' + esc(v.status) + "</span>" +
              "</div>" +
              '<textarea class="mv-text" rows="6" style="width:100%; box-sizing:border-box; margin-top:0.3rem; ' +
                'resize:vertical;"' + (offen ? "" : " disabled") + ">" + esc(v.text) + "</textarea>" +
              (offen
                ? '<div class="knopfzeile" style="margin-top:0.3rem;">' +
                    '<button type="button" class="mv-bestaetigen">bestätigen</button>' +
                    '<button type="button" class="leise mv-ablehnen">ablehnen</button>' +
                  "</div>"
                : "") +
            "</div>";
          }).join("")
        : '<div style="font-size:0.76rem; color:#666;">noch keine Vorschläge</div>';
      return liste.some(function(v) { return v.status === "offen"; });
    });
}
// 2026-08-14, Daniel: "ich will ne zeit die hochlaeuft und ich will ne
// ungefaehre geschaetze zeit" -- Uhr zaehlt jede Sekunde hoch (Beweis dass
// wirklich noch etwas laeuft, nicht nur ein statischer "laeuft..."-Text), die
// Schaetzung basiert auf dem tatsaechlichen Durchschnitt der bereits fertigen
// Wesen DIESES Laufs -- kein fester Rateweert, weil die Dauer stark mit der
// aktuellen Systemlast schwankt (7-12 Minuten pro Wesen unter Last beobachtet).
var mvGesamtWesen = 0, mvErledigtWesen = 0, mvDauerSummeSek = 0,
    mvAktuellerStart = 0, mvBatchStart = 0, mvTimerHandle = null;

function mvZeitFormat(sek) {
  sek = Math.max(0, Math.round(sek));
  var m = Math.floor(sek / 60), s = sek % 60;
  return m + ":" + (s < 10 ? "0" : "") + s;
}
function mvTimerAktualisieren() {
  var vergangen = (Date.now() - mvBatchStart) / 1000;
  var text = "läuft seit " + mvZeitFormat(vergangen);
  if (mvErledigtWesen > 0) {
    var schnitt = mvDauerSummeSek / mvErledigtWesen;
    var verbleibend = mvGesamtWesen - mvErledigtWesen;
    if (verbleibend > 0) {
      text += " — geschätzt noch ~" + mvZeitFormat(schnitt * verbleibend) +
              " für " + verbleibend + " verbleibende Wesen (Ø " + mvZeitFormat(schnitt) + "/Wesen bisher)";
    }
  }
  document.getElementById("mv-timer").textContent = text;
}
function mvGeneriereVorschlaege() {
  var knopf = document.getElementById("mv-generieren"), alt = knopf.textContent;
  knopf.disabled = true; knopf.textContent = "generiert …";
  document.getElementById("mv-status").textContent = "läuft …";
  mvGesamtWesen = (SITZUNG.teilnehmer || []).filter(function(w) { return w !== "GENI"; }).length;
  mvErledigtWesen = 0; mvDauerSummeSek = 0;
  mvBatchStart = mvAktuellerStart = Date.now();
  if (mvTimerHandle) clearInterval(mvTimerHandle);
  mvTimerHandle = setInterval(mvTimerAktualisieren, 1000);
  mvTimerAktualisieren();
  return fetch("/api/gruppenchat/sitzungen/" + encodeURIComponent(SITZUNG.id) + "/memory_vorschlaege/generieren", {
    method: "POST"
  }).then(function(r) {
    var reader = r.body.getReader();
    var dec = new TextDecoder();
    var puffer = "";
    function lesen() {
      return reader.read().then(function(chunk) {
        if (chunk.done) { fertig(); return; }
        puffer += dec.decode(chunk.value, {stream: true});
        var zeilen = puffer.split("\\n");
        puffer = zeilen.pop();
        for (var i = 0; i < zeilen.length; i++) {
          var z = zeilen[i];
          if (!z.startsWith("data: ")) continue;
          var payload = z.slice(6);
          if (payload === "[DONE]") continue;
          try {
            var d = JSON.parse(payload);
            if (d.beginnt) {
              document.getElementById("mv-status").textContent = d.beginnt + " liest und überlegt …";
              mvAktuellerStart = Date.now();
            } else if (d.fertig) {
              var dauerSek = (Date.now() - mvAktuellerStart) / 1000;
              mvDauerSummeSek += dauerSek; mvErledigtWesen += 1;
              document.getElementById("mv-status").textContent =
                d.fertig + ": " + d.anzahl + " Vorschläge (" + mvZeitFormat(dauerSek) + ")";
              mvTimerAktualisieren();
              ladeMemoryVorschlaege();
            }
          } catch (e) {}
        }
        return lesen();
      });
    }
    return lesen();
  }).catch(function(err) { document.getElementById("mv-status").textContent = "Fehler: " + err.message; })
    .finally(function() {
      knopf.disabled = false; knopf.textContent = alt;
      if (mvTimerHandle) { clearInterval(mvTimerHandle); mvTimerHandle = null; }
      document.getElementById("mv-timer").textContent = "";
      document.getElementById("mv-status").textContent = "";
      ladeMemoryVorschlaege();
    });
}
document.getElementById("mv-generieren").addEventListener("click", mvGeneriereVorschlaege);
document.getElementById("mv-liste").addEventListener("click", function(e) {
  var box = e.target.closest(".mv-box[data-vid]");
  if (!box) return;
  var vid = box.getAttribute("data-vid");
  if (e.target.classList.contains("mv-bestaetigen")) {
    var text = box.querySelector(".mv-text").value.trim();
    var kategorie = box.querySelector(".mv-kategorie").value;
    if (!text) return;
    fetch("/api/gruppenchat/sitzungen/" + encodeURIComponent(SITZUNG.id) + "/memory_vorschlaege/" + vid + "/bestaetigen", {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify({text: text, kategorie: kategorie})
    }).then(function() { ladeMemoryVorschlaege(); });
  } else if (e.target.classList.contains("mv-ablehnen")) {
    fetch("/api/gruppenchat/sitzungen/" + encodeURIComponent(SITZUNG.id) + "/memory_vorschlaege/" + vid + "/ablehnen",
          { method: "POST" }).then(function() { ladeMemoryVorschlaege(); });
  }
});
document.getElementById("mv-eigen-hinzufuegen").addEventListener("click", function() {
  var wesen = document.getElementById("mv-eigen-wesen").value;
  var kategorie = document.getElementById("mv-eigen-kategorie").value;
  var text = document.getElementById("mv-eigen-text").value.trim();
  var fehler = document.getElementById("mv-eigen-fehler");
  if (!text) { fehler.textContent = "Text fehlt."; return; }
  fetch("/api/gruppenchat/sitzungen/" + encodeURIComponent(SITZUNG.id) + "/memory_manuell", {
    method: "POST", headers: {"Content-Type": "application/json"},
    body: JSON.stringify({wesen: wesen, kategorie: kategorie, text: text})
  }).then(function(r) { return r.json(); }).then(function(d) {
    if (d.fehler) { fehler.textContent = d.fehler; return; }
    fehler.textContent = "";
    document.getElementById("mv-eigen-text").value = "";
  }).catch(function() { fehler.textContent = "Fehler beim Hinzufügen."; });
});

// ── Alle antworten, ECHT nacheinander (Daniel, 2026-08-13: "ich will einen
// knopf der ... alle direkt antworten [laesst] ... aber wirklich alle aktuellen
// sachen jeweils komplett ausliest") -- ein Klick, mehrere echte LLM-Aufrufe
// hintereinander (kein simulierter Multi-Voice-Call, das war exakt der Bug bei
// jumpa). Server-Stream enthaelt mehrere 'fertig'-Ereignisse hintereinander und
// erst am Ende ein einzelnes [DONE] -- braucht deshalb einen eigenen Reader statt
// des bestehenden streameAntwort(), der beim ERSTEN [DONE] aufhoert zu lesen.
function streameAlleAntworten(url) {
  document.getElementById("sa-alle-antworten").disabled = true;
  return fetch(url, { method: "POST", headers: {"Content-Type": "application/json"}, body: "{}" })
    .then(function(r) {
      var reader = r.body.getReader();
      var dec = new TextDecoder();
      var puffer = "";
      function lesen() {
        return reader.read().then(function(chunk) {
          if (chunk.done) { fertig(); return; }
          puffer += dec.decode(chunk.value, {stream: true});
          var zeilen = puffer.split("\\n");
          puffer = zeilen.pop();
          for (var i = 0; i < zeilen.length; i++) {
            var z = zeilen[i];
            if (!z.startsWith("data: ")) continue;
            var payload = z.slice(6);
            if (payload === "[DONE]") continue;  // erst am ganz Ende, Stream laeuft trotzdem weiter
            try {
              var d = JSON.parse(payload);
              if (d.beginnt) {
                status(d.beginnt + " antwortet … (echt, einzeln)");
              } else if (d.fertig) {
                ladeSitzung(SITZUNG.id);
              }
            } catch (e) {}
          }
          return lesen();
        });
      }
      return lesen();
    }).catch(function(err) { status("Fehler: " + err.message); }).finally(fertig);

  function fertig() {
    document.getElementById("sa-alle-antworten").disabled = false;
    ladeSitzungsliste();
    status("");
  }
}
document.getElementById("sa-alle-antworten").addEventListener("click", function() {
  if (!SITZUNG) return;
  streameAlleAntworten("/api/gruppenchat/sitzungen/" + encodeURIComponent(SITZUNG.id) + "/alle_antworten");
});

// ── Kontextfenster ansehen + bearbeiten (Daniel: "ich will das aktuelle
// kontextfenster sehen und auch editieren können so wie in den anderen chat") --
// vereinfachte Variante der 1:1-Chat-Redaktion: Saetze statt einzelner Woerter
// auswaehlbar (deckt "ganze Saetze ... loeschen" ab, nicht die feinste Koernung
// von dort -- bewusste Vereinfachung fuer den ersten Wurf).
function splitSaetze(text) {
  return text.match(/[^.!?]+[.!?]*/g) || [text];
}
document.getElementById("sa-kontext-oeffnen").addEventListener("click", function() {
  if (!SITZUNG) return;
  var sel = document.getElementById("kd-wesen");
  sel.innerHTML = SITZUNG.teilnehmer.filter(function(w) { return w !== "GENI"; }).map(function(w) {
    return '<option value="' + esc(w) + '">' + esc(w) + '</option>';
  }).join("");
  document.getElementById("kd-inhalt").innerHTML = "";
  document.getElementById("kd-entfernen").disabled = true;
  document.getElementById("kontext-dialog").style.display = "flex";
});
document.getElementById("kd-schliessen").addEventListener("click", function() {
  document.getElementById("kontext-dialog").style.display = "none";
});
function kdAuswahlAktualisieren() {
  var leer = document.querySelectorAll("#kd-inhalt .kd-satz.gewaehlt").length === 0;
  document.getElementById("kd-entfernen").disabled = leer;
}
document.getElementById("kd-laden").addEventListener("click", function() {
  var name = document.getElementById("kd-wesen").value;
  var box = document.getElementById("kd-inhalt");
  box.innerHTML = "lädt …";
  fetch("/api/gruppenchat/sitzungen/" + encodeURIComponent(SITZUNG.id) + "/kontext/" + encodeURIComponent(name))
    .then(function(r) { return r.json(); }).then(function(d) {
      if (d.fehler) { box.textContent = d.fehler; return; }
      var kopf = '<div style="margin-bottom:0.6rem;">Gesamt ' + d.summe_tokens + ' Token' +
        (d.slot_ctx ? ' von ' + d.slot_ctx + ' (' + Math.round((d.auslastung||0)*100) + '%)' : '') + '</div>' +
        d.schichten.map(function(s) {
          return '<div class="kontext-zeile"><span>' + esc(s.titel) + '</span><span>' + s.tokens + ' Tok</span></div>';
        }).join("");
      var nachrichten = '<div style="margin-top:0.8rem; font-weight:bold; color:#c8c8c8;">Nachrichten (Sätze anklicken zum Markieren):</div>' +
        d.nachrichten.map(function(n) {
          var saetze = splitSaetze(n.inhalt).map(function(satz) {
            return '<span class="kd-satz" data-index="' + n.index + '">' + esc(satz) + '</span>';
          }).join(" ");
          return '<div class="kd-nachricht' + (n.redigiert ? " kd-redigiert" : "") + '">' +
            '<div class="n-kopf"><span class="n-sprecher">#' + n.index + ' ' + esc(anzeigeName(n.sprecher)) + '</span>' +
            (n.redigiert ? '<span style="color:#c87a7a;">bereits bearbeitet</span>' : '') + '</div>' +
            saetze + '</div>';
        }).join("");
      box.innerHTML = kopf + nachrichten;
    });
});
document.getElementById("kd-inhalt").addEventListener("click", function(e) {
  if (!e.target.classList.contains("kd-satz")) return;
  e.target.classList.toggle("gewaehlt");
  kdAuswahlAktualisieren();
});
document.getElementById("kd-entfernen").addEventListener("click", function() {
  var gewaehlt = document.querySelectorAll("#kd-inhalt .kd-satz.gewaehlt");
  var proIndex = {};
  gewaehlt.forEach(function(el) {
    var idx = el.getAttribute("data-index");
    (proIndex[idx] = proIndex[idx] || []).push(el.textContent);
  });
  var anfragen = Object.keys(proIndex).map(function(idx) {
    return fetch("/api/gruppenchat/sitzungen/" + encodeURIComponent(SITZUNG.id) +
                 "/nachricht/" + idx + "/redaktion", {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify({entfernt: proIndex[idx]})
    });
  });
  Promise.all(anfragen).then(function() {
    document.getElementById("kd-laden").click();
    ladeSitzung(SITZUNG.id);
  });
});

ladeSitzungsliste();
</script>
</body>
</html>"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002, log_level="warning")
