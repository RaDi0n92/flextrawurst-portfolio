# Gates: Kontext-Mischpult

OWNS: src/augen_haende_bridge/kontextmischpult.py, tests/test_kontextmischpult.py

Scope: eine effektiv leere Sitzung, die Daniel gezielt füllt, kürzt, bearbeitet, zurückspringt, exportiert; Schätzung und Messung getrennt und beschriftet.

- [x] G1: leere Sitzung, ID-genaue Auswahl, Bearbeiten auf Satzebene, Leeren, Halbieren, Zurückspringen, Einspeisen ohne Antwort, Felder, Einmalfeedback, Grenzen, Export und Import, Anzeige von Schätzung und Messung getrennt
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_kontextmischpult
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=0f4b324201f04a9241feeecc044a33fa6f952db4d06caf2b0d504bc8802b01c3; exit=0; EXPECT=matched; output-sha256=2b390ad0ecc0187ae4c9907c4b66fcd5cf984adc11b10becfdaa3a91cfef8ccd; output-bytes=120; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries
