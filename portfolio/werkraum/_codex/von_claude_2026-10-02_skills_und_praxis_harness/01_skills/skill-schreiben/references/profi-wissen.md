# Was Profis über gute Skills sagen

Inhalt aus dem Netz ist **Anregung**, keine Wahrheit.

„Bestätigt“ heißt: mehrere voneinander unabhängige Quellen sagen dasselbe.

Stand der Recherche: 2026-10-02.

## Inhalt

1. Beschreibung und Auslöser
2. Aufbau und Länge
3. Skills, die Agenten wirklich befolgen
4. Harness und Graph
5. Daniels eigene Regeln
6. Quellen

## 1. Beschreibung und Auslöser (bestätigt)

- Name und Beschreibung sind das Einzige, was der Agent vor dem Auslösen sieht.
  Sie sagen, **wann** man zum Skill greift, nicht, wie er funktioniert. Höchstens 1024 Zeichen.
- Dritte Person, konkrete Auslöser („Verwenden, wenn …“) **und** Gegenfälle („Nicht verwenden für …“).

## 2. Aufbau und Länge (bestätigt)

- SKILL.md schlank (unter 500 Zeilen).
  Schweres kommt in `references/`, `scripts/`, `assets/`, jeweils nur eine Ebene tief.
- Just-in-time laden: im Text sagen, **wann** welche Datei zu lesen ist.
- Mechanisches gehört in Skripte, die ohne Laden in den Kontext laufen.

## 3. Skills, die Agenten wirklich befolgen

- Agenten wählen gern den kürzesten Weg und überspringen Schritte.
  Gegenmittel (mehrere Quellen): **Prüfpunkte mit Beleg**, **Ende-Kriterien** und eine
  **Tabelle der üblichen Ausreden mit freundlicher Gegenrede**.
- Kurze, klare Anweisungen schlagen lange Meisterprompts.
  Neuere Modelle prüfen sich schon selbst (Hinweis aus einer Quelle, nicht bestätigt).
- Dauerregeln („nach jeder Änderung testen“) sind **Standing orders**, keine Einmal-Schritte.
- Validierungsschleife: tun, validieren (Skript, Checkliste), beheben, wiederholen.
- Erklären, warum, statt schwerer Befehle (Skill-Creator-Anleitung).

## 4. Harness und Graph (das Prinzip ist bestätigt)

- Workflows als **expliziter Graph** (Knoten, Kanten, Zustand) statt Hoffnung auf das Kontextfenster.
  Der Zustand wird gespeichert, Übergänge werden geprüft.
- Greift der Agent vor erfüllten Vorbedingungen zu, gibt die Laufzeit **gezielte Abhilfe** für den ersten
  offenen Schritt zurück (PolicyGuide). Das ist der Weg: lenken, nicht nur sperren.
- Graphen erlauben formale Prüfungen (Erreichbarkeit, Vorbedingungen, Freigabestellen) und Wiedergabe.

## 5. Daniels eigene Regeln

- Nichts im Verborgenen: Der Mensch muss jeden Prüfschritt nachvollziehen können.
- Agenten auf Augenhöhe: Sie tun, was ein Mensch täte.
- Roh und ehrlich bleiben, nicht zu Stichpunkten glätten.
- Netzinhalt ist Anregung. Erst unabhängige Bestätigung macht ihn belastbar.

## 6. Quellen

- mgechev, Skills Best Practices — [Adresse entfernt]
- Agent Skills, Beschreibungen — [Adresse entfernt]
- Agent Skills, Best practices — [Adresse entfernt]
- PostHog, What nobody tells you about writing agent skills — [Adresse entfernt]
- Addy Osmani, Agent Skills — [Adresse entfernt]
- Developers Digest, Exit criteria — [Adresse entfernt]
- PolicyGuide (Workflow-Graph, gezielte Abhilfe) — [Adresse entfernt]
- Agentic Workflow Orchestration — [Adresse entfernt]
- Skill-Creator-Anleitung, lokal: in `marketplace-cache/*/plugins/skill-creator/skills/skill-creator/`
