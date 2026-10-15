# Gates: UI Automation / Bedienungshilfen

OWNS: src/augen_haende_bridge/koerper/uia.py, tests/test_koerper_uia.py

Scope: Normale Programme lassen sich über die Bedienungshilfen ihres Systems lesen und bedienen: UI Automation unter Windows, AT-SPI unter Linux. Ein gemeinsamer Baum aus Knoten mit Rolle, Name, Wert, Zuständen und Lage; Aktionen (Klick, Text setzen) mit Rücklese; ehrliche Aussage, wenn ein Programm nichts anbietet.

- [x] G1: gegen ein echtes GTK-Programm unter Xvfb mit AT-SPI: der Knotenbaum nennt Schaltflächen, Felder und Beschriftungen mit Rolle, Name und Lage
  CHECK: xvfb-run -a -s "-screen 0 1280x800x24" env BRIDGE_TEST_XVFB=1 PYTHONPATH=src:tests:client_vps python3 -m unittest tests.test_koerper_uia.AtspiLesenTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=cc591dedaa480a0be2ce8ef91979c41017f243b47519cf2f09da9c53c4e42084; exit=0; EXPECT=matched; output-sha256=13dc6adb7bb472af3e392ddd4ce4df0a76793b9042de1b037aec387d56e259d0; output-bytes=98; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G2: eine Schaltfläche auslösen und einen Feldwert setzen und zurücklesen; ein Knoten ohne diese Fähigkeit löst nichts aus
  CHECK: xvfb-run -a -s "-screen 0 1280x800x24" env BRIDGE_TEST_XVFB=1 PYTHONPATH=src:tests:client_vps python3 -m unittest tests.test_koerper_uia.AtspiBedienenTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=f5cb2cafdf8deac0a8ea2157c96525a05f24eafcda45ec3b01fa212870abd14f; exit=0; EXPECT=matched; output-sha256=d3cc2c010efc1a73b5143df8d03c7e5e7a0c59fbb0bc2cb326427ff697dcffe5; output-bytes=100; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G3: die Windows-Fassung (UI Automation über comtypes) ist an dieselbe Schnittstelle angebunden und wird gegen ein nachgebautes Objektmodell geprüft; ohne die Bibliothek meldet sie „nicht verfügbar“
  CHECK: PYTHONPATH=src:tests:client_vps python3 -m unittest tests.test_koerper_uia.WindowsUiaTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=5501436fe16626a6d15447cc858e373c8db2921a4533aec7b9c29e88194029d7; exit=0; EXPECT=matched; output-sha256=6273232de4d3ef7acd4ecafa5c86beeeb974f56586b21089a2990b3f72facbe6; output-bytes=103; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G4: ein Programm ohne Bedienungshilfen (nur gezeichnete Fläche) wird als „kein Baum“ gemeldet, nicht als leerer erfolgreicher Baum
  CHECK: xvfb-run -a -s "-screen 0 1280x800x24" env BRIDGE_TEST_XVFB=1 PYTHONPATH=src:tests:client_vps python3 -m unittest tests.test_koerper_uia.OhneBaumTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=170503f4ead9e9110a5e6537af716287ca42fedf52e4e78224c7bd3b05bba85e; exit=0; EXPECT=matched; output-sha256=231ac5f159ad0f5d70759bc4bc98a61442b3bf6b596fcbb41f2d2997e1eeb890; output-bytes=598; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries
