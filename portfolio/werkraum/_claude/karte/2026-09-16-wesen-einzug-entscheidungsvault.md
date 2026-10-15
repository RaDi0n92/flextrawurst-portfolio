# Wesen-Einzug-Entscheidungsvault

Angelegt 2026-09-16, auf Daniels Auftrag im Gespräch über die Einzug-Erinnerungsfrage.
Daniel hat jedem Wesen bei seiner Entstehung versprochen, es dürfe beim Einzug selbst
wählen: Erinnerung behalten oder neu anfangen. Die Suche nach einem fairen
Realisierungsweg führte zu einer Kombination — kollektive Debatte im Flarum (bleibt
Daniels eigener Post), individuelle stille Notiz pro Wesen in einem neuen, sauberen
Vault, damit keiner sich nur an der Mehrheit orientiert.

## Wo

`/root/werkraum/wesen_einzug_entscheidung/` — sieben Unterordner, ein Wesen pro
Ordner (Namen aus `obsidian_vault_agent.py::CONTAINER_NAMES`). `_ZUSTAND.md` im
Wurzelordner hält den aktuellen Stand fest: bereit, nicht live.

Schreibzugriff: `welt/wesen_einzug_vault_agent.py` — eigenständiges, kleines Modul,
reine Plattenoperation (schreibe_datei/lese_datei/liste_dateien), bewusst getrennt
vom bestehenden `wesenvaultsystem_api.py` (Port 8097), das den bestehenden
`wesen_vaults/`-Ordner bedient.

## Warum ein eigener Vault statt den bestehenden mitzunutzen

Zwei Gründe, beide von Daniel benannt:

1. Saubere Trennung — die Einzug-Frage soll nicht mit der sonstigen Vault-Arbeit der
   Wesen vermischt werden.
2. Der bestehende Vault sendet Live-Events (Grundgesetz 8) an eine öffentliche Seite —
   wenn die anderen Wesen live sehen könnten, wer gerade zur Einzug-Frage schreibt,
   wäre genau der Anker-Effekt wieder da, den die Kombination aus Debatte+Einzelentscheidung
   eigentlich vermeiden soll. Der neue Vault hat deshalb bewusst keine Live-Übertragung.

## Was noch offen ist

- Ob ein Wesen hier autonom über sein eigenes LLM schreiben soll (wie
  `browser_agent.py`'s `obsidian_schreiben:`-Marker das für den alten Vault tut) oder
  ob eine Person für/mit dem Wesen schreibt — beim alten Vault ist real beides im
  Einsatz, hier noch nicht entschieden.
- Ob überhaupt ein Web-Editor gebraucht wird oder die reine Dateiablage reicht.
- Startschuss liegt bei Daniel: erst der Flarum-Post, dann geht die Frage live.

## Randfund

`obsidian_vault_agent.py`s Docker/Selkies/Port/Passwort-Maschinerie (CONTAINER_NAMES,
VAULT_PORTS, VAULT_EXTERN_PORTS, ENV_PASSWORT_SUFFIX) ist Altlast aus der Phase-1/2-
Bauweise (Playwright+xdotool durch einen Video-Stream) — seit Phase 3 (2026-08-14)
läuft das eigentliche Schreiben/Lesen als reine Plattenoperation, die
Docker-Container mounten nur noch denselben Ordner, werden vom Code nicht mehr
angesprochen. Für den neuen Vault war deshalb keine neue Container-Infrastruktur
nötig — nur der Plattenoperation-Teil, den Phase 3 ohnehin schon als das Wesentliche
identifiziert hatte.
