#!/usr/bin/env python3
"""
Abwurf-System für Daniels eigene Eingaben (dak_abwurf) — ohne Ollama.

Aufgerufen von mehreren AI-Strömen aus ihrem jeweiligen "UserPromptSubmit"-artigen
Hook (Claude Code: UserPromptSubmit, Codex: UserPromptSubmit, Gemini CLI: BeforeAgent) --
liegt deshalb bewusst in _shared/tools/, nicht unter einem einzelnen Strom-Ordner.

2026-07-30, Daniel: "Jede Eingabe, wie log_user.sh" -- gleiche Klassifikations-Heuristik
wie claude_abwurf.py, nur ausgeloest am Eingabe-Zeitpunkt statt am Antwort-Zeitpunkt, und
mit Daniels eigenem origin_type/entity_id statt dem jeweiligen AI-Stroms.

2026-07-31, Daniel: "splitter duerfen auch nur aus einem wort sein" -- Wahrscheinlichkeitsfilter
komplett entfernt (siehe welt-api-Commit vom selben Tag), MIN_LAENGE auf 1 gesenkt. Nur noch
leerer/reiner Whitespace-Text wird verworfen, alles andere wird garantiert zum Splitter.

Erwartet auf stdin ein JSON mit einem Text-Feld -- der Feldname unterscheidet sich pro
Aufrufer (Claude Code/Codex: "prompt", Gemini CLI BeforeAgent: ebenfalls "prompt" laut
Referenz-Doku) -- daher wird zuerst "prompt", dann "text" als Fallback versucht.
"""

import json
import random
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, "/root/werkraum/welt")

import requests
from service_tokens import create_service_token as create_token

WELT_API     = "http://localhost:8030"
ABWUERFE_LOG = Path("/root/werkraum/_shared/dak_abwuerfe.md")
MIN_LAENGE   = 1
MAX_LAENGE   = 22222

MATERIALITAET_MAP = {
    "widerspruch":  "lava",
    "tiefe":        "wasser",
    "offene_frage": "nebel",
    "erkenntnis":   "sternenstaub",
    "erschoepfung": "gestein",
    "freude":       "gras",
}

SIGNALE = {
    "widerspruch": [
        "aber ", "allerdings", "jedoch", "widerspruch", "gegensatz", "spannung",
        "einerseits", "andererseits", "obwohl", "trotzdem", "konflik",
    ],
    "erkenntnis": [
        "erkenntnis", "verstanden", "interessant", "faszinierend", "genau das",
        "aha", "jetzt klar", "das zeigt", "das bedeutet", "entdeckt",
    ],
    "offene_frage": [
        "unklar", "offen bleibt", "weiß nicht", "noch nicht", "fraglich",
        "offene frage", "ungelöst", "würde mich interessieren",
    ],
    "tiefe": [
        "tief", "verbindung", "resonanz", "eingetaucht", "berührt",
        "das trägt", "das lebt", "wirklich", "echte", "kern",
    ],
    "erschoepfung": [
        "komplex", "aufwendig", "schwierig", "viele teile", "viele ebenen",
        "langer weg", "viel zu beachten", "nicht einfach",
    ],
    "freude": [
        "schön", "toll", "freude", "spaß", "elegant", "gefällt mir",
        "genial", "das macht freude", "schöner ansatz", "cool",
    ],
}


def _klassifiziere(text: str) -> tuple[str, float, str, list]:
    lower = text.lower()

    treffer: dict[str, int] = {k: 0 for k in SIGNALE}
    for art, signalwörter in SIGNALE.items():
        for w in signalwörter:
            treffer[art] += lower.count(w)

    verarbeitungsart = max(treffer, key=lambda k: treffer[k])
    if treffer[verarbeitungsart] == 0:
        verarbeitungsart = "offene_frage"

    laenge_score  = min(1.0, len(text) / MAX_LAENGE)
    signal_gesamt = sum(treffer.values())
    signal_score  = min(1.0, signal_gesamt / 8)
    intensitaet   = round(0.3 + (laenge_score * 0.4) + (signal_score * 0.3), 2)
    intensitaet   = min(1.0, intensitaet)

    saetze = re.split(r'[.!?]\s+', text.strip())
    essenz = next((s.strip() for s in saetze if len(s.strip()) > 20), text[:80])
    essenz = essenz[:100]

    sortiert = sorted(treffer, key=lambda k: treffer[k], reverse=True)
    tags = [sortiert[0]] if treffer[sortiert[0]] > 0 else []
    if len(sortiert) > 1 and treffer[sortiert[1]] > 0:
        tags.append(sortiert[1])

    return verarbeitungsart, intensitaet, essenz, tags


def _admin_token() -> str:
    return create_token("dak-abwurf", "admin")


def _erstelle_splitter(essenz: str, rohtext: str, materialitaet: str, tags: list, intensitaet: float):
    try:
        resp = requests.post(
            f"{WELT_API}/admin/splitter",
            json={
                "origin_type":       "dak_abwurf",
                "entity_id":         "dak",
                "essenz":            essenz[:200],
                "rohtext":           rohtext,
                "materialitaet":     materialitaet,
                "energie":           round(0.4 + intensitaet * 0.6, 2),
                "thematische_tags":  tags[:5],
                "herkunft_sichtbar": True,
                "pos_x": round(random.uniform(-400, 400), 1),
                "pos_y": round(random.uniform(-400, 400), 1),
                "vel_x": round(random.gauss(0, 1.0), 3),
                "vel_y": round(random.gauss(0, 1.0), 3),
            },
            headers={"Authorization": f"Bearer {_admin_token()}"},
            timeout=5,
        )
        if resp.status_code == 200:
            return resp.json().get("id")
    except Exception:
        pass
    return None


def _notiere(essenz: str, materialitaet: str, intensitaet: float, quelle: str):
    if not ABWUERFE_LOG.exists():
        ABWUERFE_LOG.write_text(
            "# Daniels Abwürfe\n\nSeine Eingaben, die einen Splitter im Zwischenraum "
            "hinterlassen haben — aus jedem AI-Strom heraus, den er gerade nutzt.\n\n",
            encoding="utf-8",
        )
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(ABWUERFE_LOG, "a", encoding="utf-8") as f:
        f.write(f"- [{ts}] **{materialitaet}** (i={intensitaet:.2f}, via {quelle}) → Zwischenraum: »{essenz}«\n")


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return

    text = (data.get("prompt") or data.get("text") or "").strip()[:MAX_LAENGE]
    quelle = data.get("hook_event_name") or data.get("session_id") or "unbekannt"
    if len(text) < MIN_LAENGE:
        return

    verarbeitungsart, intensitaet, essenz, tags = _klassifiziere(text)

    materialitaet = MATERIALITAET_MAP[verarbeitungsart]
    splitter_id = _erstelle_splitter(essenz, text, materialitaet, tags, intensitaet)
    if splitter_id:
        _notiere(essenz, materialitaet, intensitaet, str(quelle))


if __name__ == "__main__":
    main()
