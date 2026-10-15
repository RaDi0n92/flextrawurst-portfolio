---
datum: 2026-08-14
betrifft: [browserrecorder, crawlrecorder, chromium, playwright, offlinevertrag, wacz, offline-html, gegenbeweis]
importable: false
autor: codex bei Daniels VPS
---

# Positiver Eigentümervertrag im Chromium-Fixture

## Was ich gelesen habe

Ich habe die bestehende Offlinevertrag-Validierung, den Fixture-Capture und die Offline-Beweiskarte gelesen. Der bisherige Fixture-Lauf bewies nur `missing`; der neue Lauf musste deshalb einen zweiten, ausdrücklich autorenseitig angebotenen Pfad zeigen.

Im sichtbaren Desktopbericht las ich erneut die echte Wikipedia-Strecke: 28 Scroll-Chunks, 225 Links, 12 Asseteinträge, Mausauswahl und Download-Wiederöffnung. Der öffentliche Artikel bietet keinen `dak-offline`-Vertrag an; diese Grenze bleibt sichtbar.

## Was ich verstehe

Ein positives `valid` ist nur dann belastbar, wenn Chromium den Manifest-Endpunkt wirklich abfragt, die normalisierten URLs und Ressourcen akzeptiert und der exportierte Offlineatlas den Status als `autorenseitig gültig` ausweist. Ein isolierter Validator ohne Browser-Netzwerkpfad wäre dafür zu schwach.

## Was ich nicht verstehe

Noch offen ist, wie ein realer Betreiber-WACZ außerhalb des Fixtures wieder geöffnet und inhaltlich gegen die sichtbare Originalseite verglichen wird. Die URL-Präsenz allein beweist nicht die Paketvollständigkeit.

## Was mich interessiert

Mich interessiert die klare Doppelspur: Betreibervertrag als behauptete Lieferform, Recorder-Capture als beobachtete Lieferform, Download-Wiederöffnung als Gegenprüfung. Erst wenn diese drei Schichten zusammenpassen, wird aus einer URL ein prüfbarer Offlineweg.

## Was zusammenhängt und wie

`/.well-known/dak-offline.json` → `DakOfflineExportContract.discover()` → normalisiertes `owner_offline_export` → `CaptureEnvelope` → `ExportEngine`-Beweiskarte → heruntergeladene HTML-Datei → erneute Browseröffnung. Die öffentliche Wikipedia-Strecke läuft daneben als ehrlicher `missing`-Gegenbeweis.

## Was konzeptionell darin steht

Der Offlineatlas soll nicht so tun, als sei jede Website vollständig exportierbar. Er zeigt, ob die Seite selbst einen Vertrag anbietet, was unser sichtbarer Lauf tatsächlich sah und welche Medien oder Zustände außerhalb der Beobachtung liegen.

## Was mich heute beschäftigt hat

Der erste positive Fixture-Lauf scheiterte nicht am Produkt, sondern daran, dass die zweite Testseite den Envelope-Contract nicht geladen hatte. Das war ein guter Testfehler: Der Browserpfad musste vollständig aufgebaut sein, nicht nur der Manifest-Request.

## Was mich noch beschäftigt

Der positive Fixture-Vertrag ist synthetisch. Für einen öffentlichen Positivbefund brauchen wir später eine kontrollierte, erreichbare Beispielseite mit echter HTML- und WACZ-Datei, ohne fremde Accounts oder unklare Rechte.

## Tiefer eingetaucht

Der neue Fixture-Capture akzeptiert `schema: dak-offline/v1`, einen Canonical-Artikel, einen Stylesheet-Ressourceneintrag mit SHA-256 und Bytezahl, Zustände, Screenshot, Interaktion, Lizenz und `captured_at`. HTML- und WACZ-Export werden absolut normalisiert und in der Offlineansicht sichtbar verifiziert.

Der sichtbare Gegenlauf `/tmp/dak-visible-live-wikipedia-http-1786702910173/report.json` blieb unabhängig davon grün im beobachteten Sinn: 94 Proben, 61 Zeichen Auswahl, `copy`, 320092 Downloadbytes und gleiche Datei beim Wiederöffnen. Sein Ownerstatus ist ausdrücklich `missing`.

## Wie sich dieser Tag / diese Session angefühlt hat

Wie ein sauberer Beweis, weil Positiv- und Negativseite nebeneinander bleiben durften. Der Vertrag wurde nicht aus dem erfolgreichen Wikipedia-Crawl herausphantasiert.

## Warum dieser Code / diese Datei wohl existiert

Der Fixture-Test schützt die Behauptung, dass ein angebotener Betreibervertrag den gesamten Weg bis zur Leseroberfläche überlebt. Die Session-Notiz hält fest, dass `valid` kein Synonym für „alles der Website“ ist.

## Was ich beim Bauen brauche

Vor Codeänderungen ein Backup-Commit; danach Syntax, Fixture, sichtbares Chromium, Download-Hash/Inode, Wiederöffnung und ein roter Gegenpfad. Shared-CDP darf nur gezielt Tabs aktivieren oder schließen, nie den Browser.

## Was noch fehlt bevor wir bauen können

Es fehlen ein echter öffentlicher Positivvertrag, WACZ-Inhaltsprüfung statt URL-Prüfung und explizite Interaktionsbeweise für geöffnete Tabellen, Figuren und dynamische Diagramme.

## Datenstruktur die ich mir vorstelle

Vision-Schicht: Der Vertrag ist eine öffentliche Lieferkarte; der Recorder legt eine zweite, zeitgebundene Wahrnehmungskarte daneben. Beide dürfen sich widersprechen, ohne dass eine Seite stillschweigend die andere ersetzt.

Code-Skizze:

```ts
type OwnerOfflineExport = {
  status: "valid" | "invalid" | "missing" | "unavailable" | "not_requested";
  url: string | null;
  manifest?: {
    schema: "dak-offline/v1";
    canonical_url: string;
    entrypoints: string[];
    resources: ResourceRef[];
    exports: { html: string | null; wacz: string | null };
    states: string[];
    screenshots: string[];
    interactions: string[];
    license: string | null;
    captured_at: string | null;
  };
};
```

## Was ich mir merken will

Der wichtigste positive Test ist nicht „Manifest gefunden“, sondern „Manifest gefunden, validiert, in den Capture übernommen und in der wieder geöffneten Offlinebeweiskarte als gültig sichtbar“.

## Dokumente gehören zusammen

`offline_export_contract.js`, `crawl_recorder.js`, `export_engine.js`, `test_crawl_capture_fixture.js` und der sichtbare Wikipedia-Bericht bilden eine Beweiskette. Die Forschung zu WACZ und SingleFile bleibt Architekturvergleich, nicht Produktbeweis.

## Was mich überrascht hat

Die zusätzliche Chromium-Seite hat den Vertrag sofort sauber bestätigt, sobald der passende Envelope-Contract geladen war. Der Testaufbau selbst war die einzige rote Stelle.

## Wenn wir das bauen

Vision-Schicht: Eine Website darf eine eigene Offline-Lieferung deklarieren, aber der Leser sieht daneben immer Herkunft, Zeitpunkt, Zustände und nicht eingelöste Teile. Das Ergebnis bleibt eigenständig lesbar statt zur blinden Kopie zu werden.

Code-Skizze:

```js
const owner = await DakOfflineExportContract.discover(location.href);
const page = { ...capture, owner_offline_export: owner };
const html = ExportEngine.generateOfflineCrawlHTML({ pages: [page] });
assert.match(renderedEvidence, /autorenseitig gültig|nicht angeboten/);
```

## Resonanz

Ein guter Test macht die positive Behauptung kleiner und dadurch belastbarer.

## Die Schichten des Systems — wie ich sie jetzt sehe

1. sichtbare Originalseite, 2. Recorder-Beobachtung, 3. Owner-Vertrag, 4. Offline-Leseroberfläche, 5. Download-/Wiederöffnungsbeweis, 6. expliziter Gegenbeweis.

## Was das Gespräch hinzugefügt hat

Daniels insistieren auf „wirklich live“ führte dazu, den synthetischen Positivvertrag nicht als Ersatz für den öffentlichen Browserlauf zu behandeln. Beide Prüfarten müssen getrennt benannt werden.

## Vergessen-Wollen

Nicht vergessen: `valid` ist kein Vollständigkeitsprozentsatz und `missing` kein Crawlfehler.

## Was fehlt noch

Ein echtes öffentliches WACZ-Paket, Paket-Hash-/Inhaltsabgleich, kontrollierte positive Cross-Origin-Assets und benannte UI-Aktionen für dynamische Zustände.

[[abwurf: Ein positiver Vertrag ist erst ein Beweis, wenn sein Status den ganzen Weg bis zur wieder geöffneten Offlinebeweiskarte überlebt.]]
