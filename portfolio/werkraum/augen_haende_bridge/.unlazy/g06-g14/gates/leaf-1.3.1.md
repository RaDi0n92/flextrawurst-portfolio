# Gates: Agentenregister, Gruppen, Delegation, Pause

OWNS: src/augen_haende_bridge/koerper/agentenregister.py, client_vps/terminal_launcher.py, client_vps/bridge_cli.py, src/augen_haende_bridge/transport.py, src/augen_haende_bridge/koerper/anwendung.py, src/augen_haende_bridge/koerper/erster_koerper.py, tests/test_koerper_agentenregister.py

Scope: Mehrere Sitzungen desselben Stroms, verschiedene Agenten und ein gemeldeter Unteragent bleiben richtig zugeordnet. Gruppen, Nachrichten ohne Echo, Aufträge mit Status nur vom Empfänger, Pause und Fortsetzen der Prozessgruppe, Beenden auch pausiert.

- [x] G1: das Register hält Agenten, Gruppen, Eltern und Kinder, Aufträge und die Fähigkeitsmatrix richtig (Namen, Schleifenschutz, Auftragsstatus nur vom Empfänger, Speichern und tolerantes Laden, Grenzen)
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_koerper_agentenregister.RegisterTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=ed89d1df91acefa8418bcab548cd0791b0ced43c80b409018a79ea161abd755e; exit=0; EXPECT=matched; output-sha256=ce895947b8ffcb2e77addf8382970fd1c07ecab9486fbbfca209319a47c37f4f; output-bytes=110; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G2: im echten Starter mit echten PTY-Sitzungen: zwei Sitzungen desselben Stroms bleiben getrennt, Nachrichten (einzeln, Gruppe) kommen im Empfänger an und nie beim Absender, Aufträge laufen mit Rückmeldung, ein Unteragent ist gemeldet aber nicht ansprechbar
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_koerper_agentenregister.StarterTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=d2aa100523004607514f174c62e159c9c90024349b73ec22786a492fa1b45529; exit=0; EXPECT=matched; output-sha256=1ac55ef4635d8f4d36d32bc2b24d1c336e3f143d27d68767e21c8bbd926c7448; output-bytes=106; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G3: Pause hält die Prozessgruppe wirklich an (Prozesszustand T), Fortsetzen lässt sie die gepufferte Eingabe abarbeiten, Beenden funktioniert auch pausiert; die Oberfläche bietet es im Menü an und zeigt „pausiert“
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_koerper_agentenregister.StarterTests.test_pause_haelt_die_prozessgruppe_wirklich_an_und_fortsetzen_laesst_sie_weiterlaufen tests.test_koerper_agentenregister.StarterTests.test_beenden_funktioniert_auch_bei_einem_pausierten_agenten tests.test_koerper_agentenregister.KoerperPauseTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=8c80d813f5c4acdef159d8913ed2b6ed7146f06c3d63a651ba2ead35ef41516a; exit=0; EXPECT=matched; output-sha256=8fc8eb80a1a0f4929ef266dbb64ffeba7f4fa18fddc6b9c06472719f4b5ced4d; output-bytes=103; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G4: der Relay kennt den Zustand „paused“ und die Nachricht `terminal_steuern` streng (nur Desktops, nur pause/fortsetzen)
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_koerper_agentenregister.RelayPruefungTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=7a459628fef43bab9202f75b39ec7729ada62644ce29838e256e7144db5a8655; exit=0; EXPECT=matched; output-sha256=15e1b3902e99e62bc7f061b84c3f571d085b893e42f8ed52ac52d3ab8d134652; output-bytes=98; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G5: das Werkzeug des Agenten kennt alle neuen Befehle und die bisherigen Tests des Starters, der Oberfläche und des Relays bleiben grün
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_koerper_agentenregister.CliTests tests.test_terminal_launcher tests.test_terminal_launcher_startnachricht tests.test_koerper_anwendung tests.test_koerper_erster_koerper tests.test_bridge_agent tests.test_koerper_anwendung_relay
  EXPECT: /^OK/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=439fa0614d15afe8702547979e7a74f7fb16213fa7a78c27dddafe33e633b3f8; exit=0; EXPECT=matched; output-sha256=04690bdc501f90bb8c604d4cdcbd42f18506cedc15f82b9f33fb43f43f6e14f3; output-bytes=247; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries
