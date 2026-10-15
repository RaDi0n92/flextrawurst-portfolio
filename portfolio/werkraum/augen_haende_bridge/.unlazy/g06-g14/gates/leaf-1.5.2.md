# Gates: Auflösen, Ausführen, Rücklesen

OWNS: src/augen_haende_bridge/koerper/weltdom_aktion.py, src/augen_haende_bridge/koerper/cdp.py, tests/test_koerper_weltdom_aktion.py

Scope: Ein Auftrag an einen benannten Knoten wird je Herkunft aufgelöst, am richtigen Ziel ausgeführt und zurückgelesen. Ein nicht auflösbarer, veralteter oder fähigkeitsloser Knoten löst nichts aus.

- [x] G1: die Fälle, in denen nichts passieren darf: unbekannter, projizierter, veralteter, fähigkeitsloser, virtueller Knoten, fehlende oder kaputte Quelle, Hände lehnen ab; jeder Fall nennt seinen Grund und fasst Quelle und Hände nicht an
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_koerper_weltdom_aktion.RegelTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=9e6e378de689c5be60e793b09dc8276ef47341a416b7b5f177cd9d476691f295; exit=0; EXPECT=matched; output-sha256=f8f7b0ac7f2b53ac4e96000f166430c488f2c37e059ad5502b09d60f29d363b8; output-bytes=106; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G2: in einem echten Chromium: Klick auf einen Knoten mit Rücklese (bestätigt, nicht bestätigt, nicht nachprüfbar), Text in ein Feld und zurückgelesen, verschwundener und mehrdeutiger Knoten lösen nichts aus, eine ungültige Kennung wird über Rolle und Namen wiedergefunden
  CHECK: xvfb-run -a -s "-screen 0 1280x800x24" env BRIDGE_TEST_XVFB=1 PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_koerper_weltdom_aktion.BrowserAktionTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=94dd652976ff3b5e98ff2a0ed2c61634964daaf77be611b7d62ae76d97b4cfd2; exit=0; EXPECT=matched; output-sha256=4d95ae652f43f53bee76e0af298b3c993ddf252af3607d4aced74e11553da44b; output-bytes=103; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G3: in einem echten GTK-Programm über AT-SPI: Knopf ausgelöst und Feld gesetzt mit Rücklese, ein Etikett lässt sich nur lesen, ein fehlender Knoten und veraltete Knoten ändern nichts, ein geänderter Pfad wird über Rolle und Namen gefunden
  CHECK: xvfb-run -a -s "-screen 0 1280x800x24" env BRIDGE_TEST_XVFB=1 PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_koerper_weltdom_aktion.AtspiAktionTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=758b8261446ae5c9976d4cf8698bc13885c2db06c8b83520f0f6b1fbc63d5fc3; exit=0; EXPECT=matched; output-sha256=02a24bf71fcc253b611f5bf9c9da54d909705a14aec5f9d1f012ff4f2bcaa3b6; output-bytes=102; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G4: erschlossene und erfundene Knoten werden nur über die echten Hände (Käfig, Bild) geklickt und wirken im Programm; nach einer Verschiebung lehnen die Hände ab und nichts wird geklickt
  CHECK: xvfb-run -a -s "-screen 0 1280x800x24" env BRIDGE_TEST_XVFB=1 PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_koerper_weltdom_aktion.KoordinatenAktionTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=1812a0b55d3f3b61a0d7421e18ae7615fa3bb6a159b547b350c90769a3c53f47; exit=0; EXPECT=matched; output-sha256=0ec9e83f88a739a5b90eff8fa3ca6aeedf3a32abbf61115cb71c282151ab85e9; output-bytes=723; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries
