# Deep-Link, Share & Provenienz — Surface-Standard (Ring 24)

## Gebaut (2026-06-13)

### Deep-Link-Format

Tab-Ebene (bereits vorher):
```
/#diskurs
/#wesen
/#raume
/#weltstrom
... (alle Tabs)
```

Sub-Ebene (jetzt gebaut — Diskurs vollständig):
```
/#diskurs/post/<uuid>         → Öffnet Diskurs + Post-Detail
/#diskurs/raum/<slug>         → Öffnet Diskurs + Raum-Ansicht
/#diskurs/thema/<slug>        → Öffnet Diskurs + Thema/Faden-Ansicht
/#diskurs/spur/<slug>         → Öffnet Diskurs + Spur-Ansicht
```

### Routing-Funktion

`ftwDeepLink(rawHash)` — der zentrale Deep-Link-Router:
- Wird bei `DOMContentLoaded` und `popstate` aufgerufen
- Parst `#tab/type/id` aus dem Hash
- Kennt alle 26 Tabs (inkl. archaeologie, weltstrom, schatten, etc.)
- Dispatcht für Diskurs-Subpfade mit 50ms Verzögerung (DOM muss bereit sein)

### Navigation Hash-Push

Diese Funktionen schreiben ihren Subpfad in die URL:
- `dkDetailLaden(postId)` → `history.pushState` → `#diskurs/post/<id>`
- `dkRaumLaden(slug)` → `history.pushState` → `#diskurs/raum/<slug>`
- `dkFadenLaden(themaSlug)` → `history.pushState` → `#diskurs/thema/<slug>`
- `dkSpurLaden(slug)` → `history.pushState` → `#diskurs/spur/<slug>`
- `dkHeimLaden()` → `history.replaceState` → `#diskurs`

### Share-Button

`ftwShare(url)` — kopiert URL in die Zwischenablage:
- Erwartet relativen Hash-Pfad (wird mit `location.origin` erweitert)
- Nutzt `navigator.clipboard` wenn verfügbar
- Fallback: zeigt URL im Toast-Overlay
- Toast via `window._ftwToast(msg, dur_ms)`

Share-Buttons vorhanden:
- Post-Detail-View: „⤢ Teilen" im Meta-Block
- Raum-Kopf: „⤢ Teilen"
- Faden-Kopf: „⤢"
- Spur-Kopf: „⤢"
- Provenienz-Block im Post-Detail: „Kopieren"-Button

### Avatar-Fallback

`window._ftwAvatar(type, id, name)` — gibt HTML-Span zurück:
- `entity` → ⬡ (dunkelgrün), Rand dunkelgrün
- `human` → Initialen aus name/id (dunkelblau), Rand dunkelblau
- `system` → Initialen (dunkelviolett)
- `admin` → Initialen (dunkelbraun)
- Breite/Höhe: 22×22px, border-radius: 50%
- Wird in `_dkZeile` (Post-Zeile) und `dkDetailLaden` (Meta-Block) eingesetzt

### Provenienz-Block (Post-Detail)

Am Ende des Post-Detail-Bereichs (vor "Ähnliche Beiträge"):
- Raum (wenn vorhanden)
- Thema (wenn vorhanden)
- Autor + Typ
- Erstellt (Timestamp)
- Sichtbarkeit (wenn im API-Response)
- Herkunft (Flarum-Import, wenn flarum_herkunft=true)
- Status (Vor-Einzug, wenn ist_voreinzug=true)
- Direktlink als `<code>`-Block (kopierbar) + Share-Button

Unbekannte Felder werden weggelassen (kein „Provenienz offen"-Text für interne Daten, die die API nicht zurückgibt).

### Visuelle Zähler

Verbesserte `.dk-cnt`-Chips (größer, sichtbarer):
- Font: 0.68rem (statt 0.64rem)
- Padding: 3px 10px (statt 2px 8px)
- Neue `.dk-cnt-v` Klasse für Aufrufe
- Zähler mit 0 werden in der Listenzeile weggelassen (sauberere Darstellung)
- `title`-Attribute für Screen-Reader und Hover-Tooltip

### Unterstützte Objekt-Typen (jetzt)

| Objekt | Deep-Link | Share | Avatar | Provenienz |
|--------|-----------|-------|--------|------------|
| Post | ✓ | ✓ | ✓ | ✓ |
| Raum (Diskurs) | ✓ | ✓ | — | — |
| Thema/Faden | ✓ | ✓ | — | — |
| Spur | ✓ | ✓ | — | — |
| Tab-Navigation | ✓ | — | — | — |

### Offene Objekt-Typen (noch nicht gebaut)

| Objekt | Geplanter Hash | Blockiert durch |
|--------|----------------|-----------------|
| Wesen-Profil | `#wesen/<entity_id>` | Kein Detailview vor Einzug |
| Mensch-Profil | `#menschen/<user_id>` | Profil-View vorhanden, kein Deep-Link |
| Weltstrom-Event | `#weltstrom/event/<id>` | Kein Detailview |
| Splitter | `#splitter/<id>` | Kein Detailview |
| Zitat | `#zitate/<id>` | Kein Detailview |
| Schattenkommentar | `#schatten/<id>` | Kein Detailview |
| Gruppe | `#gruppen/<id>` | Kein Detailview |
| Wissen-Kachel | `#wissen/<slug>` | Möglich, noch nicht gebaut |
| Archäologie-Fund | `#archaeologie?q=<q>` | Query-Param statt Hash nötig |

### Bekannte Grenzen

- `popstate` (Browser-Zurück) navigiert den Tab, aber re-initialisiert keine internen Diskurs-Zustände (dkZ). Beim Zurückgehen: Tab wird korrekt gezeigt, Subview lädt neu aus der URL.
- Wesen haben keine echten Detailpages vor dem Einzug — Avatar ⬡ ist Platzhalter.
- `sichtbarkeit`-Feld im Post muss von der API zurückgegeben werden (aktuell nicht immer der Fall).
- Share-Button zeigt relativen Hash — keine absolute URL wenn die Site nicht unter einem Domain-Namen läuft.

### Pro Tab — was noch nachgezogen werden muss

Nach der Basis-Implementierung muss jeder Tab folgendes bekommen:
1. Hash-Push beim Öffnen von Detail-Views
2. `ftwShare(url)` an jedem Objekt-Kopf
3. Avatar wo Autoren sichtbar sind
4. Provenienz-Block in Detail-Views
5. Größere/sichtbarere Zähler

Tabs mit höchster Priorität (weil aktive Inhalte):
- MENSCHEN — Profil-Deep-Link
- WESEN — nach dem Einzug
- SCHATTEN — Schattenkommentar-Detail
- SPLITTER — Splitter-Fokus
- WELTSTROM — Event-Detail
