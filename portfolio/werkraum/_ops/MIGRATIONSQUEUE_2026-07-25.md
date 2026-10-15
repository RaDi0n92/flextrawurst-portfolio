# MIGRATIONSWARTESCHLANGE 2026-07-25

Statuswerte:

- `GESCHÜTZT` = live oder referenziert, nicht verschieben
- `PRÜFEN` = Herkunft oder Nutzung noch nicht vollständig geklärt
- `QUARANTÄNE-KANDIDAT` = wahrscheinlich entbehrlich oder doppelt, aber noch nicht löschbar
- `EXPORT-KANDIDAT` = aus Root in einen datierten Exportbereich überführbar, sobald Archivtest und Hash vorliegen
- `BACKUP-KANDIDAT` = wichtige Sicherung, geordnet ablegen, niemals als Müll behandeln
- `SONDERFALL` = braucht eigenes technisches Verfahren

| Status | Pfad / Gruppe | Nächste notwendige Prüfung | Vorgesehenes Ziel |
|---|---|---|---|
| GESCHÜTZT | `/root/werkraum` | live eingebunden, Git-Änderungen vorhanden | bleibt |
| GESCHÜTZT | `/root/flextrawurst` | live eingebunden | bleibt |
| GESCHÜTZT | `/root/visionen` | live eingebunden | bleibt |
| GESCHÜTZT | `/root/zensi/obsidian_vault` | live eingebunden | bleibt |
| GESCHÜTZT | `/root/werkraum/wesen_vaults/*` | live in Wesen-Container eingebunden | bleibt |
| SONDERFALL | `/root/werkraum_main_wt` | Git-Worktree-Beziehung, zwei lokale Änderungen | später Git-Worktree-gerecht nach `_worktrees` |
| SONDERFALL | Docker-Container `obsidian_dead` | gemeinsames Volume mit aktivem Obsidian, Overlay2-Fehler | getrennte Docker-Reparatur, kein Dateiaufräumen |
| EXPORT-KANDIDAT | `/root/FLEXTRAWURST_ALLES_IN_EINER_DATEI.zip` | Archivtest, Manifest, Hash | `/root/werkraum/_exports/2026-07-25/flextrawurst/` |
| EXPORT-KANDIDAT | `/root/KOSMOS_GESAMT_ALLE_DATEIEN.zip` | Archivtest, Inhaltsliste, Vergleich | `/root/werkraum/_exports/2026-07-25/kosmos/` |
| EXPORT-KANDIDAT | `/root/KOSMOS_VOLLSTAENDIG_ALLE_91_DATEIEN.zip` | Archivtest, Inhaltsliste, Vergleich | `/root/werkraum/_exports/2026-07-25/kosmos/` |
| BACKUP-KANDIDAT | `/root/vault-backup-before-mojibake-fix-2026-05-22-040500.tar.gz` | Archivtest, Wiederherstellungsnotiz, Hash | `/root/werkraum/_backups/manuell/2026-05-22/` |
| PRÜFEN | `/root/vollexportv2.zip` | Herkunft und Ersatzstatus | Export oder Archiv |
| EXPORT-KANDIDAT | `/root/KOSMOS_3D_PAKET_FUER_CHATGPT.zip` | Archivtest und Inhalt | datierter Kosmos-Exportbereich |
| EXPORT-KANDIDAT | `/root/WUPPER_ENNEPE_KOSMOS_VOLLSTAENDIG.zip` | Archivtest und Inhalt | datierter Kosmos-Exportbereich |
| QUARANTÄNE-KANDIDAT | `/root/server.js.save` | Referenzsuche; Inhalt ist identisch zu `server.js` | `_quarantaene/root-altstaende/` |
| PRÜFEN | `/root/node`, `/root/sss`, `/root/^c` | Referenzsuche und Dateityp | Quarantäne, falls unbenutzt |
| PRÜFEN | `/root/server.js`, `package*.json` | Prozess- und Referenzsuche | geordneter Dienstkörper oder bleibt |
| PRÜFEN | `/root/composer.json`, `/root/composer.lock` | Projektzugehörigkeit | geordneter Projektkörper oder bleibt |
| PRÜFEN | `/root/Modelfile` | aktive Modellreferenz | Modellkörper oder bleibt |
| PRÜFEN | `/root/setup-claude.sh` | aktive Nutzung und Provenienz | `_ops` oder Archiv |
| QUARANTÄNE-KANDIDAT | Werkraum-XWD-Doppelgruppen | Referenzsuche, einen kanonischen Vertreter bestimmen | `_quarantaene/screens/2026-07-25/` |
| QUARANTÄNE-KANDIDAT | Werkraum-JPG-/PNG-Doppelgruppen | Referenzsuche, einen kanonischen Vertreter bestimmen | `_quarantaene/screens/2026-07-25/` |
| QUARANTÄNE-KANDIDAT | Werkraum-`Untitled`-/leere Platzhalter | Inhalt und Backlinks prüfen | `_quarantaene/platzhalter/2026-07-25/` |
| GESCHÜTZT | `kosmos/venv/bin/python*`, `pip*`, Paket-`__init__.py` | keine | technisch erwartete Doppelungen, bleiben |

## Verschiebegate

Ein Eintrag darf erst real bewegt werden, wenn alle zutreffenden Punkte erfüllt sind:

- [ ] Metadaten gelesen
- [ ] Hash oder Inhaltsvergleich vorhanden
- [ ] Referenzsuche abgeschlossen
- [ ] Container- und Dienstbezug ausgeschlossen oder angepasst
- [ ] Git-Bezug ausgeschlossen oder sauber behandelt
- [ ] Zielpfad eindeutig
- [ ] Vorher-Nachher-Nachweis vorgesehen
- [ ] Rücklesetest vorgesehen
- [ ] Laufzeittest vorgesehen

## Noch nicht ausgeführt

Mit dem aktuell verfügbaren VPS-MCP existiert kein freigegebener Datei-Verschiebe-, Lösch- oder Shell-Befehl. Deshalb wurden in diesem Ring keine Bestandsdateien heimlich bewegt oder gelöscht. Real angelegt wurden nur die Ordnungskarte, Zielzonen und diese Warteschlange.
