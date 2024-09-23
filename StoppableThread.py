import threading

class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self._stop_event = threading.Event()
        print(f"NouvelleThread::{self.name}")

    def stop(self):
        self._stop_event.set()
        if not self.daemon:
            print(f"thread {self.getName()} stopped")

    def stopped(self):
        return self._stop_event.is_set()
    
    