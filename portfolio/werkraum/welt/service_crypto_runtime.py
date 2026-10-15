"""Find Ed25519 dependencies without modifying the read-only API virtualenv."""
import importlib.util
import sys
from pathlib import Path


def enable_crypto():
    if importlib.util.find_spec("cryptography") is None:
        packages = Path(__file__).resolve().parent / ".service_crypto"
        if packages.is_dir() and str(packages) not in sys.path:
            sys.path.insert(0, str(packages))
