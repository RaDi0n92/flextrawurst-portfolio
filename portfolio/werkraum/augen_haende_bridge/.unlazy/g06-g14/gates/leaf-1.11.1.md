# Gates: Praxistest als Graph und Skill

OWNS: src/augen_haende_bridge/praxis/lauf.py, src/augen_haende_bridge/praxis/szenario_menschlich.json, client_vps/praxis_dienst.py, skills/bridge-praxistest/SKILL.md, tests/test_praxis_lauf.py, tests/test_praxis_dienst.py, tests/test_skill_praxistest.py

Scope: ein Programm führt zwei Agenten Schritt für Schritt durch den Praxistest auf Augenhöhe: Ansage in der eigenen Raute vor jedem Schritt, Lesezeit, Handeln mit echten Spuren, eigener Blick, Zuschauer, freundlich und nicht zu umgehen; ein Skill erklärt es.

- [x] G1: der Graph (Knoten, Kanten) bildet Ansage, Lesezeit, Handeln, Sehen, Urteil, Zuschauer, Klären, Planänderung, Zurückstellen und Wiederholung ab; Rollen wechseln; Reihenfolge ist nicht zu überspringen; Fehlermeldungen sind freundlich und nennen den nächsten Schritt
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_praxis_lauf
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=31361a7cefa6aa7aebf93eff475d959bebbf86fd7c949a826900e6436300db55; exit=0; EXPECT=matched; output-sha256=b03146dce3866e98a0d25d48a96bb742835fdd51c121c18eec59f2a149c1c4bf; output-bytes=125; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G2: im Starter öffnen nur echte Spuren aus dem Ereignisprotokoll (Hände, Bilder, Befehle des richtigen Agenten, nach der Ansage) die Knoten; say, schreibe und see hinterlassen Spuren; die Ansage wird in die Raute des Handelnden getippt; das Protokoll entsteht live; das Werkzeug ist streng
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_praxis_dienst
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=e1eff257de1130b8666890d77cdac0bc21014645ebf1b0bd69260a8037e362a8; exit=0; EXPECT=matched; output-sha256=9ce00e249971d4000af3a4607a20c22b0d14c19412a59a08501f307176f0321f; output-bytes=109; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G3: der Skill ist gesund: Kopf, Länge, Verweise, jeder genannte Befehl existiert im Werkzeug, die Vorlage der Karte erfüllt die eigene Ansage-Regel
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_skill_praxistest
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=f4b1511f4c9829bf42e3cb05498b860e576d069da11fa8c82fc39d0e78a3ec63; exit=0; EXPECT=matched; output-sha256=a25b5619af971eae96a8c9d37ebc69133b4c28e990455e210be0507206df182c; output-bytes=104; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G4: Szenarien wählbar nach Namen (nur schlichte Namen), Rollenmodus wählbar; der Skill skill-schreiben mit Gerüst-Skript (überschreibt nie, erzeugt gültiges Szenario) und Prüfer (findet fehlende Verweise, nicht vorhandene Befehle, Platzhalter, zu lange Beschreibung, drohenden Ton, ungültige Szenarien); beide Skills bestehen die eigene Prüfung
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_skill_schreiben tests.test_skill_praxistest tests.test_praxis_lauf.SzenarienTests tests.test_praxis_dienst.SzenarioWahlTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=545f52a31bb956c0cb42f22522cca9f0c5ca83448dc91acfb9399a79267f9cf9; exit=0; EXPECT=matched; output-sha256=9fa03b455ed561e6cb3461a42db056127dc392b309d6c95903b893a639506457; output-bytes=1579; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries
