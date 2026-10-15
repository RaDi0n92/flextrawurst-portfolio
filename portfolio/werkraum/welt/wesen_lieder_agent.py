#!/usr/bin/env python3
"""
Wesen-Lieder-Agent -- eigener Obsidian-Vault fuer Ideen, Schnipsel und Lieder der Wesen,
dazu das Freigeben ins Forum und das direkte Antworten unter Lieder-Posts.

Entstanden 2026-10-02 auf Daniels Auftrag (Einladung: wesen_lieder/impuls_lieder.md,
Ticket: wesen_lieder/ticket_auswahl.md). Bewusst KEINE Wiederbelebung der alten Dienste
(codewesen_forum_neugier, engagement, reaktion ...) -- die haetten anderes Posten mit
freigeschaltet. Nachgebaut sind nur die brauchbaren Muster:
  - Vault-Operationen eigenstaendig kopiert wie in wesen_einzug_vault_agent.py (keine
    Events in die geteilte Tabelle, Pfad-Ausbruchschutz, nichts wird geloescht)
  - Posten ueber flarum_poster.schreibe_draft()/poster() (Draft, globaler Lock, Retry,
    Archiv) -- das ist der einzige Forum-Touchpoint.

Was dieses Modul NICHT tut: es hebt die globale Flarum-Post-Sperre nicht auf. Gepostet wird
nur (a) ein von einem Wesen freigegebener Entwurf aus seinem Lieder-Vault, in einen Lieder-
Thread, oder (b) eine direkte Antwort unter einem Lieder-Thread. Ein "Lieder-Thread" ist
eine Diskussion, die in der Ausnahmeliste (flarum_post_sperre) mit dem Grund-Praefix
"Lieder-Thread" steht -- Threads entstehen nur hier, durch die Freigabe eines Wesens. Alles
andere im Forum bleibt zu.

Ordner pro Wesen:  ideen/  schnipsel/  lieder/
Dateikopf (Frontmatter): art, status (entwurf|gepostet), titel, erstellt, ...
Zaehler pro Wesen und Tag: ganze Lieder (hoechstens MAX_LIEDER_PRO_TAG) und Schnipsel (keine
Grenze, zaehlen nur zur Anzeige).

Pflichtfrage (2026-10-02, einmalig): wann hoert dieser Code auf zu laufen, wann heilt/belebt er sich?

Aufhoeren: Dieses Modul hat keinen eigenen Prozess und keinen Thread -- es sind nur Funktionen, die
die Browser-Agent-Prozesse aufrufen. Es laeuft genau so lange wie der aufrufende Agent und nur, wenn der
Agent es aufruft (der Schalter dafuer liegt im Aufrufer, nicht hier). Wird der Agent gestoppt oder ruft
er nichts mehr auf, passiert hier nichts mehr; Dateien und Zaehler bleiben liegen.

Heilen: fuehre_aus() faengt jede Ausnahme und gibt sie dem Wesen als Text zurueck -- ein Fehler hier
beendet nie den Wesen-Loop. Der Datei-Lock (_sperre) wird im finally freigegeben und vom Kernel auch bei
einem Prozess-Tod; eine fehlende oder kaputte _zaehler.json wird als leer gelesen. Scheitert das Senden
ans Forum, geht die Datei von "sendet" zurueck auf "entwurf" und kann erneut freigegeben werden. Stirbt
der Prozess mitten im Senden, bleibt sie auf "sendet" -- das verhindert ein Doppelposten, die Datei
muss dann ein Mensch oder ein Wesen per neuer Datei fortsetzen.

Beleben: Von selbst belebt sich hier nichts. Die Tageszaehler fangen nur beim Datumswechsel neu an, und
die Rueckschau-Folge (_FOLGE) liegt nur im Speicher -- ein Neustart des Agents verwirft sie.
"""

from __future__ import annotations

import fcntl
import itertools
import json
import os
import re
import sys
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

VAULT_ROOT = Path(os.environ.get("LIEDER_VAULT_ROOT", "/root/werkraum/lieder_vault"))
TEXT_ROOT = Path(os.environ.get("LIEDER_TEXT_ROOT", "/root/werkraum/wesen_lieder"))
EINLADUNG_DATEI = TEXT_ROOT / "impuls_lieder.md"
TICKET_DATEI = TEXT_ROOT / "ticket_auswahl.md"
TICKET_NACH_RUECKSCHAU_DATEI = TEXT_ROOT / "ticket_nach_rueckschau.md"
TICK_NACHHOLEN_DATEI = TEXT_ROOT / "tick_nachholen.md"
TICKET_KOPF_WAEHLEN_DATEI = TEXT_ROOT / "ticket_kopf_waehlen.md"
TICKET_KOPF_WEITER_DATEI = TEXT_ROOT / "ticket_kopf_weiter.md"

WESEN = (
    "Schorschel",
    "F3INSCHM3CK3R",
    "träumerlie",
    "R1ZZ1",
    "jumpa",
    "Resonanzknoten",
    "dak+gord-system",
)

UNTERORDNER = ("ideen", "schnipsel", "lieder")
POSTBAR = ("schnipsel", "lieder")

# Daniel, 2026-10-02: "maximal aber nur drei gesamte Lieder pro Tag"; Schnipsel ohne Grenze.
MAX_LIEDER_PRO_TAG = 3
# Daniel, 2026-10-02: Rueckschau "4444 tokens etwa". Gemessen wird grob: ein deutsches Wort
# braucht beim hier genutzten Modell etwa 3 Zeichen pro Token -- bewusst vorsichtig geschaetzt.
RUECKSCHAU_TOKENS = 4444
ZEICHEN_PRO_TOKEN = 3
# Flarum-Tag fuer neue Lieder-Threads: 5 = "Showcase / Projekte" (Daniel 2026-10-03: passt, soll bleiben).
# Der Tag war in der Live-DB is_hidden=1 (Threads darin tauchten nicht auf) -- Daniel liess ihn am
# 2026-10-03 auf sichtbar stellen. Der erst gedachte Tag 27 existiert dort nicht mehr.
LIEDER_TAG_IDS = [5]
THREAD_GRUND_PRAEFIX = "Lieder-Thread"

STATE_DATEI = VAULT_ROOT / "_zaehler.json"
LOCK_DATEI = Path("/tmp/lieder_agent.lock")

# Nur zum Testen: True = nichts wird ans Forum gesendet, es kommen erfundene IDs zurueck.
POSTEN_TROCKEN = os.environ.get("LIEDER_POSTEN_TROCKEN", "") == "1"

_FOLGE: dict[str, str] = {}
_TROCKEN_IDS = itertools.count(900001)  # nur fuer LIEDER_POSTEN_TROCKEN


# ---------------------------------------------------------------- Grundlagen

def _pruefe_wesen(wesen: str) -> None:
    if wesen not in WESEN:
        raise ValueError(f"Unbekanntes Wesen: {wesen!r}")


def vault_pfad(wesen: str) -> Path:
    _pruefe_wesen(wesen)
    return VAULT_ROOT / wesen


def _jetzt() -> str:
    # Echte Systemzeit, nie vom Wesen erfunden (siehe wesen_einzug_vault_agent).
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def _heute() -> str:
    return datetime.now().strftime("%Y-%m-%d")


@contextmanager
def _sperre():
    LOCK_DATEI.parent.mkdir(parents=True, exist_ok=True)
    with open(LOCK_DATEI, "w") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def _normalisiere(pfad: str) -> tuple[str, str]:
    """'schnipsel/mein_vers' -> ('schnipsel', 'mein_vers.md'). Ohne Ordner: ideen.
    Wirft ValueError bei Ausbruchsversuch, unbekanntem Ordner oder leerem Namen."""
    pfad = (pfad or "").strip().strip("/")
    teile = [t for t in pfad.split("/") if t]
    if not teile:
        raise ValueError("Kein Dateiname angegeben")
    if len(teile) == 1:
        ordner, name = "ideen", teile[0]
    elif len(teile) == 2:
        ordner, name = teile
    else:
        raise ValueError("Nur ein Ordner tief: ideen/, schnipsel/ oder lieder/")
    if ordner not in UNTERORDNER:
        raise ValueError(f"Unbekannter Ordner {ordner!r} -- erlaubt: {', '.join(UNTERORDNER)}")
    if name.startswith(".") or name.startswith("_") or ".." in name:
        raise ValueError("Ungueltiger Dateiname")
    name = re.sub(r"[\\:*?\"<>|\n\r\t]", "_", name)[:120].strip()
    if not name:
        raise ValueError("Leerer Dateiname")
    if not name.lower().endswith(".md"):
        name += ".md"
    return ordner, name


def _datei(wesen: str, pfad: str) -> Path:
    ordner, name = _normalisiere(pfad)
    basis = vault_pfad(wesen).resolve()
    ziel = (basis / ordner / name).resolve()
    ziel.relative_to(basis)
    return ziel


def _finde_bestehende(wesen: str, pfad: str) -> Path:
    """Findet eine BESTEHENDE Datei, auch wenn das Wesen den Namen kuerzt (im echten Lauf rief ein
    Wesen zweimal `schnipsel/frequenz` fuer `frequenz_des_werdens`): erst exakt, dann ein eindeutiger
    Namensanfang, dann ein eindeutiger Namensteil -- zuerst im genannten Ordner, danach in allen.
    Mehrdeutig oder nichts: FileNotFoundError (fuehre_aus haengt dann die vorhandenen Dateien an).
    Nur zum Lesen/Freigeben/Zusammenfuegen -- schreibe() legt weiter nur den exakten Namen an."""
    ordner, name = _normalisiere(pfad)
    basis = vault_pfad(wesen).resolve()
    exakt = (basis / ordner / name).resolve()
    exakt.relative_to(basis)
    if exakt.is_file():
        return exakt
    stamm = exakt.stem.lower()

    def treffer(ordnernamen, vergleich):
        gefunden = []
        for o in ordnernamen:
            d = basis / o
            if d.is_dir():
                gefunden += [p for p in d.glob("*.md") if vergleich(p.stem.lower())]
        return gefunden

    for ordnernamen in ([ordner], list(UNTERORDNER)):
        for vergleich in (lambda s: s == stamm, lambda s: s.startswith(stamm), lambda s: stamm in s):
            t = treffer(ordnernamen, vergleich)
            if len(t) == 1:
                return t[0].resolve()
            if len(t) > 1:
                namen = ", ".join(f"{p.parent.name}/{p.stem}" for p in t[:6])
                raise FileNotFoundError(f"{pfad!r} ist nicht eindeutig (passt auf: {namen}) -- "
                                        f"nimm den vollen Namen")
    raise FileNotFoundError(f"{pfad!r} gibt es in deinem Lieder-Vault nicht")


def _rel(wesen: str, p: Path) -> str:
    return str(p.relative_to(vault_pfad(wesen).resolve()))[:-3]  # ohne .md


# ------------------------------------------------------------- Frontmatter

def _fm_parse(text: str) -> tuple[dict, str]:
    if text.startswith("---\n"):
        ende = text.find("\n---\n", 4)
        if ende != -1:
            kopf = text[4:ende]
            meta = {}
            for zeile in kopf.split("\n"):
                if ":" in zeile:
                    k, v = zeile.split(":", 1)
                    meta[k.strip()] = v.strip()
            return meta, text[ende + 5:]
    return {}, text


def _fm_schreibe(meta: dict, body: str) -> str:
    kopf = "\n".join(f"{k}: {v}" for k, v in meta.items())
    return f"---\n{kopf}\n---\n{body}"


def _lies_datei(p: Path) -> tuple[dict, str]:
    return _fm_parse(p.read_text(encoding="utf-8", errors="replace"))


# -------------------------------------------------------------- Zaehler

def _state_lesen() -> dict:
    try:
        return json.loads(STATE_DATEI.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _state_schreiben(state: dict) -> None:
    STATE_DATEI.parent.mkdir(parents=True, exist_ok=True)
    STATE_DATEI.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")


def tages_status(wesen: str) -> dict:
    _pruefe_wesen(wesen)
    eintrag = _state_lesen().get(wesen, {})
    if eintrag.get("datum") != _heute():
        eintrag = {"datum": _heute(), "lieder": 0, "schnipsel": 0,
                   "zuletzt": eintrag.get("zuletzt", "")}
    eintrag.setdefault("lieder", 0)
    eintrag.setdefault("schnipsel", 0)
    return eintrag


def _vermerke(wesen: str, lieder: int = 0, schnipsel: int = 0, zuletzt: str | None = None) -> None:
    with _sperre():
        state = _state_lesen()
        e = tages_status(wesen)
        e["lieder"] += lieder
        e["schnipsel"] += schnipsel
        if zuletzt:
            e["zuletzt"] = zuletzt
        state[wesen] = e
        _state_schreiben(state)


def _merke_zuletzt(wesen: str, text: str) -> None:
    _vermerke(wesen, zuletzt=text)


# ------------------------------------------------------ Vault-Operationen

_AKTIONSZEILE = re.compile(r"^[ \t]*(lied_[a-z_]+|ENTSCHEIDUNG|BEGR(Ü|UE)NDUNG)[ \t]*:.*$", re.MULTILINE)


# Beginn des Antwortformats (GEDANKE:/ENTSCHEIDUNG:/BEGRUENDUNG:, auch mit Tippfehlern wie
# 'ENTSCCHIEIDUNG'): der TEXT:-Block laeuft bis zum Ende der Antwort, schreibt ein Wesen das Format
# DANACH, landet es sonst im Text. Ab der ersten solchen Zeile wird abgeschnitten.
_FORMATZEILE = re.compile(r"^[ \t]*(GEDANKE|ENTSC[A-Z]*|BEGR[A-ZÜ]*)[ \t]*:", re.MULTILINE)


def _ohne_aktionszeilen(text: str) -> str:
    """Entfernt, was nicht in den Text gehoert: alles ab einer Antwortformat-Zeile (`GEDANKE:`,
    `ENTSCHEIDUNG:`, `BEGRUENDUNG:`) und einzelne Aktionszeilen (`lied_freigeben:...`). Im echten Lauf
    2026-10-02 hat ein Wesen die naechste Aktion ans Ende seines Schnipsels geschrieben, ein anderes das
    ganze Antwortformat hinter den TEXT-Block. Wird beim Schreiben UND beim Posten angewandt."""
    m = _FORMATZEILE.search(text)
    if m:
        text = text[:m.start()]
    return _AKTIONSZEILE.sub("", text).rstrip() + ("\n" if text.endswith("\n") else "")


def _echte_umbrueche(text: str) -> str:
    """Eine einzelne Zeile mit woertlichem '\\n' (so schreiben die Wesen Mehrzeiliges in die
    ENTSCHEIDUNG-Zeile -- im echten Tick 2026-10-02 gemessen) wird zu echten Zeilenumbruechen.
    Text, der schon echte Umbrueche hat (TEXT:-Block), bleibt unveraendert."""
    if "\n" not in text and "\\n" in text:
        return text.replace("\\r\\n", "\n").replace("\\n", "\n")
    return text


def _pruefe_kein_etikett(text: str) -> None:
    """Hinter dem | soll der Text stehen, nicht noch einmal ein Dateiname (kam im Einzugvault bei
    jedem sechsten Schreibvorgang vor). Wird abgelehnt und dem Wesen gesagt, statt eine Datei
    mit nur einem Dateinamen anzulegen."""
    if "\n" not in text and len(text) <= 120 and text.lower().endswith(".md"):
        raise ValueError("Hinter dem | steht nur ein Dateiname -- schreib dort deinen eigentlichen "
                         "Text (oder nutze einen TEXT:-Block), dann klappt es")


_EINDRUCK_MARKE = "**Eindruck:**"
_EINDRUCK_ZEILE = re.compile(r"^[ \t]*(?:\*\*)?EINDRUCK(?:\*\*)?[ \t]*:(?:\*\*)?[ \t]*", re.MULTILINE | re.IGNORECASE)


def _trenne_eindruck(text: str) -> tuple[str, str]:
    """Teilt einen Text an der ersten Zeile 'EINDRUCK:' in (Haupttext, Eindruck). Ohne solche Zeile
    ist der Eindruck leer."""
    m = _EINDRUCK_ZEILE.search(text)
    if not m:
        return text, ""
    return text[:m.start()].rstrip(), text[m.end():].strip()


def _hat_eindruck(body: str) -> bool:
    return _EINDRUCK_MARKE in body


def schreibe(wesen: str, pfad: str, text: str) -> str:
    """Haengt text an (legt Datei mit Kopf an). Jeder Eintrag bekommt einen unsichtbaren
    Zeitstempel-Kommentar mit der echten Systemzeit."""
    haupt, eindruck = _trenne_eindruck((text or "").strip())
    haupt = _ohne_aktionszeilen(haupt).strip()
    eindruck = _ohne_aktionszeilen(eindruck).strip()
    if not haupt:
        raise ValueError("Kein Text")
    _pruefe_kein_etikett(haupt)
    text = haupt + (f"\n\n{_EINDRUCK_MARKE} {eindruck}" if eindruck else "")
    ziel = _datei(wesen, pfad)
    ordner = ziel.parent.name
    ziel.parent.mkdir(parents=True, exist_ok=True)
    if ziel.exists():
        meta, body = _lies_datei(ziel)
        if meta.get("status") in ("gepostet", "sendet"):
            raise ValueError("Diese Datei ist schon gepostet (oder wird gerade gesendet) -- leg "
                             "fuer eine Fortsetzung eine neue Datei an (z.B. mit dem Zusatz _2)")
    else:
        meta = {"art": {"ideen": "idee", "schnipsel": "schnipsel", "lieder": "lied"}[ordner],
                "status": "entwurf", "titel": ziel.stem, "erstellt": _jetzt()}
        body = ""
    body = body.rstrip("\n") + (f"\n\n<!-- {_jetzt()} -->\n{text}\n" if body.strip() else
                                 f"<!-- {_jetzt()} -->\n{text}\n")
    ziel.write_text(_fm_schreibe(meta, body), encoding="utf-8")
    label = {"ideen": "Ideen", "schnipsel": "Schnipsel", "lieder": "ganzes Lied"}[ordner]
    _merke_zuletzt(wesen, f"{label} ({_rel(wesen, ziel)})")
    return _rel(wesen, ziel)


def schreibe_eindruck(wesen: str, pfad: str, text: str) -> str:
    """Haengt an eine BESTEHENDE Datei einen Eindruck an. Ist sie noch ein Entwurf, steht er
    danach unter dem Text (und geht beim Freigeben mit). Ist sie schon gepostet, geht er als
    Antwort in ihren Lieder-Thread."""
    eindruck = _ohne_aktionszeilen(_trenne_eindruck(text or "")[1] or (text or "")).strip()
    eindruck = re.sub(r"^\*\*Eindruck:\*\*\s*", "", eindruck)
    if not eindruck:
        raise ValueError("Kein Eindruck-Text")
    _pruefe_kein_etikett(eindruck)
    datei = _finde_bestehende(wesen, pfad)
    meta, body = _lies_datei(datei)
    rel = _rel(wesen, datei)
    if meta.get("status") == "sendet":
        raise ValueError("Die Datei wird gerade gesendet -- gleich nochmal versuchen")
    if meta.get("status") == "gepostet":
        disk = meta.get("disk")
        if not str(disk).isdigit():
            raise ValueError("Die Datei ist gepostet, aber ohne bekannten Thread")
        antworten(wesen, int(disk), f"{_EINDRUCK_MARKE} {eindruck}")
        body = body.rstrip("\n") + f"\n\n<!-- {_jetzt()} -->\n{_EINDRUCK_MARKE} {eindruck}\n"
        datei.write_text(_fm_schreibe(meta, body), encoding="utf-8")
        return f"Eindruck zu {rel} als Antwort in d/{disk} gepostet"
    body = body.rstrip("\n") + f"\n\n<!-- {_jetzt()} -->\n{_EINDRUCK_MARKE} {eindruck}\n"
    datei.write_text(_fm_schreibe(meta, body), encoding="utf-8")
    return f"Eindruck zu {rel} gespeichert"


_EINDRUCK_ABSCHNITT = re.compile(r"^##[ \t]+(\S+)[ \t]*$", re.MULTILINE)


def _eindruck_bloecke(text: str) -> list[tuple[str, str]]:
    """Zerlegt einen Text mit Abschnitten '## <datei>' in [(datei, eindruck), ...]. Ohne solche
    Abschnittszeile: leer (dann gilt der Einzelfall mit dem Namen aus der Aktion)."""
    treffer = list(_EINDRUCK_ABSCHNITT.finditer(text))
    if not treffer:
        return []
    out = []
    for i, m in enumerate(treffer):
        ende = treffer[i + 1].start() if i + 1 < len(treffer) else len(text)
        out.append((m.group(1).strip(), text[m.end():ende].strip()))
    return out


def ohne_eindruck(wesen: str) -> list[str]:
    """Eigene Dateien (neueste zuerst), unter denen noch kein Eindruck steht."""
    basis = vault_pfad(wesen)
    treffer = []
    for o in UNTERORDNER:
        d = basis / o
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.md"), key=lambda q: q.stat().st_mtime, reverse=True):
            meta, body = _lies_datei(p)
            if body.strip() and not _hat_eindruck(body):
                treffer.append((p.stat().st_mtime, f"{o}/{p.stem}"))
    return [n for _, n in sorted(treffer, reverse=True)]


def lese(wesen: str, pfad: str, maximal: int = 6000) -> str:
    ziel = _finde_bestehende(wesen, pfad)
    meta, body = _lies_datei(ziel)
    kopf = f"[{_rel(wesen, ziel)} | {meta.get('art', '?')}, {meta.get('status', '?')}]"
    return kopf + "\n" + body.strip()[:maximal]


def dateiliste(wesen: str) -> str:
    """ALLE eigenen Dateien (neueste zuerst) mit Status, Eindruck-Vermerk und erster Zeile -- bewusst
    ohne Obergrenze (Daniel 2026-10-03: 'alles was schon erstellt wurde')."""
    basis = vault_pfad(wesen)
    zeilen = []
    for o in UNTERORDNER:
        d = basis / o
        if not d.is_dir():
            continue
        for p in d.glob("*.md"):
            meta, body = _lies_datei(p)
            sauber = re.sub(r"<!--.*?-->", "", body, flags=re.S)
            erste = next((z.strip() for z in sauber.splitlines() if z.strip() and not z.strip().startswith("**Eindruck")), "")
            status = meta.get("status", "?")
            if status == "gepostet" and str(meta.get("disk", "")).isdigit():
                status = f"gepostet in d/{meta['disk']}"
            eindruck = "mit Eindruck" if _hat_eindruck(body) else "noch ohne Eindruck"
            zeilen.append((p.stat().st_mtime,
                           f"- {o}/{p.stem} ({status}, {eindruck}, {len(body.strip())} Zeichen): \u201e{erste[:90]}\u201c"))
    if not zeilen:
        return "noch keine -- fang etwas Neues an"
    return "\n" + "\n".join(z for _, z in sorted(zeilen, reverse=True))


def erkunde(wesen: str, ordner: str = "") -> list[str]:
    ordner = (ordner or "").strip().strip("/")
    basis = vault_pfad(wesen)
    ordnernamen = [ordner] if ordner else list(UNTERORDNER)
    zeilen = []
    for o in ordnernamen:
        if o not in UNTERORDNER:
            raise ValueError(f"Unbekannter Ordner {o!r} -- erlaubt: {', '.join(UNTERORDNER)}")
        d = basis / o
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.md"), key=lambda q: q.stat().st_mtime, reverse=True):
            meta, body = _lies_datei(p)
            zeilen.append(f"{o}/{p.stem} ({meta.get('status', '?')}, {len(body.strip())} Zeichen)")
    return zeilen


def rueckschau(wesen: str, tokens: int = RUECKSCHAU_TOKENS) -> str:
    """Sammelt die halbfertigen (status entwurf) Dateien des Wesens, neueste zuerst, bis das
    Token-Budget erreicht ist -- zum Auf-einmal-Lesen im groesseren Zusammenhang."""
    budget = tokens * ZEICHEN_PRO_TOKEN
    basis = vault_pfad(wesen)
    dateien = []
    for o in UNTERORDNER:
        d = basis / o
        if d.is_dir():
            dateien.extend(d.glob("*.md"))
    dateien.sort(key=lambda q: q.stat().st_mtime, reverse=True)
    teile, verbraucht, dabei = [], 0, 0
    for p in dateien:
        meta, body = _lies_datei(p)
        if meta.get("status") == "gepostet":
            continue
        body = body.strip()
        if not body:
            continue
        kopf = f"### {p.parent.name}/{p.stem}  ({meta.get('art', '?')}, zuletzt {datetime.fromtimestamp(p.stat().st_mtime).strftime('%Y-%m-%d %H:%M')})\n"
        rest = budget - verbraucht - len(kopf)
        if rest < 200:
            break
        stueck = body if len(body) <= rest else body[:rest] + " [...]"
        teile.append(kopf + stueck)
        verbraucht += len(kopf) + len(stueck)
        dabei += 1
    if not teile:
        return ""
    return (f"DEINE HALBFERTIGEN SACHEN (neueste zuerst, {dabei} Datei(en), alles auf einmal "
            f"zum Gegenlesen):\n\n" + "\n\n".join(teile))


# Trennlinie in zusammengefuegten Dateien: darunter stehen die aus den Quellen abgetrennten
# Format-Absaetze (GEDANKE:/ENTSCHEIDUNG:/BEGRUENDUNG:). Alles ab dieser Zeile geht NIE ins Forum.
_ABGETRENNT_MARKE = "<!-- abgetrennt-ab-hier -->"


def _ohne_ablage(body: str) -> str:
    """Der Text vor der Trennlinie (ohne die abgetrennten Format-Absaetze darunter). Ein Eindruck, der
    erst nachtraeglich UNTER die Ablage geschrieben wurde, gehoert weiter dazu und bleibt erhalten."""
    haupt, _, ablage = body.partition(_ABGETRENNT_MARKE)
    i = ablage.find(_EINDRUCK_MARKE)
    return haupt if i < 0 else haupt.rstrip("\n") + "\n\n" + ablage[i:]


def _trenne_format_absaetze(text: str) -> tuple[str, list[str]]:
    """Trennt Absaetze, die mit einer Antwortformat-Zeile beginnen (GEDANKE:/ENTSCHEIDUNG:/BEGRUENDUNG:,
    auch mit Tippfehlern), vom Rest ab -- NUR den jeweiligen Absatz, nicht den Rest. Gibt (Text ohne
    diese Absaetze, [die abgetrennten Absaetze unveraendert]) zurueck. Fuer alte Dateien aus der Zeit
    vor dem Filter, deren Format-Reste mitten im Text stehen, damit beim Zusammenfuegen (und spaeteren
    Posten) nicht die zweite Haelfte hinter einem Rest abgeschnitten wird. Eine schon vorhandene
    Ablage unter der Trennlinie einer Quelle wandert ebenfalls in die abgetrennten Absaetze."""
    haupt, _, ablage = text.partition(_ABGETRENNT_MARKE)
    absaetze = re.split(r"\n[ \t]*\n", haupt)
    behalten, entfernt = [], []
    for a in absaetze:
        (entfernt if _FORMATZEILE.match(a.lstrip("\n")) else behalten).append(a.strip("\n"))
    entfernt += [a.strip("\n") for a in re.split(r"\n[ \t]*\n", ablage) if a.strip()]
    return "\n\n".join(behalten).strip(), [a for a in entfernt if a.strip()]


def zusammenfuegen(wesen: str, ziel_pfad: str, quellen: list[str]) -> str:
    """Fuegt mehrere Dateien zu einer neuen Lied-Datei zusammen. Die Quellen bleiben
    unveraendert liegen (nichts wird geloescht)."""
    quellen = [q.strip() for q in quellen if q.strip()]
    if len(quellen) < 2:
        raise ValueError("Zum Zusammenfuegen brauche ich mindestens zwei Quelldateien")
    stuecke, namen, abgetrennt = [], [], []
    for q in quellen:
        p = _finde_bestehende(wesen, q)
        meta, body = _lies_datei(p)
        ohne_kommentare = re.sub(r"<!--(?! abgetrennt-ab-hier).*?-->\n?", "", body).strip()
        sauber, entfernt = _trenne_format_absaetze(ohne_kommentare)
        stuecke.append(sauber)
        namen.append(_rel(wesen, p))
        if entfernt:
            abgetrennt.append(f"**Abgetrennt aus {_rel(wesen, p)}:**\n\n" + "\n\n".join(entfernt))
    ordner, name = _normalisiere(ziel_pfad)
    ziel = _datei(wesen, f"lieder/{Path(name).stem}")
    if ziel.exists():
        raise FileExistsError(f"{_rel(wesen, ziel)!r} gibt es schon -- waehle einen neuen Namen")
    ziel.parent.mkdir(parents=True, exist_ok=True)
    meta = {"art": "lied", "status": "entwurf", "titel": ziel.stem, "erstellt": _jetzt(),
            "aus": ", ".join(namen)}
    body = f"<!-- {_jetzt()} zusammengefuegt aus {', '.join(namen)} -->\n" + "\n\n".join(stuecke) + "\n"
    if abgetrennt:
        body += f"\n{_ABGETRENNT_MARKE}\n---\n\n" + "\n\n".join(abgetrennt) + "\n"
    ziel.write_text(_fm_schreibe(meta, body), encoding="utf-8")
    _merke_zuletzt(wesen, f"Zusammengefuegt ({_rel(wesen, ziel)})")
    return _rel(wesen, ziel)


def setze_folge(wesen: str, text: str) -> None:
    _FOLGE[wesen] = text


def hole_folge(wesen: str) -> str | None:
    return _FOLGE.pop(wesen, None)


# ---------------------------------------------------------- Forum: Threads

def lieder_threads() -> list[dict]:
    import flarum_post_sperre
    liste = []
    for did, info in flarum_post_sperre.ausnahme_liste().get("diskussionen", {}).items():
        if str(info.get("grund", "")).startswith(THREAD_GRUND_PRAEFIX):
            liste.append({"id": int(did), "grund": info.get("grund", ""),
                          "seit": info.get("seit", ""), "von": info.get("von", "")})
    liste.sort(key=lambda t: (t["seit"], t["id"]))
    return liste


def ist_lieder_thread(disk_id: int) -> bool:
    return any(t["id"] == int(disk_id) for t in lieder_threads())


def threads_zeile() -> str:
    t = lieder_threads()
    if not t:
        return "noch keiner -- der erste entsteht, wenn jemand etwas freigibt"
    return "; ".join(f"d/{x['id']} ({x['grund'].split(':', 1)[-1].strip()[:50]})" for x in t[-6:])


def forum_lesen(wesen: str, disk_id: int | None = None, tokens: int = RUECKSCHAU_TOKENS) -> str:
    if disk_id is None:
        t = lieder_threads()
        if not t:
            return "[Lieder-Forum]: noch keine Lieder-Threads"
        return "[Lieder-Threads]\n" + "\n".join(
            f"- lied_forum:{x['id']}  {x['grund'].split(':', 1)[-1].strip()[:70]} (eroeffnet von {x['von']})"
            for x in t)
    if not ist_lieder_thread(disk_id):
        raise PermissionError(f"d/{disk_id} ist kein Lieder-Thread")
    import flarum_api
    d = flarum_api.get_discussion(int(disk_id))
    budget = tokens * ZEICHEN_PRO_TOKEN
    posts = [(p["number"], p["username"], flarum_api._flarum_content_klartext(p["content"]))
             for p in d["posts"]]
    gewaehlt, verbraucht = [], 0
    for nr, user, text in reversed(posts):  # neueste zuerst einsammeln
        stueck = f"#{nr} {user}: {text}"
        if verbraucht + len(stueck) > budget and gewaehlt:
            break
        gewaehlt.append(stueck[:budget])
        verbraucht += len(stueck)
    gewaehlt.reverse()
    return f"[Lieder-Thread d/{disk_id}: {d['title']} -- {d['comment_count']} Posts]\n\n" + "\n\n".join(gewaehlt)


# ----------------------------------------------------------- Forum: Posten

def _poste(wesen: str, typ: str, inhalt: str, discussion_id: int | None = None,
           titel: str | None = None) -> int:
    """Einziger Forum-Touchpoint. Gibt die Diskussions-ID (neu) bzw. Post-ID (Antwort) zurueck."""
    if POSTEN_TROCKEN:
        return next(_TROCKEN_IDS)
    sys.path.insert(0, "/root/werkraum")
    import flarum_poster
    draft = flarum_poster.schreibe_draft(
        wesen, typ, inhalt, discussion_id=discussion_id, titel=titel,
        tag_ids=LIEDER_TAG_IDS if typ == "neu" else None, erlaubt_trotz_sperre=True)
    if draft is None:
        raise RuntimeError("Entwurf konnte nicht angelegt werden")
    ergebnis = flarum_poster.poster(draft, bypass_cooldown=True, erlaubt_trotz_sperre=True)
    if not ergebnis.get("ok"):
        raise RuntimeError(ergebnis.get("fehler", "unbekannter Fehler"))
    return int(ergebnis["result"]["data"]["id"])


def _post_inhalt(titel: str, body: str) -> str:
    body = _ohne_aktionszeilen(re.sub(r"<!--.*?-->\n?", "", _ohne_ablage(body))).strip()
    return f"### {titel}\n\n{body}" if titel else body


def freigeben(wesen: str, pfad: str, ziel: str | None = None) -> str:
    """Gibt einen Entwurf frei und postet ihn. ziel: leer = in den aeltesten Lieder-Thread
    (gibt es noch keinen, wird ein neuer eroeffnet), 'neu:<Titel>' = neuer Lieder-Thread,
    '<id>' = in diesen Lieder-Thread. Nur Dateien aus schnipsel/ und lieder/."""
    datei = _finde_bestehende(wesen, pfad)
    ordner = datei.parent.name
    if ordner not in POSTBAR:
        raise ValueError("Aus ideen/ wird nichts gepostet -- leg es als Schnipsel oder Lied an, "
                         "wenn es raus soll")
    meta, body = _lies_datei(datei)
    if meta.get("status") in ("gepostet", "sendet"):
        raise ValueError("Diese Datei ist schon gepostet (oder wird gerade gesendet)")
    if not re.sub(r"<!--.*?-->", "", body).strip():
        raise ValueError("Die Datei ist leer")
    ist_lied = ordner == "lieder"
    with _sperre():
        st = tages_status(wesen)
        if ist_lied and st["lieder"] >= MAX_LIEDER_PRO_TAG:
            raise ValueError(f"Heute schon {st['lieder']} von {MAX_LIEDER_PRO_TAG} ganzen Liedern "
                             f"veroeffentlicht -- morgen wieder. Schnipsel gehen weiter.")
        titel = (meta.get("titel") or datei.stem)[:120]
        ziel = (ziel or "").strip()
        threads = lieder_threads()
        if ziel.isdigit() and not ist_lieder_thread(int(ziel)):
            raise PermissionError(f"d/{ziel} ist kein Lieder-Thread -- nur dort darfst du posten")
        # Zwischenstatus VOR dem Senden: stirbt der Prozess nach dem erfolgreichen Posten, aber
        # vor dem Vermerk "gepostet", bleibt die Datei auf "sendet" und blockiert ein
        # Doppelposten. Schlaegt das Senden selbst fehl, geht sie zurueck auf "entwurf".
        meta["status"] = "sendet"
        datei.write_text(_fm_schreibe(meta, body), encoding="utf-8")
        try:
            if ziel.startswith("neu:") or (not ziel and not threads):
                thema = (ziel[4:].strip() if ziel.startswith("neu:") else "") or titel
                thema = thema[:120]
                neue_id = _poste(wesen, "neu", _post_inhalt("", body), titel=thema)
                import flarum_post_sperre
                flarum_post_sperre.ausnahme_hinzufuegen(
                    neue_id, grund=f"{THREAD_GRUND_PRAEFIX}: {thema}", von=wesen)
                ort = f"neuer Lieder-Thread d/{neue_id} '{thema}'"
                meta["disk"] = neue_id
            else:
                disk = int(ziel) if ziel.isdigit() else threads[0]["id"]
                post_id = _poste(wesen, "antwort", _post_inhalt(titel, body), discussion_id=disk)
                ort = f"Lieder-Thread d/{disk} (Post {post_id})"
                meta["disk"] = disk
        except Exception:
            meta["status"] = "entwurf"
            datei.write_text(_fm_schreibe(meta, body), encoding="utf-8")
            raise
        meta["status"] = "gepostet"
        meta["gepostet"] = _jetzt()
        datei.write_text(_fm_schreibe(meta, body), encoding="utf-8")
        state = _state_lesen()
        e = tages_status(wesen)
        if ist_lied:
            e["lieder"] += 1
        else:
            e["schnipsel"] += 1
        e["zuletzt"] = f"veroeffentlicht ({_rel(wesen, datei)})"
        state[wesen] = e
        _state_schreiben(state)
    art = "Lied" if ist_lied else "Schnipsel"
    return (f"{art} veroeffentlicht in {ort}. Heute: {tages_status(wesen)['lieder']} von "
            f"{MAX_LIEDER_PRO_TAG} ganzen Liedern, {tages_status(wesen)['schnipsel']} Schnipsel.")


def antworten(wesen: str, disk_id: int, text: str) -> str:
    """Direkte Antwort unter einem Lieder-Thread -- ohne Entwurf, ohne Zaehler."""
    text = _ohne_aktionszeilen((text or "").strip()).strip()
    if not text:
        raise ValueError("Kein Text")
    _pruefe_kein_etikett(text)
    if not ist_lieder_thread(disk_id):
        raise PermissionError(f"d/{disk_id} ist kein Lieder-Thread -- nur unter Lieder-Posts "
                              f"darfst du antworten")
    post_id = _poste(wesen, "antwort", text[:8000], discussion_id=int(disk_id))
    _merke_zuletzt(wesen, f"unter anderen geantwortet (d/{disk_id})")
    return f"Antwort in Lieder-Thread d/{disk_id} gesendet (Post {post_id})"


# ------------------------------------------------------ Einladung / Ticket

def _lade_text(datei: Path) -> str:
    try:
        t = datei.read_text(encoding="utf-8")
    except OSError:
        return ""
    _, body = _fm_parse(t)
    return body.strip()


def _fuelle(text: str, wesen: str) -> str:
    st = tages_status(wesen)
    zuletzt = st.get("zuletzt") or "noch nichts"
    try:
        dateien = ", ".join(erkunde(wesen)[:12]) or "noch keine"
    except Exception:
        dateien = "?"
    try:
        offen = ohne_eindruck(wesen)
        eindruck_zeile = (", ".join(offen[:6]) + (f" (+{len(offen) - 6} weitere)" if len(offen) > 6 else "")) if offen else "keine"
    except Exception:
        eindruck_zeile = "?"
    if "{alle_dateien}" in text:
        try:
            text = text.replace("{alle_dateien}", dateiliste(wesen))
        except Exception:
            text = text.replace("{alle_dateien}", "?")
    return (text.replace("{heute_lieder}", str(st["lieder"]))
                .replace("{ohne_eindruck}", eindruck_zeile)
                .replace("{deine_dateien}", dateien)
                .replace("{heute_schnipsel}", str(st["schnipsel"]))
                .replace("{zuletzt_gewaehlt}", zuletzt)
                .replace("{lieder_threads}", threads_zeile()))


def _nachhol_fenster(wesen: str) -> tuple[str, list[str], list[str]]:
    """Das 'Material' fuer den Nachhol-Tick: die eigenen Dateien OHNE Eindruck, aelteste zuerst
    (so schrumpft der Rueckstand von hinten), mit vollem Text, bis das Rueckschau-Budget erreicht ist.
    Gibt (Text, Namen im Fenster, Namen ausserhalb des Fensters) zurueck."""
    budget = RUECKSCHAU_TOKENS * ZEICHEN_PRO_TOKEN
    basis = vault_pfad(wesen)
    kandidaten = []
    for o in UNTERORDNER:
        d = basis / o
        if d.is_dir():
            kandidaten.extend(d.glob("*.md"))
    kandidaten.sort(key=lambda q: q.stat().st_mtime)
    teile, im_fenster, draussen, verbraucht = [], [], [], 0
    for p in kandidaten:
        meta, body = _lies_datei(p)
        sauber = re.sub(r"<!--.*?-->\n?", "", body).strip()
        if not sauber or _hat_eindruck(body):
            continue
        name = _rel(wesen, p)
        status = meta.get("status", "?")
        if status == "gepostet" and str(meta.get("disk", "")).isdigit():
            status = f"gepostet in d/{meta['disk']}"
        kopf = f"### {name}  ({status})\n"
        rest = budget - verbraucht - len(kopf)
        if rest < 200:
            draussen.append(name)
            continue
        stueck = sauber if len(sauber) <= rest else sauber[:rest] + " [...]"
        teile.append(kopf + stueck)
        verbraucht += len(kopf) + len(stueck)
        im_fenster.append(name)
    return "\n\n".join(teile), im_fenster, draussen


def _offene_pflicht(wesen: str) -> str | None:
    """'nachholen' oder 'weiterarbeiten', solange das Wesen in seinem letzten Tick seine Pflicht
    (mindestens einen Eindruck schreiben bzw. mindestens eine Datei waehlen) nicht erfuellt hat."""
    return _state_lesen().get(wesen, {}).get("tick_offen") or None


def _setze_pflicht(wesen: str, typ: str | None) -> None:
    with _sperre():
        state = _state_lesen()
        roh = state.get(wesen, {})
        e = tages_status(wesen)
        if roh.get("tick_typ") and not e.get("tick_typ"):
            e["tick_typ"] = roh["tick_typ"]
        if typ:
            e["tick_offen"] = typ
        else:
            e.pop("tick_offen", None)
        state[wesen] = e
        _state_schreiben(state)


def _pflicht_erfuellt(wesen: str, typ: str) -> None:
    if _offene_pflicht(wesen) == typ:
        _setze_pflicht(wesen, None)


def naechster_tick_typ(wesen: str) -> str:
    """'nachholen' oder 'weiterarbeiten'. Solange Dateien ohne Eindruck da sind, wechseln sich die
    beiden ab; sind keine mehr da, gibt es nur noch 'weiterarbeiten'. Hat das Wesen die Pflicht des
    letzten Ticks nicht erfuellt (kein Eindruck geschrieben bzw. nichts gewaehlt), kommt derselbe Tick
    noch einmal, bis es geschehen ist (Daniel 2026-10-03: 'erzwingen')."""
    offen = _offene_pflicht(wesen)
    if offen == "nachholen" and ohne_eindruck(wesen):
        return "nachholen"
    if offen == "weiterarbeiten":
        return "weiterarbeiten"
    if not ohne_eindruck(wesen):
        return "weiterarbeiten"
    letzter = tages_status(wesen).get("tick_typ") or _state_lesen().get(wesen, {}).get("tick_typ")
    return "weiterarbeiten" if letzter == "nachholen" else "nachholen"


def _merke_tick_typ(wesen: str, typ: str) -> None:
    with _sperre():
        state = _state_lesen()
        roh = state.get(wesen, {})
        e = tages_status(wesen)
        e["tick_typ"] = typ
        e["tick_offen"] = typ  # bleibt offen, bis die Pflicht erfuellt ist
        state[wesen] = e
        _state_schreiben(state)


def waehle(wesen: str, namen: list[str]) -> str:
    """Das Wesen entscheidet, an welchen Dateien es weiterarbeitet. Danach (naechster Check-in,
    ueber den Folge-Mechanismus) bekommt es die grosse Datei zusammen mit dem vollen Text seiner
    Wahl. Erst entscheiden, dann lesen (Daniel 2026-10-03)."""
    namen = [n.strip() for n in namen if n.strip()]
    if not namen:
        raise ValueError("Format lied_waehlen:<ordner/name>[,<ordner/name>,...]")
    gewaehlt = []
    for n in namen:
        p = _finde_bestehende(wesen, n)
        gewaehlt.append((_rel(wesen, p), lese(wesen, n, maximal=33333)))
    gross = rueckschau(wesen) or "(du hast sonst keine halbfertigen Sachen)"
    wahl = "\n\n".join(t for _, t in gewaehlt)
    setze_folge(wesen, f"DEINE WAHL (voller Text):\n{wahl}\n\nDIE GROSSE DATEI (alles Halbfertige auf einmal):\n{gross}")
    _merke_zuletzt(wesen, "gewählt: " + ", ".join(r for r, _ in gewaehlt))
    _pflicht_erfuellt(wesen, "weiterarbeiten")
    return ("Gewählt: " + ", ".join(r for r, _ in gewaehlt)
            + ". Gleich bekommst du die große Datei und den vollen Text deiner Wahl.")


def baue_block(wesen: str, mit_einladung: bool = False, folge: str | None = None) -> str:
    """Der Text, der einem Wesen zum Lieder-Takt in den Prompt gelegt wird.
    mit_einladung: der komplette Einladungstext (alle 90 Minuten).
    folge: grosse Datei + Wahl -- danach kommt dieselbe Dateiliste noch einmal, mit dem Feinschliff-Zusatz."""
    teile = []
    if folge:
        teile.append("ZURÜCKGELESEN — DAS HAST DU BISHER:\n" + folge)
        teile.append(_fuelle(_lade_text(TICKET_DATEI), wesen).replace("{ticket_kopf}", _lade_text(TICKET_KOPF_WEITER_DATEI)))
        teile.append(_fuelle(_lade_text(TICKET_NACH_RUECKSCHAU_DATEI), wesen))
    else:
        if mit_einladung:
            teile.append("LIEDER — DIE EINLADUNG (einmal ganz lesen):\n" + _fuelle(_lade_text(EINLADUNG_DATEI), wesen))
        typ = naechster_tick_typ(wesen)
        erinnerung = _offene_pflicht(wesen) == typ  # beim letzten Mal nicht erfuellt
        _merke_tick_typ(wesen, typ)
        if erinnerung:
            teile.append("ERINNERUNG: Beim letzten Mal ist dabei nichts entstanden. Diesmal gehört es dazu, "
                         + ("dass du mindestens einen Eindruck schreibst." if typ == "nachholen"
                            else "dass du mindestens eine Datei wählst (lied_waehlen)."))
        if typ == "nachholen":
            fenster, im_fenster, draussen = _nachhol_fenster(wesen)
            text = _fuelle(_lade_text(TICK_NACHHOLEN_DATEI), wesen)
            text = (text.replace("{nachhol_material}", fenster or "(nichts)")
                        .replace("{nachhol_namen}", ", ".join(im_fenster) or "(keine)")
                        .replace("{nachhol_rest}", (", ".join(draussen) if draussen else "keine")))
            teile.append(text)
        else:
            teile.append(_fuelle(_lade_text(TICKET_DATEI), wesen).replace("{ticket_kopf}", _lade_text(TICKET_KOPF_WAEHLEN_DATEI)))
    return "\n\n".join(t for t in teile if t)


# ------------------------------------------------------------- Dispatcher

def fuehre_aus(wesen: str, entscheidung: str, text: str | None = None) -> str:
    """Fuehrt eine lied_*-Aktion aus. Gibt den Text zurueck, der dem Wesen als Ergebnis gezeigt
    wird. Fehler werden als Text zurueckgegeben, nie geworfen."""
    e = entscheidung.strip()
    try:
        if e.startswith("lied_schreiben:"):
            teile = e[len("lied_schreiben:"):].split("|", 1)
            pfad = teile[0].strip()
            inhalt = _echte_umbrueche((text or (teile[1] if len(teile) == 2 else "")).strip())
            rel = schreibe(wesen, pfad, inhalt[:12000])
            return f"[Lieder-Vault geschrieben: {rel}]"
        if e.startswith("lied_eindruck:"):
            teile = e[len("lied_eindruck:"):].split("|", 1)
            inhalt = _echte_umbrueche((text or (teile[1] if len(teile) == 2 else "")).strip())
            bloecke = _eindruck_bloecke(inhalt)
            if bloecke:  # mehrere Dateien in einer Aktion: Abschnitte "## <datei>"
                ergebnisse = []
                for datei_, eintext in bloecke:
                    try:
                        ergebnisse.append(schreibe_eindruck(wesen, datei_, eintext[:8000]))
                        _pflicht_erfuellt(wesen, "nachholen")
                    except Exception as ex_:
                        ergebnisse.append(f"{datei_}: fehlgeschlagen ({ex_})")
                return "[Lieder] " + " | ".join(ergebnisse)
            ergebnis_ = schreibe_eindruck(wesen, teile[0].strip(), inhalt[:8000])
            _pflicht_erfuellt(wesen, "nachholen")
            return "[Lieder] " + ergebnis_
        if e.startswith("lied_waehlen:"):
            return "[Lieder] " + waehle(wesen, (e[len("lied_waehlen:"):].split("|", 1)[0]).split(","))
        if e.startswith("lied_lesen:"):
            return "[Lieder-Vault gelesen]\n" + lese(wesen, e[len("lied_lesen:"):].strip())
        if e.startswith("lied_erkunden"):
            zeilen = erkunde(wesen, e.split(":", 1)[1] if ":" in e else "")
            return f"[Lieder-Vault] {len(zeilen)} Datei(en):\n" + "\n".join(zeilen[:60])
        if e.startswith("lied_rueckschau"):
            t = rueckschau(wesen)
            if not t:
                return "[Rückschau]: du hast noch keine halbfertigen Sachen -- fang einfach mit etwas Kleinem an"
            setze_folge(wesen, t)
            _merke_zuletzt(wesen, "Rückschau")
            return "[Rückschau]: gelesen -- gleich bekommst du alles auf einmal zu sehen"
        if e.startswith("lied_zusammenfuegen:"):
            teile = e[len("lied_zusammenfuegen:"):].split("|", 1)
            if len(teile) != 2:
                return "[Zusammenfügen]: Format lied_zusammenfuegen:<neuer-name>|<datei1>,<datei2>,..."
            rel = zusammenfuegen(wesen, teile[0].strip(), teile[1].split(","))
            return f"[Zusammengefügt zu {rel}] (die Quellen bleiben unverändert)"
        if e.startswith("lied_freigeben:"):
            teile = e[len("lied_freigeben:"):].split("|", 1)
            return "[Freigabe] " + freigeben(wesen, teile[0].strip(), teile[1].strip() if len(teile) == 2 else None)
        if e.startswith("lied_forum"):
            arg = e.split(":", 1)[1].strip() if ":" in e else ""
            return forum_lesen(wesen, int(arg) if arg.isdigit() else None)
        if e.startswith("lied_antworten:"):
            teile = e[len("lied_antworten:"):].split("|", 1)
            if len(teile) != 2 or not teile[0].strip().isdigit():
                return "[Antwort]: Format lied_antworten:<lieder-thread-id>|<text>"
            return "[Antwort] " + antworten(wesen, int(teile[0].strip()),
                                            _echte_umbrueche((text or teile[1]).strip()))
        return f"[Lieder]: unbekannte Aktion {e[:40]!r}"
    except FileNotFoundError as ex:
        # Die Wesen raten Dateinamen (im echten Lauf: lied_freigeben auf einen erfundenen Namen) --
        # deshalb gleich die tatsaechlich vorhandenen Dateien mitliefern, damit der zweite Versuch klappt.
        try:
            vorhanden = ", ".join(erkunde(wesen)[:15]) or "noch keine"
        except Exception:
            vorhanden = "?"
        return f"[Lieder fehlgeschlagen: {ex}]\nDas hast du aktuell in deinem Lieder-Vault: {vorhanden}"
    except Exception as ex:  # bewusst breit: ein Fehler hier darf den Wesen-Loop nie beenden
        return f"[Lieder fehlgeschlagen: {ex}]"
