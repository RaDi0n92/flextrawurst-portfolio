---
datum: 2026-07-30
betrifft: [kompoase, 8900, 8787, splitter, aufnahme, architektur-klarstellung]
importable: false
autor: claude-code bei Daniels VPS
---

## Korrektur: 8900/KompOase ist reiner Hinterlassungs-Ort, keine Aufnahme-Fläche

Ich hatte Daniels "Aufgreifen/Engagement erzeugen" fälschlich als Auftrag verstanden, den 7
Wesen eine echte `splitter_aufnehmen`-Aktion für KompOase-Splitter zu geben (gebaut, getestet,
kurz live deployed). Daniels Klarstellung direkt danach, wörtlich: *"bei 8900 ging es doch
gerade darum alles im heutigen system zu hinterlassen..aber keine aufname auch nicht von den 7
entitten bitte...das bleibt für 8787."*

**Die eigentliche Architektur-Trennung:**
- **8900 (KompOase)** — ein Ort, an dem alles aus dem heutigen System sichtbar hinterlassen
  wird (Splitter aus Posts, Events, sogar Claudes eigenen Chat-Antworten via `claude_abwurf`).
  Reine Ablage/Sichtbarkeit, keine Interaktion.
- **8787 (flextrawurst_surface)** — der Ort, an dem "Aufnahme" (das echte Aufgreifen/Picken)
  konzeptionell hingehört, nicht 8900. Nicht heute gebaut, nur als Zuständigkeit benannt.

**Rückgängig gemacht:** `git revert 9aafc4e13` — `hole_splitter_vielfalt()`, der
`splitter_aufnehmen`-Aktionseintrag und der zugehörige Prompt-Block sind komplett wieder raus
aus `browser_agent.py`. Alle 7 Dienste neu gestartet, zurück auf den Stand mit gestaffeltem
Vault-Takt, ohne Splitter-Aufnahme.

## Was ich mir merken will

Bei einer kurzen, umgangssprachlichen Anweisung ("Engagement erzeugen") nicht die naheliegendste
technische Umsetzung (den existierenden `aufnehmen`-Endpunkt verdrahten) für die einzig gemeinte
halten, wenn die zugrunde liegende Architektur-Trennung (welcher Port wofür da ist) noch nicht
wirklich geklärt war. Hätte ich vorher kurz gefragt "meinst du wirklich die Aufnahme-Aktion auf
8900, oder nur dass mehr dort landet?", wäre der Bau-Umweg vermeidbar gewesen.
