---
titel: Admin-Route-Guard (SEC-005/007) — Bearer-Doppelung machte die Prüfung für ALLE unbrauchbar
typ: system
erstellt: 2026-09-30
autor: claude-code bei Daniels VPS
---

# Admin-Route-Guard (SEC-005/007) — Bearer-Doppelung machte die Prüfung für ALLE unbrauchbar

[[INDEX|← Index]]

## Zweck

`flextrawurst/scripts/admin_route_guard.ts` schützt seit 2026-09-17 (Codex-Sicherheitsreview
SEC-005/SEC-007, siehe `_claude/_import_codex_grundriss/berichte/2026-09-07-flextrawurst-
sicherheitsreview.md` und `.../2026-09-16-sicherheitsfixes-umsetzung.md`) alle zustandsändernden
Requests unter fünf Pfad-Präfixen: `/wesen`, `/api/wesen-dienst-wizard`, `/api/flarumstyler`,
`/dolphin`, `/aufgabenchats`. Vor diesem Fix konnte jeder anonyme Internet-Besucher ohne jede
Anmeldung bestehende Wesen überschreiben oder löschen, Container-Admin-Aktionen auslösen und
mehr — eine echte, im Review dokumentierte Lücke.

Serverseitig: `requiresAdministrativeAuth()`/`permitsAdministrativeOrigin()`/
`administrativeAuthStatus()` in `admin_route_guard.ts`, geprüft in `serve_process_camera_preview.ts`
vor jedem Routing. Clientseitig: `admin_auth_client.js`, ausgeliefert unter `/admin-auth-client.js`,
in jede geschützte Seite per `withAdministrativeClient()` als `<script>`-Tag im `<head>` injiziert —
patcht `window.fetch`, hängt bei administrativen Requests den in `localStorage['ftw_token']`
gespeicherten Login-Token als `Authorization`-Header an.

## Der Fund, 2026-09-30

Daniel meldete: `/codexium2`-Formular abschicken gibt einen Fehler, auch nach Login mit seinem
Admin-Konto. Erst vermutet: abgelaufener Token (JWT-Laufzeit 7 Tage, `welt/auth.py`,
`_TOKEN_DAYS = 7`) oder fehlende Admin-Rolle (Registrierung vergibt laut `welt/api.py:_create_user`/
`/auth/register` immer `role='mensch'`, kein Selbstbedienungsweg zu `role='admin'`) — beides von
Daniel verneint bzw. nicht der Fall ("trotz einloggen ist es fehler" / "bin als admin da
eingeloggt").

**Tatsächliche Ursache, im Code gefunden:** `build_surface.ts` speichert den Login-Token beim
Login UND bei der Registrierung bereits fertig formatiert:
```js
localStorage.setItem("ftw_token", "Bearer " + d.token);
```
Eine bereits länger funktionierende Stelle im selben Code (`build_surface.ts:17364`,
Supporter-Bewerbung) verwendet den gespeicherten Wert entsprechend direkt:
```js
headers:{'Authorization': localStorage.getItem('ftw_token')||''}
```

`admin_auth_client.js` (SEC-005/007, neuer Code) tat das nicht — es behandelte den gespeicherten
Wert fälschlich als rohen Token ohne Präfix:
```js
const token = localStorage.getItem('ftw_token');
if (token) headers.set('Authorization', 'Bearer ' + token);   // Bug: token enthaelt schon "Bearer "
```
Ergebnis: `Authorization: Bearer Bearer eyJhbGc...` — ein doppeltes Präfix. Der Server-Regex in
`administrativeAuthStatus()` (`^Bearer \S+$`) akzeptiert das nicht (der zweite Leerraum nach dem
ersten "Bearer" bricht die Übereinstimmung), gibt also unabhängig vom Kontostatus **immer** 401
zurück — für Admins genau wie für Anonyme. Die Prüfung war seit ihrer Aktivierung
(2026-09-17) für **jeden** Aufrufer unbenutzbar, nicht nur für Nicht-Admins. Das erklärt auch,
warum Daniel schon vor vier Tagen (26.09.) denselben Fehler hatte, egal was er versuchte.

## Fix

`admin_auth_client.js`: `headers.set('Authorization', token)` statt `'Bearer ' + token` — der
gespeicherte Wert wird jetzt direkt übernommen, kein zweites Präfix mehr.

Keine Serverkomponente betroffen — die Datei wird pro Request frisch von der Platte gelesen
(`readFileSync` in `serve_process_camera_preview.ts`, Route `/admin-auth-client.js`), kein
Dienst-Neustart nötig.

## Verifikation

Live, per Playwright, mit einem über `/auth/register` echt angelegten Testkonto (Rolle
automatisch `mensch`, keinerlei Admin-Rechte):
- Request-Header nach dem Fix: `Authorization: Bearer eyJhbGc...` (einfaches Präfix, korrekt).
- Antwort von `/wesen/save`: **403** ("kein aktives Admin-Konto") statt vorher 401 — die Prüfung
  erreicht jetzt tatsächlich `welt-api`s `/auth/admin-check` und wertet die echte Kontorolle aus,
  statt schon am Regex zu scheitern. Für ein echtes Admin-Konto (Daniels eigenes) sollte
  dieselbe Kette jetzt mit 200 durchlaufen — von Daniel selbst noch zu bestätigen, da sein
  Kontostatus von hier aus nicht direkt einsehbar ist (kein Produktions-DB-Zugriff aus diesem
  Container).

## Was das für die anderen vier Präfixe bedeutet

`/dolphin`, `/aufgabenchats`, `/api/flarumstyler`, `/api/wesen-dienst-wizard` nutzen denselben
`admin_auth_client.js` — hatten also denselben Bug, unabhängig ob dort schon jemand darüber
gestolpert ist. Mit diesem einen Fix sind alle fünf Bereiche gleichzeitig repariert.

## Bestätigt, 2026-09-30

Daniel hat sich nach dem Fix einmal neu auf der Surface angemeldet — `/codexium2` funktioniert
seitdem einwandfrei. Der Bearer-Doppelung-Bug war die vollständige Ursache, kein weiteres
Problem mit seinem Kontostatus. Nichts mehr offen an dieser Stelle.

*Weiter: [[21_wesen_chat_testbed]] | [[38_vps_mcp_werkzeugkoerper]]*
