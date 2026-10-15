# Gates: Restpunkte als Ganzes

Scope: alle Restpunkte sind belegt, und das ganze Projekt bleibt grün.

- [x] N1: das Teilstück leaf-1.9.1 ist erfüllt
  CHECK: node /config/.claude/skills/unlazy/scripts/gate-check.mjs --root . --cwd . --approve --reverify --jobs 1 --timeout 1200 .unlazy/g06-g14/gates/leaf-1.9.1.md
  EXPECT: /ALL MET/
  EVIDENCE: automatic-evidence=v1; definition-sha256=e141f96980b1f97a281e912e3b241e7a75faef68f057ef15e9521e95309f7acf; exit=0; EXPECT=matched; output-sha256=2abb71c3beea431bbee0f9c899c9c1b92205d3792382f5687e89b1f203ba24ac; output-bytes=4999; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] N2: mit echtem Relay, Starter, zwei Agenten und dem echten Werkzeug laufen G10, G11 und G13/G14 weiterhin durch
  CHECK: node -e "const {execSync}=require('child_process');const env={...process.env,BRIDGE_TEST_XVFB:'1',PYTHONPATH:'src:tests:client_vps:.'};execSync('xvfb-run -a -s \"-screen 0 1280x800x24\" python3 -m unittest tests.test_g10_integration tests.test_g11_integration tests.test_g13_g14_integration',{env,stdio:'inherit'});console.log('INTEGRATION-OK')"
  EXPECT: /INTEGRATION-OK/
  EVIDENCE: automatic-evidence=v1; definition-sha256=0bd15abdb22d47dad32dcf555a6e5a386519b9c39e9ce805da8393d3d276f7a0; exit=0; EXPECT=matched; output-sha256=0ab63e193b291429767e5d52d0781517b5ba197347b28dc79b3fc37a7bf9599a; output-bytes=2590; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries

- [x] N3: das ganze Projekt bleibt grün bis auf die drei bekannten, umgebungsabhängigen Fehlschläge
  CHECK: PYTHONPATH=src:tests:client_vps timeout 1500 python3 tests/regression_alle.py 2>&1 | tail -3
  EXPECT: /REGRESSION OK/
  EVIDENCE: automatic-evidence=v1; definition-sha256=3e547f89d73f11a9c7184be0c0e4c7181f58c8b302eb6b9e2481e0f4071adacc; exit=0; EXPECT=matched; output-sha256=b070cb0f17a0654135e7aef00993840f24a9cd5740a77d817f3526e69855af5b; output-bytes=162; shell=/bin/sh; cwd=/vps_root/werkraum/augen_haende_bridge; path=169990e33451/10 entries
