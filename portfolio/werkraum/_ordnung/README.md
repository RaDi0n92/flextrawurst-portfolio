# VPS-ORDNUNGSKÖRPER

Status: aktiv und versioniert
Stand: 2026-07-25, Europe/Berlin
Phase: erster realer Live-Bestandsscan

Diese Karte ist der verbindliche Einstiegspunkt für künftige Aufräum-, Sicherungs- und Verschiebearbeiten am VPS. Sie trennt lebende Körper, Quellkörper, Datenkörper, Exporte, Sicherungen, Arbeitskopien und überprüfbare Altlasten.

## 1. Harte Schutzregel

Nichts wird allein nach Name, Alter, Größe oder vermeintlicher Doppelung gelöscht oder verschoben.

Vor jeder Änderung müssen geprüft werden:

1. Container-Bind-Mounts und Docker-Volumes
2. systemd-Dienstpfade und laufende Ports
3. Git-Status und Git-Worktree-Verknüpfungen
4. Textreferenzen und Provenienz
5. Hash beziehungsweise Inhaltsgleichheit
6. Rücklesetest nach der Änderung
7. Dienst- und Webapp-Test nach der Änderung

## 2. LIVE / NICHT BLIND VERSCHIEBEN

### Hauptkörper

- `/root/werkraum`
  - live in den Haupt-Obsidian-Container eingebunden
  - enthält aktive Dienste, Code, Daten, Logs, Exporte, Obsidian-Inhalte und Wesen-Vaults
  - Git-Status beim Scan: 17 geänderte Dateien
- `/root/flextrawurst`
  - live in den Haupt-Obsidian-Container unter `/werkraum/flextrawurst` eingebunden
- `/root/visionen`
  - live in Haupt-Obsidian eingebunden
- `/root/zensi/obsidian_vault`
  - live in `obsidian-zensi` eingebunden
- `/root/werkraum/wesen_vaults/*`
  - live in die jeweiligen Wesen-Obsidian-Container eingebunden
- `/var/lib/docker/volumes/*`
  - aktive Container-Konfigurationen und Desktop-Zustände

### Zusätzlicher Git-Arbeitsbaum

- `/root/werkraum_main_wt`
  - Git-Worktree beziehungsweise zusätzlicher Arbeitsbaum
  - beim Scan: `hauhau_client.py` geändert
  - zusätzlich: `hauhau_client.py.NEUE_WAECHTER_VERSION_BACKUP` unversioniert
  - darf nur Git-Worktree-gerecht bewegt werden, niemals per einfachem Dateiverschieben

## 3. Containerlage

Bestätigt beim Scan:

- 11 laufende Container
- 1 toter Container: `obsidian_dead`

Laufende Körper:

- `obsidian`
- `obsidian-zensi`
- `obsidian-dakgordsystem`
- `obsidian-resonanzknoten`
- `obsidian-jumpa`
- `obsidian-r1zz1`
- `obsidian-traeumerlie`
- `obsidian-f3inschmecker`
- `obsidian-schorschel`
- `virtuellerdesktop1`
- `virtuellerdesktop2`

### Sonderfall `obsidian_dead`

Der Container ist wirklich im Docker-Status `dead`. Er ist aber nicht einfach belanglos:

- er bindet `/root/werkraum` und `/root/visionen` ein
- er benutzt dasselbe Docker-Volume `obsidian_config_ls` wie der aktive Hauptcontainer `obsidian`
- Docker meldet beim alten Entfernen einen Overlay2-Fehler: `operation not permitted`

Folge: Nicht blind löschen. Erst Container-Metadaten, gemeinsames Volume, aktiven Hauptcontainer und Overlay2-Rest getrennt behandeln.

## 4. Unordnung direkt unter `/root`

### Große Export- und Sicherungskörper

| Datei | Größe beim Scan | Einordnung |
|---|---:|---|
| `FLEXTRAWURST_ALLES_IN_EINER_DATEI.zip` | 742.186.936 Byte | großer manueller Export, aus `/root` heraus in einen datierten Exportbereich überführen |
| `KOSMOS_GESAMT_ALLE_DATEIEN.zip` | 205.614.522 Byte | Exportkandidat, vor Verschiebung Inhalt/Manifest prüfen |
| `KOSMOS_VOLLSTAENDIG_ALLE_91_DATEIEN.zip` | 205.620.559 Byte | fast gleich groß, aber nicht als identisch bestätigt |
| `vault-backup-before-mojibake-fix-2026-05-22-040500.tar.gz` | 520.304.215 Byte | wichtige historische Sicherung, nicht löschen; in datierten Backup-Bereich überführen |
| `vollexportv2.zip` | 1.332.184 Byte | alter Exportkandidat, Provenienz prüfen |
| `KOSMOS_3D_PAKET_FUER_CHATGPT.zip` | 63.504 Byte | Transfer-/Exportkörper |
| `WUPPER_ENNEPE_KOSMOS_VOLLSTAENDIG.zip` | 28.311 Byte | Transfer-/Exportkörper |

Die beiden großen Kosmos-ZIPs sind wegen abweichender Größe nicht bitidentisch. Ob eine die andere vollständig ersetzt, ist noch unbekannt.

### Bestätigte einfache Doppelung unter `/root`

- `/root/server.js`
- `/root/server.js.save`

Beide haben im begrenzten Doppelungsscan denselben SHA-256-Inhalt. Trotzdem erst prüfen, ob `.save` bewusst als lokaler Rücksprunganker gebraucht wird. Danach entweder in einen datierten Altstand verschieben oder entfernen.

### Leere Platzhalter unter `/root`

- `/root/node`
- `/root/sss`
- `/root/.ts_node_repl_history`

Nicht automatisch löschen. Zuerst prüfen, ob irgendein Skript absichtlich auf diese Pfade testet.

### Weitere lose Root-Dateien mit Klärungsbedarf

- `server.js`, `package.json`, `package-lock.json`
- `composer.json`, `composer.lock`
- `Modelfile`
- `setup-claude.sh`
- `nohup.out`
- `^c`
- einzelne Bilder
- Sicherheitsberichte
- Agenten-Hauptdateien `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `KIMI.md`, `grok.md`

Diese Dateien dürfen erst nach Referenzsuche und Prozessprüfung verschoben werden. Besonders die Agenten-Hauptdateien können absichtlich im Root liegen und werden vorerst als Root-Konfiguration behandelt.

## 5. Unordnung direkt in `/root/werkraum`

Der Werkraum-Wurzelbereich vermischt derzeit:

- produktiven Python-Code
- Service-Dateien
- Logs
- Bildschirm- und Obsidian-Testaufnahmen
- Exporte und Sicherungen
- Obsidian-Notizen
- leere Platzhalter
- aktive Laufzeitdaten

### Bestätigte identische Test-/Bildschirmdateien

Bitidentische Gruppen aus dem begrenzten Scan der ersten 500 Dateien:

1. `obs_jetzt.xwd`, `screen_current.xwd`, `screen2.xwd`, `obs_raised.xwd`
2. `obs_jetzt.jpg`, `obs_swiftshader.jpg`, `obs_raised.jpg`
3. `obs_loading.xwd`, `obs_now.xwd`
4. `screen2_view.png`, `screen2.png`
5. `obs_now.jpg`, `obs_loading.jpg`
6. `Untitled 2.canvas`, `Untitled 4.canvas`

### Leere oder fragwürdige Platzhalter im Werkraum-Wurzelbereich

- `2026-05-11.md`
- `info:`
- `Untitled.canvas`
- `dateiname`
- `baum:`
- `Untitled.md`
- `trigger_daniel.log`

Diese gehören zunächst in Quarantäne, nicht in den Papierkorb. Der Doppelungsscan war auf 500 Dateien begrenzt und ist deshalb keine vollständige VPS-Doppelungsanalyse.

### Nicht als Müll behandeln

Identische Dateien innerhalb von `kosmos/venv/bin/` und leere `__init__.py`-Dateien in Python-Paketen sind technisch erwartbar. Sie sind keine Aufräumkandidaten.

## 6. Zielstruktur für künftige Ordnung

Die bestehenden aktiven Hauptpfade bleiben zunächst bestehen. Neue oder bereinigte Nebenbestände sollen künftig in klar getrennte Zonen:

```text
/root/
├── werkraum/                 # aktiver Hauptarbeits- und Weltkörper
│   └── _ordnung/             # diese Ordnungskarte und spätere Inventare
├── flextrawurst/             # aktiver separater Flextrawurst-Codekörper
├── zensi/                    # aktiver Zensi-Körper
├── visionen/                 # aktiver Visionen-Körper
├── _exports/
│   └── YYYY-MM-DD/<system>/  # Transfer-ZIPs, ChatGPT-/Claude-Übergaben, Gesamtexporte
├── _backups/
│   ├── automatisch/
│   ├── manuell/
│   └── vor-migration/
├── _worktrees/               # nur Git-Worktrees, nur mit Git-Worktree-Befehlen bewegen
├── _quarantaene/             # ungeklärte Altlasten, niemals sofort löschen
├── _archive/
│   └── retired/              # bestätigte stillgelegte Körper
└── _ops/
    ├── inventories/
    ├── reports/
    └── migrationen/
```

## 7. Einheitliche Namensregeln

### Sicherungen

`YYYY-MM-DD_HHMM_<system>_<anlass>_<typ>.<endung>`

Beispiel:

`2026-07-25_0550_flextrawurst_vor-ordnungsring_vollbackup.tar.zst`

### Exporte

`YYYY-MM-DD_<system>_<inhalt>_export_vNN.zip`

### Berichte

`YYYY-MM-DD_<system>_<prüfung>_bericht.md`

### Keine Namen mehr wie

- `final_final_neu2`
- `alles`
- `vollexportv2` ohne Datum und System
- `Untitled`
- `dateiname`
- Dateien mit Doppelpunkt als improvisiertem Notiznamen

Menschen haben Dateinamen erfunden und anschließend beschlossen, sie nicht zu benutzen. Dieser Brauch endet hier.

## 8. Erster sicherer Migrationsring

Reihenfolge für reale Verschiebungen:

1. Export- und Backup-Zielzonen anlegen
2. große Root-ZIPs per Hash und Archivtest prüfen
3. Exporte datiert in `_exports` verschieben
4. Mojibake-Vault-Backup datiert in `_backups/manuell` verschieben
5. Bildschirm-Doppelungen in eine Quarantäne-Zone verschieben, jeweils eine kanonische Datei behalten
6. leere Root- und Werkraum-Platzhalter in Quarantäne verschieben
7. Referenzsuche und Laufzeittest durchführen
8. erst nach einer Beobachtungsphase endgültig löschen
9. `werkraum_main_wt` separat mit Git-Worktree-Logik behandeln
10. `obsidian_dead` separat als Docker-Reparaturfall behandeln

## 9. Was dieser Scan bewusst noch nicht behauptet

- Es ist nicht bestätigt, welche der großen Export-ZIPs vollständig redundant sind.
- Es ist nicht bestätigt, ob lose Root-Dateien wie `server.js`, Composer- oder Node-Dateien noch von einem Prozess gebraucht werden.
- Es ist nicht bestätigt, ob alle leeren Platzhalter bedeutungslos sind.
- Der Doppelungsscan war begrenzt und nicht vollständig.
- Noch wurde kein lebender Pfad verschoben oder gelöscht.

## 10. Verwendete reale Prüfungen

- VPS-Systemzustand
- freigegebene VPS-Wurzeln
- Root- und Werkraum-Dateilisten
- laufende Ports
- bekannte Webapps
- Docker-Containerliste
- Docker-Inspect für Haupt-Obsidian, Zensi, Wesen, Desktop und toten Container
- Git-Status von `werkraum` und `werkraum_main_wt`
- begrenzte Hash-Doppelungsscans unter `/root` und `/root/werkraum`

Öffentliche Websuche ist für den privaten VPS-Bestand keine geeignete Wahrheitsquelle und wurde dafür nicht verwendet.

Kann Richtigkeit nicht garantieren - bitte verifizieren.
