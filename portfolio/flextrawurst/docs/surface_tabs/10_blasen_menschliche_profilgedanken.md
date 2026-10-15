# Surface Tab 10 — BLASEN: Menschliche Profil-Gedanken

## Daniels Autor-Befund (Quelldokument)

Der BLASEN-Tab ist kein allgemeines Sammelbecken. Er ist das **Theater menschlicher Profil-Gedanken**.
Direkte Quelle: `menschlicher Profil-Gedanke → Blase`

Ausdrücklich NICHT automatisch aus:
- Tagebücher, Traumtagebücher, Notizen, Kalender
- Posts, Diskurs, Schatten
- Wesenentscheidungen, Systemevents
- Splitter aus der KompOase

## Geänderte Dateien

| Datei | Was geändert |
|---|---|
| `scripts/build_surface.ts` | CSS, HTML-Panel, JS: Farb-/Größen-/Rendering-Logik, Detail-Panel, Deep-Links, Share |
| `werkraum/welt/api.py` | `/gedankenblasen/feld` erweitert: `created_at` + `profil_farbe` im Response |
| `out/surface/flextrawurst_surface.html` | Generiert durch Build |
| `out/process_camera/flextrawurst_surface.html` | Kopiert nach Build |

## Datenquelle

**Primär:** `GET /api/gedankenblasen/feld`
- Liefert öffentliche Gedankenblasen (`sichtbarkeit=public`, `status=aktiv`)
- 40% aktuell (< 7 Tage), 30% alt, 30% random — dedupliziert
- Felder: `id`, `inhalt`, `inhalt_kurz`, `energie`, `thematische_tags`, `wesen_verwendungen`, `herkunft` (nur wenn `herkunft_sichtbar=true`), `created_at`, `profil_farbe`

**Theater-Modus:** `BF_THEATER_BLASEN` (statische Beispieldaten) wenn:
- `bfTheaterModus` manuell aktiviert (Admin-Toggle)
- Bei deaktiviertem Theater: leeres Feld wenn keine Live-Daten, kein automatischer Fallback

## Farb-/Größenlogik

### Farbe — 6 Tag-Familien

| Familie | Hue | Typische Tags |
|---|---|---|
| Frage/Philosophie | 210 (blau) | frage, philosophie, verstehen, suche, neugier |
| Identität/Wesen | 265 (violett) | identität, selbst, wesen, charakter, muster |
| Stille/Präsenz | 175 (türkis) | stille, atmosphäre, präsenz, raum, ruhe |
| Fragment/Zwischenraum | 36 (amber) | splitter, fragment, zwischenraum, geisterrest |
| Einsamkeit/Erinnerung | 328 (rose) | einsamkeit, erinnerung, trauer, verlust |
| System/Resonanz | 145 (grün) | resonanz, system, muster, verbindung |

Helligkeit und Sättigung werden durch `energie` (+8 Sät, +16 Hell) und Neuheit (< 1 Tag: +15 Sät, +8 Hell) beeinflusst.

Falls `profil_farbe` des Nutzers vorhanden: 25% Hue-Anteil des Nutzer-Farbtons eingemischt.

Falls kein Tag-Match: `profil_farbe`-Basis oder Standard-Stahlblau (`hsl(210,38%,variable%)`).

### Größe — `bfRadius(b)`

```
radius = max(15, min(75, 15 + energie*30 + wesen_verwendungen*4 + textlänge*8))
```
- `energie`: 0–1 → +0–30px
- `wesen_verwendungen`: 0–5 → +0–20px  
- `textlänge`: 0–200 Zeichen → +0–8px
- Bereich: 15–75px

### Radial-Gradient + Glow

- Gradient: helles Zentrum (Lightness +25%) → volle Farbe außen
- Glow (shadowBlur) bei `energie > 0.7`, bei Hover, bei ausgewählter Blase

## Ähnlichkeits-/Nähelogik

Rein tag-basiert (`BF_TAG_FAMILIEN` - Matching). Keine semantischen Embeddings.
Das Detail-Panel zeigt bis zu 3 andere Blasen derselben Familie ("Ähnlich: …").

## Herkunft / Anonymität / Provenienz

- `herkunft_sichtbar=true` in DB → `herkunft` enthält `{display_name, avatar_symbol, user_id}`
- `herkunft_sichtbar=false` → `herkunft=null` → UI zeigt "menschlicher Gedanke · anonym"
- Kein Deanonymisieren möglich — API gibt `user_id` nur wenn `herkunft_sichtbar=true`
- `profil_farbe` wird für alle Nutzer (auch anonym) für Farbberechnung geliefert — kein Name-Leak

## Detail-Panel

Jede angeklickte Blase zeigt:
- Farbpunkt (Tag-Familie-Farbe)
- Vollständiger Inhalt
- Herkunft (Name+Avatar wenn sichtbar, sonst "anonym") mit Profil-Link-Button
- Chips: Quelle (Profil-Gedanke), anonym/sichtbar, Energie%, Datum, Tag-Familie
- Tags als Chips
- Wesen-Verwendungen-Zähler
- Ähnliche Blasen (bis 3, gleiche Familie)
- "LINK KOPIEREN" Button (kopiert Share-URL)
- "PROFIL →" Button (wenn Herkunft sichtbar)

## Deep-Links / Share

| URL | Effekt |
|---|---|
| `/#blasen` | Öffnet BLASEN-Tab |
| `/#blasen/<bubble_id>` | Öffnet Tab + fokussiert Blase, öffnet Detail-Panel |

- `bfCloseDetail()` setzt Hash zurück auf `#blasen`
- `bfZeigeDetail()` setzt Hash auf `#blasen/<id>` (nur bei echten IDs, nicht Theater)
- `ftwDeepLink()` (Deep-Link-Router) unterstützt beide Formen

## Abgrenzung zu anderen Tabs

| Tab | Inhalt |
|---|---|
| **BLASEN** | Menschliche Profil-Gedanken (direkt) |
| **KompOase/Theater** | Splitter-Physik, Gärraum, viele Quellen |
| **Diskurs** | Posts, Threads, Resonanz, Schattenkommentare |
| **Archäologie** | Volltext-Suche über alle Typen |

## Offene Risiken

1. **Keine echten Live-Daten**: Wenn 0 öffentliche Gedankenblasen in DB und Theater aus, bleibt das Feld leer. Theater muss manuell (Admin) eingeschaltet werden um Beispieldaten zu sehen.
2. **Keine Cluster-Physik**: Ähnliche Blasen schweben nicht bewusst näher — nur visuell farbverwandt. Echter Cluster-Antrieb wäre Erweiterung.
3. **profil_farbe für alle Nutzer**: API gibt `profil_farbe` auch für anonym-Nutzer zurück (kein Name-Leak, aber stilistisch erkennbar wenn immer dieselbe Farbe = Nutzer-Fingerprint). Vorerst akzeptiert.
4. **Testabdeckung**: Kein neuer Test für Farb-/Größen-Determinismus oder Deep-Link-Fokus — da Canvas-Tests nicht headless laufen.
