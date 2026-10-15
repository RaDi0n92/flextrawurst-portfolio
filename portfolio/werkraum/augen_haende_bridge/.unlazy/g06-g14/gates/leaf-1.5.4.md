# Gates: WorldDOM-Profile

OWNS: src/augen_haende_bridge/koerper/weltdom_profile.py, tests/test_weltdom_profile.py

Scope: gemeinsam Angelegtes pro Programm, Seite oder Spiel als Profil speichern (versioniert, nichts überschrieben oder gelöscht), über Namen wiederfinden und mit relativer Lage in einem anderen Fenster laden.

- [ ] G1: Speichern, Versionen, Laden mit relativer Lage, nichts geraten ohne Fenster, Ausblenden statt Löschen, kaputte Dateien, strenge Befehlsprüfung, Dienst
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_weltdom_profile
  EXPECT: /^OK$/m
