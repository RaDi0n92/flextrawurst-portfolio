# Sitz / Goals / Loops / Review / Lernen · dünner Denkrahmen

Status: **Arbeitsmodell, nicht finale Engine.**

## 1. Der Sitz

Der Orchestrierungssitz ist ein dauerhaft vorhandener **leerer Platz**.

Er orchestriert nicht selbst.

Daniel kann situativ eine konkrete Instanz hineinsetzen und ihr Scope/Verantwortung geben – von einem kleinen Ausschnitt bis zur gesamten Koordination.

Nach Ende darf der Sitz wieder leer sein.

Keine permanente Chef-KI daraus ableiten.

## 2. Delegation braucht nur das, was die konkrete Arbeit braucht

Mögliche Angaben:
- Goal / gewünschter Zustand
- Scope
- relevante Rechte/Grenzen
- Ausgangsmaterial
- erwartete Belege/Review

Nicht jedes Delegat braucht sofort universelles Schema.

## 3. Goal statt Aufgabenende

Ein Goal ist langlebiger als eine einzelne Session oder ein Task.

Arbeitsannahme:

`Goal → konkrete Arbeit → Wirkung/Beleg → Review → nächste Arbeit oder erreicht`

Ein `completed`-Task beweist nicht automatisch, dass der gewünschte Weltzustand erreicht wurde.

Für V0 reichen:
- Goaltext
- wenige Kriterien
- Belege
- Status offen/erreicht/neu prüfen, wenn wirklich gebraucht

## 4. Körper ≠ Run

`gkos.koerper.v1` zeigt bereits wiederverwendbare Ablaufstruktur.

Ein konkretes Durchlaufen dieser Struktur ist etwas anderes.

Deshalb als Denkmodell:
- **Körper** = Strecke / zusammengesetztes Arbeitsgerüst
- **Run** = konkrete Fahrt zu einem Zeitpunkt mit konkreter Instanz und konkretem Zustand

Die bereits gebauten `gkos.run.v0`-Prototypen testen diese Trennung, sind aber kein Zwang für jede spätere Szene.

## 5. Aktiver Node gehört zur Fahrt, nicht zur Strecke

Ein Körper kann mehrfach durchlaufen werden.

Darum darf `wo bin ich gerade?` nicht den wiederverwendbaren Ablaufkörper selbst dauerhaft umschreiben.

Ob dafür langfristig Run-Datei, Projektion oder anderer Körper benutzt wird, erst aus Nutzung entscheiden.

## 6. Loop heißt nicht Endlosschleife

Ein Rückpfeil bedeutet nur:
> diese Strecke kann wieder zu einem früheren Schritt führen.

Ob wirklich eine weitere Runde nötig ist, entscheidet der konkrete Zustand/Review/Goal.

Keine automatische Wiederholung allein aufgrund einer Loop-Kante.

## 7. Review ist Arbeit an Wirkung und Beleg

Review fragt z. B.:
- ist die behauptete Wirkung wirklich eingetreten?
- reichen die Belege?
- ist das Goal erreicht?
- braucht es eine weitere Runde?
- wurde etwas Allgemeines gelernt, das später dauerhaft helfen kann?

Review muss nicht derselbe Akteur sein, der gebaut hat.

## 8. Handoff ist kein Run-Ende

Eine Instanz kann Arbeit übergeben und verschwinden, während Goal/Run/Arbeitskörper weiterbestehen.

Übergabe sollte mindestens klar machen:
- woran wurde gearbeitet?
- was ist tatsächlich passiert?
- was bleibt offen?
- wo liegen Belege/Material?

Nicht aus jeder Übergabe neue Weltontologie bauen.

## 9. Warten sitzt am blockierten Zweig

Wenn ein konkreter Proposal auf Daniel wartet, muss nicht der gesamte Strom/Run eingefroren sein.

Nur wenn wirklich nichts Relevantes weitergehen kann, ist der ganze Arbeitskörper blockiert.

## 10. Lernen ohne Modellmagie

Bereits vorhandenes brauchbares Muster:

`wiederholter Fund → Beförderungskandidat → Review → akzeptieren/ablehnen`

Das ist ein guter Start für „das Gerüst späterer Läufe verbessert sich“.

Nicht behaupten:
- Modellgewichte wurden gelernt
- jede Review-Erkenntnis wird automatisch Regel
- jede einmalige Korrektur verdient dauerhafte Beförderung

## 11. Schutz vor Selbstvermüllung

Eine dauerhafte Änderung sollte stärker begründet sein als eine lokale Lösung.

Fragen:
- tritt das Muster wiederholt auf?
- gibt es Belege?
- hilft die Änderung später wirklich?
- kann sie wieder verworfen/korrigiert werden?

Wenn nicht: lokal lassen.

## 12. Schrottplatz-Impulse

Nur Bilder, kein Kanon:
- leerer Sitz als real sichtbarer Verantwortungsort
- konkrete Fahrt als mobiler Arbeitskörper
- Review als Prüfstand am Werk
- Handoff als übergebbares Paket/Material
- nächste Iteration als erneute Fahrt statt „Agent respawnt“

Der Erfolg ist nicht die Metapher, sondern dass Daniel **ohne Ablaufdiagramm versteht, was noch lebt und warum**.

## Nicht jetzt

- vollständige Goal-Engine
- universelle Run-State-Machine
- automatische Orchestratorwahl
- Konfliktlösung für beliebige parallele Runs
- generische Lernmaschine

Erst echte Szenen zeigen, welche Teile davon wirklich gebraucht werden.