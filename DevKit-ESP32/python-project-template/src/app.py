import machine

from time import ticks_cpu, sleep

from src.settings import Config
from src.utils.abstract_singleton import SingletonBase


class AppState:
    SETUP = 0
    RUNNING = 1
    STOPPED = 2
    SHUTDOWN = 3
    IDLE = 4


class App(SingletonBase):
    # Event hooks
    setup = []
    update = []
    shutdown = []

    # Constants
    SLOWED = True
    DEBUG = False

    # App state
    state = AppState.SETUP

    def _init_once(self):
        self.config = Config()
        self.shutdown_request = False
        self.ticks = ticks_cpu

    def idle(self):
        self.state = AppState.IDLE
        led = self.config.pins["led"]
        led.value(0 if led.value() else 1)
        sleep(0.2)
        machine.idle()

    def run(self):
        for setup in self.setup:
            setup()
        self.state = AppState.RUNNING
        while not self.shutdown_request:
            if self.state == AppState.RUNNING:
                if self.DEBUG:
                    print(f"App state: {self.state} | slowed: {self.SLOWED}")
                for update in self.update:
                    update()
                if self.SLOWED:
                    sleep(0.3)
        else:
            self.state = AppState.SHUTDOWN
            for shutdown in self.shutdown:
                shutdown()
