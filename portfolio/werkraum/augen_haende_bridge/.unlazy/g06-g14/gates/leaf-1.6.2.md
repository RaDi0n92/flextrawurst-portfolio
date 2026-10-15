# Gates: Modi und Delegation

OWNS: src/augen_haende_bridge/ablauf_modi.py, client_vps/ablauf_dienst.py, src/augen_haende_bridge/koerper/anwendung.py, src/augen_haende_bridge/transport.py, tests/test_ablauf_modi.py

Scope: Free, Shadow, Witness, Daniel-Gate, Learning und Delegated Learning einzeln und kombiniert; Lernen anfangs aus; Daniel steuert über die Oberfläche.

- [x] G1: jeder Modus wirkt einzeln und in Kombinationen (Shadow gewinnt, Daniel-Gate fragt vor jeder handelnden Aktion, Tor fragt immer, Witness meldet ohne aufzuhalten, Lernen nur nach ausdrücklichem Einschalten und nie aus Simuliertem)
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_ablauf_modi
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=ebd65f95a436c1e7dbbe4e11ff05bf9b17f0376c54d50371276cbb0dd8687109; exit=0; EXPECT=matched; output-sha256=41a5e10536a78de71d4945b6059a46285fac10e3ca27f4281ac362961a9a1428; output-bytes=116; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G2: im Starter: Freigabe durch Daniel führt aus, Verweigern und Schweigen nicht, Aufgabenbereich aus hält handelnde Knoten an, nur Daniel schaltet das Lernen ein, Steuerung nur von fähigen Desktops
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_ablauf_dienst.DienstTests.test_daniel_gate_ueber_den_starter_freigeben tests.test_ablauf_dienst.DienstTests.test_aufgabenbereich_aus_haelt_handelnde_knoten_an tests.test_ablauf_dienst.DienstTests.test_daniel_steuert_alle_laeufe_und_hat_den_lernschalter tests.test_ablauf_dienst.DienstTests.test_steuern_nur_von_faehigen_desktops tests.test_ablauf_dienst.DienstTests.test_ein_agent_steuert_nur_eigene_laeufe_und_kann_das_lernen_nicht_einschalten
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=78538d4dbe30698813dc24613850eddac5b63e48285307ec8be1bce96a64367b; exit=0; EXPECT=matched; output-sha256=0e628cb3078fa3ef493bd5a6614aae5fc2e52bb11383774d0738b3c32af009c1; output-bytes=103; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G3: das Relay prüft die neuen Nachrichten streng, die Oberfläche zeigt Läufe, Freigaben, Start und Lernschalter nur mit neuem Starter und sendet die Aktion, das Werkzeug kennt alle Ablauf-Befehle und gibt langen Befehlen einen langen Timeout
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_ablauf_dienst.RelayTests tests.test_ablauf_dienst.KoerperTests tests.test_ablauf_dienst.CliTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=21a712d9979569f447e213a413eb17a244ac08088c62ff01f5de3a989451c449; exit=0; EXPECT=matched; output-sha256=e7868349f80d90e9674de9c2df12e50a116d24331e4cdf921e14d11d317a3981; output-bytes=107; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries
