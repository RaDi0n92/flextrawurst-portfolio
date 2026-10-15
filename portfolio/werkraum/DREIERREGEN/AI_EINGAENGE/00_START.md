---
titel: AI-Eingänge
typ: sammelkarte
status: aktiv
erstellt: 2026-07-26
tags:
  - ai_stroeme
  - eingang
  - provenienz
---

# AI-EINGÄNGE

Jeder AI-Strom besitzt einen getrennten Eingang.

- [[claude/README|Claude Code]]
- [[chatgpt/README|GPT-5.6-sol-hoch / ChatGPT]]
- [[gemini/README|Gemini]]
- [[grok/README|Grok]]
- [[kimi/README|Kimi]]

## Eingangsregel

Ein Beitrag bleibt zunächst in seinem Herkunftsordner und wird nicht automatisch in Kernvertrag, Matrix oder Bauauftrag kopiert.

Jede Eingabedatei sollte enthalten:

```yaml
ai_strom:
modell:
sitzung:
datum:
ausloeser:
quellen:
wahrheitsklasse:
status: eingang_nicht_kanonisch
```

## Mögliche Wahrheitsklassen

- `QUELLENBEFUND`
- `ABLEITUNG`
- `MODELL`
- `GEGENENTWURF`
- `BAUVORSCHLAG`
- `REDTEAM`
- `UNGEPRUEFT`

## Übernahme

Eine Übernahme in den gemeinsamen Körper benötigt:

- unveränderten Originalpfad,
- Benennung des übernommenen Ausschnitts,
- erkennbare Auslassungen,
- Daniel-Freigabe bei Weltbedeutung,
- Eintrag im Entscheidungslog,
- neues Ziel mit eigenem Status.

## Kein Stimmenbrei

Widersprüche bleiben zunächst nebeneinander. Es wird kein künstlicher Konsens erzeugt, nur weil mehrere Modelle höflich dieselben Substantive benutzen.

---

Zurück: [[../00_START_HIER]] · [[../08_ZUSAMMENARBEIT_DER_AI_STROEME]]
