# Sicherheitslücke geschlossen: Auth-Gate auf Planer-APIs + Cookie-Pfad-Bug gefunden und behoben

Fortsetzung des heute Vormittag validierten Megaplans (10:14-10:27, drei Explore-Agents
+ ein Validierungs-Agent für Betriebssystem/Briefkasten). Der Validator hatte gefunden:
`/api/state/`, `/api/files/`, `/api/streams/` liefen komplett unauthentifiziert auf der
echten, öffentlich erreichbaren Website - der Origin-Check greift nicht ohne
Origin-Header und ist trivial umgehbar. Django hat aber bereits ein fertiges
`is_staff`-Muster (wie `lexicon/views.py` `curator_required`), Daniels eigener User ist
schon `is_staff`/`is_superuser`.

## Fix 1: Auth-Gate

`_require_staff(request)` in `planner_api.py` ergänzt, an den Anfang von
`planner_state_api`, `planner_files_api` (deckt auch alle `koerper-*`-Ops ab) und
`planner_streams_api` gehängt. Liefert `401 {"ok": false, "error": "auth_required"}`
statt 403-Redirect, da es reine JSON-Fetch-Endpunkte sind, keine Seiten-Navigation.
Live verifiziert: anonym `401`, die Seite selbst bleibt bei `200` (nicht gegated).

Statt Daniels eigenen Account zu nutzen, extra dafür einen separaten `is_staff`-User
`ai_stroeme` angelegt (kein Superuser) - per Django-Shell, ohne Daniels eigenes
Passwort zu berühren. Zugangsdaten liegen in
`WorldWORDS-ANTIBIBEL-Website/secrets/ai_stroeme_planner_login.txt` (bereits
vorhandener, gitignorter `secrets/`-Ordner, chmod 600, owner `worldwords`).

## Fix 2: Cookie-Pfad-Bug (beim Testen gefunden, nicht vorher bekannt)

Nach dem ersten Login blieb der Planer trotzdem bei "Server nicht erreichbar" hängen.
Ursache: `SESSION_COOKIE_PATH = FORCE_SCRIPT_NAME + "/"` (also
`/WORLDwordsANTIbibel/`) in `settings.py` - ein bewusst gesetzter Wert für die
Haupt-Website. Der Planer hängt aber unter einer eigenen, unpräfigierten Nginx-Route
(`/Mein-Gesamtkonstrukt-planer/` → direkt zu Django) und sein JS ruft die API über
absolute Root-Pfade auf (`workspace.js`: `API = "/Mein-Gesamtkonstrukt-planer/api/files/"`).
Das pfad-eingeschränkte Cookie kam bei diesen Aufrufen nie an - Login lief technisch
durch, half dem Planer aber nichts. War vorher nie sichtbar, weil der Planer bis eben
komplett offen war (kein Auth = kein Cookie-Problem).

Mit Daniel abgestimmt (drei Optionen genannt: Cookie domainweit, Nginx-Route
umhängen, oder Planer-JS auf den Präfix umstellen - er hat sich für die erste,
einfachste entschieden): `SESSION_COOKIE_PATH` auf `"/"` gesetzt, `CSRF_COOKIE_PATH`
unverändert gelassen (Planer-Views sind ohnehin `@csrf_exempt`, betrifft sie nicht).

**Eigener Fehler dabei, sofort behoben:** Die Edit hat `settings.py` mit `root:root`-
Ownership statt `worldwords:worldwords` weggeschrieben (dieser Container mountet
`/vps_root` mit root-Rechten). `ExecStartPre=manage.py check` läuft aber als
`worldwords`-User und konnte die Datei danach nicht mehr lesen - der Dienst ging kurz
in eine Restart-Schleife (`PermissionError: [Errno 13]`). Sofort per `chown` behoben,
Downtime lag im Bereich weniger Sekunden (ein fehlgeschlagener Startversuch, dann
sofort erfolgreich). Lehre für zukünftige Edits an Dateien unter `/vps_root/werkraum/WorldWORDS-ANTIBIBEL-Website/`:
Ownership nach jedem Edit prüfen, nicht nur Syntax.

Zusätzlich musste das bereits gesetzte `sessionid`/`csrftoken`-Cookie in der eigenen
Browser-Session per CDP (`Network.deleteCookies` + `Network.setCookie`) manuell mit
`path:"/"` neu gesetzt werden, weil Django ein bereits gültiges Session-Cookie nicht
von selbst mit neuem Pfad re-issued - nur bei echtem Neu-Login würde ein frisches
Cookie mit dem neuen Pfad kommen.

## Ergebnis, live verifiziert

- Anonymer Zugriff auf `/api/state/`, `/api/files/`, `/api/streams/`: `401`
- Lexikon-Website (unbeteiligt): weiterhin `200`, keine Downtime dort
- Eigener eingeloggter Browser-Tab: Statusanzeige wechselt von "NICHT GESPEICHERT ·
  Server nicht erreichbar" zu "SERVER · einzige Wahrheit · Stand s780"

## Was noch offen ist vom Megaplan

- Live-Updates (SSE) - nicht begonnen, Validator warnt vor Concurrency-Risiko (nur 6
  gleichzeitige Request-Slots insgesamt, WSGI/gthread, kein ASGI)
- Echter VPS-Dateisystem-Schreibzugriff - nicht begonnen, braucht von Daniel benannte
  Pfade + systemd-`ReadWritePaths`-Edit
- Mehrstrom-Briefkasten - nur `ChatGPT_Work` fest verdrahtet, `Claude_Work` nicht,
  kein "neu angekommen"-Indikator
