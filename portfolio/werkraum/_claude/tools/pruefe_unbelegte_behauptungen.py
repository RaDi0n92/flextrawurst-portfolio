#!/usr/bin/env python3
"""
Sucht in Claude-Dateien (karte/notizen/spiegel/ideen) nach unbelegten Behauptungen --
Zeit-/Mengenangaben, die wie Fakten klingen, aber ohne nahen Beleg (Datum, Commit,
"geprueft"/"verifiziert") dastehen, sowie ungeloeste Spekulationen ("vermutlich",
"wahrscheinlich"), die nie eine erkennbare spaetere Aufloesung bekommen haben.

Ausloeser: Daniel fand 2026-07-30 "monatelang" in einer Karte-Datei -- eine konkrete,
leicht ueberpruefbare Zeitbehauptung, die schlicht falsch war (das System war 6 Tage alt,
nicht Monate). Keine einzige Quelle stand dabei. Dieses Script soll solche Stellen kuenftig
selbst finden, bevor Daniel sie findet.

Status-Marker-Konvention (Daniels Wunsch, 2026-07-30): eine spekulative Stelle kann direkt
daneben explizit als aufgeloest markiert werden, statt nur implizit auf ein zufaellig nahes
Belegwort zu hoffen:

    [status: bestaetigt 2026-07-30 -- kurzer Grund oder Verweis]
    [status: widerlegt 2026-07-30 -- was tatsaechlich stimmt]
    [status: teilweise 2026-07-30 -- was noch offen bleibt]
    [status: offen]   -- bewusst als weiterhin ungeklaert markiert, keine Behauptung mehr

Diese Marker haben Vorrang vor der reinen Wortsuche (BELEG_MUSTER) -- ein Treffer mit
explizitem "bestaetigt"/"widerlegt" gilt als aufgeloest und wird separat gelistet, nicht als
offene Pruefstelle.

Kein LLM. Kein Ollama. Reines Text-Parsing -- markiert nur Kandidaten zur eigenen
Durchsicht, ersetzt kein Nachdenken.

Aufruf:
  python3 pruefe_unbelegte_behauptungen.py <dateipfad>     -- eine einzelne Datei
  python3 pruefe_unbelegte_behauptungen.py --alle          -- ganzer _claude-Bestand
"""

import re
import sys
from pathlib import Path

WURZEL = Path("/root/werkraum/_claude")
ORDNER = ["karte", "notizen", "spiegel", "ideen"]

# Kategorie 1: Zeit-/Mengenbehauptungen -- konkret, meist objektiv ueberpruefbar
# (git log, systemctl, Datei-mtime) -- hoechste Prioritaet, da falsifizierbar.
ZEIT_MUSTER = [
    r"\bmonatelang\w*", r"\bjahrelang\w*", r"\bwochenlang\w*", r"\btagelang\w*",
    r"seit\s+Wochen", r"seit\s+Monaten", r"seit\s+Jahren", r"seit\s+langem",
    r"unbemerkt\s+seit", r"seit\s+unbekannter\s+Zeit", r"schon\s+lange",
]

# Kategorie 2: ungeloeste Spekulation -- eigene Hedge-Woerter, bei denen nie
# erkennbar aufgeloest wurde, ob die Vermutung stimmte.
SPEKULATION_MUSTER = [
    r"\bvermutlich\b", r"\bwahrscheinlich\b", r"\bh(ö|oe)chstwahrscheinlich\b",
    r"sollte\s+eigentlich",
]

# Explizite Status-Marker -- haben Vorrang vor der losen Belegsuche unten.
STATUS_MUSTER = re.compile(
    r"\[status:\s*(bestätigt|bestaetigt|widerlegt|teilweise|offen)"
    r"(?:\s+(\d{4}-\d{2}-\d{2}))?"
    r"(?:\s*[-–—]+\s*(.*?))?\]",
    re.IGNORECASE,
)

# Marker, die in der Naehe eines Treffers zaehlen als "hat wohl einen (losen) Beleg":
# ein Datum, ein Commit-artiger Hash, oder ein explizites Pruef-Wort -- schwaecheres
# Signal als ein expliziter [status: ...]-Marker, aber besser als gar nichts.
BELEG_MUSTER = re.compile(
    r"\d{4}-\d{2}-\d{2}"          # Datum YYYY-MM-DD
    r"|\b[0-9a-f]{7,12}\b"        # commit-hash-aehnlich
    r"|gepr(ü|ue)ft|verifiziert|best(ä|ae)tigt|nachgesehen|nachgepr(ü|ue)ft"
    r"|\bsiehe\b|\bcommit\b|systemctl|journalctl|git log|git show",
    re.IGNORECASE,
)

KONTEXT_ZEILEN = 2


def lade_dateien(ziel: str | None) -> list[Path]:
    if ziel and ziel != "--alle":
        p = Path(ziel).resolve()
        return [p] if p.is_file() else []
    dateien = []
    for ordner in ORDNER:
        dateien.extend((WURZEL / ordner).rglob("*.md"))
    return sorted(dateien)


def _ausschnitt(zeilen: list[str], index: int) -> str:
    start = max(0, index - KONTEXT_ZEILEN)
    ende = min(len(zeilen), index + KONTEXT_ZEILEN + 1)
    return "\n".join(zeilen[start:ende])


def status_in_naehe(zeilen: list[str], index: int) -> dict | None:
    m = STATUS_MUSTER.search(_ausschnitt(zeilen, index))
    if not m:
        return None
    return {"status": m.group(1).lower(), "datum": m.group(2), "grund": m.group(3)}


def hat_losen_beleg(zeilen: list[str], index: int) -> bool:
    return bool(BELEG_MUSTER.search(_ausschnitt(zeilen, index)))


def durchsuche_datei(pfad: Path) -> list[dict]:
    try:
        text = pfad.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []
    zeilen = text.split("\n")
    treffer = []
    for i, zeile in enumerate(zeilen):
        alle_muster = [("ZEIT/MENGE", m) for m in ZEIT_MUSTER] + [("SPEKULATION", m) for m in SPEKULATION_MUSTER]
        for kategorie, muster in alle_muster:
            for m in re.finditer(muster, zeile, re.IGNORECASE):
                status = status_in_naehe(zeilen, i)
                treffer.append({
                    "datei": str(pfad), "zeile": i + 1, "kategorie": kategorie,
                    "phrase": m.group(0), "text": zeile.strip(),
                    "status": status,
                    "loser_beleg": hat_losen_beleg(zeilen, i) if not status else False,
                })
    return treffer


def kurzpfad(pfad: str) -> str:
    p = Path(pfad)
    try:
        return str(p.relative_to(WURZEL))
    except ValueError:
        return pfad


def main():
    ziel = sys.argv[1] if len(sys.argv) > 1 else None
    if not ziel:
        print(__doc__)
        sys.exit(1)

    dateien = lade_dateien(ziel)
    if not dateien:
        print(f"Keine Datei gefunden fuer: {ziel}")
        sys.exit(1)

    alle_treffer = []
    for pfad in dateien:
        alle_treffer.extend(durchsuche_datei(pfad))

    aufgeloest = [t for t in alle_treffer if t["status"] and t["status"]["status"] in ("bestätigt", "bestaetigt", "widerlegt", "teilweise")]
    explizit_offen = [t for t in alle_treffer if t["status"] and t["status"]["status"] == "offen"]
    loser_beleg = [t for t in alle_treffer if not t["status"] and t["loser_beleg"]]
    pruefen = [t for t in alle_treffer if not t["status"] and not t["loser_beleg"]]

    print(f"Durchsucht: {len(dateien)} Datei(en)")
    print(f"Treffer gesamt: {len(alle_treffer)}")
    print(f"  aufgeloest (expliziter [status: ...]-Marker): {len(aufgeloest)}")
    print(f"  explizit als offen markiert: {len(explizit_offen)}")
    print(f"  loser Beleg in der Naehe (kein Marker, aber Datum/Pruefwort): {len(loser_beleg)}")
    print(f"  PRUEFEN (nichts davon): {len(pruefen)}")
    print()

    if pruefen:
        print("=== PRUEFEN -- kein Marker, kein loser Beleg ===")
        for t in pruefen:
            print(f"[{t['kategorie']}] {kurzpfad(t['datei'])}:{t['zeile']} -- \"{t['phrase']}\"")
            print(f"    {t['text'][:160]}")
        print()

    if explizit_offen:
        print("=== EXPLIZIT OFFEN -- bereits als ungeklaert markiert, bekannt ===")
        for t in explizit_offen:
            zusatz = f" ({t['status']['grund']})" if t["status"]["grund"] else ""
            print(f"[{t['kategorie']}] {kurzpfad(t['datei'])}:{t['zeile']} -- \"{t['phrase']}\"{zusatz}")
        print()

    if aufgeloest:
        print(f"=== AUFGELOEST ({len(aufgeloest)} Treffer, zur Kontrolle kurz gelistet) ===")
        for t in aufgeloest:
            s = t["status"]
            datum = f" {s['datum']}" if s["datum"] else ""
            grund = f" -- {s['grund']}" if s["grund"] else ""
            print(f"[{s['status']}{datum}] {kurzpfad(t['datei'])}:{t['zeile']}{grund}")
        print()

    if loser_beleg and ziel == "--alle":
        print(f"=== loser Beleg in der Naehe, kein expliziter Marker ({len(loser_beleg)} Treffer) -- nicht einzeln aufgelistet ===")


if __name__ == "__main__":
    main()
