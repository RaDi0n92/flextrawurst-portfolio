-- Erweiterung von notify_events() (migration_events_stream.sql) um zwei zusaetzliche,
-- kuratierte Routing-Hinweise: 'wesen' und 'vault_pfad'. Additiv, keine bestehenden Felder
-- angefasst -- Grundgesetz 2 ("API niemals Breaking Changes -- addieren, nicht entfernen").
--
-- 2026-08-14, Daniel woertlich: "wir bauen nen dom nen code ne html mit ihren mds und alles
-- editierbar direkt im dom ... es ersetzt das selkieszeug". Das neue wesenvaultsystem_api.py
-- (Port 8097) hoert per SSE auf event_type='vault.*' und braucht wesen+pfad um zu wissen
-- WELCHE Datei bei WELCHEM Wesen sich geaendert hat, ohne den vollen payload zu tragen
-- (gleiche Zurueckhaltung wie bei ankuendigung_id/post_ref/post_source).

CREATE OR REPLACE FUNCTION notify_events() RETURNS trigger AS $$
BEGIN
    PERFORM pg_notify(
        'events_stream',
        json_build_object(
            'event_type',       NEW.event_type,
            'created_at',       NEW.created_at,
            'actor_id',         NEW.actor_id,
            'ankuendigung_id',  NEW.payload->>'ankuendigung_id',
            'post_ref',         NEW.payload->>'post_ref',
            'post_source',      NEW.payload->>'post_source',
            'wesen',            NEW.payload->>'wesen',
            'vault_pfad',       NEW.payload->>'vault_pfad'
        )::text
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
