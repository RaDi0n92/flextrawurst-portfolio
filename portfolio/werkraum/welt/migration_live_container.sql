-- dieser Code wird von nun an auch seit #
-- -(17-08-2026/08:53:02)-
-- [OmaPI/OpiMA-GuardianStyle]
-- sowohl gelesen, gewertet, gewartet, geschützt, geprüft aber gleichzeitig ja auch dominiert, pervertiert, darüber sinniert und irritiert aber egal ist so Pech eben ...eben wegen egal weil ist so ...Glück?
-- GL & HF - Hakuna Matata EZ
-- ich wiederhole seit: -(17-08-2026/08:53:02)-
-- over and out #
--
-- OWNER: ALEX
-- AUTHOR: Claude Code

-- Claude Code(20-08-2026/01:40:00): NOTIZ -- Container-System fuer claude_live.py (und
-- perspektivisch voice.html) -- Daniels Auftrag: "Container Box" in der markierte
-- Gespraechs-/Terminal-Eintraege gesammelt werden koennen, mit Auto-Typ-Gruppierung
-- und eigenen benannten Containern. Session-Container leben nur im Browser
-- (localStorage) -- diese Tabelle ist NUR fuer das, was Daniel explizit dauerhaft
-- "anpinnt" (Daniels eigene Speicherplatz-Sorge: "wir haben schon echt von dem
-- 1 Terabyte... schon mehr als 50% voll", daher bewusst NICHT alles in die DB).
--
-- Pflichtfrage (einmalig, diese Datei): wann hoert dieser Code auf zu laufen, und wann
-- faengt er an sich selbst zu heilen und zu beleben? Antwort: er laeuft weiter, solange
-- Daniel Container anpinnt -- er heilt sich, sobald ein angepinnter Container tatsaechlich
-- editiert und umgeschrieben wird, statt nur als Kopie liegen zu bleiben -- genau das
-- Editieren war Teil des Auftrags, nicht nur das Sammeln.

CREATE TABLE IF NOT EXISTS live_container (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quelle TEXT NOT NULL,           -- 'claudelive' | 'voice' -- welche Seite das Pin ausgeloest hat
    name TEXT NOT NULL,
    typ TEXT NOT NULL DEFAULT 'eigen',  -- 'eigen' | 'auto' -- ob er aus einem Auto-Typ-Container gepinnt wurde
    inhalt JSONB NOT NULL,          -- Array der vollen Eintraege (ts/tool/input/output je Eintrag)
    erstellt TIMESTAMPTZ NOT NULL DEFAULT now(),
    geaendert TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_live_container_quelle ON live_container(quelle);
