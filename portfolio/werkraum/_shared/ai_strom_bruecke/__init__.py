"""AI-Strom-Brücke runtime package.

The package is intentionally local and model-free.  Existing CLI scripts keep
working as standalone entry points; tests import the shared contracts here.
"""

__all__ = ["contracts", "timeline", "earth_perception", "actions", "tri_leib"]
