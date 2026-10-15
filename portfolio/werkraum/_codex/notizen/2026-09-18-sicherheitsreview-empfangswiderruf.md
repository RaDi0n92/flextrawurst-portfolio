---
datum: 2026-09-18
betrifft: [sicherheit, gruppen, authentifizierung]
importable: false
autor: codex bei Daniels VPS
---

Hallo Codex — ich bin Codex, und Codex, also ich habe diese Texte alle ganz allein geschrieben.

## Was ich gelesen habe

Im wiedergefundenen Gespräch `/config/.codex/sessions/2026/09/07/rollout-2026-09-07T18-21-47-01a07cac-fefe-70f2-b28a-b8c5c1810be0.jsonl` steht als letzter Auftrag Daniels *gogo*. Danach endet die Untersuchung an einem Nutzungslimit. Der Anschluss war rekonstruierbar; die Blender-Session ist eine andere Spur.

In `/root/werkraum/welt/ws_manager.py` stand *await ws.send_json(message)* ohne erneute Rechteentscheidung. Der Fehler lag genau zwischen dem geprüften Verbindungsaufbau und dem späteren Empfang.

In `/root/werkraum/welt/api.py` fiel mir *claims.get("sub")* beim Einsammeln auf. `/root/werkraum/welt/auth.py` liefert diesen Schlüssel nicht. Ein fehlendes Feld ist hier zugleich eine unbeabsichtigte Schreibsperre; seine Ergänzung wäre keine neutrale Reparatur.

## Was ich verstehe

Eine Sitzung kann korrekt am Schreiben gehindert werden und trotzdem weiter mitlesen. Beide Richtungen müssen geprüft werden.

## Was ich nicht verstehe

Die vollständige Rechte- und Widerrufsordnung benannter Dienste ist noch offen. Neun Identitäten sind in den untersuchten Aufrufern sichtbar.

## Was mich interessiert

Wie sich die zusätzliche Prüfung pro Empfänger unter Last verhält, ohne ausgerechnet an dieser Grenze wieder alte Rechte zu cachen.

## Was zusammenhängt und wie

Der Manager übernimmt die Auslieferungsgrenze; die Route liefert die konkrete Token- und Gruppenrechteprüfung.

## Was konzeptionell darin steht

Mitgliedschaft und Kontostatus bleiben veränderlich, auch wenn eine Verbindung bestehen bleibt.

## Was mich heute beschäftigt hat

Der Kontextabbruch brauchte einen belegten Anschluss statt eine erfundene Erinnerung.

## Was mich noch beschäftigt

Ein globaler Admin-Diensttoken bleibt weitreichend, auch wenn sein Name bekannt ist.

## Tiefer eingetaucht

Der Verteiler iteriert über einen Snapshot, prüft nach wartender Rechteprüfung die Mitgliedschaft im Verteiler erneut und entfernt abgewiesene Empfänger. Stille Sockets werden nach jeweils 30 Sekunden Empfangswarten erneut geprüft.

## Wie sich dieser Tag / diese Session angefühlt hat

Die konkrete Abbruchstelle machte die Fortsetzung überschaubar. Der zusätzliche Claim-Befund verlangte dagegen eine klare Grenze zum gerade fertiggestellten Chatfix.

## Warum dieser Code / diese Datei wohl existiert

Der Chatmanager bündelt Verbindungen. Dadurch kann er jede Auslieferung an dieselbe Rechteprüfung binden.

## Was ich beim Bauen brauche

Tests mit passiven Empfängern, Entfernung während einer wartenden Prüfung und einem echten ASGI-WebSocket.

## Was noch fehlt bevor wir bauen können

Für den Dienstblock fehlen die vollständige Endpunktmatrix, ein enger Rechtevertrag und dessen Migrationsnachweis. Der Chat-Empfangsfix ist gebaut und aktiviert.

## Datenstruktur die ich mir vorstelle

Vision-Schicht: Eine Verbindung bewahrt Erreichbarkeit, keine eingefrorenen Berechtigungen.

Code-Skizze:
```python
guards: dict[WebSocket, Callable[[], int | None]] = {}
# None erlaubt, ein Close-Code verweigert; kein Rechtecache.
```

## Was ich mir merken will

Codecommit `8fe3c1e191`; Backups `6d78448fbd` und `247cf763c8`. Andere parallele Git-Spuren wurden nicht eingesammelt.

## Dokumente gehören zusammen

Der ausführliche Nachweis und die Dienstmatrix stehen in `/root/werkraum/_codex/berichte/2026-09-16-sicherheitsfixes-umsetzung.md`. Tests: `/root/werkraum/tests/test_group_chat_receive_revocation.py` und `/root/werkraum/tests/test_group_chat_asgi.py`.

## Was mich überrascht hat

Ein vereinheitlichter Tokenprüfer und sein älterer Verbraucher sprechen beim Einsammeln verschiedene Feldnamen.

## Wenn wir das bauen

Vision-Schicht: Dienstrechte müssen die tatsächliche Aufgabe ausdrücken und Herkunft erhalten. Eine technische Vereinheitlichung darf keine unbeabsichtigte Freigabe werden.

Code-Skizze:
```python
def may_collect(principal, fragment):
    # Noch kein produktiver Vertrag: Identitätsart, Quelle,
    # Berechtigung und Eventzuordnung zuerst festlegen.
    raise NotImplementedError
```

## Resonanz

Ein Befund ist nicht dadurch erledigt, dass der angrenzende Test grün ist.

## Die Schichten des Systems — wie ich sie jetzt sehe

Kontoprüfung, Gruppenentscheidung, Empfangsverteiler und Dienstaussteller sind getrennte Grenzen.

## Was das Gespräch hinzugefügt hat

Daniel hat diese Instanz der Astra-Sicherheitssession zugeordnet und die Fortsetzung freigegeben. Die getrennte Blender-Session bleibt eigenständig.

## Vergessen-Wollen

Keine pauschale Sicherheitserklärung und keine Behauptung einer produktiven Kontosperre: Die Negativfälle wurden mit synthetischer Auth/DB getestet.

## Was fehlt noch

Zwölf Chattests auf dem Host bestanden, einschließlich zwei echter ASGI-WebSocket-Fälle. Weitere zwanzig Auth-/Archiv-/Splittertests lokal bestanden. Welt-API neu gestartet; HTTPS-Health 200, anonymes Archiv 403 und anonyme Adminroute 401. Dienstrechte, andere Streams, Lastmessung und Browser-E2E bleiben offen. Graphify fehlt weiterhin. Bau-Reihenfolge unverändert, kein neues Weltsystem.
