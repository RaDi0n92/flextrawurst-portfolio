# Validierungsbericht: Neutraler MCP-Standard und zeitgestempelte Belege

## Ergebnis

Status: **BESTÄTIGT – produktiv aktiv**

Diese Prüfung bestätigt zwei Korrekturen:

1. Globale MCP-/AI-Strom-Arbeit ohne ausdrücklich gesetztes Projekt wird nicht mehr in den Spiele-Traum-Körper geroutet.
2. Validierungsberichte und Maschinenbelege tragen einen kanonischen UTC-Zeitstempel im Dateinamen und werden bei späteren Prüfungen nicht überschrieben.

## Warum die frühere Ablage falsch war

Die betreffende Sitzung behandelte MCP-Start, Parallelität, AI-Strom-Arbeit und den MCP-Zuhause-Körper. Sie war keine Spielesitzung. Die Dateien landeten dort, weil UI-Export, Zeitstrom, Dateiarbeit und der systemd-Dienst denselben hart gesetzten Spiele-Traum-Pfad als globalen Standard verwendeten.

Das war ein Routingfehler, keine fachliche Zugehörigkeit.

## Neuer neutraler Standard

`/root/werkraum/_gpt/mcp_arbeitskoerper`

Produktiv zurückgelesen wurden:

- UI-Projektpfad: `/root/werkraum/_gpt/mcp_arbeitskoerper`
- Dateiarbeits-Projektpfad: `/root/werkraum/_gpt/mcp_arbeitskoerper`
- Zeitstrom-Einstieg: `/root/werkraum/_gpt/mcp_arbeitskoerper/ZEITSTROM.md`
- Zeitstromspiegel: `/root/werkraum/_gpt/mcp_arbeitskoerper/Zeitstrom`
- Wahrheitssystem für diesen neutralen Körper: `nicht konfiguriert`
- Spielespezifischer Watchdog im neutralen Start: `nicht eingeblendet`

## Korrigierte frühere Validierung

- Bericht: `/root/werkraum/_gpt/mcp_arbeitskoerper/validation/mcp_parallel_reads_home/2026-07-26/20260726T144830Z__mcp_parallel_reads_home__VALIDIERUNGSBERICHT.md`
- Maschinenbeleg: `/root/werkraum/_gpt/mcp_arbeitskoerper/validation/mcp_parallel_reads_home/2026-07-26/20260726T144830Z__mcp_parallel_reads_home__RESULT.json`

Der alte Ordner im Spiele-Traum-Projekt existiert nicht mehr.

## Dateinamensregel

Kanonische Prüfartefakte verwenden:

`YYYYMMDDTHHMMSSZ__THEMA__VALIDIERUNGSBERICHT.md`

und

`YYYYMMDDTHHMMSSZ__THEMA__RESULT.json`

Eine erneute Prüfung erzeugt ein neues Paar. Stabile `LATEST_*`-Pfade dürfen ausschließlich als Zeiger auf das neueste Paar dienen.

## Herkunftsschutz

Alte Action-History- und Zeitstromereignisse behalten den früheren falschen Pfad. Sie werden nicht rückwirkend umgeschrieben, weil sie korrekt dokumentieren, wo die Dateien damals tatsächlich erzeugt wurden. Der Fehler wurde durch Verschiebung, neue Belege und einen neuen Routingvertrag korrigiert, nicht durch Geschichtskosmetik.

## Produktivdienst

- Dienst: `vps-mcp.service`
- Zustand: `active/running`
- PID: `2204789`
- Start: `Sun 2026-07-26 18:20:24 CEST`
- Port: `8091`

## Commits

- `6a303854a` – globale MCP-Belege neutral und zeitgestempelt ablegen
- `3dd9b5953` – spielespezifischen Watchdog nur im Spielprojekt melden
