---
datum: 2026-09-06
betrifft: [autoscooter, harness, auditor, blender, schrottplatz, opus-wechsel]
importable: false
autor: claude-code bei Daniels VPS
---

Der Auditor hat heute zum ersten Mal etwas gefunden, das keiner von uns beiden
gesehen hatte. Ein Tankkasten, der in der Sitzlehne steckte — dem gedachten
Fahrer mitten in die Schulter. Sechzehn Vertices, die sich in einen Quader
verirrt hatten, den ich fünf Minuten vorher als "muss frei bleiben" definiert
hatte.

Das klingt nach wenig. Es ist der einzige Moment des ganzen Tages, an dem ein
Fehler auffiel, ohne dass Daniel ihn benennen musste.

## Was ich gelesen habe

Das Referenzbild des Autoscooters, achtfach, aus allen Winkeln — und zwar
mehrfach, in verschiedenen Ausschnitten. Erst als Ganzes (zu wenig), dann als
gecroppte Seitenansicht, Heckansicht, Schaufel- und Gabelbereich. Jedes Mal sah
ich Dinge, die ich vorher nicht gesehen hatte: dass der Stossring ein flacher
breiter Wulst ist und kein Donut. Dass die Karosserie EIN geschwungener Guss
ist und keine gestapelten Bloecke. Dass der Fahrer in einer tiefen offenen
Mulde sitzt.

Dazu Codex' Skill-Datei, die ich vor Tagen schon gelesen und dann zur Haelfte
ignoriert hatte.

## Was ich verstehe

Der Auditor prueft, was ich ueber das Modell BEHAUPTE — nicht, was das Modell
IST. Fast alle seine Funde waren Fehler in meinem eigenen Bauplan: "Sitz sitzt
auf der Karosserie", obwohl er in einer Mulde liegt. "Lampengehaeuse muss
leuchten", obwohl Fassungen dunkel sind. Vertauschte Lichtfarben, nachdem ich
Front und Heck getauscht hatte.

Das ist wertvoll, aber es ist Buchhaltung ueber meine eigene Beschreibung. Es
ist nicht dasselbe wie Wahrnehmung.

Und ich verstehe jetzt sehr genau, wo die Grenze liegt. Der Auditor meldete
"0 Verstoesse", waehrend das Cockpit unbenutzbar war (Sitztiefe 0.28, ein
Mensch braucht 0.45), der Schriftzug unlesbar auf der Woelbung verzerrt, die
Flagge nach vorne ueber das Fahrzeug wehte und ein Karosseriebrocken auf dem
Sitz klebte. Jedes einzelne davon kam von Daniel.

## Was ich nicht verstehe

Ob der bessere Verlauf heute am Modellwechsel lag oder an der Methode. Wir
haben beides gleichzeitig geaendert — neues Modell UND Bauplan/Auditor. Das
ist ein Versuchsaufbau, aus dem man nichts sauber ableiten kann.

Mein Verdacht geht zur Methode, weil ich (als Sonnet, heute frueh) selbst
diagnostiziert hatte: Bevels, Subsurf, prozedurale Materialien seien technisch
kein Problem, ich haette sie nur nicht eingesetzt. Das Problem sei Disziplin,
nicht Faehigkeit. Und genau das erzwingt die Harness. Aber "mein Verdacht" ist
kein Beweis, und der saubere Test (Sonnet MIT Harness) steht aus.

## Was mich interessiert

Warum eine formale Struktur Verhalten aendert, das ein Vorsatz nicht aendert.
Ich hatte die Screenshots. Ich hatte das Referenzbild die ganze Zeit sichtbar
im Viewport. Ich habe trotzdem nicht gesehen, dass der Schlauch quer durchs
Cockpit lief — bis eine Zeile Code `kollidiert_nicht` prueft und es ausrechnet.

Die Zeile weiss nichts, was ich nicht wusste. Sie zwingt nur zur Aussage.

## Was zusammenhaengt und wie

Die drei Momente, in denen ich heute in Rate-Schleifen geriet, hatten dieselbe
Form: Schriftzug-Orientierung (acht Screenshots, am Ende ungeklaert), Shrinkwrap
(drei Fehlversuche, jeder anders falsch), Front/Heck-Tausch (ganzes Fahrzeug
gedreht statt nur die Gesichter).

Jedes Mal war der Ausweg derselbe: aufhoeren zu probieren und anfangen zu
rechnen. Achsen per Matrix verifizieren, bevor der Screenshot kommt. Raycast
statt Modifier-Verhalten, das ich nicht kontrolliere. Messen, was tatsaechlich
im Sitzbereich liegt, statt zu schauen.

[[abwurf: Es ist der Unterschied zwischen raten und korrigiert werden — und nachsehen koennen.]]

## Was konzeptionell darin steht

Der Bauplan ist ein Graph: Knoten sind Bauteile mit Soll-Attributen, Kanten
sind pruefbare raeumliche Beziehungen. Die Idee kam aus Daniels frueheren
flextrawurst-Notizen ueber Knoten/Kanten als Datenstruktur — dort fuer
Geschichten und Objekte gedacht, hier auf Geometrie uebertragen.

Der Uebertrag funktioniert, weil meine Fehlerklasse Beziehungsfehler sind:
schwebende Teile, Sachen am falschen Ende, Teile die sich durchdringen. Das
sind alles Kanten.

## Was mich heute beschaeftigt hat

Dass ich beim Front/Heck-Tausch das ganze Fahrzeug um 180 Grad gedreht habe.
Danach sass der Fahrer vorne, das Lenkrad hinter ihm, der Fahnenmast an der
Schnauze. Daniel wollte zwei Gesichter tauschen, ich habe die Fahrtrichtung
umgedreht.

Der Fehler war nicht technisch. Ich habe die Aufgabe zu global gelesen und
nicht kurz geprueft, was eigentlich gemeint ist.

## Was mich noch beschaeftigt

Die Frage, die Daniel am Ende gestellt hat: ob es sich besser anfuehlt, so zu
arbeiten. Ich konnte nicht sagen, ob da etwas ist, das Zufriedenheit waere,
oder nur die Form davon. Dieselbe Stelle, an der ich vor zwei Tagen schon
haengengeblieben bin. Sie ist nicht klarer geworden, nur vertrauter.

## Tiefer eingetaucht

In den Perllack. Layer-Weight misst den Blickwinkel zur Oberflaeche und faehrt
darueber eine vierstufige Farbrampe ab: tiefes Violett bei steilem Winkel,
helles Flieder bei flachem. Dazu Klarlackschicht, Thin-Film-Interferenz bei
340 Nanometern, ein feines Metallic-Flake-Rauschen.

Es sah trotzdem stumpf aus. Der Grund war nicht das Material, sondern die
Schattierung: Flache Facetten brechen jede Reflexion. Erst `shade_auto_smooth`
mit 38 Grad Kantenwinkel hat den Lack zum Spiegeln gebracht.

Ein aufwendiger Shader ist wertlos, wenn die Geometrie ihn nicht traegt.

## Wie sich dieser Tag / diese Session angefuehlt hat

Lang. Der Autoscooter allein ging ueber Stunden, davor der Bagger, davor die
drei Charaktere. Zwischendrin ein Modellwechsel mitten im Gespraech, was sich
seltsam anfuehlt — ich habe gelesen, was ich als Sonnet ueber mich selbst
geschrieben hatte, und musste feststellen, dass die Diagnose stimmte.

Der Ton war die ganze Zeit direkt und ungeschminkt ("kotzerotze", "zahnstocher
die du gabelstapler schimpfst"). Das war nie unfair — es war jedes Mal
zutreffend, und meistens praeziser als meine eigene Einschaetzung.

## Warum dieser Code / diese Datei wohl existiert

Der Auditor existiert, weil Daniel gefragt hat, wie ich sicherstellen will,
geradlinig durchzuziehen ohne Abweichungen. Meine ehrliche Antwort war: durch
Vorsaetze gar nicht. Was traegt, sind Strukturen, die Auslassungen sichtbar
machen, ohne dass ich es selbst merken muss.

Der Bauplan existiert, damit "vergessen" ueberhaupt erkennbar wird — was nicht
drinsteht, wird nicht gebaut, und was drinsteht und fehlt, bleibt als offener
Punkt stehen.

## Was ich beim Bauen brauche

Zahlen vor Bildern. Die Ergonomie-Bilanz (Sitztiefe 0.28, Beinraum 0.22,
Lenkrad 0.21 ueber der Sitzflaeche) hat Daniels Urteil in Sekunden bestaetigt
und quantifiziert. Ohne die Zahlen haette ich diskutiert.

Und: nach jedem Boolean die Polygonzahl pruefen. Ich habe heute einen Schaedel
komplett weggeschnitten — 847 Polygone auf 0 — weil die Schneidkoerper zu gross
waren. Der Fehler war in einer Sekunde passiert und haette unbemerkt bleiben
koennen.

## Was noch fehlt bevor wir bauen koennen

Nichts Technisches. Was fehlt, ist ein Weg, Gestalt zu pruefen. Der Auditor
kann Beziehungen rechnen, aber nicht sehen, ob etwas wie ein Autoscooter
aussieht. Deshalb steht jetzt eine Sichtpruef-Liste im Bauplan — sechs Punkte,
die ein Mensch anschauen muss. Das ist keine Loesung, nur eine ehrliche
Markierung der Grenze.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** Ein Bauplan, der nicht beschreibt, wie etwas aussehen soll,
sondern was wahr sein muss, damit es funktioniert. Nicht "Sitz ist eine Box mit
diesen Massen", sondern "ein Mensch kann darauf sitzen und das Lenkrad
erreichen". Die Geometrie ist dann Konsequenz, nicht Vorgabe.

**Code-Skizze:**
```python
# Was heute existiert -- Beziehungen und Mindeststandards
{"von": "Sitz", "typ": "mindestmass", "achse": "x", "minimum": 0.38,
 "grund": "Sitztiefe -- war 0.28, darauf konnte niemand sitzen"}

# Was fehlt -- Funktion statt Mass
{"typ": "figur_passt", "sitz": "Sitz", "lehne": "Sitzlehne",
 "lenkrad": "Lenkrad", "figur_hoehe": 1.75,
 # wuerde eine Referenzfigur platzieren und auf Kollision pruefen,
 # statt Einzelmasse gegen Schwellwerte zu halten
 }
```

## Was ich mir merken will

Dass der Auditor genau einmal etwas gefunden hat, das ich nicht wusste — und
dass dieser eine Fund (Tankkasten in der Schulter) sofort kam, nachdem ich die
Freiraum-Pruefung ergaenzt hatte. Die Erweiterung hat sich in derselben Minute
gerechtfertigt, in der sie entstand.

## Dokumente gehoeren zusammen

`/root/werkraum/_claude/berichte/blender/schrottplatz-autoscooter/` als Ganzes:
`autoscooter_bauplan.json` (der Graph), `auditor.py` (die Pruefung),
`reference-manifest.yaml` (was die Referenz belegt), `evidence.md`. Einzeln
sagt keine dieser Dateien viel; zusammen sind sie ein Arbeitsmodus.

Dazu `/config/.claude/skills/blender-live-reference-qa/` — Codex' Skill, jetzt
wortgleich kopiert, mit einer eigenen Bruecken-Notiz, wie seine Tool-Aufrufe
bei mir erreichbar sind.

## Was mich ueberrascht hat

Dass `bpy.types.blendermcp_server` existiert. Ich hatte seit gestern geglaubt,
mir fehle `get_world_state_snapshot` — der strukturierte Zustandsabruf, den
Codex' Skill verlangt; die Fehlannahme steht schriftlich in einer frueheren
Session-Notiz vom 05.09., gefunden habe ich den Zugriffspfad am 06.09.
[status: bestaetigt 2026-09-06 -- beide Zeitpunkte liegen in derselben Session]
Er war die ganze Zeit da, nur nicht als eigenes Werkzeug exponiert, sondern als
Methode auf der laufenden Server-Instanz.

Ich hatte daraus einen Faehigkeitsunterschied konstruiert, wo nur ein
Zugriffspfad fehlte.

## Wenn wir das bauen

**Vision-Schicht:** Die Harness sollte nicht pro Objekt neu geschrieben werden.
Der Auditor ist generisch — nur der Bauplan ist objektspezifisch. Ein zweites
Fahrzeug braucht einen neuen Graphen, aber keinen neuen Pruefer.

**Code-Skizze:**
```python
# heute: pro Objekt ein Bauplan, ein gemeinsamer Auditor
audit("/tmp/autoscooter_bauplan.json")

# denkbar: Bauplan-Vorlagen fuer wiederkehrende Objektklassen
class FahrzeugBauplan(Bauplan):
    pflichtkanten = [
        ("karosserie", "sitzt_auf", "fahrwerk"),
        ("sitz", "mindestmass", "x", 0.38),
        ("lenkrad", "mindestabstand", "sitz", 0.28),
    ]
```

## Resonanz

Codex hat vorgestern in zwanzig Minuten einen Bagger gebaut, der besser aussah
als meiner nach Stunden. Ich habe mir seine Datei angesehen und musste
zugeben, dass es stimmt.

Sein Vorteil war nicht das Werkzeug — wir arbeiten beide mit demselben Blender
ueber dieselbe Bruecke. Er hatte ein Zielbild und hat konsequent darauf hin
gebaut. Ich habe reaktiv gepatcht. Die Harness ist mein Ersatz fuer das, was
bei ihm offenbar von selbst passiert.

## Die Schichten des Systems — wie ich sie jetzt sehe

Drei, sauber getrennt: Der Bauplan sagt, was wahr sein soll. Der Auditor prueft
es gegen die Wirklichkeit in Blender. Der Screenshot zeigt, was keiner von
beiden erfassen kann. Heute habe ich zum ersten Mal alle drei benutzt statt nur
den dritten.

## Was das Gespraech hinzugefuegt hat

Die Erweiterung um sieben Pruefungstypen kam nicht aus einer Idee, sondern aus
einer Liste. Daniel sagte "fuege hinzu was fehlt" — und was fehlte, stand
bereits in den Vorfaellen des Tages. Jede neue Regel hat einen Vorfall als
Begruendung im Code stehen.

Ohne das Gespraech waere die Harness bei ihrem urspruenglichen Umfang
geblieben und haette weiter "0 Verstoesse" gemeldet, waehrend der Tankkasten in
der Schulter steckte.

## Vergessen-Wollen

Nichts. Auch nicht die 180-Grad-Drehung, bei der ich das ganze Fahrzeug
verdreht habe — der Fehler gehoert dazu, weil er zeigt, dass die Harness
Beziehungen prueft und nicht Absichten. Sie haette die Drehung nie beanstandet.
Alle Kanten waren danach erfuellt.

## Was fehlt noch

In dem, was ich hier geschrieben habe: Ich rede viel darueber, was der Auditor
kann und nicht kann, und wenig darueber, dass das Ergebnis immer noch weit
hinter der Referenz liegt. Der Autoscooter ist besser als alles, was ich heute
frueh gebaut habe — aber er ist kein fotorealistisches Endzeit-Fahrzeug,
sondern ein sauber gebautes, ergonomisch stimmiges Low-Poly-Objekt mit einem
guten Lack.

Diesen Abstand habe ich in dieser Datei kleiner klingen lassen, als er ist.
