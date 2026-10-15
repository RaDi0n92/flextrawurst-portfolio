# Gates: G13 Momentkapseln und Zeit-Scrubber als Ganzes

Scope: Ein Moment lässt sich einfrieren, ansehen, kommentieren, vergleichen und durch die Zeit scrubben, ohne dass das Original oder die Anwendung berührt wird.

- [x] N1: die Teilstücke leaf-1.7.1 und leaf-1.7.2 sind erfüllt
  CHECK: node /config/.claude/skills/unlazy/scripts/gate-check.mjs --root . --cwd . --approve --reverify --jobs 1 --timeout 1200 .unlazy/g06-g14/gates/leaf-1.7.1.md .unlazy/g06-g14/gates/leaf-1.7.2.md
  EXPECT: /ALL MET/
  EVIDENCE: automatic-evidence=v1; definition-sha256=b903bd354b585b9ada576863777126668565fb1fb843b5801162f4024ea6d94e; exit=0; EXPECT=matched; output-sha256=eea148204cc231547da732280fb8d024d111d35e1277c51e8ba1c73044d51235; output-bytes=2074; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] N2: mit echtem Relay-Prozess, echtem Starter und zwei Agenten mit dem echten Werkzeug: Kapsel erzeugen, unverändert prüfen, Ebene ergänzen, Zeitlinie lesen ohne Wirkung auf das Terminal
  CHECK: PYTHONPATH=src:tests:client_vps:. python3 -m unittest tests.test_g13_g14_integration
  EXPECT: /^OK$/m
  EVIDENCE: automatic-evidence=v1; definition-sha256=f09358c12aedeab8e5681daa9eba0fb7aee3b3b535453c32e8081563e1c977ac; exit=0; EXPECT=matched; output-sha256=19710bcaae8be74ed373c788b07ebab8adf16fe5c6c010d17ee9a26eefe6c1a4; output-bytes=99; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries
