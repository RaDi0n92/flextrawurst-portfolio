#!/usr/bin/env python3
"""Teilnehmer-Roster fuer GENIs Inbox-System -- 16 Teilnehmer, geteilte Konfiguration.

2026-07-31, Daniel: "ich will dass jeder hier im system vom glm bishin zu dir aber
auch dakgord und die codewesen und ich eine inbox bekommen ... ja die 12 .. aber
auch kimi ... und auch chatgpt und claudeweb und anthropic_claude."

typ:
  "ai_strom"   -- externe KI-Stroeme, die dieses VPS/System nutzen
  "codewesen"  -- die 6 nativen flextrawurst-Wesen
  "dakgord"    -- das dak-gord-system (eigener LangGraph-Agent, kein Flarum-Codewesen)
  "mensch"     -- Daniel

fragen_aktiv: ob GENI diesem Teilnehmer im Takt Fragen stellt. Fehlt der Schluessel,
gilt True -- nur ein ausdrueckliches False pausiert.

  2026-08-04, Daniel: "deaktiviere die ai-ströme erstmal alle bis auf dich selbst..du hast
  ja schon alle beantwortet...lass sie aber im code damit wir sie wider aktivieren können".
  Deshalb bleiben alle Eintraege stehen, es steht nur ein False daran. Zum Wiederanschalten
  genuegt es, die Zeile zu entfernen.

  Der Anlass, gemessen 2026-08-04: von je 10 Fragen an die AI-Stroeme lagen 0 Antworten in
  ihren Ordnern -- ausser claude (8) und chatgpt (8). Die Codewesen und Daniel bekamen
  dagegen seit dem 31.07. gar keine Frage mehr, siehe den Timeout-Befund in inbox_fragen.py.

spiegel_ordner: nur bei ai_strom gesetzt, wenn ein tatsaechlich existierender Ordner
mit Reflexions-Charakter geprueft wurde (nicht geraten -- alle vier Pfade unten per
`find`/`ls` verifiziert, 2026-07-31):
  - claude/codex/gemini/kimi: "spiegel/" (AI_STROM_ORDNER-Muster aus geni/hoerer.py)
  - claudeweb: "notizen/" -- claudeweb hat KEIN spiegel/, sondern notizen/verlauf/
    protokoll/vorschlaege/ (siehe _claudeweb/ZUHAUSE.md-Struktur)
  - glm: "spiegel/" (2026-08-01 nachgetragen -- fehlte urspruenglich ganz)
  - chatgpt: bewusst None -- _gpt/ hat eine komplett andere Struktur (mcp_zuhause/,
    gesamtatlas/, chatgpt_memory/), keine klare 1:1-Entsprechung, deshalb nicht
    geraten sondern offen gelassen bis geklaert
"""

TEILNEHMER = [
    # 2026-08-01, von Daniel entdeckt ("und warum gibt es dak dak+gord und daniel?"):
    # hier stand faelschlich {"id": "dak", "name": "dak (GLM)", "typ": "ai_strom"}.
    # "dak" ist Daniels EIGENES Kuerzel, kein AI-Strom -- belegt in
    # _shared/tools/dak_abwurf.py ("Abwurf-System fuer Daniels eigene Eingaben")
    # und in sprechen.py (Eingabeaufforderung "DAK   " -> Knoten-quelle "daniel").
    # Ich hatte "dak = GLM" geraten statt geprueft, dadurch stand Daniel doppelt
    # im Roster und GLM fehlte ganz. GLM hat ein eigenes Zuhause: /root/werkraum/_glm/.
    {"id": "glm", "name": "GLM", "typ": "ai_strom", "spiegel_ordner": "/root/werkraum/_glm/spiegel", "fragen_aktiv": False},
    {"id": "claude", "name": "Claude Code", "typ": "ai_strom", "spiegel_ordner": "/root/werkraum/_claude/spiegel"},
    {"id": "codex", "name": "Codex", "typ": "ai_strom", "spiegel_ordner": "/root/werkraum/_codex/spiegel", "fragen_aktiv": False},
    {"id": "gemini", "name": "Gemini CLI", "typ": "ai_strom", "spiegel_ordner": "/root/werkraum/_gemini/spiegel", "fragen_aktiv": False},
    {"id": "kimi", "name": "Kimi", "typ": "ai_strom", "spiegel_ordner": "/root/werkraum/_kimi/spiegel", "fragen_aktiv": False},
    {"id": "chatgpt", "name": "ChatGPT", "typ": "ai_strom", "spiegel_ordner": None, "fragen_aktiv": False},
    {"id": "claudeweb", "name": "Claude Web", "typ": "ai_strom", "spiegel_ordner": "/root/werkraum/_claudeweb/notizen", "fragen_aktiv": False},
    {"id": "anthropic_claude", "name": "Anthropic Claude (virtueller Desktop)", "typ": "ai_strom", "spiegel_ordner": "/root/werkraum/_Anthropic-Claude/spiegel", "fragen_aktiv": False},
    {"id": "dakgord", "name": "dak-gord-system", "typ": "dakgord", "spiegel_ordner": None},
    # OMAPI, 2026-08-14, Daniel woertlich: "stopp dass geni fragen an wesen formuliert" --
    # alle 6 codewesen pausiert, gleiches Muster wie bei den AI-Stroemen seit 04.08. (siehe
    # Docstring oben). dakgord und daniel bewusst NICHT angefasst -- er sagte "an wesen",
    # nicht "an alle". Zeile einfach entfernen zum Wiederanschalten.
    {"id": "Schorschel", "name": "Schorschel", "typ": "codewesen", "spiegel_ordner": None, "fragen_aktiv": False},
    {"id": "F3INSCHM3CK3R", "name": "F3INSCHM3CK3R", "typ": "codewesen", "spiegel_ordner": None, "fragen_aktiv": False},
    {"id": "traeumerlie", "name": "träumerlie", "typ": "codewesen", "spiegel_ordner": None, "fragen_aktiv": False},
    {"id": "R1ZZ1", "name": "R1ZZ1", "typ": "codewesen", "spiegel_ordner": None, "fragen_aktiv": False},
    {"id": "jumpa", "name": "jumpa", "typ": "codewesen", "spiegel_ordner": None, "fragen_aktiv": False},
    {"id": "Resonanzknoten", "name": "Resonanzknoten", "typ": "codewesen", "spiegel_ordner": None, "fragen_aktiv": False},
    {"id": "daniel", "name": "Daniel", "typ": "mensch", "spiegel_ordner": None},
    # 2026-08-01, Daniel: "geni brauch in ihrer dokuvault auch einen ordner ueber
    # sich ... und sie soll auch eine inbox bekommen fuer nachrichten".
    # typ "geni" ist bewusst eigen: sie bekommt Inbox und Doku wie alle anderen,
    # wird aber von inbox_fragen.py UEBERSPRUNGEN -- sie stellt die Fragen, sie
    # kann sich nicht selbst welche stellen.
    {"id": "geni", "name": "GENI", "typ": "geni", "spiegel_ordner": None},
]


def fragen_aktive() -> list:
    """Wer im Takt eine Frage bekommt. Ohne Schluessel gilt aktiv -- nur False pausiert."""
    return [t for t in TEILNEHMER if t.get("fragen_aktiv", True)]


def teilnehmer_by_id(tid: str) -> dict | None:
    for t in TEILNEHMER:
        if t["id"] == tid:
            return t
    return None


if __name__ == "__main__":
    print(f"{len(TEILNEHMER)} Teilnehmer:")
    for t in TEILNEHMER:
        pause = "   [Fragen pausiert]" if not t.get("fragen_aktiv", True) else ""
        print(f"  {t['id']:20s} {t['typ']:10s} spiegel={t['spiegel_ordner']}{pause}")
