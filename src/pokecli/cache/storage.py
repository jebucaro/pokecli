"""A JSON storage for TinyDB that survives a corrupt cache file.

The default JSONStorage reads with ``json.load`` and writes in place, so an
interrupted or overlapping write can leave trailing bytes that make every later
read raise ``JSONDecodeError``. This storage backs up and resets a corrupt file
on read, and writes atomically via a temp file and ``os.replace``.
"""

import json
import os
import sys
import tempfile
import time
from typing import Any, Optional

from tinydb.storages import JSONStorage


class ResilientJSONStorage(JSONStorage):
    def __init__(self, path: str, *args, **kwargs):
        self._path = path
        self._warned = False
        super().__init__(path, *args, **kwargs)

    def read(self) -> Optional[dict[str, dict[str, Any]]]:
        try:
            return super().read()
        except json.JSONDecodeError:
            self._quarantine()
            return None

    def write(self, data: dict[str, dict[str, Any]]) -> None:
        serialized = json.dumps(data, **self.kwargs)
        directory = os.path.dirname(self._path) or "."
        fd, tmp_path = tempfile.mkstemp(dir=directory, prefix=".cache-", suffix=".tmp")
        try:
            with os.fdopen(fd, "w") as tmp:
                tmp.write(serialized)
                tmp.flush()
                os.fsync(tmp.fileno())
            os.replace(tmp_path, self._path)
            # the old handle points at the replaced inode, reopen on the new file
            self._handle.close()
            self._handle = open(self._path, mode=self._mode)
        except BaseException:
            # leave the live file untouched and drop the temp file
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise

    def _quarantine(self) -> None:
        """Move the corrupt file aside so a fresh cache can take its place.

        ``clear`` reads every table, so this can fire many times in one run.
        We back up once, reopen the handle on a fresh empty file, and warn once.
        """
        backup = f"{self._path}.corrupt-{time.strftime('%Y%m%d-%H%M%S')}"
        try:
            self._handle.close()
            os.replace(self._path, backup)
            # recreate an empty file and reopen so later reads see empty state
            open(self._path, "a").close()
            self._handle = open(self._path, mode=self._mode)
            if not self._warned:
                print(
                    f"pokecli: cache file was corrupt, backed it up to {backup} "
                    "and started fresh",
                    file=sys.stderr,
                )
                self._warned = True
        except OSError:
            # if we cannot move it, there is nothing more we can do here
            pass
