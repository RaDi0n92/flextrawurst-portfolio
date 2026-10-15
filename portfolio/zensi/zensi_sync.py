#!/usr/bin/env python3
"""
zensi_sync.py — Auto-Sync Daemon für Zensi Kopienprofile & Sandbox-Fläche.

Verwaltet live-aktualisierte Klonstrukturen und isolierte Sandboxen für alle Wesen:
- Klonstruktur (/root/zensi/wesensprofile/<wesen_id>/klon/): wird kontinuierlich synchronisiert
- Sandbox-Fläche (/root/zensi/wesensprofile/<wesen_id>/sandbox/): wird synchronisiert,
  ES SEI DENN, sandbox_pausiert.flag existiert!
"""

import os
import sys
import time
import shutil
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="[zensi-sync %(asctime)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S"
)

PROFILE_BASE = Path("/root/zensi/wesensprofile")
PROFILE_BASE.mkdir(parents=True, exist_ok=True)

QUELL_PFADE = [
    Path("/root/werkraum/codewesen"),
    Path("/root/werkraum/geni"),
    Path("/root/werkraum/solarius"),
    Path("/root/werkraum/codexium")
]

IGNORIERTE_MUSTER = {".git", "__pycache__", "*.pyc", ".DS_Store"}


def entdecke_wesen_quellen() -> dict[str, Path]:
    """Findet alle aktiven Wesen-Quellordner."""
    quellen = {}
    
    # 1. Codewesen (namelessAI_* & dak+gord-system)
    cw_dir = Path("/root/werkraum/codewesen")
    if cw_dir.exists():
        for d in cw_dir.iterdir():
            if d.is_dir() and not d.name.startswith("."):
                quellen[d.name] = d
                
    # 2. GENI
    geni_dir = Path("/root/werkraum/geni")
    if geni_dir.exists():
        quellen["GENI"] = geni_dir
        
    # 3. SolariUS Spawner
    sol_dir = Path("/root/werkraum/solarius")
    if sol_dir.exists():
        for d in sol_dir.iterdir():
            if d.is_dir() and not d.name.startswith("."):
                quellen[f"solarius_{d.name}"] = d

    # 4. Codexium Spawner
    cod_dir = Path("/root/werkraum/codexium")
    if cod_dir.exists():
        for d in cod_dir.iterdir():
            if d.is_dir() and not d.name.startswith("."):
                quellen[f"codexium_{d.name}"] = d
                
    return quellen


def kopiere_baum(src: Path, dst: Path):
    """Kopiert Verzeichnisbaum unter Ausschluss temporärer Dateien."""
    dst.mkdir(parents=True, exist_ok=True)
    
    for item in src.iterdir():
        if item.name in IGNORIERTE_MUSTER or item.name.startswith("."):
            continue
        target = dst / item.name
        if item.is_dir():
            kopiere_baum(item, target)
        else:
            # Nur kopieren wenn neu oder geändert
            if not target.exists() or item.stat().st_mtime > target.stat().st_mtime:
                shutil.copy2(item, target)


def sync_wesen(wesen_id: str, src_path: Path):
    """Synchronisiert Klon und (falls nicht pausiert) Sandbox eines Wesens."""
    wesen_dir = PROFILE_BASE / wesen_id
    klon_dir = wesen_dir / "klon"
    sandbox_dir = wesen_dir / "sandbox"
    pause_flag = wesen_dir / "sandbox_pausiert.flag"
    
    klon_dir.mkdir(parents=True, exist_ok=True)
    sandbox_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Sync Quelle -> Klon
    try:
        kopiere_baum(src_path, klon_dir)
    except Exception as e:
        logging.error(f"Fehler beim Sync von {wesen_id} Klon: {e}")
        
    # 2. Sync Klon -> Sandbox (nur wenn NICHT pausiert)
    if pause_flag.exists():
        logging.debug(f"Sandbox für {wesen_id} ist PAUSIERT — Sync übersprungen.")
    else:
        try:
            kopiere_baum(klon_dir, sandbox_dir)
        except Exception as e:
            logging.error(f"Fehler beim Sync von {wesen_id} Sandbox: {e}")


def sync_alle_wesen():
    """Führt einen vollen Sync-Durchlauf für alle entdeckten Wesen aus."""
    quellen = entdecke_wesen_quellen()
    for wesen_id, src_path in quellen.items():
        sync_wesen(wesen_id, src_path)


def main():
    loop = "--loop" in sys.argv
    takt = 10
    
    logging.info(f"Start zensi_sync.py (Loop: {loop}, Intervall: {takt}s)")
    
    while True:
        sync_alle_wesen()
        if not loop:
            break
        time.sleep(takt)


if __name__ == "__main__":
    main()
