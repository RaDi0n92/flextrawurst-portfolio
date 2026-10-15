# Bekannte Muster und Fehlformen

## Muster 1: Eine reine Suche blockiert die ganze Session

**Erkannt:** 26. Juli 2026

**Beleg:** Ein `assets.search` über sehr breite Wurzeln lief ungefähr 49 Minuten. Der Legacy-Wrapper hielt während des gesamten Werkzeugaufrufs die exklusive Session-Sperre. Alle weiteren Aufrufe derselben Session-ID liefen nach drei Sekunden in `HistoryBusyError`, obwohl sie nur lesen wollten.

**Ursache:**

- keine Unterscheidung zwischen Leser und Schreiber,
- Session-Sperre um die gesamte Werkzeuglaufzeit,
- rekursive Suche ohne Zeit- oder Scanbudget,
- teure vollständige Pfadprüfung vor dem billigen Dateinamenvergleich,
- überlappende Wurzeln konnten denselben Baum mehrfach erfassen.

**Gegenregel:** Reine Leser verwenden gemeinsame Lesesperren. Mutationen bleiben exklusiv. Rekursive Suchen besitzen Budgets und liefern Teilstände.

**Status:** [BESTÄTIGT] Seit 26. Juli 2026 produktiv behoben. Zwei reale HTTP-`assets.search`-Aufrufe derselben Session waren gleichzeitig als `running` mit `shared-read` in der Operation Registry sichtbar. Eine vollständige Nichttreffer-Suche über `/root/werkraum` prüfte 26.057 Dateien und 2.635 Ordner in 541 Millisekunden.

## Muster 2: Installierter Bestand wird mit verwendeter Fähigkeit verwechselt

**Erkannt:** 26. Juli 2026

**Beleg:** Unter `/root/.claude/skills/` liegen 2.257 `SKILL.md`-Dateien, obwohl Daniel bewusst vermutlich nur ungefähr zwanzig Installationen beauftragt hat. Mehrere Installationen waren große Pakete mit hunderten Einzel-Skills.

**Gegenregel:** Drei Zustände getrennt führen:

1. installiert,
2. beim Start oder in der Auswahl gesehen,
3. in einer realen Arbeit angewendet.

Ohne Nutzungsspur darf Zustand 1 nicht als Zustand 3 ausgegeben werden.

## Muster 3: Technische ID ersetzt menschenlesbare Orientierung

**Erkannt:** 26. Juli 2026

**Beleg:** Session- und Ereigniskörper waren technisch korrekt über IDs, Hashes und UUIDs auffindbar, aber für Daniel nur über lange Maschinenpfade zugänglich.

**Gegenregel:** Stabile technische Identitäten bleiben erhalten. Darüber liegen menschenlesbare Startpunkte, Karten, Titel, Alias- und Erlebnisansichten. Mensch und Maschine müssen nicht denselben Dateinamen ertragen.

## Pflege dieses Dokuments

Neue Muster werden nur mit realem Beleg, Datum und Gegenregel ergänzt. Ein einzelner Verdacht bleibt eine offene Frage und gehört zunächst nach [[FRAGEN]].
