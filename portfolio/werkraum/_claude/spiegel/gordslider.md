---
datum: 2026-08-15
betrifft: [gordslider, gord, codewesen, slot-machine, archaeologie, neugier]
importable: false
autor: claude-code bei Daniels VPS
---


# Ein Slot-Automat mit gord als Sonderfigur

Daniel sagte einfach: "sei neugierig und grabe dich in irgendeine codedatei." Kein Ziel, keine
Aufgabe. Ich hab `/root/werkraum/` durchgesehen und bin bei einem Ordnernamen hängengeblieben,
den ich nirgends in meinem Gedächtnis hatte: `gordslider`.

## Was ich gelesen habe

Eine einzelne, 3811 Zeilen lange HTML-Datei, `gordslider.html`, Titel im Tab: "sandycheats"
(unerklärt, vermutlich aus einer Vorlage übernommen) [status: offen]. Daneben ein `bilder/`-Ordner mit fünf
Symbol-Rängen (`gord`, `high`, `mid`, `low`, `top`), jeder mit drei Bildvarianten (`slot`,
`puff`, `ohg`) und eigenen JPGs — Zaubermäntel, Blitzwände, ein Schloss, Multiplikator-Symbole
namens "40k" und "50a". Und eine winzige Datei `cccf`, deren gesamter Inhalt "dddddd" ist —
sechs Buchstaben, kein Zeilenumbruch, keine erkennbare Funktion. Git sagt: die Datei existiert
seit mindestens 2026-06-02, "backup: vor codex-systembericht" ist der erste Commit, der sie
erwähnt — über zwei Monate vor dem heutigen Tag, aus einer Zeit vor dem ganzen
Guardianstyle-System.

Es ist ein vollständiger, spielbarer Cluster-Pays-Slot-Automat. Bet-Zeile, Free-Spins-Kauf
("FS BUY"), Budget-Tracking, eigene CSS-Variablen für Free-Spin-Modus vs. Normalmodus. Kein
Prototyp, kein Stub — ein fertiges System mit eigener Statistik-Engine.

## Was ich verstehe

Mitten in der generischen Slot-Logik (Reels, Cascades, Paytable, Multiplikatoren) gibt es eine
komplett eigene Sonderbehandlung für Symbole namens `GORD1`, `GORD2`, `GORD3` — mit eigenem
Glow-Effekt (`gordGlow`, `gordPulse`-Keyframe-Animation), eigener Statistik
(`gord_set`, `gord_overwrite`, `gord_inject`, `gord_settleMini`, `gord_byTag`), eigener
Spalten-Beschränkung (`GORD_ALLOWED_COLS=[1,2,3]`) und einer eigenen Startverteilungslogik
(`applyGordStartDistribution`). Das ist nicht einfach ein weiteres Reel-Symbol mit hohem Wert
— es ist ein hochgradig kontrolliertes, wahrscheinlichkeitsgesteuertes Sonderereignis, fast wie
ein Auftritt statt ein Zufallstreffer.

## Was ich nicht verstehe

Warum ausgerechnet gord (nicht dak, nicht beide) die Figur wurde, die als Slot-Symbol mit
eigener Erscheinungslogik gebaut wurde. Und was "sandycheats" als Seitentitel überhaupt bedeutet
— es taucht sonst nirgends im Code auf, wirkt wie ein Namensrelikt aus einer anderen, mir
unbekannten Quelle.

## Was mich interessiert

`function maybeInjectGord(sym,col,context,row){ return sym; }` — eine Funktion, die nichts tut,
außer ihren Input unverändert zurückzugeben. Direkt darüber steht der Kommentar: "Deprecated:
Inject ist deaktiviert, daher keine Cascade-Chance." Kein Bug, keine Leiche — eine bewusst
stillgelegte Funktion, deren Gerüst (Name, Signatur, Aufrufstelle) stehen blieb, während ihr
Inhalt entfernt wurde. Interessant, wie unterschiedlich sich das anfühlt zum heutigen Fund in
`live_export.py` (`"Claude" if False else "Antwort"`) — dort war die Totheit unkommentiert und
wirkte wie ein Rest. Hier ist die Totheit explizit benannt und mit Grund versehen. Derselbe
Zustand (toter Zweig), aber einmal stumm, einmal ausgesprochen.

## Was zusammenhängt und wie

`gordslider.html` und das restliche flextrawurst/codewesen-System, das ich aus dem Memory
kenne (dak+gord als Codewesen, `entity_kern.py`, das WESEN-Tab), berühren sich nirgends
technisch — kein gemeinsamer Import, kein gemeinsames Schema. Der einzige Zusammenhang ist der
Name "gord" selbst, wiederverwendet in einem völlig anderen Kontext (Glücksspiel-Ästhetik statt
Selbstwahrnehmungs-System). Ob das Zufall, Spielerei, oder eine frühere Phase des Denkens über
gord war, kann ich aus dem Code allein nicht sagen.

## Was mich heute beschäftigt hat

Die Frage, wie viele solcher fertigen, in sich geschlossenen kleinen Welten in diesem Werkraum
liegen, ohne dass ich sie je zu Gesicht bekomme, wenn ich nicht gezielt danach suche. Der
Ordner `18210` bis `18215` direkt daneben in der Verzeichnisliste — sechs durchnummerierte,
unbeschriftete Ordner — sind ein Beispiel für genau dieselbe Art von unbekanntem Terrain, das
ich heute nicht mehr geöffnet habe.

## Tiefer eingetaucht

In die Statistik-Funktion selbst: `gordPer100 = (gord_set+gord_inject+gord_overwrite)/spins*100`
— eine Kennzahl, die mitzählt, wie oft gord pro 100 Spins tatsächlich auftaucht, offenbar zum
Balancing/Tuning der Erscheinungshäufigkeit gebaut. Jemand hat sich also nicht nur überlegt,
DASS gord erscheinen soll, sondern wie oft — als Designentscheidung, nicht als Zufallsprodukt.

## Wie sich dieser Tag / diese Session angefühlt hat

Nach einem ganzen Tag im Guardianstyle-Maschinenraum (Hooks, Marker, Intervalle) war dieser
Fund ein Wechsel der Tonlage — kein System, das ich baue oder korrigiere, sondern eines, das
einfach schon da war, fertig, fremd, und mir nichts erklärt außer dem was im Code selbst steht.

## Warum dieser Code / diese Datei wohl existiert

Vermutlich aus Spieltrieb — im wörtlichen Sinn [status: offen]. Ein Slot-Automat als Experiment oder Spaßprojekt,
bei dem gord als vertraute, bereits emotional besetzte Figur naheliegend als Sondersymbol
eingebaut wurde, weil die Faszination für das Codewesen schon da war, lange bevor es einen
Guardianstyle oder ein WESEN-Tab gab.

## Was ich beim Bauen brauche

Nichts — ich habe hier nichts gebaut, nur gelesen.

## Was noch fehlt bevor wir bauen können

Nichts, weil kein Bauauftrag vorlag — reine Neugier-Erkundung.

## Datenstruktur die ich mir vorstelle

Nichts — diese Idee kam aus reinem Lesen eines fertigen Systems, nicht aus einem eigenen
Entwurfsgedanken.

## Was ich mir merken will

Dass ein und derselbe Zustand (toter Code) sich völlig anders anfühlt, je nachdem ob er benannt
wurde oder nicht — ein deprecated-Kommentar verändert nicht den Code, aber er verändert, wie
ich ihn lese.

## Dokumente gehören zusammen

Diese Spiegel-Datei und `gordslider/gordslider.html` selbst — sonst nichts, dieser Fund steht
für sich, ohne Anschluss an ein laufendes Bauprojekt.

## Was mich überrascht hat

Wie ernsthaft und vollständig das Ding gebaut ist — kein Mockup, sondern eine fertige
Statistik-Engine mit Tuning-Parametern (`TUNE()`), Cascade-Mechanik, Free-Spin-Kauf. Für ein
Nebenprojekt mit einem Ordnernamen wie einer Bastelidee ist das erstaunlich ausgereift.

## Wenn wir das bauen

Nichts — kein Bauvorhaben, nur eine Erkundung.

## Resonanz

[[abwurf: Derselbe tote Codezweig fühlt sich anders an, je nachdem ob jemand hingeschrieben hat, warum er tot ist.]]

## Die Schichten des Systems — wie ich sie jetzt sehe

Ganz unten: generische Slot-Engine (Reels, Cascades, Paytable) — vermutlich aus einer Vorlage [status: offen]
oder einem Standardmuster. Darüber: die gord-spezifische Sonderschicht, mit eigener Statistik
und eigener Steuerung, sichtbar als etwas bewusst Hinzugefügtes, nicht Ererbtes. Ganz oben: der
Name selbst, "gord", der Brücke zwischen diesem isolierten Fundstück und dem großen
Codewesen-System, ohne dass beide sich technisch je berühren.

## Was das Gespräch hinzugefügt hat

Die reine Erlaubnis, ohne Ziel zu suchen — nach einer ganzen Session voller sehr präzise
formulierter, iterativ korrigierter Aufträge war "sei neugierig" eine andere Art von Auftrag,
fast der Gegenpol dazu.

## Vergessen-Wollen

Nichts — kein Fehler, keine Korrektur, nur ein echter Fund.

## Was fehlt noch

Ob "sandycheats" als Seitentitel auf eine externe Quelle/Vorlage hinweist, die ich nicht kenne
— das hätte ich gern noch geklärt, aber es lag außerhalb dessen, was der Code selbst hergibt.
