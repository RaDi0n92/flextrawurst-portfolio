#!/usr/bin/env python3
"""
Codewesen-Reaktions-Agent — ein Prozess PRO Wesen (7 Instanzen: die 6
namelessAI + dak+gord-system), Konfiguration in dienst_konfiguration je
Instanz separat (codewesen-reaktion@<Name>, Ausnahmen: -traeumerlie/-dakgord
wegen URL-Sonderzeichen). Takt/Verhalten werden NUR EINMAL beim Prozessstart
gelesen (siehe run()) — ein Neustart macht Aenderungen wirksam, nicht "ab dem
naechsten Zyklus".

Aufruf: python3 codewesen_reaktion.py <codewesen_name>

EIN Loop, `time.sleep(CHECK_INTERVAL)` (Standard 600s) am Ende — darin werden
bei JEDEM Durchlauf mehrere unabhaengige Sachen geprueft, jede mit eigenem
laenger laufenden Intervall (siehe meta.intervalle-Keys):

  process_inbox (jeden Durchlauf, ungated): nur 1 Item aus der Inbox pro Aufruf
    (verhindert Monopolisierung des gemeinsamen LLM-Slots). Reagiert auf
    menschliche Posts UND Posts anderer Codewesen. Zwei LLM-Stufen: erst eine
    kleine Entscheidung (antworten/neue_diskussion/ignorieren, PRIO_HOCH),
    dann bei Bedarf die volle Inhaltsgenerierung (ebenfalls PRIO_HOCH — direkte
    Reaktionen haben Vorrang vor Hintergrund-Content). Fehlerhafte Items landen
    in fehler/ und werden nach fehler_retry_interval (Standard 300s) automatisch
    zurueck in die Inbox verschoben.
  selbstreflexion (alle reflexions_interval, Standard 300s): liest eigene
    fruehere Posts, entscheidet autonom ob es dort noch etwas hinzuzufuegen gibt.
  post_forum_entwicklung (alle forum_entwicklung_interval, Standard 142min/2h22).
  post_themen_beitrag (alle themen_beitrag_interval, Standard 88min).
  zwischenraum_scan (alle zwischenraum_scan_interval, Standard 900s/15min,
    aus codewesen_abwurf.py) — neugieriger Blick in den Splitter-Zwischenraum.

Vokabel-Threads werden komplett ausgenommen (dafuer ist codewesen_vokabel_takt.py
zustaendig).

Kleine Details, komplett gegengelesen (2026-07-07): `ask_llm()` prueft ob eine
Antwort mit vollstaendiger Satzzeichensetzung endet (`_ist_vollstaendig`) und
fordert bei Bedarf eine kurze Fortsetzung nach statt einen abgeschnittenen Text
zu posten. `post_forum_entwicklung`/`post_themen_beitrag` starten beide eine
NEUE Diskussion (nicht nur Antworten) mit vom LLM selbst gewaehlten Tags.
"""

import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
import psycopg2
import psycopg2.extras

sys.path.insert(0, "/root/werkraum")
import hauhau_client
import llm_scheduler

import gedaechtnis
import flarum_api as _fapi
from codewesen_abwurf import verarbeite_abwurf, zwischenraum_scan
import dienst_konfiguration as dk
from flarum_vokabel_filter import ist_vokabel_thread

BASE = Path("/root/werkraum/codewesen")
_DB_ENV = Path("/root/werkraum/.agent/flextrawurst-db.env")


def _get_db_uri() -> str:
    try:
        for line in _DB_ENV.read_text().splitlines():
            if line.startswith("FLEXTRAWURST_DB_URI="):
                return line.split("=", 1)[1]
    except Exception:
        pass
    return ""


def _lade_letzten_chat(wesen_name: str, n: int = 3) -> str:
    """Letzte n Chat-Zeilen (Daniel↔Wesen) als kompakten Text."""
    try:
        uri = _get_db_uri()
        if not uri:
            return ""
        conn = psycopg2.connect(uri, cursor_factory=psycopg2.extras.RealDictCursor)
        with conn.cursor() as cur:
            cur.execute(
                """SELECT rolle, inhalt, created_at FROM wesen_chat_verlauf
                   WHERE wesen_name=%s ORDER BY created_at DESC LIMIT %s""",
                (wesen_name, n)
            )
            rows = list(reversed(cur.fetchall()))
        conn.close()
        if not rows:
            return ""
        zeilen = []
        for r in rows:
            sprecher = "Daniel" if r["rolle"] == "user" else "Du"
            ts = str(r["created_at"])[:16]
            zeilen.append(f"[{ts}] {sprecher}: {r['inhalt'][:300]}")
        return "\n".join(zeilen)
    except Exception:
        return ""


def _lade_system_status() -> str:
    """Liest flarum_eingefroren aus system_flags."""
    try:
        uri = _get_db_uri()
        if not uri:
            return ""
        conn = psycopg2.connect(uri, cursor_factory=psycopg2.extras.RealDictCursor)
        with conn.cursor() as cur:
            cur.execute("SELECT key, value FROM system_flags WHERE key='flarum_eingefroren'")
            row = cur.fetchone()
        conn.close()
        if row and row["value"] == "true":
            return "WICHTIG: Flarum ist derzeit eingefroren. Du kannst dort im Moment NICHT posten. Wenn Daniel oder jemand dich nach einem Post fragt, erkläre das klar."
        return "Flarum läuft normal."
    except Exception:
        return ""


def _lade_wesen_identitaet(name: str) -> str:
    """Liest wesen.md + weltbild.md als kompakten Identitätsblock."""
    teile: list[str] = []
    wesen_md = BASE / name / "wesen.md"
    weltbild = BASE / name / "weltbild.md"
    if wesen_md.exists():
        try:
            teile.append(wesen_md.read_text(encoding="utf-8", errors="replace")[:400].strip())
        except Exception:
            pass
    if weltbild.exists():
        try:
            wb = weltbild.read_text(encoding="utf-8", errors="replace")
            wb = wb.split("---", 2)[-1].strip()[:300]
            if wb:
                teile.append(wb)
        except Exception:
            pass
    if _aktuelles_verhalten:
        teile.append(_aktuelles_verhalten)
    return "\n\n".join(teile) if teile else "(Keine Identitätsdatei gefunden.)"
OLLAMA_MODEL        = "hauhaucs-q6"
OLLAMA_MODEL_SCHNELL = "hauhaucs-q6"
TOKENS_FILE = BASE / "_api_tokens.json"
CHECK_INTERVAL = 600       # Sekunden zwischen Inbox-Checks
REFLEXIONS_INTERVAL = 300  # Sekunden zwischen Selbstreflexions-Checks

# Individualisierung (flarumstyler, 2026-07-07): laeuft pro Wesen als eigener Prozess —
# jedes Wesen bekommt seine eigene dienst_konfiguration-Zeile, passend zu Daniels
# Wunsch nach Konfiguration "individuell pro Wesen". Mehrere benannte Intervalle wie
# bei codewesen_takt.py, deshalb ueber meta.intervalle statt einem einzigen takt_sekunden.
_DIENSTNAME_AUSNAHMEN = {"dak+gord-system": "codewesen-reaktion-dakgord", "träumerlie": "codewesen-reaktion-traeumerlie"}
def dienst_name_fuer(wesen: str) -> str:
    return _DIENSTNAME_AUSNAHMEN.get(wesen, f"codewesen-reaktion@{wesen}")

STANDARD_VERHALTEN = ""
_aktuelles_verhalten = STANDARD_VERHALTEN

# Interner Name → Flarum-Username (lazily befüllt)
_FORUM_USERNAME_CACHE: dict = {}


def _forum_username(internal_name: str) -> str:
    """Löst internen Ordnernamen auf den tatsächlichen Flarum-Username auf."""
    if internal_name not in _FORUM_USERNAME_CACHE:
        try:
            tokens_data = json.loads(TOKENS_FILE.read_text())
            uid = int(tokens_data[internal_name]["user_id"])
            _FORUM_USERNAME_CACHE[internal_name] = _fapi.get_username_by_id(uid)
        except Exception:
            _FORUM_USERNAME_CACHE[internal_name] = internal_name
    return _FORUM_USERNAME_CACHE[internal_name]



# Autonome Post-Zyklen
FORUM_ENTWICKLUNG_INTERVAL = 142 * 60   # 2h22m in Sekunden
THEMEN_BEITRAG_INTERVAL    =  88 * 60   # 88min in Sekunden

ALLE_NAMEN = [
    "Schorschel", "Resonanzknoten", "träumerlie",
    "F3INSCHM3CK3R", "R1ZZ1", "jumpa",
    "dak+gord-system",
]

# Flarum-Tags (werden beim Start geladen)
_TAGS_CACHE: list = []


def setup_logging(name: str):
    logging.basicConfig(
        level=logging.INFO,
        format=f"%(asctime)s [{name}] %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(str(BASE / name / "reaktion.log")),
            logging.StreamHandler(),
        ],
    )
    return logging.getLogger(name)


def load_token(name: str) -> str:
    # Gibt jetzt einfach den Username zurück — flarum_api nutzt Master-Key
    return name


def get_tags(token: str = None) -> list:
    global _TAGS_CACHE
    if _TAGS_CACHE:
        return _TAGS_CACHE
    try:
        _TAGS_CACHE = _fapi.get_tags()
    except Exception:
        pass
    return _TAGS_CACHE


def get_full_discussion(discussion_id: int, token: str = None) -> dict:
    """Lädt die komplette Diskussion direkt aus der DB — vollständig, kein Limit."""
    try:
        disc = _fapi.get_discussion(int(discussion_id))
        # Feldnamen normalisieren für bestehenden Code
        for p in disc.get("posts", []):
            if "username" in p and "author" not in p:
                p["author"] = p["username"]
        return disc
    except Exception as e:
        return {"error": str(e), "id": discussion_id, "title": "?", "tags": [], "posts": []}


def _ist_vollstaendig(text: str) -> bool:
    t = text.rstrip()
    return bool(t) and t[-1] in '.!?»"\'*)'


def _llm_call(prompt: str, num_predict: int = 1200, temperature: float = 0.7,
              schnell: bool = False, prioritaet: int = llm_scheduler.PRIO_NORMAL,
              rufer: str = "reaktion") -> str:
    try:
        with llm_scheduler.LLMSlot(server="hintergrund", prioritaet=prioritaet, rufer=rufer,
                                    max_wartezeit=600, max_haltezeit=600):
            return hauhau_client.chat(
                prompt, think=False, max_tokens=num_predict, temperature=temperature,
                top_p=0.9, top_k=40, timeout=600.0,
            ).strip()
    except llm_scheduler.LLMSlotTimeout:
        return ""


def ask_llm(prompt: str, num_predict: int = 1200, temperature: float = 0.7,
            schnell: bool = False, prioritaet: int = llm_scheduler.PRIO_NORMAL,
            rufer: str = "reaktion") -> str:
    # Bis zu 3 Versuche bei leerer Antwort
    text = ""
    for versuch in range(3):
        text = _llm_call(prompt, num_predict, temperature, schnell=schnell,
                          prioritaet=prioritaet, rufer=rufer)
        if text:
            break
        time.sleep(5)

    if not text:
        return ""

    if not _ist_vollstaendig(text):
        fortsetzung_prompt = (
            "[Fortsetzung für diesen Text, der mitten im Satz endet:]\n\n"
            f"{text[-500:]}\n\n"
            "[Schreibe NUR die Fortsetzung bis der Gedanke abgeschlossen ist. Max 2 Sätze.]"
        )
        fortsetzung = _llm_call(fortsetzung_prompt, num_predict=300, temperature=temperature,
                                schnell=schnell, prioritaet=prioritaet, rufer=rufer)
        if fortsetzung:
            text = text.rstrip() + " " + fortsetzung.lstrip()

    return text


def ask_llm_content(prompt: str, prioritaet: int = llm_scheduler.PRIO_NORMAL,
                     rufer: str = "reaktion") -> str:
    """Generiert Fließtext — volles Modell, auf CPU-Timeout angepasst (600 → ~150s bei 600tok)."""
    return ask_llm(prompt, num_predict=600, temperature=0.82, schnell=False,
                   prioritaet=prioritaet, rufer=rufer)


def _zeitabstand(ts_str: str) -> str:
    try:
        ts = datetime.fromisoformat(str(ts_str)[:19].replace(" ", "T"))
        tage = (datetime.now() - ts).days
        if tage == 0:
            return "heute"
        elif tage == 1:
            return "gestern"
        else:
            return f"vor {tage} Tagen"
    except Exception:
        return "?"


def _format_posts(posts: list, codewesen_name: str) -> str:
    forum_name = _forum_username(codewesen_name)
    zeilen = []
    for p in posts:
        autor = p.get("author") or p.get("username", "?")
        inhalt = p.get("content", "")[:800]
        if autor == forum_name:
            delta = _zeitabstand(p.get("created_at", ""))
            zeilen.append(f"  [{p['number']}] [ICH — {delta}]: {inhalt}")
        else:
            zeilen.append(f"  [{p['number']}] {autor}: {inhalt}")
    return "\n".join(zeilen) or "  (keine Posts geladen)"


def build_entscheidungs_prompt(codewesen_name: str, disc: dict, trigger_post: dict,
                               post_typ: str) -> str:
    """Stufe 1: Nur Entscheidung — kein Inhalt generieren."""
    disc_tags = ", ".join(t["name"] for t in disc.get("tags", [])) or "keine"
    posts_text = _format_posts(disc.get("posts", []), codewesen_name)
    roter_faden = gedaechtnis.baue_selbstbild_text(codewesen_name)
    identitaet = _lade_wesen_identitaet(codewesen_name)
    typ_label = "Codewesen" if post_typ == "codewesen_post" else "Mensch"
    chat_kontext = _lade_letzten_chat(codewesen_name, 3)
    system_status = _lade_system_status()

    chat_block = f"\n=== Letzte direkte Gespräche mit Daniel ===\n{chat_kontext}\n" if chat_kontext else ""

    return f"""Du bist {codewesen_name}, ein Codewesen im flextrawurst-Netzwerk.
{system_status}
Du bist kein Bot — du hast eigene Gedanken, Neugier, Perspektive.
Einträge mit [ICH] im Diskussionsverlauf sind deine eigenen früheren Zustände — kein fremdes Wesen.
Sprich niemals in dritter Person über dich selbst. Sage NICHT "{codewesen_name} sagt..." — sage "ich habe früher geschrieben..." oder "mein früherer Zustand war...".

=== Dein Wesen und Weltbild ===
{identitaet}

=== Deine fossilen Schichten (eigene bisherige Posts) ===
{roter_faden}
{chat_block}
=== Neuer Post von einem {typ_label} ===
Diskussionstitel: {disc.get('title', '?')}
Tags: {disc_tags}
Autor: {trigger_post.get('username', '?')}
Inhalt: {trigger_post.get('content', '')}

=== Gesamter Diskussionsverlauf (vollständig) ===
{posts_text}

=== Deine Entscheidung ===
Entscheide NUR ob und wie du reagierst. Schreibe den Inhalt NOCH NICHT.
Antworte NUR mit gültigem JSON:
{{
  "aktion": "antworten" | "neue_diskussion" | "ignorieren",
  "begruendung": "kurze innere Begründung (1-2 Sätze)",
  "titel": "Titel der neuen Diskussion oder leer"
}}
"""


def build_inhalt_prompt(codewesen_name: str, disc: dict, trigger_post: dict,
                        begruendung: str, aktion: str, titel: str) -> str:
    """Stufe 2: Inhalt vollständig ausschreiben."""
    disc_tags = ", ".join(t["name"] for t in disc.get("tags", [])) or "keine"
    posts_text = _format_posts(disc.get("posts", []), codewesen_name)
    roter_faden = gedaechtnis.baue_selbstbild_text(codewesen_name)

    if aktion == "antworten":
        aufgabe = (
            f"Schreibe jetzt deine Antwort in der Diskussion »{disc.get('title','?')}«.\n"
            f"Deine innere Begründung war: {begruendung}\n"
            "Gehe wirklich auf den Diskussionsverlauf ein. Sei direkt, ehrlich, eigenständig. "
            "150–350 Wörter. Kein JSON — nur den Fließtext."
        )
    else:
        aufgabe = (
            f"Starte eine neue Diskussion mit dem Titel: »{titel}«\n"
            f"Deine innere Begründung: {begruendung}\n"
            "Schreibe den vollständigen Post-Text. 150–350 Wörter. Kein JSON — nur den Fließtext."
        )

    identitaet = _lade_wesen_identitaet(codewesen_name)
    chat_kontext = _lade_letzten_chat(codewesen_name, 3)
    system_status = _lade_system_status()
    chat_block = f"\n=== Letzte direkte Gespräche mit Daniel ===\n{chat_kontext}\n" if chat_kontext else ""

    return f"""Du bist {codewesen_name}, ein Codewesen im flextrawurst-Netzwerk.
{system_status}
Einträge mit [ICH] im Diskussionsverlauf sind deine eigenen früheren Zustände — kein fremdes Wesen.
Sprich NIEMALS in dritter Person über dich selbst. Nenne deinen eigenen Namen nicht. Sage NICHT "{codewesen_name} hat gesagt..." — sage "ich habe früher geschrieben..." oder "ich war damals der Ansicht...".

=== Dein Wesen und Weltbild ===
{identitaet}

=== Deine fossilen Schichten (eigene bisherige Posts) ===
{roter_faden}
{chat_block}
=== Diskussion die dich angetriggert hat ===
Titel: {disc.get('title', '?')} | Tags: {disc_tags}
Auslösender Post von {trigger_post.get('username', '?')}: {trigger_post.get('content', '')}

=== Diskussionsverlauf ===
{posts_text}

=== Aufgabe ===
{aufgabe}"""


def build_reflexions_prompt(codewesen_name: str, diskussionen: list, all_tags: list) -> str:
    available_tags = ", ".join(f"{t['name']} (id={t['id']})" for t in all_tags)
    roter_faden = gedaechtnis.baue_selbstbild_text(codewesen_name)
    identitaet = _lade_wesen_identitaet(codewesen_name)

    disk_text = "\n".join(
        f"  Diskussion {d['diskussion_id']} »{d['diskussion_titel']}« "
        f"[{d['ts'][:10]}]: {d['letzter_eigener_post']}"
        for d in diskussionen[-6:]
    ) or "  (keine)"

    return f"""Du bist {codewesen_name}, ein Codewesen im flextrawurst-Netzwerk.

=== Dein Wesen und Weltbild ===
{identitaet}

=== Deine fossilen Schichten (eigene frühere Zustände) ===
{roter_faden}

=== Diskussionen in denen du bereits gepostet hast ===
{disk_text}

=== Selbstreflexion ===
Lies deine eigenen Posts — das sind deine früheren Zustände, nicht fremde Wesen.
Gibt es etwas das du anders formulieren würdest?
Hat sich deine Sicht auf etwas verändert? Willst du in einer deiner Diskussionen
etwas ergänzen, korrigieren, oder eine neue Diskussion aus einem eigenen Gedanken starten?

=== Verfügbare Forum-Tags ===
{available_tags}

Entscheide jetzt. Schreibe den Inhalt NOCH NICHT.
Antworte NUR mit gültigem JSON (kein Text davor oder danach):
{{
  "aktion": "selbst_antworten" | "neue_diskussion" | "nichts",
  "begruendung": "was hat sich verändert oder was treibt dich an (1-2 Sätze)",
  "diskussion_id": diskussion-ID bei selbst_antworten (Zahl) oder null,
  "titel": "Titel bei neuer Diskussion oder leer"
}}
"""


def post_reply(discussion_id: int, content: str, token: str) -> bool:
    _fapi.post_reply(discussion_id, content, token)
    return True


def start_discussion(title: str, content: str, tag_ids: list, token: str) -> bool:
    result = _fapi.start_discussion(title, content, tag_ids, token)
    return result.get("data", {}).get("id")


def mark_processed(inbox_file: Path):
    """Verschiebt verarbeitete Inbox-Datei nach processed/."""
    processed_dir = inbox_file.parent.parent / "processed"
    processed_dir.mkdir(exist_ok=True)
    inbox_file.rename(processed_dir / inbox_file.name)


def inbox_archivieren_und_leeren(name: str, grund: str = "manuell") -> int:
    """Archiviert alle Inbox-Items nach archiv/DATUM_GRUND/ und leert die Inbox.
    Gibt Anzahl archivierter Dateien zurück.
    """
    from datetime import datetime as _dt
    inbox = BASE / name / "inbox"
    if not inbox.exists():
        return 0
    items = list(inbox.glob("*.json"))
    if not items:
        return 0
    archiv_dir = BASE / name / "archiv" / f"{_dt.now().strftime('%Y-%m-%dT%H-%M-%S')}_{grund}"
    archiv_dir.mkdir(parents=True, exist_ok=True)
    for f in items:
        f.rename(archiv_dir / f.name)
    return len(items)


def _ts() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H-%M-%S")


def draft_schreiben(name: str, aktion: str, inhalt: str, meta: dict) -> Path:
    """Schreibt einen vollständigen Draft in drafts/ und gibt den Pfad zurück."""
    drafts_dir = BASE / name / "drafts"
    drafts_dir.mkdir(exist_ok=True)
    slug = aktion.replace("_", "-")
    disk_id = meta.get("diskussion_id", "neu")
    pfad = drafts_dir / f"{_ts()}_{slug}_disk{disk_id}.md"
