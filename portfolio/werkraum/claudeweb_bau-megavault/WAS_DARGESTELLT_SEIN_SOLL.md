# Was dargestellt sein soll

Konkrete Inhalte, die pro Datei/Knoten sichtbar/abrufbar sein sollen -- nur was
tatsächlich besprochen und bestätigt wurde.

- Wer: welches Wesen/welcher Strom die Datei angelegt/berührt hat (aus echtem
  Pfad-Präfix abgeleitet -- `_gpt`, `_claude`, `_gemini`, `_codex`, `_kimi`,
  `_glm`, `_shared`, `wesen_vaults`).
- Wann: echtes Erstellungs- und Änderungsdatum (os.stat, keine Erfindung).
- Wo: echter Dateipfad, echte Ordnerhierarchie (aus Pfaden abgeleitet, kein
  neuer Knotentyp im Register).
- Was: Dateigröße, echter Inhalt (Volltext lesbar), Klartext-Vorschau aus
  Metadatenfeldern wie `gedanke`, `inhalt`, `frage`, `antwort` etc.
- Mit wem: echte Kanten aus dem Beziehungsregister (Verbindungen zu anderen
  Knoten, nur beim Hover sichtbar).
- Tags/Index/Wiki: noch nicht konkret umgesetzt -- offen.
- Historie: echte Git-Commit-Historie + echter Diff pro Datei, wo die Datei in
  einem Git-Arbeitsbaum liegt.
