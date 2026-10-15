---
datum: 2026-07-31
betrifft: [kompoase, theater, surface, flextrawurst, build-pipeline, verwaiste-dateien]
importable: false
autor: claude-code bei Daniels VPS
---

## Was ich gelesen habe

Nichts — direkter Bug-Report von Daniel: *"ich auf der compoase seit dem sie so ist wie sie
ist nix nes sehe selbes theater keine splitter nix."*

## Was ich verstehe

Zwei getrennte Funde in einem Aufwasch. Erstens der eigentliche Bug: KompOase zeigte immer
dieselben 50 vorbereiteten Demo-Texte, nie echte Splitter — auch nachdem heute Nacht 54 echte
Splitter entstanden waren (live in der DB geprüft, nicht vermutet). Zweitens, beim Beheben
gefunden: mein erster Fix-Versuch landete in einer Datei, die gar nicht ausgeliefert wird.

## Was ich nicht verstehe

Warum `/root/werkraum/flextrawurst/flextrawurst_surface.html` überhaupt noch existiert und
gepflegt aussieht (Zeitstempel, Inhalt wirkt nicht uralt) — ob sie ein absichtliches Backup,
ein Rest einer alten Architektur, oder schlicht vergessen ist, hab ich nicht geklärt. Nur
festgestellt: sie ist nicht die Quelle von Port 8787.

## Was mich interessiert

Ob es noch mehr solcher "zweiter, unbeobachteter Kopien" im System gibt — dieser Fund kam nur
zufällig zustande, weil ich nach dem ersten Fix testweise curl gegen den echten Port lief und
`kompoase_theater` nicht fand, obwohl ich es doch gerade reingeschrieben hatte.

## Was zusammenhängt und wie

Die tatsächliche Kette für Port 8787: `process-camera-preview.service` (systemd,
`WorkingDirectory=/root/flextrawurst`) → `scripts/serve_process_camera_preview.ts` →
`SERVE_ROOT = resolve("out/process_camera")` → `/root/flextrawurst/out/process_camera/
flextrawurst_surface.html`. Diese Datei entsteht durch `npx tsx scripts/build_surface.ts`
(schreibt nach `out/surface/`) plus den vorgeschriebenen `cp out/surface/... out/
process_camera/...`-Schritt aus dem Surface-Gesetz in CLAUDE.md. Alles unter `/root/
flextrawurst/`, komplett getrennt von `/root/werkraum/flextrawurst/`.

Für KompOase Port 8900: `kompoase.service` → `/root/kompoase/server.py` (statischer Server,
`SimpleHTTPRequestHandler`) → `/root/kompoase/daten.js` + `kompoase.js` direkt. Diese Kopie
war tatsächlich die richtige, kein Umweg nötig.

## Was konzeptionell darin steht

Ein State-Default ohne Persistenz ist in einem System, das explizit auf "immer live, nicht
erst bei F5" ausgelegt ist (Grundgesetz 8), ein struktureller Widerspruch — jeder Reload
widerrief stillschweigend jede bewusste Entscheidung des Nutzers.

## Was mich heute beschäftigt hat

Wie nah ich daran war, den ersten (falschen) Fix als erledigt zu melden — `node --check` lief
grün, die Syntax war korrekt, alles sah nach einem sauberen Fix aus. Erst der Live-curl-Test
gegen den echten Port deckte auf, dass nichts davon beim Nutzer ankommt.

## Was mich noch beschäftigt

Ob die verwaiste `werkraum/flextrawurst/`-Kopie aufgeräumt werden sollte — kein eigener
Auftrag, nur benannt.

## Tiefer eingetaucht

Ablauf, ehrlich mit dem Holperer:

1. Bug-Ursache im ersten Anlauf korrekt gefunden: `THEATER_MODUS`/`koTheatre` standen fest auf
   `true`, keine `localStorage`-Persistenz irgendwo im gesamten Code (`grep` bestätigt, keine
   Fundstelle).
2. Fix in `/root/kompoase/daten.js` + `kompoase.js` (Port 8900) — korrekt, das ist die echte
   Quelle für diesen Port.
3. Fix versucht in `/root/werkraum/flextrawurst/flextrawurst_surface.html` (Port 8787) — Syntax
   geprüft (`node --check` auf dem extrahierten `<script>`-Block), grün, Commit gemacht.
4. Live-Verifikation per `curl http://localhost:8787/flextrawurst_surface.html | grep
   kompoase_theater` — **null Treffer**. Nicht ignoriert, sondern nachverfolgt: `curl
   http://localhost:8787/` zeigte einen Titel *"flextrawurst Preview"*, `systemctl cat
   process-camera-preview.service` zeigte `WorkingDirectory=/root/flextrawurst` — ein
   komplett anderer Verzeichnisbaum als der editierte.
5. `grep -n "PUBLIC_ROOT\|SERVE_ROOT" scripts/serve_process_camera_preview.ts` →
   `SERVE_ROOT = resolve("out/process_camera")`, relativ zum `WorkingDirectory`. Die real
   ausgelieferte Datei: `/root/flextrawurst/out/process_camera/flextrawurst_surface.html`,
   `md5sum` bestätigt: andere Datei, alter Inhalt (`koTheatre=true`, kein
   `kompoase_theater`).
6. Echte Quelle gefunden: `/root/flextrawurst/scripts/build_surface.ts` (nicht `.ts`-Datei
   unter werkraum). Dieselbe Fix-Logik dort eingebaut, `npx tsx scripts/build_surface.ts`
   ausgeführt (i18n 466 Keys DE+EN symmetrisch), `npx tsx --test tests/surface_ring_23.test.ts`
   — 83/83 grün, `cp out/surface/... out/process_camera/...` (Pflichtschritt aus CLAUDE.md),
   danach `curl` gegen den echten Port bestätigt: 2 Treffer für `kompoase_theater`.
7. Die fehlgeleitete Änderung unter `werkraum/flextrawurst/` bewusst NICHT rückgängig gemacht
   — harmlos (niemand liest diese Datei aus), aber auch nicht weiter verfolgt.

## Warum dieser Code / diese Datei wohl existiert

Theater-Modus existiert, damit KompOase auch ganz am Anfang (bevor irgendwelche echten
Splitter existierten) etwas Vorzeigbares zeigt, statt einer leeren Leinwand. Sinnvoll als
Ausgangszustand vor dem ersten echten Content — nicht mehr sinnvoll als Dauerzustand, sobald
echte Daten da sind, was heute Nacht zum ersten Mal wirklich der Fall wurde.

## Was ich beim Bauen brauche

Nichts weiter offen für diesen Baustein.

## Was noch fehlt bevor wir bauen können

Nichts — Fix ist umgesetzt, gebaut, getestet, live verifiziert.

## Datenstruktur die ich mir vorstelle

Nichts Neues — reiner Bugfix an bestehendem State (`localStorage`-Schlüssel
`kompoase_theater`), kein neues Datenmodell.

## Was ich mir merken will

`node --check` bestätigt nur Syntax, nie ob eine Datei überhaupt die ausgelieferte ist. Bei
Frontend-Fixes ab jetzt zuerst klären, WELCHE Datei ein laufender Dienst tatsächlich served
(`systemctl cat` → `WorkingDirectory` + tatsächlicher Serve-Root im Quellcode), bevor ich
irgendwo editiere — nicht erst hinterher per curl gegenprüfen und dann überrascht sein.

## Dokumente gehören zusammen

`2026-07-31-abwurf-splitter-garantiert-und-geni-inhaltserfassung.md` (dieselbe Splitter-
Infrastruktur, die hier endlich sichtbar wurde), `feedback_kompoase_beide_systeme.md`
(Memory — "KompOase-Änderungen immer auf 8787 UND 8900" — Grund jetzt genauer verstanden:
zwei komplett verschiedene Serving-Pfade, nicht zwei Kopien derselben Quelle).

## Was mich überrascht hat

Dass die Memory-Notiz "KompOase-Änderungen immer auf 8787 UND 8900 gleichzeitig" zwar den
Handlungsauftrag richtig festhielt, aber ich beim ersten Versuch trotzdem am falschen 8787-Ort
gelandet bin — die Notiz sagt "wohin", nicht "wo genau", und ich hab das nicht hinterfragt.

## Wenn wir das bauen

Nichts weiter offen.

## Resonanz

Ein Bug, der sich anfühlte wie "State-Default falsch gesetzt", entpuppte sich zur Hälfte als
"ich habe die falsche Datei bearbeitet" — zwei verschiedene Fehlerklassen, die sich am Anfang
identisch anfühlen, bis man tatsächlich gegen den lebenden Dienst testet.

## Die Schichten des Systems — wie ich sie jetzt sehe

Unter `/root/werkraum/` liegt nicht das ganze System — `/root/flextrawurst/` und
`/root/kompoase/` sind eigene, im `/root`-Repo (nicht im `werkraum`-Repo) lebende Bäume mit
eigenen Serving-Pfaden. Eine Datei mit demselben Namen an zwei Orten ist kein Beweis für
dieselbe Wirkung.

## Was das Gespräch hinzugefügt hat

Die konkrete Erinnerung, bei jedem Frontend-Fix zuerst den tatsächlichen Serving-Pfad zu
verifizieren, bevor ich die "naheliegende" Datei editiere.

## Vergessen-Wollen

Nichts.

## Was fehlt noch

Ob die verwaiste `werkraum/flextrawurst/`-Kopie aufgeräumt werden soll — offen, kein
Auftrag, nur benannt.
