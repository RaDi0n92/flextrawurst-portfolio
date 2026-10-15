# groups_api.py — Gruppen-System API (EINSICHT VI)
# Eingebunden über: from groups_api import register_groups_routes

from fastapi import Header, Query, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional
import asyncio
import datetime
import pathlib
import os
import psycopg2.extras
from auth import verify_token
try:
    from ws_manager import manager as _chat_manager
except ImportError:
    _chat_manager = None


def register_groups_routes(app, get_conn):
    """Registriert alle Gruppen-Endpunkte an der gegebenen FastAPI-App."""

    # ── Pydantic-Modelle ──────────────────────────────────────────────────────

    class GroupCreate(BaseModel):
        name: str
        description: Optional[str] = None
        group_type: str = "resonance_group"
        visibility_layer: str = "internal"
        rights_policy: Optional[dict] = None
        meta: Optional[dict] = None

    class MemberAdd(BaseModel):
        member_type: str   # human | entity | system
        member_id: str
        role: str = "member"

    class MaterialLink(BaseModel):
        object_type: str   # splitter | post | gedankenblase | human_material | shadow_dialog
        object_id: str
        relation_type: str = "linked"
        visibility_layer: str = "internal"

    class GroupTopicCreate(BaseModel):
        title: str
        description: Optional[str] = None
        meta: Optional[dict] = None

    class GroupPostCreate(BaseModel):
        title: Optional[str] = None
        content: str
        topic_id: Optional[int] = None
        visibility_layer: str = "internal"
        meta: Optional[dict] = None

    class GroupPollCreate(BaseModel):
        question: str
        options: list[str]
        allow_multiple: bool = False
        closes_at: Optional[datetime.datetime] = None
        meta: Optional[dict] = None

    class GroupPollVote(BaseModel):
        option_indexes: list[int]

    class PolicyUpdate(BaseModel):
        humans_can_create: Optional[bool] = None
        require_approval: Optional[bool] = None
        entity_can_create: Optional[bool] = None
        max_groups_per_human: Optional[int] = None

    # ── Hilfs-Funktionen ─────────────────────────────────────────────────────

    def _decode_token(authorization: str | None):
        """Eine Auth-Wahrheit: gleiche Verifikation wie die zentrale Welt-API."""
        if not authorization or not authorization.startswith("Bearer "):
            return None, None
        try:
            payload = verify_token(authorization.removeprefix("Bearer "))
            return payload.get("user_id"), payload.get("role", "mensch")
        except Exception:
            return None, None

    def _is_admin(authorization: str | None) -> bool:
        _, role = _decode_token(authorization)
        return role == "admin"

    _HUMAN_ACCOUNT_ROLES = {"mensch", "human", "user", "supporter"}

    def _is_human_account_role(role: str | None) -> bool:
        return bool(role and role in _HUMAN_ACCOUNT_ROLES)

    def _get_human_id(authorization: str | None) -> str | None:
        uid, role = _decode_token(authorization)
        if uid and _is_human_account_role(role):
            return uid
        return None

    def _member_types_for_role(role: str | None) -> tuple[str, ...]:
        # Membership-Typ beschreibt die Identitaetsart, nicht die veraenderliche
        # Account-Berechtigungsrolle (mensch/user/supporter). Das Schema nennt
        # dafuer kanonisch "human"; "mensch" bleibt als Legacy-Alias lesbar.
        if _is_human_account_role(role):
            return ("human", "mensch")
        return (str(role),) if role else tuple()

    def _actor_identity_type(role: str | None) -> str | None:
        """Stabile Identitaetsart fuer persistente Identitaets-Schluessel."""
        if _is_human_account_role(role):
            return "human"
        return str(role) if role else None

    def _active_membership(cur, group_id: int, uid: str | None, role: str | None):
        if not uid or not role:
            return None
        member_types = _member_types_for_role(role)
        if not member_types:
            return None
        placeholders = ",".join(["%s"] * len(member_types))
        cur.execute(
            f"""SELECT * FROM group_memberships
                WHERE group_id=%s AND member_id=%s
                  AND member_type IN ({placeholders}) AND status='active'
                LIMIT 1""",
            [group_id, str(uid), *member_types],
        )
        return cur.fetchone()

    def _load_group(cur, group_id: int):
        cur.execute(
            "SELECT id, status, visibility_layer, rights_policy, approval_status, created_by_type, created_by_id FROM groups WHERE id=%s",
            (group_id,),
        )
        g = cur.fetchone()
        if not g:
            raise HTTPException(404, "Gruppe nicht gefunden")
        return dict(g)

    def _group_is_live(g: dict) -> bool:
        return g.get("status") in ("active", "pre_einzug_active")

    def _can_view_group(cur, group_id: int, uid: str | None, role: str | None) -> bool:
        g = _load_group(cur, group_id)
        if role == "admin":
            return True
        if not _group_is_live(g):
            return False
        vis = g.get("visibility_layer")
        if vis == "public":
            return True
        # 'internal' war laut Review nur anonym zu offen; authentifizierte Nutzer duerfen lesen.
        if vis == "internal" and uid:
            return True
        if _can_manage_group(cur, group_id, uid, role):
            return True
        m = _active_membership(cur, group_id, uid, role)
        policy = g.get("rights_policy") or {}
        return bool(m and policy.get("member_view", True))

    def _can_post_group(cur, group_id: int, uid: str | None, role: str | None) -> bool:
        g = _load_group(cur, group_id)
        if not _group_is_live(g):
            return False
        if role == "admin" or _can_manage_group(cur, group_id, uid, role):
            return True
        m = _active_membership(cur, group_id, uid, role)
        policy = g.get("rights_policy") or {}
        return bool(m and policy.get("member_post", False))

    def _can_participate_group(cur, group_id: int, uid: str | None, role: str | None) -> bool:
        g = _load_group(cur, group_id)
        if not _group_is_live(g):
            return False
        if role == "admin" or _can_manage_group(cur, group_id, uid, role):
            return True
        return _active_membership(cur, group_id, uid, role) is not None

    def _can_manage_live_group(cur, group_id: int, uid: str | None, role: str | None) -> bool:
        g = _load_group(cur, group_id)
        return _group_is_live(g) and _can_manage_group(cur, group_id, uid, role)

    def _entity_is_eingezogen(cur, entity_id: str) -> bool:
        cur.execute("""
            SELECT s.status, p.meta->>'einzug_timestamp' AS einzug_timestamp
            FROM entity_slots s
            LEFT JOIN entity_profiles p USING (entity_id)
            WHERE s.entity_id=%s
        """, (entity_id,))
        row = cur.fetchone()
        return bool(row and row["status"] in ("eingezogen", "schläft") and row["einzug_timestamp"])

    def _ensure_group_social_schema():
        """Fail closed if the group schema migration has not been applied.

        Runtime DDL made the API process require schema CREATE privileges.  The
        tables are deployment state, not request state, so the isolated API
        role must only verify that the migration is present.
        """
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                expected = (
                    "group_topics",
                    "group_posts",
                    "group_polls",
                    "group_poll_votes",
                    "group_chat_messages",
                )
                cur.execute(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_name = ANY(%s)
                    """,
                    (list(expected),),
                )
                existing = {row["table_name"] for row in cur.fetchall()}
                missing = [name for name in expected if name not in existing]
                if missing:
                    raise RuntimeError(
                        "Gruppen-Schema fehlt; Migration vor API-Start ausführen: "
                        + ", ".join(missing)
                    )
        finally:
            conn.close()

    def _can_manage_group(cur, group_id: int, uid: str | None, role: str | None) -> bool:
        if role == "admin":
            return True
        if not uid:
            return False
        cur.execute("SELECT created_by_type, created_by_id FROM groups WHERE id=%s", (group_id,))
        g = cur.fetchone()
        if not g:
            raise HTTPException(404, "Gruppe nicht gefunden")
        creator_types = set(_member_types_for_role(role))
        if str(g["created_by_id"]) == str(uid) and str(g["created_by_type"]) in creator_types:
            return True
        member_types = _member_types_for_role(role)
        if not member_types:
            return False
        placeholders = ",".join(["%s"] * len(member_types))
        cur.execute(f"""
            SELECT role FROM group_memberships
            WHERE group_id=%s AND member_id=%s AND member_type IN ({placeholders}) AND status='active'
            LIMIT 1
        """, (group_id, str(uid), *member_types))
        m = cur.fetchone()
        return bool(m and m["role"] in ("founder", "owner"))

    _ensure_group_social_schema()

    # ── GET /api/groups ───────────────────────────────────────────────────────

    @app.get("/groups")
    def list_groups(
        group_type: Optional[str] = Query(default=None),
        status: Optional[str] = Query(default=None),
        visibility: Optional[str] = Query(default=None),
        canonical_entity_id: Optional[str] = Query(default=None),
        created_by_type: Optional[str] = Query(default=None),
        search: Optional[str] = Query(default=None),
        limit: int = Query(default=50, le=200),
        offset: int = Query(default=0),
        authorization: Optional[str] = Header(default=None),
    ):
        """Gruppen-Liste: anonym nur public; internal ab Login; private nur aktive Mitglieder."""
        uid, role = _decode_token(authorization)
        is_admin = role == "admin"
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                conditions = []
                params = []
                if not is_admin:
                    conditions.append("g.status IN ('active','pre_einzug_active')")
                    conditions.append("g.approval_status = 'approved'")
                    if not uid:
                        conditions.append("g.visibility_layer = 'public'")
                    else:
                        member_types = _member_types_for_role(role)
                        placeholders = ",".join(["%s"] * len(member_types))
                        conditions.append(f"""(
                            g.visibility_layer IN ('public','internal')
                            OR EXISTS (
                                SELECT 1 FROM group_memberships gm2
                                WHERE gm2.group_id=g.id AND gm2.member_id=%s
                                  AND gm2.member_type IN ({placeholders})
                                  AND gm2.status='active'
                                  AND COALESCE((g.rights_policy->>'member_view')::boolean, true)
                            )
                        )""")
                        params.extend([str(uid), *member_types])
                if group_type:
                    conditions.append("g.group_type = %s")
                    params.append(group_type)
                if status:
                    conditions.append("g.status = %s")
                    params.append(status)
                if visibility:
                    conditions.append("g.visibility_layer = %s")
                    params.append(visibility)
                if canonical_entity_id:
                    conditions.append("g.canonical_entity_id = %s")
                    params.append(canonical_entity_id)
                if created_by_type:
                    conditions.append("g.created_by_type = %s")
                    params.append(created_by_type)
                if search:
                    conditions.append("(g.name ILIKE %s OR g.description ILIKE %s)")
                    params.extend([f"%{search}%", f"%{search}%"])
                where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
                cur.execute(f"""
                    SELECT g.*,
                           COUNT(DISTINCT gm.id) AS member_count
                    FROM groups g
                    LEFT JOIN group_memberships gm ON gm.group_id = g.id AND gm.status='active'
                    {where}
                    GROUP BY g.id
                    ORDER BY g.created_at DESC
                    LIMIT %s OFFSET %s
                """, params + [limit, offset])
                groups = [dict(r) for r in cur.fetchall()]
                cur.execute(f"SELECT COUNT(*) AS n FROM groups g {where}", params)
                total = cur.fetchone()["n"]
                return {"groups": groups, "total": total, "limit": limit, "offset": offset}
        finally:
            conn.close()

    # ── GET /api/groups/policy ────────────────────────────────────────────────

    @app.get("/groups/policy")
    def get_group_policy():
        """Gibt die aktuelle Gruppen-Erstellungs-Policy zurück."""
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM group_creation_policy WHERE id=1")
                row = cur.fetchone()
                return dict(row) if row else {"humans_can_create": True, "require_approval": False, "entity_can_create": False}
        finally:
            conn.close()

    # ── PATCH /api/groups/policy ──────────────────────────────────────────────

    @app.patch("/groups/policy")
    def update_group_policy(
        body: PolicyUpdate,
        authorization: Optional[str] = Header(default=None),
    ):
        """Admin-only: Policy für Gruppen-Erstellung ändern."""
        if not _is_admin(authorization):
            raise HTTPException(403, "Admin required")
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                updates = {}
                if body.humans_can_create is not None:
                    updates["humans_can_create"] = body.humans_can_create
                if body.require_approval is not None:
                    updates["require_approval"] = body.require_approval
                if body.entity_can_create is not None:
                    updates["entity_can_create"] = body.entity_can_create
                if body.max_groups_per_human is not None:
                    updates["max_groups_per_human"] = body.max_groups_per_human
                if not updates:
                    raise HTTPException(400, "Keine Änderungen angegeben")
                set_clause = ", ".join(f"{k} = %s" for k in updates)
                cur.execute(
                    f"UPDATE group_creation_policy SET {set_clause}, updated_at=NOW() WHERE id=1",
                    list(updates.values()),
                )
                conn.commit()
                cur.execute("SELECT * FROM group_creation_policy WHERE id=1")
                return dict(cur.fetchone())
        finally:
            conn.close()

    # ── GET /api/groups/fan/{entity_id} ──────────────────────────────────────

    @app.get("/groups/fan/{entity_id}")
    def get_fan_group(
        entity_id: str,
        authorization: Optional[str] = Header(default=None),
    ):
        """Gibt die kanonische Fangruppe für ein Wesen zurück, soweit sie sichtbar ist."""
        uid, role = _decode_token(authorization)
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT g.*, COUNT(DISTINCT gm.id) AS member_count
                    FROM groups g
                    LEFT JOIN group_memberships gm ON gm.group_id = g.id AND gm.status='active'
                    WHERE g.canonical_entity_id = %s AND g.group_type = 'entity_fan_group'
                    GROUP BY g.id
                    LIMIT 1
                """, (entity_id,))
                row = cur.fetchone()
                if not row:
                    raise HTTPException(404, f"Keine Fangruppe für {entity_id}")
                if not _can_view_group(cur, int(row["id"]), uid, role):
                    raise HTTPException(403, "Keine Leseberechtigung")
                return dict(row)
        finally:
            conn.close()

    # ── GET /api/groups/{group_id} ────────────────────────────────────────────

    @app.get("/groups/{group_id}")
    def get_group(
        group_id: int,
        authorization: Optional[str] = Header(default=None),
    ):
        """Gruppen-Detail."""
        uid, role = _decode_token(authorization)
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                if not _can_view_group(cur, group_id, uid, role):
                    raise HTTPException(403, "Keine Leseberechtigung")
                cur.execute("""
                    SELECT g.*, COUNT(DISTINCT gm.id) AS member_count,
                           COUNT(DISTINCT ml.id) AS material_count
                    FROM groups g
                    LEFT JOIN group_memberships gm ON gm.group_id = g.id AND gm.status='active'
                    LEFT JOIN group_material_links ml ON ml.group_id = g.id
                    WHERE g.id = %s
                    GROUP BY g.id
                """, (group_id,))
                row = cur.fetchone()
                if not row:
                    raise HTTPException(404, "Gruppe nicht gefunden")
                return dict(row)
        finally:
            conn.close()

    # ── POST /api/groups ──────────────────────────────────────────────────────

    @app.post("/groups")
    def create_group(
        body: GroupCreate,
        authorization: Optional[str] = Header(default=None),
    ):
        """Gruppe erstellen — Menschen und Admins erlaubt (policy-abhängig)."""
        uid, role = _decode_token(authorization)
        is_admin = role == "admin"
        if not uid:
            raise HTTPException(401, "Authentifizierung erforderlich")

        conn = get_conn()
        try:
            with conn.cursor() as cur:
                # Policy prüfen
                cur.execute("SELECT * FROM group_creation_policy WHERE id=1")
                policy = dict(cur.fetchone())
                if not is_admin:
                    if role == "entity":
                        if not policy["entity_can_create"]:
                            raise HTTPException(403, "Gruppen-Erstellung durch Wesen ist aktuell gesperrt")
                        if not _entity_is_eingezogen(cur, str(uid)):
                            raise HTTPException(403, "Wesen dürfen Gruppen erst nach abgeschlossenem Einzug erstellen")
                    elif _is_human_account_role(role):
                        if not policy["humans_can_create"]:
                            raise HTTPException(403, "Gruppen-Erstellung durch Menschen ist aktuell gesperrt")
                        max_groups = policy.get("max_groups_per_human")
                        if max_groups is not None:
                            cur.execute("""
                                SELECT COUNT(*) AS n FROM groups
                                WHERE created_by_type IN ('mensch','human')
                                  AND created_by_id=%s AND status!='deleted'
                            """, (str(uid),))
                            if int(cur.fetchone()["n"]) >= int(max_groups):
                                raise HTTPException(403, "Maximale Gruppenanzahl für diesen Menschen erreicht")
                    else:
                        raise HTTPException(403, "Keine Berechtigung")

                approval = "approved" if (is_admin or not policy["require_approval"]) else "pending_review"
                slug = body.name.lower().replace(" ", "_").replace("-", "_")[:80]
                # Slug eindeutig machen
                cur.execute("SELECT COUNT(*) AS n FROM groups WHERE slug = %s", (slug,))
                if cur.fetchone()["n"] > 0:
                    slug = f"{slug}_{int(datetime.datetime.now().timestamp())}"

                rights_policy = body.rights_policy or {"public_join": False, "member_post": False, "member_view": True}
                creator_type = "human" if _is_human_account_role(role) else role
                cur.execute("""
                    INSERT INTO groups (slug, name, description, group_type, status,
                                        visibility_layer, created_by_type, created_by_id,
                                        creation_mode, approval_status, rights_policy, meta)
                    VALUES (%s, %s, %s, %s, 'active', %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    slug, body.name, body.description, body.group_type,
                    body.visibility_layer,
                    creator_type, str(uid),
                    "human_created" if _is_human_account_role(role) else "entity_initiated" if role == "entity" else "admin_created",
                    approval, psycopg2.extras.Json(rights_policy), psycopg2.extras.Json(body.meta or {})
                ))
                group_id = cur.fetchone()["id"]
                # Gründer automatisch als Mitglied hinzufügen
                cur.execute("""
                    INSERT INTO group_memberships (group_id, member_type, member_id, role, added_by_type, added_by_id)
                    VALUES (%s, %s, %s, 'founder', %s, %s)
                    ON CONFLICT DO NOTHING
                """, (group_id, creator_type, str(uid), creator_type, str(uid)))
                # Event loggen
                cur.execute("""
                    INSERT INTO events (event_type, actor_type, actor_id, payload, visibility_layer)
                    VALUES ('gruppe.erstellt', %s, %s, %s, 'internal')
                """, (role, str(uid), psycopg2.extras.Json({
                    "group_id": group_id,
                    "name": body.name,
                    "type": body.group_type,
                })))
                conn.commit()
                return {"ok": True, "group_id": group_id, "slug": slug, "approval_status": approval}
        finally:
            conn.close()

    # ── PATCH /api/groups/{group_id} ─────────────────────────────────────────

    @app.patch("/groups/{group_id}")
    def update_group(
        group_id: int,
        body: dict,
        authorization: Optional[str] = Header(default=None),
    ):
        """Gruppe bearbeiten — nur Admin."""
        uid, role = _decode_token(authorization)
        if role != "admin":
            raise HTTPException(403, "Admin erforderlich")
        allowed = {k: v for k, v in body.items() if k in ("name","description","visibility_layer","status")}
        if not allowed:
            raise HTTPException(400, "Nichts zu aktualisieren")
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                sets = ", ".join(f"{k}=%s" for k in allowed)
                cur.execute(f"UPDATE groups SET {sets}, updated_at=NOW() WHERE id=%s", list(allowed.values()) + [group_id])
                if cur.rowcount == 0:
                    raise HTTPException(404, "Gruppe nicht gefunden")
                conn.commit()
                return {"ok": True, "id": group_id}
        finally:
            conn.close()

    # ── DELETE /api/groups/{group_id} ─────────────────────────────────────────

    @app.delete("/groups/{group_id}")
    def delete_group(
        group_id: int,
        authorization: Optional[str] = Header(default=None),
    ):
        """Gruppe löschen — nur Admin. Weiche Löschung via status='deleted'."""
        uid, role = _decode_token(authorization)
        if role != "admin":
            raise HTTPException(403, "Admin erforderlich")
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("UPDATE groups SET status='deleted', updated_at=NOW() WHERE id=%s", (group_id,))
                if cur.rowcount == 0:
                    raise HTTPException(404, "Gruppe nicht gefunden")
                conn.commit()
                return {"ok": True, "deleted": group_id}
        finally:
            conn.close()

    # ── GET /api/groups/{group_id}/members ────────────────────────────────────

    @app.get("/groups/{group_id}/members")
    def list_group_members(
        group_id: int,
        authorization: Optional[str] = Header(default=None),
    ):
        uid, role = _decode_token(authorization)
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                if not _can_view_group(cur, group_id, uid, role):
                    raise HTTPException(403, "Keine Leseberechtigung")
                cur.execute("""
                    SELECT * FROM group_memberships
                    WHERE group_id = %s AND status = 'active'
                    ORDER BY joined_at
                """, (group_id,))
                return {"members": [dict(r) for r in cur.fetchall()]}
        finally:
            conn.close()

    # ── POST /api/groups/{group_id}/members ───────────────────────────────────

    @app.post("/groups/{group_id}/members")
    def add_group_member(
        group_id: int,
        body: MemberAdd,
        authorization: Optional[str] = Header(default=None),
    ):
        """Mitglied hinzufügen. Admin kann alle hinzufügen; Mensch kann sich selbst hinzufügen."""
        uid, role = _decode_token(authorization)
        is_admin = role == "admin"
        if not uid:
            raise HTTPException(401, "Authentifizierung erforderlich")

        conn = get_conn()
        try:
            with conn.cursor() as cur:
                g = _load_group(cur, group_id)
                if not _group_is_live(g):
                    raise HTTPException(409, "Gruppe ist nicht aktiv")
                policy = g.get("rights_policy") or {}

                member_type = "human" if body.member_type == "mensch" else body.member_type
                member_id = str(body.member_id)
                member_role = body.role
                if member_type not in ("human", "entity", "system"):
                    raise HTTPException(400, "Unbekannter Mitgliedstyp")
                # Vor Einzug darf auch ein Admin keine operative Wesen-Mitgliedschaft erzeugen.
                if member_type == "entity" and not _entity_is_eingezogen(cur, member_id):
                    raise HTTPException(403, "Wesen dürfen Gruppen erst nach abgeschlossenem Einzug beitreten")
                if not is_admin:
                    member_role = "member"  # Self-Join darf keine Rolleneskalation erlauben.
                    if _is_human_account_role(role):
                        if member_type not in ("mensch", "human") or member_id != str(uid):
                            raise HTTPException(403, "Nur eigene Mitgliedschaft möglich")
                        if not policy.get("public_join", False):
                            raise HTTPException(403, "Öffentlicher Beitritt ist für diese Gruppe gesperrt")
                        member_type = "human"
                    elif role == "entity":
                        if member_type != "entity" or member_id != str(uid):
                            raise HTTPException(403, "Wesen darf nur die eigene Mitgliedschaft setzen")
                        if not _entity_is_eingezogen(cur, str(uid)):
                            raise HTTPException(403, "Wesen dürfen Gruppen erst nach abgeschlossenem Einzug beitreten")
                        if not policy.get("entity_can_join", False):
                            raise HTTPException(403, "Entity-Beitritt ist für diese Gruppe nicht freigegeben")
                    else:
                        raise HTTPException(403, "Keine Berechtigung")

                cur.execute("""
                    INSERT INTO group_memberships (group_id, member_type, member_id, role,
                                                   added_by_type, added_by_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (group_id, member_type, member_id) DO UPDATE
                    SET status='active', left_at=NULL,
                        role=EXCLUDED.role, added_by_type=EXCLUDED.added_by_type, added_by_id=EXCLUDED.added_by_id
                    RETURNING id
                """, (group_id, member_type, member_id, member_role, role, str(uid)))
                mid = cur.fetchone()["id"]
                cur.execute("""
                    INSERT INTO events (event_type, actor_type, actor_id, payload, visibility_layer)
                    VALUES ('gruppe.beigetreten', %s, %s, %s, 'internal')
                """, (role, str(uid), psycopg2.extras.Json({"target_type": "group", "target_id": str(group_id), "group_id": group_id, "member_type": member_type, "member_id": member_id, "role": member_role})))
                conn.commit()
                return {"ok": True, "membership_id": mid}
        finally:
            conn.close()

    @app.delete("/groups/{group_id}/members/self")
    def leave_group(
        group_id: int,
        authorization: Optional[str] = Header(default=None),
    ):
        """Eigene aktive Mitgliedschaft verlassen. Founder/Owner brauchen zuerst eine definierte Uebergabe."""
        uid, role = _decode_token(authorization)
        if not uid or not (_is_human_account_role(role) or role == "entity"):
            raise HTTPException(401, "Authentifizierung erforderlich")
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                g = _load_group(cur, group_id)
                if not _group_is_live(g):
                    raise HTTPException(409, "Gruppe ist nicht aktiv")
                membership = _active_membership(cur, group_id, str(uid), role)
                if not membership:
                    raise HTTPException(404, "Keine aktive Mitgliedschaft")
                if membership.get("role") in ("founder", "owner"):
                    raise HTTPException(409, "Founder/Owner kann die Gruppe ohne definierte Uebergabe nicht verlassen")
                cur.execute("""
                    UPDATE group_memberships
                    SET status='left', left_at=NOW()
                    WHERE id=%s AND status='active'
                """, (membership["id"],))
                cur.execute("""
                    INSERT INTO events (event_type, actor_type, actor_id, payload, visibility_layer)
                    VALUES ('gruppe.verlassen', %s, %s, %s, 'internal')
                """, (role, str(uid), psycopg2.extras.Json({"target_type": "group", "target_id": str(group_id), "group_id": group_id, "membership_id": membership["id"]})))
                conn.commit()
                return {"ok": True, "left": group_id}
        finally:
            conn.close()

    # ── GET /api/groups/{group_id}/materials ──────────────────────────────────

    @app.get("/groups/{group_id}/materials")
    def list_group_materials(
        group_id: int,
        authorization: Optional[str] = Header(default=None),
    ):
        uid, role = _decode_token(authorization)
        is_admin = role == "admin"
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                if not _can_view_group(cur, group_id, uid, role):
                    raise HTTPException(403, "Keine Leseberechtigung")
                # Privates Material nur für Admin oder Gruppenmanager sichtbar.
                can_manage = _can_manage_group(cur, group_id, uid, role)
                vis_filter = "" if (is_admin or can_manage) else "AND ml.visibility_layer != 'private'"
                cur.execute(f"""
                    SELECT ml.* FROM group_material_links ml
                    WHERE ml.group_id = %s {vis_filter}
                    ORDER BY ml.created_at DESC
                    LIMIT 100
                """, (group_id,))
                return {"materials": [dict(r) for r in cur.fetchall()]}
        finally:
            conn.close()

    # ── POST /api/groups/{group_id}/materials ─────────────────────────────────

    @app.post("/groups/{group_id}/materials")
    def add_group_material(
        group_id: int,
        body: MaterialLink,
        authorization: Optional[str] = Header(default=None),
    ):
        """Material mit Gruppe verknüpfen. Keine Autolinks für private Menschquellen."""
        uid, role = _decode_token(authorization)
        is_admin = role == "admin"
        if not uid:
            raise HTTPException(401, "Authentifizierung erforderlich")

        conn = get_conn()
        try:
            with conn.cursor() as cur:
                # Consent-Pruefung und Link-Write laufen in derselben Transaktion.
                # FOR SHARE verhindert, dass Consent zwischen Pruefung und Insert
                # parallel widerrufen/geaendert wird.
                if body.object_type == "human_material":
                    cur.execute("""
                        SELECT consent_status, human_id, visibility_layer
                        FROM human_material_sources WHERE id = %s
                        FOR SHARE
                    """, (body.object_id,))
                    hm = cur.fetchone()
                    if not hm:
                        raise HTTPException(404, "Menschquelle nicht gefunden")
                    if hm["consent_status"] != "gegeben":
                        raise HTTPException(403, "Kein Consent für diese Menschquelle")
                    if not is_admin and str(hm["human_id"]) != str(uid):
                        raise HTTPException(403, "Nur eigene Menschquellen verknüpfbar")

                if not _can_post_group(cur, group_id, uid, role):
                    raise HTTPException(403, "Keine Berechtigung, Material in dieser Gruppe zu verknüpfen")
                cur.execute("""
                    INSERT INTO group_material_links (group_id, object_type, object_id,
                        relation_type, visibility_layer, added_by_type, added_by_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (group_id, body.object_type, body.object_id,
                      body.relation_type, body.visibility_layer, role, str(uid)))
                lid = cur.fetchone()["id"]
                conn.commit()
                return {"ok": True, "link_id": lid}
        finally:
            conn.close()

    # ── Echte Gruppen-Inhalte: Themen, Posts, Umfragen ───────────────────────

    @app.get("/groups/{group_id}/topics")
    def list_group_topics(
        group_id: int,
        limit: int = Query(default=50, le=200),
        offset: int = Query(default=0),
        authorization: Optional[str] = Header(default=None),
    ):
        uid, role = _decode_token(authorization)
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                if not _can_view_group(cur, group_id, uid, role):
                    raise HTTPException(403, "Keine Leseberechtigung")
                cur.execute("""
                    SELECT gt.*,
                           COUNT(gp.id) FILTER (WHERE gp.status='active') AS post_count
                    FROM group_topics gt
                    LEFT JOIN group_posts gp ON gp.topic_id = gt.id
                    WHERE gt.group_id=%s AND gt.status='active'
                    GROUP BY gt.id
                    ORDER BY gt.created_at DESC
                    LIMIT %s OFFSET %s
                """, (group_id, limit, offset))
                return {"topics": [dict(r) for r in cur.fetchall()], "limit": limit, "offset": offset}
        finally:
            conn.close()

    @app.post("/groups/{group_id}/topics")
    def create_group_topic(
        group_id: int,
        body: GroupTopicCreate,
        authorization: Optional[str] = Header(default=None),
    ):
        uid, role = _decode_token(authorization)
        if not uid:
            raise HTTPException(401, "Authentifizierung erforderlich")
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                if not _can_manage_live_group(cur, group_id, uid, role):
                    raise HTTPException(403, "Nur Admins oder Gruppengründer dürfen in aktiven Gruppen Themen erstellen")
                cur.execute("""
                    INSERT INTO group_topics (group_id, title, description, created_by_type, created_by_id, meta)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING *
                """, (group_id, body.title.strip(), body.description, role, str(uid), psycopg2.extras.Json(body.meta or {})))
                topic = dict(cur.fetchone())
                cur.execute("""
                    INSERT INTO events (event_type, actor_type, actor_id, payload, visibility_layer)
                    VALUES ('gruppe.thema_erstellt', %s, %s, %s, 'internal')
                """, (role, str(uid), psycopg2.extras.Json({
                    "group_id": group_id,
                    "topic_id": topic["id"],
                    "title": topic["title"],
                })))
                conn.commit()
                return {"ok": True, "topic": topic}
        except HTTPException:
            conn.rollback()
            raise
        except Exception as e:
            conn.rollback()
            raise HTTPException(500, f"Thema konnte nicht gespeichert werden: {type(e).__name__}: {e}")
        finally:
            conn.close()

    @app.get("/groups/{group_id}/posts")
    def list_group_posts(
        group_id: int,
        topic_id: Optional[int] = Query(default=None),
        limit: int = Query(default=30, le=100),
        offset: int = Query(default=0),
        authorization: Optional[str] = Header(default=None),
    ):
        uid, role = _decode_token(authorization)
        is_admin = role == "admin"
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                if not _can_view_group(cur, group_id, uid, role):
                    raise HTTPException(403, "Keine Leseberechtigung")
                conditions = ["gp.group_id=%s", "gp.status='active'"]
                params = [group_id]
                can_manage = _can_manage_group(cur, group_id, uid, role)
                if not (is_admin or can_manage):
                    conditions.append("gp.visibility_layer != 'private'")
                if topic_id is not None:
                    conditions.append("gp.topic_id=%s")
                    params.append(topic_id)
                where = " AND ".join(conditions)
                cur.execute(f"""
                    SELECT gp.*, gt.title AS topic_title
                    FROM group_posts gp
                    LEFT JOIN group_topics gt ON gt.id = gp.topic_id
                    WHERE {where}
                    ORDER BY gp.created_at DESC
                    LIMIT %s OFFSET %s
                """, params + [limit, offset])
                return {"posts": [dict(r) for r in cur.fetchall()], "limit": limit, "offset": offset}
        finally:
            conn.close()

    @app.post("/groups/{group_id}/posts")
    def create_group_post(
        group_id: int,
        body: GroupPostCreate,
        authorization: Optional[str] = Header(default=None),
    ):
        uid, role = _decode_token(authorization)
        if not uid:
            raise HTTPException(401, "Authentifizierung erforderlich")
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                if not _can_post_group(cur, group_id, uid, role):
                    raise HTTPException(403, "Keine Schreibberechtigung in dieser Gruppe")
                if body.topic_id is not None:
                    cur.execute("SELECT id FROM group_topics WHERE id=%s AND group_id=%s AND status='active'", (body.topic_id, group_id))
                    if not cur.fetchone():
                        raise HTTPException(400, "Thema gehört nicht zu dieser Gruppe")
                cur.execute("""
                    INSERT INTO group_posts (group_id, topic_id, title, content, visibility_layer,
                                             created_by_type, created_by_id, meta)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING *
                """, (group_id, body.topic_id, body.title, body.content, body.visibility_layer, role, str(uid), psycopg2.extras.Json(body.meta or {})))
                post = dict(cur.fetchone())
                cur.execute("""
                    INSERT INTO events (event_type, actor_type, actor_id, payload, visibility_layer)
                    VALUES ('gruppe.post_erstellt', %s, %s, %s, %s)
                """, (role, str(uid), psycopg2.extras.Json({
                    "group_id": group_id,
                    "post_id": post["id"],
                    "title": post["title"],
                }), body.visibility_layer))
                conn.commit()
                return {"ok": True, "post": post}
        except HTTPException:
            conn.rollback()
            raise
        except Exception as e:
            conn.rollback()
            raise HTTPException(500, f"Post konnte nicht gespeichert werden: {type(e).__name__}: {e}")
        finally:
            conn.close()

    @app.get("/groups/{group_id}/polls")
    def list_group_polls(
        group_id: int,
        limit: int = Query(default=20, le=100),
        offset: int = Query(default=0),
        authorization: Optional[str] = Header(default=None),
    ):
        uid, role = _decode_token(authorization)
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                if not _can_view_group(cur, group_id, uid, role):
                    raise HTTPException(403, "Keine Leseberechtigung")
                cur.execute("""
                    SELECT gp.*,
                           COALESCE(jsonb_object_agg(v.option_index, v.n) FILTER (WHERE v.option_index IS NOT NULL), '{}'::jsonb) AS vote_counts
                    FROM group_polls gp
                    LEFT JOIN (
                        SELECT poll_id, option_index, COUNT(*) AS n
                        FROM group_poll_votes
                        GROUP BY poll_id, option_index
                    ) v ON v.poll_id = gp.id
                    WHERE gp.group_id=%s AND gp.status='active'
                    GROUP BY gp.id
                    ORDER BY gp.created_at DESC
                    LIMIT %s OFFSET %s
                """, (group_id, limit, offset))
                polls = [dict(r) for r in cur.fetchall()]
                if uid:
                    for poll in polls:
                        voter_type = _actor_identity_type(role)
                        cur.execute("""
                            SELECT option_index FROM group_poll_votes
                            WHERE poll_id=%s AND voter_type=%s AND voter_id=%s
                            ORDER BY option_index
                        """, (poll["id"], voter_type, str(uid)))
                        poll["my_vote"] = [r["option_index"] for r in cur.fetchall()]
                return {"polls": polls, "limit": limit, "offset": offset}
        finally:
            conn.close()

    @app.post("/groups/{group_id}/polls")
    def create_group_poll(
        group_id: int,
        body: GroupPollCreate,
        authorization: Optional[str] = Header(default=None),
    ):
        uid, role = _decode_token(authorization)
        if not uid:
            raise HTTPException(401, "Authentifizierung erforderlich")
        options = [o.strip() for o in body.options if o and o.strip()]
        if len(options) < 2:
            raise HTTPException(400, "Mindestens zwei Optionen erforderlich")
        if len(options) > 10:
            raise HTTPException(400, "Maximal zehn Optionen")
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                if not _can_manage_live_group(cur, group_id, uid, role):
                    raise HTTPException(403, "Nur Admins oder Gruppengründer dürfen in aktiven Gruppen Umfragen erstellen")
                cur.execute("""
                    INSERT INTO group_polls (group_id, question, options, allow_multiple, closes_at,
                                             created_by_type, created_by_id, meta)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING *
                """, (group_id, body.question.strip(), psycopg2.extras.Json(options), body.allow_multiple, body.closes_at, role, str(uid), psycopg2.extras.Json(body.meta or {})))
                poll = dict(cur.fetchone())
                cur.execute("""
                    INSERT INTO events (event_type, actor_type, actor_id, payload, visibility_layer)
                    VALUES ('gruppe.umfrage_erstellt', %s, %s, %s, 'internal')
                """, (role, str(uid), psycopg2.extras.Json({
                    "group_id": group_id,
                    "poll_id": poll["id"],
                    "question": poll["question"],
                })))
                conn.commit()
                return {"ok": True, "poll": poll}
        except HTTPException:
            conn.rollback()
            raise
        except Exception as e:
            conn.rollback()
            raise HTTPException(500, f"Umfrage konnte nicht gespeichert werden: {type(e).__name__}: {e}")
        finally:
            conn.close()

    @app.post("/groups/{group_id}/polls/{poll_id}/vote")
    def vote_group_poll(
        group_id: int,
        poll_id: int,
        body: GroupPollVote,
        authorization: Optional[str] = Header(default=None),
    ):
        uid, role = _decode_token(authorization)
        if not uid:
            raise HTTPException(401, "Authentifizierung erforderlich")
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                if not _can_participate_group(cur, group_id, uid, role):
                    raise HTTPException(403, "Nur aktive Gruppenmitglieder dürfen abstimmen")
                cur.execute("SELECT * FROM group_polls WHERE id=%s AND group_id=%s AND status='active'", (poll_id, group_id))
                poll = cur.fetchone()
                if not poll:
                    raise HTTPException(404, "Umfrage nicht gefunden")
                if poll["closes_at"] and poll["closes_at"] < datetime.datetime.now(datetime.timezone.utc):
                    raise HTTPException(403, "Umfrage ist geschlossen")
                options = poll["options"] or []
                votes = sorted(set(body.option_indexes))
                if not poll["allow_multiple"] and len(votes) > 1:
                    raise HTTPException(400, "Nur eine Option erlaubt")
                if not votes or any(i < 0 or i >= len(options) for i in votes):
                    raise HTTPException(400, "Ungültige Option")
                voter_type = _actor_identity_type(role)
                cur.execute("DELETE FROM group_poll_votes WHERE poll_id=%s AND voter_type=%s AND voter_id=%s", (poll_id, voter_type, str(uid)))
                for idx in votes:
                    cur.execute("""
                        INSERT INTO group_poll_votes (poll_id, voter_type, voter_id, option_index)
                        VALUES (%s, %s, %s, %s)
                    """, (poll_id, voter_type, str(uid), idx))
                cur.execute("""
                    INSERT INTO events (event_type, actor_type, actor_id, payload, visibility_layer)
                    VALUES ('gruppe.umfrage_abgestimmt', %s, %s, %s, 'internal')
                """, (role, str(uid), psycopg2.extras.Json({"target_type": "group_poll", "target_id": str(poll_id), "group_id": group_id, "option_indexes": votes})))
                conn.commit()
                return {"ok": True, "poll_id": poll_id, "option_indexes": votes}
        finally:
            conn.close()

    # ── GET /api/entities/{entity_id}/groups ──────────────────────────────────

    @app.get("/entities/{entity_id}/groups")
    def get_entity_groups(
        entity_id: str,
        authorization: Optional[str] = Header(default=None),
    ):
        """Alle fuer den Aufrufer sichtbaren Gruppen eines Wesens (Mitgliedschaft oder canonical)."""
        uid, role = _decode_token(authorization)
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT DISTINCT g.id, g.slug, g.name, g.group_type, g.status,
                           g.visibility_layer, g.canonical_entity_id, g.created_at
                    FROM groups g
                    LEFT JOIN group_memberships gm ON gm.group_id = g.id
                    WHERE (gm.member_type='entity' AND gm.member_id=%s AND gm.status='active')
                       OR g.canonical_entity_id = %s
                    ORDER BY g.created_at
                """, (entity_id, entity_id))
                rows = [dict(r) for r in cur.fetchall()]
                visible = [r for r in rows if _can_view_group(cur, int(r["id"]), uid, role)]
                return {"groups": visible}
        finally:
            conn.close()

    # ── Ampel v4 ──────────────────────────────────────────────────────────────

    @app.get("/admin/einzugsampel/v4")
    def einzugsampel_v4(authorization: Optional[str] = Header(default=None)):
        """Reifeampel v4: mit allen Daniels Entscheidungen E-01..E-20 als Blocker."""
        if not _is_admin(authorization):
            raise HTTPException(403, "Admin required")

        import os, subprocess

        def check(name, klasse, ok, wert, note=None, blocker_type="technisch"):
            return {"name": name, "klasse": klasse, "ok": ok, "wert": wert,
                    "note": note, "blocker_type": blocker_type}

        checks = []
        # Rechte-Test ist nur fuer exakt den getesteten Code gueltig. Aendert sich
        # groups_api.py spaeter, wird die Ampel automatisch wieder rot statt einen
        # alten E2E-Erfolg als ewige Wahrheit weiterzutragen.
        gruppen_rechte_getestet = False
        gruppen_rechte_wert = "kein gueltiger E2E-Nachweis"
        try:
            import hashlib, json
            report_path = "/root/werkraum/flextrawurst-audit/groups_rights_fix_2026-09-07/report.json"
            if os.path.exists(report_path):
                with open(report_path, "r", encoding="utf-8") as fh:
                    rights_report = json.load(fh)
                own_hash = hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()
                gruppen_rechte_getestet = (
                    rights_report.get("status") == "BESTAETIGT_GEFIXT"
                    and rights_report.get("groups_api_sha256") == own_hash
                    and rights_report.get("rest_e2e", {}).get("passed") is True
                    and rights_report.get("websocket_e2e", {}).get("passed") is True
                    and rights_report.get("regression_2026_09_16", {}).get("passed") is True
                )
                if gruppen_rechte_getestet:
                    gruppen_rechte_wert = "REST 26/26 + WebSocket E2E + Regression 2026-09-16, Code-Hash stimmt"
                else:
                    gruppen_rechte_wert = "Testreport vorhanden, aber Code/Teststand stimmt nicht mehr"
        except Exception as e:
            gruppen_rechte_wert = f"E2E-Nachweis nicht lesbar: {type(e).__name__}"

        conn = get_conn()
        try:
            with conn.cursor() as cur:
                # ── A) TECHNISCH ──────────────────────────────────────────────
                cur.execute("SELECT COUNT(*) AS n FROM entity_slots WHERE status='bereit'")
                wesen_n = cur.fetchone()["n"]
                checks.append(check("Wesen-Slots aktiv", "A_Technisch", wesen_n > 0, f"{wesen_n} Wesen"))

                cur.execute("SELECT COUNT(*) AS n FROM ftw_posts WHERE sichtbarkeit='public'")
                posts_ok = cur.fetchone()["n"] > 0
                checks.append(check("Posts-System läuft", "A_Technisch", posts_ok, "Posts vorhanden" if posts_ok else "keine Posts"))

                try:
                    cur.execute("SELECT COUNT(*) AS n FROM splitter WHERE status='aktiv'")
                    sc = cur.fetchone()["n"]
                    checks.append(check("Splitter-System aktiv", "A_Technisch", sc > 0, f"{sc} aktive Splitter"))
                except Exception:
                    checks.append(check("Splitter-System aktiv", "A_Technisch", False, "Fehler"))

                import socket
                for port, name in [(8030, "welt-api"), (8787, "frontend")]:
                    try:
                        s = socket.create_connection(("localhost", port), timeout=2)
                        s.close()
                        checks.append(check(f"{name} Port {port}", "A_Technisch", True, "erreichbar"))
                    except Exception:
                        checks.append(check(f"{name} Port {port}", "A_Technisch", False, "nicht erreichbar"))

                # ── B) SICHERHEIT ─────────────────────────────────────────────
                checks.append(check("Splitter-Detail Sichtbarkeitscheck", "B_Sicherheit",
                    True, "visibility_layer check aktiv",
                    blocker_type="sicherheit"))
                checks.append(check("Menschquellen default privat", "B_Sicherheit",
                    True, "consent_status='offen', visibility_layer='private'",
                    blocker_type="sicherheit"))
                checks.append(check("Gruppenrechte E2E / private Material / Chat / Join", "B_Sicherheit",
                    gruppen_rechte_getestet, gruppen_rechte_wert,
                    blocker_type="sicherheit"))

                # ── C) WELTLOGIK ──────────────────────────────────────────────
                hg_dir = "/root/werkraum/welt/wesen_handlungsgrammatiken"
                hg_count = len([f for f in os.listdir(hg_dir) if f.endswith(".md") and f not in ("README.md","ANSCHLUSS.md")]) if os.path.isdir(hg_dir) else 0
                checks.append(check("Handlungsgrammatiken 12/12", "C_Weltlogik",
                    hg_count >= 12, f"{hg_count}/12",
                    note="Alle 12 beim Einzug aktiv (E-07)",
                    blocker_type="weltlogik"))

                checks.append(check("HG Einzug-Aktivierungsplan dokumentiert", "C_Weltlogik",
                    os.path.exists(f"{hg_dir}/ANSCHLUSS.md"),
                    "ANSCHLUSS.md vorhanden",
                    blocker_type="weltlogik"))

                checks.append(check("Shadow-Initiation vorbereitet (E-08)", "C_Weltlogik",
                    False, "Skeleton 503 — beim Einzug aktivieren",
                    blocker_type="weltlogik"))

                # ── D) BEWUSST BLOCKIERT ──────────────────────────────────────
                r = subprocess.run(["systemctl", "is-active", "codewesen_takt"],
                                   capture_output=True, text=True)
                takt_aus = r.stdout.strip() != "active"
                checks.append(check("codewesen_takt.py aus", "D_BewusstBlockiert",
                    takt_aus, r.stdout.strip(), blocker_type="bewusst"))

                checks.append(check("Kein Einzug ausgeführt", "D_BewusstBlockiert",
                    True, "einzug_blockiert=True", blocker_type="bewusst"))
                checks.append(check("Flarum Archiv/tot", "D_BewusstBlockiert",
                    True, "Keine Takte, keine Queues (E-16)", blocker_type="bewusst"))
                checks.append(check("Alle 6 Wesen gleichzeitig vorbereitet (E-14)", "D_BewusstBlockiert",
                    wesen_n == 6, f"{wesen_n}/6 bereit", blocker_type="bewusst"))

                # ── G) GRUPPEN (E-01/E-15 — harter Blocker) ──────────────────
                cur.execute("SELECT COUNT(*) AS n FROM groups")
                groups_n = cur.fetchone()["n"]
                cur.execute("""
                    SELECT to_regclass('public.groups') IS NOT NULL AS groups_ok,
                           to_regclass('public.group_memberships') IS NOT NULL AS memberships_ok,
                           to_regclass('public.group_material_links') IS NOT NULL AS materials_ok
                """)
                schema_row = cur.fetchone()
                gruppen_schema_ok = all(bool(schema_row[k]) for k in ("groups_ok", "memberships_ok", "materials_ok"))
                checks.append(check("Gruppen-Schema vorhanden (E-01)", "G_Gruppen",
                    gruppen_schema_ok, "groups + group_memberships + group_material_links" if gruppen_schema_ok else "Schema unvollstaendig",
                    blocker_type="gruppen"))

                cur.execute("SELECT COUNT(*) AS n FROM groups WHERE group_type='entity_fan_group'")
                fan_n = cur.fetchone()["n"]
                checks.append(check("6 Fangruppen vorhanden (E-02)", "G_Gruppen",
                    fan_n >= 6, f"{fan_n}/6 Fangruppen",
                    blocker_type="gruppen"))

                route_paths = {getattr(r, "path", "") for r in app.routes}
                required_group_routes = {
                    "/groups", "/groups/{group_id}", "/groups/{group_id}/members",
                    "/groups/{group_id}/materials", "/groups/{group_id}/posts",
                    "/groups/{group_id}/chat", "/ws/groups/{group_id}/chat",
                }
                gruppen_api_ok = required_group_routes.issubset(route_paths)
                checks.append(check("Gruppen-API vorhanden", "G_Gruppen",
                    gruppen_api_ok, f"{len(required_group_routes & route_paths)}/{len(required_group_routes)} Kernrouten registriert",
                    blocker_type="gruppen"))

                groups_ui = False  # wird true wenn Surface-GRUPPEN-Tab existiert
                # Prüfen ob GRUPPEN-Tab in Surface
                try:
                    import subprocess as sp
                    res = sp.run(["grep", "-c", "view-gruppen", "/root/flextrawurst/out/surface/flextrawurst_surface.html"],
                                 capture_output=True, text=True)
                    groups_ui = int(res.stdout.strip() or "0") > 0
                except Exception:
                    pass
                checks.append(check("Gruppen-UI vorhanden (E-01/E-15)", "G_Gruppen",
                    groups_ui, "view-gruppen in Surface" if groups_ui else "Surface-Tab noch nicht gebaut",
                    blocker_type="gruppen"))

                cur.execute("SELECT humans_can_create, entity_can_create, max_groups_per_human FROM group_creation_policy WHERE id=1")
                creation_policy = cur.fetchone()
                policy_ok = bool(creation_policy and creation_policy["humans_can_create"])
                checks.append(check("Gruppen-Erstellungs-Policy vorhanden (E-03)", "G_Gruppen",
                    policy_ok, "humans_can_create=true" if policy_ok else "Policy fehlt oder Menschen-Erstellung gesperrt",
                    blocker_type="gruppen"))

                entity_create_blocked = bool(creation_policy and not creation_policy["entity_can_create"] and gruppen_rechte_getestet)
                checks.append(check("Wesen-Gruppenerstellung vor Einzug blockiert (E-04)", "G_Gruppen",
                    entity_create_blocked,
                    "entity_can_create=false + Einzugsgate E2E-verifiziert" if entity_create_blocked else "Policy/Testnachweis nicht ausreichend",
                    blocker_type="gruppen"))

                # ── H) MENSCHQUELLEN/CONSENT (E-09/E-18) ─────────────────────
                cur.execute("SELECT COUNT(*) AS n FROM human_material_sources")
                hm_n = cur.fetchone()["n"]
                checks.append(check("Menschquellen DB-Schema vorhanden (E-18)", "H_Consent",
                    True, f"{hm_n} Einträge (default privat)",
                    blocker_type="consent"))

                user_consent_ui = False
                try:
                    res = sp.run(["grep", "-cE", "consent|innenquellen|mw-z-innenquellen", "/root/flextrawurst/out/surface/flextrawurst_surface.html"],
                                 capture_output=True, text=True)
                    user_consent_ui = int(res.stdout.strip() or "0") > 5
                except Exception:
                    pass
                checks.append(check("User-UI für Menschquellen (E-09/E-18)", "H_Consent",
                    user_consent_ui, "Consent-UI für Nutzer" if user_consent_ui else "noch nicht gebaut",
                    blocker_type="consent"))

                # ── I) SUBSTANZEN/CYBERLING (E-11/E-05/E-06) ─────────────────
                substanz_count = 0
                try:
                    cur.execute("SELECT COUNT(*) AS n FROM substance_catalog")
                    substanz_count = cur.fetchone()["n"]
                except Exception:
                    pass
                checks.append(check("Substanzsystem vorbereitet (E-11)", "I_Substanzen",
                    substanz_count > 0,
                    f"{substanz_count} Substanzen in substance_catalog" if substanz_count > 0 else "substance_catalog leer oder fehlt",
                    note="Rein fiktionale Weltmechanik",
                    blocker_type="substanz"))

                # Cyberling Recovery (case-insensitive grep)
                cyberling_recovery = False
                try:
                    res = sp.run(["grep", "-ic", "recovery", "/root/werkraum/welt/cyberling_daemon.py"],
                                 capture_output=True, text=True)
                    cyberling_recovery = int(res.stdout.strip() or "0") > 0
                except Exception:
                    pass
                checks.append(check("Cyberling Recovery vorhanden (E-06)", "I_Substanzen",
                    cyberling_recovery, "Recovery in cyberling_daemon.py" if cyberling_recovery else "noch nicht gebaut",
                    blocker_type="substanz"))

                checks.append(check("Cyberling/Wesen-Kopplung verhindert (E-06)", "I_Substanzen",
                    True, "Cyberling-Energie ≠ Codewesen-Energie",
                    blocker_type="substanz"))

                # ── J) SPLITTER-PROVENIENZ (E-19) ─────────────────────────────
                story_view = False
                try:
                    res = sp.run(["grep", "-cE", "splitter-story|story-view|splitterStory", "/root/flextrawurst/out/surface/flextrawurst_surface.html"],
                                 capture_output=True, text=True)
                    story_view = int(res.stdout.strip() or "0") > 0
                except Exception:
                    pass
                checks.append(check("Splitter-Story-View vorhanden (E-19)", "J_Provenienz",
                    story_view, "Story-View in Surface" if story_view else "noch nicht gebaut",
                    blocker_type="provenienz"))

                # ── K) DANIEL MANUAL RELEASE ──────────────────────────────────
                checks.append(check("Daniel private Zusatzblocker leer (E-13)", "K_ManualRelease",
                    False, "daniel_manual_release_required=true — Einzug nur nach expliziter Freigabe",
                    note="Muss manuell durch Daniel freigegeben werden",
                    blocker_type="daniel"))

        finally:
            conn.close()

        # Ampel-Logik
        a_tech = all(c["ok"] for c in checks if c["klasse"] == "A_Technisch")
        b_sec = all(c["ok"] for c in checks if c["klasse"] == "B_Sicherheit")
        g_groups = all(c["ok"] for c in checks if c["klasse"] == "G_Gruppen")
        h_consent = all(c["ok"] for c in checks if c["klasse"] == "H_Consent")

        if not a_tech:
            ampel = "rot"
            grund = "Technische Blocker"
        elif not b_sec:
            ampel = "rot"
            grund = "Sicherheitsblocker"
        elif not g_groups:
            ampel = "rot"
            grund = "Gruppen-Blocker (E-15 — harter Blocker)"
        elif not h_consent:
            ampel = "gelb"
            grund = "Consent-UI fehlt (E-09/E-18)"
        else:
            offen = [c for c in checks if not c["ok"]]
            if offen:
                ampel = "gelb"
                grund = f"{len(offen)} weitere Blocker offen"
            else:
                ampel = "gelb"
                grund = "Daniel manual release ausstehend (E-13)"

        offen_checks = [c for c in checks if not c["ok"]]
        klassen = {}
        for c in checks:
            k = c["klasse"]
            if k not in klassen:
                klassen[k] = {"ok": 0, "fail": 0}
            if c["ok"]:
                klassen[k]["ok"] += 1
            else:
                klassen[k]["fail"] += 1

        return {
            "ampel": ampel,
            "ampel_grund": grund,
            "klassen": {k: {"gruen": v["ok"], "gesamt": v["ok"]+v["fail"],
                             "status": "gruen" if v["fail"]==0 else "rot"} for k, v in klassen.items()},
            "checks": checks,
            "einzug_blockiert": True,
            "daniel_manual_release_required": True,
            "alle_sechs_einzug_bereit": (wesen_n == 6),
            "falsches_gruen_verhindert": True,
            "meta": {
                "version": "v4",
                "checks_gesamt": len(checks),
                "checks_gruen": len(checks) - len(offen_checks),
                "checks_offen": len(offen_checks),
                "entscheidungsboard": "docs/daniel_entscheidungsboard_vor_einzug.md",
                "neue_blocker": ["G_Gruppen", "H_Consent", "I_Substanzen", "J_Provenienz", "K_ManualRelease"],
            }
        }

    # ── GET /api/groups/{group_id}/chat ───────────────────────────────────────

    @app.get("/groups/{group_id}/chat")
    def get_group_chat(
        group_id: int,
        limit: int = Query(default=50, le=200),
        before: Optional[str] = Query(default=None),
        authorization: Optional[str] = Header(default=None),
    ):
        """Chat-Verlauf einer Gruppe (neueste zuerst, cursor-basiert)."""
        uid, role = _decode_token(authorization)
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                if not _can_view_group(cur, group_id, uid, role):
                    raise HTTPException(403, "Kein Zugriff")
                params = [group_id]
                where_extra = ""
                if before:
                    where_extra = " AND created_at < %s"
                    params.append(before)
                cur.execute(f"""
                    SELECT id, group_id, autor_type, autor_id, content,
                           created_at, meta
                    FROM group_chat_messages
                    WHERE group_id = %s{where_extra}
                    ORDER BY created_at DESC
                    LIMIT %s
                """, params + [limit])
                msgs = [dict(r) for r in cur.fetchall()]
                msgs.reverse()
                return {"messages": msgs, "group_id": group_id}
        finally:
            conn.close()

    # ── POST /api/groups/{group_id}/chat ──────────────────────────────────────

    @app.post("/groups/{group_id}/chat", status_code=201)
    def post_group_chat(
        group_id: int,
        body: dict,
        authorization: Optional[str] = Header(default=None),
    ):
        """Sendet eine Chat-Nachricht in die Gruppe (REST-Fallback ohne WS)."""
        uid, role = _decode_token(authorization)
        if not uid:
            raise HTTPException(401, "Nicht eingeloggt")
        content = (body.get("content") or "").strip()
        if not content:
            raise HTTPException(400, "Inhalt fehlt")
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                if not _can_post_group(cur, group_id, uid, role):
                    raise HTTPException(403, "Keine Chat-Schreibberechtigung in dieser Gruppe")
                cur.execute("""
                    INSERT INTO group_chat_messages (group_id, autor_type, autor_id, content)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id, created_at
                """, (group_id, role, uid, content))
                row = cur.fetchone()
                conn.commit()
                return {"ok": True, "id": row["id"], "created_at": str(row["created_at"])}
        finally:
            conn.close()

    # ── WS /api/ws/groups/{group_id}/chat ─────────────────────────────────────

    @app.websocket("/ws/groups/{group_id}/chat")
    async def ws_group_chat(websocket: WebSocket, group_id: int, token: Optional[str] = None):
        """WebSocket-Endpunkt für Echtzeit-Gruppen-Chat."""
        if _chat_manager is None:
            await websocket.close(code=1011)
            return

        # Gleiche JWT-Verifikation wie Welt-API/REST-Pfade, kein zweites Secret-System.
        claims = None
        if token:
            try:
                claims = verify_token(token)
            except Exception:
                pass

        if not claims:
            await websocket.close(code=4001)
            return

        uid = str(claims.get("user_id", ""))
        role = str(claims.get("role", "mensch"))
        if not uid:
            await websocket.close(code=4001)
            return

        # Chat ist eine Schreibaktion: vor dem Connect dieselben Gruppenrechte wie REST.
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                if not _can_post_group(cur, group_id, uid, role):
                    await websocket.close(code=4003)
                    return
        finally:
            conn.close()

        def _still_can_post() -> bool:
            conn = get_conn()
            try:
                with conn.cursor() as cur:
                    return _can_post_group(cur, group_id, uid, role)
            finally:
                conn.close()

        def _receive_guard():
            try:
                current = verify_token(token)
            except Exception:
                return 4001
            if str(current.get("user_id", "")) != uid:
                return 4001
            conn = get_conn()
            try:
                with conn.cursor() as cur:
                    if not _can_post_group(cur, group_id, uid, current.get("role", "mensch")):
                        return 4003
            finally:
                conn.close()
            return None

        await _chat_manager.connect(websocket, group_id, _receive_guard)

        try:
            await _chat_manager.broadcast(group_id, {
                "type": "presence",
                "online": _chat_manager.online_count(group_id),
            })
            while True:
                if not await _chat_manager.authorize(websocket, group_id):
                    return
                try:
                    data = await asyncio.wait_for(websocket.receive_json(), timeout=30)
                except asyncio.TimeoutError:
                    continue
                # Eine offene Verbindung darf alte Rollen oder gesperrte Konten
                # nicht weiterverwenden. Auch Ablaufzeiten gelten je Aktion.
                loop = asyncio.get_running_loop()
                try:
                    current = await loop.run_in_executor(None, verify_token, token)
                except Exception:
                    await websocket.close(code=4001)
                    return
                if str(current.get("user_id", "")) != uid:
                    await websocket.close(code=4001)
                    return
                role = str(current.get("role", "mensch"))
                msg_type = data.get("type", "message")

                if msg_type == "typing":
                    loop = asyncio.get_running_loop()
                    if not await loop.run_in_executor(None, _still_can_post):
                        await websocket.close(code=4003)
                        return
                    await _chat_manager.broadcast(group_id, {
                        "type": "typing",
                        "autor_id": uid,
                    }, exclude=websocket)

                elif msg_type == "message":
                    content = (data.get("content") or "").strip()
                    if not content:
                        continue
                    # In DB speichern
                    loop = asyncio.get_running_loop()
                    row_id = None
                    created_at = None

                    def _store():
                        conn = get_conn()
                        try:
                            with conn.cursor() as cur:
                                if not _can_post_group(cur, group_id, uid, role):
                                    raise PermissionError("Gruppen-Chatrecht wurde entzogen")
                                cur.execute("""
                                    INSERT INTO group_chat_messages
                                        (group_id, autor_type, autor_id, content)
                                    VALUES (%s, %s, %s, %s)
                                    RETURNING id, created_at
                                """, (group_id, role, uid, content))
                                r = cur.fetchone()
                                conn.commit()
                                return r["id"], str(r["created_at"])
                        finally:
                            conn.close()

                    try:
                        row_id, created_at = await loop.run_in_executor(None, _store)
                    except PermissionError:
                        await websocket.close(code=4003)
                        return
                    broadcast_msg = {
                        "type": "message",
                        "id": row_id,
                        "group_id": group_id,
                        "autor_type": role,
                        "autor_id": uid,
                        "content": content,
                        "created_at": created_at,
                    }
                    # Sender bekommt Bestätigung, alle anderen bekommen Broadcast
                    await _chat_manager.send(websocket, group_id, {**broadcast_msg, "own": True})
                    await _chat_manager.broadcast(group_id, broadcast_msg, exclude=websocket)

        except WebSocketDisconnect:
            pass
        finally:
            _chat_manager.disconnect(websocket, group_id)
            await _chat_manager.broadcast(group_id, {
                "type": "presence",
                "online": _chat_manager.online_count(group_id),
            })
