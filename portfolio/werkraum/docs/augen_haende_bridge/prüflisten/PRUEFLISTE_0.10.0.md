# Prüfliste 0.10.0 (G06 bis G14)

Vorher: `bash /root/relay-neu.sh`, dann Agenten starten. Alle Befehle tippst du in einem Bridge-Terminal. Von dir abgenommen ist noch nichts; was nur nativ unter Windows prüfbar ist, steht als „offen“.

## G06 Körper und Anzeigeorte
1. Agent starten: Raute, Terminal und Chat erscheinen.
2. Auf KDE 1 umziehen: alles erscheint dort und verschwindet auf Windows.
3. Ziel auf einen anderen Desktop setzen: Bilder kommen nur von diesem Ziel.

## G06.7 Fensterbild
1. Fenster binden, `bridge_cli.py see`: Pfad und Alter kommen zurück.
2. Fenster teilweise verdecken: das Bild zeigt trotzdem das ganze Fenster.
3. Windows mit Browser und Spiel: offen.

## G09 Agenten und Aufträge
1. `agenten`; `sende B "hallo"`: B sieht es.
2. `auftrag B "mach X"`: Status bleibt offen, bis B `auftrag-status ID fertig` meldet.
3. Pause über das Menü und Fortsetzen.

## G10 Hände und Controller
1. `klick 100 100` ohne Lease: abgelehnt.
2. `lease`, dann `klick`, `tippe "x"`, `taste "Strg+S"`: kommt an.
3. Während einer Eingabe selbst die Maus bewegen: die Bridge stoppt sofort. F12: alles steht.
4. Controller (Profil „controller“ oder „hybrid“ am Agenten wählen, Lease nehmen): `controller knopf a`, `controller stick links 1 0`, `controller trigger rechts 1`, `controller loslassen`, `--geraet=0..3`. Linux: das Gerät „Bridge virtueller Controller N“ erscheint. Windows: braucht Paket vgamepad und Treiber ViGEmBus, sonst kommt der Grund „controller_treiber_vigembus_fehlt“. Installiert wird nichts von selbst.
5. Windows nativ (Klicken, Fokus, Controller): offen.

## G11 WorldDOM und Profile
1. `weltdom`: Knoten mit Herkunft, Alter, Vertrauen.
2. `knoten ID lesen`; `anker "Test" 200 200`; `weltdom --herkunft=authored`: der Anker ist da, auch nach Neustart.
3. `zeige 200 200` zeigt nur ein Zeichen; mit `--einfuegen` ist es eine echte Handlung.
4. `profil speichern "Browser Suche" --programm=firefox --seite=example.org`, Fenster wechseln oder neu starten, `profil liste --programm=firefox`, `profil laden "Browser Suche"`: die Anker stehen an derselben relativen Stelle. `profil weg NAME` blendet aus, `profil zurueck NAME` holt zurück; gelöscht wird nie.
5. Windows UIA: offen.

## G12 Abläufe
1. `ablauf neu DATEI.json` zweimal: beide Versionen bleiben.
2. `ablauf start ID --modi=shadow`: es passiert nichts. `--modi=daniel_gate`: es fragt dich, Nein = nichts.
3. Pause, Weiter, `checkpoint`, `zweig`: der alte Lauf bleibt.
4. Regiespruch „Pause“ pausiert wirklich.

## G13 Kapseln und Zeitlinie
1. `kapsel moment --art=agent "Test"`, `kapsel zeige K`: „unverändert“ ist True.
2. `kapsel ebene K kommentar "Beinahe"`: Original bleibt unverändert.
3. `kapsel zeitlinie`, dann mit einer Zeit: im Terminal kommt nichts an.
4. Mit gebundenem Ziel enthält die Kapsel Bindung, Anker und WorldDOM-Knoten. Fehlt etwas, steht der Grund in den Lücken.

## G14 Hauhaucs und Mischpult
1. `chat "Hallo"`, `chat "Und noch was"`: das Modell antwortet und kennt den ersten Austausch.
2. `pult zeige`, `pult halbieren`, `pult leeren`, `pult zurueck`: du siehst genau, was ans Modell geht.
3. `beobachtung start Codex`, Nachrichten schicken, `beobachtung status`: „aufgezeichnet“ steigt, „verarbeitet“ bleibt 0.
4. `beobachtung jetzt "Fasse zusammen"`: Ausarbeitung mit Quellen wie [e-12].
5. `beobachtung stop`, dann `jetzt`: „gestoppt“. Der Chat geht weiter.
6. Gegen den echten Chat-Server 11435: bisher nicht gelaufen, offen.

## Offen
Windows nativ (Hände, Fokus, Fensterbild, UIA, Controller-Treiber), Claude hinter dem Vertrauensdialog, Kimi und GLM, Erkennung physischer Controller, ChatGPT und Mikrofon (zurückgestellt), Wayland, Windows.Graphics.Capture, Chat mit den Entitäten, Zensi und Handy (erst Entscheidung zum Speicherort).
