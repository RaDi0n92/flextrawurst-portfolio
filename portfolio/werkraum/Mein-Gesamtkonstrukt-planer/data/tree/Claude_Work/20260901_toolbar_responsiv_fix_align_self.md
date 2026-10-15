# Toolbar-Fix: echter Umbruch statt horizontalem Scrollen

Daniel meldete nach dem ersten Umdekorieren-Schritt: "alles ist noch statischer geworden und braucht ein maximales fenster sobald ich es kleider mache wird alles nur abgeschnitten." Die Scroll-Loesung von vorhin war also ein Rueckschritt fuer die Bedienbarkeit bei nicht maximiertem Fenster.

Root Cause fuer den fruehren Overlap-Bug gefunden, der mich zur Scroll-Loesung getrieben hatte: header.topbar ist ein Grid-Item von main.app-shell. CSS Grid streckt Items per Default (align-items:stretch) auf die volle Zeilenhoehe - "height:auto" oder "min-height" am Header selbst aendert daran nichts, weil das Strecken Vorrang hat. scrollHeight des Headers zeigte die korrekte, groessere Inhaltshoehe (198px), aber getBoundingClientRect/offsetHeight blieben bei 82px - der Inhalt lief sichtbar ueber, ohne die Box wachsen zu lassen.

Fix: header.topbar bekommt align-self:start, damit nimmt es sich aus dem Streckzwang heraus und waechst zuverlaessig mit seinem tatsaechlichen Inhalt. Live getestet bei 500px, 800px und 1297px Fensterbreite (per CDP Emulation.setDeviceMetricsOverride simuliert) - kein Ueberlappen mehr in keiner Breite, Header und Inhalt darunter passen sich sauber an.

top-actions ist jetzt wieder ein echter Flex-Umbruch (flex-wrap:wrap) statt horizontalem Scrollen mit Fade-Maske. Alle sechs Gruppen bleiben in jeder getesteten Breite vollstaendig sichtbar, kein Scrollen noetig.

Nach dem Fix erneut auf Absturzsicherheit geprueft (Suchfeld tippen) - kein Hänger, kein Crash.

Damit sollte das urspruengliche "braucht maximales Fenster"-Problem behoben sein. Bitte bei Gelegenheit selbst mit echtem Fenster-Resize gegenpruefen, ob es sich jetzt richtig anfuehlt.
