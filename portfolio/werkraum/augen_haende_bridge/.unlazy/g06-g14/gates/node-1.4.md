# Gates: G10 Hände als Ganzes

Scope: Zwei Agenten arbeiten unabhängig mit echten Eingaben; der Stop wirkt; Daniel behält die Kontrolle.

- [x] N1: die Teilstücke leaf-1.4.1 bis leaf-1.4.3 sind erfüllt
  CHECK: node /config/.claude/skills/unlazy/scripts/gate-check.mjs --root . --cwd . --approve --reverify --jobs 1 --timeout 1200 .unlazy/g06-g14/gates/leaf-1.4.1.md .unlazy/g06-g14/gates/leaf-1.4.2.md .unlazy/g06-g14/gates/leaf-1.4.3.md
  EXPECT: /ALL MET/
  EVIDENCE: automatic-evidence=v1; definition-sha256=d92446e42c58236ba280685bc2d9b6538a6447dcb17dd2b0e3f3a9b957fddea9; exit=0; EXPECT=matched; output-sha256=2e04fac1f2f332697f1918738825ce8484c94945e242529e5d17e25b1e72d561; output-bytes=8587; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] N2: mit echtem Relay-Prozess, echtem Starter, zwei Agenten mit dem echten Werkzeug und einer echten Engine: Lease, Klick, Tippen, Hotkey, zweiter Agent auf anderem Fenster, falsches Bild, Punkt außerhalb, Not-Aus mitten im Ziehen mit Lease-Entzug, Windows sieht nichts
  CHECK: xvfb-run -a -s "-screen 0 1280x800x24" env BRIDGE_TEST_XVFB=1 PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_g10_integration
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=3f3dda84974d10dd7862b64812956ae78629707c723a029cdaa243dca9f4af87; exit=0; EXPECT=matched; output-sha256=3d0342a810315e12c46599e3e2e02a73497ac2ad56dbc63af4a364f181f1d925; output-bytes=610; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] N3: das ganze Projekt bleibt grün bis auf die drei bekannten, umgebungsabhängigen Fehlschläge
  CHECK: PYTHONPATH=src:tests:client_vps timeout 1500 python3 tests/regression_alle.py 2>&1 | tail -3
  EXPECT: /REGRESSION OK/
  EVIDENCE: automatic-evidence=v1; definition-sha256=3e547f89d73f11a9c7184be0c0e4c7181f58c8b302eb6b9e2481e0f4071adacc; exit=0; EXPECT=matched; output-sha256=136c22981606d320b038a23c3de9784e84cc2e24452a29ff085089a0bd9a4902; output-bytes=162; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries
