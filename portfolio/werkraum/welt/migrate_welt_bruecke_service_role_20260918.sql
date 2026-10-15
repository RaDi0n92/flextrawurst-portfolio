-- Reproducible DB boundary for welt-bruecke.service.
-- Run as a PostgreSQL administrator while connected to flextrawurst.

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'flex_bridge') THEN
        CREATE ROLE flex_bridge LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE
            NOINHERIT NOREPLICATION NOBYPASSRLS;
    ELSE
        ALTER ROLE flex_bridge LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE
            NOINHERIT NOREPLICATION NOBYPASSRLS;
    END IF;
END
$$;

GRANT CONNECT ON DATABASE flextrawurst TO flex_bridge;
GRANT USAGE ON SCHEMA public TO flex_bridge;

REVOKE ALL PRIVILEGES ON public.entity_states, public.events FROM flex_bridge;
GRANT SELECT ON public.entity_states TO flex_bridge;
GRANT INSERT (
    entity_id, stimmung, fokus, version, core, tendencies,
    relationships, symbolic_image_id, last_reflection_time,
    raw_model, visibility, updated_at
) ON public.entity_states TO flex_bridge;
GRANT UPDATE (
    stimmung, fokus, version, core, tendencies, relationships,
    symbolic_image_id, last_reflection_time, raw_model,
    visibility, updated_at
) ON public.entity_states TO flex_bridge;
GRANT INSERT (
    event_type, actor_type, actor_id, payload,
    origin_type, visibility_layer
) ON public.events TO flex_bridge;
