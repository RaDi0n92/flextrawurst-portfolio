# 04 · Kontextinjektor, Bauwirkung und harter Funktionsbeweis

**Status:** NEUER SYSTEMKÖRPER AB 17.08.2026  
**Rohherkunft:** `01_rohgespraech_2026-08-17_wahrnehmung_spielsprachen_kontextinjektor.md`

---

## Problem

Das Spiel besitzt inzwischen sehr viele Texte, Funde, Regeln, Ideen, Quellkörper, Tests und historische Varianten. Gefundene oder archivierte Information ist aber noch keine wirksame Bauinformation.

Ein künftiger Bauagent darf nicht davon abhängen, dass Daniel jedes Mal manuell sagt:

- lies Datei X,
- denk wieder an System Y,
- beachte die alte Korrektur Z.

Gleichzeitig darf keine einzelne statische Masterdatei als absolute Wahrheit behandelt werden, weil spätere Tiefenbergungen ältere sauber dokumentierte Aussagen widerlegen können.

Konkreter Lehrfall aus `gemgems-spielbeobachtung`: Ein älterer Quellenatlas hielt eine große ZIP-Datei für nicht existent; eine spätere Tiefenbergung fand sie real. Das zeigt: **Mastertexte brauchen Zeit-, Herkunfts- und Überschreibungslogik.**

---

## Ziel

**Die Bedeutung eines Arbeitsauftrags zieht automatisch den relevanten Kontext an.**

Ein Bauagent soll bei einem Auftrag nicht den gesamten VPS lesen, sondern die für diesen Eingriff relevanten Regeln, Primärquellen, Korrekturen, offenen Fragen, Beweise und Schutzgrenzen automatisch erhalten.

Arbeitsname:

`SPIEL_KONTEXTINJEKTOR`

Der Name ist vorläufig. Die Funktion ist wichtiger als das Etikett.

---

## Kontextpipeline

### 1. Auftrag semantisch zerlegen

Beispiel:

`Baue im Casino eine SNES-artige Wikinger-Vergangenheit mit Bienenwahrnehmung.`

Erkannte Themen könnten sein:

- Casino,
- Vergangenheit,
- Zeit,
- Wikinger / historische Rekonstruktion,
- Spielsprache,
- SNES / 2D,
- Wahrnehmung,
- biologische Forschung,
- Biene,
- Verkörperung,
- Persistenz,
- Weltatom,
- Performance,
- Schwellen-/Portalarchitektur,
- Save/Reload,
- Regressionstest.

### 2. Quellenräume bestimmen

Der Injektor durchsucht typisierte Quellen statt alles gleich zu behandeln:

- Rohgespräche / Daniels Ursprungsformulierungen,
- neue aktive Setzungen,
- archäologische Funde,
- Primärdateien,
- Quellcode,
- Runtime-Zustände,
- Tests und Beweise,
- Red-Team-Berichte,
- spätere Korrekturen,
- offene Fragen,
- verworfene oder historische Varianten.

### 3. Relevanz auswählen

Nicht nur Schlüsselwortsuche.

Beziehungen müssen mitgezogen werden. `Casino` kann beispielsweise automatisch verbinden zu:

- Standortrealität,
- Casino-Organismus,
- Zeitkörper,
- Spielsprachen,
- Performance,
- Weltatom,
- Streaming,
- Wahrnehmung,
- bestehende Gordslider-Zelle.

### 4. Zeit und Widerspruch auflösen

Kontext bekommt mindestens:

- Aussage,
- Quelle,
- Quelldatum,
- Quellentyp,
- spätere Korrekturen,
- `supersedes` / `contradicts` / `extends`,
- Gültigkeitsstatus,
- Implementierungsstatus,
- Beweisstatus.

Der Injektor darf ältere Aussagen nicht löschen. Er muss aber klar erkennen können, welche davon aktuell überstimmt wurden.

### 5. Primärquelle bevorzugen

Eine Zusammenfassung ist kein Ersatz für den Primärkörper.

Wenn eine Entscheidung auf einem Originalgespräch, einer konkreten Datei oder echtem Runtime-Beweis beruht, muss der Bauagent den Primäranker kennen und bei kritischen Punkten bei Bedarf direkt lesen.

### 6. Kleinen Operationskontext erzeugen

Der Agent erhält keinen 400-MB-Textblock, sondern eine operationsbezogene Kapsel:

- Arbeitsauftrag,
- relevante Weltgesetze,
- aktuelle Wahrheiten,
- relevante Primärquellen,
- vorhandene Implementierung,
- offene Konflikte,
- verbotene Annahmen,
- Beweisbedingungen,
- betroffene Nachbarsysteme.

### 7. Vor dem Bau Abhängigkeitsprüfung

Frage:

**Welche bereits vorhandenen Systeme kann diese Änderung verändern oder brechen?**

Erst danach wird implementiert.

### 8. Nach dem Bau Rückkopplung

Der Eingriff erzeugt wiederum neue indexierbare Information:

- geänderte Dateien,
- neue Weltatome,
- neue Regeln,
- Tests,
- Screenshots,
- Laufzeitbeweise,
- Fehler,
- neue Korrekturen,
- Entscheidungen von Daniel.

Diese Information fließt zurück in den Kontextkörper.

---

## Kreislauf

`ARCHÄOLOGIE / ROHQUELLEN → AKTUELLE WAHRHEIT → RELEVANZINDEX → OPERATIONS-KONTEXT → BAU → TEST / REDTEAM → NEUE WAHRHEIT → INDEX`

Der Kreislauf ist wichtiger als eine einzelne Masterdatei.

---

## Indizierung

Langfristig soll jede wichtige Information zusätzliche maschinenlesbare Metadaten erhalten können.

Mögliche Felder:

- `id`
- `title`
- `source_path`
- `source_type`
- `created_at`
- `observed_at`
- `topics`
- `entities`
- `world_atoms`
- `systems`
- `status`
- `truth_class`
- `implementation_status`
- `evidence_status`
- `supersedes`
- `contradicts`
- `extends`
- `depends_on`
- `affects`
- `needs_human_decision`
- `confidence`

Die genaue Form ist noch nicht festgelegt.

---

## Automatische Aktivierung

Künftige Spielbau-Sessions sollen beim Einstieg nicht nur eine `START_HIER.md` lesen.

Der Einstieg soll ungefähr lauten:

1. Session meldet Arbeitsabsicht.
2. System erkennt, dass es um das Spiel geht.
3. Spielindex und aktuelle aktive Schicht werden geladen.
4. Auftrag wird semantisch klassifiziert.
5. Relevante Kontexte und Primärquellen werden injiziert.
6. Agent nennt intern die berührten Systeme.
7. Erst danach beginnt der Bau.
8. Nach dem Bau werden Ergebnis und neue Beziehungen zurückgeschrieben.

Ziel: Daniel muss nicht zum menschlichen RAG-System werden.

---

## Harter Funktionsbegriff

Ein Feature ist nicht funktionierend, weil:

- eine Datei existiert,
- eine Variable existiert,
- ein Menüpunkt sichtbar ist,
- irgendein Test eine Zeichenkette findet,
- ein Datenobjekt behauptet, der Effekt sei aktiv.

Für ein relevantes spielbares Feature gilt je nach Art eine vollständige Beweiskette.

### Mindestkette

1. Spieler kann es erreichen.
2. Spieler kann es verstehen oder bewusst entdecken.
3. Spieler kann es tatsächlich auslösen.
4. Es gibt eine echte sichtbare, hörbare, fühlbare oder systemische Reaktion.
5. Der kanonische Weltzustand verändert sich korrekt.
6. Betroffene Nachbarsysteme reagieren korrekt.
7. Zustand wird gespeichert, falls Persistenz vorgesehen ist.
8. Frischer Neustart stellt ihn korrekt wieder her.
9. Rückkehr / Wiederholung funktioniert.
10. Fehlerpfade werden geprüft.
11. Regressionen werden geprüft.
12. Performance wird gemessen, wenn der Eingriff Laufzeitkosten erzeugt.

### Beweisarten

Je nach Feature:

- Unit-/Logiktest,
- Integrationstest,
- echte Eingabe,
- Save/Reload,
- Screenshot oder Framebeweis,
- Renderprüfung,
- Audio-/Eventbeweis,
- Performanceprofil,
- Regressionstest,
- Grenzfalltest,
- Wiederholungs-/Langzeittest,
- Wechsel zwischen Spielsprachen,
- Wechsel zwischen Wahrnehmungen,
- Wechsel zwischen Zeitkörpern.

Ein Test muss beweisen, was sein Name behauptet.

---

## Zusammenhang mit GemGems-Archäologie

`/root/werkraum/gemgems-spielbeobachtung/spiel/` bleibt Fundkörper und Herkunftsraum.

Der Injektor darf ihn verwenden, aber nicht jeden Fund als aktuelle Wahrheit behandeln.

Die neue aktive Schicht ab 17.08.2026 liegt unter:

`/root/werkraum/gemgems-spielbeobachtung/NEU_AB_2026-08-17_SPIELWEITERBAU_CHATGPT/`

Damit sind mindestens zwei Zeitschichten explizit getrennt:

- archäologisch wiedergefunden,
- ab 17.08.2026 neu aktiv weitergedacht.

Spätere aktive Phasen dürfen weitere datierte Schichten erhalten.

---

## Noch offen / gemeinsam zu entscheiden

- tatsächliches Indexformat,
- Datenbank vs Dateien vs beides,
- Chunking-/Embeddings-/Volltextstrategie,
- automatische Trigger für Spielbau-Sessions,
- Priorisierung widersprüchlicher Quellen,
- Umgang mit sehr großen Rohkörpern,
- UI für Daniel zur Sichtung des injizierten Kontextes,
- automatische Rückschreibregeln,
- Schutz vor Selbstverstärkung falscher Zusammenfassungen,
- Tests dafür, dass ein Bauagent den relevanten Kontext wirklich erhalten hat.

Diese Punkte sind `GEMEINSAM_ZU_FEINJUSTIEREN`.
