# Gates: Restpunkte und Recherchefunde (Goals G04, G09, G11, G12, G13)

OWNS: client_vps/terminal_launcher.py, src/augen_haende_bridge/ereignisprotokoll.py, src/augen_haende_bridge/koerper/weltdom_markierung.py, src/augen_haende_bridge/ablauf.py, tests/test_weltdom_markierung.py

Scope: was aus Netzrecherche und Nachprüfung als Lücke blieb, belegt je Goal.

- [x] G1: G04: ein Mehrbyte-Zeichen, das über zwei Lesestücke geht, bleibt im Terminalmodell und im Ereignisprotokoll ganz (jede Schnittstelle, byteweise)
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_koerper_terminal_modell.StueckgrenzenTests tests.test_kapseln.StueckgrenzenProtokollTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=d1f0e52f012e02c9307060c3807b15adc9c46d47523393b317b735630df82191; exit=0; EXPECT=matched; output-sha256=120fcf1e1b1ef6883b716f1b33b4fbea79c7089f1d1ff950e98c9608d82abb42; output-bytes=102; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G2: G09: Nachrichten kommen je Empfänger in der gesendeten Reihenfolge an, Text und Enter vermischen sich nie
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_terminal_launcher.ZustellReihenfolgeTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=d2968e9ea142aad60eba5647ad305884370befb06362ea4c205fdd1f90eafeea; exit=0; EXPECT=matched; output-sha256=0276289a917b36926f4a82fd7b7e1660cb3eb443b96c998d41c5d3cf04007a39; output-bytes=98; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G3: G13: ein Zweig aus einer Kapsel startet erst nach frischer Messung; das Modellgespräch wird in der Kapsel festgehalten, ohne Modellaufruf wiedergegeben und ins Mischpult geladen (rückgängig machbar)
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_kapsel_dienst
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=e63544b51c2bf4d78a3f4d55084c825a1a97baba83a2d345f16cb26ffe7e900e; exit=0; EXPECT=matched; output-sha256=eab4281419f49474c6773f172eab4705e82da9e9196e5418e92a366609bcb99e; output-bytes=107; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G4: G12: ein Ablauf kann erwartete Knoten nennen; fehlt etwas oder lässt sich nicht messen, startet er nicht von selbst (mit ausdrücklichem „trotzdem“ geht es)
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_ablauf_dienst.AlternTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=7b256b2c1d3a28f03472588fc299f0e0a9165fcf257ece381871808eca0b1599; exit=0; EXPECT=matched; output-sha256=209637c5270ea62667d3505f25f6e8e713fd220b3020983b799e40ff6ae4138a; output-bytes=105; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G5: G11: Set-of-Mark: Bild mit nummerierten Rahmen um bedienbare gemessene Knoten, Tabelle Nummer zu Kennung, begrenzt, als Frame zum Agenten, über Starter, Körper und Werkzeug
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_weltdom_markierung tests.test_koerper_weltdom_anbindung
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=2ac1950e1a292dea4cb75dcdcbcfe027264f4941b5324b0ae586b3523a1c4b82; exit=0; EXPECT=matched; output-sha256=c2ec203816ca7884e1092912579293b82bf8adc07f7365b4a2645823692b7ac2; output-bytes=636; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries
