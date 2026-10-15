# UI-Neubau · Gesamtkonstrukt-Betriebssystem

## Entscheidung

Die bisherige Oberfläche ist Legacy. Sie behandelt **Start / Canvas / Netz / Plan / Zeitspur / Replicas** als globale Ansichten derselben offenen Planerdatei. Das ist nicht die gewünschte Arbeitsform.

Der Neubau beginnt nicht mit CSS und nicht mit einem „mobilen Modus“, sondern mit einer anderen Bedienlogik:

```
Arbeitsraum (Orte + Wurzeln)
  → Arbeitskörper (gewählte Datei, Objekt, Ablauf oder Raum)
    → passende Werkzeuge
      → echte Änderung / Ereignis / Rückweg
```

## Drei Ebenen, keine globalen Sechs-Tabs

1. **Arbeitsraum**
   - einklappbare Wurzeln, Ordner, Dateien, Papierkorb
   - Anlegen, umbenennen, verschieben, löschen/wiederherstellen
   - später: unabhängige Wurzeln für Gesamtkonstrukt, Gesamtatlas und Megavault

2. **Arbeitskörper**
   - das gerade bearbeitete Ding, mit Quelle, Zustand, Beziehungen, Notizen, Verlauf und nächster Handlung
   - eine Datei ist zuerst Quelle; „übernehmen“ macht daraus bewusst einen verknüpfbaren Körper
   - kein alter Auswahlrest darf sich als aktueller Körper ausgeben

3. **Werkzeuge**
   - ein Werkzeug öffnet zum gewählten Körper oder zu einem bewusst angelegten Raum
   - Canvas, Netz, Plan und Zeit sind Arbeitsweisen, keine Seiten des ganzen Systems
   - jede Replica ist eine eigene Werkstatt mit Eingängen, Handlungen, Ergebnis und Rückgabe

## Desktop

- linker Bereich: Arbeitsraum, jederzeit komplett ein- und ausklappbar
- Mitte: gewählter Körper oder geöffnete Werkstatt
- rechter Bereich: nur kontextbezogene Inspektion / Beziehungen / Verlauf; einklappbar
- Fenster/Paneele dürfen bewusst geöffnet, verschoben, geteilt oder geschlossen werden
- keine feste Mitte, keine erzwungene Dauer-Dreispaltigkeit

## Telefon

- genau **eine** Arbeitsfläche gleichzeitig
- Kopf: Rückweg + Name des aktuellen Körpers + sichtbarer Speicher-/Quellenstatus
- unten: Arbeitsraum · Körper · Werkzeuge · Notiz
- Ordnerbaum als volle Ebene, nicht als 31%-Seitenleiste
- Aktionen groß genug und nie hinter Horizontal-Scroll versteckt
- Werkstätten wechseln als ganze Arbeitsfläche, nicht in einem winzigen Replica-Tabstreifen

## Replica- und Graphvertrag

Jede der 17 Werkstätten erhält eine eigene Steueroberfläche. Nicht nur andere Farben:

- eigene Eingänge;
- eigene konkrete Aktionen/Buttons;
- eigene Zustände und Fehlwege;
- eigene Ergebnisform;
- eigene Ebenen;
- sichtbare Rückgabe in den gemeinsamen Bestand.

Die Registry `server/replica_registry.js` hält für jede Werkstatt genau diese Startstruktur bereit. Sie ist erst der Bauvertrag, nicht die Behauptung, dass die 17 Werkstätten schon fertig implementiert seien.

Graphen sind keine einzelne Ansicht. Sie werden als getrennt ein- und ausblendbare Ebenen geführt:

- Struktur / Enthält
- belegte Beziehungen
- Abläufe
- Ereignisse und Versionen
- Vorschläge
- freie Skizze und Annotation

Keine Ebene darf sich als eine andere ausgeben; Vorschläge und freie Skizzen werden nie als belegte Kante gezeichnet.

## Nicht wieder tun

- keinen globalen Ansichtsumschalter über allem
- keine „Replica“ ohne eigene produktive Kernhandlung
- keinen Kontext nur grün anzeigen, während ein anderes Objekt bearbeitet wird
- keine verschachtelten Scrollzonen als Layout-Ersatz
- keine neue Datei/Notiz ohne sichtbaren Ort und Rückweg

## Erste Baufolge

1. Legacy-Shell als solche markieren; keine weiteren kosmetischen Reparaturen.
2. Neue Arbeitsraum-/Körper-/Werkzeug-Navigation als separate echte Shell bauen.
3. Sie zuerst mit Datei, übernommenem Dokument, Notiz und Kante gegen VPS + Reload prüfen.
4. Erst danach Canvas, Netz, Plan und Zeit nacheinander in diese Shell heben.
5. Replicas nur einziehen, wenn ihre eigene Ein-/Ausgabe und Rückgabe existiert.

## Abnahme

Ein Mensch muss auf PC oder Telefon ohne Raten beantworten können:

- Wo bin ich?
- Was bearbeite ich gerade?
- Ist es Quelle, Entwurf oder echter Körper?
- Was darf ich hier tun?
- Wo landet das Ergebnis?
- Wie komme ich zurück?

