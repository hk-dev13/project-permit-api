"""
Global client import shim.
Tries to import KLHKClient from known locations and re-exports it for app usage.

Note: This is a temporary adapter to legacy KLHK client.
Replace with actual EPA client implementation when available.
"""

try:
	# Preferred relative import when used within the package
	from experiments.klhk_client_fixed import KLHKClient  # type: ignore
except Exception:
	# Fallback to direct module import if package context differs
	try:
		from klhk_client_fixed import KLHKClient  # type: ignore
	except Exception as e:
		# Raise a clear error for missing dependency
		raise ImportError(
			"Could not import KLHKClient from experiments.klhk_client_fixed or klhk_client_fixed."
		) from e

__all__ = ["KLHKClient"]
