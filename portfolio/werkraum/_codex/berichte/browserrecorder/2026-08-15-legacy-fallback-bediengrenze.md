# Abnahme: Legacy-Fallback bleibt sichtbar und bedienergebunden

EVIDENCE_VERSION: 1

Datum: 2026-08-15 15:26 +0200  
Ort: isolierte Chromium-Erweiterung; Quellprüfung des Claude-Kompatibilitätsfallbacks

## Eine Änderung

Der alte Fallback reagierte auf `recorder_start_import` bisher mit eigener
Navigation zum Anfang, automatischem Scrollen bis zum Ende und Klicks auf
eingeklappte Bereiche. Diese drei impliziten Aktionen wurden entfernt. Der
Fallback liest beim Start nur den aktuell sichtbaren Bereich und liest bei
weiterem eigenem Scrollen erneut sichtbare Bereiche.

## Sichtbares Ergebnis

Im isolierten Erweiterungsfenster blieb die UI ausführbar. Die Importdarstellung
zeigte beim frischen Zustand `autoExpandDefault: false`; die erzeugte Sichtprobe
liegt unter `/tmp/dak-recorder-ui-security.png`. Die Screenshotansicht zeigt den
Recorder selbst, nicht eine echte Claude-Fallback-Seite.

## Rücklese und Gegenprüfung

Der Live-UI-Test las DOM und Quellartefakt erneut:

- HTML-Injektion blieb Text: `activeNodes: 0`.
- Neue Aufnahme: `autoExpandDefault: false`.
- `content.js` enthält kein `window.scrollTo` und kein `button.click()` mehr.
- Der Fallback kennzeichnet `scope: "visible_scrolled_range"`,
  `automatic_navigation: false` und `automatic_expand: false`.
- `node --check` für Core, Fallback und Seitenleiste war grün.

## Ehrliche Grenze

Die echte Claude-Seite ohne modernen Core wurde in diesem Lauf nicht geöffnet;
deren Fallback-Lauf ist daher als `nicht live geprüft` zu behandeln. Bewiesen ist
die Entfernung der automatischen Navigation aus dem ausgelieferten Fallback,
nicht die Vollständigkeit einer Claude-Aufnahme.

## Marker

- REC-GATE-001: PASS — der Vertragssatz der Recorder-Skills ist vorhanden;
  Evidence-Gate wurde ausgeführt.
- REC-CRAWL-001: PASS — der geprüfte Fallback folgt keiner URL, scrollt nicht
  selbst und öffnet nichts implizit; sichtbarer Bereich bleibt begrenzt.
- REC-FETCH-001: PASS — Fetch-/Asset-Provenienz wurde in dieser Änderung nicht
  berührt; die separate Fetch-Abnahme bleibt der maßgebliche Beleg.
- REC-EYE-001: PASS für die isolierte UI-Abnahme; echter Claude-Fallback:
  `nicht geprüft`.
- REC-DOC-001: PASS — Aktion, sichtbares Ergebnis, Rücklese und offene Grenze
  stehen in dieser Markdown-Abnahme.

OUTCOME: PASS

## Aussage

Ein Aufnahme-Klick im Fallback behauptet keine Vollständigkeit mehr. Vollständige
historische Automatik ist nur im modernen, ausdrücklich beschrifteten
Automatikpfad vorhanden; auch dort bleibt sie ein eigener Bedienvorgang und kein
Beleg menschlichen Lesens.
