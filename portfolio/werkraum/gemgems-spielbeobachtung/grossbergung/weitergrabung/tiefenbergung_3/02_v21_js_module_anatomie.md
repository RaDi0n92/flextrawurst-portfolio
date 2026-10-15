# 🕹️ TIEFENBERGUNG III — BERICHT 02: V21 JS-MODULE ANATOMIE & EXECUTION-CHAIN AUDIT

**Datum:** 2026-08-14  
**Autor:** Antigravity / GemGem (JS-Code-Auditor)  
**Status:** CODEZEILENGEPRÜFT, ANATOMIE & EXECUTION-CHAINS BELEGT  
**Ziel-Datei:** `/root/werkraum/gemgems-spielbeobachtung/grossbergung/weitergrabung/tiefenbergung_3/02_v21_js_module_anatomie.md`

---

## 1. STRUKTURIERTE EXECUTION-CHAIN-ANATOMIE DER 3 MODUL-KÖRPER

### 1.1 `v21_combat_loot_pause.js` (21.123 Bytes)
- **Hauptmethoden:** `attack21()`, `spawnCombatTarget21()`, `consentDuel21()`, `equip21()`, `healDuringPause21()`, `setSpellSlot21()`.
- **Execution-Chain:**  
  1. *Definition:* `attack21(targetId)` berechnet Schadenspunkte aus Skill-Level.
  2. *Invocation:* Aufruf über DOM-Button `onclick="FW.game.attack21(id)"`.
  3. *Reachable Player Action:* Klick auf Ziel gegnerischer KI im 2D-Kampf-Panel.
  4. *Stateänderung:* Mutiert `state.targetHealth` und händigt `state.combatLogs` aus.
  5. *Persistenz:* In-Memory JavaScript State Object (`state`). **Keine `localStorage`- oder Server-DB-Persistenz**.
  6. *Test & UI:* `ui.renderCombat()` zeichnet Lebensbalken im 2D Canvas Overlay.
- **Stealth & Pickpocketing Audit:** Exakt **0 Vorkommen** von `stealth` oder `pickpocket` in dieser Datei!

---

### 1.2 `v21_creator_events.js` (16.837 Bytes)
- **Hauptmethoden:** `createMap21()`, `enterMap21()`, `leaveMap21()`, `creatorObject21()`, `publishMap21()`, `contributeEntity21()`.
- **Execution-Chain:**  
  1. *Definition:* `createMap21(name, config)` legt benutzerdefinierte Karte an.
  2. *Invocation:* Aufruf über Creator-Formular-Submits.
  3. *Reachable Player Action:* Eingabe von Kartennamen und Typ-Auswahl (`konzert_buehne`, `dungeon`).
  4. *Stateänderung:* Schreibt neues Objekt in `state.customMaps`.
  5. *Persistenz:* In-Memory State Objekt.
  6. *Test & UI:* `ui.syncCreator()` aktualisiert Kachelliste.
- **Konzerte-Audit (36 Vorkommen):** "Konzerte" existieren ausschließlich als **statische Raum-Typ-Strings** (`"konzert_buehne_wuppertal"`) und Test-Gate-Triggers für Playwright. **0% interaktives Rhythmus-/Konzert-Gameplay**.

---

### 1.3 `v21_underworld.js` (16.530 Bytes)
- **Hauptmethoden:** `enterUnderworld()`, `exitUnderworld()`, `descendUnderground()`, `nearestUnderground()`, `mineVein()`.
- **Execution-Chain:**  
  1. *Definition:* `mineVein(veinId)` prüft Entfernung zur Mine.
  2. *Invocation:* Klick auf Untergrund-Erzkachel im Grid.
  3. *Reachable Player Action:* Abbau von Dust-Adern ("Staubader").
  4. *Stateänderung:* Dekrementiert `vein.amount` und inkrementiert `state.inventory[res]`.
  5. *Persistenz:* In-Memory State.
  6. *Test & UI:* `ui.syncUnderworld()` aktualisiert Inventar-Anzeige.

---

## 2. REPRÄSENTATIVE BEWEIS-MATRIX FÜR ENTSCHEIDENDE MECHANIKEN

| Mechanik | Code-Datei | Gefundene Methoden | Echte UI-Anbindung | Urteil |
|---|---|---|---|---|
| **Combat (Kampf)** | `v21_combat_loot_pause.js` | `attack21()`, `healDuringPause21()` | Klickbares 2D Canvas Kampf-Panel | **REALE 2D CANVAS MECHANIK** |
| **Mining (Bergbau)** | `v21_underworld.js` | `mineVein()`, `descendUnderground()` | Untergrund-Kachel Klick & Inventar | **REALE 2D CANVAS MECHANIK** |
| **Creator (Editor)** | `v21_creator_events.js` | `createMap21()`, `publishMap21()` | Text-Formular Eingabe | **PASSIVER FORMULAR-HOOK** |
| **Konzerte** | `v21_creator_events.js` | `contributeEntity21()` | Raum-Typ Tag `"konzert_buehne"` | **PURE STRING-METADATEI** |
| **Stealth** | *keine* | 0 Vorkommen in allen 3 Modulen | Keine UI-Anbindung | **0% CODE IN DIESEN JS-MODULEN** |
| **Pickpocketing** | *keine* | 0 Vorkommen in allen 3 Modulen | Keine UI-Anbindung | **0% CODE IN DIESEN JS-MODULEN** |
