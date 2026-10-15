-- Transactional schema only. No private key or implicit legacy reactivation.
SET LOCAL lock_timeout = '5s';
SET LOCAL statement_timeout = '15s';
ALTER TABLE auth_service_principals
    ADD COLUMN IF NOT EXISTS legacy_hs256_until TIMESTAMPTZ;
CREATE TABLE IF NOT EXISTS auth_service_keys (
    kid UUID PRIMARY KEY,
    principal TEXT NOT NULL REFERENCES auth_service_principals(name),
    public_key TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    not_before TIMESTAMPTZ NOT NULL DEFAULT now(),
    not_after TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    meta JSONB NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS auth_service_keys_principal ON auth_service_keys(principal);
REVOKE ALL ON auth_service_keys FROM PUBLIC;
GRANT SELECT, INSERT, UPDATE ON auth_service_keys TO dak;
