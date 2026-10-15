# B4.5b — gekäfigte Live-Terminalprobe

EVIDENCE_VERSION: 1  
STAGE: B4.5b  
OUTCOME: PASS

## Sichtbarer Beweis

- `PW-B4.5B-01: PASS —` Playwright erzeugt ausschließlich ein eigenes, isoliertes Konsole-Probe-Terminal und bindet es als `terminal-probe` mit `source=real`.
- `PW-B4.5B-02: PASS —` Die Policy akzeptiert die Terminalaktion nur mit der expliziten `terminal`-Capability und `proof-terminal-lease`.
- `PW-B4.5B-03: PASS —` Der Handadapter sendet nur den validierten Marker über `pty-controller:unix-socket` als `printf`-Probe; keine freie Shell-Payload wird angenommen.
- `PW-B4.5B-04: PASS —` Der Marker `AUGEN_HAENDE_PROBE_0001` erscheint im echten Konsole-Scrollback mit Prompt, ausgeführter Probe und Ausgabe.
- `PW-B4.5B-05: PASS —` Die sichtbare Surface und der Audit zeigen exakt `accepted -> delivered -> echoed -> observed -> audited`.
- `PW-B4.5B-06: PASS —` Nach dem Beleg wird nur das von der Proof-Runtime erzeugte Probe-Terminal geschlossen; die vier vorher vorhandenen Konsole-Sessions bleiben bestehen.
- Screenshot: `/root/werkraum/augen_haende_bridge/tests/evidence/playwright_b4_5b_terminal_probe.png`.

## Plattformgrenzen, die der Beweis sichtbar gemacht hat

- `org.kde.konsole.Session.sendText` und `runCommand` wurden im laufenden Konsole-Profil mit `org.freedesktop.DBus.Error.AccessDenied` und „Security sensitive DBus API is disabled in the settings“ abgewiesen.
- `wtype` konnte in der laufenden Wayland-Komposition wegen fehlendem Virtual-Keyboard-Protokoll nicht verwendet werden.
- Deshalb wird für das eigens erzeugte Probe-Terminal ein kontrollierter PTY-Controller verwendet. Konsole bleibt die sichtbare echte Oberfläche; der Rücklesebeleg kommt weiterhin aus `getAllDisplayedText`.
- Diese Probe ermächtigt keinen Zugriff auf laufende Codex-, Claude- oder Gemini-Terminals. Für sie bleibt die Bridge bei read-only Inspection, bis Daniel ein konkretes Target und eine eigene Lease freigibt.
