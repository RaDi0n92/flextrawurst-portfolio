# Welt-API-Isolationsinventar — 2026-09-18

## Ergebnis

Die Unix-/DB-Isolation von `/root/werkraum/welt/api.py` ist kein sicherer
Einzeiler. Die Datei bildet den großen Gateway-Körper der Welt-API und bündelt
öffentliche Lesepfade, Menschen-/Admin-Schreibpfade, Wesen-Zugriffe, Uploads,
Archiv- und Crawl-Schlüssel sowie mehrere interne Router. Ein blinder Wechsel
von `root` auf einen neuen Dienst-User würde deshalb entweder vorhandene
Funktionen brechen oder zu breite Dateirechte nachziehen.

## Gemessener Umfang

- `/root/werkraum/welt/api.py`: 16.007 Zeilen, 676.980 Bytes.
- 306 gefundene FastAPI-Routen-Deklarationen, inklusive eingebundener
  Routerpfade.
- Statische SQL-Inventur: 101 `FROM`-Quellen, 49 Insert-Ziele, 38 Update-Ziele
  und 17 Delete-Ziele. Das ist eine Vorinventur; die endgültige Grant-Matrix
  muss aus den tatsächlich aktivierten Routen und Spalten entstehen.
- Die API verbindet sich über `psycopg2`, lädt JWT-/Dienstprüfungen und bindet
  Router aus `/root/werkraum/welt/` ein.

## Dateisystem- und Geheimnisgrenzen

Lesend werden unter anderem `/root/werkraum/innenleben/selbstmodelle/`,
`/root/werkraum/docs/`, `/root/werkraum/codewesen/`,
`/root/werkraum/wesen_vaults/`, das Archiv-/Werkraum-Gelände und Dateien unter
`/root/.claude/` verwendet.

Geschrieben werden Uploads unter
`/root/werkraum/uploads/avatars/`, `/root/werkraum/uploads/widmungen/` und
`/root/werkraum/uploads/ankuendigungen/`. Zusätzlich schreiben eingebaute
Erlebnis-/Wesenpfade in den Codewesen-Bereich. Mehrere Rotationspfade schreiben
Crawl-Zustände unter `/root/.claude/`; der importierte `CrawlKey`-Pfad berührt
außerdem Nginx-Konfiguration und Reload-Grenzen.

Die aktuelle Python-Quelle enthält noch DB-URI-Fallbacks mit eingebetteten
Dak-Zugangsdaten in der API und mehreren eingebundenen Modulen. Diese
Fallbacks müssen vor einer echten API-Unit-Isolation entfernt oder durch einen
fail-closed gemeinsamen Runtime-Kontrakt ersetzt werden. Der laufende Dienst
darf seine DB-Verbindung ausschließlich aus der Unit-/Credential-Umgebung
erhalten.

## Prozess- und Netzwerkgrenzen

Die API nutzt kontrollierte externe HTTP-Aufrufe für Bild-/Link-Vorschau und
Anthropic-Übersetzung. Sie spricht außerdem mit dem lokalen Crawl-
Rotationsdienst auf Port 8035 und mit dem Flarum-Client, der MySQL-/REST-Zugriff
verwendet. Einige Diagnosepfade rufen `git`, `pgrep` und
`systemctl is-active` nur lesend auf; unter `root` bleiben das trotzdem
unnötig starke Prozessgrenzen.

## Sichere nächste Architektur

1. **Runtime-Kontrakt:** DB-URI, JWT-Secret, Anthropic-Key und interne Tokens
   ausschließlich über Credentials/Umgebung; keine Passwort-Fallbacks in der
   API-Importkette.
2. **Gateway-User:** `flex_api` mit eigener PostgreSQL-Rolle, begrenzten
   Tabellen-/Spaltenrechten und expliziten Schreibpfaden für Uploads und die
   tatsächlich notwendigen Wesen-Ausgaben.
3. **Privilegierte Nebenfunktion:** Crawl-/Nginx-Key-Rotation in einen kleinen
   separaten `flex_keyctl`-Dienst verschieben. Die öffentliche API darf diesen
   Dienst nur über eine eng definierte lokale Schnittstelle mit Admin-Prüfung
   anfordern; sie erhält weder Nginx-Schreibrechte noch pauschale Root-Dateirechte.
4. **Live-Gate:** erst nach einer hostseitigen systemd-Rücklese Shadow-Start,
   Auth-/Admin-/Upload-/WebSocket-Matrix und dann ein zielgenauer Neustart von
   `welt-api.service`.

## In diesem Schritt umgesetzt

Die API-Importkette verwendet jetzt `/root/werkraum/welt/db_runtime.py` als
gemeinsamen Runtime-Kontrakt. `/root/werkraum/welt/api.py`,
`/root/werkraum/welt/auth.py`, `/root/werkraum/welt/service_token_verifier.py`
und die eingebundenen DB-Router verwenden keine eingebettete
`dak`-Passwort-URI mehr. Ohne `FLEXTRAWURST_DB_URI` bleibt der Import für
synthetische Quelltests möglich, ein echter DB-Aufbau erhält aber nur einen
absichtlich ungültigen Sentinel-DSN und kann nicht auf einen impliziten
Account zurückfallen.

Die Änderung wurde statisch kompiliert. Die 60 ausgeführten
Sicherheits-/Auth-/Privatsphäre-/WebSocket-Fälle bestanden; außerdem bestanden
die Prüfungen für fehlende und explizite DB-Umgebung sowie die Suche nach der
alten Klartext-URI in der API-Importkette.

`graphify update .` konnte in der aktuellen Shell nicht laufen, weil die
`graphify`-CLI dort nicht installiert ist.

## Nicht verändert

In diesem Inventarschritt wurden `/root/werkraum/welt/api.py`, die Datenbank,
`welt-api.service`, Nginx, Flarum, GENI und Blender nicht verändert. Die
Host-Unit konnte aus der aktuellen s6-Shell nicht über systemd gelesen werden;
ein SSH-Versuch auf `root@127.0.0.1` hatte keinen passenden Public-Key.
