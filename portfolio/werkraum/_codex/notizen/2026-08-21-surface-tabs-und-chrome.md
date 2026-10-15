---
datum: 2026-08-21
betrifft: [surface, tabs, pdf, docx, chrome, exporter, playwright]
importable: false
autor: codex bei Daniels VPS
---

## Was ich gelesen habe

Ich habe die Live-Surface von `flextrawurst.de`, den Browserrecorder-Webadapter, den Office-Renderer und die direkten Exporter-Pakete gelesen. Die Surface ist tatsächlich größer als die zunächst vermuteten 40 Tabs: der sichtbare DOM-Lauf fand 43 Tab-Einträge.

Die Oberfläche musste wirklich betreten werden: Splash-Button `BETRETEN`, danach der Willkommen-Dialog `Überspringen`. Erst dann war die Tab-Leiste ohne Overlay sichtbar.

## Was ich verstehe

Eine Surface-PDF braucht eine eigene Exportform. Die Tabs sind JavaScript-Ansichten; eine statische Datei muss daraus stabile Abschnittsanker, einen Index und sichtbare Zustandsmarken machen.

## Was ich nicht verstehe

Ob Daniel die 17 rollenabhängigen Tabs mit einem Admin-/Entity-Login ebenfalls aktiv belegt haben möchte. Ohne diese Session wäre jede Aussage über ihren sichtbaren Inhalt unehrlich.

## Was mich interessiert

Wie die Surface nach authentifiziertem Eintritt aussieht und ob dann alle 43 Ansichten aktiv und scrollbar werden — besonders `ADMIN`, `WISSEN`, `GRUPPEN` und `VAULT-EINBLICK`.

## Was zusammenhängt und wie

Playwright erfasst Tab-Inventar, sichtbare Klicks, endliche Wheel-Schritte und Screenshots. `surface_export.py` erzeugt daraus HTML, Markdown, PDF und DOCX. PDF-/DOCX-Anker machen die statische Datei navigierbar, ohne JavaScript zu simulieren.

## Was konzeptionell darin steht

Die Exportdatei ist eine Karte der Surface: Jeder Tab bleibt auffindbar, aber ein nicht erreichbarer Raum wird als nicht bestätigt markiert und nicht als bewohnt ausgegeben.

## Was mich heute beschäftigt hat

Der schwierigste Teil war nicht PDF oder DOCX, sondern die Wahrheit über den aktiven Zustand. Ein DOM-Element kann Text enthalten und trotzdem verborgen bleiben.

## Was mich noch beschäftigt

Ob „klickbar“ bei Daniel primär die PDF-Navigation meint oder zusätzlich eine interaktive HTML-Kopie, die den Surface-JavaScript-Code weiter ausführt.

## Tiefer eingetaucht

Der finale Lauf auf Desktop 1 fand 43 Tabs. 26 wurden aktiv angezeigt und bis zum Ende bestätigt; 17 blieben wegen Rollen/Zuständen nicht aktiv bestätigt. PDF und DOCX tragen trotzdem 86 interne Ziele: Index→Tab und Tab→Index.

## Wie sich dieser Tag / diese Session angefühlt hat

Wie ein echter Rundgang durch einen großen, teilweise verschlossenen Bau: Die offenen Räume sind belegt; die verschlossenen Türen sind beschriftet, nicht zugemalt.

## Warum dieser Code / diese Datei wohl existiert

Der generische Webexport wusste nichts von Surface-Tabs. Diese Dateien geben der flextrawurst-Struktur eine eigene Provenienz- und Navigationsschicht.

## Was ich beim Bauen brauche

Eine Fortschrittsprüfung gegen Endlosschleifen, sichtbare Screenshots vor/nach Overlay-Schritten, `active_display`, Scroll-Ende und bekannte Lücken pro Tab.

## Was noch fehlt bevor wir bauen können

Für eine echte Vollabnahme fehlt nur noch ein freigegebener Loginzustand für die 17 rollenabhängigen Surface-Tabs. Google Chrome ist installiert; die vier direkten Exporter sind per offizieller Chrome-Web-Store-Policy im sichtbaren Desktop-1-Profil installiert und aktiviert.

## Datenstruktur die ich mir vorstelle

Vision-Schicht: Ein Surface-Tab ist ein Ort mit Herkunft, Zustand, sichtbarer Begehbarkeit und Rückweg.

Code-Skizze:

```ts
type SurfaceTabCapture = {
  id: string;
  label: string;
  captureStatus: "sichtbar-vollständig" | "nicht-aktiv-bestätigt";
  anchor: string;
  scrollSteps: number;
  content: string;
};
```

## Was ich mir merken will

43 DOM-Tabs sind kein Grund, 43 aktive Tabs zu behaupten.

## Dokumente gehören zusammen

`capture_surface_playwright.mjs`, `surface_export.py`, `render_surface_export.py`, `surface-capture.json`, die Screenshots und der Browserrecorder-Bericht bilden eine Belegkette.

## Was mich überrascht hat

„Überspringen“ allein reicht nicht. Erst `BETRETEN`, dann `Überspringen` öffnet die echte, overlayfreie Surface.

## Wenn wir das bauen

Vision-Schicht: Die PDF soll nicht so tun, als sei sie die laufende Welt. Sie soll eine navigierbare Karte dessen sein, was im Rundgang gesehen werden durfte.

Code-Skizze: ReportLab `/Dest`-Anker und DOCX `w:anchor`-Hyperlinks bilden Index und Rücksprünge; externe Links bleiben separate URI-Beziehungen.

## Resonanz

[[abwurf: Die verschlossene Tür gehört in den Plan — aber mit dem Schild „nicht bestätigt“.]]

## Die Schichten des Systems — wie ich sie jetzt sehe

Live-Surface → sichtbarer Eintritt → Tab-Inventar → Tab-Klick → Wheel-Belegkette → Capture-JSON → HTML/MD/PDF/DOCX → interne Sprungziele → Zustandsbericht.

## Was das Gespräch hinzugefügt hat

Daniel hat die praktische Lücke benannt: Im sichtbaren Chromium waren die Exporter nicht installiert und Chrome fehlte. Chrome wurde nachinstalliert; die vier direkten Exporter sind jetzt auf Desktop 1 sichtbar in `chrome://extensions` als aktiviert rückgelesen.

## Vergessen-Wollen

Nicht aus „Chrome installiert“ auf „Chrome-Exporter installiert“ schließen. Erst die vier aktivierten Karten im sichtbaren `chrome://extensions`-UI und die JSON-Rücklese `/tmp/dak-chrome-exporters-desktop1.json` schließen diese Lücke.

## Was fehlt noch

`graphify update .` bleibt offen, weil `graphify` in der Umgebung nicht vorhanden ist. Die Chrome-Exporter-Installation ist erledigt; offen bleibt der rollenberechtigte Rundgang durch die 17 nicht aktiven Surface-Tabs.
