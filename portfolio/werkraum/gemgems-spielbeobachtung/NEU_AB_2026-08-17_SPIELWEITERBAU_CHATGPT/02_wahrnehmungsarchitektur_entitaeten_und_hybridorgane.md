# 02 · Wahrnehmungsarchitektur · Entitäten, Tiere, Technik, AI und Hybridorgane

**Status:** NEUER KONZEPTKÖRPER AB 17.08.2026  
**Rohherkunft:** `01_rohgespraech_2026-08-17_wahrnehmung_spielsprachen_kontextinjektor.md`

---

## Kernsatz

**Jede Entität darf eine eigene Wahrnehmungsphysik besitzen.**

Wahrnehmung ist im Spiel nicht bloß Bildschirmfilter oder Bonuswert. Sie entscheidet, welche Eigenschaften der kanonischen Welt für eine bestimmte Entität überhaupt relevant, sichtbar, hörbar, messbar, fühlbar oder handhabbar werden.

Arbeitsmodell:

`KANONISCHE WELT → VERKÖRPERUNG → WAHRNEHMUNGSAPPARAT → ERLEBNIS / HANDLUNG`

Der Weltzustand bleibt derselbe. Unterschiedlich ist, welche Signale eine Entität daraus gewinnt und wie sie diese Signale erlebt.

---

## Wahrnehmungsklassen

### Menschliche Basis

Der Spieler beginnt mit einer menschlichen Wahrnehmungsbasis. Diese kann später erweitert, verändert, zeitweise überlagert oder mit anderen Wahrnehmungsorganen kombiniert werden.

### Biologische Wesen

Bei Tieren und anderen biologischen Wesen soll reale Wahrnehmungsforschung Ausgangsmaterial sein.

Mögliche Forschungsfelder:

- Facettenaugen und zeitliche Auflösung bei Insekten,
- UV- oder Polarisationswahrnehmung,
- artspezifische Farbräume,
- Hörbereiche außerhalb menschlicher Grenzen,
- Echolokation,
- Geruchs- und chemische Wahrnehmung,
- Magnetorezeption,
- Druck-, Vibrations- oder Strömungswahrnehmung,
- unterschiedliche Blickfelder und räumliche Auflösung.

Bei jeder späteren Umsetzung werden getrennt:

1. `WISSENSCHAFTLICH_NACHGEWIESEN`
2. `PLAUSIBLE_INTERPRETATION`
3. `SPIELERISCHE_ÜBERSETZUNG`
4. `FREI_ERFUNDENE_ERWEITERUNG`

### Technische Geräte

Technische Entitäten erhalten nicht automatisch menschliche Augen. Ihre Wahrnehmung darf aus Funktion, Sensorik, Grenzen und inneren Zuständen entstehen.

Beispielrichtungen, noch nicht kanonisiert:

- Staubsaugerroboter: erreichbare Fläche, Hindernisse, Schmutzverteilung, Ladestation, Funkraum, Akkuzustand, Kartenvertrauen.
- Drucker: Papierwege, Druckwarteschlangen, Temperatur, Materialvorrat, Stau, mechanischer Widerstand, Verbindungszustand.
- Mikrowelle: Zeit, Leistungsstufe, Türzustand, Innenraum, technische Wärme-/Feuchtezustände als spielerische Übersetzung.
- Toaster: Heizelementzustand, Zeit, Widerstand, Materialzustand, Auswurfschwellwert.
- Auto / Flugzeug: Geschwindigkeit, Orientierung, Sensorik, Energie, Strecken, Warnzustände, technische Umgebungsmodelle.
- alter Algorithmus / alte Software: Eingaben, Trigger, Ports, Zustände, Fehlergrenzen, Zeitfenster, Warteschlangen und erreichbare Ressourcen.

Designregel: **Funktion kann Wahrnehmungsphysik werden.**

### AI- und Codewesen-Wahrnehmung

Es gibt keine einheitliche `AI-Sicht`.

Verschiedene AI-Ströme, Codewesen und künstliche Entitäten dürfen unterschiedliche Wahrnehmungskörper besitzen, beispielsweise über:

- semantische Beziehungen,
- Provenienz und Herkunft,
- Zustandsänderungen,
- Unsicherheit,
- Konflikt- oder Ähnlichkeitsfelder,
- Aktivität anderer Entitäten,
- symbolische statt optische Nähe,
- Prozesse, Dateien und Ereignisse,
- tatsächliche visuelle Wahrnehmung, sofern das Wesen einen Bild-/Vision-Leib besitzt.

Diese Wahrnehmung wird später je Entität eigenständig definiert und nicht durch ein generisches AI-HUD ersetzt.

---

## Wahrnehmungsorgane des Spielers

Der Spieler kann perspektivisch Wahrnehmungsorgane oder Wahrnehmungsfragmente erwerben, erlernen, mit Wesen zusammenwachsen oder kombinieren.

Nicht:

`+8 Wahrnehmung`

Sondern beispielsweise:

`MENSCHLICHE BASIS + BIOLOGISCHES FRAGMENT + TECHNISCHES ORGAN + WESENORGAN`

Diese Zusammensetzung kann verändern:

- was überhaupt sichtbar wird,
- welche Geräusche Bedeutung bekommen,
- welche Zeitauflösung erlebt wird,
- welche Materialien unterscheidbar werden,
- welche Distanzen oder Bewegungen relevant werden,
- welche Maschinen und Wesen lesbar werden,
- welche Gefahren erkannt werden,
- welche Wege oder Interaktionen überhaupt zugänglich erscheinen.

Wichtig: Die Kombination verändert Wahrnehmung und Handlungszugang, nicht heimlich den kanonischen Weltzustand.

---

## Wahrnehmung × Verkörperung × Performance

Wahrnehmung ist nicht dasselbe wie LOD oder Qualitätsprofil.

- `Verkörperung` beantwortet: Wie vollständig besitzt ein Objekt gerade einen berechneten und dargestellten Körper?
- `Wahrnehmung` beantwortet: Welche Eigenschaften dieses Weltobjekts kann diese Entität überhaupt aufnehmen und deuten?
- `Performanceprofil` beantwortet: Wie teuer darf diese konkrete Verkörperung auf dem aktuellen Gerät sein?

Arbeitsmatrix:

`WAS MUSS DIE ENTITÄT WAHRNEHMEN? × WIE VOLLSTÄNDIG IST DAS OBJEKT VERKÖRPERT? × WAS DARF DAS GERÄT KOSTEN?`

Manche Wahrnehmungsarten können billigere Darstellungen erlauben. Andere können teurer sein. Ressourcenersparnis ist möglicher Nebeneffekt, nicht der Grund, Wahrnehmungen zu erfinden.

---

## Beispiel: derselbe Baum

`world_atom_id = BAUM_00441`

Variante A:

- Verkörperung: `FERNKÖRPER`
- Betrachter: Mensch
- Wahrnehmung: `human_base + bee_fragment + technical_distance`

Variante B:

- Verkörperung: `NAHKÖRPER`
- Betrachter: anderes Wesen
- Wahrnehmung: `species_base + chemical_perception`

Der Baum bleibt `BAUM_00441`.

Keine Wahrnehmung erzeugt heimlich eine zweite Fake-Welt.

---

## Forschungsauftrag für später

Tier- und Biowahrnehmung wird Art für Art recherchiert. Für jede relevante Art entstehen später:

- Quellen,
- belegte Sinnesfähigkeiten,
- Grenzen und Unsicherheiten,
- spielerisch interessante Übersetzungen,
- mögliche kombinierbare Wahrnehmungsorgane,
- Performancefolgen,
- Interaktionsfolgen.

Dieser Forschungsblock ist noch nicht ausgeführt.

---

## Noch offen / gemeinsam zu entscheiden

- Welche Wahrnehmungsorgane besitzt der menschliche Spieler zu Beginn?
- Wie wird Zusammenwachsen mit einem Wesen ausgelöst und begrenzt?
- Können Organe dauerhaft, temporär, kombinierbar oder konfliktbehaftet sein?
- Welche Wahrnehmung besitzen einzelne Codewesen konkret?
- Welche technischen Entitäten werden wirklich spielbar oder verschmelzbar?
- Wie werden Wahrnehmungen visuell, auditiv, haptisch und über UI übersetzt?
- Wie verhindert man, dass Wahrnehmungsvielfalt zu unlesbarem Effektchaos wird?

Diese Entscheidungen sind `GEMEINSAM_ZU_FEINJUSTIEREN`.
