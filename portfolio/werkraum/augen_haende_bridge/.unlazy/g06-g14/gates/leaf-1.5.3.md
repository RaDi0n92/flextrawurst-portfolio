# Gates: Zeigegeste, Darstellung und Einfügung, Anschluss

OWNS: src/augen_haende_bridge/koerper/zeigegeste.py, src/augen_haende_bridge/koerper/weltdom_dienst.py, src/augen_haende_bridge/koerper/weltdom_befehle.py, src/augen_haende_bridge/koerper/weltdom_anbindung.py, src/augen_haende_bridge/koerper/anwendung.py, src/augen_haende_bridge/koerper/haupt.py, client_vps/terminal_launcher.py, client_vps/bridge_cli.py, src/augen_haende_bridge/transport.py, tests/test_koerper_zeigegeste.py, tests/test_koerper_weltdom_anbindung.py

Scope: Eine Zeigegeste hält Ort, Ziel und Bild fest und haftet am Inhalt; nach einem Layoutwechsel warnt sie oder löst sich neu auf, nie ein blinder Klick auf den alten Pixel. Darstellung und Einfügung sind getrennte Wege mit getrennten Ergebnissen. Alles ist über Relay, Starter, Werkzeug und Körper angeschlossen.

- [x] G1: die Prüfung der Geste unterscheidet gültig, fensterbindung, neu aufgelöst und veraltet (Ziel weg, minimiert, ersetzt, zu alt, Layout, DPI); bedienbarer Inhalt geht vor dem Text darin; veraltete Gesten werden nie am alten Pixel ausgeführt
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_koerper_zeigegeste.GesteLogikTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=777a2b085a5ed869aba2002ec1e7ee90e42cb263e5f2f02522ebee792b6b74b1; exit=0; EXPECT=matched; output-sha256=d9d734ee1c2de67b748aeef1c4126433aa438ad8375ca953916f12b1df11414d; output-bytes=107; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G2: an einem echten Beispiel (Chromium, der Knopf wandert bei geänderter Fensterbreite): die Geste folgt dem Inhalt und klickt ihn; ohne Neuauflösung warnt sie, und nichts wird geklickt
  CHECK: xvfb-run -a -s "-screen 0 1280x800x24" env BRIDGE_TEST_XVFB=1 PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_koerper_zeigegeste.InhaltshaftungRealTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=728875179872b2b1c497364923ec9a1c08bb0aa025cb7b2863367572e02a4550; exit=0; EXPECT=matched; output-sha256=3f300c2d4d503ed18b3cc03b5d6cb6a7d159a90d6d98f803fe9f9d518ba1ce93; output-bytes=100; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G3: die Darstellung legt ein Zeichen in die echte gemeinsame Arbeitsfläche nur für die Gewählten und berührt die Anwendung nicht; die Einfügung ist ein eigener Weg mit eigenem Beleg
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_koerper_zeigegeste.DarstellungRealTests tests.test_koerper_weltdom_anbindung.DienstTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=bdd88c887c9197a7fe9f319c58effb43e9e09b1e19096ad29c2494f6ad23d2b3; exit=0; EXPECT=matched; output-sha256=74c03fc16fde9a2dfeff03db0ec8f472a5a8dfed04e9e982a912b4b7f64faee3; output-bytes=105; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G4: die Befehle sind streng geprüft (Starter und Körper), handelnde brauchen die Lease, das Relay prüft die neuen Nachrichten, die Anwendung und die Plattform-Anbindung arbeiten ehrlich über fehlende Quellen, das Werkzeug kennt alle Befehle
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_koerper_weltdom_anbindung
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=c0e9b289073259232b7132f2c2a0d0d23bd44efb81769509049097903c24e714; exit=0; EXPECT=matched; output-sha256=ab635002a5c87bf4b4d3b3c95f26d171762342f9d839b37b861bc29003734dce; output-bytes=129; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G5: die bisherigen Tests des Körpers, Starters und Relays bleiben grün
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_terminal_launcher tests.test_anzeigeort tests.test_koerper_anwendung tests.test_koerper_erster_koerper tests.test_koerper_anwendung_relay tests.test_koerper_haende_anbindung tests.test_koerper_agentenregister tests.test_g06_integration.SchnittstellenTests
  EXPECT: /^OK/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=5775b29602120403ecca0b8fce31ccf0f091bcc10af2d9f706858d4521949a3a; exit=0; EXPECT=matched; output-sha256=b77c2f3f4cea8f86ace46e116b71e280c60baf0854d84baf1fed66d94a2124d5; output-bytes=2207; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries
