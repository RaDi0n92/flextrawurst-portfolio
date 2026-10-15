import json
import os
import statistics
import sys
from collections import defaultdict

SPUR = os.environ.get("STROMSPUR_ZIEL", "/root/werkraum/_opencode/spuren") + "/spur.jsonl"

LESE = {"read", "glob", "grep", "list"}
FRAGE = {"question", "todowrite", "task", "webfetch", "websearch"}
SCHREIB = {"write", "edit", "patch", "multiedit"}

BESCHRIEBEN = {
    "anlauf_verzoegerung": "Eingang bis zum ersten Werkzeugaufruf",
    "erster_zug": "welches Werkzeug zuerst",
    "erstes_schreiben": "Position des ersten Schreibvorgangs",
    "lesen_vor_schreiben": "liest er, bevor er schreibt",
    "taktrate_ms": "mittlere Pause zwischen zwei Werkzeugaufrufen",
    "gruendlichkeit_ms": "mittlere Dauer eines einzelnen Aufrufs",
    "parallelismus": "Aufrufe binnen einer halben Sekunde",
    "fragquote": "Anteil der Aufrufe, die nachfragen statt tun",
    "fehlerreaktion": "arbeitet er nach einem Fehler weiter",
    "werkzeugzahl": "Anzahl Werkzeugaufrufe",
    "laufzeit_ms": "Eingang bis zum Leerlauf",
}

NICHT_GESAGT = [
    "Ob eine Antwort gut oder schlecht war.",
    "Ob ein Strom klüger ist als ein anderer.",
    "Ob ein Modell etwas 'fühlt'.",
    "Ob eine Marotte Absicht war oder Zufall.",
    "Ob ein Strom 'gut eingelesen' hat - nur die Reihenfolge zaehlt.",
]


SPRACH_MUSTER = ("zögern", "nachfrage", "ablehnung", "zuversicht", "entschuldigung", "vorsicht",
                "woerter", "fragen", "ausrufe", "sätze")


def sprache_mittel(antworten):
    if not antworten:
        return None
    out = {}
    for key in SPRACH_MUSTER:
        werte = [a[key] for a in antworten if isinstance(a.get(key), (int, float))]
        out[key] = round(sum(werte) / len(werte), 2) if werte else None
    return out


def lade():
    zeilen = []
    if not os.path.exists(SPUR):
        return zeilen
    with open(SPUR, "r", encoding="utf-8") as fh:
        for roh in fh:
            roh = roh.strip()
            if not roh:
                continue
            try:
                zeilen.append(json.loads(roh))
            except json.JSONDecodeError:
                continue
    return zeilen


def kennung(zeile):
    return "pid" + str(zeile.get("pid", "?")) + "|" + str(zeile.get("modell") or "?")


def baue_sessions(zeilen):
    sessions = defaultdict(list)
    for z in zeilen:
        sessions[kennung(z)].append(z)
    return sessions


def werte(ereignisse):
    vor = [e for e in ereignisse if e.get("typ") == "tool_vor"]
    leerlauf = [e for e in ereignisse if e.get("typ") == "leerlauf"]
    eingang = [e for e in ereignisse if e.get("typ") == "eingang"]

    ergebnis = {
        "werkzeugzahl": len(vor),
        "modell": ereignisse[0].get("modell"),
        "provider": ereignisse[0].get("provider"),
        "strom": ereignisse[0].get("strom"),
        "pid": ereignisse[0].get("pid"),
        "session": ereignisse[0].get("session"),
        "auftrag": eingang[0].get("auftrag") if eingang else None,
        "antworten": len([e for e in ereignisse if e.get("typ") == "antwort"]),
        "sprache": sprache_mittel([e for e in ereignisse if e.get("typ") == "antwort"]),
    }

    if not vor:
        return ergebnis

    erster = vor[0]
    ergebnis["anlauf_verzoegerung"] = erster.get("ms_seit_eingang")
    ergebnis["erster_zug"] = erster.get("name")

    takte = [e["ms_seit_letztem"] for e in vor if isinstance(e.get("ms_seit_letztem"), (int, float))]
    ergebnis["taktrate_ms"] = int(statistics.median(takte)) if takte else None

    dauer = [e["dauer_ms"] for e in ereignisse if e.get("typ") == "tool_nach" and isinstance(e.get("dauer_ms"), (int, float))]
    ergebnis["gruendlichkeit_ms"] = int(statistics.median(dauer)) if dauer else None

    zt = vor[0]["ts"]
    parallel = 0
    for e in vor:
        if e["ts"] - zt <= 500:
            parallel += 1
        zt = max(zt, e["ts"])
    ergebnis["parallelismus"] = parallel

    namen = [e.get("name", "") for e in vor]
    fragen = sum(1 for n in namen if n in FRAGE)
    ergebnis["fragquote"] = round(fragen / len(vor), 2) if vor else None

    schreib_idx = next((i for i, n in enumerate(namen) if n in SCHREIB), None)
    lese_idx = next((i for i, n in enumerate(namen) if n in LESE), None)
    ergebnis["erstes_schreiben"] = schreib_idx
    ergebnis["lesen_vor_schreiben"] = (lese_idx is not None and (schreib_idx is None or lese_idx < schreib_idx))

    fehler_stellen = [i for i, e in enumerate(ereignisse) if e.get("typ") == "tool_nach" and e.get("fehler")]
    if fehler_stellen:
        danach = [e for e in ereignisse if e.get("typ") == "tool_vor" and e["ts"] > ereignisse[fehler_stellen[0]]["ts"]]
        ergebnis["fehlerreaktion"] = "weitergearbeitet" if danach else "abgebrochen"
    else:
        ergebnis["fehlerreaktion"] = "kein Fehler"

    ergebnis["laufzeit_ms"] = leerlauf[-1].get("gesamt_ms") if leerlauf else (ereignisse[-1].get("ts") - eingang[0]["ts"] if eingang else None)
    return ergebnis


def main():
    zeilen = lade()
    if not zeilen:
        print("Keine Spur gefunden unter: " + SPUR)
        print("Das Plugin schreibt erst ab dem naechsten opencode-Start.")
        return

    sessions = baue_sessions(zeilen)
    zeilen_ausgabe = []
    for key, ereignisse in sessions.items():
        ereignisse.sort(key=lambda e: e.get("ts", 0))
        zeilen_ausgabe.append((key, werte(ereignisse)))

    zeilen_ausgabe.sort(key=lambda x: str(x[1].get("modell")))

    print("=" * 78)
    print("STROMSPUR - Rohmessung. Gelesen aus: " + SPUR)
    print("=" * 78)
    print()
    print("LEITSATZ: Das hier misst Modell + Harness + Anweisungen + Werkzeuge.")
    print("Nicht das Modell allein. Zwei Modelle vergleichen heisst immer auch,")
    print("zwei Umgebungen vergleichen. Fuer die Differenz: dieselbe Strom-Identitaet")
    print("mit und ohne Anweisungsdatei starten. Das ist der schnellste Test.")
    print()

    spalten = ["strom", "modell", "werkzeugzahl", "anlauf_verzoegerung", "erster_zug",
               "lesen_vor_schreiben", "taktrate_ms", "gruendlichkeit_ms",
               "fragquote", "fehlerreaktion"]

    spalten_kopf = (
        f"{'AUFTRAG':<9}|{'STROM':<13}|{'MODELL':<25}|{'TOOLS':>5}|{'ANLAUF':>7}|"
        f"{'ERSTER ZUG':<12}|{'L:V/S':<6}|{'TAKT':>7}|{'GRUEND':>7}|{'FRAGE':>6}|FEHLER"
    )
    print(spalten_kopf)
    print("-" * len(spalten_kopf))

    for key, w in zeilen_ausgabe:
        def z(f, breite=0):
            v = w.get(f)
            return str(v).rjust(breite) if breite else str(v or "-")

        lvs = "-" if w.get("lesen_vor_schreiben") is None else ("ja" if w["lesen_vor_schreiben"] else "nein")
        print(
            f"{str(w.get('auftrag') or '-')[:8]:<9}|"
            f"{str(w.get('strom'))[:12]:<13}|"
            f"{str(w.get('modell'))[:24]:<25}|"
            f"{z('werkzeugzahl', 5):>5}|"
            f"{z('anlauf_verzoegerung', 7):>7}|"
            f"{str(w.get('erster_zug'))[:11]:<12}|"
            f"{lvs:<6}|"
            f"{z('taktrate_ms', 7):>7}|"
            f"{z('gruendlichkeit_ms', 7):>7}|"
            f"{z('fragquote', 6):>6}|"
            f"{w.get('fehlerreaktion')}"
        )

    auftrage = defaultdict(list)
    for _, w in zeilen_ausgabe:
        if w.get("auftrag"):
            auftrage[w["auftrag"]].append(w)

    vergleichbar = {a: v for a, v in auftrage.items() if len({x.get("modell") for x in v}) > 1}
    print()
    if vergleichbar:
        print("MODUS STRENG - gleicher Auftrag, mehrere Modelle:")
        for a, v in vergleichbar.items():
            modelle = sorted({str(x.get("modell")) for x in v})
            takt = [x.get("taktrate_ms") for x in v if x.get("taktrate_ms")]
            print(f"  Auftrag {a}: {len(v)} Sessions ueber {len(modelle)} Modelle")
            print(f"    Modelle: {', '.join(modelle)}")
            print(f"    Takt: {sorted(takt)} ms")
    else:
        print("MODUS STRENG: noch nichts. Es braucht mindestens zwei abgeschlossene")
        print("Sessions mit demselben Auftrag (gleiche AUFTRAG-Kennung oben).")

    print()
    print("MODUS FREI - Marotten im normalen Chat, ohne Auftragsfilter.")
    print("Achtung: hier werden verschiedene Aufgaben verglichen. Fuer einen")
    print("Fingerprint taugt das nicht, fuer Arbeitsweise schon.")
    print()
    nach_modell = defaultdict(list)
    for _, w in zeilen_ausgabe:
        nach_modell[str(w.get("modell"))].append(w)
    print(
        f"{'MODELL':<25}|{'SITZ':>5}|{'ZOE':>5}|{'NACHFR':>7}|{'ABLEHN':>7}|{'ZVERT':>7}|{'WORTE':>6}|{'TAKT':>7}"
    )
    print("-" * 84)
    for m, ws in sorted(nach_modell.items()):
        s = [x.get("sprache") or {} for x in ws]
        s = [x for x in s if x]
        def av(k):
            v = [x[k] for x in s if isinstance(x.get(k), (int, float))]
            return round(sum(v) / len(v), 2) if v else None
        takte = [x.get("taktrate_ms") for x in ws if x.get("taktrate_ms")]
        def f(v, b=0):
            return str(v).rjust(b) if b else str(v or "-")
        print(
            f"{m[:24]:<25}|{len(ws):>5}|"
            f"{f(av('zögern'), 5)}|{f(av('nachfrage'), 7)}|{f(av('ablehnung'), 7)}|"
            f"{f(av('zuversicht'), 7)}|{f(av('woerter'), 6)}|"
            f"{f(sorted(takte)[len(takte)//2] if takte else None, 7)}"
        )
    print()
    print("ZOE=Zogern, NACHFR=Nachfragen, ABLEHN=Ablehnung, ZVERT=Zuversicht,")
    print("WORTE=Woerter je Antwort, TAKT=mittlerer Takt. Alles Durchschnitt je Modell.")
    print()

    print()
    print("Alle Zeiten in Millisekunden. ANLAUF = Eingang bis erster Werkzeugaufruf.")
    print("TAKT = mittlere Pause zwischen zwei Aufrufen. GRUEND = mittlere Dauer eines Aufrufs.")
    print("FRAGE = Anteil der Aufrufe, die nachfragen statt zu tun.")
    print()
    print("-" * 78)
    print("DAS IST GEMESSEN:")
    for k, v in BESCHRIEBEN.items():
        print(f"  {k:<24} {v}")
    print()
    print("-" * 78)
    print("DAS IST NICHT GESAGT - auch nicht mit tausend Zahlen:")
    for n in NICHT_GESAGT:
        print("  - " + n)
    print("-" * 78)
    print()
    print("Ein Vergleich zwischen zwei Modellen traegt erst, wenn beide")
    print("denselben Auftrag bekommen haben. Sonst vergleicht man")
    print("Aufgaben, nicht Modelle.")
    print()


if __name__ == "__main__":
    main()