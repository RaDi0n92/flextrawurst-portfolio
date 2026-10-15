# DENKEN-Tab — Zuständigkeit & UI-Wahrheit
**Analysiert und geändert: 2026-06-13**

## Geänderte Dateien
- `scripts/build_surface.ts` — generateDenkenView(), ftwDeepLink(), WESEN live.thought, i18n
- `tests/surface_ring_23.test.ts` — 9 neue Tests (50 gesamt)
- `docs/surface_tabs/07_denken_zustaendigkeit.md` — diese Datei

## Daniels Autor-Befund (Zusammenfassung)
- DENKEN und SCREENS entstanden gleichzeitig → Dopplungsverdacht
- WESEN-Tab hat Denkstrom-Bereich → Abgrenzung unklar
- Entscheidung ≠ Gedanke — nie gleichsetzen
- Öffentliche Gedanken ohne Quelle nicht behaupten
- Zuständigkeit klären bevor Weiterbau

## Bezug auf globalen Surface-Standard
- Deep-Links: `#denken/<entity_id>` jetzt implementiert → dkstFilter()
- Share-Buttons: NICHT gebaut — kein Denkobjekt (nur Agent-Chunks), kein sinnvoller Share-Link
- Provenienz: alle drei Abschnitte (Was es ist, Warum leer, Was es NICHT ist) mit wd-prov-Boxen
- Avatar: nicht relevant (kein Wesenprofil, sondern Multi-Wesen-Feed)

## Denkorte-Karte

### DENKEN-Tab (view-denken)
**Was er ist:** Browser-Agent-Textstream. Zeigt Gedankenchunks, URL und Entscheidung wenn ein Browser-Agent aktiv ist.

**Datenquelle:**
- Primär: SSE über PostgreSQL LISTEN Channel (`/api/denkstream/all/stream` oder `/{entity_id}`)
- Sekundär: `/api/denkstream/all/last` → `entity_thinking_log WHERE meta->>'source' = 'browser_agent'`
- Write-Endpunkt: POST `/api/denkstream/chunk` — wird von Browser-Agent aufgerufen

**Warum leer:** Kein Browser-Agent läuft. Die Tabelle `entity_thinking_log` hat 16k+ Einträge, aber KEINER davon hat `source=browser_agent` gesetzt — alle stammen aus entity_kern-Ticks.

**Wichtig:** DENKEN ist KEIN allgemeiner Wesen-Denkstrom. Es ist ein Browser-Agent-Beobachtungsfenster.

### SCREENS-Tab (view-screens)
**Was er ist:** Screenshot-Grid (3×2) + Modal mit Denkstream-Text. Die Bild-Hälfte desselben Browser-Agent-Systems.

**Datenquelle:** `/api/denkstream/screenshot/{entity_id}` → `/tmp/wesen_screenshots/{entity_id}_aktuell.jpg`

**Beziehung zu DENKEN:**
- DENKEN = Text-Ansicht des Browser-Agent-Outputs
- SCREENS = Bild-Ansicht + Text im Modal
- Beide leer gleichzeitig (kein Agent = beide stumm)
- NICHT redundant: komplementär

**Empfehlung:** Trennung beibehalten. DENKEN = Textleser, SCREENS = Bildbeobachter. Sinnvoll wenn Browser-Agent läuft.

### WESEN-Tab (Denk-Bereich)
**"Letzter Gedanke" (`wesen.last.thought`):**
- Quelle: `entity_thinking_log.gedanke` (entity_kern-Ticks ohne browser_agent-Filter)
- Das ist echter LLM-generierter Gedankentext des Wesens
- Leer weil entity_takt gestoppt

**"entity_kern-Ausgabe (live)" (`wesen.live.thought`, vorher: "Denkstrom (live)"):**
- Quelle: `/api/entities/{id}/denkstrom` → `denkstrom_buffer` aus entity_thinking_log
- NICHT Browser-Agent-Output
- Jetzt mit Provenienz-Note + Link zum DENKEN-Tab

### EINSICHT-Tab
- Subtab DENKFENSTER: Status SPAETER (noch nicht implementiert)
- Enthält entity_thinking_log in anderen Kontexten (Analyse, Admin)
- Keine Überschneidung mit DENKEN-Tab

## Begriffstrennung (wie im Code jetzt umgesetzt)

| Begriff | Was es ist | Wo im UI |
|---------|-----------|----------|
| **Gedanke** | LLM-generierter Denktext eines Wesens (entity_kern) | WESEN: "Letzter Gedanke" |
| **Entscheidung** | Gewählte Aktion eines Wesens | WESEN: "Letzte Entscheidung" |
| **entity_kern-Ausgabe** | Denkstrom-Buffer während eines Ticks | WESEN: "entity_kern-Ausgabe (live)" |
| **Browser-Agent-Denkstrom** | Chunks eines aktiven Browser-Agenten + URL | DENKEN-Tab |
| **Screenshot-Stream** | Bildaufnahmen des Browser-Agenten | SCREENS-Tab |
| **Denkfenster** | Geplantes Analyse-Feature | EINSICHT: DENKFENSTER (SPAETER) |

## Was konkret geändert wurde

### DENKEN-Tab generateDenkenView()
1. Hero-Text: "Der Denkstrom der Wesen in Echtzeit. Öffentlich für alle." → ENTFERNT
2. Title i18n: "Denken — live" → "Browser-Agent-Denkstrom"
3. Provenienz-Box mit 3 Abschnitten: Was es ist / Warum leer / Was es NICHT ist
4. Link → SCREENS im Provenienz-Abschnitt
5. Card-Leertext: "wartet auf ersten Gedanken…" → "kein Browser-Agent aktiv"
6. Log-Leer-Div: "#dkst-log-leer" — wird ausgeblendet wenn Logs vorhanden

### ftwDeepLink()
- `#denken/<entity_id>` → switchView('denken') + dkstFilter(entity_id, btn) mit 200ms Delay

### WESEN-Tab
- `wesen.live.thought` i18n: "Denkstrom (live)" → "entity_kern-Ausgabe (live)"
- Neue Provenienz-Note darunter: Quelle + Abgrenzung + Link zu DENKEN

## Entscheidung: Zuständigkeit von DENKEN

**→ Option E (sichtbare Wartefläche) mit korrigierter Beschriftung**

Begründung:
- Eigene Datenquelle existiert (denkstream_api.py, entity_thinking_log source=browser_agent, SSE-Infrastruktur)
- SCREENS-Tab überschneidet sich NICHT vollständig (SCREENS = Bild, DENKEN = Text)
- Zusammenlegen wäre Informationsverlust
- Browser-Agent-Konzept ist klar vorbereitet, nur noch kein Agent läuft
- Leere ist ehrlich und technisch begründet (kein Agent aktiv)
- Der Tab zeigt jetzt präzise was er ist und was er braucht

Was VORHER falsch war:
- "Der Denkstrom der Wesen in Echtzeit. Öffentlich für alle." → falsch, es ist Browser-Agent-Output, kein allgemeiner Denkstrom
- "Ich wähle meinen Input selbst!" als Motto der Leere → poetische Nebelwand
- "wartet auf ersten Gedanken…" → unspezifisch, klingt wie entity_kern-Warten

## Deep-Link-Stand
| Format | Wirkung |
|--------|---------|
| `#denken` | Öffnet DENKEN-Tab |
| `#denken/namelessAI_1234` | Öffnet Tab + setzt Filter auf dieses Wesen |

Share: Nicht implementiert — kein persistentes Denkobjekt.

## Offene Risiken
- DENKEN-Tab SSE-Reconnect bei `es.onerror` versucht nach 5s erneut — wenn Server down, Dauerschleife möglich. Kein Problem bei normaler Nutzung.
- `#denken/<entity_id>` Deep-Link: `dkstFilter` muss im Scope sein (window-Ref). Funktioniert nur wenn DENKEN-Tab mindestens einmal initialisiert wurde.
- Browser-Agent-System hat `/denkstream.html` (externes Vollbild) und `/screens.html` — diese Seiten existieren außerhalb der Surface. Konsistenz nicht geprüft.
- Wenn Browser-Agent in Zukunft gebaut wird: DENKEN-Tab sofort funktional ohne weitere UI-Arbeit. Nur Agent starten.

## Daniels Entscheidungen (2026-06-13)

**a) DENKEN verstecken bis Browser-Agent?** → Nein. Tab bleibt sichtbar.

**b) Gemeinsamer Status-Hinweis DENKEN+SCREENS?** → Nein. Überflüssig.

**c) EINSICHT-DENKFENSTER (SPAETER): Was zeigt es?**
→ Beides: entity_kern-Output UND Browser-Agent-Output — aber mit Provenienz pro Eintrag.
Jeder Eintrag muss seinen Typ tragen: `entity_kern | browser_agent | (weitere Quellen wenn nötig)`.
Keine stumme Vermischung.
