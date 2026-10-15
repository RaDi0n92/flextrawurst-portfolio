# Gates: Zeit-Scrubber

OWNS: src/augen_haende_bridge/scrubber.py, tests/test_kapseln.py

Scope: durch den aufgezeichneten Verlauf laufen und sehen, was damals war — nur lesen, keine Wirkung auf Anwendungen.

- [x] G1: Marken, Schritte vor und zurück, Zustand an jedem Zeitpunkt mit benannten Lücken, ohne Wirkung auf die Anwendung
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_kapseln.ScrubberTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=fdc02a68bb60e5c1e35baaf8f85123aba094fd18fa30ebacf31f7bcf23d894f5; exit=0; EXPECT=matched; output-sha256=feabb4add9e2ca3374e538560634d1ec97dc4f4ce89aab12f3d726e36ea9b2f6; output-bytes=102; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries
