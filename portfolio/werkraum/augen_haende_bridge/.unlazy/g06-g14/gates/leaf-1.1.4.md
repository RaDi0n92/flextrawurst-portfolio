# Gates: Linux-Körper starten

OWNS: src/augen_haende_bridge/koerper/haupt.py, src/augen_haende_bridge/koerper/haupt_linux.py, src/augen_haende_bridge/koerper/einstellungen.py, src/augen_haende_bridge/koerper/anzeigeort.py, client_vps/koerper_linux_starten.sh, tests/test_koerper_haupt_linux.py, probes/linux_koerper_e2e.py

Scope: Das Programm des Körpers läuft auf KDE 1 und KDE 2 wie unter Windows: ein Start, ein Selbsttest, Anmeldung am Relay als eigener Anzeigeort, Raute, Terminal, Chat, Regie, Banner, Ticker, Zeichnen und Bild-Elemente aus derselben Logik. Windows bleibt unverändert (derselbe Ablauf, jetzt über eine Plattformbeschreibung).

- [x] G1: `haupt.py` setzt den Körper über eine Plattformbeschreibung zusammen, und für Windows ergibt das dieselben Bausteine wie zuvor; die Linux-Beschreibung liefert Aufnahme, Scanner, Hände, Not-Aus, Dateiwahl, Sichtquelle, Pfade und Ort des Desktops
  CHECK: PYTHONPATH=src:tests:client_vps python3 -m unittest tests.test_koerper_haupt_linux.PlattformTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=f5d34549dc220d0443b76e12a25e96f0f7cafb8bb0dbbe12774141f235903c65; exit=0; EXPECT=matched; output-sha256=1af5ad9b784fb37a2cd3651b9494b61d289fd5ead2f08debc7fa03ac1d79f196; output-bytes=105; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G2: der Linux-Selbsttest meldet Anzeige, Fenster, Aufnahme (auch ohne Bridge-Fenster), Eingabe, Not-Aus, Hotkeys, Schriften und Relay-Zugang einzeln als ok oder fehlt, ohne etwas zu verändern
  CHECK: xvfb-run -a -s "-screen 0 1280x800x24" env BRIDGE_TEST_XVFB=1 PYTHONPATH=src:tests:client_vps python3 -m unittest tests.test_koerper_haupt_linux.SelbsttestTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=e0b88a754be6f764d8281c1d6f0f272873cc7926b64f080c0ebf59a7f3056bf9; exit=0; EXPECT=matched; output-sha256=5bba73c014b9a3d4e19c877047077e2fca4da1a2485120ceb02ca31b1885680e; output-bytes=15654; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G3: ein echter Linux-Körper unter eigenem Xvfb meldet sich am Relay als KDE 1 an, startet einen Agenten, zeigt Raute, Terminal und Chat, bekommt die Ausgabe, nimmt Tastatureingaben im Terminal an und sendet Bilder seines Ziels
  CHECK: xvfb-run -a -s "-screen 0 1280x800x24" env BRIDGE_TEST_XVFB=1 PYTHONPATH=src:tests:client_vps python3 -m unittest tests.test_koerper_haupt_linux.KoerperEndeZuEndeTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=95647fc1f2ce63e435b7fe8198a6b6950b748dcf79e31334686d691bcc17bf57; exit=0; EXPECT=matched; output-sha256=e28c05f34373953db9ffa05b0c8f2bc02e2a2fcddffa837a5b55fef69759ffeb; output-bytes=986; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G4: der Linux-Körper hält Einstellungen (Orte, Namen, Farben) in der XDG-Konfiguration und das Log im XDG-Zustandsordner, und ein Neustart stellt Ort und Größe der Fenster wieder her
  CHECK: xvfb-run -a -s "-screen 0 1280x800x24" env BRIDGE_TEST_XVFB=1 PYTHONPATH=src:tests:client_vps python3 -m unittest tests.test_koerper_haupt_linux.PfadeTests tests.test_koerper_haupt_linux.EinstellungenFensterTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=ef51e681e0803d63d6ac8140227567219115ad83478d1f2a6610ba71ec55fce3; exit=0; EXPECT=matched; output-sha256=41c7129cb59107d47f5dd3c741303cf01b7737c09ce3884b53adbbf9fcb748fc; output-bytes=8142; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G5: das Startskript startet den Körper für KDE 1 oder KDE 2 mit den richtigen Zugangsdaten und verweigert unbekannte Orte
  CHECK: PYTHONPATH=src:tests:client_vps python3 -m unittest tests.test_koerper_haupt_linux.StartskriptTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=9c7820f5ce27271dbdbf467091db83f607cd0f1cf44ea92472d1c949c5729cf5; exit=0; EXPECT=matched; output-sha256=31a40e0aac5b8a465fc663aa61e0feacd953908c6242e4b677d970857b8ecda1; output-bytes=102; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries
