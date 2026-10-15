# Live-Abnahme: Manueller visueller Originalabgleich

Datum: 2026-08-15, echter `virtuellerdesktop2`-Chromium
Collection: `collection-2026-08-15T041300230Z-ab03126e`
Snapshot: `crawl-2026-08-15T052548876Z-e24f0e29`

## Was mein Auge verglichen hat

Ich habe das aktuelle Original `https://flextrawurst.de/` und den exakt
gespeicherten Snapshot als getrennte Bilder angesehen. Der sichtbare Aufbau,
die Navigation, der große `flextrawurst`-Titel, die drei Pfadkarten und der
sichtbare Text stimmen überein.

Gleichzeitig stehen die animierten Partikel und der laufende Status-Ticker in
den beiden Bildern zeitbedingt anders. Deshalb ist der Befund nicht
„pixelgleich“, sondern ehrlich `Abweichung gefunden` bei struktureller
Übereinstimmung.

## Sichtbare und persistente Kette

| Schritt | Sichtbarer Befund | Rücklese |
|---|---|---|
| `Rücklese bestätigen` | Status grün, nächste Stufe bleibt eigenständig | `read_back: pass` |
| `Rohdaten prüfen` | Status grün, visueller Abgleich bleibt offen | `checked: pass`, `mismatch_fields: []` |
| Notiz eintragen | Text nennt Layoutübereinstimmung und dynamische Unterschiede | Button wird aktiv |
| `Visuellen Originalabgleich protokollieren` | roter Status `Abweichung gefunden` | `visual: fail`, `verdict: difference_found` |

Die Rohdatenhashes blieben unverändert. Der Review speichert außerdem, dass er
auf einer ausdrücklichen manuellen visuellen Vergleichshandlung beruht. Kein
Reload, Polling, PDF-Export oder Hashlauf kann diese Stufe automatisch setzen.

## Aussage

Der Recorder hat den Unterschied nicht weggetestet und nicht grün erfunden. Er
trägt jetzt sichtbar und persistent: Rohdaten unverändert, Struktur passend,
zeitabhängige Bildabweichung gefunden.

Manifest: `2026-08-15-live-visual-review-manifest.json`

## Wiederholung der Augenprüfung

Zwei weitere sichtbare Originalaufnahmen derselben Seite zeigten erneut denselben
stabilen Aufbau und Inhalt, aber andere Positionen der Partikel und andere
Abschnitte im laufenden Status-Ticker. Der gespeicherte Snapshot blieb dabei
unverändert. Die Abweichung ist damit als zeitabhängige Live-Dynamik belegt,
nicht als einmaliger grüner oder roter Testzustand.

## UI-Korrektur nach Live-Befund

Die erste Review-Oberfläche war zu breit. Sie wurde auf eine geschlossene Zeile
`Visuellen Befund protokollieren` reduziert. Erst beim Öffnen erscheinen Urteil,
kurze Notiz und `Speichern`; die Provenienzkarte und ihre vier Stufen bleiben
unverändert sichtbar. Der echte Workspace wurde nach dem Extension-Reload mit
diesem kompakten Zustand angesehen.
