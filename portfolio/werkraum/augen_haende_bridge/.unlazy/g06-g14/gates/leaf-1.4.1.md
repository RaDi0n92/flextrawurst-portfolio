# Gates: Eingabeadapter Windows und Linux

OWNS: src/augen_haende_bridge/koerper/eingabe_adapter.py, tests/test_koerper_eingabe_adapter.py, tests/helfer_gtk_haende.py, probes/haende_wine.py

Scope: Klicken, Doppelklick, Ziehen, Tippen, Tastenkombinationen und Mausrad auf einem bestimmten Fenster, hinter einem Käfig, mit echten Plattformaufrufen (XTEST unter X11, SendInput unter Windows/Wine). Das Ergebnis trennt zugelassen, übergeben, nachgemessen und protokolliert.

- [x] G1: der Käfig lehnt jeden Fall mit festem Grund ab (Not-Aus, Rechte, Profil, Lease, Ziel weg/minimiert/ersetzt, Bild unbekannt/veraltet/anderes Ziel, Verschiebung und DPI, Punkt außerhalb, gesperrte Tasten) und rechnet Bildpunkte skaliert auf den Bildschirm um; Aktionen werden streng gelesen
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_koerper_eingabe_adapter.KaefigTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=e3599e00a0ef3ebf67e00b68df362765022ce0017f4b112164974b2bbc33e49d; exit=0; EXPECT=matched; output-sha256=cf8d3a2572a7898fcf32a4c2dd1445509b3d59e66061853243c4627f80695068; output-bytes=109; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G2: die Engine führt in Schritten aus, prüft vor jedem Schritt Stopp und Ziel, lässt in jedem Fall los (auch bei Fehler, Abbruch, Verschiebung des Ziels, scheiternder Taste), erkennt ein Fenster vor dem Punkt und meldet Fokusverlust ehrlich
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_koerper_eingabe_adapter.EngineTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=ee7bff87a95a67684d3fe546a02e7362600e47117cffc06b5503821ba27e6c4f; exit=0; EXPECT=matched; output-sha256=798e16770649ccf4a7f43e9e84211cf0c819d3d3b20e06865bbe12a61716ab19; output-bytes=114; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G3: unter X11 gegen echte GTK-Fenster: Klick zählt im Programm, Text mit Umlauten und Emoji und Strg+A, Doppelklick, Rechtsklick, Rad, Ziehen mit echtem Zeigerweg und Loslassen, Schieberegler
  CHECK: xvfb-run -a -s "-screen 0 1280x800x24" env BRIDGE_TEST_XVFB=1 PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_koerper_eingabe_adapter.X11HaendeTests.test_klick_auf_die_schaltflaeche_wirkt_wirklich tests.test_koerper_eingabe_adapter.X11HaendeTests.test_tippen_und_tastenkombination_wirken_im_eingabefeld tests.test_koerper_eingabe_adapter.X11HaendeTests.test_doppelklick_rechtsklick_und_mausrad tests.test_koerper_eingabe_adapter.X11HaendeTests.test_ziehen_hat_ein_echtes_ergebnis_und_laesst_los tests.test_koerper_eingabe_adapter.X11HaendeTests.test_schieberegler_per_klick_auf_die_spur
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=f17ad52f7beb75a4a6a7ccb91b14eecd35fbdf8ea315a94dca169ff478c7aa90; exit=0; EXPECT=matched; output-sha256=ebded7495298dcaf63eefb69dea0f8cb62acb86013b0548664ab1487afbb473d; output-bytes=724; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G4: Negativtests an echten Fenstern: ein Fenster davor, falsches Ziel, veraltetes Bild, verschobenes Fenster, fehlende Lease, fehlende Rechte, Not-Aus; zwei Agenten arbeiten gleichzeitig an zwei Fenstern und jeder Klick landet im richtigen
  CHECK: xvfb-run -a -s "-screen 0 1280x800x24" env BRIDGE_TEST_XVFB=1 PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_koerper_eingabe_adapter.X11HaendeTests.test_ein_fenster_davor_verhindert_den_klick tests.test_koerper_eingabe_adapter.X11HaendeTests.test_falsches_ziel_veraltetes_bild_und_verschobenes_fenster tests.test_koerper_eingabe_adapter.X11HaendeTests.test_ohne_lease_ohne_rechte_und_im_not_aus_geht_nichts tests.test_koerper_eingabe_adapter.X11HaendeTests.test_zwei_agenten_arbeiten_unabhaengig_an_zwei_fenstern
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=540182000adb950e78d9d8578abaf8e9945a90d04c50e05690ebe5bc7a73ac9b; exit=0; EXPECT=matched; output-sha256=e8016d6ce0640d9535127c9bb0929252da53990149c6e523ffe7360ef7b5922f; output-bytes=102; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G5: unter Windows (SendInput, Wine) gegen ein echtes Win32-Fenster: Klick, Unicode-Text, Strg+A, Rad und Ziehen kommen an, der Zeiger steht auf dem berechneten Bildschirmpunkt
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_koerper_eingabe_adapter.WineHaendeTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=14ad5d519a454fc7d8c07387be18471256cb07aab7cba101c6e9e32eecaa355d; exit=0; EXPECT=matched; output-sha256=96febdcb8770cc87559c0f6ead752beb4aae4fb1be8833911b6fe71b1fcee323; output-bytes=101; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries
