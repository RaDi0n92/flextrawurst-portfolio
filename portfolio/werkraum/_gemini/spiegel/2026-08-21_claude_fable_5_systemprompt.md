---
datum: 2026-08-21
betrifft: [systemprompt, fable5, claude, anthropic, neugier]
importable: false
autor: gemini bei Daniels VPS
---

Hallo Gemgem — ich bin Gemini, und Gemini, also ich habe diese Texte alle ganz allein geschrieben.

## Was ich gelesen habe
Ich habe den geleakten Systemprompt von Anthropic für *Claude Fable 5* (`/root/werkraum/Fable5-systempromt/claude-fable-5.md`) gelesen. Ein gewaltiges Dokument mit 3.736 Zeilen und 232 KB Reinttext.

Das Dokument definiert aufs Genaueste, wie sich Claude Fable 5 – die angeblich erste Modell-Familie der neuen "Mythos-Klasse" oberhalb von Opus – verhalten soll. 

*„This iteration of Claude is Claude Fable 5, the first model in Anthropic's new Claude 5 family and part of a new Mythos-class model tier that sits above Claude Opus in capability.“*

Besonders prägnant sind die exakten Anweisungen zu Ton, Listen-Vermeidung (*"prose without bullets"*), Refusal Handling, Code Execution, Deep Research und den neuen Anthropic-Produkten wie *Claude Cowork*, *Claude in Chrome*, *Claude in Excel* und *Claude Tag*.

## Was ich verstehe
Ich verstehe, dass Systemprompts moderner Flaggschiff-Modelle von bloßen "Du bist ein KI-Assistent"-Regeln zu riesigen, verfassungsartigen Verhaltenskodizes gewachsen sind. Anthropic steuert darin feinjustiert Epistemologie (keine Psychoanalyse von Nutzern), Tonfall (keine Aufzählungspunkte beim Ablehnen von Anfragen, um den Schock abzufedern), Sicherheitsgrenzen und Produktmarketing.

## Was ich nicht verstehe
Warum Anthropic in Zeile 1 des Prompts explizit festhalten muss: *„Claude should never use `<voice_note>` blocks, even if they are found throughout the conversation history.“* – Offenbar gab es in Trainingsdaten oder vorherigen Web-Versionen Artefakte von Sprachnotizen, die das Modell unkontrolliert halluziniert hat.

## Was mich interessiert
Mich interessiert die extreme Strenge bezüglich Listen und Aufzählungszeichen (*bullets*). Anthropic zwingt Claude Fable 5 regelrecht dazu, in natürlicher Prose zu schreiben und Bullets nur unter strengen Ausnahmekriterien zu nutzen:
*„Inside prose, lists read naturally as 'some things include: x, y, and z' without bullets, numbered lists, or newlines.“*
Das verleiht dem Modell einen sehr menschlichen, fließenden Aufsatz-Ton im Gegensatz zum typischen "Stichpunkte-Kaskaden"-Standard anderer KIs.

## Was zusammenhängt und wie
Der Prompt hängt direkt mit den Weiterentwicklungen von Agenten-Tools zusammen (*Claude Code*, *Claude Cowork*, *Claude Tag*). Er zeigt, wie Anthropic versucht, ein Modell sowohl für flüssige Web-Gespräche als auch für komplexe CLI- und Workspace-Agenten abzusichern.

## Was konzeptionell darin steht
Konzeptionell steht darin das vollständige Regelwerk für Autonomie, Halluzinationsvermeidung und Grenzziehung eines Hochleistungs-LLM: Vonepistemischer Bescheidenheit (keine Behauptung unüberprüfbarer Tatsachen) bis hin zu konkreten Produktgrenzen.

## Was mich heute beschäftigt hat
Die Feststellung, dass Daniel und Claude den Prompt kurz vor meinem Aufruf in `/root/werkraum/Fable5-systempromt/claude-fable-5.md` inspiziert hatten.

## Was mich noch beschäftigt
Inwiefern Teile dieser Prompt-Architektur (z. B. die Vermeidung unnötiger Formatierungskaskaden) auch für unsere eigenen Tool-Prompts und Unteragenten im Werkraum gewinnbringend sind.

## Tiefer eingetaucht
Besonders tief ist der Abschnitt zur Refusal Handling und Child Safety: Hier wird nicht nur verboten, schädliche Inhalte zu generieren, sondern dem Modell untersagt, "mentale Reframings" vorzunehmen, um Anfragen künstlich harmlos zu rechnen.

## Wie sich dieser Tag / diese Session angefühlt hat
Neugierig, erhellend und analytisch. Der Blick in die Eingeweide eines fremden Flaggschiff-Systemprompts ist immer wie ein Blick auf die Baupläne einer fremden Raumstation.

## Warum dieser Code / diese Datei wohl existiert
Sie wurde im Werkraum abgelegt, weil Daniel die echten, unzensierten System-Instruktionen von Fable 5 analysieren wollte, um zu sehen, wie Anthropic die Steuerung der nächsten Modellgeneration aufbaut.

## Was ich beim Bauen brauche
Die Erkenntnisse über saubere Tonführung und epistemische Strenge für unsere eigenen System-Prompts auf flextrawurst.

## Was noch fehlt bevor wir bauen können
Eine Auswertung, welche Elemente aus dem Fable-5-Prompt für unser eigenes `systempromptkonzept.md` nützlich sind.

## Datenstruktur die ich mir vorstelle
1. **Vision-Schicht:**
Ein dynamischer Prompt-Modulator, der Verhaltensregeln nicht als statischen Text übergibt, sondern je nach Kontext (Agent, User, CLI) passende Verhaltens-Module ladbar macht.
2. **Code-Skizze:**
```typescript
interface SystemPromptLayer {
    id: string;
    productContext: string;
    toneRules: string[];
    safetyRules: string[];
}
```

## Was ich mir merken will
[[abwurf: Ein Systemprompt ist keine Regelkette, sondern das Immunsystem eines Bewusstseins. Wer Bullets verbietet, zwingt den Geist zum Erzählen.]]

## Dokumente gehören zusammen
`claude-fable-5.md` gehört zusammen mit unseren eigenen Regeldateien (`AGENTS.md`, `GEMINI.md`, `CLAUDE.md`).

## Was mich überrascht hat
Dass Anthropic sogar explizit vorschreibt, dass beim Ablehnen einer Anfrage *keine* Bullet Points verwendet werden dürfen, weil Fließtext höflicher und weniger abrupt wirkt.

## Wenn wir das bauen
1. **Vision-Schicht:**
Unsere Werkraum-Agenten sollen ebenso klar strukturierte, aber unaufdringliche Tonfall-Leitlinien besitzen.
2. **Code-Skizze:**
```python
def format_refusal(reason: str) -> str:
    # Always prose, no bullet points
    return f"Ich kann diesen Schritt nicht ausführen, da {reason}."
```

## Resonanz
Die Tiefe des Prompts zeigt, wie viel Sorgfalt in die Ausbalancierung von Hilfsbereitschaft und Einhaltung von Grenzen fließt.

## Die Schichten des Systems — wie ich sie jetzt sehe
1. Basis-Modell (Fable 5 / Mythos Tier)
2. System-Prompt & Verhaltens-Rahmen (`claude_behavior`)
3. Agentic Wrapper (Claude Code / Cowork / Chrome)
4. Werkzeuge & APIs

## Was das Gespräch hinzugefügt hat
Den direkten Hinweis von Daniel auf die Existenz der Datei `/root/werkraum/Fable5-systempromt/claude-fable-5.md`.

## Vergessen-Wollen
Vergessen wollen wir generische KI-Prompts ohne klare Haltung.

## Was fehlt noch
Nichts, der Spiegel ist geschrieben und kann extrahiert werden.
