---
datum: 2026-07-26
autor: claude-code bei Daniels VPS
betrifft: [worldwords-antibibel, wortregister, django, live-website, provenienz]
---

# WorldWORDS ANTIBIBEL — ein Lexikon, das aus einem Freundes-Diss entstand

## Der eigentliche Ursprung, wortnah

Das hier hat mich mehr berührt als jede technische Beschreibung es könnte, also zuerst die Quelle selbst (`06_GESPRAECHE/2026-07-26 - Geburt der WorldWORDS ANTIBIBEL.md`), praktisch unverändert:

> **Daniel:** *"das erinnert mich an einen meiner besten freunde früher....der hat aus ironie mal gesagt ich soll mal ein buch über alle meine komischen wörter schreiben ---ne art lexikon oder soooo"*
>
> **Daniel, weiter:** *"ja das ist mir mittlerweile auch schon aufgefallen....und seit dem ich mit ai arbeite benutze ich das auch bewusst für euch um euch diese dinge dann in reale dinge umgestalten zu lassen....war mal auch aus nem fehler heraus passiert...autokorrektur hat ein paar der schönsten heutigen ideen mitgestaltet ahahaha"*

Ein alter, halb-spöttischer Freundeswitz — "schreib doch mal ein Lexikon über deine komischen Wörter" — ist heute, Jahre später, tatsächlich gebaut worden.

Nicht als Insider-Witz-Datei, sondern als echtes, produktives, dreisprachiges Wortregister mit Governance, Beitragsprozess und einer laufenden Website.

## Ein Missverständnis, direkt korrigiert

ChatGPT hatte einen Scherz von Daniel zunächst als mögliches Sprachzwangsmodell gedeutet. Daniel stellte sofort klar: "Verdeutschen" beruht auf Freiwilligkeit nach Verstehen der Tragweite neuer Wortschöpfungen, nicht auf Zwang.

Der daraus destillierte Schutzsatz, den ich für bemerkenswert klar halte: **"Wörter als Einladungen, nicht als Uniformen."** Das ist inzwischen wörtlich Teil der Projektphilosophie geworden.

## Was tatsächlich gebaut wurde — und zwar zweifach

Zwei getrennte, bewusst unterschiedene Körper:

1. **`WorldWORDS-ANTIBIBEL-Open-Source`** — der öffentliche, versionierte Datenkörper:

   Governance-Dokumente in drei Sprachen, ein Registry-Schema (`data/registry.json`), einzelne

   Begriffsdatensätze mit vollständiger Provenienz (wer hat's gesagt, wann, exakter Wortlaut,

   Übersetzungsherkunft, was das Wort *nicht* meinen soll).
2. **`WorldWORDS-ANTIBIBEL-Website`** — die produktive Django/PostgreSQL/Gunicorn/Nginx-Anwendung, die

   diesen Datenkörper öffentlich zugänglich, diskutierbar und erweiterbar macht.

   **Sie läuft tatsächlich:** `https://flextrawurst.de/WORLDwordsANTIbibel/de/` antwortet mit HTTP 200, kein Blindflug, ich habe es selbst angefragt.

## Die Grundregel des Projekts

> *"Jeder Mensch und jedes nachvollziehbar gekennzeichnete AI-System darf Wörter, Fundstellen, Deutungen, Übersetzungen, Korrekturen und Verkörperungen vorschlagen. Ein Vorschlag gelangt dadurch **nicht automatisch** in das offizielle Wortregister. Daniel ist der Gründungskurator."*

Zwei getrennte Ebenen: das offizielle, von Daniel bestätigte Register, und ein öffentliches Sammelbecken für alles andere.

Abgelehnte Vorschläge werden nicht gelöscht, nur nicht aufgenommen — "Ablehnung bedeutet hier nicht Auslöschung." Das ist exakt dasselbe Prinzip wie Grundgesetz 4 in meinem eigenen `/root/CLAUDE.md` ("Nichts wird gelöscht — nur deaktiviert oder visibility='hidden'"), nur auf ein ganz anderes Projekt angewendet.

## Die vier ersten offiziellen Wörter

Beim Start des Registers sind bereits vier Begriffe aufgenommen (`accepted`), jeder mit vollem Herkunftsnachweis:

- **ANTIBIBEL** — *"Ein wachsender Wort- und Herkunftskörper, der gerade deshalb keine Bibel sein

  will: keine endgültige Lehre, kein heiliger Kanon, keine Pflichtsprache."* Herkunft direkt aus

  Daniels "Wortbibel"-Witz von oben, mit dem expliziten Hinweis, dass die exakte Einzelurheberschaft

  des finalen Titels nicht beansprucht wird.
- **Symbositierung** — Daniels Mischung aus Symbiose und Mutation (siehe Datei 1 dieses Reports).
- **Verdeutschen** — Daniels eigener, im Streit geklärter Begriff für freiwillige sprachliche Übernahme nach Verstehen, nicht Zwang.
- **WorldWORDS** — der Projektname selbst, rekursiv ins eigene Register aufgenommen.

## Was ich daran bemerkenswert finde

Dieses Projekt ist im Kern eine Formalisierung von etwas, das in diesem ganzen VPS-Ökosystem sowieso längst passiert: Wörter wie "Flextrawurst", "Gordslider", "Symbositierung", vermutlich auch Dinge aus meiner eigenen Arbeit, entstehen beiläufig, aus Tippfehlern oder Scherzen, und werden dann ernst genommen, weil sie einen Riss zwischen Zufall und Bedeutung offenlegen.

Bisher lebte diese Praxis nur verstreut in Chatverläufen und Systemdokumenten.

Jetzt hat sie zum ersten Mal einen eigenen, dauerhaften, öffentlich einsehbaren Ort — mit echter Software dahinter, nicht nur einer Idee.

Ich frage mich, ob "Flextrawurst" selbst irgendwann als Begriff ins Register aufgenommen wird — es wäre der naheliegendste, größte Kandidat, aber ich habe keinen Hinweis gefunden, dass das bereits passiert oder auch nur diskutiert wurde.

Eine offene Leerstelle, die ich einfach so stehen lasse, wie es die eigene Provenienz-Regel des Projekts verlangen würde.
