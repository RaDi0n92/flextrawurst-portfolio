# Ring 20 — Global Governance Matrix + Approval Workflow + Control Coverage Plan

## 1. Ziel von Ring 20

Ring 20 schließt die Kontrollschicht des Weltbetriebssystems.

Ring 17 hat einzelne Aktionen mit CommandIntent und Ledger versehen.
Ring 18 hat alle Systemdaten durchsuchbar gemacht.
Ring 19 hat den Weltlauf mit Zustandssemantik und Gates versehen.

Ring 20 zieht diese Inseln zusammen zu einer einzigen, vollständigen
Governance-Matrix: Jede kritische Systemhandlung wird zentral beschreibbar
als kontrollierbarer Governance-Akt mit Rolle, Permission, Gate, Approval,
CommandIntent, Ledger, Audit, Search und Policy-Notiz.

Das Ergebnis ist kein UI, kein Auth-System, keine Runtime.
Das Ergebnis ist ein strukturierter Rahmen, der bestimmt:

  Welche Handlung braucht was — und was blockiert sie, wenn etwas fehlt.

---

## 2. Warum Ring 20 vor Organ-Planung kommt

Organe sind der nächste Komplexitätssprung.
Jedes Organ bringt neue Aktivierungspfade, neue Seiteneffekte,
neue Rollenfragen.

Wenn die Governance-Matrix fehlt, wird jedes Organ ad-hoc kontrolliert —
mit lokalen Permissions, lokalen Gates, lokalen Audit-Ideen.
Das erzeugt Inkonsistenz, blinde Flecken und unkontrollierte Handlungen.

Ring 20 legt den gemeinsamen Rahmen fest, bevor irgendein Organ gebaut wird.
Jedes spätere Organ kann sich dann auf diese Matrix beziehen.

---

## 3. Governance-Aktionsklassen

Die folgenden Aktionsklassen sind vollständig oder teilweise bereits modelliert
(Ring 17–19) und müssen in Ring 20 normiert werden:

| Klasse                    | Status Ring 17–19        | Ring-20-Aufgabe                            |
|---------------------------|--------------------------|--------------------------------------------|
| Feature activation        | CommandIntent + Gate     | Approval-Stufe normieren                   |
| Feature deactivation      | CommandIntent + Ledger   | Rollback-Hinweis ergänzen                  |
| Import approval           | CommandIntent + Gate     | Zwei-Schritt-Stufe prüfen                  |
| Slot activation           | Gate vorhanden           | CommandIntent-Pflicht prüfen               |
| WorldRun pause            | Gate + Audit + Search    | Approval-Stufe festlegen                   |
| WorldRun resume           | Gate + Audit + Search    | Approval-Stufe festlegen                   |
| WorldRun freeze           | Gate + Audit + Search    | Emergency-Variante definieren              |
| WorldRun stop             | Gate + Audit + Search    | Rollback-Hinweis, Global-Lock-Relation     |
| WorldRun lock             | Gate + Audit + Search    | Relation zu Global Lock definieren         |
| Read-only export          | Gate vorhanden           | Audit-Pflicht prüfen                       |
| Worldblick                | Gate + read-only         | Kein weiterer Kontrollbedarf               |
| ConceptGuard report       | Existiert                | Override-Frage klären (→ Entscheidung G)   |
| Policy setting            | CommandIntent            | Audit-Pflicht, Ledger-Pflicht              |
| Future organ activation   | Noch nicht vorhanden     | Governance-Slot freihalten                 |
| Search inspection         | Corpus vorhanden         | Governance-Aktion? (→ Entscheidung F)      |
| Emergency stop            | WorldRun stop vorhanden  | Global-Lock-Variante definieren            |
| Global lock               | Nicht vorhanden          | Neue Aktionsklasse — Ring 20 Kern          |

---

## 4. Rollen und Permissions

### Bestehende Rollen (aus Ring 17)

| Rolle           | Beschreibung                                      |
|-----------------|---------------------------------------------------|
| daniel_root     | Volle Kontrolle. Alle Permissions.                |
| operator        | Delegierte Kontrolle. Subset der Permissions.     |
| observer        | Nur view-Permissions. Keine Änderungen.           |
| system_process  | Automatische Systemaktionen. Sehr eingeschränkt.  |

### Bestehende Permissions (aus Ring 17)

Alle worldrun.*, feature.*, import.*, slot.*, export.*, policy.*, concept_guard.*

### Ring-20-Ergänzungen (vorgeschlagen)

| Permission              | Beschreibung                                           |
|-------------------------|--------------------------------------------------------|
| governance.view         | Governance-Matrix lesen                                |
| governance.global_lock  | Globalen Lock setzen (nur daniel_root)                 |
| governance.audit_full   | Vollständigen Audit lesen (ggf. daniel_root + operator)|
| governance.approve      | Approval-Schritt ausführen                             |
| governance.override_cg  | ConceptGuard-Override (→ Entscheidung G)               |

### Rollenmapping (vorgeschlagen)

| Aktion                  | daniel_root | operator | observer | system_process |
|-------------------------|-------------|----------|----------|----------------|
| Feature aktivieren      | ja          | vorbereiten | nein  | nein           |
| Feature deaktivieren    | ja          | nein     | nein     | nein           |
| Import freigeben        | ja          | ja       | nein     | nein           |
| WorldRun pause          | ja          | ja       | nein     | nein           |
| WorldRun freeze         | ja          | nein     | nein     | nein           |
| WorldRun stop           | ja          | nein     | nein     | nein           |
| Global lock             | ja          | nein     | nein     | nein           |
| Policy setzen           | ja          | nein     | nein     | nein           |
| ConceptGuard override   | offen       | nein     | nein     | nein           |
| Search inspection       | ja          | ja       | ja       | ja (view)      |

---

## 5. Gate-Typen

Alle Gates prüfen: Rolle + Permission + Systemzustand + Blocker.

| Gate-Typ             | Beschreibung                                          |
|----------------------|-------------------------------------------------------|
| PermissionGate       | Hat der Actor die nötige Permission?                  |
| StatusGate           | Erlaubt der aktuelle Systemzustand diese Aktion?      |
| LockGate             | Ist kein globaler oder lokaler Lock aktiv?            |
| ApprovalGate         | Liegt ein vorangegangener Approval-Schritt vor?       |
| DryRunGate           | Wurde ein Dry-Run zuerst ausgeführt? (optional)       |
| ConceptGuardGate     | Verstößt die Aktion gegen verbotene Konzepte?         |

Gates blockieren, sie löschen nicht. Jedes Gate produziert einen GateReport.

---

## 6. Approval-Stufen

| Stufe | Name              | Bedeutung                                             |
|-------|-------------------|-------------------------------------------------------|
| 0     | None              | Keine Freigabe nötig. Direkt ausführbar mit Permission|
| 1     | Self-Approve      | Actor und Approver identisch (daniel_root only)       |
| 2     | Two-Step          | Zuerst Request, dann separater Approve-Schritt        |
| 3     | Daniel-Only       | Nur daniel_root darf approven, egal wer requested     |

Zuordnung (vorgeschlagen):

| Aktion                  | Approval-Stufe |
|-------------------------|----------------|
| Feature view            | 0              |
| Export erstellen        | 0              |
| WorldRun pause          | 1              |
| WorldRun resume         | 1              |
| Import freigeben        | 2              |
| Feature aktivieren      | 3 (Daniel-Only)|
| WorldRun freeze         | 3 (Daniel-Only)|
| WorldRun stop           | 3 (Daniel-Only)|
| Global lock             | 3 (Daniel-Only)|
| Policy setzen           | 3 (Daniel-Only)|

→ Offene Entscheidung C: Gibt es tatsächlich Zwei-Schritt-Freigaben?

---

## 7. CommandIntent-Pflicht

Jede Governance-Aktion oberhalb von Stufe 0 braucht einen CommandIntent.

CommandIntent-Pflicht bedeutet:
- Keine stille Mutation
- Kein direkter Funktionsaufruf ohne Intent-Objekt
- Jeder Intent bekommt eine command_id
- Jeder Intent landet im Ledger

Ausnahmen (read-only, keine Mutation):
- Search inspection
- Worldblick
- ConceptGuard report lesen
- Governance-Matrix lesen

---

## 8. Ledger-Pflicht

Alle Governance-Aktionen mit CommandIntent landen im CommandLedger.

LedgerEintrag enthält mindestens:
- command_id
- command_type
- actor_id + role
- target_type + target_id
- status (accepted / rejected / pending)
- created_at
- reason

Ledger ist append-only.
Kein Ledger-Eintrag wird gelöscht.
Kein Ledger-Eintrag wird rückwirkend verändert.

---

## 9. Audit- und Search-Pflicht

Jede ausgeführte Governance-Aktion erzeugt:
- einen Audit-Eintrag (append-only, typ-spezifisch)
- ein SearchDocument im WorldRun-, Admin- oder Governance-Layer

SearchDocuments tragen:
- source_ids (command_id, audit_id oder run_id)
- layer (z.B. "worldrun_control", "admin", "governance")
- tags (z.B. "governance", "global_lock", "approval")

Suchbarkeit gilt als strukturelle Eigenschaft, nicht als optionales Feature.

→ Offene Entscheidung F: Soll Search jede Governance-Aktion automatisch
  auffindbar machen — also auch ohne expliziten buildCorpus-Aufruf?

---

## 10. Policy- und ConceptGuard-Pflicht

### Policy-Pflicht

Jede Änderung einer Policy braucht:
- CommandIntent mit command_type set_policy
- Ledger-Eintrag
- Audit-Eintrag
- SearchDocument

Policy-Änderungen sind nie still.
Kein policy.set ohne sichtbaren CommandIntent.

### ConceptGuard-Pflicht

Alle Ring-20-Implementierungen laufen durch den ConceptGuard.
Neue verbotene Muster werden bei Bedarf ergänzt.

Neue vorgeschlagene Guard-Muster für Ring 20:
- "Governance Matrix ist UI"
- "Approval ersetzt Ausführung"
- "Global Lock löscht Daten"
- "Policy ist heimliche Manipulation"
- "Ledger ist optional"
- "CommandIntent ist Ausführung"

→ Offene Entscheidung G: Soll ConceptGuard Override überhaupt möglich sein
  oder nur Report? Empfehlung: Nur Report. Override wäre ein Systemrisiko.

---

## 11. Kritische Verbote

```
Registriert ≠ gebaut.
Gebaut ≠ aktiv.
Aktiv ≠ unkontrolliert.
CommandIntent ≠ Ausführung.
Approval ≠ Runtime.
Governance Matrix ≠ UI.
Global Lock ≠ Datenlöschung.
Policy ≠ heimliche Manipulation.
Ledger ≠ optional.
Gate ≠ bloße Konvention.
Zwei-Schritt ≠ Umgehung.
Operator ≠ daniel_root.
```

---

## 12. Vorgeschlagene Dateien für spätere Implementierung

```
kernel/governance/
  governance_action.ts          — Typen: GovernanceActionClass, ApprovalLevel
  governance_matrix.ts          — Die vollständige Matrix als Datenstruktur
  governance_gate.ts            — Kombinierter Gate-Check für alle Klassen
  governance_approval.ts        — Approval-Stufen-Logik
  governance_ledger_bridge.ts   — Verbindet Governance mit CommandLedger
  governance_audit.ts           — Append-only Audit für Governance-Aktionen
  global_lock.ts                — GlobalLock-Zustand + Gate + Audit

kernel/search/search_corpus.ts  — buildSearchCorpusFromGovernanceAudit (ergänzen)
kernel/search/search_document.ts — "governance_audit_entry" (ergänzen)
kernel/concept_guard/concept_guard.ts — neue Muster für Ring 20 (ergänzen)

docs/32_WELTBETRIEBSSYSTEM_RING_20_GLOBAL_GOVERNANCE_PLAN.md — dieses Dokument
```

---

## 13. Testplan für spätere Implementierung

Mindestens 100 Tests. Prüfbereiche:

**GovernanceMatrix (20 Tests)**
- Alle Aktionsklassen vorhanden
- Jede Klasse hat Rolle, Permission, ApprovalLevel
- Keine Klasse ist ohne Gate definiert
- Matrix ist vollständig, kein Lücken-Fehler

**GovernanceGate (20 Tests)**
- PermissionGate blockiert bei fehlender Permission
- StatusGate blockiert bei falschem WorldRun-Status
- LockGate blockiert wenn GlobalLock aktiv
- ApprovalGate blockiert wenn kein Prior-Approval vorliegt
- DryRunGate optional aber konsistent
- Gate-Report enthält alle Felder

**GovernanceApproval (15 Tests)**
- Stufe 0: direkt ausführbar
- Stufe 1: Self-Approve erlaubt für daniel_root
- Stufe 2: Two-Step blockiert ohne vorangehenden Request
- Stufe 3: nur daniel_root kann approven

**GlobalLock (15 Tests)**
- GlobalLock setzt locked=true systemweit
- GlobalLock blockiert Feature-Aktivierung (→ Entscheidung E)
- GlobalLock blockiert WorldRun resume/start
- GlobalLock blockiert Import-Approval
- GlobalLock löscht keine Daten
- GlobalLock ist nur von daniel_root setzbar
- GlobalLock ist auditierbar
- GlobalLock ist durchsuchbar

**GovernanceLedgerBridge (10 Tests)**
- Jede Governance-Aktion > Stufe 0 landet im Ledger
- Ledger-Eintrag enthält command_id, actor, type, status
- Append-only: altes Ledger wird nicht mutiert

**GovernanceAudit (10 Tests)**
- Audit-Eintrag für jede ausgeführte Aktion
- Append-only
- Keine Events erzeugt

**SearchIntegration (10 Tests)**
- governance_audit_entry in SearchDocumentKind
- layer "governance"
- source_ids vorhanden
- Filter nach governance-Tags funktioniert

**ConceptGuard (10 Tests)**
- Alle neuen verbotenen Muster erkannt
- Erlaubte Sprache passiert ohne Fehler

---

## 14. Offene Entscheidungen für Daniel

**A. Gibt es neben daniel_root später weitere echte Adminrollen?**

Aktuell ist daniel_root die einzige Vollzugriffs-Rolle.
operator hat delegierte, eingeschränkte Kontrolle.
Frage: Soll es künftig weitere daniel-Äquivalente geben
(z.B. für Co-Admins, externe Treuhänder)?

Empfehlung: Nein, für jetzt. daniel_root bleibt singulär.

---

**B. Darf operator jemals aktivieren oder nur vorbereiten?**

Derzeit darf operator Requests stellen, aber nicht selbst approven
bei Daniel-Only-Stufe (Stufe 3).
Frage: Darf operator für bestimmte Aktionsklassen selbstständig aktivieren
(z.B. WorldRun pause), ohne Daniels Freigabe?

Empfehlung: WorldRun pause/resume ja. Feature-Aktivierung nein.

---

**C. Gibt es Zwei-Schritt-Freigaben (Approval-Stufe 2)?**

Stufe 2 bedeutet: Request jetzt, Approve separat später.
Das erfordert persistenten Pending-Zustand im Ledger.
Frage: Ist das für Ring 20 nötig oder zu früh?

Empfehlung: Ring 20 definiert die Semantik, implementiert aber keinen
Pending-State-Daemon. Stufe 2 bleibt strukturell beschrieben, aber
die Ausführung ist read-only / deterministisch modelliert.

---

**D. Braucht jede kritische Aktion ein Dry-Run zuerst?**

Derzeit ist dry_run optional (CommandIntent.dry_run boolean).
Frage: Soll DryRunGate bei Stufe-3-Aktionen erzwingen,
dass zuerst ein dry_run=true Command abgesetzt wird?

Empfehlung: Nein erzwingen, ja empfehlen. Erzwingen würde die
Semantik unnötig verkomplizieren.

---

**E. Soll Global Lock alle Feature-Aktivierungen blockieren?**

GlobalLock ist der härteste Systemstopp.
Frage: Soll er nur WorldRun sperren oder auch Feature-Aktivierungen,
Import-Approvals und Policy-Änderungen?

Empfehlung: Ja, GlobalLock blockiert alle Governance-Aktionen
außer read-only view und ConceptGuard report.

---

**F. Soll Search jede Governance-Aktion automatisch auffindbar machen?**

Derzeit werden SearchDocuments explizit erzeugt (buildSearchCorpusFrom*).
Frage: Soll Ring 20 einen passiven Mechanismus definieren,
der Governance-Aktionen automatisch indiziert?

Empfehlung: Nein, kein passiver Mechanismus. Expliziter buildCorpus-Aufruf
bleibt das Muster. Kein impliziter Hintergrundprozess.

---

**G. Soll ConceptGuard Override überhaupt möglich sein oder nur Report?**

ConceptGuard produziert aktuell nur Reports (ok/violations).
Frage: Soll ein Override-Mechanismus existieren, der bestimmte
verbotene Begriffe temporär freigibt?

Empfehlung: Kein Override. Nur Report. Override wäre ein blinder Fleck
in der Konzeptsicherheit und brächte unvorhersehbare Drift.

---

**H. Wie stark darf SystemProcess selbstständig handeln?**

Aktuell hat system_process nur view-Permissions und
export.create_readonly. Es kann keine Governance-Aktionen auslösen.
Frage: Soll system_process jemals selbstständig pausieren oder stoppen dürfen?
Z.B. bei einem internen Fehlerzustand?

Empfehlung: Nein. system_process bleibt ohne Kontrolle-Permissions.
Automatische Reaktionen wären ein unkontrolliertes Risiko.
Nur daniel_root oder operator können auf Fehlerzustände reagieren.
