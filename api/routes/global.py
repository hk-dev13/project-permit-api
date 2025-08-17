from __future__ import annotations

# Re-export global_bp from a single source-of-truth module to avoid duplication
from .global_data import global_bp  # noqa: F401

__all__ = ["global_bp"]
