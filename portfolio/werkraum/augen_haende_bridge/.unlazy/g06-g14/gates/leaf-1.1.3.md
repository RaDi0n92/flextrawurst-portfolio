# Gates: Relay-Routing und Anzeigeort

OWNS: client_vps/anzeigeorte.py, client_vps/desktops.json, client_vps/bridge_server.py, client_vps/terminal_launcher.py, src/augen_haende_bridge/transport.py, src/augen_haende_bridge/koerper/anzeigeort.py, src/augen_haende_bridge/koerper/anwendung.py, src/augen_haende_bridge/koerper/erster_koerper.py, tests/test_anzeigeort.py, tests/test_bridge_server_anzeigeort.py

Scope: Der Relay kennt mehrere Desktops (Windows, KDE 1, KDE 2) als eigene, getrennt angemeldete Anzeigeorte. Ein Terminal gehört einer Sitzung (Laufort Host/vd1/vd2), wird auf genau einem Anzeigeort gezeigt und hat ein Arbeitsziel, das davon unabhängig auf einem anderen Desktop liegen darf. Anzeigeort wechselt, ohne dass die Sitzung ihre Identität verliert; Bilder und Hände gelten nur für den Zielort.

- [x] G1: aus `desktops.json` entstehen je Desktop eigene Anmeldedaten (Windows behält seine bisherigen Kennungen, die KDE-Desktops bekommen private Token-Dateien mit Rechten 0600, nie im Log), der Relay nimmt alle Desktops gleichzeitig an, und doppelte oder schwache Zugangsdaten werden abgewiesen
  CHECK: PYTHONPATH=src:tests:client_vps python3 -m unittest tests.test_anzeigeort.KonfigurationsTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=98488a517fc57dcb2d3f307c40446625f39776c09636a6555fba4515196532a2; exit=0; EXPECT=matched; output-sha256=5bf704d6a53aa11c1f6f50fb3fc51ff163320afad0127d3e61ca37f2c382b6f0; output-bytes=112; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G2: ein Terminal erscheint nur auf seinem Anzeigeort (Ausgabe, Zustand, Liste); Eingaben von einem anderen Desktop werden abgewiesen; Wechsel des Anzeigeorts entfernt es vom alten, zeigt es auf dem neuen mit Wiederaufnahme und unveränderter Sitzungsidentität
  CHECK: PYTHONPATH=src:tests:client_vps python3 -m unittest tests.test_anzeigeort.RoutingTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=914647c7feb747b78ad906d19824be806d1d69566a36b9b72bf615a8ac39561c; exit=0; EXPECT=matched; output-sha256=7c758af7411e05fc2e6c4fb89045f7a03d9a5957d5305092903a23a66373d034; output-bytes=107; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G3: das Arbeitsziel ist vom Anzeigeort unabhängig: Bilder kommen nur vom Zielort an, Bilder anderer Desktops werden abgewiesen und gezählt, und ein verschwundenes oder ersetztes Ziel bindet nie still ein anderes
  CHECK: PYTHONPATH=src:tests:client_vps python3 -m unittest tests.test_anzeigeort.ZielTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=8d31af3b547768d0673b7c0edf5e9dc13fac850fd19f60b099b9bb41d53e4e60; exit=0; EXPECT=matched; output-sha256=60bb849356ffbc091f601e17fc6ae0b2eb5e26d734d433da020c6e775efbf97f; output-bytes=106; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G4: Host, Arbeitsplatz (Anzeigeort), Sitzung und Ziel werden getrennt gemeldet, samt sichtbarer Fähigkeit für inaktive, minimierte und verdeckte Ziele
  CHECK: PYTHONPATH=src:tests:client_vps python3 -m unittest tests.test_anzeigeort.AnzeigeTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=7c6720ba7daa130e7ab7da9ebd5fed465cb701721ddaf346ba98da667d18d3fd; exit=0; EXPECT=matched; output-sha256=80144f3bf12d071a1497821467ab02765712cb11da3f547a5e2b5cf79f938e9a; output-bytes=102; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G5: mit einem echten Relay, echtem Starter und einer echten PTY-Sitzung laufen drei verbundene Desktops gleichzeitig; Start auf KDE 1, Ausgabe, Wechsel auf Windows mit Wiederaufnahme, Eingabe und Beenden stimmen
  CHECK: PYTHONPATH=src:tests:client_vps python3 -m unittest tests.test_bridge_server_anzeigeort
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=0d3617468d7af286bd5580ab307ea780c04b3e331b5add548b62014def49a16d; exit=0; EXPECT=matched; output-sha256=9f69a8d5405082a3496e47dda1d2e3fc275567b34ba849dd7cfb1787583a86bb; output-bytes=99; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G6: der Körper kennt die Anzeigeorte: Menü „Anzeigeort“ (Wechsel), Auflistung mit Online-Zustand, Entfernen und Aufnehmen des Körpers beim Wechsel, ohne dass der Windows-Ablauf sich ändert
  CHECK: PYTHONPATH=src:tests:client_vps python3 -m unittest tests.test_anzeigeort.KoerperTests tests.test_anzeigeort.KoerperAnwendungTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=0f23563137d491649c3fa7455935e91e9b37c9fac4821f3b32a2f76948616504; exit=0; EXPECT=matched; output-sha256=dbe758c0c680006d7470814f86ecd9d4edba4c186dac4407b7f7ffa5e00295fc; output-bytes=116; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries
