---
datum: 2026-08-13
betrifft: [browserrecorder, web-capture, playwright, links, offline-html]
importable: false
autor: codex bei Daniels VPS
---

Hallo Codex — ich bin Codex, und Codex, also ich habe diesen Text ganz allein geschrieben.

## Was ich gelesen habe

Ich habe den bestehenden Browserrecorder gelesen: Provider-Registry, Content-Script-Bootstrap, `recorder_core.js`, Seitenleiste und die Python-Ereignisablage. Der Kern arbeitet bereits mit echten Browserereignissen und lokalem IndexedDB-Puffer; die historische Chat-Projektion sollte nicht für Webseiten umgebogen werden.

Die wichtige Stelle war die Trennung zwischen sichtbarem Inhalt und Serverexport. Der neue Modus liest keine API-Antworten und führt keine Seitenskripte in der Offline-Datei aus. Die Links kamen aus sichtbaren `<a href>`-Elementen; relative Ziele wurden gegen die aktuelle URL aufgelöst.

Beim Playwright-Lauf sah ich zuerst einen echten Randfall: Der Wheel-Schritt wurde an derselben Mausposition wiederholt und die Seite blieb bei 167 px. Mit realer Mausbewegung vor jedem Wheel lief die Fixture vollständig bis zum Rand. Das ist kein grüner Scheinbeleg, sondern eine konkrete Bediengeometrie, die für Nachrichtenseiten wichtig bleibt.

## Was ich verstehe

Der Recorder kann als opt-in Webprovider jede normale HTTP/HTTPS-Seite beobachten, solange ihr sichtbarer Inhalt im DOM steht. Er speichert sichtbare Textbereiche, Links und Medienquellen; der Server erzeugt daraus `PAGE.md`, `PAGE.html`, `LINKS.json` und behält das Manifest.

## Was ich nicht verstehe

Noch nicht bewiesen ist, wie gut stark virtualisierte Feeds auf Facebook oder X die sichtbare DOM-Oberfläche während eines langen Scrolls stabil halten. Ebenso ist noch offen, welche Medien als echte herunterladbare Kopie neben der URL gespeichert werden sollen; derzeit werden Quellen nur referenziert.

## Was mich interessiert

Mich interessiert die Grenze zwischen „alles Sichtbare“ und „alles, was die Seite technisch kennt“. Für diesen Recorder ist die Grenze bewusst beim sichtbaren, gerenderten DOM gezogen. Das schützt vor heimlichem API-Auslesen, bedeutet aber bei Infinite-Scroll und Login-Schranken eine echte Sichtbarkeitsgrenze.

## Was zusammenhängt und wie

Provider-Erkennung entscheidet, ob eine Seite `web` ist. Der Webadapter liefert Blöcke und Links. Der generische Import sendet Ereignisse. Der Webexport liest daraus eine sichere Projektion. Playwright prüft die Kette mit Home, echten Klicks, echten Wheel-Ereignissen und stabilen Doppel-Snapshots.

## Was konzeptionell darin steht

Eine Webseite wird nicht als heimliches Abbild ihrer internen Daten aufgefasst, sondern als sichtbare, navigierbare Oberfläche. Der Offline-Export erhält die Erinnerung an den gelesenen Inhalt und lässt externe Links bewusst zurück in ihre Onlinewelt zeigen.

## Was mich heute beschäftigt hat

Die Runtime-Kopie war nicht dieselbe Erweiterung wie der Quellordner. Erst der Befund aus `chrome://extensions` machte sichtbar, dass Chromium die Referenzkopie v1.8.0 lädt. Beide Pfade wurden deshalb gezielt ergänzt, ohne die Referenzgrenze zu verwischen.

## Was mich noch beschäftigt

Der erste Serverexport blieb offen, weil der Zugangsschlüssel nach dem Runtime-Neuladen nicht in dieser Browsersitzung lag. Danach wurde der Schlüssel sichtbar im Panel gesetzt, 28 gepufferte Ereignisse wurden bestätigt, und der hashbasierte Webcapture exportierte am VPS 3 Bereiche und 3 Links.

## Tiefer eingetaucht

Der gefährlichste kleine Fehler war die doppelte Identität: Adapter und Hintergrunddienst hatten unterschiedliche IDs für dieselbe URL. Dadurch sah die Seite erkannt aus, aber die explizite Freigabe griff nicht. Nach dem Abgleich wurde die sichtbare Aufnahme freigegeben und der Lauf konnte stattfinden.

## Wie sich dieser Tag / diese Session angefühlt hat

Erst schnell, dann sehr konkret. Die Oberfläche sagte „Webseite“, aber der Browser sagte zunächst noch nicht dasselbe. Gut war, dass die echten Playwright-Prüfungen die kleinen Unstimmigkeiten sofort an die Oberfläche brachten.

## Warum dieser Code / diese Datei wohl existiert

Der Webadapter existiert, um den vorhandenen Recorder auf sichtbare Nicht-Chat-Seiten zu erweitern, ohne ChatGPT- oder Claude-Provenienz zu überschreiben. Der Webexport existiert, um aus Ereignissen einen wiederverwendbaren, scriptfreien Offlinekörper zu bauen.

## Was ich beim Bauen brauche

Ich brauche immer die tatsächlich geladene Erweiterung, eine lokale Fixture mit langen Bereichen, einen echten sichtbaren Seitenleistenstart und ein Server- oder Pufferprotokoll. Ein DOM-Test allein reicht hier nicht.

## Was noch fehlt bevor wir bauen können

Für produktive Facebook-, X- und Nachrichtenseitentests fehlt eine gestufte Testmatrix: öffentlich, eingeloggter Feed, Infinite-Scroll, Cookie-/Consent-Overlay, virtualisierte Liste und externe Links. Außerdem fehlt ein bewusster Medien-Copy-Auftrag, falls Bilder lokal eingebettet werden sollen.

## Datenstruktur die ich mir vorstelle

Vision-Schicht: Jeder Webcapture trägt Quelle, sichtbare Bereiche, beobachtete Verweise und eine zeitliche Aufnahmegrenze. Offline bedeutet nicht „Internet weg“, sondern „Text und Navigation bleiben als sichere Projektion erhalten“.

Code-Skizze:

```python
WebCapture = {
    "provider_id": "web",
    "source_url": str,
    "title": str,
    "messages": [{"content": str, "links": list[dict], "media": list[dict]}],
    "links": [{"href": str, "text": str, "source_block_id": str | None}],
    "artifacts": {"markdown": "PAGE.md", "html": "PAGE.html"},
}
```

## Was ich mir merken will

Links müssen absolut gespeichert werden, aber ihre Ziele werden nicht automatisch rekursiv gecrawlt. Im Offline-HTML stehen sie mit `target="_blank"` und `rel="noopener noreferrer"`.

## Dokumente gehören zusammen

`web_adapter.js`, `web_bootstrap.js`, `recorder_core.js`, `browser_capture.py`, `app.py`, die Runtime-Referenzkopie und die Playwright-Fixture sind eine Kette. Die Chat-Exportfunktionen bleiben eine getrennte Schicht.

## Was mich überrascht hat

Die kleine Fixture hatte in Chromium nur 233 px Viewport-Höhe und der erste echte Wheel-Lauf blieb scheinbar hängen. Nicht der Recorder war kaputt; die Mausposition lag für die weitere Wheel-Interaktion ungünstig. Mit expliziter Mausbewegung war der Lauf stabil.

## Wenn wir das bauen

Vision-Schicht: Die Seite soll sich während der Aufnahme wie eine lesbare Oberfläche verhalten, nicht wie eine Datenbank, die der Agent heimlich leert. Der Export soll offline ruhig sein und externe Navigation ausdrücklich sichtbar lassen.

Code-Skizze:

```javascript
await root.click({position: {x: 8, y: 180}});
await page.keyboard.press("Home");
const delta = Math.floor(viewportHeight * 0.70);
await page.mouse.move(viewportWidth / 2, viewportHeight / 2);
await page.mouse.wheel(0, delta);
// zwei gleiche Struktur-Snapshots, danach nächstes Fenster
```

## Resonanz

Die generische Erweiterung fühlt sich richtig an, solange sie ihre Grenze sichtbar hält: beobachtete Webseite, nicht behauptete Vollständigkeit des Internets.

## Die Schichten des Systems — wie ich sie jetzt sehe

Browser-UI: sichtbarer DOM und echte Eingaben. Extension: Adapter, Import, Puffer. VPS: append-only Ereignisse und Projektion. Offline: sichere HTML-/Markdown-Datei mit externen Links. Provenienz: Chat- und Webcapture bleiben unterscheidbar.

## Was das Gespräch hinzugefügt hat

Daniel hat den entscheidenden Produktkern ergänzt: Links müssen mitkommen und im Offline-HTML anklickbar sein, wobei ein neuer Tab geöffnet wird. Daraus wurde der konkrete Linkvertrag mit absoluter URL und `noopener`.

## Vergessen-Wollen

Nicht vergessen werden darf, dass ein funktionierender lokaler Fixturelauf noch kein Beleg für Facebook, X oder jede Nachrichtenseite ist. Diese Namen bleiben Testziele, keine bereits bewiesenen Adapter.

## Was fehlt noch

Der Zugangsschlüssel wird bewusst nur flüchtig in der Browsersitzung gehalten und muss nach einem Extension-Reload sichtbar erneut gesetzt werden. Der Panel-Export bietet jetzt sichtbare Downloads für MD, HTML und Links-JSON über `chrome.downloads`; offen bleiben produktive Testläufe auf realen Facebook-, X- und Nachrichtenseiten.

[[abwurf: Offline heißt hier nicht, dass die Welt verschwindet — es heißt, dass ihr Inhalt ruhig wird und ihre Links weiter nach außen zeigen.]]
