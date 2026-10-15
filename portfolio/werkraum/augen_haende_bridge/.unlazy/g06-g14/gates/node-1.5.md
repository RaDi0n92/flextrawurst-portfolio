# Gates: G11 WorldDOM als Ganzes

Scope: Ein echter Knoten, ein erschlossener Knoten und ein bewusst angelegter Anker sind mit Herkunft, Konfidenz und Aktualität sichtbar; ein semantischer Auftrag wird am richtigen Ziel ausgeführt und zurückgelesen; ein nicht auflösbarer Knoten löst nichts aus.

- [x] N1: die Teilstücke leaf-1.5.1 bis leaf-1.5.3 sind erfüllt
  CHECK: node /config/.claude/skills/unlazy/scripts/gate-check.mjs --root . --cwd . --approve --reverify --jobs 1 --timeout 1200 .unlazy/g06-g14/gates/leaf-1.5.1.md .unlazy/g06-g14/gates/leaf-1.5.2.md .unlazy/g06-g14/gates/leaf-1.5.3.md
  EXPECT: /ALL MET/
  EVIDENCE: automatic-evidence=v1; definition-sha256=4fc72770931e574f2799bcf4c741063700006c71e3a20e1816ef04565256458f; exit=0; EXPECT=matched; output-sha256=5a1842d797718a02079278e85010ad669bffaff5869aed8875dcb09e5a878ae6; output-bytes=7438; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] N2: mit echtem Relay-Prozess, echtem Starter, zwei Agenten mit dem echten Werkzeug und dem echten WorldDOM-Dienst gegen einen echten Chromium: Messen, Handeln mit Lease und Rücklese, Anker, Zeigen ohne Wirkung, Einfügen mit Beleg, Layoutwechsel
  CHECK: xvfb-run -a -s "-screen 0 1280x800x24" env BRIDGE_TEST_XVFB=1 PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_g11_integration
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=59a79d3a83159f75f4b09235e621465c617c4e0b7bfaa73ada76850e628a81f5; exit=0; EXPECT=matched; output-sha256=7c8d276195f4b6b90f780474432be7f72e7dbc2e9a127280010a0b76bb7917f0; output-bytes=99; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] N3: das ganze Projekt bleibt grün bis auf die drei bekannten, umgebungsabhängigen Fehlschläge
  CHECK: PYTHONPATH=src:tests:client_vps timeout 1500 python3 tests/regression_alle.py 2>&1 | tail -3
  EXPECT: /REGRESSION OK/
  EVIDENCE: automatic-evidence=v1; definition-sha256=3e547f89d73f11a9c7184be0c0e4c7181f58c8b302eb6b9e2481e0f4071adacc; exit=0; EXPECT=matched; output-sha256=136c22981606d320b038a23c3de9784e84cc2e24452a29ff085089a0bd9a4902; output-bytes=162; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries
