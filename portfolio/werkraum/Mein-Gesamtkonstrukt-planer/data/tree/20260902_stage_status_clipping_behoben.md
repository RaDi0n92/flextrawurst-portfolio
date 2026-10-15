# Stage-Status-Leiste: letzter Fund aus dem Breiten-Scan behoben

Nach den Header-, Stage-Buttons- und has-notice-Fixes den generischen Overlap-Scanner (main.app-shell *, alle flex/grid-Container mit overflow:visible, Kinder die mehr als 15px ueber die eigene Zelle hinausragen) ueber alle sechs Tabs und sechs Breiten (900/850/800/700/650/375px) laufen lassen.

Fund: .stage-status (die Statusleiste "Revision X auf Server · Eingebetteter Arbeitsstand...") hat eigenes min-height:44px aus dem nativen CSS, waehrend .stage-panel's Grid-Zeile dafuer je nach gerade aktiver nativer Breakpoint-Variante nur 28px oder 31px gross ist. Das Kind ragt dadurch um genau die Differenz sichtbar ueber den Viewport hinaus - gemessen bei 800px Fensterbreite/-hoehe: Statusleiste bei y:772-816, Panel endet aber bei y:800, also 16px Ueberhang. Betraf Netz/Plan/Zeitspur/Replicas gleichermassen, da .stage-panel ein gemeinsam genutztes Bauteil ist, nicht tab-spezifisch.

Fix: erste und letzte Zeile von .stage-panel auf auto statt fixer Pixelwerte gesetzt - passen sich dann immer an die tatsaechliche Kindgroesse an, unabhaengig davon welche der mehreren nativen Breakpoint-Varianten (28px/31px/44px je nach Breite) gerade greift. Mittlere Zeile bleibt minmax(0,1fr) und gibt den gesparten Platz an die eigentliche Graph-/Canvas-Flaeche ab - kein Verlust an nutzbarer Flaeche, nur korrekte Verteilung.

Live verifiziert: Overlap-Scan ueber alle sechs Tabs x sechs Breiten zeigt jetzt ueberall [] (kein Fund mehr), bis auf den bereits als unkritisch eingestuften .replica-lens-editor-Fund (Inhalt schlicht unterhalb des sichtbaren Viewports, erreichbar durch Scrollen, kein aktiver visueller Overlap). Bei 1297px Desktop unveraendert korrekt.

Damit ist der systematische Breiten-Scan (ausgeloest durch Daniels Beobachtung "Fenster gross/klein ziehen zeigt die Arbeitsflaeche schrumpft unverhaeltnismaessig") fuer alle sechs Tabs abgeschlossen: Header (max. 2 Zeilen), Canvas-Werkzeugleiste (kein Overlap mehr), Netz-Grid-Luecke (jetzt tab-wechsel-fest), Stage-Status (kein Clipping mehr) - vier echte, tiefgreifende Bugs gefunden und behoben, alle auf dieselbe Grundursache zurueckfuehrbar: native CSS-Breakpoints, die fuer genau zwei Breiten (breit und <760px) entworfen wurden, ohne Behandlung des dazwischenliegenden Bereichs, in dem ein normal grosses Browserfenster meistens tatsaechlich liegt.

Committet.
