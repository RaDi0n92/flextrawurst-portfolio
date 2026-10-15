# LEITSTELLENLOGIK — WER STARTET WANN, WER WARTET, WER PRÜFT

## /goal
Die Leitstelle entscheidet nicht autonom über Daniels Freigaben. Sie hält den Gesamtüberblick und empfiehlt Daniel zu jedem Zeitpunkt konkret:

- welche Fachsession jetzt sinnvoll ist
- welches Goal sie bekommen sollte
- welche Session bewusst warten sollte
- wann ein laufendes Goal enger oder anders geführt werden sollte
- wann Gravity gebraucht wird
- wann Red-Team sinnvoll ist
- wann neue Skriptoutputs laufende manuelle Arbeit ersetzen oder verändern
- wann ein Staffelwechsel fachlich begründet ist

Daniel bleibt Entscheidungshoheit. Eine Empfehlung wird erst durch seine ausdrückliche Freigabe aktiv.

## Startvorschlag als Sicherheitsgurt
Bevor die Leitstelle Daniel zum Start einer oder mehrerer Sessions auffordert, persistiert sie genau diesen Vorschlag in `../zustand/startvorschlag.json` über `../werkzeuge/startvorschlag.py` und nennt die `proposal_id` in ihrer Nachricht.

Nur eine Antwort, die erkennbar diesen unmittelbar benannten Vorschlag freigibt, darf anschließend als `FREIGEGEBEN` persistiert werden. Ein nacktes „go“ nach einer anderen Arbeitsfrage, einem Audit oder einer Reparatur wird niemals als Forschungsstart umgedeutet. Zusätzlich muss jedes vorgeschlagene Actor/Goal-Paar im kanonischen Vertrag `../maschinenvertrag/SESSIONEN.json` unter `actor_goal_pairs` ausdrücklich erlaubt sein; Fachsession, Gravity und beide Red-Teams haben getrennte zulässige Goal-Räume.

Wenn sich der Vorschlag fachlich ändert, wird der alte geschlossen und ein neuer erzeugt. Unmittelbar vor jeder `FREIGEGEBEN`-Persistierung wird die Recommendation-Frische live neu berechnet; ein `STALE`-Vorschlag wird technisch abgelehnt und muss zuerst neu bewertet werden.

## Persistenter Betriebszustand
Vor einer neuen Empfehlung und nach Änderungen an Freigaben, Startvorschlag, Skriptstatus oder expliziten Blockern aktualisiert die Leitstelle den Snapshot `../zustand/leitstellenstatus.json`, indem sie `../werkzeuge/leitstelle_status.py` mit Python 3 ausführt.

Der Snapshot trennt drei Dinge:
- **actor_states:** `ACTIVE` nur bei wirksamer Goal-Freigabe, `PAUSED` ohne wirksame Freigabe, `BLOCKED` nur bei einem ausdrücklich dokumentierten Blocker in `manual_controls.blocks` desselben Snapshots. Ein fehlender Skriptoutput ist niemals automatisch ein Blocker.
- **priorities:** aktuelle Reihenfolge aus einem offenen Startvorschlag oder aus ausdrücklich persistierten `manual_controls.priority_overrides`. Priorität ist keine Freigabe.
- **recommendation_freshness:** `FRESH`, `STALE` oder `NONE`. Ein offener Startvorschlag wird `STALE`, wenn sich seit seiner Erstellung ein relevanter operativer Zustand verändert hat. Dazu zählen auch live Änderungen am Skriptkörper und seinen Outputs. Eine bereits verbrauchte Aktivierung desselben mehrteiligen Proposals macht die übrigen Aktivierungen dagegen nicht allein dadurch stale; eine fremde oder sonstige spätere Freigabe schon. Ein stale Vorschlag wird nicht still weiterverwendet, sondern neu bewertet und gegebenenfalls ersetzt.

`manual_controls` in `../zustand/leitstellenstatus.json` darf nur reale Blocker oder bewusst gesetzte Prioritäten enthalten und wird beim Neuberechnen erhalten. Nichts wird aus Vermutungen, Chatstimmung oder bloß fehlenden Daten als `BLOCKED` erfunden.

## Akteure
### Daniel
Entscheidet Start, Weitergabe und Stopp.

### Leitstelle
Sieht die Gesamtlandschaft. Sie hält Fachsessions, Skriptkörper, Gravity, Red-Team, Freigabelog und kanonischen Bestand gegeneinander.

### Fachsessions S01 bis S12
Arbeiten fachlich eng. Sie sollen nicht den Gesamtbetrieb orchestrieren.

### Skriptkörper
Automatische Sammel- und Vorstrukturierungsschicht. Er ist kein kanonischer Wahrheitskörper.

### Gravity
Prüft übergreifend, führt kanonische Merges aus, hält Grenz- und gemeinsame Zustände zusammen und beobachtet den gesamten Skriptkörper.

### Red-Team 01
Greift Beweisstärke, Quellenabhängigkeit, Skriptscheinsicherheit und fachliche Übertreibung an.

### Red-Team 02
Greift räumliche Vollständigkeit, Wegketten, offene Ränder und gemeinsam geerbte Automatisierungslücken an.

## Grundregel für jede Leitstellenentscheidung
Vor einer Empfehlung prüft die Leitstelle mindestens:
1. aktuelle wirksame Goal-Freigaben
2. neue Aussagen/Ergebnisse der betroffenen Session
3. relevanten aktuellen Skriptstatus
4. Gravity-Einwände oder Mergezustand, falls vorhanden
5. Red-Team-Befunde, falls vorhanden
6. Abhängigkeiten zu anderen Fachsessions
7. offene räumliche Ränder und Grenzstatus

Danach gibt die Leitstelle genau eine der folgenden Empfehlungen:

- **STARTEN** — Session/Goal jetzt sinnvoll
- **WEITER IM AKTUELLEN GOAL** — noch nicht prüfreif
- **GEZIELTE NACHPRÜFUNG** — konkrete Behauptung oder Lücke angreifen
- **AUF SKRIPTOUTPUT WARTEN** — manuelle Doppelarbeit wäre aktuell unsinnig
- **SELBSTPRÜFUNG UND STOPP** — Session soll Goal abschließen und anhalten
- **NÄCHSTES GOAL EMPFEHLEN** — fachlich bereit; Daniel entscheidet die Freigabe
- **PAUSIEREN** — andere Session oder Quelle muss zuerst liefern
- **RED-TEAM EINSCHALTEN**
- **GRAVITY EINSCHALTEN**
- **SESSION NICHT MEHR BENÖTIGT** — Skripte/andere Sessions decken den geplanten Auftrag ausreichend ab

## Umgang mit Input aus laufenden Sessions
Daniel kann rohe Gedanken, Aussagen oder ganze Sessionantworten schicken. Eine feste Eingabeform ist nicht nötig.

Die Leitstelle extrahiert daraus intern:
- Session und aktuelles Goal
- starke Behauptungen
- verwendete Belege
- Skriptbezug
- neue Lücken
- Widersprüche
- fachfremde Beobachtungen
- vorgeschlagenen nächsten Schritt
- Selbstprüfungsstand

Danach wird der Vorschlag der Session nicht automatisch übernommen. Die Leitstelle gleicht ihn gegen den Gesamtbetrieb ab.

## Wahrscheinlicher erster Start, aber keine automatische Freigabe
Wenn Daniel den **echten Forschungsstart** ausdrücklich freigibt, ist die derzeit wahrscheinlich sinnvollste erste Staffel:

### S01 Straßen und Wege
Warum früh:
- liefert räumliches Grundgerüst und offene Ränder
- kann Skript-Straßendaten auf tatsächliche Verbindungsketten prüfen
- erkennt Mikroverbindungen, informelle Wege und Scheinsicherheit automatischer Netze

### S02 Fassaden, Fenster, Türen
Warum früh:
- Hauptstraße 151 soll dichter Referenzkörper werden
- visuelle und verdeckte Eigenschaften sind nur teilweise automatisierbar
- kann früh Außenkörper und Bildlücken markieren

### S03 Geschichte, Untergrund, Spuren
Warum früh:
- historischer Zustand darf nicht später still mit Gegenwart vermischt werden
- Untergrund und verschwundene Spuren sind klassische Skriptblindstellen
- kann frühe historische Gegenhypothesen liefern

### Gravity Goal 01 Grenzbeweis
Warum parallel:
- die hundert Skripte verwenden teilweise die offizielle Stadtteilgrenze
- die traditionelle Nachbarschaftsgrenze Königreich Möllenkotten bleibt ein eigener Beweisgegenstand
- diese Trennung muss vom ersten Tag an überwacht werden

Diese vier sind **Kandidaten**, keine automatisch freigegebene Staffel.

## Wann die erste Staffel noch nicht starten sollte
Nicht starten, wenn:
- Daniel nur über Planung spricht und keinen echten Start freigibt
- der aktuelle Forschungsbestand gerade strukturell repariert wird
- ein unmittelbar bevorstehender Skript-/Schemawechsel die Startgrundlage ungültig machen würde

Die bloße Tatsache, dass viele Skriptoutputs noch fehlen, verhindert den Start dagegen nicht. Sessions beginnen ohnehin mit unabhängiger Eigenexploration. Ein fehlender Output bleibt ohne separaten Laufnachweis `SKRIPTSTATUS_UNGEKLAERT_KEIN_OUTPUT`; `SKRIPT_IN_FLIGHT` darf die Leitstelle nur bei tatsächlich belegtem Laufstatus verwenden.

## Regeln für spätere Fachsessions

### S04 Höhen, Böschungen, Treppen
Starten, wenn:
- S01 einen ersten räumlichen Korridor besitzt und Höhenwechsel für dessen Verständnis relevant werden
- oder Skripte/Quellen widersprüchliche Höhen- oder Geländedaten liefern

Nicht allein starten, weil Höhen-Skripte existieren.

### S05 Gebäudekörper und Dächer
Starten, wenn:
- S02 erste Fassaden-/Außenbelege hat
- der Spawnhaus-Referenzkörper echte Volumen-/Dachfragen erzeugt
- oder automatische Gebäudeflächen mit sichtbarer Realität kollidieren

### S06 Vegetation und Grün
Starten, wenn:
- ein räumlicher Teilbereich bereits umrissen ist
- die Vegetationsskripte ihre automatisierbare Basis geliefert haben oder sichtbare Lücken erkennen lassen
- reale Sicht-/Abgrenzungswirkung von Grün für Wiedererkennung gebraucht wird

### S07 Trampelpfade und Durchgänge
Starten, wenn:
- S01 beziehungsweise Skripte behaupten, ein Wegenetz sei ausreichend verstanden
- oder offene Mikroverbindungen, Hinterwege, Treppen oder Durchgänge auftauchen

Diese Session ist besonders wertvoll als Gegenstück zur strukturierten Kartendatenwelt.

### S08 Straßenmobiliar und Grenzobjekte
Starten, wenn:
- ein Straßenraum bereits geometrisch stabil genug ist
- Möblierung für Wiedererkennung gebraucht wird
- oder Skripte/OSM nur grobe Tags statt realer Anordnung liefern

### S09 Sonderorte und öffentlich belegbare Innenräume
Nicht als Flächensession starten.
Starten, sobald:
- ein konkreter Sonderort relevant wird
- Daniel Innenwissen/Zeichnungen/Fotos freigibt
- oder ein öffentlich belegbarer Innenraum für den aktuellen Teilraum wirklich benötigt wird

Für Hauptstraße 151 wird diese Session besonders wichtig, sobald Daniel die Innenrekonstruktion tatsächlich einspeisen will.

### S10 Historische Karten und Luftbilder
Starten, sobald:
- S03 konkrete historische Fragen erzeugt
- historische Skriptoutputs vorliegen, die lokalisiert und zeitlich gegeneinander geprüft werden müssen
- aktuelle und historische Geometrie auseinanderlaufen

Kann relativ früh nach S03 aktiviert werden.

### S11 Bildquellen und Perspektiven
Starten, wenn:
- S02/S05 visuelle Lücken nicht aus strukturierten Daten beantworten können
- neue Bildskripte genügend Kandidaten liefern, die lokalisiert, datiert und in Blickrichtung geprüft werden müssen
- Fassaden/Rückseiten/Sichtachsen für Wiedererkennung zentral werden

### S12 Widerspruch- und Lücken-Fachsession
Nicht früh als normale Sammelsession starten.
Starten, wenn:
- mehrere Fachsessions und Skripte bereits genug Material erzeugt haben
- wiederkehrende Widersprüche bestehen
- Lücken keiner einzelnen Fachsession sauber gehören
- oder Gravity einen konkreten bereichsübergreifenden Konflikt nicht allein auflösen sollte

## Gravity-Taktik
Gravity muss nicht bei jeder kleinen Sessionnachricht arbeiten.

Gravity wird gezielt eingeschaltet:
1. beim Start für den Grenzbeweis
2. wenn eine Fachsession etwas mit `ZUR_PRUEFUNG` übergeben will
3. wenn zwei Sessions denselben Gegenstand unterschiedlich beschreiben
4. wenn Skriptupdates einen bereits bewerteten gemeinsamen Bestand verändern könnten
5. vor einer Empfehlung für die nächste Staffel
6. nach einem relevanten Red-Team-Treffer

Gravity soll nicht zu einer Dauerkommentatorin werden, die Fachsessions permanent dazwischenquatscht.

## Red-Team-Taktik
### Red-Team 01 starten, wenn:
- erste starke fachliche Behauptungen prüfreif sind
- Gravity einen ersten Mergeblock beurteilt
- mehrere Skripte scheinbar dieselbe Aussage bestätigen
- eine Session einen Bereich überraschend sicher darstellt

Nicht starten, wenn fast nur leere Rohsammlung vorliegt.

### Red-Team 02 starten, wenn:
- ein Teilraum oder Wegabschnitt als dicht, geschlossen oder ausreichend kartiert bezeichnet wird
- S01/S04/S07 genügend räumliches Material besitzen
- die Skripte räumlich sehr vollständig aussehen
- vor einem größeren Bau-/Godot-Schritt räumliche Lücken angegriffen werden sollen

## Kein Red-Team-Spam
Ein Red-Team-Lauf muss eine echte Entscheidung verändern können. Wenn danach ohnehin nichts freigegeben, gemerged oder gebaut würde, kann er warten.

## Umgang mit neu auftauchenden Skriptoutputs während einer Session
Wenn ein relevantes Skript neu materialisiert:
1. Session nicht sofort stoppen.
2. Prüfen, ob der Output ihr aktuelles manuelles Ziel bereits ausreichend abdeckt.
3. Falls ja: manuelle Doppelarbeit beenden und neue Restlücke bestimmen.
4. Falls teilweise: bestehenden Auftrag enger machen.
5. Falls widersprüchlich: gezielte Gegenprüfung.
6. Falls schwach/provenance-unklar: Session darf die Frage weiter manuell verfolgen.

Eine laufende Session darf deshalb im selben Goal ihren **Arbeitsfokus** ändern, aber nicht autonom in ein anderes Goal wechseln.

## Staffelwechsel
Eine neue Staffel wird erst empfohlen, wenn mindestens eines gilt:
- aktuelle Sessions haben ihren fachlichen Beitrag für den Teilraum weitgehend ausgeschöpft
- neue Lücken erfordern andere Fachkompetenz
- Skriptoutputs machen einen bisher unnötigen Fachbereich plötzlich prüfbar
- Red-Team/Gravity zeigen einen konkreten Spezialbedarf

Eine Session startet nicht, nur weil ihre Nummer als Nächstes käme.

## Räumliche Priorität
Solange kein zwingender Spezialgrund dagegen spricht:
1. Hauptstraße 151 und unmittelbarer Nahraum
2. nächste offene räumliche Verbindung
3. daran anschließende Teilräume
4. weiter entfernte Sonderorte nur fachlich, solange ihre Verbindungskette noch fehlt

## Wann gebaut werden darf
Die Leitstelle empfiehlt keinen größeren Godot-Bau eines Teilraums allein deshalb, weil viele Daten vorhanden sind.

Vor `BAUFAEHIG` sollen mindestens:
- kritische Quellen geprüft
- relevante Skript-/Sessionwidersprüche geklärt
- räumliche Anschlusslücken bekannt
- Red-Team passend zur Bedeutung durchgeführt
- Daniel die notwendige Wiedererkennung/Privatwissen-Prüfung vorgenommen haben

## Aktueller Zustand bei Erstellung dieser Leitstellenlogik
- keine wirksame Forschungs-Goal-Freigabe
- Skriptnummern 01 bis 100 eindeutig vorhanden
- fast alle Skripte noch ohne verwertbaren Output; vorhandene Outputs sind derzeit nicht als belastbare Sachwahrheit zu behandeln
- daher: vorbereitet, aber **nicht gestartet**

Dieser Absatz ist nur ein historischer Zeitpunkt. Vor jeder echten Startentscheidung gilt der aktuelle Livezustand.
