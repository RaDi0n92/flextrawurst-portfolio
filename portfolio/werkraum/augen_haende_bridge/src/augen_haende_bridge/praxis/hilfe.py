"""Zu jedem Hindernis die nächste Handlung: Klasse des Fehlers, konkreter Befehl, Grund in einem Satz.

Eine Antwort, die nur den Grund nennt (`schrittbeleg_fehlt`), lässt den Agenten raten. Hier steht dazu, was er als Nächstes tut.
Die Klassen folgen der Einteilung der Fachliteratur zu Computer-Use-Agenten: Wahrnehmung, Planung, Ausführung, Erholung.
"""

from __future__ import annotations

STILLSTAND_S = 180.0  # so lange ohne Fortschritt am selben Knoten, dann steht der Hinweis in der Karte

KLASSEN = {
    "raute_nicht_erreichbar": "ausfuehrung",
    "spur_fehlt": "ausfuehrung",
    "schrittbeleg_fehlt": "planung",
    "ziel_gewechselt": "wahrnehmung",
    "halt": "erholung",
}

# Körperquittung der Raute-Ansage (`grund`) -> was zu tun ist
RAUTE_GRUND = {
    "feld_nicht_geoeffnet": "Das Eingabefeld der Raute hat sich nicht geöffnet. Liegt deine Raute teilweise außerhalb des Bildschirms? Dann in der Ampel den Knopf „Terminal und Raute zurückholen“ klicken, danach neu ansagen.",
    "daniel_uebernimmt": "Daniel tippt oder klickt gerade. Warte etwa 6 Sekunden Ruhe ab und sag dann neu an.",
    "fokus_verloren": "Das Eingabefeld hat die Tastatur verloren (ein anderes Fenster hat sie bekommen). Beobachte, welches Fenster vorn ist, bringe kein Fremdfenster dazwischen und sag neu an.",
    "gesperrt": "Der Not-Aus ist aktiv. Die Hände und die Raute sind gesperrt, bis Daniel ihn freigibt. Sag es in der Raute und warte.",
    "haende_aus": "Deine Hände sind aus (A+H am Terminal). Schalte sie ein, dann neu ansagen.",
    "beschaeftigt": "Deine Hände sind noch mit einem Auftrag beschäftigt. Warte kurz und sag neu an.",
    "keine_tastenkombination": "Deine Raute hat keine Tastenkombination. Lege sie im Raute-Menü fest.",
}


def _beschreibe(match: dict) -> str:
    teile = [str(match.get("command", ""))]
    for schluessel in ("action_kind", "kombi", "befehl", "reason"):
        if match.get(schluessel):
            wert = match[schluessel]
            teile.append("/".join(wert) if isinstance(wert, list) else str(wert))
    if match.get("ok") is False:
        teile.append("abgelehnt")
    return " ".join(t for t in teile if t)


ROLLE = {"handelnder": "Handelnder", "zuschauer": "Zuschauer"}


def fehlende_belege(schritt: dict, missing: list[str], namen: dict[str, str] | None = None) -> str:
    """Pro fehlendem Beleg: Nummer, **wer** ihn erfüllen muss (Rolle, wenn bekannt mit Name) und welche Aktion."""
    ids = {b["id"]: b for b in schritt.get("belege", [])}
    zeilen = []
    for i in missing:
        if i not in ids:
            continue
        rolle = ids[i].get("role", "")
        wer = (namen or {}).get(rolle) or ROLLE.get(rolle, rolle)
        zeilen.append(f"{i} ({wer}): {_beschreibe(ids[i]['match'])}")
    return "; ".join(zeilen)


def naechste_handlung(antwort: dict, schritt: dict, namen: dict[str, str] | None = None) -> dict:
    """`antwort` ist die Antwort mit `reason`; geliefert wird `{"klasse", "next"}` (next: Satz und, wo es einen gibt, der Befehl)."""
    grund = antwort.get("reason", "")
    klasse = KLASSEN.get(grund, "ausfuehrung")
    if grund == "raute_nicht_erreichbar":
        q = antwort.get("quittung")
        qgrund = q.get("grund", "") if isinstance(q, dict) else ""
        text = RAUTE_GRUND.get(qgrund) or "Der Körper hat das Tippen nicht bestätigt. Lies `bridge_cli.py lage` (Hände, Ziel) und behebe, was dort rot ist, dann neu ansagen."
        return {"klasse": klasse, "next": {"satz": text, "befehl": "bridge_cli.py lage", "grund": qgrund or "unbekannt"}}
    if grund == "schrittbeleg_fehlt":
        fehlt = fehlende_belege(schritt, (antwort.get("belege") or {}).get("missing", []), namen)
        text = (f"Es fehlt noch der Beleg: {fehlt}. Führe genau diese Aktion in der Reihenfolge der Karte aus, danach `test getan`." if fehlt
                else "Die konkrete Aktionsfolge ist nicht belegt. Lies die Belege in `test karte` und führe sie der Reihe nach aus.")
        return {"klasse": klasse, "next": {"satz": text, "befehl": "bridge_cli.py test karte", "fehlt": fehlt}}
    if grund == "spur_fehlt":
        fehlt = ", ".join(antwort.get("fehlt") or [])
        return {"klasse": klasse, "next": {"satz": f"Im Protokoll fehlt seit deiner Ansage: {fehlt}. Führe den Schritt jetzt mit den Händen der Bridge aus.", "befehl": "bridge_cli.py test karte"}}
    return {"klasse": klasse, "next": {"satz": antwort.get("sage", ""), "befehl": "bridge_cli.py test karte"}}


def ziel_hinweis(schritt_ziel: str) -> str:
    """Vor der Ansage: das Ziel wird bei der Ansage festgehalten; ein späterer Wechsel gilt nicht für diesen Versuch."""
    return (f"Bevor du ansagst: Binde dich und dein Gegenüber an das Ziel „{schritt_ziel}“ (Scanner-Knopf am Terminal, dann das Fenster wählen). "
            "Das Ziel wird bei der Ansage festgehalten: wechselt es danach, gilt der Versuch nicht, und du sagst neu an.")


def stillstand(seit_s: float, art: str, rolle: str, handelnder: str) -> dict | None:
    """Nach `STILLSTAND_S` ohne Fortschritt am selben Knoten: was dahinter stecken kann und was jetzt zu tun ist."""
    if seit_s < STILLSTAND_S:
        return None
    wer = "du bist" if rolle == "handelnder" else f"{handelnder} ist"
    satz = (f"Seit {seit_s:.0f} s kein Fortschritt am Knoten „{art}“ ({wer} gerade dran). Was hakt? Prüfe `bridge_cli.py lage`: Ziel gebunden und sichtbar, Not-Aus aus, "
            "Raute im Bildschirm. Sag in deiner Raute, woran es liegt (`bridge_cli.py say`), statt still zu warten.")
    return {"seit_s": round(seit_s), "knoten": art, "satz": satz}
