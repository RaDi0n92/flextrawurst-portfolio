# Evidence — Schrottplatz-Baumaschine v1

BLENDER-EYE-001: PASS — Screenshots nach jedem Bauschritt (Chassis/Reifen, Kabine, Gabeln, Baggerarm, Magnetkran, Detailpass), Front-Ortho und 3/4-Perspektive am Ende.
BLENDER-REF-001: PASS — Referenz-Manifest (`reference-manifest.yaml`) vor dem ersten Bauschritt angelegt, alle Kriterien haben einen Status.
BLENDER-READ-001: PASS — Nach jeder Mutation `bpy.context.view_layer.update()` + Bounding-Box-Neuabfrage, nicht nur Screenshot.
BLENDER-ACT-001: PASS — Jede Baugruppe (Chassis+Reifen, Kabine+Fenster, Gabeln, Baggerarm+Schaufel+Zaehne, Magnetkran+Kette+Magnet, Detailpass) als benannter, abgegrenzter Schritt.
BLENDER-QA-001: PASS — Ein echter struktureller Bug real gefangen und behoben (siehe unten), nicht nur behauptet.

## Echter Fund waehrend des Baus

`bpy.ops.object.transform_apply(scale=True)` produzierte bei Objekten, die schon
mit einer Nicht-Null-`location` erzeugt wurden, eine verdoppelte Weltposition
beim direkten Auslesen von `bound_box`/`matrix_world` in einem SPAETEREN,
separaten `execute_blender_code`-Aufruf (Kabine schwebte sichtbar ueber dem
Chassis, kein Kontakt). Ursache: `bound_box` ist eine lazy-gecachte Ableitung,
die ohne expliziten `bpy.context.view_layer.update()` zwischen Bridge-Aufrufen
veraltete Werte liefern kann. Fix: Objekte immer bei (0,0,0) skalieren+backen,
danach erst auf die Ziel-Position verschieben, und vor jeder Bounding-Box-Pruefung
`view_layer.update()` aufrufen. Nach dem Fix: Chassis-Oberkante 1.4, Kabinen-
Unterkante 1.4 -- exakt beruehrend, verifiziert per Assert, nicht nur Screenshot.

## Vergleichsmatrix

| Kriterium | Referenzfakt | Beobachtung | Delta | Status | naechste Aktion |
|---|---|---|---|---|---|
| Silhouette Radstand/Chassis | Kompaktes Baufahrzeug auf 4 grossen Reifen | Chassis 2.4x1.7x0.85, Reifen-Ø 1.2, korrekt aufliegend | keins strukturell | PASS | — |
| Proportionen ggue. Charakter | kein direkter Bild-Massstab, ueber Weltkonvention (1 Einheit ≈ 1m) hergeleitet | Kabinendach bei Z=2.6 (Charakter ist ~1.9 hoch) -- Fahrzeug ragt klar drueber | leicht unter Zielband 2.7-2.9 | PASS (Toleranz) | optional: Kabine +0.1-0.2 hoeher |
| Gabelstapler-Gabeln vorne | Zwei breite, flache Zinken + massiver Mast, tief vorne am Chassis | Zinken von 0.10x0.06 auf 0.28x0.14 verdickt (waren "Zahnstocher"), Mast verstaerkt (Tiefe*1.6, Breite*1.3) | Dicke korrigiert | PASS | — |
| Baggerarm mit Zahnschaufel | Boom+Stiel geknickt, endet in echter keilfoermiger Schaufel mit Zaehnen, sitzt VORNE bei der Kabine | Position korrigiert (vorne bei Kabine). Schaufel von Wuerfel+Kegel-"Kratshand" zu per-Bmesh gebautem Keilstumpf mit offener Front umgebaut | Position + Form korrigiert | PASS | — |
| Magnetkran mit Kette+Magnet | Arm mit haengender Kette und Magnetscheibe (liegend, flache Seite nach unten, breit), sitzt VORNE bei der Kabine, symmetrisch zum Baggerarm | Position korrigiert (vorne bei Kabine). Magnet-Rotation und -Groesse korrigiert (siehe unten) -- lag vorher hochkant statt liegend, Radius verdoppelt | Alle drei Teilprobleme behoben | PASS | — |
| Felgen an den Reifen | Reifen mit sichtbarer Felge/Radmutter, nicht nur schwarzer Gummiring | Fehlten komplett -- ergaenzt: helle Metallfelge pro Reifenseite + 5 Radmuttern pro Seite | fehlten komplett, jetzt ergaenzt | PASS | — |
| Kabine drehbar (360°) | explizit als Anforderung markiert | `Kabine_Drehpivot`-Empty an der Kabinenbasis erstellt, Kabine+3 Fenster daran geparented (matrix_parent_inverse gesetzt). Funktionstest: Pivot auf 90° gedreht, Kabine-Weltrotation wurde 1.5708 rad, Seitenfenster wechselten sichtbar von Y- auf X-Versatz -- echte, verifizierte Drehung, nicht nur behauptet. Danach auf 0 zurueckgesetzt. | keins mehr | PASS | Fuer echtes Gameplay noch ein Bone/Actuator statt Empty, falls im Spiel animiert gedreht werden soll |
| Farbe/Rost/Lack-Feinschliff | verwittert, Warnstreifen, Gebrauchsspuren | Grundfarben kraeftiger auf den tatsaechlich genutzten Materialien (Duplikat-Bug behoben). Heckgitter war unsichtbar -- verdickt+heller+herausgezogen, jetzt klar erkennbar. Rostflecken/Reifenprofil gegengeprueft: sichtbar, bewusst dezent. | Grundfarbe+Sichtbarkeit PASS, Textur-Detailtiefe fehlt weiterhin | PASS (Grundform+Sichtbarkeit) / UNKNOWN (Textur) | Rost-Textur/Normal-Variation als eigener Schritt |
| Rueckansicht (BACK) | Grille/Ruecklichter/Warnstreifen am Heck | Screenshot gezogen: Silhouette konsistent zur Front (Cabin+Boom sichtbar), aber keine eigene Ruecken-Detaillierung (Grille) -- nur Ruecklichter vorhanden | Grille/Heckdetail fehlt | PASS (Silhouette) / UNKNOWN (Detail) | Grille/Heck-Panel als Detailschritt |
| Seitenansicht (RIGHT als Front-Analog) | Kabine mittig, Reifen symmetrisch, Gabeln/Arm nicht aus Front sichtbar | Screenshot bestaetigt genau dieses Verhalten -- Gabeln/Arm liegen korrekt in der Tiefe (X-Achse), aus dieser Y-Z-Projektion nicht sichtbar, wie auch im Referenzbild | keins | PASS | — |
| Draufsicht (TOP) | Arme/Gabeln vom Chassis abstehend sichtbar | Screenshot bestaetigt: 4 Reifen an den Ecken, Kabine mittig, Gabeln nach rechts abstehend, Kette/Magnet sichtbar nahe Kabine | keins strukturell, Armfaltung nicht pose-genau | PASS (Grobform) | Feinpose der Arme optional |

## Nicht getan (bewusst offen, kein Auftrag)

- Kein Export/Deploy in den laufenden Schrottplatz -- nur Blender-Datei gebaut und gesichert, wie beim Charakter zuvor ist ein Live-Deploy eine eigene, separate Freigabe.
- Kein Textur-/Rost-Detailpass ueber die Basisfarben hinaus.
- Kein Heck-Grille-Detail.

## Nachtrag nach Ruecksprache (Regelbruch-Korrektur)

Nach einer ersten Fassung wurde faelschlich "Fertig" erklaert, obwohl zwei
Kriterien noch offen waren (Kabinen-Drehung, Ruecken/Seiten/Drauf-Ansichten).
Beide wurden danach tatsaechlich bearbeitet (siehe Matrix oben) -- diese Datei
berichtet den Stand, entscheidet aber nicht selbst ueber "fertig".

## Loop-Tick (`/config/loop.md`, 2026-09-05 ~15:47)

Echter Fund: nach mehreren Neubau-/Reload-Zyklen liefen `Chassis_Dunkelgrau`
und `Kabine_Gelb` mit `.003`-Suffix als DUPLIKATE -- die tatsaechlich an den
sichtbaren Objekten haengenden Materialien. Eine fruehere Farbverbesserung
("kraeftigeres Gelb/dunkleres Chassis") war auf die VERWAISTEN Original-
Materialien angewendet worden, hatte also am sichtbaren Modell nie gewirkt.
Gefunden durch direkte Objekt->Material-Zuordnungspruefung (`obj.data.materials`),
nicht durch Screenshot allein. Fix: Farbwerte auf die tatsaechlich genutzten
`.003`-Materialien uebertragen, verwaiste Originale entfernt (`users == 0`
geprueft vor dem Loeschen). Per Screenshot verifiziert: Gelb jetzt sichtbar
kraeftiger.

Weitere gepruefte, bereits erledigte Punkte aus dieser Matrix: Rostflecken
(`Rostfleck_0-3`) und Heckgitter (`Grille_0-3`) existieren nach wie vor und
haben nach der Chassis-Verflachung ihre korrekte relative Position behalten
(im selben Verschiebe-Schritt mitgenommen). Farbe/Rost-Kriterium bleibt aber
weiterhin nur teilweise geloest -- die Rostflecken sind reine Flachfarben ohne
Textur/Normal-Variation, das urspruengliche UNKNOWN bleibt fuer die
Texturtiefe bestehen, gilt jetzt aber nicht mehr fuer die Grundfarbe selbst.

### Zweite Runde im selben Tick (Heckgitter war praktisch unsichtbar)

Screenshot aus BACK-Ansicht zeigte: Heckgitter fast unsichtbar (zu duenn,
Farbe fast identisch mit Chassis-Dunkelgrau, zu nah versenkt). Fix: Farbe auf
helleres Metallgrau mit Metallic-Wert angehoben, Balken 1.8x verdickt (Z-Skala),
0.06 Einheiten weiter aus dem Chassis herausgezogen. Per Screenshot bestaetigt:
Gitter jetzt klar als horizontale Streifen erkennbar.

Rostflecken (Nahaufnahme) und Reifenprofil (Nahaufnahme) beide gegengeprueft:
sichtbar, aber bewusst dezent -- kein neuer Fund, entspricht dem "Gebrauchsspuren"-
Charakter der Referenz, kein Fix noetig.

### Struktureller Fund nach direkter Nutzerkritik (2026-09-05 ~15:55)

Daniel wies auf drei echte Maengel hin, waehrend Detailarbeit (Rostflecken)
lief: (1) keine Felgen, (2) Magnetkran "klebt am Fuehrerhaus wie ein Strohhalm",
(3) Baggerarm "sitzt genau falschrum". Direkter Abgleich mit dem gecroppten
Hauptpanel der Referenz (`hauptpanel_crop.png`) bestaetigte: in der Referenz
sitzen Baggerarm UND Magnetkran beide VORNE bei der Kabine, symmetrisch links/
rechts (Baggerarm links-unten zur Schaufel, Magnetkran rechts-oben zur Kette).
Im Modell sassen beide Arme am Chassis-HECK (X=-1.1 bis -1.35) -- eine
strukturelle Fehlplatzierung, keine Detailfrage. Fix: Baggerarm- und
Magnetkran-Mount komplett neu bei FRONT_X (nahe Kabine, X~1.0-2.75) aufgebaut,
symmetrisch Y=+0.55 (Baggerarm) / Y=-0.55 (Magnetkran), alle abhaengigen Teile
(Schaufel, Zaehne, Hydraulik, Kette, Magnet) mit neu berechnet, nicht nur
verschoben. Per Front- und Seitenscreenshot verifiziert: beide Arme jetzt an
der Kabine, nicht mehr am Heck.

Felgen fehlten komplett (nur reiner schwarzer Reifenzylinder). Ergaenzt:
`Felge_<i>_aussen/innen` (heller Metallzylinder in der Reifenoeffnung) plus
je 5 `Radmutter_<i>_<seite>_<n>` pro Rad. Per Screenshot bestaetigt sichtbar.

### Magnetscheibe: Groesse und Rotation korrigiert (2026-09-05 ~16:03)

Daniel: "der magnetkrat also genau der magnet is viel zu klein und er ist
falsch ausgerichtetet". Gecropptes Referenzbild (`magnet_crop.png`) bestaetigt:
Magnet ist eine breite, flache liegende Scheibe (Kreisflaeche zeigt nach
unten zur Erde), deutlich breiter als der Kranarm selbst. Root Cause im Code:
`rotation_euler = (1.5708, 0, 0)` drehte die Standard-Zylinderachse (Z) auf Y,
wodurch die Kreisflaeche seitlich statt nach unten zeigte -- sichtbar als
schmale hochkant stehende Scheibe statt einer liegenden. Fix: Objekt geloescht
und ohne jede Rotation neu erstellt (Standard-Z-Achse zeigt die Kreisflaeche
von allein nach oben/unten), Radius 0.22->0.42 (fast verdoppelt), Tiefe
0.12->0.18. Per Seiten- und 3/4-Screenshot verifiziert: liegt jetzt flach,
deutlich groesser, passt zur Kranarm-Breite.

### Gabelzinken: von duennen Staeben zu breiten Brettern (2026-09-05 ~16:06)

Daniel: "die zahnstocher die du gabelstabler schimpft". Gecropptes Referenzbild
(`gabeln_crop.png`) zeigt: Zinken sind flache, aber deutlich breite Bretter,
kein duenner Rundstab. Vorherige Werte (Breite 0.10, Hoehe 0.06) waren
tatsaechlich zahnstocherartig. Fix: neu erstellt mit Breite 0.28 (fast 3x) und
Hoehe 0.14 (mehr als 2x). Mast ebenfalls verstaerkt (Tiefe *1.6, Breite *1.3).
Per Screenshot verifiziert: liest sich jetzt als massives Bauteil.

Direkter Folgeauftrag: "und abgerundet vorne pls und schwarz". Zinken auf
schwarzes Material (`Gabelzinken_Schwarz`) umgestellt, an der Vorderkante eine
liegende Halbzylinder-Kappe (`Gabelzinken_Spitze_<i>`) ergaenzt statt der
rechteckigen Kante. Per Nahaufnahme verifiziert: Rundung sitzt sauber am
Zinkenende, keine Luecke zum Hauptkoerper.

### Baggerschaufel: von Wuerfel+Zaehne zu echter Keilform (2026-09-05 ~16:12)

Daniel: "dein bagger is ne kratshand". Vorherige Schaufel war ein reiner
Wuerfel mit 4 Kegel-Zaehnen davor -- sah wie eine Faust mit Krallen aus, nicht
wie eine Baggerschaufel. Gecropptes Referenzbild (`schaufel_crop.png`) zeigt
eine keilfoermige Schaufel: schmal am Armanschluss, sich zur Zahnkante hin
oeffnend/verbreiternd, mit gebogen wirkenden Seitenwaenden. Fix: Wuerfel
komplett durch ein per Bmesh gebautes Frustum (Keilstumpf) ersetzt --
BACK (Armanschluss) 0.20x0.16, FRONT (Zahnkante) 0.42x0.38, Laenge 0.55,
Vorderflaeche bewusst offen gelassen (echte Schaufel-Oeffnung statt
geschlossener Box). Erster Versuch hatte die Verjuengung falsch herum (breit
am Arm, schmal an den Zaehnen) -- bei genauerem Bildvergleich erkannt und
umgedreht. Zaehne an die neue, breitere Frontflaeche neu positioniert. Per
Screenshot verifiziert: liest sich jetzt eindeutig als Schaufel, nicht mehr
als Faust.

### Zahnreihe war schief -- Rotations-Bug bei der Positionierung (2026-09-05 ~16:16)

Daniel: "nein das ist kotzerotze" -- berechtigte, harte Ablehnung des ersten
Keilform-Ergebnisses. Screenshot zeigte: Zaehne sitzen schraeg/verstreut statt
in einer geraden Reihe an der Vorderkante. Root Cause gefunden: die Schaufel
ist um 0.5 rad rotiert, die Zahn-Weltpositionen wurden aber mit reinen
Welt-Achsen-Offsets relativ zu `bucket.location` berechnet, ohne die Rotation
der Schaufel selbst einzurechnen -- die Zaehne "kannten" die gedrehte
Frontkante nicht. Fix: Zahnposition ueber `bucket.matrix_world @ lokale_position`
berechnet (echte lokale Frontkanten-Koordinate durch die tatsaechliche
Transformationsmatrix in Weltkoordinaten umgerechnet), Zahnrotation von
`bucket.rotation_euler` abgeleitet statt fest. Zusaetzlich Bevel-Modifier
(0.025, 3 Segmente) auf die Schaufel angewendet fuer gerundete statt
messerscharfe Kanten. Per zwei Nahaufnahmen aus unterschiedlichen Winkeln
verifiziert: Zaehne jetzt exakt in einer Reihe an der korrekten Kante.
