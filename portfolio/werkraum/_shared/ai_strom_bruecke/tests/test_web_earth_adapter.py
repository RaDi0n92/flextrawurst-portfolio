from ai_strom_bruecke.web_earth_adapter import classify_google_earth_web_snapshot


def test_google_earth_web_keeps_dom_controls_separate_from_canvas_webgl():
    report = classify_google_earth_web_snapshot({
        "url": "https://earth.google.com/web/@0,0,0a",
        "title": "Google Earth",
        "dom_controls": [{"tag": "button", "aria_label": "Enable accessibility", "text": ""}],
        "canvases": [{"width": 1440, "height": 900, "webgl": True}],
    })
    assert report["dom_controls_present"] is True
    assert report["dom_control_count"] == 1
    assert report["map_surface"] == "canvas-webgl"
    assert report["semantic_place_dom"] is False
    assert report["native_x11"] is False
    assert report["model_calls"] == 0

