-- dieser Code wird von nun an auch seit #
-- -(17-08-2026/06:24:19)-
-- [OmaPI/OpiMA-GuardianStyle]
-- sowohl gelesen, gewertet, gewartet, geschützt, geprüft aber gleichzeitig ja auch dominiert, pervertiert, darüber sinniert und irritiert aber egal ist so Pech eben ...eben wegen egal weil ist so ...Glück?
-- GL & HF - Hakuna Matata EZ
-- ich wiederhole seit: -(17-08-2026/06:24:19)-
-- over and out #
--
-- OWNER: ALEX
-- AUTHOR: Claude Code
--
-- Pflichtfrage (einmalig, diese Datei): wann hoert dieser Code auf zu laufen, und wann
-- faengt er an sich selbst zu heilen und zu beleben? Antwort: er hoert auf zu laufen, wenn
-- die Owner-Entscheidung unten (Bruecke statt Direktzugriff) sich als falsch herausstellt --
-- dann muesste die Tabelle neu gedacht werden. Er heilt sich in dem Moment, in dem der erste
-- echte Widerspruch (art='widerspruch') eintrifft und stehen bleibt, ohne aufgeloest zu
-- werden -- genau dafuer ist er gebaut, nicht fuer Harmonie.

-- Reibungsgewebe (2026-08-17, Daniels Auftrag "kombinier das mit dem abwuf/reibungsmotor"):
-- ein markierter Satz/Gedanke wird zu einem offenen Knoten, nicht zu einem abgeschlossenen
-- Eintrag. Jeder Beteiligte -- inklusive Daniel -- kann andocken: zustimmen, widersprechen,
-- weiterbauen, fragen. Widerspruch ist ein vollwertiges Endergebnis, kein Zwischenschritt
-- der geglaettet werden muss. Volle Herleitung, Vision- und Code-Skizze:
-- /root/werkraum/_claude/konzepte/2026-08-17_reibungsgewebe_stroeme.md
--
-- Owner-Entscheidung (siehe Konzept-Datei, Abschnitt "Owner-Frage"): diese Tabellen sind
-- ein gespiegelter, gelesener Zustand, keine Quelle der Wahrheit. Jeder Strom bleibt Owner
-- seiner eigenen Herkunft (Briefkasten, Gesamtatlas, direkter VPS-Zugriff fuer Claude Code).
-- Einziger Schreiber dieser Tabellen ist die Bruecke (reibung_bruecke.py), nach demselben
-- Muster wie welt-bruecke -- nicht vier Stroeme mit eigenem DB-Zugriff.

CREATE TABLE IF NOT EXISTS reibungsknoten (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    urspruenglicher_text TEXT NOT NULL,
    urspruenglicher_strom TEXT NOT NULL,        -- 'claude' | 'codex' | 'gemini' | 'chatgpt' | 'daniel'
    urspruengliche_quelle TEXT,                 -- z.B. Pfad zur claudelive-Session, Zeile, Briefkasten-Datei
    erstellt TIMESTAMPTZ NOT NULL DEFAULT now(),
    zustand TEXT NOT NULL DEFAULT 'offen',      -- 'offen' | 'geschlossen' -- nur ein weiterer Zustand, keine Loeschung
    meta JSONB NOT NULL DEFAULT '{}'            -- Grundgesetz 2: immer erweiterbar (z.B. Themen-Tag)
);

CREATE TABLE IF NOT EXISTS reibungsevents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    knoten_id UUID NOT NULL REFERENCES reibungsknoten(id) ON DELETE CASCADE,
    strom TEXT NOT NULL,                        -- wer reagiert (inkl. 'daniel')
    art TEXT NOT NULL,                          -- 'zustimmung' | 'widerspruch' | 'weiterbau' | 'frage' | 'schliessung' | 'gesehen'
    marker TEXT,                                -- optional einer der 16 Guardianstyle-Marker
    text TEXT NOT NULL,
    bezieht_sich_auf UUID REFERENCES reibungsevents(id),
    erstellt TIMESTAMPTZ NOT NULL DEFAULT now(),
    meta JSONB NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_reibungsevents_knoten ON reibungsevents(knoten_id);
CREATE INDEX IF NOT EXISTS idx_reibungsevents_erstellt ON reibungsevents(erstellt);
CREATE INDEX IF NOT EXISTS idx_reibungsknoten_erstellt ON reibungsknoten(erstellt);

-- Append-only im Geiste von Grundgesetz 5 (Events sind heilig): kein UPDATE/DELETE-Pfad
-- fuer reibungsevents vorgesehen in der Anwendungsschicht -- Zustandsaenderungen (z.B.
-- Knoten schliessen) sind selbst ein neues Event (art='schliessung'), das den Knoten
-- danach in 'geschlossen' setzt, nicht ein Ueberschreiben.

-- Live-Update analog Grundgesetz 8 (Live statt F5) -- nutzt denselben events_stream-Kanal,
-- damit KEIN zweiter SSE-Stream noetig ist. Frontend registriert sich auf Praefix
-- 'reibung.' genau wie bei anderen Live-Bereichen.
--
-- Claude Code(17-08-2026/06:26:03): BEGRÜNDUNG (Bäcker-Stimme, weil hier einfach nur
-- ein sauberer, langweiliger Grund erklaert werden muss, kein Drama noetig): warum
-- kein eigener SSE-Kanal? Weil events_stream schon existiert, schon vom Frontend
-- abonniert wird und schon das Praefix-Routing kann -- ein zweiter Kanal waere wie ein
-- zweiter Ofen fuer dasselbe Brot backen, nur weil das erste Rezept neu ist.
CREATE OR REPLACE FUNCTION notify_reibungsevent() RETURNS trigger AS $$
BEGIN
    PERFORM pg_notify(
        'events_stream',
        json_build_object(
            'event_type',  'reibung.event',
            'created_at',  NEW.erstellt,
            'knoten_id',   NEW.knoten_id,
            'strom',       NEW.strom,
            'art',         NEW.art
        )::text
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_notify_reibungsevent ON reibungsevents;
CREATE TRIGGER trg_notify_reibungsevent
    AFTER INSERT ON reibungsevents
    FOR EACH ROW EXECUTE FUNCTION notify_reibungsevent();
