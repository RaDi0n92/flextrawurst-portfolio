# Gates: Browser über CDP

OWNS: src/augen_haende_bridge/koerper/cdp.py, tests/test_koerper_cdp.py

Scope: Ein Chromium-Browser (Chrome, Edge, Chromium) lässt sich über das DevTools-Protokoll lesen und bedienen: Ziele auflisten, Seitenbild, DOM und Bedienungshilfen-Baum, Klick und Eingabe auf Elemente, mit Aussage, was bei kleinem, verdecktem und minimiertem Fenster ankommt.

- [x] G1: gegen einen echten Chromium unter Xvfb: Ziele auflisten, eine Seite verbinden, Seitenbild holen, Titel, Text und den Baum der Bedienungshilfen lesen
  CHECK: xvfb-run -a -s "-screen 0 1280x800x24" env BRIDGE_TEST_XVFB=1 PYTHONPATH=src:tests:client_vps python3 -m unittest tests.test_koerper_cdp.LesenTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=363f04de2ca9a5918a2f9cde09b8221fa6e9e750b673cb0dc6cf11e6f3cdb46a; exit=0; EXPECT=matched; output-sha256=d3612596bbd3a61b0b1a63a01cd6b8cb2cfbb82f46c86d7c4d90cd5c7d1cce0b; output-bytes=100; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G2: einen Knoten ansteuern: Klick auf eine Schaltfläche, Text in ein Feld tippen, Wert zurücklesen; ein nicht auffindbarer Knoten löst nichts aus
  CHECK: xvfb-run -a -s "-screen 0 1280x800x24" env BRIDGE_TEST_XVFB=1 PYTHONPATH=src:tests:client_vps python3 -m unittest tests.test_koerper_cdp.BedienenTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=6dcbdaf9b9b9e419087de2e3c5f38a3638e4668357926a3cfdd7d303e1517346; exit=0; EXPECT=matched; output-sha256=4808c7aa79b6ff46166f3cf8f8e4ee6821d3e518b34144fd1ceed7f0e3d40672; output-bytes=100; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G3: Aussage zu kleinem, verdecktem und minimiertem Fenster: das Seitenbild kommt über CDP vollständig, auch wenn ein anderes Fenster davorliegt oder das Fenster klein ist; was bei minimiert gilt, ist gemessen und festgehalten
  CHECK: xvfb-run -a -s "-screen 0 1280x800x24" env BRIDGE_TEST_XVFB=1 PYTHONPATH=src:tests:client_vps python3 -m unittest tests.test_koerper_cdp.FensterZustandTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=a01836ebf259f9552e109e3db85a9c7e5c3683d75193b9fa2d48ce1b27ac2d9b; exit=0; EXPECT=matched; output-sha256=3803800cd5c50d37a666cca90f181d88661f67de68043487d0f8bf1f8651ca61; output-bytes=101; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G4: Verbindungsfehler, ein Browser ohne offenen Debug-Anschluss und ungültige Antworten werden ehrlich gemeldet (nicht verfügbar statt erfundener Erfolg)
  CHECK: PYTHONPATH=src:tests:client_vps python3 -m unittest tests.test_koerper_cdp.FehlerTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=b0fdd34f37b8bcff20bd3494287753f7d358a2858ce85aa05a657caf8af8ca56; exit=0; EXPECT=matched; output-sha256=8c4a69b7fc42341b3955c0c896b2523c8ca31538ff11b2fd8f4c90ee217bb014; output-bytes=581; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries
