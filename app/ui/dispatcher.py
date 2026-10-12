"""Deliver worker results without calling Tcl from worker threads."""

import logging
from queue import Empty, Queue


class UIDispatcher:
    def __init__(self, root):
        self.root = root
        self.queue = Queue()
        self.closed = False
        self.timer = root.after(50, self._drain)

    def post(self, callback, *args):
        if not self.closed:
            self.queue.put((callback, args))

    def _drain(self):
        for _ in range(100):
            if self.closed:
                return
            try:
                callback, args = self.queue.get_nowait()
            except Empty:
                break
            try:
                callback(*args)
            except Exception:
                logging.getLogger(__name__).exception("UI callback failed")
        if not self.closed:
            self.timer = self.root.after(50, self._drain)

    def close(self):
        self.closed = True
        self.root.after_cancel(self.timer)
        while not self.queue.empty():
            self.queue.get_nowait()
