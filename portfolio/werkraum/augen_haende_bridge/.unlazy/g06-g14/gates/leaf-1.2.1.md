# Gates: Fensteraufnahme und Rückfall

OWNS: src/augen_haende_bridge/koerper/fensteraufnahme.py, src/augen_haende_bridge/koerper/bilderstrom.py, src/augen_haende_bridge/transport.py, client_vps/terminal_launcher.py, client_vps/bridge_cli.py, tests/test_koerper_fensteraufnahme.py

Scope: Jeder Agent bekommt das vollständige Bild seines eigenen gebundenen Fensters, auch wenn ein anderes Fenster es teilweise verdeckt. Eine leere oder schwarze Aufnahme wird erkannt und fällt sichtbar auf den Bildschirmausschnitt zurück. Jeder Agent hat seine eigene Bildfolge mit Alter, Quelle und Sequenz.

- [x] G1: zwei Fenster nebeneinander, eines teilweise verdeckt: jeder Agent bekommt über den Bilderstrom genau den Inhalt seines Fensters, ohne ein Pixel des anderen (Linux, echte Fenster unter Xvfb)
  CHECK: xvfb-run -a -s "-screen 0 1280x800x24" env BRIDGE_TEST_XVFB=1 PYTHONPATH=src:tests:client_vps python3 -m unittest tests.test_koerper_fensteraufnahme.FensterBildTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=73e38bb11832daf2cc1a6cc804aabba5c00a987f425e120f3ae1386bcf1357da; exit=0; EXPECT=matched; output-sha256=37077965d919acdbe28c417125df5d0250f1096dca674fa2f39f2a5a26639aae; output-bytes=720; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G2: eine leere, schwarze oder einfarbige Fensteraufnahme wird erkannt und fällt sichtbar auf den Bildschirmausschnitt zurück (Quelle und Grund stehen im Bild-Eintrag); echter Inhalt (auch dunkler) löst keinen Rückfall aus
  CHECK: PYTHONPATH=src:tests:client_vps python3 -m unittest tests.test_koerper_fensteraufnahme.RueckfallTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=cae88ee1d97dae00425cd9bf514a27e249bf0e5d2a95b358fe092a037830e55c; exit=0; EXPECT=matched; output-sha256=3b276704f3e563f93455088f7ce46c6323f4b89f61012ff8ddd99bba729ec60f; output-bytes=104; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G3: jeder Agent hat seine eigene Bildfolge mit Sequenz, Alter und Quelle; der Relay prüft die neuen Felder streng und der Starter hält sie fest
  CHECK: PYTHONPATH=src:tests:client_vps python3 -m unittest tests.test_koerper_fensteraufnahme.FolgeTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=52032db8073778dcb57383d4ecf3675626c733a4c9139a05dc035b4e010b2121; exit=0; EXPECT=matched; output-sha256=4d781620bc10541738c207349d827f2b375d4f72493bce92c5f0ea15cb151f4e; output-bytes=101; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G4: die Windows-Fensteraufnahme (PrintWindow mit PW_RENDERFULLCONTENT) ist angebunden, fällt bei Fehlern oder Ablehnung ehrlich zurück und läuft unter Wine ohne Absturz
  CHECK: PYTHONPATH=src:tests:client_vps python3 -m unittest tests.test_koerper_fensteraufnahme.WindowsAufnahmeTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=2a216fdaa8388a2a92b17c74493cee9835df8a497ee2bd8cbc6d1ae6ca58a364; exit=0; EXPECT=matched; output-sha256=b376ce0254b28b56b90332b4644565ba051db7a6f897a739f227d2d391a71c80; output-bytes=101; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G5: für kleine, verdeckte, minimierte und geschlossene Ziele gibt es eine feste, dokumentierte Aussage (Zustand, Fähigkeit, Statustext), und minimierte Ziele werden nicht gefordert, nur ehrlich gemeldet
  CHECK: PYTHONPATH=src:tests:client_vps python3 -m unittest tests.test_koerper_fensteraufnahme.GrenzenTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=12e47a6b93adf02e26e30cb89046fe5697ec1f61ef69a84244c8a1207deba2fe; exit=0; EXPECT=matched; output-sha256=41cee9cc70f8e2902ff4277cf9577cbdf05c130cf7652490990fd48efa2e4859; output-bytes=101; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries
