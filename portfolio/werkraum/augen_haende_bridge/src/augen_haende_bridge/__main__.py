"""Command-line entry point for the read-only MCP-P0 runner."""

from .mcp_p0 import _cli


if __name__ == "__main__":
    raise SystemExit(_cli())
