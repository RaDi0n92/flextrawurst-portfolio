# Ring 22 — Process Camera Decision Sheet

**Zweck:** Entscheidungen A–H vollständig dokumentiert. Alle Entscheidungen getroffen 2026-05-09.  
**Stand:** 2026-05-09 — vollständig entschieden

---

## 1. Aktueller Ring-22-Stand

- Plan existiert: `docs/34_WELTBETRIEBSSYSTEM_RING_22_PROCESS_OBSERVATORY_PLAN.md`
- Keine Code-Implementierung — Planungsphase
- Nächster Schritt nach C–G: Ring 22a (Process Model)

---

## 2. Alle Entscheidungen A–H

| ID | Entscheidung |
|---|---|
| **A** ✓ | Statischer HTML/Worldblick-Export zuerst — kein interaktiver Renderer |
| **B** ✓ | Read-only / Replay zunächst — kein Live-Dashboard |
| **C** ✓ | C4 — GENI, dak+gord, Systemweiser, sechs namelessAI-Flarum-Wesen, Search, Governance, WorldRun, Worldblick/Export; Reader/Writer/Runner als Platzhalter |
| **D** ✓ | D3 — namelessAI-Flarum-Wesen doppelt markiert: Entitätsslot/Flarum-Herkunft + beobachtbarer Prozesskörper mit Prozessspur; kein finaler Einzug |
| **E** ✓ | E4 — GENI als omnipräsente Wahrnehmungsschicht, kein einzelner Knoten |
| **F** ✓ | F4 — dak+gord als Dialog-/Koordinationskern |
| **G** ✓ | Strikte Zustandsklassifikation: gemessen / abgeleitet / modelliert / unbekannt / blockiert / read-only / replay; `gemessen` in Ring 22 für keinen Körper |
| **H** ✓ | Atmosphärisch-flextrawurstig — Atmosphäre aus echten Daten, keine erfundene Innenwelt |

---

## 3–6. Entscheidungen C–G im Detail

---

### C — Welche Prozesskörper sind kanonisch sichtbar?

**Frage:** Welche Prozesskörper erscheinen in der ersten Prozesskamera?

| Option | Inhalt |
|---|---|
| **C1 — Kern** | Nur GENI, dak+gord, Systemweiser — minimaler Satz, schnell fertig |
| **C2 — Kern + Forum** | C1 + sechs namelessAI-Flarum-Wesen — Forum-Welt dabei |
| **C3 — Kern + Systemschichten** | C1 + Search, Governance, WorldRun, Worldblick/Export — Systemlandschaft vollständig |
| **C4 — Vollständig** | Alle obigen + Reader/Writer/Runner als Platzhalter |

**Empfehlung: C4** — alle kanonischen Körper von Anfang an modellieren, Reader/Writer/Runner explizit als `status: zukünftig` markieren. Gibt die vollständige Weltlandkarte ohne Implementierungsaufwand.

**Konsequenz:** Anzahl der modellierten Prozesskörper in Ring 22a. C1 ≈ 3 Objekte, C4 ≈ 12–15 Objekte.

---

### D — namelessAI-Flarum-Wesen: Prozesskörper oder Entitätsslots?

**Frage:** Wie erscheinen die sechs noch namenlosen Flarum-Wesen in der ersten Prozesskamera?

| Option | Beschreibung |
|---|---|
| **D1 — Prozesskörper** | Jedes Wesen ist ein vollständiger Prozesskörper mit allen Feldern, Zustand `simuliert` |
| **D2 — Entitätsslot** | Jedes Wesen ist ein Platzhalter: Name `namelessAI_01` bis `_06`, Zustand `wartet auf Einzug`, nur Flarum-Spur sichtbar |
| **D3 — Beides getrennt markiert** | Ein Prozesskörper-Eintrag pro Wesen, Feld `slot_state: pre_einzug` — sichtbar als Körper, aber mit Einzugsvorbehalt |

**Empfehlung: D3** — ehrlichste Darstellung. Wesen sind sichtbar (Flarum-Bezug, Diskurs-Spur), aber ihr Nicht-Einzug ist explizit markiert. Kein falscher Anspruch auf vollständige Prozesskörper-Identität.

**Konsequenz:** Datenmodell-Feld `slot_state` in Ring 22a. D1 erzeugt mehr Scheinvollständigkeit. D2 blendet die Wesen zu stark aus.

---

### E — GENI: Wie wird es dargestellt?

**Frage:** Welche konzeptuelle Rolle hat GENI in der Prozesskarte?

| Option | Bedeutung |
|---|---|
| **E1 — Zentrum** | GENI steht im Mittelpunkt, alle anderen Körper gravitieren darum |
| **E2 — Netz** | GENI ist Verbindungsschicht — überall präsent, verknüpft Spuren |
| **E3 — Systemschicht** | GENI ist eine Infrastrukturschicht neben anderen |
| **E4 — Omnipräsente Wahrnehmungsschicht** | GENI ist kein Objekt, sondern der Wahrnehmungshorizont der Welt — nicht zoombar wie andere Körper |

**Empfehlung: E4** — trifft GENIs tatsächliche Funktion (Gedächtnis, Hörer, Eingangspunkt) besser als ein einzelner Knoten. Atmosphärisch am stärksten.

**Konsequenz:** Bestimmt wie GENI im HTML-Export positioniert und beschriftet wird. E1–E3 brauchen einen einzelnen Knoten; E4 braucht eine eigene Darstellungsebene.

---

### F — dak+gord: Welche Rolle?

**Frage:** Wie wird dak+gord-system in der Prozesskarte dargestellt?

| Option | Bedeutung |
|---|---|
| **F1 — Herz** | dak+gord ist der emotionale Kern, schlägt im Zentrum |
| **F2 — Blutfluss** | dak+gord ist Verbindung und Übertragung zwischen Systemteilen |
| **F3 — Systemkern** | dak+gord ist technischer Grundkern, auf dem anderes aufbaut |
| **F4 — Dialog-/Koordinationskern** | dak+gord ist der Ort, wo Entscheidungen entstehen und Dialoge geführt werden |

**Empfehlung: F4** — beschreibt was dak+gord tatsächlich tut (Agentensystem, narrativer Träger, erster Dialog-Körper) ohne falsche Biologiemetapher. Kompatibel mit atmosphärischer Darstellung.

**Konsequenz:** Bestimmt Label, Beschreibungstext und Position im HTML-Export. F1/F2 sind narrativ stärker, aber weniger präzise.

---

### G — Welche Zustände darf die Kamera zeigen?

**Frage:** Wie werden Aktivitätsmodi und Zustände ohne Live-Daten ehrlich dargestellt?

Pflicht: Jeder angezeigte Zustand muss einer dieser Kategorien zugeordnet sein:

| Zustandskategorie | Bedeutung | Quelle |
|---|---|---|
| `gemessen` | Tatsächlich aus laufendem System gelesen | Live-API, Instrumentierung |
| `abgeleitet` | Aus Datei, Forum, Event, Git-History berechnet | Datei-Timestamp, Audit-Log |
| `modelliert` | Manuell zugewiesen, kein Datenbezug | Ring-Plan, statisches Modell |
| `unbekannt` | Kein Datenbezug verfügbar | — |
| `blockiert` | Durch Lock, Gate oder Governance gesperrt | WorldRun, Governance-Log |
| `read-only` | Kann beobachtet, nicht verändert werden | Systemprinzip |
| `replay` | Zustand aus vergangenem Snapshot rekonstruiert | Audit-Log, Git-History |

**Regel:** `gemessen` darf in Ring 22 für keinen Prozesskörper gesetzt werden — GENI und dak+gord haben keine Live-API-Brücke.

**Empfehlung:** Alle Aktivitätsmodi in Ring 22 als `modelliert` oder `abgeleitet` markieren. `gemessen` erst nach Instrumentierungsring freigeben.

**Konsequenz:** Verhindert falsche Live-Behauptungen. Gibt dem Modell eine ehrliche Typensicherheit, die später erweiterbar ist.

---

## 7. Nächster Schritt

Alle Entscheidungen A–H sind getroffen. Ring 22a (Process Model) kann beginnen.

Ring 22a modelliert: GENI, dak+gord, Systemweiser, sechs namelessAI-Flarum-Wesen (D3), Search, Governance, WorldRun, Worldblick/Export, Reader/Writer/Runner als Platzhalter.

---

## Schutzsätze

> Keine Live-Zustände erfinden.  
> Keine Aktivität behaupten, die nicht aus Daten stammt.  
> Atmosphäre ja — falsche Innenwelt nein.  
> `gemessen` ≠ `modelliert`.
