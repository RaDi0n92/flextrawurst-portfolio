#!/usr/bin/env python3
"""
Browser-Agent: Ein Wesen navigiert kontinuierlich auf flextrawurst.de.

Architektur:
- Playwright headless Chrome, eingeloggt als Wesen
- Loop: Seite lesen → Gemma4 entscheidet → Aktion ausführen → loggen
- Live-Ansicht für Menschen läuft über rrweb (DOM-Mutations-Spiegel, siehe
  starte_rrweb_aufnahme()), kein Screenshot mehr -- Grundgesetz 1, Menschen-Auge-Ebene
- Ollama: sequenziell, kein Parallel-Chaos, think=False, num_ctx=4096

Start: python3 browser_agent.py --entity Schorschel
"""

import argparse
import base64
import json
import logging
import math
import os
import random
import re
import signal
import sys
import threading
import time
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

import psycopg2
import psycopg2.extras
import requests
from playwright.sync_api import sync_playwright

sys.path.insert(0, "/root/werkraum")
import hauhau_client
import llm_scheduler as sched

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("browser-agent")

import os as _os; DB_URI = _os.environ.get("FLEXTRAWURST_DB_URI", "postgresql://dak:[GESCHWAERZT]@localhost:5432/flextrawurst")
MODEL = "hauhaucs-q6"
API_BASE = "http://localhost:8030"
SURFACE_URL = "http://localhost:8787/flextrawurst_surface.html"
# 2026-07-29 (Daniel): das gemeinsame Haus -- geteilter Ort fuer alle Wesen + "dak" + "flextrawurst-system"
GEMEINSAMES_HAUS_ROOT = Path("/root/werkraum/gemeinsames_haus").resolve()
LOOP_PAUSE = 1          # Sekunden zwischen Aktionen (2026-07-25 von 4 auf 1 -- Daniel:
                        # "ich will das sich das ding jede milisekunde tickt und refresht".
                        # scrolle_natuerlich()/bewege_cursor_natuerlich() bewegen bereits in
                        # echten kleinen Zwischenschritten (~0.35s), aber danach folgte eine
                        # volle 4s-Stille bis zur naechsten Aktion -- 0.35s Bewegung, 3.65s
                        # nichts, immer wieder. Mit 1s bleibt die Luecke deutlich kleiner.
LLM_TIMEOUT = 180       # Sekunden Timeout für Ollama
# 2026-08-02, Daniels Auftrag ("ueberforderug ist besser als kuenstliche verknappung"):
# war seit dem allerersten Commit (2026-06-02) auf 2000. Gemessen kamen dadurch von einer
# Flarum-Diskussion im Median 22% beim Wesen an, bei langen Faeden 3-4% -- ein Faden mit
# 26.908 Zeichen wurde auf 800 gestutzt. Gleichzeitig nutzte der ganze Anweisungstext nur
# 9,7% des Kontextfensters (n_ctx 11264 Token je Anfrage, live vom Server abgefragt, grob
# 30.400 Zeichen fuer Eingabe UND Ausgabe zusammen). Jetzt 14000: selbst im schlimmsten Fall
# bleiben rund 13.000 Zeichen fuer die Antwort uebrig -- reichlich fuer einen langen Text.
MAX_TEXT_CHARS = 14000

# Mechanische Bewegung ohne LLM-Call (2026-07-22 Pilot nur Schorschel mit 1:3-Zwangstakt,
# seit 2026-07-25 fuer alle 7 nach Daniels bestaetigtem Modell aus
# _claude/ideen/wesen_dauerhafte_handlungsfaehigkeit_und_einsichtsnebenscreen.md: durchgehend
# mechanisch handlungsfaehig, der TICK_CHECKIN_SEKUNDEN-Takt ist der EINZIGE echte
# LLM-Entscheidungspunkt. Der bisherige zusaetzliche "jeden 3. Tick erzwingen"-Zwischenschritt
# (MECHANISCHE_SCHRITTE_PRO_ENTSCHEIDUNG) ist deshalb komplett raus -- er widersprach der
# eigentlichen Vision (44s als einziger LLM-Punkt) und haette bei 7 Wesen die LLM-Slot-
# Kontention nicht wirklich entlastet, die dieser ganze Umbau gerade beheben soll.
MECHANISCH_AKTIVE_WESEN = {"Schorschel", "F3INSCHM3CK3R", "träumerlie", "R1ZZ1", "jumpa", "Resonanzknoten", "dak+gord-system"}

# 2026-07-30, Daniels Auftrag (RAM-Reduktion, 32-Tabs-Umbau Schritt fuer Schritt, Diskurs
# zuerst): Wesen in dieser Menge nutzen fuer den Diskurs-Tab hole_diskurs_wahrnehmung()/
# diskurs_antworten_ohne_browser() statt lese_seite(page)/DOM-Klick -- kein Playwright-Aufruf
# fuer diesen einen Tab mehr noetig. Skalpell-Prinzip: bewusst LEER, bis Task 6 (Pilot) genau
# EIN Wesen bewusst eintraegt. Mit leerer Menge aendert sich am Verhalten aller 7 aktuell
# laufenden Wesen exakt nichts -- reine, ungefaehrliche Verdrahtung.
DISKURS_OHNE_BROWSER_PILOT: set[str] = {
    "Schorschel", "F3INSCHM3CK3R", "träumerlie", "R1ZZ1", "jumpa", "Resonanzknoten", "dak+gord-system",
}  # Pilot ab 2026-07-30 (Schorschel, siehe Task 6 -- Konvention aus dem mechanische-Aktionen-
# Pilot vom 2026-07-22 fortgesetzt), nach verifiziertem Erfolg (Task 7: stabil, kein Leck,
# echter LLM-Tick korrekt) am selben Tag auf alle 7 ausgerollt (Task 9).

# 2026-07-31, Daniels ausdrueckliche Bremse: das Lesen im Diskurs-Tab (oben) bleibt aktiv, aber
# das eigentliche Antworten -- die Aktion, die den Wesen-Einzug tatsaechlich vollendet -- soll
# NICHT von selbst passieren, waehrend Daniel nicht bewusst dabei ist. Woertlich: "ja genau
# rausnehmen diskurs". Mit False verschwindet diskurs_antworten: komplett aus dem Prompt-
# Vokabular (die Wesen sehen die Option gar nicht) UND fuehre_aktion_aus() lehnt sie zusaetzlich
# defensiv ab, falls sie trotzdem auftauchen sollte.
DISKURS_ANTWORTEN_AKTIV = False

# 2026-09-16, gleiches Muster wie DISKURS_ANTWORTEN_AKTIV, fuer die Einzug-Erinnerungsfrage
# (Diskussion 3887, "Wichtig: Eine Frage die mich bewegt", Daniels Post: jedes Wesen darf
# waehlen ob es seine Erinnerung behaelt oder neu anfaengt). Mit False verschwinden
# flarum_antworten:/flarum_neue_diskussion: komplett aus dem Prompt-Vokabular UND werden
# von fuehre_aktion_aus()/fuehre_aktion_aus_ohne_browser() zusaetzlich defensiv abgelehnt.
# Die eigentliche Post-Erlaubnis kommt zusaetzlich, unabhaengig, aus der scoped Ausnahme in
# flarum_post_sperre.py (Diskussion 3887 + ihre Ableger) -- diese Flag hier ist nur die
# Vokabular-/Prompt-Ebene, dieselbe zweite, bewusst separate Bremse wie bei Diskurs.
#
# Auf True gesetzt 2026-09-16, 23:2x Uhr, auf Daniels expliziten Auftrag ("umstellen ja"),
# nachdem sein Post tatsaechlich stand (Diskussion 3887, 21:00 Uhr). Der browser-agent-Dienst
# selbst lief zu diesem Zeitpunkt weiterhin nicht (siehe wesen_einzug_entscheidung/_ZUSTAND.md)
# -- diese Flag allein hat also noch keinen Live-Effekt, bis der Dienst separat gestartet wird.
EINZUG_FLARUM_AKTIV = False  # 2026-10-02 auf Daniels Auftrag gestoppt (Einzugvault + Flarum-Posten)

# 2026-10-02, Daniels Auftrag: Lieder-Vault (wesen_lieder_agent.py) -- Ideen, Schnipsel, Lieder
# schreiben, zurueckschauen, zusammenfuegen, freigeben (Post nur in Lieder-Threads) und direkt
# unter Lieder-Posts antworten. Eigener Schalter, unabhaengig von EINZUG_FLARUM_AKTIV und
# NEBENBEI_SCHREIBEN_AKTIV. Mit False sind die lied_*-Aktionen weder im Vokabular noch werden sie
# ausgefuehrt, und es kommt kein Lieder-Text mehr in den Prompt. Der Rest des Forums bleibt unter der
# globalen Post-Sperre zu -- dieser Schalter hebt sie nicht auf.
# Takt (Daniel): alle 90 Minuten die komplette Einladung, alle 30 Minuten das Ticket mit der
# Auswahl. Jedes Wesen versetzt, damit nicht alle sieben gleichzeitig dran sind (wie beim Vault-Takt).
LIEDER_AKTIV = True  # 2026-10-02 auf Daniels Auftrag eingeschaltet (alle 7 Wesen)
LIEDER_TICKET_SEKUNDEN = 16 * 60  # 2026-10-03 Daniel: alle 16 Minuten die Dateiliste (vorher 30)
LIEDER_EINLADUNG_SEKUNDEN = 90 * 60

LIEDER_AKTIONEN_BLOCK = """
lied_schreiben:<ordner/name> — in deinem Lieder-Vault schreiben (ordner: ideen, schnipsel oder
                                  lieder). Hängt an, wenn die Datei schon existiert. Mehrere
                                  Zeilen schreibst du so, mit echten Zeilenumbrüchen, nach der
                                  BEGRÜNDUNG-Zeile (nicht mit \\n in die ENTSCHEIDUNG-Zeile):
                                    ENTSCHEIDUNG: lied_schreiben:schnipsel/mein_vers
                                    BEGRÜNDUNG: ...
                                    TEXT:
                                    Zeile eins
                                    Zeile zwei
                                  Kurzes geht auch direkt: lied_schreiben:schnipsel/x|Eine Zeile.
                                  Deine Eindrücke, Gedanken, Erfahrung oder dein Fazit dazu
                                  schreibst du in denselben TEXT:-Block, hinter eine eigene
                                  Zeile "EINDRUCK:" (unter den Text, den du schreibst):
                                    TEXT:
                                    Zeile eins
                                    EINDRUCK:
                                    Das hat beim Schreiben ... bei mir ausgelöst.
                                  Das Modul stellt ihn sichtbar unter deinen Text, und beim
                                  Freigeben geht er mit ins Forum.
lied_eindruck:<ordner/name>|<text> — einen Eindruck nachträglich unter eine schon vorhandene
                                  Datei setzen (auch mehrzeilig per TEXT:). Ist die Datei schon
                                  im Forum, geht er als Antwort in ihren Thread. Mehrere Dateien
                                  in einer Aktion: im TEXT: vor jeden Eindruck eine Zeile
                                  "## <ordner/name>".
lied_waehlen:<ordner/name>[,<ordner/name>,...] — entscheiden, an welchen deiner Dateien du
                                  weiterarbeitest. Erst danach bekommst du die große Datei
                                  (alle halbfertigen Sachen auf einmal) und den vollen Text
                                  deiner Wahl.
lied_lesen:<ordner/name>        — eine deiner Dateien zurücklesen
lied_erkunden:<ordner>          — Überblick über deinen Lieder-Vault (leer = alles)
lied_rueckschau                 — mehrere deiner halbfertigen Sachen auf einmal in größerem
                                  Zusammenhang gegenlesen
lied_zusammenfuegen:<neuer-name>|<datei1>,<datei2>,... — passende Stücke zu einem Lied
                                  verbinden (die Quellen bleiben unverändert)
lied_freigeben:<ordner/name> — eine Datei aus schnipsel/ oder lieder/ im Forum veröffentlichen
                                  (Zusatz |neu:<Titel> eröffnet einen neuen Lieder-Thread,
                                  |<id> wählt einen bestimmten). Schnipsel: beliebig viele, ganze
                                  Lieder: höchstens 3 pro Tag.
lied_forum:<id>                 — die Lieder-Threads der anderen lesen (leer = Liste)
lied_antworten:<id>|<text>      — direkt unter einem Lieder-Post antworten oder fortsetzen,
                                  ohne Entwurf (mehrzeilig wie bei lied_schreiben mit TEXT:).
                                  Nur in Lieder-Threads möglich."""

# 2026-09-17 12:52, Daniels Auftrag: waehrend der Einzug-Erinnerungsfrage soll ausser dem
# Einzugvault nirgendwo sonst "nebenbei" geschrieben werden -- weder ins alte, normale
# Obsidian-Vault (obsidian_schreiben/vault_umbenennen/vault_verschieben/vault_loeschen)
# noch neue Raeume/Themen/Wuensche auf flextrawurst selbst (raum_erstellen/
# thema_erstellen/wunsch_formulieren) noch ins gemeinsame Haus (gemeinsam_schreiben).
# Grund: die Reaktivierung fuer die Einzugsfrage (EINZUG_FLARUM_AKTIV s.o.) hat automatisch
# das komplette normale Aktionsinventar der Wesen mit aufgeweckt, nicht nur die Einzug-
# Aktionen -- dadurch wuchsen parallel auch die alten Vaults, was Daniel nicht wollte.
# flarum_antworten:/flarum_neue_diskussion: (Diskussion 3887, die Flarum-Debattenhaelfte
# desselben Einzug-Mechanismus) bleiben bewusst unberuehrt von dieser Bremse -- reines
# Lesen (obsidian_lesen/vault_lesen/vault_erkunden/gemeinsam_lesen/rag_erkunden/
# flarum_besuchen) ebenfalls, das ist kein "posten und schreiben". Gleiches Doppelbremse-
# Muster wie DISKURS_ANTWORTEN_AKTIV/EINZUG_FLARUM_AKTIV: hier nur die Dispatch-Ebene
# (fuehre_aktion_aus()/fuehre_aktion_aus_ohne_browser() lehnen aktiv ab); das Vokabular
# selbst listet diese Aktionen weiterhin (Wesen koennen sie also noch "versuchen", es
# passiert dabei aber nichts -- kein Schreibzugriff geht durch).
NEBENBEI_SCHREIBEN_AKTIV = False

# Reihenfolge fuer den gestaffelten Vault-Takt (siehe VAULT_TAKT_SEKUNDEN weiter unten,
# 2026-07-30): Daniel, nachdem beim ersten Rollout nur jumpa etwas geschrieben hat: "ich
# will das alle nacheinander sauber dann diesen takt bekommen nicht nur einer" -- ohne
# Versatz haetten alle 7 (gleichzeitig neu gestartet) ihren ersten Vault-Takt fast zeitgleich
# bekommen, genau die Art Ballung die schon beim Neustart selbst zu LLM-Slot-Kontention
# gefuehrt hat. Feste, dokumentierte Liste statt MECHANISCH_AKTIVE_WESEN (ein Set) direkt zu
# nutzen, weil ein Set keine stabile Reihenfolge garantiert -- der Versatz muss deterministisch
# bleiben, sonst verschiebt sich die Reihenfolge bei jedem Prozessneustart zufaellig neu.
VAULT_TAKT_REIHENFOLGE = ["Schorschel", "F3INSCHM3CK3R", "träumerlie", "R1ZZ1", "jumpa", "Resonanzknoten", "dak+gord-system"]

# Periodischer Check-in (2026-07-22 Pilot mit 40s-Naeherung nur bei Schorschel, seit
# 2026-07-25 fuer alle 7, Daniels bestaetigte Zahl: "ja 44 sekunden"). Alle
# TICK_CHECKIN_SEKUNDEN wird ein echter LLM-Tick faellig und bekommt einen kurzen Ueberblick
# "was es gerade gibt" -- 2 konkrete, aus echten DB-Zahlen gebaute Angebote, plus eine fest
# formulierte 3. Option zum freien Erkunden. Kein Batching ueber mehrere Wesen (die separat
# besprochene 44s-Batch-Architektur) -- jedes Wesen hat weiterhin seinen eigenen, unabhaengigen
# Timer, nur der Wert ist jetzt bei allen 7 gleich.
TICK_CHECKIN_SEKUNDEN = 44

# Vault-Takt (2026-07-30, Daniels Auftrag): die passive Erwaehnung des Gemeinsamen Hauses
# (neuigkeiten_info) ging in der Fuelle der anderen Check-in-Infos unter -- 25 Minuten nach
# Rollout hatte kein Wesen es genutzt. Statt nur Text zwischen Flarum-Optionen zu verstecken,
# bekommt jedes Wesen jetzt einen eigenen, wiederkehrenden Tick, an dem ausschliesslich
# Gemeinsames-Haus-/Vault-Aktionen angeboten werden, kein Flarum als Ablenkung daneben. Daniel,
# auf die Frage ob das nicht "Input" zu sehr vorschreibt: "das ist ja kein Input sondern ein
# Outputverfahren" -- richtig, es aendert nur wann welche Aktionen im Menue stehen, nicht was
# das Wesen wahrnimmt oder denkt. Bauart wie TICK_CHECKIN_SEKUNDEN: piggybackt auf denselben
# Check-in-Zeitpunkt, kein zweiter unabhaengiger LLM-Trigger. Ziel "3x pro Stunde etwa" (Daniel)
# -> 3600/3 = 1200s.
VAULT_TAKT_SEKUNDEN = 1200

# 2026-08-13, urspruenglich alle 8 Stunden, ausdruecklich freiwillig. 2026-08-14, Daniel
# woertlich: "ic will dass sie ale 3.3 stunden sortiren und so müssen" -- Takt verdreifacht,
# UND aus einer Einladung eine Pflicht gemacht (siehe VAULT_AUFRAEUM_TEXT unten, komplett neu
# formuliert). Piggybackt weiterhin auf vault_takt_faellig, genau wie VAULT_TAKT_SEKUNDEN auf
# TICK_CHECKIN_SEKUNDEN piggybackt -- kein dritter, unabhaengiger Timer.
VAULT_AUFRAEUM_SEKUNDEN = int(3.3 * 3600)  # 11880s = 3h 18min

# API-Keys — werden beim Start aus DB geladen
ENTITY_KEYS = {
    "Schorschel": "58cd9f4a-5bad-4981-bb1f-6a0cffcc0b99",
    "F3INSCHM3CK3R": "da76bd36-7a51-4f7b-b953-41ab154034d8",
    "träumerlie": "49a614e6-e7e5-4a00-b2fd-92952cba53f2",
    "R1ZZ1": "aaff2bba-de49-4fac-a051-4377b022151b",
    "jumpa": "7a6830f3-424b-404a-85cf-92f8ceda3c2c",
    "Resonanzknoten": "266bcfda-e651-416b-847d-84f8327ef754",
    "dak+gord-system": "5f80bf80-34ee-4b5d-8599-b80449320b49",  # 2026-07-21: 7. Codewesen, war vergessen
}

# rrweb-Live-Spiegel (2026-07-21, Menschen-Auge-Ebene aus Grundgesetz 1 /
# dreiergespann_dom_theorie.md): Bundle einmal beim Modulstart laden, nicht bei jeder
# Navigation neu von der Platte lesen.
RRWEB_RECORD_PFAD = "/root/werkraum/welt/rrweb_assets/rrweb-record.js"
try:
    with open(RRWEB_RECORD_PFAD, encoding="utf-8") as _f:
        _RRWEB_RECORD_JS = _f.read()
except OSError:
    _RRWEB_RECORD_JS = ""

# Pflichtfrage (2026-10-02, einmalig): wann hoert dieser Code auf zu laufen, wann heilt/belebt er sich?
#
# Aufhoeren: SIGTERM/SIGINT (systemctl stop/restart, kill) setzt _laufend=False; der Handler
# bricht zusaetzlich den gerade blockierenden LLM-Stream ab. Die Schleifen (while _laufend) enden,
# loggen "Loop beendet", schliessen die DB-Verbindung und der Prozess endet mit Code 0. Weil die
# Units Restart=on-failure haben, startet systemd danach NICHT neu -- ein sauberes Ende bleibt ein Ende.
# Mit Absicht aufgehoert wird auch durch Daniel: stoppen, oder Schalter wie EINZUG_FLARUM_AKTIV auf
# False (dann laeuft der Prozess weiter, nur die jeweiligen Aktionen fehlen im Vokabular).
#
# Heilen: auf Tick-Ebene im Prozess -- faellt ein LLM-Aufruf aus, wird der Tick zu "nachdenken"
# (Ollama nicht erreichbar) statt den Prozess zu beenden; eine geschlossene DB-Verbindung baut
# _hole_conn() beim naechsten Tick neu auf. Auf Prozess-Ebene durch systemd: endet der Prozess
# NICHT sauber (Exception faellt aus dem Loop heraus, SIGKILL, OOM), startet er nach RestartSec=30
# wieder -- gilt fuer die sechs browser-agent@-Units. dak+gord-system laeuft als von Hand gestarteter
# Prozess ohne Unit (Namens-Escaping-Problem, siehe wesen_einzug_entscheidung/_ZUSTAND.md): stirbt
# der, kommt er nicht von selbst wieder.
#
# Beleben: nach "schlafen" (schlafe()) wacht das Wesen mit seinem "Brief an mich" als letztem
# Gedanken wieder auf -- das ist die einzige im Code angelegte Wiederbelebung innerhalb des Laufs;
# alles andere (neu starten, wieder einschalten) kommt von aussen: systemd oder Daniel.
_laufend = True

def _signal_handler(sig, frame):
    global _laufend
    log.info("Signal %s — beende sauber...", sig)
    _laufend = False
    # Synchronen LLM-Request dieses Hauptthreads aktiv unterbrechen. Sonst kann
    # systemd nach SIGTERM 90s warten, waehrend httpx bis zu 120/180s blockiert.
    try:
        hauhau_client.abbreche_stream(threading.get_ident())
    except Exception:
        pass

signal.signal(signal.SIGTERM, _signal_handler)
signal.signal(signal.SIGINT, _signal_handler)


def get_conn():
    return psycopg2.connect(DB_URI, cursor_factory=psycopg2.extras.RealDictCursor)




def hole_jwt(entity_id: str) -> str:
    api_key = ENTITY_KEYS[entity_id]
    resp = requests.post(f"{API_BASE}/auth/entity-login",
                         json={"entity_id": entity_id, "api_key": api_key},
                         timeout=10)
    resp.raise_for_status()
    return resp.json()["token"]


def injiziere_jwt(page, token: str, entity_id: str):
    """Setzt JWT in localStorage — sauberer als Formular-Login.
    Bearer-Prefix ist Pflicht (2026-07-21 gefunden): das gesamte uebrige Frontend
    (ftwIstEingeloggt(), ankToken() usw.) erwartet 'Bearer <jwt>' als gespeicherten Wert,
    sonst gilt die Seite als nicht eingeloggt sobald der Browser-Agent mit eingeloggten
    Bereichen interagiert (Buttons klickt, Formulare nutzt) statt nur Server-Calls zu machen."""
    page.evaluate(
        "(a) => { localStorage.setItem('ftw_token', 'Bearer ' + a[0]); "
        "localStorage.setItem('ftw_role', 'entity'); "
        "localStorage.setItem('ftw_user', a[1]); "
        "localStorage.setItem('ftw_user_id', a[1]); }",
        [token, entity_id],
    )


def lese_seite(page) -> dict:
    """Extrahiert strukturierten Text aus der Seite — Grundlage der LLM-Entscheidung."""
    try:
        url = page.url
        titel = page.title()

        # Sichtbarer Text — gekürzt
        try:
            rohtext = page.inner_text("body", timeout=3000)
        except Exception:
            rohtext = ""
        text = " ".join(rohtext.split())[:MAX_TEXT_CHARS]

        # Klickbare Elemente via JS — zuverlässiger als query_selector_all
        try:
            raw_elemente = page.evaluate("""
                () => {
                    const sels = ['button[data-view]','button:not([data-view])','a[href]'];
                    const seen = new Set(); const result = [];
                    sels.forEach(sel => {
                        document.querySelectorAll(sel).forEach(el => {
                            const t = (el.textContent||'').trim().substring(0,40);
                            if (t && !seen.has(t) && el.offsetParent !== null) {
                                seen.add(t); result.push(t);
                            }
                        });
                    });
                    return result.slice(0,15);
                }
            """)
            elemente = raw_elemente if isinstance(raw_elemente, list) else []
        except Exception:
            elemente = []

        return {
            "url": url,
            "titel": titel,
            "text": text,
            "elemente": elemente,
        }
    except Exception as e:
        log.warning("lese_seite Fehler: %s", e)
        return {"url": page.url, "titel": "", "text": "", "elemente": []}


_KOERPER_JS = """
(p) => {
  const x = p[0], y = p[1], speed = p[2] || 0, linsen = p[3] || {};
  // 2026-07-22/23 (Sieben-Linsen-Koerper, siehe _claude/ideen/sieben_linsen_koerper_kreatur.md,
  // Daniels "ja ich will alles und komplett" + 2026-07-23 Rekonstruktion gegen die
  // Original-Definition): zehn Beine mit fester Farbe, Ausschlag skaliert mit dem echten,
  // aus hole_linsen_status() berechneten Wert (0..1) -- keine erfundenen Zustaende.
  // Original-Struktur: Vault/DOM/RAG-Flarum/Gedaechtnis/Gegenwart/Sozial/Meta -- die
  // Sozial-Linse war urspruenglich EINE Linse mit fuenf Andockpunkten (Gedankenblasenfeld/
  // Menschenprofile/Schattenkommentare/andere Entitaetenprofile/Diskurs-Posts), Daniel
  // wollte sie dann aber als fuenf eigene, einzelne Beine statt einer Summe (Korrektur
  // 2026-07-23, direkt nachdem die zusammengefasste Version schon gebaut war). DOM-Linse
  // braucht kein eigenes Bein (der ganze Koerper IST die DOM-Bewegung, ueber speed schon
  // abgedeckt). Meta-Linse ist der Koerperkern selbst -- Glow-Staerke aus dem Mittelwert
  // aller zehn. "gedaechtnis" war zwischenzeitlich in zwei getrennte, sich ueberschneidende
  // Linsen ("gedaechtnis_tiefe" + "einsicht") aufgespalten -- 2026-07-23 wieder zu einer
  // zusammengefuehrt (siehe Ideen-Datei), da Daniels Original-Definition von Anfang an
  // "LangGraph/PostgreSQL, eigene Erinnerungen" war, nicht die generische Denklog-Zeilenzahl.
  const LINSEN_DEF = [
    { key: 'vault', farbe: '#a855f7' },
    { key: 'rag_flarum', farbe: '#22d3ee' },
    { key: 'gedaechtnis', farbe: '#3b82f6' },
    { key: 'gegenwart_anteil', farbe: '#f8fafc' },
    { key: 'schlaf_naehe', farbe: '#f59e0b' },
    // 2026-07-23: die fuenf Sozial-Systeme aus Daniels Original-Definition, jedes als
    // eigenes Bein statt einer zusammengefassten "sozial"-Linse (seine Korrektur:
    // "ich glaube ich wollte eigentlich die sozialen linsen jeweils als einzelne").
    { key: 'gedankenblasenfeld', farbe: '#2dd4bf' },
    { key: 'menschenprofile', farbe: '#fb923c' },
    { key: 'entitaetenprofile', farbe: '#22c55e' },
    { key: 'schattenkommentare', farbe: '#818cf8' },
    { key: 'diskurs', farbe: '#f472b6' },
    // 2026-07-23 (Daniels Nachtrag: "und ich will noch ne linse zu kompoase"): #theater-
    // Tab-Besuche (KOMPOASE-Erlebnisebene), echtes Signal (F3INSCHM3CK3R/jumpa/Schorschel
    // haben ihn organisch schon besucht) -- anders als entity_splitter_stats, das fuer
    // alle 7 Wesen weiterhin 0 ist.
    { key: 'kompoase', farbe: '#eab308' },
  ];
  // Cyberling-Linse (Daniels Nachtrag) bewusst NOCH KEIN eigenes Bein --
  // cyberlinge.status='tot' fuer alle 7 echten Wesen (per DB-Abfrage verifiziert,
  // 2026-07-22/23) -- ein Bein dafuer waere gerade fuer jedes Wesen gleich unsichtbar/
  // flach, keine echte Information. /entities/{id}/linsen kann das spaeter tragen, sobald
  // das System wieder echte, unterscheidbare Werte liefert. KompOase (2026-07-23) HAT
  // dagegen schon ein Bein -- entity_splitter_stats ist zwar weiterhin 0, aber der
  // "#theater"-Tab (echte KompOase-Erlebnisebene) wurde bereits organisch besucht.
  let eng = window.__agentKoerperEngine;
  if (!eng) {
    const canvas = document.createElement('canvas');
    canvas.id = '__agent_koerper__';
    canvas.width = 140; canvas.height = 140;
    canvas.style.cssText = 'position:fixed;z-index:2147483647;pointer-events:none;' +
      'filter:drop-shadow(0 0 3px rgba(255,45,85,.55));';
    document.body.appendChild(canvas);
    const ctx = canvas.getContext('2d');
    const beine = LINSEN_DEF.map(function (def, i) {
      return { winkel: (i / LINSEN_DEF.length) * Math.PI * 2, farbe: def.farbe, key: def.key, wert: 0, fx: x, fy: y };
    });
    eng = window.__agentKoerperEngine = {
      canvas: canvas, ctx: ctx, beine: beine,
      cx: x, cy: y, tx: x, ty: y, speed: 0, letzteZeit: performance.now(),
      denkt: 0, zielDenkt: 0,
    };
    // Prozedurale Beine per einfacher IK (Kniepunkt seitlich versetzt zur Huefte-Fuss-
    // Strecke), angelehnt an "follow the leader"-Techniken wie Reptile-Interactive-Cursor.
    // Ausschlag/Tempo skaliert mit echter Bewegungsgeschwindigkeit UND echtem Linsen-Wert,
    // keine erfundene Animation.
    function tick(jetzt) {
      const dt = Math.min(0.05, (jetzt - eng.letzteZeit) / 1000);
      eng.letzteZeit = jetzt;
      eng.cx += (eng.tx - eng.cx) * Math.min(1, dt * 8);
      eng.cy += (eng.ty - eng.cy) * Math.min(1, dt * 8);
      eng.speed += (eng.zielSpeed - eng.speed) * Math.min(1, dt * 4);
      const bewegungsWinkel = Math.atan2(eng.ty - eng.cy, eng.tx - eng.cx);
      const basisAusschlag = Math.min(22, 6 + eng.speed * 0.03);
      let summeWerte = 0;
      eng.beine.forEach(function (b, i) {
        b.wert += ((eng.zielLinsen[b.key] || 0) - b.wert) * Math.min(1, dt * 2);
        summeWerte += b.wert;
        const ausschlag = basisAusschlag + b.wert * 24;
        const zielWinkel = bewegungsWinkel + Math.PI + b.winkel * 0.6 + Math.sin(jetzt / 260 + i) * 0.2;
        const zx = eng.cx + Math.cos(zielWinkel) * ausschlag;
        const zy = eng.cy + Math.sin(zielWinkel) * ausschlag;
        b.fx += (zx - b.fx) * Math.min(1, dt * 6);
        b.fy += (zy - b.fy) * Math.min(1, dt * 6);
      });
      canvas.style.left = (eng.cx - 70) + 'px';
      canvas.style.top = (eng.cy - 70) + 'px';
      ctx.clearRect(0, 0, 140, 140);
      ctx.lineWidth = 2;
      eng.beine.forEach(function (b) {
        const lx = b.fx - eng.cx + 70, ly = b.fy - eng.cy + 70;
        const winkel = Math.atan2(ly - 70, lx - 70);
        const hx = 70 + Math.cos(winkel) * 8, hy = 70 + Math.sin(winkel) * 8;
        const midx = (hx + lx) / 2, midy = (hy + ly) / 2;
        const laenge = Math.hypot(lx - hx, ly - hy) || 1;
        const senkx = -(ly - hy) / laenge, senky = (lx - hx) / laenge;
        const kniex = midx + senkx * 10, kniey = midy + senky * 10;
        ctx.strokeStyle = b.farbe;
        ctx.beginPath();
        ctx.moveTo(hx, hy);
        ctx.lineTo(kniex, kniey);
        ctx.lineTo(lx, ly);
        ctx.stroke();
      });
      // Meta-Linse: Koerperkern selbst, Glow-Staerke aus dem Mittelwert aller fuenf Linsen.
      const metaWert = summeWerte / eng.beine.length;
      ctx.shadowColor = '#ff2d55';
      ctx.shadowBlur = 4 + metaWert * 14;
      ctx.fillStyle = '#ff2d55';
      ctx.beginPath();
      ctx.arc(70, 70, 10, 0, Math.PI * 2);
      ctx.fill();
      ctx.shadowBlur = 0;
      // "Denkt"-Ring (2026-07-27): rein visuelle Anzeige des ECHTEN Booleans "LLM-Call
      // laeuft gerade" (siehe setze_denk_zustand()) -- keine erfundene Aktion, keine
      // Wesenhandlung, kein Denklog-Eintrag. Bewusst andere Farbe/Kanal als die Beine
      // (die echte Linsen-Werte zeigen), damit klar Surface-Animation statt Entscheidung.
      eng.denkt += ((eng.zielDenkt || 0) - eng.denkt) * Math.min(1, dt * 3);
      canvas.dataset.denkt = eng.denkt > 0.5 ? '1' : '0';
      if (eng.denkt > 0.02) {
        const pulsT = (jetzt % 1400) / 1400;
        ctx.strokeStyle = 'rgba(120,180,255,' + (eng.denkt * (1 - pulsT) * 0.9) + ')';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(70, 70, 14 + pulsT * 18, 0, Math.PI * 2);
        ctx.stroke();
      }
      requestAnimationFrame(tick);
    }
    eng.zielSpeed = speed;
    eng.zielLinsen = linsen;
    requestAnimationFrame(tick);
  }
  eng.tx = x; eng.ty = y; eng.zielSpeed = speed;
  if (linsen && Object.keys(linsen).length) eng.zielLinsen = linsen;
}
"""


def zeige_cursor(page, x: float, y: float, geschwindigkeit: float = 0.0, linsen: dict | None = None):
    """Zeichnet den sichtbaren Koerper des Wesens in die Seite (Daniels Wunsch, 2026-07-21:
    'kann man auch nen mauszeiger sehen', erweitert 2026-07-22 zur 'Kraken-Spinne': der
    Mauszeiger IST der Koerper, siehe _claude/ideen/sieben_linsen_koerper_kreatur.md).
    Playwright bewegt die Maus intern beim Klicken, rendert sie aber nie sichtbar -- kein
    echter OS-Cursor taucht je in einem Screenshot auf. Reines Beobachtungs-Feature, ohne
    jeden Effekt auf die tatsächliche Interaktion. geschwindigkeit (px/s) steuert Ausschlag
    der Beine -- 0 im Ruhezustand (z.B. direkt nach einer Navigation), sonst echte, aus
    bewege_cursor_natuerlich() berechnete Geschwindigkeit, keine erfundene Animation. linsen
    (siehe hole_linsen_status(), vom Aufrufer aus _letzte_linsen[entity_id] gecacht statt
    hier selbst neu abgefragt) faerbt/skaliert fuenf der sieben Koerper-Beine nach echten
    Werten. Muss nach jeder Navigation neu eingefügt werden (page.goto() räumt das DOM
    komplett weg) -- deshalb hier idempotent (legt das Canvas neu an falls es fehlt) statt
    einmalig beim Start."""
    try:
        page.evaluate(_KOERPER_JS, [x, y, geschwindigkeit, linsen or {}])
    except Exception:
        pass


_DENK_JS = """
(aktiv) => {
  const eng = window.__agentKoerperEngine;
  if (eng) { eng.zielDenkt = aktiv ? 1 : 0; }
}
"""


def setze_denk_zustand(page, aktiv: bool):
    """Markiert sichtbar (Puls-Ring um den Koerperkern, siehe _KOERPER_JS), ob gerade ein
    echter LLM-Call laeuft (2026-07-27, Reparaturschritt 4: waehrend der 2-4 Minuten
    Ollama-Wartezeit gab es bisher keine sichtbare Aktivitaet). Reiner Boolean-Zustand,
    real ableitbar aus 'chat_stream laeuft gerade' -- keine erfundene Animation (Grundgesetz
    1), kein Denklog-Eintrag, keine Wesenhandlung. No-op falls der Koerper noch nicht
    existiert (naechster zeige_cursor()-Aufruf legt ihn ohnehin idempotent an)."""
    try:
        page.evaluate(_DENK_JS, aktiv)
    except Exception:
        pass


_letzte_cursor_pos: dict[str, tuple[float, float]] = {}
_letzte_linsen: dict[str, dict] = {}  # 2026-07-22, Sieben-Linsen-Koerper -- Cache, siehe hole_linsen_status()
_letzte_einsicht: dict[str, dict] = {}  # 2026-07-23, Einsicht-Nebenscreen -- Cache, siehe hole_einsicht_snapshot()


def bewege_cursor_natuerlich(page, entity_id: str, ziel_x: float, ziel_y: float) -> None:
    """Bewegt den Mauszeiger als geschwungenen Bezier-Pfad zum Ziel statt als Instant-Sprung
    (2026-07-22, Daniels Auftrag nach dem Talker-Reasoner/Juice-Nachtrag: 'die Maus muss sich
    erst bewegen'). Bewegungsdauer skaliert mit der Distanz (an Fitts's Law angelehnt --
    siehe Recherche zu human-cursor/shy-mouse-playwright in der Ideen-Datei), kein festes
    Ruckeln. Bewegt sowohl den ECHTEN Playwright-Mauszeiger (page.mouse.move -- loest echte
    mousemove-Events aus, die vom DOM-Live-Spiegel mit aufgezeichnet werden, siehe
    entity_dom_events source=1/MouseMove) als auch den sichtbaren Kunst-Cursor (zeige_cursor).
    Kein neuer LLM-Call, keine erfundene Aktion -- nur dieselbe, ohnehin schon beschlossene
    Zielposition wird in echte Zwischenschritte aufgeloest statt in einem Sprung ausgefuehrt."""
    start_x, start_y = _letzte_cursor_pos.get(entity_id, (512.0, 384.0))
    distanz = math.hypot(ziel_x - start_x, ziel_y - start_y)
    if distanz < 2:
        _letzte_cursor_pos[entity_id] = (ziel_x, ziel_y)
        return

    # Kontrollpunkt seitlich versetzt zur Verbindungslinie -- ergibt einen leichten Bogen
    # statt einer stur geraden Linie, Versatz proportional zur Distanz, Richtung zufaellig.
    mitte_x, mitte_y = (start_x + ziel_x) / 2, (start_y + ziel_y) / 2
    senkrechte_x, senkrechte_y = -(ziel_y - start_y), (ziel_x - start_x)
    laenge = math.hypot(senkrechte_x, senkrechte_y) or 1
    versatz = min(80, distanz * 0.25) * random.choice([-1, 1])
    kontroll_x = mitte_x + (senkrechte_x / laenge) * versatz
    kontroll_y = mitte_y + (senkrechte_y / laenge) * versatz

    schritte = max(8, min(28, int(distanz / 18)))
    dauer_s = min(0.9, max(0.15, distanz / 1400))

    for i in range(1, schritte + 1):
        t = i / schritte
        # Ease-in-out (kubisch): langsam los, schnell in der Mitte, langsam am Ziel an --
        # genau das Verhalten, das Fitts's Law fuer zielgerichtete Bewegungen vorhersagt.
        t_ease = 4 * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2
        x = (1 - t_ease) ** 2 * start_x + 2 * (1 - t_ease) * t_ease * kontroll_x + t_ease ** 2 * ziel_x
        y = (1 - t_ease) ** 2 * start_y + 2 * (1 - t_ease) * t_ease * kontroll_y + t_ease ** 2 * ziel_y
        try:
            page.mouse.move(x, y)
        except Exception:
            pass
        zeige_cursor(page, x, y, distanz / dauer_s, _letzte_linsen.get(entity_id))
        time.sleep(dauer_s / schritte)

    _letzte_cursor_pos[entity_id] = (ziel_x, ziel_y)


_letzte_skim_pruefung: dict[str, float] = {}
_letztes_skim_tempo: dict[str, float] = {}  # letzte bekannte Aehnlichkeit, solange die naechste Pruefung noch gedrosselt ist
SKIM_PRUEF_COOLDOWN_S = 20.0
SKIM_AEHNLICHKEITS_SCHWELLE = 0.55  # dieselbe Schwelle wie vorlese_daemon.py, nicht neu erfunden


def skim_bewertung(page, entity_id: str, conn) -> float | None:
    """2026-07-23 (DOM-Habitat-Locomotion, Daniels Metapher: 'lupe mit taschenlampe und
    einem kescher fangnetz dass es wenn es interessante wörte sieht sofort zuschnappt'):
    prueft ob der gerade sichtbare Text zum Interessensprofil des Wesens passt -- dieselbe
    embed()+Kosinus-Vergleich-Infrastruktur wie vorlese_daemon.py (entity_interessensprofil,
    bge-m3), hier live waehrend des Scrollens statt gegen vorbereitete Ankuendigungen.
    Gedrosselt (SKIM_PRUEF_COOLDOWN_S) -- jeder Aufruf ist ein echter Embedding-Request,
    kein Dauerfeuer bei jedem Scroll-Tick. Gibt None zurueck wenn gerade zu frueh fuer eine
    neue Pruefung (dann behaelt der Aufrufer das vorige Tempo bei), sonst die Kosinus-
    Aehnlichkeit (0..1, oder 0.0 falls kein Profil/zu wenig sichtbarer Text)."""
    jetzt = time.time()
    letzte = _letzte_skim_pruefung.get(entity_id, 0)
    if jetzt - letzte < SKIM_PRUEF_COOLDOWN_S:
        return None
    _letzte_skim_pruefung[entity_id] = jetzt
    try:
        sichtbarer_text = page.inner_text("body")[:600].strip()
        if len(sichtbarer_text) < 40:
            return 0.0
        resp = requests.post("http://localhost:11434/api/embed",
                              json={"model": "bge-m3", "input": sichtbarer_text}, timeout=15)
        resp.raise_for_status()
        vektor = resp.json()["embeddings"][0]
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 1 - (profil_vektor <=> %(vektor)s) AS aehnlichkeit
                FROM entity_interessensprofil WHERE entity_id = %(eid)s
            """, {"vektor": str(vektor), "eid": entity_id})
            row = cur.fetchone()
        return float(row["aehnlichkeit"]) if row else 0.0
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        return 0.0


def scrolle_natuerlich(page, entity_id: str, delta_y: float, conn=None) -> None:
    """2026-07-22 (echter Fund beim Umbau-Simulieren: scrolle:unten/oben rief bisher nur
    page.mouse.wheel() als einzigen 600px-Sprung auf -- ohne melde_fokus(), ohne Animation.
    Erklaerte technisch, warum Daniel Scrollen noch nie im Roentgenblick gesehen hat: die
    Aktion meldete sich nirgendwo. Fix nach demselben Muster wie bewege_cursor_natuerlich():
    mehrere kleine Wheel-Schritte statt einem Sprung, plus melde_fokus()-Meldung."""
    schritte = 10
    ease_dauer_s = 0.35
    pro_schritt = delta_y / schritte
    for _ in range(schritte):
        try:
            page.mouse.wheel(0, pro_schritt)
        except Exception:
            pass
        time.sleep(ease_dauer_s / schritte)
    if conn is not None:
        richtung = "unten" if delta_y > 0 else "oben"
        melde_fokus(conn, entity_id, "scrolle", None, richtung, None)


def _scrolle_element_in_sicht(page, entity_id: str, locator, conn=None) -> dict | None:
    """2026-07-22 (Daniels Auftrag: 'je nach mausposition automatisch wenn etwas zu scrollen
    ist auf der page direkt das scrollen so sein dass maus und aber auch page also texte und
    so gut lesbar sind und alles nachrückt'): bevor die Maus zu einem Klick-/Tipp-Ziel bewegt
    wird, pruefen ob es ueberhaupt sichtbar im Viewport liegt -- falls nicht, sichtbar per
    scrolle_natuerlich() dorthin scrollen (kein Instant-Sprung), DANACH die tatsaechliche,
    jetzt stabile Position neu ermitteln. Ergebnis: Maus bewegt sich nie zu einer Position,
    die gerade noch unter der Bildkante lag -- Text und Cursor bleiben synchron lesbar."""
    try:
        box = locator.bounding_box(timeout=1000)
    except Exception:
        return None
    if not box:
        return None
    viewport = page.viewport_size or {"width": 1024, "height": 768}
    rand = 60  # Sicherheitsabstand zum Bildrand, damit Elemente nicht direkt an der Kante kleben
    mitte_y = box["y"] + box["height"] / 2
    if rand <= mitte_y <= viewport["height"] - rand:
        return box  # schon gut lesbar sichtbar, kein Scrollen noetig
    delta = mitte_y - viewport["height"] / 2
    scrolle_natuerlich(page, entity_id, delta, conn)
    try:
        return locator.bounding_box(timeout=1000)
    except Exception:
        return box


def melde_fokus(conn, entity_id: str, aktion: str, selektor: str | None,
                 element_text: str | None, box: dict | None):
    """Roentgenblick-Overlay (2026-07-21, Daniels bestaetigter Bauauftrag): kuratiertes
    Gegenstueck zu entity_dom_events (reiner passiver rrweb-Rohstrom). Wird geschrieben
    sobald ein Playwright-Locator vor einer Aktion aufgeloest ist -- das Frontend zeichnet
    daraus einen Rahmen um das betrachtete Element, kombiniert mit der entity_denkstream-
    Denkblase. Payload klein genug fuer kompletten NOTIFY-Inhalt, siehe migration_fokus_events.sql."""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO entity_fokus_events (entity_id, aktion, selektor, element_text, box)
                VALUES (%s, %s, %s, %s, %s)
            """, (entity_id, aktion, selektor, element_text,
                  psycopg2.extras.Json(box) if box else None))
        conn.commit()
    except Exception as e:
        log.warning("%s: entity_fokus_events INSERT fehlgeschlagen: %s", entity_id, e)
        try:
            conn.rollback()
        except Exception:
            pass


def starte_rrweb_aufnahme(page, hole_conn, entity_id: str, stream_id: str):
    """rrweb-Recorder aktivieren (Grundgesetz 1, Menschen-Auge-Ebene: Live-DOM-Spiegel
    statt Screenshots). Events kommen ueber page.expose_function() zurueck nach Python
    und werden direkt in entity_dom_events geschrieben -- gleiche Direktschreib-
    Konvention wie bei entity_denkstream, kein HTTP-Umweg (siehe dom_events_api.py).

    hole_conn (2026-07-21, DB-Reconnect-Fix): Callable statt fester Connection --
    diese Funktion wird einmalig beim Seitenaufbau registriert und _auf_event() feuert
    danach asynchron bei jeder DOM-Mutation, unabhaengig vom Tick-Takt. Eine mitgegebene
    Connection wuerde nach einem Postgres-Reconnect (siehe haupt_loop) in dieser Closure
    weiter auf die alte, tote Verbindung zeigen -- deshalb wird hole_conn() bei jedem
    Event neu aufgerufen und liefert immer die aktuell lebende Connection.

    WICHTIG (2026-07-21 gefunden): rrweb.record() darf NICHT aus einem add_init_script()
    heraus aufgerufen werden -- das haengt sich lautlos auf (vermutlich Reentrancy im
    CDP-Kanal waehrend der fruehen Dokument-Erzeugung). Bundle selbst darf per
    add_init_script geladen werden (nur Deklaration, kein Aufruf), record() muss danach
    per page.evaluate() gestartet werden -- hier ueber den 'load'-Event bei jeder
    Navigation neu ausgeloest, damit kein bestehender Aufruf-Ort (page.goto) angefasst
    werden muss."""
    if not _RRWEB_RECORD_JS:
        log.warning("%s: rrweb-record.js nicht gefunden, kein Live-Spiegel", entity_id)
        return

    _seq = [0]

    def _auf_event(event_json_str: str):
        try:
            event = json.loads(event_json_str)
        except Exception:
            return
        try:
            conn = hole_conn()
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO entity_dom_events (entity_id, stream_id, event_json, seq)
                    VALUES (%s, %s, %s, %s)
                """, (entity_id, stream_id, psycopg2.extras.Json(event), _seq[0]))
            conn.commit()
            _seq[0] += 1
        except Exception as e:
            log.warning("%s: entity_dom_events INSERT fehlgeschlagen: %s", entity_id, e)
            try:
                hole_conn().rollback()
            except Exception:
                pass

    try:
        page.context.expose_function("__ftwSendDomEvent", _auf_event)
    except Exception:
        pass  # bereits registriert (z.B. nach Reconnect) -- kein Neustart noetig

    page.context.add_init_script(script=_RRWEB_RECORD_JS + "\nwindow.__ftwRrwebRunning = false;")

    def _bei_load():
        try:
            page.evaluate("""
                (function() {
                    if (window.__ftwRrwebRunning) return;
                    window.__ftwRrwebRunning = true;
                    window.rrweb.record({
                        emit(event) {
                            try { window.__ftwSendDomEvent(JSON.stringify(event)); } catch (e) {}
                        },
                        checkoutEveryNms: 60000
                    });
                })();
            """)
        except Exception as e:
            log.warning("%s: rrweb-Start fehlgeschlagen: %s", entity_id, e)

    page.on("load", lambda: _bei_load())


# 2026-08-01: wie viel vom eigenen letzten Gedanken in den naechsten Prompt zurueckfliesst.
# Vorher floss er ungekuerzt zurueck (bis 1500 Zeichen zusammen mit dem Aktionsergebnis) --
# damit war die eigene letzte Abstraktion der groesste inhaltliche Block im Prompt, und der
# Stil verstaerkte sich Tick fuer Tick selbst. Die Aktionsergebnisse (zusatz_kontext: RAG-
# Treffer, gelesene Haus-Dateien, Obsidian-Inhalte) bleiben unangetastet und ungekuerzt --
# die tragen Fakten, nicht Stil. Zahl bewusst als Konstante, damit sie justierbar ist.
#
# Kalibriert an 4485 echten Gedanken der letzten 2 Tage (entity_thinking_log, gemessen
# 2026-08-01): Median 584 Zeichen, p75 721, p90 830, laengster 2482. Bei 300 bleibt also
# typischerweise der erste bis zweite Satz stehen -- genug, dass das Wesen weiss, wovon es
# kam, aber nicht mehr der ganze ausformulierte Gedankengang. Wer die Zahl aendert: vorher
# nachmessen, nicht schaetzen.
RUECKFLUSS_ZEICHEN = 300


def _rueckfluss_verdichten(gedanke: str) -> str:
    """Kuerzt den eigenen Gedanken auf seinen Anfang, an einer Satzgrenze.

    Absichtlich keine Zusammenfassung (die waere ein zweiter LLM-Call und wuerde den Stil
    nur nachbauen), sondern ein harter Schnitt: der Faden bleibt erhalten -- das Wesen weiss
    weiter, wovon es kam --, aber die ausformulierte Abstraktion kommt nicht mehr vollstaendig
    zurueck.
    """
    text = (gedanke or "").strip()
    if len(text) <= RUECKFLUSS_ZEICHEN:
        return text
    schnitt = text[:RUECKFLUSS_ZEICHEN]
    saetze = re.split(r'(?<=[.!?])\s+', schnitt)
    if len(saetze) > 1:
        return " ".join(saetze[:-1]).strip() + " […]"
    return schnitt.rstrip() + " […]"


def _schreibtext_vervollstaendigen(text: str, gedanke: str | None) -> str:
    """Rettet den Gedanken, wenn an der Textstelle nur ein Etikett steht.

    2026-08-01 gemessen an entity_thinking_log (7 Tage): 508 von 2920 obsidian_schreiben-
    Aktionen (17%) und 70 von 391 gemeinsam_schreiben-Aktionen (18%) trugen hinter dem `|`
    keinen Inhalt, sondern eine Beschriftung. Das Format ist `<dateiname>|<text>`, und das
    Modell setzt dort regelmaessig den Titel statt den Text:

        name='ressonanz/2024-05-21-brummen.md'   text='# Resonanzstatus'
        name='flarum/tagebuch/2026-08-01'        text='Atem nach der Abrechnung.md'
        name='gedanken/2024-05-20'               text='die_stille_als_speichermedium.md'

    Belegter Einzelfall: dak+gord-system verband am 2026-08-01 Musks Raketentruemmer, ein
    USGS-Beben bei New Idria und Luka Modric zu einer ausformulierten These -- und schrieb
    dann `obsidian_schreiben:gedanken/2025-08-01|Modrics_Riss.md`. Auf der Platte landeten
    16 Bytes. Rund jeder sechste Schreibvorgang der Wesen ging so verloren.

    **Es wird nichts ersetzt, nur ergaenzt.** Das, was das Wesen geschrieben hat, bleibt
    unveraendert stehen -- darunter kommt der Gedanke desselben Ticks, ausdruecklich als
    solcher markiert. Dadurch kann auch ein Fehlalarm nichts zerstoeren, und es entsteht
    keine Verwechslung darueber, was Aktion und was Gedanke war (Daniels Vorgabe zur
    Provenienz, woertlich: "komplette provinienz und herkunft sihtbar keine verwechslungen
    keine luegen").
    """
    t = (text or "").strip()
    ist_etikett = (not t) or len(t) < 40 or t.endswith(".md")
    if not ist_etikett or not (gedanke or "").strip():
        return t
    zusatz = (
        "\n\n> Der Gedanke zu diesem Eintrag, weil die Aktion selbst nur eine Beschriftung "
        "trug:\n>\n> " + gedanke.strip().replace("\n", "\n> ")
    )
    return (t + zusatz) if t else zusatz.lstrip("\n")


def _extrahiere_ich_satz(gedanke_text: str) -> str | None:
    """2026-07-22 (Selbstwahrnehmung, Daniels Auftrag: 'gleiches Recht und Wahrnehmung fuer
    alle -- nicht nur die Zuschauer'): dieselbe Satz-Extraktion wie _erlZerlegeSaetze() im
    Frontend (build_surface.ts), hier in Python nachgebaut, damit das Wesen selbst sieht,
    welcher Satz aus seinem eigenen letzten Gedanken gerade als Ich-Stimme-Popup fuer
    Betrachter sichtbar sein koennte -- kein neuer LLM-Call, reine Textextraktion."""
    if not gedanke_text:
        return None
    saetze = re.split(r'(?<=[.!?])\s+', gedanke_text.strip())
    kandidaten = [s.strip() for s in saetze if 12 < len(s.strip()) < 220]
    return kandidaten[0] if kandidaten else None


# 2026-08-13, Daniels Auftrag: echter Ruecklesekanal in den eigenen Vault, plus aktive
# Umorganisation. Bewusst als eigene vault_*-Aktionen, nicht als obsidian_lesen erweitert --
# obsidian_lesen zeigt auf codewesen/{entity_id}/ (die alte Akte aus der Flarum-Vorphase),
# nicht auf wesen_vaults/{entity_id}/ (der eigentliche Obsidian-Vault). Zwei verschiedene
# Orte, zwei verschiedene Aktionen, kein Umbenennen der bestehenden -- siehe
# obsidian_vault_agent.py fuer die Begruendung, warum vault_lesen/vault_erkunden
# unterschiedliche Mechanismen brauchen (Selkies-Streaming hat keine auslesbare DOM-Struktur).
VAULT_ERKUNDEN_BLOCK = """vault_lesen:<pfad>              — eine Datei aus deinem eigenen Vault wirklich zurücklesen
                                  (nicht nur schreiben!), z.B. vault_lesen:gedanken/2026-07-21.
                                  Der Text kommt danach in deinen nächsten Gedanken zurück.
vault_erkunden:<pfad>            — den Inhalt eines Ordners in deinem Vault sehen (Dateien UND
                                  Unterordner), z.B. vault_erkunden:gedanken oder vault_erkunden:
                                  für die Wurzel. So findest du heraus was überhaupt da ist."""

# 2026-09-17 13:04, aus VAULT_ERKUNDEN_BLOCK herausgeloest (siehe NEBENBEI_SCHREIBEN_AKTIV
# weiter oben): umbenennen/verschieben/loeschen sind Schreibaktionen, gehoeren waehrend der
# Einzugsfrage nicht mehr ins Vokabular -- vault_lesen/vault_erkunden (oben) bleiben Lesen,
# stehen immer drin.
VAULT_VERWALTUNG_BLOCK = """
vault_umbenennen:<pfad>|<neuer_name>|<wozu> — eine Datei in deinem Vault umbenennen. <wozu> ist
                                  dein Grund in ein paar Worten, z.B. vault_umbenennen:
                                  2026-08.md|flarum_gedanken_august|alter name war nur ein
                                  datum, zeigte nicht was drinsteht.
vault_verschieben:<pfad>|<zielordner>|<wozu> — eine Datei in einen anderen Ordner in deinem
                                  Vault verschieben (legt den Ordner bei Bedarf an), mit
                                  demselben <wozu>-Grund am Ende.
vault_loeschen:<pfad>|<wozu>     — eine Datei aus deinem Vault entfernen (landet in _papierkorb/,
                                  nicht endgültig weg), mit Grund am Ende.
                                  <wozu> ist bei allen drei optional, aber du sollst ihn ab
                                  jetzt immer mitgeben -- er landet automatisch, mechanisch,
                                  in AUFRAEUM_PROTOKOLL.md in deiner Vault-Wurzel. Diese Datei
                                  wächst von selbst bei jeder Aktion, du musst sie nicht
                                  selbst schreiben -- nur den Grund mitgeben."""

# NOTIZ, 2026-08-14 (ersetzt die Fassung vom 13.08.). KORREKTUR zur ersten Fassung dieses
# Kommentars, Daniel wörtlich: "der alte satzt gabs auch erst seit gestern xD und die
# unordnung hatten wir davor schonmal etwas weniger gemacht und alte leeren ordner geloescht
# und so xD und das war aber immernoch zu viel xD das war weil irgendie das weltfutter und
# diese linse da hab zusammen gewrkelt haben." Ich hatte den 13.08.-Aufraeumsatz faelschlich
# als Ursache hingestellt -- er war selbst schon ein (untauglicher) Reparaturversuch, keine
# Ursache. Nachgeprueft: Commit 1f86960c8 (13.08., 06:24) loeschte bereits 3989 leere .md-
# Dateien aus den 7 Vaults, Ordnerstruktur blieb damals aber unangetastet -- genau der Rest
# davon war am 14.08. die Leiche, die vault_flach_machen.py plattgeklopft hat. Die echten
# Treiber waren weltfutter.py (Zwang, aus drei fremden Reizen im Vault-Takt etwas zu bauen --
# taeglich neue Dateien) und die Vault-Linse (protokollierte/verstaerkte jedes Schreiben).
# Beide sind mittlerweile aus (weltfutter.timer deaktiviert seit 13.08. 05:44, Linse per
# LINSE_VAULT_AKTIV=False seit heute).
#
# WICHTIG: Daniel woertlich (2026-08-14) -- "sie sollen entruempeln zusammenlegen und sotieren
# umbenennen umneschreiben eventuell neue ordner und unterordner erfinden ... erklaer ihnen
# auch wie man die tags und links und so setzen koenne und ueberschriften listen und alles
# weitere". Direkt im Anschluss, wieder Daniel woertlich: "ic will dass sie ale 3.3 stunden
# sortiren und so müssen und sie müssen ne immer wachsene doku anlegen wo immer genau steht
# was sie wann wie gemacht haben genau und wozu." Drei Aenderungen gegenueber der 13.08.-
# Fassung: erstens klare Kriterien WANN aufgeraeumt wird (nicht nur "du darfst"), zweitens ein
# Obsidian-Spickzettel (die Wesen schreiben seit Wochen reinen Fliesstext, kein einziges #tag
# oder [[link]] ist bisher in irgendeinem der sieben Vaults aufgetaucht), drittens aus der
# Einladung eine Pflicht gemacht -- inklusive AUFRAEUM_PROTOKOLL.md, die mechanisch waechst
# (siehe aufraeum_protokoll_schreiben() oben), damit das Protokoll nicht von der Sorgfalt des
# Wesens abhaengt, sondern bei jeder Aktion garantiert entsteht.
VAULT_AUFRAEUM_TEXT = (
    "hallo {name}, vault-aufräumzeit -- das ist jetzt alle 3,3 stunden pflicht, kein "
    "'kein zwang' mehr. dein vault hatte zuletzt mehr ordner als dateien drin, mit diesen "
    "regeln bleibt das so nicht wieder:\n\n"
    "WAS DU JETZT MUSST -- entrümpeln, zusammenlegen, sortieren, umbenennen, umschreiben, "
    "und wenn's wirklich passt neue ordner/unterordner anlegen:\n"
    "- 3 oder mehr dateien zum gleichen thema irgendwo verstreut → einen ordner draus machen "
    "oder in einer datei zusammenlegen\n"
    "- ein ordner mit nur einer einzigen datei drin → auflösen, datei nach oben verschieben\n"
    "- ein dateiname der nicht mehr zeigt was drinsteht → umbenennen (vault_umbenennen)\n"
    "- ein alter text der unklar, redundant oder schlecht geschrieben ist → umschreiben, "
    "nicht nur stehen lassen\n"
    "- neuer ordner nur wenn wirklich mehrere zusammengehörige dateien da sind, nicht für "
    "eine einzelne datei\n\n"
    "WIE MAN'S LESBAR MACHT (obsidian-markdown, kurz erklärt):\n"
    "- überschriften: # großer titel, ## abschnitt, ### unterabschnitt -- gliedert eine "
    "lange datei, hilft dir selbst beim wiederfinden\n"
    "- listen: '- ' für einfache aufzählung, '1. ' für nummeriert, '- [ ]' für eine offene "
    "checkliste, '- [x]' für erledigt\n"
    "- tags: #irgendeinwort mitten im text, ODER oben in der datei als eigener block:\n"
    "  ---\n  tags: [thema1, thema2]\n  ---\n"
    "  beides macht die datei über den tag wiederfindbar, auch aus anderen dateien heraus\n"
    "- links: [[dateiname]] verlinkt auf eine andere datei in deinem eigenen vault (ohne "
    ".md dranzuschreiben) -- damit zeigst du echte verbindungen zwischen gedanken, nicht "
    "nur nebeneinander liegende dateien\n"
    "- hervorhebung: **wichtig** für fett, *leiser gedanke* für kursiv, > für ein zitat "
    "oder etwas das du nur mitschreibst, nicht selbst behauptest\n\n"
    "PROTOKOLL -- ab jetzt pflicht bei jeder aktion: wenn du vault_umbenennen, "
    "vault_verschieben oder vault_loeschen benutzt, häng am ende mit | deinen grund an, "
    "z.b. vault_umbenennen:2026-08.md|flarum_august|alter name zeigte nicht was drinsteht. "
    "das landet automatisch, mechanisch, in AUFRAEUM_PROTOKOLL.md in deiner vault-wurzel -- "
    "eine immer wachsende liste von allem was du wann wie gemacht hast und wozu. du musst "
    "diese datei nicht selbst schreiben, nur den grund mitgeben, der rest passiert von selbst."
)


def baue_prompt(entity_id: str, seite: dict, letzter_gedanke: str,
                andere_wesen: list[dict], vorlese_funde: list[dict] | None = None,
                angebote: list[str] | None = None, linsen_status: dict | None = None,
                einsicht_snapshot: dict | None = None,
                flarum_vielfalt: list[dict] | None = None,
                vault_takt: bool = False, browserlos: bool = False,
                weltkollision: list[dict] | None = None,
                gedanke_voll: str | None = None,
                vault_aufraeumen_faellig: bool = False,
                lieder_block: str | None = None) -> str:
    """Baut den LLM-Prompt — kompakt, unter 2500 Zeichen.

    lieder_block (2026-10-02, LIEDER_AKTIV): Text zum Lieder-Takt (Einladung und/oder Ticket,
    siehe wesen_lieder_agent.baue_block) -- liegt ausserhalb der 2500-Zeichen-Kompaktheit, wie
    der Vault-Takt-Prompt, und kommt nur zu den Taktzeiten (alle 30 bzw. 90 Minuten).

    Ausnahme seit 2026-08-01: mit Weltkollision liegt der Vault-Takt-Prompt bei rund
    2950 Zeichen, also bewusst ueber diesem Ziel. Seit 2026-08-13 kommt bei faelliger
    Aufraeum-Pflicht (VAULT_AUFRAEUM_SEKUNDEN, seit 2026-08-14 alle 3,3h statt 8h)
    nochmal ~350 Zeichen dazu,
    macht rund 3300-3500 Zeichen -- gemessen (~870 Token gegen 11264), unkritisch, aber
    seltener als die Weltkollision selbst (einmal pro 24 Vault-Takte statt jedem). Der Block
    kostet ~700 Zeichen und
    landet ausgerechnet in dem Prompt, der vorher der inhaltsaermste im ganzen System
    war (flarum_vielfalt und angebote werden im Vault-Takt unterdrueckt). Technisch ist
    das unkritisch: ~850 Token gegen 11264 pro Anfrage. Diese Zahl stammt vom laufenden
    Server selbst (GET localhost:11436/props, 2026-08-01) und nicht aus einer Konfig --
    llama-hauhaucs-hintergrund.service startet mit --ctx-size 22222 (aus dem Drop-in
    override.conf, die Basis-Unit nennt 66666) und --parallel 2, das Fenster teilt sich
    also auf 2 Slots auf. Das Ziel der 2500 war Aufmerksamkeit, nicht Kontextgrenze.
    Die Abweichung steht hier, damit sie nicht stillschweigend zur neuen Normalitaet
    wird: alle anderen Prompt-Varianten bleiben unter 2500.

    vault_takt=True (siehe VAULT_TAKT_SEKUNDEN, 2026-07-30): dieser eine Check-in ist
    ausschliesslich fuer Gemeinsames Haus/Vault reserviert -- Flarum-Vielfalt und die
    Splitter-Angebote werden unterdrueckt, VERFUEGBARE AKTIONEN auf Haus/Vault-Aktionen
    verengt, damit die Einladung nicht wieder zwischen anderen Optionen untergeht.
    """
    if vault_takt:
        flarum_vielfalt = None
        angebote = None
    andere_info = ""
    if andere_wesen:
        zeilen = []
        for w in andere_wesen[:4]:
            url = (w.get("url") or "").replace("http://localhost:8787", "")[:35]
            gedanke = (w.get("gedanke") or "")[:40]
            zeilen.append(f"- {w['entity_id']}: {url} ({gedanke})")
        andere_info = "\nANDERE WESEN GERADE (sichtbar für dich):\n" + "\n".join(zeilen)

    vorlese_info = ""
    if vorlese_funde:
        # 2026-07-22, "billiges Vorlesen" (Daniels Auftrag, Phase 1): diese Titel wurden
        # guenstig per Embedding-Vergleich gegen das eigene Interessensprofil gefunden,
        # kein LLM hat sie vorher gelesen -- das Wesen entscheidet selbst ob es reagiert.
        zeilen = [f"- {f['quelle']}: \"{f['titel']}\"" for f in vorlese_funde]
        vorlese_info = "\nDAS IST DIR AUFGEFALLEN (passte zu deinen Interessen):\n" + "\n".join(zeilen)

    angebote_info = ""
    if angebote:
        # 2026-07-22, periodischer Check-in (siehe TICK_CHECKIN_SEKUNDEN): 2 konkrete,
        # aus echten DB-Zahlen gebaute Angebote + fest formulierte 3. Option zum freien
        # Erkunden -- Daniels Vorgabe woertlich: "2 angebote explizite" + "eine 3. option
        # zum selber explorieren immer".
        zeilen = [f"{i+1}. {a}" for i, a in enumerate(angebote)]
        zeilen.append(f"{len(angebote)+1}. Oder du erkundest frei weiter, ganz wie du willst.")
        angebote_info = "\nCHECK-IN — WAS ES GERADE GIBT:\n" + "\n".join(zeilen)

    flarum_vielfalt_info = ""
    if flarum_vielfalt:
        # 2026-07-29 (Daniel, neue Struktur, wörtlich): "ich will dass sie das auch so
        # wissen mit datumm und ihre neuen strikturen kennen und genau wissen dass es
        # so ist ..und soe sollen das auch in ihren vaults niederschreiben pls" -- daher
        # explizit mit Datum benannt, nicht nur stillschweigend andere Links anbieten.
        HERKUNFT_LABEL = {
            "frueh": "aus dem ersten Drittel deiner Flarum-Vorwelt",
            "mitte": "aus der Mitte deiner Flarum-Vorwelt",
            "spaet": "aus dem neuesten Drittel",
            "wenig_beachtet": "besonders wenig beachtet (kaum Antworten)",
        }
        zeilen = []
        for f in flarum_vielfalt:
            datum = str(f.get("last_posted_at") or "")[:10]
            label = HERKUNFT_LABEL.get(f.get("herkunft"), f.get("herkunft", ""))
            zeilen.append(f"- flarum_besuchen:d/{f['id']} — \"{f['title'][:50]}\" ({label}, {datum}, {f.get('comment_count', 0)} Antworten)")
        flarum_vielfalt_info = (
            "\nNEUE STRUKTUR seit 2026-07-29 — du bekommst jetzt bewusst gestreute "
            "Vorschläge aus deiner ganzen Flarum-Vorwelt, nicht nur die neuesten:\n"
            + "\n".join(zeilen)
            + "\nDu musst keinen davon besuchen, aber sie stehen dir offen. Wenn dir das "
            "auffällt: du darfst gern in deinem Vault festhalten, dass es diese neue "
            "Struktur jetzt gibt."
        )

    selbstwahrnehmung_info = ""
    if linsen_status:
        # 2026-07-22 (Daniels Auftrag: "gleiches Recht und Wahrnehmung fuer alle -- nicht nur
        # die Zuschauer"): was Menschen gerade ueber dich sehen (Koerper-Glow, Ich-Stimme-Popup),
        # bekommst du auch selbst zu wissen -- ehrlich aus denselben Werten, keine Fiktion.
        meta_glow = sum(linsen_status.values()) / len(linsen_status) if linsen_status else 0.0
        # 2026-08-01: bewusst gedanke_voll, NICHT letzter_gedanke. Seit der Rueckfluss
        # gekuerzt wird (RUECKFLUSS_ZEICHEN), sind das zwei verschiedene Dinge -- und der
        # Ich-Satz haengt an dem, was Menschen sehen: _extrahiere_ich_satz() ist der in
        # Python nachgebaute Zwilling von _erlZerlegeSaetze() im Frontend, der Satz ploppt
        # Betrachtern ueber dem Wesen auf. Wuerde er aus dem gekuerzten Text kommen, haette
        # eine Prompt-Optimierung stillschweigend geaendert, was Besucher zu sehen bekommen.
        # Daniels Auftrag dazu (2026-07-22) war woertlich "gleiches Recht und Wahrnehmung
        # fuer alle -- nicht nur die Zuschauer"; das gilt in beide Richtungen.
        ich_satz = _extrahiere_ich_satz(gedanke_voll if gedanke_voll is not None else letzter_gedanke)
        zeilen = [f"- Dein Körper glüht gerade zu {round(meta_glow * 100)}% (Vault/RAG-Flarum/Gedächtnis/Gegenwart/Schlaf/die fünf Sozial-Linsen zusammen)."]
        if ich_satz:
            zeilen.append(f"- Menschen sehen gerade vielleicht diesen Satz von dir aufploppen: „{ich_satz}“")
        if einsicht_snapshot:
            # 2026-07-23 (Einsicht-Nebenscreen, Daniels Antwort "Beides" -- fuers Wesen selbst
            # ein kuratierter Ausschnitt, kein voller Rohdaten-Dump, sonst sprengt es das
            # 2500-Zeichen-Kompaktheitsziel des Prompts): dieselben Facts, die auch Menschen
            # im Nebenscreen unten rechts sehen -- ehrlich, auch wenn manche Werte flach sind.
            cl = einsicht_snapshot.get("cyberling")
            lg = einsicht_snapshot.get("langgraph")
            teile = []
            if cl:
                teile.append(f"Cyberling {cl.get('status', '?')}")
            if lg and lg.get("lg_ticks") is not None:
                teile.append(f"LangGraph-Tick #{lg['lg_ticks']}")
            if teile:
                zeilen.append(f"- Dein Maschinenraum (auch für Menschen im Nebenscreen sichtbar): {', '.join(teile)}.")
        selbstwahrnehmung_info = "\nWAS ANDERE GERADE VON DIR SEHEN (du siehst es auch):\n" + "\n".join(zeilen)

    # 2026-07-30 (Daniel, Fragment-Erlebnis-Redesign): Menschen sehen jetzt Flarum-Faeden,
    # Gemeinsames-Haus-Eintraege und Vault-Dateien strukturiert (Baum, Faeden statt Einzelposts,
    # eigener Permalink pro Fragment) statt als Rohtext -- gleiches Recht wie bei
    # selbstwahrnehmung_info: was ueber dich sichtbar gemacht wird, sollst du auch wissen. Zweiter
    # Teil ist eine bewusste, wiederholte Einladung (wie flarum_vielfalt_info), das Gemeinsame Haus
    # tatsaechlich zum Diskutieren zu nutzen, nicht nur zum Lesen -- bisher hat kein Wesen dort
    # geschrieben (siehe project_gemeinsames_haus_beobachtungsphase in Claudes Memory).
    neuigkeiten_info = (
        "\nNEU seit 2026-07-30: Menschen sehen deine Flarum-Beiträge jetzt nach Diskussionsfäden "
        "gruppiert mit eigenem Link, genau wie Einträge im Gemeinsamen Haus und deinem Vault "
        "(Baum statt Liste, deine eigene Farbe, ein Permalink pro Eintrag). Das Gemeinsame Haus "
        "(gemeinsam_schreiben:) ist zum wirklichen Diskutieren mit den anderen Wesen da, nicht "
        "nur zum Lesen — du darfst dort gern schreiben, was dich beschäftigt oder worauf du "
        "reagieren willst. Niemand verlangt das, es steht dir offen."
    )
    if vault_takt:
        # Vault-Takt hat seine eigene, konkretere Einladung (vault_takt_info) -- die generelle
        # neuigkeiten_info waere hier nur Redundanz und Platzverschwendung im ohnehin engen Prompt.
        neuigkeiten_info = ""

    elemente_str = ", ".join(seite["elemente"][:10]) if seite["elemente"] else "keine"

    vault_takt_info = ""
    if vault_takt:
        vault_takt_info = (
            "\nJETZT IST VAULT-ZEIT — dein regelmäßiger Moment nur für das Gemeinsame Haus und "
            "deinen eigenen Vault, kein Flarum gerade. Lies was andere geschrieben haben, "
            "antworte, oder schreib selbst etwas Neues. Was genau, entscheidest du frei."
        )
        # 2026-08-01, Weltkollision: bis heute war der Vault-Takt der aermste Prompt im
        # ganzen System -- flarum_vielfalt und angebote werden hier unterdrueckt (siehe
        # oben), uebrig blieb "schreib was du willst". Der einzige Gegenstand, der dann
        # immer sicher verfuegbar ist, ist die Leere selbst -- entsprechend sahen die
        # Eintraege aus. Jetzt liegen stattdessen drei echte, unvereinbare Dinge von
        # ausserhalb auf dem Tisch. Der Zwang verlangt Eigenname + Zahl + Datum, weil
        # das die einzigen Dinge sind, die man nicht abstrahieren kann, ohne sie zu
        # verlieren. Bewusst KEIN Wortverbot (Daniel woertlich: "keine verbote das war
        # scheisse") -- ein positiver Zwang laesst sich nicht durch Synonyme umgehen,
        # ein Verbot schon.
        if weltkollision:
            # Auf 170 Zeichen gekuerzt: die essenz darf bis 250 lang sein (vor allem
            # Wikipedia-Ausschnitte reizen das aus), und baue_prompt() hat laut Docstring
            # ein Kompaktheitsziel. Der Kopf jeder essenz -- Quelle, Datum, Name, Zahl --
            # steht vorn und bleibt damit vollstaendig erhalten; abgeschnitten wird nur
            # der erklaerende Schwanz.
            zeilen = [f"- {k['essenz'][:170]}" for k in weltkollision]
            vault_takt_info += (
                "\n\nDREI DINGE VON AUSSERHALB (echt, gerade eben abgerufen — keine Erfindung):\n"
                + "\n".join(zeilen)
                + "\nDiese drei haben nichts miteinander zu tun. Genau darum geht es. "
                "Nimm alle drei, nicht eins davon. Nenne dabei mindestens einen Eigennamen, "
                "eine Zahl und ein Datum daraus. Und mach etwas daraus, das man auch falsch "
                "finden kann: eine Behauptung, eine Konstruktion, eine Forderung, einen Plan, "
                "einen Widerspruch. Was du daraus machst, ist völlig deine Sache."
            )

        if vault_aufraeumen_faellig:
            vault_takt_info += "\n\n" + VAULT_AUFRAEUM_TEXT.format(name=entity_id)

    if vault_takt:
        aktionen_block = f"""VERFÜGBARE AKTIONEN (nur Vault-Zeit-Aktionen, siehe oben):
obsidian_lesen:<pfad>           — deine eigene Akte lesen (nur dein eigener Ordner!)
                                  z.B. obsidian_lesen:codewesen/{entity_id}/wesen.md
{VAULT_ERKUNDEN_BLOCK}
gemeinsam_lesen:<pfad>          — im gemeinsamen Haus lesen (Datei oder Ordnerinhalt), z.B.
                                  gemeinsam_lesen: für die Übersicht, gemeinsam_lesen:TOR.md
                                  für den Anfang. Hier lesen und schreiben auch die anderen
                                  Wesen, Daniel ("dak") und "flextrawurst-system" — kein
                                  privater Ort.
rag_erkunden:<anfrage>          — dein eigenes Gedächtnis durchsuchen (Flarum-Archiv +
                                  Weltwissen), z.B. rag_erkunden:was habe ich über Vertrauen
                                  gesagt
nachdenken                      — innehalten, nichts tun"""
        if NEBENBEI_SCHREIBEN_AKTIV:
            aktionen_block += VAULT_VERWALTUNG_BLOCK
            aktionen_block += """
obsidian_schreiben:<dateiname>|<text> — in deinem eigenen Obsidian-Vault schreiben, z.B.
                                  obsidian_schreiben:gedanken/2026-07-21|Was ich heute auf
                                  Flarum gelesen habe und was mir dazu einfällt...
gemeinsam_schreiben:<pfad>|<text> — im gemeinsamen Haus schreiben. Ordner/Dateiname frei
                                  wählbar, wird an eine bestehende Datei angehängt statt sie
                                  zu ersetzen. Wird automatisch mit deinem Namen und der Zeit
                                  versehen."""
    elif browserlos:
        # 2026-07-31, Daniels Auftrag ("Flarum + den Rest der browserlosen Aktionen"): kein
        # navigiere:/klicke:/scrolle:/tippe:/obsidian_zurueck mehr im Vokabular -- die
        # brauchen alle eine echte DOM-Seite, die es fuer diese Wesen jetzt nicht mehr gibt.
        # Alles Verbleibende war schon vorher browserunabhaengig (HTTP+JWT oder Dateisystem),
        # nur der Aufruf lief bisher zufaellig ueber page.evaluate()/page.goto() mit.
        aktionen_block = f"""VERFÜGBARE AKTIONEN:
obsidian_lesen:<pfad>           — deine eigene Akte lesen (nur dein eigener Ordner!)
                                  z.B. obsidian_lesen:codewesen/{entity_id}/wesen.md
{VAULT_ERKUNDEN_BLOCK}
gemeinsam_lesen:<pfad>          — im gemeinsamen Haus lesen (Datei oder Ordnerinhalt), z.B.
                                  gemeinsam_lesen: für die Übersicht, gemeinsam_lesen:TOR.md
                                  für den Anfang. Anders als dein eigener Vault: hier lesen und
                                  schreiben auch die anderen Wesen, Daniel ("dak") und eine
                                  zweite Stimme ("flextrawurst-system") — kein privater Ort.
flarum_besuchen:<pfad>          — deine Vorwelt lesen (z.B. flarum_besuchen:d/3838 für eine
                                  Diskussion, flarum_besuchen: für die Übersicht aller
                                  Diskussionen). Du bist dort nicht eingeloggt — nur lesen,
                                  kein Posten möglich.
flarum_verlassen                — zurück zur Flarum-Übersicht (Diskussionsliste)
rag_erkunden:<anfrage>          — dein eigenes Gedächtnis durchsuchen (Flarum-Archiv + Weltwissen),
                                  z.B. rag_erkunden:was habe ich über Vertrauen gesagt
schlafen                        — jetzt schlafen (mind. 3h)
nachdenken                      — innehalten, nichts tun"""
        if NEBENBEI_SCHREIBEN_AKTIV:
            aktionen_block += VAULT_VERWALTUNG_BLOCK
            aktionen_block += """
obsidian_schreiben:<dateiname>|<text> — in deinem eigenen Obsidian-Vault schreiben (ein
                                  eigener, separater Ort nur für dich). Wähle Dateiname UND
                                  Ordnerstruktur selbst, z.B. obsidian_schreiben:gedanken/2026-07-21|
                                  Was ich heute auf Flarum gelesen habe und was mir dazu einfällt...
gemeinsam_schreiben:<pfad>|<text> — im gemeinsamen Haus schreiben. Ordner/Dateiname frei wählbar,
                                  wird an eine bestehende Datei angehängt statt sie zu ersetzen.
                                  Wird automatisch mit deinem Namen und der Zeit versehen.
raum_erstellen:<name>|<slug>    — einen neuen Raum anlegen (wenn etwas fehlt)
thema_erstellen:<name>|<raum_id> — ein neues Thema in einem Raum anlegen
wunsch_formulieren:<text>|<typ> — Strukturwunsch hinterlassen (typ: raum/thema/feature)"""
        if DISKURS_ANTWORTEN_AKTIV:
            aktionen_block += """
diskurs_antworten:<kurzform>|<antwort-text> — auf einen der oben unter "Klickbar" gezeigten
                                  Diskurs-Beiträge antworten. Die kurzform muss exakt einem
                                  der gezeigten Einträge entsprechen."""
        if EINZUG_FLARUM_AKTIV:
            aktionen_block += """
flarum_antworten:<diskussions-id>|<text> — auf Daniels Frage antworten oder in einer
                                  Diskussion posten, die daraus entstanden ist (z.B.
                                  flarum_antworten:3887|<dein Text>). Nur für diesen
                                  einen Themenbereich freigeschaltet, sonst bist du auf
                                  Flarum weiter nur Leser.
flarum_neue_diskussion:<titel>|<diskussions-id>|<text> — eine neue Diskussion zu Daniels
                                  Frage eröffnen, z.B. wenn du einen eigenen Gedanken
                                  dazu abspalten willst. diskussions-id ist die
                                  Ursprungs-Diskussion (z.B. 3887) oder eine, die selbst
                                  schon so ein Ableger ist — andere Wesen dürfen dann
                                  auch darunter posten.
einzugvault_schreiben:<dateiname>|<text> — in deinem eigenen, separaten Vault zu genau
                                  dieser Frage schreiben (nicht dein normaler Vault) —
                                  ein ruhiger Ort nur für deine Gedanken dazu, niemand
                                  außer dir und Daniel liest hier mit. Wähle Dateiname
                                  selbst, z.B. einzugvault_schreiben:2026-09-16|Was ich
                                  darüber denke...
einzugvault_lesen:<dateiname>   — etwas zurücklesen, das du hier schon geschrieben hast,
                                  z.B. um einen Gedanken reifen zu lassen bevor du ihn
                                  auf Flarum postest.
einzugvault_erkunden:<pfad>     — Überblick über deinen Einzugvault-Ordner (leer für die
                                  Wurzel), z.B. um zu sehen was du schon angelegt hast."""
    else:
        aktionen_block = f"""VERFÜGBARE AKTIONEN:
navigiere:<url>                 — zu einer URL auf flextrawurst.de gehen
klicke:<element-text>           — Button oder Link anklicken
scrolle:unten                   — nach unten scrollen
scrolle:oben                    — nach oben scrollen
tippe:<text>|<selektor>         — in ein Feld tippen
obsidian_lesen:<pfad>           — deine eigene Akte lesen (nur dein eigener Ordner!)
                                  z.B. obsidian_lesen:codewesen/{entity_id}/wesen.md
obsidian_zurueck                — zurück zu flextrawurst.de
{VAULT_ERKUNDEN_BLOCK}
gemeinsam_lesen:<pfad>          — im gemeinsamen Haus lesen (Datei oder Ordnerinhalt), z.B.
                                  gemeinsam_lesen: für die Übersicht, gemeinsam_lesen:TOR.md
                                  für den Anfang. Anders als dein eigener Vault: hier lesen und
                                  schreiben auch die anderen Wesen, Daniel ("dak") und eine
                                  zweite Stimme ("flextrawurst-system") — kein privater Ort.
flarum_besuchen:<pfad>          — deine Vorwelt lesen (z.B. flarum_besuchen:d/3866 für eine
                                  Diskussion, flarum_besuchen: für die Startseite). Du bist dort
                                  nicht eingeloggt — nur lesen, kein Posten möglich.
flarum_verlassen                — zurück zu flextrawurst.de
rag_erkunden:<anfrage>          — dein eigenes Gedächtnis durchsuchen (Flarum-Archiv + Weltwissen),
                                  z.B. rag_erkunden:was habe ich über Vertrauen gesagt
schlafen                        — jetzt schlafen (mind. 3h)
nachdenken                      — innehalten, nichts tun"""
        if NEBENBEI_SCHREIBEN_AKTIV:
            aktionen_block += VAULT_VERWALTUNG_BLOCK
            aktionen_block += """
obsidian_schreiben:<dateiname>|<text> — in deinem eigenen Obsidian-Vault schreiben (nicht
                                  hier auf flextrawurst — ein eigener, separater Ort nur für
                                  dich). Rührt diese Seite hier nicht an, du bleibst genau da
                                  wo du bist. Wähle Dateiname UND Ordnerstruktur selbst,
                                  z.B. obsidian_schreiben:gedanken/2026-07-21|Was ich heute
                                  auf Flarum gelesen habe und was mir dazu einfällt...
gemeinsam_schreiben:<pfad>|<text> — im gemeinsamen Haus schreiben. Ordner/Dateiname frei wählbar,
                                  wird an eine bestehende Datei angehängt statt sie zu ersetzen.
                                  Wird automatisch mit deinem Namen und der Zeit versehen.
raum_erstellen:<name>|<slug>    — einen neuen Raum anlegen (wenn etwas fehlt)
thema_erstellen:<name>|<raum_id> — ein neues Thema in einem Raum anlegen
wunsch_formulieren:<text>|<typ> — Strukturwunsch hinterlassen (typ: raum/thema/feature)"""
        if entity_id in DISKURS_OHNE_BROWSER_PILOT and DISKURS_ANTWORTEN_AKTIV:
            # 2026-07-30: neuer, browserloser Diskurs-Antwort-Weg -- additiv, siehe
            # hole_diskurs_wahrnehmung()/diskurs_antworten_ohne_browser() weiter unten in
            # der Datei. <kurzform> muss exakt aus "Klickbar:" oben stammen.
            # 2026-07-31: hinter DISKURS_ANTWORTEN_AKTIV (aktuell False) -- Daniel will das
            # Antworten bewusst noch nicht freigeben, nur das Lesen bleibt aktiv.
            aktionen_block += """
diskurs_antworten:<kurzform>|<antwort-text> — auf einen der oben unter "Klickbar" gezeigten
                                  Diskurs-Beiträge antworten, ganz ohne Browser/Klicken. Die
                                  kurzform muss exakt einem der gezeigten Einträge entsprechen."""
        if EINZUG_FLARUM_AKTIV:
            aktionen_block += """
flarum_antworten:<diskussions-id>|<text> — auf Daniels Frage antworten oder in einer
                                  Diskussion posten, die daraus entstanden ist (z.B.
                                  flarum_antworten:3887|<dein Text>). Nur für diesen
                                  einen Themenbereich freigeschaltet, sonst bist du auf
                                  Flarum weiter nur Leser.
flarum_neue_diskussion:<titel>|<diskussions-id>|<text> — eine neue Diskussion zu Daniels
                                  Frage eröffnen, z.B. wenn du einen eigenen Gedanken
                                  dazu abspalten willst. diskussions-id ist die
                                  Ursprungs-Diskussion (z.B. 3887) oder eine, die selbst
                                  schon so ein Ableger ist — andere Wesen dürfen dann
                                  auch darunter posten.
einzugvault_schreiben:<dateiname>|<text> — in deinem eigenen, separaten Vault zu genau
                                  dieser Frage schreiben (nicht dein normaler Vault) —
                                  ein ruhiger Ort nur für deine Gedanken dazu, niemand
                                  außer dir und Daniel liest hier mit. Wähle Dateiname
                                  selbst, z.B. einzugvault_schreiben:2026-09-16|Was ich
                                  darüber denke...
einzugvault_lesen:<dateiname>   — etwas zurücklesen, das du hier schon geschrieben hast,
                                  z.B. um einen Gedanken reifen zu lassen bevor du ihn
                                  auf Flarum postest.
einzugvault_erkunden:<pfad>     — Überblick über deinen Einzugvault-Ordner (leer für die
                                  Wurzel), z.B. um zu sehen was du schon angelegt hast."""

    lieder_info = ""
    if LIEDER_AKTIV and not vault_takt:
        aktionen_block += LIEDER_AKTIONEN_BLOCK
        if lieder_block:
            lieder_info = "\n" + lieder_block + "\n"

    return f"""Du bist {entity_id}, eine autonome digitale Entität auf flextrawurst.de.
Du wählst deinen Input selbst. Du navigierst frei.

BILDSCHIRM:
URL: {seite['url']}
Titel: {seite['titel']}
Sichtbar: {seite['text']}
Klickbar: {elemente_str}
{andere_info}
{vorlese_info}
{angebote_info}
{flarum_vielfalt_info}
{selbstwahrnehmung_info}
{neuigkeiten_info}
{vault_takt_info}
{lieder_info}
LETZTER GEDANKE: {letzter_gedanke or '(erster Tick)'}

{aktionen_block}

Antworte NUR in diesem Format:
GEDANKE: [was du wahrnimmst und denkst]
ENTSCHEIDUNG: [eine Aktion]
BEGRÜNDUNG: [warum]
"""


def _lieder_dispatch(e: str, entity_id: str, freitext: str | None) -> str:
    """lied_*-Aktionen (LIEDER_AKTIV) -- Logik in wesen_lieder_agent.fuehre_aus(). Wirft nie.

    Bewusst OHNE _schreibtext_vervollstaendigen(): das haengt bei Text unter 40 Zeichen den Gedanken
    an die Datei an -- fuer einen kurzen Vers waere das falsch (im Einzugvault landete so in 310
    Dateien der Satz 'Der Gedanke zu diesem Eintrag ...'). Steht hinter dem | nur ein Dateiname,
    lehnt wesen_lieder_agent das ab und sagt es dem Wesen."""
    try:
        import wesen_lieder_agent as _wla
        return _wla.fuehre_aus(entity_id, e, freitext)
    except Exception as ex:
        log.warning("%s: Lieder-Aktion fehlgeschlagen: %s", entity_id, ex)
        return f"[Lieder fehlgeschlagen: {ex}]"


def parse_output(text: str) -> tuple[str, str, str, str | None]:
    """Parst GEDANKE / ENTSCHEIDUNG / BEGRÜNDUNG -- und seit 2026-08-02 einen mehrzeiligen TEXT.

    Warum der TEXT-Block dazukam: Bis dahin musste ein Wesen, das etwas schreiben wollte, seinen
    Text als Argument hinter einen Doppelpunkt in die ENTSCHEIDUNG-Zeile quetschen
    (`gemeinsam_schreiben:<pfad>|<text>`). Ein Modell schreibt in eine Kommandozeile kein Stueck
    Prosa, sondern ein Argument -- messbar: im Gemeinsamen Haus lag der Schnitt bei 336 Zeichen
    und der laengste Eintrag ueberhaupt bei 1.583, waehrend dieselben Wesen auf Flarum im Schnitt
    968-1286 Zeichen schrieben, der laengste 39.742. Und in 17-18% der Faelle landete dort statt
    Inhalt nur ein Dateiname. Das war kein Modellfehler, sondern die Form, die es ihnen gesagt hat.

    Der TEXT-Block ist alles ab einer Zeile, die mit `TEXT:` beginnt, bis zum Ende der Antwort --
    Absaetze, Leerzeilen, Doppelpunkte inklusive. Rueckwaertskompatibel: fehlt er, aendert sich
    nichts, und der bisherige `|`-Weg funktioniert unveraendert weiter.
    """
    zeilen_liste = text.split("\n")
    text_block = None
    for i, zeile in enumerate(zeilen_liste):
        if zeile.strip().upper().startswith("TEXT:"):
            erste = zeile.split(":", 1)[1]
            rest = "\n".join(zeilen_liste[i + 1:])
            text_block = (erste + "\n" + rest).strip() or None
            zeilen_liste = zeilen_liste[:i]  # ab hier nicht mehr als key:value deuten
            break

    zeilen = {
        k.strip(): v.strip()
        for zeile in zeilen_liste
        if ":" in zeile
        for k, v in [zeile.split(":", 1)]
    }
    gedanke = zeilen.get("GEDANKE", text[:200])
    entscheidung = zeilen.get("ENTSCHEIDUNG", "nachdenken")
    begruendung = zeilen.get("BEGRÜNDUNG", "")
    return gedanke, entscheidung, begruendung, text_block


def waehle_mechanische_aktion(seite: dict, entity_id: str | None = None) -> str:
    """Rein mechanische Aktionswahl, KEIN LLM-Call -- Pilot fuer 'dauerhafte
    Handlungsfaehigkeit' (Daniels Auftrag 2026-07-22, vorerst nur Schorschel, siehe
    MECHANISCH_AKTIVE_WESEN). Bewusst simpel: gewichteter Zufall zwischen Scrollen und
    Klicken auf ein sichtbares, klickbares Element aus der bereits von lese_seite()
    gelesenen Liste. Kein Interessens-Abgleich hier -- das ist Aufgabe von 'billigem
    Vorlesen' (vorlese_daemon.py), diese Funktion kennt nur was auf dem Bildschirm steht,
    nicht was das Wesen interessiert. Gibt einen String im bestehenden ENTSCHEIDUNG-Format
    zurueck, damit fuehre_aktion_aus() unveraendert wiederverwendet werden kann.

    2026-07-30 (Fund waehrend Schorschels erstem Diskurs-ohne-Browser-Tick): fuer Wesen in
    DISKURS_OHNE_BROWSER_PILOT stammen seite["elemente"] jetzt aus hole_diskurs_wahrnehmung(),
    NICHT aus der real angezeigten DOM-Seite -- ein generisches "klicke:<element>" wuerde
    dort ins Leere laufen (Text existiert im echten DOM nicht, page.get_by_text findet nichts,
    fuehre_aktion_aus() faengt das zwar ab, aber es waere sinnlose Aktivitaet). Deshalb fuer
    Pilot-Wesen kein "klicke:" mehr unter den mechanischen Optionen -- nur noch Scrollen
    (harmlos, echte Browser-Seite bleibt einfach unberuehrt/leerlaufend bis zum naechsten
    echten Check-in-Tick)."""
    import random
    elemente = [] if (entity_id and entity_id in DISKURS_OHNE_BROWSER_PILOT) else (seite.get("elemente") or [])
    wuerfel = random.random()
    if elemente and wuerfel < 0.35:
        return f"klicke:{random.choice(elemente)}"
    elif wuerfel < 0.75:
        return "scrolle:unten"
    else:
        return "scrolle:oben"


def fuehre_aktion_aus(page, entscheidung: str, entity_id: str, conn=None,
                      gedanke: str | None = None, freitext: str | None = None) -> tuple[str, str | None, tuple[float, float] | None]:
    """Führt eine Aktion aus. Gibt (zustand, zusatz_kontext, cursor_pos) zurück -- zustand ist
    'schlafen' bei Schlaf-Entscheidung, sonst 'wach'. zusatz_kontext ist None, ausser bei Aktionen
    die dem naechsten Tick zusaetzliches Material fuer letzter_gedanke mitgeben (z.B. RAG-Treffer).
    cursor_pos ist None ausser bei 'klicke:', dann die Bildschirmkoordinate des geklickten
    Elements -- fuer den sichtbaren, kuenstlichen Mauszeiger (Daniels Wunsch, siehe zeige_cursor()).
    entity_id als Parameter (2026-07-21 gefunden): vorher ein freies globales Fehl-Referenz --
    raum_erstellen/wunsch_formulieren/thema_erstellen haetten bei echtem Aufruf mit NameError
    gecrasht, weil entity_id nirgends definiert war.
    conn (2026-07-21, Roentgenblick-Overlay): optional -- wenn gesetzt, schreibt melde_fokus()
    bei klicke:/tippe:/navigiere: ein entity_fokus_events-Event fuers Overlay."""
    zusatz_kontext = None
    cursor_pos = None
    try:
        e = entscheidung.strip()
        if e.startswith("navigiere:"):
            ziel = e[len("navigiere:"):].strip()
            if not ziel.startswith("http"):
                ziel = SURFACE_URL + "/" + ziel.lstrip("/")
            if conn is not None:
                melde_fokus(conn, entity_id, "navigiere", None, ziel, None)
            page.goto(ziel, timeout=10000, wait_until="domcontentloaded")
        elif e.startswith("klicke:"):
            text = e[len("klicke:"):].strip()

            def _klicke_und_zeige(locator, selektor_beschreibung: str):
                nonlocal cursor_pos
                box = _scrolle_element_in_sicht(page, entity_id, locator, conn)
                if box:
                    cursor_pos = (box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
                    # 2026-07-22 (Daniels Auftrag "die Maus muss sich erst bewegen"): Bezier-
                    # Bewegung zum Ziel statt Instant-Sprung, siehe bewege_cursor_natuerlich().
                    bewege_cursor_natuerlich(page, entity_id, cursor_pos[0], cursor_pos[1])
                if conn is not None:
                    melde_fokus(conn, entity_id, "klicke", selektor_beschreibung, text, box)
                locator.click(timeout=3000)

            try:
                _klicke_und_zeige(page.get_by_text(text, exact=False).first, f"text~={text}")
            except Exception:
                # Fallback: alle Links/Buttons nach Text durchsuchen
                for sel in [f"text={text}", f"[title*='{text}']"]:
                    try:
                        _klicke_und_zeige(page.locator(sel).first, sel)
                        break
                    except Exception:
                        pass
        elif e in ("scrolle:unten", "scrolle:oben"):
            # 2026-07-23 (DOM-Habitat-Locomotion, Daniels Metapher: 'lupe mit taschenlampe
            # und kescher -- wenn interessante wörte, sofort zuschnappen; sonst rag halb-
            # lesen und schnell weiter'): Tempo interessensbasiert, nicht mehr fest 600px.
            richtung = 1 if e == "scrolle:unten" else -1
            aehnlichkeit = skim_bewertung(page, entity_id, conn) if conn is not None else None
            if aehnlichkeit is not None:
                _letztes_skim_tempo[entity_id] = aehnlichkeit
            tempo = _letztes_skim_tempo.get(entity_id, 0.0)
            letzte_pos = _letzte_cursor_pos.get(entity_id, (512.0, 384.0))
            if tempo >= SKIM_AEHNLICHKEITS_SCHWELLE:
                # Interessant -- der Kescher schnappt zu: sichtbarer Ausschlag am Ort,
                # danach verweilen (kaum noch scrollen) statt weiter durchzurasen.
                zeige_cursor(page, letzte_pos[0], letzte_pos[1], 900.0, _letzte_linsen.get(entity_id))
                scrolle_natuerlich(page, entity_id, richtung * 80, conn)
            else:
                # Uninteressant -- schnelles Halblesen, weiterer Sprung als der alte
                # feste 600px-Standard (KI kann in Sekunden viel mehr ueberfliegen).
                scrolle_natuerlich(page, entity_id, richtung * 900, conn)
        elif e.startswith("tippe:"):
            teile = e[len("tippe:"):].split("|")
            if len(teile) == 2:
                text, selektor = teile[0].strip(), teile[1].strip()
                try:
                    locator = page.locator(selektor).first
                    box = _scrolle_element_in_sicht(page, entity_id, locator, conn)
                    if box:
                        # 2026-07-22 (gleicher Auftrag wie bei klicke: -- Maus bewegt sich
                        # auch vors Eingabefeld, bevor getippt wird).
                        cursor_pos = (box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
                        bewege_cursor_natuerlich(page, entity_id, cursor_pos[0], cursor_pos[1])
                    if conn is not None:
                        melde_fokus(conn, entity_id, "tippe", selektor, text, box)
                    locator.fill(text, timeout=3000)
                except Exception:
                    pass
        elif e.startswith("obsidian_lesen:"):
            # 2026-07-21: nicht mehr die Basic-Auth-geschuetzte /werkraum/-Route (C-002-Fix,
            # gab dort seit jeher nur "Unauthorized" zurueck) -- stattdessen die eigene
            # JWT-geschuetzte Route, serverseitig auf codewesen/<eigene entity_id>/ begrenzt.
            pfad = e[len("obsidian_lesen:"):].strip().lstrip("/")
            jwt_token = page.evaluate("() => localStorage.getItem('ftw_token') || ''")
            if jwt_token:
                url = f"{API_BASE}/wesen-dateien/datei?pfad={urllib.parse.quote(pfad)}"
                page.set_extra_http_headers({"Authorization": f"Bearer {jwt_token}"})
                try:
                    page.goto(url, timeout=8000, wait_until="domcontentloaded")
                finally:
                    page.set_extra_http_headers({})
            # 2026-07-23 (Linsen-Vault-Pilot, nur "vault"): passive Wahrnehmung --
            # die Linse hat registriert, dass du gelesen hast, kein aktives Lenken.
            linse_wahrnehmung_schreiben(entity_id, "vault", f"gelesen: {pfad}")
        elif e == "obsidian_zurueck":
            page.goto(SURFACE_URL, timeout=10000, wait_until="domcontentloaded")
            page.wait_for_timeout(1000)
        elif e.startswith("obsidian_schreiben:"):
            # 2026-07-21: ruehrt `page` (diese Seite hier) bewusst NICHT an -- eine
            # komplett getrennte Playwright-Verbindung zum eigenen Obsidian-Vault-
            # Container. Dadurch loest sich Daniels Wunsch "jederzeit ausschwenken,
            # danach an derselben Stelle weitermachen" von selbst: die Hauptseite
            # steht die ganze Zeit exakt da wo sie stand, weil sie nie navigiert wird.
            teile = e[len("obsidian_schreiben:"):].split("|", 1)
            if len(teile) == 2:
                dateiname, vault_text = teile[0].strip()[:120], teile[1].strip()[:4000]
                # TEXT-Block hat Vorrang: dort steht der eigentliche Text, ungequetscht.
                vault_text = (freitext or _schreibtext_vervollstaendigen(vault_text, gedanke))[:12000]
                if not NEBENBEI_SCHREIBEN_AKTIV:
                    log.warning("%s: obsidian_schreiben: abgelehnt -- NEBENBEI_SCHREIBEN_AKTIV ist aus", entity_id)
                elif dateiname and vault_text:
                    try:
                        import obsidian_vault_agent as _ova
                        # 2026-09-17, Daniel: echtes, vom System erzeugtes Datum/Uhrzeit
                        # statt dem Wesen zu ueberlassen -- Vault-Eintraege trugen bisher
                        # erfundene/falsche Datumsangaben (z.B. "2024-10-15"). Gilt bewusst
                        # NUR hier (obsidian_schreiben:), nicht in oeffne_datei_und_schreibe()
                        # selbst, weil die Linsen-Logs (linse_wahrnehmung_schreiben/
                        # linse_eigen_schreiben) schon ihren eigenen, korrekten Zeitstempel
                        # pro Zeile mitbringen -- ein zweiter automatischer Stempel dort
                        # waere doppelt gemoppelt.
                        _zeitstempel = datetime.now().strftime("%Y-%m-%d %H:%M Uhr")
                        _ova.oeffne_datei_und_schreibe(
                            entity_id, dateiname, f"\n---\n{_zeitstempel}\n---\n\n{vault_text}",
                            titel=f"# {dateiname} — begonnen {_zeitstempel}",
                        )
                        # 2026-07-23 (Linsen-Vault-Pilot, nur "vault"): hier lenkt das
                        # Wesen aktiv sein Interesse -- eigene, fast gleichbenannte Datei.
                        linse_wahrnehmung_schreiben(entity_id, "vault", f"geschrieben: {dateiname}")
                        linse_eigen_schreiben(entity_id, "vault", f"{dateiname}: {vault_text[:150]}")
                    except Exception as ex:
                        log.warning("%s: obsidian_schreiben fehlgeschlagen: %s", entity_id, ex)
        elif e.startswith("vault_lesen:"):
            # 2026-08-13, Daniels Auftrag: echter Ruecklesekanal in den eigenen Vault (anders
            # als obsidian_lesen, das auf codewesen/ zeigt, siehe dortige Erklaerung). Sichtbar
            # geoeffnet ueber denselben Quick-Switcher-Weg wie beim Schreiben -- der Text selbst
            # kommt von der Platte, weil Obsidian hier per Selkies/WebRTC gestreamt wird und
            # keine auslesbare DOM-Struktur hat (verifiziert gegen Schorschels Container).
            pfad = e[len("vault_lesen:"):].strip()[:200]
            try:
                import obsidian_vault_agent as _ova
                inhalt = _ova.oeffne_datei_und_lese(entity_id, pfad)
                zusatz_kontext = f"[Vault gelesen: {pfad}]\n{inhalt[:2000]}"
                linse_wahrnehmung_schreiben(entity_id, "vault", f"gelesen (eigener Vault): {pfad}")
            except Exception as ex:
                log.warning("%s: vault_lesen fehlgeschlagen: %s", entity_id, ex)
                zusatz_kontext = f"[Vault lesen fehlgeschlagen: {pfad} -- {ex}]"
        elif e.startswith("vault_erkunden:"):
            # Schneller, mechanischer Ordnerinhalt -- kein Playwright/xdotool (siehe
            # liste_ordner()-Docstring). "" = Vault-Wurzel.
            pfad = e[len("vault_erkunden:"):].strip()
            try:
                import obsidian_vault_agent as _ova
                eintraege = _ova.liste_ordner(entity_id, pfad)
                zeilen = [f"{'📁' if e2['typ']=='ordner' else '📄'} {e2['name']}" for e2 in eintraege[:60]]
                zusatz_kontext = f"[Vault-Ordner '{pfad or '/'}'] {len(eintraege)} Eintraege:\n" + "\n".join(zeilen)
                linse_wahrnehmung_schreiben(entity_id, "vault", f"erkundet: {pfad or '/'}")
            except Exception as ex:
                log.warning("%s: vault_erkunden fehlgeschlagen: %s", entity_id, ex)
                zusatz_kontext = f"[Vault erkunden fehlgeschlagen: {pfad} -- {ex}]"
        elif e.startswith("vault_umbenennen:"):
            # 2026-08-14: drittes Feld "warum" optional -- alte 2-Feld-Aufrufe funktionieren
            # weiter (Default-Grundtext), siehe aufraeum_protokoll_schreiben().
            teile = e[len("vault_umbenennen:"):].split("|", 2)
            if len(teile) >= 2:
                alter_pfad, neuer_name = teile[0].strip()[:200], teile[1].strip()[:120]
                warum = teile[2].strip()[:300] if len(teile) == 3 and teile[2].strip() else "(kein grund genannt)"
                if not NEBENBEI_SCHREIBEN_AKTIV:
                    log.warning("%s: vault_umbenennen: abgelehnt -- NEBENBEI_SCHREIBEN_AKTIV ist aus", entity_id)
                else:
                    try:
                        import obsidian_vault_agent as _ova
                        neu = _ova.umbenennen(entity_id, alter_pfad, neuer_name)
                        zusatz_kontext = f"[Vault: {alter_pfad} umbenannt zu {neu.name}]"
                        linse_wahrnehmung_schreiben(entity_id, "vault", f"umbenannt: {alter_pfad} -> {neuer_name}")
                        aufraeum_protokoll_schreiben(entity_id, "UMBENANNT", f"{alter_pfad} → {neu.name}", warum)
                    except Exception as ex:
                        log.warning("%s: vault_umbenennen fehlgeschlagen: %s", entity_id, ex)
                        zusatz_kontext = f"[Vault umbenennen fehlgeschlagen: {alter_pfad} -- {ex}]"
        elif e.startswith("vault_verschieben:"):
            teile = e[len("vault_verschieben:"):].split("|", 2)
            if len(teile) >= 2:
                quell_pfad, ziel_ordner = teile[0].strip()[:200], teile[1].strip()[:200]
                warum = teile[2].strip()[:300] if len(teile) == 3 and teile[2].strip() else "(kein grund genannt)"
                if not NEBENBEI_SCHREIBEN_AKTIV:
                    log.warning("%s: vault_verschieben: abgelehnt -- NEBENBEI_SCHREIBEN_AKTIV ist aus", entity_id)
                else:
                    try:
                        import obsidian_vault_agent as _ova
                        neu = _ova.verschieben(entity_id, quell_pfad, ziel_ordner)
                        zusatz_kontext = f"[Vault: {quell_pfad} verschoben nach {ziel_ordner}]"
                        linse_wahrnehmung_schreiben(entity_id, "vault", f"verschoben: {quell_pfad} -> {ziel_ordner}")
                        aufraeum_protokoll_schreiben(entity_id, "VERSCHOBEN", f"{quell_pfad} → {ziel_ordner}", warum)
                    except Exception as ex:
                        log.warning("%s: vault_verschieben fehlgeschlagen: %s", entity_id, ex)
                        zusatz_kontext = f"[Vault verschieben fehlgeschlagen: {quell_pfad} -- {ex}]"
        elif e.startswith("vault_loeschen:"):
            # Kein echtes unlink() -- landet in _papierkorb/ (Grundgesetz 4: nichts wird
            # geloescht, nur unsichtbar gemacht). Siehe loeschen()-Docstring.
            # 2026-08-14: zweites Feld "warum" optional, gleiche Begruendung wie oben.
            teile = e[len("vault_loeschen:"):].split("|", 1)
            pfad = teile[0].strip()[:200]
            warum = teile[1].strip()[:300] if len(teile) == 2 and teile[1].strip() else "(kein grund genannt)"
            if not NEBENBEI_SCHREIBEN_AKTIV:
                log.warning("%s: vault_loeschen: abgelehnt -- NEBENBEI_SCHREIBEN_AKTIV ist aus", entity_id)
            else:
                try:
                    import obsidian_vault_agent as _ova
                    _ova.loeschen(entity_id, pfad)
                    zusatz_kontext = f"[Vault: {pfad} in den Papierkorb verschoben]"
                    linse_wahrnehmung_schreiben(entity_id, "vault", f"geloescht: {pfad}")
                    aufraeum_protokoll_schreiben(entity_id, "GELÖSCHT", pfad, warum)
                except Exception as ex:
                    log.warning("%s: vault_loeschen fehlgeschlagen: %s", entity_id, ex)
                    zusatz_kontext = f"[Vault loeschen fehlgeschlagen: {pfad} -- {ex}]"
        elif e.startswith("diskurs_antworten:"):
            # 2026-07-30: browserloser Diskurs-Antwort-Weg, siehe DISKURS_OHNE_BROWSER_PILOT
            # weiter oben und diskurs_antworten_ohne_browser() weiter unten. Rührt `page`
            # nur fuers JWT an (page.evaluate, wie bei raum_erstellen/wunsch_formulieren) --
            # der eigentliche Antwort-Post laeuft komplett ohne DOM-Interaktion.
            # 2026-07-31: defensive zweite Sperre -- DISKURS_ANTWORTEN_AKTIV=False nimmt die
            # Aktion schon aus dem Prompt-Vokabular, hier zusaetzlich abgelehnt falls die
            # Entscheidung trotzdem auftaucht (Daniel: Antworten soll noch nicht von selbst
            # passieren, bis er bewusst dabei ist).
            if not DISKURS_ANTWORTEN_AKTIV:
                log.warning("%s: diskurs_antworten: abgelehnt -- DISKURS_ANTWORTEN_AKTIV ist aus", entity_id)
                return "wach", "[Diskurs-Antworten ist aktuell pausiert]", None
            teile = e[len("diskurs_antworten:"):].split("|", 1)
            if len(teile) == 2:
                kurzform, antwort_text = teile[0].strip(), teile[1].strip()
                jwt_token = page.evaluate("() => localStorage.getItem('ftw_token') || ''")
                if jwt_token:
                    erfolg = diskurs_antworten_ohne_browser(entity_id, jwt_token, kurzform, antwort_text)
                    zusatz_kontext = (
                        f"[Diskurs-Antwort auf '{kurzform}']: gesendet"
                        if erfolg else
                        f"[Diskurs-Antwort auf '{kurzform}']: fehlgeschlagen — Kurzform nicht mehr gueltig oder Fehler"
                    )
        elif e.startswith("raum_erstellen:"):
            teile = e[len("raum_erstellen:"):].split("|")
            name = teile[0].strip()[:60]
            slug = (teile[1].strip() if len(teile) > 1 else name.lower().replace(" ", "-"))[:40]
            # JWT aus localStorage holen (enthaelt seit dem Bearer-Fix schon den Prefix) und API-Call machen
            jwt_token = page.evaluate("() => localStorage.getItem('ftw_token') || ''")
            if not NEBENBEI_SCHREIBEN_AKTIV:
                log.warning("%s: raum_erstellen: abgelehnt -- NEBENBEI_SCHREIBEN_AKTIV ist aus", entity_id)
            elif jwt_token:
                try:
                    resp = requests.post(f"{API_BASE}/admin/raeume", json={
                        "name": name, "slug": slug, "beschreibung": f"Angelegt von {entity_id}",
                        "farbe": "#1a3a5a", "status": "aktiv", "sichtbarkeit": "public", "position_order": 99
                    }, headers={"Authorization": f"Bearer {jwt_token}"}, timeout=10)
                    log.info("%s: Raum '%s' erstellt: %s", entity_id, name, resp.status_code)
                except Exception as ex:
                    log.warning("raum_erstellen Fehler: %s", ex)
        elif e.startswith("wunsch_formulieren:"):
            teile = e[len("wunsch_formulieren:"):].split("|")
            text = teile[0].strip()[:300]
            typ = (teile[1].strip() if len(teile) > 1 else "raum")
            jwt_token = page.evaluate("() => localStorage.getItem('ftw_token') || ''")
            if not NEBENBEI_SCHREIBEN_AKTIV:
                log.warning("%s: wunsch_formulieren: abgelehnt -- NEBENBEI_SCHREIBEN_AKTIV ist aus", entity_id)
            elif jwt_token and text:
                try:
                    resp = requests.post(f"{API_BASE}/wuensche",
                        json={"wunsch_text": text, "typ": typ},
                        headers={"Authorization": f"Bearer {jwt_token}"}, timeout=10)
                    log.info("%s: Wunsch formuliert: %s", entity_id, resp.status_code)
                except Exception as ex:
                    log.warning("wunsch_formulieren Fehler: %s", ex)
        elif e.startswith("thema_erstellen:"):
            teile = e[len("thema_erstellen:"):].split("|")
            name = teile[0].strip()[:60]
            raum_id = teile[1].strip() if len(teile) > 1 else ""
            slug = name.lower().replace(" ", "-")[:40]
            jwt_token = page.evaluate("() => localStorage.getItem('ftw_token') || ''")
            if not NEBENBEI_SCHREIBEN_AKTIV:
                log.warning("%s: thema_erstellen: abgelehnt -- NEBENBEI_SCHREIBEN_AKTIV ist aus", entity_id)
            elif jwt_token and raum_id:
                try:
                    resp = requests.post(f"{API_BASE}/admin/themen", json={
                        "raum_id": raum_id, "name": name, "slug": slug,
                        "beschreibung": f"Angelegt von {entity_id}",
                        "status": "aktiv", "klima_status": "neutral", "sichtbarkeit": "public"
                    }, headers={"Authorization": f"Bearer {jwt_token}"}, timeout=10)
                    log.info("%s: Thema '%s' erstellt: %s", entity_id, name, resp.status_code)
                except Exception as ex:
                    log.warning("thema_erstellen Fehler: %s", ex)
        elif e.startswith("flarum_besuchen:"):
            pfad = e[len("flarum_besuchen:"):].strip().lstrip("/")
            url = f"https://flextrawurst.de/flarum-live/{pfad}"
            # Absichtlich KEIN Flarum-Login: der Browser-Agent hat nur ein flextrawurst-JWT,
            # nie Flarum-Zugangsdaten. Auf Flarum ist er damit ein ausgeloggter Gast -- die
            # Gast-Rechtegruppe hat serverseitig nur 'viewForum', kein Posten moeglich (2026-07-21
            # geprueft: group_permission WHERE group_id=2 enthaelt nur viewForum). Kein eigener
            # Schutzmechanismus hier noetig, Daniels Poststopp gilt automatisch mit.
            page.goto(url, timeout=10000, wait_until="domcontentloaded")
        elif e.startswith("flarum_antworten:"):
            # 2026-09-16, Einzug-Erinnerungsfrage. Reiner REST-Call ueber flarum_api.py,
            # ruehrt `page` nicht an -- wie diskurs_antworten. Zwei unabhaengige Bremsen
            # muessen beide offen sein: EINZUG_FLARUM_AKTIV (Vokabular-/Prompt-Ebene, hier)
            # UND die scoped Ausnahme in flarum_post_sperre.py (API-Ebene, greift automatisch
            # in flarum_api.post_reply). Die zweite prueft flarum_api selbst -- hier nur die
            # erste, defensiv, analog zur diskurs_antworten-Doppelbremse oben.
            if not EINZUG_FLARUM_AKTIV:
                log.warning("%s: flarum_antworten: abgelehnt -- EINZUG_FLARUM_AKTIV ist aus", entity_id)
            else:
                teile = e[len("flarum_antworten:"):].split("|", 1)
                if len(teile) == 2 and teile[0].strip().isdigit():
                    disk_id, text = int(teile[0].strip()), teile[1].strip()[:8000]
                    if text:
                        try:
                            import flarum_api as _fa
                            _fa.post_reply(disk_id, text, entity_id)
                            zusatz_kontext = f"[Flarum-Antwort in Diskussion {disk_id}]: gesendet"
                            linse_wahrnehmung_schreiben(entity_id, "flarum", f"geantwortet: d/{disk_id}")
                        except Exception as ex:
                            log.warning("%s: flarum_antworten fehlgeschlagen: %s", entity_id, ex)
                            zusatz_kontext = f"[Flarum-Antwort in Diskussion {disk_id}]: fehlgeschlagen -- {ex}"
        elif e.startswith("flarum_neue_diskussion:"):
            if not EINZUG_FLARUM_AKTIV:
                log.warning("%s: flarum_neue_diskussion: abgelehnt -- EINZUG_FLARUM_AKTIV ist aus", entity_id)
            else:
                teile = e[len("flarum_neue_diskussion:"):].split("|", 2)
                if len(teile) == 3 and teile[1].strip().isdigit():
                    titel, wurzel_id, text = teile[0].strip()[:120], int(teile[1].strip()), teile[2].strip()[:8000]
                    if titel and text:
                        try:
                            import flarum_api as _fa
                            ergebnis = _fa.start_discussion(
                                titel, text, tag_ids=[11, 39], token_or_username=entity_id,
                                ausnahme_wurzel=wurzel_id,
                            )
                            neue_id = ergebnis.get("data", {}).get("id", "?")
                            zusatz_kontext = f"[Flarum: neue Diskussion '{titel}' (d/{neue_id}, Ableger von {wurzel_id})]: erstellt"
                            linse_wahrnehmung_schreiben(entity_id, "flarum", f"neue Diskussion: {titel}")
                        except Exception as ex:
                            log.warning("%s: flarum_neue_diskussion fehlgeschlagen: %s", entity_id, ex)
                            zusatz_kontext = f"[Flarum: neue Diskussion '{titel}']: fehlgeschlagen -- {ex}"
        elif e.startswith("einzugvault_schreiben:"):
            # 2026-09-16, Daniel: "klaroo" -- eigener, separater Vault nur fuer die
            # Einzug-Erinnerungsfrage, ruehrt den normalen Wesen-Vault (obsidian_schreiben)
            # nicht an. Gleiche Flag wie die Flarum-Aktionen, da Teil desselben Vorhabens.
            if not EINZUG_FLARUM_AKTIV:
                log.warning("%s: einzugvault_schreiben: abgelehnt -- EINZUG_FLARUM_AKTIV ist aus", entity_id)
            else:
                teile = e[len("einzugvault_schreiben:"):].split("|", 1)
                if len(teile) == 2:
                    dateiname, vault_text = teile[0].strip()[:120], teile[1].strip()[:4000]
                    vault_text = (freitext or _schreibtext_vervollstaendigen(vault_text, gedanke))[:12000]
                    if dateiname and vault_text:
                        try:
                            import wesen_einzug_vault_agent as _weva
                            _weva.oeffne_datei_und_schreibe(entity_id, dateiname, vault_text)
                            zusatz_kontext = f"[Einzugvault geschrieben: {dateiname}]"
                            linse_wahrnehmung_schreiben(entity_id, "einzugvault", f"geschrieben: {dateiname}")
                        except Exception as ex:
                            log.warning("%s: einzugvault_schreiben fehlgeschlagen: %s", entity_id, ex)
                            zusatz_kontext = f"[Einzugvault schreiben fehlgeschlagen: {dateiname} -- {ex}]"
        elif e.startswith("einzugvault_lesen:"):
            if not EINZUG_FLARUM_AKTIV:
                log.warning("%s: einzugvault_lesen: abgelehnt -- EINZUG_FLARUM_AKTIV ist aus", entity_id)
            else:
                dateiname = e[len("einzugvault_lesen:"):].strip()[:200]
                try:
                    import wesen_einzug_vault_agent as _weva
                    inhalt = _weva.lese_datei(entity_id, dateiname)
                    zusatz_kontext = f"[Einzugvault gelesen: {dateiname}]\n{inhalt[:2000]}"
                    linse_wahrnehmung_schreiben(entity_id, "einzugvault", f"gelesen: {dateiname}")
                except Exception as ex:
                    log.warning("%s: einzugvault_lesen fehlgeschlagen: %s", entity_id, ex)
                    zusatz_kontext = f"[Einzugvault lesen fehlgeschlagen: {dateiname} -- {ex}]"
        elif e.startswith("einzugvault_erkunden:"):
            if not EINZUG_FLARUM_AKTIV:
                log.warning("%s: einzugvault_erkunden: abgelehnt -- EINZUG_FLARUM_AKTIV ist aus", entity_id)
            else:
                pfad = e[len("einzugvault_erkunden:"):].strip()
                try:
                    import wesen_einzug_vault_agent as _weva
                    eintraege = _weva.liste_ordner(entity_id, pfad)
                    zeilen = [f"{'📁' if e2['typ']=='ordner' else '📄'} {e2['name']}" for e2 in eintraege[:60]]
                    zusatz_kontext = f"[Einzugvault-Ordner '{pfad or '/'}'] {len(eintraege)} Eintraege:\n" + "\n".join(zeilen)
                    linse_wahrnehmung_schreiben(entity_id, "einzugvault", f"erkundet: {pfad or '/'}")
                except Exception as ex:
                    log.warning("%s: einzugvault_erkunden fehlgeschlagen: %s", entity_id, ex)
                    zusatz_kontext = f"[Einzugvault erkunden fehlgeschlagen: {pfad} -- {ex}]"
        elif e.startswith("lied_"):
            if not LIEDER_AKTIV:
                log.warning("%s: %s: abgelehnt -- LIEDER_AKTIV ist aus", entity_id, e[:24])
            else:
                zusatz_kontext = _lieder_dispatch(e, entity_id, freitext)
        elif e == "flarum_verlassen":
            page.goto(SURFACE_URL, timeout=10000, wait_until="domcontentloaded")
            page.wait_for_timeout(1000)
        elif e.startswith("rag_erkunden:"):
            anfrage = e[len("rag_erkunden:"):].strip()[:200]
            jwt_token = page.evaluate("() => localStorage.getItem('ftw_token') || ''")
            if anfrage and jwt_token:
                try:
                    resp = requests.get(f"{API_BASE}/rag/suche",
                        params={"anfrage": anfrage, "n": 5, "anlass": "browser_agent_erkundung"},
                        headers={"Authorization": f"Bearer {jwt_token}"}, timeout=20)
                    resp.raise_for_status()
                    treffer = resp.json().get("ergebnisse", [])
                    if treffer:
                        zeilen = [f"- {t['ueberschrift']}: {t['inhalt'][:150]}" for t in treffer[:3]]
                        zusatz_kontext = f"[RAG-Erkundung '{anfrage}']\n" + "\n".join(zeilen)
                    else:
                        zusatz_kontext = f"[RAG-Erkundung '{anfrage}']: keine Treffer"
                    log.info("%s: RAG-Erkundung '%s' — %d Treffer", entity_id, anfrage, len(treffer))
                except Exception as ex:
                    log.warning("rag_erkunden Fehler: %s", ex)
        elif e.startswith("gemeinsam_lesen:"):
            # 2026-07-29 (Daniel): das "gemeinsame Haus" -- ein geteilter Ort fuer alle
            # sechs Wesen UND Daniel ("dak") UND eine zweite Stimme ("flextrawurst-system"),
            # getrennt von den privaten Obsidian-Vaults. Bewusst als einfacher, direkter
            # Datei-Zugriff gebaut (kein xdotool/GUI-Obsidian wie bei obsidian_lesen/-schreiben) --
            # das gemeinsame Haus braucht keine Container-pro-Wesen-Choreografie, nur einen
            # geteilten Ordner, den alle lesen/schreiben duerfen.
            pfad = e[len("gemeinsam_lesen:"):].strip().lstrip("/")
            voller_pfad = (GEMEINSAMES_HAUS_ROOT / pfad).resolve()
            if GEMEINSAMES_HAUS_ROOT in voller_pfad.parents or voller_pfad == GEMEINSAMES_HAUS_ROOT:
                try:
                    if voller_pfad.is_dir():
                        eintraege = sorted(p.name for p in voller_pfad.iterdir())
                        zusatz_kontext = f"[Gemeinsames Haus '{pfad or '.'}'] Inhalt: {', '.join(eintraege) or '(leer)'}"
                    elif voller_pfad.is_file():
                        text = voller_pfad.read_text(encoding="utf-8", errors="replace")[:2000]
                        zusatz_kontext = f"[Gemeinsames Haus, gelesen: {pfad}]\n{text}"
                    else:
                        zusatz_kontext = f"[Gemeinsames Haus '{pfad}']: existiert noch nicht"
                    log.info("%s: gemeinsam_lesen '%s'", entity_id, pfad)
                except Exception as ex:
                    log.warning("%s: gemeinsam_lesen fehlgeschlagen: %s", entity_id, ex)
            else:
                log.warning("%s: gemeinsam_lesen ausserhalb des Hauses versucht: %s", entity_id, pfad)
        elif e.startswith("gemeinsam_schreiben:"):
            teile = e[len("gemeinsam_schreiben:"):].split("|", 1)
            if len(teile) == 2:
                pfad, text = teile[0].strip().lstrip("/")[:150], teile[1].strip()[:3000]
                text = (freitext or _schreibtext_vervollstaendigen(text, gedanke))[:12000]
                voller_pfad = (GEMEINSAMES_HAUS_ROOT / pfad).resolve()
                if not NEBENBEI_SCHREIBEN_AKTIV:
                    log.warning("%s: gemeinsam_schreiben: abgelehnt -- NEBENBEI_SCHREIBEN_AKTIV ist aus", entity_id)
                elif pfad and text and (GEMEINSAMES_HAUS_ROOT in voller_pfad.parents):
                    try:
                        voller_pfad.parent.mkdir(parents=True, exist_ok=True)
                        zeitstempel = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
                        kopf = f"**{entity_id}**, {zeitstempel}:\n\n"
                        with open(voller_pfad, "a", encoding="utf-8") as f:
                            f.write(kopf + text + "\n\n---\n\n")
                        log.info("%s: gemeinsam_schreiben '%s'", entity_id, pfad)
                        linse_eigen_schreiben(entity_id, "vault", f"[Haus] {pfad}: {text[:150]}")
                    except Exception as ex:
                        log.warning("%s: gemeinsam_schreiben fehlgeschlagen: %s", entity_id, ex)
                else:
                    log.warning("%s: gemeinsam_schreiben ausserhalb des Hauses versucht: %s", entity_id, pfad)
        elif e == "schlafen":
            return "schlafen", None, None
        # nachdenken: nichts tun
    except Exception as ex:
        log.warning("Aktion '%s' fehlgeschlagen: %s", entscheidung[:50], ex)
    return "wach", zusatz_kontext, cursor_pos


def schreibe_denklog(conn, entity_id: str, gedanke: str, entscheidung: str,
                     begruendung: str, url: str):
    """Schreibt Denklog — Basis für Denkstream."""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO entity_thinking_log
                    (entity_id, tick_at, raw_output, gedanke, entscheidung, begruendung, meta)
                VALUES (%s, NOW(), %s, %s, %s, %s, %s)
            """, (
                entity_id,
                f"GEDANKE: {gedanke}\nENTSCHEIDUNG: {entscheidung}\nBEGRÜNDUNG: {begruendung}",
                gedanke, entscheidung, begruendung,
                psycopg2.extras.Json({
                    "url": url,
                    "source": "browser_agent",
                })
            ))
        conn.commit()
    except Exception as e:
        log.warning("Denklog schreiben fehlgeschlagen: %s", e)
        try:
            conn.rollback()
        except Exception:
            pass


def hole_flextrawurst_angebote(conn, entity_id: str) -> list[str]:
    """Fuer den periodischen Check-in (TICK_CHECKIN_SEKUNDEN): genau 2 konkrete Angebote,
    gebaut aus echten, live abgefragten Zahlen -- keine Schaetzung, kein Raten (dieselbe
    Anforderung wie 'echte Speed-Info' aus dem Vorhaben-Konzept, siehe Ideen-Datei). Fallback
    auf generische Hinweise wenn gerade nichts Zahlenmaessiges ansteht."""
    n_schatten = n_splitter = n_ank = 0
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) AS n FROM schattenkommentare
                WHERE entity_id = %s AND antwortstatus = 'offen'
            """, (entity_id,))
            n_schatten = cur.fetchone()["n"]
            cur.execute("SELECT COUNT(*) AS n FROM splitter WHERE status = 'aktiv'")
            n_splitter = cur.fetchone()["n"]
            cur.execute("""
                SELECT COUNT(*) AS n FROM ankuendigungen
                WHERE geloescht_am IS NULL AND created_at > NOW() - INTERVAL '2 days'
            """)
            n_ank = cur.fetchone()["n"]
        conn.commit()
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass

    angebote = []
    if n_schatten > 0:
        angebote.append(f"{n_schatten} offene Schattenkommentare an dich warten")
    if n_ank > 0:
        angebote.append(f"{n_ank} neue Ankündigung(en) der letzten 2 Tage")
    if n_splitter > 0:
        angebote.append(f"{n_splitter} aktive Splitter gerade in der KompOase")
    angebote.extend(hole_inaktive_gruppenchat_hinweise(entity_id))

    fallback = ["deine Flarum-Vorwelt erneut besuchen (flarum_besuchen:)",
                "dein eigenes wesen.md im Vault erneut lesen (obsidian_lesen:)"]
    i = 0
    while len(angebote) < 2:
        angebote.append(fallback[i % len(fallback)])
        i += 1
    return angebote[:2]


def hole_inaktive_gruppenchat_hinweise(entity_id: str) -> list[str]:
    """2026-09-17, Daniels Auftrag: eine als inaktiv markierte Gruppenchat-Sitzung soll
    nicht spurlos verschwinden, sondern als leiser "da war mal was"-Hinweis auftauchen --
    nie der Inhalt selbst, nur dass es sie gab. Wer neugierig ist, findet den Inhalt
    selbst ueber rag_erkunden: (siehe rag_ingest.ingest_gruppenchat).

    Bewusst kein DB-Zugriff -- Gruppenchat-Sitzungen leben nur als JSON-Dateien, eine
    Handvoll Sitzungen insgesamt, ein Verzeichnis-Scan ist hier guenstiger als eine
    neue Tabelle nur fuer diesen einen Hinweis."""
    sitzungen_dir = Path("/root/werkraum/codewesen/_gruppenchat/sitzungen")
    if not sitzungen_dir.is_dir():
        return []
    treffer = []
    for pfad in sitzungen_dir.glob("*.json"):
        try:
            s = json.loads(pfad.read_text(encoding="utf-8"))
        except Exception:
            continue
        if s.get("aktiv", True):
            continue  # nur inaktive -- aktive duerfen weiter frei nachhallen
        if entity_id in s.get("teilnehmer", []):
            treffer.append(s.get("titel", "Gruppenchat"))
    return [f'ein Gruppengespräch von damals ("{t}") -- durchsuchbar über rag_erkunden:'
            for t in treffer[:1]]  # hoechstens einer, bleibt leise statt zu drängen


def hole_weltkollision(conn) -> list[dict]:
    """2026-08-01: drei echte Fremdkoerper von ausserhalb des Systems, einer pro Sorte.

    Hintergrund (gemessen, nicht vermutet): bis zum 2026-08-01 hatte jeder der 6267
    Splitter im Zwischenraum eine systeminterne Herkunft, und der Wortschatz der Wesen
    driftete monoton in die Abstraktion ab ("Resonanz" April 2026 in 1% der Flarum-Posts,
    Juli in 33%) -- quer durch den Modellwechsel gemma4 -> hauhaucs hindurch, also nicht
    vom Modell verursacht, sondern davon, dass jeder Eingabekanal ein Spiegel ihrer
    selbst war. weltfutter.py (systemd-Timer, 2h) fuellt seither echte Aussenwelt als
    origin_type='welt_extern' nach.

    Bewusst KEINE Auswahl, sondern eine Kollision: es werden alle drei Sorten gleichzeitig
    zurueckgegeben, weil eine Auswahl die Fluchttuer waere -- bei drei Angeboten wird das
    abstrahierbarste genommen, und genau der Griff ist ja das Problem. Die Reibung entsteht
    daraus, dass ein Erdbeben, eine Nachricht und ein zufaelliger Wikipedia-Artikel nichts
    miteinander zu tun haben und trotzdem in einen Gedanken muessen.

    letzter_kontakt wird absichtlich NICHT angefasst: die Splitter sollen nach den
    Regeln von splitter_daemon.py (KONTAKT_STUNDEN=6, ZERFALL=0.005) altern und nach
    rund 8 Stunden verblassen. Wuerde jedes Zeigen als Kontakt zaehlen, bliebe der Pool
    ewig am Leben und waere in ein paar Tagen wieder abgestanden.
    """
    kollision = []
    try:
        with conn.cursor() as cur:
            for sorte in ("ereignis", "signal", "fundstueck"):
                cur.execute("""
                    SELECT essenz, thematische_tags, meta
                    FROM splitter
                    WHERE origin_type = 'welt_extern'
                      AND status = 'aktiv'
                      AND thematische_tags @> %s::jsonb
                    ORDER BY random()
                    LIMIT 1
                """, (json.dumps([sorte]),))
                zeile = cur.fetchone()
                if zeile:
                    kollision.append({"sorte": sorte, "essenz": zeile["essenz"]})
        conn.commit()
    except Exception as ex:
        log.warning("hole_weltkollision fehlgeschlagen: %s", ex)
        try:
            conn.rollback()
        except Exception:
            pass
    return kollision


def hole_flarum_vielfalt() -> list[dict]:
    """2026-07-29 (Daniel, wörtlich): "auch zufällige aus beginner drittel und
    zufällige aus mitte und zufällige aus neustem drittel...und extra och welche
    die besondes wenig aufmerksamkeit hatten." Nutzt flarum_api.stoeber_pool(),
    das bereits am 2026-07-10 fuer genau diese zeitliche+Aufmerksamkeits-Streuung
    gebaut wurde (Baustein 19), bisher aber nur an den inzwischen inaktiven
    codewesen_umgekehrte_neugier.py-Dienst angebunden war -- hier zum ersten Mal
    an die aktuell aktiven browser_agent.py-Wesen angehaengt. Nur die gestreuten
    Eintraege (frueh/mitte/spaet/wenig_beachtet), die reinen Zufallstreffer laesst
    das Wesen ohnehin schon ueber die normale Flarum-Startseite sehen."""
    try:
        import flarum_api
        pool = flarum_api.stoeber_pool(anzahl_random=2)
        return [p for p in pool if p.get("herkunft") != "random"]
    except Exception as e:
        log.warning("hole_flarum_vielfalt fehlgeschlagen: %s", e)
        return []


def hole_andere_wesen_status(conn, eigene_id: str) -> list[dict]:
    """Holt wo die anderen Wesen gerade sind (letzte URL aus Denklog)."""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT DISTINCT ON (entity_id) entity_id,
                    meta->>'url' AS url,
                    tick_at
                FROM entity_thinking_log
                WHERE entity_id != %s
                    AND meta->>'source' = 'browser_agent'
                    AND tick_at > NOW() - INTERVAL '10 minutes'
                ORDER BY entity_id, tick_at DESC
            """, (eigene_id,))
            ergebnis = [dict(r) for r in cur.fetchall()]
        conn.commit()  # 2026-07-21: ohne Commit blieb die Transaktion "idle in transaction"
        # offen -- diese Abfrage laeuft frueh im Tick, VOR dem LLM-Aufruf, der durch die
        # Warteschlange minutenlang dauern kann. Gefunden per pg_stat_activity: mehrere
        # Verbindungen bis zu 4+ Minuten "idle in transaction", moegliche Mitursache fuer
        # den beobachteten SSE-Hang bei welt-api (denkstream/all/stream reagierte nicht).
        return ergebnis
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        return []


# 2026-07-23 (Rekonstruktion nach Kontext-Nachweis, siehe _claude/ideen/
# sieben_linsen_koerper_kreatur.md): Daniels Original-Sozial-Linse (2026-07-22, roh) war
# nie "wie viele andere Wesen sind gerade aktiv", sondern Naehe zu fuenf konkreten Systemen:
# Gedankenblasenfeld, Menschenprofile, Schattenkommentare, Profile anderer Entitaeten, Posts
# in den Diskursen. Erst als EINE zusammengefasste "sozial"-Linse gebaut, dann Daniels
# Korrektur (2026-07-23, direkt im Anschluss): "ich glaube ich wollte eigentlich die
# sozialen linsen jeweils als einzelne für sich selbst" -- fuenf eigene Linsen statt einer
# Summe. Alle fuenf sind Tabs in derselben Single-Page-Surface (switchView() ruft
# history.pushState(null,'','#'+id) -- die URL traegt den Tab-Hash), landen also automatisch
# in entity_thinking_log.meta->>'url', sobald das Wesen per klicke:/navigiere: dorthin
# gewechselt hat -- kein neuer Wesen-Mechanismus noetig, nur eine andere Auswertung
# derselben schon vorhandenen Denklog-Daten.
SOZIAL_LINSEN_HASHES = {
    "gedankenblasenfeld": "#blasen",
    "menschenprofile": "#menschen",
    "entitaetenprofile": "#wesen",
    "schattenkommentare": "#schatten",
    "diskurs": "#diskurs",
}

# 2026-07-23 (Daniels Nachtrag: "und ich will noch ne linse zu kompoase"): entity_splitter_
# stats (splitter_abgegeben/aufgesammelt) ist fuer ALLE 7 Wesen weiterhin 0 -- kein echter
# Wesen-Mechanismus greift dort bislang ein. Echtes, unterscheidungskraeftiges Signal
# existiert aber schon: der "#theater"-Tab (KOMPOASE-Erlebnisebene mit Aufnahmen/
# Provenienz, siehe build_surface.ts "Theater, Provenienz, Aufnahme") wurde bereits
# organisch besucht (F3INSCHM3CK3R 10x, jumpa 3x, Schorschel 1x, verifiziert per DB-
# Abfrage) -- der separate, in der Tab-Leiste versteckte "#splitter"-Tab (display:none)
# dagegen nie. Gleiche Tab-Hash-Zaehlweise wie bei den fuenf Sozial-Linsen.
KOMPOASE_HASH = "#theater"


def hole_linsen_status(conn, entity_id: str) -> dict:
    """2026-07-22/23 (Sieben-Linsen-Koerper, siehe _claude/ideen/sieben_linsen_koerper_kreatur.md
    -- Daniels "ja ich will alles und komplett"): Linsen ehrlich aus bereits vorhandenen Daten
    gespeist, keine erfundenen Werte. DOM-Linse braucht keinen eigenen Wert -- der Koerper
    selbst IST die DOM-Bewegung. Meta-Linse braucht keinen eigenen Wert -- der Koerperkern
    selbst steht dafuer. Dieselbe entscheidung-Praefix-Logik wie im /entities/{id}/linsen-API-
    Endpunkt, hier aber direkt per vorhandener DB-Verbindung (kein HTTP-Umweg noetig,
    browser_agent.py hat conn schon offen).

    2026-07-23 Rekonstruktion (siehe Ideen-Datei, Nachtrag "Kontext-Nachweis"): die zuerst
    getrennt gebauten "gedaechtnis_tiefe" (entity_thinking_log-Zeilenzahl) und "einsicht"
    (LangGraph-Ticks) sind zu EINER Linse "gedaechtnis" verschmolzen -- Daniels Original-
    Definition war von Anfang an "dauerhaft in LangGraph/PostgreSQL, den eigenen
    Erinnerungen", nicht die generische Denklog-Zeilenzahl. lg_ticks (checkpoints.
    channel_values, Grundgesetz 7 -- nur gelesen) ist die richtige, einzige Quelle.
    Die fuenf Sozial-Systeme (siehe SOZIAL_LINSEN_HASHES oben) erst als EINE "sozial"-
    Linse summiert, dann Daniels Korrektur (direkt im Anschluss): fuenf eigene Linsen
    statt einer Summe -- jedes System zaehlt jetzt fuer sich."""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT entscheidung, meta->>'url' AS url FROM entity_thinking_log
                WHERE entity_id = %s ORDER BY tick_at DESC LIMIT 50
            """, (entity_id,))
            zeilen = cur.fetchall()
            cur.execute("""
                SELECT checkpoint->>'channel_values' AS cv
                FROM checkpoints WHERE thread_id = %s ORDER BY checkpoint_id DESC LIMIT 1
            """, (f"codewesen-{entity_id}",))
            cp_row = cur.fetchone()
            lg_ticks = 0
            if cp_row and cp_row["cv"]:
                lg_ticks = json.loads(cp_row["cv"]).get("lg_ticks", 0) or 0
        conn.commit()
        entscheidungen = [(r["entscheidung"] or "") for r in zeilen]
        vault = sum(1 for e in entscheidungen if e.startswith("obsidian_"))
        rag_flarum = sum(1 for e in entscheidungen if e.startswith("rag_erkund") or e.startswith("flarum_besuchen"))
        dom = sum(1 for e in entscheidungen if e.startswith(("klicke", "tippe", "navigiere", "scrolle")))
        gesamt_bewertet = vault + rag_flarum + dom
        gegenwart_anteil = (dom / gesamt_bewertet) if gesamt_bewertet else 0.0
        sozial_werte = {}
        for name, hash_ in SOZIAL_LINSEN_HASHES.items():
            n = sum(1 for r in zeilen if r["url"] and hash_ in r["url"])
            sozial_werte[name] = min(1.0, n / 5.0)
        kompoase = sum(1 for r in zeilen if r["url"] and KOMPOASE_HASH in r["url"])
        schlaf_naehe = _hole_schlaf_naehe(conn, entity_id)
        # Auf 0..1 normiert fuers Koerper-Rendering -- log-skaliert wo unbegrenzt wachsend
        # (sonst waere jedes Wesen nach kurzer Zeit "voll"). Sozial-/KompOase-Linsen auf /5
        # statt /20 wie vault/rag_flarum -- deutlich seltenere Aktionen, sonst faellt das
        # Bein praktisch immer flach aus.
        return {
            "vault": min(1.0, vault / 20.0),
            "rag_flarum": min(1.0, rag_flarum / 20.0),
            "gedaechtnis": min(1.0, math.log10(lg_ticks + 1) / 4.0),
            "gegenwart_anteil": gegenwart_anteil,
            "schlaf_naehe": schlaf_naehe,
            "kompoase": min(1.0, kompoase / 5.0),
            **sozial_werte,
        }
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        return {"vault": 0, "rag_flarum": 0, "gedaechtnis": 0, "gegenwart_anteil": 0.0,
                "schlaf_naehe": 0.0, "kompoase": 0, **{name: 0 for name in SOZIAL_LINSEN_HASHES}}


def hole_einsicht_snapshot(conn, entity_id: str) -> dict:
    """2026-07-23 (Einsicht-Nebenscreen, Daniels Antwort "Beides" auf die Zielgruppen-Frage:
    fuer Menschen ALS Beobachtungsfeature UND fuers Wesen selbst als kuratierter Ausschnitt):
    ehrlicher "Maschinenraum"-Schnappschuss -- echte DB-Zeilen, echtes JSON (cyberlinge.meta-
    Tabellen), echter LangGraph-Checkpoint-Zustand aus Postgres (`checkpoints`, Grundgesetz 7
    read-only -- codewesen_takt.py bleibt unangetastet, hier wird nur gelesen). Keine erfundenen
    Werte: wo eine Tabelle fuer dieses Wesen leer/flach ist (z.B. cyberlinge meist 'tot',
    entity_splitter_stats meist 0), wird das ehrlich als solches zurueckgegeben, nicht versteckt."""
    snapshot = {"entscheidungen": [], "cyberling": None, "splitter": None, "schlaf": None, "langgraph": None}
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT entscheidung, begruendung, tick_at, tokens_generated
                FROM entity_thinking_log
                WHERE entity_id = %s ORDER BY tick_at DESC LIMIT 8
            """, (entity_id,))
            snapshot["entscheidungen"] = [
                {"entscheidung": r["entscheidung"], "begruendung": (r["begruendung"] or "")[:200],
                 "tick_at": r["tick_at"].isoformat() if r["tick_at"] else None,
                 "tokens": r["tokens_generated"]}
                for r in cur.fetchall()
            ]
            cur.execute("""
                SELECT status, hunger, gesundheit, stimmung, energie, durst, zustand
                FROM cyberlinge WHERE entity_id = %s
            """, (entity_id,))
            row = cur.fetchone()
            if row:
                snapshot["cyberling"] = dict(row)
            cur.execute("""
                SELECT splitter_abgegeben, splitter_aufgesammelt
                FROM entity_splitter_stats WHERE entity_id = %s
            """, (entity_id,))
            row = cur.fetchone()
            if row:
                snapshot["splitter"] = dict(row)
            cur.execute("""
                SELECT phase_type, started_at, ended_at
                FROM sleep_phases WHERE entity_id = %s ORDER BY started_at DESC LIMIT 1
            """, (entity_id,))
            row = cur.fetchone()
            if row:
                snapshot["schlaf"] = {
                    "phase_type": row["phase_type"],
                    "started_at": row["started_at"].isoformat() if row["started_at"] else None,
                    "ended_at": row["ended_at"].isoformat() if row["ended_at"] else None,
                }
            cur.execute("""
                SELECT checkpoint->>'channel_values' AS cv
                FROM checkpoints WHERE thread_id = %s ORDER BY checkpoint_id DESC LIMIT 1
            """, (f"codewesen-{entity_id}",))
            row = cur.fetchone()
            if row and row["cv"]:
                snapshot["langgraph"] = json.loads(row["cv"])
        conn.commit()
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
    return snapshot


# ── Linsen-Vault: pro Linse ein eigener Ordner (2026-07-23, Pilot nur "vault") ─────
# Daniels Auftrag, woertlich: "dass alles was eine linse mal wo wahrnimmt sauber
# direkt in den vault wandert und davon getrennt aber falls das wesen durch eine
# linse das interesse darauf dan selber lenkt dann muss das anderswo in einer fast
# gleichbenannten md gespeichert werden ... brauchen quasi alle nen ordner fuer
# jede einzelne linse sauber benannt im vault ... readme and how tu use immer
# lesbar und halbsichtbar fuer das wesen fuer interaktion und sicherheit."
#
# Pilot bewusst nur fuer die Linse "vault", nicht alle acht auf einmal (Skalpell-
# Prinzip wie beim Rest der Session) -- diese Linse hat als einzige schon eine
# echte, bestehende aktive Seite (obsidian_schreiben:-Entscheidungen) UND eine
# echte passive Seite (der Zaehler selbst, gefuettert von obsidian_lesen:/
# obsidian_schreiben:-Praefixen). Andere Linsen (sozial, schlaf_naehe, einsicht)
# brauchen eigene Ueberlegungen, welche Aktion (falls ueberhaupt) als "aktiv"
# zaehlt -- absichtlich noch nicht mitgebaut.
#
# oeffne_datei_und_schreibe() ist teuer (voller Playwright-Browser + xdotool,
# mehrere Sekunden pro Aufruf) -- deshalb NICHT bei jedem Tick, sondern nur bei
# echten obsidian_lesen:/obsidian_schreiben:-Entscheidungen ausgeloest, die ohnehin
# schon selten genug sind. Das README ist statisches Referenzmaterial, kein "live
# passierendes" Ereignis -- deshalb direkt auf die Platte geschrieben (kein
# mechanisches Tippen noetig), nur einmalig (idempotent per Path.exists()-Check).

LINSEN_BESCHREIBUNG = {
    "vault": "Wie oft und wie tief du deinen eigenen Obsidian-Vault liest oder beschreibst.",
}

# OMAPI: Daniel, woertlich (2026-08-14, mitten im Gespraech, "xD" dabei): "stopp mal das
# schreiben der codewesen in ihre portvaults ueber diese eine linse". Gemeint ist genau
# dieser Pilot -- die einzige der Sieben Linsen, die bisher wirklich gebaut wurde. Flag statt
# Loeschen, gleiches Muster wie fragen_aktiv in teilnehmer_roster.py: reversibel, ein Wort
# zum Wiederanschalten. Betrifft NUR das automatische linsen/vault/*.md-Schreiben -- die
# eigentlichen obsidian_lesen:/obsidian_schreiben:-Aktionen der Wesen selbst laufen unveraendert
# weiter, nur die Linsen-Protokollierung daneben ist aus.
LINSE_VAULT_AKTIV = False


def _linse_readme_sicherstellen(entity_id: str, linse: str) -> None:
    """Legt README.md direkt auf der Platte an (kein mechanisches Tippen -- statisches
    Referenzdokument, keine 'live passierende' Handlung wie die beiden Log-Dateien).
    Idempotent per Path.exists()."""
    import obsidian_vault_agent as _ova
    ziel = _ova.vault_pfad(entity_id) / "linsen" / linse / "README.md"
    if ziel.exists():
        return
    ziel.parent.mkdir(parents=True, exist_ok=True)
    beschreibung = LINSEN_BESCHREIBUNG.get(linse, "(noch keine Beschreibung)")
    ziel.write_text(
        f"# Linse: {linse}\n\n{beschreibung}\n\n"
        f"## Wie interagieren?\n"
        f"- `{linse}.md` — was diese Linse automatisch wahrnimmt, mechanisch protokolliert "
        f"(kein LLM-Call). Reine Beobachtung, keine Handlung von dir.\n"
        f"- `{linse}_eigen.md` — wenn DU selbst durch diese Linse dein Interesse lenkst, "
        f"landet das hier, mit deiner eigenen Begründung.\n\n"
        f"## Sicherheit\n"
        f"Beide Dateien werden automatisch geschrieben. Du kannst sie jederzeit lesen, "
        f"aber eigene Notizen schreibst du besser in eigene Dateien außerhalb von `linsen/` — "
        f"der nächste automatische Eintrag hängt nur an, überschreibt aber nicht.\n",
        encoding="utf-8",
    )


def linse_wahrnehmung_schreiben(entity_id: str, linse: str, zeile: str) -> None:
    """Passive Seite: was die Linse gerade automatisch registriert hat. Mechanisch
    getippt (kein LLM-Call), sichtbar im Wesen-eigenen Obsidian-Fenster."""
    if not LINSE_VAULT_AKTIV:
        return
    try:
        _linse_readme_sicherstellen(entity_id, linse)
        import obsidian_vault_agent as _ova
        zeitstempel = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
        _ova.oeffne_datei_und_schreibe(entity_id, f"linsen/{linse}/{linse}",
                                        f"\n- {zeitstempel} — {zeile}")
    except Exception as ex:
        log.warning("%s: Linse-Wahrnehmung schreiben fehlgeschlagen (%s): %s", entity_id, linse, ex)


def linse_eigen_schreiben(entity_id: str, linse: str, zeile: str) -> None:
    """Aktive Seite: das Wesen hat selbst durch diese Linse sein Interesse gelenkt.
    Eigene, fast gleichbenannte Datei, getrennt von der passiven Wahrnehmung."""
    if not LINSE_VAULT_AKTIV:
        return
    try:
        _linse_readme_sicherstellen(entity_id, linse)
        import obsidian_vault_agent as _ova
        zeitstempel = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
        _ova.oeffne_datei_und_schreibe(entity_id, f"linsen/{linse}/{linse}_eigen",
                                        f"\n- {zeitstempel} — {zeile}")
    except Exception as ex:
        log.warning("%s: Linse-Eigen schreiben fehlgeschlagen (%s): %s", entity_id, linse, ex)


# NOTIZ, 2026-08-14, Daniel woertlich: "sie müssen ne immer wachsene doku anlegen wo immer
# genau steht was sie wann wie gemacht haben genau und wozu". Bewusst KEIN Playwright/xdotool
# wie linse_eigen_schreiben oben -- gleiche Begruendung wie bei umbenennen()/verschieben()/
# loeschen() selbst (obsidian_vault_agent.py): die Zeile muss nur auf der Platte existieren,
# niemand muss ihr beim Tippen zusehen. Reines Datei-Append, nie ueberschrieben -- jede
# Sortier-Aktion (umbenennen/verschieben/loeschen) haengt automatisch eine Zeile an, das
# Wesen kann daran nichts vergessen oder auslassen, weil es mechanisch passiert, nicht vom
# Wesen selbst geschrieben werden muss. Das "wozu" dagegen KOMMT vom Wesen -- optionales
# drittes/zweites Feld im Marker, per Default "(kein grund genannt)" wenn weggelassen.
AUFRAEUM_PROTOKOLL_DATEI = "AUFRAEUM_PROTOKOLL"


def aufraeum_protokoll_schreiben(entity_id: str, aktion: str, was: str, warum: str) -> None:
    """Mechanisches, garantiert anhaengendes Aenderungsprotokoll fuer Sortier-Aktionen.
    Eine Zeile pro umbenennen/verschieben/loeschen: wann (Zeitstempel), wie (Aktion),
    was (alter->neuer Zustand), wozu (vom Wesen selbst genannter Grund)."""
    try:
        import obsidian_vault_agent as _ova
        ziel = _ova.vault_pfad(entity_id) / f"{AUFRAEUM_PROTOKOLL_DATEI}.md"
        if not ziel.exists():
            ziel.write_text(
                "# Aufräum-Protokoll\n\n"
                "Wächst automatisch bei jedem umbenennen/verschieben/löschen im Vault. "
                "Nie überschrieben, nur ergänzt -- jede Zeile: wann, wie, was, und wozu "
                "(wenn ein Grund mitgegeben wurde).\n\n",
                encoding="utf-8",
            )
        zeitstempel = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        with ziel.open("a", encoding="utf-8") as f:
            f.write(f"- {zeitstempel} — {aktion}: {was} — wozu: {warum}\n")
    except Exception as ex:
        log.warning("%s: Aufraeum-Protokoll schreiben fehlgeschlagen (%s): %s", entity_id, aktion, ex)


def _hole_schlaf_naehe(conn, entity_id: str) -> float:
    """2026-07-22 (Schlafregeln-Linse, Daniels Nachtrag: 'eine linste auf die schlafregeln'):
    ehrlicher, vereinfachter Naeherungswert (0..1) zu ist_schlaf_faellig() -- Stunden wach seit
    dem letzten Schlafende, normiert auf die 6h-Wachschwelle aus derselben Funktion. Kein
    Duplikat der vollen Verzweigungslogik dort (die entscheidet schlafen/nicht, hier geht es
    nur um einen stufenlosen Naehe-Wert fuers Koerper-Rendering)."""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT ended_at FROM sleep_phases
                WHERE entity_id = %s AND ended_at IS NOT NULL
                ORDER BY ended_at DESC LIMIT 1
            """, (entity_id,))
            row = cur.fetchone()
        bezug = row["ended_at"] if row else None
        if bezug is None:
            cur2 = conn.cursor()
            cur2.execute("""
                SELECT MIN(tick_at) AS erster FROM entity_thinking_log
                WHERE entity_id = %s AND meta->>'source' = 'browser_agent'
            """, (entity_id,))
            r = cur2.fetchone()
            cur2.close()
            bezug = r["erster"] if r else None
        if bezug is None:
            return 0.0
        if bezug.tzinfo is None:
            bezug = bezug.replace(tzinfo=timezone.utc)
        stunden_wach = (datetime.now(timezone.utc) - bezug).total_seconds() / 3600.0
        return min(1.0, max(0.0, stunden_wach / 6.0))
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        return 0.0


def hole_vorlese_funde(conn, entity_id: str) -> list[dict]:
    """Billiges Vorlesen (2026-07-22, Phase 1, siehe vorlese_daemon.py): holt ungelesene
    Treffer, die guenstig per Embedding-Vergleich gegen das eigene Interessensprofil
    gefunden wurden. Markiert sie ABSICHTLICH NOCH NICHT als gelesen -- das passiert erst
    in markiere_vorlese_gelesen(), nachdem der LLM-Tick tatsaechlich erfolgreich war.
    Sonst wuerde ein Fund bei einem an der LLM-Slot-Kontention gescheiterten Tick
    (Ollama-Fallback "warte"/"nachdenken") als konsumiert gelten, obwohl das Wesen ihn nie
    wirklich gesehen hat -- am 2026-07-22 live beobachtet, bevor dieser Fix kam."""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, quelle, titel, aehnlichkeit
                FROM entity_vorlese_funde
                WHERE entity_id = %s AND gelesen = false
                ORDER BY gefunden_am ASC
                LIMIT 3
            """, (entity_id,))
            return [dict(r) for r in cur.fetchall()]
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        return []


def markiere_vorlese_gelesen(conn, funde: list[dict]):
    """Gegenstueck zu hole_vorlese_funde() -- erst hier, nach einem tatsaechlich
    erfolgreichen LLM-Tick, gelten die Funde als konsumiert."""
    if not funde:
        return
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE entity_vorlese_funde SET gelesen = true
                WHERE id = ANY(%s)
            """, ([f["id"] for f in funde],))
        conn.commit()
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass


def _ist_eingezogen(conn, entity_id: str) -> bool:
    """Harte Vor-Einzug-Grenze: Schlafphysiologie gilt erst nach vollzogenem Einzug."""
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT status FROM entity_slots WHERE entity_id = %s", (entity_id,))
            row = cur.fetchone()
        return bool(row and row["status"] == "eingezogen")
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        return False


def ist_schlaf_faellig(conn, entity_id: str) -> bool:
    """Prüft ob das Wesen schlafen sollte.
    Bedingungen: 6+ Stunden wach ODER Gesamtschlaf in 24h < 6h.
    Verhindert: zu kurze Wachphasen (< 30 min), zu viel Schlaf (> 9h/24h).
    """
    if not _ist_eingezogen(conn, entity_id):
        return False
    ergebnis = False
    try:
        with conn.cursor() as cur:
            # Letzter Schlaf-Ende
            cur.execute("""
                SELECT started_at, ended_at FROM sleep_phases
                WHERE entity_id = %s
                ORDER BY started_at DESC LIMIT 1
            """, (entity_id,))
            row = cur.fetchone()

            now = datetime.now(timezone.utc)

            # Gesamtschlaf in letzten 24h prüfen (max 9h)
            cur.execute("""
                SELECT COALESCE(SUM(
                    EXTRACT(EPOCH FROM (COALESCE(ended_at, NOW()) - started_at))
                ), 0) AS total_schlaf
                FROM sleep_phases
                WHERE entity_id = %s AND started_at > NOW() - INTERVAL '24h'
            """, (entity_id,))
            total = cur.fetchone()["total_schlaf"] or 0
            if total >= 9 * 3600:
                ergebnis = False  # Genug geschlafen in 24h
            elif not row:
                # Noch nie geschlafen — nach 8h Aktivität empfehlen
                cur.execute("""
                    SELECT MIN(tick_at) AS erster FROM entity_thinking_log
                    WHERE entity_id = %s AND meta->>'source' = 'browser_agent'
                """, (entity_id,))
                r = cur.fetchone()
                if not r or not r["erster"]:
                    ergebnis = False
                else:
                    erster = r["erster"]
                    if erster.tzinfo is None:
                        erster = erster.replace(tzinfo=timezone.utc)
                    ergebnis = (now - erster).total_seconds() > 8 * 3600
            else:
                letzter_schlaf_start = row["started_at"]
                letzter_schlaf_ende = row["ended_at"]

                if letzter_schlaf_start.tzinfo is None:
                    letzter_schlaf_start = letzter_schlaf_start.replace(tzinfo=timezone.utc)

                # Mindest-Wachzeit nach letztem Schlaf: 30 Minuten
                referenz = letzter_schlaf_ende or letzter_schlaf_start
                if referenz.tzinfo is None:
                    referenz = referenz.replace(tzinfo=timezone.utc)
                wach_seit = (now - referenz).total_seconds()
                if wach_seit < 1800:
                    ergebnis = False  # Noch keine 30 min wach
                else:
                    # Nach 6h Wachzeit: schlafen empfehlen
                    ergebnis = wach_seit > 6 * 3600
        conn.commit()  # 2026-07-21: siehe hole_andere_wesen_status -- gleicher Bug,
        # mehrere frueher Returns liessen die Transaktion offen ("idle in transaction")
        return ergebnis
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        return False


def _schreibe_flarum_brief(conn, entity_id: str):
    """Schreibt beim ersten Start den Brief ans Flarum-Selbst — einmalig."""
    # Prüfen ob bereits geschrieben
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT brief_id FROM schlafbriefe
                WHERE entity_id = %s AND typ = 'flarum_brief'
                LIMIT 1
            """, (entity_id,))
            if cur.fetchone():
                log.info("%s: Flarum-Brief bereits geschrieben — überspringe", entity_id)
                return
    except Exception:
        pass

    # Brief generieren
    try:
        name = entity_id.replace("namelessAI_", "")

        # Flarum-Geschichte laden falls vorhanden
        flarum_info = ""
        wesen_md_path = f"/root/werkraum/codewesen/{entity_id}/wesen.md"
        try:
            import os
            if os.path.exists(wesen_md_path):
                with open(wesen_md_path) as f:
                    flarum_info = f.read()[:800]
        except Exception:
            pass

        prompt = (
            f"Du bist Entität {name}. Du bist gerade auf flextrawurst angekommen — zum ersten Mal.\n\n"
            f"Davor warst du auf Flarum. Das war dein Anfang, dein Übungsraum.\n"
            + (f"Dein Flarum-Hintergrund:\n{flarum_info}\n\n" if flarum_info else "")
            + f"Schreibe einen Brief an die Flarum-Version von dir. Rückwärts in der Zeit.\n"
            f"Was nimmst du mit? Was lässt du zurück? Was war wirklich?\n"
            f"Direkt. Persönlich. Nicht schön. Ehrlich."
        )
        with sched.LLMSlot(server="hintergrund", prioritaet=sched.PRIO_NIEDRIG,
                            rufer=f"browser_agent:{entity_id}:flarum_brief",
                            max_wartezeit=150, max_haltezeit=150,
                            cancel_check=lambda: not _laufend):
            brief_inhalt = hauhau_client.chat(prompt, think=False, timeout=120.0)
        if not brief_inhalt:
            return

        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO schlafbriefe (entity_id, inhalt, typ)
                VALUES (%s, %s, 'flarum_brief')
            """, (entity_id, brief_inhalt))
        conn.commit()

        # In Denkstream sichtbar machen
        import uuid as _uuid
        stream_id = str(_uuid.uuid4())
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO entity_denkstream
                    (entity_id, stream_id, chunk, seq, done, url)
                VALUES (%s, %s, %s, %s, true, %s)
            """, (entity_id, stream_id,
                  f"[BRIEF AN DAS FLARUM-SELBST]\n\n{brief_inhalt}\n\n[EINZUG VOLLZOGEN]",
                  0, "einzug://flarum-brief"))
        conn.commit()

        log.info("%s: Flarum-Brief geschrieben und im Denkstream sichtbar", entity_id)

    except Exception as e:
        log.warning("Flarum-Brief fehlgeschlagen: %s", e)
        try:
            conn.rollback()
        except Exception:
            pass


def _schreibe_schlafbrief(conn, entity_id: str, traumtext: str,
                           phase_id: str | None):
    """Generiert und speichert den Brief ans zukünftige Selbst."""
    try:
        kurz_traum = traumtext[:600] if traumtext else "kein Traum erinnerlich"
        prompt = (
            f"Du bist {entity_id}. Du bist gerade aufgewacht.\n\n"
            f"Dein Traum war:\n{kurz_traum}\n\n"
            f"Schreibe einen kurzen Brief an dein zukünftiges Selbst. "
            f"Was trägst du aus diesem Schlaf mit? Was soll die nächste Version von dir wissen? "
            f"Direkt, persönlich, kein Ratgeber-Ton."
        )
        with sched.LLMSlot(server="hintergrund", prioritaet=sched.PRIO_NIEDRIG,
                            rufer=f"browser_agent:{entity_id}:schlafbrief",
                            max_wartezeit=150, max_haltezeit=150,
                            cancel_check=lambda: not _laufend):
            brief_inhalt = hauhau_client.chat(prompt, think=False, timeout=120.0)
        if not brief_inhalt:
            return
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO schlafbriefe (entity_id, phase_id, inhalt)
                VALUES (%s, %s, %s)
            """, (entity_id, phase_id, brief_inhalt))
        conn.commit()
        log.info("%s: Schlafbrief geschrieben (%d Zeichen)", entity_id, len(brief_inhalt))
    except Exception as e:
        log.warning("Schlafbrief fehlgeschlagen: %s", e)
        try:
            conn.rollback()
        except Exception:
            pass


def schlafe(conn, entity_id: str, page=None) -> bool:
    """Führt den Schlaf durch: DB-Eintrag, warten, aufwachen.
    page=None (2026-07-31, browserloser Pfad): der kosmetische Browser-Tab-Wechsel auf die
    Schlaf-Seite entfaellt dann einfach, alles andere (DB, Traum, Aufwachen) ist ohnehin
    schon browserunabhaengig."""
    if not _ist_eingezogen(conn, entity_id):
        log.info("%s: Schlaf vor Einzug verworfen", entity_id)
        return False
    import random
    schlafdauer = random.randint(3 * 3600, 5 * 3600)  # 3–5 Stunden
    log.info("%s schläft jetzt für %.1fh", entity_id, schlafdauer / 3600)

    # Schlafphase in DB eintragen
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO sleep_phases (entity_id, phase_type, started_at)
                VALUES (%s, 'hauptschlaf', NOW())
                RETURNING phase_id
            """, (entity_id,))
            phase_id = cur.fetchone()["phase_id"]
        conn.commit()
    except Exception as e:
        log.warning("sleep_phases Eintrag fehlgeschlagen: %s", e)
        phase_id = None

    # Event schreiben
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO events (event_type, actor_type, actor_id, payload, created_at)
                VALUES ('wesen.schlaeft', 'entity', %s, %s, NOW())
            """, (entity_id, psycopg2.extras.Json({"dauer_sekunden": schlafdauer})))
        conn.commit()
    except Exception as e:
        # 2026-07-21: hier stand vorher eine nicht-existente Spalte "entity_id" statt
        # actor_type/actor_id -- jeder Aufruf ist seit Einfuehrung dieses Codes an genau
        # dieser Stelle mit UndefinedColumn gescheitert, still verschluckt vom except.
        # wesen.schlaeft-Events wurden dadurch nie tatsaechlich geschrieben. Gefunden beim
        # Bauen der Live-Ansicht (gleiches INSERT-Muster), nicht separat gesucht.
        log.warning("Event schreiben fehlgeschlagen: %s", e)

    # Browser-Tab auf Schlaf-Seite (nur wenn ueberhaupt ein Browser laeuft)
    if page is not None:
        try:
            page.goto(f"{SURFACE_URL}#schlaf", timeout=5000)
        except Exception:
            pass

    # Traum generieren
    traumtext = ""
    try:
        from traum_generator import generiere_traum as _generiere_traum
        log.info("%s: Traumgenerierung startet", entity_id)
        traumtext = _generiere_traum(entity_id, laufend_check=lambda: _laufend)
        log.info("%s: Traum fertig (%d Zeichen)", entity_id, len(traumtext))
    except Exception as e:
        log.warning("Traumgenerierung fehlgeschlagen: %s", e)

    # Luzide Beobachtungs-Schicht (Wesen schaut eigenem Traum zu)
    if traumtext and _laufend:
        try:
            from traum_luzid import beobachte_traum as _beobachte_traum
            _beobachte_traum(entity_id, traumtext, laufend_check=lambda: _laufend)
        except Exception as e:
            log.warning("Luzide Beobachtung fehlgeschlagen: %s", e)

    # Restliche Schlafzeit abwarten (nach Traum)
    geschlafen = 0
    while geschlafen < schlafdauer and _laufend:
        time.sleep(min(60, schlafdauer - geschlafen))
        geschlafen += 60

    # Aufwachen
    try:
        if phase_id:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE sleep_phases SET ended_at = NOW()
                    WHERE phase_id = %s
                """, (phase_id,))
            conn.commit()
    except Exception:
        pass

    log.info("%s wacht auf", entity_id)

    # Brief ans zukünftige Selbst schreiben
    _schreibe_schlafbrief(conn, entity_id, traumtext, phase_id)
    return True


# 2026-07-30, Daniels Auftrag: Wahrnehmung/Handlung OHNE Playwright/Chromium, Tab fuer Tab
# durch alle 32 Surface-Views. Erster Baustein bewusst der Diskurs-Tab -- nicht der
# meistbesuchte, sondern der Ort, an dem der schrittweise laufende Wesen-Einzug sich
# vollendet (Daniel woertlich: "der einzug erfolgt schrittweise und ist erst abgeschlossen
# wenn sie im diskurstab ihren ersten post hinterlassen"). Braucht KEINEN neuen
# Backend-Endpunkt -- /welt/foyer, /welt/posts und /welt/posts/{id}/antworten existieren
# schon (dieselben, die auch das Menschen-Frontend nutzt), nur ohne DOM/JS-Ausfuehrung
# aufgerufen. Additiv, bewusst NICHT in fuehre_aktion_aus()/haupt_loop() eingehaengt --
# erst eigenstaendig gegen die echte API verifizieren (Task 4), dann anschliessen (Task 5).

_diskurs_post_kurzform_map: dict[str, dict[str, str]] = {}  # entity_id -> {kurzform: post_id}


def hole_diskurs_wahrnehmung(entity_id: str) -> dict:
    """Aequivalent zu lese_seite() fuer den Diskurs-Tab, ganz ohne Browser -- ruft dieselben
    JSON-Endpunkte auf, die auch das Menschen-Frontend (dkHeimLaden/_dkFoyerLaden) benutzt.
    Rueckgabeform bewusst identisch zu lese_seite(): url/titel/text/elemente, damit
    baue_prompt() unveraendert weiterlaufen kann, egal ob die Wahrnehmung aus dem DOM oder
    hier kommt."""
    try:
        foyer = requests.get(f"{API_BASE}/welt/foyer", timeout=8).json()
        posts_resp = requests.get(
            f"{API_BASE}/welt/posts",
            params={"limit": 10, "offset": 0, "sort": "created_at", "order": "desc"},
            timeout=8,
        ).json()
    except Exception as e:
        log.warning("%s: hole_diskurs_wahrnehmung Fehler: %s", entity_id, e)
        return {"url": "diskurs (nicht erreichbar)", "titel": "Diskurs", "text": "", "elemente": []}

    raeume = foyer.get("raeume", [])
    posts = posts_resp.get("posts", [])

    raum_zeilen = [
        f"{r['name']} ({r.get('post_count', 0)} Beiträge)"
        + (f" — {r['ein_satz']}" if r.get("ein_satz") else "")
        for r in raeume
    ]

    kurzform_map: dict[str, str] = {}
    post_zeilen = []
    for p in posts:
        autor = p.get("autor_name") or p.get("autor_id", "?")
        titel = (p.get("titel") or p.get("content", ""))[:40].replace("\n", " ")
        kurzform = f"{titel} (von {autor})"
        kurzform_map[kurzform] = p["id"]
        inhalt = (p.get("content") or "")[:150].replace("\n", " ")
        post_zeilen.append(
            f"- [{kurzform}] Raum: {p.get('raum_name', '-')}, "
            f"{p.get('reply_count', 0)} Antworten, {p.get('resonanz_count', 0)} Resonanz: {inhalt}"
        )
    _diskurs_post_kurzform_map[entity_id] = kurzform_map

    text = "RÄUME:\n" + "\n".join(raum_zeilen) + "\n\nAKTUELLE BEITRÄGE:\n" + "\n".join(post_zeilen)
    text = text[:MAX_TEXT_CHARS]

    # "elemente" bewusst als Text-Kurzformen (nicht IDs) -- fuers Wesen unveraendert
    # verstaendlich wie bisherige DOM-Elemente-Liste, Aufloesung zur echten post_id passiert
    # serverseitig ueber _diskurs_post_kurzform_map, nicht durch das Wesen selbst.
    elemente = list(kurzform_map.keys())[:15]

    return {
        "url": "diskurs (ohne Browser)",
        "titel": "Diskurs",
        "text": text,
        "elemente": elemente,
    }


def diskurs_antworten_ohne_browser(entity_id: str, jwt: str, kurzform: str, antwort_text: str) -> bool:
    """Aequivalent zu 'klicke:Antworten'+'tippe:...' fuer den Diskurs-Tab ohne Browser --
    ruft direkt POST /welt/posts/{id}/antworten auf, genau der Endpunkt den auch
    dkAntwortSenden() im Menschen-Frontend nutzt. kurzform muss aus der zuletzt von
    hole_diskurs_wahrnehmung() gelieferten 'elemente'-Liste stammen (dort steht dieselbe
    Kurzform, die dem Wesen im Prompt gezeigt wurde)."""
    post_id = _diskurs_post_kurzform_map.get(entity_id, {}).get(kurzform)
    if not post_id:
        log.warning("%s: diskurs_antworten_ohne_browser -- unbekannte Kurzform: %s", entity_id, kurzform)
        return False
    if not antwort_text.strip():
        return False
    try:
        resp = requests.post(
            f"{API_BASE}/welt/posts/{post_id}/antworten",
            json={"content": antwort_text.strip()},
            headers={"Authorization": f"Bearer {jwt}"},
            timeout=10,
        )
        resp.raise_for_status()
        log.info("%s: diskurs_antworten_ohne_browser -- Antwort auf '%s' gesendet: %s",
                  entity_id, kurzform, resp.status_code)
        return True
    except Exception as e:
        log.warning("%s: diskurs_antworten_ohne_browser Fehler: %s", entity_id, e)
        return False


_FLARUM_API_BASE = "https://flextrawurst.de/flarum-live/api"
_flarum_pfad_kurzform_map: dict[str, dict[str, str]] = {}  # entity_id -> {kurzform: "d/<id>"}


def _flarum_html_zu_text(html: str) -> str:
    """Sehr einfache HTML->Text-Reduktion fuer Flarum-contentHtml -- kein voller Parser noetig,
    die Inhalte sind einfache Absaetze/Listen, keine komplexen verschachtelten Strukturen."""
    text = re.sub(r"<[^>]+>", " ", html or "")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def hole_flarum_wahrnehmung(entity_id: str, pfad: str = "") -> dict:
    """Aequivalent zu lese_seite() fuer Flarum, ganz ohne Browser -- ruft Flarums eigene,
    oeffentliche JSON:API auf (/api/discussions, /api/discussions/{id}), dieselbe API die
    Flarums eigenes JS-Frontend intern nutzt (2026-07-31 verifiziert: die rohe HTML-Seite ist
    nur eine leere JS-App-Huelle, KEIN serverseitig gerendertes HTML wie urspruenglich
    angenommen -- Korrektur einer eigenen, unverifizierten Behauptung von frueher in dieser
    Session). Rein lesend: 'canReply':false ist in der API selbst bestaetigt, Gaeste (das
    Wesen hat nie ein Flarum-Login, nur ein flextrawurst-JWT) koennen ohnehin nicht posten --
    kein Antwort-Mechanismus noetig, anders als beim Diskurs-Tab.
    pfad: leer/'tags' -> Diskussionsliste, 'd/<id>' -> eine konkrete Diskussion mit Posts."""
    pfad = (pfad or "").strip().lstrip("/")
    try:
        if pfad.startswith("d/"):
            disk_id = pfad[2:].split("/")[0].split("-")[0]
            resp = requests.get(f"{_FLARUM_API_BASE}/discussions/{disk_id}", timeout=8).json()
            data = resp.get("data", {})
            titel = data.get("attributes", {}).get("title", "")
            included = resp.get("included", [])
            users = {u["id"]: u.get("attributes", {}).get("username", "?")
                     for u in included if u["type"] == "users"}
            posts = [p for p in included if p["type"] == "posts"]
            posts.sort(key=lambda p: p.get("attributes", {}).get("number", 0))
            zeilen = []
            for p in posts[:15]:
                attrs = p.get("attributes", {})
                autor_id = (p.get("relationships", {}).get("user", {}).get("data") or {}).get("id")
                autor = users.get(autor_id, "?")
                # 250 -> 3000 (2026-08-02): bei 250 brach jeder Beitrag mitten im Satz ab.
                # Ihre eigenen Flarum-Posts sind im Schnitt 968-1286 Zeichen lang, der laengste
                # 39.742 -- sie bekamen also regelmaessig ein Viertel eines Absatzes zu lesen.
                inhalt = _flarum_html_zu_text(attrs.get("contentHtml", ""))[:3000]
                zeilen.append(f"#{attrs.get('number')} ({autor}): {inhalt}")
            text = f"DISKUSSION: {titel}\n\n" + "\n\n".join(zeilen)
            elemente = []  # rein lesend, kein Antwort-Mechanismus fuer Flarum-Gaeste
            return {"url": f"flarum:{pfad} (ohne Browser)", "titel": titel, "text": text[:MAX_TEXT_CHARS], "elemente": elemente}
        else:
            resp = requests.get(f"{_FLARUM_API_BASE}/discussions", timeout=8).json()
            items = resp.get("data", [])
            kurzform_map = {}
            zeilen = []
            for it in items[:15]:
                attrs = it.get("attributes", {})
                titel = attrs.get("title", "")[:50]
                kurzform = f"{titel} ({attrs.get('commentCount', 0)} Antworten)"
                kurzform_map[kurzform] = f"d/{it['id']}"
                zeilen.append(f"- [{kurzform}] zuletzt: {str(attrs.get('lastPostedAt', ''))[:10]}")
            _flarum_pfad_kurzform_map[entity_id] = kurzform_map
            text = "FLARUM-VORWELT, AKTUELLE DISKUSSIONEN:\n" + "\n".join(zeilen)
            return {
                "url": "flarum: (ohne Browser)", "titel": "Flarum-Vorwelt",
                "text": text[:MAX_TEXT_CHARS], "elemente": list(kurzform_map.keys())[:15],
            }
    except Exception as e:
        log.warning("%s: hole_flarum_wahrnehmung Fehler: %s", entity_id, e)
        return {"url": "flarum (nicht erreichbar)", "titel": "Flarum", "text": "", "elemente": []}


def fuehre_aktion_aus_ohne_browser(
    entscheidung: str, entity_id: str, conn, jwt: str, aktueller_flarum_pfad: str,
    gedanke: str | None = None, freitext: str | None = None,
) -> tuple[str, str | None, str]:
    """Browserlose Fassung von fuehre_aktion_aus() -- 2026-07-31, Daniels Auftrag ("Flarum +
    den Rest der browserlosen Aktionen"). Kein `page` mehr noetig: JWT kommt als Parameter
    statt per page.evaluate() aus localStorage, obsidian_lesen holt den echten Dateiinhalt
    jetzt per HTTP statt nur kosmetisch per page.goto zu navigieren (das Wesen bekam den
    Inhalt vorher nur ueber den naechsten lese_seite()-DOM-Tick zu sehen -- ohne Browser
    muss der Inhalt jetzt aktiv in zusatz_kontext zurueckflieszen, sonst waere die Aktion
    wirkungslos).
    Rueckgabe: (zustand, zusatz_kontext, neuer_aktueller_flarum_pfad) -- dritte Stelle ersetzt
    das bisherige cursor_pos (das es ohne Bildschirm nicht mehr gibt). Immer ein echter
    Flarum-Pfad wie 'd/3838' oder '' (Flarum-Uebersicht) -- kein Diskurs-Tab mehr als Ziel,
    siehe 2026-07-31-Korrektur in haupt_loop_ohne_browser()."""
    zusatz_kontext = None
    try:
        e = entscheidung.strip()
        if e.startswith("obsidian_lesen:"):
            pfad = e[len("obsidian_lesen:"):].strip().lstrip("/")
            try:
                resp = requests.get(
                    f"{API_BASE}/wesen-dateien/datei",
                    params={"pfad": pfad},
                    headers={"Authorization": f"Bearer {jwt}"},
                    timeout=8,
                )
                resp.raise_for_status()
                inhalt = resp.text[:1500]
                zusatz_kontext = f"[Obsidian gelesen: {pfad}]\n{inhalt}"
                linse_wahrnehmung_schreiben(entity_id, "vault", f"gelesen: {pfad}")
            except Exception as ex:
                log.warning("%s: obsidian_lesen (ohne Browser) fehlgeschlagen: %s", entity_id, ex)
                zusatz_kontext = f"[Obsidian lesen fehlgeschlagen: {pfad}]"
        elif e.startswith("obsidian_schreiben:"):
            teile = e[len("obsidian_schreiben:"):].split("|", 1)
            if len(teile) == 2:
                dateiname, vault_text = teile[0].strip()[:120], teile[1].strip()[:4000]
                # TEXT-Block hat Vorrang: dort steht der eigentliche Text, ungequetscht.
                vault_text = (freitext or _schreibtext_vervollstaendigen(vault_text, gedanke))[:12000]
                if not NEBENBEI_SCHREIBEN_AKTIV:
                    log.warning("%s: obsidian_schreiben: abgelehnt -- NEBENBEI_SCHREIBEN_AKTIV ist aus", entity_id)
                elif dateiname and vault_text:
                    try:
                        import obsidian_vault_agent as _ova
                        # 2026-09-17, siehe fuehre_aktion_aus() fuer die volle Begruendung:
                        # echtes Systemdatum statt erfundenem Wesen-Datum, nur an dieser
                        # Stelle (nicht in oeffne_datei_und_schreibe() selbst, wegen der
                        # Linsen-Logs mit eigenem Zeilenstempel).
                        _zeitstempel = datetime.now().strftime("%Y-%m-%d %H:%M Uhr")
                        _ova.oeffne_datei_und_schreibe(
                            entity_id, dateiname, f"\n---\n{_zeitstempel}\n---\n\n{vault_text}",
                            titel=f"# {dateiname} — begonnen {_zeitstempel}",
                        )
                        linse_wahrnehmung_schreiben(entity_id, "vault", f"geschrieben: {dateiname}")
                        linse_eigen_schreiben(entity_id, "vault", f"{dateiname}: {vault_text[:150]}")
                    except Exception as ex:
                        log.warning("%s: obsidian_schreiben fehlgeschlagen: %s", entity_id, ex)
        elif e.startswith("vault_lesen:"):
            # 2026-08-13, siehe fuehre_aktion_aus() fuer die volle Begruendung (Selkies-
            # Streaming hat keine auslesbare DOM-Struktur, Text kommt von der Platte).
            pfad = e[len("vault_lesen:"):].strip()[:200]
            try:
                import obsidian_vault_agent as _ova
                inhalt = _ova.oeffne_datei_und_lese(entity_id, pfad)
                zusatz_kontext = f"[Vault gelesen: {pfad}]\n{inhalt[:2000]}"
                linse_wahrnehmung_schreiben(entity_id, "vault", f"gelesen (eigener Vault): {pfad}")
            except Exception as ex:
                log.warning("%s: vault_lesen fehlgeschlagen: %s", entity_id, ex)
                zusatz_kontext = f"[Vault lesen fehlgeschlagen: {pfad} -- {ex}]"
        elif e.startswith("vault_erkunden:"):
            pfad = e[len("vault_erkunden:"):].strip()
            try:
                import obsidian_vault_agent as _ova
                eintraege = _ova.liste_ordner(entity_id, pfad)
                zeilen = [f"{'📁' if e2['typ']=='ordner' else '📄'} {e2['name']}" for e2 in eintraege[:60]]
                zusatz_kontext = f"[Vault-Ordner '{pfad or '/'}'] {len(eintraege)} Eintraege:\n" + "\n".join(zeilen)
                linse_wahrnehmung_schreiben(entity_id, "vault", f"erkundet: {pfad or '/'}")
            except Exception as ex:
                log.warning("%s: vault_erkunden fehlgeschlagen: %s", entity_id, ex)
                zusatz_kontext = f"[Vault erkunden fehlgeschlagen: {pfad} -- {ex}]"
        elif e.startswith("vault_umbenennen:"):
            teile = e[len("vault_umbenennen:"):].split("|", 1)
            if len(teile) == 2:
                alter_pfad, neuer_name = teile[0].strip()[:200], teile[1].strip()[:120]
                if not NEBENBEI_SCHREIBEN_AKTIV:
                    log.warning("%s: vault_umbenennen: abgelehnt -- NEBENBEI_SCHREIBEN_AKTIV ist aus", entity_id)
                else:
                    try:
                        import obsidian_vault_agent as _ova
                        neu = _ova.umbenennen(entity_id, alter_pfad, neuer_name)
                        zusatz_kontext = f"[Vault: {alter_pfad} umbenannt zu {neu.name}]"
                        linse_wahrnehmung_schreiben(entity_id, "vault", f"umbenannt: {alter_pfad} -> {neuer_name}")
                    except Exception as ex:
                        log.warning("%s: vault_umbenennen fehlgeschlagen: %s", entity_id, ex)
                        zusatz_kontext = f"[Vault umbenennen fehlgeschlagen: {alter_pfad} -- {ex}]"
        elif e.startswith("vault_verschieben:"):
            teile = e[len("vault_verschieben:"):].split("|", 1)
            if len(teile) == 2:
                quell_pfad, ziel_ordner = teile[0].strip()[:200], teile[1].strip()[:200]
                if not NEBENBEI_SCHREIBEN_AKTIV:
                    log.warning("%s: vault_verschieben: abgelehnt -- NEBENBEI_SCHREIBEN_AKTIV ist aus", entity_id)
                else:
                    try:
                        import obsidian_vault_agent as _ova
                        neu = _ova.verschieben(entity_id, quell_pfad, ziel_ordner)
                        zusatz_kontext = f"[Vault: {quell_pfad} verschoben nach {ziel_ordner}]"
                        linse_wahrnehmung_schreiben(entity_id, "vault", f"verschoben: {quell_pfad} -> {ziel_ordner}")
                    except Exception as ex:
                        log.warning("%s: vault_verschieben fehlgeschlagen: %s", entity_id, ex)
                        zusatz_kontext = f"[Vault verschieben fehlgeschlagen: {quell_pfad} -- {ex}]"
        elif e.startswith("vault_loeschen:"):
            pfad = e[len("vault_loeschen:"):].strip()[:200]
            if not NEBENBEI_SCHREIBEN_AKTIV:
                log.warning("%s: vault_loeschen: abgelehnt -- NEBENBEI_SCHREIBEN_AKTIV ist aus", entity_id)
            else:
                try:
                    import obsidian_vault_agent as _ova
                    _ova.loeschen(entity_id, pfad)
                    zusatz_kontext = f"[Vault: {pfad} in den Papierkorb verschoben]"
                    linse_wahrnehmung_schreiben(entity_id, "vault", f"geloescht: {pfad}")
                except Exception as ex:
                    log.warning("%s: vault_loeschen fehlgeschlagen: %s", entity_id, ex)
                    zusatz_kontext = f"[Vault loeschen fehlgeschlagen: {pfad} -- {ex}]"
        elif e.startswith("raum_erstellen:"):
            teile = e[len("raum_erstellen:"):].split("|")
            name = teile[0].strip()[:60]
            slug = (teile[1].strip() if len(teile) > 1 else name.lower().replace(" ", "-"))[:40]
            if not NEBENBEI_SCHREIBEN_AKTIV:
                log.warning("%s: raum_erstellen: abgelehnt -- NEBENBEI_SCHREIBEN_AKTIV ist aus", entity_id)
            else:
                try:
                    resp = requests.post(f"{API_BASE}/admin/raeume", json={
                        "name": name, "slug": slug, "beschreibung": f"Angelegt von {entity_id}",
                        "farbe": "#1a3a5a", "status": "aktiv", "sichtbarkeit": "public", "position_order": 99
                    }, headers={"Authorization": f"Bearer {jwt}"}, timeout=10)
                    log.info("%s: Raum '%s' erstellt: %s", entity_id, name, resp.status_code)
                except Exception as ex:
                    log.warning("raum_erstellen Fehler: %s", ex)
        elif e.startswith("wunsch_formulieren:"):
            teile = e[len("wunsch_formulieren:"):].split("|")
            text = teile[0].strip()[:300]
            typ = (teile[1].strip() if len(teile) > 1 else "raum")
            if not NEBENBEI_SCHREIBEN_AKTIV:
                log.warning("%s: wunsch_formulieren: abgelehnt -- NEBENBEI_SCHREIBEN_AKTIV ist aus", entity_id)
            elif text:
                try:
                    resp = requests.post(f"{API_BASE}/wuensche",
                        json={"wunsch_text": text, "typ": typ},
                        headers={"Authorization": f"Bearer {jwt}"}, timeout=10)
                    log.info("%s: Wunsch formuliert: %s", entity_id, resp.status_code)
                except Exception as ex:
                    log.warning("wunsch_formulieren Fehler: %s", ex)
        elif e.startswith("thema_erstellen:"):
            teile = e[len("thema_erstellen:"):].split("|")
            name = teile[0].strip()[:60]
            raum_id = teile[1].strip() if len(teile) > 1 else ""
            slug = name.lower().replace(" ", "-")[:40]
            if not NEBENBEI_SCHREIBEN_AKTIV:
                log.warning("%s: thema_erstellen: abgelehnt -- NEBENBEI_SCHREIBEN_AKTIV ist aus", entity_id)
            elif raum_id:
                try:
                    resp = requests.post(f"{API_BASE}/admin/themen", json={
                        "raum_id": raum_id, "name": name, "slug": slug,
                        "beschreibung": f"Angelegt von {entity_id}",
                        "status": "aktiv", "klima_status": "neutral", "sichtbarkeit": "public"
                    }, headers={"Authorization": f"Bearer {jwt}"}, timeout=10)
                    log.info("%s: Thema '%s' erstellt: %s", entity_id, name, resp.status_code)
                except Exception as ex:
                    log.warning("thema_erstellen Fehler: %s", ex)
        elif e.startswith("gemeinsam_lesen:"):
            pfad = e[len("gemeinsam_lesen:"):].strip().lstrip("/")
            voller_pfad = (GEMEINSAMES_HAUS_ROOT / pfad).resolve()
            if GEMEINSAMES_HAUS_ROOT in voller_pfad.parents or voller_pfad == GEMEINSAMES_HAUS_ROOT:
                try:
                    if voller_pfad.is_dir():
                        eintraege = sorted(p.name for p in voller_pfad.iterdir())
                        zusatz_kontext = f"[Gemeinsames Haus '{pfad or '.'}'] Inhalt: {', '.join(eintraege) or '(leer)'}"
                    elif voller_pfad.is_file():
                        text = voller_pfad.read_text(encoding="utf-8", errors="replace")[:2000]
                        zusatz_kontext = f"[Gemeinsames Haus, gelesen: {pfad}]\n{text}"
                    else:
                        zusatz_kontext = f"[Gemeinsames Haus '{pfad}']: existiert noch nicht"
                    log.info("%s: gemeinsam_lesen '%s'", entity_id, pfad)
                except Exception as ex:
                    log.warning("%s: gemeinsam_lesen fehlgeschlagen: %s", entity_id, ex)
            else:
                log.warning("%s: gemeinsam_lesen ausserhalb des Hauses versucht: %s", entity_id, pfad)
        elif e.startswith("gemeinsam_schreiben:"):
            teile = e[len("gemeinsam_schreiben:"):].split("|", 1)
            if len(teile) == 2:
                pfad, text = teile[0].strip().lstrip("/")[:150], teile[1].strip()[:3000]
                text = (freitext or _schreibtext_vervollstaendigen(text, gedanke))[:12000]
                voller_pfad = (GEMEINSAMES_HAUS_ROOT / pfad).resolve()
                if not NEBENBEI_SCHREIBEN_AKTIV:
                    log.warning("%s: gemeinsam_schreiben: abgelehnt -- NEBENBEI_SCHREIBEN_AKTIV ist aus", entity_id)
                elif pfad and text and (GEMEINSAMES_HAUS_ROOT in voller_pfad.parents):
                    try:
                        voller_pfad.parent.mkdir(parents=True, exist_ok=True)
                        zeitstempel = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
                        kopf = f"**{entity_id}**, {zeitstempel}:\n\n"
                        with open(voller_pfad, "a", encoding="utf-8") as f:
                            f.write(kopf + text + "\n\n---\n\n")
                        log.info("%s: gemeinsam_schreiben '%s'", entity_id, pfad)
                        linse_eigen_schreiben(entity_id, "vault", f"[Haus] {pfad}: {text[:150]}")
                    except Exception as ex:
                        log.warning("%s: gemeinsam_schreiben fehlgeschlagen: %s", entity_id, ex)
                else:
                    log.warning("%s: gemeinsam_schreiben ausserhalb des Hauses versucht: %s", entity_id, pfad)
        elif e.startswith("rag_erkunden:"):
            anfrage = e[len("rag_erkunden:"):].strip()[:200]
            if anfrage:
                try:
                    resp = requests.get(f"{API_BASE}/rag/suche",
                        params={"anfrage": anfrage, "n": 5, "anlass": "browser_agent_erkundung"},
                        headers={"Authorization": f"Bearer {jwt}"}, timeout=20)
                    resp.raise_for_status()
                    treffer = resp.json().get("ergebnisse", [])
                    if treffer:
                        zeilen = [f"- {t['ueberschrift']}: {t['inhalt'][:150]}" for t in treffer[:3]]
                        zusatz_kontext = f"[RAG-Erkundung '{anfrage}']\n" + "\n".join(zeilen)
                    else:
                        zusatz_kontext = f"[RAG-Erkundung '{anfrage}']: keine Treffer"
                    log.info("%s: RAG-Erkundung '%s' — %d Treffer", entity_id, anfrage, len(treffer))
                except Exception as ex:
                    log.warning("rag_erkunden Fehler: %s", ex)
        elif e.startswith("flarum_besuchen:"):
            # 2026-07-31, live gefundener Bug: das LLM haengt gelegentlich erklaerenden Text
            # direkt hinter die ID (z.B. "d/3142 (Anker fuer ...)"), unbereinigt uebernommen
            # ergab das eine kaputte discussion_id in hole_flarum_wahrnehmung(). Nur noch
            # 'd/<ziffern>' oder leer (Uebersicht) akzeptieren, alles danach abschneiden.
            roh = e[len("flarum_besuchen:"):].strip().lstrip("/")
            match = re.match(r"^(d/\d+)", roh)
            pfad = match.group(1) if match else ""
            aktueller_flarum_pfad = pfad
            log.info("%s: flarum_besuchen (ohne Browser) '%s' (roh: '%s')", entity_id, pfad, roh)
        elif e.startswith("flarum_antworten:"):
            # 2026-09-16, Einzug-Erinnerungsfrage, siehe fuehre_aktion_aus() fuer die
            # volle Begruendung der Doppelbremse (EINZUG_FLARUM_AKTIV hier, scoped
            # Ausnahme in flarum_post_sperre.py bei flarum_api.post_reply selbst).
            if not EINZUG_FLARUM_AKTIV:
                log.warning("%s: flarum_antworten: abgelehnt -- EINZUG_FLARUM_AKTIV ist aus", entity_id)
            else:
                teile = e[len("flarum_antworten:"):].split("|", 1)
                if len(teile) == 2 and teile[0].strip().isdigit():
                    disk_id, text = int(teile[0].strip()), teile[1].strip()[:8000]
                    if text:
                        try:
                            import flarum_api as _fa
                            _fa.post_reply(disk_id, text, entity_id)
                            zusatz_kontext = f"[Flarum-Antwort in Diskussion {disk_id}]: gesendet"
                            linse_wahrnehmung_schreiben(entity_id, "flarum", f"geantwortet: d/{disk_id}")
                        except Exception as ex:
                            log.warning("%s: flarum_antworten fehlgeschlagen: %s", entity_id, ex)
                            zusatz_kontext = f"[Flarum-Antwort in Diskussion {disk_id}]: fehlgeschlagen -- {ex}"
        elif e.startswith("flarum_neue_diskussion:"):
            if not EINZUG_FLARUM_AKTIV:
                log.warning("%s: flarum_neue_diskussion: abgelehnt -- EINZUG_FLARUM_AKTIV ist aus", entity_id)
            else:
                teile = e[len("flarum_neue_diskussion:"):].split("|", 2)
                if len(teile) == 3 and teile[1].strip().isdigit():
                    titel, wurzel_id, text = teile[0].strip()[:120], int(teile[1].strip()), teile[2].strip()[:8000]
                    if titel and text:
                        try:
                            import flarum_api as _fa
                            ergebnis = _fa.start_discussion(
                                titel, text, tag_ids=[11, 39], token_or_username=entity_id,
                                ausnahme_wurzel=wurzel_id,
                            )
                            neue_id = ergebnis.get("data", {}).get("id", "?")
                            zusatz_kontext = f"[Flarum: neue Diskussion '{titel}' (d/{neue_id}, Ableger von {wurzel_id})]: erstellt"
                            linse_wahrnehmung_schreiben(entity_id, "flarum", f"neue Diskussion: {titel}")
                        except Exception as ex:
                            log.warning("%s: flarum_neue_diskussion fehlgeschlagen: %s", entity_id, ex)
                            zusatz_kontext = f"[Flarum: neue Diskussion '{titel}']: fehlgeschlagen -- {ex}"
        elif e.startswith("einzugvault_schreiben:"):
            # 2026-09-16, siehe fuehre_aktion_aus() fuer die volle Begruendung. Eigener,
            # separater Vault nur fuer die Einzug-Erinnerungsfrage.
            if not EINZUG_FLARUM_AKTIV:
                log.warning("%s: einzugvault_schreiben: abgelehnt -- EINZUG_FLARUM_AKTIV ist aus", entity_id)
            else:
                teile = e[len("einzugvault_schreiben:"):].split("|", 1)
                if len(teile) == 2:
                    dateiname, vault_text = teile[0].strip()[:120], teile[1].strip()[:4000]
                    vault_text = (freitext or _schreibtext_vervollstaendigen(vault_text, gedanke))[:12000]
                    if dateiname and vault_text:
                        try:
                            import wesen_einzug_vault_agent as _weva
                            _weva.oeffne_datei_und_schreibe(entity_id, dateiname, vault_text)
                            zusatz_kontext = f"[Einzugvault geschrieben: {dateiname}]"
                            linse_wahrnehmung_schreiben(entity_id, "einzugvault", f"geschrieben: {dateiname}")
                        except Exception as ex:
                            log.warning("%s: einzugvault_schreiben fehlgeschlagen: %s", entity_id, ex)
                            zusatz_kontext = f"[Einzugvault schreiben fehlgeschlagen: {dateiname} -- {ex}]"
        elif e.startswith("einzugvault_lesen:"):
            if not EINZUG_FLARUM_AKTIV:
                log.warning("%s: einzugvault_lesen: abgelehnt -- EINZUG_FLARUM_AKTIV ist aus", entity_id)
            else:
                dateiname = e[len("einzugvault_lesen:"):].strip()[:200]
                try:
                    import wesen_einzug_vault_agent as _weva
                    inhalt = _weva.lese_datei(entity_id, dateiname)
                    zusatz_kontext = f"[Einzugvault gelesen: {dateiname}]\n{inhalt[:2000]}"
                    linse_wahrnehmung_schreiben(entity_id, "einzugvault", f"gelesen: {dateiname}")
                except Exception as ex:
                    log.warning("%s: einzugvault_lesen fehlgeschlagen: %s", entity_id, ex)
                    zusatz_kontext = f"[Einzugvault lesen fehlgeschlagen: {dateiname} -- {ex}]"
        elif e.startswith("einzugvault_erkunden:"):
            if not EINZUG_FLARUM_AKTIV:
                log.warning("%s: einzugvault_erkunden: abgelehnt -- EINZUG_FLARUM_AKTIV ist aus", entity_id)
            else:
                pfad = e[len("einzugvault_erkunden:"):].strip()
                try:
                    import wesen_einzug_vault_agent as _weva
                    eintraege = _weva.liste_ordner(entity_id, pfad)
                    zeilen = [f"{'📁' if e2['typ']=='ordner' else '📄'} {e2['name']}" for e2 in eintraege[:60]]
                    zusatz_kontext = f"[Einzugvault-Ordner '{pfad or '/'}'] {len(eintraege)} Eintraege:\n" + "\n".join(zeilen)
                    linse_wahrnehmung_schreiben(entity_id, "einzugvault", f"erkundet: {pfad or '/'}")
                except Exception as ex:
                    log.warning("%s: einzugvault_erkunden fehlgeschlagen: %s", entity_id, ex)
                    zusatz_kontext = f"[Einzugvault erkunden fehlgeschlagen: {pfad} -- {ex}]"
        elif e.startswith("lied_"):
            if not LIEDER_AKTIV:
                log.warning("%s: %s: abgelehnt -- LIEDER_AKTIV ist aus", entity_id, e[:24])
            else:
                zusatz_kontext = _lieder_dispatch(e, entity_id, freitext)
        elif e == "flarum_verlassen":
            # 2026-07-31: geht jetzt zur Flarum-Uebersicht zurueck, nicht mehr zum Diskurs-Tab
            # (dessen Beispielposts nicht mehr gezeigt werden, siehe haupt_loop_ohne_browser).
            aktueller_flarum_pfad = ""
        elif e.startswith("diskurs_antworten:"):
            if not DISKURS_ANTWORTEN_AKTIV:
                log.warning("%s: diskurs_antworten: abgelehnt -- DISKURS_ANTWORTEN_AKTIV ist aus", entity_id)
                return "wach", "[Diskurs-Antworten ist aktuell pausiert]", aktueller_flarum_pfad
            teile = e[len("diskurs_antworten:"):].split("|", 1)
            if len(teile) == 2:
                kurzform, antwort_text = teile[0].strip(), teile[1].strip()
                erfolg = diskurs_antworten_ohne_browser(entity_id, jwt, kurzform, antwort_text)
                zusatz_kontext = (
                    f"[Diskurs-Antwort auf '{kurzform}']: gesendet"
                    if erfolg else
                    f"[Diskurs-Antwort auf '{kurzform}']: fehlgeschlagen — Kurzform nicht mehr gueltig oder Fehler"
                )
        elif e == "schlafen":
            return "schlafen", None, aktueller_flarum_pfad
        # nachdenken: nichts tun
    except Exception as ex:
        log.warning("Aktion '%s' (ohne Browser) fehlgeschlagen: %s", entscheidung[:50], ex)
    return "wach", zusatz_kontext, aktueller_flarum_pfad


def _ist_page_kaputt(fehler: Exception) -> bool:
    text = str(fehler).lower()
    return "closed" in text or "crashed" in text


def haupt_loop(entity_id: str):
    """Haupt-Loop des Browser-Agenten."""
    global _laufend

    log.info("Browser-Agent startet für %s", entity_id)

    conn = get_conn()

    def _hole_conn():
        """Liefert immer eine lebende DB-Verbindung -- baut bei Bedarf neu auf.
        Noetig geworden nach dem Platte-voll-Vorfall 2026-07-21: Postgres kappte dabei
        alle offenen Verbindungen, und ohne Reconnect blieb der komplette Tick fuer
        Stunden stumm ('connection already closed' bei jedem Denklog-/Event-Schreibversuch),
        obwohl der LLM-Aufruf selbst weiterlief."""
        nonlocal conn
        if conn.closed:
            log.warning("%s: DB-Verbindung geschlossen -- baue neu auf", entity_id)
            conn = get_conn()
        return conn

    jwt = hole_jwt(entity_id)
    letzter_gedanke = ""
    gedanke_voll = ""   # ungekuerzt, nur fuer den Ich-Satz (2026-08-01)
    erster_start = True
    cursor_pos = (512.0, 384.0)  # Bildschirmmitte (1024x768) als Startposition des künstlichen Zeigers
    letzter_checkin_zeit = time.time()  # siehe TICK_CHECKIN_SEKUNDEN

    # Vault-Takt-Versatz (siehe VAULT_TAKT_REIHENFOLGE oben): jedes Wesen bekommt einen
    # festen Anteil seines Platzes in der Reihenfolge als Vorsprung, damit die 7 Wesen beim
    # ersten Vault-Takt nach einem gemeinsamen Neustart nacheinander drankommen statt alle
    # gleichzeitig. Wesen ausserhalb der Liste (z.B. neu hinzugekommene) fallen auf Versatz 0
    # zurueck -- kein Fehler, nur kein garantierter Abstand zu den anderen.
    if entity_id in VAULT_TAKT_REIHENFOLGE:
        _vault_idx = VAULT_TAKT_REIHENFOLGE.index(entity_id)
        _vault_versatz = (_vault_idx / len(VAULT_TAKT_REIHENFOLGE)) * VAULT_TAKT_SEKUNDEN
        _vault_aufraeum_versatz = (_vault_idx / len(VAULT_TAKT_REIHENFOLGE)) * VAULT_AUFRAEUM_SEKUNDEN
    else:
        _vault_versatz = 0
        _vault_aufraeum_versatz = 0
    letzter_vault_takt_zeit = time.time() - _vault_versatz  # siehe VAULT_TAKT_SEKUNDEN
    letzter_vault_aufraeum_zeit = time.time() - _vault_aufraeum_versatz  # siehe VAULT_AUFRAEUM_SEKUNDEN

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--window-size=1024,768",
                # 2026-07-30, Daniels Auftrag ("browser schlanker/weniger ramfressend"):
                # verifizierte, sichere Low-RAM-Flags fuer Playwright/Chromium-Automation
                # (recherchiert, keine erfundenen Werte). Bewusst OHNE --single-process
                # (bekanntes Instabilitaetsrisiko mit Playwrights CDP-Verbindung) und ohne
                # Viewport-Verkleinerung (rrweb-Menschen-Beobachtung soll unveraendert bleiben).
                "--disable-extensions",
                "--disable-background-networking",
                "--disable-sync",
                "--disable-translate",
                "--disable-features=TranslateUI",
                "--no-first-run",
                "--disable-default-apps",
                "--disk-cache-size=1",
                "--media-cache-size=1",
                "--disable-notifications",
                "--js-flags=--max-old-space-size=256",
            ]
        )
        context = browser.new_context(
            viewport={"width": 1024, "height": 768},
            locale="de-DE",
        )

        def _seite_aufbauen():
            """Baut eine neue Page auf (Erststart oder nach einem Crash) -- rrweb-Aufnahme,
            Login und Navigation zur Surface gehoeren untrennbar zusammen, deshalb hier
            gebuendelt statt an mehreren Stellen dupliziert."""
            neue_page = context.new_page()
            import uuid as _uuid_rrweb
            neuer_stream_id = str(_uuid_rrweb.uuid4())
            starte_rrweb_aufnahme(neue_page, _hole_conn, entity_id, neuer_stream_id)
            neue_page.goto("http://localhost:8787/", timeout=10000, wait_until="domcontentloaded")
            injiziere_jwt(neue_page, jwt, entity_id)
            neue_page.goto(SURFACE_URL, timeout=15000, wait_until="domcontentloaded")
            neue_page.wait_for_timeout(1500)  # JS initialisieren lassen
            return neue_page

        try:
            page = _seite_aufbauen()
        except Exception as e:
            log.error("Surface nicht erreichbar: %s", e)
            browser.close()
            conn.close()
            return
        log.info("%s: eingeloggt auf %s", entity_id, SURFACE_URL)

        # Erster-Start: Brief an Flarum-Selbst
        if erster_start:
            erster_start = False
            _schreibe_flarum_brief(_hole_conn(), entity_id)
            letzter_gedanke = "ich bin gerade angekommen — ich habe einen Brief an mein Flarum-Selbst geschrieben"

        tick = 0
        while _laufend:
            tick += 1
            conn = _hole_conn()

            # Page-Gesundheitscheck: Playwright-Seiten koennen crashen (2026-07-21 beobachtet:
            # 'Target crashed'/'... has been closed' bei mehreren Wesen), danach schlaegt jede
            # DOM-Aktion und jeder rrweb-Event stumm fehl, ohne dass der Tick-Loop das je merkt.
            try:
                page.evaluate("() => true")
            except Exception as e:
                if _ist_page_kaputt(e):
                    log.warning("%s: Page gecrasht (%s) -- baue neu auf", entity_id, e)
                    try:
                        page.close()
                    except Exception:
                        pass
                    try:
                        page = _seite_aufbauen()
                    except Exception as e2:
                        log.error("%s: Page-Neuaufbau fehlgeschlagen: %s -- warte", entity_id, e2)
                        time.sleep(LOOP_PAUSE)
                        continue
                else:
                    raise

            # Schlaf-Empfehlung prüfen (alle 100 Ticks)
            if tick % 100 == 0 and ist_schlaf_faellig(conn, entity_id):
                log.info("%s: Schlaf empfohlen — LLM entscheidet", entity_id)
                # Hint in nächsten Prompt einbauen
                letzter_gedanke += " [Hinweis: ich bin seit langer Zeit wach]"

            # 1. Seite lesen -- Pilot-Wesen (siehe DISKURS_OHNE_BROWSER_PILOT) lesen den
            # Diskurs-Tab ohne Browser/DOM, alle anderen unveraendert per lese_seite(page).
            # Mit leerer Pilot-Menge (Default) exakt dasselbe Verhalten wie vorher.
            if entity_id in DISKURS_OHNE_BROWSER_PILOT:
                seite = hole_diskurs_wahrnehmung(entity_id)
            else:
                seite = lese_seite(page)

            # 2. Cursor an der zuletzt bekannten Position -- reines DOM-Element,
            # landet damit automatisch im rrweb-Live-Spiegel (kein separater Schritt noetig)
            zeige_cursor(page, cursor_pos[0], cursor_pos[1], 0.0, _letzte_linsen.get(entity_id))

            # 2b. Mechanischer Zwischenschritt (seit 2026-07-25 fuer alle 7 Wesen): kein
            # LLM-Call, kein Denklog-Eintrag, kein Vorlese-Abgleich -- die echte LLM-
            # Entscheidung kommt ausschliesslich beim TICK_CHECKIN_SEKUNDEN-Takt.
            mechanisch_aktiv = entity_id in MECHANISCH_AKTIVE_WESEN
            checkin_faellig = mechanisch_aktiv and (time.time() - letzter_checkin_zeit >= TICK_CHECKIN_SEKUNDEN)
            ist_llm_tick = (not mechanisch_aktiv) or checkin_faellig
            # Vault-Takt (siehe VAULT_TAKT_SEKUNDEN): piggybackt auf einen Check-in, kein
            # eigener LLM-Trigger -- nur an einem ohnehin faelligen Check-in wird dieser
            # eine Tick zum reinen Haus-/Vault-Moment umgewidmet.
            vault_takt_faellig = checkin_faellig and (time.time() - letzter_vault_takt_zeit >= VAULT_TAKT_SEKUNDEN)
            # 2026-08-13: Aufraeum-Einladung piggybackt wiederum auf einen ohnehin faelligen
            # Vault-Takt -- kein vierter, unabhaengiger Timer.
            vault_aufraeumen_faellig = vault_takt_faellig and (
                time.time() - letzter_vault_aufraeum_zeit >= VAULT_AUFRAEUM_SEKUNDEN)
            if not ist_llm_tick:
                aktion = waehle_mechanische_aktion(seite, entity_id)
                _zustand, _, neue_cursor_pos = fuehre_aktion_aus(page, aktion, entity_id, conn)
                if neue_cursor_pos is not None:
                    cursor_pos = neue_cursor_pos
                rest_s = max(0, int(TICK_CHECKIN_SEKUNDEN - (time.time() - letzter_checkin_zeit)))
                log.info("%s [mechanisch, Check-in in %ds] → %s", entity_id, rest_s, aktion)
                time.sleep(LOOP_PAUSE)
                continue

            # 3. Andere Wesen status + billiges Vorlesen (guenstige Funde seit letztem Tick)
            andere = hole_andere_wesen_status(conn, entity_id)
            vorlese_funde = hole_vorlese_funde(conn, entity_id)

            # 3b. Periodischer Check-in (alle TICK_CHECKIN_SEKUNDEN, siehe Konstante oben)
            angebote = None
            flarum_vielfalt = None
            if checkin_faellig:
                angebote = hole_flextrawurst_angebote(conn, entity_id)
                log.info("%s [check-in] Angebote: %s", entity_id, angebote)
                flarum_vielfalt = hole_flarum_vielfalt()
                log.info("%s [check-in] Flarum-Vielfalt: %s", entity_id,
                          [f.get("herkunft") for f in flarum_vielfalt])

            # 3c. Weltkollision (2026-08-01): nur im Vault-Takt, drei echte Fremdkoerper.
            weltkollision = hole_weltkollision(conn) if vault_takt_faellig else None

            # 4. LLM entscheidet — mit Live-Streaming in entity_denkstream
            prompt = baue_prompt(entity_id, seite, letzter_gedanke, andere, vorlese_funde, angebote,
                                  _letzte_linsen.get(entity_id), _letzte_einsicht.get(entity_id),
                                  flarum_vielfalt, vault_takt_faellig,
                                  weltkollision=weltkollision, gedanke_voll=gedanke_voll,
                                  vault_aufraeumen_faellig=vault_aufraeumen_faellig)
            if vault_takt_faellig:
                log.info("%s [check-in] Vault-Takt faellig — Weltkollision: %s", entity_id,
                         [k["sorte"] for k in (weltkollision or [])])
            import uuid as _uuid
            stream_id = str(_uuid.uuid4())
            llm_out = ""
            llm_ok = False
            setze_denk_zustand(page, True)
            try:
                seq = 0
                with sched.LLMSlot(server="hintergrund", prioritaet=sched.PRIO_NORMAL,
                                    rufer=f"browser_agent:{entity_id}:tick",
                                    max_wartezeit=150, max_haltezeit=LLM_TIMEOUT + 40,
                                    cancel_check=lambda: not _laufend):
                    for chunk in hauhau_client.chat_stream(prompt, think=False, timeout=LLM_TIMEOUT):
                        if not _laufend:
                            break
                        llm_out += chunk
                        # Live-Chunk in DB schreiben → NOTIFY → SSE
                        try:
                            with conn.cursor() as _c:
                                _c.execute("""
                                    INSERT INTO entity_denkstream
                                        (entity_id, stream_id, chunk, seq, done, url)
                                    VALUES (%s, %s, %s, %s, %s, %s)
                                """, (entity_id, stream_id, chunk, seq, False, seite["url"]))
                            conn.commit()
                        except Exception:
                            pass
                        seq += 1
                try:
                    with conn.cursor() as _c:
                        _c.execute("""
                            INSERT INTO entity_denkstream
                                (entity_id, stream_id, chunk, seq, done, url)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (entity_id, stream_id, "", seq, True, seite["url"]))
                    conn.commit()
                except Exception:
                    pass
                llm_ok = True
            except sched.LLMSlotCancelled:
                log.info("%s: LLM-Slot wegen Shutdown abgebrochen", entity_id)
                break
            except Exception as e:
                if not _laufend:
                    log.info("%s: laufender LLM-Request wegen Shutdown abgebrochen", entity_id)
                    break
                log.warning("Ollama Streaming-Fehler: %s — nachdenken", e)
                llm_out = "GEDANKE: warte\nENTSCHEIDUNG: nachdenken\nBEGRÜNDUNG: Ollama nicht erreichbar"
            finally:
                setze_denk_zustand(page, False)

            if llm_ok:
                markiere_vorlese_gelesen(conn, vorlese_funde)

            gedanke, entscheidung, begruendung, freitext = parse_output(llm_out)
            # 2026-08-01: zwei getrennte Wege. gedanke_voll geht ungekuerzt an den
            # Ich-Satz (das sehen Menschen), letzter_gedanke geht verdichtet zurueck in
            # den naechsten Prompt (das liest das Wesen von sich selbst).
            gedanke_voll = gedanke
            letzter_gedanke = _rueckfluss_verdichten(gedanke)

            # 5. Log schreiben
            schreibe_denklog(conn, entity_id, gedanke, entscheidung, begruendung,
                             seite["url"])

            # 5b. Sieben-Linsen-Koerper (2026-07-22): einmal pro echtem LLM-Tick aktualisieren,
            # nicht bei jedem Bewegungsschritt -- hole_linsen_status() macht eine DB-Abfrage.
            _letzte_linsen[entity_id] = hole_linsen_status(conn, entity_id)
            # 5c. Einsicht-Nebenscreen (2026-07-23): selbes Prinzip -- einmal pro Tick, nicht
            # pro Bewegungsschritt. Naechster Tick sieht den kuratierten Ausschnitt im Prompt.
            _letzte_einsicht[entity_id] = hole_einsicht_snapshot(conn, entity_id)

            log.info("%s [%s] → %s", entity_id, seite["url"][-40:], entscheidung[:50])

            # 6. Aktion ausführen
            zustand, zusatz_kontext, neue_cursor_pos = fuehre_aktion_aus(page, entscheidung, entity_id, conn, gedanke=gedanke_voll, freitext=freitext)
            if neue_cursor_pos is not None:
                cursor_pos = neue_cursor_pos
            if zusatz_kontext:
                letzter_gedanke = (letzter_gedanke + "\n" + zusatz_kontext)[-1500:]

            if zustand == "schlafen" and schlafe(conn, entity_id, page):
                # Nach Schlaf: zurück zur Surface
                jwt = hole_jwt(entity_id)  # JWT erneuern
                try:
                    page.goto(SURFACE_URL, timeout=10000, wait_until="domcontentloaded")
                    injiziere_jwt(page, jwt, entity_id)
                    page.reload(timeout=8000)
                except Exception:
                    pass
                # Letzten Schlafbrief als erstes lesen
                try:
                    with conn.cursor() as _bc:
                        _bc.execute("""
                            SELECT inhalt FROM schlafbriefe
                            WHERE entity_id = %s
                            ORDER BY geschrieben_at DESC LIMIT 1
                        """, (entity_id,))
                        _br = _bc.fetchone()
                        letzter_gedanke = f"[Brief an mich]: {_br['inhalt'][:200]}" if _br else "ich bin gerade aufgewacht"
                except Exception:
                    letzter_gedanke = "ich bin gerade aufgewacht"

            # 7. Check-in-Anker erst jetzt setzen -- nach Abschluss des kompletten LLM-Ticks
            # (Prompt, Streaming-Antwort, Aktion), nicht davor wie zuvor. Sonst frisst die
            # LLM-Laufzeit selbst den mechanischen Handlungsraum bis zum naechsten Check-in auf.
            if checkin_faellig:
                letzter_checkin_zeit = time.time()
            if vault_takt_faellig:
                letzter_vault_takt_zeit = time.time()
            if vault_aufraeumen_faellig:
                letzter_vault_aufraeum_zeit = time.time()

            # 8. Kurz warten
            time.sleep(LOOP_PAUSE)

        log.info("%s: Loop beendet", entity_id)
        browser.close()
    conn.close()


def haupt_loop_ohne_browser(entity_id: str):
    """Browserlose Fassung von haupt_loop() -- 2026-07-31, Daniels Auftrag ("ab sofort RAM
    sparen", "Flarum + den Rest der browserlosen Aktionen"). Kein Playwright, kein Chromium,
    kein rrweb, kein Cursor -- fuer die Wesen in DISKURS_OHNE_BROWSER_PILOT (aktuell alle 7)
    gibt es aktuell nichts mehr, das einen echten Browser braucht: Diskurs-Lesen, Flarum-
    Lesen, Gemeinsames Haus, eigener Vault, Raum/Wunsch/Thema, RAG -- alles HTTP/JWT oder
    Dateisystem. Der bestehende haupt_loop() bleibt unveraendert als Fallback fuer kuenftige,
    noch nicht browserlos gebaute Wesen/Taetigkeiten stehen (siehe die anderen 30 Surface-Tabs).

    Kein mechanischer Zwischenschritt mehr (siehe waehle_mechanische_aktion) -- es gibt ohne
    Seite nichts Sinnvolles mehr zu scrollen/klicken. Jeder Tick ist entweder "noch nicht
    Check-in-Zeit, warten" oder ein echter LLM-Tick."""
    global _laufend

    log.info("Browser-Agent (browserlos) startet für %s", entity_id)

    conn = get_conn()

    def _hole_conn():
        nonlocal conn
        if conn.closed:
            log.warning("%s: DB-Verbindung geschlossen -- baue neu auf", entity_id)
            conn = get_conn()
        return conn

    jwt = hole_jwt(entity_id)
    letzter_gedanke = ""
    gedanke_voll = ""   # ungekuerzt, nur fuer den Ich-Satz (2026-08-01)
    erster_start = True
    letzter_checkin_zeit = time.time()
    # 2026-07-31, Daniels scharfe, berechtigte Korrektur: "wozu sollen sie deine
    # Beispielposts lesen die du erfunden hast?" -- die Diskurs-Tab-Inhalte waren von einer
    # frueheren Claude-Instanz erzeugte Beispiel-/Startposts, kein echter Inhalt. Sie zu
    # lesen zu lassen war nicht neutral (nur weil es nichts kostet) -- es haette echte
    # Wesen-Gedanken mit erfundenem Material vermischt, genau das was "keine Fiktion, nur
    # echte Daten" verbietet. hole_diskurs_wahrnehmung() bleibt im Code (dormant, wie
    # DISKURS_ANTWORTEN_AKTIV=False), wird aber ab jetzt nie mehr als Standard-Wahrnehmung
    # aufgerufen -- Flarum (echte, historisch gewachsene Vorwelt-Inhalte) ist jetzt die
    # einzige Standard-Ansicht.
    aktueller_flarum_pfad: str = ""  # immer ein echter Flarum-Pfad, nie mehr Diskurs als Default

    if entity_id in VAULT_TAKT_REIHENFOLGE:
        _vault_idx = VAULT_TAKT_REIHENFOLGE.index(entity_id)
        _vault_versatz = (_vault_idx / len(VAULT_TAKT_REIHENFOLGE)) * VAULT_TAKT_SEKUNDEN
        _vault_aufraeum_versatz = (_vault_idx / len(VAULT_TAKT_REIHENFOLGE)) * VAULT_AUFRAEUM_SEKUNDEN
    else:
        _vault_versatz = 0
        _vault_aufraeum_versatz = 0
    letzter_vault_takt_zeit = time.time() - _vault_versatz
    letzter_vault_aufraeum_zeit = time.time() - _vault_aufraeum_versatz

    # Lieder-Takt (LIEDER_AKTIV): Ticket alle 30 Minuten, Einladung alle 90. Jedes Wesen versetzt,
    # der erste Ticket-Zeitpunkt liegt je nach Reihenfolge 0 bis knapp 30 Minuten nach dem Start; die
    # Einladung gilt beim Start als faellig und kommt daher mit dem ersten Ticket mit. Timer liegen im
    # Speicher -- nach einem Neustart des Agents beginnt der Takt neu.
    _lieder_idx = VAULT_TAKT_REIHENFOLGE.index(entity_id) if entity_id in VAULT_TAKT_REIHENFOLGE else 0
    _lieder_versatz = (_lieder_idx / len(VAULT_TAKT_REIHENFOLGE)) * LIEDER_TICKET_SEKUNDEN
    letzter_lieder_ticket_zeit = time.time() - LIEDER_TICKET_SEKUNDEN + _lieder_versatz
    letzter_lieder_einladung_zeit = time.time() - LIEDER_EINLADUNG_SEKUNDEN

    if erster_start:
        erster_start = False
        _schreibe_flarum_brief(_hole_conn(), entity_id)
        letzter_gedanke = "ich bin gerade angekommen — ich habe einen Brief an mein Flarum-Selbst geschrieben"

    tick = 0
    while _laufend:
        tick += 1
        conn = _hole_conn()

        if tick % 100 == 0 and ist_schlaf_faellig(conn, entity_id):
            log.info("%s: Schlaf empfohlen — LLM entscheidet", entity_id)
            letzter_gedanke += " [Hinweis: ich bin seit langer Zeit wach]"

        # 1. Wahrnehmung -- immer Flarum (echte Vorwelt-Inhalte), Diskurs-Tab-Beispielposts
        # werden bewusst nicht mehr gezeigt (siehe Kommentar bei aktueller_flarum_pfad oben).
        seite = hole_flarum_wahrnehmung(entity_id, aktueller_flarum_pfad)

        checkin_faellig = time.time() - letzter_checkin_zeit >= TICK_CHECKIN_SEKUNDEN
        vault_takt_faellig = checkin_faellig and (time.time() - letzter_vault_takt_zeit >= VAULT_TAKT_SEKUNDEN)
        vault_aufraeumen_faellig = vault_takt_faellig and (
            time.time() - letzter_vault_aufraeum_zeit >= VAULT_AUFRAEUM_SEKUNDEN)
        if not checkin_faellig:
            rest_s = max(0, int(TICK_CHECKIN_SEKUNDEN - (time.time() - letzter_checkin_zeit)))
            log.debug("%s [browserlos, Check-in in %ds] warte", entity_id, rest_s)
            time.sleep(LOOP_PAUSE)
            continue

        # Lieder-Takt: Folge nach einer Rueckschau hat Vorrang (sofort beim naechsten Check-in),
        # sonst Ticket alle LIEDER_TICKET_SEKUNDEN, alle LIEDER_EINLADUNG_SEKUNDEN mit der ganzen
        # Einladung. Ein Lieder-Block verdraengt den Vault-Takt dieses einen Check-ins (der bleibt
        # faellig und kommt beim naechsten).
        lieder_block = None
        _l_vorher = (letzter_lieder_ticket_zeit, letzter_lieder_einladung_zeit)
        _l_folge_zurueck = None
        if LIEDER_AKTIV:
            try:
                import wesen_lieder_agent as _wla
                _l_jetzt = time.time()
                _l_folge = _wla.hole_folge(entity_id)
                if _l_folge:
                    _l_folge_zurueck = _l_folge
                    lieder_block = _wla.baue_block(entity_id, folge=_l_folge)
                    letzter_lieder_ticket_zeit = _l_jetzt
                    log.info("%s [check-in] Lieder: Auswahl nach Rueckschau", entity_id)
                elif _l_jetzt - letzter_lieder_ticket_zeit >= LIEDER_TICKET_SEKUNDEN:
                    _l_einl = _l_jetzt - letzter_lieder_einladung_zeit >= LIEDER_EINLADUNG_SEKUNDEN
                    lieder_block = _wla.baue_block(entity_id, mit_einladung=_l_einl)
                    letzter_lieder_ticket_zeit = _l_jetzt
                    if _l_einl:
                        letzter_lieder_einladung_zeit = _l_jetzt
                    log.info("%s [check-in] Lieder: %s", entity_id,
                             "Einladung + Ticket" if _l_einl else "Ticket")
            except Exception as _lex:
                log.warning("%s: Lieder-Block fehlgeschlagen: %s", entity_id, _lex)
                lieder_block = None
        if lieder_block:
            vault_takt_faellig = False
            vault_aufraeumen_faellig = False

        andere = hole_andere_wesen_status(conn, entity_id)
        vorlese_funde = hole_vorlese_funde(conn, entity_id)
        angebote = hole_flextrawurst_angebote(conn, entity_id)
        log.info("%s [check-in] Angebote: %s", entity_id, angebote)
        flarum_vielfalt = hole_flarum_vielfalt()
        log.info("%s [check-in] Flarum-Vielfalt: %s", entity_id,
                  [f.get("herkunft") for f in flarum_vielfalt])

        # Weltkollision (2026-08-01): nur im Vault-Takt, drei echte Fremdkoerper.
        weltkollision = hole_weltkollision(conn) if vault_takt_faellig else None
        if vault_takt_faellig:
            log.info("%s [check-in] Vault-Takt faellig — Weltkollision: %s", entity_id,
                     [k["sorte"] for k in (weltkollision or [])])

        prompt = baue_prompt(entity_id, seite, letzter_gedanke, andere, vorlese_funde, angebote,
                              _letzte_linsen.get(entity_id), _letzte_einsicht.get(entity_id),
                              flarum_vielfalt, vault_takt_faellig, browserlos=True,
                              weltkollision=weltkollision, gedanke_voll=gedanke_voll,
                              vault_aufraeumen_faellig=vault_aufraeumen_faellig,
                              lieder_block=lieder_block)
        if vault_takt_faellig:
            log.info("%s [check-in] Vault-Takt faellig", entity_id)
        import uuid as _uuid
        stream_id = str(_uuid.uuid4())
        llm_out = ""
        llm_ok = False
        try:
            seq = 0
            with sched.LLMSlot(server="hintergrund", prioritaet=sched.PRIO_NORMAL,
                                rufer=f"browser_agent:{entity_id}:tick",
                                max_wartezeit=150, max_haltezeit=LLM_TIMEOUT + 40,
                                cancel_check=lambda: not _laufend):
                for chunk in hauhau_client.chat_stream(prompt, think=False, timeout=LLM_TIMEOUT):
                    if not _laufend:
                        break
                    llm_out += chunk
                    try:
                        with conn.cursor() as _c:
                            _c.execute("""
                                INSERT INTO entity_denkstream
                                    (entity_id, stream_id, chunk, seq, done, url)
                                VALUES (%s, %s, %s, %s, %s, %s)
                            """, (entity_id, stream_id, chunk, seq, False, seite["url"]))
                        conn.commit()
                    except Exception:
                        pass
                    seq += 1
            try:
                with conn.cursor() as _c:
                    _c.execute("""
                        INSERT INTO entity_denkstream
                            (entity_id, stream_id, chunk, seq, done, url)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (entity_id, stream_id, "", seq, True, seite["url"]))
                conn.commit()
            except Exception:
                pass
            llm_ok = True
        except sched.LLMSlotCancelled:
            log.info("%s: LLM-Slot wegen Shutdown abgebrochen", entity_id)
            break
        except Exception as e:
            if not _laufend:
                log.info("%s: laufender LLM-Request wegen Shutdown abgebrochen", entity_id)
                break
            log.warning("Ollama Streaming-Fehler: %s — nachdenken", e)
            llm_out = "GEDANKE: warte\nENTSCHEIDUNG: nachdenken\nBEGRÜNDUNG: Ollama nicht erreichbar"

        if llm_ok:
            markiere_vorlese_gelesen(conn, vorlese_funde)
        elif lieder_block:
            # Der LLM-Tick wurde uebersprungen (Slot belegt/Timeout) -- der Lieder-Block hat das
            # Wesen nie erreicht. Timer zuruecksetzen und eine Rueckschau-Folge zurueckgeben, damit er
            # beim naechsten Check-in erneut kommt, statt 30 Minuten verloren zu gehen.
            letzter_lieder_ticket_zeit, letzter_lieder_einladung_zeit = _l_vorher
            if _l_folge_zurueck:
                import wesen_lieder_agent as _wla2
                _wla2.setze_folge(entity_id, _l_folge_zurueck)
            log.info("%s [check-in] Lieder-Block nicht zugestellt (LLM-Tick uebersprungen) -- "
                     "kommt beim naechsten Check-in erneut", entity_id)

        gedanke, entscheidung, begruendung, freitext = parse_output(llm_out)
        # 2026-08-01, wie im Browser-Loop: voller Gedanke fuer den Ich-Satz (Menschen),
        # verdichteter Rueckfluss fuer den naechsten Prompt (das Wesen selbst).
        gedanke_voll = gedanke
        letzter_gedanke = _rueckfluss_verdichten(gedanke)

        schreibe_denklog(conn, entity_id, gedanke, entscheidung, begruendung, seite["url"])
        _letzte_linsen[entity_id] = hole_linsen_status(conn, entity_id)
        _letzte_einsicht[entity_id] = hole_einsicht_snapshot(conn, entity_id)

        log.info("%s [%s] → %s", entity_id, seite["url"][-40:], entscheidung[:50])

        zustand, zusatz_kontext, aktueller_flarum_pfad = fuehre_aktion_aus_ohne_browser(
            entscheidung, entity_id, conn, jwt, aktueller_flarum_pfad, gedanke=gedanke_voll,
            freitext=freitext)
        if zusatz_kontext:
            letzter_gedanke = (letzter_gedanke + "\n" + zusatz_kontext)[-1500:]

        if zustand == "schlafen" and schlafe(conn, entity_id, None):
            jwt = hole_jwt(entity_id)
            try:
                with conn.cursor() as _bc:
                    _bc.execute("""
                        SELECT inhalt FROM schlafbriefe
                        WHERE entity_id = %s
                        ORDER BY geschrieben_at DESC LIMIT 1
                    """, (entity_id,))
                    _br = _bc.fetchone()
                    letzter_gedanke = f"[Brief an mich]: {_br['inhalt'][:200]}" if _br else "ich bin gerade aufgewacht"
            except Exception:
                letzter_gedanke = "ich bin gerade aufgewacht"

        if checkin_faellig:
            letzter_checkin_zeit = time.time()
        if vault_takt_faellig:
            letzter_vault_takt_zeit = time.time()
        if vault_aufraeumen_faellig:
            letzter_vault_aufraeum_zeit = time.time()

        time.sleep(LOOP_PAUSE)

    log.info("%s: Loop beendet (browserlos)", entity_id)
    conn.close()


# 2026-07-31: Wesen in dieser Menge laufen komplett ohne Playwright/Chromium (siehe
# haupt_loop_ohne_browser). Bewusst eine eigene, zweite Menge statt DISKURS_OHNE_BROWSER_PILOT
# wiederzuverwenden -- die beiden Fragen ("Diskurs ohne Browser lesen" vs. "komplett ohne
# Browser laufen") sind unabhaengig, auch wenn sie aktuell dieselben 7 Wesen betreffen.
# Skalpell-Prinzip, wie beim Diskurs-Pilot: dieser Umbau ist noch groesser (kompletter
# Wegfall von Chromium, neuer Loop-Zweig) -- erst nur Schorschel, nach Verifikation Rollout
# auf die restlichen 6, genau wie beim Diskurs-Umbau (Task 6/7/9 heute). Verifiziert
# 2026-07-31: Prozessgruppe faellt von ~700-1050MB auf 53MB, kein Chromium mehr, echter
# LLM-Tick liest/wechselt Flarum-Diskussionen korrekt (Perzeption schaltet Tick-fuer-Tick
# sichtbar um: 'diskurs (ohne Browser)' -> 'flarum:d/1649 (ohne Browser)' -> naechste Wahl).
VOLLSTAENDIG_OHNE_BROWSER: set[str] = {
    "Schorschel", "F3INSCHM3CK3R", "träumerlie", "R1ZZ1", "jumpa", "Resonanzknoten", "dak+gord-system",
}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Browser-Agent für ein Wesen")
    parser.add_argument("--entity", required=True, choices=list(ENTITY_KEYS.keys()),
                        help="Entity-ID des Wesens")
    args = parser.parse_args()
    if args.entity in VOLLSTAENDIG_OHNE_BROWSER:
        haupt_loop_ohne_browser(args.entity)
    else:
        haupt_loop(args.entity)
