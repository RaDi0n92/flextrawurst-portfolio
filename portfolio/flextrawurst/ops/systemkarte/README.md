# Systemkarte — Quellen der zwölf Diagramme

Dieser Ordner enthält, woraus die Diagramme im Tab SYSTEMKARTE entstehen. Doku zum Tab:
`/root/werkraum/docs/systemdoku/81_systemkarte_tab.md`.

## Dateien

- `build_i18n.py` — beschreibt sechs Diagramme (Knoten, Pfeile, Karten) in Deutsch und Englisch.
  Aufruf `python3 build_i18n.py de` und `... en`, schreibt nach `cand/<sprache>/<slug>/`.
  Texte stehen als `T("deutsch", "english")`. Pro Diagramm eine Darstellungs-Vorlage und eine
  Unterzeile (Tabellen `PRESET` und `SUB` oben in der Datei).
- `merge_manifest.py` — fügt die Manifeste zu `i18n/systemkarte.json` zusammen.
- `regenerate.sh` — die ganze Kette: erzeugen, mit Archify prüfen und rendern, nach `public/` legen.

## Neu erzeugen

```bash
git clone https://github.com/tt-a1i/archify     # MIT-Lizenz; verwendet wurde Stand d5a1333
ARCHIFY_DIR=/pfad/zu/archify/archify ./regenerate.sh
cd /root/flextrawurst && npx tsx scripts/build_surface.ts && npx tsx --test tests/surface_ring_23.test.ts
```

Der Lauf bricht ab, wenn ein Diagramm die Archify-Prüfung nicht besteht.

## Grenzen, die beim Ändern zählen

- Breite höchstens 1240 px, sonst schrumpft die Schrift unter die Lesbarkeitsgrenze. Deshalb nur
  wenige waagerechte Pfeil-Beschriftungen im Gesamtbild.
- Ein Knoten braucht je nach Breite eine kurze Unterzeile (bei 120 px etwa 20 Zeichen).
- Inhalte, die öffentlich stehen dürfen: keine Zugangs-Hinweise (Crawler-Schlüssel, Passwörter).
  Ein Test in `tests/surface_ring_23.test.ts` prüft die zwölf Dateien darauf.
- Stand der Inhalte ist der Tag der Erzeugung (im Titel: 2026-10-01). Beim Neuerzeugen den Stand
  in `build_i18n.py` und `merge_manifest.py` (`STAND`) anpassen und die Zahlen neu abfragen.
