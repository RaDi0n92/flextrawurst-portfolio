# Gates: Linux-Fensterbackend

OWNS: src/augen_haende_bridge/koerper/fenster_linux.py, src/augen_haende_bridge/koerper/plattform.py, src/augen_haende_bridge/koerper/win32_linux.py, src/augen_haende_bridge/koerper/menue_linux.py, src/augen_haende_bridge/koerper/x11_helfer.py, src/augen_haende_bridge/koerper/tasten_x11.py, tests/test_koerper_fenster_linux.py, probes/linux_fenster_smoketest.py, probes/linux_koerper_zeichnen.py

Scope: Die Fensterschicht des Körpers (Fenster, Leinwand, Schrift, Anwendung, Tasten, Menüs, Zwischenablage) läuft auf Linux über GTK 3 mit derselben Schnittstelle wie unter Windows, auswählbar per Umgebungsvariable; Windows bleibt unverändert der Standard.

- [x] G1: Linux- und Windows-Backend haben dieselbe öffentliche Schnittstelle (Namen und Parameter von Fenster, Leinwand, Schrift, Anwendung und den Hilfsfunktionen)
  CHECK: PYTHONPATH=src:tests python3 -m unittest tests.test_koerper_fenster_linux.ParitaetTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=759ed2adedb30095ede6906f48cdc6b0401bea456a8866c4ea484e846e73ddd4; exit=0; EXPECT=matched; output-sha256=2a3f0238916f0e45bc0f1d2644d7e004c388fbf347857aa4184984a6485fd7ce; output-bytes=297; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G2: dieselbe Zeichenlogik erzeugt auf der Linux-Leinwand die erwarteten Pixel an den erwarteten Stellen (Regie-Leiste, Raute, Terminal-Rahmen, Zeichenpalette)
  CHECK: PYTHONPATH=src:tests python3 -m unittest tests.test_koerper_fenster_linux.DarstellungTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=532d2665a198b30fa294e55e17018323bcc72b5de533fdcec2f5fce7c4b80066; exit=0; EXPECT=matched; output-sha256=1a1252527126d4f15832d8f3116ff4c99886f519b31c1e5b56552141ff778793; output-bytes=101; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G3: ein echtes GTK-Fenster unter eigenem Xvfb zeigt sich, bekommt Maus, Tasten, Rad und Doppelklick als bei_*-Aufrufe, lässt sich verschieben und in der Größe ändern, nimmt Durchklick und Formmaske an
  CHECK: xvfb-run -a -s "-screen 0 1280x800x24" env BRIDGE_TEST_XVFB=1 BRIDGE_BACKEND=linux PYTHONPATH=src:tests python3 probes/linux_fenster_smoketest.py
  EXPECT: linux fenster probe ok
  EVIDENCE: automatic-evidence=v1; definition-sha256=3ade314ece72f73dacf72ab5b04f63a10548ddc0934e09543634b3d1d1cbcd2a; exit=0; EXPECT=matched; output-sha256=128dc57ccf7769682bfd397c76a85982377370d5b7248d7d8e6d9275385ccecb; output-bytes=659; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G4: die Backend-Wahl folgt BRIDGE_BACKEND, und ohne die Variable bleibt es das Windows-Backend
  CHECK: PYTHONPATH=src:tests python3 -m unittest tests.test_koerper_fenster_linux.BackendWahlTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=6459a46ca51ca4946538d2ece3951fbefde641fe3ea90903906d99ea23871a30; exit=0; EXPECT=matched; output-sha256=7dc324daea29790a189513234901e30ab60149e22d0196dbe9f20ae32ac309dc; output-bytes=104; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G5: alle bisherigen Körper-Tests bleiben unverändert grün (kein Rückschritt für Windows)
  CHECK: PYTHONPATH=src:tests:client_vps python3 -m unittest discover -s tests -p "test_koerper*.py"
  EXPECT: /^OK( \(skipped=\d+\))?$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=5a3c4155f28198f40dd3f585d29a6c5b0825237a623b3eb0962e3087215105dd; exit=0; EXPECT=matched; output-sha256=aa9213cf7568f6924c089ae6248635630fb8d0f68c1d2422faee92ce422a8c45; output-bytes=1799; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries
