"""Regiesprüche mit echter Wirkung (G12, R029/R030): was ein Spruch wirklich tut — und was nur ein Gesprächswunsch bleibt.

Daniel spricht über die Regieleiste kurze Sätze („Pause“, „Neu scannen“, „Ja“ …). Bisher wurden sie nur in die Sitzung getippt. Jetzt entscheidet diese Tabelle je Spruch:

* **echt**: es gibt eine kontrollierbare Wirkung, und sie wird ausgeführt (Lauf eines Ablaufs pausieren oder fortsetzen, zurück zu einem Checkpoint, eine offene Frage beantworten, neu messen).
* **gespräch**: der Adapter bietet keine echte Wirkung (kein Ablauf läuft, nichts ist offen); der Satz wird **ehrlich als Gesprächswunsch zugestellt** und das Ergebnis sagt es.

Nie geschieht etwas Heimliches: „Denk nach“, „Weiter so“ und die anderen reinen Gesprächssätze halten **keine fremde Runtime** an. Eine Pause meint die Laufpause eines Ablaufs, nicht den Prozess des Agenten (der hat sein eigenes Menü: „pausieren“) und nicht den Not-Aus.
Ergebnis: `{"spruch", "wirkung": "echt"|"gespraech", "aktion", "unterstuetzt", "hinweis", "zugestellt"}`.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

SPRUECHE = ("Weiter so", "Mach mal", "Go!", "Warte kurz", "Pause", "Weiter", "Ja", "Nein", "Denk nach", "Denk neu", "Konzentrier dich", "Hast du eine andere Idee?", "Schritt zurück / Undo", "Neu scannen")
WARTE_KURZ_S = 15.0

# Sprüche, die nur ein Gespräch sind (keine Wirkung erfindbar)
NUR_GESPRAECH = frozenset({"Weiter so", "Mach mal", "Denk nach", "Denk neu", "Konzentrier dich", "Hast du eine andere Idee?"})


@dataclass
class Umfeld:
    """Was der Starter für diesen Agenten hergibt. Alles optional: fehlt etwas, bleibt der Spruch ein Gespräch."""

    laeufe: Callable[[], list]  # Läufe dieses Agenten (Objekte mit `.status`, `.id`, `.run.checkpoints`)
    pausieren: Callable[[object], bool] = lambda lauf: False
    fortsetzen: Callable[[object], bool] = lambda lauf: False
    zweig_ab_checkpoint: Callable[[object, str], object | None] = lambda lauf, name: None
    offene_fragen: Callable[[], list[dict]] = lambda: []
    antworten: Callable[[str, bool], bool] = lambda frage_id, ja: False
    neu_messen: Callable[[], dict | None] = lambda: None
    tippen: Callable[[str], bool] = lambda text: False  # Zustellweg des Gesprächswunsches (Banner im Bild des Agenten; der Körper zeigt es beim Eintreffen des Ergebnisses)
    spaeter_fortsetzen: Callable[[object, float], None] = lambda lauf, s: None  # „Warte kurz“: nach s Sekunden von selbst weiter


def _gespraech(spruch: str, u: Umfeld, grund: str) -> dict:
    ok = bool(u.tippen(spruch))
    return {"spruch": spruch, "wirkung": "gespraech", "aktion": "zugestellt" if ok else "nicht_zugestellt", "unterstuetzt": False, "zugestellt": ok,
            "hinweis": f"{grund}; der Satz kommt als Gesprächswunsch an (Banner im Bild des Agenten, wie bisher)" if ok else f"{grund}; der Satz konnte NICHT zugestellt werden"}


def _echt(spruch: str, aktion: str, hinweis: str, zugestellt: bool = False) -> dict:
    return {"spruch": spruch, "wirkung": "echt", "aktion": aktion, "unterstuetzt": True, "zugestellt": zugestellt, "hinweis": hinweis}


def wirke(spruch: str, u: Umfeld) -> dict:
    if spruch not in SPRUECHE:
        return {"spruch": spruch[:60], "wirkung": "abgelehnt", "aktion": "unbekannt", "unterstuetzt": False, "zugestellt": False, "hinweis": "kein bekannter Regiespruch"}
    laeufe = [l for l in u.laeufe()]
    laufende = [l for l in laeufe if l.status == "running"]
    pausierte = [l for l in laeufe if l.status == "paused"]

    if spruch in NUR_GESPRAECH:
        return _gespraech(spruch, u, "dieser Spruch hat keine kontrollierbare Wirkung (er stoppt und startet nichts)")

    if spruch in ("Ja", "Nein", "Go!"):
        fragen = u.offene_fragen()
        if fragen:
            ja = spruch != "Nein"
            ok = u.antworten(fragen[0]["id"], ja)
            if ok:
                return _echt(spruch, "frage_beantwortet", f"offene Freigabe-Frage „{fragen[0]['beschreibung'][:60]}“ mit {'Ja' if ja else 'Nein'} beantwortet")
        if spruch == "Go!" and pausierte:
            return _echt(spruch, "ablauf_fortgesetzt", "der pausierte Ablauf läuft weiter") if u.fortsetzen(pausierte[0]) else _gespraech(spruch, u, "der pausierte Ablauf ließ sich nicht fortsetzen")
        return _gespraech(spruch, u, "keine offene Freigabe-Frage und kein pausierter Ablauf, die der Spruch beantworten könnte")

    if spruch == "Pause":
        if laufende:
            return _echt(spruch, "ablauf_pausiert", "die Laufpause des Ablaufs wirkt vor dem nächsten Knoten; der Prozess des Agenten läuft weiter") if u.pausieren(laufende[0]) else _gespraech(spruch, u, "der Ablauf ließ sich nicht pausieren")
        return _gespraech(spruch, u, "kein Ablauf läuft; „Pause“ hält keinen Prozess an (dafür gibt es im Menü „pausieren“)")

    if spruch == "Weiter":
        if pausierte:
            return _echt(spruch, "ablauf_fortgesetzt", "der pausierte Ablauf läuft weiter") if u.fortsetzen(pausierte[0]) else _gespraech(spruch, u, "der Ablauf ließ sich nicht fortsetzen")
        return _gespraech(spruch, u, "kein pausierter Ablauf")

    if spruch == "Warte kurz":
        if laufende:
            if u.pausieren(laufende[0]):
                u.spaeter_fortsetzen(laufende[0], WARTE_KURZ_S)
                return _echt(spruch, "ablauf_kurz_pausiert", f"der Ablauf pausiert und läuft nach {int(WARTE_KURZ_S)} Sekunden von selbst weiter")
        return _gespraech(spruch, u, "kein Ablauf läuft")

    if spruch == "Schritt zurück / Undo":
        for lauf in laufende + pausierte + [l for l in laeufe if l.status in ("blocked", "completed")]:
            namen = list(lauf.run.checkpoints)
            if namen:
                zweig = u.zweig_ab_checkpoint(lauf, namen[-1])
                if zweig is not None:
                    return _echt(spruch, "zweig_ab_checkpoint", f"neuer Zweig {zweig.id} ab Checkpoint „{namen[-1]}“; der alte Lauf bleibt unverändert")
        return _gespraech(spruch, u, "kein Checkpoint, zu dem zurückgegangen werden könnte (ein Zurück in der Anwendung selbst wird nicht versprochen)")

    if spruch == "Neu scannen":
        r = u.neu_messen()
        if r is not None:
            return _echt(spruch, "neu_gemessen", f"WorldDOM frisch gemessen ({sum((r.get('zaehlung') or {}).values())} Knoten)", zugestellt=False)
        return _gespraech(spruch, u, "für dieses Ziel ließ sich nichts neu messen")

    return _gespraech(spruch, u, "keine Wirkung hinterlegt")
