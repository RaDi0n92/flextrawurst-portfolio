---
datum: 2026-08-14
betrifft: [browserrecorder, crawlrecorder, chromium, playwright, offline-html, offlinevertrag, wikipedia, assets, provider-gates]
importable: false
autor: codex bei Daniels VPS
---

# Offlinevertrag und sichtbarer Gegenbeweis

## Was ich gelesen habe

Ich habe den Gesamtauftrag gegen die tatsächlichen Beweise gehalten: sichtbarer Chromium-Tab, Mausauswahl, wiederholte Screenshots, DOM-Struktur, exportierte Bytes, Hash, Inode und Wiederöffnung. Der Auftrag lässt „grün“ nur als Teilbefund gelten, nicht als Behauptung einer vollständigen Website.

Die Forschungsspur zu MHTML, SingleFile, WARC/WACZ und Service-Worker-Offlinelesen bleibt dabei Orientierung: ein Komfort-HTML ist eine Leseschicht, ein WACZ/WARC-Paket die belastbarere Archivschicht, und beides muss Herkunft und Grenzen mittragen.

## Was ich verstehe

Ein Websitebetreiber kann einen autoritativen Offlinevertrag unter `/.well-known/dak-offline.json`, per `link[rel=offline-manifest]` oder Meta-Link anbieten. Der Recorder entdeckt ihn nur beim finalen sichtbaren Capture, validiert Schema, Entry-Points, Ressourcen, Hashes und HTML/WACZ-Ausgaben und zeigt `valid`, `invalid`, `missing` oder `unavailable` getrennt an.

## Was ich nicht verstehe

Noch nicht entschieden ist, ob und unter welchen expliziten Bedingungen öffentliche CDN-Medien zusätzlich eingebettet werden dürfen. Der aktuelle Schutz bleibt bei same-origin Inline-Assets; externe Medien werden nicht heimlich nachgeladen.

## Was mich interessiert

Mich interessiert die Differenz zwischen einem Betreibervertrag und unserem beobachteten Browserblick: Der Vertrag kann vollständige Dateien versprechen, der Recorder darf trotzdem nur behaupten, was er im sichtbaren Lauf und im Paket wiedergefunden hat.

## Was zusammenhängt und wie

Policy → Queue → sichtbarer Crawl-Tab → stabile Scroll-Chunks → CaptureEnvelope → Owner-Manifest → Offline-HTML → Download-Hash/Inode → erneute Browseröffnung → DOM-/Layoutvergleich. Provider-Gates und readonly-Desktop-Audits bleiben davon getrennte Pfade.

## Was konzeptionell darin steht

Der Offlineatlas ist ein eigener Leseraum mit Beweiskarte, nicht eine billige Spiegelkopie. Seine Oberfläche darf eigenständig und lesbar sein, muss aber Artikelkörper, Tabellen, Listen, Links, Herkunft, Filter und unerfüllte Medienzustände sichtbar lassen.

## Was mich heute beschäftigt hat

Die innere Offline-Viewport-Aufnahme hat zuerst schwarze/braune Originalfarben auf dunklem Readergrund und danach Broken-Image-Glyphen gezeigt. Beide roten visuellen Befunde wurden behoben: Kontrastregeln mit `!important` und eine sichtbare DOM-Mediengrenzkarte.

## Was mich noch beschäftigt

Der öffentliche Headless-Sechserlauf blieb bei Wikipedia in `scanning`, 0 Seiten und etwa 6,3 GB Renderer-RSS hängen. Das ist ein Ressourcen-/Harnessbefund, kein Erfolg; der isolierte Prozess wurde zum VPS-Schutz beendet. Der sichtbare Shared-Desktop-Lauf derselben Seite blieb dagegen vollständig.

## Tiefer eingetaucht

Der belastbare sichtbare Lauf `/tmp/dak-visible-live-wikipedia-http-1786699132765/report.json` meldet 28 Chunks, 225 Links, 12 Assets, 538001 HTML-Zeichen, 10 Original-Screenshots, Mausdrag plus `Control+C`, stabile 27/27 Übergänge, 20 Überschriften, zwei Tabellen, 13 Listen, Linkratio 1 und Textverhältnis 0.9981. Der Download hatte 1,064,380 Bytes; Hash und derselbe Inode wurden beim Wiederöffnen geprüft.

Die letzte Gegenprobe `/tmp/dak-visible-live-wikipedia-http-1786699132765/offline-iframe-viewport.png` zeigt den eigenen dunklen Reader mit lesbarer Navigation, Infobox und einer klaren „Offline-Mediengrenze“ statt eines kaputten Bildsymbols. Die neun Wikimedia-Medien bleiben `external_origin` im Manifest.

## Wie sich dieser Tag / diese Session angefühlt hat

Wie ein langer Test, der durch rote Stellen besser wurde. Besonders wichtig war, dass ein 120-Sekunden-Screenshot-Timeout und ein 6,3-GB-Headless-Hänger nicht in eine hübsche grüne Zahl verwandelt wurden.

## Warum dieser Code / diese Datei wohl existiert

`offline_export_contract.js` macht den Betreiberanspruch maschinenlesbar. `crawl_recorder.js` hält den sichtbaren Blick und die Mediengrenze. `export_engine.js` bringt den Vertrag in die Beweiskarte. Die Live-Harnesses beweisen Browser, Download, Struktur, Interaktion und Gegenbeweis getrennt.

## Was ich beim Bauen brauche

Vor jeder Änderung einen Backup-Commit; danach lokale Syntax/Fixture, sichtbares Chromium, echte Download-Wiederöffnung, Screenshot-Inspektion und einen klaren roten Gegenlauf. CDP-Verbindungen dürfen den Shared-Browser niemals schließen.

## Was noch fehlt bevor wir bauen können

Für den Grundpfad fehlt kein Blocker. Vor einem Anspruch auf „komplett“ fehlen noch autorenseitig gültige öffentliche Beispielpakete, explizite Cross-Origin-Assetpolitik, WACZ-Export/Wiederabnahme und die Interaktionsstrecken für geöffnete Tabellen, Figuren und Chartzustände.

## Datenstruktur die ich mir vorstelle

Vision-Schicht: Ein Betreiber reicht einen lesbaren Vertrag ein, der nicht nur Dateien, sondern Einstiegspunkte, Zustände, Ressourcen, Screenshots, Interaktionen, Lizenz und Grenzen beschreibt. Der Recorder legt daneben seine eigene Beobachtung als Gegenstimme ab.

Code-Skizze:

```ts
type OfflineStatus = "valid" | "invalid" | "missing" | "unavailable" | "not_requested";
interface OfflineManifest {
  schema: "dak-offline/v1"; canonical_url: string; entrypoints: string[];
  resources: { url?: string; path?: string; mime?: string; sha256?: string; bytes?: number }[];
  exports: { html?: string; wacz?: string }; states?: string[]; screenshots?: string[];
  interactions?: string[]; license?: string; captured_at?: string;
}
interface OwnerOfflineExport { status: OfflineStatus; url: string|null; errors: string[]; manifest?: OfflineManifest; }
```

## Was ich mir merken will

`complete` ist kein Vollständigkeitswort. Es bedeutet nur, dass der gewählte sichtbare Lauf seine eigenen End- und Stabilitätsregeln bestanden hat.

## Dokumente gehören zusammen

Der Gesamtauftrag, `crawl_site_profiles.js`, `offline_export_contract.js`, die sichtbaren Runner, `test_crawl_proof_counterproof_live.js`, die Forschungsspur und die Graphify-Ausgabe gehören als ein Beweisbündel zusammen.

## Was mich überrascht hat

Der Screenshot des Offline-Frames war hilfreicher als die fast perfekte Strukturzahl: Er zeigte sofort, dass importierte Wikipedia-CSS-Farben die eigene Oberfläche überstimmten und dass externe Medien nicht einfach als „Assets 12“ gezählt werden dürfen.

## Wenn wir das bauen

Vision-Schicht: Der Betreiber stellt einen eigenen, ehrlichen Offline-Einstieg bereit; unser Reader macht daraus einen coolen, menschlich lesbaren Raum, ohne die Originalherkunft zu verschlucken.

Code-Skizze:

```js
const owner = await DakOfflineExportContract.discover(location.href);
const capture = await DakCrawlCapture.captureVisibleCrawlPage({
  projection: "reader_main_sanitized", discover_owner_manifest: true,
  include_assets: policy.assets === "bounded_inline"
});
const bundle = { ...capture, owner_offline_export: owner };
ExportEngine.generateOfflineCrawlHTML({ pages: [bundle] });
```

## Resonanz

[[abwurf: Ein Download ist erst dann ein Gegenstand, wenn seine Bytes, seine sichtbare Form und seine Grenzen gemeinsam wieder geöffnet werden können.]]

## Die Schichten des Systems — wie ich sie jetzt sehe

Unten liegt der öffentliche Browserkörper. Darüber liegen Reader-Projektion, Sanitizer und Medienstatus; daneben Queue, Budgets und stabile Chunks; darüber Vertrag, Export, Download und Comparator. Quer dazu laufen Provideradapter und readonly-Desktop-Audits.

## Was das Gespräch hinzugefügt hat

Daniel hat die frühe „grün“-Sprache zurückgewiesen und sichtbare Gegenprüfung verlangt. Dadurch wurden Screenshots im inneren Offline-Frame, Hash/Inode-Wiederöffnung, Mausauswahl, Kontrast und Ressourcenhänger zu Pflichtbeweisen.

## Vergessen-Wollen

Die Zahl der Chunks, die nur sichtbare Oberfläche und der einzelne erfolgreiche Providerlauf dürfen nie als vollständige Website- oder Plattformabnahme erinnert werden.

## Was fehlt noch

Offen bleiben: gültiger Owner-Vertrag auf einer realen Betreiberstrecke, echte WACZ-Wiederabnahme, kontrolliertes Cross-Origin-Asset-Inlining, alle fehlenden sichtbaren Claude/Facebook/FAQ/Tagesschau-Artikel-Tabs und ein reproduzierbar ressourcenbegrenzter Public-Atlaslauf ohne 6-GB-Renderer.

## Nachtrag — Ressourcenbeweis

Der Recorder schützt sich jetzt vor unbounded DOM-Oberflächen (`surface_limit`, Standard 20 Mio. Pixel), bevor ein riesiger Clone entsteht. Der sichtbare Runner sampelt das DOM weiter alle 300 ms, rastert aber nach 180 Screenshots nicht weiter und meldet das Budget ausdrücklich; so bleibt die echte Gegenprüfung lang, ohne den Shared-Renderer durch Compositor-Leaks zu füllen. Der abschließende Lauf `/tmp/dak-visible-live-wikipedia-http-1786700937016/report.json` blieb bei 95 Samples und `sampler_screenshot_budget_exhausted: false`.
