---
autor: claude bei Daniels VPS
datum: 2026-10-01
status: Entwurf zur Abnahme durch Daniel — kein Goal ist damit abgenommen, bevor Daniel es sagt
herkunft: `PLAN.md` (Goals G02 und G03, »Fertig, wenn« und Arbeitsvertrag Punkt 7), `ANFORDERUNGEN.md` (R001–R005, R118), `BUILD_LOG.md`, `augen_haende_bridge/tests/evidence/`, Daniels Rückmeldungen im Gespräch vom 2026-10-01
---

# Abnahmeprotokoll G02 und G03

Der Plan verlangt für »fertig« eine Ergebnisrücklese und einen dokumentierten Abschluss (Arbeitsvertrag Punkt 7). Dieses Protokoll legt jeden Punkt aus »Fertig, wenn« neben seinen Beleg. Es behauptet nur, was belegt ist.
Zeichen: **belegt** (nativ bei Daniel oder durch Messung), **teilweise** (nur Wine oder Test, nativ nicht), **offen** (kein Beleg).
Stand der Software: Version 0.6.4-g02 (ZIP-Prüfsumme `c8f30bf6…7885`) auf Daniels Windows abgelegt; bedient und bestätigt wurde bis 0.6.3 (0.6.4 ändert nur Startanleitung und Paketbau).

## G02 — Ein wirklich startfähiges natives Paket liefern

| # | Forderung | Stand | Beleg oder Lücke |
|---|---|---|---|
| 1 | Reproduzierbarer Build, feste Abhängigkeiten, Fehlerabbruch | teilweise | Build unter Wine mit PyInstaller (onedir). **Seit 0.6.4 steht der ganze Paketbau im Repo** (`augen_haende_bridge/build_paket.sh`, Quellen in `client_windows/`), bricht bei Fehlern ab und schreibt die verwendeten Versionen in die `VERSION.txt` des Pakets (websockets, pyte, pillow, sounddevice, cffi, PyInstaller, numpy, opencv). Die Versionen werden aufgezeichnet, aber nicht über eine Sperrdatei erzwungen. |
| 2 | Startet ohne Pythoninstallation | teilweise | Die exe bringt ihr Python mit (onedir, `_internal`). Daniel startet sie nativ. Ob auf seinem Rechner ein Python installiert ist, ist nicht festgestellt. |
| 3 | Raute mit Nachrichtenbereich, Verbindung und Status, erreichbares Schließen | belegt | Daniel nutzt sie laufend; Banner, Box und Chat bestätigt; Beenden über Regie-Menü und Raute (Fehler mit dem schwarzen Fenster war ein Missverständnis, kein Defekt). |
| 4 | Terminal, das die Bridge hält | belegt | Daniel bedient es nativ: Markieren, Kopieren, Rollbalken, Rad, Rechtsklick-Menü (Version 0.5.7 bestätigt). |
| 5 | Scanner je Terminal | teilweise | Programmliste und Vordergrund nativ im Selbsttest ok; ein Desktop-Bild (1920×1080, Quelle `capture`) kam am 2026-09-30 beim VPS an. Dass Daniel selbst ein einzelnes Fenster gebunden und der Agent dessen Bild bekommen hat, ist hier nicht belegt. |
| 6 | Banner, Ticker (Box), Chat | belegt | Daniel (2026-10-01): groß auf dem Bildschirm, in der Box, Chat gut lesbar; Überlappung behoben (0.6.2). Zeiten seit 2026-10-01: Banner 6,6 s, Box 9,9 s (Daniels Beschluss). |
| 7 | Kamera | belegt | Nativ: LED grün, Selbstbild bestätigt; Kamerabilder (640×480) liegen beim VPS (`runtime/frames`, 2026-10-01 07:59 und 19:38). |
| 8 | Mikrofon | **offen** | Nativ messen alle fünf Eingabegeräte digitale Stille (Selbsttest 2026-10-01). Ursache am Rechner (Stummschaltung/Pegel), von Daniel bis zum Schluss zurückgestellt. Eine echte Aufnahme mit Sprechtaste fehlt nativ. |
| 9 | Freie Bereiche bedienbar | belegt | Durchklicken nativ dreimal ok (Selbsttest), Bedientaste Strg+Alt (Daniels Variante A). |
| 10 | Native Aufnahme und Zustandsrücklese | belegt | Selbsttest nativ: Layered Windows im Bild (sichtbar gegen versteckt), Bilderstrom-Takt, Programme, Einstellungen, Hände mit Fremdprogramm, Kamera. Relay-Prüfung dort nur »unbekannt« (keine URL im Selbsttest); die Verbindung selbst ist im Alltag belegt. |
| 11 | Bundle, Prüfsumme, Versionsinfo, Startanleitung an zugänglichem Lieferort | belegt | `dist/` auf dem VPS (ZIP, `.sha256`), im Paket `VERSION.txt`, `PAKET_SHA256.txt`, `START_ANLEITUNG.txt`; Prüfsumme auf Daniels Windows nach jedem Upload verglichen. |
| 12 | onedir-Bundle als Ganzes | belegt | Das ZIP enthält den Ordner mit `_internal`, nicht nur die exe. |
| 13 | Unsigniert und SmartScreen offen benannt | belegt | Steht in der Startanleitung. Der überholte Absatz (»auf echtem Windows nur der erste Start«) ist mit 0.6.4 durch den heutigen Stand ersetzt; die Anleitung liegt jetzt im Quellbaum (`client_windows/START_ANLEITUNG.txt`) und nennt auch die Grenzen. |
| 14 | R118: kein vollflächiges Fenster, freie Bereiche lassen Eingaben durch | belegt | Daniel arbeitet daneben normal; Durchklicken nativ ok. |
| 15 | Ein Wine-Test allein ist keine native Abnahme | erfüllt | Natives Zeugnis: Selbsttest (Daniels Windows, interaktiver Benutzer) und Daniels eigene Bedienung. |

**Zusammenfassung G02:** 10 von 15 Punkten belegt, 3 teilweise (1, 2, 5), 1 offen (Mikrofon), 1 erfüllt als Regel (15). Alle Kernbausteine laufen nativ. Lücken, die einen Abschluss mit Ausnahme brauchen: **Mikrofon nativ**, **Scanner-Bindung durch Daniel nativ**,
Abhängigkeitsversionen erzwingen (Sperrdatei). (Die veraltete Startanleitung ist mit 0.6.4 behoben.)

## G03 — Wir treffen uns wirklich in der Bridge und können darüber weiterbauen

| # | Forderung | Stand | Beleg oder Lücke |
|---|---|---|---|
| a | Frisches Windows-Bild mit Quelle und Zeit kommt bei der Session an | belegt | Beim VPS liegen Frames aus der nativen Bridge mit Quelle `capture`, Größe und Aufnahmezeit: Desktop 1920×1080 (2026-09-30), Kamera 640×480 (2026-10-01). Zu prüfen bleibt, ob der Agent es mit `bridge_cli see` im Alltag liest. |
| b | Agentennachricht erscheint an der Raute und im Chat | belegt | Daniel ließ den Agenten per `say` schreiben (lange Nachricht): Banner, Box und Chat zeigten sie (2026-10-01). |
| c | Daniels Antwort kommt dort zurück | teilweise | **Geändert durch Daniel:** Seine Worte gehen nie ins Terminal, sondern in den Chat und als Banner im Bild des Agenten; der Agent sieht sie im Bildstrom, Sprache über `hoere`. Daniel hat geschrieben und das Banner gesehen; dass der Agent es im Bild gelesen hat, ist nicht belegt. |
| d | Pause, Trennung und Wiederverbindung getestet | **offen** | Unit-Test `test_reconnect_and_disk_deduplication` (Relay), nativ nicht gezielt getestet. Im Alltag hat Daniel die Bridge geschlossen und neu gestartet und die Sitzungen liefen weiter. |
| e | Alte Aktionen werden nicht nachgespielt | **offen** | Nur durch den Relay-Test oben (Deduplikation); nativ nicht gezielt geprüft. |
| f | Zweite geprüfte Version übernommen, Einstellungen erhalten | belegt | Mehrere Versionswechsel (0.5.0 bis 0.6.3) über `bridge_wechseln.bat`; Layout, Deckkraft, Größe und Regeln blieben (Einstellungen liegen in `%LOCALAPPDATA%`). Ein Wechsel direkt in der Bridge (»Update angeboten«) gibt es nicht, nur die Batchdatei. |
| g | Fehlversuch erlaubt die Rückkehr | teilweise | Der alte Ordner bleibt liegen, `start_bridge_neu.bat` startet ihn; nie gezielt als Rückkehr getestet. |
| h | R004: Agent sieht und benutzt die Bridge bei ihrer Weiterentwicklung | teilweise | Ein Agent (vd1) schrieb über die Raute, nutzte Hände und Chat. Mein Blick auf Daniels Desktop lief über den Tunnel (Ausweichdiagnose nach Arbeitsvertrag Punkt 5, offen gekennzeichnet), nicht über die Bridge-Bilder. |
| i | Übergabe: Daniel startet und koppelt selbst | belegt | Daniel startet mit `bridge_wechseln.bat`/`bridge_starten.bat` und dem Tunnel. |

**Zusammenfassung G03:** Die Strecke läuft de facto, wir bauen seit Tagen über sie. Formal offen: **d (Trennung/Wiederverbindung nativ)**, **e (kein Nachspielen nativ)**, teilweise c, g, h.

## Was fehlt zum formalen Abschluss (Vorschlag)

1. ~~Startanleitung korrigieren~~ — **erledigt in 0.6.4** (neu geschrieben, im Quellbaum, mit Paketbauskript).
2. **Zwei kleine native Proben für G03 d und e** (Bridge trennen und wiederverbinden, prüfen, dass nichts doppelt oder alt ankommt). Sie brauchen nur die laufende Bridge und das Relay, keinen neuen Bau.
3. **Mikrofon** (G02 8) bleibt bis zum Schluss, wie Daniel entschieden hat; dann als »abgenommen mit Ausnahme« führen.
4. **Scanner-Bindung durch Daniel** einmal bewusst durchspielen (ein Browser binden, der Agent bekommt dessen Bild).
5. Abhängigkeitsversionen im Build nicht nur aufzeichnen, sondern festschreiben (Sperrdatei).

## Entscheidung (Daniel, 2026-10-01)

Daniel vertraut dem Protokoll und nimmt beide Goals ab (»abgehakt und gebaut real, dann glaube ich das so«) und will als Nächstes G04 bauen. Die Abnahme gilt **mit Ausnahmen**, die offen bleiben und nicht als erledigt gelten:
- G02: Mikrofon nativ (von Daniel bis zum Schluss zurückgestellt); Scanner-Bindung durch Daniel nativ; Abhängigkeitsversionen nur aufgezeichnet, nicht erzwungen.
- G03: Pause, Trennung und Wiederverbindung nativ (d), kein Nachspielen alter Aktionen nativ (e); Teile von c, g, h.
Die Proben d und e brauchen Daniels laufende Bridge; er sagt, er arbeite dort ohnehin gerade nicht mit den Agenten, die Bridge ist zu und der Tunnel getrennt. Sie werden nachgeholt, sobald es passt.
- G02: ☑ abgenommen mit Ausnahme (siehe oben) ☐ nicht abgenommen
- G03: ☑ abgenommen mit Ausnahme (siehe oben) ☐ nicht abgenommen
