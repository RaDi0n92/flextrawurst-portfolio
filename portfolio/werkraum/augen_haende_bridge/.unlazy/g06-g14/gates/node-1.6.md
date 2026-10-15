# Gates: G12 Workflows als Ganzes

Scope: Ein Agent entwirft einen Ablauf, speichert und führt ihn aus, bei Abweichung greift ein Fallback, ein Teilauftrag geht mit Zustand und Unsicherheit an einen zweiten Agenten; Daniel startet, pausiert, setzt fort, bricht ab und wählt einen Zweig; frühere Durchläufe bleiben.

- [x] N1: die Teilstücke leaf-1.6.1 bis leaf-1.6.3 sind erfüllt
  CHECK: node /config/.claude/skills/unlazy/scripts/gate-check.mjs --root . --cwd . --approve --reverify --jobs 1 --timeout 1200 .unlazy/g06-g14/gates/leaf-1.6.1.md .unlazy/g06-g14/gates/leaf-1.6.2.md .unlazy/g06-g14/gates/leaf-1.6.3.md
  EXPECT: /ALL MET/
  EVIDENCE: automatic-evidence=v1; definition-sha256=672e8572e1f9e9053d364cc42915cda70f0e14ec13654f0425127a0e92d028b6; exit=0; EXPECT=matched; output-sha256=433c9fb8923debebf1c4c130c61796256c3d81a64513d82c8ffc5cf62d702d4d; output-bytes=8173; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] N2: mit echtem Relay-Prozess, echtem Starter und zwei Agenten mit dem echten Werkzeug: Entwurf, zwei Versionen, Delegation mit Zustand und Unsicherheit und Rückmeldung des Empfängers, Daniel-Gate mit Nein und Ja, Shadow ohne Wirkung, Regiesprüche (Pause, Weiter, Denk nach), Lernen nur durch Daniel
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_g12_integration
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=e04e60597e501e2405c00f023153676da9ea9d341b0590a31e345d1a468e6b5f; exit=0; EXPECT=matched; output-sha256=ed8fda2946fa25b2ed915affc9c07844a14a5f8e538c31b406aee4f0fcdf6331; output-bytes=99; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] N3: das ganze Projekt bleibt grün bis auf die drei bekannten, umgebungsabhängigen Fehlschläge
  CHECK: PYTHONPATH=src:tests:client_vps timeout 1500 python3 tests/regression_alle.py 2>&1 | tail -3
  EXPECT: /REGRESSION OK/
  EVIDENCE: automatic-evidence=v1; definition-sha256=3e547f89d73f11a9c7184be0c0e4c7181f58c8b302eb6b9e2481e0f4071adacc; exit=0; EXPECT=matched; output-sha256=dd98f74faaf2887c69eb1396d8090dfa2c93e40e9d224bdf75e2d356bf8f174f; output-bytes=162; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries
