import json

path = "/root/.claude/settings.json"
with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

hooks = data.get("hooks", {})

# PostToolUse: Guardianstyle-Trio raus (guardianstyle_open_hook.py, codegeil_reminder_hook.py,
# write_edit_verify_hook.py), log_action.sh + log_text.sh bleiben.
ptu = hooks.get("PostToolUse", [])
if ptu:
    keep_substrings = ("log_action.sh", "log_text.sh")
    entry = ptu[0]
    entry["hooks"] = [
        h for h in entry.get("hooks", [])
        if any(s in h.get("command", "") for s in keep_substrings)
    ]

# SessionStart: komplett leeren (session_start_ritual.sh, memory_full_load.sh,
# lieder_spiegel_full_load.sh, ritual_full_load.sh raus), bis CLAUDE.md/Memory neu geschrieben sind.
hooks["SessionStart"] = []

# Stop, UserPromptSubmit, PreToolUse unveraendert lassen (speak.sh, log_text.sh, claude_abwurf.py,
# claude_zwischenraum_scan.py, log_user.sh, dak_abwurf.py bleiben aktiv).

data["hooks"] = hooks

with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
    f.write("\n")

print("OK geschrieben")
print("PostToolUse hooks jetzt:", [h["command"] for h in data["hooks"]["PostToolUse"][0]["hooks"]])
print("SessionStart jetzt:", data["hooks"]["SessionStart"])
