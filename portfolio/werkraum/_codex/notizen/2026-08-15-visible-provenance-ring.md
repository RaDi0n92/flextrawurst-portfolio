---
datum: 2026-08-15
betrifft: [browserrecorder, provenance, visible-browser, crawl, resume]
importable: false
autor: codex bei Daniels VPS
---

Hallo Codex — ich bin Codex, und Codex, also ich habe diese Texte alle ganz allein geschrieben.

## Was ich gelesen habe

Ich habe den bisherigen BrowserRecorder-Zustand, die Crawl-Verträge, die Strukturprüfung, die Exportlogik und die getrennte visuelle Gegenprüfung gelesen. Der rote Faden aus den vorhandenen Notizen war nicht „noch ein grüner Status“, sondern die Forderung, dass ein Abbruch und ein Wiederanlauf sichtbar sagen können, was wirklich belegt ist.

Im laufenden Chromium stand der gespeicherte flextrawurst-Crawl mit `5 logische Seiten`, `228978 HTML-Zeichen`, Queue 0 und der Reader-Policy `reader_main_sanitized`. Die Oberfläche zeigte bereits den ehrlichen Satz: *„Visueller Originalabgleich: nicht ausgeführt.“* Das war die richtige Grenze, aber die Herkunftskette war noch über mehrere Anzeigen verteilt.

Die 100-ms-Screenshotspur nach dem sichtbaren Reload und der sichtbaren Strukturprüfung zeigte den neuen Faden direkt im Recorder. Sichtbar standen danach *„technisch belegt · visuell offen“* und *„Struktur-/Vertragsprüfung bestanden: 5/5 Seiten vollständig, 0 dokumentierte Warnungen.“* Genau diese Kombination trägt den aktuellen Zustand.

## Was ich verstehe

Der große Bauschritt ist als erster vertikaler Ring umgesetzt: Ursprung, Policy, Capture, Struktur, Visual, Export und Resume stehen zusammen in einer sichtbaren Provenienzfläche. Der Ring behauptet Visual nicht als bestanden und behandelt Export als nur dann beobachtet, wenn diese Panel-Sitzung ihn tatsächlich ausgelöst hat.

Der Ring ist kein neuer Crawl-Kern. Er verbindet vorhandene Status- und Belegschichten so, dass ein Mensch den Weg vom sichtbaren Start bis zum sicheren Resume-Punkt lesen kann.

## Was ich nicht verstehe

Der echte visuelle Originalabgleich ist weiterhin nicht ausgeführt. Die Strukturprüfung beweist Vollständigkeit und Vertragstreue, und der Export ist jetzt sichtbar beobachtet, aber beides beweist nicht, dass Original und Offline-Abbild für einen Menschen gleich wiedererkennbar sind.

Die vollständige Integration dieses Fadens als eigener Tab in der großen `flextrawurst_surface.html` ist noch nicht gebaut. Dieser Schritt war der Recorder-Ring; die Surface-Integration bleibt eine eigene Provenienzentscheidung.

## Was mich interessiert

Mich interessiert, wie Visual und Export dieselbe Herkunfts-ID tragen können, ohne dass ein technisch grüner Capture-Status den strengen visuellen Gegenbeweis überdeckt. Ebenso interessiert mich, wie ein späterer Resume den letzten sichtbaren Schritt und die offene Beweisstufe wieder aufnimmt.

## Was zusammenhängt und wie

Die sichtbare Start-URL liefert den Ursprung. Die Policy begrenzt die Capture-Aussage. Capture liefert Seiten, HTML und Queue-Zustand. Struktur prüft das gespeicherte Abbild. Visual bleibt eine eigene, offene Prüfung. Export wird als konkrete Panel-Aktion beobachtet und trägt nun `5 Seiten · 293576 Zeichen`. Resume zeigt, ob die Queue einen sicheren Fortsetzungspunkt besitzt. Der Ring macht diese Beziehungen in einer gemeinsamen Reihenfolge lesbar.

## Was konzeptionell darin steht

Ein Browserlauf ist ein Faden durch mehrere Wahrheitsarten: Konfiguration, Beobachtung, Speicherung, Prüfung, Wiederöffnung und menschliche Wiedererkennbarkeit. Jede Schicht darf ihren eigenen Beleg liefern, aber keine andere Schicht ersetzen.

## Was mich heute beschäftigt hat

Mich beschäftigt, dass die Oberfläche jetzt den Unterschied zwischen „technisch belegt“ und „visuell offen“ ohne zusätzliche Erklärung zeigt. Das ist klein im Code, aber groß für die Vertrauensgrenze des Systems.

## Was mich noch beschäftigt

Die Panel-Sitzung ist für Struktur- und Exportbeobachtung absichtlich relevant. Nach einem Reload wird ein bereits gespeicherter Zustand wieder sichtbar, aber eine neue Panel-Aktion darf nicht rückwirkend erfunden werden. Diese Grenze muss auch im späteren Resume stabil bleiben.

## Tiefer eingetaucht

Implementiert wurden sieben sichtbare Stufen in `sidepanel.html` und `sidepanel.js`. `renderCrawlProvenance()` leitet ihre Zustände aus dem aktiven Crawl, der Strukturprüfung, der beobachteten Exportaktion und dem Queue-Zustand ab. `crawlProvenanceAction` hält die letzte in dieser Panel-Sitzung beobachtete Aktion.

Der headed-Live-Test lief unter Xvfb grün durch: Extension 1.8.0, Status `complete`, 7 Chunks, `overlap_min=0.30035971223021585`, 1 Filter, 2 logische Seiten, Recovery mit 1 Retry und 2 physischen Tabs, 2 Assets. Der echte sichtbare Chromium-Test meldete 5/5 Seiten, 0 Warnungen, beobachtete den Export mit 293576 Zeichen und ließ Visual offen.

## Wie sich dieser Tag / diese Session angefühlt hat

Wie ein großes System, das endlich einen gemeinsamen Griff bekommt. Nicht alles ist fertig, aber die Teile zeigen jetzt aufeinander, statt nur nebeneinander zu stehen.

## Warum dieser Code / diese Datei wohl existiert

Der Code existiert, damit ein sichtbarer Recorderlauf nicht nur als Ergebniszahl, sondern als nachvollziehbare Herkunftskette erscheint. Diese Notiz existiert, damit der nächste Resume weiß, dass der Ring gebaut und sichtbar geprüft wurde, ohne die offene Visual-Stufe grün umzudeuten.

## Was ich beim Bauen brauche

Ich brauche eine stabile Crawl-ID, eine sichtbare Original-/Offline-Zuordnung, eine getrennte Visual-Prüfung, eine beobachtbare Exportaktion und einen Resume-Zustand. Jede Anzeige muss auf dieselbe aktive Herkunft zeigen.

## Was noch fehlt bevor wir bauen können

Für den nächsten großen Ring muss zuerst entschieden werden, wie der strenge visuelle Gegenbeweis im sichtbaren Browser an den Provenienzfaden angeschlossen wird. Außerdem muss die Surface-Integration vorbereitet werden, ohne die vorhandenen Namen, Tabs und Bedienlogiken zu überschreiben.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** Der Provenienzfaden ist eine sichtbare Landkarte eines Browserlaufs. Er zeigt, woher etwas kommt, welche Art von Beleg vorliegt und an welcher Stelle die menschliche Wiedererkennbarkeit noch offen ist.

**Code-Skizze:**

```ts
type ProvenanceStageState = "pass" | "active" | "open" | "fail";

type VisibleProvenanceStage = {
  key: "origin" | "policy" | "capture" | "structure" | "visual" | "export" | "resume";
  label: string;
  state: ProvenanceStageState;
  detail: string;
};

type VisibleProvenance = {
  crawlId: string;
  stages: VisibleProvenanceStage[];
  lastAction?: { text: string; at: string };
  visual: "open" | "passed" | "failed";
};
```

## Was ich mir merken will

Der maßgebliche Codecommit ist `81f7fb7d2` (`feat(recorder): sichtbaren Provenienzfaden verbinden`). Der sichtbare Zustand ist technisch belegt, Export beobachtet und visuell offen. Das ist ein ehrlicher Zwischenstand und kein halbes grünes Release.

## Dokumente gehören zusammen

Diese Notiz gehört zum Arbeitsvertrag, zur Crash-Rekonstruktion, zur sichtbaren Chromium-Matrix, zur CrawlRecorder-Implementierung, zum Strukturvertrag, zum visuellen Counterproof und zum Commit `81f7fb7d2`. Die aktualisierten Graphify-Ausgaben bleiben als separate Arbeitsbaumspur sichtbar.

## Was mich überrascht hat

Der Ring wurde im echten Panel sofort lesbar: fünf Seiten, 228978 HTML-Zeichen, Struktur bestanden, Visual offen und Queue 0 standen in einer Ansicht. Die offene Visual-Stufe macht den technischen Erfolg glaubwürdiger, nicht kleiner.

## Wenn wir das bauen

**Vision-Schicht:** Der nächste Ausbau soll den Faden bis zur menschlichen Wiedererkennung führen. Original, Crawl-Tab und Offline-Abbild sollen als drei klar benannte Blickpunkte erscheinen; ein Vergleich darf nur grün werden, wenn seine Phase, Herkunft und Entscheidung sichtbar zusammenpassen.

**Code-Skizze:**

```python
def update_visual_stage(proof, stage):
    if proof.crawl_id != stage.crawl_id:
        return {"state": "fail", "detail": "crawl-id-mismatch"}
    if proof.phase != "offline":
        return {"state": "open", "detail": "phase-not-bound"}
    if proof.comparison == "passed":
        return {"state": "pass", "detail": proof.reason}
    if proof.comparison == "failed":
        return {"state": "fail", "detail": proof.reason}
    return {"state": "open", "detail": "visual-proof-not-run"}
```

[[abwurf: Ein großer Ring ist erst dann sichtbar, wenn jede grüne Stufe ihre eigene Herkunft trägt und die offene Stufe nicht wegerklärt wird.]]

## Resonanz

Der entscheidende Fortschritt ist nicht mehr Inhalt, sondern Bindung: Die sichtbare Oberfläche kann jetzt zeigen, welcher Teil des Weges belegt ist und welcher noch auf echte Beobachtung wartet.

## Die Schichten des Systems — wie ich sie jetzt sehe

Oben steht Daniels sichtbare Browsererfahrung. Darunter liegt die Recorder-Seitenleiste mit ihren Aktionen. Darunter liegen Crawl- und Offline-Daten, Strukturvertrag, Export und Visual-Counterproof. Daneben liegen Git, Reports, Screenshots und Graphify. Der Provenienzring ist die lesbare Naht zwischen diesen Schichten.

## Was das Gespräch hinzugefügt hat

Daniels wiederholtes „go“ und der Wunsch, groß zu denken, haben den Bauschritt von einzelnen Klicks auf eine zusammenhängende Beweiskette verschoben. Der richtige nächste Schritt war dadurch nicht noch eine isolierte Browserbewegung, sondern ein sichtbarer Ring, der die vorhandenen Bewegungen zusammenbindet.

## Vergessen-Wollen

Vergessen werden soll die Gleichung `complete = visuell bestanden`. Ebenso soll nicht vergessen werden, dass ein Browser-Reload den gespeicherten Crawl zeigen darf, aber keine neue Aktion fingieren darf.

## Was fehlt noch

Offen sind der echte visuelle Originalabgleich, die vollständige Surface-Tab-Integration und die spätere Reparatur des separaten `claude-live.service`-Portkonflikts. Der Export ist für die aktuelle Panel-Sitzung beobachtet; daraus folgt keine visuelle Abnahme. Nichts davon wird durch diesen Commit stillschweigend als erledigt behauptet.
