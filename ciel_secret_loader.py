"""Compatibility import for legacy scripts.

The canonical implementation lives in ``scripts.ciel_secret_loader``.  Keeping
this tiny forwarding module makes imports work both when scripts are executed
directly and when they are imported as the ``scripts`` package by pytest.
"""

from scripts.ciel_secret_loader import *  # noqa: F401,F403
