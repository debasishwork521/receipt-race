import threading

from receipts import Stage


def test_done_and_timeout_cannot_both_write_a_receipt():
    in_window = threading.Event()
    release = threading.Event()

    def hook(kind):
        # Park the completion thread between its check and its write.
        if kind == "done":
            in_window.set()
            release.wait()

    receipts = []
    stage = Stage(receipts, before_write=hook)

    completion = threading.Thread(target=stage.complete)
    completion.start()
    assert in_window.wait(timeout=5), "completion never reached the write"

    stage.timeout()  # the watchdog fires at exactly this point

    release.set()
    completion.join(timeout=5)

    assert receipts == ["done"]
