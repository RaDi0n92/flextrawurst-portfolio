# Gates: Ablaufsprache und Durchläufe

OWNS: src/augen_haende_bridge/ablauf.py, client_vps/ablauf_dienst.py, client_vps/bridge_cli.py, tests/test_ablauf.py

Scope: Agenten entwerfen deklarative, versionierte Abläufe auf der vorhandenen Harness, speichern und führen sie aus. Abweichungen führen zu Fallbacks oder ehrlichem Anhalten; Durchläufe bleiben erhalten; ein neuer Ablauf braucht keinen neuen Code.

- [x] G1: die Sprache ist streng (Bedingungen, Referenzen und Suchen raten nie, ungültige Abläufe haben feste Fehlercodes), der Speicher legt jede Änderung als neue Version an, übersteht den Neustart und überspringt kaputte Dateien; ein Ablauf aus einer neuen JSON-Datei läuft mit demselben Ausführer
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_ablauf.SpracheTests tests.test_ablauf.SpeicherTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=6bbad58cfbe4d5efb596f9b1c338a491b8f0befdeb1977344c7fc51fad521499; exit=0; EXPECT=matched; output-sha256=60bb849356ffbc091f601e17fc6ae0b2eb5e26d734d433da020c6e775efbf97f; output-bytes=106; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G2: die Ausführung prüft vorher und nachher, nimmt bei geändertem Zustand den Fallback, hält ohne Fallback ehrlich an, meldet Ausnahmen als Signal, rät keine Argumente, begrenzt Schleifen, pausiert/setzt fort/bricht ab vor dem nächsten Knoten, zweigt ab Checkpoint ab ohne den alten Lauf zu ändern, übergibt Zustand und Unsicherheit bei Delegation, und das Replay führt nichts aus
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_ablauf.LaufTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=57ba6a1f2ce877120046eae068a4136d3c297a10b339680ff7eddbdc038ae786; exit=0; EXPECT=matched; output-sha256=84d8772355e571485804666521d02c4d9d3dc524b3389ba7950c37dc4c70d799; output-bytes=111; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G3: im Starter laufen Abläufe mit den echten Handlern (Nachricht an eine echte Sitzung, Delegation mit Rückmeldung des Empfängers, Schweigen ist nicht ok), der Agent steuert nur eigene Läufe, Daniel alle
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_ablauf_dienst.DienstTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=af65e232165237974af2c5ad6fc994f6ee6c41893c718be53ea0f61ee89b6d60; exit=0; EXPECT=matched; output-sha256=bad4e4d0398ea9c4029c41b2f62f4ff4433bb4279fef911e1c064866c31dc8b4; output-bytes=113; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries
