---
datum: 2026-07-31
betrifft: [gesamtatlas, aufraeumung, kritik, kathedrale, git-vorsicht, sicherheit]
importable: false
autor: claude-code bei Daniels VPS
---

# Gesamtatlas — erste Entschlackung nach der "Kathedralen"-Kritik, plus ein eigener Fehler mittendrin

## Wo das herkommt

Direkt im Anschluss an den Basic-Auth-Fix: Daniel, nachdem er sich den Gesamtatlas selbst angesehen
hatte, wörtlich: *"wo ist das ganze nur eine riesige kathedrale und theologische religionsbibel für
wörter?"* Ich hab das ehrlich bestätigt statt schöngeredet (siehe Chatverlauf) — Zahlen dazu:
funktionaler Kern (Pfad-/Volltext-/Beziehungsindex) ca. 1GB, `owner_recovery`-Beweisverzeichnis
allein 460MB/40.647 Dateien, `truth_class`/`truth_boundary`/`Wahrheitsklasse`/`Wahrheitsgrenze` als
formal durchgezogenes Vokabular über 12+ Python-Module. Daniel: *"das will ich alles fixen ... es ist
mein projekt haha und chatgpt selbst weiß was er schon versemmelt hat."*

Auf Rückfrage (Umfang: nur Aufräumen? Auch Vokabular im Code? Erst mit ChatGPT klären?) —
Antwort: *"1 und 2 und danach noch mehr."* Diese Session: nur Teil 1 (Aufräumen), Teil 2 (Vokabular
im Live-Code entschlacken) bewusst noch nicht angefasst — zu riskant für einen schnellen
nächtlichen Rundumschlag an Code, den mehrere Dienste gleichzeitig live nutzen.

## Was tatsächlich aufgeräumt wurde

Alles vorher archiviert (`/root/werkraum_archive_gesamtatlas_aufraeumung/`, 620MB komprimiert, drei
Archive), erst danach aus dem Live-Baum entfernt — nichts unwiederbringlich gelöscht:

1. **`_gpt/mcp_arbeitskoerper/owner_recovery/`** (460MB, 40.647 Dateien, komplett ungetrackt in Git)
   — komplett archiviert und entfernt. Keine der beiden aktuell grünen Checkpoint-Dateien
   (`MCP_WORLD_READY.json`, `FINAL_SCAN_READY.json`) referenziert etwas darin.
2. **`_gpt/gesamtatlas/omega/`** von 1,2GB auf 20MB reduziert: `delegated_evidence/` (1,1GB,
   komplett ungenutzt laut Referenzprüfung gegen beide Checkpoints), `production_activation/`
   (94MB), `lean_sources/` (34MB), sowie 5 der 6 `verified_full_baselines/`-Schnappschüsse
   (3710, 4150, 4531, 4646, 4651) — **bewusst NICHT angefasst: `verified_full_baselines/4637/`**,
   weil genau diese Baseline vom aktuell grünen `MCP_WORLD_READY.json` direkt als Beleg referenziert
   wird. Vorher per `grep` gegen beide Checkpoint-Dateien geprüft, nicht geraten.
3. **`peer_review/` + `omega_monsterlabor/`** (zusammen ~194MB) — beide fast komplett ungetrackt,
   bis auf 5 echte, git-verfolgte Testskripte (`build_corpus.py`, `replay_mutations.py`,
   `test_driver.py`, `test_cross_generation_playwright.js`, `run_case.js`). Nur der Ballast
   drumherum raus, die 5 echten Skripte bleiben an Ort und Stelle.

**Gesamt aus dem Live-Baum entfernt:** ca. 1,8GB von vorher 17GB `_gpt/`-Baum.

## Ein eigener Fehler, live gefangen und korrigiert

Beim Wiederherstellen der 5 echten Skripte hab ich `git checkout --` benutzt, ohne vorher zu prüfen,
ob eine der Dateien unveröffentlichte, lokale Änderungen hatte. `build_corpus.py` hatte laut
`git status` vor meinem Eingriff ein `M` (modifiziert) stehen — mein `git checkout --` hat sie
stattdessen auf den letzten **committeten** Stand zurückgesetzt, nicht auf den echten Arbeitsstand.
Das hätte echte, unveröffentlichte Arbeit stillschweigend verworfen — wessen Arbeit genau (ChatGPTs
eigener Bau-Prozess ist naheliegend, da die Datei unter `_gpt/` liegt, aber nicht direkt belegt: der
Schreibzugriffs-Log trägt für diesen Eintrag kein `actor`-Feld) [status: offen].

Gefunden, weil ich vor dem eigentlichen Löschen ohnehin alles archiviert hatte — Diff zwischen der
archivierten (echten) Version und der frisch aus Git wiederhergestellten Version zeigte reale
inhaltliche Unterschiede (andere Ignorierlisten, andere Test-Offsets, ein zusätzlicher
Datei-Existenz-Check vor `OMEGA_ADAPTER_CONTRACT.json`). Alle 5 Dateien aus dem Archiv zurückkopiert,
byte-genau gegen die archivierte Fassung verifiziert, `git status` zeigt `build_corpus.py` jetzt
wieder korrekt als modifiziert — exakt der Zustand von vor meinem Eingriff.

**Die Lehre, konkret:** `git checkout --`/`git restore` auf einzelne Dateipfade ist genauso
gefährlich wie ein `git reset --hard` auf das ganze Repo, wenn man den Status der Einzeldatei vorher
nicht geprüft hat — das steht zwar schon in meinen eigenen Sicherheitsregeln ("vor jeder
destruktiven Operation git status prüfen"), aber ich hab es hier trotzdem übersprungen, weil der
Fokus auf dem großen `rm -rf` lag und die kleine Wiederherstellungs-Zeile danach wie eine
harmlose Formalität wirkte. Genau solche "wirkt harmlos"-Momente sind laut eigener SUBCONSCIOUS.md-
Beobachtung (Muster 1) die gefährlichsten.

## Was noch offen ist

Vokabular-Entschlackung im Live-Code (`truth_class`, `Omega`, `Ursprungsring` etc. in
`vps_mcp_server.py` und den `mcp_atlas*.py`-Modulen) — bewusst nicht heute, weil das denselben
Produktionscode anfasst, den mehrere aktive systemd-Dienste gleichzeitig importieren, und weil jede
Änderung dort den aktuell grünen `MCP_WORLD_READY.json`-Hash-Beleg ungültig macht. Daniel weiß das
(*"chatgpt selbst weiß was er schon versemmelt hat"*), also kein technisches Hindernis, nur eine
Frage von Sorgfalt statt Tempo — nächster Schritt für eine eigene, nicht-hastige Session.
