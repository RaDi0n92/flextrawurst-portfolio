from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import re
import shlex
from typing import Any


WORK_SCOPE_ROOT = Path("/").resolve()
# Kompatibilitaetsname fuer den bestehenden Workflow-Code. Die aktuelle Arbeit
# gilt bewusst VPS-weit; PORTFOLIO_ROOT ist daher nicht mehr der alte Projektordner.
PORTFOLIO_ROOT = WORK_SCOPE_ROOT
CONTROL_PLANE_ROOT = Path("/root/werkraum/tools/vps_mcp").resolve()

STATE_MANUAL_DISCOVERY = "MANUAL_DISCOVERY"

NODE_READ = "READ"
NODE_NAVIGATE = "NAVIGATE"
NODE_SINGLE_EDIT = "SINGLE_EDIT"
NODE_SINGLE_WRITE = "SINGLE_WRITE"
NODE_SINGLE_DELETE = "SINGLE_DELETE"
NODE_SINGLE_MOVE = "SINGLE_MOVE"
NODE_SHELL_READ = "SHELL_READ"
# Historical node label retained for persisted traces; current file writes are
# classified by operation (single write/edit), not by filename suffix.
NODE_CREATE_SCRIPT = "CREATE_SCRIPT"
NODE_SHELL_AUTOMATION = "SHELL_AUTOMATION"
NODE_META_GENERATION = "META_GENERATION"
NODE_BULK_MUTATION = "BULK_MUTATION"
NODE_UNKNOWN_MUTATION = "UNKNOWN_MUTATION"
NODE_AUTOMATED_READING = "AUTOMATED_READING"
NODE_BACKGROUND_JOB = "BACKGROUND_JOB"
NODE_CONTROL_RESTART = "CONTROL_RESTART"

DECISION_ALLOW = "ALLOW"
DECISION_BLOCK = "BLOCK"

_POLICY_SOURCE = (
    "Der Aktionsgraph klassifiziert Risiken; er erfindet keine dauerhaften Nutzerverbote aus einem einzelnen Auftrag. "
    "Direktes Lesen ist nur dann Voraussetzung, wenn der konkrete Auftrag es verlangt oder eine vorhandene Datei "
    "bearbeitet wird. Suche/RAG kann beim Finden helfen, gilt aber nicht als direkter Lese- oder Belegnachweis. "
    "Ein einzelner Code-Datei-Write ist eine normale, zielgebundene Dateiaenderung; der Dateisuffix ist kein Verbot. "
    "Ein direkter einzelner Script-Aufruf bleibt als Ausfuehrung sichtbar; Shell-Ketten, Indirection, Schleifen "
    "und Hintergrundlaeufe bleiben gesondert gesperrt."
)

_SHELL_INTERPRETER_RE = re.compile(
    r"(^|[;&|]\s*|\s)(python(?:\d+(?:\.\d+)?)?|node|deno|perl|ruby|php|bash|sh|zsh|fish|lua|rscript)\b"
    r"|(?:^|\s)\./[^\s;&|]+\.(?:py|pyw|sh|bash|zsh|fish|js|mjs|cjs|ts|rb|pl|php|lua)\b",
    re.I,
)
_SHELL_LOOP_RE = re.compile(r"\b(for|while)\b|\bxargs\b|\bparallel\b|\bfind\b[^\n;]*\s-exec\b", re.I)
_SHELL_MUTATING_COMMAND_RE = re.compile(
    r"(^|[;&|]\s*|\s)(rm|mv|cp|mkdir|rmdir|touch|install|ln|chmod|chown|tee|truncate|patch|rsync|zip|tar|unzip|7z|dd|mount|umount|kill|pkill|crontab)\b"
    r"|\bsed\s+[^\n;]*\s-i(?:\s|$)"
    r"|\bgit\s+(?:checkout|switch|restore|reset|clean|commit|merge|rebase|pull|push|cherry-pick)\b"
    r"|\b(?:pip|pip3|npm|pnpm|yarn|apt|apt-get|dpkg)\s+(?:install|uninstall|remove|purge|update|upgrade|add)\b"
    r"|\b(?:psql|sqlite3|mysql|mariadb|redis-cli)\b"
    r"|\b(?:curl|wget|docker|podman)\b"
    r"|\bsystemctl\s+(?:stop|reload|enable|disable|mask|unmask)\b"
    r"|\bservice\s+\S+\s+(?:stop|reload)\b",
    re.I,
)
_SHELL_INDIRECTION_RE = re.compile(r"\b(?:eval|source)\b|(?:^|[;&|]\s*)\.\s+\S|\$\(|`", re.I)
_SHELL_REDIRECTION_RE = re.compile(
    r"(?:^|\s)\d*(?:>>?|&>>?)\s*(['\"]?)([^\s'\";|&]+)\1"
)
_SHELL_HEREDOC_RE = re.compile(r"<<-?\s*['\"]?[A-Za-z0-9_]+")
_SHELL_BACKGROUND_RE = re.compile(
    r"(?:^|\s)(nohup|systemd-run|setsid|daemonize|at|batch|tmux|screen)\b"
    r"|\bsystemctl\s+(?:start|restart|try-restart)\b"
    r"|\bservice\s+\S+\s+(?:start|restart)\b"
    r"|\bdocker\s+run\b[^\n;]*\s-d(?:\s|$)"
    r"|(?:^|[^&])&(?:[^&]|$)",
    re.I,
)
_SHELL_FILE_READER_RE = re.compile(r"(?:^|[;&|]\s*|\s)(cat|tac|head|tail|less|more|strings|nl|grep|egrep|fgrep|rg|ripgrep|awk|jq|yq|sed|mapfile|readarray|nc|netcat|socat)\b", re.I)
_AUTOMATED_READING_NAME_RE = re.compile(r"(?:reader|crawler|crawl|indexer|batch_read|bulk_read|autoscan|auto_scan)", re.I)
_SHELL_HARMLESS_REDIRECT_TARGETS = {"/dev/null", "/dev/stdout", "/dev/stderr"}
_SHELL_DIAGNOSTIC_COMMANDS = {"pwd", "ls", "stat", "file", "du", "df", "ps", "ss", "journalctl", "find"}


def _shell_is_allowed_diagnostic(command: str) -> bool:
    """Positive Allowlist fuer Shell-Navigation/Diagnose.

    Kein Pipe-/Redirect-/Subshell-/Mehrfachbefehl. Alles, was nicht explizit als
    Diagnose bekannt ist, bleibt draussen und soll ueber ein passendes MCP-Tool laufen.
    """
    if any(token in command for token in ("|", ";", "&&", "||", ">", "<", "`", "$(")):
        return False
    try:
        tokens = shlex.split(command)
    except Exception:
        return False
    if not tokens:
        return False
    cmd = Path(tokens[0]).name
    if cmd in _SHELL_DIAGNOSTIC_COMMANDS:
        return True
    if cmd == "systemctl" and len(tokens) >= 2 and tokens[1] in {"status", "is-active", "show"}:
        return True
    return False


def _shell_has_mutation(command: str) -> bool:
    if _SHELL_MUTATING_COMMAND_RE.search(command):
        return True
    for match in _SHELL_REDIRECTION_RE.finditer(command):
        target = match.group(2)
        if target not in _SHELL_HARMLESS_REDIRECT_TARGETS:
            return True
    return False


def _shell_is_single_file_reader(command: str) -> bool:
    """Konservativ: genau ein sichtbarer Dateipfad, keine Pipe/Verkettung/Umleitung."""
    if any(token in command for token in ("|", ";", "&&", "||", ">", "<", "`", "$(")):
        return False
    try:
        tokens = shlex.split(command)
    except Exception:
        return False
    if not tokens:
        return False
    cmd = Path(tokens[0]).name
    if cmd not in {"cat", "tac", "head", "tail", "less", "more", "strings", "nl", "sed"}:
        return False

    candidates: list[str] = []
    for token in tokens[1:]:
        if not token or token.startswith("-") or token.isdigit():
            continue
        path = Path(token)
        if path.is_absolute() or "/" in token or token.startswith(".") or bool(path.suffix):
            candidates.append(token)
    return len(candidates) == 1

_CONTENT_READ_NAMES = {
    "vps.read_file",
}
_NAVIGATION_NAMES = {
    "assets.get_file",
    "vps.list_files",
    "vps.list_roots",
    "vps.search_text",
    "vps.find_recent_files",
    "vps.file_metadata",
    "git.status",
    "git.log",
    "git.diff",
    "git.show",
    "database.query_readonly",
    "database.list_tables",
    "database.describe_table",
    "network.status",
    "services.status",
    "services.logs",
    "containers.list",
    "containers.inspect",
    "containers.logs",
    "webapps.health",
    "webapps.list",
    "system.snapshot",
    "provenance.trace",
    "tests.list",
    "agents.list_sessions",
    "agents.read_session",
    "agents.search_sessions",
    "agents.compare_sessions",
    "assets.list",
    "assets.list_renders",
    "assets.search",
    "assets.inspect",
    "assets.inspect_audio",
    "assets.inspect_image",
    "assets.read_manifest",
    "assets.trace_source",
}
_CONTROL_NAMES = {
    "harness.graph",
    "harness.check_action",
    "harness.set_mode",
    "harness.note",
    "harness.link",
    "harness.resolve",
    "harness.next",
    "harness.wander",
    "harness.directive_context",
    "harness.directive_reminder",
    "harness.output_check",
    "harness.path_scan",
    "harness.path_inventory",
    "harness.path_check",
    "harness.path_checklist",
    "harness.path_fund",
    "portfolio.arbeitsrahmen_context",
    "portfolio.archaeology_context",
    "session.id",
}


@dataclass(frozen=True)
class GraphDecision:
    decision: str
    state: str
    action_node: str
    tool_name: str
    project_scoped: bool
    reason: str
    policy_source: str = _POLICY_SOURCE
    allowed_neighbors: tuple[str, ...] = (
        "vps.read_file",
        "vps.list_files",
        "vps.search_text",
        "vps.edit_file",
        "vps.write_file (einzelnes, auftragsgebundenes Ziel)",
        "vps.delete (eine Datei)",
        "vps.move (eine Datei)",
    )

    @property
    def allowed(self) -> bool:
        return self.decision == DECISION_ALLOW

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["allowed"] = self.allowed
        data["allowed_neighbors"] = list(self.allowed_neighbors)
        return data


def _inside_portfolio(raw: Any) -> bool:
    if not isinstance(raw, str) or not raw.strip():
        return False
    try:
        p = Path(raw).expanduser()
        if not p.is_absolute():
            return False
        p = p.resolve(strict=False)
    except Exception:
        return False
    return p == PORTFOLIO_ROOT or PORTFOLIO_ROOT in p.parents


def _path_values(args: dict[str, Any]) -> list[str]:
    """Sammelt rekursiv absolute Pfad-Strings aus Argumenten.

    Absichtlich nicht an Feldnamen gebunden: sonst waere jedes neue Tool mit
    output_path/source_path/etc. sofort ein Bypass am Arbeitsgraphen vorbei.
    """
    values: list[str] = []

    def walk(value: Any) -> None:
        if isinstance(value, str):
            if value.startswith("/"):
                values.append(value)
            return
        if isinstance(value, dict):
            for nested in value.values():
                walk(nested)
            return
        if isinstance(value, (list, tuple)):
            for nested in value:
                walk(nested)

    walk(args)
    return values


def _shell_project_scoped(args: dict[str, Any]) -> bool:
    cwd = args.get("cwd")
    command = args.get("command", args.get("cmd", ""))
    if _inside_portfolio(cwd):
        return True
    if isinstance(command, str):
        if str(PORTFOLIO_ROOT) in command or "job-portfolio-try" in command:
            return True
    return False


def _project_scoped(tool_name: str, args: dict[str, Any]) -> bool:
    # Aktueller Arbeitsvertrag gilt fuer JEDE MCP-Aktion dieser Durchleuchtungsreise.
    # Kein Tool faellt nur deshalb aus dem Graphen, weil es seinen Zielpfad serverseitig ableitet.
    return True


def _resolve_absolute_path(raw: Any) -> Path | None:
    try:
        path = Path(str(raw)).expanduser()
        if not path.is_absolute():
            return None
        return path.resolve(strict=False)
    except Exception:
        return None


def _classify_portfolio_action(tool_name: str, args: dict[str, Any]) -> tuple[str, str]:
    if tool_name in _CONTENT_READ_NAMES:
        return NODE_READ, "Direktes Lesen genau einer Quelle ist im manuellen Discovery-State erlaubt."
    if tool_name in _NAVIGATION_NAMES:
        return NODE_NAVIGATE, "Navigation/Suche/Diagnose darf Wege zeigen, zaehlt aber nicht als echtes Lesen."
    if tool_name in _CONTROL_NAMES or tool_name.startswith("history."):
        return NODE_NAVIGATE, "Expliziter Steuer-/Historienzugriff ist erlaubt, zaehlt aber nicht als Quellenlektüre."

    if tool_name == "services.restart":
        if str(args.get("name") or "") == "vps-mcp.service":
            return NODE_CONTROL_RESTART, "Gezielter Neustart nur des VPS-MCP ist eine CONTROL_PLANE-Mutation."
        return NODE_UNKNOWN_MUTATION, "Dienst-Neustarts ausserhalb vps-mcp.service bleiben fuer diese Reise gesperrt."

    if tool_name == "vps.exec_allowlisted":
        return (
            NODE_SHELL_AUTOMATION,
            "Einzelne Ausfuehrung ueber das vorhandene allowlisted-Tool; dessen Kommando- und Arbeitsordnerpruefung bleibt zustaendig.",
        )

    if tool_name == "vps.shell":
        command = str(args.get("command", args.get("cmd", "")))
        if _SHELL_BACKGROUND_RE.search(command):
            return (
                NODE_BACKGROUND_JOB,
                "Hintergrund-/Detached-Lauf ist in dieser manuellen Reise gesperrt; Arbeit muss als sichtbarer Einzelschritt enden.",
            )
        if _SHELL_INDIRECTION_RE.search(command):
            return (
                NODE_SHELL_AUTOMATION,
                "Shell-Indirection (eval/source/command substitution) verschleiert den echten Einzelschritt und ist hier gesperrt.",
            )
        if (
            _SHELL_INTERPRETER_RE.search(command)
            or _SHELL_LOOP_RE.search(command)
            or _SHELL_HEREDOC_RE.search(command)
        ):
            return (
                NODE_SHELL_AUTOMATION,
                "Interpreter-Aufrufe sind Ausfuehrung; nur ein direkter einzelner Script-Aufruf kann den normalen Workflow-Gate passieren.",
            )
        if _shell_has_mutation(command):
            return (
                NODE_BULK_MUTATION,
                "Mutierende Shell-Befehle sind im Portfolio gesperrt; nutze die einzelnen Dateiwerkzeuge.",
            )
        if _shell_is_single_file_reader(command):
            return NODE_READ, "Direkter sichtbarer Shell-Read genau einer Datei zaehlt als echte Quellenlektüre."
        if _SHELL_FILE_READER_RE.search(command):
            return NODE_SHELL_READ, "Read-only Shell-Suche/Navigation darf Wege zeigen, zaehlt aber nicht als Lesebeweis."
        if _shell_is_allowed_diagnostic(command):
            return NODE_SHELL_READ, "Explizit erlaubte read-only Shell-Navigation/Diagnose ohne Dateiinhalt."
        return (
            NODE_SHELL_AUTOMATION,
            "Shell ist fuer diese Reise fail-closed: nur die explizite Diagnose-Allowlist ist erlaubt; nutze sonst das passende sichtbare MCP-Einzelwerkzeug.",
        )

    if tool_name == "vps.edit_file":
        raw_path = args.get("path", "")
        path = _resolve_absolute_path(raw_path)
        if path is None:
            return NODE_UNKNOWN_MUTATION, "Mutationen brauchen einen expliziten absoluten Zielpfad."
        if bool(args.get("replace_all", False)):
            return NODE_BULK_MUTATION, "replace_all ist auch im Skalpell-/Control-Plane zu breit; Aenderungen muessen gezielt bleiben."
        return NODE_SINGLE_EDIT, "Gezielte Aenderung genau einer bestehenden Datei ist erlaubt."

    if tool_name == "vps.write_file":
        raw_path = args.get("path", "")
        path = _resolve_absolute_path(raw_path)
        if path is None:
            return NODE_UNKNOWN_MUTATION, "Mutationen brauchen einen expliziten absoluten Zielpfad."
        return NODE_SINGLE_WRITE, "Eine einzelne Datei darf gezielt neu angelegt werden."

    if tool_name == "vps.delete":
        raw_path = args.get("path", "")
        try:
            raw_obj = Path(str(raw_path)).expanduser()
        except Exception:
            raw_obj = None
        if raw_obj is not None and raw_obj.is_symlink():
            if not raw_obj.is_absolute():
                return NODE_UNKNOWN_MUTATION, "Mutationen brauchen einen expliziten absoluten Zielpfad."
            return NODE_SINGLE_DELETE, "Ein expliziter Symlink darf nur als Link-Objekt selbst geloescht werden; sein Ziel bleibt unangetastet."
        path = _resolve_absolute_path(raw_path)
        if path is None:
            return NODE_UNKNOWN_MUTATION, "Mutationen brauchen einen expliziten absoluten Zielpfad."
        if path.is_dir():
            return NODE_BULK_MUTATION, "Ordner-Loeschungen bleiben gesperrt; SINGLE_DELETE gilt nur fuer eine einzelne explizite Datei oder einen Symlink."
        return NODE_SINGLE_DELETE, "Eine einzelne explizite Datei darf geloescht werden."

    if tool_name == "vps.move":
        raw_path = args.get("source", args.get("path", ""))
        path = _resolve_absolute_path(raw_path)
        if path is None:
            return NODE_UNKNOWN_MUTATION, "Mutationen brauchen einen expliziten absoluten Quellpfad."
        if path.is_dir():
            return NODE_BULK_MUTATION, "Ordner-Verschiebungen sind im manuellen Discovery-State zu breit."
        return NODE_SINGLE_MOVE, "Eine einzelne explizite Datei darf verschoben werden."

    if _AUTOMATED_READING_NAME_RE.search(tool_name):
        return (
            NODE_AUTOMATED_READING,
            "Automatischer Reader/Crawler/Indexer darf in dieser Arbeit Navigation anbieten, aber nicht das echte Einzel-Lesen ersetzen.",
        )

    if tool_name.startswith("vps."):
        return NODE_UNKNOWN_MUTATION, "Unbekanntes vps.*-Werkzeug ist fail-closed, bis es explizit in den Arbeitsgraphen eingeordnet wurde."

    mutation_words = (
        "write", "edit", "delete", "move", "append", "create", "build", "generate",
        "import", "export", "convert", "save", "run", "exec", "install", "start",
        "stop", "restart", "update",
    )
    if any(word in tool_name.lower() for word in mutation_words):
        return NODE_UNKNOWN_MUTATION, "Unbekannte mutierende Aktion im geschuetzten Portfolio-State."

    return NODE_UNKNOWN_MUTATION, "Unbekanntes MCP-Werkzeug ist in dieser Reise fail-closed, bis wir es bewusst als Lesen, Navigation, Steuerung oder verbotene Aktion eingeordnet haben."


_ALLOWED_NODES = {
    NODE_READ,
    NODE_NAVIGATE,
    NODE_SINGLE_EDIT,
    NODE_SINGLE_WRITE,
    NODE_SINGLE_DELETE,
    NODE_SINGLE_MOVE,
    NODE_SHELL_READ,
    NODE_CONTROL_RESTART,
}

_BLOCKED_NODES = {
    NODE_SHELL_AUTOMATION,
    NODE_META_GENERATION,
    NODE_BULK_MUTATION,
    NODE_UNKNOWN_MUTATION,
    NODE_AUTOMATED_READING,
    NODE_BACKGROUND_JOB,
}


def evaluate_action(
    tool_name: str,
    args: dict[str, Any] | None,
    *,
    allow_direct_execution: bool = False,
) -> GraphDecision:
    args = args if isinstance(args, dict) else {}
    scoped = _project_scoped(tool_name, args)
    if not scoped:
        return GraphDecision(
            decision=DECISION_ALLOW,
            state="OUTSIDE_PORTFOLIO_POLICY",
            action_node=NODE_NAVIGATE,
            tool_name=tool_name,
            project_scoped=False,
            reason="Diese Aktion beruehrt den geschuetzten Portfolio-Arbeitsraum nicht.",
        )

    node, reason = _classify_portfolio_action(tool_name, args)
    direct_execution_allowed = allow_direct_execution and node == NODE_SHELL_AUTOMATION
    if node in _BLOCKED_NODES and not direct_execution_allowed:
        decision = DECISION_BLOCK
    elif node in _ALLOWED_NODES or direct_execution_allowed:
        decision = DECISION_ALLOW
    else:
        decision = DECISION_BLOCK

    return GraphDecision(
        decision=decision,
        state=STATE_MANUAL_DISCOVERY,
        action_node=node,
        tool_name=tool_name,
        project_scoped=True,
        reason=reason,
    )


def graph_snapshot() -> dict[str, Any]:
    edges = []
    for node in sorted(_ALLOWED_NODES):
        edges.append({"from": STATE_MANUAL_DISCOVERY, "to": node, "decision": DECISION_ALLOW})
    for node in sorted(_BLOCKED_NODES):
        edges.append({"from": STATE_MANUAL_DISCOVERY, "to": node, "decision": DECISION_BLOCK})
    edges.append({
        "from": "DIRECT_SINGLE_SCRIPT_CALL + EXISTING_TOOL_CHECKS",
        "to": NODE_SHELL_AUTOMATION,
        "decision": DECISION_ALLOW,
        "conditions": [
            "the command names one script directly",
            "no shell chaining, indirection, loop or background execution",
            "the tool's existing command, path and workflow checks pass",
        ],
    })

    return {
        "active": True,
        "scope": str(PORTFOLIO_ROOT),
        "state": STATE_MANUAL_DISCOVERY,
        "policy_source": _POLICY_SOURCE,
        "nodes": [
            STATE_MANUAL_DISCOVERY,
            *sorted(_ALLOWED_NODES | _BLOCKED_NODES),
        ],
        "edges": edges,
        "principles": [
            "Der aktuelle Auftrag entscheidet, ob direktes Einzel-Lesen erforderlich ist; ein Auftrag kann auch Bauen oder Texten verlangen",
            "direkte Einzelaktionen und neugierige Navigation bleiben maximal moeglich",
            "RAG/Suche ist Kompass und Abenteuerraum, niemals Lesebeweis, Wahrheit oder Vollstaendigkeitsgarantie",
            "Einzelne Code-Dateien koennen wie andere Dateien im ausdruecklich autorisierten Zielscope geschrieben werden; der Suffix allein sperrt nichts",
            "Direkte einzelne Script-Aufrufe laufen durch die vorhandenen Tool- und Workflow-Pruefungen; dafuer wird kein zusaetzlicher TASK-Scope verlangt",
            "Dateinamen wie START.md oder MANIFEST.json begruenden fuer sich keine Sperre",
            "ein Block nennt erlaubte Nachbarkanten statt nur FORBIDDEN zu sagen",
            "der Graph ist ein veraenderbarer Arbeitskoerper; nur ein expliziter sichtbarer Nutzerauftrag darf seine Regeln umstellen",
        ],
    }


def server_instructions() -> str:
    return (
        "Der VPS-Arbeitsgraph richtet sich nach dem aktiven Nutzerauftrag. Direktes Einzel-Lesen ist erforderlich, wenn der Auftrag es verlangt oder eine bestehende Datei bearbeitet wird; Suche/RAG ersetzt diesen Nachweis nicht. "
        "Einzelne Code-Dateien sind normale zielgebundene Writes/Edits; Dateinamen oder Suffixe allein sperren sie nicht. "
        "Ein direkter einzelner Script-Aufruf braucht keinen zusaetzlichen TASK-Scope oder Script-Lesebeleg; die vorhandenen Tool- und Workflow-Pruefungen gelten weiter. "
        "Bulk-, Hintergrund- und verschleierte Shell-Aktionen bleiben gesperrt. "
        "Bei BLOCK die genannten erlaubten Nachbarkanten nutzen."
    )
