"""A pipeline stage that must write exactly one terminal receipt."""


class Stage:
    def __init__(self, store, before_write=None):
        self.store = store                      # where receipts are written
        self._finished = False
        self._before_write = before_write or (lambda kind: None)  # test seam

    def _write(self, kind):
        if self._finished:                      # check...
            return False
        self._before_write(kind)                # (window: another thread can pass the check here)
        self._finished = True                   # ...then act
        self.store.append(kind)
        return True

    def complete(self):
        """Called by the stage when its work finishes."""
        return self._write("done")

    def timeout(self):
        """Called by the watchdog thread when the stage overruns."""
        return self._write("timeout")
