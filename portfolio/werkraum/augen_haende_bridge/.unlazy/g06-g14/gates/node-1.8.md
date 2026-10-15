# Gates: G14 Hauhaucs-Beobachter und Mischpult als Ganzes

Scope: Daniel wählt Agenten, Hauhaucs zeichnet auf, das Mischpult zeigt genau, was hinausgeht, und nur ein ausdrücklicher Auftrag ruft das Modell; Stop und Budget wirken sofort.

- [x] N1: die Teilstücke leaf-1.8.1 und leaf-1.8.2 sind erfüllt
  CHECK: node /config/.claude/skills/unlazy/scripts/gate-check.mjs --root . --cwd . --approve --reverify --jobs 1 --timeout 1200 .unlazy/g06-g14/gates/leaf-1.8.1.md .unlazy/g06-g14/gates/leaf-1.8.2.md
  EXPECT: /ALL MET/
  EVIDENCE: automatic-evidence=v1; definition-sha256=dc2ed199d2b035a7a2d89190d8cf3a8885ff4655ecabdad2271223ec39f4d062; exit=0; EXPECT=matched; output-sha256=d0112f408cdb7be25cb9d5c71eb935f8a3561f755fc9bbfc734b75b1ce7b9ca0; output-bytes=2090; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] N2: mit echtem Relay, Starter und Werkzeug und einem Fake-Modell: aufzeichnen ohne Modellaufruf, zustellen, Dokumentieren auf Wort, Bilder nur zugeschaltet, Pult leeren und zurück, Stop verweigert sofort
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_g13_g14_integration
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=f09358c12aedeab8e5681daa9eba0fb7aee3b3b535453c32e8081563e1c977ac; exit=0; EXPECT=matched; output-sha256=a1e6b01849ee9a74f94139d0e0a534cc1efb2c27d45157ed633367869cdad61b; output-bytes=99; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] N3: das ganze Projekt bleibt grün bis auf die drei bekannten, umgebungsabhängigen Fehlschläge
  CHECK: PYTHONPATH=src:tests:client_vps timeout 1500 python3 tests/regression_alle.py 2>&1 | tail -3
  EXPECT: /REGRESSION OK/
  EVIDENCE: automatic-evidence=v1; definition-sha256=3e547f89d73f11a9c7184be0c0e4c7181f58c8b302eb6b9e2481e0f4071adacc; exit=0; EXPECT=matched; output-sha256=136c22981606d320b038a23c3de9784e84cc2e24452a29ff085089a0bd9a4902; output-bytes=162; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries
