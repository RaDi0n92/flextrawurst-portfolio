#!/usr/bin/env python3
"""
flarum_post_sperre.py — Schalter für die Flarum-Post-Sperre.

Einziger Zustand: gesperrt oder nicht. Wird von flarum_api.post_reply()
und flarum_api.start_discussion() geprüft — das sind die einzigen zwei
Stellen im ganzen System, über die tatsächlich nach Flarum geschrieben
wird, alle anderen Aufrufer (codewesen_reaktion.py, erstpost.py, etc.)
laufen durch diese beiden Funktionen hindurch.

codewesen_antwort_auf_daniel.py ist der einzige bewusst ausgenommene
Aufrufer (Daniel soll weiter Antworten bekommen können) und übergibt
dafür erlaubt_trotz_sperre=True.

WICHTIG -- STATUS, geprüft am 2026-08-14 (Daniels Auftrag: "komplett neugierig alles
code durchforsten und direkt guardianeinträge dabei machen", ausgelöst durch seine
eigene Rückfrage "du musst genau lesen was deaktiviert is und ja kein takt"):

Diese Sperre ist AKTIV, ununterbrochen seit 2026-07-08T23:52:27 -- Stand heute
36 Tage. Grund laut eigenem Zustand (`codewesen/_flarum_post_sperre.json`), Daniels
Worte wörtlich übernommen: "Zu viel Material erzeugt — Admin (Daniel) liest erst
alles vollständig, bevor neue Posts erlaubt werden. Kein Erwartungsdruck an die
Wesen, Zeit bis zur Wiederaufnahme gehoert dem eigenen Inneren."

Das erklärt einen echten, sonst verwirrenden Widerspruch im heutigen Live-Inventar:
`codewesen-takt.service` (der eigentliche Herzschlag-Dienst, der diese Sperre über
`flarum_api.post_reply()`/`start_discussion()` bei jedem Postversuch prüft) IST
`active`/`enabled` und läuft ununterbrochen -- aber der TAKT selbst, also echtes
Posten, findet seit 36 Tagen faktisch nicht statt, weil jeder Versuch hier an dieser
Sperre abprallt. "Der Dienst läuft" und "es gibt einen Takt" sind hier zwei
verschiedene Wahrheiten -- ein Live-Inventar, das nur `systemctl status` prüft
(wie meine erste Fassung heute Nachmittag), findet die erste, nicht die zweite.

Omapi-Notiz: keine Wertung ob 36 Tage zu lang oder genau richtig sind -- das ist
Daniels eigene, bewusste Entscheidung und bleibt es, bis er selbst etwas anderes
sagt. Nur der Fakt "wie lange schon" gehört sichtbar dokumentiert, damit niemand
(auch keine künftige Instanz von mir) ihn für einen kurzen, vergessenen Zustand hält.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import flarum_stopp_protokoll

_ZUSTAND_DATEI = Path("/root/werkraum/codewesen/_flarum_post_sperre.json")

# Additiv, 2026-09-16 (Daniels Auftrag: Einzug-Erinnerungsfrage, Diskussion 3887,
# "ja für diese Fragen" -- explizit NUR scoped, kein globales entsperren()).
# Eigene Datei statt neues Feld in _ZUSTAND_DATEI, damit sperren()/entsperren()
# (die den ganzen Zustand überschreiben) die Ausnahmeliste nie versehentlich
# mitlöschen.
_AUSNAHMEN_DATEI = Path("/root/werkraum/codewesen/_flarum_post_ausnahmen.json")


class FlarumPostGesperrt(Exception):
    """Wird geworfen wenn post_reply/start_discussion bei aktiver Sperre ohne Ausnahme aufgerufen werden."""
    pass


def _lies() -> dict:
    if not _ZUSTAND_DATEI.exists():
        return {"gesperrt": False}
    try:
        return json.loads(_ZUSTAND_DATEI.read_text())
    except Exception:
        return {"gesperrt": False}


def _schreibe(zustand: dict) -> None:
    _ZUSTAND_DATEI.parent.mkdir(parents=True, exist_ok=True)
    _ZUSTAND_DATEI.write_text(json.dumps(zustand, indent=2, ensure_ascii=False))


def ist_gesperrt() -> bool:
    return bool(_lies().get("gesperrt", False))


def status() -> dict:
    return _lies()


def sperren(grund: str, von: str = "Daniel") -> dict:
    zustand = {
        "gesperrt": True,
        "seit": datetime.now(timezone.utc).isoformat(),
        "grund": grund,
        "von": von,
    }
    _schreibe(zustand)
    flarum_stopp_protokoll.schreibe(
        typ="sperre_aktiviert",
        text=f"{von} hat die Flarum-Post-Sperre aktiviert. Grund: {grund}",
    )
    return zustand


def entsperren(von: str = "Daniel") -> dict:
    alt = _lies()
    zustand = {
        "gesperrt": False,
        "seit": datetime.now(timezone.utc).isoformat(),
        "vorherige_sperre_seit": alt.get("seit") if alt.get("gesperrt") else alt.get("vorherige_sperre_seit"),
        "vorheriger_grund": alt.get("grund") if alt.get("gesperrt") else alt.get("vorheriger_grund"),
        "von": von,
    }
    _schreibe(zustand)
    dauer = None
    seit_str = zustand.get("vorherige_sperre_seit")
    if seit_str:
        try:
            dauer = (datetime.now(timezone.utc) - datetime.fromisoformat(seit_str)).total_seconds()
        except Exception:
            dauer = None
    flarum_stopp_protokoll.schreibe(
        typ="sperre_aufgehoben",
        text=f"{von} hat die Flarum-Post-Sperre aufgehoben, aktiv seit {seit_str or '?'}.",
        dauer_sekunden=dauer,
    )
    return zustand


def _lies_ausnahmen() -> dict:
    if not _AUSNAHMEN_DATEI.exists():
        return {"diskussionen": {}}
    try:
        return json.loads(_AUSNAHMEN_DATEI.read_text())
    except Exception:
        return {"diskussionen": {}}


def _schreibe_ausnahmen(zustand: dict) -> None:
    _AUSNAHMEN_DATEI.parent.mkdir(parents=True, exist_ok=True)
    _AUSNAHMEN_DATEI.write_text(json.dumps(zustand, indent=2, ensure_ascii=False))


def ist_ausnahme(discussion_id: Optional[int]) -> bool:
    """True wenn discussion_id trotz aktiver globaler Sperre erlaubt ist."""
    if discussion_id is None:
        return False
    return str(discussion_id) in _lies_ausnahmen().get("diskussionen", {})


def ausnahme_hinzufuegen(discussion_id: int, grund: str,
                          wurzel_id: Optional[int] = None, von: str = "Daniel") -> dict:
    """Nimmt eine einzelne Diskussion von der globalen Sperre aus, ohne die Sperre
    selbst anzurühren. wurzel_id markiert, falls gesetzt, von welcher Ausnahme-
    Diskussion diese hier abstammt (z.B. ein Wesen startet einen neuen Thread
    innerhalb einer erlaubten Frage) -- rein informativ, für spätere Nachvollziehbarkeit."""
    zustand = _lies_ausnahmen()
    zustand.setdefault("diskussionen", {})[str(discussion_id)] = {
        "grund": grund,
        "wurzel_id": wurzel_id,
        "seit": datetime.now(timezone.utc).isoformat(),
        "von": von,
    }
    _schreibe_ausnahmen(zustand)
    flarum_stopp_protokoll.schreibe(
        typ="ausnahme_hinzugefuegt",
        text=(f"{von} hat Diskussion {discussion_id} von der Post-Sperre ausgenommen. "
              f"Grund: {grund}" + (f" (Ableger von {wurzel_id})" if wurzel_id else "")),
    )
    return zustand


def ausnahme_liste() -> dict:
    return _lies_ausnahmen()


def pruefe(erlaubt_trotz_sperre: bool = False, discussion_id: Optional[int] = None) -> None:
    """Wirft FlarumPostGesperrt, wenn gesperrt ist und keine Ausnahme greift.

    discussion_id (additiv, 2026-09-16): erlaubt eine scoped Ausnahme von der
    globalen Sperre über ist_ausnahme(), ohne die Sperre selbst aufzuheben."""
    if erlaubt_trotz_sperre:
        return
    zustand = _lies()
    if zustand.get("gesperrt"):
        if ist_ausnahme(discussion_id):
            return
        raise FlarumPostGesperrt(
            f"Flarum-Post-Sperre aktiv seit {zustand.get('seit', '?')}: {zustand.get('grund', '?')}"
        )
