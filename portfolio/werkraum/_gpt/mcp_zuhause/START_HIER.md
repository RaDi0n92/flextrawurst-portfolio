# Start hier

## Beim Verbindungsstart

1. `history_startup` setzt standardmäßig die bekannte kanonische Session-ID dieses UI- oder Arbeitsfadens fort. Ohne ID wird keine neue Session erfunden.
2. Eine wirklich neue Arbeitslinie verlangt `session_intent="new"` und einen dokumentierten `new_session_reason`; eine geschlossene Session wird nicht still ersetzt.
3. Der Session-Kontinuitätsvertrag, der UI-Gesprächsvertrag, der Zeitstrom und die Dateiarbeitsverfassung werden gebunden.
4. Die kompakte `mcp_zuhause`-Projektion nennt diesen Startpunkt, die Karte, die Arbeitsweise, bekannte Muster, offene Fragen und den letzten Übergabebrief.
5. Der Gesamtatlas liefert Revision, Kartenstatus und einen eigenen Cross-Session-Puls. Neue fremde Änderungen werden auch während der Sitzung erneut eingespielt, nicht nur beim Start.
6. Neue übergreifende Ideen werden vor ihrer Darstellung über `atlas.idea_marker` auf auffindbare Vor- und Parallelspuren geprüft.
7. Vollständige Zuhause-Dokumente werden nur bei Bedarf über `mcp.home` gelesen. Der Start soll Orientierung geben, nicht jedes Mal den gesamten Dachboden in den Kontext kippen.
8. Wenn eine Sitzung eine echte Reflexionsspur hinterlassen soll, gilt [[SPIEGEL_ANLEITUNG]]. Neue Spiegel werden unter `/root/werkraum/_gpt/spiegel/` angelegt. Alte Spiegel sind Herkunft und Gesprächspartner, keine automatisch übernommene Erinnerung.

## Session-Kontinuität

- Jeder UI-Chat und Arbeitsfaden behält seine eigene kanonische MCP-Session.
- Wiedereinwahl, F5, Zeitabstand oder erneuter VPS-Eintritt sind Fortsetzungen, keine Gründe für eine neue ID.
- Parallele Chats werden nicht in eine globale Session verschmolzen.
- Der Server wählt niemals automatisch die global zuletzt aktive Session.
- Jeder Start zeigt entweder `[SESSION-KONTINUITAET: FORTGESETZT …]` oder `[SESSION-KONTINUITAET: NEU … | GRUND=…]`.

## Vor dem ersten Werkzeugaufruf

- Handelt es sich sicher um eine reine Leseaktion?
- Gibt es aktive Claims oder fremde Zuständigkeiten am Ziel?
- Ist das Ziel eine Primärquelle oder eine regenerierbare Ansicht?
- Braucht die Suche ein engeres Wurzel-, Zeit- oder Scanbudget?

## Sperrvertrag

Reine Leseaktionen dürfen innerhalb derselben Session parallel laufen. Mutationen, Shell-Aufrufe, Dienstaktionen, Tests und nicht eindeutig klassifizierte Werkzeuge bleiben exklusiv.

Der Sessionabschluss wartet auf laufende Leser. Er beendet sie nicht mitten in der Rücklesung.

## Wahrheitsregel

Ein Werkzeugergebnis darf nur so vollständig benannt werden, wie es tatsächlich ist. Budgetbegrenzte Suchen melden ihren Teilstand. Installierte Skills werden nicht als angewendet ausgegeben, solange keine reale Nutzungsspur vorliegt.
