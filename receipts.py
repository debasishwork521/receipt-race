"""A pipeline stage that must write exactly one terminal receipt."""

import threading


class Stage:
    def __init__(self, store, before_write=None):
        self.store = store                      # where receipts are written
        self._finished = False
        self._lock = threading.Lock()
        self._before_write = before_write or (lambda kind: None)  # test seam

    def _write(self, kind):
        with self._lock:                        # claim atomically: check-and-set
            if self._finished:
                return False
            self._finished = True
        self._before_write(kind)
        self.store.append(kind)
        return True

    def complete(self):
        """Called by the stage when its work finishes."""
        return self._write("done")

    def timeout(self):
        """Called by the watchdog thread when the stage overruns."""
        return self._write("timeout")
