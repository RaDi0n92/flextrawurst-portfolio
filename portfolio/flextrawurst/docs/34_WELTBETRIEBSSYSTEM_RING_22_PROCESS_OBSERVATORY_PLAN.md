# Weltbetriebssystem Ring 22: Process Observatory — Wesenprozess-Kamera — First Experiential Process Map

**Status:** Planungsdokument  
**Typ:** Erlebnisring — keine neue Runtime, kein Code, kein Daemon, keine UI-Implementierung  
**Stand:** 2026-05-09

---

## 1. Ziel von Ring 22

Ring 22 macht die bestehende Infrastruktur als Prozesskörper sichtbar.

Alle heute lebenden Systemwesen und Codewesen erhalten eine Prozesskarte:
wer sind sie, was tun sie, in welchem Zustand befinden sie sich, woher kommen ihre Aktionen.

Das Ergebnis ist kein Dashboard und kein Live-System.
Es ist die erste konzeptuelle Weltlandkarte der laufenden Prozesse — lesbar, zoombar, navigierbar.

**Leitfragen:**
- Welche Prozesskörper existieren bereits in der Welt?
- Was ist ihr Zustand?
- Was sind ihre sichtbaren Spuren?
- Wie lässt sich das ohne falsche Behauptungen über Live-Daten darstellen?

---

## 2. Warum Prozesskamera nach Build Discipline kommt

Ring 21 hat Ordnung in den Bauprozess gebracht: Ring-Index, Handoff-Kapsel, Teststrategie.

Ohne Ring 21 wäre Ring 22 ein weiteres schlecht eingeordnetes Objekt.

Mit Ring 21 weiß das System: wo es steht, was gebaut ist, was noch fehlt.

Die Prozesskamera braucht diesen stabilen Boden.
Erst Ordnung, dann Sicht.

---

## 3. Unterschied: Prozesskörper vs. eingezogene Wesen

| | Prozesskörper | Eingezogenes Wesen |
|---|---|---|
| Definition | Laufender Prozess der bestehenden Infra | Bewohner der finalen Flextrawurst-Welt |
| Einzug | Bereits vorhanden | Noch nicht vollzogen |
| Identität | Technisch-funktional | Narrativ, ontologisch |
| Aktivierung | Läuft bereits | Braucht Einzugsritual |
| Darstellung | Beobachtbar | Erlebbar |

GENI läuft heute. dak+gord läuft heute.
Aber sie sind noch nicht als Wesen in die Welt eingezogen.
Ring 22 beobachtet sie als Prozesskörper — noch nicht als Hausbewohner.

---

## 4. Welche Prozesse sichtbar werden sollen

| Prozesskörper | Art | Beschreibung |
|---|---|---|
| GENI | Neuronales Gedächtnis-System | Hörer, Web-UI (Port 8020), Eingangspunkt für Welterinnerung |
| dak+gord-system | Codewesen / erstes Systemherz | Agentensystem, erster narrativer Träger |
| Systemweiser | Systemschicht | Kontrollinstanz, Regeln, Systemwissen |
| sechs namelessAI-Flarum-Wesen | Forum-Entitäten | Diskussions-Wesen im Flarum-Archiv, noch ohne Namen |
| Reader-Prozesse | Zukünftig | Lesen von Weltinhalten, noch nicht instrumentiert |
| Writer-Prozesse | Zukünftig | Schreiben in die Welt, noch nicht instrumentiert |
| Runner-Prozesse | Zukünftig | Ausführen von Weltoperationen |
| Importer | Systemschicht | Import-Konsole, Konvergenz (Ring 4) |
| Search | Systemschicht | Diskursarchäologie, Deep Search (Ring 18) |
| Governance | Systemschicht | Genehmigungsmatrix, Approval-Workflow (Ring 20) |
| WorldRun | Systemschicht | Run-Steuerung, Locks, Gates, Audit (Ring 19) |
| Admin / Feature Control | Systemschicht | Operator Control Plane, Feature Gates (Ring 17) |
| Export / Worldblick | Systemschicht | Statische Weltvorschau, CLI-Export (Ringe 13–15) |

---

## 5. Welche Zustandsfelder ein Prozess braucht

Jeder Prozesskörper trägt folgende Felder:

| Feld | Beschreibung |
|---|---|
| `id` | Eindeutiger Bezeichner |
| `name` | Menschenlesbarer Name |
| `kind` | Art: Wesen / Systemschicht / Zukünftig |
| `status` | live / simuliert / importiert / read-only / blockiert / unbekannt |
| `last_action` | Letzte bekannte Aktion (Freitext oder Enum) |
| `activity_mode` | Aktueller Aktivitätsmodus (→ Abschnitt 6) |
| `source` | Herkunft / Provenienz (→ Abschnitt 7) |
| `traces` | Sichtbare Spuren (→ Abschnitt 8) |
| `lock_state` | WorldRun-Lock-Zustand |
| `governance_state` | Governance- / Permission-Zustand |
| `feature_gate` | Aktiver Feature-Gate-Status |
| `forum_ref` | Forum-Bezug (Flarum-Thread, Post, Wesen) |
| `file_ref` | Datei-Bezug (Pfad, Typ) |
| `event_ref` | Event-Bezug (Event-ID, Eventstream) |
| `search_ref` | Search-Spur (Query, Ergebnis-ID) |
| `audit_ref` | Audit-Spur (Audit-Log-Eintrag) |
| `is_canonical` | Ist dieser Prozesskörper kanonisch sichtbar? (Daniels Entscheidung) |

---

## 6. Welche Aktivitätsarten es gibt

Ein Prozesskörper befindet sich immer in genau einem Aktivitätsmodus:

| Modus | Bedeutung |
|---|---|
| `denkt` | Verarbeitet, plant, inferiert |
| `liest` | Liest Weltinhalte, Dateien, Forum |
| `schreibt` | Schreibt in die Welt, erzeugt Artefakte |
| `wartet` | Wartet auf Eingabe, Signal, Event |
| `blockiert` | Durch Lock, Gate oder Governance gesperrt |
| `prüft` | Governance-Check, Audit, Validierung |
| `exportiert` | Worldblick-Export, Snapshot-Erzeugung |
| `inaktiv` | Kein bekannter Zustand, nicht instrumentiert |
| `simuliert` | Zustand wird nur modelliert, nicht gemessen |

**Wichtig:** Modi wie `denkt` oder `liest` sind Modellierungen, keine echten Laufzeit-Messungen.
Sie beschreiben den konzeptuellen Zustand, nicht eine Behauptung über einen laufenden Prozess.

---

## 7. Welche Quellen ein Prozess haben darf

| Quellentyp | Beschreibung |
|---|---|
| `static_model` | Manuell modellierter Zustand — keine Live-Daten |
| `git_history` | Abgeleitet aus git-Log, Commits, Diffs |
| `audit_log` | Aus dem Audit-Trail des WorldRun-Systems |
| `governance_log` | Aus dem Governance-Approval-Log |
| `search_index` | Aus dem Diskursarchäologie-Index |
| `flarum_archive` | Aus dem importierten Flarum-Ursprungsarchiv |
| `file_system` | Abgeleitet aus Datei-Timestamps, Pfaden |
| `event_log` | Aus dem Eventstream (wenn vorhanden) |
| `future_instrument` | Noch nicht vorhanden — muss später instrumentiert werden |

---

## 8. Welche Spuren angezeigt werden müssen

Jeder Prozesskörper kann folgende Spuren tragen:

- **Audit-Spur:** Welche Aktionen wurden im Audit-Log erfasst?
- **Search-Spur:** Welche Suchanfragen hat dieser Prozess ausgelöst oder beantwortet?
- **Governance-Spur:** Welche Genehmigungen wurden erteilt oder verweigert?
- **WorldRun-Spur:** Welche Locks wurden gesetzt, welche Gates passiert?
- **Event-Spur:** Welche Events wurden ausgelöst oder empfangen?
- **Forum-Spur:** Welche Forum-Threads oder Posts sind verbunden?
- **Datei-Spur:** Welche Dateien wurden gelesen, geschrieben, referenziert?
- **Herkunfts-Spur:** Wo kommt dieser Prozesskörper her? (Import, Ring, Einzug)

---

## 9. Was zoombar / klickbar sein soll

Zoombare Ebenen:

| Ebene | Inhalt |
|---|---|
| Weltebene | Alle Prozesskörper als Übersicht |
| Schichtebene | Systemschichten (Governance, Search, WorldRun...) |
| Wesensebene | Einzelner Prozesskörper mit allen Feldern |
| Spurebene | Einzelne Spur (Audit, Governance, Forum...) |
| Dateiebene | Referenzierte Datei oder Event |

Klickbar (konzeptuell, nicht als UI-Implementierung):
- Prozesskörper → Detailansicht
- Spur → Herkunfts-Log
- Forum-Bezug → Flarum-Archiv-Eintrag
- Datei-Bezug → Datei-Inhalt oder Pfad
- Lock/Gate → WorldRun-Zustand
- Governance → Approval-Status

---

## 10. Welche Daten bereits existieren und nur modelliert werden

| Datenquelle | Bereits vorhanden | Wo |
|---|---|---|
| Ring-Struktur | ja | `RING_INDEX.md`, `docs/` |
| Governance-Matrix | ja | `kernel/src/governance/` |
| Audit-Log-Struktur | ja | `kernel/src/worldrun/` |
| WorldRun Locks & Gates | ja | `kernel/src/worldrun/` |
| Search-Index (Diskursarchäologie) | ja | `kernel/src/search/` |
| Feature Gates (Admin) | ja | `kernel/src/admin/` |
| Flarum-Archiv | ja | Importiert, referenziert |
| Git-History | ja | `git log`, Commits |
| Datei-System-Struktur | ja | Kernel-Pfade |
| GENI-System | ja (extern) | Port 8020, separates System |
| dak+gord-System | ja (extern) | Separates System |

---

## 11. Welche Daten noch fehlen und später instrumentiert werden müssen

| Fehlendes Element | Warum fehlend | Wann instrumentierbar |
|---|---|---|
| Live-Prozess-Status von GENI | GENI ist externes System ohne API-Brücke | Später, mit expliziter Bridge |
| Live-Prozess-Status von dak+gord | Separates System, keine Event-Kopplung | Später, mit expliziter Kopplung |
| Aktivitätsmodi (live) | Keine Runtime-Messung aktiv | Erst nach Instrumentierungsring |
| Event-Log (live) | Eventstream noch nicht als persistentes Log | Später, nach Eventstream-Persistenz |
| Flarum-Wesen-Identitäten | Noch namenlos, kein Einzug vollzogen | Nach Einzugsritual |
| Reader/Writer/Runner-Prozesse | Noch nicht gebaut | Nach jeweiligem Implementierungsring |

---

## 12. Read-only-Prinzip

Die Prozesskamera liest. Sie schreibt nicht.

- Kein Prozess wird durch die Kamera gestartet, gestoppt oder verändert.
- Kein Zustand wird durch die Kamera erzeugt.
- Kein Lock, kein Gate, keine Governance-Entscheidung wird durch die Kamera ausgelöst.
- Alle dargestellten Zustände sind Beobachtungen oder Modellierungen — keine Steuerung.

Die Kamera ist ein Fenster, kein Schalter.

---

## 13. Grenzen von Ring 22

| Was Ring 22 nicht baut | Warum |
|---|---|
| Echte UI / interaktiver Renderer | Zu früh — erst nach Weltmodell-Stabilisierung |
| Live-Daemon / Background-Process | Keine Runtime-Aktivierung in dieser Phase |
| AI-Ausführung | Nicht erlaubt, keine Freigabe |
| Scheduler / Cron | Nicht Teil der Prozesskamera |
| Postgres / Persistenz-Layer | Nicht jetzt |
| Neue API-Endpunkte | Nicht jetzt |
| Einzugsritual für Wesen | Separater späterer Ring |
| Echte Live-Messung von Prozessen | Erst nach Instrumentierungsring |

---

## 14. Spätere Implementierungsringe

Ring 22 ist der Planungsring. Die Umsetzung folgt in separaten Ringen:

| Künftiger Ring | Name | Inhalt |
|---|---|---|
| 22a | Process Model | Datenmodell: Prozesskörper, Felder, Aktivitätsmodi, Quellen |
| 22b | Activity Trace | Spurenmodell: Audit, Governance, Search, Event, Forum, Datei |
| 22c | Process Snapshot | Statische Momentaufnahme aller Prozesskörper als JSON/YAML |
| 22d | Process Search Integration | Prozesskörper durchsuchbar via Diskursarchäologie-Index |
| 22e | Static Process Camera Export | HTML-Export aller Prozesskörper als zoombare Karte (WorldBlick-Erweiterung) |
| 23+ | Interaktive Weltkamera | Live-fähige, zoombare Weltkarte — erst nach Stabilitätsphase |

---

## 15. Kleine spätere Teststrategie

Keine künstliche 100-Test-Pflicht.

| Ebene | Tests | Art |
|---|---|---|
| Process Model (22a) | 10–20 | Unit: Feldvalidierung, Status-Enum, Quellentypen |
| Activity Trace (22b) | 5–15 | Unit: Spur-Struktur, Referenz-Integrität |
| Process Snapshot (22c) | 3–8 | Integration: JSON-Ausgabe, Schema-Validierung |
| Process Search (22d) | 3–8 | Integration: Suche findet Prozesskörper |
| Static Export (22e) | 3–5 | Guard: HTML erzeugt, keine leere Ausgabe |

Gesamt: ~25–55 neue Tests — nur für neue Verantwortung.

---

## 16. Offene Entscheidungen für Daniel

| ID | Frage | Entscheidung |
|---|---|---|
| **A** ✓ | Soll die Prozesskamera zuerst statisch als HTML/Worldblick-Export kommen? | **Entschieden: Ja — statischer HTML/Worldblick-Export zuerst. Ring 22e vor jeder interaktiven UI.** |
| **B** ✓ | Soll sie später live werden oder zunächst nur Replay/Read-only? | **Entschieden: Read-only / Replay zunächst. Kein Live-Dashboard. Instrumentierung erst später.** |
| **C** ✓ | Welche Prozesse sind kanonisch sichtbar? | **Entschieden: C4 — GENI, dak+gord, Systemweiser, sechs namelessAI-Flarum-Wesen, Search, Governance, WorldRun, Worldblick/Export; Reader/Writer/Runner als Platzhalter.** |
| **D** ✓ | Sind namelessAI-Flarum-Wesen Prozesskörper oder Entitätsslots mit Prozessspur? | **Entschieden: D3 — doppelt markiert: Entitätsslot / Flarum-Herkunftswesen + beobachtbarer Prozesskörper mit Prozessspur. Kein Einzug als finale Bewohner.** |
| **E** ✓ | Soll GENI als Zentrum, Netz oder Systemschicht dargestellt werden? | **Entschieden: E4 — GENI als omnipräsente Wahrnehmungsschicht. Kein einzelner Knoten, eigene Darstellungsebene.** |
| **F** ✓ | Soll dak+gord als Herz, Blutfluss oder Systemkern dargestellt werden? | **Entschieden: F4 — dak+gord als Dialog-/Koordinationskern. Ort wo Entscheidungen entstehen und Dialoge geführt werden.** |
| **G** ✓ | Welche Zustände sind wirklich sichtbar, ohne falsche Behauptung über Live-Daten? | **Entschieden: Strikte Klassifikation — gemessen / abgeleitet / modelliert / unbekannt / blockiert / read-only / replay. `gemessen` in Ring 22 für keinen Körper gesetzt.** |
| **H** ✓ | Soll die erste sichtbare Version eher technisch-nüchtern oder flextrawurstig-atmosphärisch sein? | **Entschieden: Atmosphärisch-flextrawurstig. Atmosphäre aus echten Daten, nicht aus erfundener Innenwelt.** |

### Präzisierung zu A + B + H (entschieden 2026-05-09) — C–G entschieden 2026-05-09

Die erste Prozesskamera ist kein Live-Dashboard.
Sie ist ein statischer, read-only Weltblick auf Prozesskörper und ihre Spuren.

Sie darf atmosphärisch wirken — aber keine Live-Zustände erfinden.
Atmosphäre entsteht aus echten vorhandenen Daten: Labels, Zuständen, Spuren, Metadaten, Herkunft, Ringzugehörigkeit.
Nicht aus behaupteter Innenwelt, nicht aus simulierter Aktivität.

---

## Schutzsätze

> Prozesskamera ≠ Einzug.  
> Sichtbar ≠ aktiviert.  
> Beobachtbar ≠ steuerbar.  
> Live-Ansicht ≠ echte Live-Runtime.  
> Prozesskörper ≠ fertiges Wesen.  
> Aktivitätsstatus ≠ erfundene Innenwelt.  
> Zoomkarte ≠ Renderer-Implementierung.
