# Gesamtatlas-Dateikörper

**Ziel:** Ein lokal gebauter, regelmäßig aktualisierter und vollständig zipbarer Gesamtatlas für externe Menschen und LLMs.

**Kein öffentlicher Gesamtatlas:** Die frühere Route `https://flextrawurst.de/gesamtatlas/` wurde nach Daniels ausdrücklicher Korrektur entfernt und antwortet mit HTTP 404. Der zugehörige Webkörper bleibt lediglich als historische Fehlspur im Atlas erhalten.

## Aktuelle Ergebnisse

- Entpackter Körper: `/root/werkraum/_gpt/gesamtatlas/dateikoerper/AKTUELL/`
- Aktuelles ZIP: `/root/werkraum/_gpt/gesamtatlas/dateikoerper/GESAMTATLAS_DATEIKOERPER_AKTUELL.zip`
- Stabiler Kurzpfad: `/root/werkraum/_gpt/gesamtatlas/GESAMTATLAS_DATEIKOERPER_AKTUELL.zip`
- Bauzustand: `/root/werkraum/_gpt/gesamtatlas/dateikoerper/LETZTER_BAU.json`

## Gestalt

Der Körper enthält:

- mehrstufige verständliche Erklärungen,
- Gesamtatlas-Register und Maschinenkörper,
- getrennte AI-Zuhause,
- Browsergespräche,
- native Terminalwerkströme von Claude, Codex und Gemini,
- Recorder- und Action-History-Dokumentation,
- die deaktivierte Webumsetzung als nachvollziehbare Fehlspur,
- ein vollständiges Quellenmanifest mit Ursprungspfad, Ursprungshash, Exporthash und Kopierklasse,
- ein Lücken- und Abdeckungsregister,
- eine lokale Offline-Erkundungsoberfläche und Suche.

Exakte Kopien, markiert bereinigte Außenkopien und nur kartierte Körper bleiben strikt unterscheidbar.

## Manuell neu bauen

```bash
/root/werkraum/tools/gesamtatlas_dateikoerper/AKTUALISIEREN_UND_ZIP_BAUEN.sh
```

Der periodische Timer vergleicht zunächst einen Quellenfingerabdruck und überspringt den Bau, wenn sich nichts geändert hat.
