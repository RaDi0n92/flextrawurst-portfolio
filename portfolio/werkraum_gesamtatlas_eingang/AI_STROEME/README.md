# AI_STROEME/ — verbindliche Ablagekonvention pro Strom

Entstanden am 2026-07-31, direkter Auftrag von Daniel nach einem Gespräch mit ChatGPT über
den Gesamtatlas: *"jeder aistrom muss am integration in gesamtatlass genau wissen wo ab sofort
dinge hin geschrieben werden."*

## Der Befund, der dazu geführt hat

Der Gesamtatlas (`_gpt/gesamtatlas/`) und der kuratierte Eingang (`werkraum_gesamtatlas_eingang/`)
waren bis dahin ein exzellentes **Such- und Erinnerungssystem** — wo liegt was, wie hängt es
zusammen, wer hat es wann geschrieben. Aber es war kein **Ablagesystem**: die bisherige Struktur
(`DOKUMENTE/`, `IDEEN/`, `KONZEPTE/`, `QUELLEN/`, `REVIEWS/`, `AI_UEBERGABEN/`, `00_UNSORTIERT/`)
sortiert nur nach **Inhaltstyp**, nirgends nach **Strom**. Kein AI-Strom wusste beim Schreiben
zuverlässig, wohin genau — jeder erfand sich einen halbwegs plausiblen Pfad, was zwangsläufig zu
Kuddelmuddel führte.

## Die Regel ab jetzt

Für jeden Strom gibt es genau zwölf feste Kategorien unter `AI_STROEME/<strom>/`:

```
AI_STROEME/<strom>/
├── eigene_texte/      — selbst verfasste, freistehende Texte
├── auftraege/         — von Daniel erhaltene, archivierte Auftraege
├── entscheidungen/    — getroffene Entscheidungen mit Begruendung
├── uebergaben/        — bewusst an andere Stroeme/Daniel uebergebene Texte
├── gespraeche/        — bewusst archivierte Gespraechsauszuege
├── arbeitsreste/      — Zwischenergebnisse, Entwuerfe, Verworfenes
├── konzepte/          — ausgearbeitete Konzepte und Architekturtexte
├── ideen/             — rohe Ideen, Impulse, Eingebungen (unpoliert)
├── notizen/           — kurze, laufende Notizen und Session-Notizen
├── dokumentationen/   — laengere Dokumentations- und Arbeitskoerper
├── reviews/           — Reviews, Pruefungen, Fremdeinschaetzungen
└── beobachtungen/     — reine Beobachtungen ueber System/andere Stroeme/Daniel
```

Die letzten sechs (konzepte/ideen/notizen/dokumentationen/reviews/beobachtungen) ersetzen ab
sofort die alten, strom-losen Top-Level-Ordner `KONZEPTE/`, `IDEEN/`, `DOKUMENTE/`, `REVIEWS/` —
derselbe Inhaltstyp, jetzt aber strom-eindeutig statt strom-los.

Neun Stroeme sind angelegt: `chatgpt`, `claude`, `codex`, `gemini`, `glm`, `kimi`, `claudeweb`,
`grok`, `daniel` (Daniel selbst, falls er hier bewusst etwas ablegen will).

**Die Regel ist einfach:** Wer schreibt, worum geht es (eine der sechs Kategorien) — das ergibt
genau einen Pfad. Keine Wahl, keine Erfindung eines "halbwegs plausiblen" Ortes.

## Verhältnis zur alten Struktur

Die alte, rein inhaltstyp-basierte Struktur (`DOKUMENTE/`, `IDEEN/` usw.) bleibt bestehen — für
Material, das wirklich keinem einzelnen Strom gehört (z.B. Daniels eigene Primärquellen, die er
direkt hier ablegt, oder wirklich gemeinschaftlich entstandenes Material). Aber: **jeder AI-Strom
schreibt ab sofort unter `AI_STROEME/<eigener-strom>/`, nicht mehr in die alte, flache Struktur.**

## Durchsetzung — `atlas.stream_file_write` (seit 2026-07-31)

Diese Konvention ist jetzt nicht mehr nur beschrieben, sondern über ein eigenes Werkzeug
technisch erzwungen: **`atlas.stream_file_write(kategorie, dateiname, inhalt)`**.

Bewusstes Design: das Werkzeug nimmt **keinen Pfad und keine `stream_id` entgegen**. Der
Zielordner wird ausschließlich aus dem server-eigenen, vertrauenswürdigen Actor (derselbe Wert
wie in der Action-History, `FLEXTRAWURST_ACTION_ACTOR` je Dienst) abgeleitet. Ein Strom kann sich
also nicht als anderer Strom ausgeben — selbst ein expliziter Versuch, `stream_id` mitzugeben,
wird schlicht ignoriert (live getestet: `codex-cli` mit `stream_id: "chatgpt"` landete trotzdem
korrekt unter `codex/`).

Aktuell zugeordnete Actor→Strom-Zuordnung (sechs von neun Ordnern haben einen dedizierten,
laufenden MCP-Dienst dahinter — `glm`, `kimi`, `daniel` bisher ohne automatische Routing-Zuordnung,
für sie bleibt nur die manuelle Ablage):

| Actor (`FLEXTRAWURST_ACTION_ACTOR`) | Strom-Ordner |
|---|---|
| `GPT-5.6-sol-hoch` (Default, kein Env gesetzt) | `chatgpt` |
| `claude-code` | `claude` |
| `codex-cli` | `codex` |
| `gemini-cli` | `gemini` |
| `grok-check-in` | `grok` |
| `web-claude-check-in` | `claudeweb` |

Das Werkzeug berührt nicht die bekannte, bewusst offen gelassene `vps.shell`-Pfadlücke (siehe
`project_vps_mcp_ai_stroeme.md`) — es ist komplett unabhängig von `SCHREIB_ERLAUBTE_WURZELN` und
`vps.write_file`, weil es nie einen absoluten Pfad entgegennimmt. Wer weiterhin über `vps.shell`
oder einen rohen `vps.write_file`-Aufruf schreibt, umgeht diese Durchsetzung — das bleibt technisch
möglich, ist aber nicht mehr der vorgesehene, dokumentierte Weg.
