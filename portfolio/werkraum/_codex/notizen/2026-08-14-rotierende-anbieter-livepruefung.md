---
datum: 2026-08-14
betrifft: [browserrecorder, chromium, playwright, anbieterrotation, chatgpt, claude, gemini, grok, twitter, facebook, sichtbarkeit, zugangsschluessel]
importable: false
autor: codex bei Daniels VPS
---

# Rotierende Anbieterpaare und sichtbarer Desktop

## Was ich gelesen habe

Ich habe den öffentlichen Profilkatalog, den Crawl-Runner, das Sidepanel und die aktuellen Chromium-Ziele gelesen. Der Auftrag war klar: neue Seiten je Anbieter, zwei gleichzeitig, nach einer festen Schwelle weiterrotieren und die Ergebnisse real im Browser samt Download prüfen.

## Was ich verstehe

Ein Anbieter-Batch besteht aus zwei begrenzten Tiefe-0-Seiten. Beide starten im sichtbaren Chromium, werden mit 300-ms-DOM-/Screenshotproben begleitet und nach maximal 120 Sekunden als `complete`, `blocked`, `possibly_incomplete`, `timeout` oder Gegenbeweisfehler abgelegt.

## Was ich nicht verstehe

Noch offen ist, warum einzelne Seiten bei wiederholten Läufen trotz gleichem Profil gelegentlich am Scroll-Scroller instabil werden. Das wird als `possibly_incomplete` sichtbar gehalten, nicht geglättet.

## Was mich interessiert

Mich interessiert jetzt der Unterschied zwischen „parallel gestartet“ und „parallel wirklich stabil beobachtet“. Der zweite Wert ist der eigentliche Qualitätsmaßstab; deshalb bleiben Download- und Wiederöffnungsfehler rot.

## Was zusammenhängt und wie

Profilquelle → Anbieterpaar → zwei sichtbare Zieltabs → zwei Sidepanel-Startaktionen → aktive Crawl-Map → Terminalschwelle → HTML-Comparator → Chrome-Download → gleiche Datei per Hash/Inode → Offline-Wiederöffnung → Sidepanel bleibt am letzten Zieltab offen.

## Was konzeptionell darin steht

Der Test soll wandern. Kein Anbieter bekommt unendlich viel Aufmerksamkeit, und ein langsamer Tab darf die sichtbare Arbeitsfläche nicht verschlucken. Rotation ist hier eine Sicherheits- und Wahrnehmungsregel, keine bloße Parallelisierung.

## Was mich heute beschäftigt hat

Der Desktop zeigte wieder nur den Recorder-Tab. Die Ursache war nicht ein fehlender Crawl, sondern die falsche Sichtbarkeit: Der Runner schloss seine Zieltabs und öffnete den Recorder als normale Seite. Der echte `chrome.sidePanel.open()`-Pfad bindet ihn jetzt an den letzten offiziellen Seitentab.

## Was mich noch beschäftigt

Der Zugangsschlüssel ist in der aktuellen Browsersitzung tatsächlich leer. Das Panel zeigt „Kein Zugangsschlüssel für diese Browsersitzung“; das Feld wurde fokussiert, aber kein Geheimnis erfunden oder eingetragen.

## Tiefer eingetaucht

Die neue Katalogschicht enthält je zwei öffentliche Ziele für OpenAI, Anthropic, Gemini, xAI, X/Twitter und Meta/Facebook. Belegt komplett wieder geöffnet wurden unter anderem Gemini API Guide/Reference, xAI News und Grok 4.5 sowie Anthropic Constitution; Consent- und Scrollgrenzen blieben als eigene Befunde.

Der abschließende Sichtbarkeitstest ließ das aktive Fenster auf `Introducing Grok 4.5 | SpaceXAI - Chromium` stehen. Der Sidepanel-Modus ist an diesen Tab gebunden; nur der zweite Testtab wird nach dem Paarlauf geschlossen.

## Wie sich dieser Tag / diese Session angefühlt hat

Wie ein Zurückholen der Arbeit auf den Bildschirm. Der wichtige Fehler war nicht im HTML, sondern darin, dass der Mensch den laufenden Beweis nicht sehen konnte.

## Warum dieser Code / diese Datei wohl existiert

Der Rotationsrunner verhindert Endlosschleifen und hält reale Befunde auseinander. Die Sidepanel-Endbedingung sorgt dafür, dass ein Lauf nicht mit einer leeren Arbeitsfläche endet.

## Was ich beim Bauen brauche

Vor Änderungen Backup-Commit; danach sichtbares Chromium, stabile DOM-Proben, echte Downloads, Hash/Inode-Wiederöffnung, Screenshotbudget und einen ehrlichen roten Status. Zugangsschlüssel bleiben Benutzereingabe.

## Was noch fehlt bevor wir bauen können

Es fehlen weitere gezielte Interaktionsaktionen für dynamische Anbieterzustände und ein echter autorenseitiger öffentlicher Offlinevertrag. Der Rotationsmechanismus selbst ist live geprüft.

## Datenstruktur die ich mir vorstelle

Vision-Schicht: Ein wandernder Prüfstrom, der jedem Anbieter zwei Seiten leiht, sie sichtbar befragt und den letzten Beweisraum offen lässt. Die Oberfläche verschwindet nicht, nur weil die Messung endet.

Code-Skizze:

```ts
type RotationBatch = {
  provider: string;
  profiles: string[]; // exactly two
  threshold_seconds: number;
  outcomes: Array<"complete" | "blocked" | "possibly_incomplete" | "timeout" | "counterproof_failed">;
  kept_target_url: string | null;
};
```

## Was ich mir merken will

„Sichtbar“ bedeutet: offizieller Seitentab aktiv, echter Chrome-Sidepanel daneben, Download wieder geöffnet — nicht nur ein JSON-Report im Terminal.

## Dokumente gehören zusammen

`crawl_site_profiles.js`, `test_crawl_public_rotation_live.js`, `sidepanel.js`, die Rotationsberichte unter `/tmp/dak-public-rotation-*` und die Desktop-CDP-Ziele gehören zusammen.

## Was mich überrascht hat

Ein normal geöffnetes Sidepanel-HTML kann den Eindruck erzeugen, der Recorder sei sichtbar, obwohl die eigentliche Seite verschwunden ist. Die Sidepanel-API löst genau diese Verwechslung.

## Wenn wir das bauen

Vision-Schicht: Jeder Lauf endet in einem sichtbaren Ort, an dem Daniel sofort weitersehen und den Schlüssel einsetzen kann. Kein stiller Abschluss im Hintergrund.

Code-Skizze:

```js
const lastTarget = await runLastBatch({ keepTarget: true });
await chrome.sidePanel.open({ tabId: await tabId(lastTarget) });
await lastTarget.bringToFront();
```

## Resonanz

Ein Test ist erst fertig, wenn sein Ende für den Menschen sichtbar ist.

## Die Schichten des Systems — wie ich sie jetzt sehe

1. öffentliche Zielseite, 2. sichtbarer Crawl, 3. rotierender Batch, 4. Downloadbeweis, 5. Offline-Rekonstruktion, 6. Sidepanel-/Zugangsschlüssel-Sichtbarkeit.

## Was das Gespräch hinzugefügt hat

Daniels Hinweis, dass auf dem Desktop nichts sichtbar bleibt, verschob den Schwerpunkt von „Runner erfolgreich“ zu „Runner endet mit sichtbarem Arbeitszustand“.

## Vergessen-Wollen

Nicht vergessen: Ein fehlender Schlüssel ist kein Grund, einen Schlüsselstatus zu behaupten. Und ein roter Scroller ist kein grüner Vollbeweis.

## Was fehlt noch

Schlüssel-Eingabe durch Daniel, weitere stabile Interaktionspfade, autorenseitige öffentliche Offlinepakete und eine gezielte Ursachenanalyse der intermittierenden Scroller-Grenzen.

[[abwurf: Sichtbarkeit ist kein Komfortfeature; sie ist der letzte Gegenbeweis gegen einen Test, der nur im Terminal existiert.]]
