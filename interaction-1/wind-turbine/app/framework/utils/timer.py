from framework.app import App
import time

class Timer:
    def __init__(self, duration_ms, on_timeout, autostart=False):
        self.duration_ms = int(duration_ms)
        self.on_timeout = on_timeout

        self.start_time = None
        self.running = False
        self._registered = False

        if autostart:
            self.start()

    @property
    def started(self):
        return self.start_time is not None

    def _register(self):
        if not self._registered:
            App().update.append(self.update)
            self._registered = True

    def _unregister(self):
        if self._registered:
            try:
                App().update.remove(self.update)
            except ValueError:
                pass
            self._registered = False

    def start(self):
        self.reset()
        self.play()

    def reset(self):
        self.start_time = time.ticks_ms()

    def play(self):
        if self.running:
            return
        if self.start_time is None:
            self.reset()
        self.running = True
        self._register()

    def stop(self):
        self.running = False

    def restart(self):
        self.start()

    def quit(self):
        self.stop()
        self._unregister()

    def update(self):
        if not self.running or self.start_time is None:
            return

        if time.ticks_diff(time.ticks_ms(), self.start_time) >= self.duration_ms:
            # Important: désarmer avant callback si le callback recrée/stoppe des trucs
            self.quit()
            try:
                self.on_timeout()
            except Exception as e:
                print("Timer on_timeout error:", e)