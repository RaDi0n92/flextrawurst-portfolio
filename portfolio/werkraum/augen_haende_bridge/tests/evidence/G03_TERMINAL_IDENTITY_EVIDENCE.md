# G03 — Stabile Terminal-Identität und Slot-Sicherheit

**STAGE:** G03 terminal identity and slot mapping
**DATE:** 2026-09-20
**OUTCOME:** PASS (Core/Browser slice), native Windows/KDE bridge binding remains NOT_PROVEN

## FocusContract

- **Goal:** Eine laufende Original-Konsole darf bei Discovery-Reihenfolge, Schließen oder Wiedererscheinen nicht still unter eine andere Bindung rutschen.
- **Next stone:** Den Registry-Readback über die echte Bridge an den Windows-Overlay-Refresh anschließen; danach native Windows-Evidence.
- **Preserved anchors:** historische sichtbare IDs `terminal-1..4`, `win-desktop` als Default, `terminal-probe` als isoliertes Ziel, getrennte Anzeige-/Arbeitsziele.
- **Forbidden drift:** Keine Eingabe an eine bloße Slot-ID ohne stabile Session-Identität; kein Playwright-PASS als native Abnahme; kein Zugriff auf laufende Agenten-Terminals als Probe.

## Implemented

- `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/target_registry.py` bildet `service|session_path` als `stable_identity` ab.
- Sichtbare `terminal-N`-IDs bleiben als UI-Slots erhalten, werden aber über `_terminal_slot_by_identity` stabil zugeordnet.
- Ein überlebendes Terminal behält seinen Slot trotz Discovery-Reordering; ein geschlossenes Terminal verschwindet, ohne das verbleibende Terminal auf seinen alten Slot zu verschieben.
- Die Registry baut den neuen Record-Satz außerhalb des sichtbaren Zustands und tauscht ihn atomar aus; zweiphasige Slotreservierung schützt erinnerte Slots vor neuen Sessions.
- Discovery läuft außerhalb des Registry-Locks; ein Refresh-Coalescing-Gate und eine Sequenznummer verwerfen überholte Läufe, ohne den letzten guten Snapshot zu zerstören.
- Ein `TerminalDiscovery`-Status unterscheidet `ok` von `degraded`, `error` und `unavailable`; fehlerhafte Discovery wird nicht als leere Welt angewendet.
- `terminal-probe` reserviert seine Session-Identität, wird nicht doppelt als normales Ziel entdeckt und übernimmt bei Bedarf die Auswahl atomar.
- Der synthetische `terminal-1`-Fallback wird unmittelbar wiederhergestellt; ausgewählte, weiterhin lebende Ziele bleiben nach Refresh ausgewählt.

## Core evidence

- `PYTHONPATH=src python3 -m unittest discover -s tests -v` → **90 Tests OK**.
- `python3 -m py_compile src/augen_haende_bridge/target_registry.py client_windows/overlay_app.py src/augen_haende_bridge/windows_scanner.py` → **PASS**.
- Tests decken Reordering/Schließen, Auswahl-Erhalt, Slot-Identität, Probe-Deduplizierung, Fallback und Windows-No-op-Start ab.

## Playwright evidence

- `/root/werkraum/augen_haende_bridge/tests/transport_playwright_proof.py` → **PASS**.
- `/root/werkraum/augen_haende_bridge/tests/reference_surface_proof.py` → **PASS**.
- Die Browserläufe prüfen ausschließlich den browserbedienbaren lokalen Transport-/Referenzpfad. Sie behaupten keine native Windows-Overlay-, Win32-Capture- oder Input-Abnahme.

## Reviewer correction trail

- Gemini/Antigravity fand im Review einen echten Fehler: Die Auswahl wurde vor der Wiederbevölkerung zurückgesetzt. Das wurde behoben und durch `test_selected_live_session_survives_refresh` abgesichert.
- Gemini fand danach einen echten Probe-Randfall: Beim Umwandeln eines ausgewählten entdeckten Terminals in `terminal-probe` fehlten sofortige Auswahlmigration und Fallback. Beides ist behoben und getestet.
- Gemini fand anschließend zwei echte Refresh-Randfälle: Zwischenzustand während Discovery und Slot-Stehlen durch neue Sessions. Atomarer Record-Tausch, Locking und zweiphasige Slotreservierung sind umgesetzt und durch den Reordering-Test abgesichert.
- Claude fand als nächste echte Anschlussrisiken Fehler-als-leere-Welt und Refresh-Starvation. Discovery-Status, Snapshot-Erhalt, Sequenzinvalidierung und Coalescing sind umgesetzt und getestet.
- Gemini bestätigte den aktuellen Lifecycle-Diff mit **PASS**; Claude bestätigte den Lifecycle-Follow-up mit **approve**, bei offenen Produktanschluss-Hinweisen.
- Ein früher Gemini-Hinweis zu einem angeblichen `inspect`-Signaturaufruf war nicht im tatsächlichen Code vorhanden und wurde durch lokale Ausführung widerlegt.
- Claude Opus bestätigte die Architektur des Identitäts-/Slot-Ansatzes im G02-Kontext; die native Plattformabnahme bleibt ausdrücklich offen.

## Open boundary

Der Windows-Client ruft die Registry bisher beim Start lokal auf; ein echter Bridge-Readback-Refresh von KDE-Terminals ist noch nicht der Produktpfad. Windows-ConPTY, Win32-Capture, Overlay-Hit-Test, Not-Aus und native Eingabe brauchen jeweils eigene Plattform-Evidence. ChatGPT bleibt als Reviewer ungeclaimt, solange C2C keine gebundene Projektsession mit realem Review liefert.
