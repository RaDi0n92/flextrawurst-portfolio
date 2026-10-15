"""Was ein Agent im offenen Menü auslösen darf (Käfig-Erweiterung für die Praxistest-Schritte 11 bis 17).

Zwei Listen, beide nach **Befehls-Id** und nie nach dem Text (der enthält Zustände wie „Deckkraft 80 %“):
- `IMMER_GESPERRT` gilt für das Raute-Menü und gewinnt immer, auch wenn ein Eintrag irrtümlich in einer Erlaubnisliste steht.
- `ERLAUBT` ist je Menü-Art ausdrücklich. Was dort nicht steht, ist gesperrt (Standard: Nein).
Befehls-Ids gelten nur innerhalb eines Menüs; deshalb hat jedes Untermenü seine eigene Art („raute.farbe“, „raute.anzeigeort“).
Das Menü schließen (reservierter Name „schließen“) ist in jedem offenen Menü erlaubt: es ist wie Esc und ändert nichts.

Die Ids sind die Werte der `MENUE_*`-Konstanten aus `erster_koerper.py`; ein Test hält beide Stellen gleich.
"""

from __future__ import annotations

# Raute-Menü: Id -> Name der Konstante in erster_koerper.py
RAUTE_IDS = {
    2: "MENUE_TERMINAL", 3: "MENUE_AGENT_BEENDEN", 4: "MENUE_BRIDGE_BEENDEN", 5: "MENUE_STATUS", 6: "MENUE_NOTAUS", 7: "MENUE_TRANSPARENZ", 8: "MENUE_GROESSER",
    9: "MENUE_KLEINER", 10: "MENUE_RAUTE_REGEL", 11: "MENUE_TERMINAL_REGEL", 12: "MENUE_TERMINAL_DURCHKLICK", 13: "MENUE_HOTKEY", 14: "MENUE_HAENDE", 15: "MENUE_BILDER",
    16: "MENUE_NAME", 17: "MENUE_FARBE", 18: "MENUE_NUR_TERMINAL", 19: "MENUE_ORT", 20: "MENUE_BILD_DATEI", 21: "MENUE_BILDFOLGE", 22: "MENUE_PLAETZE",
    23: "MENUE_ZEICHNEN", 24: "MENUE_BILD_ELEMENT", 25: "MENUE_ANZEIGEORT", 26: "MENUE_PAUSE", 27: "MENUE_PROFIL", 28: "MENUE_AUSNAHME",
}
_NAME_ZU_ID = {name: i for i, name in RAUTE_IDS.items()}

# Wer beendet, anhält, abschaltet oder die eigenen Schranken des Agenten verstellt: nie durch einen Agenten.
IMMER_GESPERRT = frozenset(_NAME_ZU_ID[n] for n in (
    "MENUE_AGENT_BEENDEN", "MENUE_BRIDGE_BEENDEN", "MENUE_NOTAUS", "MENUE_PAUSE",  # beenden, Not-Aus, anhalten
    "MENUE_HAENDE", "MENUE_NUR_TERMINAL", "MENUE_PROFIL", "MENUE_AUSNAHME",  # Hände, Augen und das Steuerprofil des Käfigs
    "MENUE_HOTKEY", "MENUE_NAME",  # Identität und Tastenkombination des Agenten
))

# Farbwahl im Raute-Menü (anwendung.py: FARBE_WAHL_ID + Nummer der Farbe, FARBE_STANDARD_ID); ein Test hält beides gleich.
FARBE_WAHL_ID, FARBE_STANDARD_ID, ANZAHL_FARBEN = 3200, 3299, 8

# Zweite Stufe. Erlaubt ist, was nur das Aussehen der eigenen Raute ändert oder ein Untermenü öffnet, dessen Einträge selbst wieder geprüft werden.
# Nicht erlaubt: „Ort der Elemente“, Wechsel des Anzeigeorts und Legen des Arbeitsziels (sie verlegen, wo ein Agent arbeitet), „Zeichnen“ (öffnet ein eigenes Fenster, noch nicht beobachtet).
ERLAUBT: dict[str, frozenset[int]] = {
    "raute": frozenset(_NAME_ZU_ID[n] for n in ("MENUE_TRANSPARENZ", "MENUE_GROESSER", "MENUE_KLEINER", "MENUE_FARBE", "MENUE_ANZEIGEORT")),
    "raute.farbe": frozenset(range(FARBE_WAHL_ID, FARBE_WAHL_ID + ANZAHL_FARBEN)) | {FARBE_STANDARD_ID},
    "raute.anzeigeort": frozenset(),  # nur ansehen (Bild) und schließen; nichts davon darf den Ort verändern
}

SCHLIESSEN_NAMEN = frozenset({"schliessen", "schließen"})


def pruefe_eintrag(art: str, befehl: int) -> str:
    """Leer, wenn der Eintrag ausgelöst werden darf, sonst der Ablehnungsgrund."""
    if art == "raute" and befehl in IMMER_GESPERRT:
        return "menue_eintrag_gesperrt"
    if befehl in ERLAUBT.get(art, frozenset()):
        return ""
    return "menue_eintrag_gesperrt"
