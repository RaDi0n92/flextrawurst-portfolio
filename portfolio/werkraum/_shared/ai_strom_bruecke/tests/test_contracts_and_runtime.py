from __future__ import annotations

import io
import json
import threading
import time

from PIL import Image, ImageDraw

from ai_strom_bruecke.actions import ActionExecutor, RecordingBackend
from ai_strom_bruecke.contracts import ActionExpectation, ActionPhase, CoordinateKind, DiffKind
from ai_strom_bruecke.earth_perception import coordinate_plausible, parse_earth_status_text
from ai_strom_bruecke.timeline import FrameTimeline, compare_frames
from ai_strom_bruecke.tri_leib import build_tri_view_capsule, validate_tri_view_object
from ai_strom_bruecke.object_store import TriViewObjectStore
from ai_strom_bruecke.native_proxy import native_claim_to_capsule
from ai_strom_bruecke.web_dom_adapter import capture_page_objects, extract_page_objects
from ai_strom_bruecke.anchors import AnchorStore, validate_anchor_candidate
from ai_strom_bruecke.analysis_overlay import render_analysis_overlay
from ai_strom_bruecke.network_guard import runtime_status, scan_sources
from ai_strom_bruecke.world_flow import WorldFlow
from ai_strom_bruecke.camera_analysis import build_camera_state, calibrate_pointer, center_claim_from_pointer, classify_camera
from ai_strom_bruecke.render_surface import RenderMetrics, human_surface_from_object
from ai_strom_bruecke.web_dom_adapter import install_mutation_stream, read_mutations, read_rrweb_events
from ai_strom_bruecke.organ_effects import derive_effects
from ai_strom_bruecke.web_session import WebDomSession
from ai_strom_bruecke.inventory import build_inventory


def png(color: str, marker: int = 0) -> bytes:
    image = Image.new("RGB", (96, 64), color)
    draw = ImageDraw.Draw(image)
    draw.rectangle((marker, 0, marker + 7, 63), fill="white")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_atomic_json_write_survives_concurrent_writers(tmp_path):
    from ai_strom_bruecke import bridge

    path = tmp_path / "state.json"

    def write(index):
        for iteration in range(20):
            bridge._write_json(path, {"writer": index, "iteration": iteration})

    workers = [threading.Thread(target=write, args=(index,)) for index in range(6)]
    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join()

    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["writer"] in range(6)
    assert value["iteration"] in range(20)
    assert not list(tmp_path.glob("*.tmp"))


def test_timeline_keeps_duplicate_as_evidence(tmp_path):
    timeline = FrameTimeline(retention_seconds=60, fps=10, frame_dir=tmp_path)
    first = timeline.ingest(png("black"), target="google-earth")
    duplicate = timeline.ingest(png("black"), target="google-earth")
    moved = timeline.ingest(png("black", 30), target="google-earth")
    assert first.envelope.sequence == 1
    assert duplicate.envelope.duplicate_of == first.envelope.frame_id
    assert duplicate.envelope.freshness == "duplicate"
    assert moved.envelope.duplicate_of is None
    assert len(list(tmp_path.glob("*.png"))) == 3


def test_compare_frames_distinguishes_no_change_and_motion():
    unchanged = compare_frames(png("black"), png("black"))
    moved = compare_frames(png("black"), png("black", 30))
    popup = compare_frames(png("black"), png("black"), popup_after=True)
    assert unchanged.kind == DiffKind.UNCHANGED
    assert moved.kind in {DiffKind.MINOR_CHANGE, DiffKind.CAMERA_MOVED}
    assert popup.kind == DiffKind.POPUP_APPEARED


def test_coordinate_claim_preserves_source_and_pointer_kind():
    claim = parse_earth_status_text(
        "51°16'55\"N 7°17'46\"O Höhe 173 m",
        frame_id="frame-1",
        pointer_xy={"x": 840, "y": 208},
    )
    assert claim.latitude is not None and abs(claim.latitude - 51.281944) < 0.00001
    assert claim.longitude is not None and abs(claim.longitude + 7.296111) < 0.00001
    assert claim.coordinate_kind == CoordinateKind.POINTER
    assert claim.source == "earth-statusbar-ocr"
    assert coordinate_plausible(claim)


def test_held_gesture_always_releases_button(tmp_path):
    backend = RecordingBackend()
    executor = ActionExecutor(backend, lease_path=tmp_path / "lease.lock")
    transaction = executor.gesture(
        actor="test",
        target="google-earth",
        points=[(1, 2), (4, 5), (8, 9)],
        hold_delay_s=0,
        expectation=ActionExpectation(explanation="test gesture"),
    )
    assert transaction.phase == ActionPhase.DISPATCHED
    assert [call[0] for call in backend.calls] == ["move", "mousedown", "move", "move", "mouseup"]
    acknowledged = executor.acknowledge(
        transaction,
        accepted=True,
        frame_ids=["frame-2"],
        evidence={"diff": "camera-moved"},
    )
    assert acknowledged.phase == ActionPhase.ACCEPTED
    assert acknowledged.observed_frames == ["frame-2"]


def test_key_hold_releases_on_normal_exit(tmp_path):
    backend = RecordingBackend()
    executor = ActionExecutor(backend, lease_path=tmp_path / "lease.lock")
    transaction = executor.key_hold(actor="test", target="google-earth", key="w", duration_s=0.001)
    assert transaction.phase == ActionPhase.DISPATCHED
    assert backend.calls[0] == ("keydown", "w")
    assert backend.calls[-1] == ("keyup", "w")


def test_triview_is_atomic_and_has_rot_block():
    obj = build_tri_view_capsule(
        {
            "object_id": "splitter_7281",
            "type": "splitter",
            "html_fragment": "<div data-id='splitter_7281'></div>",
            "actions": ["lesen", "berühren"],
            "provenance": ["post_3093"],
            "linked_organs": ["kompoase", "gruppen"],
        },
        dom_kind="real",
    )
    validate_tri_view_object(obj)
    value = obj.to_dict()
    assert set(value) >= {"codewesen_leib", "menschen_leib", "organ_leib"}
    assert value["rot_block"]
    assert value["codewesen_leib"]["forbidden_context"] == value["rot_block"]


def test_triview_native_proxy_requires_confidence():
    obj = build_tri_view_capsule(
        {"id": "earth-label", "type": "native-label"},
        context={"dom_confidence": 0.87, "dom_source": "earth-statusbar-ocr"},
        dom_kind="semantic-proxy",
    )
    assert obj.codewesen_leib["dom_kind"] == "semantic-proxy"
    assert obj.codewesen_leib["confidence"] == 0.87


def test_triview_object_store_is_append_only_and_versioned(tmp_path):
    store = TriViewObjectStore(tmp_path / "objects.jsonl")
    first = store.create({"id": "post-1", "type": "post", "provenance": ["human-1"]})
    second = store.update("post-1", {"type": "post", "scene": "warm", "provenance": ["event-2"]})
    assert first["version"] == 1
    assert second["version"] == 2
    assert len((tmp_path / "objects.jsonl").read_text(encoding="utf-8").splitlines()) == 2
    assert store.get("post-1")["organ_leib"]["provenance_effect"]["sources"][-1] == "event-2"


def test_playwright_real_dom_is_extracted_into_all_three_leiber(tmp_path):
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_content(
            """
            <main>
              <article id="post-card" data-fw-object-id="post-1"
                       data-fw-object-type="post"
                       data-fw-provenance="post-1,event-2"
                       data-fw-organs="kompoase,gruppen">
                <h2>Ein echter DOM-Post</h2>
                <button aria-label="Antworten">Antworten</button>
              </article>
            </main>
            """
        )
        extracted = extract_page_objects(page)
        store = TriViewObjectStore(tmp_path / "objects.jsonl")
        captured = capture_page_objects(page, store)
        browser.close()

    assert extracted[0]["object_id"] == "post-1"
    assert extracted[0]["dom_path"] == '[data-fw-object-id="post-1"]'
    assert "Ein echter DOM-Post" in extracted[0]["html_fragment"]
    assert extracted[0]["actions"][0]["label"] == "Antworten"
    assert captured[0]["codewesen_leib"]["dom_kind"] == "real"
    assert captured[0]["codewesen_leib"]["dom_path"] == '[data-fw-object-id="post-1"]'
    assert captured[0]["menschen_leib"]["scene"] == "DOM-Objekt post-1"
    assert captured[0]["organ_leib"]["provenance_effect"]["sources"] == ["post-1", "event-2"]
    validate_tri_view_object(captured[0])


def test_native_proxy_keeps_native_source_and_rot_boundary():
    claim = parse_earth_status_text(
        "51°16'55\"N 7°17'46\"O Höhe 173 m",
        frame_id="frame-9",
        pointer_xy={"x": 840, "y": 208},
    )
    capsule = native_claim_to_capsule(
        object_id="earth-conti",
        object_type="native-label",
        label="Eismanufaktur Gelateria Conti",
        window_id="559",
        frame_id="frame-9",
        claim=claim,
        actions=["zoom", "mittelmaus-halten"],
        provenance=["x11", "google-earth"],
    )
    validate_tri_view_object(capsule)
    assert capsule["codewesen_leib"]["dom_kind"] == "semantic-proxy"
    assert capsule["codewesen_leib"]["html_fragment"] == ""
    assert capsule["codewesen_leib"]["confidence"] == claim.confidence
    assert capsule["codewesen_leib"]["source"] == claim.source
    assert "nicht_als_html_dom_behaupten" in capsule["rot_block"]


def test_anchor_requires_pointer_claim_and_keeps_evidence(tmp_path):
    claim = parse_earth_status_text("51°16'55\"N 7°17'46\"O Höhe 173 m", frame_id="frame-a", pointer_xy={"x": 10, "y": 20})
    camera = {"state_id": "camera-a", "frame_id": "frame-a", "target": "google-earth", "pointer_anchor": claim.to_dict()}
    anchor = AnchorStore(tmp_path / "anchors.jsonl").create(
        label="Conti", claim=claim, camera=camera, frame_id="frame-a", frame_digest="digest-a", provenance=["earth"]
    )
    assert anchor["status"] == "confirmed"
    assert anchor["claim"]["coordinate_kind"] == "pointer"
    assert anchor["provenance"][-2:] == ["frame-a", claim.claim_id]
    assert len((tmp_path / "anchors.jsonl").read_text(encoding="utf-8").splitlines()) == 1


def test_fw27_anchor_guard_rejects_bad_ocr_center_edge_scene_and_unchanged_frame(tmp_path):
    claim = parse_earth_status_text(
        "51°16'55\"N 7°17'46\"O", frame_id="frame-fw27", pointer_xy={"x": 500, "y": 300}
    )
    base_camera = {
        "state_id": "camera-fw27", "frame_id": "frame-fw27", "target": "google-earth",
        "map_bounds": {"left": 100, "top": 50, "right": 1000, "bottom": 700},
    }
    bad = dict(claim.to_dict(), latitude=None, normalized_text="unparsed")
    assert "coordinate-invalid-or-unparsed" in validate_anchor_candidate(bad, base_camera, frame_id="frame-fw27")["reasons"]
    center = dict(claim.to_dict(), coordinate_kind="center")
    assert "coordinate-is-not-pointer-claim" in validate_anchor_candidate(center, base_camera, frame_id="frame-fw27")["reasons"]
    edge = dict(claim.to_dict(), pointer_xy={"x": 105, "y": 300})
    assert "pointer-at-map-edge-or-outside-safe-rect" in validate_anchor_candidate(edge, base_camera, frame_id="frame-fw27")["reasons"]
    forest = dict(base_camera, scene_context="forest", target_label_visible=False)
    assert "scene-needs-visible-target-label" in validate_anchor_candidate(claim, forest, frame_id="frame-fw27")["reasons"]
    unchanged = dict(base_camera, frame_diff={"kind": "unchanged"})
    assert "evidence-frame-unchanged" in validate_anchor_candidate(claim, unchanged, frame_id="frame-fw27")["reasons"]
    accepted = validate_anchor_candidate(claim, dict(base_camera, scene_context="forest", target_label_visible=True, frame_diff={"kind": "camera-moved"}), frame_id="frame-fw27")
    assert accepted["accepted"] is True
    anchor = AnchorStore(tmp_path / "fw27-anchors.jsonl").create(
        label="Conti", claim=claim, camera=base_camera, frame_id="frame-fw27", frame_digest="digest-fw27"
    )
    assert anchor["status"] == "confirmed"


def test_overlay_is_a_distinct_visible_evidence_frame():
    original = png("black")
    overlay = render_analysis_overlay(original, pointer_xy={"x": 20, "y": 20}, target_xy={"x": 40, "y": 40}, label="proof")
    assert overlay != original
    assert Image.open(io.BytesIO(overlay)).size == (96, 64)


def test_world_flow_updates_all_leiber_and_emits_causal_event(tmp_path):
    store = TriViewObjectStore(tmp_path / "objects.jsonl")
    flow = WorldFlow(store, tmp_path / "world-events.jsonl")
    obj, created = flow.create({"object_id": "splitter-1", "object_type": "splitter", "provenance": ["post-1"], "scene": "roh"})
    updated, event = flow.apply(
        obj["object_id"], source="codewesen.action", action_id="action-1",
        human_effect={"scene": "sichtbar bewegt", "motion": "lebt", "interaction": ["berühren"]},
        organ_effect={"splitter_effect": {"merged": True}, "resonance_effect": {"fresh_capsule": True}},
    )
    assert created["after_state"]["version"] == 1
    assert updated["version"] == 2
    assert updated["menschen_leib"]["scene"] == "sichtbar bewegt"
    assert updated["organ_leib"]["splitter_effect"]["merged"] is True
    assert event["human_effect"]["motion"] == "lebt"
    assert event["codewesen_effect"]["fresh_capsule"] is True
    assert len(flow.all_events()) == 2


def test_platform_organ_families_are_explicit_not_hidden_side_effects():
    for object_type, expected_key in {
        "post": "kompoase_effect", "splitter": "splitter_effect", "group": "groups_effect",
        "shadow-comment": "shadow_effect", "kompoase": "kompoase_effect", "profile": "profile_effect",
    }.items():
        effects = derive_effects(object_type)
        assert effects[expected_key]["status"] == "linked"
        assert effects[expected_key]["object_type"] == object_type


def test_model_free_runtime_guard_has_no_forbidden_source_findings(tmp_path):
    source = tmp_path / "safe.py"
    source.write_text("def capture():\n    return 0\n", encoding="utf-8")
    assert scan_sources([source]) == []
    assert runtime_status()["llm_calls"] == 0


def test_control_cli_gesture_records_dispatch_ack_and_release(tmp_path, monkeypatch, capsys):
    import ai_strom_bruecke.bridge as bridge

    backend = RecordingBackend()
    before_path = tmp_path / "before.png"
    before_path.write_bytes(png("black"))
    bridge.LOCK = tmp_path / "control.lock"
    bridge.ACTIONS = tmp_path / "actions.jsonl"
    bridge.STATE = tmp_path / "state.json"
    monkeypatch.setattr(bridge, "XdotoolBackend", lambda **_: backend)
    monkeypatch.setattr(bridge, "_capture_for_action", lambda target: (before_path, png("black")))
    monkeypatch.setattr(bridge, "_acknowledge_native_action", lambda transaction, before, target, wait_ms: bridge.ActionExecutor.acknowledge(transaction, accepted=True, frame_ids=["frame-after"], evidence={"diff": "camera-moved"}))
    args = bridge.parser().parse_args([
        "control", "gesture", "--lease", "--unsafe-no-vision-gate", "--target", "active",
        "--points", "10,10;20,20;30,25", "--hold-delay-ms", "0",
    ])
    assert bridge.run_control(args) == 0
    output = capsys.readouterr().out
    assert '"phase": "accepted"' in output
    assert [call[0] for call in backend.calls] == ["move", "mousedown", "move", "move", "mouseup"]
    action = json.loads((tmp_path / "actions.jsonl").read_text(encoding="utf-8").splitlines()[-1])
    assert action["phase"] == "accepted"
    assert action["observed_frames"] == ["frame-after"]
    assert action["held_buttons"] == []


def test_control_cli_stop_releases_all_native_holds(tmp_path, monkeypatch):
    import ai_strom_bruecke.bridge as bridge

    calls = []
    bridge.ACTIONS = tmp_path / "actions.jsonl"
    monkeypatch.setattr(bridge, "_xdotool", lambda *args: calls.append(args) or "")
    args = bridge.parser().parse_args(["control", "stop", "--lease", "--target", "active"])
    assert bridge.run_control(args) == 0
    assert ("mouseup", "1") in calls and ("mouseup", "3") in calls
    assert ("keyup", "w") in calls and ("keyup", "d") in calls
    event = json.loads((tmp_path / "actions.jsonl").read_text(encoding="utf-8").splitlines()[-1])
    assert event["phase"] == "accepted"
    assert len(event["released"]) >= 7


def test_legacy_control_commands_share_transaction_path(tmp_path, monkeypatch, capsys):
    import ai_strom_bruecke.bridge as bridge

    backend = RecordingBackend()
    before_path = tmp_path / "before.png"
    before_path.write_bytes(png("black"))
    bridge.LOCK = tmp_path / "control.lock"
    bridge.ACTIONS = tmp_path / "actions.jsonl"
    bridge.STATE = tmp_path / "state.json"
    monkeypatch.setattr(bridge, "XdotoolBackend", lambda **_: backend)
    monkeypatch.setattr(bridge, "_capture_for_action", lambda target: (before_path, png("black")))
    monkeypatch.setattr(bridge, "_xdotool", lambda *args: "X=5\nY=7\n" if args[:1] == ("getmouselocation",) else "")
    monkeypatch.setattr(bridge, "_acknowledge_native_action", lambda transaction, before, target, wait_ms: bridge.ActionExecutor.acknowledge(transaction, accepted=True, frame_ids=["frame-after"], evidence={"diff": "minor-change"}))
    for command in (["move", "30", "40"], ["click", "30", "40"], ["key", "Page_Up"], ["type", "hello"]):
        args = bridge.parser().parse_args(["control", *command, "--lease", "--unsafe-no-vision-gate"])
        assert bridge.run_control(args) == 0
        assert '"phase": "accepted"' in capsys.readouterr().out
    names = [call[0] for call in backend.calls]
    assert "move" in names and "click" in names and "key" in names and "type" in names
    assert all(json.loads(line)["phase"] == "accepted" for line in (tmp_path / "actions.jsonl").read_text(encoding="utf-8").splitlines())


def test_camera_distinguishes_pointer_center_focus_popup_and_local_calibration():
    first = parse_earth_status_text("51°16'55\"N 7°17'46\"O", frame_id="f1", pointer_xy={"x": 100, "y": 100})
    second = parse_earth_status_text("51°16'56\"N 7°17'45\"O", frame_id="f2", pointer_xy={"x": 110, "y": 90})
    center = center_claim_from_pointer(first, frame_id="f2")
    camera = build_camera_state(frame_id="f2", target="google-earth", pointer_claim=second, center_claim=center, zoom=173, popup="popup-1", focus=True)
    assert camera.pointer_anchor.coordinate_kind == CoordinateKind.POINTER
    assert camera.map_center.coordinate_kind == CoordinateKind.CENTER
    assert camera.popup == "popup-1"
    assert "d_lon_per_pixel" in calibrate_pointer(first, second)
    assert classify_camera(focus=False, popup=None, loading=False, frame_available=True)["state"] == "focus-lost"
    assert classify_camera(focus=True, popup=None, loading=False, frame_available=False)["state"] == "window-closed"


def test_render_metrics_are_measured_and_8k_66fps_is_not_falsely_claimed():
    metrics = RenderMetrics()
    metrics.record(now=1.0, previous_at=None, width=1920, height=816)
    metrics.record(now=1.02, previous_at=1.0, width=1920, height=816)
    value = metrics.to_dict()
    assert value["fps"] == 50.0
    assert value["target_fps"] == 66
    assert value["target_resolution"] == "8K"
    assert value["target_status"] == "measured-below-target"
    assert value["target_met"] is False
    assert metrics.meets_target() is False
    surface = human_surface_from_object({"object_id": "x", "menschen_leib": {"scene": "scene", "render_metrics": value}})
    assert surface["render_metrics"]["fps"] == 50.0


def test_playwright_mutation_stream_reports_fresh_dom_change():
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_content('<article data-fw-object-id="post-m"><span id="text">alt</span></article>')
        install_mutation_stream(page)
        page.locator("#text").evaluate("node => node.textContent = 'neu'")
        page.wait_for_timeout(20)
        changes = read_mutations(page)
        rrweb = read_rrweb_events(page)
        browser.close()
    assert changes
    assert changes[0]["object_id"] == "post-m"
    assert changes[0]["kind"] in {"characterData", "childList"}
    assert rrweb[0]["type"] == 3
    assert rrweb[0]["data"]["source"] == 0


def test_web_dom_session_recovers_and_checks_out_fresh_version(tmp_path):
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_content('<article data-fw-object-id="recover-1" data-fw-object-type="post"><span>eins</span></article>')
        session = WebDomSession(page, TriViewObjectStore(tmp_path / "objects.jsonl"))
        first = session.checkout()
        page.set_content('<article data-fw-object-id="recover-1" data-fw-object-type="post"><span>zwei</span></article>')
        recovered = session.recover(page)
        second = session.checkout()
        browser.close()
    assert first["objects"][0]["version"] == 1
    assert recovered["recovered"] is True
    assert second["objects"][0]["version"] == 2
    assert "zwei" in second["objects"][0]["codewesen_leib"]["html_fragment"]
    assert second["mirror_schema"] == "rrweb-compatible.v1"


def test_inventory_keeps_v1_and_additive_v2_paths_visible():
    inventory = build_inventory(__import__("pathlib").Path(__file__).resolve().parents[1])
    assert inventory["compatibility"] == "additive-v2-no-v1-removal"
    assert all(item["present"] for item in inventory["v1"]["paths"] if item["path"] not in {"events.jsonl", "state.json", "latest.png"})
    assert any(item["path"] == "web_dom_adapter.py" and item["present"] for item in inventory["v2"]["paths"])


def test_requirement_registry_has_source_reference_for_every_input():
    from ai_strom_bruecke.requirements import summary

    report = summary()
    assert report["total"] == 72
    assert all(item["source_refs"] for item in report["items"])
    assert all("DOKUMENTATION.md" in item["source_refs"][0] for item in report["items"])


def test_bridge_records_earth_claim_and_camera_state(tmp_path, monkeypatch):
    import ai_strom_bruecke.bridge as bridge

    output = tmp_path / "frame.png"
    output.write_bytes(png("black"))
    state_path = tmp_path / "state.json"
    timeline_path = tmp_path / "timeline.json"
    bridge.STATE = state_path
    bridge.TIMELINE_JSON = timeline_path
    bridge.ACTIONS = tmp_path / "actions.jsonl"
    bridge.FRAME_TIMELINE = FrameTimeline(retention_seconds=60, fps=10, frame_dir=tmp_path / "frames")
    bridge.LAST_FRAME_PAYLOAD = None
    bridge.LAST_OCR_CLAIM = None
    bridge.LAST_OCR_AT = 0.0
    monkeypatch.setattr(bridge, "_xdotool", lambda *args: "X=42\nY=24\nSCREEN=0\nWINDOW=559\n")
    monkeypatch.setattr(bridge, "ocr_status_bar", lambda *args, **kwargs: "51°16'55\"N 7°17'46\"O Höhe 173 m")

    bridge._record_frame(output, "google-earth")
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["frame_sequence"] == 1
    assert state["claims"][0]["pointer_xy"] == {"x": 42, "y": 24}
    assert state["camera"]["target"] == "google-earth"
    assert state["camera"]["pointer_anchor"]["confidence"] > 0


def test_capture_error_closes_gate_without_erasing_last_frame(tmp_path):
    import ai_strom_bruecke.bridge as bridge

    bridge.STATE = tmp_path / "state.json"
    bridge.STATE.write_text(json.dumps({"frame_sequence": 9, "frame_id": "frame-9", "gate": {"allow_input": True}}), encoding="utf-8")
    bridge._record_capture_error("active", RuntimeError("window closed"))
    state = json.loads(bridge.STATE.read_text(encoding="utf-8"))
    assert state["frame_sequence"] == 9
    assert state["frame_id"] == "frame-9"
    assert state["gate"]["allow_input"] is False
    assert state["capture_error"] == "window closed"
