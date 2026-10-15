# Testobjekte aufgeraeumt, Korrektur zu Grundgesetz 4

Daniel korrigierte (2026-09-01): eigene Testklickartefakte (object-46541dcc "Neue Idee", object-ef725b51 "Offene Frage") sollten nicht liegen bleiben, nur weil Grundgesetz 4 ("nichts wird geloescht") existiert. Grundgesetz 4 gilt fuer echten, gewachsenen Arbeitsbestand - nicht fuer Muell, den ich selbst beim Durchklicken der Griffe erzeugt habe. "Wir wollen doch was sauberes bauen hier."

Beide Objekte ueber die echte UI entfernt (Metadaten-Tab -> "Objekt entfernen", 0 belegte Beziehungen bei beiden). Auf dem Server bestaetigt: Objektliste vorher/nachher verglichen, beide IDs nicht mehr vorhanden.

Technischer Fund dabei: "Objekt entfernen" loest einen echten Browser-window.confirm()-Dialog aus. Ohne CDP-Dialogbehandlung blockiert das den kompletten Tab (Runtime.evaluate und Page.captureScreenshot haengen unbegrenzt, waehrend einfache Page-Domain-Befehle wie getNavigationHistory noch antworten). Loesung: Page.enable, dann Klick per Runtime.evaluate absenden ohne auf die Antwort zu warten, parallel auf das Event Page.javascriptDialogOpening lauschen und mit Page.handleJavaScriptDialog({accept:true}) bestaetigen - dann kommt auch die urspruengliche Klick-Antwort durch. Skript cdp_click_confirm.py im Scratchpad angelegt, fuer alle kuenftigen Aktionen mit Bestaetigungsdialog wiederverwendbar.
