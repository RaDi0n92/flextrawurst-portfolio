#!/usr/bin/env python3
"""Loescht alle Ordner/Unterordner in einem Wesen-Vault, verschiebt alle Dateien
an die Wurzel. Kollisionssicher: bei gleichem Dateinamen wird der relative
Pfad (mit '__' statt '/') vorangestellt, nie stillschweigend ueberschrieben.

2026-08-14, Daniel woertlich: "so und nun loesche aus alldiesen valuls von ihnen
alle ordner und unterordner aber lass alle dateien da". Vorher IMMER ein Backup
(wesen_vaults_backup_vor_flach_2026-08-14/), gleiche Konvention wie schon am
13.08. bei der letzten Vault-Aufraeumung.

Aufruf: python3 vault_flach_machen.py <vault_pfad>
"""
import sys
import shutil
from pathlib import Path


def eindeutiger_zielname(wurzel: Path, rel_pfad: Path, belegt: set) -> str:
    name = rel_pfad.name
    if name not in belegt and not (wurzel / name).exists():
        return name
    # Kollision: relativen Ordnerpfad als Praefix, mit __ statt /
    praefix = "__".join(rel_pfad.parent.parts)
    kandidat = f"{praefix}__{name}" if praefix else name
    if kandidat not in belegt and not (wurzel / kandidat).exists():
        return kandidat
    # Immer noch belegt (sehr selten) -- Zaehler anhaengen
    stamm, punkt, ext = kandidat.rpartition(".")
    i = 2
    while True:
        variante = f"{stamm}_{i}.{ext}" if punkt else f"{kandidat}_{i}"
        if variante not in belegt and not (wurzel / variante).exists():
            return variante
        i += 1


def flach_machen(vault: Path) -> list[tuple[str, str]]:
    if not vault.is_dir():
        raise SystemExit(f"kein Verzeichnis: {vault}")

    alle_dateien = [p for p in vault.rglob("*") if p.is_file()]
    belegt = {p.name for p in vault.iterdir() if p.is_file()}
    verschoben = []

    for datei in alle_dateien:
        rel = datei.relative_to(vault)
        if len(rel.parts) == 1:
            continue  # liegt schon in der Wurzel
        ziel_name = eindeutiger_zielname(vault, rel, belegt)
        ziel = vault / ziel_name
        shutil.move(str(datei), str(ziel))
        belegt.add(ziel_name)
        verschoben.append((str(rel), ziel_name))

    # Alle jetzt leeren Unterordner entfernen, tiefste zuerst
    ordner = sorted([p for p in vault.rglob("*") if p.is_dir()],
                     key=lambda p: len(p.parts), reverse=True)
    entfernt = 0
    for o in ordner:
        try:
            o.rmdir()
            entfernt += 1
        except OSError as e:
            print(f"  WARNUNG: {o} nicht leer/nicht entfernbar: {e}")

    print(f"{vault.name}: {len(verschoben)} Dateien verschoben, {entfernt} Ordner entfernt")
    return verschoben


if __name__ == "__main__":
    vault_pfad = Path(sys.argv[1])
    protokoll = flach_machen(vault_pfad)
    umbenannt = [(a, b) for a, b in protokoll if Path(a).name != b]
    if umbenannt:
        print(f"  davon {len(umbenannt)} umbenannt wegen Namenskollision:")
        for a, b in umbenannt:
            print(f"    {a}  ->  {b}")
