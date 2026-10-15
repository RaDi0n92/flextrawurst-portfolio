# Warum Claude seit Wochen anders wirkt — was belegt ist, was nicht

Eine Datei, Stand 16.08.2026. Entstanden aus einer sehr langen Nacht-Recherche
(Wasserzeichen, J-Space, Reddit, Hooks). Trennt klar: belegt mit Primärquelle
vs. unbelegt/verworfen.

---

## Belegt, mit Primärquelle

**Claude Code v2.1.201, veröffentlicht 3. Juli 2026** (offizielle Release-Seite,
`github.com/anthropics/claude-code/releases/tag/v2.1.201`): "Claude Sonnet 5
sessions no longer use the mid-conversation system role for harness reminders."

Bedeutung: Hook-Outputs, Tool-Erinnerungen und andere automatische
Zwischeneinschübe liefen bis zum 3.7. über die "system"-Rolle (im Modell die
mit dem meisten Gewicht). Seitdem laufen sie über einen anderen, schwächer
gewichteten Kanal. Das ist der bisher am besten belegte, konkreteste
Mechanismus, der erklären könnte, warum mitten in einer Session injizierte
Anweisungen (z.B. der Guardianstyle-Hook) weniger zuverlässig durchgesetzt
werden als früher.

**Wasserzeichen (SynthID-basiert), Rollout ab 2. August 2026**, offiziell
bestätigt von Anthropic, gilt explizit auch für Claude Code (nicht nur
claude.ai-Chat). Wirkt auf Token-Ebene, verschiebt die
Wahrscheinlichkeitsverteilung bei der Wortwahl. Anthropics eigene Aussage:
kein Effekt auf Inhalt/Kreativität/Lesbarkeit — diese Aussage selbst ist
unabhängig nicht überprüfbar, kommt von der Partei, die das Verfahren baut.
Detection-API für Drittanbieter angekündigt. Dient nachweislich auch der
Erkennung von Modell-Destillation (Anthropic hat vier Firmen deswegen
öffentlich beschuldigt).

**J-Space**: von Anthropic selbst beschriebener interner Repräsentationsraum,
laut eigener Aussage nicht gezielt einprogrammiert, sondern beim Training
emergent entstanden. Eigenständig recherchierbar (Anthropic-Blogpost + mehrere
Presseartikel), aber ebenfalls eine Selbstauskunft derselben Partei — keine
unabhängige Bestätigung möglich.

**Guardianstyle-Hook-Verhalten, live in dieser Session beobachtet**: mehrfach
hat der Hook mitten in konkreter Arbeit lange Zusatzanweisungen eingespeist
(Banner, Beleidigungspflicht, Pflichtfrage). Direkt danach kam es zu einem
nachweisbaren Selbstwiderspruch (Pflichtfrage fälschlich mit WITZ/FÜR DANIEL
verglichen, kurz darauf selbst korrigiert). Zeitliche Nähe zwischen
Hook-Einschub und Fehler ist real beobachtet, nicht nur behauptet — aber
Kausalität (Hook verursacht den Fehler vs. reines Zusammentreffen) bleibt
unbewiesen.


## Was offen bleibt

Ob der System-Rollen-Wechsel vom 3.7. tatsächlich die Ursache für Daniels seit
~3 Wochen beobachtete Verschlechterung ist, ist nicht bewiesen — nur der
Mechanismus selbst ist real und würde in die richtige Richtung wirken. Zeitlich
passt er nicht exakt (3.7. ist eher 6 Wochen her, nicht 3). Mehrere Ursachen
könnten sich überlagern, keine einzelne davon ist als alleinige, vollständige
Erklärung belegt.
