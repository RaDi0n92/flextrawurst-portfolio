# EINORDNUNG DER CROSS-SESSION-ABSPRACHE

Dieser Unterordner ist eine Provenienz-Kopie der während des parallelen Aufbaus ausgetauschten Koordinationsnotizen.

Die Arbeitsbereiche bleiben getrennt:
- Skriptkörper-Session besitzt Fachskripte und Rohoutputs.
- Forschungsbetrieb besitzt Session-, Gravity-, Red-Team- und kanonische Forschungsordnung.
- Die Forschungsseite liest den Skriptkörper dynamisch und verändert ihn nicht.

Der aktuelle maschinenlesbare Beobachtungsstand liegt in `../../zustand/skriptkoerper_status.json`.

Wichtig: Eine in den Absprachedateien genannte Skriptanzahl ist ein historischer Zeitpunkt. Für den aktuellen Ist-Stand gilt der dynamische Status-Snapshot beziehungsweise ein neuer Live-Aufruf von `../../werkzeuge/skriptkoerper_status.py`.
