# Wichtiger Nachtrag: has-notice-Fix war nicht tab-wechsel-fest

Beim systematischen Ueberpruefen weiterer Breiten (nach dem Header- und Stage-Buttons-Fund) mit einem generischen Overlap-Scanner ueber alle sechs Tabs geprueft. Auf Netz/Plan/Zeitspur/Replicas denselben kleinen Fund gemacht (.stage-status ragt ~16px ueber den Viewport, geringe Prioritaet, nicht weiter verfolgt) - aber beim Nachschauen auf Netz bei 800px tauchte die GROSSE leere Flaeche wieder auf, die eigentlich schon behoben war.

Ursache: main.app-shell's className wird von React bei jedem Re-Render (z.B. einfachem Tab-Wechsel Netz -> Canvas -> Netz) komplett neu berechnet und ersetzt. Die has-notice-Klasse, die der fruehere Fix per einmaligem classList.add gesetzt hatte, ging dabei wieder verloren - live reproduziert: main.app-shell zeigte nach dem Tab-Wechsel wieder "app-shell mobile-panel-stage" ohne has-notice, grid-template-rows sprang zurueck auf die falsche 2-Zeilen-Aufteilung (147px/410px/243px statt korrekt 147px/49px/604px). Die urspruenglich behobene leere Flaeche kam also bei jedem Tab-Wechsel zurueck, nicht nur beim ersten Laden - der committete Fix war in echter Nutzung praktisch wirkungslos.

Fix: ein MutationObserver auf main.app-shell's class-Attribut haelt has-notice jetzt dauerhaft aufrecht statt es nur einmal zu setzen - reagiert auf jeden React-Re-Render, der die Klasse entfernt, und fuegt sie sofort wieder hinzu. Selbstheilend, keine Endlosschleife (Check-vor-Mutation, gleiches Muster wie bei den anderen Observern in diesem Codebase).

Sicherheitscheck: alle anderen classList.add-Aufrufe im Code geprueft (workspace.js, streams.js, operating_shell.js) - die setzen alle "open" auf selbst erzeugten Panels/Overlays, die AUSSERHALB von Reacts Baum liegen (document.body angehaengt) und daher nie von React-Re-Renders betroffen sind. Nur main.app-shell (ein React-verwaltetes Element) war betroffen, also nur dieser eine Fix musste abgesichert werden.

Live verifiziert: mehrfacher Tab-Wechsel bei 800px UND bei 375px - has-notice bleibt jetzt erhalten, kein Rueckfall der Luecke mehr.

Committet.
