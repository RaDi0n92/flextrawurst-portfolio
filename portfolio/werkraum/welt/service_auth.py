"""Admin-managed grants for existing internal Splitter issuers; no token secrets."""
from fastapi import Header, HTTPException, Query
from pydantic import BaseModel, Field
from psycopg2.extras import Json
from uuid import UUID


class ServicePolicy(BaseModel):
    is_active: bool = True
    origin_types: list[str] = Field(default_factory=list, max_length=100)
    entity_ids: list[str | None] = Field(default_factory=list, max_length=1000)
    meta: dict = Field(default_factory=dict)


def register_service_admin_routes(app, get_conn, require_admin):
    @app.get("/admin/auth/services/{name}/keys")
    def list_keys(name: str, authorization: str | None = Header(default=None),
                  limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0)):
        require_admin(authorization)
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT kid, is_active, not_before, not_after, created_at, meta "
                            "FROM auth_service_keys WHERE principal=%s ORDER BY created_at DESC "
                            "LIMIT %s OFFSET %s", (name, limit, offset))
                return {"keys": [dict(row) for row in cur.fetchall()]}
        finally:
            conn.close()

    @app.post("/admin/auth/services/{name}/keys/{kid}/revoke")
    def revoke_key(name: str, kid: UUID, authorization: str | None = Header(default=None)):
        actor = require_admin(authorization)
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("UPDATE auth_service_keys SET is_active=false WHERE principal=%s AND kid=%s "
                            "RETURNING kid", (name, str(kid)))
                if not cur.fetchone(): raise HTTPException(404, "Schlüssel nicht gefunden")
                cur.execute("INSERT INTO events(event_type,actor_type,actor_id,payload,visibility_layer) "
                            "VALUES ('auth.service_key_revoked','human',%s,%s,'internal')",
                            (actor["user_id"], Json({"service": name, "kid": str(kid)})))
            conn.commit()
            return {"ok": True}
        finally:
            conn.close()

    @app.get("/admin/auth/services")
    def list_services(authorization: str | None = Header(default=None),
                      search: str = "", limit: int = Query(50, ge=1, le=100),
                      offset: int = Query(0, ge=0), sort: str = "name", order: str = "asc"):
        require_admin(authorization)
        if sort not in ("name", "updated_at") or order not in ("asc", "desc"):
            raise HTTPException(400, "ungültige Sortierung")
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT name, is_active, grants, meta, updated_at FROM auth_service_principals "
                    f"WHERE name ILIKE %s ORDER BY {sort} {order}, name ASC LIMIT %s OFFSET %s",
                    ("%" + search + "%", limit, offset),
                )
                return {"services": [dict(row) for row in cur.fetchall()]}
        finally:
            conn.close()

    @app.put("/admin/auth/services/{name}")
    def set_service(name: str, body: ServicePolicy, authorization: str | None = Header(default=None)):
        actor = require_admin(authorization)
        if not name or len(name) > 100 or any(c.isspace() for c in name):
            raise HTTPException(400, "ungültige Dienstidentität")
        try:
            UUID(name)
        except ValueError:
            pass
        else:
            raise HTTPException(400, "Menschen-UUID ist keine Dienstidentität")
        grants = {"splitter:create": {"origin_types": body.origin_types, "entity_ids": body.entity_ids}}
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO auth_service_principals (name, is_active, grants, meta) "
                    "VALUES (%s, %s, %s, %s) ON CONFLICT (name) DO UPDATE SET "
                    "is_active=EXCLUDED.is_active, grants=EXCLUDED.grants, "
                    "meta=auth_service_principals.meta || EXCLUDED.meta, updated_at=now()",
                    (name, body.is_active, Json(grants), Json(body.meta)),
                )
                cur.execute(
                    "INSERT INTO events (event_type, actor_type, actor_id, payload, visibility_layer) "
                    "VALUES ('auth.service_policy_changed', 'human', %s, %s, 'internal')",
                    (actor["user_id"], Json({"service": name, "is_active": body.is_active, "grants": grants})),
                )
            conn.commit()
            return {"ok": True, "name": name}
        finally:
            conn.close()
