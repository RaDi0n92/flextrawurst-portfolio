# Gates: Hauhaucs als Beobachter

OWNS: src/augen_haende_bridge/hauhaucs.py, tests/test_hauhaucs.py

Scope: Hauhaucs beobachtet bis zu drei Agenten; Aufnahme ohne Modell, Modellaufruf nur auf Daniels Wort; aufgezeichnet, zugestellt, verarbeitet getrennt; Bilder getrennt zuschaltbar; Budget und Stop wirken sofort; Quellen werden geprüft; die Hintergrundinstanz bleibt unberührt.

- [x] G1: Steuern, Zähler, Dokumentieren mit Quellenprüfung, Bilder, Budget, Stop und Fehler gegen ein Fake-Modell im OpenAI-Format
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_hauhaucs
  EXPECT: /^OK/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=1c722672dc1bb2d165f2d83d47418a58ebc1b5e09cc84b1042c37d4c0ef1e1df; exit=0; EXPECT=matched; output-sha256=86560bc7947996bb525a511093e8883a7429a1f005bcf13e91c60976c45bbccb; output-bytes=637; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G2: im Quelltext steht keine Anbindung an Port 11436 und kein Import aus dem Hauhau-System
  CHECK: node -e "const fs=require('fs');const s=fs.readFileSync('src/augen_haende_bridge/hauhaucs.py','utf8')+fs.readFileSync('client_vps/kapsel_dienst.py','utf8');if(/11436/.test(s.replace(/\(11436\)/g,'').split('\n').filter(l=>!/^\s*(\"\"\"|#)/.test(l)&&!/Port 11436/.test(l)).join('\n'))){console.log('GEFUNDEN');process.exit(1)}console.log('KEINE-ANBINDUNG-AN-11436')"
  EXPECT: /KEINE-ANBINDUNG-AN-11436/
  EVIDENCE: automatic-evidence=v1; definition-sha256=ee5923bc4887ca8b9304a8460181cfc07a118e8323dc58e857d92d9b9919132d; exit=0; EXPECT=matched; output-sha256=c6541398436ae83eca6087126466007a3d959d1461791b3b122c983feabf70ab; output-bytes=25; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G3: freies Gespräch mit dem Modell: der Verlauf liegt im Pult und geht mit, kein Beobachtungsbudget, geht auch nach Stop, Grenzen gelten, unbeantwortete Frage bleibt nicht hängen
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_hauhaucs.ChatTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=eddcd940a264dbf5ebfc658da83b5262327c667745768a1327fcbc52c4d9663d; exit=0; EXPECT=matched; output-sha256=06f4bc73ad2beda776ef9473c6c97e5ab023a7f52bcf7c149d33e333fd4394bc; output-bytes=103; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] G4: eine Fehlerantwort des Modellservers ist „erreicht, aber abgelehnt“: zu großer Prompt (400 mit n_prompt_tokens und n_ctx) heißt kontext_zu_gross mit Zahlen, andere Codes heißen modell_antwortet_mit_fehler; ein Aufruf zählt dann nicht gegen das Budget
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_hauhaucs.ServerFehlerTests
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=cd9f88a488d67ab45504399963bca963c654176489b60bd4b9c75c2ce65dfe43; exit=0; EXPECT=matched; output-sha256=e744a91dd9967ab39274010b3e5ef88a5e3cb805e84bb96a486142b17f25844e; output-bytes=601; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries
