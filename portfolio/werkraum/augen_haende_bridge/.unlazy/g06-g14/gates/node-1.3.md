# Gates: G09 Multi-Agent als Ganzes

Scope: Mehrere Agenten arbeiten zusammen; Neu starten und Anbinden bleiben getrennte Aktionen; die Adapterwege sind benannt.

- [x] N1: die Teilstücke leaf-1.3.1 und leaf-1.3.2 sind erfüllt
  CHECK: node /config/.claude/skills/unlazy/scripts/gate-check.mjs --root . --cwd . --approve --reverify --jobs 1 --timeout 900 .unlazy/g06-g14/gates/leaf-1.3.1.md .unlazy/g06-g14/gates/leaf-1.3.2.md
  EXPECT: /ALL MET/
  EVIDENCE: automatic-evidence=v1; definition-sha256=a036cd1d9c5e3dab5226577d944a4a8c06a1861249ec392dd92321f616f9b14c; exit=0; EXPECT=matched; output-sha256=4069de2c46cd7b26deb49ca6e1e9ccf045ad63239d4afd5aa85aeba0369255bd; output-bytes=4484; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] N2: mit echtem Relay-Prozess, echtem Starter und zwei verbundenen Desktops: ein Agent wird gestartet, pausiert und fortgesetzt (Zustand kommt an beiden Enden an), Anbinden einer laufenden Sitzung startet keine neue
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_g09_integration
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=ddee01cc96de855f36fc58143a7d4d8992ea048cdbefa1f3aa879220aa24d658; exit=0; EXPECT=matched; output-sha256=8ce36b92094a0cdb13dd7ba948c6c3dc72a52609c7c4230a9122b1d5f1b0e691; output-bytes=99; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] N3: das ganze Projekt bleibt grün bis auf die drei bekannten, umgebungsabhängigen Fehlschläge
  CHECK: PYTHONPATH=src:tests:client_vps timeout 1500 python3 tests/regression_alle.py 2>&1 | tail -3
  EXPECT: /REGRESSION OK/
  EVIDENCE: automatic-evidence=v1; definition-sha256=3e547f89d73f11a9c7184be0c0e4c7181f58c8b302eb6b9e2481e0f4071adacc; exit=0; EXPECT=matched; output-sha256=136c22981606d320b038a23c3de9784e84cc2e24452a29ff085089a0bd9a4902; output-bytes=162; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries
