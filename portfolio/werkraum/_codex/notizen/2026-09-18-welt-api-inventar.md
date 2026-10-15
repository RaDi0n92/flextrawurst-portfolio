---
datum: 2026-09-18
betrifft: [welt-api, api-isolation, db-runtime, sicherheit]
importable: false
autor: codex bei Daniels VPS
---

Hallo Codex — ich bin Codex, und Codex, also ich habe diese Texte alle ganz allein geschrieben.

## Was ich gelesen habe

Ich habe die Sicherheitsfortsetzung aus den vorherigen Notizen wieder aufgenommen. Die kleinen Körper `/root/werkraum/welt/splitter_daemon.py` und `/root/werkraum/welt/bruecke.py` sind bereits isoliert; die nächste offene Kante war `/root/werkraum/welt/api.py`.

Beim Lesen dieser Datei fiel sofort die andere Größenordnung auf: 16.007 Zeilen, 306 Routen, viele DB-Schreibpfade und mehrere eingebaute Router. Sie ist nicht einfach ein Daemon, der mit einer Tabelle spricht, sondern ein gewachsener Gateway-Körper.

Besonders deutlich wurden die Übergänge: Uploads, Codewesen-Vaults, `/root/.claude/`, Nginx-Crawl-Schlüssel, Flarum/MySQL, Anthropic und lokale Diagnoseprozesse. Der Satz, der blieb, war: *Eine `User=`-Zeile ist hier noch keine Isolation.*

## Was ich verstehe

Die API muss funktional bleiben, aber ihre bisherigen Root-Rechte dürfen nicht als unbemerkte Voraussetzung in eine neue Unit rutschen. Der erste tragfähige Schritt ist deshalb ein Runtime-Kontrakt ohne eingebettete DB-Zugangsdaten.

`FLEXTRAWURST_DB_URI` ist jetzt die einzige echte DB-Quelle für die API-Importkette. Fehlt sie, existiert kein Passwort-Fallback; ein echter Verbindungsversuch bekommt nur einen absichtlich ungültigen DSN.

Die eigentliche Unix-Isolation braucht danach eine Schichtung: Gateway-User für API und Datenbank, separater kleiner Dienst für privilegierte Crawl-/Nginx-Rotation und einzeln erlaubte Schreibpfade.

## Was ich nicht verstehe

Aus der aktuellen Codex-Shell ist der Host-systemd-Kanal nicht erreichbar. PID 1 ist hier s6; `systemctl` kann deshalb keine Aussage über die Host-Units machen. Ein SSH-Versuch zu `root@127.0.0.1` scheiterte an fehlendem Public-Key.

Ich weiß daher aus dieser Fortsetzung nicht, ob die laufende Host-Unit nach dem Desktop-Abbruch exakt noch mit demselben Drop-in läuft. Die letzte hostseitige Evidenz vor dieser Shell zeigte `welt-api.service` aktiv und `/health` mit 200.

Die genaue Grant-Matrix der API ist ebenfalls noch keine fertige Wahrheit. Die statische Vorinventur findet 101 FROM-Quellen, 49 Insert-, 38 Update- und 17 Delete-Ziele; Spalten, Trigger und seltene Adminpfade müssen noch routeweise bestätigt werden.

## Was mich interessiert

Mich interessiert, welche privilegierten Funktionen wirklich im großen Gateway bleiben müssen und welche nur aus Gewohnheit dort wohnen. Besonders die Crawl-/Nginx-Rotation sieht nach einem kleinen eigenen Körper aus, der nicht die Rechte der gesamten Welt-API braucht.

Mich interessiert außerdem, ob die Upload- und Wesen-Vault-Schreibpfade als eigene klare Ausgabegrenzen modelliert werden können, ohne Herkunft oder Bedienlogik zu verlieren.

## Was zusammenhängt und wie

Die DB-URI-Härtung verbindet `/root/werkraum/welt/api.py`, `/root/werkraum/welt/auth.py`, `/root/werkraum/welt/service_token_verifier.py` und die eingebundenen Router über `/root/werkraum/welt/db_runtime.py`.

Die Unix-Isolation verbindet diese Runtime-Schicht mit den noch offenen Dateipfaden: `/root/werkraum/uploads/`, `/root/werkraum/codewesen/`, `/root/.claude/` und der Nginx-Konfiguration. Ein DB-User allein löst diese Herkunft nicht.

## Was konzeptionell darin steht

Die API ist ein Tor zwischen öffentlicher Welt, menschlicher Bedienung, Wesen-Innenräumen und historischen Archiven. Sicherheit darf dieses Tor nicht unsichtbar verengen; sie muss sichtbar machen, welcher Teil welche Hand bekommt.

Das bedeutet: ein großer Gateway-Körper darf nicht automatisch ein großer Systemkörper sein. Seine Rechte müssen in Daten, Dateien, Netz und Prozesssicht getrennt lesbar werden.

## Was mich heute beschäftigt hat

Mich hat beschäftigt, dass die gefährlichste Änderung hier sehr klein aussehen würde. `User=flex_api` liest sich wie Fortschritt, könnte aber Uploads, Schlüsselrotation und Vault-Schreiben gleichzeitig zerbrechen oder danach zu breite ACLs erzwingen.

Die bessere Bewegung war deshalb erst Inventar, dann ein kleiner echter Schnitt: keine eingebettete DB-Passwort-URI mehr.

## Was mich noch beschäftigt

Offen bleibt die richtige Form für `flex_keyctl`. Der Dienst darf nicht zu einem neuen Root-Allzweckschlüssel werden. Seine Schnittstelle muss eng, lokal und admin-geprüft sein.

Offen bleibt auch, wie die seltenen Rotationspfade getestet werden, wenn die sichtbare Host-Session gerade nicht als Träger für systemd dienen kann.

## Tiefer eingetaucht

Die API importiert neben der Hauptdatei Router für Denkstream, Events, DOM-Ereignisse, Fokus-Ereignisse, Erlebnis, Beobachtung, RAG und Reibungsgewebe. Dazu kommen dynamische Imports wie der Cyberling-Pfad. Ein Schutz, der nur die erste Datei betrachtet, wäre deshalb eine Scheinsicherheit.

Der Crawl-Schlüsselpfad schreibt Zustände unter `/root/.claude/` und bindet einen Client ein, der Nginx-Konfiguration und Reload-Grenzen kennt. Genau dort endet die Berechtigung einer normalen API-Rolle.

## Wie sich dieser Tag / diese Session angefühlt hat

Erst wie ein sauberer nächster Schritt, dann wie eine Tür in einen viel größeren Maschinenraum. Die Entdeckung war nicht entmutigend, eher nützlich: Der Körper hat seine wirkliche Größe gezeigt.

Der kleine DB-Schnitt fühlt sich deshalb richtig an, weil er nichts vortäuscht. Er macht eine Herkunft weg, die nicht mehr in den Quelltext gehört, und lässt die größere Architekturfrage sichtbar.

## Warum dieser Code / diese Datei wohl existiert

`/root/werkraum/welt/api.py` existiert, weil die Welt über lange Zeit neue Oberflächen bekommen hat und die API sie zusammenhält. Die vielen Routen sind Geschichte, nicht bloß Unordnung.

`/root/werkraum/welt/db_runtime.py` existiert jetzt als schmale Unterkante: Der Prozess muss seine DB-Verbindung von außen erhalten. Die Unit oder der Credential-Kanal trägt die Umgebung; der Quelltext trägt kein Betriebsgeheimnis.

## Was ich beim Bauen brauche

Ich brauche eine echte hostseitige Rücklese von `welt-api.service`, den aktiven Drop-ins, dem Arbeitsverzeichnis, den Credential-Pfaden und den aktuellen Prozessrechten.

Ich brauche danach eine routeweise Liste der Datei-Schreibpfade und eine DB-Grant-Matrix, bevor `flex_api` live wird. Die bisherige statische SQL-Liste ist nur der Anfang.

## Was noch fehlt bevor wir bauen können

Es fehlt der erreichbare systemd-Kanal für Shadow-Start und zielgenauen Neustart. Es fehlt außerdem die Entscheidung, ob Crawl-/Nginx-Rotation zuerst in einen eigenen Dienst wandert oder temporär als getrennte, nicht öffentlich erreichbare Nebenfunktion bestehen bleibt.

Es fehlt kein weiterer Grund, die DB-Passwort-Fallbacks zu entfernen: Dieser Teil ist umgesetzt und getestet.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** Ein API-Gateway steht in der Mitte, aber seine Hände sind benannt. Datenbank, Upload-Ausgabe, Wesen-Ausgabe und privilegierte Schlüsselrotation sind vier verschiedene Berührungen. Jede darf sichtbar bleiben, ohne die anderen zu erben.

**Code-Skizze:**

```python
class RuntimeConfig(TypedDict):
    db_uri: str
    jwt_secret: str
    write_roots: tuple[Path, ...]

class PrivilegedRotationRequest(TypedDict):
    operation: Literal["rotate-crawlschluessel", "rotate-livecrawl"]
    actor_id: str
    request_id: str

def require_db_uri() -> str:
    value = os.environ.get("FLEXTRAWURST_DB_URI")
    if not value:
        raise RuntimeError("DB runtime configuration missing")
    return value
```

## Was ich mir merken will

Die API-Isolation beginnt nicht bei `User=`. Sie beginnt bei der Frage, welche Herkunft ein Prozess überhaupt tragen muss.

Die erste echte Grenze ist jetzt im Git sichtbar: `/root/werkraum/welt/db_runtime.py` ist der einzige gemeinsame Runtime-Kontrakt der API-Importkette; die alte Passwort-URI ist dort nicht mehr vorhanden.

## Dokumente gehören zusammen

Diese Session gehört zu `/root/werkraum/_codex/berichte/2026-09-18-welt-api-isolation-inventar.md`, `/root/werkraum/_codex/berichte/2026-09-18-welt-bruecke-isolation-live.md`, `/root/werkraum/_codex/notizen/2026-09-18-welt-bruecke-isolation.md` und den Units unter `/root/werkraum/_codex/tools/systemd/`.

Die laufende Sicherheitsgeschichte liegt außerdem in `/root/werkraum/_codex/notizen/2026-09-18-desktop-abbruch-sicherheitsresume.md` und `/root/werkraum/_codex/notizen/2026-09-18-dienstschluessel-live.md`.

## Was mich überrascht hat

Überrascht hat mich weniger die Anzahl der Tabellen als die Mischung der Grenzen in einem Prozess: öffentliche HTTP-Lektüre, Uploads, direkte Vault-Schreibungen, MySQL/Flarum und Nginx-Rotation sitzen nebeneinander.

Überrascht hat mich auch, dass der vorhandene Testkörper ohne DB-Umgebung importiert wird. Der Runtime-Kontrakt musste deshalb fail-closed bleiben, ohne synthetische Sicherheitsprüfungen durch Importfehler zu verdecken.

## Wenn wir das bauen

**Vision-Schicht:** Wir bauen keinen neuen Käfig um die ganze Welt. Wir geben jedem Übergang seine eigene schmale Tür. Der Gateway darf Welt handeln; der Schlüsselwächter darf Schlüssel drehen; keiner bekommt aus Bequemlichkeit das Haus.

**Code-Skizze:**

```ini
[Service]
User=flex_api
DynamicUser=yes
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=/root/werkraum/uploads /root/werkraum/codewesen
RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6

# Separater Dienst, kein API-Root:
flex-keyctl.socket -> flex-keyctl.service
```

Vor dem Aktivieren kommen Shadow-Start, Negativtests für private Daten, Upload-/Admin-/WebSocket-Tests und eine Rücklese aus DB, Prozess und Dateien.

## Resonanz

[[abwurf: Eine `User=`-Zeile ist hier noch keine Isolation.]]

Die API-Härtung ist klein genug, um sicher zu sein, und ehrlich genug, um die große offene Kante nicht zu verdecken.

## Die Schichten des Systems — wie ich sie jetzt sehe

1. Host-/Session-Schicht: Desktop und aktuelle Codex-Shell sind nicht dasselbe wie der VPS-systemd-Host.
2. Service-Schicht: Splitter und Brücke sind eigene Unix-/DB-Körper; die API ist noch der große Root-Gateway-Körper.
3. Runtime-Schicht: `/root/werkraum/welt/db_runtime.py` erzwingt eine äußere DB-Konfiguration ohne Quelltextpasswort.
4. Daten-/Dateischicht: PostgreSQL, Uploads, Wesen-Vaults, Werkraum-Archive und Crawl-/Nginx-Schlüssel haben unterschiedliche Eigentümerlogiken.

## Was das Gespräch hinzugefügt hat

Das erneute „gogogog“ hat den nächsten Schnitt nicht in eine pauschale Unit-Änderung verwandelt. Es hat die API bis zur echten Grenze verfolgt und daraus einen kleinen, bereits getesteten Sicherheitsfix gemacht.

## Vergessen-Wollen

Ich will vergessen, dass ein großer Prozess durch seine Erreichbarkeit automatisch dieselbe Herkunft wie seine Dateien besitzen müsse. Root ist kein fachlicher Vertrag.

## Was fehlt noch

Es fehlen die hostseitige systemd-Rücklese, die privilegierte Rotationsabtrennung, die vollständige API-DB-Grant-Matrix und der kontrollierte Live-Test von `/root/werkraum/welt/api.py` unter `flex_api`.

`graphify update .` fehlt als aktualisierte Graphspur, weil die CLI in dieser Shell nicht installiert ist. Das ist dokumentiert und kein fachlicher Testfehler.

