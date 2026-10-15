# Gates: Adapterwege je Strom

OWNS: src/augen_haende_bridge/adapterwege.py, probes/adapterweg_tui.py, tests/test_adapterwege.py

Scope: Für jeden gewünschten Strom (Codex, Gemini, Claude, Kimi, Opencode) steht, welcher Weg real am echten Programm geprüft ist und was offen bleibt. Nichts gilt als belegt ohne Messung.

- [x] G1: die Tabelle deckt jeden Eintrag der Startliste und alle gewünschten Ströme ab, jedes Ergebnis hat eine Bemerkung, ungemessene Wege stehen als „offen“, kein kopfloser Lauf wird als ausgeführt behauptet
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_adapterwege.TabelleTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=2715e9b81a4e9fe687564f449fafa773fa8e6be889d6b8579a9f315698a652e8; exit=0; EXPECT=matched; output-sha256=e6ec182765cd965f2837d8eeaef5a64af48a104f245cd1a0b7281559194c57c1; output-bytes=102; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G2: die Prüfung nennt für ein fehlendes Programm „nicht installiert“, liest Versionen aus echter Ausgabe, übersteht ein hängendes Programm, und die auf diesem Rechner liegenden Agenten (claude, codex, opencode, agy) nennen eine echte Version
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_adapterwege.PruefTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=f4512ef9cbe99151642905723463636c3ca9b06534b33182cecf7db973dd93f4; exit=0; EXPECT=matched; output-sha256=d70b5174d26345ca9c8e45ca9bcd21ae13612bcdff099d473837807e84abc7a5; output-bytes=102; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G3: die TUI-Probe läuft gegen den echten Starter und findet die getippte Marke im Ausgabestrom (Prüfling `cat`); die Messergebnisse für die echten Programme stehen mit Datum in der Tabelle `adapterwege.py` und im Abnahmeprotokoll
  CHECK: python3 probes/adapterweg_tui.py cat
  EXPECT: /"marke_im_tui": true/
  EVIDENCE: automatic-evidence=v1; definition-sha256=e3f41fbe880ba9fb7aaafa25d760602974a80a0db3077da03cfc7758317836be; exit=0; EXPECT=matched; output-sha256=39608181c1bf8bbc6a5efdf6736730d71c789d12b0e495ffae62f2b108f93da3; output-bytes=128; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries
