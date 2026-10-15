---
datum: 2026-08-21
betrifft: [browserrecorder, crawler, wikipedia, export, pdf, docx]
importable: false
autor: codex bei Daniels VPS
---

## Was ich gelesen habe

Ich habe den Recorder-Vertrag, die direkten Exporter-Spuren und die aktuelle Web-Adapter-/Office-Export-Implementierung gelesen. Entscheidend war Daniels knappe Forderung: „echter sichtbarer Wikipedia-Lauf auf Desktop 1“, Downloads mit Hash-Rücklese und PDF/DOCX.

Im sichtbaren Chromium wurde `https://de.wikipedia.org/wiki/Browser` geöffnet und als `Webbrowser – Wikipedia` vollständig durchlaufen. Die Screenshots zeigen den unteren Original-Seitenrand mit Quellen-/Footer-Bereich; die Downloadfläche zeigt alle sieben Links.

## Was ich verstehe

Die Webexporte sind Projektionen aus sichtbar erfassten DOM-Blöcken. Der Beleg muss deshalb drei Dinge gleichzeitig zeigen: Originalseite, vollständiges Ende und identische Bytes zwischen erzeugtem Artefakt und finalem Browserdownload.

## Was ich nicht verstehe

Nicht geklärt ist, ob Daniel zusätzlich einen echten Backend-authentifizierten Sidepanel-Klick auf der laufenden Recorder-Instanz möchte. Für diese Abnahme war die kontrollierte sichtbare Playwright-Downloadfläche ausreichend; ein Service-Neustart war nicht nötig.

## Was mich interessiert

Wie sich dieselbe Belegkette später für beliebige öffentliche Seiten mit eingebetteten Medien und nachladenden Bereichen verhält, ohne aus einem endlichen Lauf eine falsche Vollständigkeitsbehauptung zu machen.

## Was zusammenhängt und wie

Der Web-Adapter liefert sichtbare Blöcke und Links. `browser_web_export_data` projiziert sie nach MD/HTML/TXT/CSV/JSON. `browser_web_office_export` verwendet dieselbe Projektion für PDF/DOCX. Playwright prüft Sichtbarkeit, Downloadabschluss und Hash-Rücklese.

## Was konzeptionell darin steht

Ein Export ist kein magischer Seitenkopierer, sondern eine provenance-markierte Momentaufnahme: Quelle, sichtbarer Umfang, bekannte Lücken, Projektion und finale Datei bleiben zusammen lesbar.

## Was mich heute beschäftigt hat

Die Hash-Gleichheit fühlt sich hier wichtiger an als die Dateiendung. Erst wenn Originalartefakt und Download bytegleich sind, ist „heruntergeladen“ nicht nur ein UI-Satz.

## Was mich noch beschäftigt

Die Text-Rekonstruktion erreicht in diesem Lauf Token-Recall 1 gegen die erfasste Originalseite, aber das sagt noch nichts über Pixel-, CSS- oder Medienidentität aus.

## Tiefer eingetaucht

Der Lauf endete bei `scrollY=10157`, `scrollHeight=10977`, `viewportHeight=820`. Für jedes Format wurde ein eigener vollständiger Durchlauf dokumentiert; PDF und DOCX wurden zusätzlich textuell rückgelesen.

## Wie sich dieser Tag / diese Session angefühlt hat

Nüchtern und gut prüfbar: wenig Glanz, viele konkrete Dateien, sieben Hashpaare, ein sichtbarer unterer Seitenrand.

## Warum dieser Code / diese Datei wohl existiert

Die neuen Artefakte schließen die Lücke zwischen „Webseite sichtbar“ und „Webseite als portable Datei“. Der Bericht existiert, damit ein späterer Agent nicht aus einem grünen Test auf einen echten Browserlauf schließen muss.

## Was ich beim Bauen brauche

Vor jedem weiteren Recorder-Schritt: Contract-Gate, enger Backup-Commit, sichtbare Belegbilder, finale Hash-Rücklese und ein expliziter Scope für nicht archivierte Assets.

## Was noch fehlt bevor wir bauen können

Für Medienarchivierung fehlt ein eigener, ausdrücklich freigegebener Fetch-/Asset-Lauf. Für einen authentifizierten Sidepanel-Lauf fehlen keine Codebausteine, aber eine laufende Session mit gültigem Token.

## Datenstruktur die ich mir vorstelle

Vision-Schicht: Jede Seite trägt ihre Herkunft, ihren sichtbaren Ausschnitt und ihre Projektionen gemeinsam. Kein Format löscht die Spur des anderen.

Code-Skizze:

```ts
type WebArtifact = {
  format: 'md'|'html'|'txt'|'csv'|'json'|'pdf'|'docx';
  sourceUrl: string;
  captureId: string;
  bytes: number;
  sha256: string;
  downloadComplete: boolean;
};
```

## Was ich mir merken will

„Download fertig“ zählt erst nach `saveAs`, Bytezahl und SHA-256-Rücklese.

## Dokumente gehören zusammen

`browser_capture.py`, `office_export.py`, die Sidepanel-/Background-Erweiterung, die Playwright-Vergleichsdatei und der Browserrecorder-Bericht sind eine Kette, keine fünf unabhängigen Behauptungen.

## Was mich überrascht hat

Wikipedia leitete sichtbar auf `Webbrowser` um; diese Weiterleitung blieb als tatsächliche Quell-URL im Lauf erhalten. PDF und DOCX waren trotz Projektion vollständig extrahierbar.

## Wenn wir das bauen

Vision-Schicht: Der Export soll sich wie ein sauberer Abdruck des gesehenen Ortes anfühlen, nicht wie eine heimliche globale Datensammlung.

Code-Skizze: `POST /api/v1/web-pages/{identifier}/office-export` erzeugt serverseitig den kanonischen Office-Blob; der Background-Handler prüft Base64, Bytes und SHA-256, bevor `chrome.downloads` schreibt.

## Resonanz

[[abwurf: Erst die Rücklese macht aus einem Download eine Aussage.]]

## Die Schichten des Systems — wie ich sie jetzt sehe

Originalseite → sichtbarer DOM-Lauf → kanonische Webprojektionen → Office-Projektionen → Browserdownload → Hash- und Text-Rücklese → Evidenzbericht.

## Was das Gespräch hinzugefügt hat

Daniel hat die Priorität auf den echten sichtbaren Wikipedia-Lauf gelegt. Damit wurde aus einer Exporter-Idee ein konkret prüfbarer Desktop-1-Abnahmeschritt.

## Vergessen-Wollen

Nicht aus dem Auge verlieren: Ein Token-Recall von 1 ist keine Zusage über Bilder, Layout oder externe Ressourcen.

## Was fehlt noch

`graphify update .` konnte nicht laufen, weil das Kommando in dieser Umgebung nicht vorhanden ist. Die fachliche Abnahme ist grün; die Graph-Aktualisierung bleibt als Infrastrukturrest offen.
