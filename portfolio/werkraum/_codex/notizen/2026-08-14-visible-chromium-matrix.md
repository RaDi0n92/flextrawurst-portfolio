---
datum: 2026-08-14
autor: codex bei Daniels VPS
importable: false
---

## Was ich gelesen habe

Ich habe die wiederhergestellte Arbeitsgeschichte gelesen: Der alte Capture-Status `complete` war zu grob, weil er Download, Inode und Struktur als Erfolg ausgab, ohne Original und Offline-Raster an denselben sichtbaren Scrollpunkten zu vergleichen. Die neue Beweiskette verlangt drei gemeinsame Punkte bei 0, 0.5 und 1, Original-/Offline-Screenshot, DOM-/Geometriesignatur, RMSE, MAE, pHash und ein separates 0.88-Gate.

Ich habe die Codex-Notizen, Claudes importierten Grundriss, Werkraumkarte, Resonanzfeld, Briefkastenregeln, die 490-Punkte-Vision und den aktuellen Graphreport gelesen. Die Herkunft bleibt dabei getrennt: Claudes und GPTs Spuren sind Referenz, nicht meine Erinnerung; der sichtbare Chromium im virtuellen Desktop ist der einzige Browserraum dieser Prüfung.

Ich habe die aktuellen sichtbaren Läufe gelesen und im bereits laufenden Chromium fortgesetzt: OpenAI, Gemini, xAI/Grok, Meta/Meta-AI und X waren schon mit dem neuen Gegenbeweis geprüft. Danach kamen Flextrawurst, die sechs Ideen-Seiten, der direkte Facebook-Anker und Tagesschau hinzu.

## Was ich verstehe

Daniel wollte nach dem Abbruch keine neue unsichtbare Testwelt. Gemeint ist: im virtuellen Desktop, im bereits sichtbaren Chromium, über sichtbare Tabs und sichtbare Panel-Klicks arbeiten; die Belege müssen so entstehen, dass die Browseroberfläche und ihre Herkunft nachvollziehbar bleiben.

Die Statusklassen müssen getrennt bleiben. `blocked` bedeutet Zugangsschranke, `possibly_incomplete` bedeutet kein stabiler Abschluss, ein Strukturfehler endet vor dem visuellen Gate, und `visual_counterproof_failed` bedeutet: Capture und Download können stimmen, aber die sichtbare Rekonstruktion ist nicht hinreichend ähnlich.

## Was ich nicht verstehe

Noch offen ist, wie externe Fonts, Bilder, dynamische Datenkarten und eingeloggte Sitzungen so normalisiert werden können, dass der Vergleich fair bleibt, ohne die Herkunft der Seite zu überschreiben. Das ist keine Erlaubnis, den 0.88-Schwellenwert nachträglich weich zu machen.

Beim direkten Facebook-Test ist nicht abschließend geklärt, ob die öffentliche Start-URL grundsätzlich eine Login-/Consentseite liefern würde: In Daniels sichtbarem Chromium war bereits eine eingeloggte, dynamische Sitzung vorhanden. Deshalb wurde daraus kein öffentlicher Offlinebeweis abgeleitet.

## Was mich interessiert

Mich interessiert die Grenze zwischen „öffentliche URL“ und „öffentlicher beobachtbarer Zustand“. Eine URL kann öffentlich erreichbar sein und trotzdem im vorhandenen Browser private, dynamische Inhalte zeigen. Der Recorder muss diese Herkunft erkennen und darf sie nicht als neutrale Webseite in einen öffentlichen Atlas schreiben.

Mich interessiert außerdem, ob der Leser-Modus eine verständliche eigene Projektion sein darf, ohne dass der Status den Eindruck einer 1:1-Kopie erweckt. Die roten Raster zeigen, dass Lesbarkeit und visuelle Identität zwei verschiedene Dinge sind.

## Was zusammenhängt und wie

Die Kette lautet: sichtbarer Originaltab → sichtbare Panel-Auswahl → begrenzter Ein-Seiten-Crawl → stabiler Scrollendpunkt → Export → Browser-Download → SHA- und Inode-Gegenbeweis → erneute Dateiöffnung im selben Chromium → drei gemeinsame Rasterpunkte → DOM-/Geometrievergleich → Status.

Wenn der Crawl vor dem Export scheitert, gibt es keinen visuellen Status. Wenn der Export stimmt, aber die Bilder auseinanderlaufen, bleibt der Status rot. Wenn der sichtbare Tab privat oder dynamisch ist, wird er nicht zu einem öffentlichen Beleg.

## Was konzeptionell darin steht

Ein Offlineabbild ist ein Gegenstück mit Herkunft und Grenze, kein Wahrheitsstempel. „Vollständig heruntergeladen“ und „vom Menschen wiedererkannt“ sind zwei verschiedene Behauptungen.

[[abwurf: Ein sichtbarer Originaltab ist nicht automatisch ein öffentlicher Zustand, und ein vollständiger Download ist nicht automatisch dieselbe Seite.]]

## Was mich heute beschäftigt hat

Mich hat beschäftigt, dass die sechs Ideen-Seiten sehr verschieden scheitern: PLOS verlor bereits im Offline-Reader fast den gesamten sichtbaren Körper, MDN blieb an einem unsichtbar werdenden Textziel hängen, OWID unterschritt den HTML-Schwellenwert, während ArXiv und Gutenberg technisch sauber liefen und erst am Rastervergleich rot wurden.

Mich hat auch beschäftigt, dass der direkte Facebook-Lauf Screenshots einer eingeloggten persönlichen Sitzung erzeugte. Der Lauf wurde als `possibly_incomplete` behandelt, der Facebook-Tab geschlossen und der einzelne temporäre Testordner in den Papierkorb verschoben. Private Inhalte sind kein Belegmaterial.

## Was mich noch beschäftigt

Die Rotation schrieb vor der Korrektur `ok:false`, konnte aber mit Exit 0 enden. Das war eine zweite Wahrheitsschieflage neben dem früheren hartcodierten `ok:true`. Die Rotation überträgt den Reportstatus jetzt auf Exit 2; diese Regel muss bei jedem neuen Runner erhalten bleiben.

## Tiefer eingetaucht

Flextrawurst erreichte 33 Chunks, 5 Links und 169237 HTML-Zeichen. Der Download war bytegleich und die Wiederöffnung teilte den Inode, aber der visuelle Score lag bei 0.829555, pHash-Maximum 96.6628.

ArXiv erreichte 7 Chunks, 50 Links und 24018 HTML-Zeichen. Die Struktur lag bei 0.923245, der Gesamt-Score aber nur bei 0.720925; der pHash-Maximalwert war 1551.83. Gutenberg erreichte 8 Chunks, 63 Links und 30962 HTML-Zeichen, blieb mit 0.692845 und pHash 1708.43 rot.

## Wie sich dieser Tag / diese Session angefühlt hat

Es fühlte sich an wie eine Rückkehr in einen laufenden Raum, in dem zu viele Tabs und zu viele alte Statuswörter gleichzeitig sprechen. Der sichtbare Chromium hat geholfen: Die roten Diffs waren nicht abstrakt, und die Facebook-Grenze war unmittelbar als Herkunftsproblem erkennbar.

## Warum dieser Code / diese Datei wohl existiert

`visual_counterproof.js` existiert, damit gespeicherte Screenshots zu einem Gegenbeweis werden. `test_crawl_visible_desktop_live.js` bindet sichtbare Mausauswahl, sichtbare Panel-Klicks, Download und Wiederöffnung. `test_crawl_public_rotation_live.js` hält Anbieterläufe getrennt und muss seinen Exitstatus ebenso ehrlich wie sein JSON ausgeben.

Der additive Profilanker `facebook-public` existiert nur, damit die direkte Facebook-URL nicht stillschweigend mit Meta-Newsroom verwechselt wird. Er erlaubt keinen Login- oder Umgehungsversuch.

## Was ich beim Bauen brauche

Ich brauche den bereits sichtbaren Chromium, einen eindeutig gebundenen Testtab, das sichtbare Recorder-Panel, eine begrenzte Profilpolicy, einen stabilen Crawlabschluss, den Download-/Inode-Beleg und die drei gemeinsam gerasterten Original-/Offlinepunkte. Außerdem brauche ich eine separate Herkunftsmarkierung für private, eingeloggte oder dynamische Zustände.

## Was noch fehlt bevor wir bauen können

Es fehlt eine robuste, sichtbare Blockadeerkennung für eingeloggte öffentliche URLs wie Facebook. Es fehlen außerdem stabile sichtbare Textziele für Seiten mit dynamischen oder versteckten Templates wie MDN und Tagesschau sowie eine bewusste Asset-Allowlist für externe Fonts und Medien.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** Jede Seite trägt neben ihrem Inhalt auch den beobachteten Zustand: öffentlich, blockiert, privat eingeloggter Zustand, unvollständig oder visuell gegengeprüft. Original, Rekonstruktion und Differenz liegen als benannte Zeugen nebeneinander.

**Code-Skizze:**

```ts
type ObservationStatus =
  | "complete"
  | "blocked"
  | "possibly_incomplete"
  | "structural_failed"
  | "visual_counterproof_failed"
  | "visual_counterproof_passed";

type VisibleProfile = {
  id: string;
  url: string;
  provider?: string;
  reader_focus: boolean;
  include_assets: boolean;
  minimum_chunks: number;
  minimum_links: number;
  minimum_html: number;
};

type VisualCheckpoint = {
  ratio: 0 | 0.5 | 1;
  source_png: string;
  offline_png: string;
  diff_png: string;
  structural_score: number;
  rmse: number | null;
  mae: number | null;
  phash: number | null;
};

type CrawlEvidence = {
  status: ObservationStatus;
  private_or_authenticated: boolean;
  download_sha256?: string;
  source_inode?: string;
  reopened_path?: string;
  checkpoints: VisualCheckpoint[];
  score?: number;
};
```

## Was ich mir merken will

Die Frage ist nicht „ist die Datei da?“, sondern „welcher sichtbare Zustand wurde mit welcher Herkunft wieder geöffnet?“. Ein roter Gegenbeweis ist ein gültiges Ergebnis. Ein Exit-0 bei `ok:false` ist es nicht.

## Dokumente gehören zusammen

Zusammengehören: `refferenzen/AI-UI-RECORDER-v1.6.5-DIREKT-LADEN/core/crawl_site_profiles.js`, `_codex/tools/test_crawl_visible_desktop_live.js`, `_codex/tools/test_crawl_public_rotation_live.js`, `_codex/tools/visual_counterproof.js`, die Reports unter `/tmp/dak-visible-live-*` und die Graphspur `graphify-out/GRAPH_REPORT.md` / `graphify-out/graph.json`.

Die fachliche Änderung ist in Commit `78468f036` gesichert. Die vorherigen visuellen Gegenbeweis- und Backupspuren bleiben als eigene Commits sichtbar.

## Was mich überrascht hat

ArXiv hatte einen hohen Strukturwert von 0.923245 und war trotzdem visuell weit entfernt. Flextrawurst war mit 0.829555 näher, aber wegen pHash 96.6628 ebenfalls nicht bestanden. Das zeigt, warum kein einzelner Strukturwert als Identität gelten darf.

## Wenn wir das bauen

**Vision-Schicht:** Ein öffentlicher Atlas soll nicht so tun, als sei jede beobachtete Seite gleichartig. Er muss zeigen, ob er eine Seite gelesen, eine Seite rekonstruiert, eine Schranke gesehen oder einen privaten Zustand vorgefunden hat. Sichtbarkeit und Herkunft bleiben bis zum letzten Status erhalten.

**Code-Skizze:**

```js
const result = await runVisibleChromiumProfile(profile);

if (result.private_or_authenticated) {
  result.status = "possibly_incomplete";
  result.public_proof = false;
} else if (!result.visual?.evidence_complete) {
  result.status = "structural_failed";
  result.public_proof = false;
} else if (result.visual.status !== "visual_counterproof_passed") {
  result.status = "visual_counterproof_failed";
  result.public_proof = false;
} else {
  result.public_proof = true;
}

process.exitCode = result.public_proof ? 0 : 2;
```

## Resonanz

Die gewünschte Strenge hat die Matrix nicht schöner, aber wahrer gemacht. OpenAI blieb blockiert, Gemini, xAI/Grok, Meta-Newsroom und X blieben visuell rot, Meta-AI blockiert; nur Anthropic-Newsroom hatte in der früheren Runde einen bestandenen visuellen Gegenbeweis, während Constitution rot blieb. Die neue Flextrawurst- und Ideenmatrix bestätigt dieselbe Regel.

## Die Schichten des Systems — wie ich sie jetzt sehe

1. Virtueller Desktop und bereits laufendes sichtbares Chromium.
2. Sichtbarer Originaltab mit echter Maus-/Panel-Interaktion.
3. Begrenzte Profilpolicy und beobachteter DOM-/Scroll-/Assetzustand.
4. Reader-Projektion oder sichtbares DOM mit klarer Herkunft.
5. Download, SHA, exakter Inode und Offline-Wiederöffnung.
6. Drei gemeinsame Rasterpunkte plus DOM-/Geometrie-Gegenbeweis.
7. Status und Exitcode, die dieselbe Aussage tragen.

## Was das Gespräch hinzugefügt hat

Daniel hat nach dem Abbruch die Arbeitsbedingung wieder scharf gestellt: nicht in einer unsichtbaren Ersatzumgebung weiterlaufen, sondern direkt im sichtbaren virtuellen Desktop-Chromium, sodass die Arbeit und ihre Grenzen nachvollziehbar bleiben. Außerdem wurde Facebook als direkter Fall von Meta getrennt und der Exitcode als Teil des Beweises behandelt.

## Vergessen-Wollen

Vergessen werden soll die bequeme Gleichung `complete = grün = wahr`. Ebenso soll ein direkter Facebook-Tab nicht als öffentliche Seite gelten, nur weil seine URL öffentlich ist.

## Was fehlt noch

Offen bleiben ein stabiler isolierter Atlaslauf ohne `pages:0`, die Asset-Allowlist, robuste Blockade-/Privatzustandserkennung, MDN-/Tagesschau-Interaktionsziele und eine spätere Entscheidung, ob visuelle Eigenständigkeit von Flextrawurst als eigene Projektion dokumentiert oder weiter an Originaltreue angenähert werden soll. Die aktuelle Matrix ist abgeschlossen als Befund, nicht als „alles bestanden“.
