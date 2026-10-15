---
datum: 2026-07-31
betrifft: [zensi, geni, sicherheit, aufraeumung, private-schluessel]
importable: false
autor: claude-code bei Daniels VPS
---

# Zensi/GENI — 27GB alte Testbestände weg, dabei ein doppelt liegender privater Schlüssel gefunden

## Wo das herkommt

Direkter Anschluss an die Gesamtatlas-Kritik: beim "was ist scheiße"-Rundgang war Zensis
`observed_path_count` für `zensi` (5.236.402) auffällig, `indexed_path_count` nur 5.518 —
2,6 Mio. der beobachteten Dateien liegen unter `wesensprofile/`, davon 2.521.158 (96%) allein
unter `GENI/{klon,sandbox}/`. Daniel: *"ich habe nach bau niemals zensi benutzt das müssen
alles alte testbestände durch den bau sein die man löschen kann oder?"*

## Verifiziert statt angenommen

Neueste Datei im gesamten `GENI`-Ordner: `2026-07-26 22:24:57` — **106 Stunden (4,4 Tage) alt**,
obwohl `zensi.service` durchgehend aktiv lief (PID lebt). Bestätigt Daniels Vermutung: alte
Bau-/Testbestände, seit über vier Tagen unberührt.

## Der eigentliche Grund, warum Zensi bei mir "nur lesend" markiert war

Daniel hat gefragt, warum genau. Meine erste Antwort (aus dem Gedächtnis zitiert, "Systemdoku 38
Abschnitt 17-18") war falsch — die Datei hat gar nicht so viele Abschnitte. Nachgesehen statt
weiter aus der Erinnerung zitiert: der echte Grund steht direkt im Code
(`tools/vps_mcp/vps_mcp_server.py`, Zeile 1849ff.): unter `wesensprofile/GENI/{klon,sandbox}/`
liegen echte private TLS-Schlüssel (`ssl_key.pem`), `server.py` hat einen fest einprogrammierten
DB-Connection-String. Ein Redteam-Fund vom 2026-07-23 zeigte, dass `/root/zensi` in
`ALLOWED_ROOTS` steht und `server.py` dadurch live über normale Datei-Tools lesbar war
(Dateiname unauffällig genug für `SECRET_MUSTER`). Sofortmaßnahme damals: `server.py` gezielt in
`_EXAKTE_GEHEIME_PFADE` gesperrt — die größere Architekturfrage ("sollte `/root/zensi` überhaupt
volle lesbare Wurzel sein?") blieb bewusst offen für Daniel, nicht gelöst.

## Der Fund beim genaueren Hinsehen

Das `ssl_cert.pem` unter `wesensprofile/GENI/klon/` per `openssl x509` geprüft: `CN=geni-vps`,
SHA1-Fingerabdruck `CF:47:46:7E:EA:E7:94:2E:BF:16:DA:47:C3:83:3C:2A:B9:CF:69:3C`. Gegen den
tatsächlich live von `geni-web.service` (Port 8020) ausgelieferten Zertifikat-Fingerabdruck
geprüft (`openssl s_client -connect 127.0.0.1:8020`) — **exakt identisch**. Der zugehörige
private Schlüssel in der Zensi-Testkopie ist also keine Test-Fake-Datei, sondern eine echte
Kopie des aktuell aktiven privaten TLS-Schlüssels von GENI Web. Der echte, maßgebliche Schlüssel
liegt unter `/root/werkraum_geni/ssl_key.pem` — unangetastet, dort gehört er hin.

## Was gemacht wurde

1. Beide `ssl_key.pem`-Kopien (`klon/` und `sandbox/`) **direkt gelöscht, ohne sie ins Archiv
   mitzunehmen** — bewusste Entscheidung: ein Archiv hätte die unnötige Schlüssel-Duplizierung
   nur an einen dritten Ort verschoben statt sie zu beenden. Der echte Schlüssel bei
   `werkraum_geni` bleibt die einzige Quelle.
2. Verifiziert: `werkraum_geni/ssl_key.pem` unangetastet, `geni-web.service` weiterhin aktiv.
3. Rest des `GENI`-Ordners (27GB, 2.521.156 Dateien) komplett archiviert
   (`/root/werkraum_archive_gesamtatlas_aufraeumung/zensi_geni_alte_testbestaende_20260731T0645Z.tar.gz`,
   2,9GB komprimiert), Dateizahl im Archiv exakt gegen das Original geprüft (2.521.156 = 2.521.156).
4. Danach `rm -rf` auf den Live-Ordner. **26GB frei geworden** (642G → 616G belegt).
5. Nachverifiziert: `geni-web.service` weiterhin aktiv, echte HTTPS-Antwort (200) von Port 8020
   bestätigt — kein Seiteneffekt auf den laufenden Dienst.

## Nachtrag: ein zweites, komplettes Duplikat gefunden

Direkt danach aufgefallen: `/root/zensi/wesensprofile/GENI/` (ohne `obsidian_vault/` davor) ist ein
**zweiter, komplett eigenständiger Ordner** mit identischer Dateizahl (2.521.156), identischen
Zeitstempeln und denselben zwei `ssl_key.pem`-Kopien — kein Symlink, zwei echte physische Kopien
derselben alten Testdaten. Gleiche Behandlung: Schlüssel direkt gelöscht (nicht archiviert), Rest
archiviert (`zensi_geni_zweites_duplikat_20260731T0710Z.tar.gz`, 2,9GB, Dateizahl exakt geprüft:
2.521.156 = 2.521.156), danach `rm -rf`. **Weitere 27GB frei geworden** (619G → 592G belegt).
Beide Dienste (`geni-web.service`, `zensi.service`) danach erneut als aktiv + funktionsfähig
bestätigt. Zusammen mit dem ersten Fund: **53GB** aus zwei parallelen Kopien derselben toten
Testdaten entfernt.

## Korrektur zu einer eigenen früheren Aussage

Auf Daniels Nachfrage ("welche Geheimnisse genau?") eine echte inhaltsbasierte Suche gemacht
(nicht nur nach verdächtigen Dateinamen wie `SECRET_MUSTER` es tut, sondern nach tatsächlichen
Passwort-/Schlüssel-Mustern im Dateiinhalt selbst) über alle Code-Dateien direkt unter
`/root/zensi/` — **keine weiteren versteckten Geheimnisse gefunden.** Dabei auch festgestellt:
meine vorherige Aussage, `server.py` habe weiterhin einen "fest einprogrammierten
DB-Connection-String", war **veraltet** — das wurde bereits am 2026-07-23, demselben Tag wie der
Redteam-Fund, in Zensi selbst behoben (`_db_uri()` liest jetzt aus
`/root/werkraum/.agent/flextrawurst-db.env`, kein Klartext-Passwort mehr im Code). Die
Blockierung von `server.py` in `_EXAKTE_GEHEIME_PFADE` ist seitdem eine zusätzliche
Vorsichtsmaßnahme, kein noch bestehendes akutes Loch mehr.

## Ehrlich offen

Die größere Architekturfrage aus dem 2026-07-23-Redteam-Fund (soll `/root/zensi` überhaupt eine
volle lesbare `ALLOWED_ROOTS`-Wurzel sein, oder enger gefasst werden) ist weiterhin nicht gelöst —
heute nur die konkreten Datenfunde behoben, nicht die grundsätzliche Zugriffsfrage. Zensi bleibt
außerhalb meines Schreibbereichs für alles andere. Ob es noch weitere Duplikate derselben
GENI-Testdaten an einem dritten Ort gibt, wurde nicht systematisch mit einer vollständigen
Dubletten-Suche über das ganze VPS geprüft — nur die zwei, die beim Rundgang auffielen.
