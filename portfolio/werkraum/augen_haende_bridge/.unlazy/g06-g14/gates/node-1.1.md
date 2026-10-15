# Gates: G06 Plattform und Anzeigeort — Integration

Scope: Die vier Teilstücke (Linux-Fensterschicht, X11-Adapter, Relay mit Anzeigeorten, Linux-Körper) bilden zusammen das, was G06 verlangt: der Körper erscheint auf KDE 1 und KDE 2 wie unter Windows, der Anzeigeort wechselt ohne Sitzungsverlust, das Arbeitsziel ist davon unabhängig. Alles Native (Daniels echte KDE-Desktops und Windows) steht im Übergabe-Ledger, nicht hier.

- [x] N1: alle vier Teilstücke bestehen ihre Gates erneut (Parent-Reverify aus den genauen Ledgern)
  CHECK: node /config/.claude/skills/unlazy/scripts/gate-check.mjs --root . --cwd . --approve --reverify --jobs 1 --timeout 900 .unlazy/g06-g14/gates/leaf-1.1.1.md .unlazy/g06-g14/gates/leaf-1.1.2.md .unlazy/g06-g14/gates/leaf-1.1.3.md .unlazy/g06-g14/gates/leaf-1.1.4.md
  EXPECT: ALL MET
  EVIDENCE: automatic-evidence=v1; definition-sha256=5754cd8697b9c1cddfd49a57bf3fbc7fc6c7d98862ed436bd2e7606ef5aee13b; exit=0; EXPECT=matched; output-sha256=e228ffed139ca40c001739a7ec4e3256947bc38aa631e65156e05c2b108764e4; output-bytes=11273; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] N2: die Nachrichten des Relays, des Starters und des Körpers passen zusammen (jede erlaubte Nachricht hat Prüfung und Empfänger, Ziel-Schlüssel und Scanner sprechen dieselbe Sprache)
  CHECK: PYTHONPATH=src:tests:client_vps python3 -m unittest tests.test_g06_integration.SchnittstellenTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=bac45ea54e472b3c6910a564ab27b6b690f63fea3beb258f915abaca8af8afec; exit=0; EXPECT=matched; output-sha256=6f2f4ed7447de96be8d4978c72e5aff47361835a427d50b21b8ea362e9269d59; output-bytes=102; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] N3: zwei echte Linux-Körper auf zwei Bildschirmen (KDE 1, KDE 2) mit einem echten Relay: der Körper eines Agenten erscheint auf KDE 1, wandert nach KDE 2, verschwindet von KDE 1 und nimmt die Sitzung mit ihrem Verlauf wieder auf; beide Logs ohne Fehler
  CHECK: xvfb-run -a -s "-screen 0 1280x800x24" env BRIDGE_TEST_XVFB=1 PYTHONPATH=src:tests:client_vps python3 -m unittest tests.test_g06_integration.ZweiKoerperTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=26dd793f76a74ea6cd26238db6efc7e5b2e86d85385df6ca4e9376bc82086c8d; exit=0; EXPECT=matched; output-sha256=bdf7df2b6b9f24b839ebc056462257ceef74ae0b4bd4f79e4f1d85809a7bae90; output-bytes=99; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] N4: die Windows-Fassung (GDI unter Wine) und die Linux-Fassung (GTK) zeichnen dieselben acht Fenster mit höchstens 12 % Größenabweichung (Schrift) und mindestens 80 % je Fenster und 92 % im Mittel übereinstimmenden Pixeln
  CHECK: xvfb-run -a -s "-screen 0 1280x800x24" env BRIDGE_TEST_XVFB=1 PYTHONPATH=src:tests:client_vps python3 -m unittest tests.test_g06_integration.ParitaetTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=90693741e4eabf37897322994ef44e1124206208359eca56904e274e86191362; exit=0; EXPECT=matched; output-sha256=4d3f45bf71999452921276cc660e69556a6be635d46125733a4facbd7d39ca6f; output-bytes=558; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] N5: das ganze Projekt bleibt grün bis auf die drei bekannten, umgebungsabhängigen Fehlschläge
  CHECK: python3 tests/regression_alle.py
  EXPECT: REGRESSION OK
  EVIDENCE: automatic-evidence=v1; definition-sha256=f8a70e5d86a747abecfc79f5318dde0d201e7b474987584e1188e16c27038eb2; exit=0; EXPECT=matched; output-sha256=4486de84df09ad4826896fc520fdb2e4c2a63911ec07ac9fc907b0a4610b6ef9; output-bytes=1243; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries
