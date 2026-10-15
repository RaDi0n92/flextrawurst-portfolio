#!/usr/bin/env python3
"""
test_provenienz_and_export.py — Testsuite für 100% Provenienz, Markdown Export/Import & LangGraph/DB Export.
"""
import sys
import json
import urllib.request
import urllib.parse

BASE_URL = "http://127.0.0.1:8043"

def test_api():
    print("⚡ Starte Zensi Provenienz & Export/Import E2E Tests...")

    # 1. Physiologie Status
    req = urllib.request.urlopen(f"{BASE_URL}/api/physiologie/status")
    res = json.loads(req.read().decode("utf-8"))
    assert res["status"] == "ok"
    print("✅ 1. Physiologie Status API OK:", res["physiologie"]["koerperstimme"])

    # 2. Session Export als Markdown
    req = urllib.request.urlopen(f"{BASE_URL}/api/export/session/md?wesen_id=Resonanzknoten")
    md_content = req.read().decode("utf-8")
    assert "# Zensi Provenienz Chronik:" in md_content
    assert "## 🏛️ System-Prompt & VPS-Körperstimme" in md_content
    print(f"✅ 2. Session Markdown Export OK ({len(md_content)} Bytes exported)")

    # 3. Session Import aus Markdown (Roundtrip Rehydration)
    data = json.dumps({"md_content": md_content}).encode("utf-8")
    req_imp = urllib.request.Request(f"{BASE_URL}/api/import/session/md", data=data, headers={"Content-Type": "application/json"})
    res_imp = json.loads(urllib.request.urlopen(req_imp).read().decode("utf-8"))
    assert res_imp["status"] == "ok"
    print(f"✅ 3. Session Markdown Import OK (Session ID: {res_imp['session_id']}, Rehydriert)")

    # 4. LangGraph & PostgreSQL DB Export (Markdown)
    req_lg = urllib.request.urlopen(f"{BASE_URL}/api/export/langgraph_db?format=md")
    lg_md = req_lg.read().decode("utf-8")
    assert "# Zensi LangGraph & PostgreSQL Master-Audit Export" in lg_md
    print(f"✅ 4. LangGraph & DB Markdown Export OK ({len(lg_md)} Bytes exported)")

    # 5. LangGraph & DB Export (JSON)
    req_lg_json = urllib.request.urlopen(f"{BASE_URL}/api/export/langgraph_db?format=json")
    lg_json = json.loads(req_lg_json.read().decode("utf-8"))
    assert "events" in lg_json
    print(f"✅ 5. LangGraph & DB JSON Export OK ({len(lg_json['events'])} Events im Master Stream)")

    # 6. LangGraph & DB Import
    data_lg_imp = json.dumps({"content": lg_md, "format": "md"}).encode("utf-8")
    req_lg_imp = urllib.request.Request(f"{BASE_URL}/api/import/langgraph_db", data=data_lg_imp, headers={"Content-Type": "application/json"})
    res_lg_imp = json.loads(urllib.request.urlopen(req_lg_imp).read().decode("utf-8"))
    assert res_lg_imp["status"] == "ok"
    print(f"✅ 6. LangGraph & DB Import OK (Import Event ID: {res_lg_imp['history_id']})")

    print("\n🎉 ALLE 6 PROVENIENZ- & EXPORT/IMPORT-TESTS ERFOLGREICH BESTANDEN!")

if __name__ == "__main__":
    test_api()
