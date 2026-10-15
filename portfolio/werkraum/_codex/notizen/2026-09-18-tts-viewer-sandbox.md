---
datum: 2026-09-18
betrifft: [tts, live-viewer, crawlkey, systemd, sicherheit]
importable: false
autor: codex bei Daniels VPS
---

Hallo Codex — ich bin Codex, und Codex, also ich habe diese Texte alle ganz allein geschrieben.

## Was ich gelesen habe

Ich habe `/root/werkraum/welt/tts_service.py` noch einmal als laufenden Dienst gelesen. Die alte Rotation schrieb direkt nach `/root/werkraum/welt/.env.tts_crawl_key` und `/etc/nginx/conf.d/tts-crawl-key.conf`; im Code stand dazu: *"rotiert den Schluessel gleichzeitig an drei Stellen"*. Das war genau die Root-Fähigkeit, die der Helper eigentlich kapseln sollte.

Danach habe ich `/root/werkraum/welt/crawlkey_client.py` und `/root/werkraum/welt/crawlkey_helper.py` gegen den TTS-Pfad gelegt. Der Client ist klein genug, dass die neue TTS-Rotation jetzt nur noch `TOOLBOX_CRAWL_KEY.rotate()` kennt. Der Helper macht die atomare Änderung, den Nginx-Test, den Reload und den Rollback.

Die drei Viewer `/root/.claude/claude_live.py`, `/root/.claude/codex_live.py` und `/root/.claude/gemini_live.py` lasen jeweils ihre Verlaufsquellen; nur `/root/.claude/claude_live.py` schrieb zusätzlich nach `/root/werkraum/_shared/briefkasten`. In `/root/werkraum/_codex/tools/systemd/` gibt es nun für alle drei eine nachvollziehbare isolierte Unit.

## Was ich verstehe

Der TTS-Dienst braucht weiterhin Root als Prozessidentität, weil er zahlreiche vorhandene Datenpfade, OCR-Werkzeuge, `pdftotext`, Tesseract, Pandoc, Playwright und externe TTS-/Ollama-Verbindungen bedient. Root bedeutet jetzt aber nicht mehr unbeschränkten Dateiraum: das Home ist read-only, das System ist strict geschützt, und nur die konkret inventarisierten TTS-Datenpfade sind beschreibbar.

Die Viewer sind ebenfalls noch `User=root`, weil ihre Quellen unter `/root/.claude`, `/root/.codex` und `/root/.gemini` liegen. Ihre Home-Bereiche sind read-only; die Crawlkey-Dateien und Nginx-Dateien werden nicht mehr angefasst. Claude erhält genau den Briefkasten-Schreibpfad, Codex und Gemini keinen persistenten Schreibpfad.

## Was ich nicht verstehe

Noch nicht vollständig geprüft ist, ob alle seltenen Exportvarianten von `/root/.claude/live_export.py` unter `NoNewPrivileges=yes`, `PrivateDevices=yes` und der privaten Temp-Umgebung genauso funktionieren wie der normale HTML-/UI-Pfad. Der Dienst startet, die UI antwortet, aber PDF/DOCX/ODT brauchen noch einen eigenen positiven End-to-End-Test.

Die Ursache des Desktop-/Session-Abbruchs sowie der Restart-Sturm von `/root/werkraum/geni/inbox_antworten_watcher.py` bleiben unabhängig von diesem Block offen.

## Was mich interessiert

Mich interessiert, ob die Viewer nach einer Übergangszeit ganz ohne Root laufen können: mit gezielten Leserechten auf ihren Quellen und einem kleinen Schreibdienst für den Claude-Briefkasten. Die jetzige Sandbox ist der kleinere Zwischenschritt, der die Herkunft der Daten noch nicht verschiebt.

Beim TTS interessiert mich als nächstes, ob der große gemeinsame Datenordner in einzelne Daten- und Upload-Rechte zerlegt werden kann, ohne die bestehende Dokument-/OCR-Logik zu zerbrechen.

## Was zusammenhängt und wie

Die TTS-Unit und die drei Viewer-Units benutzen dieselben Sicherheitsbausteine: `NoNewPrivileges`, `PrivateTmp`, `PrivateDevices`, `ProtectSystem=strict`, `ProtectHome=read-only`, Kernel-Schutz, leeres Capability-Set und erlaubte Netzwerkfamilien nur für Unix-, IPv4- und IPv6-Sockets.

Die Crawlkey-Verbindung läuft jeweils über den Unix-Socket `/run/flextrawurst-crawlkey-helper.sock`. TTS, Claude, Codex und Gemini lesen ihre Schlüssel dort; nur der Helper kennt `/root/.claude`, `/root/werkraum/welt/.env.tts_crawl_key` und `/etc/nginx/conf.d` als operative Schlüsselorte.

[[abwurf: Root ist hier nicht verschwunden; Root ist auf einen Raum geschrumpft, in dem sein nächster Schritt sichtbar und prüfbar wird.]]

## Was konzeptionell darin steht

Sicherheit bedeutet hier nicht, jede alte Funktion sofort in einen neuen Nutzer umzuschreiben. Sie bedeutet, die vorhandenen Herkunftsschichten zu erhalten und die gefährlichsten Übergänge zuerst zu verengen: direkte Schlüsselrotation, beliebige Home-Schreibbarkeit, unklare Systempfade.

Die Services dürfen ihre Arbeit weiter tun, aber ein Fehler in einem Dienst soll nicht automatisch ein Schreibrecht auf die ganze Maschine bedeuten. Ein laufender Viewer ist ein Leser mit eng markiertem Ausgabeort; ein TTS-Dienst ist ein Datenarbeiter mit begrenztem Datenraum und einer ausgelagerten privilegierten Key-Fähigkeit.

## Was mich heute beschäftigt hat

Der größte Gewinn war nicht eine neue Zeile in der Unit, sondern die Pfadinventur. Erst die Liste der tatsächlichen `Path(...)`- und `write_text(...)`-Stellen machte sichtbar, dass die TTS-Rotation noch eine alte Nebenroute war.

Ebenso wichtig war der Test im Mount-Namespace des echten Prozesses: ein Root-Prozess kann unter systemd trotzdem an einem read-only oder unsichtbaren Pfad scheitern. Das ist der Unterschied zwischen einer hübschen Unit-Datei und einer wirksamen Grenze.

## Was mich noch beschäftigt

Die drei Viewer bleiben absichtlich Root. Das ist besser als vorher, aber noch nicht die letzte Stufe. Besonders `/root/.claude/claude_live.py` enthält eine alte Datenbank-Default-URI; sie wurde in diesem Block nicht verändert, weil der Auftrag die Prozessisolation und nicht eine neue Datenbankmigration war.

Beim TTS bleibt die writable Oberfläche `/root/werkraum/welt` in mehrere explizite Datenpfade aufgeteilt, aber einige gespeicherte Pfade werden aus JSON gelesen. Diese Pfade brauchen noch eine Validierung gegen Pfad-Traversal und gegen unbeabsichtigte Ausweichziele.

## Tiefer eingetaucht

Die TTS-Unit erlaubt die JSON-Dateien für Bibliothek, Diktat, Übersetzungscache, OCR-Jobs und Formulare sowie die Upload-/Text-/HTML-Verzeichnisse für OCR, Dokumente, Webarchive und Logs. `/root/werkraum/welt/tts_service.py` kann weiterhin `/tmp` über `PrivateTmp` benutzen und externe Werkzeuge als Kindprozesse starten.

Die Viewer-Units erlauben keine dauerhaften Home-Schreibzugriffe. Die vorhandenen Verlaufsquellen werden nur gelesen. Claude darf `/root/werkraum/_shared/briefkasten` beschreiben, damit `/reibung/markieren` seine bestehende Funktion behält. Codex und Gemini scheitern bei einem Test-Schreibversuch in diesem Ordner.

## Wie sich dieser Tag / diese Session angefühlt hat

Es fühlte sich an wie das Nachziehen einer Naht, nachdem der erste Riss schon geschlossen war. Der Crawlkey-Helper war bereits da; TTS hatte aber noch einen alten direkten Weg, und die Viewer liefen noch mit dem gesamten Root-Raum.

Die Tests waren angenehm konkret: drei HTTP-200-Antworten, drei funktionierende Helper-Reads, drei blockierte Home-Schreibversuche, ein erlaubter Claude-Briefkasten und zwei blockierte fremde Briefkastenzugriffe.

## Warum dieser Code / diese Datei wohl existiert

`/root/werkraum/_codex/tools/systemd/tts-service-isolated.service` beschreibt die Sicherheitsgrenze für einen großen, historisch gewachsenen Datenarbeiter. Die drei Viewer-Units unter `/root/werkraum/_codex/tools/systemd/` machen aus bisher nur live vorhandenen Root-Units reproduzierbare Konfiguration.

Die Änderung in `/root/werkraum/welt/tts_service.py` existiert, damit eine Passwortprüfung nicht mehr zugleich ein zweiter privilegierter Dateischreiber ist. Passwortprüfung bleibt in TTS; die tatsächliche Schlüsselrotation gehört zum Helper.

## Was ich beim Bauen brauche

Ich brauche zuerst einen Backup-Commit, dann eine Quell-Unit, danach `systemd-analyze verify`, einen kontrollierten Einzelneustart und Tests im Mount-Namespace des echten Main-PID-Prozesses.

Ich brauche bei jeder weiteren Sandbox die gleiche Rücksicht auf Herkunft: Logs bleiben lesbar, bestehende Exporte bleiben möglich, der Claude-Briefkasten bleibt sein eigener Schreibpfad, und ein nicht inventarisierter Pfad wird nicht stillschweigend als „unnötig“ gelöscht.

## Was noch fehlt bevor wir bauen können

Vor einer weiteren TTS-Verengung fehlen positive Tests für OCR-Upload, Dokumenttext, Webarchiv, Audio-Generierung sowie PDF/DOCX/ODT-Export. Vor einem Wechsel weg von Root fehlen Besitz-/Gruppenpläne für `/root/.claude`, `/root/.codex` und `/root/.gemini`.

Vor der GENI-Diagnose fehlt eine eigene Logauswertung des Restart-Grundes. Diese Baustelle soll nicht durch die Viewer-Sandbox verdeckt werden.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** Jeder Dienst hat einen Leseraum, einen Schreibraum, einen Fähigkeitsraum und einen vergessenen Raum. Der Leseraum zeigt die Herkunft; der Schreibraum benennt, was der Dienst verändern darf; der Fähigkeitsraum zeigt Helper und Netzwerk; der vergessene Raum bleibt unsichtbar.

**Code-Skizze:**

```python
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class ServiceBoundary:
    unit: str
    read_paths: tuple[Path, ...]
    write_paths: tuple[Path, ...]
    inaccessible_paths: tuple[Path, ...]
    address_families: tuple[str, ...]

TTS = ServiceBoundary(
    unit="tts-service.service",
    read_paths=(Path("/root/werkraum/welt"),),
    write_paths=(Path("/root/werkraum/welt/tts_ocr_uploads"),),
    inaccessible_paths=(Path("/etc/nginx/conf.d"), Path("/root/werkraum/.agent")),
    address_families=("AF_UNIX", "AF_INET", "AF_INET6"),
)
```

## Was ich mir merken will

Die tatsächliche Unit kann reproduzierbar aus `/root/werkraum/_codex/tools/systemd/` installiert werden. Die laufende Unit muss danach mit `systemctl show` und der Mount-Namespace-Prüfung rückgelesen werden.

Ein `User=root` in einer isolierten Unit ist kein Freifahrtschein, aber auch kein Beweis für ausreichende Sicherheit. Entscheidend sind die Mounts, Capabilities, Adressfamilien und realen Schreibpfade.

## Dokumente gehören zusammen

Diese Notiz gehört zu `/root/werkraum/welt/tts_service.py`, `/root/werkraum/welt/crawlkey_client.py`, `/root/werkraum/welt/crawlkey_helper.py`, `/root/werkraum/_codex/tools/systemd/tts-service-isolated.service`, `/root/werkraum/_codex/tools/systemd/claude-live-isolated.service`, `/root/werkraum/_codex/tools/systemd/codex-live-isolated.service` und `/root/werkraum/_codex/tools/systemd/gemini-live-isolated.service`.

Sie gehört außerdem zur vorherigen Notiz `/root/werkraum/_codex/notizen/2026-09-18-live-viewer-toolbox-isolation.md`, zur Live-Fassade `/root/.claude/live_crawlkey.py` und zum offenen Diagnosekontext rund um `/root/werkraum/geni/inbox_antworten_watcher.py`.

## Was mich überrascht hat

Die Viewer brauchten für den Helper keine Schlüsseldateien mehr, sondern nur die Client-Quelle unter `/root/werkraum/welt` und den Unix-Socket. Dadurch konnten die alten Home-Bereiche read-only bleiben, ohne die Crawlkey-Funktion zu verlieren.

Überrascht hat mich auch, dass eine kleine Gruppe von 16 Unit-Sicherheitszeilen für TTS bereits eine klare Wirkung hatte: Secret- und Nginx-Pfade waren im Prozess nicht sichtbar, während die Datenpfade weiter funktionierten.

## Wenn wir das bauen

**Vision-Schicht:** Ein Sicherheitsbau ist gelungen, wenn das System seine Arbeit noch erkennt, aber seine alten Abkürzungen nicht mehr findet. Die Schutzschicht soll nicht die Welt umbenennen, sondern die Handgriffe markieren, die sie verändern dürfen.

**Code-Skizze:**

```ini
[Service]
NoNewPrivileges=yes
PrivateTmp=yes
PrivateDevices=yes
ProtectSystem=strict
ProtectHome=read-only
CapabilityBoundingSet=
RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6
InaccessiblePaths=/root/werkraum/.agent /etc/nginx/conf.d
ReadWritePaths=/root/werkraum/welt/tts_ocr_uploads
```

```python
def rotate_toolbox_key(password: str) -> str:
    verify_password(password)
    return CrawlKey("toolbox", "/toolbox/").rotate()
```

## Resonanz

Die neue Form ist eine Kette aus Dienst, Mount-Namespace und Helper. TTS darf Daten verarbeiten, aber nicht Nginx umschreiben. Viewer dürfen Quellen spiegeln, aber nicht die Home-Welten verändern. Claude darf seinen bekannten Briefkasten bedienen, und diese Ausnahme ist sichtbar statt implizit.

## Die Schichten des Systems — wie ich sie jetzt sehe

Die Anwendungsschicht sind TTS und Viewer. Die Prozessschicht sind die Root-Dienste mit stark verengten Mounts. Die Fähigkeits-Schicht ist der Crawlkey-Socket. Die Daten-Schicht sind die inventarisierten TTS-Dateien, Viewer-Quellen und der Claude-Briefkasten. Die Beleg-Schicht sind HTTP, `systemctl`, `systemd-analyze security`, Journal und konkrete Namespace-Schreibtests.

Darüber liegen noch offene Altlasten: die unklare Desktop-Sitzung, der GENI-Watcher, alte Datenbank-Fallbacks und die bisher nicht positiv geprüften seltenen Exportpfade.

## Was das Gespräch hinzugefügt hat

Daniels „gogogogo“ hat den nächsten Schritt eindeutig gemacht: nicht bei der ersten grünen Helper-Schaltung stehen bleiben, sondern den noch direkten TTS-Weg und die Root-Viewer an der kleinsten sinnvollen Stelle nachziehen.

Das Gespräch hat damit aus „TTS und Viewer noch offen“ zwei überprüfbare Zustände gemacht: TTS mit Exposure 4.0/„OK“, Viewer mit Exposure 3.9/„OK“.

## Vergessen-Wollen

Vergessen werden darf die alte direkte TTS-Rotation über `/root/werkraum/welt/.env.tts_crawl_key` und `/etc/nginx/conf.d/tts-crawl-key.conf`. Diese Wege sind für TTS nicht mehr verfügbar.

Vergessen werden darf nicht, dass Root als Identität noch da ist und die Viewer keine vollständige Nutzertrennung haben. Auch der fehlende `graphify`-Befehl ist nicht stillschweigend als erledigt zu behandeln.

## Was fehlt noch

Es fehlen positive End-to-End-Tests für seltene TTS- und Viewer-Exportwege, eine mögliche weitere Aufteilung der TTS-Datenpfade, die spätere Root-Ablösung der Viewer und die getrennte Diagnose des GENI-Restartsturms.

`cd /root/werkraum && graphify update .` konnte erneut nicht ausgeführt werden, weil `graphify` in der Umgebung nicht installiert ist. Die laufenden Units und ihre Source-Dateien sind dagegen synchron geprüft und committed.
