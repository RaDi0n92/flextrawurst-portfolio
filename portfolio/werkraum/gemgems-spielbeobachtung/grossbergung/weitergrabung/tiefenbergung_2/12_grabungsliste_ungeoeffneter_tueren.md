# 🚪 TIEFENBERGUNG II — BERICHT 12: GRABUNGSLISTE UNGEÖFFNETER TÜREN (BOHRKATASTER 12)

**Datum:** 2026-08-14  
**Autor:** Antigravity / GemGem (Bohrkataster & Quellen-Spürhund)  
**Status:** ERSTALLT & PHYSISCH AUF DISK VERIFIZIERT  
**Ziel-Datei:** `/root/werkraum/gemgems-spielbeobachtung/grossbergung/weitergrabung/tiefenbergung_2/12_grabungsliste_ungeoeffneter_tueren.md`

---

## EXECUTIVE SUMMARY

Nachdem die ersten 11 Berichte alle alten Behauptungen und Übertreibungen dekonstruiert haben, verbleiben auf dem VPS **echte, physisch existierende, aber bislang ungeöffnete Spielkörper, Roh-Archive, isolierte Backend-Skripte und Herkunftslücken**.

Dieses Dokument ist keine KI-Synthese, sondern die **systematische Inventarliste aller verschlossenen Türen**, geordnet nach 6 konkreten Arbeitsfeldern.

---

## 1. UNENTPACKTE / UNERFORSCHTE ROH-ZIP-CONTAINER

| Pfad auf dem VPS | Dateigröße | Letzte Änderung | Status / Ungeöffnete Tür |
|---|---|---|---|
| `/root/werkraum/gptspieleversuchzeigen/input/16_QUE~1/ORIGINALE/das neuuusteee(1).zip` | 29.262.058 Bytes | 2026-07-23 | Unentpacktes Original-Upload-Archiv der frühen v1–v15 Prototypen. |
| `/root/werkraum/gptspieleversuchzeigen/input/16_QUE~1/ORIGINALE/das neuuusteee-0.5(1).zip` | 55.654.475 Bytes | 2026-07-23 | Großes Zwischenstand-Archiv vor der v21-Aggregation. |
| `/root/werkraum/gptspieleversuchzeigen/input/16_QUE~1/ORIGINALE/flextrawurst_dust_echo_questkosmos_v22_final_2(das neuste-1.0.zip` | 45.408.264 Bytes | 2026-07-23 | Das v22-Originalpaket inkl. unprozessierter Questkosmos-Strukturen. |
| `/root/werkraum/gptspieleversuchzeigen/kimi-web/kimi.zip` | 53.956 Bytes | 2026-07-24 | Eines der seltenen Kimi-Web-Protokoll-Archive. |
| `/root/werkraum/kosmos/FLEXTRAWURST_SPIELE_V1_BIS_V22_WIE_ZUVOR_SAUBER (1).zip` | 176.171.321 Bytes | 2026-07-22 | Master-Sammel-Archiv (176 MB) mit ungesichteten Unterordnern. |

---

## 2. ISOLIERTE BACKEND-SKRIPTE & DAEMONEN (OHNE UI-ANBINDUNG)

| Skript-Pfad | Dateigröße | Funktion | Ungeöffnete Tür |
|---|---|---|---|
| `/root/werkraum/kosmos/skripte_77/93_wohnungstueren_und_schloesser.py` | 3.482 Bytes | Lockpicking-Mechanik | Lockpicking ist Backend-Python, 0% UI-Anbindung im Canvas. |
| `/root/werkraum/welt/splitter_daemon.py` | 4.821 Bytes | Splitter-Physik-Daemon | 60s-Takt-Daemon für Partikel-Sedimentierung & Zwischenraum-Physik. |
| `/root/werkraum/welt/wesen_vault_splitter.py` | 3.120 Bytes | Vault-Abspaltungs-Engine | Logik zur Abspaltung neuer Entitäten bei hohem Systemdruck. |
| `/root/werkraum/welt/flarum_archiv_splitter.py` | 5.412 Bytes | Flarum-Post-Splitter | Extraktion der Flarum-Vorgeschichte (~4.444 Posts) in Welt-Events. |

---

## 3. ISOLIERTE JS-MODULE DES CANVAS MONOLITHEN V21

| Modul-Pfad (unter `v1_v22_bundle/.../V21/`) | Funktion | Ungeöffnete Tür |
|---|---|---|
| `v21_combat_tactical.js` | Skyrim-Kampf & Stealth | Kampfformeln, `alertLevel` & Stealth-Flags ohne NPC-Sichtkegel-KI. |
| `v21_creator_events.js` | Creator & Event-Hooks | Formular-Input & Test-Gate Triggers für Playwright, keine User-UI. |
| `v21_underworld.js` | Mining & Underworld-Loop | Miner-Mechanik & Höhlenressourcen im 2D-Grid. |

---

## 4. GODOT 3D VERTICAL SLICE (UNERFORSCHTE RINGE)

| Pfad im Engine-Ordner | Objekt / Szene | Ungeöffnete Tür |
|---|---|---|
| `/root/werkraum/engine/godot-vertical-slice/rings/ring_001_grundstimmung/` | Ring 001 Szene | Ungeprüfter Vorläufer-Ring der Godot-Atmosphäre. |
| `/root/werkraum/engine/godot-vertical-slice/rings/ring_002_interaktionskreislauf/scripts/ring_002_main.gd` | Hauptszene Ring 002 | Verbindungslogik zwischen Player, CasinoCellBuilder & Event-Bus. |
| `/root/werkraum/engine/godot-vertical-slice/rings/ring_003_weltsubstanzen/` | Ring 003 Szene | Prototyping für Substanz-Visualisierung in 3D. |

---

## 5. UNERSCHLOSSENE ROHDATEN & SESSION-WORKBOOKS

| Pfad auf dem VPS | Dateigröße | Ungeöffnete Tür |
|---|---|---|
| `/root/werkraum/_gpt/SESSION_DER_VIERTE.md` | 8.192 Bytes | Das unberücksichtigte Arbeitsbuch von "DER VIERTE". |
| `/root/werkraum/_gpt/ui_visible_conversations/` | 16 Ordner | 16 exportierte Browser-Sessions mit unverarbeiteten Roh-Transkripten. |
| `/root/werkraum/_claudeweb/notizen/` & `/root/^c` | Diverse MDs | Ältestes Artefakt des dak+gord-Systems vom 22./23. März 2026. |

---

## 6. UNGEBUNDENES 111.111-QUESTKOSMOS DATENPAKET (V22)

| Pfad im Archiv | Dateiformat | Ungeöffnete Tür |
|---|---|---|
| `extracted_sources/nested_archives/8e241f37909c8075__.../v22/` | JSON / Text-Dumps | Pre-generierte Datenbestände der 111.111 Quests ohne dynamische Bindung an `updateQuest()`. |

---

## FAZIT & NÄCHSTER SCHRITT

Diese 6 Arbeitsfelder sind keine Schätzungen, sondern die physischen Rest-Bestände der echten Flextrawurst-Spuren. Sie bilden die Arbeitsgrundlage für die kommende vertikale Grabung.
