# Schichten des gemeinsamen Arbeitskörpers

## Skill

Die beiden Skills unter `/root/werkraum/augen_haende_bridge/skills/` sind
direkte Verweise auf die kanonischen Codex-Quellen. Sie beschreiben Bauzyklus,
Fokusvertrag, Evidence, Zielbindung, Terminalparität, Scanner und Guardian.

## Harness und Runtime

Der echte Python-Arbeitskörper liegt unter
`/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/`. Besonders
wichtig sind `harness.py`, `guardian.py`, `contracts.py`, `policy.py`,
`target_registry.py`, `windows_scanner.py`, `terminal_channel.py`,
`terminal_renderer.py`, `transport.py` und `mcp_p0.py`.

## Tests und Evidence

Die Tests liegen unter `/root/werkraum/augen_haende_bridge/tests/`; Evidence
liegt unter `/root/werkraum/augen_haende_bridge/tests/evidence/`. Ein grüner
Test ist kein Ersatz für native Windows-/KDE-Evidence.

## Doku

Die Bridge-Dokumentation liegt live unter
`/root/werkraum/augen_haende_bridge/bridge_docs/` und stammt aus
`/root/werkraum/docs/augen_haende_bridge/`.
