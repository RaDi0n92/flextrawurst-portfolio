# Gates: Not-Aus, hängende Tasten, Daniels Übernahme

OWNS: src/augen_haende_bridge/koerper/uebernahme.py, probes/uebernahme_wine.py, tests/test_koerper_eingabe_adapter.py

Scope: Der lokale Stop wirkt trotz Verbindungsabbruch und hängendem GUI-Faden, nichts bleibt gedrückt, Daniels eigene Eingabe hält die Hände an, seine bewusste Ausnahme ist möglich, und beides lässt den Not-Aus bestehen. Zeiten werden gemessen und nie als Zusage geschrieben.

- [x] G1: F12 über den echten Hook stoppt ein laufendes Ziehen, auch bei hängendem GUI-Faden; ein Verbindungsabbruch stoppt es ebenfalls; danach ist keine Maustaste und keine Taste gedrückt; die Not-Aus-Taste selbst wird nicht gesendet; nach dem Not-Aus geht es erst nach Freigabe weiter
  CHECK: xvfb-run -a -s "-screen 0 1280x800x24" env BRIDGE_TEST_XVFB=1 PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_koerper_eingabe_adapter.X11StopTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=b773c8d9173054d2b3feee18c492ed20609b62bad8556b8cdbbeeab46c147d3d; exit=0; EXPECT=matched; output-sha256=776da3e322f0851cdf2d547c33bb79eeb6b864252574d488b06beef86c35cd80; output-bytes=758; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G2: Daniels Eingabe (X11, gezählt gegen die eigenen Ereignisse) hält die Hände an und lässt los, sperrt sie für die Pause, löst bei eigener Eingabe nie einen falschen Alarm aus; mit der Ausnahme laufen die Hände weiter, der Not-Aus gilt trotzdem
  CHECK: xvfb-run -a -s "-screen 0 1280x800x24" env BRIDGE_TEST_XVFB=1 PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_koerper_eingabe_adapter.X11UebernahmeTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=87d9eea7a0f51904c2a7406dc7cdc3fd57e662b8354c7520aca7981d2e81a53e; exit=0; EXPECT=matched; output-sha256=b8ed8c963b0e2d27ab36984b78de3211af482d453acce18c2b9c601887fa405a; output-bytes=615; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G3: unter Wine unterscheiden die Hooks eigene (injizierte) Eingabe von fremder Eingabe, die Hände stoppen bei fremder und arbeiten nach der Pause weiter
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_koerper_eingabe_adapter.WineUebernahmeTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=ecff613a58826b87926d7a01a3745556cb3c030a0b7064dda3d48f186a144eec; exit=0; EXPECT=matched; output-sha256=e89ba168fb0210fe7c8e422496b1bdef69a3d29fc63659b9b59d5c1e9ec98bea; output-bytes=559; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G4: in der Engine mit Attrappe: Not-Aus und Verbindungsabbruch mitten im Ziehen lassen sofort los, ein Stopp-Zustand sperrt weitere Aufträge bis zur Freigabe, scheiternde Tasten hinterlassen nichts Gedrücktes
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_koerper_eingabe_adapter.EngineTests.test_not_aus_mitten_im_ziehen_laesst_sofort_los_und_meldet_abgebrochen tests.test_koerper_eingabe_adapter.EngineTests.test_verbindungsabbruch_stoppt_und_laesst_los tests.test_koerper_eingabe_adapter.EngineTests.test_scheitert_eine_taste_mitten_in_der_kombination_bleibt_nichts_haengen tests.test_koerper_eingabe_adapter.EngineTests.test_backend_fehler_beim_klick_wird_fehler_und_laesst_los
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=8c4875f9a6cbfa79e163520789dcb3f77e256c43ab2cc0c328f161a1a0c3312b; exit=0; EXPECT=matched; output-sha256=cc6df7a1e40d841d0953742559c5bc4fb0c96e336082ed40f38d48b79a84491e; output-bytes=102; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries
