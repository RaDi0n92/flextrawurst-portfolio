# Netz zeigt 2D statt 3D - Ursache geklaert, Herkunft offen

Nach dem NaN-Fix zeigt Netz jetzt echte Knoten und Kanten, aber als 2D-SVG (fallback-graph), nicht als die von Daniel erinnerte zoombare 3D-Ansicht.

Geprueft ueber chrome://gpu in genau diesem Browser (virtuellerdesktop1): WebGL ist komplett deaktiviert. Zitate aus dem GPU-Report: "WebGL: Unavailable", "WebGL has been disabled via blocklist or the command line", "GL driver is software rendered. GPU acceleration is disabled", "Gpu compositing has been disabled ... hardware acceleration will be unavailable." Direkt reproduziert: sowohl canvas.getContext('webgl2') als auch ('webgl') liefern hier false.

Der native App-Code (app/index.html) prueft genau das beim Start der Graph-Komponente (Test auf webgl2/webgl-Context) und schaltet bei Fehlschlag automatisch auf die 2D-SVG-Ersatzansicht (fallback-graph) um - das ist die vorgesehene, funktionierende Kompatibilitaetsschicht der App selbst, kein Bug meinerseits.

Herkunft der Erinnerung "frueher 3D" bleibt offen: Daniel weiss nicht mehr genau, ob das auf einem anderen Geraet/Browser war oder mal genau hier in virtuellerdesktop1 lief - ChatGPT hatte die 3D-Graph-Ansicht mal gebaut. [status: offen]

Nicht weiterverfolgt: eine echte 3D-Faehigkeit haette GPU-Passthrough in den virtuellerdesktop1-Container hinein zur Voraussetzung - eine Container-/Infrastruktur-Aenderung ausserhalb der Planner-App und ausserhalb des jetzigen Auftrags. Auf Wunsch von Daniel nur dokumentiert, nicht angefasst.
