# Surface Tab 11 — MENSCHEN: Profile, Sichtbarkeit, Splitter

## Daniels Autor-Befund

Der MENSCHEN-Tab soll keine langweilige Accountliste sein, sondern strukturierte Menschenprofile:
echte Menschen statt Systemdienste, pro Beitrag explizite Veröffentlichung,
je Kategorie nur letzter Beitrag sichtbar und Rest aufklappbar, aufgenommene Splitter als Sammlung.

## Geänderte Dateien

| Datei | Was geändert |
|---|---|
| `scripts/build_surface.ts` | CSS neu (website-feel), `loadMenschenListe()` verbessert, `selectMensch()` komplett restrukturiert, Deep-Link-Router ergänzt, neue Hilfsfunktionen |
| `werkraum/welt/api.py` | `/menschen` filtert Systemkonten via Username-Liste, `include_system=true` für Admin |
| `out/surface/flextrawurst_surface.html` | Generiert durch Build |
| `out/process_camera/flextrawurst_surface.html` | Kopiert nach Build |

## Systemkonten-Befund

Alle 8 Accounts in der DB haben `role = 'admin'` — Rollen-Filter allein reicht nicht.

| Username | Typ | Status |
|---|---|---|
| daniel | Echter Mensch (Betreiber) | sichtbar |
| HakunaMatata | Echter Mensch (oder Test) | sichtbar |
| klappspaten | Unbekannt (kein System-Zeichen) | sichtbar |
| 1337 | Test/Alt-Account | sichtbar |
| System | Systemkonto | **gefiltert** |
| Admin | Systemkonto | **gefiltert** |
| entity_takt | Daemon-Konto (Entity-Takt System) | **gefiltert** |
| flextrawurst | Plattform-Konto | **gefiltert** |

**entity_takt / Entity-Takt System:** Ist der Daemon, der `entity_kern.py` antreibt —
automatisierter Takt-Service für Wesen-Aktivität. Kein echter Mensch.

**Filter-Mechanismus:** `SYSTEM_USERNAMES` Tuple in `api.py`, per SQL `NOT IN`.
Admin kann alle sehen mit `?include_system=true`. Keine DB-Schema-Änderung nötig.
Langfristig: `meta->>'is_system'` in `human_users` per `UPDATE` — sauberer.

## Profilstruktur (neu)

Jedes Profil besteht jetzt aus:

1. **Header** — Cover-Gradient (Profil-Hintergrundfarbe), Avatar (72px, klickbar für Lightbox),
   Name, Handle, Motto, Tags, Profil-Farbe, Joined-Datum
2. **Action-Buttons** — `⬡ Link` (Share/Deep-Link), `Bearbeiten` (nur eigenes Profil),
   `Supporter`, `Nachricht` (für andere Profile wenn eingeloggt)
3. **Welt-Spuren** — Activity-Tiles: Tagebuch, Notizen, Träume, Kalender, Gedanken (Counts)
   mit Privat-Hinweis: "Inhalte werden nur auf Wunsch veröffentlicht"
4. **Öffentliche Gedanken** — letzter Gedanke sichtbar, Rest aufklappbar (Toggle-Button)
5. **Splitter — Destillat** — 3 neueste Splitter, Rest aufklappbar, Typ-Badge, Provenienz
6. **Gedankenwelt** — wenn vorhanden und öffentlich
7. **Aufgenommene Splitter** — Platzhalter mit Hinweis (Protokoll in Vorbereitung)

## Per-item Sichtbarkeit

**Ist-Zustand in der DB:**

| Tabelle | Visibility-Feld | Situation |
|---|---|---|
| `gedankenblasen` | `sichtbarkeit` (public/private/…) | vorhanden, wird genutzt |
| `mw_tagebuch` | `zitierbar` bool (nur für Wesen) | kein public/private Feld |
| `mw_notizen` | `zitierbar` bool | kein public/private Feld |
| `mw_traumtagebuch` | `zitierbar` bool | kein public/private Feld |
| `mw_kalender` | — | kein Sichtbarkeitsfeld |

Konsequenz: Tagebuch/Notizen/Kalender/Traumtagebuch zeigen nur **Counts**, keinen Inhalt.
Inhalt bleibt privat bis ein eigenes `sichtbarkeit`-Feld pro Tabelle hinzukommt.
Das ist der sichere Stand und verhindert ungewollte Veröffentlichungen.

Gedankenblasen werden mit `sichtbarkeit = 'public'` gefiltert — korrekte per-item Freigabe.
Splitter sind Destillat-Artefakte die vom System aus publizierbaren Quellen erzeugt werden.

## Aufklappbares Archiv

Für Gedankenblasen: erste Blase sichtbar, Rest in `#mp-g-rest-<id>` versteckt.
Für Splitter: erste 3 sichtbar, Rest in `#mp-spl-rest-<id>` versteckt.
Toggle via `mpToggleExpand(btn)` — liest `data-target`, `data-mehr`, `data-weniger`.

## Aufgenommene Splitter

Status: **in Vorbereitung** — kein `splitter_aufnahmen`-Protokoll in der DB.
Die `splitter`-Tabelle hat `aufnahmen` (Zähler wie oft aufgenommen), aber keine
per-User-Zuordnung wer was aufgenommen hat.

Zeigt aktuell: Hinweis + Anleitung (KompOase öffnen → Splitter anklicken → aufnehmen).
i18n-Keys `komp.aufgenommene.titel` / `komp.aufgenommene.wartet` bleiben erhalten (Test).

## Gedankenblasen-Aufnahme durch Menschen / Wesen

Status: **nicht implementiert** — weder für Menschen noch für Wesen.
Gedankenblasen haben keine `user_collections`-Tabelle.
Vorbereitung: `user_blasen_sammlung(user_id, blase_id, aufgenommen_at)` als nächster Schritt.

## Deep-Links und Share

| URL | Effekt |
|---|---|
| `/#menschen` | Öffnet MENSCHEN-Tab, erstes Profil |
| `/#menschen/<user_id>` | Öffnet Tab, wählt Profil direkt aus |

- `history.replaceState()` aktualisiert URL beim Profilwechsel
- `mpShareLink(id)` kopiert URL in Zwischenablage, Button zeigt "✓ Link kopiert" für 2s
- Deep-Link-Router in `ftwDeepLink()` behandelt `#menschen/<id>` korrekt

## Profilidentität

- Avatar mit Profil-Farbe als Rand
- Symbol-Avatar nutzt Profil-Farbe (kein einheitliches Grau mehr)
- Sidebar-Listeneinträge mit Profil-Farbe für Name + Avatar-Rand
- Cover-Gradient aus Profil-Hintergrundfarbe

## Privat-Kollision (Arbeitsschritt 12)

**Menschliche Spuren als Weltmaterial (aus `ÜBER`-Tab):**
"No opt-in required. Beings can quote everything humans write in flextrawurst"

**Aktueller Datenschutz-Stand:**
- `menschenprofil_lesen()` ist implementiert — Wesen können Profil lesen
- Gedankenblasen: nur `public` Blasen (opt-in via `sichtbarkeit`-Feld)
- Tagebuch/Notizen/Kalender: nur Counts sichtbar, kein Inhalt
- Wesen zitieren nur was tatsächlich öffentlich (public) markiert ist

Die Aussage "No opt-in required" bezieht sich auf das Prinzip, nicht auf private Inhalte.
Private Inhalte bleiben privat. Diese Kollision ist akzeptiert und dokumentiert —
Daniels Entscheidung ob und wie das ÜBER-Tab weiter präzisiert werden soll.

## Offene Risiken

1. **Systemkonten-Liste hardcoded**: `SYSTEM_USERNAMES` in `api.py` muss manuell gepflegt werden
   → Lösung: `meta->>'is_system'` per DB-UPDATE (braucht explizites Daniel-OK für SQL-Schreibzugriff)
2. **`klappspaten` / `1337`**: Unklarer Status — wenn System-Account, manuell markieren
3. **Keine per-item Sichtbarkeit für mw_* Inhalte**: Nur Counts öffentlich, keine Inhalte
4. **Keine Gedankenblasen-Sammlung**: Noch nicht implementiert (weder für Menschen noch Wesen)
5. **Keine Aufgenommene-Splitter-Protokoll**: Zähler vorhanden, aber kein per-User-Record
