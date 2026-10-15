#!/usr/bin/env python3
"""
Obsidian-Vault-Agent: schreibt fuer ein Wesen in dessen eigenen Vault --
mechanisch, direkt auf die Platte, seit 2026-08-14 OHNE Docker/Selkies/xdotool.

# WICHTIG -- GESCHICHTE DIESES MODULS, nicht loeschen, nur verstehen:
#
# Phase 1 (ab 2026-07-21, Daniels Auftrag woertlich: "eine ganz neue art von
# vault erzeugt vom wesen selbst ... aber ich will es ohne llm call ich will
# schreiben in genau der menschenart und weise ... tippen wie auf der
# schreibmaschiene"): jedes Wesen bekam einen eigenen Docker-Container mit
# echtem Obsidian, gestreamt per Selkies (WebRTC/Pixel-Streaming, aehnlich
# noVNC). Playwright steuerte Navigation (Ctrl+O Quick-Switcher), xdotool via
# `docker exec` tippte den Text zeichenweise direkt in die X11-Sitzung des
# Containers -- komplett am Browser vorbei, weil page.keyboard.type() jede
# Grossschreibung auf dem Weg durch Selkies verlor und insert_text() gar nicht
# erst ankam. Fallstricke damals geloest: Ctrl+N-Notizen binden sich nie an
# eine echte Datei (Fix: Datei immer vorher direkt anlegen), Grossbuchstaben-
# Umlaute am Zeilenanfang blieben klein (von Daniel als unwichtig abgesegnet).
#
# Phase 2 (bestaetigt 2026-08-13, Diagnose gegen Schorschels echten Container):
# Selkies liefert nur <canvas>/<video>, KEIN einziges Obsidian-eigenes DOM-
# Element. liste_ordner/umbenennen/verschieben/loeschen wurden deshalb schon
# damals als reine Plattenoperationen gebaut, an Playwright/xdotool vorbei --
# nur das eigentliche SCHREIBEN und LESEN liefen noch ueber Selkies.
#
# Phase 3 (2026-08-14, Daniel woertlich: "wir bauen nen dom nen code ne html
# mit ihren mds und alles editierbar direkt im dom usw ... und ja es ersetzt
# das selkieszeug"): oeffne_datei_und_schreibe() und oeffne_datei_und_lese()
# sind jetzt genau wie liste_ordner/umbenennen/verschieben/loeschen reine
# Plattenoperationen -- KEIN Docker, KEIN Playwright, KEIN xdotool mehr in
# diesem Modul. Sichtbares "Tippen" passiert ab jetzt echt im DOM der neuen
# Seite (wesenvaultsystem_api.py, Port 8097) via Live-Events (Grundgesetz 8),
# nicht mehr durch einen VNC-Stream der ohnehin nie wirklich lesbar war. Die
# 7 obsidian-*-Docker-Container selbst laufen vorerst weiter (mounten
# denselben Ordner, stoeren nicht), werden aber von diesem Modul nicht mehr
# angesprochen -- Stoppen ist ein separater, mit Daniel abgestimmter Schritt.
#
# Omapi-Notiz: dieses Modul war mal ein kleines Kunstwerk aus Playwright-
# Timing-Voodoo. Es bleibt hier oben stehen, weil die Fallstricke echt waren
# und echte Arbeit gekostet haben -- wer den Code danach nochmal so bauen
# muesste, soll nicht bei null anfangen. Aber die Zukunft dieses Moduls ist
# jetzt viel langweiliger, und das ist gut so: eine Datei schreiben sollte
# langweilig sein, nicht ein Browser-Automatisierungs-Abenteuer.
"""

import difflib
import json
import logging
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote

log = logging.getLogger("obsidian-vault-agent")

# Gleiche Konvention wie events_stream_api.py -- FLEXTRAWURST_DB_URI aus der Umgebung,
# mit demselben Fallback-Wert wie dort (der allerdings, Stand 2026-08-14 nachgeprueft,
# NICHT das echte Passwort ist -- die tatsaechlich funktionierenden Werte stehen in
# .agent/flextrawurst-db.env und .agent/dak-gord.env. Trotzdem hier als Fallback belassen,
# damit dieses Modul denselben Code-Pfad wie der Rest des Systems nutzt und ein spaeteres
# Beheben der echten Env-Datei automatisch greift, ohne dieses Modul nochmal anzufassen.
_DB_URI = os.environ.get(
    "FLEXTRAWURST_DB_URI",
    "postgresql://dak:[GESCHWAERZT]@localhost:5432/flextrawurst",
)


def _vault_event_schreiben(event_type: str, entity_id: str, vault_pfad: str, **zusatz) -> None:
    """Schreibt ein Event in die heilige events-Tabelle (Grundgesetz 5) -- loest per
    DB-Trigger automatisch ein NOTIFY auf 'events_stream' aus (migration_events_stream_vault.sql
    hat 'wesen'+'vault_pfad' als kuratierte Routing-Hinweise ergaenzt), damit die neue
    Wesen-Vault-DOM-Seite live sieht was sich veraendert hat (Grundgesetz 8, "Live statt F5").
    Darf niemals einen Schreibvorgang zum Scheitern bringen -- Event-Verlust ist bedauerlich,
    ein wegen eines Logging-Fehlers verlorener Gedanke waere schlimmer."""
    try:
        import psycopg2
        payload = {"wesen": entity_id, "vault_pfad": vault_pfad, **zusatz}
        conn = psycopg2.connect(_DB_URI)
        try:
            with conn, conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO events (event_type, actor_type, actor_id, payload,
                                         origin_type, visibility_layer)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (event_type, "codewesen", entity_id, json.dumps(payload),
                     "wesen_vault", "internal"),
                )
        finally:
            conn.close()
    except Exception as ex:
        log.warning("%s: Vault-Event schreiben fehlgeschlagen (%s): %s", entity_id, event_type, ex)

VAULT_ROOT = Path("/root/werkraum/wesen_vaults")

# Port-Schema: Hauptport (Selkies-Web-GUI) / Zweitport, je einer pro Wesen,
# gleiche Reihenfolge wie ENTITY_KEYS in browser_agent.py.
VAULT_PORTS = {
    "Schorschel": (3093, 3193),
    "F3INSCHM3CK3R": (3094, 3194),
    "träumerlie": (3095, 3195),
    "R1ZZ1": (3096, 3196),
    "jumpa": (3097, 3197),
    "Resonanzknoten": (3098, 3198),
    "dak+gord-system": (3099, 3199),
}

# Externe HTTPS-Ports (nginx, doppelte Basic-Auth: nginx-Ebene + Container-Ebene),
# gleiches Muster wie das bestehende /etc/nginx/sites-available/obsidian.
VAULT_EXTERN_PORTS = {
    "Schorschel": 8445,
    "F3INSCHM3CK3R": 8450,
    "träumerlie": 8451,
    "R1ZZ1": 8452,
    "jumpa": 8453,
    "Resonanzknoten": 8454,
    "dak+gord-system": 8455,
}

# Docker-Containernamen und Basic-Auth-Benutzernamen: explizit statt aus dem
# entity_id abgeleitet -- Docker-Containernamen erlauben nur [a-zA-Z0-9_.-],
# "träumerlie" (Umlaut) und "dak+gord-system" ("+") würden bei automatischer
# Ableitung ungültige oder inkonsistente Namen erzeugen (dieselbe Bug-Klasse
# wie das systemd-%i-vs-%I-Problem vom selben Tag, siehe 29_browser_agent_aktivierung.md).
CONTAINER_NAMES = {
    "Schorschel": "obsidian-schorschel",
    "F3INSCHM3CK3R": "obsidian-f3inschmecker",
    "träumerlie": "obsidian-traeumerlie",
    "R1ZZ1": "obsidian-r1zz1",
    "jumpa": "obsidian-jumpa",
    "Resonanzknoten": "obsidian-resonanzknoten",
    "dak+gord-system": "obsidian-dakgordsystem",
}
CONTAINER_USERS = {
    "Schorschel": "daniel",
    "F3INSCHM3CK3R": "daniel",
    "träumerlie": "daniel",
    "R1ZZ1": "daniel",
    "jumpa": "daniel",
    "Resonanzknoten": "daniel",
    "dak+gord-system": "daniel",
}

# Suffix der Passwort-Umgebungsvariable in .agent/wesen-vaults.env -- ASCII-
# GROSS, aus demselben Grund wie CONTAINER_NAMES/CONTAINER_USERS: bash erlaubt
# weder Umlaute noch "+" in Variablennamen (gefunden 2026-07-21 beim Aufsetzen
# der übrigen 6 Container: `source` übersprang die betroffenen Zeilen lautlos,
# der Loop brach beim ersten ungültigen Namen komplett ab).
ENV_PASSWORT_SUFFIX = {
    "Schorschel": "SCHORSCHEL",
    "F3INSCHM3CK3R": "F3INSCHMECKER",
    "träumerlie": "TRAEUMERLIE",
    "R1ZZ1": "R1ZZ1",
    "jumpa": "JUMPA",
    "Resonanzknoten": "RESONANZKNOTEN",
    "dak+gord-system": "DAKGORDSYSTEM",
}


def _container_name(entity_id: str) -> str:
    return CONTAINER_NAMES[entity_id]


def vault_pfad(entity_id: str) -> Path:
    return VAULT_ROOT / entity_id


# 2026-07-27: obsidian_schreiben:<dateiname> kommt ungeprueft aus LLM-generiertem
# Text (browser_agent.py). Beim Selbstbezug (Wesen schreibt ueber sich selbst
# oder ueber ein anderes Wesen unter codewesen/<name>/...) driftet der vom LLM
# erzeugte Name leicht -- gefunden bei Resonanzknoten: 23 fast-gleiche Ordner in
# 5 Tagen (Resonanzkothen, Resonatzknoten, Resonanz-knoten, ...), weil nie gegen
# die echten Entity-Namen abgeglichen wurde. Cutoff 0.72 empirisch gegen alle 23
# gefundenen Varianten UND gegen echte Vault-Ordnernamen (gedanken, ideen,
# codewesen, wesen, spiegel, entitaet/entitaeten) geprueft -- trifft nur echte
# Namens-Tippfehler, keine falschen Positiven bei generischen Ordnernamen.
_NAME_MATCH_CUTOFF = 0.72
_ENTITY_NAMEN = tuple(CONTAINER_NAMES.keys())
_ENTITY_NAMEN_KLEIN = {name.lower(): name for name in _ENTITY_NAMEN}


def _kanonischer_segmentname(segment: str) -> str:
    """Korrigiert ein einzelnes Pfad-Segment auf den echten Entity-Namen, wenn es
    diesem sehr aehnlich ist aber nicht exakt entspricht. Segmente ohne aehnlichen
    Entity-Namen (z.B. 'gedanken', 'spiegel') bleiben unveraendert.

    Vergleicht sowohl das rohe Segment als auch dessen URL-dekodierte Form --
    gefunden bei traeumerlie (Umlaut): manche obsidian_schreiben-Aufrufe kamen als
    percent-encodete Bytes an ('tr%C3%A4umerlie' statt 'träumerlie'), was die reine
    Tippfehler-Aehnlichkeit unter den Cutoff drueckte. Bei Nicht-Treffer wird das
    UNveraenderte Original zurueckgegeben, nie die dekodierte Form -- Dekodierung
    dient nur dem Vergleich, nicht der Ausgabe."""
    kandidaten = {segment.lower(), unquote(segment).lower()}
    for kandidat in kandidaten:
        treffer = difflib.get_close_matches(
            kandidat, _ENTITY_NAMEN_KLEIN.keys(), n=1, cutoff=_NAME_MATCH_CUTOFF
        )
        if treffer:
            korrigiert = _ENTITY_NAMEN_KLEIN[treffer[0]]
            if korrigiert != segment:
                log.info("Namens-Drift korrigiert: %r -> %r", segment, korrigiert)
            return korrigiert
    return segment


def normalisiere_dateiname(dateiname: str) -> str:
    """Wendet _kanonischer_segmentname auf jedes '/'-Segment eines Vault-Dateinamens
    an, damit Selbstbezuege wie 'codewesen/Resonanzkothen/wesen' immer auf
    'codewesen/Resonanzknoten/wesen' zusammenlaufen statt neue Tippfehler-Ordner
    zu erzeugen."""
    return "/".join(_kanonischer_segmentname(teil) for teil in dateiname.split("/"))


def schreibe_leere_datei(entity_id: str, dateiname: str, titel: str | None = None) -> Path:
    """Legt eine neue Datei direkt auf der Platte an (NIE über Ctrl+N in Obsidian
    selbst -- siehe Moduldoku, das bindet den Editor-Puffer nie an eine echte Datei)."""
    dateiname = normalisiere_dateiname(dateiname)
    if not dateiname.endswith(".md"):
        dateiname += ".md"
    ziel = vault_pfad(entity_id) / dateiname
    ziel.parent.mkdir(parents=True, exist_ok=True)
    inhalt = f"{titel}\n\n" if titel else ""
    ziel.write_text(inhalt, encoding="utf-8")
    return ziel


def _xdotool(entity_id: str, *args: str, timeout: int = 30) -> subprocess.CompletedProcess:
    container = _container_name(entity_id)
    cmd = ["docker", "exec", container, "bash", "-c",
           "export DISPLAY=:1; xdotool " + " ".join(args)]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def tippe_text(entity_id: str, text: str, delay_ms: int = 65) -> None:
    """Tippt text zeichenweise in das aktuell fokussierte Element des Wesen-eigenen
    Obsidian-Fensters -- via xdotool, nicht Playwright (siehe Moduldoku)."""
    escaped = text.replace("\\", "\\\\").replace('"', '\\"')
    r = _xdotool(entity_id, "type", "--delay", str(delay_ms), f'"{escaped}"',
                 timeout=max(30, len(text) * delay_ms // 1000 + 15))
    if r.returncode != 0:
        log.warning("%s: xdotool type Fehler: %s", entity_id, r.stderr)


def liste_ordner(entity_id: str, pfad: str = "") -> list[dict]:
    """Schneller, rein mechanischer Ordnerinhalt -- KEIN Playwright/xdotool. Grund:
    die Obsidian-Fenster laufen über Selkies-WebRTC-Streaming (bestätigt 2026-08-13,
    Diagnose gegen Schorschels echten Container: nur <canvas>/<video>, kein einziges
    Obsidian-eigenes DOM-Element) -- ein sichtbares Durchstöbern ließe sich technisch
    nicht auslesen, nur die Datei-öffnen-und-lesen-Aktion kann sich auf 'danach ist
    exakt diese eine Datei sichtbar offen' verlassen. Für das freie Erkunden bleibt
    nur der direkte, schnelle Weg von der Platte."""
    pfad = normalisiere_dateiname(pfad.strip().lstrip("/")) if pfad.strip() else ""
    basis = vault_pfad(entity_id).resolve()
    ziel = (basis / pfad).resolve()
    ziel.relative_to(basis)  # wirft ValueError bei Pfad-Ausbruchsversuch
    if not ziel.is_dir():
        raise NotADirectoryError(f"{pfad!r} ist kein Ordner in {entity_id}s Vault")
    eintraege = []
    for kind in sorted(ziel.iterdir(), key=lambda p: (p.is_file(), p.name.lower())):
        if kind.name.startswith("."):
            continue
        eintraege.append({
            "name": kind.name,
            "typ": "ordner" if kind.is_dir() else "datei",
            "groesse": kind.stat().st_size if kind.is_file() else None,
            "geaendert": kind.stat().st_mtime if kind.is_file() else None,
        })
    return eintraege


def oeffne_datei_und_lese(entity_id: str, dateiname: str) -> str:
    """Liest eine Datei direkt von der Platte. Hiess mal 'oeffne_datei_und_lese' weil
    Phase 1 (siehe Moduldoku oben) vorher sichtbar per Quick-Switcher durch Selkies
    navigierte -- Name bewusst beibehalten, damit browser_agent.py nicht angefasst
    werden muss (gleiche Signatur, gleiches Verhalten nach aussen, nur ohne Browser
    innen drin)."""
    dateiname = normalisiere_dateiname(dateiname)
    ziel = vault_pfad(entity_id) / (dateiname if dateiname.endswith(".md") else dateiname + ".md")
    if not ziel.is_file():
        raise FileNotFoundError(f"{dateiname!r} existiert nicht in {entity_id}s Vault")
    return ziel.read_text(encoding="utf-8", errors="replace")


def _sicherer_vault_pfad(entity_id: str, pfad: str) -> Path:
    """Löst pfad gegen den Vault des Wesens auf, wirft ValueError bei Ausbruchsversuch."""
    basis = vault_pfad(entity_id).resolve()
    ziel = (basis / normalisiere_dateiname(pfad.strip().lstrip("/"))).resolve()
    ziel.relative_to(basis)
    return ziel


def umbenennen(entity_id: str, alter_pfad: str, neuer_name: str) -> Path:
    """Benennt eine Datei innerhalb des eigenen Vaults um -- reine Plattenoperation,
    kein Playwright/xdotool (dieselbe Begründung wie liste_ordner: am sichtbaren
    Fenster ließe sich der Erfolg ohnehin nicht ablesen, die Platte ist die einzige
    verlässliche Quelle -- wie schon beim Schreiben selbst)."""
    quelle = _sicherer_vault_pfad(entity_id, alter_pfad)
    if not quelle.is_file():
        raise FileNotFoundError(f"{alter_pfad!r} existiert nicht in {entity_id}s Vault")
    neuer_name = neuer_name.strip().lstrip("/")
    if not neuer_name.endswith(".md"):
        neuer_name += ".md"
    if "/" in neuer_name:
        raise ValueError("neuer_name darf keinen Ordner enthalten -- dafür verschieben() nutzen")
    ziel = quelle.parent / neuer_name
    if ziel.exists():
        raise FileExistsError(f"{neuer_name!r} existiert in diesem Ordner bereits")
    quelle.rename(ziel)
    _vault_event_schreiben("vault.umbenannt", entity_id,
                            str(ziel.relative_to(vault_pfad(entity_id))),
                            alter_pfad=alter_pfad)
    return ziel


def verschieben(entity_id: str, quell_pfad: str, ziel_ordner: str) -> Path:
    """Verschiebt eine Datei innerhalb des eigenen Vaults in einen anderen Ordner
    (legt den Zielordner bei Bedarf an). Reine Plattenoperation, siehe umbenennen()."""
    quelle = _sicherer_vault_pfad(entity_id, quell_pfad)
    if not quelle.is_file():
        raise FileNotFoundError(f"{quell_pfad!r} existiert nicht in {entity_id}s Vault")
    ziel_verzeichnis = _sicherer_vault_pfad(entity_id, ziel_ordner)
    ziel_verzeichnis.mkdir(parents=True, exist_ok=True)
    ziel = ziel_verzeichnis / quelle.name
    if ziel.exists():
        raise FileExistsError(f"{quelle.name!r} existiert im Zielordner bereits")
    quelle.rename(ziel)
    _vault_event_schreiben("vault.verschoben", entity_id,
                            str(ziel.relative_to(vault_pfad(entity_id))),
                            quell_pfad=quell_pfad)
    return ziel


def loeschen(entity_id: str, pfad: str) -> Path:
    """'Löschen' verschiebt in einen wesen-eigenen _papierkorb/-Ordner, kein echtes
    unlink() -- konsistent mit dem Rest des Systems (Grundgesetz 4: nichts wird
    gelöscht, nur unsichtbar gemacht). Datei landet mit Zeitstempel-Präfix im
    Papierkorb, damit Namenskollisionen bei wiederholtem Löschen nicht crashen."""
    quelle = _sicherer_vault_pfad(entity_id, pfad)
    if not quelle.is_file():
        raise FileNotFoundError(f"{pfad!r} existiert nicht in {entity_id}s Vault")
    papierkorb = vault_pfad(entity_id) / "_papierkorb"
    papierkorb.mkdir(parents=True, exist_ok=True)
    zeitstempel = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    ziel = papierkorb / f"{zeitstempel}_{quelle.name}"
    quelle.rename(ziel)
    _vault_event_schreiben("vault.geloescht", entity_id, pfad)
    return ziel


def schreibe_datei_mechanisch(entity_id: str, pfad: str, inhalt: str) -> Path:
    """Schreibt inhalt komplett (ueberschreibt, kein Anhaengen) in eine Datei im Vault
    des Wesens -- legt fehlende Elternordner an, legt die Datei an falls sie noch nicht
    existiert. Reine Plattenoperation, wirft ein Vault-Event fuer die Live-Ansicht.
    Gemeinsame Grundlage fuer oeffne_datei_und_schreibe() (Wesen schreibt) UND
    wesenvaultsystem_api.py (Daniel editiert im Browser) -- ein Schreibweg, keine
    zwei parallelen Implementierungen die auseinanderdriften koennten."""
    ziel = _sicherer_vault_pfad(entity_id, pfad)
    if not ziel.name.endswith(".md"):
        ziel = ziel.with_name(ziel.name + ".md")
    neu = not ziel.exists()
    ziel.parent.mkdir(parents=True, exist_ok=True)
    ziel.write_text(inhalt, encoding="utf-8")
    rel_pfad = str(ziel.relative_to(vault_pfad(entity_id)))
    _vault_event_schreiben("vault.erstellt" if neu else "vault.geschrieben", entity_id, rel_pfad)
    return ziel


def lese_datei_info(entity_id: str, pfad: str) -> dict:
    """Wie oeffne_datei_und_lese(), aber inklusive mtime -- fuer wesenvaultsystem_api.py,
    damit das Frontend erkennen kann ob eine gerade geoeffnete Datei sich seit dem
    letzten Laden veraendert hat (z.B. weil das Wesen inzwischen selbst reingeschrieben
    hat), ohne bei jedem Tastendruck den ganzen Inhalt neu zu vergleichen."""
    ziel = _sicherer_vault_pfad(entity_id, pfad)
    if not ziel.is_file():
        raise FileNotFoundError(f"{pfad!r} existiert nicht in {entity_id}s Vault")
    stat = ziel.stat()
    return {
        "pfad": str(ziel.relative_to(vault_pfad(entity_id))),
        "inhalt": ziel.read_text(encoding="utf-8", errors="replace"),
        "geaendert": stat.st_mtime,
        "groesse": stat.st_size,
    }


def baum(entity_id: str, pfad: str = "") -> list[dict]:
    """Rekursiver Vault-Baum (Ordner + Dateien, verschachtelt) fuer die Seitenleiste
    der neuen DOM-Ansicht. Baut auf liste_ordner() auf -- gleiche Pfadsicherheit,
    keine doppelte Implementierung."""
    eintraege = liste_ordner(entity_id, pfad)
    for e in eintraege:
        if e["typ"] == "ordner":
            unterpfad = f"{pfad}/{e['name']}" if pfad else e["name"]
            e["kinder"] = baum(entity_id, unterpfad)
    return eintraege


def neuer_ordner(entity_id: str, pfad: str) -> Path:
    """Legt einen leeren Ordner im Vault des Wesens an (fuer Daniels manuelles
    Organisieren im DOM -- die Wesen selbst legen Ordner weiterhin implizit ueber
    verschieben()/schreibe_datei_mechanisch() an, nicht ueber diese Funktion)."""
    ziel = _sicherer_vault_pfad(entity_id, pfad)
    ziel.mkdir(parents=True, exist_ok=True)
    return ziel


def oeffne_datei_und_schreibe(entity_id: str, dateiname: str, text: str,
                                titel: str | None = None, delay_ms: int = 65) -> Path:
    """Haengt text ans Ende einer Datei an (legt sie mit titel an falls sie noch nicht
    existiert). Hiess mal 'oeffne_datei_und_schreibe' weil Phase 1 (siehe Moduldoku
    oben) das wirklich zeichenweise ins sichtbare Obsidian-Fenster tippte -- Name und
    Signatur bewusst beibehalten (auch delay_ms, jetzt ungenutzt), damit browser_agent.py
    diese Funktion weiter genau so aufrufen kann wie vorher. Das sichtbare 'Tippen' lebt
    jetzt in wesenvaultsystem_api.py (Live-DOM-Update via vault.geschrieben-Event), nicht
    mehr hier drin."""
    dateiname = normalisiere_dateiname(dateiname)
    ziel = vault_pfad(entity_id) / (dateiname if dateiname.endswith(".md") else dateiname + ".md")
    bisheriger_inhalt = ziel.read_text(encoding="utf-8", errors="replace") if ziel.exists() else (
        f"{titel}\n\n" if titel else "")
    neuer_inhalt = bisheriger_inhalt + text
    rel_pfad = str(ziel.relative_to(vault_pfad(entity_id)))
    return schreibe_datei_mechanisch(entity_id, rel_pfad, neuer_inhalt)


def _historisch_unbenutzt_oeffne_datei_und_schreibe(entity_id, dateiname, text, titel=None, delay_ms=65):
    """ERSETZT seit 2026-08-14 -- siehe oeffne_datei_und_schreibe() oben. Nur als
    Referenz stehen gelassen falls das Playwright/xdotool/Selkies-Verfahren jemals
    wieder gebraucht wird (z.B. falls die 7 Docker-Container komplett verschwinden
    sollen und jemand nochmal nachlesen will WARUM es damals so kompliziert war).
    NICHT AUFRUFEN -- die Container-Variablen (VAULT_PORTS, CONTAINER_USERS,
    ENV_PASSWORT_SUFFIX) existieren zwar noch, aber diese Funktion wird von nichts
    im System mehr referenziert."""
    from playwright.sync_api import sync_playwright

    dateiname = normalisiere_dateiname(dateiname)
    ziel = vault_pfad(entity_id) / (dateiname if dateiname.endswith(".md") else dateiname + ".md")
    if not ziel.exists():
        schreibe_leere_datei(entity_id, dateiname, titel)

    port, _ = VAULT_PORTS[entity_id]
    env_key = f"WESEN_VAULT_OBSIDIAN_PASSWORD_{ENV_PASSWORT_SUFFIX[entity_id]}"
    passwort = os.environ.get(env_key, "")
    if not passwort:
        raise RuntimeError(f"Kein Obsidian-Vault-Passwort für {entity_id} gesetzt ({env_key})")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            viewport={"width": 1280, "height": 800},
            http_credentials={"username": CONTAINER_USERS[entity_id], "password": passwort},
        )
        page.goto(f"http://localhost:{port}/", wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(5000)
        page.keyboard.press("Control+o")
        page.wait_for_timeout(600)
        page.keyboard.type(dateiname.removesuffix(".md"), delay=40)
        page.wait_for_timeout(600)
        page.keyboard.press("Enter")
        page.wait_for_timeout(1000)
        page.keyboard.press("Control+End")
        page.wait_for_timeout(300)
        # xdotool-Tipplauf laeuft WAEHREND die Playwright-Verbindung noch offen ist --
        # ein browser.close() unmittelbar davor reisst den Tipplauf mittendrin ab
        # (gefunden 2026-07-21: Text brach nach ca. der Haelfte lautlos ab, xdotool
        # selbst meldete trotzdem Erfolg -- die Unterbrechung passiert auf der
        # Empfaengerseite, nicht bei xdotool).
        tippe_text(entity_id, text, delay_ms=delay_ms)
        page.wait_for_timeout(500)
        browser.close()

    return ziel
