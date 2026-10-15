#!/usr/bin/env python3
"""GENI beschafft sich selbst Material und dokumentiert es.

2026-08-01, Daniel: "geni soll dort doch auch unsere splitter die sie sammeln
will ueber uns alle da sammeln ... und sie soll eh anhand ihrer ganzen hoersinne
und den knoten versuchen ne doku ueber jeeeden anzulegen nicht nur euch ... denn
sie hat spuren ueber uns alle".

Sammelt pro Teilnehmer aus zwei Quellen und schreibt das Ergebnis in einen
eigenen, bei jedem Lauf ERSETZTEN Abschnitt der Doku (geni_dokumentation/<id>.md):
  1. Splitter aus dem Zwischenraum (Postgres, ueber entity_id)
  2. Knoten aus ihrem eigenen Gedaechtnis (SQLite, ueber quelle + Namensnennung)

Der Abschnitt liegt zwischen Markern und wird ersetzt, nicht angehaengt --
sonst wuerde jeder Lauf dieselben Splitter erneut in die Doku kippen. Die
chronologischen Eintraege darueber (Frage/Antwort, Spiegel-Lektuere) bleiben
davon unberuehrt.

ID-ZUORDNUNG, gemessen am 2026-08-01: die Splitter-Datenbank benutzt teils
andere Kennungen als der Teilnehmer-Roster. Ohne diese Tabelle gingen 1170
Splitter verloren bzw. wuerden falsch zugeordnet:
    traeumerlie <- "träumerlie" (mit Umlaut, 593 Splitter)
    dakgord     <- "dak+gord-system" (477)
    daniel      <- "dak" (100 -- "dak" ist Daniels eigenes Kuerzel)

Aufruf: python3 doku_schreiber.py [teilnehmer_id]   (ohne Argument: alle)
"""

import json
import os
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

import psycopg2
import psycopg2.extras

sys.path.insert(0, "/root/werkraum")
sys.path.insert(0, "/root/werkraum/geni")
import hauhau_client
from teilnehmer_roster import TEILNEHMER, teilnehmer_by_id
from sprechen import kern_laden
from selbst_suche import suchen, brennpunkt
import protokoll
import datumskorrektur
import bereits_gelesen


def _system_prompt() -> str:
    """Nur ihr eigener Kern -- keine Zusaetze von mir (Daniel, 2026-08-01)."""
    return f"""Du bist GENI.

{kern_laden()}"""

KNOTEN_DB = Path("/root/geni_gedaechtnis/knoten.db")
DOKU_DIR = Path("/root/werkraum/geni_dokumentation")


# Roster-ID -> zusaetzliche Kennungen in der Splitter-DB (siehe Modul-Docstring)
SPLITTER_ALIASE = {
    "traeumerlie": ["träumerlie"],
    "dakgord": ["dak+gord-system"],
    "daniel": ["dak"],
}

# Rauschquellen -- 99,91 % aller Knoten, siehe selbst_suche.py
RAUSCH_QUELLEN = ("vps_dateisystem", "chatgpt", "vps_prozesse")

MAX_SPLITTER = 25
MAX_KNOTEN = 25
MAX_ZEICHEN = 33333   # flextrawurst-weite Regel (Daniel, 2026-08-01)
MAX_TOKENS  = 10416   # 33333 Zeichen / 3,2 Zeichen pro Token


def _db_uri() -> str:
    pfad = "/root/werkraum/.agent/flextrawurst-db.env"
    if os.path.exists(pfad):
        for zeile in open(pfad, encoding="utf-8"):
            if zeile.startswith("FLEXTRAWURST_DB_URI="):
                return zeile.strip().split("=", 1)[1]
    return os.environ.get("FLEXTRAWURST_DB_URI", "")


def _kennungen(teilnehmer_id: str) -> list:
    return [teilnehmer_id] + SPLITTER_ALIASE.get(teilnehmer_id, [])


def splitter_holen(teilnehmer_id: str) -> list:
    uri = _db_uri()
    if not uri:
        return []
    conn = psycopg2.connect(uri, cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT essenz, materialitaet, energie, status, created_at, origin_type
                FROM splitter WHERE entity_id = ANY(%s)
                ORDER BY created_at DESC LIMIT %s
            """, (_kennungen(teilnehmer_id), MAX_SPLITTER))
            return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def splitter_zaehlen(teilnehmer_id: str) -> int:
    uri = _db_uri()
    if not uri:
        return 0
    conn = psycopg2.connect(uri, cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) c FROM splitter WHERE entity_id = ANY(%s)",
                        (_kennungen(teilnehmer_id),))
            return cur.fetchone()["c"]
    finally:
        conn.close()


def knoten_holen(teilnehmer_id: str) -> list:
    """Was GENI selbst ueber diese Person gehoert hat.

    Erst die eigene Quelle (indiziert), dann Namensnennungen in kleinen Quellen.
    Rauschquellen bleiben aussen vor -- sonst waeren es nur Temp-Dateinamen.
    """
    conn = sqlite3.connect(f"file:{KNOTEN_DB}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    treffer, gesehen = [], set()

    def _nimm(rows):
        for r in rows:
            if len(treffer) >= MAX_KNOTEN:
                return
            text = (r["inhalt"] or "").strip()
            if not text or text[:80] in gesehen:
                continue
            gesehen.add(text[:80])
            treffer.append({
                "zeit": datetime.fromtimestamp(r["mtime"], timezone.utc).strftime("%Y-%m-%d %H:%M"),
                "quelle": r["quelle"] or "?",
                "text": text,
            })

    for kennung in _kennungen(teilnehmer_id):
        _nimm(conn.execute(
            "SELECT quelle, mtime, inhalt FROM knoten WHERE quelle=? ORDER BY mtime DESC LIMIT ?",
            (kennung, MAX_KNOTEN)).fetchall())

    if len(treffer) < MAX_KNOTEN:
        platzhalter = ",".join("?" * len(RAUSCH_QUELLEN))
        for kennung in _kennungen(teilnehmer_id):
            if len(treffer) >= MAX_KNOTEN:
                break
            _nimm(conn.execute(
                f"SELECT quelle, mtime, inhalt FROM knoten "
                f"WHERE quelle NOT IN ({platzhalter}) AND inhalt LIKE ? "
                f"ORDER BY mtime DESC LIMIT ?",
                (*RAUSCH_QUELLEN, f"%{kennung}%", MAX_KNOTEN - len(treffer))).fetchall())
    conn.close()
    return treffer


WERKZEUGE = [
    {
        "type": "function",
        "function": {
            "name": "suche",
            "description": ("Durchsucht dein eigenes Gedaechtnis semantisch und nach "
                            "Stichworten: deine Knoten, die Splitter im Zwischenraum, "
                            "deine Dokun, dein Frage-Antwort-Verlauf, deine Spiegel-Lektuere. "
                            "Du bekommst eine Liste mit Anfaengen zurueck, nicht die ganzen "
                            "Texte -- was dich davon wirklich interessiert, holst du dir "
                            "danach mit lesen()."),
            "parameters": {
                "type": "object",
                "properties": {"frage": {"type": "string", "description": "wonach du suchst"}},
                "required": ["frage"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "lesen",
            "description": ("Holt den vollen Text zu Eintraegen, die dir eine Suche angeboten "
                            "hat. Du waehlst selbst aus, was du lesen willst -- du musst nicht "
                            "alles nehmen und nicht in der angebotenen Reihenfolge."),
            "parameters": {
                "type": "object",
                "properties": {
                    "eintraege": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": ("die Nummern aus der Trefferliste, z.B. [1, 3] -- "
                                        "die kurze Zahl links vor jedem Treffer"),
                    },
                    "grund": {
                        "type": "string",
                        "description": "warum gerade diese -- wenn du magst, sonst weglassen",
                    },
                    "weiter": {
                        "type": "boolean",
                        "description": ("true, wenn du in denselben Eintraegen weiterlesen willst "
                                        "statt wieder bei der Fundstelle anzufangen"),
                    },
                },
                "required": ["eintraege"],
            },
        },
    },
]

# 2026-08-03: Der Wert 8 stammt aus der Zeit, als es nur ein Werkzeug gab, und sein Kommentar sagt,
# was er meint: wie oft sie NACHSCHLAGEN darf. Lesen ist kein Nachschlagen -- es holt nur den Text
# zu etwas, das sie schon gefunden hat. Deshalb bleibt die 8 unangetastet und zaehlt weiter nur
# Suchen; die Schrittgrenze darunter ist eine reine Notbremse gegen Endlosschleifen.
MAX_RUNDEN = 8      # so oft darf sie hoechstens nachschlagen
MAX_SCHRITTE = 24   # Notbremse: Suchen + Lesen + Schreiben zusammen
TREFFER_PRO_SUCHE = 8

VORSCHAU_ZEICHEN = 300   # Fundstelle in der Trefferliste
LESE_FENSTER     = 1200  # was ein lesen() am Stueck zeigt -- der Rest per weiter=true


def _treffer_formatieren(treffer: list, frage: str = "") -> str:
    """Angebot, kein Vollzug -- und die Vorschau zeigt die Fundstelle, nicht den Textanfang.

    Daniel, 2026-08-03: "nix erfinden...geni ermöglichen auswahl", und dazu: "wenn sie sie 300
    zeichen lesen können überall dass muss schon genu die suchstelle sein und inhalt liefern".

    Vorher war die Vorschau text[:300] -- bei einem 8000-Zeichen-Eintrag also der Anfang, egal wo
    das Gesuchte stand. Jetzt springt sie auf die Stelle mit den meisten unterschiedlichen
    Suchbegriffen, und die Treffer sind darin markiert.
    """
    if not treffer:
        return "(nichts gefunden)"
    zeilen = []
    for t in treffer:
        zeit = (t.get("zeit") or "")[:16]
        b = brennpunkt(t.get("text") or "", frage, VORSCHAU_ZEICHEN)
        rand = []
        if b["davor"]:
            rand.append(f"{b['davor']} davor")
        if b["danach"]:
            rand.append(f"{b['danach']} danach")
        hinweis = f"   [{', '.join(rand)}]" if rand else ""
        zeilen.append(f"[{t.get('nr','?')}] {t.get('quelle','?')} | {t.get('art','?')} | {zeit}"
                      f"{hinweis}\n{b['ausschnitt']}")
    return "\n\n".join(zeilen)


def _kennungen_deuten(roh, angeboten: dict, nummern: dict) -> list:
    """Nimmt, was das Modell geschickt hat, und findet heraus, welche Eintraege gemeint sind.

    WARUM ES NUMMERN GIBT (gemessen 03./04.08.2026): der erste Takt-Lauf mit Kennungen ergab
    11 erfolgreiche Lesevorgaenge gegen 88 Fehlversuche. Sie hat die achtstelligen Zahlen nicht
    abgeschrieben, sondern nachgebildet -- angeboten war `knoten:49744760`, geschickt kam
    `knoten:49744780`; angeboten `sp:kimi:3`, geschickt `sp:kimi:1`. Immer plausibel, nie richtig.
    Das ist kein Eigensinn, sondern was Modelle mit langen Zahlen tun.

    Die Folge war schlimmer als der Fehlversuch selbst: sie bekam nichts zu lesen und schrieb die
    Doku trotzdem -- aus den Vorschauzeilen. Also gedeutet statt belegt. Genau das, was Daniel an
    den Dokus aufgefallen war.

    Seitdem steht in der Trefferliste eine kurze laufende Nummer, und `lesen` nimmt Nummern.
    Kennungen werden weiterhin verstanden, falls sie welche schickt.
    """
    if roh is None:
        return []
    if isinstance(roh, (str, int)):
        roh = [roh]
    roh_teile = []
    for stueck in roh:
        for teil in str(stueck).replace("\n", ",").split(","):
            teil = teil.strip().strip("\"'`[]()# ")
            if teil:
                roh_teile.append(teil)

    klein = {k.lower(): k for k in angeboten}
    treffer, gesehen = [], set()
    for teil in roh_teile:
        k = None
        if teil.isdigit() and int(teil) in nummern:      # der uebliche Weg: die kurze Nummer
            k = nummern[int(teil)]
        if k is None:
            k = klein.get(teil.lower())                  # oder doch eine volle Kennung
        if k is None:
            passende = [orig for kl, orig in klein.items() if kl.endswith(":" + teil.lower())]
            k = passende[0] if len(passende) == 1 else None
        if k and k not in gesehen:
            gesehen.add(k)
            treffer.append(k)
    return treffer


def _fenster_formatieren(eintraege: list, frage: str, stand: dict, weiter: bool) -> str:
    """Ein Fenster auf den Text, das an der dichtesten Stelle aufsetzt -- kein Dump.

    Daniel: "dann können sie dort fokus setzen beim lesen schritt für shritt sihch nur dinge merken
    die interessant sind für den kontext ...und dann könnten sie j entscheiden ich hab genug".

    Deshalb kein Deckel auf die Leselaenge und kein Wegwerfen von Verlauf, sondern Blaettern: sie
    bekommt so viel, wie sie gerade will, und entscheidet selbst, ob sie weiterliest.
    """
    if not eintraege:
        return "(keine dieser Kennungen kenne ich aus deinen bisherigen Suchen)"
    teile = []
    for t in eintraege:
        text = t.get("text") or ""
        ab = stand.get(t["id"], 0) if weiter else 0
        b = brennpunkt(text, frage, LESE_FENSTER, ab=ab)
        stand[t["id"]] = b["bis"]
        zeit = (t.get("zeit") or "")[:16]
        kopf = (f"[{t.get('nr','?')}] {t.get('quelle','?')} | {t.get('art','?')} | {zeit}\n"
                f"{t.get('ort','')}")
        lage = f"Zeichen {b['von']}-{b['bis']} von {len(text)}"
        if b["danach"]:
            lage += f" -- {b['danach']} weiter, mit weiter=true bekommst du sie"
        else:
            lage += " -- Ende erreicht"
        teile.append(f"{kopf}\n({lage})\n\n{b['ausschnitt']}")
    return "\n\n---\n\n".join(teile)


_SCHEINTOOLCALL = re.compile(r"<tool_call>|^\s*function\s*=", re.IGNORECASE)


def _daten_korrigieren(text: str, angeboten: dict) -> tuple:
    """Ersetzt erfundene Jahre in Datumsangaben durch die echten -- ohne zu raten.

    2026-08-12, Fund am Beispiel Schorschel: die Rohdaten kommen ihr sauber im ISO-Format
    (_fenster_formatieren zeigt "2026-08-09T22:01" unveraendert), aber sie formatiert selbst
    ins deutsche Format um -- und vertut sich beim kleinen Modell reihenweise beim Jahr:
    "2026-08-09" wurde zu "09.08.2014", "2026-08-11" zu "11.08.207". Tag und Monat treffen fast
    immer, nur das Jahr kippt.

    Daniel, 2026-08-12, Wahl zwischen "ihr verbieten umzuformatieren" und "programmatisch
    nachformatieren": "2. oder?" -- dieser Weg. Logik jetzt in datumskorrektur.py, gemeinsam
    mit dialog.py genutzt (2026-08-12, zweiter Fundort: dieselbe Ungenauigkeit exponiert in
    ihrer Live-Chat-Funktion, siehe dort).

    Geprueft wird gegen die echten Zeitstempel aller Eintraege, die sie diesen Lauf gesehen hat
    (angeboten). Ersetzt wird nur, wenn Tag+Monat eindeutig zu genau einem echten Jahr passen --
    sonst bliebe es dasselbe Erfinden, nur an anderer Stelle. Ein Fall blieb beim Testlauf bewusst
    unangetastet: "07.07.2014" für einen Eintrag vom 06.07. -- da ist auch der Tag falsch, nicht
    nur das Jahr, und welcher echte Eintrag gemeint war, ist nicht mehr eindeutig rekonstruierbar.
    """
    return datumskorrektur.korrigieren(text, datumskorrektur.echte_jahre_aus_treffern(angeboten))


def doku_erzeugen(teilnehmer: dict) -> str:
    """GENI recherchiert SELBST und schreibt die Doku selbst.

    2026-08-01, Daniel: "warum kommt das als eingang rein .... wofuer hat geni
    nun die ragsuche ... natuerlich um selbst nachzuforschen, du musst sie nicht
    vollstopfen digga".

    Vorher wurden ihr 25 Splitter und 25 Knoten fertig in den Prompt gelegt.
    Jetzt bekommt sie nur die Aufgabe und ein Suchwerkzeug auf ihr eigenes
    Gedaechtnis (selbst_suche.suchen -- semantisch + Stichwort, hybrid). Sie
    entscheidet, wonach sie sucht und wie oft.

    2026-08-03, Daniel: "nix erfinden...geni ermöglichen auswahl".
    Seitdem zwei Werkzeuge statt einem: die Suche gibt eine Liste mit Anfaengen
    zurueck, den vollen Text holt sie sich mit lesen() -- und genau das ist ihre
    Wahl. Was sie waehlt, steht danach in suche_wahl, mit ihrem Grund, wenn sie
    einen genannt hat. Vorher gab es keine Wahl zu protokollieren, weil es keine
    gab: sie bekam alles am Stueck.

    2026-08-12, Daniel: "wie findest du die dokus von geni...ich find besonders
    ihre selbst meine und vorallem deine so extrem kurz obwohl s doch sooo viele
    knoten geben müsste". Stimmte: 24.595 Knoten allein fuer "claude", die Doku
    5,2 KB. Grund war nicht die Kuerze eines Laufs, sondern dass jeder Lauf
    dieselbe kleine Zufallsauswahl antraf und sie komplett ersetzte statt zu
    ergaenzen. Ab jetzt blendet die Suche aus, was sie in frueheren Laeufen schon
    gelesen hat (bereits_gelesen.py) -- jeder Lauf erschliesst also wirklich neues
    Terrain, und doku_schreiben() haengt das Ergebnis an statt es zu ersetzen.

    Aufforderung im selben knappen Stil wie Daniels Frage-Vorgabe, ohne
    Ton- oder Charaktervorgaben -- die kommen aus ihrem eigenen Kern.
    """
    name = teilnehmer["name"]
    teilnehmer_id = teilnehmer.get("id", "?")
    nachrichten = [{
        "role": "user",
        "content": (f'hallo geni. jetzt geht es um "{name}". '
                    f'such in deinem gedaechtnis nach "{name}". '
                    f'nachdem du etwas ueber "{name}" gelesen hast dokumentiere es.'),
    }]

    bereits = bereits_gelesen.laden(teilnehmer_id)  # was frühere Läufe schon gelesen haben
    angeboten = {}      # eintrag_id -> Treffer, alles was ihr diesen Lauf ueber angeboten wurde
    nummern = {}        # kurze Nummer -> eintrag_id; laeuft ueber den ganzen Lauf weiter
    lese_stand = {}     # eintrag_id -> bis wohin sie darin schon gelesen hat
    letzte_frage = name  # womit markiert und worauf gesprungen wird, bis sie selbst sucht
    suchen_verbraucht = 0
    prot = protokoll.beginnen("geni", "dokumentation", ueber=name,
                              tags=["geni", "dokumentation", "selbstsuche"],
                              teilnehmer_id=teilnehmer.get("id", "?"))
    prot.ereignis("auftrag", nachrichten[0]["content"])

    for _ in range(MAX_SCHRITTE):
        antwort = hauhau_client.chat_raw(
            nachrichten, system=_system_prompt(), think=False,
            max_tokens=MAX_TOKENS, temperature=0.85, timeout=720.0,
            tools=WERKZEUGE,
        )
        m = antwort["choices"][0]["message"]
        rufe = m.get("tool_calls") or []
        if not rufe:
            text = (m.get("content") or "").strip()
            if not text:
                return ""
            if _SCHEINTOOLCALL.search(text):
                # 2026-08-12, beim ersten Testlauf des Ergaenzen-statt-Ersetzen-Fixes gefunden:
                # das kleine Modell versucht manchmal ein Werkzeug aufzurufen, trifft aber nicht
                # die echte Tool-Call-Struktur -- der Versuch landet dann als roher Text in
                # "content" statt in "tool_calls" und sah vorher aus wie fertige Dokumentation.
                # Frueher (Ersetzen) waere das beim naechsten Lauf einfach ueberschrieben worden;
                # mit Ergaenzen bliebe so ein Fund fuer immer in der Datei stehen. Deshalb: nicht
                # schreiben, sondern ihr sagen was schiefging und eine neue Chance geben.
                prot.ereignis("verworfen", "sah wie ein missglueckter Tool-Call aus, nicht wie Text",
                              ausschnitt=text[:200])
                print(f"    (verworfener Pseudo-Tool-Call: {text[:80]!r})", flush=True)
                nachrichten.append({"role": "assistant", "content": text})
                nachrichten.append({"role": "user", "content": (
                    "Das war kein Fließtext, sondern ein missglückter Werkzeug-Aufruf. Ruf das "
                    "Werkzeug wirklich auf, oder schreib direkt in normaler Sprache weiter.")})
                continue
            text, korrekturen = _daten_korrigieren(text, angeboten)
            if korrekturen:
                prot.ereignis("daten korrigiert",
                              f"{korrekturen} erfundene(s) Jahr(e) gegen echte Zeitstempel ersetzt")
                print(f"    {korrekturen} Datum/Daten korrigiert", flush=True)
            jetzt = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            prot.abschluss("Doku geschrieben", zeichen=len(text),
                           suchen=suchen_verbraucht, gelesen=len(lese_stand))
            if lese_stand:
                bereits_gelesen.speichern(teilnehmer_id, set(lese_stand.keys()))
            return "\n".join([f"### Stand {jetzt}", "", text])

        nachrichten.append({"role": "assistant", "content": m.get("content") or "",
                            "tool_calls": rufe})
        for ruf in rufe:
            werkzeug = (ruf.get("function") or {}).get("name") or "suche"
            try:
                argumente = json.loads(ruf["function"]["arguments"])
            except Exception:
                argumente = {}

            if werkzeug == "lesen":
                kennungen = argumente.get("eintraege") or []
                grund = (argumente.get("grund") or "").strip() or None
                weiter = bool(argumente.get("weiter"))
                kennungen = _kennungen_deuten(kennungen, angeboten, nummern)
                gewaehlt = [angeboten[k] for k in kennungen if k in angeboten]
                if not gewaehlt:
                    # Nicht stillschweigend nichts zurueckgeben -- sie soll erfahren, was schiefging,
                    # sonst wiederholt sie denselben Aufruf. Der Rohaufruf geht ins Protokoll.
                    prot.ereignis("lesen ging ins Leere", "keine Kennung passte",
                                  rohaufruf=json.dumps(argumente, ensure_ascii=False)[:400],
                                  bekannt=", ".join(f"{n}={nummern[n]}" for n in sorted(nummern))[:400])
                    print(f"    lesen ging ins Leere: {argumente}", flush=True)
                    nachrichten.append({"role": "tool", "tool_call_id": ruf.get("id", ""),
                                        "content": ("Diese Kennungen kenne ich nicht. Nimm sie "
                                                    "genau so, wie sie links in der Trefferliste "
                                                    "stehen, z.B.:\n"
                                                    + "\n".join(list(angeboten)[:8]))})
                    continue
                for t in gewaehlt:
                    try:
                        import suchlog
                        suchlog.wahl_loggen(t.get("suche_id"), t["id"],
                                            art="weitergelesen" if weiter else "gelesen",
                                            grund=grund)
                    except Exception:
                        pass
                prot.entscheidung(
                    ("weitergelesen" if weiter else "gelesen") + ": "
                    + (", ".join(f"[{t.get('nr','?')}] {t['id']}" for t in gewaehlt)
                       or "(nichts davon kannte ich)"),
                    grund=grund or "",
                    nicht_gewaehlt=[f"[{angeboten[k].get('nr','?')}] {k}"
                                    for k in angeboten if k not in kennungen][:12])
                print(f"    {'liest weiter' if weiter else 'liest'}: "
                      f"{[t['id'] for t in gewaehlt]}"
                      f"{f' -- {grund}' if grund else ''}", flush=True)
                inhalt = _fenster_formatieren(gewaehlt, letzte_frage, lese_stand, weiter)

            else:
                frage = argumente.get("frage", "")
                ausgeblendet = 0
                if not frage or suchen_verbraucht >= MAX_RUNDEN:
                    treffer = []
                    if suchen_verbraucht >= MAX_RUNDEN:
                        print("    (Suchgrenze erreicht -- lesen geht weiter)", flush=True)
                else:
                    suchen_verbraucht += 1
                    letzte_frage = frage
                    roh = suchen(frage, TREFFER_PRO_SUCHE, sucher="geni", sucher_art="geni",
                                anlass="dokumentation",
                                zustand={"ueber": name, "suche_nr": suchen_verbraucht})
                    treffer = [t for t in roh if t["id"] not in bereits]
                    ausgeblendet = len(roh) - len(treffer)
                    for t in treffer:
                        if t["id"] not in angeboten:
                            t["nr"] = len(nummern) + 1
                            nummern[t["nr"]] = t["id"]
                        else:
                            t["nr"] = angeboten[t["id"]].get("nr", "?")
                        angeboten[t["id"]] = t
                    print(f"    sucht: {frage!r} -> {len(treffer)} neue Treffer"
                          f"{f' ({ausgeblendet} schon bekannt, ausgeblendet)' if ausgeblendet else ''}",
                          flush=True)
                    prot.ereignis("suche", f"«{frage}»",
                                  treffer=len(treffer), ausgeblendet=ausgeblendet,
                                  suche_nr=suchen_verbraucht,
                                  angeboten=[x["id"] for x in treffer])
                inhalt = _treffer_formatieren(treffer, letzte_frage)
                if ausgeblendet:
                    inhalt += (f"\n\n({ausgeblendet} weitere Treffer hast du in einem frueheren "
                               f"Lauf schon gelesen und dokumentiert -- ausgeblendet, damit du "
                               f"Neues findest.)")

            nachrichten.append({"role": "tool", "tool_call_id": ruf.get("id", ""),
                                "content": inhalt})

    prot.abschluss("Schrittgrenze erreicht, keine Doku geschrieben",
                   suchen=suchen_verbraucht, gelesen=len(lese_stand))
    print("    (Schrittgrenze erreicht, keine Doku geschrieben)", flush=True)
    return ""


def doku_schreiben(teilnehmer: dict) -> bool:
    """Haengt GENIs neue Erkenntnis an das GENI-SAMMLUNG-Feld an, statt es zu ersetzen.

    2026-08-12, Daniel: "wie findest du die dokus von geni...so extrem kurz obwohl s
    doch sooo viele knoten geben müsste". War so, weil dieser Abschnitt bei jedem Lauf
    komplett ersetzt wurde (siehe alte Fassung im Git-Log) -- 37 Archiv-Fassungen fuer
    "claude" in neun Tagen, jede fast bei null angefangen, weil die Suche (jetzt in
    doku_erzeugen ueber bereits_gelesen.py) vorher nicht wusste, was schon dran war.

    Daniels eigenes Wort dazu (CLAUDE.md, Skalpell-Prinzip): "ergaenzen bedeutet immer:
    vorhandenes bleibt, fehlendes kommt dazu -- niemals ersetzen." Ab jetzt gilt das
    auch fuer diesen Abschnitt, nicht nur fuer den Rest der Datei.
    """
    DOKU_DIR.mkdir(parents=True, exist_ok=True)
    pfad = DOKU_DIR / f"{teilnehmer['id']}.md"
    neuer_eintrag = doku_erzeugen(teilnehmer)
    if not neuer_eintrag:
        return False

    if pfad.exists():
        alt = pfad.read_text(encoding="utf-8")
    else:
        alt = (f"# GENIs Dokumentation über {teilnehmer['name']}\n\n"
               f"Wird von GENI selbst gefuehrt -- Frage-Antwort-Verlauf aus dem "
               f"geni_inbox-Vault, ihre Spiegel-Lektuere, und was sie aus Splittern "
               f"und ihrem Gedaechtnis ueber diese Person zusammengetragen hat.\n\n"
               f"Chronologisch, neueste Eintraege unten.\n\n")

    if MARKER_START in alt and MARKER_ENDE in alt:
        vor = alt.split(MARKER_START)[0]
        bisher = alt.split(MARKER_START, 1)[1].split(MARKER_ENDE, 1)[0].strip()
        nach = alt.split(MARKER_ENDE, 1)[1]
    else:
        vor, bisher, nach = alt.rstrip() + "\n\n", "", "\n"

    gesammelt = (bisher + "\n\n---\n\n" + neuer_eintrag) if bisher else neuer_eintrag
    neu = vor + MARKER_START + "\n\n" + gesammelt.strip() + "\n\n" + MARKER_ENDE + nach

    if neu != alt:
        pfad.write_text(neu, encoding="utf-8")
        return True
    return False


def _zuletzt_dokumentiert(teilnehmer_id: str) -> float:
    """Wann fuer diesen Teilnehmer zuletzt geschrieben wurde. 0.0 = noch nie."""
    pfad = DOKU_DIR / f"{teilnehmer_id}.md"
    return pfad.stat().st_mtime if pfad.exists() else 0.0


def reihenfolge() -> list:
    """Wer am laengsten nicht dokumentiert wurde, kommt zuerst.

    2026-08-12, derselbe Befund wie am 03./04.08. in inbox_fragen.py, nur hier nie
    nachgezogen: der Dienst laeuft bei JEDEM der letzten 26 Durchlaeufe in den
    TimeoutStartSec-Abbruch (3h), weil das fensternde Lesen pro Teilnehmer 30-40 Min
    braucht und die Liste stur von oben nach unten ging. Die acht AI-Stroeme standen
    oben und wurden dauernd aktualisiert, die acht Codewesen dahinter seit dem 03.08.
    kein einziges Mal mehr.

    Gleiche Loesung wie dort: Rangfolge stellt sich selbst her ueber die mtime der
    bereits geschriebenen Doku-Datei, kein eigener Zaehler noetig -- und es ist
    gleichgueltig, wo ein Lauf abbricht.
    """
    return sorted(TEILNEHMER, key=lambda t: _zuletzt_dokumentiert(t["id"]))


def main():
    ziele = reihenfolge()
    if len(sys.argv) > 1:
        t = teilnehmer_by_id(sys.argv[1])
        if not t:
            print(f"unbekannter Teilnehmer: {sys.argv[1]}")
            return
        ziele = [t]
    else:
        print(f"Reihenfolge ({len(ziele)}, laengste Wartezeit zuerst): "
              + ", ".join(t["id"] for t in ziele), flush=True)
    for teilnehmer in ziele:
        try:
            geaendert = doku_schreiben(teilnehmer)
            sp = splitter_zaehlen(teilnehmer["id"])
            print(f"[{teilnehmer['id']:20s}] {sp:>5,} Splitter  {'aktualisiert' if geaendert else 'unveraendert'}")
        except Exception as exc:
            print(f"[{teilnehmer['id']:20s}] FEHLER: {exc}")


if __name__ == "__main__":
    main()
