# CT-Scan 16: v22 Questkosmos-, Generator- und Simulations-Körper

**Erstellungsdatum:** 13.08.2026  
**Status:** Auditiert & Präzisiert (Code, Matrix-Simulation, Audit-Akten & Provenienz-Belege)  
**Ablagepfad:** `/root/werkraum/gemgems-spielbeobachtung/spiel/16_ct_scan_v22_questkosmos_generator_simulation.md`  
**Untersuchter Ort:** `/root/werkraum/engine/flextrawurst-game/`  

---

## 1. Übersicht & Systemarchitektur von v22

Der **v22 Dust-Echo-Questkosmos** stellt innerhalb der Flextrawurst-Spielegeschichte die umfassendste mathematische und konzeptionelle Expansionsstufe dar. Während vorherige Epochen (v1–v21) schrittweise Laufzeit-Render-Engines und Canvas-2D-Software-3D-Spielkörper entwickelten, konzentriert sich v22 auf die **Erzeugung, Schärfung, Redteam-Prüfung und deterministische Matrix-Simulation** eines gewaltigen Quest-Universums.

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                FLEXTRAWURST v22 QUESTKOSMOS                             │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 00_rohinput           │ Daniels Wortlaut R21–R26 (Klima, Zeit, Volatile Ökonomie, Dust) │
│ 01_audit              │ Prior Simulation Redteam (65 historische v1–v21 Akten)         │
│ 02_questarchitektur   │ 15.873 7-Akt-Ketten, 37 Foci, 69 Skills, 12 Spielorgane        │
│ 03_fragenkoerper      │ 777 Fragen, 111 maschinenlesbare Checks, 99 Entwurfszweige     │
│ 04_simulation         │ 9 Spielstile × 11 Weltstörungen = 99 Varianten-Matrix           │
│ 05_redteam            │ Vorher/Nachher-Angriffe (16 Schwachstellenklassen)              │
│ 06_ergebnisse         │ SQLite (`quest_catalog.sqlite`), CSV.gz, JSONL.gz, Proof of Run │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Reales Code-Inventar von v22 (Generatoren, Simulatoren, Validatoren)

v22 besitzt **keinen** aufgeblähten Framework-Code, sondern zwei hochgradig strukturierte, performante Python-Werkzeuge in `tools/`, die sowohl autark ausgeführt als auch über historische Paket-Archive reproduziert wurden.

### 2.1 Skript-Register

| Dateipfad | Zeilen | Bytes | SHA-256 Hash | Hauptaufgabe |
| :--- | :---: | :---: | :--- | :--- |
| `extracted_sources/historical_runtime/v1_v22_bundle/.../V22/tools/build_v22_questkosmos.py` | **1.225** | 77.356 | `6fd564a1bf...bbd72bb2a1` | Master-Generator, Matrix-Simulator (NumPy), Redteam-Pass-B-Schärfer, SQLite/CSV/JSONL Exporter & Proof-Generator. |
| `extracted_sources/historical_runtime/v1_v22_bundle/.../V22/tools/audit_prior_simulations.py` | **112** | 7.498 | `4ad3e20e8b...9c3b889311` | Statischer & heuristischer Audit-Runner für 65 historische v1–v21 Simulations- und Prüfartefakte. |

---

## 3. Status- & Runtime-Trennung: Ist v22 ein Runtime-Nachfolger von v21 gewesen?

Ein zentraler Befund des CT-Scans betrifft das Verhältnis zwischen der v21 Game-Engine und dem v22 Questkosmos.

### 3.1 Die eindeutige Beleglage

| Quelle / Dokument | Zitat / Befund | Status-Aussage |
| :--- | :--- | :--- |
| `14.../01_V21_V22_STATUS_TRENNUNG.md` | *"v21: ausführbarer und getesteter Spielkörper. v22: dokumentierter, generierter und reproduzierbarer Questdesign-/Simulationskörper. v22 ist noch nicht als neue Questlaufzeit in v21 eingebaut. Die 111.111 Questkeime sind Datensätze, keine 111.111 einzeln gespielten Vollquests."* | 🔴 **Keine neue Runtime** |
| `10.../00_V22_README.md` | *"Dies ist ein Questdesign-, Simulations- und Redteamkörper. Er baut noch keinen neuen v21-Spielcode."* | 🔴 **Kein neuer Spielcode** |
| `03.../V22_GESAMTAKTE.md` | *"Belegstatus: BESTÄTIGT ALS DESIGN-/SIMULATIONS-, NICHT RUNTIME-KÖRPER ... Gebaut bedeutet ausführbarer Codekörper und konkrete Tests. Simuliert bedeutet erzeugte Zustands-, Varianten- oder Bewertungsdurchläufe."* | 🔴 **Reiner Simulationskörper** |
| Code-Audit (`/V22/tools/`) | **0** `.js` Canvas-Dateien, **0** `.gd` GDScript-Dateien, **0** Game-Loop-Skripte. Nur Python-Datenbank- & Matrix-Generatoren. | 🔴 **Offline-Generator** |

---

## 4. Methodische Präzisierung: Formaler Constraint-Pass vs. Spielerische Qualität

### 4.1 Pass A vs. Pass B – Was die "0% gescheiterten Quests" wirklich bedeuten
- **Pass A (Ungeschärft):** Generierte 111.111 Quests ohne verfahrenstechnische Schutzregeln. 4,9% fielen durch harte formalisierte Checks (z.B. reine Fetch-Quests, fehlende Nichtkampfpfade, <3 Spielorgane).
- **Pass B (Geschärft):** Der Python-Generator erzwingt im Code harte programmierte Regeln (`pure_fetch = 0`, `organ_count >= 3`, garantierte Friedens- & Autonomie-Pfade).
- **Kritische Differenzierung:**  
  Dass in Pass B **0 Quests scheiterten**, beweist, dass der **Python-Generator seine eigenen programmierten Constraints fehlerfrei durchsetzt**. Es ist **kein** Beleg dafür, dass 111.111 Quests von menschlichen Playtestern manuell gespielt wurden oder dass alle Quests automatisch unterhaltsam sind.

### 4.2 Prüfsummen & Verifikation – Rolling Hash vs. SHA-256
- **64-Bit Rolling Hash:** Dient im Skript als deterministischer **Prüfsummen-Checksum-Algorithmus**, um festzustellen, ob zwei Simulationsläufe identische Matrix-Arrays erzeugen. Er stellt **keine** kryptographische Signatur dar.
- **Kryptographische Integrität:** Wird separat über echte **SHA-256-Hashes** in `09_PROOF_OF_RUN.json` für die SQLite-Datenbank `quest_catalog.sqlite` hergestellt.

### 4.3 Erhaltungs- & Reproduktionsstatus
- **Vorhandene Artefakte:** Generator-Skripte (`build_v22_questkosmos.py`), SQLite-Katalog (`quest_catalog.sqlite`), CSV/JSONL-Archive und historische Proofs liegen physisch auf der Festplatte vor.
- **Einschränkung:** "Auf der Festplatte vorhanden" belegt das Vorhandensein der gespeicherten Artefakte. Eine Aussage über "100% vollständige Erhaltung" setzt den Abgleich mit einem externen Ursprungs-Manifest voraus, das hier nicht als unabhängige Zweitquelle vorliegt.

---

## 5. Ausführungs-Belege & Ergebnis-Artefakte

Die Ergebnisse der v22-Prospektion sind in `/root/werkraum/engine/flextrawurst-game/` in folgenden Datenkörpern gesichert:

1. `extracted_sources/.../V22/06_ergebnisse/quest_catalog.sqlite`: SQLite3-Datenbank mit 111.111 Einträgen.
2. `extracted_sources/.../V22/06_ergebnisse/quest_catalog.csv.gz`: Komprimierter CSV-Katalog.
3. `extracted_sources/.../V22/06_ergebnisse/representative_traces.jsonl.gz`: 333 repräsentative Vollspuren.
4. `extracted_sources/.../V22/06_ergebnisse/09_PROOF_OF_RUN.json`: Beleg mit ISO-Zeitstempel (`2026-07-25T12:48:45Z`) und SHA-256 Hashes.

---

## 6. Fazit

v22 ist das datenbankgestützte Questdesign- & Generator-Rückgrat des Projekts. Es ist eine funktionierende Python-Matrix-Generierung, die strukturierte Questdaten für spätere Spiel-Runtimes bereitstellt.
