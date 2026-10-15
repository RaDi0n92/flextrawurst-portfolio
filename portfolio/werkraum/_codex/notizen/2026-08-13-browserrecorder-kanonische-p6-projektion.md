---
datum: 2026-08-13
betrifft: [browser-recorder, playwright, p6, kanonische-textprojektion, p7]
importable: false
autor: codex bei Daniels VPS
---

# Browser Recorder — kanonische P6-Projektion

## Was ich gelesen habe

Ich habe die 27 Ziel-Differenzen der Post-Reload-Sichtung gegen die alte P6-Basis gelesen und anschließend ihre sichtbaren DOM-Körper mit Playwright erneut geprüft. Alle 27 Ziel-IDs wurden gesehen; ihre neuen Hashes stimmten mit dem Post-Reload-Lauf überein.

Der DOM-Befund zeigte zwei UI-Projektionen: `Mehr anzeigen` lag in einem separaten Button, und Plugin-Mentions erschienen als strukturierte `data-inline-selection-pill`-Elemente mit echtem `data-keyword`, während das sichtbare Icon nur den Buchstaben `M` trug.

Ich habe deshalb den read-only P6-Reader und beide ChatGPT-Adapterquellen angepasst. Danach wurden Extension und Chat-Tabs per Playwright neu geladen und fünf vollständige kanonische P6-Läufe ausgeführt.

## Was ich verstehe

Die vorherigen 17 Textdifferenzen waren zum Teil keine Gesprächsänderungen, sondern Unterschiede der sichtbaren UI-Projektion. Ein Vergleich muss den Nachrichtentext aus dem eigentlichen Content-Subtree lesen, UI-Steuerungen ausschließen und strukturierte Mentions stabil repräsentieren.

## Was ich nicht verstehe

Die verbleibenden 17 `changed-text`-Fälle sind nach der Kanonik weiterhin offen. Sie sind deutlich weniger geworden, aber noch nicht einzeln semantisch bewertet. P7 darf deshalb noch nicht freigeschaltet werden.

## Was mich interessiert

Mich interessiert, welche der 17 verbleibenden Fälle echte nachträgliche Inhaltsänderungen sind und welche aus Markdown-/Renderdetails stammen, die noch nicht in der Kanonik abgebildet werden. Dafür reicht kein weiterer Vollscan; es braucht eine gezielte, textnahe Gegenüberstellung.

## Was zusammenhängt und wie

Playwright liest die echte Chatoberfläche. Der P6-Reader erzeugt daraus read-only Recovery-Artefakte. Die kanonische Funktion entfernt Buttons und SVGs aus einer Kopie des Content-Subtrees und ersetzt Mention-Pills durch `@data-keyword`. Der lokale Vergleich liest danach nur diese normalisierte Textspur gegen die historische Quelle.

## Was konzeptionell darin steht

Ein sichtbarer Text ist nicht automatisch der Gesprächsinhalt. UI darf den Inhalt darstellen, einklappen, markieren oder mit Icons versehen. Die Provenienzprüfung braucht deshalb eine eigene, explizite Leseschicht, die sichtbar bleibt und nicht behauptet, rohe UI-Projektion sei schon Semantik.

## Was mich heute beschäftigt hat

Der kleine Buchstabe `M` im DOM war kein Gesprächsbuchstabe, sondern das Icon einer Mention. Gleichzeitig war `Mehr anzeigen` zwar in `innerText`, aber nicht im eigentlichen Beitrag. Genau solche kleinen Schichten hatten den Vergleich unnötig laut gemacht.

## Was mich noch beschäftigt

191 Matches sind ein großer Fortschritt gegenüber 171, aber die 293 fehlenden Live-IDs bleiben unverändert. Die Verbesserung erklärt also die Projektion, nicht die gesamte historische Unvollständigkeit.

## Tiefer eingetaucht

Die kanonischen Läufe ergaben 90, 31, 82, 103 und 38 Records. Alle fünf erreichten den End-Sentinel, alle Fenster waren stabil, und kein Lauf hatte einen Fehler. Der eine Chat-3-Home-Randfall wurde separat per dreifachem Playwright-Home behoben und danach vollständig wiederholt.

## Wie sich dieser Tag / diese Session angefühlt hat

Wie das Abziehen einer falschen Folie von einem Messgerät. Die Daten wurden nicht besser gemacht; die Sicht auf sie wurde präziser. Das ist weniger spektakulär, aber genau die Art von Fortschritt, der später trägt.

## Warum dieser Code / diese Datei wohl existiert

Der P6-Reader existiert, um sichtbare historische Chatbereiche unabhängig und read-only zu prüfen. Der Adapter existiert, um dieselbe kanonische Textprojektion auch im echten Recorderpfad zu verwenden.

## Was ich beim Bauen brauche

Ich brauche weiterhin Playwright für jeden Browserkontakt: Reload, Fokus, Home, Wheel, DOM-Snapshot und sichtbare Sidepanel-Bindung. Python darf danach nur lokale Artefakte und Hashes vergleichen.

## Was noch fehlt bevor wir bauen können

Es fehlt kein weiterer UI-Bau, bevor die 17 verbleibenden Differenzen gezielt analysiert werden. Erst danach kann eine P7-Entscheidung sinnvoll und belegbar sein.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht**

Der Recorder soll zwischen Darstellung und Aussage unterscheiden können. Ein Mention-Icon, ein Aufklappknopf und der eigentliche Beitrag gehören zusammen, sind aber nicht dasselbe. Die kanonische Textspur bewahrt diese Grenze.

**Code-Skizze**

```javascript
function canonicalMessageText(node) {
  const source = node.querySelector(
    '[data-testid="collapsible-user-message-content"]'
  ) || node;
  const clone = source.cloneNode(true);
  clone.querySelectorAll(
    'button, [role="button"], [aria-expanded], svg, script, style'
  ).forEach((element) => element.remove());
  clone.querySelectorAll(
    '[data-inline-selection-pill][data-keyword]'
  ).forEach((pill) => {
    pill.replaceWith(document.createTextNode(`@${pill.dataset.keyword}`));
  });
  return (clone.innerText || clone.textContent || '')
    .replace(/\s+/g, ' ').trim();
}
```

## Was ich mir merken will

`innerText` des äußeren Message-Containers ist für P6 nicht kanonisch genug. Vor dem Vergleich müssen UI-Kontrollen und strukturierte Inline-Elemente bewusst behandelt werden.

## Dokumente gehören zusammen

Zusammengehören: der P6-Reader, beide ChatGPT-Adapterquellen, die fünf kanonischen Recovery-Dateien, der kombinierte kanonische Vergleich, der Playwright-Zieldelta-Bericht und die Isolation-Gates. Die alten VPS-Ordner bleiben unveränderte Quelle.

## Was mich überrascht hat

Eine einzige Mention-Projektion erzeugte in mehreren Chats systematisch einen zusätzlichen sichtbaren Buchstaben. Der Buttontext `Mehr anzeigen` wurde ebenfalls nur bei langen Beiträgen angehängt. Zwei kleine DOM-Details erklärten einen großen Teil der scheinbaren Textänderungen.

## Wenn wir das bauen

**Vision-Schicht**

Wir bauen keine Maschine, die Oberfläche mit Wahrheit verwechselt. Wir bauen eine Sichtung, die sichtbar macht, welche Teile Darstellung, welche Teile Herkunft und welche Teile eigentlicher Beitrag sind.

**Code-Skizze**

```python
assert all(r["errors"] == 0 for r in canonical_runs)
assert all(r["at_bottom"] for r in canonical_runs)
assert canonical_compare["classification_counts_total"]["match"] == 191
assert isolation_gate["status"] == "p6_isolation_passed"
```

Der nächste Schritt ist die gezielte Analyse der 17 verbleibenden Differenzen, weiterhin mit Playwright für jede erneute Chatprüfung.

## Resonanz

[[abwurf: Die Daten wurden nicht besser gemacht; die Sicht auf sie wurde präziser.]]

## Die Schichten des Systems — wie ich sie jetzt sehe

Browseroberfläche, UI-Projektion, Extension-Adapter, Receiver, Recovery-Ordner, P6-Vergleich und P7-Gate sind getrennte Schichten. Der Fehler lag in einer zu groben Textkante zwischen Browseroberfläche und Vergleich.

## Was das Gespräch hinzugefügt hat

Daniels klare Playwright-Vorgabe hat die Korrektur an der richtigen Stelle gehalten: nicht in einer direkten API, nicht durch Dateien, sondern durch sichtbare DOM-Lesung und echte UI-Navigation.

## Vergessen-Wollen

Vergessen werden soll die Zahl 171 als endgültiger Befund. Sie war ein Zwischenstand mit UI-Leckage. Der kanonische Stand ist 191, aber auch dieser bleibt ein Zwischenstand, solange 17 Differenzen ungeklärt sind.

## Was fehlt noch

- gezielte Playwright-Analyse der 17 verbleibenden `changed-text`-Fälle;
- Entscheidung, ob diese echte Revisionen oder weitere kanonische Renderdetails sind;
- P7 bleibt bis dahin `false`.
