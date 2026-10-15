# Code-Archäologie — Register verwaister Dateien

Kein Umzug, kein physisches Verschieben — bewusste Entscheidung (2026-08-15, siehe
`code_archaeologie_historiendoku.md`): der Fundort ist Teil der Geschichte, und ein Umzug
riskiert, eine fälschlich als tot eingestufte Datei zu beschädigen oder Zeitstempel zu
verlieren, auf denen die ganze chronologische Rekonstruktion beruht. Stattdessen: dieses
Register hält an einer einzigen, menschenlesbaren Stelle fest, was bei der laufenden
Code-Archäologie (`code_archaeologie_lernprotokoll.md` / `code_archaeologie_historiendoku.md`)
als tatsächlich verwaist bestätigt wurde.

Aufnahme-Kriterium: nicht "sieht alt aus", sondern konkret geprüft — kein aktiver Import,
kein laufender systemd-Dienst, kein Cronjob, der die Datei lädt (Nachweis jeweils in der
Historiendoku dokumentiert, hier nur die Kurzfassung + Verweis).

| Pfad (logisch) | Physischer Pfad | Nachfolger | Geprüft am | Beleg |
|---|---|---|---|---|
| `agent/dak_gord_system/zustand.py` | `/root/werkraum_agent/dak_gord_system/zustand.py` | `agent/dak_gord_system/graphen/gespraechsgraf.py` (via `web_chat.py`, `dak-gord-web.service`) | 2026-08-15 | Historiendoku Datei 1 |
| `agent/dak_gord_system/graf.py` | `/root/werkraum_agent/dak_gord_system/graf.py` | s.o. | 2026-08-15 | Historiendoku Datei 1 |
| `agent/dak_gord_system/aufforderungen/code_regeln.md` | `/root/werkraum_agent/dak_gord_system/aufforderungen/code_regeln.md` | kein direkter Nachfolger identifiziert (Prinzip lebt sinngemäß in `/root/CLAUDE.md` Skalpell-Prinzip weiter) | 2026-08-15 | Historiendoku Datei 2 |
| `agent/dak_gord_system/aufforderungen/system.md` (+ `.save`, `.save.1`, `.save.2`, `.save.3`) | `/root/werkraum_agent/dak_gord_system/aufforderungen/system.md*` | vermutlich `agent/dak_gord_system/verfassung_loader.py` + `verfassung/`-Verzeichnis (noch nicht einzeln verifiziert) | 2026-08-15 | Historiendoku Datei 3 |

Wächst mit jeder weiteren bestätigt-verwaisten Datei aus der laufenden Durchsicht.
