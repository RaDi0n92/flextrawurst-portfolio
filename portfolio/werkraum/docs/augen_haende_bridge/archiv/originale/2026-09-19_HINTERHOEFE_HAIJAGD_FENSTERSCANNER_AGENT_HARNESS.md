# Augen & Hände — Hinterhöfe-Haijagd: Fensterscanner, Agent-Harness und Live-QA

Ahhh, jetzt hab ich dich. Nicht „noch ein paar Quellen“, sondern in die Werkstätten gehen und nachsehen, wer diese Probleme schon praktisch gelöst oder sich daran blutig die Zähne ausgebissen hat.

Der wichtigste Fund: Der Fensterscanner ist nicht ein UI-Feature, sondern der zentrale Augen-/Sicherheitskern.

## Was die Hinterhöfe zeigen

`agent-desktop-harness` kommt unserer Idee erstaunlich nahe: native Windows-Fenster-/Display-Erkennung, UI-Automation, Screenshots, stabile UI-Referenzen, Beobachtungsschutz vor Aktionen und eine zusammenhängende Evidence-Kette aus Events, UI-Tree und Bild. Besonders wichtig: Koordinaten werden nicht einfach blind benutzt, sondern erst nach einer aktuellen Beobachtung freigegeben. Genau das brauchen unsere Fensterbindungen. [Agent Desktop Harness](https://github.com/xuyw1997/agent-desktop-harness)

`agent-desktop` arbeitet mit Snapshot-IDs und qualifizierten Elementreferenzen statt mit „klick mal bei x=438/y=290“. Eine Aktion bezieht sich dadurch auf genau den zuvor beobachteten Zustand. Texte und Timer gelten dort nicht als stabile Identität — Fenster, Rolle, Pfad und Geometrie sind wichtiger. Genau das brauchen unsere Fensterbindungen. [agent-desktop](https://github.com/lahfir/agent-desktop)

`windows-mcp-server` geht noch härter in Richtung Sicherheits-Harness: Aktionen werden an Gerätezustand, Policy, Auditkette und Live-Zustand gekoppelt. Das ist interessant für uns, weil der Fensterscanner damit zum Ursprung einer überprüfbaren Aktion wird, nicht bloß zum Lieferanten eines Screenshots. [windows-mcp-server](https://github.com/deploymenttheory/windows-mcp-server)

Für KDE/Wayland ist `kwin-mcp` besonders wertvoll: Es verbindet Screenshot, KWin-Fensterrechtecke, AT-SPI-Accessibility-Tree, virtuelle Sessions und EIS-Eingabe. Vor allem zeigt es, dass strukturierte Fensterdaten und Bilder gemeinsam an einen Agenten geliefert werden können — getrennt vom tatsächlichen Eingaberecht. [kwin-mcp](https://github.com/isac322/kwin-mcp)

UFO2 bestätigt architektonisch ebenfalls deine Mehragentenidee: zentraler Host-Agent, spezialisierte App-Agenten, UIA plus Vision und isolierte PiP-/Desktop-Arbeitsräume. Das ist im Grunde eine wissenschaftlich beschriebene Variante deines „mehrere Wesen in unterschiedlichen Gates“. [UFO2](https://arxiv.org/abs/2504.14603)

Und dann der unangenehme Hai: Eine aktuelle Arbeit beschreibt den Abstand zwischen Beobachtung und Aktion als TOCTOU-Problem. Fensterfokus oder Overlay können sich nach dem Screenshot ändern, bevor der Agent handelt. Die vorgeschlagene Verteidigung prüft unmittelbar vor jeder Aktion Pixel, globalen Screenshot und strukturellen Fensterzustand erneut. [Temporal UI State Inconsistency](https://arxiv.org/abs/2604.18860)

## Was das für unsere Bridge bedeutet

Der Scanner muss diese Kette liefern:

```text
vollständiger Desktop-Frame
        +
Fenster-/Desktop-Inventar
        +
UIA-/Accessibility-Struktur
        +
stabile Snapshot-ID
        +
ausgewähltes Ziel
        +
Binding-Rücklese
        +
unmittelbarer Pre-Action-Rescan
```

Der Agent bekommt also nicht nur ein Bild „hinter die Bumsbirne“, sondern:

```text
Bild:
  Was ist sichtbar?

Struktur:
  Welche Fenster, Controls und Rechtecke existieren?

Binding:
  Woran bin ich gerade gebunden?

Generation:
  Ist es noch dasselbe Fenster?

Pre-Action-Check:
  Ist die Welt unmittelbar vor der Aktion noch dieselbe?
```

Und genau hier kommt der Blender-Skill hinein:

```text
Baseline-Bild
→ strukturierter Scanner-Readback
→ genau eine Bindungs-/UI-Aktion
→ 10-Hz-Trajektorie bei Bewegung/Resize/Banner
→ unmittelbares After-Bild
→ erneuter strukturierter Readback
→ Vergleichsmatrix
→ Evidence
```

Das ist nicht bloß QA hinterher. Das ist die Betriebsweise der Bridge selbst.

Der Fensterscanner muss deshalb vor Terminal, Raute, Overlay, WorldDOM und Eingabe stehen:

```text
Scanner
  ↓
Ziel auswählen
  ↓
Zielidentität prüfen
  ↓
Capabilities lesen
  ↓
Agent/Gate binden
  ↓
Bild + Struktur liefern
  ↓
Overlay räumlich anheften
  ↓
vor jeder Aktion neu prüfen
```

Mein korrigierter Befund: Ich hatte ihn in der letzten Skill-Erweiterung zwar implizit unter „Target discovered“ versteckt, aber das war zu schwach. Der Scanner muss ein eigener Bauabschnitt und ein eigener Harness-Knotenbereich werden:

```text
SCAN_REQUESTED
FRAME_CAPTURED
INVENTORY_READ
TARGET_SELECTED
IDENTITY_VERIFIED
BINDING_CREATED
BINDING_READ_BACK
PRE_ACTION_RESCAN
TARGET_STATE_OBSERVED
```

Das ist der eigentliche Bridge-Kern. Ohne ihn haben wir nur ein Overlay, das zufällig irgendwo herumliegt.
