# Gates: Ereignisprotokoll und Momentkapseln

OWNS: src/augen_haende_bridge/ereignisprotokoll.py, src/augen_haende_bridge/kapseln.py, tests/test_kapseln.py

Scope: Das Protokoll zeichnet ohne Modell auf und sagt, was fehlt; Kapseln frieren einen Moment unveränderlich ein, nennen Quellen und Lücken, tragen Ebenen, Tags, Folge-Kapseln und Vergleiche.

- [x] G1: das Ereignisprotokoll erfasst, begrenzt, persistiert, benachrichtigt Zuhörer ohne anzuhalten und meldet verworfene Terminalstücke
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_kapseln.ProtokollTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=419d61ecf3c07ed486f3dbfe3362498feed8be31fab5b5a6cbd34d4b8f4cc734; exit=0; EXPECT=matched; output-sha256=464e0ee629edf74de09ef21e4232fbcedc26588ff7cc23c470f47fe2da88c255; output-bytes=103; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G2: Kapseln in allen sechs Entstehungsarten, unverändert prüfbar (Hash), Lücken benannt, Ebenen/Tags/Lernstrecken/Folge/Vergleich getrennt vom Original
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_kapseln.KapselTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=2471f5ea91f1184488b78f399bc46e5403e53b2351e490679617d209710c2675; exit=0; EXPECT=matched; output-sha256=3c58f6fae53a49c10a944751ab5c7b7e4674bc4597b0d51e28644fbca89e12a6; output-bytes=111; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G3: der Starter holt Zeichnungen, Bindung und WorldDOM-Knoten über den bestehenden Körper-Befehl in die Kapsel (ohne neu zu messen); antwortet der Körper nicht, steht der Grund als Lücke da
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_kapsel_dienst
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=e63544b51c2bf4d78a3f4d55084c825a1a97baba83a2d345f16cb26ffe7e900e; exit=0; EXPECT=matched; output-sha256=edb4e2159c923ea45a32656078835cdf531c3d7b414c670dd786978875cb0678; output-bytes=101; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries
