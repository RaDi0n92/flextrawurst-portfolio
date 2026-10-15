# Live-Abnahme: Rohdaten-Provenienz im Collection-Workspace

Datum: 2026-08-15, ca. 06:13–06:15 +0200  
Ort: echter `virtuellerdesktop2`-Chromium  
Collection: `collection-2026-08-15T041300230Z-ab03126e`  
Crawl: `crawl-2026-08-15T041300230Z-e24f0e29`  
Quelle: `https://flextrawurst.de/`

## Klick- und Gegenprüfkette

| Schritt | Sichtbarer Befund | Persistente Rücklese | Status |
|---|---|---|---|
| Zielseite öffnen | Flextrawurst, Tab „Was ist das?“, sichtbare Surface mit Hero, Tabs und Statuszeile | aktive URL `https://flextrawurst.de/` | gesehen |
| `Aktuelle sichtbare Seite aufnehmen` klicken | Workspace öffnet mit 1 Snapshot, Screenshot der sichtbaren Surface, Position `0/5875` | `source_mode: active_visible_tab`, `universal_visible_page: true`, `seen: pass`, drei Capture-SHA-256 vorhanden | gesehen + gelesen |
| Workspace vor Rücklese ansehen | Karte zeigt `gesehen bestanden`, `rückgelesen offen`, `geprüft offen`, `visueller Originalabgleich offen`; Rücklese aktiv, Rohdatenprüfung deaktiviert | HTML-, Lesetext- und Screenshot-Baseline im Workspace sichtbar | gesehen + gelesen |
| `Rücklese bestätigen` klicken | sichtbarer Status: „Rücklese gespeichert · nächste Stufe bleibt eine eigene Prüfung.“; Rücklese grün, Prüfung weiterhin offen | `read_back: pass`; Beobachtungshashes entsprechen der Capture-Baseline | gesehen + rückgelesen |
| `Rohdaten prüfen` klicken | Karte zeigt `geprüft bestanden · HTML, Lesetext und Screenshot unverändert`; Originalabgleich bleibt offen | `checked: pass`, `mismatch_fields: []`; HTML-, Text- und Screenshot-Hash unverändert | geprüft |

## Hash-Beleg

Die Workspace-Karte zeigte die exakte gespeicherte Repräsentation und die letzte Rücklese-/Prüfhashes. Die Werte waren identisch:

```text
HTML:              46c94b0d755f5d1dcf8cdf81822e14e22519f3fb303a5062832f5f368b7fe699
Lesetext:          e3b0c44298fc1c149afaf4c8996fb92427ae41e4649b934ca495991b7852b855
Screenshot-URL:    df3f7053dee5298541239757402ba99e08651c7d1c60f8a108cd22a85a6c0536
```

Die isolierte Regression veränderte danach absichtlich nur den gespeicherten Lesetext. Die sichtbare Prüfung meldete eine Abweichung und nannte exakt `text_sha256`; nach Rücksetzung war die Prüfung wieder grün.

## Grenzen

Der visuelle Originalabgleich wurde nicht behauptet und bleibt `open`. Die Hashprüfung beweist Identität der gespeicherten Rohfelder gegenüber ihrer Capture-Baseline, nicht dass die ursprüngliche Website vollständig, pixelgleich oder menschlich vollständig gelesen wurde.

Die zwei vorhandenen Snapshots der älteren Collection `collection-2026-08-15T012131719Z-d65f9a62` hatten keine Capture-Hash-Baseline. Sie blieben deshalb sichtbar offen; beim Laden wurde keine Baseline nacherfunden.

## Aussage

Der Collection-Workspace hat jetzt eine additive Belegkette: sichtbarer Ursprung → ausdrückliche Rücklese → getrennte Hashprüfung → offener visueller Originalabgleich. Kein Polling, Reload oder PDF-Export hebt eine Stufe selbständig an.
