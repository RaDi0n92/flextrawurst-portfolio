-- Daniel explicitly requested publication of existing anonymous material and
-- visible origin / quotability as defaults. Private unshared originals stay private.
-- Execute as postgres; backups are inaccessible to application/public roles.
\set ON_ERROR_STOP on
BEGIN;
SET LOCAL lock_timeout = '5s';
CREATE SCHEMA IF NOT EXISTS codex_security_backup;
REVOKE ALL ON SCHEMA codex_security_backup FROM PUBLIC;
CREATE TABLE IF NOT EXISTS codex_security_backup.attribution_20260917 (
    section text PRIMARY KEY,
    previous_values jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);
REVOKE ALL ON codex_security_backup.attribution_20260917 FROM PUBLIC;
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM codex_security_backup.attribution_20260917 WHERE section='completed') THEN
        RAISE NOTICE 'Already applied; no data changed.';
        RETURN;
    END IF;
    LOCK TABLE splitter, gedankenblasen, human_profiles, nutzer_sichtbarkeit,
        mw_tagebuch, mw_traumtagebuch, mw_notizen, mw_kalender, blase_verwendungen
        IN SHARE ROW EXCLUSIVE MODE;

    INSERT INTO codex_security_backup.attribution_20260917
    SELECT 'defaults', coalesce(jsonb_agg(to_jsonb(c)), '[]'::jsonb)
    FROM (SELECT table_name,column_name,column_default FROM information_schema.columns
          WHERE table_schema='public' AND column_name IN (
              'herkunft_sichtbar','zitierbar','gedankenblasen_anonym',
              'notizen_anonym','schattenkommentare_anonym','anonym')) c;

    INSERT INTO codex_security_backup.attribution_20260917
    SELECT 'splitter', coalesce(jsonb_agg(jsonb_build_object('id',id,
        'herkunft_sichtbar',herkunft_sichtbar,'status',status,'energie',energie,
        'letzter_kontakt',letzter_kontakt)), '[]'::jsonb)
    FROM splitter WHERE herkunft_sichtbar IS NOT TRUE;
    UPDATE splitter SET herkunft_sichtbar=true,
        status=CASE WHEN status='verblasst' THEN 'aktiv' ELSE status END,
        energie=CASE WHEN status='verblasst' THEN greatest(coalesce(energie,0),0.5) ELSE energie END,
        letzter_kontakt=CASE WHEN status='verblasst' THEN now() ELSE letzter_kontakt END
    WHERE herkunft_sichtbar IS NOT TRUE;

    INSERT INTO codex_security_backup.attribution_20260917
    SELECT 'profiles',coalesce(jsonb_agg(jsonb_build_object('user_id',user_id,'meta',meta)), '[]'::jsonb)
    FROM human_profiles;
    UPDATE human_profiles SET meta=coalesce(meta,'{}'::jsonb) ||
        '{"zitierbar_standard":true,"gedankenwelt_anonym":false}'::jsonb;

    INSERT INTO codex_security_backup.attribution_20260917
    SELECT 'preferences',coalesce(jsonb_agg(to_jsonb(n)), '[]'::jsonb) FROM nutzer_sichtbarkeit n;
    UPDATE nutzer_sichtbarkeit SET gedankenblasen_anonym=false,notizen_anonym=false,
        schattenkommentare_anonym=false,zitierbar=true;

    INSERT INTO codex_security_backup.attribution_20260917
    SELECT 'blases',coalesce(jsonb_agg(jsonb_build_object('id',id,'herkunft_sichtbar',herkunft_sichtbar,
        'sichtbarkeit',sichtbarkeit)), '[]'::jsonb)
    FROM gedankenblasen WHERE herkunft_sichtbar IS NOT TRUE OR sichtbarkeit='anonym';
    UPDATE gedankenblasen SET herkunft_sichtbar=true,
        sichtbarkeit=CASE WHEN sichtbarkeit='anonym' THEN 'public' ELSE sichtbarkeit END
    WHERE herkunft_sichtbar IS NOT TRUE OR sichtbarkeit='anonym';

    INSERT INTO codex_security_backup.attribution_20260917
    SELECT 'diaries',coalesce(jsonb_agg(jsonb_build_object('id',id,'zitierbar',zitierbar,'sichtbarkeit',sichtbarkeit)), '[]'::jsonb)
    FROM mw_tagebuch WHERE zitierbar IS NOT TRUE OR sichtbarkeit='anonym';
    UPDATE mw_tagebuch SET zitierbar=true, sichtbarkeit=CASE WHEN sichtbarkeit='anonym'
        AND (meta->>'deleted') IS DISTINCT FROM 'true' THEN 'public' ELSE sichtbarkeit END;
    INSERT INTO codex_security_backup.attribution_20260917
    SELECT 'dreams',coalesce(jsonb_agg(jsonb_build_object('id',id,'zitierbar',zitierbar,'sichtbarkeit',sichtbarkeit)), '[]'::jsonb)
    FROM mw_traumtagebuch WHERE zitierbar IS NOT TRUE OR sichtbarkeit='anonym';
    UPDATE mw_traumtagebuch SET zitierbar=true, sichtbarkeit=CASE WHEN sichtbarkeit='anonym'
        AND (meta->>'deleted') IS DISTINCT FROM 'true' THEN 'public' ELSE sichtbarkeit END;
    INSERT INTO codex_security_backup.attribution_20260917
    SELECT 'notes',coalesce(jsonb_agg(jsonb_build_object('id',id,'zitierbar',zitierbar,'sichtbarkeit',sichtbarkeit)), '[]'::jsonb)
    FROM mw_notizen WHERE zitierbar IS NOT TRUE OR sichtbarkeit='anonym';
    UPDATE mw_notizen SET zitierbar=true, sichtbarkeit=CASE WHEN sichtbarkeit='anonym'
        AND (meta->>'deleted') IS DISTINCT FROM 'true' THEN 'public' ELSE sichtbarkeit END;
    INSERT INTO codex_security_backup.attribution_20260917
    SELECT 'calendar',coalesce(jsonb_agg(jsonb_build_object('id',id,'sichtbarkeit',sichtbarkeit)), '[]'::jsonb)
    FROM mw_kalender WHERE sichtbarkeit='anonym' AND (meta->>'deleted') IS DISTINCT FROM 'true';
    UPDATE mw_kalender SET sichtbarkeit='public' WHERE sichtbarkeit='anonym'
        AND (meta->>'deleted') IS DISTINCT FROM 'true';

    INSERT INTO codex_security_backup.attribution_20260917
    SELECT 'uses',coalesce(jsonb_agg(jsonb_build_object('id',id,'anonym',anonym)), '[]'::jsonb)
    FROM blase_verwendungen WHERE anonym IS DISTINCT FROM false;
    UPDATE blase_verwendungen SET anonym=false WHERE anonym IS DISTINCT FROM false;

    ALTER TABLE splitter ALTER COLUMN herkunft_sichtbar SET DEFAULT true;
    ALTER TABLE gedankenblasen ALTER COLUMN herkunft_sichtbar SET DEFAULT true;
    ALTER TABLE nutzer_sichtbarkeit ALTER COLUMN gedankenblasen_anonym SET DEFAULT false,
        ALTER COLUMN notizen_anonym SET DEFAULT false,
        ALTER COLUMN schattenkommentare_anonym SET DEFAULT false,
        ALTER COLUMN zitierbar SET DEFAULT true;
    ALTER TABLE mw_tagebuch ALTER COLUMN zitierbar SET DEFAULT true;
    ALTER TABLE mw_traumtagebuch ALTER COLUMN zitierbar SET DEFAULT true;
    ALTER TABLE mw_notizen ALTER COLUMN zitierbar SET DEFAULT true;
    ALTER TABLE blase_verwendungen ALTER COLUMN anonym SET DEFAULT false;
    INSERT INTO events(event_type,actor_type,actor_id,payload,visibility_layer)
    VALUES ('system.herkunft_defaults_gesetzt','system','codex',
        '{"auftrag":"Daniel: bestehendes anonymes Material veroeffentlichen; Herkunft und Zitierbarkeit standardmaessig aktiv","migration":"attribution_20260917"}'::jsonb,'internal');
    INSERT INTO codex_security_backup.attribution_20260917 VALUES ('completed','true'::jsonb,now());
END $$;
COMMIT;
