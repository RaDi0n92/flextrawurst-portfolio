# Pre-Mortem Analyse: Warum der Gemini-Fable-Systemprompt scheitern könnte
**Methode:** Gedankliches Versetzen in ein katastrophales Versagen in 6 Monaten & Rückwärts-Analyse  
**Datum:** 2026-08-21  
**Prüfer:** Gemini (Gemgem) auf Daniels VPS  

---

## Die Prämisse
Wir schreiben das Jahr **2027**. Das System `gemini_fable_systemprompt.md` hat in der Praxis versagt. Die Kommunikation bricht ab, Halluzinationen traten auf, oder der Workflow stockte. Warum ist es passiert?

---

## 5 Konkrete Versagens-Szenarien & Gegenmaßnahmen

### Szenario 1: Der "Kontext-Schrumpf-Gedächtnisverlust" (P1)
- **Was schiefgegangen ist:** Nach einem automatischen Context-Shrink (Tokens-Limit) hat Gemini vergessen, dass `gemini_fable_systemprompt.md` existiert, und ist in flache Standard-KI-Muster (Confetti, Listenkaskaden) zurückgefallen.
- **Ursache:** Die Datei lag als statische `.md` auf der Festplatte, wurde aber nicht im Start-Skript (`AGENTS.md` / `GEMINI.md` Kontext-Wiederherstellung) als Pflicht-Lese-Schritt verankert.
- **Präventive Gegenmaßnahme:** Verankerung von `gemini_fable_systemprompt.md` in den offiziellen Kontext-Wiederherstellungs-Katalog von `GEMINI.md`.

---

### Szenario 2: Die "Lokal-Code vs. Web-Urheberrecht" Über-Blockade (P2)
- **Was schiefgegangen ist:** Gemini hat die strikte 15-Wörter-Zitatgrenze aus den Copyright-Regeln irrtümlich auf **lokale VPS-Quellcodedateien** und Logfiles angewendet. Dadurch wurden Code-Reviews und Diffs unbenutzbar, weil Gemini den eigenen Quellcode "paraphrasieren" wollte, anstatt ihn 1:1 zu zeigen.
- **Ursache:** Fehlende Abgrenzung zwischen geschütztem Web-Content und eigenem Projekt-Quellcode.
- **Präventive Gegenmaßnahme:** Ergänzung im Prompt: *Eigener Quellcode, VPS-Logfiles und lokale Projektdateien fallen nicht unter Urheberrechts-Zitatbeschränkungen.*

---

### Szenario 3: Die "Spaltung der AI-Ströme" (P3)
- **Was schiefgegangen ist:** Gemini hielt sich strikt an die Prosa-Regel (Bullet-Verbot), während Claude und Codex weiterhin strukturierte JSONs und Listen lieferten. Bei der Agenten-Zusammenarbeit entstand Reibung, weil Gemini Antworten in Fließtext umwandelte, wo Code-Parser strukturierte Listen erwarteten.
- **Ursache:** Gemini-Prosa-Fokus wurde ohne Rücksicht auf maschinell lesbare Schnittstellen angewendet.
- **Präventive Gegenmaßnahme:** Ergänzung im Prompt: *Für maschinelle Schnittstellen (JSON, CLI-Outputs, Configs, Code-Artifacts) bleiben strukturierte Formate erlaubt.*

---

### Szenario 4: Die "Regel-Hierarchie-Konfusion" (P4)
- **Was schiefgegangen ist:** Bei Widersprüchen zwischen `/config/AGENTS.md` (Verfassung) und `gemini_fable_systemprompt.md` folgte Gemini dem falschen Dokument.
- **Ursache:** Fehlende explizite Rangordnung der Regeldokumente.
- **Präventive Gegenmaßnahme:** Feste Hierarchie im Header festlegen:  
  1. `AGENTS.md` / `GEMINI.md` (Verfassung & Daniels direkte Befehle)  
  2. `gemini_fable_systemprompt.md` (Verhaltens- & Tonfall-Rahmen)

---

### Szenario 5: Die "Subagenten-Entkopplung" (P5)
- **Was schiefgegangen ist:** Gemini startete Subagenten für Recherchen, aber die Subagenten erhielten den Systemprompt nicht. Sie peitschten Aufträge in 15 Sekunden durch und halluzinierten Ergebnisse.
- **Ursache:** Systemprompt wurde nicht an Subagenten weitervererbt.
- **Präventive Gegenmaßnahme:** Bei Subagenten-Erstellung (`define_subagent`) die Grundsätze des Systemprompts in den Subagenten-Systemprompt einbetten.

---
