# Gates: Loops und Goals (G15)

OWNS: src/augen_haende_bridge/loops.py, tests/test_loops.py

Scope: Wiederholung mit Budget, nachvollziehbarem Fortschritt, Start, Pause, Stop und einem echten Abschlussgrund; nach einem Stop beginnt nichts Neues.

- [x] G1: Budget (Läufe, Zeit), Goal-Bedingung, Fehlerreihe, Pause, Stop auch mitten im Durchlauf und in der Pause, Begrenzung gleichzeitiger Loops
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_loops
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=5044ce787f32f3b2f7a11eff1b1ee3f5b04d0ca228deffcabb44837aa0440b99; exit=0; EXPECT=matched; output-sha256=b198fa8e3e2b2c9b00ad7df4068da415df72cbb846247591a311982c853258f0; output-bytes=113; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries
