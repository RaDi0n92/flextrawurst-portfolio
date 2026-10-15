# Gates: WorldDOM Knoten- und Ankermodell

OWNS: src/augen_haende_bridge/koerper/weltdom.py, src/augen_haende_bridge/koerper/weltdom_quellen.py, tests/test_koerper_weltdom.py, tests/helfer_weltdom_lauf.py

Scope: Knoten mit Herkunft (real, inferred, authored, projected), Konfidenz, Aktualität und Auflösungsmethode. Echte Struktur aus Browser und Bedienungshilfen, aus dem Bild erschlossene Flächen und Beschriftungen, bewusst angelegte Anker, die einen Neustart überleben.

- [x] G1: das Knotenmodell hält Herkunft, Konfidenz, Alter und Gültigkeit; eine Messung ersetzt den Stand ihrer Quelle und meldet Verschwundenes; erfundene Anker tragen Urheber und Ort, projizierte sind nie ausführbar, nur das Bewusste wird gespeichert und tolerant geladen
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_koerper_weltdom.ModellTests tests.test_koerper_weltdom.StoreTests tests.test_koerper_weltdom.UiBaumTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=4b43ea57324370b56d43997742de390fa82215c0fef8a0546305733cb8462476; exit=0; EXPECT=matched; output-sha256=a403b031ca53505b1068c5c1262f30475f8ef294ae83636c47835f0a12e632af; output-bytes=110; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G2: aus einem Bild werden Flächen (Schaltfläche-, Feld-ähnlich) und Beschriftungen als Vermutung erschlossen: Konfidenz unter eins, Grenzen im Knoten, keine nativen Fähigkeiten behauptet; fehlende Werkzeuge und kaputte Bilder ergeben einen Grund statt erfundener Treffer
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_koerper_weltdom.ErschlossenTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=12147722118c04ae3aca86e166ce753dd875d67de9cf6279fe9442aa73d1d7ae; exit=0; EXPECT=matched; output-sha256=737441c3294ad0db58790ec192e3410eb096540bdc0bb66f604c8ec0e7b7385c; output-bytes=102; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G3: gegen ein echtes GTK-Programm mit AT-SPI: echte Knoten (Knopf, Feld, Etikett) mit Herkunft, Lage, Konfidenz 1,0 und frischem Alter; ein Etikett kann nur gelesen werden
  CHECK: xvfb-run -a -s "-screen 0 1280x800x24" env BRIDGE_TEST_XVFB=1 PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_koerper_weltdom.RealAtspiTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=e95f10cffba5ac870a32446424afa2853830746bca88f5ed5c9b5e5d0d2b6ec0; exit=0; EXPECT=matched; output-sha256=b26a0149ab7ed2bed22d52da9f4d6c4e020a3c3415be35a9a828dafe827d7494; output-bytes=98; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G4: gegen einen echten Chromium und das Bild eines echten Fensters: echte Seitenknoten mit Lage und Herkunft (Geometrie als gemessen oder abgeleitet gekennzeichnet); aus dem Bild erschlossene Flächen und der erkannte Text liegen auf dem echten Knopf
  CHECK: xvfb-run -a -s "-screen 0 1280x800x24" env BRIDGE_TEST_XVFB=1 PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_koerper_weltdom.BrowserWeltdomTests tests.test_koerper_weltdom.ErschlossenRealTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=6d6b03b7db1c6f658589a39fe5d8b408753cbb43b933f6877a6b5bc73d7b58b9; exit=0; EXPECT=matched; output-sha256=f8886b9a06ec42acf1142a5bd203f9a57f5ccf38db7848d7370ba3bb8a77c965; output-bytes=833; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries
