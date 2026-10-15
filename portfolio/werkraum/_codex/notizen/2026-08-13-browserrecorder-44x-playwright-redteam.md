---
datum: 2026-08-13
betrifft: [browserrecorder, playwright, chromium, crawlrecorder, beweis, bedienbarkeit, redteam]
importable: false
autor: codex bei Daniels VPS
---

# Session-Notiz — 44-faches Playwright-/Chromium-Redteam

## Was ich gelesen habe

Ich habe die vollständige Konzeptdatei mit 88 Ideen, 22 Red-Team-Runden, 33 sokratischen Fragen, 11 Sokrates-Schleifen und 111 Baupunkten erneut als Gesamtsystem gelesen. Diesmal habe ich nicht nur die Architekturbegriffe betrachtet, sondern für jeden behaupteten Beleg gefragt: Wo wird er im echten Chromium gemessen, welche Nutzeraktion erzeugt ihn und welche unabhängige Prüfung kann ihn widerlegen?

## Was ich verstehe

Die entscheidende Ergänzung ist eine zweiachsige Wahrheit: Eine Funktion kann spezifiziert, implementiert, als Fixture grün, live im Chromium bewiesen oder unabhängig geprüft sein. Diese Stufen dürfen nicht zu einem einzigen grünen Status verschmelzen.

## Was ich nicht verstehe

Der normale Web-Content-Script-Pfad meldete im laufenden Chromium sowohl in bestehenden als auch in frisch geöffneten Webseiten `DakRecorderCore=false`, obwohl der Extension-Service-Worker und das Sidepanel vorhanden waren. Die genaue Ursache des Injektionszustands ist damit noch nicht diagnostiziert; sie darf aber auch nicht durch den erfolgreichen Crawlpfad verdeckt werden.

## Was mich interessiert

Mich interessiert die Trennung zwischen `chrome.scripting.executeScript` für den expliziten Crawl und dem normalen manifestbasierten Content-Script-Lebenszyklus. Beide laufen in demselben Browser, sind aber nicht derselbe Beweis. Genau an dieser Stelle entsteht echte Synergie durch gemeinsame Datenverträge, nicht durch eine falsche gemeinsame Readinessbehauptung.

## Was zusammenhängt und wie

Playwright/CDP liest den Browser- und Extensionpass. Playwright navigiert frische Dokumente, klickt sichtbare Oberflächen und bewegt echte Scrollflächen. Chromium misst im Zieltab DOM, Geometrie und Snapshot. IndexedDB bewahrt Chunks und Queuezustände. Der Export wird als Datei heruntergeladen und außerhalb seines Erzeugers erneut gelesen. ChatGPT und Claude gehen durch eigene Provider-Gates.

## Was konzeptionell darin steht

Ein Beweis ist eine Kette, kein einzelner Funktionsaufruf: Runtime bekannt, Dokument frisch, Adapter bereit, Scrollsurface bestätigt, Bewegung beobachtet, Chunk stabil, Überlappung gemessen, Ende stabil, Filter geprüft, Export erneut geparst. Fehlt eine Stufe, wird der Claim kleiner.

## Was mich heute beschäftigt hat

Der Live-Crawl von `what-is-flextrawurst.html` lief über die sichtbare Seitenleiste wirklich bis `100%`, mit 9 Chunks, Queue 0 und 7.604 HTML-Zeichen. Gleichzeitig war der allgemeine Webadapter im frischen Zieltab nicht bereit. Das ist kein Widerspruch, sondern ein sauberer negativer Befund über zwei verschiedene Runtimepfade.

## Was mich noch beschäftigt

Der manuelle Playwright-Wheel-Schritt bewegte 389,33 Pixel bei 556 Pixel Viewporthöhe und ergab `0,29976` Überlappung. Das ist knapp unter dem Zielwert. Der aktuelle Code schreibt an dieser Stelle pauschal `0.30`; der nächste Bau muss reale Rohmetriken speichern und den Grenzfall rot lassen.

## Tiefer eingetaucht

Die 44 neuen Runden greifen vier Schichten an: Laufzeit/Provenienz, Sichtung/Scrollbeweis, DOM/Filter/Export und Queue/AI-Synergie/Bedienung. Sie haben mehrere aspirative Aussagen zurückgestuft: die 30-Seiten-Decke ist noch im Code, der Filter ist noch keine Werbeklassifikation, der Statuswert `overlap: 0.30` ist noch kein Messbeleg und ein direkter Runtime-Message-Test ist noch keine UI-Abnahme.

## Wie sich dieser Tag / diese Session angefühlt hat

Wie ein Messgerät, das erst durch einen kleinen roten Wert vertrauenswürdig wird. Der Crawl war erfolgreich genug, um den Weg zu zeigen, aber unvollständig genug, um die Methodik zu schärfen.

## Warum dieser Code / diese Datei wohl existiert

Die Konzeptdatei braucht diese Redteam-Schicht, damit spätere Bauarbeit nicht aus einer guten Vision automatisch eine bewiesene Runtime macht. Die Sessionnotiz hält die Herkunft der negativen und positiven Befunde getrennt.

## Was ich beim Bauen brauche

Ich brauche zuerst R0–R3: Runtimepass, frisches Dokument, Normaladapter-/Crawladapter-Readiness. Danach R4–R8 für echte Bewegung, stabile Chunks, gemessene Überlappung und Endmarker. Erst danach sind Filter, Queue und Export sinnvoll abnahmefähig.

## Was noch fehlt bevor wir bauen können

Es fehlen die Ursachenanalyse des normalen Web-Content-Script-Injektionsproblems, ein Fixture mit Werbung/Tracker/Consent, ein echter Filterreview, die Korrektur der Überlappungsmessung, ein unabhängiger Exportcomparator und die noch nicht gebaute Queue-/Tabpool-Schicht.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** Jede Behauptung trägt ihren eigenen Belegweg. Ein Crawlstatus sagt nicht nur „fertig“, sondern wer im Browser was gesehen, gemessen, gespeichert und später erneut geprüft hat.

**Code-Skizze:**

```ts
type EvidenceRecord = {
  claim: string;
  state: "specified" | "implemented" | "fixture_passed" | "live_proven" | "independent_checked" | "blocked";
  crawlId?: string;
  pageId?: string;
  tabId?: number;
  documentId?: string;
  playwrightAction?: string;
  before?: Record<string, unknown>;
  after?: Record<string, unknown>;
  comparator?: { name: string; result: "pass" | "fail" | "not_run" };
};
```

## Was ich mir merken will

Ein grüner Crawl darf niemals den fehlenden Core im frischen Dokument überstrahlen.

## Dokumente gehören zusammen

Zusammengehören die 88-Ideen-Konzeptdatei, der aktuelle `background.js`-Crawlpfad, `crawl_recorder.js`, `crawl_db.js`, `export_engine.js`, Sidepanel, die ChatGPT-/Claude-Adapter und die realen Playwright-Smokes. Der Konzeptstatus bleibt von der Runtimeabnahme getrennt.

## Was mich überrascht hat

Der sichtbare Crawlbutton und die Crawlstatuszeile waren im Sidepanel vorhanden und funktionierten bis zum vollständigen Ein-Seiten-Test. Der normale Webadapter war dagegen im frisch geladenen Flextrawurst-Dokument nicht verfügbar. Die gleiche Extension kann also in einem Tab per injiziertem Crawlscript arbeiten und im anderen Content-Script-seitig noch nicht bereit sein.

## Wenn wir das bauen

**Vision-Schicht:** Wir bauen einen Recorder, der seine eigene Beweisstärke kennt und dem Menschen nicht mehr Sicherheit vorspiegelt, als der virtuelle Browser tatsächlich getragen hat.

**Code-Skizze:**

```ts
const transition = await readStableBeforeAfterMetrics(page);
const overlap = 1 - transition.delta / transition.viewportHeight;
if (overlap < 0.30) return markBlocked("overlap_below_threshold", transition);
await commitChunk({ ...transition, overlap, documentId, policyVersion });
```

## Resonanz

[[abwurf: Ein grüner Crawl darf niemals den fehlenden Core im frischen Dokument überstrahlen.]]

## Die Schichten des Systems — wie ich sie jetzt sehe

Unten ist Chromium mit seinen echten Dokumenten und Scrollflächen. Darüber liegen Content-Script oder Crawl-Injection als zwei verschiedene Anschlüsse. Darüber liegen Policy, Filter, Chunks und Queue. Darüber liegen Export und Comparator. Ganz oben steht der Mensch, der Start, Auswahl, Stop und Interpretation kontrolliert.

## Was das Gespräch hinzugefügt hat

Daniels Wunsch nach Playwright, virtuellem Browser und direktem Chromium hat die Konzeption von einer Featureliste zu einer Beweismethodik verschoben. Die 44 Runden machen aus „soll funktionieren“ eine Folge lokaler, gegenprüfbarer Behauptungen.

## Vergessen-Wollen

Vergessen werden darf die Idee, dass ein Statusstring, eine Hashsumme oder eine sichtbare Exportdatei allein beweist, dass eine Seite gut gelesen wurde. Vergessen werden darf auch nicht, dass menschliche Bedienbarkeit ein eigenes Gate ist.

## Was fehlt noch

- Core-/Adapter-Injection im frischen Webdokument reparieren oder sauber als blockiert markieren;
- reale Überlappung statt Konstante speichern;
- Filterpreview und Ausschlussbuch bauen;
- Queue/Tabpool mit Resume und Lease bauen;
- Exportcomparator unabhängig machen;
- ChatGPT-/Claude-Smokes nach jedem gemeinsamen Core-Schritt ausführen.

