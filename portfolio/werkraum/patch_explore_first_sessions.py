from pathlib import Path
import re

R = Path("/root/werkraum/gemgems-spielbeobachtung/2026-09-04_MOELLENKOTTEN_FORSCHUNG")
mapping = [
    ("01_STRASSEN_UND_GEWEGE","S01"),("02_FASSADEN_FENSTER_TUEREN","S02"),("03_GESCHICHTE_UNTERGRUND_SPUREN","S03"),
    ("04_HOEHEN_BOESCHUNGEN_TREPPEN","S04"),("05_GEBAEUDEKOERPER_DAECHER","S05"),("06_VEGETATION_GRUEN","S06"),
    ("07_TRAMPELPFADE_DURCHGAENGE","S07"),("08_STRASSENMOBILIAR_GRENZOBJEKTE","S08"),("09_SONDERORTE_OEFFENTLICHE_INNENRAEUME","S09"),
    ("10_HISTORISCHE_KARTEN_LUFTBILDER","S10"),("11_BILDQUELLEN_PERSPEKTIVEN","S11"),("12_WIDERSPRUCH_LUECKEN_FACHSESSION","S12"),
]

for folder, sid in mapping:
    p = R / "sessions" / folder / "00_SESSIONKERN.md"
    t = p.read_text(encoding="utf-8")
    special = (
        "Du darfst später den gesamten Skriptkörper als Vergleichsgegenstand sehen."
        if sid == "S12"
        else "Welche Skripte später fachlich zu dir gehören, wird dynamisch aus `../../maschinenvertrag/SKRIPT_SESSION_MAPPING.json` bestimmt."
    )
    block = f"""## Zusammenarbeit mit dem laufenden Skriptkörper
Deine feste Sessionkennung ist `{sid}`. {special}

**Wichtig: Öffne zu Beginn eines neuen Goals oder einer neuen konkreten Fachfrage nicht zuerst den Skriptstatus und nicht zuerst die passenden Skriptoutputs.**

Arbeite zuerst eigenständig explorativ:
- entwickle aus deinem Fachgebiet, dem Ort, den Quellen und deinen eigenen Fragen ein unabhängiges Bild;
- suche und sammle selbst;
- folge auch unerwarteten Spuren, die in keinem Skript vorgesehen sein müssen;
- halte im aktuellen `ERGEBNIS_*.md` vor dem Skriptvergleich einen Abschnitt `EIGENEXPLORATION_VOR_SKRIPTVERGLEICH` fest.

Erst **danach** führst du aus:

`python3 ../../werkzeuge/skriptkoerper_status.py --session {sid}`

Nun vergleichst du deinen eigenen Stand mit den relevanten Skripten und Outputs. Beide Seiten werden kritisch behandelt. Ein Skriptoutput darf deine erste Suchagenda nicht nachträglich umschreiben; dein eigener Fundbestand gewinnt aber ebenfalls nicht automatisch gegen ein Skript.

Frage danach ausdrücklich:
- Was habe ich gefunden, was die Skripte übersehen?
- Was haben die Skripte gefunden, was ich übersehen habe?
- Wo beruhen beide nur auf derselben Ursprungsquelle?
- Wo widersprechen sie sich?
- Welche Seite ist zu grob, zu alt, räumlich falsch oder semantisch überzogen?
- Welche neue Frage ist erst durch den Vergleich entstanden?

Erst aus diesem Vergleich leitest du die gezielte Vertiefung ab.

`NOCH_OHNE_OUTPUT` bedeutet nicht automatisch, dass ein Skript gerade läuft. Ohne eigenen Laufnachweis bleibt der Status `SKRIPTSTATUS_UNGEKLAERT_KEIN_OUTPUT`.

Vor jedem `/goal-check` prüfst du den Skriptstatus erneut, **ohne** den bereits festgehaltenen unabhängigen Eigenstand rückwirkend umzuschreiben.

Die externen Skript- und Rohoutputverzeichnisse sind für dich **read-only**. Du schreibst dort nichts.

"""
    nt = re.sub(
        r"## Zusammenarbeit mit dem laufenden Skriptkörper\n.*?\n## Dein Schreibraum\n",
        block + "## Dein Schreibraum\n",
        t,
        flags=re.S,
    )
    if nt == t:
        raise SystemExit(f"block not replaced {p}")
    p.write_text(nt, encoding="utf-8")

print("patched", len(mapping), "session cores")
