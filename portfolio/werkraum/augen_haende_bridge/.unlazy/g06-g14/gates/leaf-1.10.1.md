# Gates: Seeds (G15)

OWNS: src/augen_haende_bridge/seeds.py, client_vps/seed_dienst.py, tests/test_seeds.py, tests/test_seed_dienst.py

Scope: aus einer Erfahrung (Kapsel) wird ein Vorschlag, der nach Daniels Freigabe an Ziele ausgeliefert, wiedergefunden und zurückgenommen wird; Originale und fremde Arbeit bleiben erhalten.

- [x] G1: Lebenslauf, Versionen, Zielumfang nur mit Daniels ausdrücklichem Eintrag, Einfügen als markierter Block mit gesichertem Original, Rücknahme ohne fremde Änderungen anzurühren, kaputte Dateien
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_seeds
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=77897650c64d51082940ef1f388c32be8dc4539c8231e8e6d73481a4b15b18ae; exit=0; EXPECT=matched; output-sha256=36e632bbf6589bac8037ace7030ead9f8c8947bdb0f34d0e4b025484e5464ee7; output-bytes=114; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G2: im Starter: Vorschlag prüft Form und Herkunft (Kapsel muss existieren), Auslieferung braucht Daniels Ja über die offenen Fragen, Dateien auch im Profil selbststaendig, Eigentumsregeln, Werkzeug streng, Daniel zieht über die Oberfläche zurück
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_seed_dienst
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=6a578c58762528932fe601700d1682ef317cc7a6d1192e95830a7f3f711187b7; exit=0; EXPECT=matched; output-sha256=f66099ddc9435278e329bca4741a2121be512ea7ad6d97bf79b718411089d61d; output-bytes=116; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries
