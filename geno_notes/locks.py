"""flock-based advisory locking for state mutations.

Used by tasks.update() and indexer.reindex() to serialize rewrite-then-rename
writes when multiple Claude sessions may be active concurrently.
"""

from __future__ import annotations

import contextlib
import fcntl
from pathlib import Path


@contextlib.contextmanager
def file_lock(lock_path: Path, exclusive: bool = True):
    """Acquire an fcntl.flock on `lock_path`, creating it if needed."""
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    # Open for append so the file is created if missing, without truncating.
    fd = open(lock_path, "a+")
    try:
        fcntl.flock(fd, fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH)
        yield
    finally:
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            fd.close()
