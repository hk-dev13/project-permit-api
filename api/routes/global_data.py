from __future__ import annotations


# Thin wrapper to expose global_bp under a non-reserved module name
from importlib import import_module

_mod = import_module("api.routes.global")
global_bp = getattr(_mod, "global_bp")

__all__ = ["global_bp"]
