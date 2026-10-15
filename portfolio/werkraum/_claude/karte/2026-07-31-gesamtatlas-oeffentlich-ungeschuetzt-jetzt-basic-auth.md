---
datum: 2026-07-31
betrifft: [sicherheit, gesamtatlas, nginx, basic-auth, exposure]
importable: false
autor: claude-code bei Daniels VPS
---

# Gesamtatlas war öffentlich ohne jeden Login erreichbar — jetzt per Basic-Auth gesichert

## Was der Fall war

Direkt nachdem ich mir den Gesamtatlas auf Daniels Wunsch angeschaut hatte (öffentliche Web-Oberfläche
unter `https://flextrawurst.de/gesamtatlas/`, verifiziert HTTP 200 ohne jeden Login), hat Daniel selbst
den Finger drauf gelegt: die öffentliche Seite müsse sofort mit seinem Nutzernamen und einem
mitgeteilten Passwort gesichert werden (Passwort hier bewusst nicht wiederholt, siehe unten).

Das war kein Bagatellfund — der Gesamtatlas enthält vollständige Pfadindizes über praktisch das gesamte
VPS (188.897 indexierte Pfade, 425 Session-Verläufe, Projekt-Details, AI-Strom-Zustände), öffentlich
und unauthentifiziert erreichbar.

*(Das von Daniel im Chat genannte Passwort wird hier bewusst nicht wiederholt — Klartext-Passwörter
gehören nicht in eine dauerhaft in git versionierte Datei. Es steckt bereits gehasht in
`/etc/nginx/.htpasswd`, das ist die einzige Quelle der Wahrheit dafür.)*

## Was gemacht wurde

`/etc/nginx/sites-available/flextrawurst` hatte bereits ein etabliertes Basic-Auth-Muster für andere
sensible Routen (`/werkraum-api/`, mehrere weitere `auth_basic "Werkraum"` + `auth_basic_user_file
/etc/nginx/.htpasswd`-Blöcke) — der `location ^~ /gesamtatlas/`-Block hatte dieses Muster schlicht nie
bekommen (kein Bug, nur beim Bau der Route am 2026-07-30 offenbar nicht mitgedacht).

Vor der Änderung: Backup der kompletten nginx-Config
(`/etc/nginx/sites-available/flextrawurst.backup-vor-gesamtatlas-auth-20260731T041056Z`) — die Datei
liegt außerhalb des werkraum-Git-Repos, deshalb Dateikopie statt Commit.

Geprüft, ob Daniels genanntes Passwort bereits zum bestehenden `daniel`-Eintrag in `/etc/nginx/.htpasswd`
passt (per curl gegen eine bereits geschützte Route, `/werkraum-api/`: ohne Login 401, mit dem Passwort
404 statt 401 — Auth greift, kein neuer htpasswd-Eintrag nötig). Danach zwei Zeilen in den bestehenden
Content-Block ergänzt:
```
location ^~ /gesamtatlas/ {
    auth_basic "Werkraum";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://127.0.0.1:18108/;
    ...
```
`nginx -t` vor dem Reload geprüft (syntaktisch ok), dann `systemctl reload nginx` (kein harter Neustart,
kein Verbindungsabbruch für andere Routen).

## Verifikation

Live per curl, drei Fälle:
- ohne Login: 401
- mit falschem Passwort: 401
- mit Daniels Passwort: 200

Der reine Redirect-Endpunkt `/gesamtatlas` (ohne Slash, 308 auf `/gesamtatlas/`) bewusst ohne eigenen
Auth-Block gelassen — trägt keinen Inhalt, nur eine Weiterleitung, kein Sicherheitsrisiko.

## Nachtrag: älteres Passwort-Fragment in der Git-Historie, bewusst NICHT bereinigt

Beim Schreiben dieser Notiz aufgefallen: in `_claude/resonanz/tiefer_eingetaucht.md` steckt schon
länger ein anderes, älteres Passwort-Fragment (`[GESCHWAERZT]`, aus einer
früheren Obsidian-Reparatur-Notiz) — bereits in der Git-Historie, nicht aus dieser Session. Wegen der
Resonanzfeld-Extraktion (baut diese Datei bei praktisch jeder Session neu) ist die Zeile über sehr
viele Commits verteilt (73+ Treffer bei einer reinen Volltextsuche über die Historie, eine gezielte
`git log -S`-Suche brach nach 2 Minuten wegen der Repo-Größe ab).

Daniel dazu befragt (drei Optionen: global rotieren, nur für Gesamtatlas trennen, nichts ändern) —
**Entscheidung: nichts ändern.** Weder Passwort-Rotation noch Git-History-Bereinigung. Das geteilte
`daniel`-Konto in `/etc/nginx/.htpasswd` sichert neben Gesamtatlas auch `/werkraum-api/`, beide
virtuellen Desktops, Bildgenerator, Geni, Codewesen-Chat, dak+gord-Chat, zusatz-KompOase und
Flarumstyler-API — eine Rotation hätte all diese Logins gleichzeitig ungültig gemacht. Bewusst
liegen gelassen, kein offener Punkt für eine künftige Session, außer Daniel bringt es selbst wieder auf.

## Was ich mir merken will

Der Fund kam nicht aus eigener, proaktiver Sicherheitsprüfung — ich hatte die Seite kurz vorher besucht
und ihre Offenheit nicht selbst als Problem benannt, obwohl der Health-Check und meine eigene
Beschreibung ("öffentlich erreichbar, HTTP 200") das Signal enthielten. Daniel hat den Sicherheitsschluss
selbst gezogen. Bei künftigen "schau dir das an"-Aufträgen für neu gebaute öffentliche Oberflächen: die
Zugriffsschutz-Frage aktiv mitprüfen und benennen, nicht nur auf explizite Nachfrage reagieren.
