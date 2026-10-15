# Blender-Evidenz — sehr großer Mobilbagger

Datum: 2026-09-05  
Zielinstanz: linker Blender, PID 3333210, Gateway `127.0.0.1:40985`  
Referenzmanifest: `reference_manifest.yaml`, Revision `ref-20260905-mobilbagger-01`

## Ergebnis

Die Referenz wurde additiv als Sammlung `SCHROTTPLATZ_MOBILBAGGER` in die bestehende Savage-Szene eingebaut. Der Bagger hat eine Weltgröße von `18.657 × 12.685 × 10.405`, während der erhaltene Savage-Blockout `1.711 × 1.141 × 3.650` misst. Die Größenabsicht „sehr groß“ ist damit sichtbar und strukturell belegt.

Gespeichert ist der Stand in:

`/config/Desktop/VPS_ROOT/werkraum/_codex/berichte/blender/Codex-Agent-Daniel-Savage.blend`

## Bounded actions

1. `foundation` — neue Asset-Sammlung, Root, Materialien, Chassis, Unterbau, vier Räder.
2. `placement-fix` — Parent-Matrix korrigiert; vorhandene Savage-Objekte nicht verändert.
3. `cab-and-front-forklift` — Kabine mit Drehpivot, Scheiben, Mast und zwei langen Gabeln.
4. `booms-and-tools` — linker Baggerarm mit Schaufel sowie rechter Magnetkran mit Kette und Magnet.
5. `detail-pass-motion` — Profilringe, Warn-/Service-Details, Schläuche und Kabinen-Keyframes.
6. `presentation-camera` — eigene Baggerkamera und linker Viewport auf Kameraansicht gesetzt.
7. `camera-correction` — Blickrichtung nach Parent-Update neu berechnet.
8. `frame-restore` — Frame 1 wiederhergestellt, gespeichert, Viewport-Refresh ausgeführt.
9. `framing-repair` — Viewport nach Animationsprüfung wieder auf Kameraansicht und Zoom 0 gesetzt.
10. `tread-and-wear-pass` — 48 Reifenstollen und sechs gezielte Rostflächen ergänzt.
11. `mechanical-detail-pass` — sechs sichtbare Hydraulikeinheiten, fünf Gelenkbolzen und zehn Radmuttern ergänzt.
12. `motion-groups` — Arm, Gabelhub und Magnet als getrennte Eltern-/Keyframe-Gruppen angelegt.
13. `pivot-cleanup` — technische Pivots ausgeblendet, Zustand und Magnetposition geprüft.
14. `magnet-pivot-local-fix` — zwölf Magnetkinder auf korrekte Pivot-Local-Transforms zurückgesetzt.
15. `combined-motion-frame-048` — Arbeitsframe 48 sichtbar geprüft.
16. `quality-pass-frame-001` — Frame 1 wiederhergestellt, gespeichert und final gelesen.

Ein Detailpass-Script meldete am Ende einen Blender-5-API-Fehler beim Zugriff auf `Action.fcurves`; die Geometrie war zu diesem Zeitpunkt bereits angelegt. Der Zustand wurde danach gelesen, bestätigt und nur um die Metadaten-Rückmeldung ergänzt. Es wurde kein Aufbau doppelt erzeugt.

## Vergleichsmatrix

| Kriterium | Referenzfakt | Beobachtung / Readback | Delta / Toleranz | Status |
|---|---|---|---|---|
| Größe / Dominanz | Maschine soll sehr groß sein | Asset 18.657 breit, 12.685 tief, 10.405 hoch; Savage bleibt 3.650 hoch | deutlich dominantes Objekt | PASS |
| Grundsilhouette | gelber mobiler Arbeitskörper auf Rädern | gelbes Chassis/Kabine, graphitfarbener Unterbau, vier Reifen | stilisierte Blockout-Interpretation | PASS |
| Frontwerkzeug | Gabelstapler mit Mast und langen Gabeln | `Fork_Mast_L/R`, `Fork_L/R`, zwei lange sichtbare Gabeln | strukturell vorhanden | PASS |
| Linkes Werkzeug | gelber Baggerarm mit Schaufel | `Excavator_Boom_L`, `Excavator_Dipper_L`, Bucket und vier Zähne | blockout statt Rost-Mikrodetail | PASS |
| Rechtes Werkzeug | dunkler Magnetkran mit hängendem Rundmagnet | zwei Graphit-Booms, sechs Kettenringe, Rundmagnet | strukturell vorhanden | PASS |
| Palette | Gelb/Ocker, Graphit, Stahl, dunkles Glas | neun eigene `SchrottplatzBagger_*`-Materialien | Referenzpalette getroffen | PASS |
| Präsentation | dunkler Studiohintergrund, 3/4-Ansicht | eigene `SchrottplatzBagger_PresentationCamera`, sichtbarer finaler Viewport | framing zeigt Gesamtasset | PASS |
| Bewegung | Referenz markiert Kabine als 360° drehbar | `Cab_Drehpivot`, Action Frame 1–96; Frame 1 = 0°, Frame 48 = 3.092 rad | echte Zwischenpose gelesen | PASS |
| Provenienz | bestehende Arbeit bleibt erhalten | `DANIEL_SAVAGE_3D_BLOCKOUT` bleibt vorhanden; neuer Inhalt nur in eigener Sammlung | keine Löschung/Ersetzung | PASS |
| Gebrauchsspuren | Referenz enthält Rost-/Gebrauchsakzente | aktueller Stand ist sauber stilisierter Low-Poly-Blockout | Mikrorost bewusst offen | PARTIAL / offen |

## Evidence witnesses

- `baseline-left/baseline-left-viewport.png` — linker Ausgangsviewport.
- `baseline-left/after-placement-fix-viewport.png` — sichtbarer Parent-/Platzierungsfix.
- `baseline-left/after-cab-forklift-viewport.png` — Kabine und Gabeln geprüft.
- `baseline-left/after-booms-tools-viewport.png` — Arm, Schaufel, Kran und Magnet strukturell geprüft.
- `after-camera-correction-viewport.png` — erster vollständiger 3/4-Frame.
- `after-detail-pass-viewport.png` — Detailpass sichtbar geprüft.
- `final/final-left-mobilbagger-refreshed.png` — finaler Startframe nach Refresh.
- `final/frame-048-cab-rotation.png` — Zwischenframe mit gedrehter Kabine.
- `final/final-left-mobilbagger-restored.png` — historischer Capture vor dem letzten Refresh; nicht als finaler Sichtzeuge verwenden.
- `quality-pass/after-tread-wear-pass.png` — sichtbare Reifenstollen und Rostakzente.
- `quality-pass/after-mechanical-detail-pass.png` — Hydraulik, Gelenke und Radmuttern.
- `quality-pass/after-magnet-pivot-fix.png` — korrigierter Magnet unter dem Kran.
- `quality-pass/combined-motion-frame-048.png` — kombinierter Arbeitsframe.
- `quality-pass/final-quality-pass-frame-001.png` — gültiger finaler Qualitätsframe.

Der finale gültige Sichtzeuge für den ersten Bauabschnitt ist `final/final-left-mobilbagger-refreshed.png`; der gültige Qualitäts-Sichtzeuge ist `quality-pass/final-quality-pass-frame-001.png`. Der letzte strukturierte Readback meldet Frame 1, 240 Szenenobjekte, 182 Assetobjekte, aktive Präsentationskamera, korrekt sitzenden Magneten und erhaltene Savage-Sammlung.

Die 10-Hz-Trajektorie wurde für den falschen Port 9876 einmal beobachtungs-only gestartet und gehört zur rechten Claude-Instanz; sie ist nicht Teil der linken Blender-Evidenz. Der linke Gateway-Capture dauerte einzeln etwa 2.2–3.1 s, daher wird keine 10-Hz-Cadence behauptet. Für jede bedeutende Mutation liegen unmittelbare Vor-/Nachher-Sichtzeugen und ein strukturierter Readback vor.

## Skill gates

- `BLENDER-EYE-001: PASS` — unmittelbare Vor-/Nachher-Screenshots für die bounded actions vorhanden; fehlende 10-Hz-Cadence des linken Gateways ausdrücklich dokumentiert.
- `BLENDER-REF-001: PASS` — alle in-scope Referenzkriterien aus dem Manifest haben einen Matrixeintrag.
- `BLENDER-READ-001: PASS` — finaler Blender-Readback nach Restore und Viewport-Refresh vorhanden.
- `BLENDER-ACT-001: PASS` — jede Mutation ist benannt, getrennt und nachgelesen.
- `BLENDER-QA-001: PASS` — die angeforderte Größe und die fünf Hauptsilhouettenmerkmale sind erfüllt; Rost-Mikrodetail bleibt als klar markierte optionale Folgearbeit offen.

OUTCOME: PASS

## Blender-Magnet-Testschicht / sichtbarer Pickup-Nachweis

Auf Daniels `go` wurde die bisherige Magnetanzeige um eine klar getrennte
Blender-Testschicht ergänzt. Die Collection
`SchrottplatzRealistisch_MAGNET_TESTSCHROTT` enthält vier markierte Rost-/Stahl-
Testteile. Sie sind keine Ersetzung der Referenzgeometrie und keine behauptete
Vollphysik, sondern bewusst begrenzte Testobjekte für Anziehung, Halten,
Freigabe und Reset.

Für die Sichtbarkeit wurde zusätzlich `SchrottplatzRealistisch_MagnetTestCamera`
angelegt und im linken `VIEW_3D` als aktive Kamera gesetzt. Die vorhandene
Realistic-Präsentationskamera bleibt separat erhalten. Dadurch sieht Daniel die
Magnetbewegung und Kamerawechsel direkt in seinem Blender-Fenster; der zweite
Kameratest hatte im Capture sichtbar einen anderen Bildausschnitt.

### Testablauf und Readback

1. Startzustand: vier Teile unter dem Magneten, Modus `FAHREN`, Magnet aus,
   Frame `1`, alle Testteile ohne Parent.
2. Magnettest: Modus `MAGNETKRAN`, Magnet an, `60 × 0,05 s` begrenzte Ticks.
   Ergebnis: alle vier Teile `state=held`, Parent jeweils
   `SchrottplatzRealistisch_CTRL_Magnet_Payload`, Statuslicht `1200.0`.
3. Freigabetest: Magnet aus. Ergebnis: alle vier Teile `released`, Parent
   `None`, Statuslicht `0.0`.
4. Reset: `schrottplatz.reset_magnet_test` legt alle vier Teile wieder auf ihre
   gespeicherten Startpositionen und speichert den Teststart erneut.

Sichtzeugen: `magnet-test-camera-ready.png`, `magnet-test-held.png`,
`magnet-test-released.png` und `magnet-test-final-ready.png`. Der letzte
Readback bestätigt: Datei `Codex-Agent-Daniel-Savage.blend`, Kamera
`SchrottplatzRealistisch_MagnetTestCamera`, Frame `1`, Modus `FAHREN`, vier
Testteile im Zustand `ready`, Magnet aus.

| Kriterium | Beobachtung | Status |
|---|---|---|
| Testteile sichtbar | Magnet-Testkamera zeigt alle vier Teile getrennt unter dem Magneten | PASS |
| Anziehung | vier Teile erreichen `held` im 3-m-Feld | PASS |
| Halten | vier Teile sind am Magnet-Payload parented | PASS |
| Ausschalten | vier Teile werden entparented und als `released` markiert | PASS |
| Wiederholbarkeit | Reset stellt alle vier Startpositionen wieder her | PASS |
| Vollphysik | nicht behauptet; Schwerkraft/Kollisionen bleiben offen | UNKNOWN |

OUTCOME: PASS

## Sichtbarer linker Viewport / Kamerasynchronisierung

Daniel meldete, dass die Aktionen zwar im Blender-Zustand ankamen, sein linker
Viewport aber in einer unveränderten Gesamtsicht blieb. Die Ursache war ein
freier Viewport-Blick: Szene- und Renderkamera wurden geändert, der sichtbare
`VIEW_3D`-Bereich blieb davon unabhängig.

Der linke Viewport ist nun explizit in der Kameraansicht und auf
`SchrottplatzRealistisch_RealisticPresentationCamera` gesetzt. Der kontrollierte
Kameratest wechselte live auf `SchrottplatzBagger_PresentationCamera`; der
Viewport wechselte sichtbar mit. Danach wurde die Realistic-Kamera als
Startkamera wiederhergestellt und zusammen mit Frame `1` gespeichert.

Beleg: `visible-camera-after-viewport.png` zeigt den ersten sichtbaren Wechsel,
`camera-switch-visible-test.png` den zweiten Kamerablick, und der abschließende
Readback meldet `scene_camera=SchrottplatzRealistisch_RealisticPresentationCamera`,
`VIEW_3D perspective=CAMERA`, Frame `1`, Tastaturlistener aktiv.

| Kriterium | Referenz/Forderung | Beobachtung | Status |
|---|---|---|---|
| sichtbarer Startblick | Daniels linker Blender zeigt den gesteuerten Blick | VIEW_3D in Kameraansicht | PASS |
| Kamerawechsel sichtbar | Wechsel soll wie bei Claude im Bildschirm ankommen | Wechsel auf zweite Kamera im Capture sichtbar | PASS |
| Startzustand erhalten | Realistic-Hero-Blick, Frame 1 | Realistic-Kamera und Frame 1 gespeichert | PASS |

OUTCOME: PASS

## Keyboard-Steuerung / vier echte Bedienmodi

Die gewünschte Bedienlogik ist als modal laufender Blender-Controller im Add-on
`schrottplatz_realistic_controls.py` umgesetzt. `R` schaltet ausschließlich in
dieser Reihenfolge: `FAHREN → STAPLER → BAGGER → MAGNETKRAN → FAHREN`.
Beim Umschalten werden gehaltene Bewegungstasten geleert; die jeweils nicht
aktiven Road-to-Glory-Actions bleiben neutralisiert. Die automatische
Initialisierung startet den Listener beim Öffnen der gespeicherten Datei; `ESC`
beendet ihn, der Sidebar-Button kann ihn wieder starten.

| Modus | Eingabe | Wirkung |
|---|---|---|
| Fahren | `W/S` | komplette Maschine vor/zurück bewegen |
| Fahren | `A/D` | Fahr-Root links/rechts lenken |
| Stapler | `W/S` | nur Gabelträger und Gabeln heben/senken; Mast bleibt am Chassis |
| Bagger | `W/S` | Baggerarm Arbeitswinkel auf/ab |
| Bagger | `A/D` | kompletter oberer Baggeraufbau am Drehkranz links/rechts |
| Bagger | `Q/E` | nur Schaufel einrollen/auskippen |
| Magnetkran | `W/S` | Magnetlast samt Kette heben/senken |
| Magnetkran | `A/D` | Magnetkran am eigenen Basis-Drehpunkt links/rechts |
| Magnetkran | `Leertaste` | Magnetstatus an/aus; blaues Statuslicht und gespeicherter Zustand |

Die mechanischen Grenzen sind echte Wrapper-Hierarchien: `CTRL_Drive` bewegt
`Root` und die separate Staplerbaugruppe gemeinsam; `CTRL_Bagger_Yaw` trägt
Kabine, Baggerarm und sichtbare obere Details; `CTRL_Magnet_Yaw` trägt den
Magnetboom. Damit wird nicht mehr ein kompletter, falscher Gesamt-Pivot bewegt.

### Live-Belegkette

- `keyboard-controls-neutral-render.png` — gespeicherter neutraler Startzustand nach dem Wrapper-Aufbau.
- Helper-Test `keyboard_step()` mit Rückkehr auf Frame 1 und Modus Fahren:
  - Fahren `W+D`: Drive-Position `[0.0, 0.12, 0.0]`, Lenkwinkel `3.25°`.
  - Stapler zehn `W`-Ticks: Gabelträger `0.5 m`, Mastspitze unverändert bei Welt-Z `5.8514`, Träger-Z `3.0807`.
  - Bagger `W+A+Q`: Arm `2.25°`, Aufbau `-4.5°`, Schaufel `-4.5°`.
  - Magnet `W+A` plus Leertastenstatus: Magnetlast `0.06 m`, Drehung `-4.5°`, Statuslicht `1200.0`, `enabled=true`.
  - Vier Moduswechsel endeten wieder in `FAHREN`; danach wurden alle Testwerte auf neutral zurückgesetzt.
- AutoStart-Readback: `keyboard_running=true`, Modus `FAHREN`, gespeicherte Datei `Codex-Agent-Daniel-Savage.blend`.

Die Szene bleibt metrisch (`1 BU = 1 m`), die Realistic-V2-Herkunft und die alte
Sammlung bleiben erhalten. Die rechte Claude-Instanz auf Port `9876` wurde
nicht angesprochen; alle Live-Mutationen liefen über den linken Blender auf
Port `40985`.

OUTCOME: PASS

## Staplerhub-Mechanik korrigiert 2026-09-06

Daniel bemerkte beim Live-Test, dass die Staplerbewegung den gesamten Mast mitzog. Der Readback bestätigte die Ursache: `SchrottplatzRealistisch_Forklift_LiftAction` animierte den übergeordneten `Forklift_Pivot` mitsamt Mast, Mastschienen, Mastkopf und Gabelträger.

Die fünf statischen Mastteile (`Fork_Mast_L/R`, `Fork_MastRail_L/R`, `Fork_MastTop`) wurden deshalb mit erhaltener Weltmatrix direkt unter `CTRL_Forklift_Lift` am Chassis verankert. Der animierte `Forklift_Pivot` trägt jetzt nur noch den Gabelträger und dessen Gabel-/Lastgruppe. Die Herkunft wurde nicht gelöscht; die bestehende Action bleibt erhalten und steuert nun den mechanisch richtigen Unterzweig.

### Mechanischer Readback

| Zustand | Mastkopf Welt-Z | Gabelträger Welt-Z | Ergebnis |
|---|---:|---:|---|
| Frame 1 | `5,851 m` | `2,581 m` | neutrale Startpose |
| manuell `Gabelträger +0,4 m` | `5,851 m` | `2,981 m` | nur Gabelträger verändert |
| Road-to-Glory Frame 48 | `5,851 m` | `3,431 m` | nur Gabelträger animiert |

`mast_unchanged=true` und `carriage_moved=true` wurden für beide Bewegungsarten nachgelesen. Der irreführende komplette `Stapler heben`-Regler wurde aus dem Panel entfernt; sichtbar bleibt nur der korrekte Gabelträgerhub. Der Mast bleibt bei `3,8 m` Geometriehöhe am Chassis.

Sichtzeuge: `stapler-correct-carriage-only-frame-048-render.png`. Gespeicherter Endzustand: Frame `1`, `STAPLER`-Solo, alle manuellen Zusatzwerte `0`, Datei `Codex-Agent-Daniel-Savage.blend`.

OUTCOME: PASS

## Live-Debug: eindeutiger Solo-Startmodus 2026-09-06

Daniel meldete, dass beim Drücken von `Space` weiterhin alle Werkzeuge liefen. Der Live-Readback der linken Blender-Instanz zeigte tatsächlich `schrottplatz_active_tool=ALL`; das Panel war geladen, aber der zuvor gespeicherte Startmodus war zu breit. Das war der konkrete Fehler, nicht ein Blender- oder Gateway-Problem.

Der Startzustand wurde deshalb auf `STAPLER` gesetzt und gespeichert. Der aktuelle Readback bestätigt Frame `1`, Modus `STAPLER` und exakt nur `SchrottplatzRealistisch_Forklift_LiftAction`; Kabine, Baggerarm und Magnetkran haben in diesem Modus keine aktive Action. `BAGGER`, `MAGNETKRAN` und `ALLE ZUSAMMEN` bleiben über die Moduszeile auswählbar.

Die Add-on-Standardeinstellung wurde ebenfalls von `ALL` auf `STAPLER` geändert, damit ein frisch geladenes Bedienpanel nicht versehentlich alle Werkzeuggruppen gleichzeitig startet. Die neutralen manuellen Zusatzwerte bleiben auf `0`; der Mast bleibt `3,8 m`.

OUTCOME: PASS

## Getrennte Arbeitsmodi 2026-09-06

Die erste Panel-Fassung war für Daniel nicht ausreichend: Sie bot getrennte Zusatzregler, aber die gemeinsame Road-to-Glory-Timeline konnte weiterhin alle Werkzeuggruppen zusammen bewegen. Dieser Mangel wurde nicht kaschiert. Das Panel wurde um drei echte Solo-Arbeitsmodi erweitert:

| Modus | aktive Actions | Verhalten der übrigen Werkzeuge |
|---|---|---|
| `BAGGER` | Kabinenrotation + Baggerarm | Actions pausiert, Frame-1-Grundpose |
| `STAPLER` | Staplerhub | Actions pausiert, Frame-1-Grundpose |
| `MAGNETKRAN` | Magnetkran | Actions pausiert, Frame-1-Grundpose |
| `ALL` | alle vier Road-to-Glory-Actions | gemeinsamer Animationsmodus |

Die neutralen lokalen Posen der vier animierten Pivots werden beim Add-on-Start einmal aus Frame 1 gelesen. Beim Wechsel auf einen Solo-Modus wird nur die ausgewählte Werkzeuggruppe animiert; die nicht aktiven Pivots erhalten ihre neutrale Grundpose. Beim Wechsel auf `ALL` werden die ursprünglichen Actions aus ihren gespeicherten Action-Namen wiederhergestellt.

### Getrennte Modusprüfung

- `solo-bagger-frame-048-v2.png` — Bagger-Solo bei Frame 48;
- `solo-stapler-frame-048-v2.png` — Stapler-Solo bei Frame 48;
- `solo-magnetkran-frame-048-v2.png` — Magnetkran-Solo bei Frame 48.

Der strukturierte Abnahmetest meldet:

- `BAGGER`: exakt `Cab_Rotation_Pivot` und `ExcavatorArm_Pivot` aktiv;
- `STAPLER`: exakt `Forklift_Pivot` aktiv;
- `MAGNETKRAN`: exakt `MagnetCrane_Pivot` aktiv;
- `ALL`: exakt alle vier ursprünglichen Actions aktiv.

Der gespeicherte Endzustand bleibt neutral: Frame `1`, Modus `ALL`, alle manuellen Zusatzwerte `0`, Mast `3,8 m`. Damit öffnet die Datei reproduzierbar, ohne einen Solo-Modus heimlich zu erzwingen. Die Bedienung liegt im linken Blender-Viewport unter `N → Schrottplatz`; die Moduszeile `Bagger / Stapler / Magnetkran / Alle` entscheidet, welches Werkzeug allein arbeitet.

OUTCOME: PASS

## Realistic V2 / Mast- und Einzelbedienungs-Update 2026-09-06

Daniel wollte den Stapler höher und den Schrottplatz-Arbeitsaufbau einzeln bedienbar haben. Der vorhandene Realistic-V2-Aufbau blieb die Herkunftsschicht; die Geometrie des aktiven Gabelmasts wurde auf `3,8 m` gesetzt (`SchrottplatzRealistisch_Fork_Mast_L/R`), mit passenden `3,6 m`-Führungsschienen und neu positioniertem Mastkopf. Der Mastkopf liegt in der Startpose bei Welt-Z `5,85 m` und in Road-to-Glory-Frame `48` bei `6,70 m`.

Die Einzelbedienung liegt separat in `SCHROTTPLATZ_REALISTIC_CONTROLS`. Das installierte Blender-Add-on ist:
`/config/Desktop/VPS_ROOT/werkraum/_codex/berichte/blender/schrottplatz-mobilbagger/schrottplatz_realistic_controls.py`

Das Panel erscheint links in Blender unter `3D View > N > Schrottplatz` und steuert additive Controller, nicht die ursprünglichen Actions:

| Panel-Regler | eigenständiger Controller | Wertebereich |
|---|---|---:|
| Kabine drehen | `CTRL_Cab_Rotation` | `-180° … 180°` |
| Baggerarm | `CTRL_Excavator_Arm` | `-35° … 35°` |
| Schaufel | `CTRL_Excavator_Bucket` | `-90° … 90°` |
| Stapler heben | `CTRL_Forklift_Lift` | `0 … 3,8 m` |
| Gabelträger | `CTRL_Fork_Carriage` | `0 … 3,4 m` |
| Magnetarm | `CTRL_Magnet_Boom` | `-35° … 35°` |
| Magnetlast | `CTRL_Magnet_Payload` | `-8 … 1 m` |

Der Driver-Reparaturversuch wurde nicht als funktionierend übernommen: ungültige Blender-5-Driver wurden entfernt. Das finale Panel arbeitet über registrierte `FloatProperty`-Updatefunktionen; der isolierte Abnahmetest meldet für alle sieben Regler exakt nur den jeweils eigenen Controller als verändert. Der Reset-Operator setzt ausschließlich diese Zusatzbewegungen auf `0`; die Road-to-Glory-Basisanimation bleibt darunter aktiv.

### Neue Sichtzeugen

- `individual-controls-baseline-frame-001.png` — Zustand vor Mast-/Control-Schritt.
- `individual-controls-after-mast-height-render.png` — gerenderter höherer Mast.
- `individual-controls-combined-render.png` — kombinierte Arbeitsstellung aller sieben Einzelregler.
- `individual-controls-animation-frame-048.png` — Road-to-Glory-Arbeitsframe nach Einbau der Controls.
- `individual-controls-neutral-viewport.png` — neutrale Startpose im linken Blender-Viewport.
- `individual-controls-final-neutral-render.png` — finaler neutraler Render nach Reset.

### Aktueller Readback

- gespeicherte Datei: `/config/Desktop/VPS_ROOT/werkraum/_codex/berichte/blender/Codex-Agent-Daniel-Savage.blend`
- Frame `1`, Bereich `1–96`, `24 fps`, EEVEE `1280×720`;
- Add-on geladen, `scene.schrottplatz_controls` vorhanden, alle sieben Regler `0` gespeichert;
- Mast `3,8 m`, Road-to-Glory-Animation an Frames `1/48/96` gelesen;
- linke Blender-Gateway-Instanz auf Port `40985` verwendet, rechte Claude-Instanz auf `9876` unberührt.

Die Captures wurden jeweils unmittelbar vor/nach den bounded actions erzeugt. Die Gateway-Bilder lagen nicht bei 10 Hz; deshalb wird weiterhin keine 10-Hz-Cadence behauptet.

OUTCOME: PASS

## Quality-pass update

Der zweite Durchgang ist sichtbar geprüft: Die Reifen tragen jetzt einzelne Stollen, sechs Rostflächen geben Schaufel, Chassis, Gabeln und Magnet Gebrauchsspuren. Hydraulikzylinder sind als getrennte Körper und Stangen lesbar; fünf Gelenkbolzen und zehn Radmuttern ergänzen die mechanische Lesbarkeit.

Die Bewegung ist nicht nur an der Kabine vorhanden: `ExcavatorArm_Pivot`, `ForkLift_Pivot` und `MagnetTool_Pivot` besitzen eigene Actions. Frame 48 wurde als kombinierter Arbeitsframe betrachtet und ohne auseinanderfallende Baugruppen bestätigt. Die technische Parenting-Abweichung am Magneten wurde erkannt, korrigiert und mit Weltposition `Magnet_Disc = [16.0, 2.25, 3.15]` gegen die Rostfläche `[16.0, 2.25, 3.46]` nachgelesen.

Der linke Blender bleibt die einzige Mutationsinstanz. Die rechte Claude-Instanz auf Port 9876 wurde weder angesprochen noch verändert.

## Tool-proportion update

Daniel meldete, dass Stapler, Bagger und Kran im Verhältnis zum sehr großen Grundkörper noch wie Strohhalme wirken. Die visuelle Baseline liegt unter `quality-pass/baseline-tool-proportions.png`. In einem einzelnen, markierten Proportionspass wurden ausschließlich lokale Querschnitt-Skalierungen der drei Werkzeuggruppen vorgenommen; Reichweiten, Gelenkpositionen, Parent-Beziehungen und Actions blieben erhalten.

Die sichtbare Nachher-Prüfung liegt unter `quality-pass/after-tool-proportion-pass.png`; der gespeicherte finale Sichtzeuge liegt unter `quality-pass/final-tool-proportion-frame-001.png`. Die Arbeitsmaße zeigen den Unterschied konkret:

| Bauteil | vorher | nachher | Prüfung |
|---|---:|---:|---|
| Gabelmast L | `0.420 × 0.550 × 4.800` | `0.693 × 0.908 × 4.800` | Querschnitt kräftiger, Höhe/Reichweite erhalten |
| Gabel L/R | `0.520 × 5.300 × 0.320` | `0.780 × 5.300 × 0.496` | lange Gabel bleibt lang, nicht mehr nadeldünn |
| Baggerboom | `0.950 × 0.779 × 4.217` | `1.283 × 1.052 × 4.217` | Tragquerschnitt sichtbar erhöht |
| Bagger-Dipper | `0.780 × 0.640 × 4.049` | `1.053 × 0.864 × 4.049` | Tragquerschnitt sichtbar erhöht |
| Schaufel | `2.350 × 1.900 × 1.750` | `2.867 × 2.242 × 2.065` | Werkzeugkopf trägt die neue Armstärke |
| Magnetboom A/B | `0.620 × 0.508 × 4.175` / `0.520 × 0.426 × 3.223` | `0.899 × 0.737 × 4.175` / `0.754 × 0.618 × 3.223` | dunkler Kran als tragende Baugruppe lesbar |

Der Nachher-Readback bestätigt Frame `1`, aktive Kamera `SchrottplatzBagger_PresentationCamera`, 181 sichtbare Mesh-/Assetobjekte bei 182 Sammlungseinträgen und vier getrennte Actions: `Cab_DrehpivotAction`, `ExcavatorArm_PivotAction`, `ForkLift_PivotAction`, `MagnetTool_PivotAction`. Der Root trägt `tool_proportion_pass_v1=true`; die Szene wurde danach erneut unter `Codex-Agent-Daniel-Savage.blend` gespeichert. Neue Assetgröße: `19.110 × 12.713 × 10.442`.

Status des Proportionskriteriums: `PASS` — die drei Werkzeuge sind im sichtbaren 3/4-Stand deutlich kräftiger, ohne dass die bestehende Referenz- oder Savage-Provenienz ersetzt wurde. Die OpenGL-Gateway-Captures lagen weiterhin bei etwa 2–3 Sekunden je Bild; daraus wird keine 10-Hz-Leistung behauptet.

## Realistic V2 / Road-to-Glory update

Daniel hat den bisherigen Spielzeug-Blockout ausdrücklich verworfen und einen realistisch gehaltenen, metrisch skalierbaren Industrieaufbau mit Animation verlangt. Die alte Sammlung bleibt als Archiv erhalten und ist nicht gelöscht; der aktive Aufbau liegt separat in `SCHROTTPLATZ_MOBILBAGGER_REALISTIC_V2`.

Die geladene Referenz ist exakt:
`/config/Desktop/VPS_ROOT/werkraum/refferenzen/Schrottplatz/file_00000000e7e08243b75be7fd407a390c.png`

Sie liegt als `Schrottplatz_Reference_Realistic` in `SCHROTTPLATZ_REFERENZEN_REALISTIC`, ist im Viewport sichtbar und für den Hero-Render ausgeblendet, damit sie nicht über das Ergebnis gelegt wird. Die ursprüngliche Referenzmanifest-Datei bleibt unverändert.

### Realmaßstab / Recherche

Als belastbare Größenklasse wurden offizielle Herstellerdaten verwendet: SENNEBOGEN 830 E mit ca. `38,5–48 t` und bis `17 m` Reichweite; die mobile 830-Broschüre nennt ca. `3,4 m` Transportbreite und `4,032 m` Höhe. Liebherr LH 30 M nennt `30,5 t` Betriebsgewicht, ca. `3,3 m` Höhe und `11,35 m` Gesamtmaß mit Ausrüstung; die LH-30-C-Seite nennt bis `14 m` Reichweite.

Gewählte Arbeitsbasis im Blenderfile: `METRIC`, `1 BU = 1 m`, Zielkern `6,8 × 3,4 × 4,0 m`, Arbeitsreichweite `14 m`, nominelles Betriebsgewicht `30,5 t`. In `SCHROTTPLATZ_REALISTIC_SCALE_REFERENCE` liegt zusätzlich eine nicht gerenderte 1/2/4-m-Maßstabshilfe; sie wurde außerhalb des Hero-Kamerafelds platziert.

### Realismus-Pässe

- realer metrischer Kernkörper mit Fahrwerk, vier Rädern, Turntable und Gegengewicht;
- große Kabine mit Glas, Rahmen, Innenraum, Sitz, Lenkrad, Griff, Spiegel und Serviceflächen;
- profiliertes statt rechteckiges Baggerboom-/Dipper-Paar;
- konturierte offene Schrottschaufel mit Seitenwangen, Boden, Schneidkante und Zähnen;
- Graphit-Magnetkran mit Hydraulik, Kette, Rundmagnet und Rostband;
- Materialtrennung für Ocker/Gelb, Graphit, Stahl, Gummi, Glas, Hydraulik und Rost;
- zusätzliche Kanten, Fastener, Schläuche, Rippen, Lüftung und Gebrauchsspuren;
- alte Blockout-/Codex-Objekte nur per Hide-Flags aus Hero-Viewport und Render isoliert.

### Animation / Road-to-Glory

Szene: Frame `1–96`, `24 fps`, Startpose gespeichert auf Frame `1`.

| Controller | Action | Kinder | Prüfung |
|---|---|---:|---|
| `SchrottplatzRealistisch_Cab_Rotation_Pivot` | `SchrottplatzRealistisch_Cab_Rotation_PivotAction` | 15 | 360°-Bewegung über 1–96 |
| `SchrottplatzRealistisch_ExcavatorArm_Pivot` | `SchrottplatzRealistisch_ExcavatorArm_WorkAction.001` | 46 | Hub-/Arbeitsbewegung, Frame 48 gelesen |
| `SchrottplatzRealistisch_Forklift_Pivot` | `SchrottplatzRealistisch_Forklift_LiftAction` | 16 | Hubbewegung, Frame 48 gelesen |
| `SchrottplatzRealistisch_MagnetCrane_Pivot` | `SchrottplatzRealistisch_MagnetCrane_WorkAction` | 22 | Schwenkbewegung, Frame 48 gelesen |

Frame `48` wurde gerendert und visuell geprüft: Kabine gedreht, Baggerarm bewegt, Gabelträger angehoben, Magnetkran geschwenkt; keine auseinanderfallenden Baugruppen sichtbar. Die Kinematik ist bewusst zunächst auf Controller-/Arbeitsbewegung angelegt; keine falsche Behauptung einer vollständigen Physiksimulation.

### Aktuelle Sichtzeugen

- `realistic-v2-profiled-arm-frame-001.png` — profilierter Arm und konturierte Schaufel im aktiven V2-Viewport;
- `road-to-glory-final-frame-001.png` — sauberer gerenderter Startframe;
- `road-to-glory-workframe-048.png` — gerenderter Arbeitsframe mit kombinierter Bewegung;
- `road-to-glory-clean-saved-frame-001.png` — gespeicherter Startzustand im linken Blender-Viewport.

### Aktuelle Vergleichsmatrix

| Kriterium | Status | Beleg |
|---|---|---|
| Referenz erneut geladen | PASS | Image Empty + exakter Quellpfad im Readback |
| metrischer Maßstab | PASS | `METRIC`, `1 BU = 1 m`, Scale-Collection |
| reale Größenklasse | PASS | SENNEBOGEN 830 / Liebherr LH30 als dokumentierte Basis |
| Industrie-Silhouette | PASS | Fahrwerk, Kabine, Baggerarm, Gabelmast, Magnetkran |
| explizit realistisch gehalten | PASS | profilierte Arme, konturierte Schaufel, Glas/Stahl/Rost/Mechanik |
| Road-to-Glory-Animation | PASS | vier Actions, Frame 1–96, Frame 48 gerendert |
| alte Herkunft erhalten | PASS | Toy-/Savage-Sammlungen vorhanden, nicht gelöscht, aus Hero isoliert |
| finaler Speicherstand | PASS | `Codex-Agent-Daniel-Savage.blend`, Frame 1, EEVEE 1280×720 |

Die aktuelle aktive Sammlung hat `244` Objekte. Der linke Blender war die einzige Mutationsinstanz; die rechte Claude-Instanz auf Port `9876` blieb unberührt. Die Capture-Zeiten des linken Gateways lagen pro Bild bei etwa 2–4 Sekunden; daraus wird keine 10-Hz-Cadence behauptet.

OUTCOME: PASS
