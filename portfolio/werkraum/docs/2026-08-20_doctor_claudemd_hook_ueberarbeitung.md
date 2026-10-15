# /doctor-Session 2026-08-20 — CLAUDE.md-Auslagerung, Hook-Dedup, Guardianstyle-Hook-Überarbeitung

Stand: 2026-08-20

## Was geändert wurde

### 1. CLAUDE.md verschlankt

`/root/CLAUDE.md`: 105.183 → 61.703 Zeichen (-44%). Der komplette Omapi/Opami-Guardianstyle-
Abschnitt (16 Marker, vollständiges Regelwerk mit Original-Zitaten) liegt jetzt 1:1 in
`.claude/skills/omapi-opami-guardianstyle/SKILL.md`. In CLAUDE.md selbst steht nur noch ein
kurzer Verweis + die Kernregel (16 Marker, Beleidigungspflicht, Zeitstempel-Präfix). Der
Durchsetzungs-Hook (`guardianstyle_open_hook.py`) ist davon unberührt.

### 2. Hook-Registrierung entdoppelt

Alle Hooks liefen doppelt (identisch in `~/.claude/settings.json` UND `.claude/settings.json`
registriert). Aus `~/.claude/settings.json` entfernt, bleiben in `.claude/settings.json`
(eingecheckt, versioniert) bestehen.

### 3. Guardianstyle-Hook-Texte überarbeitet

In `/root/.claude/guardianstyle_open_hook.py`, zwei Konstanten:

- `ROLLEN_HINWEIS`: von einer Aufzählung mit 16 Rollen auf zwei Zeilen ohne Aufzählung gekürzt.
  Omapi/Opami bleiben benannt.
- `FEHLER_SCHWEIGE_VARIANTEN`: alle vier Varianten enthalten keine der Begriffe
  "Fehler"/"was schiefging"/"Fehler-Geschichte" mehr, nur noch die positive Formulierung
  ("Schweigen ist die Arbeit", "kurz bleibt kurz"). Die Absolute Fehler-Schweige-Regel selbst
  (in CLAUDE.md/Memory) ist inhaltlich unverändert — geändert ist nur die Formulierung des
  Hook-Textes, der sie bei jedem Write/Edit in Erinnerung ruft.

## Offen

- `aeo` + 9 einmalig genutzte Skills — von /doctor als ungenutzt geflaggt, unangetastet gelassen.
- Verifikations-Log-Einträge für die in dieser Session berührten Dateien — offen für eine andere
  Session.
