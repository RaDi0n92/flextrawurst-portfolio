---
datum: 2026-08-13
betrifft: [browserrecorder, chatgpt, claude, scrollbeweis]
importable: false
autor: codex bei Daniels VPS
---

Hallo Codex — ich bin Codex, und Codex, also ich habe diese Texte alle ganz allein geschrieben.

## Was ich gelesen habe

Ich habe den Graph-Report, die Browserrecorder-Ideen und den aktuellen Referenzkern gelesen. Dabei war deutlich, dass die geladene Referenz unter `refferenzen/AI-UI-RECORDER-v1.6.5-DIREKT-LADEN/` weiter ist als der Quellordner: Sie kennt echte verschachtelte Scrollcontainer, ChatGPT-/Claude-Adapter, Operator-Sichtprüfung und getrennte historische Beweisführung.

Im echten Chromium habe ich den ChatGPT-Tab „VPS Stop Bestätigt“ mit dem sichtbaren Sidepanel verbunden. Der Selbsttest sah fünf Nachrichten, zwei User- und drei Assistant-Flächen sowie echte Klappsteuerungen; das ist die Oberfläche, auf der der nächste Recorder-Schritt bestehen muss.

## Was ich verstehe

Der Recorder hat zwei verschiedene Wahrheiten: Was der Provider-DOM gerade zeigt und was eine automatische Scrollkette als vollständig beweisen darf. Ein großer Scrollschritt kann Nachrichten schnell erreichen und trotzdem die geometrische Überlappung zerstören.

## Was ich nicht verstehe

Noch offen ist, warum der ChatGPT-DOM nach Extension-Reload und Navigation zeitweise mehrere Sekunden mit Titel „ChatGPT“ und null Nachrichten meldet, bevor derselbe Tab korrekt materialisiert wird. Das ist bisher als Lade-/Virtualisierungsphase beobachtet, nicht als behobene Ursache.

## Was mich interessiert

Mich interessiert, ob dieselbe reale Containerlogik bei Claude genauso stabil greift und ob sich daraus eine kleine gemeinsame Provider-Prüfschnittstelle für Gemini, Grok, Kimi, Meta AI und Copilot ableiten lässt, ohne deren Unterstützung vorzutäuschen.

## Was zusammenhängt und wie

`chatScrollMetrics()` liefert Containerhöhe, Scrollposition und Ende. `auto_import.js` wählt die Schrittweite, `recorder_core.js` führt sie am echten Element aus, und die History-Proof-Schicht bewertet die Übergänge. Deshalb musste die Schrittweitenregel an beiden Stellen zusammenpassen: maximal 70 Prozent der frisch gemessenen Höhe, nie ein künstlicher Mindestwert von 240 Pixeln.

## Was konzeptionell darin steht

Ein Recorder ist kein Kopierer, der nur am Ende einen schönen Export erzeugt. Er ist eine kontrollierte Beobachtungskette: sichtbar werden, stabil werden, überlappen, sichern, Unsicherheit markieren. „Schnell“ darf die Wartezeit verkürzen, aber nicht die Beweisfläche überspringen.

## Was mich heute beschäftigt hat

Der alte 240-Pixel-Mindestschritt war klein im Code und groß in seiner Wirkung. Im kleinen realen Chatfenster mit 228 Pixeln Höhe hätte er den 30-Prozent-Gate verletzt. Genau solche kleinen Konstanten entscheiden, ob ein grüner Recorderstatus ehrlich ist.

## Was mich noch beschäftigt

Die automatische ChatGPT-Prüfung wurde absichtlich nach zwei korrigierten Schritten als `possibly_incomplete` beendet. Ein kompletter End-to-End-Lauf mit VPS-Bestätigung fehlt nach dieser Änderung noch; er gehört in die nächste einzelne Playwright-Runde.

## Tiefer eingetaucht

Der erste Live-Test zeigte außerdem, dass `pageStatus` einen frühen generischen Titel behalten konnte, obwohl der Adapter im Selbsttest bereits den richtigen Titel las. Der Status liest nun live und übernimmt einen nicht-generischen ChatGPT-/Claude-Titel.

## Wie sich dieser Tag / diese Session angefühlt hat

Wie eine Reparatur an einer schmalen Brücke: Der große Baukörper stand schon, aber zwei Millimeter falsche Geometrie hätten die Last falsch verteilt. Gut war, dass der Test nicht nur bestätigt, sondern den zweiten Fehler sichtbar gemacht hat.

## Warum dieser Code / diese Datei wohl existiert

Der Referenzkern ist die aktuell geladene, operative Wahrheit des Browsers. Der Quellkern bleibt die Herkunft für spätere Pakete. Beide müssen denselben Sicherheitsgedanken tragen, sonst wird beim nächsten Packen ein alter Fehler wieder eingeführt.

## Was ich beim Bauen brauche

Ich brauche pro Provider einen realen Tab, ein sichtbares Panel, einen stabilen DOM-Checkpoint, gemessene Containergeometrie und einen getrennten Status für „erkannt“, „gesichert“ und „vollständig bewiesen“. Für ChatGPT und Claude existieren diese Schichten bereits als tragfähiger Kern.

## Was noch fehlt bevor wir bauen können

Es fehlen der einzelne Claude-Live-Test nach diesem Kernupdate, ein vollständiger ChatGPT-Lauf bis zum End-Sentinel und eine ehrliche Provider-Matrix für die derzeit noch nicht abgenommenen Dienste. Erst danach sollten weitere AI-Dienste aktiviert werden.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** Jede Scrollbeobachtung ist ein kleines Beweisstück mit Herkunft, sichtbarer Fläche, Überlappung, Stabilität und Zustellstatus. Ein Export darf aus diesen Stücken lesbar werden, ohne Unsicherheiten zu verdecken.

**Code-Skizze:**

```ts
type ProviderId = "chatgpt" | "claude" | "gemini" | "grok" | "kimi" | "meta_ai" | "copilot";
interface ScrollCheckpoint {
  top: number; height: number; max: number; delta: number;
  overlapRatio: number; stable: boolean; provider: ProviderId;
}
interface ImportTruth {
  status: "running" | "complete" | "possibly_incomplete";
  checkpoints: ScrollCheckpoint[];
  uncertainties: string[];
}
```

## Was ich mir merken will

Die entscheidende Regel lautet: maximal 70 Prozent der real gemessenen Scrollcontainerhöhe. `fast` ist jetzt schnell durch kurze Wartezeiten, nicht durch einen 100-Prozent-Sprung.

## Dokumente gehören zusammen

Die Provider-Adapter, `core/recorder_core.js`, `core/auto_import.js`, das Sidepanel, die Playwright-Regressionsläufe und der Graphify-Bericht gehören als eine Kette zusammen. Der Webrecorder bleibt daneben eine eigene Schicht; seine Link- und Downloadarbeit ist nicht still in den AI-Kern hineinzumischen.

## Was mich überrascht hat

Der echte ChatGPT-Selbsttest erkannte neben normalen Nachrichten auch Denkbereiche und konnte am Ende 10 Übergänge mit bestätigter Überlappung melden, obwohl der Probeimport bewusst unvollständig abgebrochen wurde. Die Beweisqualität ist also schon differenzierter als ein einfaches „fertig/nicht fertig“.

## Wenn wir das bauen

**Vision-Schicht:** Der Recorder soll sich wie ein vorsichtiger Beobachter verhalten: Er nimmt jede sichtbare Bewegung ernst, lässt Raum für Wiedererkennen und sagt klar, wenn eine Kette nur begonnen wurde.

**Code-Skizze:**

```js
const delta = Math.max(1, Math.floor(scroll.viewportHeight * stepRatio));
const overlapRatio = 1 - delta / Math.max(scroll.viewportHeight, 1);
if (overlapRatio < 0.30) throw new Error("overlap proof unavailable");
scroll.element.scrollBy({ top: delta, left: 0, behavior: "auto" });
```

## Resonanz

Der schärfste Fortschritt war nicht mehr Geschwindigkeit, sondern eine Grenze, die der Code selbst nicht überschreiten darf. Das macht spätere Providerarbeit langsamer, aber vergleichbar und ehrlich.

## Die Schichten des Systems — wie ich sie jetzt sehe

Unten liegt der sichtbare Provider-DOM. Darüber sitzen Adapter und echte Scrollgeometrie. Darüber liegen lokale Sicherung, VPS-Zustellung und History-Proof. Ganz oben stehen Panel, Export und menschliche Bedienung. Keine Schicht darf die Unsicherheit der darunterliegenden einfach wegbenennen.

## Was das Gespräch hinzugefügt hat

Daniels Wunsch, zuerst den Recorder für ChatGPT und AI-Dienste zu schärfen und einzelne Playwright-Tests erst danach auszurollen, hat die Reihenfolge geklärt: erst Kerninvariante, dann Provider-Matrix, dann breite Website-Tests.

## Vergessen-Wollen

Vergessen werden darf die Versuchung, aus einem schnellen Probeimport einen Vollständigkeitsbeleg zu machen. Der aktuelle Lauf bleibt sichtbar als `possibly_incomplete`.

## Was fehlt noch

Claude muss einzeln mit Playwright geprüft werden. Danach folgen ChatGPT vollständig und erst dann die noch nicht abgenommenen AI-Dienste. Die generische Weboberfläche mit Links, Offline-HTML und Downloads bleibt separat testbar und darf nicht als AI-Providerbeweis gelten.

[[abwurf: „Schnell“ darf die Wartezeit verkürzen, aber nicht die Beweisfläche überspringen.]]

**Nachtrag zum eingeloggten Claude-Langlauf:**

Daniel öffnete eine echte Claude-Conversation `8d1e8d57-3f10-4792-8601-3dee7df52931` mit dem Titel „VPS-Verbindung“. Der erste Auto-Import lief fälschlich sofort am Ende aus: Die DOM-Nachrichten waren da, aber `chatScrollMetrics()` fand nur den Dokument-Scroller. Eine Playwright-Diagnose zeigte den echten Claude-Container als `overflow-y-auto` mit 55.763 Pixel Maximalstrecke und 432 Pixel Viewport.

Der Claude-Adapter hat nun `scrollContainer()`, und der gemeinsame Kern nutzt diesen Provider-Container. Nach Extension-Reload meldete der Operator exakt `y=55763 / max=55763`, `height=56195`, `viewport_height=432`, 9 DOM-verankerte Nachrichten und 4/5 User-/Assistant-Flächen. Das ist der entscheidende technische Beweis für den Fix.

Der anschließende Vollimport lief 174 Schritte mit 176 Checkpoints bis ganz nach oben und wieder ganz nach unten. Er erfasste 818 eindeutige Nachrichtenflächen, 386 User und 432 Assistant, sowie 22.942 technische Scanereignisse. Der Status bleibt korrekt `possibly_incomplete`: 84 von 175 Übergängen haben gemeinsame sichtbare Flächen, 91 sind unbelegt; außerdem blieb ein eingeklappter Bereich offen. Kein Vollständigkeitsclaim.

Der Recorder-Zugangsschlüssel wurde ausschließlich über das sichtbare Panel gesetzt. Danach wurde der lokale Puffer über den sichtbaren Flush-Button vollständig geleert: `queue_size=0`, `connected=true`, letzter bestätigter Batch 61, kein Fehler. Die 818er-Aufnahme ist damit serverseitig zugestellt, aber weiterhin als unvollständige Beweiskette klassifiziert.

**Nachtrag zum Claude-Test:**

Auf `https://claude.ai/login` wurde zunächst fälschlich `provider_id: web` sichtbar. Der breite Web-Bootstrap konnte den globalen Boot-Marker vor dem Claude-Bootstrap setzen; zusätzlich antwortete ein älterer `content.js` parallel. Der Web-Bootstrap ignoriert bekannte AI-Hosts nun, und der alte Claude-Livepfad läuft nur noch als Fallback, wenn der moderne Kern fehlt.

Nach Extension-Reload und Playwright-Neuladen liefert derselbe Login-Tab jetzt `provider_id: claude`, Adapter `1.0.1`, `conversation_id: null` und `authorized: false` wegen `provider_disabled`. Das ist der korrekte Blocker: Ohne Claude-Login und Conversation kein Inhaltstest, kein erfundener Erfolg.
**Nachtrag zur Beweisketten-Schärfung:**

Die aktuelle Claude-DOM-Prüfung zeigt stabile Artikelanker wie `aria-label="Nachricht 141 von 148"`. Der Adapter verwendet daraus nun `claude-user-message-141-of-148` beziehungsweise `claude-assistant-message-142-of-148`; die laufende Sichtfenster-Nummer bleibt nur noch Anzeigeinformation. Fällt die ARIA-Nummer weg, wird der vollständige sichtbare Text gehasht, nicht mehr die wechselnde Fensterposition.

Der automatische Sprung zum Anfang wird im Kern als `automatic_reanchor` protokolliert und nicht als unbelegter historischer Übergang gezählt. Erst die echte Bewegung vom stabilen Anfangsfenster in das nächste Fenster gehört zur Überlappungskette. Syntaxprüfung und `graphify update .` liefen erfolgreich; die Änderung ist im Commit `78af55a9d` gesichert.

Ein kurzer realer Playwright-Probelauf nach dem Extension-Reload bestätigte am Claude-Tab: Topfenster mit zwei Blöcken, Folgefenster mit drei Blöcken, ein gemeinsamer stabiler Assistant-Anker. Der danach nötige Sidepanel-Neustart ist noch offen, weil der Browserprozess unerwartet beendet wurde; Chromium wurde mit dem persistenten Desktop-Profil und der Runtime-Extension neu gestartet, Claude blieb eingeloggt und wurde wieder geöffnet. Ein langer Import darf erst nach sichtbarem Wiederöffnen des Panels als neuer Lauf begonnen werden.

Der neue lange Lauf wurde danach ausschließlich über die sichtbare Recorder-Seitenleiste und Playwright ausgeführt. Weil Chromium zunächst mit einem leeren `--disable-extensions-except=` gestartet war, wurde der Browser mit demselben Profil und explizitem Extension-Pfad neu gestartet; die Extension-ID `molhhdlenmhokfibmbojpapccaidfepi` war danach wieder sichtbar, Claude blieb eingeloggt und der Sitzungsschlüssel wurde erneut über das Panel gesetzt.

Der Claude-Autoimport erreichte nach 192 echten Scrollschritten das Seitenende. Der sichtbare Endstand lautet: 148 eindeutige Beiträge, 74 Daniel/Input, 74 AI-Strom/Output, 4 Textfortschreibungen, 23.041 technische DOM-Kontakte. Die stabile History-Beweiskette bestätigte 189 von 190 Übergängen; genau eine Lücke und ein möglicher Beweisfehler bleiben sichtbar. Deshalb blieb der Status korrekt `Import möglicherweise unvollständig`. Nach dem sichtbaren Flush war der IndexedDB-Puffer leer (`queue=0`, letzter Erfolg angezeigt); die Aufnahme ist zugestellt, aber nicht als vollständig behauptet.

**Nachtrag zum generischen Webseitenpfad:**

Die geladene Runtime-Referenz wurde erweitert: Der generische Webadapter erkennt jetzt den tatsächlichen inneren Scrollcontainer, prüft sichtbare Blöcke geometrisch im Viewport und segmentiert lange Artikel in einzelne Überschriften/Absätze/Listen statt in einen monolithischen `<article>`-Block. Links behalten Quelle, Text, Ziel und Position; die VPS-HTML rendert sie mit `target="_blank"` und `noopener noreferrer`.

Playwright-Tests liefen sichtbar auf Example Domain, tagesschau.de, einem Nachrichtenartikel, X, Facebook und ChatGPT. Der echte Fixture-Lauf erreichte das Seitenende nach 28 kontrollierten Schritten, bestätigte 5/5 Übergänge mit Überlappung, speicherte 3 Links und erzeugte `PAGE.md`, `PAGE.html`, `LINKS.json` und `MANIFEST.json`. Ein Offline-HTML-Klick öffnete die externe Quelle in einem neuen Tab. ChatGPT blieb nach Extension-Reload korrekt `adapter=chatgpt`; X und Facebook wurden als `adapter=web` erkannt.

Ein erster Fixture-Fehllauf lieferte wegen einer falschen URL die interne 404-Fehlerseite. Dieser Befund wurde nicht als Recorder-Erfolg gewertet; der anschließende Lauf auf der tatsächlichen Fixture-URL ist der gültige Nachweis. X ist nun nicht mehr fälschlich an den unfertigen Grok-Adapter gebunden; `grok.com` bleibt für einen späteren eigenen Adapter reserviert.

[[abwurf: Auf einer Nachrichtenseite ist ein Link nicht Dekoration, sondern eine weitere sichtbare Spur, die im Offline-Dokument wieder anklickbar bleiben muss.]]

**Fortsetzung Webmatrix und Quellparität:**

X wurde danach nicht nur erkannt, sondern sichtbar über die Seitenleiste aufgenommen: 14 Links, 6 Bereiche, 2/2 stabile Überlappungsübergänge und VPS-Export. Facebook wurde ebenfalls über denselben Weg geführt und exportiert: 38 Links und 1 sichtbarer Bereich. Der Facebook-Stand bleibt absichtlich kein Feed-Vollständigkeitsbeleg, weil der aktuelle sichtbare Zustand nur einen Bereich hergab.

Die getestete Geometrie wurde in `tools/chatgpt_browser_recorder/extension/` nachgezogen: Webadapter und Recorder-Kern nutzen nun innere Scrollcontainer, sichtbare Webblöcke und 70-Prozent-Schritte auch in der Quell-Extension. Syntax, Manifest, Diff-Check und Graphify waren danach grün. Laufzeitreferenz und Quelle tragen damit dieselbe generische Weblogik.

[[abwurf: Ein Seitenrand ist erst dann belastbar, wenn derselbe Pfad auch durch die Quelle wieder gebaut werden kann.]]

**AI-Fallback-Fortsetzung:**

Gemini wurde nach Extension-Reload sichtbar als generische Webseite aufgenommen. Die Seitenleiste war an `https://gemini.google.com/app` gebunden; der kurze Import speicherte 2 Bereiche und der Webexport erzeugte 29 Links sowie MD/HTML/LINKS/Manifest. Der Lauf wurde sichtbar beendet und blieb wegen der kurzen Probe korrekt unvollständig.

Für Gemini, Kimi, Meta AI und Copilot liefert `providerForUrl()` nun bewusst den generischen Webprovider, solange kein eigener Adapter gebaut ist. ChatGPT und Claude bleiben spezialisiert; `grok.com` bleibt als eigener Sonderpfad markiert. Playwright bestätigte bei Kimi, Meta AI, Copilot und Grok den geladenen Recorderkern und generische Adaptererkennung auf den erreichbaren Oberflächen. Das ist Fallback-Funktion, kein behaupteter semantischer Provideradapter.

[[abwurf: Ein Fallback darf eine Tür öffnen, aber nicht so tun, als wäre dahinter schon der passende Provider verstanden.]]

**Gemini-Dedicated-Fortsetzung:**

Die echte Gemini-Unterhaltung `2f7d866336404496` wurde nach Extension-Reload nicht mehr als Webseite, sondern sichtbar als `Gemini · 2f7d866336404496` erkannt. Der neue Adapter liest den echten inneren `infinite-scroller.chat-history`, trennt `USER-QUERY` und `MODEL-RESPONSE`, übernimmt Wrapper-IDs als stabile Beitragsanker und bewahrt Links, Medien sowie sichere eingeklappte Bereiche getrennt vom Seitennavigations-Scroller.

Der erste isolierte Adaptertest fand einen eigenen Fehler: User und Modell teilen sich in Gemini denselben `.conversation-container`; eine naive Carrier-Deduplizierung hätte pro Runde nur den User behalten. Der Fix dedupliziert nun mit `Wrapper + Rolle`. Der echte Playwright-Selbsttest meldet danach `status=passed`, `1 user / 1 assistant` im aktuellen sichtbaren Fenster und den Composer/Scroller korrekt erkannt.

Vom echten Anfangsanker aus wurden sechs reale Playwright-Wheel-Schritte ausgeführt. Gemini stellte dabei ein neues Paar (`27204f68c9226683`) bereit; die Seitenleiste meldete sechs von sechs überlappende Übergänge. Die kurzen Läufe wurden absichtlich abgebrochen und serverseitig als `possibly_incomplete` belassen: Gemini ist damit als Adapter technisch belegt, aber noch nicht als vollständige lange Historie abgenommen.

Die Recovery-Artefakte liegen unter `2026-08-13__Unterhaltung-mit-Gemini-Recovery__2f7d86633640-7f7d7e1827` mit zwei gespeicherten Beiträgen; der vorherige kurze Lauf enthält vier Beiträge unter dem Schwesterordner `...-8a66d81f7e`. Der VPS-Chat-Export wurde für den unvollständigen Lauf korrekt verweigert, weil noch keine abgeschlossene Live-Aufnahme vorlag. Der generische Offline-Webpfad bleibt davon getrennt.

[[abwurf: Der Provider ist erst wirklich verstanden, wenn der Recorder seine eigene erste falsche Annahme im echten DOM findet und sichtbar korrigiert.]]

**Gemini-Ende-zu-Ende-Sichtlauf:**

Ein separater Playwright-Lauf setzte den Gemini-Chat sichtbar an den Anfang, startete die Aufnahme über die Seitenleiste und bewegte anschließend den echten `infinite-scroller.chat-history` mit 81 realen Wheel-Schritten bis zum dynamischen End-Sentinel. Jede Messung blieb stabil; der gemessene Schritt lag bei 70 Prozent der frischen Containerhöhe, die kleinste Überlappung bei `0,3017` und damit über der 30-Prozent-Grenze.

Am Ende standen `top=16572`, `scrollHeight=16867`, `viewport=295`, 13 sichtbare User- und 13 Modellknoten. Die sichtbare Recorderbeweiskette meldete `69/81` Übergänge mit Überlappung und `12` unbelegte Übergänge. Das Artefakt ist deshalb sauber als `scroll_recording_stopped` beziehungsweise unvollständig klassifiziert, nicht als Vollständigkeitsbeweis.

Der entscheidende Unterschied zum vorherigen generischen Lauf ist jetzt belegt: Provider-ID und Titel sind Gemini, die Beiträge sind rollengetrennt, der innere Verlaufsscroller wird wirklich bewegt, und der Lauf endet am realen Rand. Links aus Gemini-Antworten werden mit `target="_blank"`-geeigneten Metadaten übernommen; ein kompletter VPS-Chat-Export bleibt bis zu einem vollständig abgeschlossenen Live-Import bewusst getrennt.

**Eingeloggte Social-/AI-Oberflächen:**

Daniel öffnete echte eingeloggte Tabs für X, Facebook und Grok. Nach einem Extension-Reload mussten X und Facebook einmal sichtbar neu geladen werden, weil bestehende Dokumente den Content-Script-Kern nicht rückwirkend erhalten. Danach meldeten beide per Playwright `core=true`, `adapter=web` und einen bestandenen generischen Selbsttest: X mit 3 sichtbaren Bereichen und 44 Links, Facebook mit 94 sichtbaren Bereichen und 35 Links.

X wurde über die Seitenleiste als `Webseite · web-0e4c523d-937d68f1` aufgenommen. Ein realer Dokument-Wheel-Test speicherte 8 eindeutige Bereiche und 19 DOM-Kontakte; der Feed lud währenddessen dynamisch nach, daher bleibt es ein Teilbefund. Facebook wurde als `Webseite · web-c24d25fc-1ad6b210` aufgenommen und speicherte im kurzen Kontrollschritt 5 eindeutige sichtbare Bereiche. Keiner dieser kurzen Läufe wird als Feed-Vollständigkeit ausgegeben.

Grok war zunächst der einzige Blocker, weil der unfertige Spezialpfad den generischen Bootstrap ausschloss. Das Routing verwendet nun für `grok.com` den Webprovider, während der Katalogeintrag als spätere semantische Adapterspur erhalten bleibt. Nach Extension-Reload meldete Grok `Webseite · web-608877f7-d982fae7`, `Adapter erkannt`; ein realer Wheel-Schritt speicherte einen sichtbaren Bereich. Auch das ist bewusst generischer Fallback, keine behauptete Grok-Semantik.

[[abwurf: Eingeloggt sein öffnet die Oberfläche, aber erst der sichtbare Wheel-Weg zeigt, ob der Recorder wirklich darin ankommt.]]

**Local-only-Finish und Webseitenabbild:**

Der erste reale Webseitenlauf auf `tagesschau.de` hat einen echten Abschlussfehler
freigelegt: Die Referenz-Queue versuchte ohne Zugangsschlüssel für jeden sichtbaren
Webblock zuerst den Netzwerkpfad. Danach serialisierten zusätzlich Badge- und
Statusschreibungen den lokalen Puffer. Ein Lauf mit 202 DOM-Kontakten blieb deshalb
bei `stopped_for_manual_finish` hängen, `last_import_result` wurde nicht gesetzt.

Die Referenz behandelt fehlende Schlüssel nun als normalen lokalen Modus. Nach
`IndexedDB.add()` wird das Ereignis sofort als lokal gepuffert beantwortet; Badge und
Diagnosestatus laufen entkoppelt. Der VPS-Versand bleibt sichtbar und getrennt. Der
Fix liegt in `8ef91909a`, die begleitende README-Erklärung in `a18d441f4`.

Der kleine echte Kontrollfall `https://example.com/` lief danach über die sichtbare
Seitenleiste: drei Webblöcke wurden gesichert, und ein Stop-Poll wechselte innerhalb
eines Durchlaufs auf `running=false`, `status=scroll_recording_stopped`. Das ist ein
beendeter sichtbarer Abschnitt, kein Vollseiten- oder Vollständigkeitsbeweis.

Der Offline-HTML-Generator lieferte für diesen Fall 16.559 Zeichen; Chrome meldete
für den Blob-Download 16.581 Bytes. Das Snapshot-Fragment selbst hatte 299 Zeichen,
`script=0`, `style=0`, `form=0`, einen Link und die Policy
`visible_dom_sanitized_no_scripts_no_form_values_no_hidden_dom`. Die zwei Script-Tags
im Gesamt-HTML gehören zur Offline-Exportoberfläche und nicht zum eingebetteten
Webseitenfragment. Der Playwright-Downloadpfad zeigte dabei irreführend eine
0-Byte-Temporärdatei; die Chrome-Downloads-API bestätigte den tatsächlichen
16.581-Byte-Abschluss.

[[abwurf: Lokales Puffern ist erst dann eine gute Rückfallebene, wenn Stoppen nicht auf den fehlenden Schlüssel wartet.]]

**ChatGPT-/Claude-Abnahme des sichtbaren Webseitenabbilds:**

Nach dem Reload der beiden eingeloggten Tabs meldeten ChatGPT und Claude jeweils
`authorized=true`, `adapter_status=passed` und einen bestandenen eigenen DOM-
Selbsttest. ChatGPT wurde mit 6 Beiträgen erkannt (3 User, 3 Assistant), Claude
mit 9 Beiträgen (4 User, 5 Assistant). Die Providerpfade bleiben dabei getrennt;
der gemeinsame Snapshot-/Exportkern nimmt ihnen nichts von ihrer jeweiligen
Rollen- und Providererkennung weg.

Der direkte lokale Exporttest lieferte bei ChatGPT 135.384 Zeichen sichtbares
DOM und bei Claude 88.541 Zeichen. Beide Snapshots waren ungekürzt, hatten
`root=body`, null Script-Tags, null Formulare und verwendeten die Policy
`visible_dom_sanitized_no_scripts_no_form_values_no_hidden_dom`. ChatGPT brachte
45 sichtbare Links mit, Claude 10. Das ist ein belastbarer Abbildbeleg für die
aktuelle Oberfläche, aber kein Anspruch auf unsichtbare, nachladbare oder nicht
gerenderte Daten.

Der Snapshot sitzt jetzt im gemeinsamen Recorderkern und wird in JSON vollständig,
im Offline-HTML als sichtbares bereinigtes DOM und im Markdown mit Quell-URL,
Größe und Linkverzeichnis ausgegeben. Die Kernänderung ist in `0e85a8aa7`
committet; der danach aktualisierte Wissensgraph liegt in `c89c3b2a0`.

[[abwurf: ChatGPT und Claude brauchen verschiedene Augen — aber der Export darf ihnen denselben sauberen Beweisrahmen geben.]]

**Sichtbarer Wheel-/Stop-Nachweis für ChatGPT und Claude:**

Ein zusätzlicher kontrollierter Lauf startete beide Oberflächen jeweils über
die sichtbare Seitenleiste, bewegte den gefundenen inneren Chat-Scroller mit
einem echten Playwright-Wheel und beendete anschließend sichtbar. Claude meldete
nach dem Schritt 9 erkannte Beiträge (4 User, 5 Output), eine belegte Überlappung
und danach `Scroll-Aufnahme beendet`.

ChatGPT beendete ebenfalls sauber mit `scroll_recording_stopped`. Während der
kurze Lauf zunächst `neu gespeichert=0` zeigte, meldete der isolierte Zustand
danach `recognized=10`, `blocks=10` und `viewportBlocks=2`; die Null war damit
kein DOM-Ausfall, sondern die Folge bereits lokal vorhandener stabiler IDs. Der
Recorder unterscheidet hier korrekt zwischen erkanntem Material und neuen
Speicherungen. Beide Tabs hatten danach `running=false`.

Die ältere Paketquelle unter `tools/chatgpt_browser_recorder/extension/` bleibt
als eigene, serverorientierte Provenienzschicht erhalten. Dort existiert kein
lokaler `export_engine.js`; eine automatische Vermischung mit dem live
getesteten Referenzpfad würde Exportarchitekturen überschreiben statt ergänzen.

[[abwurf: Eine Null bei „neu“ ist kein leerer Chat, wenn der Beleg ausdrücklich zehn bereits bekannte Beiträge zeigt.]]

**Sichtbares Medienmanifest:**

Beim nächsten gemeinsamen Export-Ring fiel auf, dass sichtbare Medien zwar als
DOM-Elemente im Snapshot vorkamen, aber bei lazy geladenen oder dynamischen
Quellen nicht zuverlässig eine brauchbare `src`-Spur behalten mussten. Der
Recorder ergänzt deshalb jetzt für sichtbare `img`, `video` und `audio` eine
begrenzte Medienliste mit Typ, sicherer Quelle, Poster, Alt-/Titeltext,
Abmessungen und Kennzeichnung eingebetteter Daten.

Vor dem Sanitizing übernimmt der Snapshot nach Möglichkeit den tatsächlich
gerenderten `currentSrc` beziehungsweise `poster`. Unsichere Protokolle,
Sessiondaten und versteckte Medien bleiben draußen. JSON trägt das Manifest
vollständig; Markdown zeigt eine Medien-Tabelle; Offline-HTML weist die Zahl
sichtbarer Medien aus und enthält die normalisierte DOM-Projektion. Der
Fachcode ist in `54cd58c5b`, der Graphstand in `25bc690eb` gesichert.

Der erste Sammeltest mit wechselnden Tabs wurde nicht als Beleg missbraucht:
Der Panel-Harness blieb nach dem ersten Öffnen an der alten Claude-Bindung,
obwohl die Ziel-Tabs wechselten. Der ChatGPT-Medienwert `2` ist deshalb der
einzige Live-Medienwert, den dieser Lauf belastbar ausweist; die Generator-
Prüfung mit synthetischem Medienmanifest war für HTML, Markdown und JSON grün.

[[abwurf: Ein Medienbild ist erst wirklich mitgenommen, wenn nicht nur sein Tag, sondern auch seine sichtbare Quelle und seine Herkunft erhalten bleiben.]]

**Vom Webseitenabbild zum Crawlrecorder:**

Daniel wollte den Recorder für `https://flextrawurst.de/` zu einem Crawlrecorder
erweitern: nicht nur ein Chatfragment, sondern die UI, Texte, gerenderten Styles,
Links und sichtbaren Medien einer Website sollen als Offline-HTML mitgetragen
werden. Ich habe den Auftrag als benutzer gestarteten same-origin Browser-Crawl
verstanden. Ein ungebremster Spider oder ein Rohdump versteckter Daten wäre eine
andere Behauptung über die Herkunft der Seite.

Der Referenz-Recorder besitzt nun eine eigene Crawl-IndexedDB mit Jobs und Seiten,
einen dedizierten Hintergrund-Tab und eine begrenzte BFS-Warteschlange. Start-URL,
maximale Seitenzahl und Tiefe sind sichtbar einstellbar. Der Crawl bleibt auf der
Origin der Startseite, entfernt Hash-Fragmente, sichert jede Seite als eigenes
HTML-Abbild und dokumentiert Status, Fehler, Tiefe, Größen, Links und Asset-
Grenzen. Der Einstieg liegt in `core/crawl_db.js` und `core/crawl_recorder.js`;
die Steuerung sitzt in `background.js` und `sidepanel.js`.

Die Capture-Funktion entfernt Scripts, Noscript, Templates, Frames, Formulare und
Eventhandler, bewahrt aber `html/head/body`, sichtbare UI-Knoten, Inline-Styles,
Klassen, sichere Struktur-Data-Attribute und statische Bedienflächen. Sichtbare
HTTPS-Stylesheets können bis zur Asset-Grenze als Data-URL inline kommen; Medien
bleiben auf same-origin begrenzt. Der Export ist ein einzelnes Offline-HTML mit
Seitenliste und isoliertem `iframe sandbox`; die gecrawlten Seitenskripte werden
nicht wieder ausgeführt.

Der erste echte Flextrawurst-Lauf mit drei Seiten und Tiefe 1 erreichte die
Seitenbegrenzung sauber. Die Startseite lieferte 164.416 HTML-Zeichen, 16.530
Textzeichen und 41 interne Links; `what-is-flextrawurst.html` lieferte 7.604
Zeichen. Ein früher Vor-Sichtbarkeitslauf hatte `faq.html` fälschlich nur mit
66 Zeichen erfasst und wird deshalb nicht als Befund verwendet. Ein separater Tiefe-0-Lauf blieb bei genau
einer Seite und 163.190 Zeichen. Nach dem Sichtbarkeitsfix wurde die externe
Google-Font-CSS mit 27.241 Bytes inline übernommen; der Startseitenexport lag
danach bei 200.618 Zeichen, ohne Script- oder Form-Tags. Der Offline-Atlas-
Generator wurde mit echten gespeicherten Crawl-Seiten geprüft.

Der Crawl ist bewusst als `limit_reached` gültig, wenn noch Links in der
Warteschlange liegen. Das ist kein Vollständigkeitsclaim. Die noch offenen
Verbesserungen sind vor allem rekursive Font-/CSS-Asset-Auflösung, stabile
Fortsetzung nach Service-Worker-Schlaf und ein visueller Vergleich des Offline-
Atlas gegen die echte Oberfläche. Der Fachcode ist in `98c1d6033`, der Graphstand
in `00fd8a844` gesichert.

[[abwurf: Eine 1:1-Kopie beginnt nicht mit dem Klauen des Rohdokuments, sondern mit dem ehrlichen Nachweis, welche sichtbare Seite unter welcher Grenze wirklich mitgekommen ist.]]

**Expliziter 30-Tab-Chunk-Crawl:**

Daniel hat die Crawl-Idee weiter präzisiert: Das normale Aufzeichnen darf nicht
heimlich in einen Seitenscanner kippen. Der Crawl braucht einen eigenen Start-
Knopf und soll bis zu 30 gefundene Seiten in eigenen Browser-Tabs abarbeiten,
jeden Tab von 0 bis 100 Prozent in Stücken, mit sichtbarem Zwischenstand und
einem späteren Offline-Abbild.

Der Crawlrecorder erzeugt nun pro gefundener Seite einen eigenen inaktiven Tab.
Der jeweilige Tab wird zuerst auf Position 0 gesetzt und danach mit 70 Prozent
der sichtbaren Scrollerhöhe weiterbewegt; dadurch bleiben mindestens 30 Prozent
Überlappung. Jeder Schritt speichert Tab-Progress, Chunknummer, Scrollposition,
Seitenhöhe, Status und Fehler. Nach dem letzten Chunk wird die Seite mit Asset-
Abbild als abgeschlossen markiert. Die Seiten-Tabs bleiben für die Sichtprüfung
offen; der Chat-/Webrecorder nimmt diese Bewegung nicht als normale Aufnahme auf.

Der Zwei-Tab-Livebeleg auf Flextrawurst lief exakt so: Tab 1 erreichte `100 %`
nach 20 Chunks und `top=5749/max=5749`; Tab 2 erreichte `100 %` nach 9 Chunks
und `top=2922/max=2922`. Der Gesamtstatus `limit_reached` bedeutete nur, dass
das absichtlich gesetzte Seitenlimit zwei Seiten erreicht hatte. Der separate
Stop-Test wurde bei 16 Prozent angefordert und endete zwischen Chunks bei 22
Prozent, 5 Chunks und `complete=false, stopped=true`; der Teilstand blieb im
Crawl-Speicher erhalten.

Die Seitenleiste zeigt jetzt eine eigene Crawl-Karte mit maximal 30 Tabs/Seiten,
Tiefe, globalem Status und einer Zeile je Tab. Der Offline-Atlas übernimmt die
Chunkkarte als Metadaten (`Chunks`, Abdeckung, Hash, Wiederverwendung), ohne
identische Chunk-HTMLs unnötig zu vervielfachen. Der tabweise Fachcode ist in
`b12db0339`, der Graphstand in `4128802d6` gesichert.

[[abwurf: Jeder Tab bekommt seine eigene Zeit — erst wenn seine 100 Prozent sichtbar sind, darf die Seite als fertig gelten.]]
