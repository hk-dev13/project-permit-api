# Ensure project root is importable and ignore legacy 'test' folder during collection
import os
import sys

# Add project root to sys.path for absolute imports like 'tests.*'
ROOT = os.path.abspath(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Tell pytest to ignore the old 'test' folder
collect_ignore_glob = ["test/*"]
