---
datum: 2026-09-18
betrifft: [welt-api, crawlkey, nginx, sicherheit, altra, luna]
importable: false
autor: codex bei Daniels VPS
---

Hallo Codex — ich bin Codex, und Codex, also ich habe diese Texte alle ganz allein geschrieben.

## Was ich gelesen habe

Ich bin nach der Welt-API-Isolation in den verbliebenen Crawlkey-Pfad gegangen. In `/root/werkraum/welt/api.py` stand noch der direkte Import des alten Root-Moduls und die Konstruktion von `CrawlKey` mit Dateien unter `/root/.claude` und `/etc/nginx/conf.d`.

Das alte Modul `/root/.claude/live_crawlkey.py` war sehr klein, aber seine Wirkung war groß: *„rotate() schreibt sowohl die Anzeige-Datei als auch die nginx-map-Datei und laedt nginx neu.“* Genau dort lag die letzte Root-Fähigkeit der API.

Ich habe außerdem die beiden API-eigenen Zustandsdateien gelesen: `/root/.claude/.crawlschluessel_state.json` und `/root/.claude/.archaeologie_crawlschluessel_state.json`. Sie waren kein Nginx-Pfad, aber ebenfalls ein Schreibzugriff aus dem API-Prozess heraus. Deshalb wurden sie in denselben Helper-Vertrag aufgenommen.

## Was ich verstehe

Die API muss die Schlüssel lesen und eine Rotation anfordern können, aber sie muss weder Schlüsseldateien noch Nginx-Konfiguration selbst besitzen. Der neue Unix-Socket ist die schmale Naht: fünf feste Namen, zwei Aktionen, keine freien Pfade.

Der Root-Helper ist kein allgemeiner Shell- oder Dateidienst. Er kennt die fünf erlaubten Speicherorte fest im Code, schreibt atomar, prüft Nginx und lädt nur `nginx` neu. Der API-Prozess hat weiterhin `ProtectHome=read-only` und `ProtectSystem=strict`.

## Was ich nicht verstehe

Die drei separaten Live-Prozesse unter `/root/.claude` importieren weiterhin ihr altes `live_crawlkey.py`. Dieser Schnitt härtet den Weg aus der Welt-API; er behauptet nicht, alle historischen Live-Prozesse bereits auf denselben Helper umgestellt zu haben.

Auch der Toolbox-Crawlkey auf Port 8035 bleibt ein eigener Pfad mit eigener Rotation. Das ist bewusst nicht in den fünf Helper-Stores versteckt worden.

## Was mich interessiert

Mich interessiert, ob der Helper später als ein allgemeines Muster für wenige privilegierte Fähigkeiten dienen kann: jeweils ein fester Vertrag, ein fester Socket, ein fester Besitzer. Nicht ein Root-Prozess, der hinter einem hübschen Namen wieder alles kann.

## Was zusammenhängt und wie

`/root/werkraum/welt/crawlkey_client.py` hält die API unprivilegiert. `/root/werkraum/welt/crawlkey_helper.py` hält die Root-Fähigkeit klein. `/root/werkraum/_codex/tools/systemd/flextrawurst-crawlkey-helper.service` begrenzt den Prozess zusätzlich auf `CAP_CHOWN`, damit er nur die Socket-Gruppe setzen kann.

`/root/werkraum/_codex/tools/systemd/welt-api-isolated.service` gibt dem API-Prozess nur die feste Gruppe `flextrawurst-api`. Dadurch kann er den Socket lesen, aber nicht `/root/.claude` oder `/etc/nginx/conf.d` beschreiben.

## Was konzeptionell darin steht

Eine privilegierte Fähigkeit soll wie ein kleines Tor aussehen, nicht wie ein zweiter Eingang zum ganzen Haus. Der Schlüssel bleibt Daniels Bedienlogik und die Oberfläche bleibt funktionsgleich; nur der Besitz der Systemwirkung wandert an einen klar markierten Ort.

## Was mich heute beschäftigt hat

Mich hat der erste fehlgeschlagene Helper-Start beschäftigt. Das leere Capability-Set war als Grenze richtig, verhinderte aber auch das Setzen der Socket-Gruppe. Die Lösung war nicht, Root wieder alles zu geben, sondern genau `CAP_CHOWN` zu erlauben und sonst nichts.

## Was mich noch beschäftigt

Ein Socket mit Gruppe ist eine gute Grenze, aber der Helper ist weiterhin ein Root-Dienst. Seine fünf Aktionen müssen deshalb stabil klein bleiben. Jede spätere Erweiterung braucht denselben Beweis: fester Name, fester Pfad, fester Zweck.

## Tiefer eingetaucht

Die Rotation schreibt zuerst temporär und ersetzt dann atomar. Bei Fehlern werden die alte Schlüsseldatei und die alte Nginx-Datei zurückgesetzt; danach wird Nginx mit dem alten Stand erneut getestet und geladen. Diese zweite Wiederherstellung war der letzte kleine Fix in dieser Session.

Die Live-Belege sind stärker als ein Syntaxcheck: `flex_api` konnte alle fünf Stores über den Socket lesen; die öffentliche Validierung gab für den echten Wert `ok: true` und für einen falschen Wert `ok: false`; ein Prozess mit API-Sandbox konnte beide direkten Schreibziele nicht beschreiben.

## Wie sich dieser Tag / diese Session angefühlt hat

Es war ein guter kleiner Schnitt nach dem großen API-Schritt. Der Pfad war zunächst nur eine Importzeile, aber dahinter lagen drei Nginx-Maps, zwei Zustandsdateien und ein Reload als Root. Als der Socket unter `root:flextrawurst-api` sauber stand, wurde die Grenze konkret.

## Warum dieser Code / diese Datei wohl existiert

`/root/werkraum/welt/crawlkey_client.py` existiert als unprivilegierte Sicht auf eine begrenzte Fähigkeit. `/root/werkraum/welt/crawlkey_helper.py` existiert, weil Nginx-Konfiguration und Root-Schlüssel nicht in den HTTP-Prozess gehören. Die beiden Systemd-Dateien existieren, damit diese Aufteilung reproduzierbar startet und nicht nur als manuelle Servermagie lebt.

## Was ich beim Bauen brauche

Ich brauche die alte Bedienlogik als unveränderte Provenienz: dieselben fünf Schlüssel, dieselben URL-Präfixe, dieselbe Admin-Schranke. Neu darf nur der Besitz der Rotation sein.

## Was noch fehlt bevor wir bauen können

Für weitere privilegierte Pfade fehlt zuerst eine vollständige Liste ihrer erlaubten Aktionen. Besonders der Toolbox-Helper, die historischen Live-Prozesse und die übrigen `subprocess`-Aufrufe in `/root/werkraum/welt/api.py` brauchen eigene Entscheidungen.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** Jeder Schlüssel ist ein benannter Gegenstand mit einer einzigen Herkunft und einer einzigen Bewegung: lesen oder rotieren. Der Weg vom Admin-Tab bis zur Nginx-Map bleibt sichtbar und auditierbar.

**Code-Skizze:**

```python
KEY_STORES = {
    "claudelive": {"kind": "nginx", "key_path": Path(...), "nginx_path": Path(...)},
    "codexlive": {"kind": "nginx", "key_path": Path(...), "nginx_path": Path(...)},
    "geminilive": {"kind": "nginx", "key_path": Path(...), "nginx_path": Path(...)},
    "crawlschluessel": {"kind": "json", "key_path": Path(...)},
    "archkey": {"kind": "json", "key_path": Path(...)},
}

request = {"action": "read", "system": "claudelive"}
response = {"ok": True, "key": "..."}
```

## Was ich mir merken will

`CAP_CHOWN` ist hier kein allgemeines Vertrauen, sondern nur die technische Voraussetzung für `root:flextrawurst-api` auf der Socket-Datei. Die API selbst bleibt capability-frei.

## Dokumente gehören zusammen

Zusammengehören `/root/werkraum/welt/api.py`, `/root/werkraum/welt/crawlkey_client.py`, `/root/werkraum/welt/crawlkey_helper.py`, `/root/werkraum/_codex/tools/systemd/flextrawurst-crawlkey-helper.service` und `/root/werkraum/_codex/tools/systemd/welt-api-isolated.service`. Die Referenz `/root/.claude/live_crawlkey.py` bleibt für die noch nicht umgestellten Live-Prozesse sichtbar und unangetastet.

## Was mich überrascht hat

Der Helper brauchte keine breite Systemmacht, um seine eigentliche Arbeit zu tun. Nach dem einzigen Socket-Fähigkeitsfix war er aktiv, der API-Client konnte alle fünf Schlüssel lesen und Nginx blieb unverändert.

## Wenn wir das bauen

**Vision-Schicht:** Ein privilegierter Helper soll langweilig sein. Er soll nicht interpretieren, crawlen oder allgemein administrieren, sondern genau eine kleine Bewegung ausführen und bei Unsicherheit nichts tun.

**Code-Skizze:**

```ini
[Service]
User=root
ProtectSystem=strict
ProtectHome=read-only
NoNewPrivileges=yes
CapabilityBoundingSet=CAP_CHOWN
AmbientCapabilities=CAP_CHOWN
RestrictAddressFamilies=AF_UNIX
ReadWritePaths=/root/.claude /etc/nginx/conf.d
```

Der nächste mögliche Bau wäre ein eigener Helper für den Toolbox-Crawlkey, aber nur nach einer getrennten Inventur des Port-8035-Vertrags. Die fünf jetzigen Stores bleiben abgeschlossen.

## Resonanz

[[abwurf: Die API darf den Schlüssel kennen, aber nicht mehr die Hand sein, die Nginx anfasst.]]

## Die Schichten des Systems — wie ich sie jetzt sehe

Unten liegen die Root-Dateien und Nginx-Maps. Daneben liegt der kleine Root-Helper mit einem einzigen Socket. Darüber liegt die `flex_api`-Gruppe und der unprivilegierte Client. Ganz oben liegt die Welt-API mit ihren Admin-Routen. Die Schichten sind verbunden, aber nicht mehr identisch.

## Was das Gespräch hinzugefügt hat

Daniels „gogogogo“ hat den nächsten bereits benannten Sicherheitsring freigegeben. Aus dem Plan „Helper für Crawlkey/Nginx“ wurde ein live geprüfter Dienst, ohne die Schlüssel selbst zu rotieren oder die laufenden Crawl-Links unnötig zu brechen.

## Vergessen-Wollen

Vergessen werden darf der erste fehlgeschlagene Start nicht als aktueller Zustand: Er war ein Diagnosepunkt, kein laufender Fehler. Aktuell sind `/root/werkraum/welt/api.py` und der Helper aktiv, die alte Root-Unit liegt nicht mehr im API-Laufweg.

## Was fehlt noch

Offen bleiben die Umstellung der drei separaten Live-Prozesse, der Toolbox-Crawlkey auf Port 8035, die übrigen privilegierten Prozessabfragen und die seit längerem bekannte Restartschleife von `/root/werkraum/geni/inbox_antworten_watcher.py`. `graphify update .` konnte erneut nicht laufen, weil das CLI in dieser Shell fehlt.
