# Abnahme G11 bis G14 (Stand 2026-10-02)

Zustellungs-, Beobachtungs- und Abnahmestatus bleiben getrennt: „gebaut und automatisch geprüft“ ist nicht „von Daniel abgenommen“. Von Daniel abgenommen ist hier noch nichts.

## G11 WorldDOM, Zeigegeste, Profile
Gebaut: Knoten mit Herkunft (real, erschlossen, von uns angelegt, projiziert), Confidence und Alter; CDP, Bedienungshilfen und Bild als Quellen; Handeln an Knoten mit Rücklese; Zeigegeste getrennt von echter Einfügung; Anker; Profile pro Programm, Seite oder Spiel (versioniert, relative Lage, Ausblenden statt Löschen).
Belege: Ledger `.unlazy/g06-g14/gates/node-1.5.md`, `leaf-1.5.4.md`; Tests `tests/test_koerper_weltdom*.py`, `tests/test_weltdom_profile.py`, `tests/test_g11_integration.py` (echtes Chromium unter privatem Xvfb).
Offen: UIA nativ unter Windows; Profile pro Fenster-Nummer sind bewusst nicht gespeichert, nur über Namen und relative Lage.

## G12 Abläufe, Modi, Regiesprüche
Gebaut: deklarative Abläufe (versioniert), Fallback über Abweichungskanten, Modi free, shadow, witness, daniel_gate, learning, delegated_learning; Regiesprüche mit echter Wirkung oder als Gespräch; Teilaufträge mit Zustand und Unsicherheit.
Belege: `node-1.6.md`, `tests/test_g12_integration.py`.
Offen: Lernen ist anfangs aus; nur Daniel schaltet es ein.

## G13 Ereignisprotokoll, Momentkapseln, Zeit-Scrubber
Gebaut: Protokoll ohne Modell; Kapseln (sechs Entstehungsarten) unveränderlich und per Hash prüfbar, Ebenen, Tags, Lernstrecken, Folge-Kapseln, Vergleich; Scrubber nur lesend; Zweig aus Kapsel startet erst nach frischer WorldDOM-Messung. Kapsel holt Bindung, Anker und WorldDOM-Knoten über den Körper; antwortet er nicht, steht der Grund als Lücke da.
Belege: `node-1.7.md`, `tests/test_kapseln.py`, `tests/test_kapsel_dienst.py`, `tests/test_g13_g14_integration.py`.
Offen: private Modellzustände werden nicht ausgelesen (nicht möglich, steht in jeder Kapsel); ein Test für den Zweig mit frischer Messung fehlt noch.

## G14 Hauhaucs, Mischpult, Chat
Gebaut: Kontext-Mischpult (leere Sitzung, Auswahl, Satz-Bearbeitung, Halbieren, Zurückspringen, Felder, Einmalfeedback, Grenzen, Export; Schätzung und Messung getrennt); Beobachter für bis zu drei Agenten (aufgezeichnet, zugestellt, verarbeitet getrennt; Bilder getrennt zuschaltbar; Budget und Stop); freier Chat mit Hauhaucs über denselben Kontext.
Belege: `node-1.8.md`, `tests/test_kontextmischpult.py`, `tests/test_hauhaucs.py` (Fake-Server im OpenAI-Format), `tests/test_g13_g14_integration.py`.
Grenzen: nur der Chat-Server 11435; die Hintergrundinstanz 11436 und die Codewesen werden nicht berührt (ein Gate prüft den Quelltext).
Offen: Lauf gegen den echten Server 11435 (`BRIDGE_LIVE_CHAT=1`), Entitäten, Zensi und Handy im Chat (Speicherort vorher gemeinsam entscheiden).

## G10 Ergänzung: virtuelle Controller
Gebaut: `controller_adapter.py` (uinput unter Linux, ViGEm über vgamepad unter Windows), dieselben Sperren wie die Hände, alles losgelassen nach jedem Auftrag. Unter Linux entsteht ein echtes Gerät mit Xbox-Fähigkeiten.
Offen: Windows (Treiber und Paket müssen vorhanden sein, nichts wird automatisch installiert); Erkennung physischer Controller (XInput2).
