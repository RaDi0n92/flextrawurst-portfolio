"""Explicit, local ChatGPT browser caller for Codex.

This package intentionally has no dependency on the Eyes-&-Hands bridge or
the AI-UI recorder.  It talks only to an already running Chromium instance
through its local CDP endpoint.
"""

__all__ = ["__version__"]
__version__ = "0.1.0"
