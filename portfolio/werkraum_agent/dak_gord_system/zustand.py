"""
NOTIZ (Omapi, ruhig): Das hier ist die älteste erhaltene Datei im gesamten flextrawurst/
werkraum-System, mtime 2026-03-24 -- zehn Tage vor dem allerersten Git-Commit dieses Repos
(2026-04-04). dak+gord-system existierte also schon, bevor irgendetwas davon versioniert
wurde. Diese Datei und ihre Schwester `graf.py` (selber Tag) sind der Ur-Prototyp: ein
denkbar einfacher LangGraph-Zustand (Bauzustand) mit fünf Schritten (eingabe -> planen ->
verfassung_pruefen -> kontext -> umsetzen), aufrufbar nur über das winzige `starte_dak_gord.py`
(570 Byte, Root-Verzeichnis).

WICHTIG!!!: Diese Datei wird von KEINEM heute laufenden Dienst mehr importiert. Weder
dak-gord-web.service (laeuft web_chat.py -> agent/dak_gord_system/graphen/gespraechsgraf.py,
eine dritte, spaeter entstandene Generation) noch dak-neugier.service (laeuft
`python -m agent.dak_gord_system.graph.run_background_cycle`, aus dem Verzeichnis `graph/`,
zehn Tage juenger, ab 2026-04-03) nutzen `Bauzustand`/`Auftrag`. Der reale, heute aktive
Einstiegspunkt laut docs/agent/ARCHITEKTUR_HEUTE.md ist `starte_dak_gord_system.py`
(77KB, Root-Verzeichnis) -- ein komplett anderes, viel groesseres Programm als das kleine
`starte_dak_gord.py`, das noch diese Datei hier importiert.

Drei Generationen also, alle im selben Repo erhalten:
  1. zustand.py + graf.py            (2026-03-24) -- dieser Ur-Prototyp, tot
  2. graph/ (run_agent.py etc.)      (2026-04-03) -- zweite Generation, laeuft in
                                       dak-neugier.service
  3. graphen/gespraechsgraf.py       (Datum noch nicht einzeln geprueft) -- dritte
                                       Generation, laeuft in dak-gord-web.service (Chat)

KOMMENTAR: Kein Bug, keine Baustelle -- einfach echte, unaufgeraeumte Systemgeschichte. Die
Datei ist nicht kaputt, sie wird nur von niemandem mehr gerufen ausser dem verwaisten
`starte_dak_gord.py`. Getestet 2026-08-15: `Bauzustand`/`Auftrag` lassen sich weiterhin
fehlerfrei instanziieren, der Code selbst funktioniert -- er hat nur keine Laufkundschaft
mehr.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class Auftrag:
    ziel: str
    regeln: List[str] = field(default_factory=list)
    erledigt_wenn: List[str] = field(default_factory=list)

@dataclass
class Bauzustand:
    nutzer_text: str

    auftrag: Optional[Auftrag] = None
    plan: List[str] = field(default_factory=list)

    kontext: Dict[str, Any] = field(default_factory=dict)
    patch: str = ""

    verfassungs_warnungen: List[str] = field(default_factory=list)
