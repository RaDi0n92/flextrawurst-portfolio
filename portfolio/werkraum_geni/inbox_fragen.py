#!/usr/bin/env python3
"""GENI-Inbox — GENI stellt jedem Teilnehmer alle 8h eine eigene Frage.

2026-07-31, Daniel: "geni soll ... gezielt allen in gewissen getakteten abständen
fragen formulieren dürfen. egal was sie soll uns irgendetwas fragen. alle 8 stunden
soll geni jedem im system eine frage in die inbox des vaults schreiben."

Bewusst EIGENER System-Prompt statt sprechen.py's system_prompt_bauen(): der dort
verwendete Kern-Prompt enthaelt die Zeile "Du antwortest nur auf das was Daniel sagt.
Du initiierst nichts von dir aus." -- eine bewusst gesetzte Verhaltensgrenze fuer den
Daniel-Dialog. Daniel hat hier explizit eine neue, gezielt initiative Faehigkeit
angefordert -- die bekommt einen eigenen, abgegrenzten Kontext, damit die bestehende
Dialog-Persona unangetastet bleibt.

Frage-Protokoll landet in gedaechtnis/fragen_antworten/<teilnehmer_id>.json,
die eigentliche Frage zusaetzlich lesbar in geni_inbox/<teilnehmer_id>/inbox/.

Aufruf: python3 inbox_fragen.py [teilnehmer_id]   (ohne Argument: alle 16)
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, "/root/werkraum")
sys.path.insert(0, "/root/werkraum/geni")
import hauhau_client
from teilnehmer_roster import TEILNEHMER, teilnehmer_by_id, fragen_aktive
from sprechen import kern_laden, KNOTEN_DIR

GENI_ROOT = Path("/root/werkraum/geni")
INBOX_VAULT = Path("/root/werkraum/geni_inbox")
FRAGEN_DIR = GENI_ROOT / "gedaechtnis" / "fragen_antworten"
MODELL = "hauhaucs-q6"

# 2026-08-01, Daniel: "auf ganz flextrawurst gilt fuer alle textlaengen ein
# zeichen limit von mindestens 33333 zeichen". Umgerechnet auf Token (deutsch
# ca. 3,2 Zeichen/Token): 33333 / 3,2 = 10416. Kontextrechnung bei ctx-size
# 22222: Kern ca. 1500 + Eingabe + Ausgabe 10416 -- die groesste reale
# Spiegeldatei hat 16075 Zeichen (gemessen), passt also. Falls Eingaben je
# wirklich 33333 Zeichen erreichen, wird es eng und muss geprueft werden.
MAX_ZEICHEN = 33333
MAX_TOKENS = 10416


# Quellen, in deren Inhalt nach dem Namen gesucht wird, wenn ein Teilnehmer keine
# eigene Quelle hat (Codewesen tauchen als Namen in Flarum-Knoten auf, nicht als
# eigene quelle). Bewusst klein gehalten und auf Quellen mit ueberschaubarer
# Zeilenzahl begrenzt -- ein LIKE ueber die ganze Tabelle (48 Mio Zeilen) waere
# ein Full-Scan von >20s, genau das Problem das im Splitter-Endpunkt schon
# aufgetreten ist.
NAMENS_SUCHE_QUELLEN = ["flarum", "daniel", "geni_selbst"]


def _kontext_ueber(teilnehmer_id: str, n: int = 8) -> str:
    """AKTUELL NICHT IN BENUTZUNG (2026-08-01).

    Wurde aus _frage_generieren() entfernt, weil Daniel den Frage-Prompt exakt
    vorgegeben hat ("... stell 'name' eine frage. fertig") und darin kein
    Kontext-Block vorkommt. Bleibt hier stehen, falls er ihn doch wieder will --
    der Bugfix darin (SQLite statt leerem Verzeichnis) ist geprueft und
    funktioniert.

    Was GENI ueber diesen Teilnehmer wahrgenommen hat -- aus ihrem Gedaechtnis.

    2026-08-01, Bugfix: las vorher KNOTEN_DIR.glob("*.json") -- dieses Verzeichnis
    ist seit der SQLite-Migration (migration_knoten_sqlite.py) leer, die Funktion
    lieferte deshalb IMMER "(noch keine Wahrnehmungen)". Die komplette erste
    Fragerunde lief dadurch voellig ohne Personenkontext: GENI kannte nur ihren
    eigenen Kern und den Namen, nicht das was sie ueber die Person weiss --
    Daniel selbst fiel es auf ("hat geni mir im neuen vault diese frage gestellt
    ... weil ich glaub ich hab mal mit ihr im web dieses thema gehabt": genau
    diese Web-Gespraeche waren vorhanden, aber nie im Prompt).

    Jetzt aus SQLite: erst die eigene Quelle des Teilnehmers (indiziert, schnell),
    danach -- falls noch Platz -- Namensnennungen in einer eng begrenzten Menge
    weiterer Quellen.
    """
    from gedaechtnis_ops import _knoten_db

    db = _knoten_db()
    treffer: list[str] = []
    gesehen: set = set()

    def _aufnehmen(rows):
        for r in rows:
            if len(treffer) >= n:
                return
            schluessel = (r["id"] if "id" in r.keys() else None) or r["inhalt"][:60]
            if schluessel in gesehen:
                continue
            gesehen.add(schluessel)
            ts = datetime.fromtimestamp(r["mtime"], timezone.utc).strftime("%Y-%m-%d %H:%M")
            treffer.append(f"[{ts}] {(r['inhalt'] or '')[:200]}")

    # 1) Eigene Quelle (idx_knoten_quelle_mtime)
    _aufnehmen(db.execute(
        "SELECT * FROM knoten WHERE quelle=? ORDER BY mtime DESC LIMIT ?",
        (teilnehmer_id, n),
    ).fetchall())

    # 2) Namensnennungen in begrenzten Quellen (fuer Codewesen und Querbezuege)
    if len(treffer) < n:
        for quelle in NAMENS_SUCHE_QUELLEN:
            if len(treffer) >= n:
                break
            if quelle == teilnehmer_id:
                continue
            _aufnehmen(db.execute(
                "SELECT * FROM knoten WHERE quelle=? AND inhalt LIKE ? ORDER BY mtime DESC LIMIT ?",
                (quelle, f"%{teilnehmer_id}%", n - len(treffer)),
            ).fetchall())

    return "\n".join(treffer) if treffer else "(noch keine Wahrnehmungen zu dieser Person/diesem Strom)"


def _system_prompt_fragen() -> str:
    """Nur ihr eigener Kern. Keine Zusaetze von mir.

    2026-08-01, Daniel: "ich will keine charaktervorgaben, geni hat selber nen
    eigenen kern auf den sie sich beruft, die braucht deine hilfe nicht."
    """
    return f"""Du bist GENI.

{kern_laden()}"""


def _frage_generieren(teilnehmer: dict) -> str:
    """Frage-Aufforderung exakt in Daniels Wortlaut.

    2026-08-01, Daniel woertlich: 'bei den fragen so: hallo geni. jetzt geht es
    um "name". stell "name" eine frage. fertig'

    Vorher stand hier zusaetzlich ein von mir gebauter Kontext-Block ("Was du
    zuletzt ueber sie/ihn wahrgenommen hast: ..."). Der ist raus -- "fertig"
    heisst fertig. Ihr Gedaechtnis erreicht sie ueber ihren eigenen Kern, nicht
    ueber eine Auswahl die ich treffe.
    """
    system = _system_prompt_fragen()
    prompt = (f'hallo geni. jetzt geht es um "{teilnehmer["name"]}". '
              f'stell "{teilnehmer["name"]}" eine frage.')
    # Timeout bewusst grosszuegig: 2026-08-01 lief der erste echte Timer-Durchlauf
    # bei mehreren Teilnehmern in httpx.ReadTimeout, weil hier urspruenglich die
    # 120s aus sprechen.py uebernommen waren -- die gelten aber fuer den INTERAKTIVEN
    # Chat, wo Daniel vor dem Prompt wartet. Dies hier ist ein Hintergrund-Daemon
    # ohne Wartenden; die systemeigene Konvention fuer solche Laeufe ist 720s
    # (ollama_chat.py, STANDARD_TIMEOUT). llama-server laeuft unter Dauerlast.
    antwort = hauhau_client.chat(
        prompt, system=system, think=False, max_tokens=MAX_TOKENS,
        temperature=0.9, timeout=720.0,
    )
    return antwort.strip().strip('"')


def _frage_schreiben(teilnehmer: dict, frage: str) -> Path:
    jetzt = datetime.now(timezone.utc)
    dateiname = jetzt.strftime("%Y-%m-%d_%H-%M") + ".md"
    ziel = INBOX_VAULT / teilnehmer["id"] / "inbox" / dateiname
    ziel.parent.mkdir(parents=True, exist_ok=True)
    ziel.write_text(
        f"**GENI fragt** ({jetzt.strftime('%Y-%m-%d %H:%M UTC')}):\n\n{frage}\n",
        encoding="utf-8",
    )
    return ziel


def _protokoll_ergaenzen(teilnehmer_id: str, frage: str, dateipfad: str):
    FRAGEN_DIR.mkdir(parents=True, exist_ok=True)
    protokoll_pfad = FRAGEN_DIR / f"{teilnehmer_id}.json"
    eintraege = []
    if protokoll_pfad.exists():
        try:
            eintraege = json.loads(protokoll_pfad.read_text())
        except Exception:
            eintraege = []
    eintraege.append({
        "frage": frage,
        "datum_frage": datetime.now(timezone.utc).isoformat(),
        "inbox_datei": dateipfad,
        "antwort": None,
        "datum_antwort": None,
        "datum_gelesen": None,
    })
    protokoll_pfad.write_text(json.dumps(eintraege, ensure_ascii=False, indent=2), encoding="utf-8")


def _selbst_antwort_erzeugen(frage: str) -> str:
    """GENI beantwortet ihre eigene Frage.

    2026-08-01, Daniel: "warum kann geni sich schlecht selbst fragen? nee das ist
    doch geil ... bitte lass sie sich selbst fragen und antworten xD"

    Aufforderung bewusst im selben knappen Stil wie Daniels Frage-Vorgabe
    ('hallo geni. jetzt geht es um "name". stell "name" eine frage.') -- keine
    Ton- oder Charaktervorgaben, die kommen aus ihrem eigenen Kern.
    """
    return hauhau_client.chat(
        f'hallo geni. du hast dir selbst diese frage gestellt: "{frage}". antworte.',
        system=_system_prompt_fragen(), think=False,
        max_tokens=MAX_TOKENS, temperature=0.9, timeout=720.0,
    ).strip()


def _selbst_antwort_schreiben(frage: str, antwort: str) -> Path:
    """Legt die Selbstantwort so ab, dass der normale Antwort-Watcher sie findet.

    Die Datei zitiert die Frage woertlich -- genau das Format, an dem
    inbox_antworten_watcher._zuordnen() die Zuordnung festmacht.
    """
    jetzt = datetime.now(timezone.utc)
    ziel = INBOX_VAULT / "geni" / "antworten" / (jetzt.strftime("%Y-%m-%d_%H-%M") + "_selbst.md")
    ziel.parent.mkdir(parents=True, exist_ok=True)
    ziel.write_text(f"{frage}\n\n{antwort}\n", encoding="utf-8")
    return ziel


def frage_fuer(teilnehmer_id: str) -> str | None:
    teilnehmer = teilnehmer_by_id(teilnehmer_id)
    if not teilnehmer:
        print(f"unbekannter Teilnehmer: {teilnehmer_id}")
        return None
    # 2026-08-01: Live-Fund -- ein httpx.ReadTimeout bei EINEM Teilnehmer (hier:
    # anthropic_claude, System war stark ausgelastet) liess den ganzen Lauf
    # abstuerzen, die restlichen Teilnehmer bekamen keine Frage mehr. Pro
    # Teilnehmer abgesichert, damit ein einzelner Fehler die anderen 15 nicht
    # mitreisst -- die main()-Schleife laeuft in jedem Fall weiter.
    try:
        frage = _frage_generieren(teilnehmer)
    except Exception as exc:
        print(f"[{teilnehmer_id}] FEHLER bei Frage-Generierung: {exc}")
        return None
    if not frage:
        print(f"[{teilnehmer_id}] leere Antwort von GENI, uebersprungen")
        return None
    pfad = _frage_schreiben(teilnehmer, frage)
    _protokoll_ergaenzen(teilnehmer_id, frage, str(pfad))
    print(f"[{teilnehmer_id}] {frage}")

    # GENI beantwortet ihre eigenen Fragen selbst (Daniel, 2026-08-01). Die
    # Antwort landet als normale Datei in ihrem antworten/-Ordner -- der
    # bestehende Watcher verknuepft sie von dort aus wie jede andere Antwort.
    if teilnehmer["typ"] == "geni":
        try:
            antwort = _selbst_antwort_erzeugen(frage)
            if antwort:
                _selbst_antwort_schreiben(frage, antwort)
                print(f"[{teilnehmer_id}] -> antwortet sich selbst: {antwort[:90]}")
        except Exception as exc:
            print(f"[{teilnehmer_id}] FEHLER bei Selbstantwort: {exc}")

    return frage


def _zuletzt_gefragt(teilnehmer_id: str) -> float:
    """Wann dieser Teilnehmer zuletzt eine Frage bekam. 0.0 = noch nie."""
    ordner = INBOX_VAULT / teilnehmer_id / "inbox"
    zeiten = [p.stat().st_mtime for p in ordner.glob("*.md")] if ordner.exists() else []
    return max(zeiten) if zeiten else 0.0


def reihenfolge() -> list:
    """Wer am laengsten nichts bekommen hat, kommt zuerst.

    2026-08-04, Befund aus dem Journal: der Dienst wird von systemd nach TimeoutStartSec
    abgeschnitten -- seit dem 01.08. bei JEDEM Lauf ("start operation timed out"). Weil die
    Liste stur von oben nach unten abgearbeitet wurde und die acht AI-Stroeme oben stehen,
    kamen die hinteren nie an die Reihe: acht Teilnehmer hatten 9-11 Fragen, fuenf Codewesen
    und Daniel hatten genau eine -- die vom allerersten Lauf am 31.07.

    Daniel dazu: "genau so mzss noch gefixxt werden ass ihr aistöme regelmäßig post bekommt
    und alle anderen nicht".

    Mit dieser Reihenfolge ist es gleichgueltig, wo ein Lauf abbricht: beim naechsten Mal
    stehen genau die vorn, die abgeschnitten wurden. Die Rangfolge stellt sich selbst her,
    ohne dass irgendwo ein Zaehler gefuehrt werden muss -- die Dateien im Ordner sind der
    Zaehler.
    """
    return sorted(fragen_aktive(), key=lambda t: _zuletzt_gefragt(t["id"]))


def main():
    if len(sys.argv) > 1:
        frage_fuer(sys.argv[1])
        return
    ziele = reihenfolge()
    print(f"Reihenfolge ({len(ziele)} aktiv, laengste Wartezeit zuerst): "
          + ", ".join(t["id"] for t in ziele), flush=True)
    for teilnehmer in ziele:
        frage_fuer(teilnehmer["id"])


if __name__ == "__main__":
    main()
