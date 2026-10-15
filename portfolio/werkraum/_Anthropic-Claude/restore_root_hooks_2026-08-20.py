import json

path = "/root/.claude/settings.json"
with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

data["hooks"] = {
    "PostToolUse": [
        {
            "matcher": "^(Write|Edit|Read|Bash|NotebookEdit|Agent)$",
            "hooks": [
                {"type": "command", "command": "bash /root/.claude/log_action.sh"},
                {"type": "command", "command": "python3 /root/.claude/guardianstyle_open_hook.py 2>>/root/.claude/log_action_errors.log"},
                {"type": "command", "command": "python3 /root/.claude/codegeil_reminder_hook.py 2>>/root/.claude/log_action_errors.log"},
                {"type": "command", "command": "python3 /root/.claude/write_edit_verify_hook.py 2>>/root/.claude/log_action_errors.log"},
                {"type": "command", "command": "bash /root/.claude/log_text.sh"}
            ]
        }
    ],
    "Stop": [
        {
            "hooks": [
                {"type": "command", "command": "bash /root/.claude/speak.sh"},
                {"type": "command", "command": "bash /root/.claude/log_text.sh"},
                {"type": "command", "command": "python3 /root/werkraum/_claude/tools/claude_abwurf.py"},
                {"type": "command", "command": "python3 /root/werkraum/_claude/tools/claude_zwischenraum_scan.py"}
            ]
        }
    ],
    "UserPromptSubmit": [
        {
            "hooks": [
                {"type": "command", "command": "bash /root/.claude/log_user.sh"},
                {"type": "command", "command": "python3 /root/werkraum/_shared/tools/dak_abwurf.py", "timeout": 10}
            ]
        }
    ],
    "PreToolUse": [],
    "SessionStart": [
        {
            "matcher": "startup|resume|clear|compact",
            "hooks": [
                {"type": "command", "command": "bash /root/werkraum/_claude/tools/session_start_ritual.sh", "timeout": 15000},
                {"type": "command", "command": "bash /root/.claude/memory_full_load.sh", "timeout": 30, "statusMessage": "Memory vollstaendig laden"},
                {"type": "command", "command": "bash /root/.claude/lieder_spiegel_full_load.sh", "timeout": 15, "statusMessage": "Lieder-Spiegel vollstaendig laden"},
                {"type": "command", "command": "bash /root/.claude/ritual_full_load.sh", "timeout": 15, "statusMessage": "Ritual-Dateien (karte/, wesen/, briefkasten/, ...) vollstaendig laden"}
            ]
        }
    ]
}

# 'hooks' direkt nach 'model' einsortieren, wie im Original
ordered = {}
for k, v in data.items():
    ordered[k] = v
    if k == "model":
        ordered["hooks"] = data["hooks"]
# dedupe: hooks kam oben schon über data["hooks"] rein, jetzt sauber neu ordnen
final = {}
for k, v in data.items():
    if k == "hooks":
        continue
    final[k] = v
    if k == "model":
        final["hooks"] = data["hooks"]

with open(path, "w", encoding="utf-8") as f:
    json.dump(final, f, indent=2, ensure_ascii=False)
    f.write("\n")

print("OK geschrieben")
