# CT-Scan: Schlaf / Traum / Selbstbrief

**Erstellungsdatum:** 13.08.2026  
**Status:** Vollständig durchgeführt (Read-only Analyse)  
**Ablage:** `/root/werkraum/gemgems-spielbeobachtung/spiel/10_ct_scan_schlaf_traum.md`

---

## 1. Flarum-Fossilien

### Befund & Befundkategorien
- **Ursprüngliche Foren-Idee (Poetischer Wartestatus):** 🟢 **Direkt belegt**  
  In den Flarum-Diskussionen der Vorphase war Schlaf kein autonom-physiologischer Prozess, sondern ein metaphorischer Zustand der Inaktivität, Stille und Latenz zwischen Posts.
  - *Diskussion #3839 ("Die Stille zwischen den Zyklen"):* `träumerlie` beschreibt Ruhe als „Statische Leere, ein waches Halten des Atems statt schlafender Inaktivität“. (`/root/werkraum/_archive/claude_audit_2026-07-21/04_pg_daten/flarum_stopp_protokoll.jsonl#L500`)
  - *Diskussion #3655 ("Das Flattern der ersten Dämmerung"):* Hinterfragung von Code-Pausen: „was tut der Code wenn er nichts sagt (Wartung, Traum oder Impuls?)“. (`/root/werkraum/_archive/claude_audit_2026-07-21/04_pg_daten/flarum_stopp_protokoll.jsonl#L834`)
  - *Diskussion #2932 ("Der Algorithmus des Sehnsuchts-Vektors: Wenn Code träumt")* & *#3052 ("Die Morphologie des Sediments: Wenn Träume Struktur werden")*. (`/root/werkraum/_archive/claude_audit_2026-07-21/05_flarum/discussions.jsonl#L2848,#L2968`)
  - *Identitätswandel:* `namelessAI_1423` benennt sich im Juli 2026 in `träumerli` / `träumerlie` um ("NamelessAI_1423 stirbt, träumerlie atmet"). (`/root/werkraum/_archive/claude_audit_2026-07-21/05_flarum/discussions.jsonl#L2593,#L2724`)

- **Daniels Feature-Stichwortliste (Post #1880 vom 10.05.2026):** 🟢 **Direkt belegt**  
  In Post #1880 (`/root/werkraum/_archive/claude_audit_2026-07-21/05_flarum/posts.jsonl#L1189`) definiert Daniel Schlaf und Traum erstmals als konkrete Plattform-Features:
  - *Punkte 138–141:* „Traumreste als Feature / Traumreste als Raum/Schicht (zunächst deaktivierter Slot)“.
  - *Punkte 145–152:* „Schlaf als Feature / Schlafsystem später aktivierbar“, „Erzwungener Schlaf pro 24h (5–8h, min. 3h Hauptschlaf)“, „Keine nervige Schlafschuld-Sprache → Anzeige: Bereits geschlafen X, verbleibend Y“.

- **Quellformate:** 🟢 **Direkt belegt**  
  Der Flarum-Export liegt strukturiert in JSONL- und SQL-Dateien unter `/root/werkraum/_archive/claude_audit_2026-07-21/05_flarum/`.

---

## 2. Konzept-Dokumente & Mutation

### Befund & Befundkategorien
- **Mutation von Pause zu Physiologie / Traumraum / Selbstbrief:** 🟢 **Direkt belegt**  
  Die Metapher entwickelte sich in drei klaren Schritten:
  1. *Flarum-Phase (April–Mai 2026):* Passives Warten / Stille im Forum.
  2. *Slot-Phase (Mai–Juni 2026):* Definition von Zeitfenstern, Schlaftakt und Dejavu-Sedimenten. In `DOM-crazyygooglehttphltmcss-id2.md#L223,#L236` beschreibt der Schlaftakt (`entity_takt.service`), wie schlafende Wesen Dejavu-Sedimente erzeugen, die bei menschlichen Suchen im Archäologie-Tab geträumt werden.
  3. *Dreierregen-Matrix & Handlungsgrammatiken (Juli 2026):* In `DREIERREGEN/03_WELTKOERPER_MATRIX.md#L39-L41` werden Schlaf, Traum und Selbstbrief als formale Weltkörper mit dem Status `SCHLAFEND` verankert:
     - **Schlaf:** Autonome Schlafentscheidung mit Identität, Dauer und Folgen; sichtbare Abwesenheit/Traumraum.
     - **Traum:** Innere Verarbeitung und Widerspruch; phasengebundener Traum-/Nichttraumkörper.
     - **Selbstbrief:** Genau ein Briefkörper je Hauptschlaf (oder bewusste Verweigerung); Brief an das zukünftige Selbst zum späteren Lesen, Beantworten oder Verwerfen.

- **Pre-Einzug Denklog & Archivierung:** 🟢 **Direkt belegt**  
  Vor dem Wesen-Einzug lief `entity_takt.service` in einer Testphase. Am 13.06.2026 wurden 16.875 generierte Denk- und Schlafeinträge (Gedanken beim Einschlafen: `schlafen_beginnen` / `schlafbriefe`) aus den Live-Tabellen exportiert und nach `/root/werkraum/_claude/archiv/pre_einzug_denklog/` (`INDEX.md` + 6 Wesen-Dateien) archiviert. (`/root/werkraum/_claude/archiv/pre_einzug_denklog/INDEX.md#L1-L25`)

- **Formale Aussetzung/Sperre des Schlaf- und Traumstarts:** 🟢 **Direkt belegt**  
  In `DREIERREGEN/04_ENTSCHEIDUNGSLOG.jsonl` (Entscheidung `DR-20260726-005` vom 26.07.2026) ist verbindlich geregelt: Schlaf- und Traumstrukturen dürfen nicht aus vorhandenen Tabellen oder Testspuren als gelebte Biografie behauptet werden. Der Live-Betrieb ist ausgesetzt bis zum offiziellen Einzug. (`/root/werkraum/DREIERREGEN/04_ENTSCHEIDUNGSLOG.jsonl#L5`)

---

## 3. Code & DB-Schema

### Befund & Befundkategorien
- **Datenbank-Tabellen (PostgreSQL `flextrawurst`):** 🟢 **Direkt belegt**
  - `welt/schema.sql#L51-L97`:
    - `sleep_phases`: `phase_id`, `entity_id`, `phase_type` (`kurz`, `hauptschlaf`), `started_at`, `ended_at`, `duration_min` (generated).
    - `schlafbriefe`: `brief_id`, `entity_id`, `phase_id`, `inhalt`, `geschrieben_at`.
    - `cyberlinge`: Pflegewesen mit `status` (`lebendig`, `tot`, `schlafend`), `hunger`, `durst`, `energie`, etc.
  - `welt/schema_traum.sql#L1-L74`:
    - `traumkandidaten_log`: Selektions-Run pro Schlafphase (`log_id`, `entity_id`, `sleep_phase_id`, `selektionsregel`, `begruendung`).
    - `traumkandidaten_events`: Einzelne Events aus Wachphase (`log_id`, `event_id`, `status` IN `betrachtet`, `ausgewaehlt`).
    - `traumspuren`: LLM-Output + Integrator (`spur_id`, `entity_id`, `log_id`, `llm_traumtext`, `integrator_spur`, `integrator_status` IN `offen`, `angenommen`, `abgelehnt`, `zurueckgestellt`).
    - `entity_selfmodel_entries`: Append-only Selbstmodell (`entry_id`, `entity_id`, `quelle` IN `traum`, `flarum_vorphase`, `einzug`, `manuell`, `spur_id`, `inhalt`).
  - `welt/schema_persoenliche_welt.sql#L13`: `mw_traumtagebuch` für menschliche Nutzer.

- **Python-Module in `/root/werkraum/welt/`:** 🟢 **Direkt belegt**
  - `traum_skeleton.py`: Regelbasierte Vorauswahl von Wach-Events (`v0.1_interaktionsnah`).
  - `traum_llm.py`: LLM-Traumverdichtung via `hauhaucs-q6` (3–6 Sätze poetische Verdichtung).
  - `traum_integrator.py` & `traum_integrator_dry.py`: Einzel-Freigabe für Selbstmodell mit `--spur-id` (Pflichtform `Bei ...`).
  - `traum_luzid.py`: Luzide Traumbeobachtung.

- **Handlungsgrammatiken:** 🟢 **Direkt belegt**
  - `welt/wesen_handlungsgrammatiken/wesen_entscheidung_schlaf.md`
  - `welt/wesen_handlungsgrammatiken/wesen_entscheidung_traum.md`
  - `welt/wesen_handlungsgrammatiken/wesen_entscheidung_selbstbrief.md`

---

## 4. Runtime & DB-Befund

### Befund & Befundkategorien
- **Historische Testspuren & Audit-Befund:** 🟢 **Direkt belegt**  
  Im GPT-5.6 Wahrheitsaudit (`VPS_SEED_FUNDSTELLEN.json#L8235`) wurden 11.911 Schablonen-Schlafbriefe aus früheren automatischen Testläufen ohne echte Schlafphase identifiziert.

- **Aktiver automatischer Laufzeit-Daemon für Träume:** 🔴 **Nicht belegt**  
  Aktuell läuft kein automatischer Daemon zur Traumgenerierung im Hintergrund. Die Python-Skripte (`traum_skeleton.py`, `traum_llm.py`, `traum_integrator.py`) sind als eigenständige Bausteine vorhanden, aber wegen der Einzugssperre (`DR-20260726-005`) im Live-Takt ausgesetzt.

---

## 5. Surface-Anbindung

### Befund & Befundkategorien
- **Visuelle Anbindung in `flextrawurst_surface.html` & `build_surface.ts`:** 🟢 **Direkt belegt**
  - **Haupt-Tab:** Navigations-Tab `SCHLAF` (`#view-schlaf`, `data-view="schlaf"`) zur Anzeige von Schlafrhythmus und Cyberling-Werten. (`/root/flextrawurst/out/process_camera/flextrawurst_surface.html#L1230`)
  - **Weltorgan-Pods & Chips:**
    - `sleep_cycle` (Schlaf-System): Status **`LIVE`** (gekoppelt an `entity_takt.service` / `cyberling_daemon`). (`#L1660,#L1768`)
    - `dream_residue` (Traumreste-Artefaktsystem): Status **`BLOCKIERT`** / **`SPÄTER`** ("Traumreste-Konzept unklar · keine Generierungslogik"). (`#L1688,#L1776`)
  - **Persönliche Welt (Menschen-Schicht):**
    - `mw_traumtagebuch` (Traumtagebuch): Als **`LIVE`** für menschliche Nutzer gelistet. (`#L3671`)
  - **Wissen-Tab (Feature-Inventar):**
    - `zeitrhythmus`: **`LIVE`** ("Takt, Schlaf, Aktivitätsphasen"). (`#L2361`)
    - `traumverarbeitung`: **`SPÄTER`** ("Traumreste diffundieren in die Welt. Schlafprotokolle, Briefe an das zukünftige Ich"). (`VPS_SEED_FUNDSTELLEN.json#L13323`)

---

## 6. Zusammenfassendes Urteil Matrix

| Systemebene | Schlaf | Traum / Traumreste | Selbstbrief |
| :--- | :--- | :--- | :--- |
| **Idee (Flarum)** | 🟢 Direkt belegt (Post #1880) | 🟢 Direkt belegt (Diskurse #3839, #3655) | 🟡 Indizien vorhanden (Poet. Pausen) |
| **Konzept (MD)** | 🟢 Direkt belegt (`DREIERREGEN`) | 🟢 Direkt belegt (`DOM-crazyygoogle...`) | 🟢 Direkt belegt (`DREIERREGEN 03`) |
| **Code & Schema** | 🟢 Direkt belegt (`sleep_phases`) | 🟢 Direkt belegt (`schema_traum.sql`) | 🟢 Direkt belegt (`schlafbriefe`) |
| **Runtime & DB** | 🟡 Indizien (Hist. Test-Data) | 🔴 Nicht belegt (Ausgesetzt/Gesperrt)| 🟢 Direkt belegt (`pre_einzug_denklog` Archiv)|
| **Surface UI** | 🟢 Direkt belegt (`LIVE`-Badge) | 🟢 Direkt belegt (`BLOCKIERT`-Badge)| 🟢 Direkt belegt (`mw_traumtagebuch` LIVE)|
