# Physik / Weltvertrag v0 · Hypothesen, nicht Verfassung

Diese Datei hält nur die **kleinsten gemeinsamen Begriffe**, die in mehreren realen Teilen bereits auftauchen.

Nicht daraus automatisch neue Tabellen, IDs oder Klassen bauen.

## Ausgangspunkt

Ältere Grundlage: `KNOTENVERTRAG.md`

Tragend daraus:
- ein Graph, viele Ordnungen, keine Datenkopien
- Identität nicht pro Ansicht neu erfinden
- Beziehung braucht Herkunft/Beleg/Unsicherheit
- Ähnlichkeit ist keine Wahrheit
- Zielwahl ist kein Ausführungsbeweis

Der neue Weltentwurf soll das **erweitern**, nicht ersetzen.

## Minimale Weltbegriffe

### Konstrukt

Ein adressierbares Ding oder eine belastbare Zusammensetzung, an der gearbeitet, beobachtet oder angeknüpft werden kann.

Nicht jeder Dateipfad muss automatisch ein eigenes Weltkonstrukt werden.

### Verbindung / Liane

Eine reale oder belegte Beziehung zwischen Dingen.

Nicht jede räumliche Nähe und nicht jede semantische Ähnlichkeit ist automatisch eine Verbindung.

### Zustand

Was über ein Ding **jetzt** gilt.

Zustand kann mehrere Achsen besitzen. Kein universelles Super-Enum erzwingen.

### Ereignis

Was tatsächlich geschah und einen Zustand/Bezug veränderte oder als relevante Handlung belegt ist.

`Zustand ≠ Ereignis` bleibt eine harte Trennung.

### Möglichkeit

Etwas, das in der aktuellen Situation tatsächlich getan werden kann.

Eine Möglichkeit hängt von Kontext, Actor, Rechten, Zustand und ggf. Bedingungen ab.

Nicht jede technisch bekannte Funktion ist für jede Instanz gerade eine Möglichkeit.

### Bedingung

Etwas, das für eine konkrete Möglichkeit/Handlung gelten muss.

Bedingungen können veralten. `stale` ist deshalb ein realer Fall, kein bloßer UI-Fehler.

### Handlung

Mindestens drei Dinge nicht vermischen:

`Vorhaben/Vorschlag → reale Ausführung → belegte Wirkung`

Eine angekündigte Handlung beweist keine Ausführung. Eine Ausführung beweist ohne Prüfung nicht automatisch die gewünschte Wirkung.

### Beleg / Spur

Quelle dafür, warum eine Behauptung über Weltzustand oder Handlung glaubwürdig ist.

Beispiele: Pfad, Hash, Diff, Test, native Session-/Toolspur, DB-Zustand, Handoff, Screenshot.

Belegstärke darf unsicher oder unvollständig sein.

### Goal

Gewünschter langlebiger Weltzustand.

Ein beendeter Task/Run ist kein automatischer Goalbeweis.

Für frühe Szenen reichen Text, wenige Kriterien und reale Belege. Keine universelle Goal-Engine auf Vorrat.

### Review / Lernen

Review prüft Wirkung/Belege und kann neue Arbeit oder eine dauerhafte Änderung des Arbeitsgerüsts auslösen.

Arbeitsannahme für „Selflearning“:

`wiederholter belegter Fund → Kandidat → Review → akzeptierte/abgelehnte dauerhafte Änderung`

Kein Modellgewichtslernen behaupten.

## Zwei Geschwindigkeiten

### Langlebige Weltwahrheit

Dinge, die Reload/Sessionwechsel überleben sollen:
- relevante Zustände
- bestätigte Wirkungen
- Goals/Reviews, wenn benutzt
- dauerhafte Beziehungen/Zuordnungen

### Transiente Lebenszeichen

Dinge wie:
- laufender Toolcall
- frische Browser-/Terminalaktivität
- kurzfristige Aufmerksamkeit
- Prozessfortschritt

Nicht jeden transienten Read/Scroll/Toolcall zur neuen Weltrevision machen.

## Native Quellen bleiben native Quellen

Claude, Codex, Gemgem, Gravityy, Haiku, Anthropic_Claude, GPT-MCP, Browser, Dienste, DB usw. dürfen unterschiedliche native Spuren besitzen.

Gemeinsame Darstellung **oberhalb** dieser Quellen, nicht künstlich identische Logs darunter.

## Was v0 ausdrücklich nicht entscheidet

- endgültiges Schema
- neue Master-ID
- vollständiges Actor-/Rechtesystem
- universelle Correlation-ID
- Renderer
- vollständige Eventtypen
- komplette Goal-/Run-Maschine
- wie jeder Haufen aussehen muss

Diese Entscheidungen sollen aus realen Szenen entstehen.

## Realitätsfilter

Bevor aus einer Hypothese Physik wird:

1. Taucht das Problem in mindestens einer echten Szene auf?
2. Taucht dieselbe Regel in einer zweiten andersartigen Szene wieder auf?
3. Löst die Abstraktion wirklich Doppelarbeit oder Widerspruch?

Wenn nicht: lokal lassen.