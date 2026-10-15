# Gates: Linux-Adapter (Fensterliste, Aufnahme, Eingabe, Not-Aus, Dateiwahl)

OWNS: src/augen_haende_bridge/koerper/linux_adapter.py, src/augen_haende_bridge/koerper/ziele.py, src/augen_haende_bridge/windows_scanner.py, src/augen_haende_bridge/windows_capture.py, src/augen_haende_bridge/contracts.py, tests/test_koerper_linux_adapter.py

Scope: Alles, was der Körper auf Windows von Win32 bekommt und nicht Fenster ist, gibt es für Linux über X11: Fensterinventar für den Scanner, Aufnahme des Desktops und einzelner Fenster (auch verdeckter) ohne die Fenster der Bridge, Tasteneingabe in beliebige Fenster, lokaler Not-Aus (F12), Dateiwahl und die Sichtquelle für die Sichtbarkeitsregeln.

- [x] G1: das Fensterinventar nennt echte X-Fenster mit Titel, Klasse, Prozess, Lage, Sichtbarkeit und Stapelreihenfolge (oben zuerst) und füttert den vorhandenen Scanner mit Frame-Paarung und stabiler Generation
  CHECK: xvfb-run -a -s "-screen 0 1280x800x24" env BRIDGE_TEST_XVFB=1 PYTHONPATH=src:tests python3 -m unittest tests.test_koerper_linux_adapter.InventarTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=82f52fb8a25fbfc4cd81ef9d39c82ceddd9b9ff1a9caf02c0c4e7cb6222a28d7; exit=0; EXPECT=matched; output-sha256=104eb5494f511692aa8bcb7308289257b5db8163d3cf7e7de76c53ff23e4dbf2; output-bytes=11371; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G2: die Aufnahme liefert die richtigen Pixel des Desktops, ein verdecktes Fenster vollständig ohne fremde Pixel, und lässt die Fenster der Bridge aus (die darunterliegenden Fenster erscheinen)
  CHECK: xvfb-run -a -s "-screen 0 1280x800x24" env BRIDGE_TEST_XVFB=1 PYTHONPATH=src:tests python3 -m unittest tests.test_koerper_linux_adapter.AufnahmeTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=1d8a3287474a7c815b2abbdfb5cc774d68a8975676b3da1f094c162b249ba585; exit=0; EXPECT=matched; output-sha256=e58273392db2da13b2337a51296a84c04f8593a60cdf719b067947eaff49141f; output-bytes=4081; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G3: Text (Umlaute, Emoji, Satzzeichen) und Tastenkombinationen kommen über XTEST in einem echten Fenster als dieselben Zeichen an, und der `schreibe`-Auftrag der Hände läuft damit von der Raute bis ins Eingabefeld
  CHECK: xvfb-run -a -s "-screen 0 1280x800x24" env BRIDGE_TEST_XVFB=1 PYTHONPATH=src:tests python3 -m unittest tests.test_koerper_linux_adapter.EingabeTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=505502a58e0e94dc2f0e1a2e6efc9186f94c10be3c2944319446c378230e9a04; exit=0; EXPECT=matched; output-sha256=6984e8c71ebc4376b926aaa9a7eed9ffb06cb290db60e7eaa5bb6e5a8d4f5821; output-bytes=81322; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G4: der F12-Not-Aus setzt das Flag aus einem eigenen Faden, auch wenn der GUI-Faden blockiert ist; andere Tasten lösen nichts aus; Beenden gibt die Taste wieder frei
  CHECK: xvfb-run -a -s "-screen 0 1280x800x24" env BRIDGE_TEST_XVFB=1 PYTHONPATH=src:tests python3 -m unittest tests.test_koerper_linux_adapter.NotAusTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=63a314f9acccb25bdbfdf75811b4396d2b1b90b58e42aa601f2ce5e4dbfd49a5; exit=0; EXPECT=matched; output-sha256=ffceaa37e1a5a10e6391c9c84aac0c9eb1f102dacb3e95325f6d0e46e32997b6; output-bytes=6177; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G5: Sichtquelle (Vordergrund, offene Programme, Bildschirm) und Dateiwahl arbeiten wie ihre Windows-Gegenstücke
  CHECK: xvfb-run -a -s "-screen 0 1280x800x24" env BRIDGE_TEST_XVFB=1 PYTHONPATH=src:tests python3 -m unittest tests.test_koerper_linux_adapter.QuelleTests tests.test_koerper_linux_adapter.DateiwahlTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=abd16ad79b140d3408b88c671a4205ed35d5b2e5cadd96ffc900de22f812a353; exit=0; EXPECT=matched; output-sha256=333eaacf0c01c5b80f18f2d91dbb498d4107b70829915b963adc7180408d7933; output-bytes=7172; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries
