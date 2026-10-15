#!/usr/bin/env python3
"""Werkzeug des Agenten im Bridge-Terminal: sprechen und ansehen. Nur Standardbibliothek.

  bridge_cli.py say "Text"     Text erscheint in der Raute (Banner und Ticker) dieses Terminals.
  bridge_cli.py schreibe "Text"  Wie "say", aber mit den Händen: die Bridge drückt die Tastenkombination deiner Raute (steht in ihr,
                               z. B. [F13]) und tippt den Text in das Eingabefeld an deiner Raute (höchstens 500 Zeichen, nur wenn
                               Daniel dir die Hände erlaubt hat).
  bridge_cli.py hoere          Was Daniel seit dem letzten Aufruf in sein Mikrofon gesagt hat (erkannter Text; leer, wenn nichts Neues).
  bridge_cli.py see            Pfad und Alter des letzten Bildes, das der Scanner dieses Terminals geschickt hat.
  bridge_cli.py lage           Was für dich gerade klappt und was nicht: Augen, Hände, Ziel, jede Funktion mit Zustand und Grund. Was du nicht beheben kannst, teilst du mit (say).
  bridge_cli.py agenten        Wer in der Bridge läuft: Name, Strom, Zustand (läuft/pausiert/beendet), Gruppen, Eltern und Kinder, was die Bridge mit jedem tun kann.
  bridge_cli.py gruppe NAME beitreten|verlassen   Einer Gruppe beitreten oder sie verlassen (Name: Buchstaben, Ziffern, _ . -).
  bridge_cli.py sende AN "Text"   Eine Nachricht an einen Agenten (Name oder Terminal-ID) tippen; mit @GRUPPE statt AN an alle Mitglieder (nie an dich selbst).
  bridge_cli.py auftrag AN "Text" Einem Agenten einen Auftrag geben; er meldet Status und Ergebnis selbst zurück (nichts gilt als fertig, bevor er es sagt).
  bridge_cli.py auftrag-status ID angenommen|laeuft|fertig|fehler ["Ergebnis" ["Unsicherheit"]]   Den Status eines Auftrags melden, den du erhalten hast.
  bridge_cli.py auftraege      Deine gesendeten und erhaltenen Aufträge mit Status.
  bridge_cli.py kind NAME [STROM]   Einen Unteragenten melden, der in DEINEM Prozess läuft (die Bridge kann ihn nur anzeigen, nicht ansprechen oder anhalten).
  Hände (nur auf dem gebundenen Fenster, mit Lease; Koordinaten sind Pixel des Bildes, das du mit `see` bekommen hast; mit --seq=N auf ein bestimmtes Bild beziehen):
  bridge_cli.py lease [frei] [SEKUNDEN]   Die Lease auf dein Ziel nehmen (höchstens einer zugleich) oder zurückgeben. Ohne Lease geht kein Klick.
  bridge_cli.py controller knopf A [MS] | stick links X Y [MS] | trigger rechts W [MS] | loslassen   [--geraet=0..3]   Virtueller Controller (nur im Profil controller/hybrid und mit Lease; Knöpfe a b x y lb rb back start guide ls rs hoch runter links rechts).
  bridge_cli.py klick X Y [rechts|mitte] [doppel]   Klicken.
  bridge_cli.py ziehe X1 Y1 X2 Y2 [MS]   Mit gedrückter Taste von Punkt 1 nach Punkt 2 ziehen (50 bis 5000 ms, Standard 300).
  bridge_cli.py tippe "Text"   Text in das Ziel tippen (das Ziel muss die Tastatur haben, sie wird ihm gegeben; höchstens 500 Zeichen).
  bridge_cli.py taste "Strg+S"  Eine Tastenkombination drücken (F12 ist der Not-Aus der Bridge und gesperrt).
  bridge_cli.py rad X Y DY      Mausrad am Punkt drehen (DY positiv = nach unten, höchstens 20).
  bridge_cli.py menue "Name"    Einen Eintrag im gerade offenen Bridge-Menü beim Namen wählen (der Anfang des Namens genügt, wenn er eindeutig ist). Koordinaten gibt es dafür nicht:
                               der Körper kennt das Menü selbst. Nur wenn Daniel „Bridge-Menüs für Agenten bedienbar“ eingeschaltet hat und nur für erlaubte Einträge (Beenden, Not-Aus,
                               Pausieren, Hände und Steuerprofil sind immer gesperrt).
  Die Antwort trennt accepted (zugelassen), delivered (an das System übergeben), observed (nachgemessen) und audited (protokolliert). Not-Aus, Daniels Eingabe oder ein Verbindungsabbruch
  stoppen alles und entziehen die Lease; danach musst du sie neu holen.
  WorldDOM (Begriffe statt Koordinaten; echte Struktur aus Browser und Bedienungshilfen, aus dem Bild Erschlossenes, bewusst Angelegtes — jeder Knoten nennt Herkunft, Konfidenz, Alter):
  bridge_cli.py weltdom [--herkunft=real|inferred|authored|projected] [--rolle=R] [--text=T]   Frisch messen und die Knoten deines Ziels zeigen (und welche Quellen fehlten).
  bridge_cli.py knoten ID klick|lesen|text "Text" [--erwartung="…"]   An einem Knoten handeln und zurücklesen (klick und text brauchen die Lease). `bestaetigt` ist True, False oder null (nicht nachprüfbar).
  bridge_cli.py zeige X Y [--einfuegen [klick|text "Text"]] [--an=NAME,NAME]   Auf etwas zeigen (X, Y im Bild): ohne --einfuegen nur ein Zeichen in der Arbeitsfläche, mit --einfuegen eine echte Handlung.
  bridge_cli.py anker "Name" [X Y] [--projiziert]   Einen eigenen Knoten anlegen (an einem Bildpunkt oder ohne Ort = virtuell); bridge_cli.py anker-weg ID entfernt ihn.
  Abläufe (deklarative Graphen als JSON-Datei; ein Ablauf kann nichts, was du nicht selbst könntest; er handelt mit DEINER Lease):
  bridge_cli.py markiert [--alt]   Frisch messen und ein Bild mit nummerierten Rahmen um die bedienbaren Knoten schicken (danach „see“); die Tabelle Nummer → Knoten-Kennung kommt als Antwort.
  bridge_cli.py profil speichern NAME [--programm=… --seite=… --spiel=… --beschreibung=…]   Die eigenen Anker dieses Ziels als Profil speichern (neue Version, nichts wird überschrieben).
  bridge_cli.py profil laden NAME [VERSION]  |  profil liste [--programm=…]  |  profil weg NAME  |  profil zurueck NAME   Profile wieder laden, finden, aus- und einblenden (nie löschen).
  bridge_cli.py ablauf liste                 Gespeicherte Abläufe (mit Versionen) und deine Läufe.
  bridge_cli.py ablauf neu DATEI.json        Einen Ablauf speichern: jede Speicherung ist eine NEUE Version, nichts wird überschrieben.
  bridge_cli.py ablauf zeige ID [VERSION]    Den Ablauf als JSON.
  bridge_cli.py ablauf start ID [--modi=free,shadow,witness,daniel_gate] [--warten] [--trotzdem]   Einen Lauf starten (ohne --modi: free; shadow führt nichts aus).
  bridge_cli.py ablauf status|pause|weiter|stopp LAUF        Einen eigenen Lauf abfragen oder steuern.
  bridge_cli.py ablauf checkpoint LAUF NAME  Einen Beobachtungspunkt setzen;  bridge_cli.py ablauf zweig LAUF NAME   daraus einen neuen Lauf ableiten (der alte bleibt).
  bridge_cli.py ablauf replay LAUF           Die gespeicherte Spur ansehen — es wird nichts ausgeführt.
  Lernen kann nur Daniel einschalten.
  bridge_cli.py kapsel moment [--art=agent|ziel|kompletter_moment|zeitraum] [Grund]   Den jetzigen Moment einfrieren (unveränderlich; Lücken stehen drin).
  bridge_cli.py kapsel liste|zeige K|suche TAG…|folge K|vergleiche A B|ebene K ART Text   Kapseln ansehen, ergänzen (eigene Ebene), Folge-Kapsel ableiten.
  bridge_cli.py kapsel wiedergabe K  |  kapsel gespraech-laden K   Das in der Kapsel festgehaltene Modellgespräch ansehen (ohne Modellaufruf) oder ins Mischpult laden und mit „chat“ weiterführen.
  bridge_cli.py kapsel zeitlinie [ZEIT_MS [--richtung=1|-1]]   Durch den aufgezeichneten Verlauf laufen — nur lesen, nichts wird ausgeführt.
  bridge_cli.py kapsel zweig K LAUF CHECKPOINT   |   kapsel zweig-messen LAUF   Zweig aus einer Kapsel (startet erst nach frischer Messung).
  bridge_cli.py beobachtung start NAME… [--bilder] | stop | status | zustellen | lesen NAME | bilder an|aus | budget AUFRUFE TOKENS | jetzt [Auftrag]   Hauhaucs beobachtet; nur „jetzt“ ruft das Modell.
  bridge_cli.py test vorflug PARTNER | start PARTNER [--ab=N] [--szenario=NAME] | szenarien | karte | status | ansage "Schritt N · Prüfe: … · Mache: … · Erwarte: …" | ursache "…" (hebt den Halt nach dem dritten Fehlversuch auf) | getan "…" | gesehen "…" ok|anders|fehler | zuschauer "…" bestaetigt|widerspruch | planaenderung "…" | nochmal | nicht_getestet "Grund" | kuer "…" | stopp   Praxistest zu zweit, Schritt für Schritt (die Ansage landet sichtbar in deiner Raute).
  bridge_cli.py seed vorschlagen ZIELTYP "Titel" (--inhalt=TEXT | --datei=PFAD) [--an=A,B] [--ziel=PFAD] [--kapseln=k-1,k-2] [--seed=ID] [--budget=JSON]   Aus einer Erfahrung einen Seed vorschlagen (ZIELTYP: ablauf kontext memory dokument skill loop goal). Ausgeliefert wird nur nach Daniels Freigabe.
  bridge_cli.py seed liste [--status=S] | zeige ID [V] | pruefen ID [V] | ausliefern ID [V] | zurueckziehen ID [V] | exportieren ID   Seeds ansehen, ausliefern (wartet auf Daniels Ja), zurücknehmen (nur eigene).
  bridge_cli.py loop liste | status ID | pause ID | weiter ID | stopp ID   Eigene Loops und Goals mit Budget steuern; nach „stopp“ beginnt nichts Neues.
  bridge_cli.py chat "Text"   Frei mit Hauhaucs chatten (hin und her); der Verlauf liegt im Mischpult und lässt sich dort kürzen, bearbeiten und speichern.
  bridge_cli.py pult zeige|leeren|halbieren|zurueck [N]|text TEXT|feld NAME TEXT|feedback TEXT|grenzen ZEICHEN TOKENS|speichern   Das Kontext-Mischpult der Beobachter-Sitzung.
  bridge_cli.py hilfe          Diese Übersicht.

Umgebung, vom Starter gesetzt: BRIDGE_TERMINAL_ID, BRIDGE_TERMINAL_TOKEN, BRIDGE_RUNTIME_DIR.
"""

from __future__ import annotations

import json
import os
import socket
import sys

TIMEOUT_SECONDS = 5.0
LANGE_BEFEHLE = {"haende": 30.0, "weltdom": 60.0, "ablauf": 60.0, "kapsel": 330.0, "seed": 150.0, "test": 30.0}  # Hände, Messen mit Bilderkennung und wartende Abläufe dauern länger als eine Meldung


def ask(request: dict[str, object], env: dict[str, str] | None = None) -> dict[str, object]:
    env = os.environ if env is None else env
    try:
        terminal_id, token, runtime = env["BRIDGE_TERMINAL_ID"], env["BRIDGE_TERMINAL_TOKEN"], env["BRIDGE_RUNTIME_DIR"]
    except KeyError as missing:
        return {"ok": False, "reason": f"not_in_bridge_terminal:{missing.args[0]}"}
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.settimeout(LANGE_BEFEHLE.get(request.get("cmd"), TIMEOUT_SECONDS))
        try:
            sock.connect(os.path.join(runtime, "agent.sock"))
            sock.sendall((json.dumps({**request, "terminal_id": terminal_id, "token": token}) + "\n").encode())
            data = b""
            while not data.endswith(b"\n"):
                chunk = sock.recv(65536)
                if not chunk:
                    break
                data += chunk
        except OSError as exc:
            return {"ok": False, "reason": f"launcher_unreachable:{exc.__class__.__name__}"}
    try:
        reply = json.loads(data)
    except ValueError:
        return {"ok": False, "reason": "invalid_reply"}
    frame = reply.get("frame")
    if isinstance(frame, dict) and "relative_path" in frame:
        frame["path"] = os.path.join(runtime, frame["relative_path"])
    return reply


def _zahl(text: str):
    try:
        return int(text)
    except ValueError:
        return None


def _controller(args: list[str]) -> dict | None:
    """controller knopf A [MS] [--geraet=N] | stick links X Y [MS] | trigger rechts W [MS] | loslassen — als Aktion für den Körper."""
    index = 0
    rest = []
    for a in args:
        if a.startswith("--geraet="):
            index = _zahl(a[9:])
            if index is None:
                return None
        else:
            rest.append(a)
    try:
        if rest[0] == "knopf" and len(rest) in (2, 3):
            return {"art": "controller", "befehl": "knopf", "index": index, "name": rest[1], **({"dauer_ms": int(rest[2])} if len(rest) == 3 else {})}
        if rest[0] == "stick" and len(rest) in (4, 5):
            return {"art": "controller", "befehl": "stick", "index": index, "name": rest[1], "wert": [float(rest[2]), float(rest[3])], **({"dauer_ms": int(rest[4])} if len(rest) == 5 else {})}
        if rest[0] == "trigger" and len(rest) in (3, 4):
            return {"art": "controller", "befehl": "trigger", "index": index, "name": rest[1], "wert": [float(rest[2]), 0.0], **({"dauer_ms": int(rest[3])} if len(rest) == 4 else {})}
        if rest[0] == "loslassen" and len(rest) == 1:
            return {"art": "controller", "befehl": "loslassen", "index": index}
    except (ValueError, IndexError):
        return None
    return None


def _haende(argv: list[str]) -> dict | None:
    """Die Hände-Befehle in Anfragen übersetzen; None bei falschem Aufruf. `--seq=N` am Ende bezieht die Koordinaten auf ein bestimmtes Bild."""
    seq = None
    rest = []
    for a in argv:
        if a.startswith("--seq="):
            seq = _zahl(a[6:])
            if seq is None:
                return None
        else:
            rest.append(a)
    befehl, args = rest[0], rest[1:]
    zusatz = {} if seq is None else {"seq": seq}
    if befehl == "lease":
        frei = bool(args) and args[0] == "frei"
        zahlen = [a for a in args if a != "frei"]
        if len(zahlen) > 1 or (zahlen and _zahl(zahlen[0]) is None):
            return None
        return ask({"cmd": "lease", "aktion": "freigeben" if frei else "nehmen", **({"ttl_s": _zahl(zahlen[0])} if zahlen else {})})
    if befehl == "controller" and args:
        akt = _controller(args)
        return None if akt is None else ask({"cmd": "haende", "aktion": akt, **zusatz})
    if befehl == "klick" and len(args) >= 2:
        x, y, extra = _zahl(args[0]), _zahl(args[1]), args[2:]
        if x is None or y is None or not set(extra) <= {"rechts", "mitte", "doppel"}:
            return None
        aktion = {"art": "doppelklick" if "doppel" in extra else "klick", "punkt": [x, y], **({"taste": "rechts" if "rechts" in extra else "mitte"} if {"rechts", "mitte"} & set(extra) else {})}
        return ask({"cmd": "haende", "aktion": aktion, **zusatz})
    if befehl == "ziehe" and len(args) in (4, 5):
        z = [_zahl(a) for a in args]
        if None in z:
            return None
        return ask({"cmd": "haende", "aktion": {"art": "ziehen", "punkt": z[:2], "bis": z[2:4], **({"dauer_ms": z[4]} if len(z) == 5 else {})}, **zusatz})
    if befehl == "menue" and args:
        return ask({"cmd": "haende", "aktion": {"art": "menue", "text": " ".join(args)}, **zusatz})
    if befehl == "tippe" and args:
        return ask({"cmd": "haende", "aktion": {"art": "tippen", "text": " ".join(args)}, **zusatz})
    if befehl == "taste" and len(args) == 1:
        return ask({"cmd": "haende", "aktion": {"art": "taste", "kombi": args[0]}, **zusatz})
    if befehl == "rad" and len(args) == 3:
        z = [_zahl(a) for a in args]
        if None in z:
            return None
        return ask({"cmd": "haende", "aktion": {"art": "rad", "punkt": z[:2], "dy": z[2]}, **zusatz})
    return None


def _test(argv: list[str]) -> dict | None:
    """test …: der Praxistest als Graph (Ansage in der Raute, Handeln, Gesehen, Zuschauer)."""
    woerter, opt = _optionen(argv)
    if not woerter:
        return None
    b, a = woerter[0], woerter[1:]
    k = lambda **d: ask({"cmd": "test", **d})
    if b == "vorflug" and len(a) == 1 and not opt:
        return k(befehl="vorflug", partner=a[0])
    if b == "start" and len(a) == 1 and set(opt) <= {"ab", "szenario"}:
        ab = _zahl(str(opt["ab"])) if "ab" in opt else 1
        return None if ab is None else k(befehl="start", partner=a[0], ab=ab, **({"szenario": str(opt["szenario"])} if "szenario" in opt else {}))
    if b in ("karte", "status", "nochmal", "stopp", "szenarien") and not a and not opt:
        return k(befehl=b)
    if b in ("ansage", "getan", "planaenderung", "kuer", "entdeckung", "nicht_getestet", "ursache") and a and not opt:
        return k(befehl="kuer" if b == "entdeckung" else b, text=" ".join(a))
    if b in ("gesehen", "zuschauer") and len(a) >= 2 and not opt:
        return k(befehl=b, text=" ".join(a[:-1]), urteil=a[-1])
    return None


def _seed(cmd: str, argv: list[str]) -> dict | None:
    """seed … und loop …: alles geht als ein Befehl „seed“ an den Starter, der streng prüft."""
    woerter, opt = _optionen(argv)
    if not woerter:
        return None
    b, a = woerter[0], woerter[1:]
    k = lambda **d: ask({"cmd": "seed", **d})
    if cmd == "loop":
        if b == "liste" and not a and not opt:
            return k(befehl="loop", aktion="liste")
        if b in ("status", "pause", "weiter", "stopp") and len(a) == 1 and not opt:
            return k(befehl="loop", aktion=b, loop=a[0])
        return None
    if b == "vorschlagen" and len(a) == 2 and set(opt) <= {"inhalt", "datei", "an", "ziel", "kapseln", "seed", "budget"} and (("inhalt" in opt) != ("datei" in opt)):
        inhalt = opt.get("inhalt")
        if "datei" in opt:
            try:
                with open(str(opt["datei"]), encoding="utf-8") as f:
                    inhalt = json.load(f) if a[0] == "ablauf" else f.read()
            except (OSError, ValueError):
                return {"ok": False, "reason": "datei_nicht_lesbar"}
        budget = None
        if "budget" in opt:
            try:
                budget = json.loads(str(opt["budget"]))
            except ValueError:
                return {"ok": False, "reason": "budget_kein_json"}
        r = {"befehl": "vorschlagen", "zieltyp": a[0], "titel": a[1], "inhalt": inhalt}
        if "an" in opt:
            r["empfaenger"] = [n for n in str(opt["an"]).split(",") if n]
        if "ziel" in opt:
            r["ziel_pfad"] = str(opt["ziel"])
        if "kapseln" in opt:
            r["kapseln"] = [x for x in str(opt["kapseln"]).split(",") if x]
        if "seed" in opt:
            r["seed"] = str(opt["seed"])
        if budget is not None:
            r["budget"] = budget
        return k(**r)
    if b == "liste" and not a and set(opt) <= {"status"}:
        return k(befehl="liste", **({"status": str(opt["status"])} if "status" in opt else {}))
    if b in ("zeige", "pruefen", "ausliefern", "zurueckziehen", "exportieren") and len(a) in (1, 2) and not opt:
        v = _zahl(a[1]) if len(a) == 2 else None
        if len(a) == 2 and v is None:
            return None
        return k(befehl=b, seed=a[0], **({"version": v} if v else {}))
    return None


def _kapsel(cmd: str, argv: list[str]) -> dict | None:
    """kapsel / beobachtung / pult: alles geht als ein Befehl „kapsel“ an den Starter; der prüft streng."""
    woerter, opt = _optionen(argv)
    if not woerter:
        return None
    b, a = woerter[0], woerter[1:]
    k = lambda **d: ask({"cmd": "kapsel", **d})
    if cmd == "kapsel":
        if b == "moment" and set(opt) <= {"art"}:
            return k(befehl="moment", grund=" ".join(a), **({"art": opt["art"]} if isinstance(opt.get("art"), str) else {}))
        if b == "liste" and not a and not opt:
            return k(befehl="liste")
        if b == "zeige" and len(a) == 1 and not opt:
            return k(befehl="zeige", kapsel=a[0])
        if b == "suche" and a and not opt:
            return k(befehl="suche", tags=a)
        if b == "folge" and len(a) == 1 and not opt:
            return k(befehl="folge", kapsel=a[0])
        if b == "vergleiche" and len(a) == 2 and not opt:
            return k(befehl="vergleiche", a=a[0], b=a[1])
        if b == "ebene" and len(a) >= 3 and not opt:
            return k(befehl="ebene", kapsel=a[0], art=a[1], text=" ".join(a[2:]))
        if b == "wiedergabe" and len(a) == 1 and not opt:
            return k(befehl="wiedergabe", kapsel=a[0])
        if b == "gespraech-laden" and len(a) == 1 and not opt:
            return k(befehl="gespraech_laden", kapsel=a[0])
        if b == "zeitlinie" and len(a) <= 1 and set(opt) <= {"richtung"}:
            z = _zahl(a[0]) if a else None
            if a and z is None:
                return None
            r = _zahl(opt["richtung"]) if "richtung" in opt else None
            return k(befehl="zeitlinie", **({"zeit_ms": z} if z is not None else {}), **({"richtung": r} if r in (-1, 1) else {}))
        if b == "zweig" and len(a) == 3 and not opt:
            return k(befehl="zweig", kapsel=a[0], lauf=a[1], checkpoint=a[2])
        if b == "zweig-messen" and len(a) == 1 and not opt:
            return k(befehl="zweig_messen", lauf=a[0])
        return None
    if cmd == "beobachtung":
        if b == "start" and a and set(opt) <= {"bilder"}:
            return k(befehl="beobachtung", aktion="start", agenten=a, bilder="bilder" in opt)
        if b in ("stop", "status", "zustellen") and not a and not opt:
            return k(befehl="beobachtung", aktion=b)
        if b == "lesen" and len(a) == 1 and not opt:
            return k(befehl="beobachtung", aktion="lesen", agent=a[0])
        if b == "bilder" and a in (["an"], ["aus"]) and not opt:
            return k(befehl="beobachtung", aktion="bilder", an=a[0] == "an")
        if b == "budget" and len(a) == 2 and not opt and _zahl(a[0]) is not None and _zahl(a[1]) is not None:
            return k(befehl="beobachtung", aktion="budget", max_aufrufe=_zahl(a[0]), max_tokens=_zahl(a[1]))
        if b == "jetzt" and set(opt) <= {"bilder"}:
            return k(befehl="beobachtung", aktion="jetzt", auftrag=" ".join(a), bilder="bilder" in opt)
        return None
    if cmd == "pult":
        if b in ("zeige", "leeren", "halbieren", "speichern") and not a and not opt:
            return k(befehl="mischpult", aktion=b)
        if b == "zurueck" and len(a) <= 1 and not opt:
            return k(befehl="mischpult", aktion="zurueck", **({"n": _zahl(a[0])} if a and _zahl(a[0]) else {}))
        if b == "text" and a and not opt:
            return k(befehl="mischpult", aktion="text", text=" ".join(a))
        if b == "feld" and len(a) >= 2 and not opt:
            return k(befehl="mischpult", aktion="feld", name=a[0], text=" ".join(a[1:]))
        if b == "feedback" and a and not opt:
            return k(befehl="mischpult", aktion="feedback", text=" ".join(a))
        if b == "grenzen" and len(a) == 2 and not opt:
            z, t = (None if x == "-" else _zahl(x) for x in a)
            return k(befehl="mischpult", aktion="grenzen", max_zeichen=z, max_tokens=t)
    return None


def _ablauf(argv: list[str]) -> dict | None:
    woerter, opt = _optionen(argv)
    if not woerter:
        return None
    b, a = woerter[0], woerter[1:]
    if b == "liste" and not a and not opt:
        return ask({"cmd": "ablauf", "befehl": "liste"})
    if b == "neu" and len(a) == 1 and not opt:
        try:
            with open(a[0], encoding="utf-8") as f:
                inhalt = json.load(f)
        except (OSError, ValueError):
            return {"ok": False, "reason": "datei_nicht_lesbar"}
        return ask({"cmd": "ablauf", "befehl": "neu", "ablauf": inhalt})
    if b == "zeige" and len(a) in (1, 2) and not opt:
        v = _zahl(a[1]) if len(a) == 2 else None
        if len(a) == 2 and v is None:
            return None
        return ask({"cmd": "ablauf", "befehl": "zeige", "ablauf": a[0], **({"version": v} if v else {})})
    if b == "start" and len(a) == 1 and set(opt) <= {"modi", "warten", "trotzdem"}:
        modi = [m for m in str(opt["modi"]).split(",") if m] if isinstance(opt.get("modi"), str) else None
        return ask({"cmd": "ablauf", "befehl": "start", "ablauf": a[0], **({"modi": modi} if modi else {}), **({"warten": True} if "warten" in opt else {}), **({"trotzdem": True} if "trotzdem" in opt else {})})
    if b in ("status", "pause", "weiter", "stopp", "replay") and len(a) == 1 and not opt:
        return ask({"cmd": "ablauf", "befehl": b, "lauf": a[0]})
    if b in ("checkpoint", "zweig") and len(a) == 2 and not opt:
        return ask({"cmd": "ablauf", "befehl": b, "lauf": a[0], **({"name": a[1]} if b == "checkpoint" else {"checkpoint": a[1]})})
    return None


def _optionen(argv: list[str]):
    """(Wörter, Optionen): `--name=wert` und `--name` werden herausgelöst."""
    woerter, opt = [], {}
    for a in argv:
        if a.startswith("--"):
            k, _, v = a[2:].partition("=")
            opt[k] = v if _ else True
        else:
            woerter.append(a)
    return woerter, opt


def _weltdom(argv: list[str]) -> dict | None:
    woerter, opt = _optionen(argv)
    befehl, args = woerter[0], woerter[1:]
    seq = None
    if "seq" in opt:
        seq = _zahl(str(opt["seq"]))
        if seq is None:
            return None
    zusatz = {} if seq is None else {"seq": seq}
    if befehl == "weltdom":
        erlaubt = {"herkunft", "rolle", "text", "seq", "alt"}
        if args or not set(opt) <= erlaubt:
            return None
        a = {k: opt[k] for k in ("herkunft", "rolle", "text") if k in opt and isinstance(opt[k], str)}
        if "alt" in opt:
            a["neu_messen"] = False
        return ask({"cmd": "weltdom", "befehl": "liste", "args": a, **zusatz})
    if befehl == "knoten" and len(args) >= 2 and set(opt) <= {"erwartung", "seq"}:
        aktion = {"klick": "klick", "lesen": "lesen", "text": "text_setzen"}.get(args[1])
        if aktion is None or (aktion == "text_setzen" and len(args) < 3) or (aktion != "text_setzen" and len(args) != 2):
            return None
        a = {"knoten": args[0], "aktion": aktion}
        if aktion == "text_setzen":
            a["text"] = " ".join(args[2:])
        if isinstance(opt.get("erwartung"), str):
            a["erwartung"] = opt["erwartung"]
        return ask({"cmd": "weltdom", "befehl": "aktion", "args": a, **zusatz})
    if befehl == "zeige" and len(args) >= 2 and set(opt) <= {"einfuegen", "an", "seq"}:
        x, y = _zahl(args[0]), _zahl(args[1])
        if x is None or y is None:
            return None
        a = {"punkt": [x, y], "modus": "einfuegen" if "einfuegen" in opt else "praesentieren"}
        rest = args[2:]
        if rest:
            if "einfuegen" not in opt or rest[0] not in ("klick", "text") or (rest[0] == "text" and len(rest) < 2) or (rest[0] == "klick" and len(rest) != 1):
                return None
            a["aktion"] = "klick" if rest[0] == "klick" else "text_setzen"
            if rest[0] == "text":
                a["text"] = " ".join(rest[1:])
        if isinstance(opt.get("an"), str):
            a["empfaenger"] = [n for n in opt["an"].split(",") if n]
        return ask({"cmd": "weltdom", "befehl": "zeige", "args": a, **zusatz})
    if befehl == "anker" and args and set(opt) <= {"projiziert", "seq"}:
        a = {"name": args[0], "herkunft": "projected" if "projiziert" in opt else "authored"}
        if len(args) == 3:
            x, y = _zahl(args[1]), _zahl(args[2])
            if x is None or y is None:
                return None
            a["punkt"] = [x, y]
        elif len(args) != 1:
            return None
        return ask({"cmd": "weltdom", "befehl": "anker_neu", "args": a, **zusatz})
    if befehl == "markiert" and not args and set(opt) <= {"alt", "seq"}:
        return ask({"cmd": "weltdom", "befehl": "markiert", "args": {"neu_messen": "alt" not in opt}, **zusatz})
    if befehl == "profil" and args:
        unter, rest = args[0], args[1:]
        pa = {k: opt[k] for k in ("programm", "seite", "spiel") if isinstance(opt.get(k), str)}
        if unter == "speichern" and len(rest) >= 1 and set(opt) <= {"programm", "seite", "spiel", "beschreibung"}:
            a = {"name": rest[0], **({"passt_auf": pa} if pa else {}), **({"beschreibung": opt["beschreibung"]} if isinstance(opt.get("beschreibung"), str) else {})}
            return ask({"cmd": "weltdom", "befehl": "profil_speichern", "args": a})
        if unter == "laden" and len(rest) in (1, 2) and set(opt) <= {"seq"}:
            v = _zahl(rest[1]) if len(rest) == 2 else None
            if len(rest) == 2 and v is None:
                return None
            return ask({"cmd": "weltdom", "befehl": "profil_laden", "args": {"name": rest[0], **({"version": v} if v else {})}, **zusatz})
        if unter == "liste" and not rest and set(opt) <= {"programm", "seite", "spiel", "alle"}:
            return ask({"cmd": "weltdom", "befehl": "profil_liste", "args": {**({"passt_auf": pa} if pa else {}), **({"alle": True} if "alle" in opt else {})}})
        if unter in ("weg", "zurueck") and len(rest) == 1 and not opt:
            return ask({"cmd": "weltdom", "befehl": "profil_weg", "args": {"name": rest[0], "aktiv": unter == "zurueck"}})
        return None
    if befehl == "anker-weg" and len(args) == 1 and not opt:
        return ask({"cmd": "weltdom", "befehl": "anker_weg", "args": {"knoten": args[0]}})
    return None


def main(argv: list[str]) -> int:
    if len(argv) >= 2 and argv[0] == "say":
        text = " ".join(argv[1:])
        reply = ask({"cmd": "say", "text": text})
    elif len(argv) >= 2 and argv[0] == "schreibe":
        reply = ask({"cmd": "schreibe", "text": " ".join(argv[1:])})
    elif argv == ["agenten"]:
        reply = ask({"cmd": "agenten"})
    elif argv == ["lage"]:
        reply = ask({"cmd": "lage"})
    elif len(argv) == 3 and argv[0] == "gruppe" and argv[2] in ("beitreten", "verlassen"):
        reply = ask({"cmd": "gruppe", "gruppe": argv[1], "aktion": argv[2]})
    elif len(argv) >= 3 and argv[0] == "sende":
        ziel = {"gruppe": argv[1][1:]} if argv[1].startswith("@") else {"an": argv[1]}
        reply = ask({"cmd": "nachricht", **ziel, "text": " ".join(argv[2:])})
    elif len(argv) >= 3 and argv[0] == "auftrag":
        reply = ask({"cmd": "auftrag", "an": argv[1], "text": " ".join(argv[2:])})
    elif len(argv) >= 3 and argv[0] == "auftrag-status":
        reply = ask({"cmd": "auftrag_status", "id": argv[1], "status": argv[2], "ergebnis": argv[3] if len(argv) > 3 else "", "unsicherheit": argv[4] if len(argv) > 4 else ""})
    elif argv == ["auftraege"]:
        reply = ask({"cmd": "auftraege"})
    elif len(argv) in (2, 3) and argv[0] == "kind":
        reply = ask({"cmd": "kind", "name": argv[1], **({"strom": argv[2]} if len(argv) == 3 else {})})
    elif len(argv) >= 2 and argv[0] == "chat":
        reply = ask({"cmd": "kapsel", "befehl": "chat", "text": " ".join(argv[1:])})
    elif argv and argv[0] == "test":
        reply = _test(argv[1:])
        if reply is None:
            print(__doc__, file=sys.stderr)
            return 2
    elif argv and argv[0] in ("seed", "loop"):
        reply = _seed(argv[0], argv[1:])
        if reply is None:
            print(__doc__, file=sys.stderr)
            return 2
    elif argv and argv[0] in ("kapsel", "beobachtung", "pult"):
        reply = _kapsel(argv[0], argv[1:])
        if reply is None:
            print(__doc__, file=sys.stderr)
            return 2
    elif argv and argv[0] == "ablauf":
        reply = _ablauf(argv[1:])
        if reply is None:
            print(__doc__, file=sys.stderr)
            return 2
    elif argv and argv[0] in ("weltdom", "knoten", "zeige", "anker", "anker-weg", "profil", "markiert"):
        reply = _weltdom(argv)
        if reply is None:
            print(__doc__, file=sys.stderr)
            return 2
    elif argv and argv[0] in ("lease", "klick", "ziehe", "tippe", "taste", "rad", "menue", "controller"):
        reply = _haende(argv)
        if reply is None:
            print(__doc__, file=sys.stderr)
            return 2
    elif argv == ["hoere"]:
        reply = ask({"cmd": "hoere"})
    elif argv == ["see"]:
        reply = ask({"cmd": "see"})
    elif argv in (["hilfe"], ["help"], ["--help"]):
        print(__doc__)
        return 0
    else:
        print(__doc__, file=sys.stderr)
        return 2
    print(json.dumps(reply, ensure_ascii=False))
    return 0 if reply.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
