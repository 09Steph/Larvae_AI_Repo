from PySide6.QtCore import QThread, Signal
import sys
import time

# Helper class to run a function in a separate thread

class ThreadWorker(QThread):
    log_signal = Signal(str)
    finished_signal = Signal(object, float)

    def __init__(self, function, *args, **kwargs):
        super().__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def run(self):
        start_time = time.time()

        old_stdout = sys.stdout
        sys.stdout = self

        try:
            result = self.function(*self.args, **self.kwargs)
        except Exception as e:
            self.log_signal.emit(f"Error: {e}")
            result = None
        finally:
            sys.stdout = old_stdout

        elapsed = time.time() - start_time
        self.finished_signal.emit(result, elapsed)

    def write(self, message):
        if message.strip():
            self.log_signal.emit(message)

    def flush(self):
        pass
