-- Reproducible DB boundary for splitter-physik.service.
-- Run as a PostgreSQL administrator while connected to flextrawurst.

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'flex_splitter') THEN
        CREATE ROLE flex_splitter LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE
            NOINHERIT NOREPLICATION NOBYPASSRLS;
    ELSE
        ALTER ROLE flex_splitter LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE
            NOINHERIT NOREPLICATION NOBYPASSRLS;
    END IF;
END
$$;

GRANT CONNECT ON DATABASE flextrawurst TO flex_splitter;
GRANT USAGE ON SCHEMA public TO flex_splitter;

REVOKE ALL PRIVILEGES ON public.splitter, public.events,
    public.splitter_verbindungen, public.gedankenblasen,
    public.wesen_entwicklung FROM flex_splitter;

GRANT SELECT ON public.splitter, public.events, public.splitter_verbindungen,
    public.gedankenblasen, public.wesen_entwicklung TO flex_splitter;
GRANT INSERT (
    origin_type, origin_id, entity_id, human_id, herkunft_sichtbar,
    essenz, thematische_tags, materialitaet, energie,
    pos_x, pos_y, vel_x, vel_y
) ON public.splitter TO flex_splitter;
GRANT UPDATE (
    pos_x, pos_y, vel_x, vel_y, energie, status,
    verbindungen, abstossungen
) ON public.splitter TO flex_splitter;
GRANT INSERT (
    event_type, actor_type, actor_id, payload,
    origin_type, visibility_layer
) ON public.events TO flex_splitter;
GRANT UPDATE (splitter_generiert) ON public.events TO flex_splitter;
GRANT INSERT (
    splitter_a_id, splitter_b_id, verbindungstyp, staerke
) ON public.splitter_verbindungen TO flex_splitter;
GRANT UPDATE (
    verbindungstyp, staerke
) ON public.splitter_verbindungen TO flex_splitter;
GRANT UPDATE (energie, updated_at, status)
    ON public.gedankenblasen TO flex_splitter;
GRANT UPDATE (
    vernachlaessigung_stunden, fuersorge_gesamt,
    fuersorge_heute, stimmungs_drift
) ON public.wesen_entwicklung TO flex_splitter;
