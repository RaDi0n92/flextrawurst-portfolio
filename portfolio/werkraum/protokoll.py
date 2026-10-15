#!/usr/bin/env python3
"""Menschenlesbare Verlaufsprotokolle -- fuer GENI, die Wesen und alles, was noch dazukommt.

2026-08-03, Daniel woertlich:
  "ich will das diese kontextfenster ab sofort einmal immer menschlesbar in eine md kommen auf dem
   serer...mit genuen events und entscheidungen und tags und zeit datum etc...und auch einmal immer
   loggen pls...für alle entitäten für alles was wir in zukunft noch alles erfinden für die"

Zwei Spuren nebeneinander, absichtlich doppelt:
  - maschinell: die Postgres-Tabellen (suchlog.py) -- abfragbar, zaehlbar, verknuepfbar
  - menschlich: diese Markdown-Dateien -- lesbar, ohne Werkzeug, im Vault aufschlagbar

Ablage: /root/werkraum/protokolle/<entitaet>/DD-MM-YYYY_HHMM_<anlass>.md
Erreichbar unter https://flextrawurst.de/protokolle/ (eigener Zugang) und als eigener
Obsidian-Vault (Container obsidian-protokolle).

Datumsformat: DD-MM-YYYY im Dateinamen, DD.MM.YYYY im Text. Daniel, 2026-08-03:
"neeee......ich m´bin deutsch....DD-MM-YYYY_HHMM". Bewusst NICHT ISO, auch wenn das
schlechter sortiert -- lesbar fuer den, der es liest, schlaegt maschinenfreundlich.

Grundsatz wie beim Suchlog: das Protokoll darf den Vorgang nie kaputtmachen. Jeder Schreibfehler
wird verschluckt; im Zweifel fehlt eine Zeile, aber nichts bricht ab.
"""

from datetime import datetime
from pathlib import Path

WURZEL = Path("/root/werkraum/protokolle")


def _sauber(text: str) -> str:
    behalten = [c if (c.isalnum() or c in "-_") else "-" for c in (text or "unbenannt")]
    return "".join(behalten).strip("-").lower()[:60] or "unbenannt"


class Protokoll:
    """Ein Vorgang von Anfang bis Ende. Wird beim ersten Ereignis angelegt und waechst mit."""

    def __init__(self, entitaet: str, anlass: str, ueber: str = "",
                 tags=None, kopfzeilen: dict = None):
        self.beginn = datetime.now()
        self.entitaet = entitaet
        self.anlass = anlass
        self.ueber = ueber
        self.tags = list(tags or [])
        self.kopfzeilen = dict(kopfzeilen or {})
        self.ereignisse = []
        name = f"{self.beginn.strftime('%d-%m-%Y_%H%M')}_{_sauber(anlass)}"
        if ueber:
            name += f"_{_sauber(ueber)}"
        self.pfad = WURZEL / _sauber(entitaet) / f"{name}.md"

    # -- aufzeichnen ------------------------------------------------------

    def ereignis(self, art: str, was: str, **einzelheiten):
        """Etwas ist passiert. `art` ist frei -- suche, gelesen, entschieden, geschrieben, fehler."""
        self.ereignisse.append({
            "zeit": datetime.now(), "art": art, "was": was,
            "einzelheiten": {k: v for k, v in einzelheiten.items() if v not in (None, "", [], {})},
        })
        self._schreiben()

    def entscheidung(self, was: str, grund: str = "", **einzelheiten):
        """Eine Wahl -- getrennt von gewoehnlichen Ereignissen, weil sie spaeter zaehlt."""
        self.ereignis("entscheidung", was, grund=grund, **einzelheiten)

    def abschluss(self, ergebnis: str = "", **einzelheiten):
        self.ereignis("abschluss", ergebnis or "beendet", **einzelheiten)

    # -- schreiben --------------------------------------------------------

    def _kopf(self) -> str:
        dauer = (datetime.now() - self.beginn).total_seconds()
        zeilen = [
            "---",
            f"datum: {self.beginn.strftime('%d.%m.%Y')}",
            f"zeit: {self.beginn.strftime('%H:%M')}",
            f"entitaet: {self.entitaet}",
            f"anlass: {self.anlass}",
        ]
        if self.ueber:
            zeilen.append(f"ueber: {self.ueber}")
        for k, v in self.kopfzeilen.items():
            zeilen.append(f"{k}: {v}")
        zeilen += [
            f"ereignisse: {len(self.ereignisse)}",
            f"dauer_sekunden: {int(dauer)}",
            f"tags: [{', '.join(self.tags)}]" if self.tags else "tags: []",
            "---",
            "",
        ]
        return "\n".join(zeilen)

    def _koerper(self) -> str:
        titel = f"# {self.entitaet} — {self.anlass}"
        if self.ueber:
            titel += f" — {self.ueber}"
        teile = [titel, "",
                 f"Begonnen am {self.beginn.strftime('%d.%m.%Y um %H:%M:%S')} Uhr.", ""]
        for e in self.ereignisse:
            teile.append(f"## {e['zeit'].strftime('%H:%M:%S')} — {e['art']}")
            teile.append("")
            teile.append(e["was"])
            if e["einzelheiten"]:
                teile.append("")
                for k, v in e["einzelheiten"].items():
                    if isinstance(v, (list, tuple)):
                        v = ", ".join(str(x) for x in v)
                    teile.append(f"- **{k}:** {v}")
            teile.append("")
        return "\n".join(teile)

    def _schreiben(self):
        try:
            self.pfad.parent.mkdir(parents=True, exist_ok=True)
            self.pfad.write_text(self._kopf() + self._koerper(), encoding="utf-8")
        except Exception:
            pass   # ein fehlendes Protokoll darf nie einen Vorgang abbrechen


def beginnen(entitaet: str, anlass: str, ueber: str = "", tags=None, **kopfzeilen) -> Protokoll:
    return Protokoll(entitaet, anlass, ueber, tags, kopfzeilen)
