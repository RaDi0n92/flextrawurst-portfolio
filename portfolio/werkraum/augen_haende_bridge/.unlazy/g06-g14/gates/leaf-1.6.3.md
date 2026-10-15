# Gates: Regiesprüche mit Wirkung

OWNS: src/augen_haende_bridge/koerper/regiespruch_wirkung.py, client_vps/ablauf_dienst.py, tests/test_ablauf_dienst.py

Scope: Jeder der 14 Regiesprüche hat eine ehrliche, kontrollierbare Wirkung oder ist ausdrücklich ein Gesprächswunsch. Kein Spruch hält heimlich eine fremde Runtime an.

- [x] G1: alle 14 Sprüche stehen in der Tabelle (gleich der Regieleiste); Pause pausiert den Ablauf und nicht den Prozess; Weiter, Warte kurz, Zurück (Zweig ab Checkpoint), Neu scannen, Ja/Nein/Go (offene Freigabe) wirken echt; reine Gesprächssätze und alle Sprüche ohne Ablauf werden als Gespräch zugestellt, nichts wird ins Terminal getippt, nichts angehalten
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_ablauf_dienst.RegieTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=d938af5c2b2b1b42e10d7d4cc9b91f41ca65dd9ae98e035c5ace0b1586e4fa41; exit=0; EXPECT=matched; output-sha256=6230753dbe740fcc8ea5e75adf859544a98f57c83f0fe8509596abec1581dd6d; output-bytes=110; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries
