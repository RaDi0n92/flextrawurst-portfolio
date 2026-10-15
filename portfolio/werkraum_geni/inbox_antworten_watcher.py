#!/usr/bin/env python3
"""GENI-Inbox — Antwort-Watcher, gezielt auf geni_inbox/*/antworten/.

2026-07-31, Daniel, ausdruecklich NICHT ueber geni/hoerer.pys generisches
Mitlesen: "sie soll gezielt wissen sobald etwas beantwortet wurde koennen wir
sie losschicken zum direktem lesen denn geni notiert sich auch jede frage ueber
jeden ... mit datum und uhrzeit und wenn eine antwort kommt dann wird das auch
mit aufgenommen von geni direkt unter der frage ... auch mit datum und uhrzeit
(lesedatum)."

Eigener, dedizierter Watchdog-Daemon (nicht hoerer.py) -- kennt die Frage/Antwort-
Struktur und verknuepft eine neue Antwort-Datei gezielt mit der zugehoerigen Frage
im Protokoll (gedaechtnis/fragen_antworten/<id>.json), statt sie wie hoerer.py nur
als generischen "Datei geaendert"-Knoten zu behandeln.

Zuordnung: eine neue Antwort-Datei wird der JEWEILS AELTESTEN noch unbeantworteten
Frage dieses Teilnehmers zugeordnet (erste offene Frage zuerst) -- nicht der
neuesten, damit bei mehreren liegengebliebenen Fragen die Reihenfolge stimmt.

Traegt jede beantwortete Frage zusaetzlich in einen EIGENEN Vault ein --
werkraum/geni_dokumentation/<id>.md -- getrennt vom geni_inbox-Vault und von
GENIs internem, nicht einsehbarem Gedaechtnis. 2026-08-01, Daniel-Korrektur:
"das ist alles ein vault ... und geni die dort doku ueber uns macht ist ein
eigener vault" -- urspruenglich faelschlich unter geni/gedaechtnis/dokumentation/
(gitignored, nicht einsehbar) abgelegt, hierher verschoben.

Aufruf: systemd-Dienst, laeuft dauerhaft. Manueller Test: python3 inbox_antworten_watcher.py
"""

import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

sys.path.insert(0, "/root/werkraum")
sys.path.insert(0, "/root/werkraum/geni")
from teilnehmer_roster import teilnehmer_by_id

INBOX_VAULT = Path("/root/werkraum/geni_inbox")
FRAGEN_DIR = Path("/root/werkraum/geni/gedaechtnis/fragen_antworten")

# 2026-08-04, Daniel: "wir brauchen einmal in jeder geni_inbox nchmal einen ordner bei jeden
# namens ...gelesen...und alle hsben die aufgame nach dem lesen die datei dort
# hinzuverschieben..und wenn geni unsere anworten gelesen hat.. kommen die auch in ihren
# 'gelesen' ordner"
#
# Die Regel, die daraus wird, ist fuer alle dieselbe: <id>/gelesen/ enthaelt, was der
# Besitzer dieses Ordners gelesen hat. Bei einem Teilnehmer sind das die Fragen aus seiner
# inbox/. Bei GENI sind es unsere Antworten -- und die landen deshalb in geni/gelesen/,
# nicht beim jeweiligen Teilnehmer.
GELESEN_VON_GENI = INBOX_VAULT / "geni" / "gelesen"

# Nicht sofort verschieben: Obsidian legt eine Notiz erst leer an und schreibt den Text beim
# Speichern nach; wer noch tippt, wuerde die Datei unter den Haenden verlieren. Erst wenn
# eine Antwort so lange unveraendert liegt, gilt sie als fertig.
RUHEZEIT_SEKUNDEN = 300
AUFRAEUM_TAKT_SEKUNDEN = 60

# 2026-08-04, Daniel woertlich -- dieser Satz geht 1:1 in ihren Prompt, nicht umformuliert:
ERLAUBNIS = "Wenn du, geni die antworten liest darfstt du überall noch kommentare abgeben"

# Vorher wurde eine Antwort nur maschinell ins Protokoll uebernommen. Am 04.08. zeigte das
# Suchlog, was das wert war: Daniels drei Antworten lagen seit dem 01.08. im Index und waren
# in KEINER Suche je aufgetaucht -- aufgenommen, aber nie gedacht. Seitdem liest GENI die
# Antwort wirklich, mit einem eigenen Aufruf, und darf dabei kommentieren.
KOMMENTAR_ANFANG = "<!-- GENI-KOMMENTARE -->"
MAX_KOMMENTARE = 8


def _protokoll_laden(teilnehmer_id: str) -> list:
    pfad = FRAGEN_DIR / f"{teilnehmer_id}.json"
    if not pfad.exists():
        return []
    try:
        return json.loads(pfad.read_text())
    except Exception:
        return []


def _protokoll_speichern(teilnehmer_id: str, eintraege: list):
    FRAGEN_DIR.mkdir(parents=True, exist_ok=True)
    (FRAGEN_DIR / f"{teilnehmer_id}.json").write_text(
        json.dumps(eintraege, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _zuordnen(inhalt: str, eintraege: list) -> list:
    """Ordnet die Antwortdatei den passenden Fragen zu.

    2026-08-01: Daniels erste echte Antwortdatei ("Meine 3 antworten auf deine
    fragen GENI.md") enthielt DREI Antworten auf drei verschiedene Fragen, jeweils
    mit der zitierten Frage darueber. Die alte Logik haette die ganze Datei der
    aeltesten offenen Frage zugeschlagen -- also zwei Antworten falsch abgelegt.

    Deshalb: taucht der Fragetext woertlich in der Datei auf, wird der Abschnitt
    ab dieser Fundstelle bis zur naechsten zitierten Frage dieser Frage zugeordnet.
    Kein Treffer -> Rueckfall auf das alte Verhalten (aelteste offene Frage
    bekommt den ganzen Text).

    Rueckgabe: Liste von (eintrag, antworttext).
    """
    fundstellen = []
    for e in eintraege:
        frage = (e.get("frage") or "").strip()
        if not frage:
            continue
        pos = inhalt.find(frage)
        if pos >= 0:
            fundstellen.append((pos + len(frage), e))

    if not fundstellen:
        offen = next((e for e in eintraege if e.get("antwort") is None), None)
        return [(offen, inhalt)] if offen else []

    fundstellen.sort(key=lambda t: t[0])
    ergebnis = []
    for i, (start, eintrag) in enumerate(fundstellen):
        ende = fundstellen[i + 1][0] - len(eintrag.get("frage") or "") if i + 1 < len(fundstellen) else len(inhalt)
        text = inhalt[start:ende].strip().lstrip(":").strip()
        # fuehrende Trennlinien/Beschriftungen wie "____" oder "Antwort von Daniel:"
        text = re.sub(r"^[_\-—\s]*", "", text)
        text = re.sub(r"^(Antwort( von [^\n:]{1,40})?)\s*:?\s*", "", text, flags=re.IGNORECASE)
        # Der Anfang des NAECHSTEN Frage-Blocks gehoert nicht mehr zu dieser
        # Antwort. Die Grenze oben rechnet nur mit der Fragelaenge, nicht mit
        # dem Vorspann ("Frage:" / "**GENI fragt** (...)"), deshalb hier hart
        # am ersten solchen Marker abschneiden.
        schnitt = re.search(r"\n\s*(Frage\s*:?|\*\*GENI fragt\*\*)", text)
        if schnitt:
            text = text[:schnitt.start()]
        text = text.strip()
        if text:
            ergebnis.append((eintrag, text))
    return ergebnis


def _antwort_verarbeiten(teilnehmer_id: str, antwort_pfad: Path):
    teilnehmer = teilnehmer_by_id(teilnehmer_id)
    if not teilnehmer:
        return
    try:
        inhalt = antwort_pfad.read_text(encoding="utf-8", errors="ignore").strip()
    except Exception:
        return
    if not inhalt:
        return

    eintraege = _protokoll_laden(teilnehmer_id)
    zuordnungen = _zuordnen(inhalt, eintraege)

    if not zuordnungen:
        neu = {"frage": "(keine protokollierte Frage gefunden)", "datum_frage": None,
               "inbox_datei": None, "antwort": None, "datum_antwort": None, "datum_gelesen": None}
        eintraege.append(neu)
        zuordnungen = [(neu, inhalt)]

    datum_antwort = datetime.fromtimestamp(antwort_pfad.stat().st_mtime, tz=timezone.utc).isoformat()
    datum_gelesen = datetime.now(timezone.utc).isoformat()

    geschrieben = 0
    for eintrag, text in zuordnungen:
        if eintrag is None:
            continue
        # Unveraenderte Wiederholung nicht erneut in die Doku schreiben
        # (on_modified feuert bei jedem Speichern in Obsidian erneut).
        if eintrag.get("antwort") == text:
            continue
        eintrag["antwort"] = text
        eintrag["antwort_datei"] = str(antwort_pfad)
        eintrag["datum_antwort"] = datum_antwort
        eintrag["datum_gelesen"] = datum_gelesen
        # 2026-08-01, Daniel: "klar entfernen wozu soll alles doppelt sein" --
        # der fertig formatierte "## Frage & Antwort"-Block wanderte bisher
        # zusaetzlich in die Doku (geni_dokumentation/). Das war doppelt (der
        # Austausch steht im geni_inbox-Vault) und ausserdem von MIR formatiert,
        # nicht von GENI geschrieben. Die Doku enthaelt nur noch ihren eigenen
        # Text; Frage, Antwort und beide Zeitstempel bleiben vollstaendig im
        # Protokoll unten erhalten.
        geschrieben += 1

    if geschrieben:
        _protokoll_speichern(teilnehmer_id, eintraege)
        print(f"[{teilnehmer_id}] {geschrieben} Antwort(en) aufgenommen aus {antwort_pfad.name}",
              flush=True)

        # Aufnehmen ist nicht Lesen. Erst hier liest sie wirklich -- und darf kommentieren.
        for eintrag, text in zuordnungen:
            if eintrag is None or eintrag.get("kommentiert"):
                continue
            try:
                kommentare = _kommentare_holen(teilnehmer_id,
                                               eintrag.get("frage") or "(unbekannt)", text)
            except Exception as exc:
                print(f"[{teilnehmer_id}] Kommentarlauf fehlgeschlagen: {exc}", flush=True)
                break
            gesetzt = _kommentare_einfuegen(antwort_pfad, kommentare)
            eintrag["kommentiert"] = datetime.now(timezone.utc).isoformat()
            eintrag["kommentare"] = kommentare
            print(f"[{teilnehmer_id}] GENI hat gelesen und {gesetzt} Kommentar(e) gesetzt",
                  flush=True)
            break   # eine Datei, ein Kommentarlauf
        _protokoll_speichern(teilnehmer_id, eintraege)


def _kommentare_holen(teilnehmer_id: str, frage: str, antwort: str) -> list:
    """GENI liest die Antwort wirklich und darf dazu sagen, was sie will.

    Daniels Erlaubnis steht woertlich im Prompt (ERLAUBNIS) -- nicht umformuliert, nicht
    geglaettet, auch die Tippfehler bleiben.

    Sie gibt Kommentare mit einem Ankerzitat zurueck, damit sie an der Stelle stehen koennen,
    auf die sie sich beziehen ("ueberall"). Der fremde Text wird dabei nie veraendert: wir
    fuegen ihre Zeilen NACH dem Ankerzitat ein, statt sie den Text neu schreiben zu lassen.
    Wer antwortet, soll seine eigenen Worte spaeter unveraendert wiederfinden.
    """
    import hauhau_client
    from sprechen import kern_laden

    nachricht = (f'{ERLAUBNIS}\n\n'
                 f'das hier ist die antwort von "{teilnehmer_id}" auf deine frage.\n\n'
                 f'DEINE FRAGE WAR:\n{frage}\n\n'
                 f'DIE ANTWORT:\n{antwort}\n\n'
                 f'gib deine kommentare als JSON-Liste zurueck, sonst nichts. jeder eintrag:\n'
                 f'{{"stelle": "ein woertliches kurzes zitat aus der antwort, an dem dein '
                 f'kommentar stehen soll", "kommentar": "was du dazu sagst"}}\n'
                 f'hoechstens {MAX_KOMMENTARE}. wenn du nichts sagen willst: []')

    antwort_roh = hauhau_client.chat_raw(
        [{"role": "user", "content": nachricht}],
        system=f"Du bist GENI.\n\n{kern_laden()}",
        think=False, max_tokens=3000, temperature=0.85, timeout=720.0)
    text = (antwort_roh["choices"][0]["message"].get("content") or "").strip()

    # Sie schreibt oft noch etwas drumherum -- die Liste herausschneiden statt daran scheitern
    if "[" in text and "]" in text:
        text = text[text.index("["):text.rindex("]") + 1]
    try:
        roh = json.loads(text)
    except Exception:
        return []
    kommentare = []
    for k in roh if isinstance(roh, list) else []:
        if isinstance(k, dict) and (k.get("kommentar") or "").strip():
            kommentare.append({"stelle": (k.get("stelle") or "").strip(),
                               "kommentar": k["kommentar"].strip()})
    return kommentare[:MAX_KOMMENTARE]


def _kommentare_einfuegen(pfad: Path, kommentare: list) -> int:
    """Schreibt GENIs Kommentare an die Stellen, auf die sie sich beziehen.

    Findet sich das Ankerzitat nicht (sie zitiert nicht immer genau), kommt der Kommentar
    unten an. Lieber am falschen Ort als verloren.
    """
    if not kommentare:
        return 0
    try:
        text = pfad.read_text(encoding="utf-8")
    except Exception:
        return 0
    if KOMMENTAR_ANFANG in text:      # schon kommentiert, nicht doppelt
        return 0

    zeit = datetime.now().strftime("%d.%m.%Y %H:%M")
    gesetzt, ohne_anker = 0, []
    for k in kommentare:
        block = f"\n\n> **GENI, {zeit}:** {k['kommentar']}\n"
        anker = k["stelle"]
        stelle = text.find(anker) if anker else -1
        if stelle == -1:
            ohne_anker.append(k["kommentar"])
            continue
        ende = text.find("\n", stelle + len(anker))
        ende = len(text) if ende == -1 else ende
        text = text[:ende] + block + text[ende:]
        gesetzt += 1

    if ohne_anker:
        text += "\n\n" + "\n\n".join(f"> **GENI, {zeit}:** {k}" for k in ohne_anker) + "\n"
        gesetzt += len(ohne_anker)

    text += f"\n{KOMMENTAR_ANFANG}\n"
    try:
        pfad.write_text(text, encoding="utf-8")
    except Exception:
        return 0
    return gesetzt


class AntwortHoerer(FileSystemEventHandler):
    def _verarbeiten(self, pfad: str, ist_verzeichnis: bool):
        if ist_verzeichnis:
            return
        p = Path(pfad)
        try:
            teile = p.relative_to(INBOX_VAULT).parts
        except ValueError:
            return
        if len(teile) < 3 or teile[1] != "antworten":
            return
        # 2026-08-01: live aufgefallen -- die .gitkeep-Dateien, die die Ordner-
        # struktur in git haelt, wurden als echte Antworten verarbeitet und
        # landeten in allen 16 Dokus. Nur sichtbare .md-Dateien zaehlen als
        # Antwort; Punktdateien (.gitkeep, .DS_Store, Obsidian-Temp) nie.
        if p.name.startswith(".") or p.suffix.lower() != ".md":
            return
        teilnehmer_id = teile[0]
        _antwort_verarbeiten(teilnehmer_id, p)

    def on_created(self, event):
        self._verarbeiten(event.src_path, event.is_directory)

    def on_moved(self, event):
        # Atomare Schreibvorgaenge (Temp+Rename) -- gleiches Muster wie der
        # on_moved-Fix in geni/hoerer.py von heute Nachmittag.
        self._verarbeiten(event.dest_path, event.is_directory)

    def on_modified(self, event):
        # 2026-08-01, an Daniels erster echter Antwort aufgefallen: Obsidian legt
        # eine neue Notiz zuerst LEER an (on_created -> Inhalt leer -> verworfen)
        # und schreibt den Text erst beim Speichern (on_modified). Ohne diesen
        # Handler kam seine Antwort nie an. _antwort_verarbeiten() ist gegen
        # Mehrfachausloesung abgesichert (unveraenderter Text wird uebersprungen).
        self._verarbeiten(event.src_path, event.is_directory)


def _ist_gelesen(teilnehmer_id: str, antwort_pfad: Path) -> bool:
    """Steht diese Antwort mit Lesedatum im Protokoll?

    Seit 2026-08-04 zaehlt zusaetzlich, ob GENI die Antwort auch kommentiert hat -- sonst
    waere "gelesen" wieder nur "maschinell aufgenommen", und genau der Unterschied war der
    Anlass fuer den Umbau.

    Der Abgleich geht ueber Pfad UND Inhalt. Grund, live gefunden 2026-08-04 an Daniels
    eigenen Antworten: er hatte die Datei in Obsidian umbenannt ("Meine 3 antworten auf deine
    fragen GENI.md" -> "Meine 3 antworten an GENI.md"). Der Pfad im Protokoll zeigte danach
    ins Leere, obwohl GENI den Text laengst gelesen hatte. Gelesen wurde der Inhalt, nicht
    der Dateiname -- also entscheidet der Inhalt.
    """
    eintraege = _protokoll_laden(teilnehmer_id)
    for e in eintraege:
        if (e.get("antwort_datei") == str(antwort_pfad)
                and e.get("datum_gelesen") and e.get("kommentiert")):
            return True
    try:
        inhalt = antwort_pfad.read_text(encoding="utf-8", errors="ignore").strip()
    except Exception:
        return False
    if not inhalt:
        return False
    for e in eintraege:
        antwort = (e.get("antwort") or "").strip()
        if (antwort and e.get("datum_gelesen") and e.get("kommentiert")
                and (antwort in inhalt or inhalt in antwort)):
            return True
    return False


def gelesene_wegraeumen() -> int:
    """Verschiebt fertig gelesene Antworten nach geni/gelesen/.

    Bewusst kein Verschieben direkt im Ereignis: erst wenn eine Datei RUHEZEIT_SEKUNDEN lang
    unveraendert liegt UND mit Lesedatum im Protokoll steht, gilt sie als abgeschlossen.
    Sonst waere sie jemandem mitten im Schreiben unter den Haenden verschwunden.

    Der Dateiname behaelt den Teilnehmer vorn, damit in GENIs Ordner erkennbar bleibt, von
    wem die Antwort kam -- der Pfad sagt es nach dem Verschieben ja nicht mehr.
    """
    GELESEN_VON_GENI.mkdir(parents=True, exist_ok=True)
    jetzt = time.time()
    bewegt = 0
    for ordner in sorted(INBOX_VAULT.glob("*/antworten")):
        teilnehmer_id = ordner.parent.name
        for datei in sorted(ordner.glob("*.md")):
            if datei.name.startswith("."):
                continue
            if jetzt - datei.stat().st_mtime < RUHEZEIT_SEKUNDEN:
                continue
            if not _ist_gelesen(teilnehmer_id, datei):
                continue
            ziel = GELESEN_VON_GENI / f"{teilnehmer_id}__{datei.name}"
            n = 2
            while ziel.exists():
                ziel = GELESEN_VON_GENI / f"{teilnehmer_id}__{datei.stem}_{n}{datei.suffix}"
                n += 1
            try:
                datei.rename(ziel)
                # Der Pfad im Protokoll muss mitwandern, sonst zeigt er ins Leere.
                eintraege = _protokoll_laden(teilnehmer_id)
                for e in eintraege:
                    if e.get("antwort_datei") in (str(datei), None):
                        if e.get("antwort_datei") == str(datei):
                            e["antwort_datei"] = str(ziel)
                            e["datum_weggeraeumt"] = datetime.now(timezone.utc).isoformat()
                _protokoll_speichern(teilnehmer_id, eintraege)
                print(f"[geni] gelesen und weggeraeumt: {teilnehmer_id}/{datei.name}", flush=True)
                bewegt += 1
            except Exception as exc:
                print(f"[geni] konnte {datei} nicht verschieben: {exc}", flush=True)
    return bewegt


def main():
    INBOX_VAULT.mkdir(parents=True, exist_ok=True)
    observer = Observer()
    observer.schedule(AntwortHoerer(), str(INBOX_VAULT), recursive=True)
    observer.start()
    print(f"GENI-Antwort-Watcher laeuft auf {INBOX_VAULT}")
    letzter_takt = 0.0
    try:
        while True:
            time.sleep(2)
            if time.time() - letzter_takt >= AUFRAEUM_TAKT_SEKUNDEN:
                letzter_takt = time.time()
                try:
                    gelesene_wegraeumen()
                except Exception as exc:
                    print(f"[geni] Aufraeumlauf fehlgeschlagen: {exc}", flush=True)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
