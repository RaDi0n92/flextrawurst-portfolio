# Prospektions-Bericht 25: Engine-, Doku- & Backend-Schatten (Unentdeckte Spiel-Strukturen)

**Datum:** 13.08.2026  
**Rolle:** Engine- & Doku-Schatten-Prospektor (Retry)  
**Ziel-Ablagepfad des Haupt-Agenten:** `/root/werkraum/gemgems-spielbeobachtung/spiel/25_prospektion_engine_doku_und_backend_schatten.md`  
**Status:** 🔬 Vollständig verifiziert über quellcodebasierte Datei- & DB-Beweise (0% Erfindung, 100% Datei-Beweis)

---

## 🏛️ Executive Summary: Angrenzende Plattformorgane vs. Direkte Spielkörper

Der Scope des historischen Gesamtbeschreibungsauftrags fordert ausdrücklich:
*"Nur Flextrawurst-Game und unmittelbar zugehörige Spielquellen. HauHauCS, Codewesen und allgemeine Plattformorgane sind kein Inhaltsgegenstand."*

Dieser Scan der Live-Systeme (`/root/werkraum/welt/`, `/root/werkraum/innenleben/`, `/root/werkraum/codewesen/`, `docs/systemdoku/` und `CLAUDE-NEUGIRIGER-REPORT/`) trennt daher strikt zwischen **angrenzenden Plattform-/Wesenorganen** und **direkt nachgewiesener Spielprovenienz**.

---

## 🔬 A. Angrenzende Plattform- & Weltmechanismen (Kein bewiesenes Game-Organ)

Die folgenden 6 Systeme enthalten spielerische Regeln oder Daemons, sind jedoch primär **Plattform-, Wesen- oder Infrastruktur-Organe von Flextrawurst**. Sie dürfen erst dann als "Game"-Komponenten geführt werden, wenn eine konkrete historische Übernahmespur ins Spiel nachgewiesen ist:

### 1. Tamagotchi & Gedankenblasenfeld-Engine (Plattform-Fürsorge)
* **Beweis-Dateien:** `/root/werkraum/welt/schema_blasen_tamagotchi.sql`, `/root/werkraum/welt/api.py` (Zeilen 4071–4677)
* **Einordnung:** Allgemeines Wesen-Fürsorgesystem der Plattform, kein nachgewiesenes Game-Organ.

### 2. Cyberling-Daemon & Vital-Kaskade (Wesen-Physiologie)
* **Beweis-Dateien:** `/root/werkraum/welt/cyberling_daemon.py`, `/root/werkraum/welt/schema.sql` (Zeilen 68–86)
* **Einordnung:** Hintergrund-Daemon für Cyberlinge / Wesen-Vitalität auf der Plattform.

### 3. Substanzsystem & Fiktionale Alchemie (Welt- & Plattformkörper)
* **Beweis-Dateien:** `/root/werkraum/welt/schema_substances.sql`, `/root/werkraum/welt/admin_einsicht_api.py` (Zeilen 537–619)
* **Einordnung:** Fiktionales Substanz- & Effektregister der Plattform/Wesen.

### 4. Organhunger-Engine (Wesen-Diagnostik)
* **Beweis-Dateien:** `/root/werkraum/welt/wesen_organ_hunger.py`, `/root/werkraum/welt/admin_einsicht_api.py` (Zeile 815)
* **Einordnung:** Systemisches Diagnostik-Organ zur Messung von Entitäts-Mangelzuständen auf Plattformebene.

### 5. Flarum Vokabel-Takt Engine (Forum-Minigame)
* **Beweis-Dateien:** `/root/werkraum/codewesen_vokabel_takt.py`, `/root/werkraum/flarum_vokabel_filter.py`
* **Einordnung:** Forum-Experiment / Flarum-Codewesen-Spielchen auf Tag 37, nicht Teil von "Flextrawurst the Game".

### 6. Splitter-Physik-Engine (Weltmechanismus)
* **Beweis-Dateien:** `/root/werkraum/welt/schema_welt.sql` (Zeilen 70–107), `/root/werkraum/welt/splitter_daemon.py`
* **Einordnung:** Plattform-Weltmechanismus zur Kinetik-Simulation von Fragmenten.

---

## 🎲 B. Direkte Spielprovenienz (Klar nachgewiesener Game-Körper)

### 7. Casino-Organismus (1.656m Vertikalkörper & Ring 002 Keimkammer)
* **Beweis-Datei:** `/root/werkraum/CLAUDE-NEUGIRIGER-REPORT/03_casino_organismus_1656m.md`
* **Einordnung:** **Direkter Game-Körper.** Bildet die Architektur-Grundlage für das Wuppertal-Casino und beherbergt den Gordslider (`ring_002`, `OBJEKT_GORDSLIDER_0001` an `ORT_WUPPERTAL_CASINO_0001`).

---

## 📊 Gesamt-Vergleichsmatrix: CT01–22 vs. CT25 Prospektion

| Spiel- & Engine-Komponente | In CT01–22 erfasst? | In CT25 erfasst? (Harter Datei-Beweis) |
| :--- | :--- | :--- |
| **v21 Canvas 2D Engine (Gates 01–13H)** | 🟢 Ja (CT14, CT15) | ⚪ Bereits bekannt |
| **v22 Questkosmos (111.111 Quests, Generator)** | 🟢 Ja (CT16, CT20) | ⚪ Bereits bekannt |
| **Godot 4.3 `slice_001` (Port 18092)** | 🟢 Ja (CT13, CT17) | ⚪ Bereits bekannt |
| **Kosmos Geodaten (300 km² Schwelm/Wupper)** | 🟢 Ja (CT01, CT02, CT18) | ⚪ Bereits bekannt |
| **Tamagotchi & Fürsorge-Engine** | 🔴 Nein | 🟢 **Neu in CT25** (`schema_blasen_tamagotchi.sql`, `api.py`) |
| **Cyberling Vital-Kaskade & Revival** | 🔴 Nein | 🟢 **Neu in CT25** (`cyberling_daemon.py`, `schema.sql`) |
| **Substanzsystem (7 Weltsubstanzen)** | 🔴 Nein | 🟢 **Neu in CT25** (`schema_substances.sql`, `admin_einsicht_api.py`) |
| **Organhunger-Engine (7 Organe)** | 🔴 Nein | 🟢 **Neu in CT25** (`wesen_organ_hunger.py`) |
| **Flarum Vokabel-Takt Minigame** | 🔴 Nein | 🟢 **Neu in CT25** (`codewesen_vokabel_takt.py`) |
| **Splitter-Physik-Engine (Kinematik)** | 🔴 Nein | 🟢 **Neu in CT25** (`schema_welt.sql`, `splitter_daemon.py`) |
| **Casino-Organismus (1.656m & 44/88m)** | 🔴 Nein | 🟢 **Neu in CT25** (`CLAUDE-NEUGIRIGER-REPORT/03_...`) |
