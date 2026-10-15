-- Run transactionally before loading the new verifier. Re-running never
-- reactivates revoked services or overwrites an administrator's policy.
SET LOCAL lock_timeout = '5s';
SET LOCAL statement_timeout = '15s';
CREATE TABLE IF NOT EXISTS auth_service_principals (
    name TEXT PRIMARY KEY,
    is_active BOOLEAN NOT NULL DEFAULT false,
    grants JSONB NOT NULL DEFAULT '{}' CHECK (jsonb_typeof(grants) = 'object'),
    meta JSONB NOT NULL DEFAULT '{}',
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
REVOKE ALL ON auth_service_principals FROM PUBLIC;
GRANT SELECT, INSERT, UPDATE ON auth_service_principals TO dak;
CREATE INDEX IF NOT EXISTS auth_service_principals_grants_gin
    ON auth_service_principals USING gin (grants);

WITH initial(name, origins, entities) AS (VALUES
 ('weltfutter', '["welt_extern"]'::jsonb, '[null]'::jsonb),
 ('flarum-archiv-sampler', '["flarum_archiv"]'::jsonb, '[null]'::jsonb),
 ('codex-abwurf', '["codex_abwurf","codex_spiegel"]'::jsonb, '["codex"]'::jsonb),
 ('claude-abwurf', '["claude_abwurf","claude_spiegel"]'::jsonb, '["claude"]'::jsonb),
 ('kimi-abwurf', '["kimi_abwurf","kimi_spiegel"]'::jsonb, '["kimi"]'::jsonb),
 ('gemini-abwurf', '["gemini_abwurf","gemini_spiegel"]'::jsonb, '["gemini"]'::jsonb),
 ('dak-abwurf', '["dak_abwurf"]'::jsonb, '["dak"]'::jsonb),
 ('dakgord-abwurf', '["dakgord_abwurf"]'::jsonb, '["dakgord"]'::jsonb),
 ('wesen-vault-sampler', '["wesen_vault"]'::jsonb,
  '["Schorschel","F3INSCHM3CK3R","träumerlie","R1ZZ1","jumpa","Resonanzknoten","dak+gord-system"]'::jsonb),
 ('system-abwurf', '["innerer_abwurf"]'::jsonb,
  (SELECT coalesce(jsonb_agg(entity_id ORDER BY entity_id), '[]'::jsonb) FROM (
    SELECT entity_id FROM entity_slots
    UNION SELECT entity_id FROM splitter WHERE origin_type='innerer_abwurf' AND entity_id IS NOT NULL
  ) identities))
)
INSERT INTO auth_service_principals (name, is_active, grants, meta)
SELECT name, true, jsonb_build_object('splitter:create',
    jsonb_build_object('origin_types', origins, 'entity_ids', entities)),
    '{"migration":"20260918","source":"existing_splitter_issuers"}'::jsonb
FROM initial ON CONFLICT (name) DO NOTHING;
