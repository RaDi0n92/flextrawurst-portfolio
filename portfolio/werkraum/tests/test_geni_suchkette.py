#!/usr/bin/env python3
"""Test der ganzen Kette, die am 03./04.08.2026 gebaut wurde -- ohne Browser.

Geprueft wird, was tatsaechlich schiefgehen kann, nicht was ohnehin laeuft:
  1. Suche liefert Treffer und schreibt sie ins Log
  2. Vorschau springt auf die Fundstelle statt auf den Textanfang
  3. Lesefenster blaettert weiter, statt alles am Stueck zu geben
  4. Kennungen: kurze Nummern werden verstanden, erfundene nicht angenommen
  5. Entstehungsverlauf ist im Index auffindbar
  6. Der Sensor sieht mehr als die letzten 2000 IDs
  7. Tiefe hat keinen Deckel mehr
  8. Inbox-Reihenfolge stellt die Uebergangenen nach vorn
  9. AI-Stroeme sind pausiert, aber vollstaendig im Roster

Aufruf: python3 /root/werkraum/tests/test_geni_suchkette.py
"""

import sys

sys.path.insert(0, "/root/werkraum")
sys.path.insert(0, "/root/werkraum/geni")

ergebnisse = []


def pruefe(name, bedingung, hinweis=""):
    ergebnisse.append((name, bool(bedingung)))
    print(f"  {'OK  ' if bedingung else 'FEHL'}  {name}{'  -- ' + str(hinweis) if hinweis else ''}",
          flush=True)


def main() -> int:
    print("GENI-Suchkette\n")

    from selbst_suche import suchen, brennpunkt, _entstehung_sammeln
    import dokumentieren as dok
    import suchlog

    frage = "haftung wächter startimpuls"
    treffer = suchen(frage, 8, sucher="test", sucher_art="test", anlass="kettentest")
    pruefe("1 Suche liefert Treffer", len(treffer) > 0, f"{len(treffer)}")
    pruefe("1 Suche wurde protokolliert", treffer and treffer[0].get("suche_id"),
           f"suche_id={treffer[0].get('suche_id') if treffer else None}")

    # 2. Brennpunkt -- an einem Text, bei dem der Begriff nachweislich nicht vorn steht
    text = "A" * 900 + " haftung steht hier hinten " + "B" * 900
    b = brennpunkt(text, "haftung", 300)
    pruefe("2 Vorschau springt auf die Fundstelle", b["von"] > 500, f"ab Zeichen {b['von']}")
    pruefe("2 Treffer ist markiert", "«haftung»" in b["ausschnitt"])
    pruefe("2 Ausschnitt bleibt unveraendert (nur Marken dazu)",
           b["ausschnitt"].replace("«", "").replace("»", "") == text[b["von"]:b["bis"]])

    # 3. Blaettern
    lang = max(treffer, key=lambda t: len(t.get("text") or ""))
    stand = {}
    erst = dok._fenster_formatieren([lang], frage, stand, False)
    zweit = dok._fenster_formatieren([lang], frage, stand, True)
    pruefe("3 zweites Fenster zeigt anderes Stueck", erst != zweit)
    pruefe("3 Lesestand wandert vorwaerts", stand[lang["id"]] > 0, stand[lang["id"]])

    # 4. Kennungen
    angeboten = {"knoten:49744760": {"nr": 1}, "sp:kimi:3": {"nr": 2}}
    nummern = {1: "knoten:49744760", 2: "sp:kimi:3"}
    pruefe("4 Nummern werden verstanden",
           dok._kennungen_deuten([1, 2], angeboten, nummern) == ["knoten:49744760", "sp:kimi:3"])
    pruefe("4 Nummern als Text ebenso",
           dok._kennungen_deuten("1, 2", angeboten, nummern) == ["knoten:49744760", "sp:kimi:3"])
    pruefe("4 erfundene Kennung wird NICHT angenommen",
           dok._kennungen_deuten(["knoten:49744780"], angeboten, nummern) == [],
           "genau der Fehler, der 88 Lesevorgaenge kostete")

    # 5. Entstehungsverlauf
    stuecke = _entstehung_sammeln()
    pruefe("5 Entstehungsverlauf zerlegt", len(stuecke) > 10, f"{len(stuecke)} Stuecke")
    gefunden = suchen("wie geni entstanden ist gespraech daniel", 20,
                      sucher="test", sucher_art="test", anlass="kettentest")
    pruefe("5 Entstehung im Index auffindbar",
           any(t["id"].startswith("entstehung:") for t in gefunden),
           [t["id"] for t in gefunden if t["id"].startswith("entstehung:")][:3])

    # 6. Sensorweite -- der alte sah nur die letzten 2000 IDs
    import sqlite3
    hoechste = sqlite3.connect("file:/root/geni_gedaechtnis/knoten.db?mode=ro", uri=True) \
        .execute("SELECT MAX(id) FROM knoten").fetchone()[0]
    ids = [int(t["id"].split(":")[1]) for t in gefunden
           if t["id"].startswith("knoten:") and t["id"].split(":")[1].isdigit()]
    pruefe("6 Sensor reicht hinter das alte Kurzfenster",
           any(i < hoechste - 2000 for i in ids) if ids else False,
           f"tiefste ID {min(ids) if ids else '-'} bei MAX {hoechste}")

    # 7. Deckel
    import inspect, gedaechtnis_ops
    quelle = inspect.getsource(gedaechtnis_ops.tiefe_erhoehen)
    pruefe("7 kein Deckel mehr bei 3", "min(3," not in quelle and "alt + 1" in quelle)

    # 8./9. Inbox
    import inbox_fragen
    from teilnehmer_roster import TEILNEHMER, fragen_aktive
    folge = [t["id"] for t in inbox_fragen.reihenfolge()]
    pruefe("8 uebergangene Codewesen stehen vorn",
           folge and folge[0] in ("F3INSCHM3CK3R", "traeumerlie", "R1ZZ1", "jumpa",
                                  "Resonanzknoten", "daniel", "geni"),
           " -> ".join(folge[:4]))
    aktiv = {t["id"] for t in fragen_aktive()}
    stroeme = {t["id"] for t in TEILNEHMER if t["typ"] == "ai_strom"}
    pruefe("9 nur claude von den AI-Stroemen aktiv", aktiv & stroeme == {"claude"},
           sorted(aktiv & stroeme))
    pruefe("9 alle Stroeme bleiben im Roster", len(stroeme) == 8, f"{len(stroeme)} Eintraege")

    # 10. das Log hat mitgeschrieben
    nie = suchlog.nie_erschienen(["knoten:2", "knoten:99999999999"])
    pruefe("10 Log beantwortet 'nie erschienen'", nie == ["knoten:99999999999"], nie)

    fehler = [n for n, ok in ergebnisse if not ok]
    print(f"\n{len(ergebnisse) - len(fehler)}/{len(ergebnisse)} bestanden")
    if fehler:
        print("nicht bestanden: " + ", ".join(fehler))
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main())
