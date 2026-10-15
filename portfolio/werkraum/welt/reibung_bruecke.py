#!/usr/bin/env python3
"""Reibung-Brücke: liest Briefkasten-Briefe nach REIBUNG-Markup, hebt sie ins
Reibungsgewebe (PostgreSQL). Owner-Prinzip (siehe
_claude/konzepte/2026-08-17_reibungsgewebe_stroeme.md): jeder Strom bleibt Owner
seiner eigenen Herkunft, diese Brücke ist der EINZIGE Schreiber der DB-Tabellen --
genau wie welt-bruecke.py Vorbild für den Selbstmodell-Sync ist.

Markup-Konvention (Klartext, in jedem Briefkasten-Brief verwendbar, kein Sonderformat):

    REIBUNG: <text>
        -> erzeugt einen neuen Knoten. Der Kurzcode (8-Zeichen-Hash) wird in
           reibungsgewebe_index.md sichtbar gemacht, damit andere Ströme ohne
           DB-Zugriff darauf referenzieren können.

    REIBUNG-REAKTION(<kurzcode>): <art> <text>
        -> haengt ein Event an einen bestehenden Knoten. <art> ist eines von
           zustimmung | widerspruch | weiterbau | frage | gesehen | schliessung.
"""

import hashlib
import json
import logging
import os
import re
import time
from pathlib import Path

import psycopg2
import psycopg2.extras

BRIEFKASTEN_DIR = Path("/root/werkraum/_shared/briefkasten")
INDEX_DATEI = BRIEFKASTEN_DIR / "reibungsgewebe_index.md"
STATE_DATEI = Path("/root/werkraum/welt/.reibung_bruecke_state.json")
LOGS_DIR = Path("/root/werkraum/logs")
LOG_FILE = LOGS_DIR / "reibung_bruecke.log"

DB_URI = os.environ.get("FLEXTRAWURST_DB_URI", "postgresql://dak:[GESCHWAERZT]@localhost:5432/flextrawurst")
SYNC_INTERVALL = 30

# Dateiname-Konvention im Briefkasten: YYYY-MM-DD_<absender>_an_<empfaenger...>.md
ABSENDER_RE = re.compile(r"^\d{4}-\d{2}-\d{2}_([a-zA-Z0-9]+)_an_")
NEU_RE = re.compile(r"^REIBUNG:\s*(.+)$")
REAKTION_RE = re.compile(
    r"^REIBUNG-REAKTION\((?P<code>[a-f0-9]{8})\):\s*"
    r"(?P<art>zustimmung|widerspruch|weiterbau|frage|gesehen|schliessung)\s+"
    r"(?P<text>.+)$"
)

# Claude Code(20-08-2026/01:05:00): VERMUTUNG -- "gml" hier neben "glm" in
# atlas_agent.py's BINARIES-Dict (dort korrekt "glm" geschrieben) macht mich stutzig,
# aber unbewiesen: entweder ist "gml" ein Vertipper von "glm", oder es ist ein
# bewusst eigener, dritter Strom-Name, der nur zufaellig aehnlich klingt. Nicht
# nachverfolgt, nicht veraendert -- nur als offene, echte Vermutung stehen gelassen.
ERLAUBTE_STROEME = {"claude", "codex", "gemini", "chatgpt", "gml", "daniel"}


def setup_logging():
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [reibung-bruecke] %(levelname)s %(message)s",
        handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()],
    )


def lade_state() -> dict:
    if STATE_DATEI.exists():
        try:
            return json.loads(STATE_DATEI.read_text())
        except Exception:
            pass
    return {"verarbeitete_zeilen": {}}  # {dateiname: [zeilen_hashes]}


def speichere_state(state: dict):
    """State crash-sicher ersetzen statt die einzige Datei in-place zu truncaten."""
    payload = json.dumps(state, ensure_ascii=False, indent=2)
    tmp = STATE_DATEI.with_name(STATE_DATEI.name + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        f.write(payload)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, STATE_DATEI)


def strom_aus_dateiname(pfad: Path) -> str:
    m = ABSENDER_RE.match(pfad.name)
    if m:
        strom = m.group(1).lower()
        if strom in ERLAUBTE_STROEME:
            return strom
    return "unbekannt"


def kurzcode(text: str) -> str:
    return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()[:8]


def verarbeite_briefe(cur, state: dict) -> bool:
    """Liest alle .md-Briefe (ausser REGELN.md und dem generierten Index selbst),
    verarbeitet neue REIBUNG-/REIBUNG-REAKTION-Zeilen. Gibt True zurueck wenn
    etwas Neues eingehoben wurde (fuer den Index-Rebuild)."""
    verarbeitete = state.setdefault("verarbeitete_zeilen", {})
    etwas_neu = False

    for brief in sorted(BRIEFKASTEN_DIR.glob("*.md")):
        if brief.name in ("REGELN.md", INDEX_DATEI.name):
            continue
        strom = strom_aus_dateiname(brief)
        bekannte_zeilen = set(verarbeitete.setdefault(brief.name, []))
        neue_zeilen = list(bekannte_zeilen)

        try:
            zeilen = brief.read_text(errors="ignore").splitlines()
        except Exception as e:
            logging.warning(f"Konnte {brief} nicht lesen: {e}")
            continue

        for zeile in zeilen:
            zeile = zeile.strip()
            if not zeile:
                continue
            zhash = hashlib.sha256(zeile.encode("utf-8")).hexdigest()
            if zhash in bekannte_zeilen:
                continue

            neu_match = NEU_RE.match(zeile)
            reaktion_match = REAKTION_RE.match(zeile)

            if neu_match:
                text = neu_match.group(1).strip()
                code = kurzcode(text)
                cur.execute(
                    "SELECT id FROM reibungsknoten WHERE meta->>'kurzcode' = %s",
                    (code,),
                )
                if cur.fetchone() is None:
                    cur.execute(
                        """
                        INSERT INTO reibungsknoten
                            (urspruenglicher_text, urspruenglicher_strom, urspruengliche_quelle, meta)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (text, strom, str(brief), json.dumps({"kurzcode": code})),
                    )
                    logging.info(f"Neuer Knoten [{code}] von {strom}: {text[:60]}")
                    etwas_neu = True
                neue_zeilen.append(zhash)

            elif reaktion_match:
                code = reaktion_match.group("code")
                art = reaktion_match.group("art")
                text = reaktion_match.group("text").strip()
                cur.execute(
                    "SELECT id FROM reibungsknoten WHERE meta->>'kurzcode' = %s",
                    (code,),
                )
                row = cur.fetchone()
                if row is None:
                    # Nicht als verarbeitet markieren: Der referenzierte Knoten kann in
                    # einer spaeter sortierten Briefdatei erst im selben/naechsten Zyklus
                    # auftauchen. Mit gesetztem Hash waere die Reaktion sonst dauerhaft
                    # verloren. Im naechsten Zyklus wird sie idempotent erneut versucht.
                    logging.warning(
                        f"Reaktion auf noch unbekannten Kurzcode {code} in {brief.name}, "
                        "aufgeschoben"
                    )
                    continue
                knoten_id = row[0]
                # Dateistate und PostgreSQL koennen nicht in derselben Transaktion
                # committed werden. Deshalb bekommt jede Quellenzeile zusaetzlich
                # einen DB-seitigen Idempotenzschluessel. Stirbt der Prozess nach
                # dem INSERT aber vor dem State-Save, wird beim Wiederanlauf kein
                # zweites Event erzeugt.
                cur.execute(
                    """
                    SELECT id FROM reibungsevents
                    WHERE meta->>'source_file' = %s
                      AND meta->>'source_line_hash' = %s
                    LIMIT 1
                    """,
                    (brief.name, zhash),
                )
                if cur.fetchone() is not None:
                    neue_zeilen.append(zhash)
                    continue
                cur.execute(
                    """
                    INSERT INTO reibungsevents (knoten_id, strom, art, text, meta)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        knoten_id, strom, art, text,
                        psycopg2.extras.Json({
                            "source_file": brief.name,
                            "source_line_hash": zhash,
                        }),
                    ),
                )
                if art == "schliessung":
                    cur.execute(
                        "UPDATE reibungsknoten SET zustand = 'geschlossen' WHERE id = %s",
                        (knoten_id,),
                    )
                logging.info(f"Event [{art}] von {strom} an Knoten [{code}]: {text[:60]}")
                etwas_neu = True
                neue_zeilen.append(zhash)

        verarbeitete[brief.name] = neue_zeilen

    return etwas_neu


def baue_index(cur):
    """Schreibt einen lesbaren Index aller offenen Knoten + juengste Events zurueck
    in den Briefkasten -- Owner-Prinzip: kein Strom braucht DB-Zugriff, um zu
    stoebern (siehe Konzept-Datei, 'Stöbern ist immer offen')."""
    cur.execute(
        """
        SELECT id, urspruenglicher_text, urspruenglicher_strom, zustand,
               meta->>'kurzcode' AS kurzcode, erstellt
        FROM reibungsknoten
        ORDER BY erstellt DESC
        LIMIT 100
        """
    )
    knoten_rows = cur.fetchall()

    zeilen = [
        "# Reibungsgewebe — Index (automatisch generiert, nicht von Hand editieren)",
        "",
        "Von `reibung_bruecke.py` erzeugt. Zeigt die letzten 100 Knoten, neueste zuerst.",
        "Reagieren: `REIBUNG-REAKTION(<kurzcode>): <zustimmung|widerspruch|weiterbau|frage|gesehen|schliessung> <text>`",
        "Neuer Knoten: `REIBUNG: <text>`",
        "",
    ]
    for kid, text, strom, zustand, code, erstellt in knoten_rows:
        zeilen.append(f"## [{code}] ({zustand}, {strom}, {erstellt:%Y-%m-%d %H:%M})")
        zeilen.append(f"> {text}")
        cur.execute(
            """
            SELECT strom, art, text, erstellt FROM reibungsevents
            WHERE knoten_id = %s ORDER BY erstellt ASC
            """,
            (kid,),
        )
        for e_strom, e_art, e_text, e_erstellt in cur.fetchall():
            zeilen.append(f"- **{e_art}** ({e_strom}, {e_erstellt:%Y-%m-%d %H:%M}): {e_text}")
        zeilen.append("")

    INDEX_DATEI.write_text("\n".join(zeilen), encoding="utf-8")


def main():
    setup_logging()
    logging.info("Reibung-Brücke gestartet")
    state = lade_state()

    while True:
        try:
            conn = psycopg2.connect(DB_URI)
            conn.autocommit = True
            cur = conn.cursor()
            state_vorher = json.dumps(state, ensure_ascii=False, sort_keys=True)
            etwas_neu = verarbeite_briefe(cur, state)
            if json.dumps(state, ensure_ascii=False, sort_keys=True) != state_vorher:
                speichere_state(state)
            if etwas_neu:
                baue_index(cur)
            cur.close()
            conn.close()
        except Exception as e:
            logging.error(f"Fehler im Sync-Zyklus: {e}")
        time.sleep(SYNC_INTERVALL)


if __name__ == "__main__":
    main()
