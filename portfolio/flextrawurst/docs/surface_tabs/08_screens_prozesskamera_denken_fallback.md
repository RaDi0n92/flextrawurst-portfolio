# Tab 08 — SCREENS: Prozesskamera & DENKEN als Fallback

## Geänderte Dateien

- `flextrawurst/scripts/build_surface.ts` — SCREENS JS-Block, `generateScreensView()`, i18n DE+EN, `ftwDeepLink()`
- `flextrawurst/tests/surface_ring_23.test.ts` — 16 neue Tests für SCREENS-Tab
- `flextrawurst/out/surface/flextrawurst_surface.html` — Build-Output
- `flextrawurst/out/process_camera/flextrawurst_surface.html` — Process-Camera-Output

## Daniels Autor-Befund (Grundlage)

SCREENS soll die Browser-Agent-Existenz der Wesen sichtbar machen:
Screenshot → Wahrnehmung → Denkstream → Auswertung → Entscheidung → Handlung → nächster Screenshot.

Der Fokus-/Vollbildmodus war zu klein. Screen und Denkstream müssen gleichzeitig sichtbar bleiben.
DENKEN bleibt als separater, leichterer Fallback-Tab bestehen.

## Bezug auf globalen Surface-Standard

- Deep-Links: `#screens/<entity_id>` öffnet Tab und Fokusmodus
- Share-Buttons: pro Karte + im Modal
- Provenienz: sichtbar in Topbar und Modal
- Avatar/Glyph: ⬡ Tag-ID pro Wesen
- Status-Badges: wach / träumt / aus (Erweiterung vorbereitet)
- i18n: alle Texte zweisprachig (DE/EN), 393 Keys — DE ✓ EN ✓

## Warum DENKEN separat bleibt

Wenn Screenshot-Prozesskamera (jedes Wesen alle 2–3s) den Server belastet oder noch nicht stabil läuft,
braucht flextrawurst einen leichten, textbasierten Denk-Ort als Reserve.
DENKEN ist dieser Fallback — nicht entfernt, nicht versteckt, nicht hart zusammengelegt.
Beide Tabs verlinken aufeinander.

## SCREENS vs DENKEN — Unterschied

| | SCREENS | DENKEN |
|---|---|---|
| Inhalt | Screenshot + Denkstream zu diesem Moment | Browser-Agent-Textausgabe (kein Bild) |
| Quelle | entity_thinking_log (source=browser_agent) + Screenshot-Bild | entity_thinking_log (source=browser_agent) |
| Fokusmodus | Ja — Bild 68% + Stream 32% | Nein |
| Zweck | Prozesskamera — sehen was das Wesen sieht | Textmodus, leichter Fallback |
| Status | wartet auf Aktivität wenn kein Agent | wartet auf Aktivität wenn kein Agent |
| Fallback | DENKEN-Link im Topbar + Modal | SCREENS-Link in Provenienz |

## Screenshot-/Denkstream-Quellen

- Screenshots: GET `/api/denkstream/screenshot/<entity_id>` — existiert, liefert 404 wenn kein Bild
- Denkstream last: GET `/api/denkstream/<entity_id>/last?limit=8`
- Denkstream SSE: GET `/api/denkstream/<entity_id>` (EventSource)
- Status aller Wesen: GET `/api/denkstream/status/all`
- Globaler Stream: GET `/api/denkstream/all/stream` (EventSource)

**Aktuell keine Browser-Agent-Live-Daten** — alle Slots zeigen `WARTET AUF AKTIVITÄT`.
Sobald ein Agent aktiv ist und Screenshots/Chunks schreibt, erscheinen sie automatisch.

## Fokusmodus — Aufbau

```
[scv-modal — 95vw × 92vh]
  [Header: ⬡ Tag | Badge | URL | ⬡ link | → DENKEN | ✕ ESC]
  [Body: flex-row]
    [scv-modal-img-wrap — 68%]
      img (object-fit: contain, top)
      scv-m-img-empty (wenn kein Screenshot)
    [scv-modal-stream — 32%, min 220px]
      Header: DENKSTREAM ● source=browser_agent
      Motto: "Ich wähle meinen Input selbst!"
      Provenienz: Quelle · Zeitstempel
      Items: Chunks/Gedanken (scrollbar)
      Leerstate: "Kein Browser-Agent-Denkstrom für dieses Wesen."
```

Mobile (≤700px): Bild oben (52%), Stream unten (48%), flex-column.

## Denkstream im Fokus

- Beim Öffnen: letzte 8 Einträge via `/api/denkstream/<id>/last` geladen
- Live: SSE `/api/denkstream/<id>` nur für dieses Wesen
- Leerstate `scv-m-empty` wird ausgeblendet sobald erster Chunk kommt
- Leerstate zeigt: "Kein Browser-Agent-Denkstrom für dieses Wesen."
- Stream ist immer sichtbar — verschwindet nicht im Fokusmodus

## Performance-Schutzmaßnahmen

- `visibilitychange`-Listener: Refresh-Timer pausiert wenn Browser-Tab versteckt
- Refresh nur wenn SCREENS-View sichtbar (`view-screens.style.display !== 'none'`)
- Bildrefresh alle 3s nur für sichtbare Slots (gleicher Intervall wie vorher)
- Modal-Bild wird per lazy-load via `new Image()` getauscht (kein Flicker)
- SSE-Verbindungen werden beim `beforeunload` geschlossen
- Kein aggressives Polling — defensiver Aufbau, wartet auf echte Daten

## Deep-Link- und Share-Formate

| Format | Verhalten |
|---|---|
| `#screens` | SCREENS-Tab öffnen |
| `#screens/namelessAI_1234` | SCREENS öffnen + Fokusmodus für dieses Wesen |
| Share-Button Karte | Kopiert `<origin>#screens/namelessAI_XXXX` |
| Share-Button Modal | Kopiert `<origin>#screens/namelessAI_XXXX` |

Hinweis: Screenshot-IDs existieren noch nicht als echte DB-IDs.
Share verlinkt auf Entity-Fokus, nicht auf einzelnen Screenshot.

## Provenienzfelder im Modal

- Wesen-ID (⬡ Tag)
- Status-Badge (wach / träumt / aus)
- URL (aktuelle Seite des Agenten)
- Quelle: `entity_thinking_log · source=browser_agent`
- Zeitpunkt: reserviertes Feld `scv-m-zeit` (noch nicht befüllt — kein Live-Agent)

## Offene Risiken

1. **Kein Browser-Agent aktiv** — alle Slots zeigen Leerstate. Warten auf echten Agent.
2. **Screenshot-IDs** — noch keine echten DB-IDs; Share verlinkt auf Entity-Ebene.
3. **Zeitstempel im Modal** (`scv-m-zeit`) — noch nicht befüllt; wird aktiv wenn API Timestamp liefert.
4. **Serverlast bei vielen Wesen** — 6 × 3s-Bildrefresh ist überschaubar; bei Skalierung auf 20+ Wesen Lastschutz überdenken.
5. **Mobil** — Touch-Bedienung funktioniert, getestet per CSS-Media-Query. Echter Mobiltest noch ausstehend.

## Was Daniel als nächstes prüfen sollte

1. SCREENS im Browser aufrufen — sieht der Fokusmodus (95vw × 92vh) gut aus?
2. Sind Bild (68%) und Denkstream (32%) im richtigen Verhältnis?
3. ESC-Taste schließt den Modal korrekt?
4. Share-Button kopiert den richtigen Link?
5. `#screens/namelessAI_1234` in der URL-Leiste tippen — öffnet Fokusmodus?
6. Link "→ DENKEN" in Topbar und Modal führt zu DENKEN-Tab?
7. DENKEN-Tab noch vorhanden und separat? (Tab-Button in View-Bar)
