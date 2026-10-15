# Abnahme G06.7 — Fensteraufnahme, Chromium (CDP), Bedienungshilfen

Stand: 2026-10-02. Belege: `.unlazy/g06-g14/gates/leaf-1.2.1.md` bis `leaf-1.2.3.md` (13 Gates, alle erfüllt, per `--reverify` neu gelaufen).

## Was gebaut und auf dem VPS belegt ist

* Der Bilderstrom fragt je Fenster-Ziel zuerst die Fensteraufnahme der Plattform (Linux: XComposite, Windows: PrintWindow mit PW_RENDERFULLCONTENT) und nimmt deren Bild, wenn es echten Inhalt hat.
  Ein verdecktes Fenster kommt vollständig und ohne ein Pixel des anderen Fensters (echte Fenster unter Xvfb).
* Eine leere, schwarze oder ganz durchsichtige Aufnahme fällt sichtbar auf den Bildschirmausschnitt zurück: `aufnahme: "ausschnitt"` mit `fallback_grund` (`leer`, `fehlt`, `fehler`, `nicht_unterstuetzt`).
  Ein Desktop-Ziel ist immer ein Ausschnitt ohne Grund. Dunkler Inhalt mit etwas Text und ein leeres weißes Blatt zählen als echter Inhalt.
* Jeder Agent hat seine eigene Bildfolge: `seq` (je Ziel, beginnt beim Neubinden bei 0), `captured_at_ms`, Quelle. Der Relay prüft die Felder `aufnahme`, `fallback_grund`, `seq` streng (ältere Körper senden sie nicht — bleibt gültig).
  Der Starter hält sie in `latest.json` fest und nennt `age_ms`.
* Minimierte Ziele werden nicht gesendet (der Ausschnitt zeigte sonst, was darunter liegt) und nicht gefordert.
* Chromium über DevTools (`cdp.py`): Ziele, Seitenbild, DOM-Knoten mit Lage, Baum der Bedienungshilfen, Klick, Tippen mit Rücklese. Nur Loopback, nicht auffindbare Knoten lösen nichts aus.
  Gemessen gegen echten Chromium: verdeckt, klein (200×150) und minimiert (mit Fensterverwaltung) liefern das Seitenbild trotzdem, weil der Browser die Seite selbst rendert.
* Bedienungshilfen (`uia.py`): Linux AT-SPI gegen ein echtes GTK-Programm (Lesen, Klicken, Text setzen mit Rücklese aus dem Programm; ein Knoten ohne Fähigkeit löst nichts aus; ein Programm ohne Bedienungshilfen ist `kein_baum`).
  PyGObject bietet die Text- und Action-Schnittstellen als statische Funktionen (`Atspi.Text.get_text(knoten, …)`).
* Windows: PrintWindow unter Wine geprüft (weißes Fenster 120×80 liefert 38 400 Bytes echte, undurchsichtige Pixel; ungültiges und minimiertes Fenster liefern `None`).
  GDI liefert Alpha 0; es wird auf 255 gesetzt, und `ist_leer` braucht kein numpy.

## Was nicht belegt ist (offen, nativ)

* PrintWindow gegen echte Windows-Fenster (Browser, Spiele): unter Wine ist nur ein einfaches Fenster geprüft; Schwarz bei Spielen/Hardwarebeschleunigung ist bekannt und führt zum sichtbaren Rückfall, aber nicht gemessen.
* UI Automation nativ (comtypes im Paket 0.10.0 nicht gebündelt): gegen ein nachgebautes Objektmodell geprüft, nie gegen echtes Windows.
* Chrome/Edge unter Windows mit `--remote-debugging-port`: nicht geprüft.
* Linux ohne Compositor: verdeckte Teile eines Fensters, die gezeichnet wurden, *bevor* die Bridge das Ziel umleitet, fehlen bis zur nächsten Neuzeichnung der Anwendung (so im Test belegt). Nach dem Binden kommen sie vollständig.
* Die Eingabe-Seite von „Hände auf einem Ziel-Knoten“ (Klick auf Knoten per Eingabeadapter) gehört zu G10/G11.
