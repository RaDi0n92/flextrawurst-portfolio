"""Die Ampel: aus dem Zustand eines Agenten werden Lampen mit Farbe, Blinken, Pieps-Wunsch und einer Behebung.

Rein, ohne Fenster: `ampel_fenster.py` zeichnet, was hier berechnet wird. Alles, was passiert und schiefgehen kann, ist sichtbar und
per Knopfdruck behebbar. Die Farbe steht nie allein: jede Lampe trägt ein Wort.

Farben (intern gruen/gelb/rot/grau, angezeigt als Blau, Orange, Rot, Grau): läuft, Achtung, kaputt, ausdrücklich aus.

Funktionsgruppen je Agent:

* **Augen** – kommt ein frisches Bild? Das Keepalive kommt alle 15 s; bis 20 s läuft es, bis 45 s ist es Achtung, darüber kaputt.
* **Hände** – wie ging die letzte Aktion aus, insgesamt, je Aktionsart und je Programm, und wenn abgelehnt: warum?
* **Ziel** – woran ist der Agent gebunden, ist das Fenster noch da, liegen die Fenster im Bildschirm?
* **System** – Verbindung zur Bridge, Not-Aus.
"""

from __future__ import annotations

from dataclasses import dataclass

GRUEN, GELB, ROT, GRAU = "gruen", "gelb", "rot", "grau"

BILD_GRUEN_S = 20.0
BILD_GELB_S = 45.0
HAENDE_FRISCH_S = 120.0  # eine Aktion, die länger her ist, zählt nicht mehr als Zustand
BLINKEN_NACH_FEHLER_S = 12.0

# Ablehnungsgründe der Hände → (Wort, Farbe, Behebe-Aktion). Aktionen setzt die Anwendung um (`ampel_aktion`).
HAENDE_GRUENDE = {
    "daniel_uebernimmt": ("Daniel bedient", GELB, None),
    "punkt_verdeckt": ("Ziel verdeckt", ROT, "fenster_vor"),
    "frame_unbekannt": ("kein Bezugsbild", ROT, "strom_neu"),
    "frame_veraltet": ("Bild zu alt", ROT, "strom_neu"),
    "ziel_weg": ("Fenster weg", ROT, "desktop_binden"),
    "lease_fehlt": ("Lease fehlt", GELB, None),
    "geometrie_geaendert": ("Fenster verschoben", GELB, "strom_neu"),
}

AKTIONS_TEXT = {
    "fenster_vor": "Fenster nach vorn",
    "strom_neu": "Bilder neu starten",
    "desktop_binden": "Desktop binden",
}


@dataclass(frozen=True)
class Led:
    name: str
    farbe: str
    wort: str
    blinkt: bool = False
    behebe: str | None = None  # Name der Aktion oder None
    piepen: bool = False  # nur beim Wechsel auf Rot, nicht in Dauerschleife (siehe `neue_pieps`)


def augen_led(*, an: bool, nur_terminal: bool, strom_vorhanden: bool, alter_s: float | None, gesperrt: bool) -> Led:
    if nur_terminal:
        return Led("augen", GRAU, "nur Terminal")
    if gesperrt:
        return Led("augen", ROT, "Not-Aus", blinkt=True)
    if not an:
        return Led("augen", GRAU, "aus (Knopf)", behebe="strom_neu")
    if not strom_vorhanden:
        return Led("augen", ROT, "kein Strom", blinkt=True, behebe="desktop_binden", piepen=True)
    if alter_s is None:
        return Led("augen", GELB, "wartet auf erstes Bild")
    if alter_s <= BILD_GRUEN_S:
        return Led("augen", GRUEN, f"Bild {int(alter_s)} s")
    if alter_s <= BILD_GELB_S:
        return Led("augen", GELB, f"Bild {int(alter_s)} s alt")
    minuten = int(alter_s // 60)
    wort = f"KEIN BILD seit {minuten} min" if minuten else f"KEIN BILD seit {int(alter_s)} s"
    return Led("augen", ROT, wort, blinkt=True, behebe="strom_neu", piepen=True)


def haende_led(*, haende_an: bool, letztes: tuple[str, str, float] | None) -> Led:
    """`letztes` = (Status, Grund, Alter in s) der letzten Aktion, None wenn noch keine kam."""
    if not haende_an:
        return Led("haende", GRAU, "aus")
    if letztes is None:
        return Led("haende", GRAU, "noch keine Aktion")
    status, grund, alter = letztes
    if alter > HAENDE_FRISCH_S:
        return Led("haende", GRAU, "ruhig")
    if status in ("ausgefuehrt", "ok"):
        return Led("haende", GRUEN, "Aktion ok")
    wort, farbe, aktion = HAENDE_GRUENDE.get(grund, (grund or "abgelehnt", ROT, None))
    frisch = alter <= BLINKEN_NACH_FEHLER_S
    return Led("haende", farbe, wort, blinkt=frisch and farbe == ROT, behebe=aktion, piepen=frisch and farbe == ROT)


def ziel_led(*, gebunden: bool, ziel_text: str, fenster_weg: bool) -> Led:
    if fenster_weg:
        return Led("ziel", ROT, "Fenster weg", blinkt=True, behebe="desktop_binden", piepen=True)
    if not gebunden:
        return Led("ziel", GELB, "ganzer Desktop")
    kurz = ziel_text.removeprefix("Ziel: ").strip()
    return Led("ziel", GRUEN, kurz[:22] or "gebunden")


def lauf_led(*, lauf: dict | None) -> Led:
    """`lauf` = {"knoten": "s7.handeln", "dran": "Opencode", "wartet_auf": "Bild", "seit_s": 410} oder None."""
    if not lauf:
        return Led("lauf", GRAU, "kein Lauf")
    dran = lauf.get("dran") or "?"
    wartet = lauf.get("wartet_auf")
    seit = float(lauf.get("seit_s") or 0)
    wort = f"{lauf.get('knoten', '?')}: {dran}"
    if wartet:
        wort += f" wartet auf {wartet}"
        if seit > 180:
            return Led("lauf", ROT, f"{wort} ({int(seit // 60)} min)", blinkt=True, piepen=True)
        if seit > 60:
            return Led("lauf", GELB, f"{wort} ({int(seit)} s)")
    return Led("lauf", GRUEN, wort)


def zeile(*, name: str, an: bool, nur_terminal: bool, haende_an: bool, strom_vorhanden: bool, alter_s: float | None,
          gesperrt: bool, letztes: tuple[str, str, float] | None, gebunden: bool, ziel_text: str, fenster_weg: bool,
          lauf: dict | None = None) -> tuple[str, list[Led]]:
    """Die LEDs eines Agenten. Die Lauf-LED erscheint nur, wenn Laufdaten da sind: eine LED, die „kein Lauf“ lügt, wäre schlimmer als keine."""
    leds = [
        augen_led(an=an, nur_terminal=nur_terminal, strom_vorhanden=strom_vorhanden, alter_s=alter_s, gesperrt=gesperrt),
        haende_led(haende_an=haende_an, letztes=letztes),
        ziel_led(gebunden=gebunden, ziel_text=ziel_text, fenster_weg=fenster_weg),
    ]
    if lauf is not None:
        leds.append(lauf_led(lauf=lauf))
    return name, leds


def neue_pieps(vorher: dict[tuple[str, str], str], zeilen: list[tuple[str, list[Led]]]) -> tuple[bool, dict[tuple[str, str], str]]:
    """Piepen genau einmal beim Wechsel einer LED auf Rot mit Pieps-Wunsch, nie dauerhaft.

    Gibt (soll_piepen, neuer Zustand) zurück; `vorher` und der neue Zustand bilden (Agent, LED) auf die letzte Farbe ab.
    """
    jetzt: dict[tuple[str, str], str] = {}
    piepen = False
    for agent, leds in zeilen:
        for led in leds:
            schluessel = (agent, led.name)
            jetzt[schluessel] = led.farbe
            if led.piepen and led.farbe == ROT and vorher.get(schluessel) != ROT:
                piepen = True
    return piepen, jetzt


def gesamt(zeilen: list[tuple[str, list[Led]]]) -> tuple[str, str, bool]:
    """Die Gesamtanzeige in der Kopfzeile: (Farbe, Wort, blinkt). Ein Blick genügt: grün heißt alles gut, rot heißt Handeln."""
    rot = sum(1 for _n, leds in zeilen for led in leds if led.farbe == ROT)
    gelb = sum(1 for _n, leds in zeilen for led in leds if led.farbe == GELB)
    if rot:
        return ROT, f"{rot} PROBLEM" + ("E" if rot > 1 else ""), True
    if gelb:
        return GELB, f"{gelb} ACHTUNG", False
    if not zeilen:
        return GRAU, "KEIN AGENT", False
    return GRUEN, "ALLES GUT", False


# ---- Der Lampenkatalog: alles, woran der Praxistest auf vd1 gescheitert ist ----------------------------------------------
# Namen werden ausgeschrieben, keine Kürzel. Intern heißen die Farben gruen/gelb/rot/grau; angezeigt werden sie
# als Blau (in Ordnung), Orange (Achtung), Rot (kaputt) und Grau (ausdrücklich aus) – siehe `ampel_fenster.py`.
ZUSTANDSWORT = {GRUEN: "läuft", GELB: "Achtung", ROT: "kaputt", GRAU: "aus"}

HAENDE_ARTEN = {"menue": "Menü", "klick": "Klicken", "klicke": "Klicken", "doppelklick": "Doppelklick", "tippe": "Tippen", "taste": "Tasten", "rad": "Mausrad",
                "ziehe": "Ziehen", "zeige": "Zeigen", "bewege": "Maus bewegen"}


@dataclass(frozen=True)
class Zustand:
    """Alles, was die Anwendung über einen Agenten misst. Fehlendes darf nicht erfunden werden: was unbekannt ist, hat keine Lampe."""
    name: str
    an: bool = True
    nur_terminal: bool = False
    haende_an: bool = True
    strom_vorhanden: bool = True
    alter_s: float | None = None
    gesperrt: bool = False
    letztes: tuple[str, str, float] | None = None  # (Status, Grund, Alter) der letzten Hände-Aktion
    gruende: dict | None = None  # Ablehnungsgrund der Hände → Sekunden seit dem letzten Auftreten
    haende_arten: dict | None = None  # Aktionsart (klick, tippe …) → (Status, Grund, Alter) der letzten Aktion dieser Art
    haende_ziele: dict | None = None  # Name des Ziels (Programm) → (Status, Grund, Alter) der letzten Aktion dort
    probleme: frozenset = frozenset()  # Gründe, aus denen der Bilderstrom gerade nichts sendet
    gebunden: bool = False
    ziel_text: str = ""
    fenster_weg: bool = False
    terminal_draussen: bool = False  # das Terminal oder die Raute des Agenten liegt ganz oder teilweise außerhalb des Bildschirms
    verbunden: bool = True
    kamera: str = "aus"  # Zustand der Selbstbild-Kamera: aus, startet, ein, fehler
    dialog: tuple[str, str, float] | None = None  # (Art, Frage, Sekunden): der Agent wartet auf einen Dialog seines Programms (dialog_erkennung.py)
    ziel_zustand: str | None = None  # ok, verdeckt, minimiert, inaktiv, weg, unbekannt (None = kein Ziel)
    aufnahme: str | None = None  # frisch, fremde_pixel, letztes_bild, keine_aufnahme, unbekannt
    anzeigeort_grund: tuple | None = None  # (Grund, Alter in s) des letzten abgelehnten Anzeigeort-Befehls


@dataclass(frozen=True)
class Lampe:
    kennung: str  # stabiler Name, z. B. "bild"
    name: str  # die Funktion, ausgeschrieben: "Bilder kommen frisch an"
    farbe: str
    wort: str  # der Zustand in Worten: "Bild 7 s", "KEIN BILD seit 4 min"
    blinkt: bool = False
    behebe: str | None = None
    piepen: bool = False

    @property
    def zustandswort(self) -> str:
        return ZUSTANDSWORT.get(self.farbe, self.farbe)


# ---- Die Gates des Käfigs, in der Prüfreihenfolge von `eingabe_adapter.pruefe` ("erst, was alles stoppt, dann Rechte, dann das Ziel, dann das Bild,
# zuletzt die Punkte"): (Grund, Name der Prüfung, Farbe bei Ablehnung, Behebung, Sekunden, die eine Ablehnung als Lampe brennt).
# `not_aus` und `verbindung_weg` haben schon ihre eigene Lampe (nota, verb); sie zählen in `ABGEDECKT_DURCH`.
HAENDE_GATES = (
    ("not_aus", "Not-Aus ist frei", ROT, None, 60.0),
    ("verbindung_weg", "Verbindung zum Starter steht", ROT, None, 60.0),
    ("daniel_uebernimmt", "Daniel bedient nicht gerade", GELB, None, 15.0),
    ("haende_aus", "Hände sind für den Agenten erlaubt", GELB, None, 60.0),
    ("profil_erlaubt_nicht", "Steuerprofil erlaubt die Aktion", GELB, None, 60.0),
    ("kein_ziel", "Ein Fenster ist als Ziel der Hände gebunden", GELB, None, 60.0),
    ("lease_fehlt", "Der Agent hat eine Lease auf das Ziel", GELB, None, 60.0),
    ("lease_abgelaufen", "Die Lease ist gültig", GELB, None, 60.0),
    ("lease_fremd", "Die Lease gehört diesem Agenten", GELB, None, 60.0),
    ("ziel_weg", "Das Ziel-Fenster existiert", ROT, "desktop_binden", 60.0),
    ("ziel_minimiert", "Das Ziel ist nicht minimiert", ROT, "fenster_vor", 60.0),
    ("menue_nicht_freigegeben", "Menü-Fenster der Bridge sind für die Hände freigegeben", GELB, None, 60.0),
    ("menue_nicht_offen", "Ein Menü des Körpers ist offen", GELB, None, 60.0),
    ("menue_eintrag_unbekannt", "Das Menü hat den genannten Eintrag", GELB, None, 60.0),
    ("menue_eintrag_unklar", "Der Name passt auf genau einen Menüeintrag", GELB, None, 60.0),
    ("menue_eintrag_gesperrt", "Der Menüeintrag ist für Agenten erlaubt", GELB, None, 60.0),
    ("menue_eintrag_abgeblendet", "Der Menüeintrag ist nicht abgeblendet", GELB, None, 60.0),
    ("notaus_taste", "Die Taste ist nicht der Not-Aus", GELB, None, 60.0),
    ("systemtaste", "Die Tastenkombination ist nicht gesperrt", GELB, None, 60.0),
    ("frame_unbekannt", "Das Bezugsbild ist dem Körper bekannt", ROT, "strom_neu", 60.0),
    ("frame_anderes_ziel", "Das Bezugsbild gehört zum Ziel", ROT, "strom_neu", 60.0),
    ("frame_veraltet", "Das Bezugsbild ist frisch genug", ROT, "strom_neu", 60.0),
    ("ziel_ersetzt", "Unter dem Ziel liegt dasselbe Fenster", ROT, "strom_neu", 60.0),
    ("geometrie_geaendert", "Das Fenster ist seit dem Bild unverändert", GELB, "strom_neu", 60.0),
    ("ausserhalb", "Der Klickpunkt liegt im Ziel", GELB, None, 60.0),
    ("punkt_verdeckt", "Am Klickpunkt liegt kein anderes Fenster davor", ROT, "fenster_vor", 60.0),
    ("fokus_verloren", "Das Ziel hat die Tastatur", ROT, "fenster_vor", 60.0),
    ("fokus_nicht_erreichbar", "Dem Ziel lässt sich die Tastatur geben", ROT, "fenster_vor", 60.0),
    ("aktion_ungueltig", "Die Aktion ist vollständig und zulässig", GELB, None, 60.0),
    ("backend_fehler", "Das System nimmt die Eingabe an", ROT, None, 60.0),
    ("abgebrochen", "Die Aktion wird nicht abgebrochen", GELB, None, 60.0),
)
ABGEDECKT_DURCH = {"not_aus": "nota", "verbindung_weg": "verb"}  # diese Gate-Gründe zeigt eine eigene Lampe

# Die Gründe, aus denen der Bilderstrom einem Ziel kein Bild gibt (`Bilderstrom._stumm`), und die Lampe, die sie zeigt.
AUGEN_GRUENDE = {"gesperrt": "nota", "ziel_aus": "strom", "fenster_weg": "weg", "ziel_unsichtbar": "sicht",
                 "aufnahme_rueckfall": "aufn", "ausschnitt_leer": "ausschnitt", "senden_abgelehnt": "send"}

# Die Gründe, aus denen die Raute-Ansage scheitert (`Anwendung.HAENDE_GRUENDE`, "der Agent tippt über seine Tastenkombination in sein Eingabefeld"):
# (Grund, Name der Prüfung, Farbe bei Misserfolg). `gesperrt` zeigt die Not-Aus-Lampe, `agent_unbekannt` und `nur_terminal` zeigt der Bilderstrom.
RAUTE_GATES = (
    ("keine_tastenkombination", "Der Agent hat eine Tastenkombination für seine Raute", GELB),
    ("feld_nicht_geoeffnet", "Die Tastenkombination öffnet das Eingabefeld der Raute", ROT),
    ("fokus_verloren", "Das Eingabefeld der Raute behält die Tastatur", ROT),
    ("sendinput_fehlgeschlagen", "Das System nimmt die Tasten der Raute an", ROT),
    ("leerer_text", "Die Ansage ist nicht leer", GELB),
    ("daniel_uebernimmt", "Daniel tippt oder klickt nicht gerade, wenn die Raute schreibt", GELB),
)
RAUTE_ABGEDECKT = {"gesperrt": "nota", "agent_unbekannt": "strom", "nur_terminal": "strom"}

# Anzeigeort-Befehle (`anzeigeort.GRUND_TEXT`): die Gründe, aus denen ein Wechsel des Anzeigeorts oder Ziels abgelehnt wird.
ANZEIGEORT_GRUENDE = ("terminal_unbekannt", "nicht_beteiligt", "ort_unbekannt", "schon_dort", "ort_offline", "nicht_unterstuetzt", "ziel_abgelehnt")

# Zustand des Ziel-Fensters (`anzeigeort.ZIEL_ZUSTAENDE`) und Leistung der Aufnahme (`anzeigeort.ZIEL_FAEHIGKEITEN`): (Farbe, Wort, Behebung)
ZIEL_ZUSTAND_LAMPE = {"ok": (GRUEN, "sichtbar", None), "verdeckt": (GELB, "verdeckt", "fenster_vor"), "minimiert": (ROT, "minimiert", "fenster_vor"),
                      "inaktiv": (GELB, "inaktiv", "fenster_vor"), "weg": (ROT, "geschlossen", "desktop_binden"), "unbekannt": (GRAU, "unbekannt", None)}
AUFNAHME_LAMPE = {"frisch": (GRUEN, "Bild frisch", None), "fremde_pixel": (GELB, "Bild mit fremden Fenstern davor", "fenster_vor"),
                  "letztes_bild": (GELB, "nur das letzte Bild", "strom_neu"), "keine_aufnahme": (ROT, "keine Aufnahme", "strom_neu"),
                  "unbekannt": (GRAU, "Aufnahme unbekannt", None)}

KATALOG = ("bild", "strom", "sicht", "aufn", "ausschnitt", "send", "kamera", "aufnahme", "hand", "dialog", "zustand", "bind", "weg", "auss", "anzeigeort", "verb", "nota")
NAMEN = {"bild": "Bilder kommen frisch an", "strom": "Bilderstrom", "sicht": "Ziel ist sichtbar", "aufn": "Bild genau dieses Fensters",
         "send": "Bilder werden gesendet", "hand": "Hände insgesamt", "ausschnitt": "Bildausschnitt liegt im Bildschirm",
         "kamera": "Selbstbild-Kamera", "aufnahme": "Aufnahme des Ziels leistet etwas", "zustand": "Zustand des Ziel-Fensters",
         "anzeigeort": "Anzeigeort-Befehle werden angenommen",
         "bind": "Ziel des Agenten (gebundenes Fenster oder Desktop)", "weg": "Gebundenes Fenster ist da", "auss": "Fenster liegen im Bildschirm", "verb": "Verbindung zur Bridge",
         "nota": "Not-Aus (sperrt Hände und Bilder)", "dialog": "Agent wartet nicht auf einen Dialog seines Programms"}
AKTIONS_TEXT["terminal_holen"] = "Terminal zurückholen"
FRISCH_GRUND_S = 60.0  # eine Hände-Ablehnung brennt so lange als Lampe
FRISCH_DANIEL_S = 15.0
HAENDE_ALT_S = 300.0  # eine ältere Ablehnung einer Art oder eines Ziels ist nur noch "Achtung", nicht mehr "kaputt"


def _grund(z: Zustand, *gruende: str) -> float | None:
    """Sekunden seit dem jüngsten dieser Ablehnungsgründe, None wenn nicht (frisch) vorgekommen."""
    daten = z.gruende or {}
    alter = [daten[g] for g in gruende if g in daten]
    return min(alter) if alter else None


DIALOG_ROT_NACH_S = 180.0  # wartet ein Agent so lange auf einen Dialog, ist es kein Hinweis mehr, sondern ein Stillstand
DIALOG_ART = {"berechtigung": "eine Berechtigung", "vertrauen": "eine Vertrauensfrage", "ja_nein": "eine Ja/Nein-Frage"}


def dialog_lampe(dialog: tuple[str, str, float] | None) -> Lampe:
    """Der Agent kommt nicht weiter, weil sein Programm eine Antwort von Daniel braucht (z. B. „Allow once“): orange, nach drei Minuten rot und blinkend."""
    if not dialog:
        return Lampe("dialog", NAMEN["dialog"], GRUEN, "kein Dialog offen")
    art, frage, seit = dialog
    wort = f"wartet seit {int(seit)} s auf {DIALOG_ART.get(art, 'einen Dialog')}: {frage}"[:110]
    if seit >= DIALOG_ROT_NACH_S:
        return Lampe("dialog", NAMEN["dialog"], ROT, wort, blinkt=True, piepen=True)
    return Lampe("dialog", NAMEN["dialog"], GELB, wort)


def _l(kennung: str, led: Led) -> Lampe:
    return Lampe(kennung, NAMEN[kennung], led.farbe, led.wort, led.blinkt, led.behebe, led.piepen)


def _haende_lampe(kennung: str, name: str, ergebnis: tuple[str, str, float]) -> Lampe:
    """Die Lampe einer Aktionsart oder eines Programms: grün nach gelungener Aktion, sonst rot (frisch) oder orange (älter)."""
    status, grund, alter = ergebnis
    if status in ("ausgefuehrt", "ok"):
        return Lampe(kennung, name, GRUEN, "letzte Aktion gelungen")
    wort, farbe, aktion = HAENDE_GRUENDE.get(grund, (grund or "abgelehnt", ROT, None))
    if alter > HAENDE_ALT_S:
        return Lampe(kennung, name, GELB, f"zuletzt: {wort}")
    return Lampe(kennung, name, farbe, wort, blinkt=farbe == ROT and alter <= BLINKEN_NACH_FEHLER_S, behebe=aktion,
                 piepen=farbe == ROT and alter <= BLINKEN_NACH_FEHLER_S)


def lampen(z: Zustand) -> list[Lampe]:
    """Die Lampen eines Agenten in fester Reihenfolge, danach die Hände nach Aktionsart und Programm. Blau (grün) heißt läuft."""
    erg = [_l("bild", augen_led(an=z.an, nur_terminal=z.nur_terminal, strom_vorhanden=z.strom_vorhanden, alter_s=z.alter_s, gesperrt=z.gesperrt))]
    if z.nur_terminal:
        erg.append(Lampe("strom", NAMEN["strom"], GRAU, "nur Terminal"))
    elif not z.strom_vorhanden:
        erg.append(Lampe("strom", NAMEN["strom"], ROT, "kein Bilderstrom", blinkt=True, behebe="desktop_binden", piepen=True))
    elif not z.an:
        erg.append(Lampe("strom", NAMEN["strom"], GRAU, "Augen aus (Knopf)", behebe="strom_neu"))
    else:
        erg.append(Lampe("strom", NAMEN["strom"], GRUEN, "Strom läuft"))
    erg.append(Lampe("sicht", NAMEN["sicht"], *((ROT, "Ziel unsichtbar") if "ziel_unsichtbar" in z.probleme else (GRUEN, "sichtbar")),
                     behebe="fenster_vor" if "ziel_unsichtbar" in z.probleme else None))
    erg.append(Lampe("aufn", NAMEN["aufn"], *((GELB, "Bildschirmausschnitt statt Fensterbild") if "aufnahme_rueckfall" in z.probleme else (GRUEN, "Fensterbild"))))
    erg.append(Lampe("ausschnitt", NAMEN["ausschnitt"], *((ROT, "Ausschnitt liegt außerhalb des Bilds") if "ausschnitt_leer" in z.probleme else (GRUEN, "im Bildschirm")),
                     behebe="terminal_holen" if "ausschnitt_leer" in z.probleme else None))
    erg.append(Lampe("send", NAMEN["send"], *((ROT, "Sender lehnt Bilder ab") if "senden_abgelehnt" in z.probleme else (GRUEN, "Senden ok")),
                     behebe="strom_neu" if "senden_abgelehnt" in z.probleme else None, piepen="senden_abgelehnt" in z.probleme))
    erg.append(Lampe("kamera", NAMEN["kamera"], *((ROT, "Kamera meldet einen Fehler") if z.kamera == "fehler" else (GRUEN, {"ein": "läuft", "startet": "startet", "aus": "aus"}.get(z.kamera, z.kamera)))))
    if z.aufnahme is not None:
        farbe, wort, behebe = AUFNAHME_LAMPE.get(z.aufnahme, AUFNAHME_LAMPE["unbekannt"])
        erg.append(Lampe("aufnahme", NAMEN["aufnahme"], farbe, wort, behebe=behebe if farbe != GRUEN else None))
    else:
        erg.append(Lampe("aufnahme", NAMEN["aufnahme"], GRAU, "kein Ziel"))
    hand = haende_led(haende_an=z.haende_an, letztes=z.letztes)
    if hand.farbe == GRAU and z.haende_an and z.letztes is None:
        hand = Led("haende", GRUEN, "bereit, noch keine Aktion")  # keine Aktion ist kein Fehler und nicht "aus"
    elif hand.farbe == GRAU and z.haende_an:
        hand = Led("haende", GRUEN, "bereit")
    erg.append(_l("hand", hand))
    erg.append(dialog_lampe(z.dialog))
    for grund, name, farbe, behebe, frisch in HAENDE_GATES:
        if grund in ABGEDECKT_DURCH:
            continue
        alter = _grund(z, grund)
        aktiv = alter is not None and alter <= frisch
        blinkt = aktiv and farbe == ROT and alter <= BLINKEN_NACH_FEHLER_S
        erg.append(Lampe(f"gate:{grund}", name, farbe if aktiv else GRUEN, f"abgelehnt: {grund}" if aktiv else "in Ordnung", blinkt=blinkt,
                         behebe=behebe if aktiv else None, piepen=blinkt))
    for grund, name, farbe in RAUTE_GATES:
        alter = _grund(z, f"raute:{grund}")
        aktiv = alter is not None and alter <= FRISCH_GRUND_S
        blinkt = aktiv and farbe == ROT and alter <= BLINKEN_NACH_FEHLER_S
        erg.append(Lampe(f"raute:{grund}", name, farbe if aktiv else GRUEN, f"fehlgeschlagen: {grund}" if aktiv else "in Ordnung", blinkt=blinkt, piepen=blinkt))
    if z.ziel_zustand is not None:
        farbe, wort, behebe = ZIEL_ZUSTAND_LAMPE.get(z.ziel_zustand, ZIEL_ZUSTAND_LAMPE["unbekannt"])
        erg.append(Lampe("zustand", NAMEN["zustand"], farbe, wort, blinkt=farbe == ROT, behebe=behebe if farbe != GRUEN else None, piepen=farbe == ROT))
    else:
        erg.append(Lampe("zustand", NAMEN["zustand"], GRAU, "kein Ziel"))
    if z.fenster_weg:
        erg.append(Lampe("bind", NAMEN["bind"], ROT, "gebundenes Fenster ist weg", blinkt=True, behebe="desktop_binden", piepen=True))
    else:
        erg.append(Lampe("bind", NAMEN["bind"], GRUEN, z.ziel_text.removeprefix("Ziel: ").strip()[:30] or "ganzer Desktop"))
    weg = z.fenster_weg or (_grund(z, "ziel_weg") is not None and _grund(z, "ziel_weg") <= FRISCH_GRUND_S)
    erg.append(Lampe("weg", NAMEN["weg"], *((ROT, "Fenster weg") if weg else (GRUEN, "da")), blinkt=weg, behebe="desktop_binden" if weg else None, piepen=weg))
    erg.append(Lampe("auss", NAMEN["auss"], *((ROT, "ragt aus dem Bildschirm") if z.terminal_draussen else (GRUEN, "im Bildschirm")),
                     blinkt=z.terminal_draussen, behebe="terminal_holen" if z.terminal_draussen else None, piepen=z.terminal_draussen))
    ao = z.anzeigeort_grund
    erg.append(Lampe("anzeigeort", NAMEN["anzeigeort"], *((GELB, f"abgelehnt: {ao[0]}") if ao and ao[1] <= FRISCH_GRUND_S else (GRUEN, "in Ordnung"))))
    erg.append(Lampe("verb", NAMEN["verb"], *((GRUEN, "verbunden") if z.verbunden else (ROT, "keine Verbindung")), blinkt=not z.verbunden, piepen=not z.verbunden))
    erg.append(Lampe("nota", NAMEN["nota"], *((ROT, "aktiv") if z.gesperrt else (GRUEN, "frei")), blinkt=z.gesperrt))
    for art, ergebnis in sorted((z.haende_arten or {}).items()):
        erg.append(_haende_lampe(f"art:{art}", f"Hände: {HAENDE_ARTEN.get(art, art.capitalize())}", ergebnis))
    for ziel, ergebnis in sorted((z.haende_ziele or {}).items()):
        erg.append(_haende_lampe(f"ziel:{ziel}", f"Hände in {ziel}", ergebnis))
    return erg


def roter_text(name: str, lampe: Lampe) -> str:
    """Eine Chatzeile für eine rote Lampe: wer, welche Funktion, was los ist und was ein Klick beheben würde."""
    text = f"⚠ [{name}] {lampe.name}: {lampe.wort}"
    if lampe.behebe:
        text += f" (Ampel-Knopf: {AKTIONS_TEXT.get(lampe.behebe, lampe.behebe)})"
    return text


def menue_zeile(lampe: Lampe) -> str:
    """Eine Zeile im Rechtsklick-Menü: die Funktion ausgeschrieben, dahinter in Klammern, wie es ihr geht."""
    if lampe.farbe == GRUEN:
        return f"{lampe.name} (läuft)"
    return f"{lampe.name} ({lampe.zustandswort}: {lampe.wort})"


GRUPPEN = (("augen", "Augen", ("bild", "strom", "sicht", "aufnahme", "aufn", "ausschnitt", "send", "kamera")),
           ("haende", "Hände", ("hand", "dialog")),
           ("ziel", "Ziel", ("zustand", "bind", "weg", "auss", "anzeigeort", "verb", "nota")))
GRUPPEN_ERKLAERUNG = {"augen": "Kommen Bilder des Ziels beim Agenten an?", "haende": "Kann der Agent klicken und tippen?",
                      "ziel": "Ist das Fenster des Agenten da, sichtbar, im Bildschirm und die Bridge verbunden?"}


def gruppe_von(kennung: str) -> str:
    """Zu welcher der drei Lampen eine Funktion gehört; Hände je Aktionsart und Programm gehören zu den Händen."""
    for gruppe, _n, mitglieder in GRUPPEN:
        if kennung in mitglieder:
            return gruppe
    return "haende" if kennung.startswith(("art:", "ziel:", "gate:", "raute:")) else "ziel"


def drei_lampen(lampen_liste: list[Lampe]) -> list[Lampe]:
    """Die drei Sammellampen Augen, Hände, Ziel: jede zeigt das Schlimmste ihrer Gruppe (Rot vor Orange vor Grau vor Blau)."""
    rang = {ROT: 0, GELB: 1, GRAU: 2, GRUEN: 3}
    erg = []
    for gruppe, name, _m in GRUPPEN:
        teile = [l for l in lampen_liste if gruppe_von(l.kennung) == gruppe]
        if not teile:
            continue
        schlimm = min(teile, key=lambda l: rang.get(l.farbe, 3))
        kaputt = sum(1 for l in teile if l.farbe in (ROT, GELB))
        wort = schlimm.wort if schlimm.farbe != GRUEN else "alles läuft"
        if kaputt > 1:
            wort += f" (+{kaputt - 1} weitere)"
        erg.append(Lampe(gruppe, name, schlimm.farbe, wort, schlimm.blinkt, schlimm.behebe, schlimm.piepen))
    return erg


def menue_gruppen(lampen_liste: list[Lampe]):
    """Für das Rechtsklick-Menü: je Gruppe Überschrift mit Erklärung, darunter alle Funktionen mit Zustand in Klammern."""
    for gruppe, name, _m in GRUPPEN:
        teile = [l for l in lampen_liste if gruppe_von(l.kennung) == gruppe]
        if teile:
            yield f"{name}: {GRUPPEN_ERKLAERUNG[gruppe]}", teile


def schlimmste(lampen_liste: list[Lampe]) -> str:
    """Die Farbe der ganzen Fläche: das Schlimmste gewinnt (Rot vor Orange vor Grau vor Blau/Grün)."""
    farben = {l.farbe for l in lampen_liste}
    for f in (ROT, GELB):
        if f in farben:
            return f
    return GRUEN


def chat_meldungen(vorher_rot: dict, zeiten: dict, jetzt: float, agent: str, lampen_liste: list[Lampe], *, takt_s: float = 20.0,
                   max_zeilen: int = 3) -> tuple[list[str], dict, dict]:
    """Dauerfeuer in den Chat, solange etwas rot ist, höchstens `max_zeilen` je Aufruf; einmal „wieder ok“, wenn es behoben ist.

    `vorher_rot`: (Agent, Lampe) → Wort; `zeiten`: (Agent, Lampe) → Zeit der letzten Meldung. Gibt (Zeilen, neu_rot, neue_zeiten) zurück."""
    zeilen: list[str] = []
    neu_rot = {k: v for k, v in vorher_rot.items() if k[0] != agent}
    neue_zeiten = dict(zeiten)
    for lampe in lampen_liste:
        schluessel = (agent, lampe.kennung)
        if lampe.farbe == ROT:
            neu_rot[schluessel] = lampe.wort
            if len(zeilen) < max_zeilen and jetzt - zeiten.get(schluessel, -1e9) >= takt_s:
                zeilen.append(roter_text(agent, lampe))
                neue_zeiten[schluessel] = jetzt
        elif schluessel in vorher_rot:
            zeilen.append(f"✓ [{agent}] {lampe.name}: wieder in Ordnung")
            neue_zeiten.pop(schluessel, None)
    return zeilen, neu_rot, neue_zeiten
