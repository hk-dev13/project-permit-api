"""
Simple in-memory cache utilities for permit data.
This module is Flask-agnostic.
"""

from typing import Any, Callable, Optional
import os
import time

# Global cache state
_data_cache: Any = None
_cache_timestamp: Optional[float] = None

# Default TTL (seconds)
CACHE_DURATION: int = int(os.getenv("CACHE_DURATION", "3600"))


def is_cache_valid(now: Optional[float] = None, ttl: Optional[int] = None) -> bool:
	"""Return True if cache exists and is within TTL."""
	global _cache_timestamp
	if _cache_timestamp is None:
		return False
	now_ts = now if now is not None else time.time()
	dur = ttl if ttl is not None else CACHE_DURATION
	return (now_ts - _cache_timestamp) < dur


def get_or_set(fetcher: Callable[[], Any], *, ttl: Optional[int] = None) -> Any:
	"""
	Return cached value if valid, else fetch using fetcher(), cache it, and return it.
	"""
	global _data_cache, _cache_timestamp
	now_ts = time.time()
	if is_cache_valid(now_ts, ttl):
		return _data_cache

	data = fetcher()
	_data_cache = data
	_cache_timestamp = now_ts
	return data


def clear_cache() -> None:
	"""Clear the cache and timestamp."""
	global _data_cache, _cache_timestamp
	_data_cache = None
	_cache_timestamp = None


def get_cache_timestamp() -> Optional[float]:
	"""Get the last cache update timestamp (epoch seconds)."""
	return _cache_timestamp


def set_cache_duration(seconds: int) -> None:
	"""Override default cache TTL (global)."""
	global CACHE_DURATION
	if isinstance(seconds, int) and seconds > 0:
		CACHE_DURATION = seconds
