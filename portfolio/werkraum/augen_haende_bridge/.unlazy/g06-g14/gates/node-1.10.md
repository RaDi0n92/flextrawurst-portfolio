# Gates: G15 als Ganzes

Scope: Daniel erzeugt aus einem realen Umweg einen Seed, wählt Empfänger und Zieltyp, gibt frei, findet die Wirkung am richtigen Ziel wieder und nimmt sie zurück; Loops und Goals haben Budget, Stop und echten Abschlussgrund.

- [x] N1: die Teilstücke leaf-1.10.1 und leaf-1.10.2 sind erfüllt
  CHECK: node /config/.claude/skills/unlazy/scripts/gate-check.mjs --root . --cwd . --approve --reverify --jobs 1 --timeout 1200 .unlazy/g06-g14/gates/leaf-1.10.1.md .unlazy/g06-g14/gates/leaf-1.10.2.md
  EXPECT: /ALL MET/
  EVIDENCE: automatic-evidence=v1; definition-sha256=701e48cc094c34d101871cd1305107e861ff504b92fb1eab6a61c20ca77a5de0; exit=0; EXPECT=matched; output-sha256=fad6dc968da817c9b4f32d4f97ae554c7e8ea2988fe7516e0d5c46a8845842ce; output-bytes=3059; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] N2: mit echtem Relay, Starter, zwei Agenten, dem echten Werkzeug und einem Desktop als Daniel: Vorschlag, Daniels Ja, Zustellung, Daniels Rücknahme
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_g13_g14_integration
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=f09358c12aedeab8e5681daa9eba0fb7aee3b3b535453c32e8081563e1c977ac; exit=0; EXPECT=matched; output-sha256=354e6e55bd7cb79e787102fab91d18f946379da1e6c9d050fe4d8a8df4eb1252; output-bytes=99; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] N3: das ganze Projekt bleibt grün bis auf die drei bekannten, umgebungsabhängigen Fehlschläge
  CHECK: PYTHONPATH=src:tests:client_vps timeout 1500 python3 tests/regression_alle.py 2>&1 | tail -3
  EXPECT: /REGRESSION OK/
  EVIDENCE: automatic-evidence=v1; definition-sha256=3e547f89d73f11a9c7184be0c0e4c7181f58c8b302eb6b9e2481e0f4071adacc; exit=0; EXPECT=matched; output-sha256=ad184ad835f3e7d0881c0e6e680848cb71159c3c505c7b8cb7926258fcea95ac; output-bytes=162; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries
