# B4.5a — Terminal-Inspector und Live-Target-Switcher

EVIDENCE_VERSION: 1  
STAGE: B4.5a  
OUTCOME: PASS

## Scope

Diese Unteretappe beweist die erste Live-„Augen“-Schicht. Die sichtbare Bridge-Surface bleibt `surface:windows:bridge`; Linux-Konsole-Sessions werden als Targets entdeckt und nicht als zweite Surface dargestellt.

## Core

- `26` Python-Tests grün.
- Discovery prüft Service, Session-Pfad, Session-PID, Foreground-PID und Titel.
- Der Scrollback wird über `org.kde.konsole.Session.getAllDisplayedText` rückgelesen.
- Statische oder nicht erreichbare Ziele bleiben explizit `synthetic|unavailable`.

## Playwright-Belege

- `PW-B4.5A-01: PASS —` die sichtbare Surface zeigt `selected target`, `source`, `availability` und `capture` aus dem laufenden Registry-Zustand.
- `PW-B4.5A-02: PASS —` Playwright wählt eine entdeckte reale Konsole-Session über den sichtbaren Target-Switcher.
- `PW-B4.5A-03: PASS —` Playwright liest einen echten Snapshot mit `source=real`, `availability=available` und `status=observed` zurück.
- `PW-B4.5A-04: PASS —` Session-PID, Foreground-PID, Scrollback und `action.requested -> action.accepted` sind in DOM/Screenshot/Audit sichtbar.
- Screenshot: `/root/werkraum/augen_haende_bridge/tests/evidence/playwright_b4_5_target_switcher.png`.

## Bewusst noch offen

Diese Evidence schließt nicht die Eingabe-Rundreise. Es wurde kein Text in ein laufendes Codex-, Claude- oder Gemini-Terminal gesendet. Die nächste Unteretappe muss dafür ein ausdrücklich gekäfigtes Probe-Terminal und die Kette `accepted -> delivered -> echoed -> observed -> audited` verwenden.
