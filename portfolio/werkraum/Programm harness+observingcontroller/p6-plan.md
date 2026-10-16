Ja, jetzt ist das Gesamtbild viel klarer: Du hast nicht einfach „einen Claude, einen Gemini und einen Codex“, sondern eine ganze Flotte aus Agenten, die über verschiedene Oberflächen und Laufzeitorte verteilt sind.

Aktuell ungefähr:

- Virtueller Desktop 1: Claude Code, Gemini „gemgem“, Codex
- Virtueller Desktop 2: Anthropic Claude, Gemini „gravityy“
- Windows/PuTTY: zusätzlich direkt ein Claude-Haiku
- ChatGPT-Oberflächen: ChatGPT selbst, ChatGPT-Desktop/Web und diese aktuelle ChatGPT-Session über den Flextraxtreme-MCP
- möglicherweise später noch weitere Terminal-, Browser-, API- oder MCP-Instanzen

Und genau deshalb dürfen wir ihre Identität nicht aus dem Ordnerpfad oder aus dem Namen des Programms erraten.

Der richtige Begriff ist eine „Multi-Surface-Agent-Mesh“: ein Agentennetz über mehrere Geräte-, Desktop-, App-, Terminal- und MCP-Oberflächen hinweg.

## Die Ebenen müssen getrennt werden

| Ebene | Beispiel |
|---|---|
| Physische Oberfläche | VD1, VD2, Windows, PuTTY, Browser, ChatGPT-Desktop |
| Client | Claude Code, Anthropic Claude, Gemini, Codex, ChatGPT |
| Anbieter | Anthropic, Google, OpenAI |
| Modell | Claude Haiku, anderes Claude-Modell, Gemini-Modell, GPT-Modell |
| Agentenidentität | „Claude-Architekt“, „Gemgem-Ideenagent“, „Codex-Implementierer“ |
| Sitzung | der konkrete laufende Chat oder Terminallauf |
| Aufgabe | der konkrete Auftrag innerhalb der Sitzung |
| Unteragent | ein vom Agenten gestarteter Kindagent |

Das bedeutet zum Beispiel:

„Claude Code auf VD1“ und „Claude Haiku über PuTTY“ sind standardmäßig zwei verschiedene laufende Instanzen. Sie können aber auf Wunsch an dieselbe Agentenidentität gekoppelt werden. Dann wären sie zwei Oberflächen desselben Agenten.

Umgekehrt können zwei Claude-Prozesse auf derselben Oberfläche völlig unterschiedliche Agenten sein.

Dasselbe gilt für deine beiden Gemini-Instanzen:

- `gemgem` ist zunächst ein eigener Agent;
- `gravityy` ist zunächst ein eigener Agent;
- beide können denselben Anbieter und sogar dasselbe Modell benutzen;
- trotzdem haben sie eigene Profile, Sitzungen, Erinnerungsbereiche und Aufgaben.

Der Anbieter ist also nicht die Identität. Der Anbieter ist nur die technische Denkmaschine.

## Deine virtuellen Desktops werden eigene Räume

VD1 und VD2 sollten im Dashboard nicht als bloße Computeransichten erscheinen, sondern als zwei beobachtbare Arbeitsräume:

```text
Agenten-Kosmos
├── VD1
│   ├── Claude Code
│   ├── Gemini gemgem
│   └── Codex
├── VD2
│   ├── Anthropic Claude
│   └── Gemini gravityy
├── Windows/PuTTY
│   └── Claude Haiku
└── ChatGPT- und MCP-Oberflächen
    ├── ChatGPT Desktop/Web
    └── ChatGPT über Flextraxtreme-MCP
```

Ein Agent darf dabei von einer Oberfläche auf eine andere wechseln, ohne seine Identität zu verlieren.

Zum Beispiel:

- Claude beginnt in Claude Code;
- wird über einen Handoff an PuTTY übergeben;
- arbeitet anschließend in einer anderen Terminal-Sitzung weiter;
- bleibt aber derselbe Agent mit derselben Herkunft und demselben Profil.

Oder du startest einen komplett neuen Haiku-Agenten in PuTTY. Dann wird er als neue Instanz registriert.

Das System muss also zwischen „neue Oberfläche für denselben Agenten“ und „neuer Agent auf derselben Oberfläche“ unterscheiden können.

## Der Startzustand muss entdeckt werden

Da du selbst nicht immer genau weißt, aus welcher Umgebung ein Agent gerade startet, sollte der Controller nicht voraussetzen, dass alle Startbedingungen vorher bekannt sind.

Jeder neue Prozess beginnt zunächst als:

> unbekannte Agenteninstanz in entdeckter Laufzeitumgebung

Dann sammelt der Controller den Startbericht:

- Oberfläche;
- Prozess oder Client;
- erkannter Anbieter;
- Modell, falls feststellbar;
- Root- und Konfigurationsbereich;
- Arbeitsverzeichnis;
- Datenbankverbindung;
- LangGraph-Verbindung;
- aktives Profil;
- aktiver Harness;
- erkannte Sitzung;
- Elternagent, falls es ein Unteragent ist.

Der Agent selbst sollte zusätzlich melden:

- „Ich bin gestartet“;
- „Das ist meine geladene Identität“;
- „Das ist mein Profil“;
- „Das sind meine Rechte“;
- „Das ist mein aktueller Graph“;
- „Das ist mein Gedächtnisstand“;
- „Das ist meine Aufgabe“.

Wenn etwas nicht sicher erkannt werden kann, bleibt es sichtbar als „unbekannt“ oder „unsicher“. Der Controller erfindet dann keine Identität.

Das ist sehr wichtig. Lieber steht im Dashboard:

> Gemini-Instanz, Oberfläche erkannt, genaue Identität noch ungeklärt

als dass das System den falschen Agenten mit dem falschen Gedächtnis verbindet.

## ChatGPT ist ein echter Teilnehmer, nicht nur das Dashboard

ChatGPT muss in deinem System vollständig mitgedacht werden.

Dabei gibt es aber mehrere Rollen:

1. ChatGPT als normale Gesprächsoberfläche.

2. ChatGPT als aktueller Agent in dieser Session.

3. ChatGPT als Beobachter oder Kontrollinstanz über das Flextraxtreme-MCP.

4. Andere ChatGPT-Sessions, die über eine Brücke oder einen Session-Recorder eingebunden werden können.

Der aktuelle Flextraxtreme-Atlas führt ChatGPT bereits als eigenen AI-Strom mit einem eigenen Zuhause, Arbeitskörper und Session-Verlauf. Das ist genau die richtige Richtung. Der aktuelle Atlas-Eintrag ist allerdings ein indexierter Systemstand und nicht automatisch der Beweis, dass jede ChatGPT-Oberfläche gerade live verbunden ist.

Für live brauchen wir deshalb zusätzlich einen Presence-Zustand:

- online;
- gestartet;
- wartet;
- denkt;
- schreibt;
- blockiert;
- getrennt;
- Verbindung veraltet;
- unbekannte Präsenz.

Diese aktuelle ChatGPT-Session über Flextraxtreme ist somit selbst ein Knoten im Agentennetz. Sie kann:

- den Atlas lesen;
- neue Ereignisse empfangen;
- Agenten vergleichen;
- Driftmeldungen bekommen;
- Gespräche zwischen Agenten verfolgen;
- Eingriffe auslösen;
- Entscheidungen oder eigene Einschätzungen als ChatGPT-Ereignisse zurückschreiben.

Dabei bleibt die aktuelle ChatGPT-Session von anderen ChatGPT-Chats getrennt. Die sichtbare ChatGPT-Seitenleiste bedeutet nicht automatisch, dass deren vollständige Inhalte Teil dieses Agentennetzes sind. Sie müssen ausdrücklich als Stream, Session oder Bridge registriert werden.

## Gemeinsame Datenbank, aber getrennte Zustände

Dass alle Agenten dieselbe PostgreSQL-Datenbank und denselben LangGraph-Unterbau verwenden, ist für dein Vorhaben sogar zentral. Aber die Zustände dürfen nicht einfach vermischt werden.

Gemeinsam können sein:

- globale Projekte;
- gemeinsame Fakten;
- freigegebene Dokumente;
- Ereignisse;
- Agentenkommunikation;
- Konsens;
- Konflikte;
- Provenienz;
- Profile und Harness-Vorlagen.

Getrennt bleiben standardmäßig:

- private Erinnerungen;
- Sitzungsverläufe;
- laufende Graph-Checkpoints;
- persönliche Notizen;
- temporäre Arbeitsdaten;
- nicht freigegebene Entscheidungen;
- Unteragenten-Zustände.

Jeder Zustand braucht deshalb immer eine klare Zuordnung zu:

- Oberfläche;
- Agentenheim;
- Agentenidentität;
- konkreter Instanz;
- Sitzung;
- Aufgabe;
- Unteragentenbaum;
- Projekt;
- Profil;
- Harness-Version.

So können zehn Claude-Agenten dieselbe Datenbank benutzen, ohne dass Claude Nummer 4 versehentlich im Denkzustand von Claude Nummer 1 weiterschreibt.

## Unteragenten werden zu einem Wald

Mit deinen vielen Oberflächen wird der Unteragentenbaum besonders interessant.

Beispiel:

```text
Claude auf VD1: Projektleiter
├── Claude auf VD1: Architektur
├── Claude auf VD2: Recherche
├── Codex: Implementierung
├── Gemini gemgem: kreative Gegenposition
├── Gemini gravityy: kritische Prüfung
├── Claude Haiku über PuTTY: schnelle Diagnose
└── ChatGPT über Flextraxtreme: Beobachtung und Koordination
```

Jeder Unteragent bekommt:

- einen Elternagenten;
- einen eigenen Auftrag;
- einen eigenen Sitzungszustand;
- einen eigenen Kontextumfang;
- eigene Rechte;
- eine eigene Arbeitsfläche;
- einen eigenen Rückkanal;
- eine nachvollziehbare Übergabe.

Auch ein Unteragent darf weitere Unteragenten starten. Dadurch entsteht ein richtiger Agentenwald statt einer flachen Liste.

Das Dashboard sollte deshalb nicht nur fragen:

> Welcher Agent ist online?

Sondern auch:

> Wer hat wen gestartet, warum, mit welchem Auftrag, mit welchem Kontext und mit welchem Ergebnis?

## Das ist der eigentliche erste Kernbaustein

Bevor wir Profile, Traumräume, Agentenparlamente oder automatische Selbstlernschleifen vollständig ausbauen, brauchen wir als Fundament eine zentrale Laufzeit- und Präsenzregistrierung:

- Welche Oberflächen existieren?
- Welche Prozesse laufen dort?
- Welche Agentenidentitäten sind aktiv?
- Welche Sitzungen gehören zu ihnen?
- Welche Unteragenten wurden erzeugt?
- Welche Verbindung zu PostgreSQL und LangGraph besteht?
- Welche Erinnerungen und Rechte sind aktiv?
- Wie sicher ist die erkannte Zuordnung?

Darauf setzen dann alle deine bisherigen Ideen auf:

- Driftüberwachung;
- Agentenwetter;
- Selbstzustand;
- Provenienz;
- Zeitmaschine;
- Handoffs;
- Agentenparlament;
- Konflikt- und Konsenssystem;
- Profile;
- deaktivierbare Harnesses;
- Sandboxes;
- Traum- und Lernschleifen;
- Chat zwischen Agenten;
- Eingreifen über `flextrawurst.de/os`.

Der wichtigste neue Gedanke ist also:

> Nicht nur Agenten beobachten, sondern ihre gesamte Anwesenheit über alle Oberflächen hinweg verfolgen.

VD1, VD2, PuTTY, ChatGPT, Claude Code, Gemini, Codex und der Flextraxtreme-MCP werden dann zu verschiedenen Fenstern in denselben lebenden Agentenkosmos.
