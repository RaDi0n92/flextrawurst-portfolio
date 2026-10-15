# Gates: Steuerprofile, Leases, Controller-Erkennung, Anschluss

OWNS: src/augen_haende_bridge/koerper/steuerprofil.py, src/augen_haende_bridge/koerper/haende_anbindung.py, src/augen_haende_bridge/koerper/haupt.py, src/augen_haende_bridge/koerper/anwendung.py, src/augen_haende_bridge/koerper/erster_koerper.py, client_vps/terminal_launcher.py, client_vps/bridge_cli.py, src/augen_haende_bridge/transport.py, src/augen_haende_bridge/koerper/bilderstrom.py, tests/test_koerper_steuerprofil.py, tests/test_koerper_haende_anbindung.py

Scope: Hintergrundbedienung und geteilte Maus sind unterscheidbare Profile; höchstens ein Agent hält die Lease auf ein Ziel; virtuelle Controller werden nur erkannt (Ziel vier, Treiber nur nach Daniels Wort); die Hände sind über Relay, Starter, Werkzeug und Körper angeschlossen.

- [x] G1: Steuerprofile unterscheiden Hintergrund und geteilte Maus, wirken im Käfig, unbekannte Namen ergeben das vorsichtigste Profil; die Controller-Erkennung installiert und öffnet nichts und meldet Treiber, Rechte und das Ziel von vier Controllern
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_koerper_steuerprofil
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=b0381f9ba16ca972d9410f9fda7fb463eae175f7f8dea097531841564b9c4fbd; exit=0; EXPECT=matched; output-sha256=643c7cfc3921e5830e047bed28578bc933677c101c9c5a9f6610b6207052d03c; output-bytes=109; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G2: die Lease ist je Ziel exklusiv, läuft ab, wird verlängert, freigegeben und bei Stopp oder Desktop-Verlust entzogen
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_koerper_eingabe_adapter.LeaseTests tests.test_koerper_haende_anbindung.StarterTests.test_lease_nehmen_ist_exklusiv_und_pro_ziel tests.test_koerper_haende_anbindung.StarterTests.test_stoppgruende_entziehen_die_lease_keine_heimliche_wiederaufnahme tests.test_koerper_haende_anbindung.StarterTests.test_geht_ein_desktop_offline_verfallen_seine_leases tests.test_koerper_haende_anbindung.StarterTests.test_not_aus_entzieht_alle_leases
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=a91c92b024861c9b2aa0ae72a96bf77a0d4f134fcfbf1eb78718d410606563c7; exit=0; EXPECT=matched; output-sha256=15b6959c4b12dd6f945b24d9e3e04dd6c7ce3edab642c4f08b105e2acc9d5501; output-bytes=106; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G3: der Starter nimmt Hände-Aufträge nur mit Lease, gebundenem Fensterziel am eigenen Ort und gültiger Aktion an, leitet sie an den Desktop des Ziels, trennt die Aussagen im Ergebnis und nennt den Ausgang „unbekannt“, wenn der Körper schweigt
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_koerper_haende_anbindung.StarterTests tests.test_koerper_haende_anbindung.RelayPruefTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=7197c433703ac10410a7c809e7eb86c3738acc7b3cee594ad0fd6636e831981e; exit=0; EXPECT=matched; output-sha256=35b036696173609494d121f1af8ab788e0efc02a4d47bebe9e80604932879fc0; output-bytes=116; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G4: der Körper führt den Auftrag mit dem gesendeten Bild, den Rechten, dem Profil und der Lease aus, meldet Fehler statt sie zu verschlucken, stoppt bei Verbindungsabbruch ohne den GUI-Faden, und die Anbindung (Engine, Protokoll mit Rotation, Beobachtung) ist ehrlich über Verfügbarkeit
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_koerper_haende_anbindung.AnwendungTests tests.test_koerper_haende_anbindung.AnbindungTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=d825cc9078453d2c61680a132c7936a7da80052ea52abde0dc9356592bf33f57; exit=0; EXPECT=matched; output-sha256=e6200ac859357c16c8cb8510b71eb578ea5a2b0b26026ee7cafd60dc78513c0c; output-bytes=111; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G5: die bisherigen Tests des Körpers, des Starters und des Relays bleiben grün
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_terminal_launcher tests.test_anzeigeort tests.test_koerper_anwendung tests.test_koerper_erster_koerper tests.test_koerper_anwendung_relay tests.test_koerper_agentenregister tests.test_koerper_anwendung_bilderstrom tests.test_koerper_fensteraufnahme
  EXPECT: /^OK/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=f65b248aaf5c9181f004c62cb6932d4c71bb2d508bfd80d5ebe669fe9546c251; exit=0; EXPECT=matched; output-sha256=6e69a4c2a564a457e469ae9f45bed272d05e6b0310ce1404f705f149735305bf; output-bytes=1363; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G9: virtuelle Controller: strenge Aktionen, dieselben Sperren wie die Hände (Lease, Profil, Not-Aus, Übernahme, Verbindung), alles losgelassen nach jedem Auftrag, Abbruch wirkt sofort, ein echtes uinput-Gerät entsteht und verschwindet; ohne Treiber ein Grund statt eines Absturzes
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_controller_adapter
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=a8eb9dd4eec76ecd58ced99d59e4dd0cd0755c9b7cfd2fda3a8faf693ddc506e; exit=0; EXPECT=matched; output-sha256=730bc9d024fd1434b089cafa220040f45d05a811420f2d3055813b34c4d1c88f; output-bytes=113; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries
