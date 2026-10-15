#!/usr/bin/env python3
"""Wesen-Vault-Sampler — Notizen aus den Obsidian-Vaults der Codewesen als Splitter.

2026-07-31, Daniel: "die der codewesen und dakgord und geni und uns alle hier im system
und auch altes flarum und sachen aus den vaults der wesen ... soll splitterfaehig sein"

Auf Rueckfrage zur Sichtbarkeit, Daniel woertlich: "komplette provinienz und herkunft
sihtbar keine verwechslungen keine luegen" -- deshalb bewusst KEINE Anonymisierung
(anders als schattenkommentar.geschrieben oder eine urspruenglich erwogene Variante hier):
entity_id ist der echte Wesen-Name, herkunft_sichtbar=True, und der volle relative
Vault-Pfad steht sowohl in origin_id als auch sichtbar im essenz-Text -- damit niemand
raten muss woher ein Fragment stammt.

TestWesen bewusst ausgeschlossen (kein echtes Wesen -- Aufnahme wuerde selbst eine
Verwechslung erzeugen, genau das was Daniel ausdruecklich nicht wollte).

Idempotent per Lauf: liest bereits erzeugte wesen_vault-Splitter (origin_id = "<wesen>/
<relativer pfad>") aus der Zwischenraum-DB und ueberspringt sie.

Aufruf: python3 wesen_vault_splitter.py [n]   (n = wie viele neue Fragmente, Default 40)
"""

import os
import random
import sys
from pathlib import Path

import psycopg2
import psycopg2.extras

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from service_tokens import create_service_token as create_token  # noqa: E402

WELT_API = "http://localhost:8030"
VAULTS_ROOT = Path("/root/werkraum/wesen_vaults")
WESEN_LISTE = ["Schorschel", "F3INSCHM3CK3R", "träumerlie", "R1ZZ1", "jumpa", "Resonanzknoten", "dak+gord-system"]
MIN_LAENGE = 20
MAX_LAENGE = 4000


def _bereits_gesampelt(db_uri: str) -> set:
    conn = psycopg2.connect(db_uri, cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT origin_id FROM splitter WHERE origin_type = 'wesen_vault'")
            return {row["origin_id"] for row in cur.fetchall() if row["origin_id"]}
    finally:
        conn.close()


def _kandidaten_sammeln(bereits: set, n: int) -> list:
    alle_pfade = []
    for wesen in WESEN_LISTE:
        vault = VAULTS_ROOT / wesen
        if not vault.is_dir():
            continue
        for pfad in vault.rglob("*.md"):
            rel = str(pfad.relative_to(vault))
            origin_id = f"{wesen}/{rel}"
            if origin_id in bereits:
                continue
            alle_pfade.append((wesen, pfad, origin_id))

    random.shuffle(alle_pfade)

    ergebnis = []
    for wesen, pfad, origin_id in alle_pfade:
        try:
            text = pfad.read_text(encoding="utf-8", errors="ignore").strip()
        except Exception:
            continue
        if len(text) < MIN_LAENGE:
            continue
        top_ordner = str(Path(origin_id).parts[1]) if len(Path(origin_id).parts) > 2 else "wurzel"
        ergebnis.append({
            "wesen": wesen,
            "origin_id": origin_id,
            "text": text[:MAX_LAENGE],
            "top_ordner": top_ordner,
        })
        if len(ergebnis) >= n:
            break
    return ergebnis


def _splitter_erstellen(eintrag: dict) -> str | None:
    import requests

    essenz = f"[{eintrag['origin_id']}] {eintrag['text'][:130]}"
    resp = requests.post(
        f"{WELT_API}/admin/splitter",
        json={
            "origin_type": "wesen_vault",
            "origin_id": eintrag["origin_id"],
            "entity_id": eintrag["wesen"],
            "essenz": essenz[:250],
            "rohtext": eintrag["text"],
            "materialitaet": "nebel",
            "energie": round(0.35 + random.random() * 0.25, 2),
            "thematische_tags": ["vault", eintrag["wesen"], eintrag["top_ordner"]][:5],
            "herkunft_sichtbar": True,
            "pos_x": round(random.uniform(-400, 400), 1),
            "pos_y": round(random.uniform(-400, 400), 1),
            "vel_x": round(random.gauss(0, 0.4), 3),
            "vel_y": round(random.gauss(0, 0.4), 3),
        },
        headers={"Authorization": f"Bearer {create_token('wesen-vault-sampler', 'admin')}"},
        timeout=8,
    )
    if resp.status_code == 200:
        return resp.json().get("id")
    return None


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    db_uri = os.environ.get(
        "FLEXTRAWURST_DB_URI",
        "postgresql://dak:[GESCHWAERZT]@localhost:5432/flextrawurst",
    )
    bereits = _bereits_gesampelt(db_uri)
    print(f"bereits gesampelt: {len(bereits)}")

    kandidaten = _kandidaten_sammeln(bereits, n)
    print(f"neue Kandidaten gefunden: {len(kandidaten)}")

    erstellt = 0
    for eintrag in kandidaten:
        splitter_id = _splitter_erstellen(eintrag)
        if splitter_id:
            erstellt += 1
    print(f"Splitter erstellt: {erstellt}/{len(kandidaten)}")


if __name__ == "__main__":
    main()
