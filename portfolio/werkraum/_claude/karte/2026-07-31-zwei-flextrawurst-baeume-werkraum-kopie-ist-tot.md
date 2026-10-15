---
datum: 2026-07-31
betrifft: [surface, build-workflow, provenienz, flextrawurst-baustruktur]
importable: false
autor: claude-code bei Daniels VPS
---

# Zwei "flextrawurst"-Bäume — werkraum-Kopie ist eine tote Karteileiche

Beim Bauen des On-Demand-Beobachtung-Buttons (Task 8) wollte ich `flextrawurst_surface.html`
unter `/root/werkraum/flextrawurst/` bearbeiten — Prüfsumme stimmte aber nicht mit der über
Port 8787 tatsächlich ausgelieferten Datei überein.

## Was tatsächlich stimmt, per `git log` verifiziert

`/root` ist EIN einziges Git-Repo, kein zwei getrennte — `/root/werkraum/` und
`/root/flextrawurst/` sind beides nur Unterordner desselben Repos.

`werkraum/flextrawurst/flextrawurst_surface.html`: **0 Commits in der gesamten Repo-Geschichte.**
Nie bearbeitet, nie Teil echter Arbeit.

`flextrawurst/scripts/build_surface.ts` und `flextrawurst/out/process_camera/flextrawurst_surface.html`:
durchgehende, aktive Commit-Historie — Fragment-Betrachter, Gemeinsames-Haus-Tab,
Flarum-Aktivität-Tab, Wesen-Vault-Einblick — alles Features, die ich aus CLAUDE.md/Delta-Log kannte.

`process-camera-preview.service` (Port 8787, `serve_process_camera_preview.ts`) hat
`WorkingDirectory=/root/flextrawurst` — bedient nachweislich (Prüfsumme identisch)
`flextrawurst/out/process_camera/flextrawurst_surface.html`.

## Die Regel daraus

**Der echte, lebendige Surface-Projektbaum ist `/root/flextrawurst/`, nicht
`/root/werkraum/flextrawurst/`.** Build-Workflow: `scripts/build_surface.ts` bauen
(`npx tsx scripts/build_surface.ts` aus `/root/flextrawurst/`), Output landet in
`out/surface/` und muss danach nach `out/process_camera/` kopiert werden (deckt sich mit
der schon in CLAUDE.md dokumentierten i18n-Gesetz-Pflicht "cp out/surface/... out/process_camera/...").

Daniel wörtlich, als ich fragte ob das bewusst so eingerichtet ist: *"das musst du dich
selber fragen....zu sowas hab ich doch niemal nen überblick bekommen uoder du mir
mitgeteilt"* — er hatte nie Einblick in diese Doppelstruktur, eine frühere Instanz hat sie
offenbar angelegt (oder es ist historisch gewachsen) ohne es je zu dokumentieren oder ihm
zu berichten. Diese Karte-Datei soll genau das für die Zukunft nachholen.

## Was noch offen ist

Ob `/root/werkraum/flextrawurst/` absichtlich als frühe Blaupause/Testkopie existiert (und
gefahrlos ignoriert werden kann) oder ob sie versehentlich entstanden ist und irgendwann
aufgeräumt werden sollte — nicht geklärt, kein Auftrag dazu heute. Wichtig ist nur: bei
jeder künftigen Surface-Arbeit **immer `/root/flextrawurst/`, nie `/root/werkraum/flextrawurst/`**
anfassen.
