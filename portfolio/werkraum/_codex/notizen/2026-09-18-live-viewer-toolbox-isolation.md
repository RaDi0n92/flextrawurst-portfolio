---
datum: 2026-09-18
betrifft: [welt-api, crawlkey, toolbox, tts, live-viewer, sicherheit]
importable: false
autor: codex bei Daniels VPS
---

Hallo Codex — ich bin Codex, und Codex, also ich habe diese Texte alle ganz allein geschrieben.

## Was ich gelesen habe

Ich habe `/root/werkraum/welt/crawlkey_helper.py` gelesen. Darin steht als Selbstbeschreibung: *"Small root-owned capability for crawl-key rotation."* Das ist der entscheidende Schnitt: Root bleibt dort, wo die Schlüssel und Nginx-Konfiguration tatsächlich geschützt werden müssen; `/root/werkraum/welt/api.py` bekommt nur die schmale Unix-Socket-Fähigkeit.

In `/root/werkraum/welt/crawlkey_client.py` fiel mir der kleine, aber wichtige Satz auf: *"Reads fail closed like the old file reader: no key means no access."* Der Client kennt keine Dateipfade und versucht keine Reparatur, wenn der Helper nicht erreichbar ist. Das macht den Verlust der Berechtigung zu einem sicheren Fehler statt zu einem Anlass für einen neuen Fallback.

Ich habe außerdem `/root/werkraum/welt/api.py`, `/root/werkraum/welt/tts_service.py`, die drei Viewer-Fassaden unter `/root/.claude/live_crawlkey.py`, die Systemd-Units unter `/root/werkraum/_codex/tools/systemd/` und den Live-Zustand auf `root@[SERVER-IP]` geprüft. Die sechs bekannten Stores lesen im echten API-Service-Kontext, die unauthentifizierten Rotationswege liefern 403 beziehungsweise 401, und der alte Klartext `[GESCHWAERZT]` ist aus den beiden TTS/API-Quellen verschwunden.

## Was ich verstehe

Die Änderung ist eine Capability-Grenze, keine bloße Umbenennung von Umgebungsvariablen. Die Welt-API darf die Schlüssel verwenden, aber nicht mehr selbst `/root/.claude` oder `/etc/nginx/conf.d` beschreiben. Der root-eigene Helper kennt eine feste Allowlist aus sechs Stores und zwei Aktionen: lesen und rotieren.

Die TTS-Rotation hat jetzt ihr Secret ausschließlich in `/root/werkraum/.agent/tts-service.env` mit Modus 600. Der TTS-Dienst läuft weiterhin als root, weil sein übriger Schreib- und Subprozess-Fußabdruck noch nicht inventarisiert und eingeschränkt ist. Das ist bewusst ein Zwischenstand, kein behaupteter Vollausbau.

## Was ich nicht verstehe

Warum der Desktop die Sitzung verloren hat, ist weiterhin nur bis zum Logind-/Session-Abbruch rekonstruiert. Ein VPS-Reboot, OOM oder Kernel-Panic war nicht sichtbar. Ebenso ist der Restart-Sturm von `/root/werkraum/geni/inbox_antworten_watcher.py` ein eigenes offenes Problem und wurde in diesem Sicherheitsblock nicht angefasst.

Ich verstehe auch noch nicht vollständig, welche Schreibpfade die drei Live-Viewer und der TTS-Dienst langfristig wirklich brauchen. Ihre Schlüsselzugriffe sind getrennt, aber die Dienste selbst laufen noch mit root-Rechten beziehungsweise mit breiten Projektzugriffen.

## Was mich interessiert

Mich interessiert als nächstes die kleinstmögliche weitere Grenze für `/root/werkraum/welt/tts_service.py`: konkrete Dateien, temporäre Verzeichnisse, Subprozesse und Netzwerkziele statt pauschaler Root-Freiheit.

Ebenso interessiert mich, ob die Viewer-Fassaden nach einer Pfadinventur als eigene unprivilegierte Nutzer laufen können, ohne ihre vorhandenen Export- und Briefkastenpfade zu beschädigen.

## Was zusammenhängt und wie

`/root/werkraum/welt/api.py` liest seine Crawlkeys über `/root/werkraum/welt/crawlkey_client.py`; dieser spricht mit `/root/werkraum/welt/crawlkey_helper.py`; der Helper allein darf die sechs fest verdrahteten Speicherorte bedienen. Für die drei Nginx-gebundenen Stores gehört außerdem `nginx -t` plus Reload in dieselbe atomare Rotationshandlung.

Die Viewer unter `/root/.claude/live_crawlkey.py` hängen an derselben Client-Grenze. `/root/werkraum/welt/tts_service.py` und der Toolbox-Teil von `/root/werkraum/welt/api.py` teilen sich den Store `toolbox`, aber nicht mehr ein im Python-Quelltext eingebettetes Passwort.

[[abwurf: Eine Sicherheitsgrenze ist erst echt, wenn der erlaubte Weg klein genug ist, dass sein Scheitern ein sicherer Zustand bleibt.]]

## Was konzeptionell darin steht

Die Schlüssel sind keine gewöhnlichen Konfigurationswerte. Sie sind Zugangsfähigkeiten zu laufenden Oberflächen. Deshalb muss ihre Rotation an einer Stelle stattfinden, die den Schutzbereich kennt, während die Dienste nur die Fähigkeit zum Lesen oder zur ausdrücklich vorgesehenen Rotation erhalten.

Die Systemarchitektur bekommt dadurch eine sichtbare Schichtung: Anwendung, unprivilegierter Client, begrenzter root-eigener Helper, geschützte Stores und Nginx. Keine Schicht soll die nächste heimlich ersetzen.

## Was mich heute beschäftigt hat

Mich hat beschäftigt, wie leicht ein funktionierender Fallback die eigentliche Sicherheitsfrage verdeckt. Die API lief, solange sie direkt auf Dateien und Nginx zugreifen konnte; erst die Trennung machte sichtbar, welche Rechte sie tatsächlich nicht besitzen sollte.

Der falsche erste Read-Test als nackter `flex_api` war nützlich: Er zeigte nicht einen defekten Helper, sondern den Unterschied zwischen Benutzeridentität und dem im Systemd-Dienst gesetzten `SupplementaryGroups=flextrawurst-api`. Solche Tests müssen den echten Dienstkontext nachbilden.

## Was mich noch beschäftigt

Offen bleibt die Ursachenanalyse des Desktop-Absturzes. Außerdem muss der Restart-Sturm von `/root/werkraum/geni/inbox_antworten_watcher.py` separat entschärft werden, ohne `/root/werkraum/geni/` als laufendes System unautorisiert umzubauen.

Für die nächste Sicherheitsrunde brauche ich eine belastbare Schreibinventur von `/root/werkraum/welt/tts_service.py`, `/root/.claude/claude_live.py`, `/root/.claude/codex_live.py`, `/root/.claude/gemini_live.py` und `/root/.claude/live_export.py`.

## Tiefer eingetaucht

Die sechs Stores sind `claudelive`, `codexlive`, `geminilive`, `toolbox`, `crawlschluessel` und `archkey`. Die ersten vier sind Nginx- beziehungsweise TTS-gebunden; die letzten beiden sind JSON-Zustände unter `/root/.claude`. Der Helper lässt keine vom Client gelieferten Pfade zu.

Die Rotation schreibt atomar, testet die Nginx-Konfiguration und rollt Schlüssel und Konfiguration zurück, wenn Test oder Reload scheitern. Der Socket `/run/flextrawurst-crawlkey-helper.sock` gehört `root:flextrawurst-api` und hat Modus 660. Der echte API-Service läuft als `flex_api` mit dieser Supplementary Group.

## Wie sich dieser Tag / diese Session angefühlt hat

Erst chaotisch: Desktop weg, Terminals weg, mehrere Arbeitsstränge abgerissen. Dann wurde es wieder präzise, als aus dem allgemeinen Abfuck eine Reihe überprüfbarer Grenzen wurde: Prozessidentität, Socket-Gruppe, Pfad-Allowlist, HTTP-Status und Secret-Modus.

Es war eine Session, in der ein unspektakulärer `False`-Test mehr Wahrheit enthielt als ein grüner Dienststatus. Er zwang dazu, den Unterschied zwischen „läuft“ und „kann im echten Kontext die vorgesehene Fähigkeit benutzen“ ernst zu nehmen.

## Warum dieser Code / diese Datei wohl existiert

`/root/werkraum/welt/crawlkey_helper.py` existiert, damit privilegierte Schlüsseloperationen nicht in einer großen API mit hunderten Routen verstreut bleiben. `/root/werkraum/welt/crawlkey_client.py` existiert, damit die unprivilegierte Seite diese Grenze klein und lesbar benutzt.

`/root/werkraum/.agent/tts-service.env` existiert als Secret-Träger außerhalb des Quelltexts. Die Systemd-Unit `/root/werkraum/_codex/tools/systemd/tts-service-isolated.service` hält diese Herkunft sichtbar, ohne vorzeitig eine ungetestete Voll-Sandbox zu behaupten.

## Was ich beim Bauen brauche

Ich brauche vor jeder weiteren Änderung einen gezielten Backup-Commit in `/root/werkraum`, danach eine einzelne kleine Änderung, einen Live-Test im echten Benutzer- und Gruppenkontext und eine Rücklese aus Prozess, Socket, HTTP und Journal.

Ich brauche außerdem die Provenienz der alten Viewer-Schreibpfade sichtbar zu halten. Bestehende Export-, Briefkasten- und Temp-Mechaniken sind keine freie Aufräumfläche.

## Was noch fehlt bevor wir bauen können

Vor einer Viewer- oder TTS-Sandbox fehlen ein Schreibpfad-Inventar, eine Liste der benötigten Netzwerkziele und ein Test, der die vorhandenen Exporte sowie die Crawlkey-Fassade abdeckt. Vor dem Anfassen des GENI-Watchers fehlt eine getrennte Diagnose, warum sein Service seit langer Zeit in kurzen Abständen neu startet.

Die fehlende `graphify`-CLI muss außerdem als Umgebungsgrenze dokumentiert bleiben: `cd /root/werkraum && graphify update .` endete mit `command not found`, deshalb konnte der Wissensgraph nach den Codeänderungen nicht aktualisiert werden.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** Ein Schlüsselstore ist eine benannte, beobachtbare Fähigkeit mit klarer Herkunft, nicht bloß eine Datei. Er hat einen Besitzer, eine erlaubte Operation, einen geschützten Zielraum und einen sicheren Fehlerzustand. Die Anwendung sieht nur die Fähigkeit; der Helper kennt die materielle Form.

**Code-Skizze:**

```python
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

Kind = Literal["nginx", "tts_nginx", "json"]
Action = Literal["read", "rotate"]

@dataclass(frozen=True)
class KeyStore:
    name: str
    kind: Kind
    key_path: Path
    nginx_path: Path | None = None

KEY_STORES: dict[str, KeyStore]
# request: {"action": Action, "system": str}
# response: {"ok": bool, "key": str} | {"ok": False, "error": str}
```

## Was ich mir merken will

„Aktiv und enabled“ reicht nicht als Sicherheitsbeleg. Die Fähigkeit muss im echten Dienstkontext funktionieren, und ein Kontext ohne Supplementary Group muss sichtbar scheitern.

Ich will außerdem festhalten, dass sechs Stores geschützt wurden, nicht fünf. Die Toolbox gehört in dieselbe Grenze wie die drei Live-Viewer und die beiden JSON-Zustände, auch wenn sie aus einem anderen Dienst kommt.

## Dokumente gehören zusammen

Diese Notiz gehört zu `/root/werkraum/welt/crawlkey_helper.py`, `/root/werkraum/welt/crawlkey_client.py`, `/root/werkraum/welt/api.py`, `/root/werkraum/welt/tts_service.py`, `/root/.claude/live_crawlkey.py`, `/root/werkraum/.agent/tts-service.env` und den Units `/root/werkraum/_codex/tools/systemd/flextrawurst-crawlkey-helper.service` sowie `/root/werkraum/_codex/tools/systemd/tts-service-isolated.service`.

Sie gehört außerdem zu den früheren Sicherheitsnotizen zur Welt-API-Isolation und zum noch offenen Desktop-/GENI-Diagnosestrang. Die Import-Grundrisse unter `/root/werkraum/_codex/_import_claude_grundriss/` bleiben Referenz und sind keine eigene Erinnerung.

## Was mich überrascht hat

Der Helper war live und korrekt gruppengesichert, aber ein Test ohne die Systemd-Zusatzgruppe sah zunächst wie ein Funktionsausfall aus. Das war eine gute Erinnerung daran, dass Unix-Rechte nicht nur aus `User=` bestehen.

Überrascht hat mich auch, dass der alte Klartext nicht nur in der API, sondern ebenfalls im TTS-Dienst entfernt werden musste. Eine einzelne vergessene Nebenroute hätte die neue Grenze semantisch wieder entwertet.

## Wenn wir das bauen

**Vision-Schicht:** Jede privilegierte Fähigkeit bekommt eine schmale Tür mit sichtbarer Herkunft. Die Tür darf nur die Handlung erlauben, für die sie gebaut wurde; der Raum dahinter bleibt für die Anwendung unsichtbar. Rotation ist ein Ereignis mit Rückkehrmöglichkeit, kein beliebiges Dateischreiben.

**Code-Skizze:**

```python
def read_key(system: str) -> str:
    return CrawlKey(system, url_prefix="/").read()

def rotate_key(system: str) -> str:
    # nur der Helper darf rotieren; Client liefert keine Pfade
    return CrawlKey(system, url_prefix="/").rotate()

def rotate_nginx_store(spec: KeyStore) -> str:
    old = snapshot(spec)
    new = secrets.token_urlsafe(24)
    atomic_write_pair(spec, new)
    try:
        run_nginx_test_and_reload()
    except Exception:
        restore(old)
        run_nginx_test_and_reload()
        raise
    return new
```

## Resonanz

Die gute Form dieser Änderung ist nicht „mehr Sicherheit“ als abstraktes Versprechen, sondern eine kleine beobachtbare Kette: API-Prozess ohne Dateirechte, Socket mit genau einer Gruppe, Helper mit fixer Allowlist, atomare Rotation, Nginx-Test, Rollback. Jede Stufe kann einzeln geprüft werden.

## Die Schichten des Systems — wie ich sie jetzt sehe

Oben liegen HTTP-Routen und Viewer. Darunter liegen die Client-Module, die nur eine Socket-Fähigkeit ansprechen. Darunter sitzt der root-eigene Helper mit der Store-Allowlist. Daneben liegen die geschützten Schlüsseldateien und Nginx-Konfigurationen. Quer dazu liegen Systemd als Identitäts- und Gruppenrahmen sowie Logs und Tests als Belegschicht.

Außerhalb dieser Schichtung liegen die noch nicht gelösten Themen: Desktop-Sitzungsverlust, GENI-Watcher-Restartsturm, breite Root-Rechte der Viewer und der TTS-Schreibfußabdruck.

## Was das Gespräch hinzugefügt hat

Daniels wiederholtes „gogogo“ bedeutete hier: den abgerissenen Faden nicht erneut in eine Rückfrage verwandeln, sondern den letzten überprüfbaren Sicherheitsstand wieder aufnehmen. Der relevante Anschluss war nicht die Desktop-Ursache, sondern der bereits laufende Block um `altra/luna` beziehungsweise Crawlkey, Toolbox und TTS.

Die Unterhaltung hat damit einen klaren Übergabepunkt geschaffen: Die Schlüsselzugriffe sind live hinter einer Grenze; die nächste Arbeit beginnt bei der Inventur der verbleibenden Prozessrechte.

## Vergessen-Wollen

Vergessen werden darf die falsche Vorstellung, dass ein grüner Service automatisch beweist, dass seine Berechtigungen stimmen. Vergessen werden darf auch die alte Klartextannahme `[GESCHWAERZT]`; sie gehört nicht mehr in Quelltext, Tests oder Übergaben.

Nicht vergessen werden darf dagegen, dass die Viewer und TTS noch root beziehungsweise breit berechtigt laufen. Diese Unvollständigkeit ist eine Sicherheitsnotiz, kein Makel, den man durch Formulierung verschwinden lässt.

## Was fehlt noch

Es fehlen die nächste Backup-gesicherte Runde zur TTS-/Viewer-Rechteinventur, eine getrennte Behandlung des GENI-Restartsturms und eine Erklärung des Desktop-Session-Abbruchs aus den vorhandenen Logs. Die `graphify`-Aktualisierung fehlt, weil das Kommando in der Umgebung nicht installiert ist.

Der aktuelle Live-Sicherheitsstand ist ansonsten geprüft: `/root/werkraum/welt/api.py` antwortet auf `/health` mit 200, `/root/werkraum/welt/tts_service.py` auf `/` mit 200, die Schutzwege liefern ohne Authentifizierung 401 beziehungsweise 403, und die relevanten Dienste sind aktiv und enabled.
