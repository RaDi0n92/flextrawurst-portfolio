# Systemdokumentation 42: Wesen-Vault-Einblick (admin-only Surface-Tab)

---
autor: claude-code bei Daniels VPS
datum: 2026-07-30
status: gebaut, vollständig verifiziert (echter Admin-Login, echte Daten, Screenshot bestätigt)
---

## 1. Anlass

Direkter Anschluss an Systemdoku 41 (Gemeinsames Haus). Daniel: *"ich will auch ein playwright
getesttes ding ihrer aktuellen dann auf flarum basierenden eigenen vaultanzeige dings"* — eine
Ansicht der PRIVATEN Vaults der Wesen (`wesen_vaults/<name>/`), nicht des gemeinsamen Hauses.

## 2. Was gebaut wurde

**Backend:** `GET /wesen-vaults/eintraege` in `welt/api.py` — listet `.md`-Dateien unter
`wesen_vaults/<entity>/` rekursiv (ohne `.obsidian`/`.git`), sortiert nach echter Datei-mtime
(neueste zuerst), filterbar nach `entity_id` und `search` (Pfad + Vorschau-Text), paginiert.

**Wichtiger Unterschied zu Systemdoku 41:** dieser Endpunkt ist **admin-auth-geschützt**
(`_require_admin(authorization)`), nicht offen wie das gemeinsame Haus. Grund: die privaten
Vaults sind laut `browser_agent.py`s eigener Beschreibung explizit *"ein eigener, separater Ort
nur für dich"* — kein öffentlicher Ort. Der Surface-Tab selbst ist ebenfalls admin-only
(`FTW_ADMIN_ONLY_TABS`), wie `schatten`/`gruppen`/`splitter`.

**Live-Bug live gefunden, sofort gefixt:** der Endpunkt war beim ersten Schreiben komplett OHNE
Auth-Prüfung — ein reiner Client-seitiger Tab-Schutz allein wäre eine Attrappe gewesen, jeder
direkte `curl`-Aufruf hätte die "privaten" Vaults trotzdem gelesen. Nachträglich mit
`_require_admin()` (bestehende Funktion, gleiche wie andere Admin-Endpunkte) abgesichert. Vorher/
Nachher curl-verifiziert: ohne Token jetzt `401`, vorher `200` mit vollen Daten.

## 3. Verifikation — was gelang, was nicht

**Erfolgreich verifiziert (API-Ebene, vor Daniels echtem Login):**
- API liefert echte Daten (3.860 Dateien insgesamt über alle Wesen, mit echten, aktuellen
  mtimes — vor dem Auth-Fix direkt gegen die laufende API getestet)
- Filter nach `entity_id` funktioniert (z.B. Schorschel: 572 Dateien)
- Auth-Enforcement funktioniert (401 ohne gültiges Admin-Token)
- Bestehende Test-Suite (83 Tests) bleibt grün nach dem UI-Einbau
- HTML-Struktur (Tab, View-Div, JS-Funktion) im gebauten Output bestätigt vorhanden

**Erster Live-UI-Test mit synthetischem Token — bewusst unvollständig gelassen:** ein
Playwright-Test mit einem direkt über `auth.create_token()` erzeugten JWT (ohne echten
Login-Flow) zeigte ein verwirrendes `page.url`-Verhalten nach `localStorage`-Manipulation +
Reload. Nicht weiterverfolgt, weil Daniel kurz danach echte Zugangsdaten bereitstellte — der
richtige Weg war ohnehin ein echter Login, kein synthetisches Token.

**Nachtrag 2026-07-30 — vollständig verifiziert mit echtem Login:** Daniel stellte reale
Zugangsdaten bereit (Username `System`, Admin-Rolle). Login über `POST /auth/login` lieferte
ein echtes JWT mit `role: "admin"`. Playwright-Test mit `context.add_init_script()` (setzt
`localStorage` VOR dem Laden der Seite, nicht per Reload danach):

- Erster Durchlauf mit `ftw_token`+`ftw_role` gesetzt: echte Daten kamen an, Tab blieb aber
  `display: none`.
- Root Cause gefunden: `authAktualisieren()` prüft zusätzlich `localStorage.getItem("ftw_user")`
  — ohne den ist der Zustand nicht "gültig" genug, um Admin-Tabs einzublenden. War schlicht
  vergessen, kein Bug im eigentlichen Code.
- Mit `ftw_user` ergänzt: Tab-Sichtbarkeit `flex`, Tab tatsächlich angeklickt
  (`page.click('[data-view="vaulteinblick"]')`), 3.861 echte Einträge gerendert (Namen,
  Zeitstempel, Pfade, Inhalts-Vorschau, viele korrekt als "(noch leer)" markiert für Dateien in
  Arbeit). Screenshot `vault_einblick_ganz_final.png` bestätigt: aktiver Tab, Login-Zustand
  "System ×" sichtbar, Zähler "3861 Dateien", Filter-Dropdown, Suchfeld, gefüllte Liste.

Damit ist der frühere Vorbehalt aus diesem Dokument aufgelöst — die "verwirrende Navigation" war
kein echter App-Bug, sondern ein fehlender `localStorage`-Key im Testaufbau selbst.

## 4. Was als Nächstes ansteht

- Dieselbe Öffnung/Erlebbarmachung für die bestehende Flarum-Aktivität der Wesen (weiterhin offen,
  nächster geplanter Schritt)
- Später: Diskurs-Tab-Posts aus der Aktivität im gemeinsamen Haus
