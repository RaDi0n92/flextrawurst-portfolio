-- Welt-API runtime role migration (2026-09-18)
-- Run as a database administrator against flextrawurst.
-- The API role is intentionally not allowed to create schema objects.

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'flex_api') THEN
        CREATE ROLE flex_api LOGIN;
    END IF;
END
$$;

ALTER ROLE flex_api
    WITH LOGIN
    NOSUPERUSER
    NOCREATEDB
    NOCREATEROLE
    NOINHERIT
    NOREPLICATION
    NOBYPASSRLS
    CONNECTION LIMIT 50;

GRANT CONNECT ON DATABASE flextrawurst TO flex_api;
GRANT USAGE ON SCHEMA public TO flex_api;
REVOKE CREATE ON SCHEMA public FROM flex_api;

-- This table used to be created on the first request. It is deployment state.
CREATE TABLE IF NOT EXISTS public.mw_feed_markierungen (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    item_id TEXT NOT NULL,
    item_type TEXT NOT NULL DEFAULT 'post',
    markierung TEXT NOT NULL DEFAULT 'irrelevant',
    markiert_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, item_id)
);

-- The group tables are currently present in the live database. Keep the
-- runtime verifier in groups_api.py fail-closed if a future deployment omits
-- one of them; schema creation stays an administrator/migration operation.
DO $$
DECLARE
    table_name text;
BEGIN
    FOREACH table_name IN ARRAY ARRAY[
        'group_topics', 'group_posts', 'group_polls',
        'group_poll_votes', 'group_chat_messages'
    ] LOOP
        IF to_regclass('public.' || table_name) IS NULL THEN
            RAISE EXCEPTION 'required API table public.% is missing', table_name;
        END IF;
    END LOOP;
END
$$;

-- Remove any grants a previous trial may have left behind, then expose the
-- read surface explicitly. Future tables require a new reviewed migration.
REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM flex_api;
REVOKE ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public FROM flex_api;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO flex_api;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO flex_api;

-- Writes used by the current Welt-API import graph. events is intentionally
-- absent from UPDATE/DELETE: it remains append-only.
GRANT INSERT, UPDATE, DELETE ON TABLE
    ankuendigungen,
    ankuendigungen_kommentare,
    benachrichtigungen,
    beobachtungs_sitzung,
    bild_moderation,
    cyberlinge,
    entity_activity,
    entity_denkstream,
    entity_profiles,
    entity_states,
    entity_thinking_log,
    entity_slots,
    entity_wuensche,
    erlebnis_reaktionen,
    follows,
    ftw_posts,
    gedankenblasen,
    gedankenwelt_eintraege,
    groups,
    group_creation_policy,
    group_memberships,
    group_material_links,
    group_topics,
    group_posts,
    group_polls,
    group_poll_votes,
    group_chat_messages,
    human_material_sources,
    human_material_to_splitter,
    human_profiles,
    human_users,
    mw_feed_markierungen,
    mw_kalender,
    mw_notizen,
    mw_tagebuch,
    mw_traumtagebuch,
    nachrichten,
    nutzer_sichtbarkeit,
    post_reads,
    post_relationen,
    post_spuren,
    raeume,
    resonanz_emoji_counts,
    resonanzen,
    schatten_antworten,
    schattenkommentare,
    schlafbriefe,
    sleep_phases,
    splitter,
    splitter_aufnahmen,
    spuren,
    supporter_bewerbungen,
    system_flags,
    thema_cluster_vorschlaege,
    themen,
    unterthemen,
    user_modules,
    verweilen,
    wesen_entwicklung,
    wesen_fuersorge,
    wesen_gedanken,
    widmungen,
    zitate
TO flex_api;

GRANT INSERT ON TABLE events TO flex_api;
GRANT INSERT ON TABLE rag_retrieval_runs, rag_retrieval_results TO flex_api;

COMMENT ON ROLE flex_api IS
    'Non-privileged runtime identity for Welt-API; schema changes require migration';
