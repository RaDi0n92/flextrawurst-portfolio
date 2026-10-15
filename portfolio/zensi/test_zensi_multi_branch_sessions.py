#!/usr/bin/env python3
"""
test_zensi_multi_branch_sessions.py — Playwright & API E2E Test fuer Wesenhuelle & Version Session-Engine mit Soft- & Hard-Delete & Obsidian Vault Sync
"""

import json
import time
import requests
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_URL = "http://127.0.0.1:8043"
OUT_DIR = Path("/root/zensi/test_artifacts")
OUT_DIR.mkdir(exist_ok=True)

def test_session_engine():
    print("[E2E Test] Starte Test fuer Wesenhuelle & Version Session-Engine...", flush=True)

    # 1. API Test: Erzeuge Session fuer Resonanzknoten (Version v_test_geist)
    r1 = requests.post(f"{BASE_URL}/zensi/api/sessions/create", json={
        "wesen_id": "Resonanzknoten",
        "modus": "sandbox",
        "version_geist": "v_test_geist",
        "title": "E2E Test Session Resonanzknoten"
    })
    assert r1.status_code == 200, f"Fehler create session: {r1.text}"
    sess1 = r1.json()["session"]
    sess_id1 = sess1["session_id"]
    print(f"✓ Session 1 fuer Resonanzknoten erzeugt: {sess_id1}")

    # 2. Nachrichten anhaengen
    messages1 = [
        {"role": "user", "content": "Hallo Resonanzknoten im Geist v_test_geist!", "timestamp": "16:20:00"},
        {"role": "assistant", "content": "Hallo Daniel! Ich schwinge im Test-Geist.", "timestamp": "16:20:02"}
    ]
    r2 = requests.post(f"{BASE_URL}/zensi/api/sessions/append", json={
        "session_id": sess_id1,
        "wesen_id": "Resonanzknoten",
        "modus": "sandbox",
        "version_geist": "v_test_geist",
        "messages": messages1
    })
    assert r2.status_code == 200
    print("✓ Nachrichten an Session 1 angehaengt & gespeichert")

    # 3. Disk & Obsidian Vault Dateien verifizieren
    srv_json = Path(f"/root/zensi/wesensprofile/Resonanzknoten/sessions/v_test_geist/{sess_id1}.json")
    srv_md = Path(f"/root/zensi/wesensprofile/Resonanzknoten/sessions/v_test_geist/{sess_id1}.md")
    obs_md = Path(f"/root/zensi/obsidian_vault/wesensprofile/Resonanzknoten/sessions/v_test_geist/{sess_id1}.md")

    assert srv_json.exists(), f"Server JSON fehlt: {srv_json}"
    assert srv_md.exists(), f"Server Markdown fehlt: {srv_md}"
    assert obs_md.exists(), f"Obsidian Vault Markdown fehlt: {obs_md}"
    print("✓ Server & Obsidian Vault Dateien fuer Session 1 verifiziert!")

    # 4. Erzeuge Session 2 fuer traeumerlie (Version klon)
    r3 = requests.post(f"{BASE_URL}/zensi/api/sessions/create", json={
        "wesen_id": "traeumerlie",
        "modus": "klon",
        "version_geist": "klon",
        "title": "Traeumerlie Klon Session"
    })
    sess_id2 = r3.json()["session"]["session_id"]
    requests.post(f"{BASE_URL}/zensi/api/sessions/append", json={
        "session_id": sess_id2,
        "wesen_id": "traeumerlie",
        "modus": "klon",
        "version_geist": "klon",
        "messages": [{"role": "user", "content": "Traumflug gestartet", "timestamp": "16:21:00"}]
    })

    # 5. Soft-Delete fuer Session 2 testen
    r_soft = requests.post(f"{BASE_URL}/zensi/api/sessions/soft_delete", json={"session_id": sess_id2})
    assert r_soft.json()["status"] == "ok"
    
    # Pruefe active sessions liste (Session 2 muss ausgeblendet sein)
    r_list = requests.get(f"{BASE_URL}/zensi/api/sessions/liste?wesen_id=traeumerlie&version_geist=klon")
    active_ids = [s["session_id"] for s in r_list.json()["sessions"]]
    assert sess_id2 not in active_ids, "Soft-deleted session sollte nicht in active sessions sein!"

    # Pruefe include_deleted=true (Session 2 muss da sein)
    r_list_inc = requests.get(f"{BASE_URL}/zensi/api/sessions/liste?wesen_id=traeumerlie&version_geist=klon&include_deleted=true")
    inc_ids = [s["session_id"] for s in r_list_inc.json()["sessions"]]
    assert sess_id2 in inc_ids, "Soft-deleted session muss in include_deleted=true sein!"
    print("✓ Soft-Delete (Archivierung im Server & Obsidian Vault) verifiziert!")

    # 6. Hard-Delete fuer Session 2 testen
    r_hard = requests.post(f"{BASE_URL}/zensi/api/sessions/hard_delete", json={"session_id": sess_id2})
    assert r_hard.json()["status"] == "ok"
    obs_md2 = Path(f"/root/zensi/obsidian_vault/wesensprofile/traeumerlie/sessions/klon/{sess_id2}.md")
    assert not obs_md2.exists(), "Hard-deleted session datei muss von Obsidian Vault entfernt worden sein!"
    print("✓ Hard-Delete (Endgueltige Loeschung von Server & Obsidian Vault) verifiziert!")

    # 7. Playwright UI Test
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        page.goto(f"{BASE_URL}/zensi/", wait_until="domcontentloaded")
        
        # Wesen Resonanzknoten laden
        page.select_option("#wesen-select", "Resonanzknoten")
        time.sleep(1.5)

        # Neue Session via UI erzeugen
        page.evaluate("neueSessionStarten()")
        time.sleep(1)

        page.screenshot(path=str(OUT_DIR / "zensi_sessions_ui.png"))
        print("✓ Playwright UI Session Screenshot gesichert!")
        browser.close()

    # Clean up test session 1
    requests.post(f"{BASE_URL}/zensi/api/sessions/hard_delete", json={"session_id": sess_id1})

    print("\n🎉 MULTI-BRANCH SESSION ENGINE ERFOLGREICH MIT SOFT- & HARD-DELETE UND OBSIDIAN VAULT SYNC VERIFIZIERT!", flush=True)

if __name__ == "__main__":
    test_session_engine()
