import sys

from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path
from lexicon import views

sys.path.insert(0, "/root/werkraum/Mein-Gesamtkonstrukt-planer/server")
from planner_api import (
    planner_auth_check,
    planner_files_api,
    planner_page,
    planner_state_api,
    planner_streams_api,
    schrottplatz_character_glb,
)
from real_fs_api import (
    real_fs_add,
    real_fs_approve,
    real_fs_browse,
    real_fs_list,
    real_fs_pending_list,
    real_fs_read,
    real_fs_reject,
    real_fs_remove,
    real_fs_propose_write,
)
from run_api import run_list_create, run_transition
from goal_api import goal_list_create, goal_update


def replica_redteam(request):
    return redirect("/Mein-Gesamtkonstrukt-planer/", permanent=True)


def replica_redteam_mobile(request):
    return redirect("/Mein-Gesamtkonstrukt-planer/", permanent=True)


def replica_redteam_mobile_test(request):
    return redirect("/Mein-Gesamtkonstrukt-planer/", permanent=True)


admin.site.site_header = "WorldWORDS Kuratorium"
admin.site.site_title = "WorldWORDS Admin"
admin.site.index_title = "Daten, Entscheidungen und Provenienz"

urlpatterns = [
    path("Mein-Gesamtkonstrukt-planer/", planner_page, name="mein_gesamtkonstrukt_planer"),
    path("Mein-Gesamtkonstrukt-planer/api/state/", planner_state_api, name="mein_gesamtkonstrukt_planer_state"),
    path("Mein-Gesamtkonstrukt-planer/api/files/", planner_files_api, name="mein_gesamtkonstrukt_planer_files"),
    path("Mein-Gesamtkonstrukt-planer/api/streams/", planner_streams_api, name="mein_gesamtkonstrukt_planer_streams"),
    path("Mein-Gesamtkonstrukt-planer/api/runs/", run_list_create, name="mein_gesamtkonstrukt_planer_runs"),
    path("Mein-Gesamtkonstrukt-planer/api/runs/transition/", run_transition, name="mein_gesamtkonstrukt_planer_run_transition"),
    path("Mein-Gesamtkonstrukt-planer/api/goals/", goal_list_create, name="mein_gesamtkonstrukt_planer_goals"),
    path("Mein-Gesamtkonstrukt-planer/api/goals/update/", goal_update, name="mein_gesamtkonstrukt_planer_goal_update"),
    path("Mein-Gesamtkonstrukt-planer/api/whoami/", planner_auth_check, name="mein_gesamtkonstrukt_planer_whoami"),
    path("Mein-Gesamtkonstrukt-planer/api/realfs/list/", real_fs_list, name="mein_gesamtkonstrukt_planer_realfs_list"),
    path("Mein-Gesamtkonstrukt-planer/api/realfs/add/", real_fs_add, name="mein_gesamtkonstrukt_planer_realfs_add"),
    path("Mein-Gesamtkonstrukt-planer/api/realfs/remove/", real_fs_remove, name="mein_gesamtkonstrukt_planer_realfs_remove"),
    path("Mein-Gesamtkonstrukt-planer/api/realfs/browse/", real_fs_browse, name="mein_gesamtkonstrukt_planer_realfs_browse"),
    path("Mein-Gesamtkonstrukt-planer/api/realfs/read/", real_fs_read, name="mein_gesamtkonstrukt_planer_realfs_read"),
    path("Mein-Gesamtkonstrukt-planer/api/realfs/propose-write/", real_fs_propose_write, name="mein_gesamtkonstrukt_planer_realfs_propose_write"),
    path("Mein-Gesamtkonstrukt-planer/api/realfs/pending/", real_fs_pending_list, name="mein_gesamtkonstrukt_planer_realfs_pending"),
    path("Mein-Gesamtkonstrukt-planer/api/realfs/approve/", real_fs_approve, name="mein_gesamtkonstrukt_planer_realfs_approve"),
    path("Mein-Gesamtkonstrukt-planer/api/realfs/reject/", real_fs_reject, name="mein_gesamtkonstrukt_planer_realfs_reject"),
    path("Mein-Gesamtkonstrukt-planer/static/daniel_char_rigged.glb", schrottplatz_character_glb, {"filename": "daniel_char_rigged.glb"}, name="mein_gesamtkonstrukt_planer_char_glb"),
    path("Mein-Gesamtkonstrukt-planer/static/daniel_char_opa.glb", schrottplatz_character_glb, {"filename": "daniel_char_opa.glb"}, name="mein_gesamtkonstrukt_planer_char_glb_opa"),
    path("Mein-Gesamtkonstrukt-planer/static/daniel_char_frau_v1_static.glb", schrottplatz_character_glb, {"filename": "daniel_char_frau_v1_static.glb"}, name="mein_gesamtkonstrukt_planer_char_glb_frau_v1"),
    path("Mein-Gesamtkonstrukt-planer/static/daniel_char_frau_v2_rigged.glb", schrottplatz_character_glb, {"filename": "daniel_char_frau_v2_rigged.glb"}, name="mein_gesamtkonstrukt_planer_char_glb_frau_v2"),
    path("Mein-Gesamtkonstrukt-planer/static/daniel_char_maennlich_v1_rigged.glb", schrottplatz_character_glb, {"filename": "daniel_char_maennlich_v1_rigged.glb"}, name="mein_gesamtkonstrukt_planer_char_glb_maennlich_v1"),
    path("Mein-Gesamtkonstrukt-planer/static/daniel_char_savage_codex.glb", schrottplatz_character_glb, {"filename": "daniel_char_savage_codex.glb"}, name="mein_gesamtkonstrukt_planer_char_glb_savage_codex"),
    path("admin/", admin.site.urls),
    path("health/", views.health, name="health"),
    path("api/v1/terms/", views.api_terms, name="api_terms"),
    path("api/v1/terms/<slug:slug>/", views.api_term, name="api_term"),
    path("replica-redteam-22/", replica_redteam, name="replica_redteam"),
    path("replica-redteam-22-mobile-app/", replica_redteam_mobile, name="replica_redteam_mobile"),
    path("replica-redteam-22-mobile-test/", replica_redteam_mobile_test, name="replica_redteam_mobile_test"),
    path("", views.root_redirect, name="root_redirect"),
    path("<str:lang>/", include(("lexicon.urls", "lexicon"), namespace="lexicon")),
]
