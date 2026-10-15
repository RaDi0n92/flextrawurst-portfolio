# HANDOFF CAPSULE — Weltbetriebssystem

**Diese Datei zuerst lesen nach: `/clear`, Accountwechsel, neuer Session.**

---

## 1. Aktueller Stand

| | |
|---|---|
| HEAD | `459cf09` feat(governance): add global governance matrix and approval workflow |
| Branch | master |
| Remote | keines |
| Tests | 1336/1336 grün (Stand: Ring 20 abgeschlossen) |
| Arbeitsfokus | Ring 21 — Build Discipline, Doku-Fundament (kein Code, keine Tests) |

Bereits erstellte Ring-21-Artefakte:
- `docs/33_WELTBETRIEBSSYSTEM_RING_21_BUILD_DISCIPLINE_PLAN.md`
- `RING_INDEX.md`
- `HANDOFF_CAPSULE.md` (diese Datei)

Noch ausstehend in Ring 21: nichts Zwingendes — Doku-Phase abgeschlossen.

---

## 2. Wichtigste Architekturregel

- Eventstream, Governance, Search, WorldRun, Admin: Kontroll- und Prüfgrundlagen — keine Runtime-Aktivierung
- Keine Organe aktivieren
- Keine UI ohne explizite Freigabe
- Kein AI-Subsystem, kein Postgres, kein Scheduler, kein Daemon
- FeatureSlots bleiben deaktiviert
- Vollständige Ring-Tabelle: → `RING_INDEX.md`

---

## 3. Token-Disziplin

- Keine künstliche 100-Test-Pflicht
- Neue Tests nur für neue Verantwortung
- Bestehende Tests laufen lassen, keine Regression akzeptiert
- Keine langen Wiederholungsblöcke in Berichten
- Gezielt lesen, nicht alles blind
- Bericht maximal 15 Zeilen

---

## 4. Nächste Schritte

1. `RING_INDEX.md` und `HANDOFF_CAPSULE.md` bei jedem Ring-Abschluss aktualisieren
2. Offene Entscheidungen C, E, F, G aus Ring 21 mit Daniel klären (→ `RING_INDEX.md` Abschnitt Offene Entscheidungen)
3. Danach entscheiden: Build-Disziplin-Code (`ring-index.ts`, `ring_manifest.json`) oder direkt Prozesskamera-Plan

---

## 5. Prozesskamera-Anker

Daniel will später alle heutigen Systemwesen als sichtbare, zoombare Prozesskörper:

**Wesen:** GENI, dak+gord-system, Systemweiser, sechs namelessAI-Flarum-Wesen, spätere Reader/Writer/Runner

**Was sichtbar wird:** Zustand, letzte Aktion, Modus (denkt/liest/schreibt/wartet/blockiert), Datei-/Forum-/Event-/Audit-/Search-/Governance-/WorldRun-Bezug

**Nicht als neue Bewohner — als beobachtbare laufende Prozesse.**

→ Implementierung erst nach Ring 21 Freigabe.

---

## 6. Startprotokoll für neue Session

```
1. RING_INDEX.md lesen
2. HANDOFF_CAPSULE.md lesen  (diese Datei)
3. git log --oneline -5
4. git status --short
5. Auftrag von Daniel abwarten
6. Bei Unsicherheit: Status prüfen, nicht raten
```

---

## 7. Verbotene Drift

- Nicht automatisch weiterbauen ohne Auftrag
- Nicht direkt Organe bauen oder Features aktivieren
- Keine Testmasse erzeugen (Tests ohne echte neue Verantwortung)
- Nicht `.planning/`, `.aider/`, `out/`, `ROADMAP.md` stagen
- Nicht committen ohne explizite Daniel-Freigabe
