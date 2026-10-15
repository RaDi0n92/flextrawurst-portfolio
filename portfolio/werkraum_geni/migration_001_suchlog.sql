-- GENI-Suchlog, Migration 001 -- 2026-08-03
--
-- Daniel, 2026-08-03, woertlich:
--   "ich will ab sofort chronologisch natürlih wissen und loggen lso dokun´mentiert haben wer wann
--    was mit welchen zuständen in einer su´che angefragt hat welche zum lesen alle vorgeschlage
--    wurden und welche gewählt wurdenu und wenn es das noch nicht gibt auch optional mit einem
--    grund"
--
-- Warum drei Tabellen und keine mit UPDATE:
--   "vorgeschlagen" und "gewaehlt" passieren zu verschiedenen Zeitpunkten. Man koennte in der
--   Trefferzeile ein Flag nachtragen -- das waere ein UPDATE. Grundgesetz 5 sagt: Ereignisse sind
--   append-only. Also ist die Wahl ein eigenes Ereignis, keine Aenderung am alten.
--
-- Wofuer das Log da ist:
--   tiefe und gewicht werden daraus ABGELEITET, statt eigenstaendig gefuehrt zu werden. Die Zahl
--   ist dann eine Sicht auf Ereignisse, keine zweite Wahrheit daneben. Ausserdem ist erst mit
--   diesem Log messbar, welche Knoten in KEINER Suche je vorkamen -- die Grundlage fuer den
--   eigenen Takt, der den Wesen genau diese Uebersehenen anbietet.
--
-- Bestehendes wird nicht angefasst: knoten.db, kanten/ und der Selbst-Index bleiben, wie sie sind.

BEGIN;

-- Eine Suchanfrage. Ein Zeile pro Aufruf von selbst_suche.suchen().
CREATE TABLE IF NOT EXISTS suche (
    id          BIGSERIAL PRIMARY KEY,
    zeit        TIMESTAMPTZ  NOT NULL DEFAULT now(),
    sucher      TEXT         NOT NULL,          -- 'geni', 'F3INSCHM3CK3R', 'claude', ...
    sucher_art  TEXT         NOT NULL,          -- 'geni' | 'codewesen' | 'ai_strom' | 'mensch'
    anlass      TEXT,                           -- 'dokumentation', 'dialog', 'takt', ...
    frage       TEXT         NOT NULL,
    zustand     JSONB        NOT NULL DEFAULT '{}',  -- "mit welchen zuständen" -- was war beim
                                                     -- Sucher los: Takt, Stimmung, Energie, Ziel
    meta        JSONB        NOT NULL DEFAULT '{}'   -- Grundgesetz 2: immer erweiterbar
);

CREATE INDEX IF NOT EXISTS idx_suche_zeit   ON suche (zeit DESC);
CREATE INDEX IF NOT EXISTS idx_suche_sucher ON suche (sucher, zeit DESC);

-- Was diese Suche zurueckgab -- ALLE Vorschlaege, nicht nur die spaeter gelesenen.
-- eintrag_id ist die id aus dem Selbst-Index ('knoten:123', 'doku:kimi', 'splitter:7', ...),
-- bewusst TEXT und ohne Fremdschluessel: der Index umfasst mehrere Quellsysteme.
CREATE TABLE IF NOT EXISTS suche_treffer (
    id          BIGSERIAL PRIMARY KEY,
    suche_id    BIGINT       NOT NULL REFERENCES suche(id) ON DELETE RESTRICT,
    rang        INTEGER      NOT NULL,          -- 1 = oberster Treffer
    eintrag_id  TEXT         NOT NULL,
    quelle      TEXT,
    art         TEXT,
    ort         TEXT,
    score       DOUBLE PRECISION,               -- RRF-Punktzahl
    wege        TEXT,                           -- 'stichwort', 'semantisch', beides
    meta        JSONB        NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_treffer_suche   ON suche_treffer (suche_id, rang);
-- Der wichtigste Index des ganzen Logs: ueber ihn ist beantwortbar, was NIE erschienen ist.
CREATE INDEX IF NOT EXISTS idx_treffer_eintrag ON suche_treffer (eintrag_id);

-- Was davon tatsaechlich gelesen, zitiert oder weitergedacht wurde.
-- Getrennt von suche_treffer, weil es spaeter passiert und weil der Unterschied zwischen
-- "erschienen" und "gewaehlt" genau die Abstufung ist, die Daniel verlangt:
--   "allein wenn ein knoten in der suche miterscheint dass er auch tiefe und gewicht erhält
--    aber wenig nicht wie die die dann zum lesengewählt werden"
CREATE TABLE IF NOT EXISTS suche_wahl (
    id          BIGSERIAL PRIMARY KEY,
    zeit        TIMESTAMPTZ  NOT NULL DEFAULT now(),
    suche_id    BIGINT       NOT NULL REFERENCES suche(id) ON DELETE RESTRICT,
    eintrag_id  TEXT         NOT NULL,
    art         TEXT         NOT NULL DEFAULT 'gelesen',  -- 'gelesen' | 'zitiert' | 'verbunden'
    grund       TEXT,                                     -- optional, Daniels "auch optional mit
                                                          -- einem grund"
    meta        JSONB        NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_wahl_suche   ON suche_wahl (suche_id);
CREATE INDEX IF NOT EXISTS idx_wahl_eintrag ON suche_wahl (eintrag_id, zeit DESC);

-- Abgeleitete Sicht: pro Eintrag, wie oft erschienen und wie oft gewaehlt, wann zuletzt.
-- Bewusst eine VIEW und keine Spalte: die Zahl ist eine Sicht auf Ereignisse, keine zweite
-- Wahrheit, die auseinanderlaufen kann.
CREATE OR REPLACE VIEW eintrag_nutzung AS
SELECT
    t.eintrag_id,
    count(*)                                   AS erschienen,
    count(DISTINCT t.suche_id)                 AS in_suchen,
    coalesce(w.gewaehlt, 0)                    AS gewaehlt,
    min(t.rang)                                AS bester_rang,
    max(s.zeit)                                AS zuletzt_erschienen,
    w.zuletzt_gewaehlt
FROM suche_treffer t
JOIN suche s ON s.id = t.suche_id
LEFT JOIN (
    SELECT eintrag_id, count(*) AS gewaehlt, max(zeit) AS zuletzt_gewaehlt
    FROM suche_wahl GROUP BY eintrag_id
) w ON w.eintrag_id = t.eintrag_id
GROUP BY t.eintrag_id, w.gewaehlt, w.zuletzt_gewaehlt;

COMMIT;
