---
datum: 2026-08-12
typ: konzeptdokumentation
status: offen
betrifft: [browserrecorder, playwright, ui-visible-conversations, export, audit, redteam]
autor: codex bei Daniels VPS
---

# Browserrecorder: 99 Ideen, Redteam und verbesserter Workflow

## Auftrag

Ziel ist eine beweisbare Kette:

`Chat sichtbar → Sichtung gespeichert → Nachricht eindeutig → VPS-Artefakt versiegelt → Download gehasht → alles identisch`

Die fünf parallelen Chats dürfen nicht nur Dateien erzeugen. Für jeden Chat muss nachvollziehbar sein, was sichtbar war, was der Recorder eindeutig erkannt hat, was auf dem VPS liegt und ob der Download exakt dieselben Bytes enthält.

Diese Fassung ist die verdichtete Endfassung des 99-Ideen-/Redteam-/Verbesserungsdurchlaufs. Jede Idee besteht aus Ausgangsgedanke, Angriff und verbesserter Form.

## 1–11: Wahrheitsquelle

1. DOM als Quelle — Redteam: Virtualisierung unterschlägt Nachrichten. Verbesserung: überlappende Sichtfenster plus Anfangs-/Endbeweis.
2. ChatGPT-Export als Quelle — Redteam: Er ist nicht zwingend derselbe sichtbare Zustand. Verbesserung: nur als Vergleichsquelle verwenden.
3. Recorder als Quelle — Redteam: Der Recorder selbst kann Lücken haben. Verbesserung: Lücken unveränderlich protokollieren.
4. VPS als Quelle — Redteam: Der VPS kann unvollständig sein. Verbesserung: Nur versiegelte Zustände dürfen vollständig heißen.
5. Download als Quelle — Redteam: Eine Datei kann nachträglich verändert werden. Verbesserung: SHA-256 plus unveränderliches Manifest.
6. Screenshot als Beweis — Redteam: Text ist nicht maschinenprüfbar. Verbesserung: Screenshot nur als visuellen Zusatzbeleg nutzen.
7. Browser-History als Beweis — Redteam: Sie enthält keine Nachrichteninhalte. Verbesserung: Nur für Tab-/Zeitzuordnung nutzen.
8. Zeitstempel als Ordnung — Redteam: Millisekunden können gleich sein. Verbesserung: Lokale Sequenznummer ergänzen.
9. CSS-Position als Ordnung — Redteam: Layouts können sich ändern. Verbesserung: Stabilen Message-Key ergänzen.
10. Sichtbare Rollen als Semantik — Redteam: Thinking-Blöcke haben oft keine Rolle. Verbesserung: `unknown` zulassen und nie still zuordnen.
11. „Datei existiert“ als Erfolg — Redteam: Existenz sagt nichts über Vollständigkeit. Verbesserung: Erfolg nur bei kompletter Beweiskette.

## 12–22: Tab- und Session-Isolation

12. Alle fünf Tabs parallel scannen — Redteam: Aktive Tab-Bindungen können verwechselt werden. Verbesserung: Prüfung seriell ausführen.
13. Tab-ID allein verwenden — Redteam: Ein Tab kann neu geladen werden. Verbesserung: Tab-ID, URL, Conversation-ID und `tab_instance_id` verbinden.
14. Conversation-ID allein verwenden — Redteam: Seitentitel oder Ordner können falsch sein. Verbesserung: ID, URL und DOM-Titel gemeinsam validieren.
15. Seitenleiste separat öffnen — Redteam: `chrome.tabs.query` sieht dann einen falschen Tab. Verbesserung: Echte angedockte Seitenleiste verwenden.
16. `bringToFront()` als Aktivierung — Redteam: Die Extension erhält nicht immer `onActivated`. Verbesserung: Sichtbaren Klick und Aktivitätsnachweis kombinieren.
17. Browser-Tabnummer speichern — Redteam: Tabs können verschoben werden. Verbesserung: Dynamische Tab-ID-Verfolgung.
18. Fenster-ID ignorieren — Redteam: Mehrere virtuelle Fenster sind möglich. Verbesserung: `windowId` in jedes Ereignis schreiben.
19. Fünf Aufnahmen unter einem Run — Redteam: Zuordnung wird unklar. Verbesserung: Pro Chat einen eigenen `run_id` führen.
20. Parallele Exportknöpfe — Redteam: Downloads können sich überschreiben. Verbesserung: Export, Hashprüfung und nächster Export strikt nacheinander.
21. Nur den aktiven Chat prüfen — Redteam: Vier andere bleiben ungeprüft. Verbesserung: Fünf verpflichtende Conversation-IDs in einer Checkliste.
22. Globale Recorder-Zähler — Redteam: Zahlen vermischen Tabs. Verbesserung: Alle Zähler pro Tab und Run speichern.

## 23–33: Scrollen und Sichtbarkeit

23. Einmal bis unten scrollen — Redteam: Virtuelle Listen laden verzögert. Verbesserung: Scrollen, warten, überlappen und wiederholen.
24. Nur Mausrad verwenden — Redteam: Wheel-Events können verschluckt werden. Verbesserung: Scrollbereich real anklicken, dann Mausrad und Position lesen.
25. `Home` ohne Fokus — Redteam: Der Browser landet nicht im Chat. Verbesserung: Sichtbaren Scrollbereich anklicken, dann `Home` senden.
26. Feste Scrollschritte — Redteam: Viewportgrößen unterscheiden sich. Verbesserung: Schrittweite aus Scrollhöhe und Überlappung berechnen.
27. Keine Überlappung — Redteam: Grenznachrichten gehen verloren. Verbesserung: Mindestens 30 Prozent Überschneidung.
28. Sichtbare Textmenge zählen — Redteam: UI-Hilfstexte werden mitgezählt. Verbesserung: Nachrichtencontainer und Rollen separat extrahieren.
29. Eingeklappte Bereiche ignorieren — Redteam: Der sichtbare Chat bleibt unvollständig. Verbesserung: Als `collapsed_unverified` markieren.
30. Eingeklappte Bereiche automatisch öffnen — Redteam: UI-Zustand wird verändert. Verbesserung: Nur im Prüfmodus und mit Ereignisprotokoll öffnen.
31. „Mehr anzeigen“ ignorieren — Redteam: Nachrichtentext fehlt. Verbesserung: Als Blocker markieren oder real anklicken und erneut erfassen.
32. Nur Endposition prüfen — Redteam: Der Anfang kann fehlen. Verbesserung: Anfangs- und End-Sentinel zwingend machen.
33. Nur DOM-Endzustand speichern — Redteam: Zwischenzustände verschwinden. Verbesserung: Jedes Sichtfenster als unveränderlichen Snapshot speichern.

## 34–44: Nachrichtenidentität

34. Rohtext vergleichen — Redteam: Präfixe und UI-Labels erzeugen falsche Abweichungen. Verbesserung: Rohe und normalisierte Hashes parallel speichern.
35. Nur normalisierten Text vergleichen — Redteam: Echte Unterschiede können weg-normalisiert werden. Verbesserung: Normalisierungsversion mitspeichern.
36. Rolle plus Text vergleichen — Redteam: Gleiche Nachrichten können mehrfach vorkommen. Verbesserung: Rolle, Sequenz, DOM-Key und Hash kombinieren.
37. DOM-Key allein verwenden — Redteam: Keys können neu erzeugt werden. Verbesserung: Key nur als ein Signal behandeln.
38. Hash allein verwenden — Redteam: Gleiche Nachrichten haben gleiche Hashes. Verbesserung: Hash plus Kontextfenster verwenden.
39. Nachrichten deduplizieren — Redteam: Echte Wiederholungen verschwinden. Verbesserung: Nur identische aufeinanderfolgende Sichtungen deduplizieren.
40. Thinking als Assistant zählen — Redteam: Turn-Zähler wird künstlich erhöht. Verbesserung: `thinking`, `tool` und `assistant` getrennt führen.
41. Unbekannte Rollen verwerfen — Redteam: Informationsverlust. Verbesserung: Behalten und als unbestimmt markieren.
42. Markdown als Vergleichsbasis — Redteam: Formatierung verändert Bytes. Verbesserung: Strukturierte Nachrichten vergleichen, Markdown nur projizieren.
43. JSON ungeordnet vergleichen — Redteam: Feldreihenfolge erzeugt Scheindifferenzen. Verbesserung: Kanonisches JSON serialisieren.
44. Semantische Gleichheit behaupten — Redteam: Der Vergleich kann falsch positiv sein. Verbesserung: `match`, `ambiguous` und `mismatch` unterscheiden.

## 45–55: Lücken und Beweisführung

45. Lücken nur zählen — Redteam: Ihre Größe bleibt unklar. Verbesserung: Start, Ende, Ursache und betroffene Fenster speichern.
46. Lücken automatisch schließen — Redteam: Das wäre Erfindung statt Beweis. Verbesserung: Nur durch neue überlappende Sichtung schließen.
47. Lücke nach Reload ignorieren — Redteam: Sessionbruch verschwindet. Verbesserung: Reload als eigenes Ereignis markieren.
48. Netzwerkfehler ignorieren — Redteam: Nachrichten fehlen still. Verbesserung: Fetch-/Recorderfehler als Blocker behandeln.
49. Zeitüberschreitung ignorieren — Redteam: Laufende Antworten werden unvollständig. Verbesserung: `streaming`, `complete` und `timeout` unterscheiden.
50. Gap-Datei editieren — Redteam: Beweiskette wird zerstört. Verbesserung: Append-only JSONL verwenden.
51. Manifest überschreiben — Redteam: Alte Wahrheit verschwindet. Verbesserung: Manifestversionen mit Parent-Hash erzeugen.
52. Nur Endmanifest sichern — Redteam: Zwischenstände fehlen. Verbesserung: Start-, Zwischen- und Endmanifest sichern.
53. Aufnahme trotz Lücke vollständig nennen — Redteam: Falsches Vertrauen. Verbesserung: Status automatisch `partial` setzen.
54. Nutzer muss Lücken interpretieren — Redteam: Workflow wird langsam. Verbesserung: Konkrete nächste Aktion anzeigen.
55. Keine Unsicherheitsklasse — Redteam: Alles wirkt binär. Verbesserung: `complete`, `partial`, `blocked` und `ambiguous` einführen.

## 56–66: Export und Downloads

56. VPS zuerst, Download danach — Redteam: Download kann andere Bytes enthalten. Verbesserung: VPS gibt genau die versiegelten Bytes zurück.
57. Download zuerst, VPS danach — Redteam: VPS kann eine andere Version speichern. Verbesserung: Download-Hash vor VPS-Siegel vergleichen.
58. Dateiname als Zuordnung — Redteam: Dateiname kann falsch sein. Verbesserung: ID und Hash im Manifest speichern.
59. Downloadordner durchsuchen — Redteam: Alte Dateien werden verwechselt. Verbesserung: Eigenen Run-Downloadordner verwenden.
60. Browser-Default-Download — Redteam: Pfad ist unklar. Verbesserung: Expliziten Downloadpfad pro Auditlauf verwenden.
61. `download.path()` verwenden — Redteam: Temporäre Datei verschwindet. Verbesserung: Sofort `saveAs()` in persistenten Auditordner.
62. Nur Dateigröße prüfen — Redteam: Gleiche Größe bedeutet nicht gleicher Inhalt. Verbesserung: SHA-256 prüfen.
63. Nur Hash prüfen — Redteam: Falsches Artefakt kann ähnliche Metadaten besitzen. Verbesserung: Hash, Conversation-ID und Turnzahl verbinden.
64. Office-Dateien nur öffnen — Redteam: Inhalt ist schwer vergleichbar. Verbesserung: DOCX/ODT/PDF extrahieren und gegen Nachrichten prüfen.
65. HTML visuell prüfen — Redteam: Inhalte können versteckt fehlen. Verbesserung: HTML-DOM erneut zählen.
66. JSON ungeordnet vergleichen — Redteam: Feldreihenfolge erzeugt Scheindifferenzen. Verbesserung: Kanonische Serialisierung und semantischen Diff nutzen.

## 67–77: Absturz, Wiederholung und Parallelität

67. Browserabsturz als Ende akzeptieren — Redteam: Der letzte Zustand fehlt. Verbesserung: Recovery-Checkpoint nach jedem Sichtfenster.
68. VPS-Netzwerkfehler verwerfen — Redteam: Lokaler Puffer geht verloren. Verbesserung: Idempotente Queue mit Ereignis-ID.
69. Doppelte Übertragung ignorieren — Redteam: Nachrichten werden doppelt. Verbesserung: Dedizierte `message_event_id` verwenden.
70. Recorder-Neustart fortsetzen — Redteam: Neuer und alter Lauf vermischen sich. Verbesserung: Neuer `run_id` mit Parent-Run.
71. Serverneustart mitten im Export — Redteam: Artefakt ist halb geschrieben. Verbesserung: Temp-Datei, `fsync`, atomarer Rename.
72. Fünf parallele Browserprozesse — Redteam: Ressourcen- und Fokusrennen. Verbesserung: Fünf Tabs zulassen, Export aber seriell durchführen.
73. Gleichzeitige Antworten — Redteam: Stream-Events werden vertauscht. Verbesserung: Tabbezogene Eventpartition.
74. Langsame Seite — Redteam: Snapshot kommt zu früh. Verbesserung: Stabilitätsfenster mit zweimal unverändertem Inhalt.
75. DOM-Änderung während Scan — Redteam: Snapshot ist inkonsistent. Verbesserung: Vorher-/Nachher-Hash und Wiederholung bei Abweichung.
76. Capture-Lock ignorieren — Redteam: Recorder schreibt noch. Verbesserung: Lockstatus prüfen und Aufnahme sauber beenden.
77. Alte Dateien wiederverwenden — Redteam: Falscher Run erscheint gültig. Verbesserung: Jeder Pfad wird im Manifest an `run_id` gebunden.

## 78–88: Daniels Workflow

78. Viele einzelne Bestätigungen — Redteam: Nutzer ermüdet. Verbesserung: Eine Freigabe für den gesamten Auditlauf.
79. Normale Schritte nachfragen — Redteam: Workflow stockt. Verbesserung: Dauerhafte operative Freigabe anwenden.
80. Destruktive Schritte automatisch erlauben — Redteam: Datenverlust. Verbesserung: Löschen und Überschreiben separat schützen.
81. Fünf Chats manuell benennen — Redteam: Tippfehler. Verbesserung: IDs automatisch aus URLs lesen.
82. Fortschritt nur am Ende zeigen — Redteam: Hänger bleiben unklar. Verbesserung: Nach jedem Chat kurze Statuszeile.
83. Technische Fehlermeldung zeigen — Redteam: Nicht handlungsorientiert. Verbesserung: Fehler plus konkrete nächste Aktion.
84. Vollständigkeit verstecken — Redteam: Falsche Sicherheit. Verbesserung: Ampel direkt neben jedem Chat.
85. Fehlende Downloads still akzeptieren — Redteam: Nutzer glaubt, sie seien geprüft. Verbesserung: Explizit „nicht vorhanden“ melden.
86. Jede Datei einzeln öffnen — Redteam: Unnötig langsam. Verbesserung: Automatisierter Hash-/Strukturbericht.
87. Nur positives Ergebnis melden — Redteam: Redteam wird unsichtbar. Verbesserung: Negativbefunde prominent speichern.
88. Prüfergebnis nicht persistieren — Redteam: Kontextverlust. Verbesserung: Auditnotiz, Manifest und Report committen.

## 89–99: Tests und Zukunftssicherheit

89. Nur Live-Test — Redteam: Nicht reproduzierbar. Verbesserung: Replay mit aufgezeichnetem Scrollplan.
90. Nur Fixture-Test — Redteam: Reale Chatänderungen fehlen. Verbesserung: Fixture plus echter Desktop-Smoke-Test.
91. Einen Chat testen — Redteam: Multi-Tab-Fehler bleibt unsichtbar. Verbesserung: Verpflichtenden Fünf-Tab-Test.
92. Zufällige Chatlänge testen — Redteam: Grenzfälle fehlen. Verbesserung: Kurz, mittel, sehr lang, eingeklappt und Streaming testen.
93. Nur Chrome testen — Redteam: Erweiterungsverhalten variiert. Verbesserung: Browser-/Extension-Version ins Manifest.
94. Nur erfolgreiche Exporte testen — Redteam: Fehlerpfade bleiben ungeprüft. Verbesserung: Lücke, Reload und Downloadabbruch absichtlich testen.
95. Keine Mutationstests — Redteam: Comparator wirkt robuster als er ist. Verbesserung: Zeichen, Rollen und Reihenfolge gezielt verändern.
96. Keine Golddateien — Redteam: Regression bleibt unbemerkt. Verbesserung: Kanonische Referenzartefakte pflegen.
97. Keine Hashkette — Redteam: Alte Dateien können ersetzt werden. Verbesserung: Parent-Hash für Manifest und Artefakte.
98. Keine unabhängige Prüfinstanz — Redteam: Recorder prüft sich selbst. Verbesserung: Zweiten read-only Comparator außerhalb der Extension einsetzen.
99. Alles in ein großes System bauen — Redteam: Schwer zu debuggen. Verbesserung: Sechs kleine Gates: Sichtung, Semantik, Lücke, VPS, Download und Bericht.

## Gewinnerarchitektur nach dem Redteam

Die robusteste Lösung besteht aus sechs voneinander prüfbaren Gates:

1. **Sichtung:** Realer Desktop, realer Klick, reales Mausrad, überlappende Sichtfenster.
2. **Semantik:** Rohtext, normalisierter Text, Rolle, Sequenz und stabiler Kontext-Key.
3. **Lücke:** Jede Lücke bleibt sichtbar und verhindert den Status `complete`.
4. **VPS:** Atomar gespeichertes, versioniertes Artefakt mit Hash und `run_id`.
5. **Download:** Genau dieselben Bytes, persistent gespeichert, gehasht und erneut geparst.
6. **Bericht:** Fünf Chatresultate, alle Pfade, alle Hashes und alle Negativbefunde.

Der Export darf niemals „1zu1“ heißen, solange nicht dieselben Nachrichten, dieselbe Reihenfolge, derselbe Hash und derselbe Download nachgewiesen sind.

## Empfohlener Arbeitsablauf

### Phase A: Lauf vorbereiten

1. Fünf offene Chat-URLs und Conversation-IDs automatisch erfassen.
2. Für jeden Chat einen eigenen `run_id` und `tab_instance_id` erzeugen.
3. Browser-, Extension-, Fenster- und Viewportdaten in das Startmanifest schreiben.
4. Einen persistenten Audit-Downloadordner erzeugen.

### Phase B: Chats prüfen

1. Nur einen Tab aktiv prüfen.
2. Den sichtbaren Scrollbereich real anklicken.
3. Mit `Home` an den Anfang gehen.
4. Überlappend durch den Chat scrollen.
5. Nach jedem Fenster warten, bis der DOM stabil ist.
6. Nachrichten, Rollen, Rohhash, Normalisierungshash und Position speichern.
7. Eingeklappte oder nicht vollständig geladene Bereiche als Blocker markieren.
8. Am Ende den End-Sentinel und den Sichtfenster-Hash speichern.

### Phase C: Gegen VPS prüfen

1. VPS-Manifest laden.
2. Nachrichtenanzahl und Rollenverteilung vergleichen.
3. Lücken und unvollständige Turns prüfen.
4. Semantischen Diff mit normalisierter Vergleichsversion ausführen.
5. Bei Abweichung den Chat als `partial`, `blocked` oder `ambiguous` markieren.

### Phase D: Export versiegeln

1. Nur bei bestandenem Semantik-Gate exportieren.
2. Exportbytes kanonisch erzeugen.
3. SHA-256 berechnen.
4. VPS-Artefakt atomar speichern.
5. VPS-Manifest mit Bytezahl, Hash, Nachrichtenanzahl und Parent-Hash ergänzen.

### Phase E: Download verifizieren

1. Genau die versiegelten Bytes als Download auslösen.
2. Download sofort in den persistenten Auditordner schreiben.
3. Download-Hash gegen VPS-Hash vergleichen.
4. Datei erneut parsen.
5. Bei HTML DOM-Nachrichten zählen, bei JSON semantisch vergleichen, bei Markdown/Office extrahieren.
6. Erst dann `download_verified: true` setzen.

### Phase F: Abschluss

1. Alle fünf Chats in einer gemeinsamen Tabelle ausgeben.
2. `complete`, `partial`, `blocked` und `ambiguous` getrennt zählen.
3. Fehlende Downloads ausdrücklich nennen.
4. Screenshots, Manifeste, Hashes und Fehlerpfade verlinken.
5. Auditnotiz und Report unveränderlich sichern.

## Ziel-Datenmodell

```ts
type AuditStatus = "complete" | "partial" | "blocked" | "ambiguous";

type AuditRow = {
  conversationId: string;
  runId: string;
  tabInstanceId: string;
  liveIndex: number;
  role: "user" | "assistant" | "tool" | "thinking" | "unknown";
  rawTextSha256: string;
  normalizedTextSha256: string;
  contextKey: string;
  vpsMessageId?: string;
  exportSha256?: string;
  status: "match" | "missing-vps" | "missing-live" | "ambiguous";
};

type ChatAudit = {
  conversationId: string;
  runId: string;
  liveMessages: number;
  vpsMessages: number;
  completeTurns: number;
  gaps: number;
  exports: ExportAudit[];
  status: AuditStatus;
  rows: AuditRow[];
};

type ExportAudit = {
  kind: "html" | "markdown" | "events" | "json" | "docx" | "odt" | "pdf";
  vpsPath?: string;
  downloadPath?: string;
  byteCount?: number;
  sha256?: string;
  downloadVerified: boolean;
};
```

## Serverseitige Versiegelung

```python
def seal_export(audit: ChatAudit, payload: bytes) -> ExportResult:
    if audit.status != "complete":
        raise ExportRefused("Audit nicht vollständig")
    if any(row.status != "match" for row in audit.rows):
        raise ExportRefused("Semantischer Nachrichtenabgleich fehlt")

    digest = sha256(payload)
    path = write_atomically(audit.run_id, digest, payload)
    return ExportResult(
        path=path,
        sha256=digest,
        bytes=len(payload),
        message_count=len(audit.rows),
    )
```

## Nicht verhandelbare Akzeptanzkriterien

- Kein Chat erhält `complete`, wenn `gap_count > 0`.
- Kein Export erhält `1zu1`, wenn eine Nachricht fehlt oder mehrdeutig ist.
- Kein Download gilt als geprüft, solange der persistente Download-Hash nicht dem VPS-Hash entspricht.
- Keine Extension-Seite außerhalb der echten Tab-/Seitenleistenbindung darf als aktiver Chatbeweis gelten.
- Jeder der fünf Chats wird separat identifiziert und separat abgeschlossen.
- Rohdaten bleiben erhalten; Normalisierung darf die Herkunft nicht überschreiben.
- Fehler, Lücken, Abbrüche und fehlende Dateien bleiben sichtbar.
- Die Prüfung verändert keine Chatnachricht und startet keinen laufenden Dienst neu.

## Erster sinnvoller Bauschritt

Der erste Baupunkt ist kein neuer Exportbutton. Es ist ein kleiner unabhängiger `audit-runner`, der die sechs Gates seriell ausführt und eine gemeinsame Fünf-Chat-Tabelle erzeugt. Erst wenn dieser Runner für den aktuellen Bestand zuverlässig `partial` beziehungsweise `blocked` meldet, darf der Export-Gate weiterentwickelt werden.

## Aktueller Befund, von dem aus gebaut wird

Die fünf getesteten Aufnahmen besitzen Dateien, aber keinen 1:1-Nachweis. Alle fünf haben Lücken; bei keinem stimmen vollständige Turns und Gesamtturns überein. Der VPS-Export wurde bei semantischer Abweichung korrekt abgebrochen. Persistente Downloads wurden im geprüften Downloadbestand nicht gefunden.
